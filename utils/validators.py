"""
Input validation utilities for the CONTRA application.
"""

import re
from typing import Dict, Any, List, Optional, Tuple, Union

# Regular expressions for validation
TOPIC_PATTERN = r'^[\w\s\-\',.!?&:()]{3,100}$'
COLOR_PATTERN = r'^#(?:[0-9a-fA-F]{3}){1,2}$|^[a-zA-Z]+$'  # Hex or named colors

def validate_topic(topic: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a topic string.
    
    Args:
        topic: User-provided topic string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not topic or not topic.strip():
        return False, "Topic cannot be empty"
    
    topic = topic.strip()
    
    if len(topic) < 3:
        return False, "Topic must be at least 3 characters"
    
    if len(topic) > 100:
        return False, "Topic must be less than 100 characters"
    
    # Check for valid characters
    if not re.match(TOPIC_PATTERN, topic):
        return False, "Topic contains invalid characters"
    
    # Check for potentially harmful inputs
    harmful_patterns = [
        r'<[^>]*>',  # HTML/XML tags
        r'javascript:',  # JavaScript protocol
        r'data:',  # Data URIs
        r'eval\s*\(',  # eval()
        r'execCommand',  # execCommand
        r'execute\s*\(',  # execute()
        r'innerHtml',  # innerHtml
        r'document\..*\(',  # document methods
        r'window\..*\(',  # window methods
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, topic, re.IGNORECASE):
            return False, "Topic contains potentially harmful content"
    
    return True, None


def validate_input(data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate input data.
    
    Args:
        data: Input data dictionary
    
    Returns:
        Tuple of (is_valid, error_message, normalized_data)
    """
    normalized = {}
    
    # Validate topic (required)
    if 'topic' not in data:
        return False, "Missing 'topic' field", None
    
    topic = data.get('topic', '').strip()
    topic_valid, topic_error = validate_topic(topic)
    if not topic_valid:
        return False, topic_error, None
    
    normalized['topic'] = topic
    
    # Validate optional fields
    
    # Tone
    valid_tones = ['informative', 'dramatic', 'poetic', 'humorous', 'technical', 'simple']
    tone = data.get('tone', 'informative').lower()
    if tone not in valid_tones:
        tone = 'informative'  # Default to informative if invalid
    normalized['tone'] = tone
    
    # Number of image variants
    try:
        variants = int(data.get('variants', 1))
        if variants < 1:
            variants = 1
        elif variants > 5:  # Limit to 5 variants
            variants = 5
    except (ValueError, TypeError):
        variants = 1
    normalized['variants'] = variants
    
    # Color scheme
    if 'colors' in data and isinstance(data['colors'], list):
        colors = []
        for color in data['colors']:
            if isinstance(color, str) and re.match(COLOR_PATTERN, color):
                colors.append(color)
        normalized['colors'] = colors
    
    # Advanced settings
    if 'advanced' in data and isinstance(data['advanced'], dict):
        advanced = {}
        adv_data = data['advanced']
        
        # Max length
        try:
            max_length = int(adv_data.get('max_length', 1024))
            if 256 <= max_length <= 4096:
                advanced['max_length'] = max_length
        except (ValueError, TypeError):
            pass
        
        # Temperature
        try:
            temp = float(adv_data.get('temperature', 0.7))
            if 0.1 <= temp <= 1.0:
                advanced['temperature'] = temp
        except (ValueError, TypeError):
            pass
        
        if advanced:
            normalized['advanced'] = advanced
    
    return True, None, normalized 