"""
Base prompt request class for input data.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from .base_prompt_config import BasePromptConfig


class BasePromptRequest(ABC):
    """
    Base class for prompt input data.
    
    This class represents the input data that a prompt needs to function.
    It can optionally use a config class for validation.
    """
    
    def __init__(self, config: Optional[BasePromptConfig] = None, **kwargs):
        """
        Initialize the request with input data.
        
        Args:
            config: Optional configuration object for validation
            **kwargs: Input data
        """
        self._data = kwargs
        self._config = config
        
        if self._config:
            # Use config for validation
            self._config = config
        else:
            # Simple validation - just check required fields
            self._validate_required_fields()
    
    @abstractmethod
    def _validate_required_fields(self) -> None:
        """
        Validate that all required fields are present.
        
        Raises:
            ValueError: If required fields are missing
        """
        pass
    
    def get_data(self) -> Dict[str, Any]:
        """Get the input data."""
        return self._data.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific value from the input data."""
        return self._data.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Get a specific value using bracket notation."""
        return self._data[key]
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the input data."""
        return key in self._data
