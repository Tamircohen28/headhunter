"""
LLM Client package for job4u application.
Provides abstract interface and implementations for different LLM services.
"""

from .base_client import BaseLLMClient
from .openai_client import OpenAIClient

__all__ = [
    'BaseLLMClient',
    'OpenAIClient'
]
