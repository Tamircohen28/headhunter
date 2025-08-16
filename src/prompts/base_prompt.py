"""
Base prompt class for all prompt implementations.
Provides a generic interface for prompt construction and response deserialization.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Generic, TypeVar
from .base_prompt_request import BasePromptRequest

# Generic type for the output of deserialization
T = TypeVar('T')


class BasePrompt(ABC, Generic[T]):
    """
    Base class for all prompt implementations.
    
    This class provides a generic interface for prompt construction and ensures
    all prompts can construct prompts and deserialize responses.
    """
    
    def __init__(self, request: BasePromptRequest):
        """
        Initialize the prompt with a request object.
        
        Args:
            request: The input request containing all necessary data
        """
        self.request = request
    
    @abstractmethod
    def construct(self) -> str:
        """
        Construct the prompt from the input request.
        
        Returns:
            The complete prompt string ready to be sent to the LLM
        """
        pass
    
    @abstractmethod
    def deserialize(self, response: str) -> Tuple[bool, T]:
        """
        Deserialize the LLM response.
        
        Args:
            response: The raw response from the LLM
            
        Returns:
            Tuple of (success: bool, result: T) where T is the expected output type
        """
        pass
    
    def get_request_data(self) -> Dict[str, Any]:
        """Get the data from the request object."""
        return self.request.get_data()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific value from the request data."""
        return self.request.get(key, default)
    
    def __str__(self) -> str:
        """
        String representation of the constructed prompt.
        
        Returns:
            The constructed prompt string
        """
        return self.construct()
