"""
Logging utilities for the job4u application.
"""

import sys
from typing import Any, Dict, Optional
from loguru import logger
from datetime import datetime


def setup_logging(config: Any) -> None:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration instance
    """
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True
    )
    
    # Add file handler
    log_file = f"logs/job4u_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.log_level,
        rotation="1 day",
        retention="7 days"
    )
    
    logger.info("🔧 Logging system initialized")
    logger.info(f"📁 Log level: {config.log_level}")
    logger.info(f"📁 Output directory: {config.output_dir}")
    logger.info(f"📁 Log file: {log_file}")


def log(level: str, message: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> None:
    """
    Generic log function for all logging needs.
    
    Args:
        level: Log level (debug, info, warning, error, critical)
        message: Main log message
        data: Optional structured data to log
        **kwargs: Additional key-value pairs to log
    """
    # Combine all data
    log_data = {}
    if data:
        log_data.update(data)
    if kwargs:
        log_data.update(kwargs)
    
    # Format the log entry
    if log_data:
        formatted_message = f"{message} | {log_data}"
    else:
        formatted_message = message
    
    # Log based on level
    level = level.lower()
    if level == "debug":
        logger.debug(formatted_message)
    elif level == "info":
        logger.info(formatted_message)
    elif level == "warning":
        logger.warning(formatted_message)
    elif level == "error":
        logger.error(formatted_message)
    elif level == "critical":
        logger.critical(formatted_message)
    else:
        logger.info(formatted_message)


def log_pipeline_start(job_url: str, study_weeks: int, hours_per_week: int) -> None:
    """Log pipeline start."""
    log("info", "🚀 Starting Interview Preparation Pipeline", {
        "job_url": job_url,
        "study_weeks": study_weeks,
        "hours_per_week": hours_per_week,
        "timestamp": datetime.now().isoformat()
    })


def log_pipeline_completion(start_time: float, total_steps: int) -> None:
    """Log pipeline completion."""
    duration = datetime.now().timestamp() - start_time
    log("info", "🎉 Pipeline completed successfully", {
        "duration_seconds": duration,
        "total_steps": total_steps
    })


def log_api_call(operation: str, model: str, prompt_length: int, conversation_id: Optional[str] = None) -> None:
    """Log API call."""
    log("info", f"🚀 API Call: {operation}", {
        "operation": operation,
        "model": model,
        "prompt_length": prompt_length,
        "conversation_id": conversation_id
    })


def log_api_response(operation: str, model: str, usage: Any, finish_reason: str, response_length: int, response_preview: str) -> None:
    """Log API response."""
    log("info", f"📡 API Response: {operation}", {
        "operation": operation,
        "model": model,
        "usage": usage,
        "finish_reason": finish_reason,
        "response_length": response_length,
        "response_preview": response_preview
    })
