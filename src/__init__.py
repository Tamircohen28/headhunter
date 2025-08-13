"""
Job4U - AI-Powered Interview Preparation Pipeline

A comprehensive system for automating job interview preparation through:
- Web scraping of job descriptions
- AI-powered analysis and research
- Custom GPT instruction generation
- Multi-agent research task execution
- Comprehensive study material generation
"""

__version__ = "2.0.0"
__author__ = "Job4U Team"
__description__ = "AI-Powered Interview Preparation Pipeline"

from .utils.config import Config
from .utils.logger import setup_logging

__all__ = [
    'Config',
    'setup_logging'
] 