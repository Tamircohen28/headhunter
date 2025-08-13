"""
File manager component for job4u application.
Handles file storage, persistence, and organization.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from loguru import logger

from ..utils.config import Config
from ..utils.helpers import generate_unique_id, sanitize_filename


class StepLocation:
    """Tracks where a step result is actually located in the continuation chain."""
    
    def __init__(self, run_name: str, step_dir_name: str, is_symlink: bool = False):
        self.run_name = run_name
        self.step_dir_name = step_dir_name
        self.is_symlink = is_symlink
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "run_name": self.run_name,
            "step_dir_name": self.step_dir_name,
            "is_symlink": self.is_symlink
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StepLocation':
        """Create from dictionary."""
        return cls(
            run_name=data["run_name"],
            step_dir_name=data["step_dir_name"],
            is_symlink=data.get("is_symlink", False)
        )

class RunState:
    """
    Represents the state of a pipeline run.
    """
    
    def __init__(self, job_url: str, run_name: str, continued_from: str = None):
        self.job_url = job_url
        self.run_name = run_name
        self.continued_from = continued_from  # Previous run name if continuing
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()
        self.status = "running"
        self.current_step = 0
        self.total_steps = 7
        self.step_statuses: Dict[str, Dict[str, Any]] = {}  # Only status and error, no results
        self.step_locations: Dict[str, StepLocation] = {}  # Where each step result is actually located
        self.conversation_id: Optional[str] = None
        self.error = None
        self.metadata = {}
        self.run_duration_seconds = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert run state to dictionary for serialization."""
        return {
            "job_url": self.job_url,
            "run_name": self.run_name,
            "continued_from": self.continued_from,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "step_statuses": self.step_statuses,
            "step_locations": {k: v.to_dict() for k, v in self.step_locations.items()},
            "conversation_id": self.conversation_id,
            "error": self.error,
            "metadata": self.metadata,
            "run_duration_seconds": self.run_duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RunState':
        """Create run state from dictionary."""
        run_state = cls(data["job_url"], data["run_name"], data.get("continued_from"))
        run_state.created_at = data.get("created_at")
        run_state.last_updated = data.get("last_updated")
        run_state.status = data.get("status", "running")
        run_state.current_step = data.get("current_step", 0)
        run_state.total_steps = data.get("total_steps", 7)
        run_state.step_statuses = data.get("step_statuses", {})
        
        # Load step locations
        step_locations_data = data.get("step_locations", {})
        run_state.step_locations = {}
        for step_key, location_data in step_locations_data.items():
            run_state.step_locations[step_key] = StepLocation.from_dict(location_data)
        
        run_state.conversation_id = data.get("conversation_id")
        run_state.error = data.get("error")
        run_state.metadata = data.get("metadata", {})
        run_state.run_duration_seconds = data.get("run_duration_seconds", 0)
        
        return run_state
    
    def update_step(self, step_number: int, status: str, error: str = None):
        """Update step status and error (no results stored in state)."""
        self.current_step = step_number
        self.last_updated = datetime.now().isoformat()
        
        step_key = f"step_{step_number}"
        if step_key in self.step_statuses:
            # Update existing step status
            step_status = self.step_statuses[step_key]
            step_status["status"] = status
            step_status["completed_at"] = datetime.now().isoformat()
            step_status["error"] = error[:200] if error else None  # Truncate long error messages
            
            # Calculate duration if we have start time
            if "started_at" in step_status:
                try:
                    start_time = datetime.fromisoformat(step_status["started_at"])
                    end_time = datetime.fromisoformat(step_status["completed_at"])
                    duration_seconds = int((end_time - start_time).total_seconds())
                    step_status["duration_seconds"] = duration_seconds
                except Exception:
                    step_status["duration_seconds"] = 0
        else:
            # Create new step status
            self.step_statuses[step_key] = {
                "status": status,
                "completed_at": datetime.now().isoformat(),
                "error": error[:200] if error else None  # Truncate long error messages
            }
        
        if error:
            self.error = error[:200]  # Truncate long error messages
            self.status = "failed"
        elif step_number >= self.total_steps:
            self.status = "completed"
            self._calculate_run_duration()
    
    def mark_step_started(self, step_number: int):
        """Mark step as started."""
        step_key = f"step_{step_number}"
        self.step_statuses[step_key] = {
            "status": "running",
            "started_at": datetime.now().isoformat()
        }
        self.current_step = step_number
        self.last_updated = datetime.now().isoformat()
    
    def _calculate_run_duration(self):
        """Calculate total run duration in seconds."""
        try:
            from datetime import datetime
            start_time = datetime.fromisoformat(self.created_at)
            end_time = datetime.fromisoformat(self.last_updated)
            self.run_duration_seconds = int((end_time - start_time).total_seconds())
        except Exception:
            self.run_duration_seconds = 0

    def add_step_location(self, step_number: int, run_name: str, step_dir_name: str, is_symlink: bool = False):
        """Add or update step location information."""
        step_key = f"step_{step_number}"
        self.step_locations[step_key] = StepLocation(run_name, step_dir_name, is_symlink)
    
    def get_step_location(self, step_number: int) -> Optional[StepLocation]:
        """Get the location of a step result."""
        step_key = f"step_{step_number}"
        return self.step_locations.get(step_key)


class FileManager:
    """
    Manages file storage and persistence for the job4u application.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the file manager.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.output_config = config.get_output_config()
        
        # Check if output directory version matches current app version
        self._check_and_cleanup_output_directory()
        
        # Ensure output directories exist
        self._setup_directories()
        
        # Load recent runs tracking
        self.recent_runs_file = Path(self.output_config['output_dir']) / "recent_runs.json"
        self.recent_runs: Dict[str, List[str]] = self._load_recent_runs()
        
        logger.info("🔧 File manager initialized successfully")
    
    def _check_and_cleanup_output_directory(self) -> None:
        """Check if output directory version matches current app version and cleanup if needed."""
        try:
            from ..utils.constants import APP_VERSION
            
            current_output_dir = Path(self.output_config['output_dir'])
            expected_output_dir = Path(f"./output_{APP_VERSION}")
            
            # If the current output directory doesn't match the expected version
            if current_output_dir != expected_output_dir:
                logger.warning(f"🔄 Output directory version mismatch detected!")
                logger.warning(f"   Current: {current_output_dir}")
                logger.warning(f"   Expected: {expected_output_dir}")
                
                # Check if old output directory exists and has content
                if current_output_dir.exists() and any(current_output_dir.iterdir()):
                    logger.info(f"🗑️ Cleaning up old output directory: {current_output_dir}")
                    
                    # Remove entire old output directory
                    import shutil
                    shutil.rmtree(current_output_dir)
                    logger.info(f"✅ Old output directory removed: {current_output_dir}")
                
                # Update config to use new versioned directory
                self.output_config['output_dir'] = str(expected_output_dir)
                logger.info(f"🔄 Updated output directory to: {expected_output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to check/cleanup output directory: {e}")
            # Continue with current directory if cleanup fails
    
    def _setup_directories(self) -> None:
        """Create necessary output directories if they don't exist."""
        try:
            # Create output directory
            output_dir = Path(self.output_config['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create logs directory
            log_dir = Path(self.output_config['log_dir'])
            log_dir.mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"📁 Output directories ready: {output_dir}, {log_dir}")
            
        except Exception as e:
            logger.error(f"Failed to setup directories: {e}")
            raise
    
    def _load_recent_runs(self) -> Dict[str, List[str]]:
        """Load recent runs from file."""
        try:
            if self.recent_runs_file.exists():
                with open(self.recent_runs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert old format (single string) to new format (list)
                    recent_runs = {}
                    for key, value in data.items():
                        if isinstance(value, str):
                            # Old format: convert to list
                            recent_runs[key] = [value]
                        elif isinstance(value, list):
                            # New format: keep as is
                            recent_runs[key] = value
                        else:
                            # Invalid format: skip
                            logger.warning(f"Invalid recent run format for {key}: {value}")
                    return recent_runs
            return {}
        except Exception as e:
            logger.error(f"Failed to load recent runs: {e}")
            return {}
    
    def _save_recent_runs(self) -> None:
        """Save recent runs to file."""
        try:
            with open(self.recent_runs_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_runs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save recent runs: {e}")
    
    def _add_run_to_recent_runs(self, job_url: str, run_name: str) -> None:
        """
        Add a run to recent runs tracking.
        
        Args:
            job_url: The job URL
            run_name: The run name to add
        """
        try:
            job_hash = self._hash_job_url(job_url)
            
            if job_hash not in self.recent_runs:
                self.recent_runs[job_hash] = []
            
            # Remove the run if it already exists (to avoid duplicates)
            if run_name in self.recent_runs[job_hash]:
                self.recent_runs[job_hash].remove(run_name)
            
            # Add the new run to the beginning (most recent)
            self.recent_runs[job_hash].insert(0, run_name)
            
            # Keep only the last 10 runs per URL to prevent the list from growing too large
            if len(self.recent_runs[job_hash]) > 10:
                self.recent_runs[job_hash] = self.recent_runs[job_hash][:10]
            
            # Save the updated recent runs
            self._save_recent_runs()
            
            logger.debug(f"📝 Added run {run_name} to recent runs for job {job_hash[:8]}...")
            
        except Exception as e:
            logger.error(f"Failed to add run to recent runs: {e}")
    
    def _hash_job_url(self, job_url: str) -> str:
        """Create a hash of the job URL for tracking."""
        return hashlib.md5(job_url.encode()).hexdigest()
    
    def find_previous_run(self, job_url: str) -> Optional[Tuple[str, str]]:
        """
        Find the most recent previous run for a job URL.
        
        Args:
            job_url: The job URL to search for
            
        Returns:
            Tuple of (run_name, run_dir_path) if found, None otherwise
        """
        try:
            job_hash = self._hash_job_url(job_url)
            
            if job_hash in self.recent_runs and self.recent_runs[job_hash]:
                # Get the most recent run (index 0)
                most_recent_run = self.recent_runs[job_hash][0]
                run_dir = Path(self.output_config['output_dir']) / most_recent_run
                
                if run_dir.exists():
                    logger.info(f"🔍 Found previous run: {most_recent_run}")
                    return most_recent_run, str(run_dir)
                else:
                    # Run directory doesn't exist, remove from recent runs
                    logger.warning(f"⚠️ Previous run directory not found: {most_recent_run}")
                    self.recent_runs[job_hash].pop(0)
                    self._save_recent_runs()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find previous run: {e}")
            return None
    
    def create_run_directory(self, job_url: str, timestamp: Optional[str] = None, 
                           continued_from: str = None) -> Tuple[str, RunState]:
        """
        Create a new run directory for a pipeline execution.
        
        Args:
            job_url: The URL of the job being processed
            timestamp: Optional timestamp for the run (defaults to current time)
            continued_from: Name of previous run if continuing
            
        Returns:
            Tuple of (run_dir_path, run_state)
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create clean run directory name (just timestamp)
            run_dir_name = f"run_{timestamp}"
            
            # Create the run directory
            run_dir = Path(self.output_config['output_dir']) / run_dir_name
            run_dir.mkdir(parents=True, exist_ok=True)
            
            # Create run state
            run_state = RunState(job_url, run_dir_name, continued_from)
            
            # Save initial run state
            self._save_run_state(run_dir, run_state)
            
            # Update recent runs tracking
            self._add_run_to_recent_runs(job_url, run_dir_name)
            
            logger.info(f"📁 Created run directory: {run_dir}")
            return str(run_dir), run_state
            
        except Exception as e:
            logger.error(f"Failed to create run directory: {e}")
            raise
    
    def create_step_directory(self, run_dir: str, step_number: int, step_name: str) -> str:
        """
        Create a directory for a specific step within a run.
        
        Args:
            run_dir: Path to the run directory
            step_number: The step number
            step_name: The step name
            
        Returns:
            Path to the created step directory
        """
        try:
            run_path = Path(run_dir)
            step_dir_name = f"step_{step_number:02d}_{step_name}"
            step_dir = run_path / step_dir_name
            step_dir.mkdir(parents=True, exist_ok=True)
            
            logger.debug(f"📁 Created step directory: {step_dir}")
            return str(step_dir)
            
        except Exception as e:
            logger.error(f"Failed to create step directory: {e}")
            raise
    
    def _save_run_state(self, run_dir: str, run_state: RunState) -> None:
        """Save run state to file."""
        try:
            run_path = Path(run_dir)
            state_file = run_path / "run_state.json"
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(run_state.to_dict(), f, indent=2, default=str)
            
            logger.debug(f"💾 Saved run state to {state_file}")
            
        except Exception as e:
            logger.error(f"Failed to save run state: {e}")
    
    def load_run_state(self, run_dir: str) -> RunState:
        """Load run state from file."""
        try:
            run_path = Path(run_dir)
            state_file = run_path / "run_state.json"
            
            if not state_file.exists():
                raise FileNotFoundError(f"Run state file not found: {state_file}")
            
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            run_state = RunState.from_dict(state_data)
            logger.debug(f"📂 Loaded run state from {state_file}")
            return run_state
            
        except Exception as e:
            logger.error(f"Failed to load run state: {e}")
            raise
    
    def update_run_state(self, run_dir: str, run_state: RunState) -> None:
        """Update and save run state."""
        try:
            run_state.last_updated = datetime.now().isoformat()
            self._save_run_state(run_dir, run_state)
            logger.debug(f"💾 Updated run state for {run_dir}")
            
        except Exception as e:
            logger.error(f"Failed to update run state: {e}")
    
    def create_step_symlink(self, current_run_dir: str, step_number: int, 
                            previous_run_name: str, previous_step_dir_name: str) -> str:
        """
        Create a symbolic link to a previous run's step directory.
        
        Args:
            current_run_dir: Current run directory
            step_number: Current step number
            previous_run_name: Name of the previous run directory
            previous_step_dir_name: Name of the previous step directory (e.g., "step_01_job_description_scraping")
            
        Returns:
            Path to the created symlink
        """
        try:
            current_run_path = Path(current_run_dir)
            # Use the same directory name as the real step directory
            step_dir = current_run_path / previous_step_dir_name
            
            # Calculate relative path from current run to previous run
            # Current run: output_1.0.1/run_20250813_210232
            # Previous run: output_1.0.1/run_20250813_210059
            # Relative path: ../run_20250813_210059/step_01_job_description_scraping
            relative_path = Path("..") / previous_run_name / previous_step_dir_name

            if not step_dir.parent.exists():
                logger.warning(f"⚠️ Current run directory not found: {step_dir.parent}")
                return None
            
            # Create symlink to previous step directory using relative path
            if os.name == 'nt':  # Windows
                # On Windows, create a junction or copy files
                # Symlinks require admin privileges, so copying is a safer fallback
                previous_step_full_path = current_run_path.parent / previous_run_name / previous_step_dir_name
                if previous_step_full_path.exists():
                    shutil.copytree(previous_step_full_path, step_dir)
                    logger.info(f"📁 Copied previous step directory (Windows fallback): {step_dir}")
                else:
                    logger.warning(f"⚠️ Previous step directory not found for copy: {previous_step_full_path}")
                    return None
            else:  # Unix-like systems
                # Create symlink using relative path
                step_dir.symlink_to(relative_path, target_is_directory=True)
                logger.info(f"🔗 Created symlink to previous step: {step_dir} -> {relative_path}")
            
            return str(step_dir)
            
        except Exception as e:
            logger.error(f"Failed to create step symlink: {e}")
            raise
    
    def save_step_result(self, run_dir: str, step_number: int, step_name: str, result: Any) -> str:
        """
        Save a step result to a file.
        
        Args:
            run_dir: Path to the run directory
            step_number: The step number
            step_name: The step name
            result: The result to save
            
        Returns:
            Path to the saved file
        """
        try:
            # Create step directory if it doesn't exist
            step_dir = self.create_step_directory(run_dir, step_number, step_name)
            
            # Determine file extension based on step type
            if step_name in ["custom_gpt_instructions", "research_prompt", "research_prompt_division", "interview_guide"]:
                file_ext = ".md"
            elif step_name in ["job_analysis", "research_results"]:
                file_ext = ".json"
            else:
                file_ext = ".txt"
            
            # Create filename
            filename = f"{step_name}{file_ext}"
            file_path = Path(step_dir) / filename
            
            # Special handling for Step 4 (research_prompt_division)
            if step_name == "research_prompt_division" and isinstance(result, dict) and "markdown_content" in result:
                # Save the Markdown content for Step 4
                content_to_save = result["markdown_content"]
            else:
                content_to_save = result
            
            # Save result based on type
            if file_ext == ".json" and isinstance(content_to_save, (dict, list)):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content_to_save, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(content_to_save))
            
            logger.info(f"💾 Saved {step_name} result to {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save step result: {e}")
            raise
    
    def load_step_result(self, run_dir: str, step_number: int, step_name: str) -> Any:
        """
        Load a step result from a file.
        
        Args:
            run_dir: Path to the run directory
            step_number: The step number
            step_name: The step name
            
        Returns:
            The loaded result or None if not found
        """
        try:
            # Determine file extension based on step type
            if step_name in ["custom_gpt_instructions", "research_prompt", "interview_guide"]:
                file_ext = ".md"
            elif step_name in ["job_analysis", "research_results"]:
                file_ext = ".json"
            else:
                file_ext = ".txt"
            
            # Create filename
            filename = f"{step_name}{file_ext}"
            file_path = Path(run_dir) / f"step_{step_number:02d}_{step_name}" / filename
            
            if not file_path.exists():
                logger.warning(f"⚠️ Step result file not found: {file_path}")
                return None
            
            # Load result based on file type
            if file_ext == ".json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to load step result: {e}")
            return None
    
    def save_pipeline_results(self, run_dir: str, step_results: Dict[str, Any]) -> Dict[str, str]:
        """
        Save pipeline step results to their respective step directories.
        
        Args:
            run_dir: Path to the run directory
            step_results: Dictionary containing step results
            
        Returns:
            Dictionary mapping step names to saved file paths
        """
        try:
            saved_files = {}
            
            for step_name, result in step_results.items():
                if result is None:
                    continue
                
                # Extract step number from step name (e.g., "step_1_job_analysis" -> 1)
                step_number = 1  # Default
                if step_name.startswith("step_") and "_" in step_name:
                    try:
                        step_number = int(step_name.split("_")[1])
                    except (ValueError, IndexError):
                        pass
                
                # Save to step directory
                file_path = self.save_step_result(run_dir, step_number, step_name, result)
                saved_files[step_name] = file_path
            
            logger.info(f"✅ Saved {len(saved_files)} pipeline results to {run_dir}")
            return saved_files
            
        except Exception as e:
            logger.error(f"Failed to save pipeline results: {e}")
            raise
    
    def create_readme(self, run_dir: str, job_analysis: Dict[str, Any], step_results: Dict[str, Any]) -> str:
        """
        Create a README file for the run directory.
        
        Args:
            run_dir: Path to the run directory
            job_analysis: The job analysis data
            step_results: Dictionary of step results
            
        Returns:
            Path to the created README file
        """
        try:
            run_path = Path(run_dir)
            readme_path = run_path / "README.md"
            
            # Build README content
            readme_content = self._build_readme_content(job_analysis, step_results)
            
            # Save README
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"📝 Created README for run: {readme_path}")
            return str(readme_path)
            
        except Exception as e:
            logger.error(f"Failed to create README: {e}")
            raise
    
    def _build_readme_content(self, job_analysis: Dict[str, Any], step_results: Dict[str, Any]) -> str:
        """Build the content for the README file."""
        try:
            company = job_analysis.get('company', 'Unknown Company')
            role = job_analysis.get('role', 'Unknown Role')
            location = job_analysis.get('location', 'Unknown Location')
            job_url = job_analysis.get('job_link', 'N/A')
            
            # Count successful steps
            successful_steps = sum(1 for result in step_results.values() if result is not None)
            total_steps = len(step_results)
            
            readme = f"""# Job4U Interview Preparation Pipeline Results

## Job Information
- **Company:** {company}
- **Role:** {role}
- **Location:** {location}
- **Job URL:** {job_url}

## Pipeline Execution Summary
- **Total Steps:** {total_steps}
- **Successful Steps:** {successful_steps}
- **Success Rate:** {(successful_steps / total_steps) * 100:.1f}%
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Step Results
"""
            
            # Add step details
            for step_name, result in step_results.items():
                if result is not None:
                    if isinstance(result, str):
                        status = "✅ Completed"
                        details = f"Generated {len(result)} characters"
                    elif isinstance(result, dict):
                        status = "✅ Completed"
                        details = f"Generated {len(str(result))} characters of structured data"
                    else:
                        status = "✅ Completed"
                        details = f"Generated result of type {type(result).__name__}"
                else:
                    status = "❌ Failed/Not Executed"
                    details = "No result generated"
                
                readme += f"- **{step_name.replace('_', ' ').title()}:** {status} - {details}\n"
            
            readme += f"""
## Files Generated
This directory contains the following files:
- `README.md` - This summary file
- `run_state.json` - Run state and metadata
- Step directories with individual results
- Any additional generated content

## Usage Notes
- Review the generated content for accuracy and completeness
- Customize the materials based on your specific needs
- Use the custom GPT instructions to create a personalized interview preparation assistant
- Follow the study timeline for structured preparation

---
*Generated by Job4U Interview Preparation Pipeline*
"""
            
            return readme
            
        except Exception as e:
            logger.error(f"Failed to build README content: {e}")
            return f"# Job4U Pipeline Results\n\nError generating README: {str(e)}"
    
    def cleanup_old_runs(self, max_runs: int = 10) -> int:
        """
        Clean up old run directories, keeping only the most recent ones.
        
        Args:
            max_runs: Maximum number of runs to keep
            
        Returns:
            Number of directories cleaned up
        """
        try:
            output_dir = Path(self.output_config['output_dir'])
            if not output_dir.exists():
                return 0
            
            # Get all run directories sorted by creation time
            run_dirs = []
            for item in output_dir.iterdir():
                if item.is_dir() and item.name.startswith('run_'):
                    run_dirs.append((item, item.stat().st_ctime))
            
            # Sort by creation time (newest first)
            run_dirs.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old directories
            removed_count = 0
            for run_dir, _ in run_dirs[max_runs:]:
                try:
                    import shutil
                    shutil.rmtree(run_dir)
                    removed_count += 1
                    logger.info(f"🗑️ Cleaned up old run directory: {run_dir.name}")
                except Exception as e:
                    logger.warning(f"Failed to remove old run directory {run_dir.name}: {e}")
            
            if removed_count > 0:
                logger.info(f"🧹 Cleaned up {removed_count} old run directories")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old runs: {e}")
            return 0
    
    def get_run_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about pipeline runs.
        
        Returns:
            Dictionary containing run statistics
        """
        try:
            output_dir = Path(self.output_config['output_dir'])
            if not output_dir.exists():
                return {"total_runs": 0, "recent_runs": []}
            
            # Count total runs
            run_dirs = [item for item in output_dir.iterdir() 
                       if item.is_dir() and item.name.startswith('run_')]
            
            # Get recent run info
            recent_runs = []
            for run_dir in sorted(run_dirs, key=lambda x: x.stat().st_ctime, reverse=True)[:5]:
                try:
                    stats = run_dir.stat()
                    recent_runs.append({
                        "name": run_dir.name,
                        "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        "size": self._get_directory_size(run_dir)
                    })
                except Exception:
                    continue
            
            return {
                "total_runs": len(run_dirs),
                "recent_runs": recent_runs
            }
            
        except Exception as e:
            logger.error(f"Failed to get run statistics: {e}")
            return {"error": str(e)}
    
    def _get_directory_size(self, directory: Path) -> str:
        """Get the size of a directory in human-readable format."""
        try:
            total_size = 0
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total_size < 1024.0:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024.0
            
            return f"{total_size:.1f} TB"
            
        except Exception:
            return "Unknown"
