#!/usr/bin/env python
"""
Script to create a proper .env file with necessary configuration.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with proper configuration."""
    env_path = Path('.env')
    
    print(f"Creating new .env file at {env_path.absolute()}")
    
    env_content = """# CONTRA Environment Variables

# API Keys
GROQ_API_KEY=your_groq_api_key_here
NEWS_API_KEY=your_news_api_key_here
STABILITY_API_KEY=

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev_secret_key_replace_in_production
PORT=5000

# Model Configuration
GROQ_MODEL=llama-3.3-70b-versatile

# Cache Configuration
ENABLE_CACHE=1
CACHE_TIMEOUT=3600
MAX_IMAGE_CACHE_SIZE=100
MAX_DATA_CACHE_SIZE=1000
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"Created .env file with proper configuration.")
    print("\nImportant note:")
    print("To use Stability AI API, you need to add your API key to the .env file.")
    print("If you don't have an API key, the application will use fallback images.")

if __name__ == "__main__":
    create_env_file()
    print("\nEnvironment setup complete!") 