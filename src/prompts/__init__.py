"""
Prompts component for job4u application.
Contains base prompt classes and implementations for different pipeline steps.
"""

from .base_prompt import BasePrompt
from .base_prompt_config import BasePromptConfig
from .base_prompt_request import BasePromptRequest
from .job_metadata_extraction_prompt import JobMetadataExtractionPrompt
from .job_metadata_extraction_request import JobMetadataExtractionRequest

# Legacy imports for backward compatibility
from .job_analysis_prompt import JobAnalysisPrompt
from .custom_gpt_instructions_prompt import CustomGPTInstructionsPrompt
from .research_division_prompt import ResearchDivisionPrompt
from .research_planning_prompt import ResearchPlanningPrompt

__all__ = [
    'BasePrompt',
    'BasePromptConfig', 
    'BasePromptRequest',
    'JobMetadataExtractionPrompt',
    'JobMetadataExtractionRequest',
    # Legacy exports
    'JobAnalysisPrompt',
    'CustomGPTInstructionsPrompt',
    'ResearchDivisionPrompt',
    'ResearchPlanningPrompt'
]
