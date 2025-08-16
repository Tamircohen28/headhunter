"""
Job metadata extraction prompt request class.
"""

from typing import Dict, Any
from .base_prompt_request import BasePromptRequest


class JobMetadataExtractionRequest(BasePromptRequest):
    """
    Request class for job metadata extraction prompts.
    
    Contains the input data needed for job metadata extraction.
    """
    
    def __init__(self, job_content: str, job_url: str):
        """
        Initialize the request.
        
        Args:
            job_content: The scraped job description content
            job_url: The URL of the job posting
        """
        super().__init__(job_content=job_content, job_url=job_url)
    
    def _validate_required_fields(self) -> None:
        """Validate that all required fields are present."""
        if not self._data.get('job_content'):
            raise ValueError("Missing required field: job_content")
        if not self._data.get('job_url'):
            raise ValueError("Missing required field: job_url")
        
        # Additional validation
        if len(self._data['job_content'].strip()) < 100:
            raise ValueError("Job content must be at least 100 characters long")
        
        if not self._data['job_url'].startswith(('http://', 'https://')):
            raise ValueError("Job URL must be a valid HTTP/HTTPS URL")
    
    @property
    def job_content(self) -> str:
        """Get the job content."""
        return self._data['job_content']
    
    @property
    def job_url(self) -> str:
        """Get the job URL."""
        return self._data['job_url']
