"""
Custom GPT instructions step implementation.
"""

from typing import Any, Dict
from .base_step import BaseStep
from ..prompts import CustomGPTInstructionsPrompt
from ..llm_client.openai_client import OpenAIClient
from ..utils.constants import BaseStepEnum, STEP_DETAILS


class CustomGPTInstructionsStep(BaseStep):
    """Step 3: Generate custom GPT instructions."""
    
    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.CUSTOM_GPT_INSTRUCTIONS
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.openai_client = OpenAIClient(config)
    
    def _execute(self, job_analysis: Dict[str, Any]) -> str:
        """Execute custom GPT instructions generation."""
        prompt = CustomGPTInstructionsPrompt(job_analysis=job_analysis)
        
        result, success = self.openai_client.execute_prompt(prompt)
        if not success:
            raise ValueError(f"Custom GPT instructions generation failed: {result}")
        
        return result
    
    def _process_result(self, result: str) -> str:
        """Process custom GPT instructions result."""
        if not result.strip():
            raise ValueError("Generated instructions are empty")
        return result
