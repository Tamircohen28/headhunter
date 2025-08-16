"""
Base prompt configuration class for input validation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePromptConfig(ABC):
    """
    Base class for prompt input configuration and validation.
    
    Each prompt that needs complex input validation should create
    a subclass of this to handle input data validation.
    """
    
    def __init__(self, **kwargs):
        """Initialize the config with input data."""
        self._data = kwargs
        self.validate()
    
    @abstractmethod
    def validate(self) -> None:
        """
        Validate the input data.
        
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def get_data(self) -> Dict[str, Any]:
        """Get the validated input data."""
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
