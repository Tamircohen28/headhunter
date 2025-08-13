"""
Base API configuration class for LLM clients.
Contains only API-related configuration, not business logic.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class BaseAPIConfig:
    """Base configuration for API calls."""
    
    # API endpoint and authentication
    api_key: str
    model: str
    
    # Optional configuration with defaults
    base_url: Optional[str] = None
    temperature: float = 0.5
    max_tokens: int = 5000
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay
        }
    
    def update(self, **kwargs) -> None:
        """Update configuration values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return getattr(self, key, default)
