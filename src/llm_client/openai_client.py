"""
OpenAI client implementation.
Handles all OpenAI API interactions with progress indication.
"""

import json
import time
from typing import Dict, Any, Tuple, Optional
from loguru import logger
from openai import OpenAI

from .base_client import BaseLLMClient
from .base_api_config import BaseAPIConfig
from ..utils.config import Config
from ..utils.exceptions import LLMError
from ..utils.logger import log_api_call, log_api_response


class OpenAIClient(BaseLLMClient):
    """OpenAI client for executing prompts and managing API calls."""
    
    def __init__(self, config: Config):
        api_config = BaseAPIConfig(
            api_key=config.openai_api_key,
            model=config.openai_model_browsing,
            temperature=config.openai_temperature,
            max_tokens=config.openai_max_tokens,
            timeout=config.openai_timeout
        )
        super().__init__(api_config)
        self.app_config = config
        self.client = OpenAI(api_key=api_config.api_key)
        logger.info("🔧 OpenAI client initialized successfully")
    
    def _make_api_call(self, prompt: 'BasePrompt', config: BaseAPIConfig) -> Tuple[Any, bool]:
        """
        Make an API call to OpenAI with progress indication.
        
        Args:
            prompt: The prompt to execute
            config: API configuration for this call
            
        Returns:
            Tuple of (response_content, success_status)
        """
        try:
            # Log API call details
            log_api_call(
                f"OpenAI API Call - {prompt.__class__.__name__}",
                config.model,
                len(str(prompt)),
                conversation_id=self.conversation_id
            )
            
            # Prepare messages
            messages = [{"role": "user", "content": str(prompt)}]
            
            # Make the API call
            logger.info(f"📡 Sending request to OpenAI API (model: {config.model})")
            
            response = self.client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                timeout=config.timeout
            )
            
            # Extract response content
            if response.choices and len(response.choices) > 0:
                response_content = response.choices[0].message.content
                
                # Log successful response
                log_api_response(
                    f"OpenAI API Response - {prompt.__class__.__name__}",
                    config.model,
                    len(response_content),
                    conversation_id=self.conversation_id
                )
                
                logger.info(f"✅ Received response from OpenAI API ({len(response_content)} characters)")
                return response_content, True
            else:
                error_msg = "No response choices received from OpenAI API"
                logger.error(f"❌ {error_msg}")
                return {"error": error_msg}, False
                
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}, False
    
    def create_api_config(self, model: str, **kwargs) -> BaseAPIConfig:
        """
        Create a new API configuration with overrides.
        
        Args:
            model: Model to use
            **kwargs: Additional configuration overrides
            
        Returns:
            New BaseAPIConfig instance
        """
        base_config = {
            "api_key": self.config.api_key,
            "model": model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout
        }
        
        # Apply overrides
        base_config.update(kwargs)
        
        return BaseAPIConfig(**base_config)
    
    def start_deep_research(self, prompt_text: str) -> Tuple[str, bool]:
        """
        Start a deep research session using OpenAI Responses API in background mode.
        Uses model from Config.deep_research_model (default: o4-mini-deep-research).
        Returns (response_id, success).
        """
        try:
            model = self.app_config.deep_research_model
            max_tokens = self.app_config.deep_research_max_tokens
            tools = self.app_config.deep_research_tools
            
            logger.info(f"📡 Starting deep research (model: {model}) in background mode")
            
            response = self.client.responses.create(
                model=model,
                input=prompt_text,
                max_output_tokens=max_tokens,
                background=True,
                modalities=["text"],
                tools=tools
            )
            
            response_id = response.id
            logger.info(f"✅ Deep research started (id: {response_id})")
            return response_id, True
        except Exception as e:
            logger.error(f"❌ Failed to start deep research: {e}")
            return {"error": str(e)}, False
    
    def poll_research_status(self, response_id: str, poll_interval: int = 10) -> Tuple[Dict[str, Any], bool]:
        """
        Poll the status of a deep research session every poll_interval seconds.
        Returns (final_response_obj, success) once terminal state reached.
        """
        try:
            logger.info(f"🔎 Polling research status for id: {response_id}")
            while True:
                status_obj = self.client.responses.retrieve(response_id)
                status = getattr(status_obj, 'status', None) or status_obj.get('status') if isinstance(status_obj, dict) else None
                
                if status in ["completed", "succeeded"]:
                    logger.info("✅ Research completed")
                    return status_obj, True
                if status in ["failed", "errored", "cancelled", "expired"]:
                    logger.error(f"❌ Research ended with status: {status}")
                    return status_obj, False
                
                logger.info(f"⏳ Status: {status}. Polling again in {poll_interval}s...")
                time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"❌ Polling failed: {e}")
            return {"error": str(e)}, False
    
    def get_research_result_markdown(self, response_obj: Any) -> Tuple[str, bool]:
        """
        Extract full text content from a completed deep research response.
        Returns (markdown_text, success).
        """
        try:
            # The Responses API may return output_text; fallback to choices/content
            # Handle both SDK objects and dicts
            text = None
            if hasattr(response_obj, 'output_text') and response_obj.output_text:
                text = response_obj.output_text
            elif isinstance(response_obj, dict) and response_obj.get('output_text'):
                text = response_obj['output_text']
            
            if not text:
                # Try messages or content
                try:
                    if hasattr(response_obj, 'output'):
                        # Newer SDK may expose output as list of content parts
                        parts = getattr(response_obj, 'output', None)
                        if parts:
                            text = "\n\n".join([getattr(p, 'content', '') or str(p) for p in parts])
                except Exception:
                    pass
            
            if not text:
                # Fallback: stringify object
                text = str(response_obj)
            
            return text, True
        except Exception as e:
            return f"Error extracting research result: {e}", False
