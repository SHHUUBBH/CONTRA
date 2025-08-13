#!/usr/bin/env python
"""
Update Gradio URL Script

This script updates the Gradio URL in the .env file for the CONTRA project.
It's designed to be easy to use when you restart your Colab notebook and
get a new Gradio URL.
"""

import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv, set_key

def update_gradio_url(new_url):
    """
    Update the Gradio URL in the .env file
    
    Args:
        new_url: The new Gradio URL from Colab
    """
    env_file = Path('.env')
    
    # Check if .env file exists
    if not env_file.exists():
        print(f"Error: .env file not found at {env_file.absolute()}")
        print("Creating a new .env file")
        env_file.touch()
    
    # Validate URL format
    if not re.match(r'^https?://.*?\.gradio\..*$', new_url):
        print(f"Warning: URL '{new_url}' doesn't look like a Gradio URL.")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("Aborted")
            return
    
    # Update the .env file
    set_key(env_file, 'SD_GRADIO_ENDPOINT', new_url)
    set_key(env_file, 'USE_CUSTOM_GRADIO', 'true')
    
    print(f"Updated .env file with new Gradio URL: {new_url}")
    print("Make sure to restart the CONTRA application to apply changes")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python update_gradio_url.py <new_gradio_url>")
        print("Example: python update_gradio_url.py https://12345abcde.gradio.live")
        return 1
    
    new_url = sys.argv[1]
    update_gradio_url(new_url)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 