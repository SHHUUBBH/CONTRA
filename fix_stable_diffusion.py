#!/usr/bin/env python
"""
Script to fix the stable_diffusion.py file to ensure proper image display.
"""

import os
import logging
import re
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_url_paths_in_stable_diffusion():
    """Fix URL paths in the stable_diffusion.py file."""
    file_path = Path("services/stable_diffusion.py")
    
    if not file_path.exists():
        logger.error(f"Could not find {file_path}")
        return False
    
    try:
        # Read the content
        content = file_path.read_text()
        
        # Patterns to fix
        # 1. Fix image URLs to ensure they're properly formatted
        old_url_pattern = r'"url": "[^"]*fallback\.jpg"'
        new_url = '"url": "/images/fallback.jpg"'
        
        # Apply fixes
        if re.search(old_url_pattern, content):
            # Replace all instances
            content = re.sub(old_url_pattern, new_url, content)
            logger.info("Fixed fallback image URL paths")
        
        # 2. Ensure image paths are correct for static files
        old_direct_static = r'"/direct-static/img/'
        new_direct_static = '"/images/'
        
        if old_direct_static in content:
            content = content.replace(old_direct_static, new_direct_static)
            logger.info("Fixed direct-static paths to use /images/")
        
        # Write the updated content
        file_path.write_text(content)
        logger.info(f"Successfully updated {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating stable_diffusion.py: {e}")
        return False

def fix_app_image_routes():
    """Fix image routes in app.py to ensure proper image serving."""
    file_path = Path("app.py")
    
    if not file_path.exists():
        logger.error(f"Could not find {file_path}")
        return False
    
    try:
        # Read the content
        content = file_path.read_text()
        
        # Check if the images blueprint has the correct route
        images_bp_pattern = r"images_bp = Blueprint\('images', __name__, url_prefix='/images'\)"
        
        if not re.search(images_bp_pattern, content):
            logger.warning("Could not find images blueprint with correct route, may need manual fix")
        else:
            logger.info("Images blueprint route looks correct")
        
        # Check the serve_image function to make sure it handles fallback correctly
        serve_image_pattern = r"@images_bp\.route\('/<path:filename>'\)\s*def serve_image\(filename\):"
        
        if not re.search(serve_image_pattern, content):
            logger.warning("Could not find serve_image route function, may need manual fix")
        else:
            logger.info("serve_image route function found")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking app.py: {e}")
        return False

def ensure_static_directories():
    """Ensure all static directories exist and contain necessary files."""
    # Create directories if needed
    dirs_to_ensure = [
        "static",
        "static/img",
        "cache",
        "cache/images"
    ]
    
    for directory in dirs_to_ensure:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        else:
            logger.info(f"Directory already exists: {directory}")
    
    # Ensure fallback image exists in both static and cache directories
    fallback_static = Path("static/img/fallback.jpg")
    fallback_cache = Path("cache/images/fallback.jpg")
    
    # If fallback image exists in static but not in cache, copy it
    if fallback_static.exists() and not fallback_cache.exists():
        try:
            import shutil
            shutil.copy(fallback_static, fallback_cache)
            logger.info(f"Copied fallback image from {fallback_static} to {fallback_cache}")
        except Exception as e:
            logger.error(f"Error copying fallback image: {e}")
    
    # If fallback image doesn't exist in static, create a basic one
    if not fallback_static.exists():
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple colored image
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
            
            # Save the fallback image
            img.save(fallback_static, "JPEG", quality=95)
            logger.info(f"Created fallback image at {fallback_static}")
            
            # Also save to cache
            img.save(fallback_cache, "JPEG", quality=95)
            logger.info(f"Created fallback image at {fallback_cache}")
            
        except Exception as e:
            logger.error(f"Error creating fallback image: {e}")
    
    return True

def restart_server():
    """Function to restart the Flask server."""
    try:
        # Check if the server is running
        import psutil
        
        # Find any Python processes running app.py or run.py
        app_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if ('python' in cmdline.lower()) and ('app.py' in cmdline or 'run.py' in cmdline):
                    app_processes.append(proc)
        
        # Kill any found processes
        if app_processes:
            logger.info(f"Found {len(app_processes)} CONTRA processes running")
            for proc in app_processes:
                try:
                    proc.terminate()
                    logger.info(f"Terminated process {proc.info['pid']}")
                except Exception as e:
                    logger.error(f"Error terminating process {proc.info['pid']}: {e}")
        
        # Start the server again
        import subprocess
        subprocess.Popen(["python", "run.py"], shell=True)
        logger.info("Started server with python run.py")
        return True
        
    except ImportError:
        logger.warning("psutil not installed, cannot automatically restart server")
        return False
    except Exception as e:
        logger.error(f"Error restarting server: {e}")
        return False

def main():
    """Main function to fix the stable_diffusion.py file."""
    print("\n===== FIXING STABLE DIFFUSION AND IMAGE DISPLAY =====\n")
    
    print("1. Fixing URL paths in stable_diffusion.py...")
    sd_fix_result = fix_url_paths_in_stable_diffusion()
    
    print("\n2. Checking app.py image routes...")
    app_fix_result = fix_app_image_routes()
    
    print("\n3. Ensuring static directories and files...")
    dirs_result = ensure_static_directories()
    
    print("\n===== FIX COMPLETED =====")
    
    print("\nWould you like to restart the server now? (y/n)")
    response = input()
    if response.lower() == 'y':
        print("\nRestarting server...")
        restart_server()
        print("\nServer restarted! Please refresh your browser.")
    else:
        print("\nPlease restart your application manually with:")
        print("python run.py")

if __name__ == "__main__":
    main() 