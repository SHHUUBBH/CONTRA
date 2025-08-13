"""
Configuration settings for the CONTRA application.
This module provides a structured way to manage environment variables,
API keys, and other configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Try to load environment variables, but don't fail if there's an issue
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Using default configuration values instead")

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Cache directories
CACHE_DIR = BASE_DIR / "cache"
IMAGE_CACHE_DIR = CACHE_DIR / "images"
DATA_CACHE_DIR = CACHE_DIR / "data"

# Create cache directories if they don't exist
IMAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# API Keys and endpoints
class APIConfig:
    """API configuration settings"""
    # Groq LLaMA API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Stable Diffusion
    SD_MODEL_VERSION = os.getenv("SD_MODEL_VERSION", "stable-diffusion-3.5-large")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
    # News API
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "your_news_api_key_here")

# Flask application settings
class FlaskConfig:
    """Flask application configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24).hex())
    DEBUG = os.getenv("FLASK_ENV", "development") == "development"
    TESTING = os.getenv("FLASK_TESTING", "0") == "1"
    PORT = int(os.getenv("PORT", 5000))

# Cache settings
class CacheConfig:
    """Cache configuration"""
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "1") == "1"
    CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", 3600))  # 1 hour default
    MAX_IMAGE_CACHE_SIZE = int(os.getenv("MAX_IMAGE_CACHE_SIZE", 100))  # Number of images
    MAX_DATA_CACHE_SIZE = int(os.getenv("MAX_DATA_CACHE_SIZE", 1000))  # Number of items

# Content generation settings
class ContentConfig:
    """Content generation configuration"""
    # Image generation
    DEFAULT_IMAGE_WIDTH = int(os.getenv("DEFAULT_IMAGE_WIDTH", 1344))
    DEFAULT_IMAGE_HEIGHT = int(os.getenv("DEFAULT_IMAGE_HEIGHT", 768))  # Using SDXL-compatible dimensions (1344x768)
    DEFAULT_NUM_VARIANTS = int(os.getenv("DEFAULT_NUM_VARIANTS", 1))
    
    # Narrative generation
    DEFAULT_MAX_LENGTH = int(os.getenv("DEFAULT_MAX_LENGTH", 1024))
    DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", 0.9))
    DEFAULT_TONE = os.getenv("DEFAULT_TONE", "informative")
    VALID_TONES = ["informative", "dramatic", "poetic", "humorous", "technical", "simple"]
    
    # Conversation settings
    CONVERSATION_MAX_TOKENS = int(os.getenv("CONVERSATION_MAX_TOKENS", 800))
    CONVERSATION_TEMPERATURE = float(os.getenv("CONVERSATION_TEMPERATURE", 0.7))
    CONVERSATION_MAX_HISTORY = int(os.getenv("CONVERSATION_MAX_HISTORY", 10))
    
    # Visualization
    DEFAULT_VIZ_THEME = os.getenv("DEFAULT_VIZ_THEME", "plotly_dark")
    TIMELINE_MAX_EVENTS = int(os.getenv("TIMELINE_MAX_EVENTS", 10))
    
    # Data fetching
    MAX_NEWS_ARTICLES = int(os.getenv("MAX_NEWS_ARTICLES", 5))
    WIKIPEDIA_SUMMARY_LENGTH = int(os.getenv("WIKIPEDIA_SUMMARY_LENGTH", 1000)) 