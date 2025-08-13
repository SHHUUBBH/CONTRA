#!/usr/bin/env python
"""
Script to update the fallback image to use a 16:9 aspect ratio.
"""

import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_16_9_fallback():
    """Create a fallback image with a 16:9 aspect ratio using SDXL-compatible dimensions."""
    # Paths for fallback images
    static_fallback = Path("static/img/fallback.jpg")
    cache_fallback = Path("cache/images/fallback.jpg")
    
    try:
        # Create a clean fallback image with SDXL-compatible dimensions (1344x768)
        width, height = 1344, 768
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
        
        # Draw some horizontal lines (like text)
        for i in range(10):
            y_pos = 350 + i * 15
            length = 100 + (i % 3) * 150
            draw.line(
                (50, y_pos, 50 + length, y_pos),
                fill=(220, 220, 240, 200),
                width=4
            )
        
        # Save to static directory
        img.save(static_fallback, "JPEG", quality=90)
        logger.info(f"Created 16:9 fallback image at {static_fallback}")
        
        # Also save to cache directory
        if not os.path.exists("cache/images"):
            os.makedirs("cache/images", exist_ok=True)
        img.save(cache_fallback, "JPEG", quality=90)
        logger.info(f"Created 16:9 fallback image at {cache_fallback}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating fallback image: {e}")
        return False

def update_low_credit_notice():
    """Update the low credit notice image to use SDXL-compatible dimensions."""
    low_credit_path = Path("static/img/low_credit_notice.jpg")
    
    try:
        # Create a image with SDXL-compatible dimensions (1344x768)
        width, height = 1344, 768
        img = Image.new('RGB', (width, height), color=(30, 30, 60))
        draw = ImageDraw.Draw(img)
        
        # Create a gradient background
        for y in range(height):
            r = int(30 + (y / height) * 20)
            g = int(30 + (y / height) * 10)
            b = int(60 + (y / height) * 40)
            for x in range(width):
                # Add some horizontal variation
                r_var = r + int((x / width) * 15)
                g_var = g + int((x / width) * 20)
                b_var = b + int((x / width) * 5)
                
                # Keep values in valid range
                r_val = max(0, min(255, r_var))
                g_val = max(0, min(255, g_var))
                b_val = max(0, min(255, b_var))
                
                draw.point((x, y), fill=(r_val, g_val, b_val))
        
        # Draw info box
        box_width, box_height = 600, 300
        box_x, box_y = (width - box_width) // 2, (height - box_height) // 2
        draw.rectangle(
            (box_x, box_y, box_x + box_width, box_y + box_height),
            fill=(40, 40, 70, 200),
            outline=(150, 150, 200, 250),
            width=2
        )
        
        # Save the image
        img.save(low_credit_path, "JPEG", quality=90)
        logger.info(f"Created 16:9 low credit notice image at {low_credit_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating low credit notice image: {e}")
        return False

def main():
    """Main function to update fallback images."""
    print("\n===== UPDATING FALLBACK IMAGES TO 16:9 RATIO =====\n")
    
    print("1. Creating 16:9 fallback image...")
    create_16_9_fallback()
    
    print("\n2. Creating 16:9 low credit notice image...")
    update_low_credit_notice()
    
    print("\n===== UPDATE COMPLETED =====")
    print("\nFallback images have been updated to 16:9 aspect ratio.")
    print("Please restart the application to see the changes.")

if __name__ == "__main__":
    main() 