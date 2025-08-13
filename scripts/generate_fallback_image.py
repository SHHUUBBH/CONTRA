#!/usr/bin/env python
"""
Script to generate and check the fallback image for the CONTRA application.
This will create a new version of the fallback image with visible text.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_text_fallback_image(output_path, width=512, height=512):
    """Create a fallback image with visible text explaining the issue."""
    try:
        # Create a dark background image
        img = Image.new('RGB', (width, height), color=(39, 41, 61))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, falling back to default if necessary
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 18)
        except:
            font_large = ImageFont.load_default()
            font_small = font_large
            
        # Add text to the image
        draw.text((width//2, height//3), "Image Not Available", fill=(255, 255, 255), 
                 font=font_large, anchor="mm")
        draw.text((width//2, height//2), "Please set STABILITY_API_KEY", fill=(255, 200, 100), 
                 font=font_small, anchor="mm")
        draw.text((width//2, height//2 + 50), "in your environment variables", fill=(255, 200, 100), 
                 font=font_small, anchor="mm")
        
        # Save the image
        img.save(output_path)
        logger.info(f"Created fallback image with text at {output_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating fallback image: {e}")
        return False

def main():
    """Main function to create fallback images."""
    # Create fallback image in static/img directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    fallback_path = os.path.join(static_dir, "fallback.jpg")
    
    # Create a new test image beside the original
    test_fallback_path = os.path.join(static_dir, "fallback_test.jpg")
    
    # Generate the test fallback image
    create_text_fallback_image(test_fallback_path)
    
    # Show image info
    if os.path.exists(fallback_path):
        try:
            with Image.open(fallback_path) as img:
                logger.info(f"Original fallback image: {fallback_path}")
                logger.info(f"  Size: {img.size}")
                logger.info(f"  Format: {img.format}")
                logger.info(f"  Mode: {img.mode}")
        except Exception as e:
            logger.error(f"Error inspecting original fallback image: {e}")
    else:
        logger.warning(f"Original fallback image does not exist: {fallback_path}")
        
    # Note to view the test image
    logger.info(f"Test fallback image created: {test_fallback_path}")
    logger.info(f"Compare the two images to see if your fallback image matches the expected format.")

if __name__ == "__main__":
    main() 