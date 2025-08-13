"""
Prompts component for job4u application.
Contains base prompt classes and implementations for different pipeline steps.
"""

from .base_prompt import BasePrompt
from .job_analysis_prompt import JobAnalysisPrompt
from .custom_gpt_instructions_prompt import CustomGPTInstructionsPrompt
from .research_division_prompt import ResearchDivisionPrompt

__all__ = [
    'BasePrompt',
    'JobAnalysisPrompt', 
    'CustomGPTInstructionsPrompt',
    'ResearchDivisionPrompt'
]
