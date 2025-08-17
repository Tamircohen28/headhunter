"""
Base step class for all pipeline steps.
Provides shared functionality and enforces a common interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
from enum import Enum

from ..utils.exceptions import Job4UException
from ..utils.constants import BaseStepEnum, StepDetails
from ..utils.logger import log


class StepStatus(Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BaseStep(ABC):
    """
    Base class for all pipeline steps.
    
    Each step must implement:
    - _execute: The actual step logic
    - _process_result: Handle and format the step result
    """
    
    def __init__(self, step_enum: BaseStepEnum, step_details: StepDetails, config: Any, file_manager: Any):
        """
        Initialize the step.
        
        Args:
            step_enum: The step enum value
            step_details: Step details containing index, name, file extension, etc.
            config: Configuration instance
            file_manager: Generic file manager instance
        """
        self.step_enum = step_enum
        self.step_details = step_details
        self.step_number = step_details.index
        self.step_name = step_details.name
        self.config = config
        self.file_manager = file_manager
        self.status = StepStatus.PENDING
        self._current_output_dir: Optional[str] = None
        
        # Get file extension and output type from step details
        self.file_extension = step_details.file_extension
        self.output_type = step_details.output_type
        
        log("info", f"🔧 Step {self.step_number} ({self.step_name}) initialized", {
            "step_enum": step_enum.value,
            "file_extension": self.file_extension,
            "output_type": self.output_type
        })
    
    def execute(self, output_dir: str, **kwargs) -> Tuple[Any, bool]:
        """
        Execute the step with logging, error handling, and file saving.
        
        Args:
            output_dir: Directory to save step output
            **kwargs: Step-specific parameters
            
        Returns:
            Tuple of (result, success_status)
        """
        try:
            log("info", f"🚀 Step {self.step_number}: Starting {self.step_name}")
            self.status = StepStatus.RUNNING
            self._current_output_dir = output_dir
            
            # Execute the step logic
            result = self._execute(**kwargs)
            
            # Process the result
            processed_result = self._process_result(result)
            
            # Save the result to file
            self._save_output(output_dir, processed_result)
            
            self.status = StepStatus.COMPLETED
            log("info", f"✅ Step {self.step_number}: {self.step_name} completed successfully")
            
            return processed_result, True
            
        except Exception as e:
            self.status = StepStatus.FAILED
            error_msg = f"Step {self.step_number} ({self.step_name}) failed: {str(e)}"
            log("error", f"❌ {error_msg}")
            return {"error": error_msg}, False
    
    def _get_step_dir(self) -> str:
        """Compute this step's directory path within the current run output dir."""
        if not self._current_output_dir:
            raise RuntimeError("Step output directory is not set")
        step_dir_name = f"step_{self.step_number:02d}_{self.step_name.lower().replace(' ', '_')}"
        return f"{self._current_output_dir}/{step_dir_name}"
    
    def _save_output(self, output_dir: str, result: Any) -> str:
        """
        Save step output to file.
        
        Args:
            output_dir: Directory to save output
            result: Result to save
            
        Returns:
            Path to saved file
        """
        # Create step directory
        step_dir_name = f"step_{self.step_number:02d}_{self.step_name.lower().replace(' ', '_')}"
        
        # Create step directory directly in the output_dir (don't prepend file manager base)
        step_dir = f"{output_dir}/{step_dir_name}"
        import os
        os.makedirs(step_dir, exist_ok=True)
        
        # Create filename
        filename = f"{self.step_name}{self.file_extension}"
        
        # Save file based on output type
        file_path = self.file_manager.save_file(
            step_dir, filename, result, self.output_type
        )
        
        log("debug", f"💾 Step {self.step_number} output saved to {file_path}")
        return file_path
    
    def _write_additional_file(self, filename: str, content: Any, file_type: str = "text") -> str:
        """Helper for steps to save extra files (e.g., prompt.md, result.md) in the step directory."""
        step_dir = self._get_step_dir()
        return self.file_manager.save_file(step_dir, filename, content, file_type)
    
    @abstractmethod
    def _execute(self, **kwargs) -> Any:
        """
        Execute the step logic.
        
        Args:
            **kwargs: Step-specific parameters
            
        Returns:
            Raw step result
        """
        pass
    
    @abstractmethod
    def _process_result(self, result: Any) -> Any:
        """
        Process and format the step result.
        
        Args:
            result: Raw step result
            
        Returns:
            Processed result
        """
        pass
    
    def get_status(self) -> StepStatus:
        """Get current step status."""
        return self.status
    
    def get_step_info(self) -> Dict[str, Any]:
        """Get step information for logging and state tracking."""
        return {
            "step_enum": self.step_enum.value,
            "step_number": self.step_number,
            "step_name": self.step_name,
            "status": self.status.value,
            "file_extension": self.file_extension,
            "output_type": self.output_type
        }
