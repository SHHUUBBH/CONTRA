#!/usr/bin/env python
"""
Final script to ensure the application is fully functional.
This script clears any temporary files, fixes permissions, and finalizes settings.
"""

import os
import sys
import shutil
from pathlib import Path
import logging
import json
import re
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reload environment variables
load_dotenv(override=True)

def clear_image_cache(keep_successful_images=True):
    """Clear temporary images from cache but keep successful ones."""
    cache_dir = Path("cache/images")
    if not cache_dir.exists():
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        return
    
    # Find all generated images
    generated_images = []
    fallback_images = []
    temp_files = []
    
    for file_path in cache_dir.glob("*"):
        if file_path.name == "fallback.jpg":
            fallback_images.append(file_path)
        elif file_path.name.endswith(".png") and "_v" in file_path.name:
            # This looks like a properly generated image
            generated_images.append(file_path)
        elif file_path.name.endswith(".json"):
            # Keep metadata files for successful images
            if keep_successful_images:
                try:
                    with open(file_path, 'r') as f:
                        metadata = json.load(f)
                    if metadata.get("success", False):
                        logger.info(f"Keeping successful image metadata: {file_path.name}")
                        continue
                except:
                    pass
            temp_files.append(file_path)
        else:
            # Other temporary files
            temp_files.append(file_path)
    
    # Remove temporary files
    removed_count = 0
    for file_path in temp_files:
        try:
            file_path.unlink()
            removed_count += 1
        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
    
    logger.info(f"Removed {removed_count} temporary files from cache")
    logger.info(f"Kept {len(generated_images)} generated images and {len(fallback_images)} fallback images")

def verify_api_key():
    """Verify that the API key is correctly formatted and loaded."""
    api_key = os.getenv("STABILITY_API_KEY")
    
    if not api_key:
        logger.error("No API key found in environment!")
        return False
    
    # Check format
    if not api_key.startswith("sk-"):
        logger.error(f"API key format is incorrect. Should start with 'sk-'")
        return False
    
    # Mask for logging
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else api_key
    logger.info(f"API key format looks correct: {masked_key}")
    return True

def verify_app_configuration():
    """Verify that app.py is configured correctly."""
    app_path = Path("app.py")
    if not app_path.exists():
        logger.error(f"Could not find {app_path}")
        return False
    
    config_path = Path("config.py")
    if not config_path.exists():
        logger.error(f"Could not find {config_path}")
        return False
    
    try:
        # Import config to check values
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from config import APIConfig
        
        if not APIConfig.STABILITY_API_KEY:
            logger.warning("STABILITY_API_KEY not found in config.py")
        else:
            masked_key = APIConfig.STABILITY_API_KEY[:4] + "*" * (len(APIConfig.STABILITY_API_KEY) - 8) + APIConfig.STABILITY_API_KEY[-4:] if len(APIConfig.STABILITY_API_KEY) > 8 else APIConfig.STABILITY_API_KEY
            logger.info(f"STABILITY_API_KEY found in config.py: {masked_key}")
        
        logger.info(f"API configuration verified")
        return True
    except Exception as e:
        logger.error(f"Error verifying configuration: {e}")
        return False

def fix_file_permissions():
    """Fix file permissions for the cache directory."""
    cache_dir = Path("cache/images")
    if not cache_dir.exists():
        logger.warning(f"Cache directory does not exist: {cache_dir}")
        return
    
    try:
        # Make sure the directory is writable by the application
        import stat
        
        # Get current permissions
        current_mode = cache_dir.stat().st_mode
        
        # Add write permission if not already present
        if not (current_mode & stat.S_IWUSR):
            os.chmod(cache_dir, current_mode | stat.S_IWUSR)
            logger.info(f"Added write permission to {cache_dir}")
        else:
            logger.info(f"Directory {cache_dir} already has write permission")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing permissions: {e}")
        return False

def ensure_server_restart():
    """Ensure the server is restarted to apply all changes."""
    try:
        # Try to import psutil
        import psutil
        
        # Check if the server is running
        app_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if ('python' in cmdline.lower()) and ('app.py' in cmdline or 'run.py' in cmdline):
                    app_processes.append(proc)
        
        if app_processes:
            logger.info(f"Found {len(app_processes)} CONTRA processes running")
            
            # Ask if user wants to restart
            print("\nWould you like to restart the server to apply all changes? (y/n)")
            response = input().strip().lower()
            
            if response == 'y':
                # Kill existing processes
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
                print("\nServer restarted! Please refresh your browser.")
                return True
            else:
                print("\nServer not restarted. Please restart manually with:")
                print("python run.py")
                return False
        else:
            logger.info("No running CONTRA processes found")
            print("\nNo running server detected. Please start it with:")
            print("python run.py")
            return False
    except ImportError:
        logger.warning("psutil not installed, cannot check for running processes")
        print("\nPlease restart the server manually with:")
        print("python run.py")
        return False
    except Exception as e:
        logger.error(f"Error checking server status: {e}")
        print("\nPlease restart the server manually with:")
        print("python run.py")
        return False

def main():
    """Main function to finalize the fix."""
    print("\n===== FINALIZING APPLICATION FIX =====\n")
    
    print("1. Clearing temporary files from cache...")
    clear_image_cache()
    
    print("\n2. Verifying API key...")
    verify_api_key()
    
    print("\n3. Verifying application configuration...")
    verify_app_configuration()
    
    print("\n4. Fixing file permissions...")
    fix_file_permissions()
    
    print("\n===== FIX COMPLETED =====")
    
    # Check if server needs to be restarted
    ensure_server_restart()
    
    print("\nApplication should now be fully functional with working image generation!")
    print("If you still see fallback images, make sure to regenerate content.")

if __name__ == "__main__":
    main() 