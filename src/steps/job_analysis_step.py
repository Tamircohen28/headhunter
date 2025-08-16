"""
Job metadata extraction step implementation.
This step extracts structured metadata from scraped job content using web search for comprehensive data.
"""

from typing import Any, Dict
from .base_step import BaseStep
from ..prompts import JobMetadataExtractionPrompt, JobMetadataExtractionRequest
from ..llm_client.openai_client import OpenAIClient
from ..utils.constants import BaseStepEnum, STEP_DETAILS


class JobAnalysisStep(BaseStep):
    """Step 2: Extract structured job metadata using AI with web search capabilities."""
    
    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.JOB_ANALYSIS
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.openai_client = OpenAIClient(config)
    
    def _execute(self, job_description: str, job_url: str) -> str:
        """Execute job metadata extraction with web search capabilities."""
        # Create request object
        request = JobMetadataExtractionRequest(
            job_content=job_description,
            job_url=job_url
        )
        
        # Create prompt and construct it
        prompt = JobMetadataExtractionPrompt(request)
        constructed_prompt = prompt.construct()
        
        # Execute with LLM using web search capabilities
        # Note: The LLM will automatically use web search when the prompt requests it
        result, success = self.openai_client.execute_prompt_text(constructed_prompt)
        if not success:
            raise ValueError(f"Job metadata extraction failed: {result}")
        
        return result
    
    def _process_result(self, result: str) -> Dict[str, Any]:
        """Process and parse job metadata extraction result."""
        try:
            # Log the raw result for debugging
            from ..utils.logger import log
            log("info", f"🔍 Processing LLM response ({len(result)} characters)")
            log("debug", f"Raw response preview: {result[:500]}...")
            
            # Create a minimal request object just for parsing (content doesn't matter for parsing)
            # We need to bypass validation since we're only using it for deserialization
            from ..prompts.base_prompt_request import BasePromptRequest
            
            class MinimalRequest(BasePromptRequest):
                def __init__(self):
                    # Initialize with dummy data that passes validation
                    super().__init__(**{
                        'job_content': 'This is dummy content that is long enough to pass validation. It contains information about a software engineering position with requirements for Python, Java, and system design skills. The company is looking for someone with 5+ years of experience in cloud architecture and microservices.',
                        'job_url': 'https://example.com/dummy-job'
                    })
                
                def _validate_required_fields(self) -> None:
                    # Skip validation for parsing purposes
                    pass
            
            # Create prompt and deserialize the response
            prompt = JobMetadataExtractionPrompt(MinimalRequest())
            success, job_metadata = prompt.deserialize(result)
            
            if not success:
                log("error", f"❌ Deserialization failed for response: {result[:1000]}...")
                raise ValueError("Failed to deserialize LLM response")
            
            log("info", f"✅ Successfully deserialized response into JobMetadata object")
            # Convert to dictionary for storage
            return job_metadata.to_dict()
            
        except Exception as e:
            log("error", f"❌ Failed to process job metadata extraction response: {e}")
            log("error", f"❌ Raw response was: {result[:1000]}...")
            raise ValueError(f"Failed to process job metadata extraction response: {e}")
