"""
Job analysis step implementation.
"""

import json
from typing import Any, Dict
from .base_step import BaseStep
from ..prompts import JobAnalysisPrompt
from ..llm_client.openai_client import OpenAIClient
from ..utils.constants import BaseStepEnum, STEP_DETAILS


class JobAnalysisStep(BaseStep):
    """Step 2: Analyze job description using AI."""
    
    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.JOB_ANALYSIS
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.openai_client = OpenAIClient(config)
    
    def _execute(self, job_description: str, job_url: str) -> str:
        """Execute job analysis."""
        prompt = JobAnalysisPrompt(
            job_description=job_description,
            job_url=job_url
        )
        
        result, success = self.openai_client.execute_prompt(prompt)
        if not success:
            raise ValueError(f"Job analysis failed: {result}")
        
        return result
    
    def _process_result(self, result: str) -> Dict[str, Any]:
        """Process and parse job analysis result."""
        try:
            if "```json" in result:
                json_start = result.find("```json") + 7
                json_end = result.find("```", json_start)
                json_content = result[json_start:json_end].strip()
            else:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_content = result[json_start:json_end]
            
            return json.loads(json_content)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse job analysis response: {e}")
