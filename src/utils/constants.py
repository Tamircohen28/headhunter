"""
Constants for the job4u application.
"""

# Application Version
APP_VERSION = "1.1.0"

from enum import Enum
from dataclasses import dataclass
from typing import Type, Any


class BaseStepEnum(Enum):
    """Enum for all pipeline steps."""
    JOB_SCRAPING = "job_scraping"
    JOB_ANALYSIS = "job_analysis"
    # RESEARCH_PROMPT = "research_prompt"  # Commented out - not needed for first 2 steps


@dataclass
class StepDetails:
    """Details for each pipeline step."""
    index: int
    name: str
    step_class: Type[Any]
    file_extension: str
    output_type: str


# Step Details Mapping - step_class will be set dynamically
STEP_DETAILS = {
    BaseStepEnum.JOB_SCRAPING: StepDetails(
        index=1,
        name="Job Description Scraping",
        step_class=None,  # Will be set dynamically
        file_extension=".txt",
        output_type="text"
    ),
    BaseStepEnum.JOB_ANALYSIS: StepDetails(
        index=2,
        name="Job Metadata Extraction with Web Research",  # Updated to reflect web search capabilities
        step_class=None,  # Will be set dynamically
        file_extension=".json",
        output_type="json"
    )
    # BaseStepEnum.RESEARCH_PROMPT: StepDetails(  # Commented out - not needed for first 2 steps
    #     index=3,
    #     name="Construct Research Prompt & Run Deep Research",
    #     step_class=None,  # Will be set dynamically
    #     file_extension=".md",
    #     output_type="markdown"
    # )
}


def set_step_classes():
    """Set the step classes dynamically to avoid circular imports."""
    from ..steps.job_scraping_step import JobScrapingStep
    from ..steps.job_analysis_step import JobAnalysisStep
    # from ..steps.research_prompt_step import ResearchPromptStep  # Commented out - not needed for first 2 steps
    
    STEP_DETAILS[BaseStepEnum.JOB_SCRAPING].step_class = JobScrapingStep
    STEP_DETAILS[BaseStepEnum.JOB_ANALYSIS].step_class = JobAnalysisStep
    # STEP_DETAILS[BaseStepEnum.RESEARCH_PROMPT].step_class = ResearchPromptStep  # Commented out


# Legacy mappings for backward compatibility (can be removed later)
STEP_MAPPING = {details.index: enum_value.value for enum_value, details in STEP_DETAILS.items()}
STEP_NAMES = {details.index: details.name for enum_value, details in STEP_DETAILS.items()}
STEP_FILE_EXTENSIONS = {details.index: details.file_extension for enum_value, details in STEP_DETAILS.items()}
STEP_OUTPUT_TYPES = {details.index: details.output_type for enum_value, details in STEP_DETAILS.items()}

# Step Classes Mapping
STEP_CLASSES = {
    1: "JobScrapingStep",
    2: "JobMetadataExtractionWithWebResearchStep"
    # 3: "ResearchPromptStep"  # Commented out - not needed for first 2 steps
}

# Step File Extensions
STEP_FILE_EXTENSIONS = {
    1: ".txt",
    2: ".json"
    # 3: ".md"  # Commented out - not needed for first 2 steps
}

# Step Output Types
STEP_OUTPUT_TYPES = {
    1: "text",
    2: "json"
    # 3: "markdown"  # Commented out - not needed for first 2 steps
}

# Logging Configuration
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Default Configuration Values
DEFAULT_OPENAI_MODEL_BROWSING = "gpt-4o-mini"  # Supports web search and browsing
DEFAULT_OPENAI_MODEL_WRITING = "gpt-4o-mini"
DEFAULT_OPENAI_TEMPERATURE = 0.5
DEFAULT_OPENAI_MAX_TOKENS = 8000  # Increased for comprehensive metadata extraction
DEFAULT_OPENAI_TIMEOUT = 120  # Increased timeout for web search operations

DEFAULT_OUTPUT_DIR = f"./output_{APP_VERSION}"
DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FILE = "logs/job4u_{time:YYYY-MM-DD_HH-mm-ss}.log"

DEFAULT_STUDY_WEEKS = 4
DEFAULT_HOURS_PER_WEEK = 10

DEFAULT_SCRAPER_TIMEOUT = 30
DEFAULT_SCRAPER_MAX_RETRIES = 3

# Research Configuration
DEFAULT_MAX_TOPICS_PER_AGENT = 4
DEFAULT_RESEARCH_TIMEOUT = 300  # 5 minutes
DEFAULT_POLL_INTERVAL = 10  # 10 seconds

# HTML Tag Constants
MAIN_TAG = "main"
BODY_TAG = "body"
DIV_TAG = "div"
SCRIPT_TAG = "script"
STYLE_TAG = "style"
NAV_TAG = "nav"
HEADER_TAG = "header"
FOOTER_TAG = "footer"

# Validation Constants
MIN_JOB_DESCRIPTION_LENGTH = 100
MAX_JOB_DESCRIPTION_LENGTH = 50000
MIN_TOPICS_COUNT = 1
MAX_TOPICS_COUNT = 20
MIN_AGENTS_COUNT = 1
MAX_AGENTS_COUNT = 10
