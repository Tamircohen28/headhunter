"""
Web scraper component for extracting job descriptions.
Uses multiple fallback methods for robust content extraction.
"""

import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from loguru import logger
from typing import Optional

from ..utils.config import Config
from ..utils.constants import *
from ..utils.exceptions import ScrapingError
from ..utils.helpers import clean_html_content, is_valid_url


class WebScraper:
    """
    Web scraper for extracting job descriptions from web pages.
    Uses multiple extraction methods with fallbacks for robustness.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the web scraper.
        
        Args:
            config: Configuration instance
        """
        self.config = config
        self.scraping_config = config.get_scraping_config()
        
        logger.info("🔧 Web scraper initialized")
    
    def scrape_job_page(self, url: str) -> str:
        """
        Scrape job description from a URL.
        
        Args:
            url: URL of the job posting
            
        Returns:
            Extracted job description text
            
        Raises:
            ScrapingError: If all scraping methods fail
        """
        try:
            logger.info(f"🌐 Scraping job page: {url}")
            
            # Try Playwright first for better JavaScript handling
            content = self._extract_with_playwright(url)
            if content and len(content.strip()) > 100:  # Check if we got meaningful content
                logger.info("✅ Successfully extracted content using Playwright")
                return content
            
            # Fallback to requests if Playwright fails or gets minimal content
            content = self._extract_with_requests(url)
            if content and len(content.strip()) > 100:
                logger.info("✅ Successfully extracted content using requests")
                return content
            
            # If both methods fail, raise an error
            error_msg = "All web scraping methods failed to extract meaningful content"
            logger.error(f"❌ {error_msg}")
            raise ScrapingError(error_msg)
            
        except ScrapingError:
            raise
        except Exception as e:
            error_msg = f"Job scraping failed with unexpected error: {e}"
            logger.error(f"❌ {error_msg}")
            raise ScrapingError(error_msg)
    
    def _extract_with_playwright(self, url: str) -> Optional[str]:
        """Extract content using Playwright for JavaScript-heavy pages."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set timeout
                page.set_default_timeout(self.scraping_config['timeout'] * 1000)
                
                # Navigate to page
                page.goto(url, wait_until='networkidle')
                
                # Wait for content to load
                time.sleep(self.scraping_config['wait_time'])
                
                # Try to find main content
                main_content = page.query_selector(MAIN_TAG)
                if main_content:
                    content = main_content.inner_text()
                else:
                    # Fallback to body content
                    body = page.query_selector(BODY_TAG)
                    content = body.inner_text() if body else page.content()
                
                browser.close()
                
                if content:
                    cleaned_content = clean_html_content(content)
                    if len(cleaned_content) > MIN_JOB_DESCRIPTION_LENGTH:
                        return cleaned_content
                
                return None
                
        except Exception as e:
            logger.error(f"Playwright extraction error: {e}")
            return None
    
    def _extract_with_requests(self, url: str) -> Optional[str]:
        """Extract content using requests and BeautifulSoup."""
        try:
            response = requests.get(
                url, 
                timeout=self.scraping_config['timeout'],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find main content
            main_tag = soup.find(MAIN_TAG)
            if main_tag:
                content = main_tag.get_text()
            else:
                # Fallback to body content
                body = soup.find(BODY_TAG)
                content = body.get_text() if body else soup.get_text()
            
            if content:
                cleaned_content = clean_html_content(content)
                if len(cleaned_content) > MIN_JOB_DESCRIPTION_LENGTH:
                    return cleaned_content
            
            return None
            
        except Exception as e:
            logger.error(f"Requests extraction error: {e}")
            return None
    
    def _extract_with_direct_request(self, url: str) -> Optional[str]:
        """Direct request fallback method."""
        try:
            response = requests.get(
                url, 
                timeout=self.scraping_config['timeout'],
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            response.raise_for_status()
            
            # Simple text extraction
            content = response.text
            
            if content:
                cleaned_content = clean_html_content(content)
                if len(cleaned_content) > MIN_JOB_DESCRIPTION_LENGTH:
                    return cleaned_content
            
            return None
            
        except Exception as e:
            logger.error(f"Direct request extraction error: {e}")
            return None
    
    def validate_content(self, content: str) -> bool:
        """
        Validate extracted content quality.
        
        Args:
            content: Extracted content to validate
            
        Returns:
            True if content is valid, False otherwise
        """
        if not content or not content.strip():
            return False
        
        content_length = len(content.strip())
        
        if content_length < MIN_JOB_DESCRIPTION_LENGTH:
            logger.warning(f"Content too short: {content_length} characters (minimum: {MIN_JOB_DESCRIPTION_LENGTH})")
            return False
        
        if content_length > MAX_JOB_DESCRIPTION_LENGTH:
            logger.warning(f"Content too long: {content_length} characters (maximum: {MAX_JOB_DESCRIPTION_LENGTH})")
            return False
        
        # Check for common indicators of poor content
        if content.count('script') > 10 or content.count('style') > 10:
            logger.warning("Content contains too many script/style tags")
            return False
        
        return True
