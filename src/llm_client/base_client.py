"""
Base LLM client class.
Provides a generic interface for all LLM operations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from loguru import logger

from .base_api_config import BaseAPIConfig
from ..prompts.base_prompt import BasePrompt


class BaseLLMClient(ABC):
    """
    Base class for LLM clients.
    
    This class provides a generic interface for LLM operations and ensures
    all clients can handle any prompt type through a single generic method.
    """
    
    def __init__(self, config: BaseAPIConfig):
        """
        Initialize the LLM client.
        
        Args:
            config: API configuration object
        """
        self.config = config
        self.conversation_id: Optional[str] = None
        self.conversation_messages = []
        
        logger.info("🔧 LLM client initialized successfully")
    
    @abstractmethod
    def _make_api_call(self, prompt: BasePrompt, config: BaseAPIConfig) -> Tuple[Any, bool]:
        """
        Make an API call to the LLM service.
        
        Args:
            prompt: The prompt object to send
            config: API configuration for this call
            
        Returns:
            Tuple of (response_data, success_status)
        """
        pass
    
    def execute_prompt(self, prompt: BasePrompt, config: Optional[BaseAPIConfig] = None) -> Tuple[Any, bool]:
        """
        Execute a prompt using the LLM service.
        
        This is the main generic method that all prompt types use.
        The client doesn't need to know what type of prompt it's processing.
        
        Args:
            prompt: Any prompt object that inherits from BasePrompt
            config: Optional API configuration override for this call
            
        Returns:
            Tuple of (response_data, success_status)
        """
        try:
            # Use provided config or default
            api_config = config or self.config
            
            # Log the prompt execution
            logger.info(f"🚀 Executing prompt: {prompt.__class__.__name__}")
            logger.debug(f"📝 Prompt length: {len(str(prompt))} characters")
            logger.debug(f"⚙️ Using model: {api_config.model}")
            
            # Make the API call
            result, success = self._make_api_call(prompt, api_config)
            
            if success:
                logger.info(f"✅ Prompt executed successfully")
                # Add to conversation context if available
                if hasattr(prompt, 'add_to_conversation'):
                    prompt.add_to_conversation(self.conversation_id)
            else:
                logger.error(f"❌ Prompt execution failed")
            
            return result, success
            
        except Exception as e:
            error_msg = f"Prompt execution error: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}, False
    
    def set_conversation_context(self, conversation_id: str) -> None:
        """
        Set the conversation context for this client.
        
        Args:
            conversation_id: The conversation ID to use
        """
        self.conversation_id = conversation_id
        logger.debug(f"💬 Set conversation context: {conversation_id}")
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """
        Add a message to the conversation context.
        
        Args:
            role: The role of the message (user/assistant)
            content: The message content
        """
        if self.conversation_id:
            self.conversation_messages.append({
                "role": role,
                "content": content
            })
            logger.debug(f"💬 Added {role} message to conversation (length: {len(content)})")
    
    def get_conversation_messages(self) -> list:
        """
        Get all conversation messages.
        
        Returns:
            List of conversation messages
        """
        return self.conversation_messages.copy()
    
    def clear_conversation(self) -> None:
        """Clear the conversation context."""
        self.conversation_messages.clear()
        self.conversation_id = None
        logger.debug("💬 Conversation context cleared")
