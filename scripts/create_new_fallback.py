#!/usr/bin/env python
"""
Script to create a new visually appealing fallback image.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_artistic_fallback_image(output_path, width=512, height=512):
    """Create a visually appealing fallback image."""
    try:
        # Create a gradient background
        img = Image.new('RGB', (width, height), color=(39, 41, 61))
        draw = ImageDraw.Draw(img)
        
        # Draw some shapes to make it look like an artistic image
        # Draw circles with gradients
        for i in range(5):
            x = 100 + i * 60
            y = 100 + i * 50
            radius = 50 + i * 10
            color = (100 + i * 30, 120 + i * 20, 200 - i * 10)
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
        
        # Draw some rectangles
        for i in range(3):
            x = 80 + i * 120
            y = 300 + i * 30
            width = 100 + i * 20
            height = 80 - i * 10
            color = (180 + i * 20, 100 + i * 30, 120 + i * 25)
            draw.rectangle((x, y, x+width, y+height), fill=color)
        
        # Add a small attribution text at the bottom
        try:
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font_small = ImageFont.load_default()
        
        draw.text((width//2, height-30), "AI art generation powered by Stability AI", 
                 fill=(200, 200, 220), font=font_small, anchor="ms")
        
        # Save the image
        img.save(output_path)
        logger.info(f"Created artistic fallback image at {output_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating fallback image: {e}")
        return False

def main():
    """Main function to create fallback images."""
    # Path to static/img directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
    
    # Path to fallback image
    fallback_path = os.path.join(static_dir, "fallback.jpg")
    
    # Create a new visually appealing fallback image
    create_artistic_fallback_image(fallback_path)
    
    logger.info(f"New fallback image created: {fallback_path}")
    logger.info("Restart your application to see the changes.")

if __name__ == "__main__":
    main() 