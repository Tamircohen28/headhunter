"""
Configuration management for the job4u application.
Provides a singleton pattern for accessing configuration values.
"""

import os
from pathlib import Path
from typing import Optional, Any
from .constants import *
from .exceptions import ConfigurationError

# Try to import python-dotenv, fallback to manual loading if not available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Config:
    """
    Singleton configuration class for job4u application.
    Loads configuration from .env file and environment variables with sensible defaults.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_environment()
            self._initialized = True
    
    def _load_environment(self) -> None:
        """Load configuration from .env file and environment variables."""
        try:
            # Load .env file if available
            self._load_dotenv_file()
            
            # Required configuration
            self.openai_api_key = self._get_required_env("OPENAI_API_KEY")
            self.test_job_url = self._get_required_env("TEST_JOB_URL")
            
            # OpenAI Model Configuration
            self.openai_model_browsing = self._get_env("OPENAI_MODEL_BROWSING", DEFAULT_OPENAI_MODEL_BROWSING)
            self.openai_model_writing = self._get_env("OPENAI_MODEL_WRITING", DEFAULT_OPENAI_MODEL_WRITING)
            
            # OpenAI API Configuration
            self.openai_temperature = float(self._get_env("OPENAI_TEMPERATURE", DEFAULT_OPENAI_TEMPERATURE))
            self.openai_max_tokens = int(self._get_env("OPENAI_MAX_TOKENS", DEFAULT_OPENAI_MAX_TOKENS))
            self.openai_timeout = int(self._get_env("OPENAI_TIMEOUT", DEFAULT_OPENAI_TIMEOUT))
            
            # Application Configuration
            self.output_dir = self._get_env("OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
            self.log_level = self._get_env("LOG_LEVEL", DEFAULT_LOG_LEVEL)
            self.log_file = self._get_env("LOG_FILE", DEFAULT_LOG_FILE)
            self.log_dir = self._get_env("LOG_DIR", "./logs")
            
            # Study Configuration
            self.study_weeks = int(self._get_env("STUDY_WEEKS", DEFAULT_STUDY_WEEKS))
            self.hours_per_week = int(self._get_env("HOURS_PER_WEEK", DEFAULT_HOURS_PER_WEEK))
            
            # Scraper Configuration
            self.scraper_timeout = int(self._get_env("SCRAPER_TIMEOUT", DEFAULT_SCRAPER_TIMEOUT))
            self.scraper_max_retries = int(self._get_env("SCRAPER_MAX_RETRIES", DEFAULT_SCRAPER_MAX_RETRIES))
            self.scraper_wait_time = int(self._get_env("SCRAPER_WAIT_TIME", 10))
            self.scraper_scroll_pause = int(self._get_env("SCRAPER_SCROLL_PAUSE", 2))
            
            # Research Configuration
            self.max_topics_per_agent = int(self._get_env("MAX_TOPICS_PER_AGENT", DEFAULT_MAX_TOPICS_PER_AGENT))
            self.research_timeout = int(self._get_env("RESEARCH_TIMEOUT", DEFAULT_RESEARCH_TIMEOUT))
            self.poll_interval = int(self._get_env("POLL_INTERVAL", DEFAULT_POLL_INTERVAL))
            self.max_research_time = int(self._get_env("MAX_RESEARCH_TIME", DEFAULT_RESEARCH_TIMEOUT))
            self.max_questions_per_task = int(self._get_env("MAX_QUESTIONS_PER_TASK", 3))
            
            # Deep Research Configuration
            self.deep_research_model = self._get_env("OPENAI_DEEP_RESEARCH_MODEL", "o4-mini-deep-research")
            self.deep_research_max_tokens = int(self._get_env("OPENAI_DEEP_RESEARCH_MAX_TOKENS", DEFAULT_OPENAI_MAX_TOKENS))
            self.deep_research_tools = [{"type": "web_search_preview"}]
            
            self._validate_configuration()

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def _load_dotenv_file(self) -> None:
        """Load environment variables from .env file."""
        try:
            if DOTENV_AVAILABLE:
                # Use python-dotenv to load .env file with override=True to force override existing values
                load_dotenv(override=True)
                print(f"🔧 Loaded environment from .env file (overriding existing values)")
            else:
                print("⚠️ python-dotenv not available. Using system environment variables only.")
                
        except Exception as e:
            print(f"⚠️ Warning: Failed to load .env file: {e}")
    
    def _load_dotenv_manual(self, env_file: Path) -> None:
        """This method is no longer used - using python-dotenv instead."""
        pass
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable."""
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(f"Required environment variable {key} is not set")
        return value
    
    def _get_env(self, key: str, default: Any) -> Any:
        """Get an environment variable with a default value."""
        return os.getenv(key, default)
    
    def _validate_configuration(self) -> None:
        """Validate configuration values."""
        if self.openai_temperature < 0 or self.openai_temperature > 2:
            raise ConfigurationError("OPENAI_TEMPERATURE must be between 0 and 2")
        
        if self.openai_max_tokens < 1 or self.openai_max_tokens > 100000:
            raise ConfigurationError("OPENAI_MAX_TOKENS must be between 1 and 100000")
        
        if self.openai_timeout < 1:
            raise ConfigurationError("OPENAI_TIMEOUT must be greater than 0")
        
        if self.max_topics_per_agent < 1 or self.max_topics_per_agent > 10:
            raise ConfigurationError("MAX_TOPICS_PER_AGENT must be between 1 and 10")
        
        if self.study_weeks < 1 or self.study_weeks > 52:
            raise ConfigurationError("STUDY_WEEKS must be between 1 and 52")
        
        if self.hours_per_week < 1 or self.hours_per_week > 168:
            raise ConfigurationError("HOURS_PER_WEEK must be between 1 and 168")
        
        if self.scraper_timeout < 1:
            raise ConfigurationError("SCRAPER_TIMEOUT must be greater than 0")
        
        if self.scraper_max_retries < 1:
            raise ConfigurationError("SCRAPER_MAX_RETRIES must be at least 1")
    
    def get_openai_config(self) -> dict:
        """Get OpenAI API configuration as a dictionary."""
        return {
            "api_key": self.openai_api_key,
            "model_browsing": self.openai_model_browsing,
            "model_writing": self.openai_model_writing,
            "temperature": self.openai_temperature,
            "max_tokens": self.openai_max_tokens,
            "timeout": self.openai_timeout
        }
    
    def get_deep_research_config(self) -> dict:
        """Get Deep Research configuration as a dictionary."""
        return {
            "model": self.deep_research_model,
            "tools": self.deep_research_tools,
            "max_tokens": self.deep_research_max_tokens,
            "background": True
        }
    
    def get_scraping_config(self) -> dict:
        """Get scraping configuration as a dictionary."""
        return {
            "timeout": self.scraper_timeout,
            "max_retries": self.scraper_max_retries,
            "wait_time": self.scraper_wait_time,
            "scroll_pause": self.scraper_scroll_pause
        }
    
    def get_research_config(self) -> dict:
        """Get research configuration as a dictionary."""
        return {
            "max_research_time": self.max_research_time,
            "poll_interval": self.poll_interval,
            "max_questions_per_task": self.max_questions_per_task,
            "max_topics_per_agent": self.max_topics_per_agent
        }
    
    def get_study_plan_config(self) -> dict:
        """Get study plan configuration as a dictionary."""
        return {
            "weeks": self.study_weeks,
            "hours_per_week": self.hours_per_week
        }
    
    def get_output_config(self) -> dict:
        """Get output and logging configuration as a dictionary."""
        return {
            "output_dir": self.output_dir,
            "log_dir": self.log_dir,
            "log_file": self.log_file,
            "log_level": self.log_level
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        return f"Config(openai_model={self.openai_model_browsing}, temperature={self.openai_temperature}, max_tokens={self.openai_max_tokens})"
    
    def __repr__(self) -> str:
        """Detailed string representation of configuration."""
        return f"Config(openai_api_key={'*' * 8 if self.openai_api_key else None}, test_job_url={self.test_job_url}, openai_model_browsing={self.openai_model_browsing}, openai_temperature={self.openai_temperature}, openai_max_tokens={self.openai_max_tokens}, openai_timeout={self.openai_timeout}, max_research_time={self.max_research_time}, poll_interval={self.poll_interval}, max_topics_per_agent={self.max_topics_per_agent}, study_weeks={self.study_weeks}, hours_per_week={self.hours_per_week}, scraper_timeout={self.scraper_timeout}, scraper_max_retries={self.scraper_max_retries}, output_dir={self.output_dir}, log_dir={self.log_dir}, log_file={self.log_file}, log_level={self.log_level})"
