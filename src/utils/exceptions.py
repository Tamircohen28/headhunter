"""
Custom exceptions for the job4u application.
Provides specific exception types for different error scenarios.
"""

from typing import Optional, Any


class Job4UException(Exception):
    """Base exception for all job4u application errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class ConfigurationError(Job4UException):
    """Raised when there's a configuration error."""
    pass


class ValidationError(Job4UException):
    """Raised when data validation fails."""
    pass


class ScrapingError(Job4UException):
    """Raised when web scraping fails."""
    pass


class LLMError(Job4UException):
    """Raised when LLM API calls fail."""
    pass


class StorageError(Job4UException):
    """Raised when storage operations fail."""
    pass


class ConversationError(Job4UException):
    """Raised when conversation management fails."""
    pass


class TaskExecutionError(Job4UException):
    """Raised when task execution fails."""
    pass


class PromptGenerationError(Job4UException):
    """Raised when prompt generation fails."""
    pass


class ResearchError(Job4UException):
    """Raised when research operations fail."""
    pass


class TimeoutError(Job4UException):
    """Raised when operations timeout."""
    pass


class APIError(Job4UException):
    """Raised when external API calls fail."""
    pass


class FileOperationError(Job4UException):
    """Raised when file operations fail."""
    pass


class StateError(Job4UException):
    """Raised when state management fails."""
    pass
