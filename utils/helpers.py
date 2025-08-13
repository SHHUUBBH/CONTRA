"""
Helper utility functions for the CONTRA application.
"""

import datetime
import re
import unicodedata
import string
from typing import Dict, Any, List, Optional, Union
from urllib.parse import quote

def iso_now() -> str:
    """
    Return the current UTC time in ISO 8601 format (e.g., '2024-05-01T12:34:56Z').
    
    Returns:
        ISO 8601 formatted timestamp string
    """
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def sanitize_filename(filename: str) -> str:
    """
    Convert a string to a valid filename by removing invalid characters.
    
    Args:
        filename: Input string to sanitize
    
    Returns:
        A sanitized string safe for use as a filename
    """
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    sanitized = ''.join(c for c in filename if c in valid_chars)
    
    # Remove leading/trailing periods and spaces
    return sanitized.strip('. ')


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace, normalizing Unicode, etc.
    
    Args:
        text: Input text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()


def truncate_text(text: str, max_length: int = 500, add_ellipsis: bool = True) -> str:
    """
    Truncate text to a maximum length, optionally adding an ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        add_ellipsis: Whether to add "..." at the end if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rstrip()
    if add_ellipsis:
        truncated += "..."
    
    return truncated


def create_wikipedia_url(topic: str) -> str:
    """
    Create a Wikipedia URL from a topic string.
    
    Args:
        topic: Topic string (e.g., "French Revolution")
    
    Returns:
        Wikipedia URL for the topic
    """
    return f"https://en.wikipedia.org/wiki/{quote(topic.replace(' ', '_'))}"


def extract_dates_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extract dates from text for timeline visualization.
    
    Args:
        text: Text to extract dates from
    
    Returns:
        List of dicts with 'year' and 'event' keys
    """
    if not text:
        return []
        
    # More comprehensive regex patterns for various date formats
    # 1. Simple year pattern (e.g., 1990, 2023)
    year_pattern = r'\b(1[0-9]{3}|20[0-2][0-9])\b'
    
    # 2. Month and year pattern (e.g., January 1990, Jan 1990)
    month_year_pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})\b'
    
    # 3. Date, month, and year pattern (e.g., 1 January 1990, 1st Jan 1990)
    date_pattern = r'\b(\d{1,2})(st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+(\d{4})\b'
    
    # 4. Year range pattern (e.g., 1990-1995, 1990—1995)
    year_range_pattern = r'\b(1[0-9]{3}|20[0-2][0-9])[\-\–\—]+(1[0-9]{3}|20[0-2][0-9])\b'
    
    dates = []
    
    # Helper function to add a date with context
    def add_date_with_context(year, match):
        # Extract sentence around the match
        sentence_start = max(0, text.rfind('.', 0, match.start()) + 1)
        sentence_end = text.find('.', match.end())
        if sentence_end == -1:
            sentence_end = len(text)
            
        context = text[sentence_start:sentence_end].strip()
        if len(context) > 100:
            # If too long, get just part around the match
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            context = "..." + text[start:end].strip() + "..."
        
        dates.append({
            'year': year,
            'event': context
        })
    
    # 1. Find simple years
    for match in re.finditer(year_pattern, text):
        year = int(match.group(1))
        add_date_with_context(year, match)
    
    # 2. Find month and year
    for match in re.finditer(month_year_pattern, text, re.IGNORECASE):
        year = int(match.group(2))
        add_date_with_context(year, match)
    
    # 3. Find full dates
    for match in re.finditer(date_pattern, text, re.IGNORECASE):
        year = int(match.group(4))
        add_date_with_context(year, match)
    
    # 4. Find year ranges (using the start year)
    for match in re.finditer(year_range_pattern, text):
        start_year = int(match.group(1))
        end_year = int(match.group(2))
        add_date_with_context(start_year, match)
    
    # Remove duplicates, keeping the first occurrence of each year
    unique_dates = []
    seen_years = set()
    
    for date in dates:
        if date['year'] not in seen_years:
            seen_years.add(date['year'])
            unique_dates.append(date)
    
    return unique_dates


def format_time_elapsed(seconds: float) -> str:
    """
    Format elapsed time in seconds to a human-readable string.
    
    Args:
        seconds: Elapsed time in seconds
    
    Returns:
        Formatted string (e.g., "1.2s", "350ms")
    """
    if seconds >= 1:
        return f"{seconds:.1f}s"
    else:
        return f"{int(seconds * 1000)}ms"


def deep_get(dictionary: Dict[str, Any], keys: Union[str, List[str]], default: Any = None) -> Any:
    """
    Safely get a value from a nested dictionary using dot notation.
    
    Args:
        dictionary: Dictionary to get value from
        keys: Key path as a dot-separated string or list of keys
        default: Default value to return if key not found
    
    Examples:
        deep_get(data, "user.profile.name", "Unknown")
        deep_get(data, ["user", "profile", "name"], "Unknown")
    
    Returns:
        Value or default if not found
    """
    if isinstance(keys, str):
        keys = keys.split('.')
    
    temp = dictionary
    for key in keys:
        if isinstance(temp, dict) and key in temp:
            temp = temp[key]
        else:
            return default
    
    return temp 