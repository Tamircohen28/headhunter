#!/usr/bin/env python3
"""
Main entry point for the job4u application.
"""

from src.utils.config import Config
from src.utils.logger import setup_logging, log
from src.storage_manager.generic_file_manager import GenericFileManager
from src.scraper.web_scraper import WebScraper
from src.llm_client.openai_client import OpenAIClient
from src.pipeline import Pipeline


def main():
    """Main application entry point."""
    try:
        # Initialize configuration
        config = Config()
        
        # Setup logging
        setup_logging(config)
        
        # Initialize generic file manager
        file_manager = GenericFileManager(config.output_dir)
        
        # Initialize web scraper
        scraper = WebScraper(config)
        
        # Initialize OpenAI client
        openai_client = OpenAIClient(config)
        
        # Initialize pipeline
        pipeline = Pipeline(config, file_manager)
        
        # Run the pipeline
        results = pipeline.run()
        
        # Log success
        log("info", "🎉 Application completed successfully")
        
    except Exception as e:
        log("error", f"Application failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
