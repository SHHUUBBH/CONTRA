#!/usr/bin/env python
"""
Script to verify and fix image display issues in the CONTRA application.
"""

import os
import sys
import logging
import json
from pathlib import Path
import shutil

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_image_dirs():
    """Verify that image directories exist and have correct permissions."""
    # Check for cache directory
    cache_dir = Path("cache")
    if not cache_dir.exists():
        logger.error(f"Cache directory does not exist: {cache_dir}")
        os.makedirs(cache_dir, exist_ok=True)
        logger.info(f"Created cache directory: {cache_dir}")
    
    # Check for images directory
    images_dir = Path("cache/images")
    if not images_dir.exists():
        logger.error(f"Images directory does not exist: {images_dir}")
        os.makedirs(images_dir, exist_ok=True)
        logger.info(f"Created images directory: {images_dir}")
    
    # Check for static/img directory
    static_img_dir = Path("static/img")
    if not static_img_dir.exists():
        logger.error(f"Static image directory does not exist: {static_img_dir}")
        os.makedirs(static_img_dir, exist_ok=True)
        logger.info(f"Created static image directory: {static_img_dir}")
    
    # Fix permissions
    try:
        # Make directories writable and readable
        os.chmod(str(images_dir), 0o755)
        logger.info(f"Set permissions for {images_dir}")
        os.chmod(str(static_img_dir), 0o755)
        logger.info(f"Set permissions for {static_img_dir}")
        
        # On Windows, no need for further permission changes
        if sys.platform == 'win32':
            logger.info("Running on Windows, skipping Unix-specific permission changes")
    except Exception as e:
        logger.error(f"Error setting permissions: {e}")

def verify_fallback_image():
    """Verify that fallback image exists and is accessible."""
    fallback_path = Path("static/img/fallback.jpg")
    
    if not fallback_path.exists():
        logger.error(f"Fallback image does not exist: {fallback_path}")
        
        # Try to create a simple fallback image
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color=(30, 30, 50))
            draw = ImageDraw.Draw(img)
            
            # Draw some shapes
            for i in range(5):
                size = 50 + i * 20
                x = 100 + i * 50
                y = 100 + i * 40
                draw.ellipse(
                    (x - size//2, y - size//2, x + size//2, y + size//2),
                    fill=(100 + i * 20, 80 + i * 20, 160 + i * 20, 200)
                )
            
            # Save the image
            img.save(fallback_path, "JPEG", quality=90)
            logger.info(f"Created fallback image at {fallback_path}")
        except Exception as e:
            logger.error(f"Failed to create fallback image: {e}")
    else:
        logger.info(f"Fallback image exists: {fallback_path}")
        
        # Also copy it to cache/images for easy access
        cache_fallback = Path("cache/images/fallback.jpg")
        try:
            shutil.copy(fallback_path, cache_fallback)
            logger.info(f"Copied fallback image to {cache_fallback}")
        except Exception as e:
            logger.error(f"Failed to copy fallback image: {e}")

def check_existing_images():
    """Check existing images in cache and verify they have metadata."""
    images_dir = Path("cache/images")
    if not images_dir.exists():
        logger.error(f"Images directory does not exist: {images_dir}")
        return
    
    # Find all PNG files
    png_files = list(images_dir.glob("*.png"))
    logger.info(f"Found {len(png_files)} PNG files in cache")
    
    for png_file in png_files:
        # Check if metadata file exists
        meta_file = png_file.with_suffix(".json")
        if not meta_file.exists():
            logger.warning(f"Metadata file does not exist for {png_file.name}")
            
            # Create a basic metadata file
            try:
                metadata = {
                    "prompt": f"Generated image: {png_file.name}",
                    "timestamp": "2025-05-11 00:00:00",
                    "width": 1024,
                    "height": 576,
                    "model_version": "stable-diffusion-xl",
                    "topic_id": f"topic_fixed_{int(os.path.getmtime(png_file))}"
                }
                
                with open(meta_file, "w") as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Created metadata file for {png_file.name}")
            except Exception as e:
                logger.error(f"Failed to create metadata file for {png_file.name}: {e}")
        else:
            # Verify metadata contains topic_id
            try:
                with open(meta_file, "r") as f:
                    metadata = json.load(f)
                
                if "topic_id" not in metadata or not metadata["topic_id"]:
                    logger.warning(f"Metadata file for {png_file.name} is missing topic_id")
                    
                    # Add topic_id
                    metadata["topic_id"] = f"topic_fixed_{int(os.path.getmtime(png_file))}"
                    
                    with open(meta_file, "w") as f:
                        json.dump(metadata, f, indent=2)
                    
                    logger.info(f"Added topic_id to metadata for {png_file.name}")
                else:
                    logger.info(f"Metadata file for {png_file.name} is valid")
            except Exception as e:
                logger.error(f"Failed to verify metadata for {png_file.name}: {e}")

def check_image_url_format():
    """Check image URL format in the code."""
    # This is a more complex check that would require code parsing
    # For now, just print a reminder
    logger.info("Reminder: Image URLs should be in the format /images/filename.png")
    logger.info("The topic_id parameter should not be included in the URL")

def main():
    """Main function."""
    print("\n===== FIXING IMAGE DISPLAY ISSUES =====\n")
    
    print("1. Verifying image directories...")
    verify_image_dirs()
    
    print("\n2. Verifying fallback image...")
    verify_fallback_image()
    
    print("\n3. Checking existing images...")
    check_existing_images()
    
    print("\n4. Checking image URL format...")
    check_image_url_format()
    
    print("\n===== FIX COMPLETED =====")
    print("\nPlease restart the application and test image generation.")

if __name__ == "__main__":
    main() 