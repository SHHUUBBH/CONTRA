#!/usr/bin/env python
"""
Restart script for the CONTRA application.
This script clears caches and ensures all directories are properly set up.
"""

import os
import shutil
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Ensure a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    else:
        logger.info(f"Directory already exists: {directory}")

def clear_cache(cache_dir, exclude=None):
    """Clear cache but preserve specified files."""
    if exclude is None:
        exclude = []
    
    if not os.path.exists(cache_dir):
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        return
    
    # Convert exclude list to absolute paths for easier comparison
    exclude_abs = [os.path.abspath(os.path.join(cache_dir, f)) for f in exclude]
    
    count = 0
    for f in os.listdir(cache_dir):
        file_path = os.path.join(cache_dir, f)
        abs_path = os.path.abspath(file_path)
        
        if os.path.isfile(file_path) and abs_path not in exclude_abs:
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to remove file {file_path}: {e}")
    
    logger.info(f"Cleared {count} files from {cache_dir}")

def ensure_fallback_image():
    """Ensure fallback image exists."""
    static_img_dir = "static/img"
    ensure_directory(static_img_dir)
    
    fallback_path = os.path.join(static_img_dir, "fallback.jpg")
    if not os.path.exists(fallback_path):
        # Create a simple colored image
        try:
            from PIL import Image
            img = Image.new('RGB', (512, 512), color=(39, 41, 61))
            img.save(fallback_path)
            logger.info(f"Created fallback image: {fallback_path}")
        except ImportError:
            logger.warning("PIL not installed, cannot create fallback image")
        except Exception as e:
            logger.error(f"Failed to create fallback image: {e}")
    else:
        logger.info(f"Fallback image already exists: {fallback_path}")

def main():
    """Main function to restart the application."""
    print("===== RESTARTING CONTRA APPLICATION =====")
    
    # Import configuration after logger setup
    from config import IMAGE_CACHE_DIR, DATA_CACHE_DIR, BASE_DIR
    
    # Ensure required directories exist
    ensure_directory("static/img")
    ensure_directory(IMAGE_CACHE_DIR)
    ensure_directory(DATA_CACHE_DIR)
    
    # Ensure fallback image exists
    ensure_fallback_image()
    
    # Clear caches
    print("\n===== CLEARING CACHES =====")
    clear_cache(IMAGE_CACHE_DIR)
    
    # Restart the application
    print("\n===== APPLICATION READY =====")
    print("You can now start the application with: python app.py")
    
    # Verify the API key
    print("\n===== VERIFYING API KEY =====")
    try:
        from config import APIConfig
        api_key = APIConfig.STABILITY_API_KEY
        if api_key:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else api_key
            print(f"Found STABILITY_API_KEY: {masked_key}")
        else:
            print("WARNING: No STABILITY_API_KEY found. Images will use fallbacks.")
    except Exception as e:
        print(f"Error checking API key: {e}")
    
    print("\nDone! The application should now work correctly with image generation.")

if __name__ == "__main__":
    main() 