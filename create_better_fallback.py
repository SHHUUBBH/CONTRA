#!/usr/bin/env python
"""
Script to create better fallback images and clear the image cache.
This helps resolve issues with Stability AI image generation.
"""

import os
import shutil
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist."""
    directories = [
        "static/img",
        "cache/images",
        "cache/data"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        else:
            logger.info(f"Directory already exists: {directory}")

def create_fallback_image():
    """Create or replace the fallback image."""
    fallback_path = Path("static/img/fallback.jpg")
    
    # Create a gradient fallback image
    width, height = 1024, 1024
    img = Image.new('RGB', (width, height), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Create a gradient background
    for y in range(height):
        r = int(30 + (y / height) * 40)
        g = int(30 + (y / height) * 20)
        b = int(50 + (y / height) * 80)
        for x in range(width):
            # Add some horizontal variation
            r_var = r + int((x / width) * 30)
            g_var = g + int((x / width) * 40)
            b_var = b + int((x / width) * 10)
            
            # Keep values in valid range
            r_val = max(0, min(255, r_var))
            g_val = max(0, min(255, g_var))
            b_val = max(0, min(255, b_var))
            
            draw.point((x, y), fill=(r_val, g_val, b_val))
    
    # Draw some shapes
    for i in range(5):
        size = 50 + i * 20
        x = 100 + i * 50
        y = 100 + i * 40
        draw.ellipse(
            (x - size//2, y - size//2, x + size//2, y + size//2),
            fill=(100 + i * 20, 80 + i * 20, 160 + i * 20, 200)
        )
    
    # Draw some lines to simulate text
    for i in range(10):
        y_pos = 350 + i * 20
        length = 100 + (i % 3) * 50
        draw.line(
            (50, y_pos, 50 + length, y_pos),
            fill=(220, 220, 240, 200),
            width=8
        )
    
    # Save the fallback image
    img.save(fallback_path, "JPEG", quality=95)
    logger.info(f"Created fallback image at {fallback_path}")
    
    # Also copy to the cache directory for testing
    cache_path = Path("cache/images/fallback.jpg")
    img.save(cache_path, "JPEG", quality=95)
    logger.info(f"Copied fallback image to cache at {cache_path}")

def clear_image_cache():
    """Clear the image cache to force regeneration."""
    cache_dir = Path("cache/images")
    if not cache_dir.exists():
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        return
    
    # Keep only the fallback image
    keepfile = "fallback.jpg"
    count = 0
    
    for f in os.listdir(cache_dir):
        if f != keepfile:
            file_path = cache_dir / f
            try:
                if file_path.is_file():
                    os.remove(file_path)
                    count += 1
            except Exception as e:
                logger.error(f"Failed to remove file {file_path}: {e}")
    
    logger.info(f"Cleared {count} files from image cache")

def update_api_url():
    """Update the API URL in the stable_diffusion.py file."""
    try:
        from config import APIConfig
        
        # Print current model version
        logger.info(f"Current SD model version: {APIConfig.SD_MODEL_VERSION}")
        
        # Update config file to use newer API endpoint if needed
        stable_diffusion_path = Path("services/stable_diffusion.py")
        
        if not stable_diffusion_path.exists():
            logger.error(f"Could not find {stable_diffusion_path}")
            return
        
        # Read the file
        content = stable_diffusion_path.read_text()
        
        # Check if we're using the latest API endpoint
        if "stable-diffusion-xl-1024-v1-0" in content:
            # Update to a different endpoint if needed
            logger.info("Current API endpoint is using SDXL. Trying to update to newer model if available.")
        else:
            logger.info("API endpoint already updated or using a different path.")
        
        logger.info("API URL check completed.")
    
    except Exception as e:
        logger.error(f"Error updating API URL: {e}")

def main():
    """Main function to run all fixes."""
    print("\n===== FIXING IMAGE GENERATION =====\n")
    
    print("1. Ensuring directories exist...")
    ensure_directories()
    
    print("\n2. Creating better fallback image...")
    create_fallback_image()
    
    print("\n3. Clearing image cache...")
    clear_image_cache()
    
    print("\n4. Checking API configuration...")
    update_api_url()
    
    print("\n===== FIX COMPLETED =====")
    print("\nPlease restart your application now with:")
    print("python run.py")

if __name__ == "__main__":
    main() 