#!/usr/bin/env python
"""
Run script for the CONTRA application.
This script:
1. Checks if required directories exist
2. Verifies that .env file exists
3. Runs the Flask application
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists."""
    env_path = Path('.env')
    if not env_path.exists():
        print("Error: .env file not found.")
        print("Please run setup.py first to create the .env file.")
        return False
    return True

def check_cache_dirs():
    """Check if cache directories exist and create them if needed."""
    cache_paths = [
        Path('cache'),
        Path('cache/images'),
        Path('cache/data')
    ]
    
    for path in cache_paths:
        if not path.exists():
            print(f"Creating missing directory: {path}")
            path.mkdir(exist_ok=True)
    
    return True

def main():
    """Main function to run the application."""
    print("Starting CONTRA application...")
    
    # Check environment and directories
    if not check_env_file() or not check_cache_dirs():
        print("Environment check failed. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Import app here to ensure .env file is loaded
    from app import create_app
    
    # Create and run the app
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    
    print(f"CONTRA is running on http://localhost:{port}")
    print("Press Ctrl+C to quit")
    
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    main() 