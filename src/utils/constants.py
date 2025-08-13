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
    CUSTOM_GPT_INSTRUCTIONS = "custom_gpt_instructions"
    RESEARCH_DIVISION = "research_division"


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
        name="Job Description Analysis",
        step_class=None,  # Will be set dynamically
        file_extension=".json",
        output_type="json"
    ),
    BaseStepEnum.CUSTOM_GPT_INSTRUCTIONS: StepDetails(
        index=3,
        name="Custom GPT Instructions",
        step_class=None,  # Will be set dynamically
        file_extension=".md",
        output_type="markdown"
    ),
    BaseStepEnum.RESEARCH_DIVISION: StepDetails(
        index=4,
        name="Research Topic Division",
        step_class=None,  # Will be set dynamically
        file_extension=".md",
        output_type="markdown"
    )
}


def set_step_classes():
    """Set the step classes dynamically to avoid circular imports."""
    from ..steps.job_scraping_step import JobScrapingStep
    from ..steps.job_analysis_step import JobAnalysisStep
    from ..steps.custom_gpt_instructions_step import CustomGPTInstructionsStep
    from ..steps.research_division_step import ResearchDivisionStep
    
    STEP_DETAILS[BaseStepEnum.JOB_SCRAPING].step_class = JobScrapingStep
    STEP_DETAILS[BaseStepEnum.JOB_ANALYSIS].step_class = JobAnalysisStep
    STEP_DETAILS[BaseStepEnum.CUSTOM_GPT_INSTRUCTIONS].step_class = CustomGPTInstructionsStep
    STEP_DETAILS[BaseStepEnum.RESEARCH_DIVISION].step_class = ResearchDivisionStep


# Legacy mappings for backward compatibility (can be removed later)
STEP_MAPPING = {details.index: enum_value.value for enum_value, details in STEP_DETAILS.items()}
STEP_NAMES = {details.index: details.name for enum_value, details in STEP_DETAILS.items()}
STEP_FILE_EXTENSIONS = {details.index: details.file_extension for enum_value, details in STEP_DETAILS.items()}
STEP_OUTPUT_TYPES = {details.index: details.output_type for enum_value, details in STEP_DETAILS.items()}

# Step Classes Mapping
STEP_CLASSES = {
    1: "JobScrapingStep",
    2: "JobAnalysisStep",
    3: "CustomGPTInstructionsStep",
    4: "ResearchDivisionStep"
}

# Step File Extensions
STEP_FILE_EXTENSIONS = {
    1: ".txt",      # Job scraping - raw text
    2: ".json",     # Job analysis - structured data
    3: ".md",       # Custom GPT instructions - markdown
    4: ".md"        # Research division - markdown
}

# Step Output Types
STEP_OUTPUT_TYPES = {
    1: "text",
    2: "json", 
    3: "markdown",
    4: "markdown"
}

# Logging Configuration
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Default Configuration Values
DEFAULT_OPENAI_MODEL_BROWSING = "gpt-4o-mini"
DEFAULT_OPENAI_MODEL_WRITING = "gpt-4o-mini"
DEFAULT_OPENAI_TEMPERATURE = 0.5
DEFAULT_OPENAI_MAX_TOKENS = 5000
DEFAULT_OPENAI_TIMEOUT = 60

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
