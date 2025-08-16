"""
Helper functions for common operations across the job4u application.
Provides utility functions for data processing, validation, and common tasks.
"""

import re
import uuid
import hashlib
import html
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
    """
    Clean HTML content by removing tags, decoding entities, and adding proper formatting.
    
    Args:
        html_content: Raw HTML content to clean
        
    Returns:
        Clean, readable text with proper formatting
    """
    if not html_content:
        return ""
    
    # Decode HTML entities (like &nbsp;, &amp;, etc.)
    decoded_content = html.unescape(html_content)
    
    # Replace common HTML entities with readable equivalents
    entity_replacements = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#39;': "'",
        '&apos;': "'",
        '&hellip;': '...',
        '&mdash;': '—',
        '&ndash;': '–',
        '&rsquo;': "'",
        '&lsquo;': "'",
        '&rdquo;': '"',
        '&ldquo;': '"',
        '&copy;': '(c)',
        '&reg;': '(R)',
        '&trade;': '(TM)',
        '&deg;': '°',
        '&plusmn;': '±',
        '&times;': '×',
        '&divide;': '÷',
        '&frac12;': '½',
        '&frac14;': '¼',
        '&frac34;': '¾',
        '&infin;': '∞',
        '&ne;': '≠',
        '&le;': '≤',
        '&ge;': '≥',
        '&alpha;': 'α',
        '&beta;': 'β',
        '&gamma;': 'γ',
        '&delta;': 'δ',
        '&epsilon;': 'ε',
        '&theta;': 'θ',
        '&lambda;': 'λ',
        '&mu;': 'μ',
        '&pi;': 'π',
        '&sigma;': 'σ',
        '&tau;': 'τ',
        '&phi;': 'φ',
        '&omega;': 'ω'
    }
    
    for entity, replacement in entity_replacements.items():
        decoded_content = decoded_content.replace(entity, replacement)
    
    # Remove HTML tags but preserve some structure
    # Replace common tags with line breaks for readability
    tag_replacements = {
        r'<br\s*/?>': '\n',           # Line breaks
        r'</p>': '\n\n',              # Paragraph endings
        r'</div>': '\n',              # Div endings
        r'</section>': '\n',          # Section endings
        r'</article>': '\n',          # Article endings
        r'</h[1-6]>': '\n\n',        # Headings
        r'</li>': '\n',               # List items
        r'</tr>': '\n',               # Table rows
        r'</td>': ' | ',              # Table cells
        r'</th>': ' | ',              # Table headers
        r'</ul>': '\n',               # Unordered lists
        r'</ol>': '\n',               # Ordered lists
        r'</blockquote>': '\n\n',     # Blockquotes
        r'</pre>': '\n\n',            # Preformatted text
        r'</code>': ' ',              # Inline code
    }
    
    # Apply tag replacements
    for pattern, replacement in tag_replacements.items():
        decoded_content = re.sub(pattern, replacement, decoded_content, flags=re.IGNORECASE)
    
    # Remove all remaining HTML tags
    decoded_content = re.sub(r'<[^>]+>', '', decoded_content)
    
    # Clean up special characters and symbols that might be artifacts
    # Remove common problematic characters
    decoded_content = re.sub(r'[  ]', ' ', decoded_content)  # Remove weird box characters
    decoded_content = re.sub(r'[ ]', ' ', decoded_content)   # Remove other weird symbols
    
    # Normalize whitespace and line breaks
    # Replace multiple spaces with single space
    decoded_content = re.sub(r' +', ' ', decoded_content)
    
    # Replace multiple newlines with double newlines for readability
    decoded_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', decoded_content)
    
    # Clean up line breaks around content
    decoded_content = re.sub(r'^\s*\n+', '', decoded_content)  # Remove leading newlines
    decoded_content = re.sub(r'\n+\s*$', '', decoded_content)  # Remove trailing newlines
    
    # Add line breaks for better readability in specific patterns
    # Add breaks after common job posting sections
    section_patterns = [
        (r'(Qualifications?)(\s*[:])', r'\1\2\n'),
        (r'(Requirements?)(\s*[:])', r'\1\2\n'),
        (r'(Responsibilities?)(\s*[:])', r'\1\2\n'),
        (r'(Benefits?)(\s*[:])', r'\1\2\n'),
        (r'(About the Role?)(\s*[:])', r'\1\2\n'),
        (r'(Overview?)(\s*[:])', r'\1\2\n'),
        (r'(Job Description?)(\s*[:])', r'\1\2\n'),
        (r'(Company?)(\s*[:])', r'\1\2\n'),
        (r'(Location?)(\s*[:])', r'\1\2\n'),
        (r'(Employment Type?)(\s*[:])', r'\1\2\n'),
        (r'(Work Site?)(\s*[:])', r'\1\2\n'),
        (r'(Travel?)(\s*[:])', r'\1\2\n'),
        (r'(Role Type?)(\s*[:])', r'\1\2\n'),
        (r'(Profession?)(\s*[:])', r'\1\2\n'),
        (r'(Discipline?)(\s*[:])', r'\1\2\n'),
    ]
    
    for pattern, replacement in section_patterns:
        decoded_content = re.sub(pattern, replacement, decoded_content, flags=re.IGNORECASE)
    
    # Add line breaks after bullet points and list items
    decoded_content = re.sub(r'(\s*[-•*]\s+)', r'\n\1', decoded_content)
    
    # Add line breaks after numbered items
    decoded_content = re.sub(r'(\s*\d+\.\s+)', r'\n\1', decoded_content)
    
    # Add line breaks for better job posting readability
    # Add breaks after job title patterns
    decoded_content = re.sub(r'(\w+\s+Engineer\s+[I]+)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(\w+\s+Developer)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(\w+\s+Manager)', r'\1\n', decoded_content)
    
    # Add breaks after location patterns
    decoded_content = re.sub(r'([A-Z][a-z]+,\s+[A-Z][a-z]+,\s+[A-Z][a-z]+)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'([A-Z][a-z]+,\s+[A-Z][a-z]+)', r'\1\n', decoded_content)
    
    # Add breaks after date patterns
    decoded_content = re.sub(r'(Date posted\s+[A-Z][a-z]+\s+\d+,\s+\d{4})', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Job number\s+\d+)', r'\1\n', decoded_content)
    
    # Add breaks after key-value pairs
    decoded_content = re.sub(r'(Work site\s+[^.]*\.)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Travel\s+[^.]*\.)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Role type\s+[^.]*\.)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Profession\s+[^.]*\.)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Discipline\s+[^.]*\.)', r'\1\n', decoded_content)
    decoded_content = re.sub(r'(Employment type\s+[^.]*\.)', r'\1\n', decoded_content)
    
    # Add breaks after sentences that end with periods
    decoded_content = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', decoded_content)
    
    # Clean up any remaining weird characters
    decoded_content = re.sub(r'[^\x00-\x7F\u00A0-\uFFFF\s]', '', decoded_content)
    
    # Final cleanup of whitespace
    decoded_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', decoded_content)  # Remove excessive newlines
    decoded_content = decoded_content.strip()
    
    return decoded_content


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


def pretty_print_topic_hierarchy(topic_hierarchy: Dict[str, List[str]], dependencies: Dict[str, List[str]] = None, learning_order: List[str] = None) -> str:
    """
    Pretty print a topic hierarchy in a readable format.
    
    Args:
        topic_hierarchy: Dictionary mapping main topics to lists of sub-topics
        dependencies: Optional dictionary mapping topics to prerequisite topics
        learning_order: Optional list of topics in logical learning sequence
        
    Returns:
        Formatted string representation of the topic hierarchy
    """
    if not topic_hierarchy:
        return "No topic hierarchy available."
    
    output = []
    output.append("🎯 COMPREHENSIVE TOPIC HIERARCHY FOR INTERVIEW PREPARATION")
    output.append("=" * 70)
    output.append("")
    
    # Print topics in learning order if available, otherwise in dictionary order
    topics_to_print = learning_order if learning_order else list(topic_hierarchy.keys())
    
    for i, main_topic in enumerate(topics_to_print, 1):
        if main_topic not in topic_hierarchy:
            continue
            
        output.append(f"{i}. {main_topic}")
        
        # Print sub-topics with bullet points
        sub_topics = topic_hierarchy[main_topic]
        for j, sub_topic in enumerate(sub_topics, 1):
            output.append(f"   • {sub_topic}")
        
        # Print dependencies if available
        if dependencies and main_topic in dependencies:
            deps = dependencies[main_topic]
            if deps:
                output.append(f"   📚 Prerequisites: {', '.join(deps)}")
        
        output.append("")
    
    # Print summary statistics
    total_main_topics = len(topic_hierarchy)
    total_sub_topics = sum(len(sub_topics) for sub_topics in topic_hierarchy.values())
    avg_sub_topics = total_sub_topics / total_main_topics if total_main_topics > 0 else 0
    
    output.append("📊 SUMMARY STATISTICS")
    output.append("-" * 30)
    output.append(f"Total Main Topics: {total_main_topics}")
    output.append(f"Total Sub-topics: {total_sub_topics}")
    output.append(f"Average Sub-topics per Topic: {avg_sub_topics:.1f}")
    
    if learning_order:
        output.append(f"Learning Order: {' → '.join(learning_order[:5])}{'...' if len(learning_order) > 5 else ''}")
    
    return "\n".join(output)
