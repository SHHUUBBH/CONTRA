#!/usr/bin/env python
"""
Setup script for the CONTRA application.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a sample .env file if it doesn't exist."""
    env_path = Path('.env')
    
    if env_path.exists():
        print("An .env file already exists. Skipping creation.")
        return
    
    print("Creating a sample .env file...")
    env_content = """# CONTRA Environment Variables

# API Keys
GROQ_API_KEY=dummy_key_replace_with_real_one
NEWS_API_KEY=dummy_key_replace_with_real_one

# Stable Diffusion
SD_GRADIO_ENDPOINT=http://localhost:7860/predict

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
    print("Sample .env file created successfully.")

def create_cache_dirs():
    """Create cache directories if they don't exist."""
    cache_paths = [
        Path('cache'),
        Path('cache/images'),
        Path('cache/data')
    ]
    
    for path in cache_paths:
        if not path.exists():
            print(f"Creating directory: {path}")
            path.mkdir(exist_ok=True)
        else:
            print(f"Directory already exists: {path}")

def main():
    """Main setup function."""
    print("Setting up CONTRA application...")
    
    # Create .env file
    create_env_file()
    
    # Create cache directories
    create_cache_dirs()
    
    print("\nSetup complete! Next steps:")
    print("1. Create a Python virtual environment (if not already done):")
    print("   Windows: python -m venv venv")
    print("   Unix/MacOS: python3 -m venv venv")
    print("\n2. Activate the virtual environment:")
    print("   Windows: venv\\Scripts\\activate")
    print("   Unix/MacOS: source venv/bin/activate")
    print("\n3. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("\n4. Edit the .env file with your actual API keys")
    print("\n5. Run the application:")
    print("   python app.py")

if __name__ == '__main__':
    main() 