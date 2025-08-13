"""
Job scraping step implementation.
"""

from typing import Any
from .base_step import BaseStep
from ..scraper.web_scraper import WebScraper
from ..utils.constants import BaseStepEnum, STEP_DETAILS


class JobScrapingStep(BaseStep):
    """Step 1: Scrape job description from URL."""
    
    def __init__(self, config: Any, file_manager: Any):
        step_enum = BaseStepEnum.JOB_SCRAPING
        step_details = STEP_DETAILS[step_enum]
        super().__init__(step_enum, step_details, config, file_manager)
        self.scraper = WebScraper(config)
    
    def _execute(self, job_url: str) -> str:
        """Execute job scraping."""
        return self.scraper.scrape_job_page(job_url)
    
    def _process_result(self, result: str) -> str:
        """Process scraped job description."""
        if not result:
            raise ValueError("Failed to scrape job description")
        return result
