"""
Run manager for handling pipeline runs, continuation, and state persistence.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ..utils.logger import log
from ..utils.constants import APP_VERSION


class RunManager:
    """
    Manages pipeline runs, including continuation logic and state persistence.
    """
    
    def __init__(self, base_dir: str):
        """
        Initialize the run manager.
        
        Args:
            base_dir: Base directory for all operations
        """
        self.base_dir = Path(base_dir)
        self.recent_runs_file = self.base_dir / "recent_runs.json"
        self.recent_runs = self._load_recent_runs()
        
        log("info", "🔧 Run manager initialized", {"base_dir": str(self.base_dir)})
    
    def _load_recent_runs(self) -> Dict[str, list]:
        """Load recent runs from file."""
        if self.recent_runs_file.exists():
            try:
                with open(self.recent_runs_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                log("error", f"Failed to load recent runs: {e}")
                return {}
        return {}
    
    def _save_recent_runs(self) -> None:
        """Save recent runs to file."""
        try:
            with open(self.recent_runs_file, 'w') as f:
                json.dump(self.recent_runs, f, indent=2)
        except Exception as e:
            log("error", f"Failed to save recent runs: {e}")
    
    def _hash_job_url(self, job_url: str) -> str:
        """Create a hash of the job URL."""
        return hashlib.md5(job_url.encode()).hexdigest()
    
    def create_run_directory(self, job_url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Create a new run directory or continue from existing run.
        
        Args:
            job_url: The job URL to process
            
        Returns:
            Tuple of (run_directory_path, run_state)
        """
        job_hash = self._hash_job_url(job_url)
        
        # Check if we have previous runs for this job
        # if job_hash in self.recent_runs and self.recent_runs[job_hash]:  # Commented out - no continuation during testing
        #     # Find the most recent incomplete run
        #     incomplete_run = self._find_incomplete_run(job_hash)
        #     
        #     if incomplete_run:
        #         log("info", f"🔄 Found incomplete run: {incomplete_run}")
        #         return self._continue_run(job_url, job_hash, incomplete_run)
        #     else:
        #         log("info", f"✅ All previous runs are complete, starting new run")
        #         return self._create_new_run(job_url, job_hash, is_continuation=False)
        # else:
        #     log("info", f"🚀 No previous run found, starting new run for job")
        #     return self._create_new_run(job_url, job_hash, is_continuation=False)
        
        # Always start fresh during testing
        log("info", f"🚀 Starting fresh run for job (continuation disabled)")
        return self._create_new_run(job_url, job_hash, is_continuation=False)
    
    def _find_incomplete_run(self, job_hash: str) -> Optional[str]:
        """Find the most recent incomplete run for a job hash."""
        if job_hash not in self.recent_runs:
            return None
        
        # Check runs in reverse order (most recent first)
        for run_name in self.recent_runs[job_hash]:
            if not self._is_run_complete(run_name):
                return run_name
        
        return None
    
    def _create_new_run(self, job_url: str, job_hash: str, is_continuation: bool) -> Tuple[str, Dict[str, Any]]:
        """Create a new run directory."""
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        run_name = f"run_{timestamp}"
        run_dir = self.base_dir / run_name
        
        # Create run directory
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create run state
        run_state = {
            "run_name": run_name,
            "job_url": job_url,
            "job_hash": job_hash,
            "started_at": datetime.now().isoformat(),
            "is_continuation": is_continuation,
            "continued_from": None,
            "app_version": APP_VERSION,
            "steps": {},
            "status": "running"
        }
        
        # Save run state
        self._save_run_state(run_dir, run_state)
        
        # Add to recent runs
        if job_hash not in self.recent_runs:
            self.recent_runs[job_hash] = []
        self.recent_runs[job_hash].insert(0, run_name)  # Add to beginning
        self._save_recent_runs()
        
        log("info", f"📁 Created new run directory: {run_dir}")
        return str(run_dir), run_state
    
    def _is_run_complete(self, run_name: str) -> bool:
        """Check if a run is complete (all steps completed successfully)."""
        run_dir = self.base_dir / run_name
        run_state_file = run_dir / "run_state.json"
        
        if not run_state_file.exists():
            return False
        
        try:
            with open(run_state_file, 'r') as f:
                run_state = json.load(f)
                
            # Check if all steps are completed
            steps = run_state.get("steps", {})
            if not steps:
                return False
                
            # A run is complete only if ALL steps are completed
            all_steps_completed = all(
                step.get("status") == "completed" 
                for step in steps.values()
            )
            
            return all_steps_completed
            
        except Exception:
            return False
    
    def _get_last_completed_step(self, run_name: str) -> int:
        """Get the last completed step number in a run."""
        run_dir = self.base_dir / run_name
        run_state_file = run_dir / "run_state.json"
        
        if not run_state_file.exists():
            return 0
        
        try:
            with open(run_state_file, 'r') as f:
                run_state = json.load(f)
                
            steps = run_state.get("steps", {})
            last_completed = 0
            
            for step_key, step_data in steps.items():
                if step_data.get("status") == "completed":
                    step_num = step_data.get("step_number", 0)
                    last_completed = max(last_completed, step_num)
            
            return last_completed
            
        except Exception:
            return 0
    
    def _create_symlink_for_step(self, current_run_dir: str, step_number: int, 
                                previous_run: str, step_name: str) -> bool:
        """
        Create a symlink to a completed step from a previous run.
        
        Args:
            current_run_dir: Current run directory
            step_number: Step number to symlink
            previous_run: Previous run name
            step_name: Step name
            
        Returns:
            True if symlink created successfully, False otherwise
        """
        try:
            current_run_path = Path(current_run_dir)
            step_dir_name = f"step_{step_number:02d}_{step_name.lower().replace(' ', '_')}"
            current_step_dir = current_run_path / step_dir_name
            
            # Create the step directory
            current_step_dir.mkdir(parents=True, exist_ok=True)
            
            # Find the previous step directory
            previous_run_path = self.base_dir / previous_run
            previous_step_pattern = f"step_{step_number:02d}_*"
            previous_step_dirs = list(previous_run_path.glob(previous_step_pattern))
            
            if not previous_step_dirs:
                log("warning", f"No previous step directory found for step {step_number}")
                return False
            
            previous_step_dir = previous_step_dirs[0]
            
            # Create symlink for each file in the previous step directory
            for file_path in previous_step_dir.glob("*"):
                if file_path.is_file():
                    symlink_path = current_step_dir / file_path.name
                    if not symlink_path.exists():
                        # Create relative symlink
                        relative_path = os.path.relpath(file_path, current_step_dir)
                        symlink_path.symlink_to(relative_path)
                        log("info", f"🔗 Created symlink: {symlink_path} -> {relative_path}")
            
            return True
            
        except Exception as e:
            log("error", f"Failed to create symlink for step {step_number}: {e}")
            return False
    
    def _continue_run(self, job_url: str, job_hash: str, previous_run: str) -> Tuple[str, Dict[str, Any]]:
        """Continue from a previous run."""
        # Create new run directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"run_{timestamp}"
        run_dir = self.base_dir / run_name
        
        # Create run directory
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the last completed step from previous run
        last_completed_step = self._get_last_completed_step(previous_run)
        
        # Create run state
        run_state = {
            "run_name": run_name,
            "job_url": job_url,
            "job_hash": job_hash,
            "started_at": datetime.now().isoformat(),
            "is_continuation": True,
            "continued_from": previous_run,
            "last_completed_step": last_completed_step,
            "app_version": APP_VERSION,
            "steps": {},
            "status": "running"
        }
        
        # Save run state
        self._save_run_state(run_dir, run_state)
        
        # Create symlinks for all completed steps
        if last_completed_step > 0:
            log("info", f"🔗 Creating symlinks for completed steps 1-{last_completed_step}")
            for step_num in range(1, last_completed_step + 1):
                # Get step name from previous run
                step_name = self._get_step_name_from_previous_run(previous_run, step_num)
                if step_name:
                    self._create_symlink_for_step(str(run_dir), step_num, previous_run, step_name)
        
        # Add to recent runs
        self.recent_runs[job_hash].insert(0, run_name)
        self._save_recent_runs()
        
        log("info", f"📁 Created continuation run directory: {run_dir}")
        return str(run_dir), run_state
    
    def _get_step_name_from_previous_run(self, previous_run: str, step_number: int) -> Optional[str]:
        """Get the step name from a previous run."""
        run_dir = self.base_dir / previous_run
        run_state_file = run_dir / "run_state.json"
        
        if not run_state_file.exists():
            return None
        
        try:
            with open(run_state_file, 'r') as f:
                run_state = json.load(f)
                
            step_key = f"step_{step_number}"
            if step_key in run_state.get("steps", {}):
                return run_state["steps"][step_key].get("step_name")
            
            return None
            
        except Exception:
            return None
    
    def _save_run_state(self, run_dir: Path, run_state: Dict[str, Any]) -> None:
        """Save run state to file."""
        state_file = run_dir / "run_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(run_state, f, indent=2)
        except Exception as e:
            log("error", f"Failed to save run state: {e}")
    
    def update_step_status(self, run_dir: str, step_number: int, step_name: str, 
                          status: str, result: Any = None, error: str = None) -> None:
        """
        Update the status of a step in the run state.
        
        Args:
            run_dir: Run directory path
            step_number: Step number
            step_name: Step name
            status: Step status
            result: Step result (optional)
            error: Error message (optional)
        """
        run_dir_path = Path(run_dir)
        state_file = run_dir_path / "run_state.json"
        
        if not state_file.exists():
            log("warning", f"Run state file not found: {state_file}")
            return
        
        try:
            with open(state_file, 'r') as f:
                run_state = json.load(f)
            
            # Get or create step data
            step_key = f"step_{step_number}"
            if step_key not in run_state["steps"]:
                # First time seeing this step - initialize it
                run_state["steps"][step_key] = {
                    "step_number": step_number,
                    "step_name": step_name,
                    "status": status,
                    "started_at": datetime.now().isoformat(),
                    "duration_seconds": None,
                    "result_file": None,
                    "error": None
                }
            else:
                # Update existing step
                current_step = run_state["steps"][step_key]
                
                # Only set started_at if not already set
                if current_step.get("started_at") is None:
                    current_step["started_at"] = datetime.now().isoformat()
                
                # Calculate duration if completing
                if status in ["completed", "failed"] and current_step.get("started_at"):
                    start_time = datetime.fromisoformat(current_step["started_at"])
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    current_step["duration_seconds"] = duration
                
                # Update status and error
                current_step["status"] = status
                if error:
                    current_step["error"] = error
                
                # Set result file path if completed successfully
                if status == "completed" and result:
                    # Find the result file in the step directory
                    step_dir_pattern = f"step_{step_number:02d}_*"
                    step_dirs = list(run_dir_path.glob(step_dir_pattern))
                    if step_dirs:
                        step_dir = step_dirs[0]
                        # Look for the main result file
                        for file_path in step_dir.glob("*"):
                            if file_path.is_file() and not file_path.name.startswith("."):
                                # Use relative path from run directory
                                relative_path = file_path.relative_to(run_dir_path)
                                current_step["result_file"] = str(relative_path)
                                break
            
            # Update overall run status
            if status == "failed":
                run_state["status"] = "failed"
            elif status == "completed":
                # Check if all steps are completed
                all_completed = all(
                    step.get("status") == "completed" 
                    for step in run_state["steps"].values()
                    if step.get("step_number", 0) > 0  # Exclude pipeline step (step_0)
                )
                if all_completed:
                    run_state["status"] = "completed"
                    run_state["completed_at"] = datetime.now().isoformat()
            
            # Save updated state
            self._save_run_state(run_dir_path, run_state)
            
        except Exception as e:
            log("error", f"Failed to update step status: {e}")
    
    def get_previous_step_results(self, run_dir: str, step_number: int) -> Optional[Any]:
        """
        Get results from a previous run's step.
        
        Args:
            run_dir: Current run directory
            step_number: Step number to get results for
            
        Returns:
            Step results if available, None otherwise
        """
        run_dir_path = Path(run_dir)
        state_file = run_dir_path / "run_state.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r') as f:
                run_state = json.load(f)
            
            # Check if this is a continuation run
            if not run_state.get("is_continuation"):
                return None
            
            previous_run = run_state.get("continued_from")
            if not previous_run:
                return None
            
            # Look for step results in previous run
            previous_run_dir = self.base_dir / previous_run
            step_pattern = f"step_{step_number:02d}_*"
            
            for step_dir in previous_run_dir.glob(step_pattern):
                # Look for result files
                for result_file in step_dir.glob("*"):
                    if result_file.is_file():
                        log("info", f"📋 Found previous step result: {result_file}")
                        return str(result_file)
            
            return None
            
        except Exception as e:
            log("error", f"Failed to get previous step results: {e}")
            return None
