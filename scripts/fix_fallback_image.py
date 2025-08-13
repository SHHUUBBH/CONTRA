#!/usr/bin/env python
"""
Script to create a test pattern fallback image that will display reliably.
This creates a more visually distinct pattern with clear indicators that it's a fallback image.
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_pattern_image(output_path, width=512, height=512):
    """Create a test pattern image with clear visual elements."""
    try:
        # Create background
        img = Image.new('RGB', (width, height), color=(25, 25, 40))
        draw = ImageDraw.Draw(img)
        
        # Draw a grid pattern
        for x in range(0, width, 32):
            line_color = (60, 60, 80) if (x // 32) % 2 == 0 else (40, 40, 60)
            draw.line([(x, 0), (x, height)], fill=line_color, width=1)
            
        for y in range(0, height, 32):
            line_color = (60, 60, 80) if (y // 32) % 2 == 0 else (40, 40, 60)
            draw.line([(0, y), (width, y)], fill=line_color, width=1)
        
        # Draw colorful shapes for visual distinction
        # Center circles
        for i in range(4):
            radius = 180 - (i * 40)
            color = (
                200 - (i * 40),
                100 + (i * 30),
                150
            )
            draw.ellipse(
                (width//2 - radius, height//2 - radius, 
                 width//2 + radius, height//2 + radius), 
                outline=color, width=3
            )
        
        # Corner triangles
        triangle_size = 100
        # Top left
        draw.polygon([(0, 0), (triangle_size, 0), (0, triangle_size)], fill=(200, 50, 50))
        # Top right
        draw.polygon([(width, 0), (width-triangle_size, 0), (width, triangle_size)], fill=(50, 200, 50))
        # Bottom left
        draw.polygon([(0, height), (triangle_size, height), (0, height-triangle_size)], fill=(50, 50, 200))
        # Bottom right
        draw.polygon([(width, height), (width-triangle_size, height), (width, height-triangle_size)], fill=(200, 200, 50))
        
        # Add text
        try:
            try:
                font_large = ImageFont.truetype("arial.ttf", 36)
                font_medium = ImageFont.truetype("arial.ttf", 24)
            except:
                # Fallback to default font if arial not available
                font_large = ImageFont.load_default()
                font_medium = font_large
            
            # Draw text shadows for better visibility
            draw.text((width//2+2, height//2+2), "TEST IMAGE", 
                    font=font_large, fill=(0, 0, 0), anchor="mm")
            draw.text((width//2, height//2), "TEST IMAGE", 
                    font=font_large, fill=(255, 255, 255), anchor="mm")
            
            draw.text((width//2+2, height//2+52), "API KEY REQUIRED FOR REAL IMAGES", 
                    font=font_medium, fill=(0, 0, 0), anchor="mm")
            draw.text((width//2, height//2+50), "API KEY REQUIRED FOR REAL IMAGES", 
                    font=font_medium, fill=(220, 220, 100), anchor="mm")
            
        except Exception as e:
            logger.error(f"Error adding text to image: {e}")
        
        # Save the image
        img.save(output_path)
        logger.info(f"Created test pattern image at {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating test pattern image: {e}")
        return False

def main():
    """Replace the fallback image with a test pattern."""
    # Get the path to the static/img directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    # Path to fallback image
    fallback_jpg = os.path.join(static_dir, "fallback.jpg")
    
    # Create a backup of the existing fallback image if it exists
    if os.path.exists(fallback_jpg):
        backup_path = os.path.join(static_dir, "fallback_backup.jpg")
        try:
            import shutil
            shutil.copy2(fallback_jpg, backup_path)
            logger.info(f"Backed up existing fallback image to {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to backup existing fallback image: {e}")
    
    # Create the test pattern image as the new fallback
    created = create_test_pattern_image(fallback_jpg)
    
    if created:
        logger.info("✅ Successfully created test pattern fallback image")
        logger.info("Restart the application to see the changes")
    else:
        logger.error("❌ Failed to create test pattern fallback image")

if __name__ == "__main__":
    main() 