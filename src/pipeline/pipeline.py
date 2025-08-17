"""
Main pipeline for interview preparation.
Orchestrates the execution of all pipeline steps.
"""

import time
from typing import Dict, Any
from pathlib import Path

from ..utils.exceptions import Job4UException
from ..utils.logger import log
from ..utils.constants import BaseStepEnum, STEP_DETAILS, set_step_classes
from ..storage_manager.run_manager import RunManager
from ..steps import (
    JobScrapingStep,
    JobAnalysisStep
    # ResearchPromptStep  # Commented out - not needed for first 2 steps
)


class Pipeline:
    """
    Main pipeline for interview preparation.
    
    This class orchestrates the execution of all pipeline steps
    and manages the flow of data between them.
    """
    
    def __init__(self, config: Any, file_manager: Any):
        """
        Initialize the pipeline.
        
        Args:
            config: Configuration instance
            file_manager: Generic file manager instance
        """
        self.config = config
        self.file_manager = file_manager
        self.run_manager = RunManager(config.output_dir)
        
        # Set step classes dynamically
        set_step_classes()
        
        # Initialize all steps using enums and constants
        self.steps = {
            STEP_DETAILS[BaseStepEnum.JOB_SCRAPING].index: JobScrapingStep(config, file_manager),
            STEP_DETAILS[BaseStepEnum.JOB_ANALYSIS].index: JobAnalysisStep(config, file_manager)
            # STEP_DETAILS[BaseStepEnum.RESEARCH_PROMPT].index: ResearchPromptStep(config, file_manager)  # Commented out - not needed for first 2 steps
        }
        
        log("info", "🔧 Pipeline initialized successfully")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete pipeline.
        
        Returns:
            Dictionary containing all step results
        """
        try:
            # Create run directory using run manager
            run_dir, run_state = self.run_manager.create_run_directory(self.config.test_job_url)
            
            log("info", f"🚀 Starting pipeline run: {run_state['run_name']}")
            
            # Initialize results
            results = {}
            
            # Execute each step in sequence using enums
            for step_enum in BaseStepEnum:
                step_details = STEP_DETAILS[step_enum]
                step_number = step_details.index
                step = self.steps[step_number]
                
                # Execute step
                step_result, success = self._execute_step(step, step_number, results, run_dir, run_state)
                
                if not success:
                    raise Job4UException(f"Step {step_number} failed: {step_result}")
                
                # Store result
                results[f"step_{step_number}"] = step_result
            
            # Mark run as completed
            self.run_manager.update_step_status(run_dir, 0, "pipeline", "completed")
            
            log("info", "🎉 Pipeline completed successfully")
            return results
            
        except Exception as e:
            log("error", f"Pipeline failed: {str(e)}")
            raise
    
    def _execute_step(self, step: Any, step_number: int, previous_results: Dict[str, Any], 
                     run_dir: str, run_state: Dict[str, Any]) -> tuple:
        """
        Execute a single step.
        
        Args:
            step: The step to execute
            step_number: Step number
            previous_results: Results from previous steps
            run_dir: Run directory for output
            run_state: Current run state
            
        Returns:
            Tuple of (result, success_status)
        """
        start_time = time.time()
        
        try:
            log("info", f"🔍 Step {step_number}: Starting {step.step_name}")
            
            # Update step status to running
            self.run_manager.update_step_status(run_dir, step_number, step.step_name, "running")
            
            # Execute step with appropriate parameters based on step enum
            if step.step_enum == BaseStepEnum.JOB_SCRAPING:
                result, success = step.execute(run_dir, job_url=self.config.test_job_url)
            elif step.step_enum == BaseStepEnum.JOB_ANALYSIS:
                result, success = step.execute(
                    run_dir,
                    job_description=previous_results["step_1"],
                    job_url=self.config.test_job_url
                )
            # elif step.step_enum == BaseStepEnum.RESEARCH_PROMPT:  # Commented out - not needed for first 2 steps
            #     result, success = step.execute(run_dir, job_metadata=previous_results["step_2"]) 
            else:
                raise ValueError(f"Unknown step enum: {step.step_enum}")
            
            if success:
                duration = time.time() - start_time
                
                # Update step status to completed
                self.run_manager.update_step_status(
                    run_dir, step_number, step.step_name, "completed", 
                    result=result, error=None
                )
                
                log("info", f"✅ Step {step_number}: {step.step_name} completed", {
                    "duration_seconds": duration
                })
                return result, True
            else:
                # Update step status to failed
                self.run_manager.update_step_status(
                    run_dir, step_number, step.step_name, "failed", 
                    result=None, error=str(result)
                )
                
                log("error", f"❌ Step {step_number}: {step.step_name} failed", {
                    "error": str(result)
                })
                return result, False
                
        except Exception as e:
            duration = time.time() - start_time
            
            # Update step status to failed
            self.run_manager.update_step_status(
                run_dir, step_number, step.step_name, "failed", 
                result=None, error=str(e)
            )
            
            log("error", f"❌ Step {step_number}: {step.step_name} failed", {
                "error": str(e),
                "duration_seconds": duration
            })
            return {"error": str(e)}, False
