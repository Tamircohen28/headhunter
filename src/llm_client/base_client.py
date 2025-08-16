"""
Base LLM client for all language model interactions.
Provides a generic interface for executing prompts.
"""

import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from loguru import logger

from .base_api_config import BaseAPIConfig
from ..prompts.base_prompt import BasePrompt


class BaseLLMClient(ABC):
    """
    Base class for all LLM clients.
    
    Provides a generic interface for executing prompts,
    independent of specific prompt types.
    """
    
    def __init__(self, config: BaseAPIConfig):
        self.config = config
        self.conversation_id: Optional[str] = None
        self.conversation_messages = []
        self._api_call_in_progress = False
        self._last_api_call_time = None
        logger.info("🔧 LLM client initialized successfully")
    
    @abstractmethod
    def _make_api_call(self, prompt: BasePrompt, config: BaseAPIConfig) -> Tuple[Any, bool]:
        """Make the actual API call. Must be implemented by subclasses."""
        pass
    
    def execute_prompt(self, prompt: BasePrompt, config: Optional[BaseAPIConfig] = None) -> Tuple[Any, bool]:
        """
        Execute a prompt with progress indication and error handling.
        
        Args:
            prompt: The prompt to execute
            config: Optional API config override
            
        Returns:
            Tuple of (response_content, success_status)
        """
        if config is None:
            config = self.config
        
        try:
            # Start progress indication
            self._start_progress_indication()
            
            # Log the API call
            logger.info(f"🚀 Executing prompt: {prompt.__class__.__name__}")
            
            # Make the API call
            response_content, success = self._make_api_call(prompt, config)
            
            if success:
                # Add to conversation history
                self.add_to_conversation("user", str(prompt))
                self.add_to_conversation("assistant", response_content)
                
                logger.info("✅ Prompt executed successfully")
                return response_content, True
            else:
                logger.error(f"❌ Prompt execution failed: {response_content}")
                return response_content, False
                
        except Exception as e:
            error_msg = f"Prompt execution error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}, False
        finally:
            # Stop progress indication
            self._stop_progress_indication()
    
    def execute_prompt_text(self, prompt_text: str, config: Optional[BaseAPIConfig] = None) -> Tuple[Any, bool]:
        """
        Execute raw prompt text with progress indication and error handling.
        
        Args:
            prompt_text: The raw prompt text to execute
            config: Optional API config override
            
        Returns:
            Tuple of (response_content, success_status)
        """
        if config is None:
            config = self.config
        
        try:
            # Start progress indication
            self._start_progress_indication()
            
            # Log the API call
            logger.info(f"🚀 Executing prompt text ({len(prompt_text)} characters)")
            
            # Create a simple prompt wrapper for the API call
            class TextPrompt:
                def __init__(self, text: str):
                    self.text = text
                    self.__class__.__name__ = "TextPrompt"
                
                def __str__(self):
                    return self.text
            
            text_prompt = TextPrompt(prompt_text)
            
            # Make the API call
            response_content, success = self._make_api_call(text_prompt, config)
            
            if success:
                # Add to conversation history
                self.add_to_conversation("user", prompt_text)
                self.add_to_conversation("assistant", response_content)
                
                logger.info("✅ Prompt text executed successfully")
                return response_content, True
            else:
                logger.error(f"❌ Prompt text execution failed: {response_content}")
                return response_content, False
                
        except Exception as e:
            error_msg = f"Prompt text execution error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}, False
        finally:
            # Stop progress indication
            self._stop_progress_indication()
    
    def _start_progress_indication(self):
        """Start progress indication for API calls."""
        self._api_call_in_progress = True
        self._last_api_call_time = time.time()
        
        # Start progress thread
        self._progress_thread = threading.Thread(target=self._show_progress, daemon=True)
        self._progress_thread.start()
    
    def _stop_progress_indication(self):
        """Stop progress indication."""
        self._api_call_in_progress = False
    
    def _show_progress(self):
        """Show progress dots while waiting for API response."""
        dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        
        while self._api_call_in_progress:
            elapsed = time.time() - self._last_api_call_time
            dot = dots[i % len(dots)]
            
            # Show progress every 2 seconds
            if int(elapsed) % 2 == 0:
                logger.info(f"⏳ Waiting for API response... {dot} (elapsed: {int(elapsed)}s)")
            
            time.sleep(1)
            i += 1
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
    
    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.conversation_messages.copy()
    
    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_messages.clear()
        self.conversation_id = None
    
    def set_conversation_id(self, conversation_id: str) -> None:
        """Set the conversation ID for tracking."""
        self.conversation_id = conversation_id
    
    def get_conversation_id(self) -> Optional[str]:
        """Get the current conversation ID."""
        return self.conversation_id
    
    def is_api_call_in_progress(self) -> bool:
        """Check if an API call is currently in progress."""
        return self._api_call_in_progress
    
    def get_last_api_call_duration(self) -> Optional[float]:
        """Get the duration of the last API call."""
        if self._last_api_call_time and not self._api_call_in_progress:
            return time.time() - self._last_api_call_time
        return None
