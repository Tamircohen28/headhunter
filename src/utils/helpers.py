"""
Helper functions for common operations across the job4u application.
Provides utility functions for data processing, validation, and common tasks.
"""

import re
import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, quote_plus


def generate_unique_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def sanitize_filename(url: str) -> str:
    """Sanitize a URL for use as a filename."""
    # Remove protocol and special characters
    sanitized = re.sub(r'[^\w\-_.]', '_', url)
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized


def sanitize_url_for_filename(url: str) -> str:
    """Sanitize a URL for use in filenames, preserving some structure."""
    parsed = urlparse(url)
    # Create a filename from domain and path
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.replace('/', '_').replace('-', '_')
    if path.startswith('_'):
        path = path[1:]
    if len(path) > 50:
        path = path[:50]
    
    filename = f"{domain}_{path}"
    return sanitize_filename(filename)


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text content."""
    url_pattern = r'https?://[^\s\)]+'
    return re.findall(url_pattern, text)


def validate_job_description_length(content: str, min_length: int = 100, max_length: int = 50000) -> bool:
    """Validate job description content length."""
    content_length = len(content.strip())
    return min_length <= content_length <= max_length


def validate_topics_count(topics: List[str], min_count: int = 1, max_count: int = 20) -> bool:
    """Validate the number of research topics."""
    return min_count <= len(topics) <= max_count


def validate_agents_count(agents: int, min_count: int = 1, max_count: int = 10) -> bool:
    """Validate the number of research agents."""
    return min_count <= agents <= max_count


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for logging and display."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.2f}h"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_html_content(html_content: str) -> str:
    """Clean HTML content by removing tags and normalizing whitespace."""
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    # Normalize whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text)
    # Remove leading/trailing whitespace
    clean_text = clean_text.strip()
    return clean_text


def calculate_token_estimate(text: str, tokens_per_char: float = 0.25) -> int:
    """Estimate token count for text (rough approximation)."""
    return int(len(text) * tokens_per_char)


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def create_safe_filename(base_name: str, extension: str = "") -> str:
    """Create a safe filename from base name and extension."""
    # Remove unsafe characters
    safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
    # Limit length
    if len(safe_name) > 50:
        safe_name = safe_name[:50]
    
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    return safe_name + extension


def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries, with dict2 values taking precedence."""
    merged = dict1.copy()
    merged.update(dict2)
    return merged


def flatten_list(nested_list: List[Any]) -> List[Any]:
    """Flatten a nested list structure."""
    flattened = []
    for item in nested_list:
        if isinstance(item, list):
            flattened.extend(flatten_list(item))
        else:
            flattened.append(item)
    return flattened


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError, IndexError):
        return default


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def retry_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """Retry an operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate that required fields are present and not empty."""
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    return True


def normalize_text(text: str) -> str:
    """Normalize text by removing extra whitespace and normalizing line endings."""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove extra whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove empty lines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text
