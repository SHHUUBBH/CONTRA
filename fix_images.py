#!/usr/bin/env python
"""
Script to ensure all image files are correctly set up.
"""

import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        "static",
        "static/img",
        "cache",
        "cache/images"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Directory {directory} confirmed.")

def create_fallback_image():
    """Create or replace the fallback image."""
    fallback_path = Path("static/img/fallback.jpg")
    
    # Create a dark blue fallback image
    img = Image.new('RGB', (512, 512), color=(32, 34, 50))
    
    # Add some text
    try:
        draw = ImageDraw.Draw(img)
        # Draw the image text
        draw.text((100, 200), "Image Not Available", fill=(255, 255, 255))
        draw.text((100, 250), "Please set STABILITY_API_KEY", fill=(200, 200, 200))
    except Exception as e:
        print(f"Error adding text to image: {e}")
    
    # Save the fallback image
    img.save(fallback_path)
    print(f"Created fallback image at {fallback_path}")
    
    # Also copy to the cache directory for testing
    cache_path = Path("cache/images/fallback.jpg")
    img.save(cache_path)
    print(f"Copied fallback image to cache at {cache_path}")

def create_placeholder_image():
    """Create or replace the placeholder image."""
    placeholder_path = Path("static/img/image_placeholder.png")
    
    # Create a lighter blue placeholder image
    img = Image.new('RGB', (512, 512), color=(50, 55, 80))
    
    # Add some text
    try:
        draw = ImageDraw.Draw(img)
        # Draw the image text
        draw.text((100, 200), "Placeholder Image", fill=(255, 255, 255))
        draw.text((100, 250), "Image could not be loaded", fill=(200, 200, 200))
    except Exception as e:
        print(f"Error adding text to image: {e}")
    
    # Save the placeholder image
    img.save(placeholder_path)
    print(f"Created placeholder image at {placeholder_path}")

if __name__ == "__main__":
    print("Setting up image files...")
    
    # Ensure directories
    ensure_directories()
    
    # Create image files
    create_fallback_image()
    create_placeholder_image()
    
    print("\nSetup complete! All image files have been created.") 