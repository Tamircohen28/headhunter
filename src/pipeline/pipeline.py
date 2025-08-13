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
from ..steps import (
    JobScrapingStep,
    JobAnalysisStep,
    CustomGPTInstructionsStep,
    ResearchDivisionStep
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
        
        # Set step classes dynamically
        set_step_classes()
        
        # Initialize all steps using enums and constants
        self.steps = {
            STEP_DETAILS[BaseStepEnum.JOB_SCRAPING].index: JobScrapingStep(config, file_manager),
            STEP_DETAILS[BaseStepEnum.JOB_ANALYSIS].index: JobAnalysisStep(config, file_manager),
            STEP_DETAILS[BaseStepEnum.CUSTOM_GPT_INSTRUCTIONS].index: CustomGPTInstructionsStep(config, file_manager),
            STEP_DETAILS[BaseStepEnum.RESEARCH_DIVISION].index: ResearchDivisionStep(config, file_manager)
        }
        
        log("info", "🔧 Pipeline initialized successfully")
    
    def run(self) -> Dict[str, Any]:
        """
        Run the complete pipeline.
        
        Returns:
            Dictionary containing all step results
        """
        try:
            # Create run directory
            run_dir = self._create_run_directory()
            
            # Initialize results
            results = {}
            
            # Execute each step in sequence using enums
            for step_enum in BaseStepEnum:
                step_details = STEP_DETAILS[step_enum]
                step_number = step_details.index
                step = self.steps[step_number]
                
                # Execute step
                step_result, success = self._execute_step(step, step_number, results, run_dir)
                
                if not success:
                    raise Job4UException(f"Step {step_number} failed: {step_result}")
                
                # Store result
                results[f"step_{step_number}"] = step_result
            
            log("info", "🎉 Pipeline completed successfully")
            return results
            
        except Exception as e:
            log("error", f"Pipeline failed: {str(e)}")
            raise
    
    def _create_run_directory(self) -> str:
        """Create a run directory for this pipeline execution."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        run_dir_name = f"run_{timestamp}"
        run_dir = self.file_manager.create_directory(run_dir_name)
        
        log("info", f"📁 Created run directory: {run_dir}")
        return run_dir
    
    def _execute_step(self, step: Any, step_number: int, previous_results: Dict[str, Any], run_dir: str) -> tuple:
        """
        Execute a single step.
        
        Args:
            step: The step to execute
            step_number: Step number
            previous_results: Results from previous steps
            run_dir: Run directory for output
            
        Returns:
            Tuple of (result, success_status)
        """
        start_time = time.time()
        
        try:
            log("info", f"🔍 Step {step_number}: Starting {step.step_name}")
            
            # Execute step with appropriate parameters based on step enum
            if step.step_enum == BaseStepEnum.JOB_SCRAPING:
                result, success = step.execute(run_dir, job_url=self.config.test_job_url)
            elif step.step_enum == BaseStepEnum.JOB_ANALYSIS:
                result, success = step.execute(
                    run_dir,
                    job_description=previous_results["step_1"],
                    job_url=self.config.test_job_url
                )
            elif step.step_enum == BaseStepEnum.CUSTOM_GPT_INSTRUCTIONS:
                result, success = step.execute(run_dir, job_analysis=previous_results["step_1"])
            elif step.step_enum == BaseStepEnum.RESEARCH_DIVISION:
                result, success = step.execute(run_dir, job_analysis=previous_results["step_1"])
            else:
                raise ValueError(f"Unknown step enum: {step.step_enum}")
            
            if success:
                duration = time.time() - start_time
                log("info", f"✅ Step {step_number}: {step.step_name} completed", {
                    "duration_seconds": duration
                })
                return result, True
            else:
                log("error", f"❌ Step {step_number}: {step.step_name} failed", {
                    "error": str(result)
                })
                return result, False
                
        except Exception as e:
            duration = time.time() - start_time
            log("error", f"❌ Step {step_number}: {step.step_name} failed", {
                "error": str(e),
                "duration_seconds": duration
            })
            return {"error": str(e)}, False
