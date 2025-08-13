"""
Base prompt class for all prompt implementations.
Provides a generic interface for prompt generation and rendering.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BasePrompt(ABC):
    """
    Base class for all prompt implementations.
    
    This class provides a generic interface for prompt generation and ensures
    all prompts can be converted to strings for API calls.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the prompt with variables.
        
        Args:
            **kwargs: Variables needed for prompt generation
        """
        self.variables = kwargs
        self._validate_variables()
    
    @abstractmethod
    def _validate_variables(self) -> None:
        """
        Validate that all required variables are present.
        
        Raises:
            ValueError: If required variables are missing
        """
        pass
    
    @abstractmethod
    def _generate_template(self) -> str:
        """
        Generate the prompt template string.
        
        Returns:
            The prompt template as a string
        """
        pass
    
    def render(self) -> str:
        """
        Render the prompt with the current variables.
        
        Returns:
            The rendered prompt string ready for API calls
        """
        template = self._generate_template()
        return template.format(**self.variables)
    
    def __str__(self) -> str:
        """
        String representation of the rendered prompt.
        
        Returns:
            The rendered prompt string
        """
        return self.render()
    
    def update_variables(self, **kwargs) -> None:
        """
        Update prompt variables.
        
        Args:
            **kwargs: New variables to update
        """
        self.variables.update(kwargs)
        self._validate_variables()
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Get a variable value.
        
        Args:
            key: Variable name
            default: Default value if key not found
            
        Returns:
            Variable value or default
        """
        return self.variables.get(key, default)
    
    def has_variable(self, key: str) -> bool:
        """
        Check if a variable exists.
        
        Args:
            key: Variable name
            
        Returns:
            True if variable exists, False otherwise
        """
        return key in self.variables
