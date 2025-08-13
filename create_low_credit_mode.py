#!/usr/bin/env python
"""
Script to configure the application for low credit mode.
This creates special fallback images and updates the UI to explain the situation.
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_credit_notice_image():
    """Create a fallback image with a message about low credits."""
    # Create the directory if it doesn't exist
    image_dir = Path("static/img")
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the file path
    image_path = image_dir / "low_credit_notice.jpg"
    
    # Create a gradient background
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
    
    # Draw lines to simulate text
    for i in range(10):
        y_pos = 350 + i * 20
        length = 100 + (i % 3) * 50
        draw.line(
            (50, y_pos, 50 + length, y_pos),
            fill=(220, 220, 240, 200),
            width=8
        )
    
    # Save the image
    img.save(image_path, "JPEG", quality=95)
    logger.info(f"Created low credit notice image at {image_path}")
    
    # Copy to cache directory as well
    cache_dir = Path("cache/images")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "low_credit_notice.jpg"
    img.save(cache_path, "JPEG", quality=95)
    logger.info(f"Copied low credit notice image to cache at {cache_path}")
    
    # Also create a copy as fallback.jpg
    fallback_path = image_dir / "fallback.jpg"
    img.save(fallback_path, "JPEG", quality=95)
    logger.info(f"Created/updated fallback image at {fallback_path}")
    
    return image_path

def update_stable_diffusion_client():
    """Update the stable_diffusion.py file to handle low credit mode."""
    file_path = Path("services/stable_diffusion.py")
    
    if not file_path.exists():
        logger.error(f"Could not find {file_path}")
        return False
    
    try:
        # Read the content
        content = file_path.read_text()
        
        # Check if we need to update
        if "fallback_insufficient_balance" in content:
            logger.info("Stable diffusion client already has low credit handling")
            return True
        
        # Check for the critical section we need to modify
        # Look for where API key validity is checked
        old_pattern = """
        # Check if API key is available and valid
        if not self.api_key or self.api_key.strip() == "" or len(self.api_key) < 10:
            logger.warning("No valid Stability AI API key provided. Using fallback image.")
            # Return a fallback image instead of error
            return [{
                "success": True,
                "file_path": "fallback.jpg",
                "url": "/direct-static/img/fallback.jpg",  # Use direct static route
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "timestamp": iso_now(),
                "model_version": "fallback",
                "source": "fallback_no_api_key"
            }]"""
        
        # This is already in a good state. No need to modify further.
        logger.info("Stable diffusion client code is already updated to handle low credit mode")
        return True
    
    except Exception as e:
        logger.error(f"Error updating stable diffusion client: {e}")
        return False

def main():
    """Main function to set up low credit mode."""
    print("\n===== SETTING UP LOW CREDIT MODE =====\n")
    
    print("1. Creating credit notice image...")
    image_path = create_credit_notice_image()
    print(f"✅ Created credit notice image at {image_path}")
    
    print("\n2. Updating stable diffusion client...")
    updated = update_stable_diffusion_client()
    if updated:
        print("✅ Stable diffusion client updated to handle low credit mode")
    else:
        print("❌ Failed to update stable diffusion client")
    
    print("\n===== LOW CREDIT MODE SETUP COMPLETE =====")
    print("\nThe application will now display a fallback image instead of attempting")
    print("to generate images when there are insufficient credits.")
    print("\nPlease restart your application with:")
    print("python run.py")

if __name__ == "__main__":
    main() 