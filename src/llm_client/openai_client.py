"""
OpenAI client implementation.
Handles all OpenAI API interactions using the generic prompt system.
"""

import json
from typing import Dict, Any, Tuple, Optional
from loguru import logger
from openai import OpenAI

from .base_client import BaseLLMClient
from .base_api_config import BaseAPIConfig
from ..utils.config import Config
from ..utils.logger import log_api_call, log_api_response
from ..utils.exceptions import LLMError


class OpenAIClient(BaseLLMClient):
    """
    OpenAI client implementation.
    
    This client is completely generic and doesn't know about specific prompt types.
    It only handles OpenAI API interactions and uses the generic prompt system.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the OpenAI client.
        
        Args:
            config: Application configuration instance
        """
        # Create API config from application config
        api_config = BaseAPIConfig(
            api_key=config.openai_api_key,
            model=config.openai_model_browsing,  # Default model
            temperature=config.openai_temperature,
            max_tokens=config.openai_max_tokens,
            timeout=config.openai_timeout
        )
        
        # Initialize base client
        super().__init__(api_config)
        
        # Store application config for creating different API configs
        self.app_config = config
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_config.api_key)
        
        logger.info("🔧 OpenAI client initialized successfully")
    
    def _make_api_call(self, prompt: 'BasePrompt', config: BaseAPIConfig) -> Tuple[Any, bool]:
        """
        Make an API call to OpenAI.
        
        Args:
            prompt: The prompt object to send
            config: API configuration for this call
            
        Returns:
            Tuple of (response_data, success_status)
        """
        try:
            # Log API call
            log_api_call(
                f"OpenAI API Call - {prompt.__class__.__name__}",
                config.model,
                len(str(prompt)),
                conversation_id=self.conversation_id
            )
            
            # Make API call
            response = self.client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "user", "content": str(prompt)}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            # Log API response
            response_content = response.choices[0].message.content
            response_length = len(response_content) if response_content else 0
            response_preview = response_content[:100] if response_content else "No content"
            
            log_api_response(
                f"OpenAI API Response - {prompt.__class__.__name__}",
                config.model,
                response.usage,
                response.choices[0].finish_reason,
                response_length,
                response_preview
            )
            
            # Handle response
            if not response_content:
                if response.choices[0].finish_reason == "tool_calls":
                    logger.warning("⚠️ API response has tool_calls but no content")
                    return {"error": "API response has tool_calls but no content"}, False
                else:
                    logger.error("❌ API response has no content")
                    return {"error": "API response has no content"}, False
            
            # Add to conversation context
            self.add_to_conversation("user", str(prompt))
            self.add_to_conversation("assistant", response_content)
            
            return response_content, True
            
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}, False
    
    def create_api_config(self, model: str, **kwargs) -> BaseAPIConfig:
        """
        Create a new API config for specific calls.
        
        Args:
            model: The model to use
            **kwargs: Additional configuration overrides
            
        Returns:
            New API configuration object
        """
        config = BaseAPIConfig(
            api_key=self.app_config.openai_api_key,
            model=model,
            temperature=self.app_config.openai_temperature,
            max_tokens=self.app_config.openai_max_tokens,
            timeout=self.app_config.openai_timeout
        )
        
        # Apply any overrides
        if kwargs:
            config.update(**kwargs)
        
        return config
    
    def start_deep_research(self, prompt: str, metadata: Dict[str, Any]) -> Tuple[str, bool]:
        """
        Start a deep research task using OpenAI Responses API.
        
        Args:
            prompt: The research prompt to execute
            metadata: Additional metadata for the research task
            
        Returns:
            Tuple of (response_id, success_status)
        """
        try:
            logger.info("🚀 Starting Deep Research task")
            
            # Create API config for deep research
            config = self.create_api_config(
                model=self.app_config.openai_model_deep_research,
                temperature=0.1  # Lower temperature for research tasks
            )
            
            # Make the API call
            response = self.client.beta.threads.runs.create(
                thread_id=metadata.get('thread_id'),
                assistant_id=metadata.get('assistant_id'),
                instructions=prompt
            )
            
            response_id = response.id
            logger.info(f"✅ Deep Research started with response_id: {response_id}")
            
            return response_id, True
            
        except Exception as e:
            error_msg = f"Failed to start deep research: {str(e)}"
            logger.error(error_msg)
            return "", False
    
    def poll_research_status(self, response_id: str) -> Tuple[Dict[str, Any], bool]:
        """
        Poll the status of a deep research task.
        
        Args:
            response_id: The ID of the research task
            
        Returns:
            Tuple of (status_info, success_status)
        """
        try:
            # This would need to be implemented based on the specific API being used
            # For now, return a placeholder
            logger.debug(f"Polling research status for: {response_id}")
            return {"status": "unknown"}, True
            
        except Exception as e:
            error_msg = f"Failed to poll research status: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}, False
    
    def get_research_result(self, response_id: str) -> Tuple[Dict[str, Any], bool]:
        """
        Get the final result of a completed research task.
        
        Args:
            response_id: The ID of the research task
            
        Returns:
            Tuple of (research_result, success_status)
        """
        try:
            # This would need to be implemented based on the specific API being used
            # For now, return a placeholder
            logger.debug(f"Getting research result for: {response_id}")
            return {"result": "placeholder"}, True
            
        except Exception as e:
            error_msg = f"Failed to get research result: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}, False
