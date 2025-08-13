#!/usr/bin/env python
"""
Script to update the Stability AI API endpoint in the stable_diffusion.py file.
This helps resolve issues with image generation using newer models.
"""

import logging
import re
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_api_endpoint():
    """Update the Stability AI API endpoint in the stable_diffusion.py file."""
    stable_diffusion_path = Path("services/stable_diffusion.py")
    
    if not stable_diffusion_path.exists():
        logger.error(f"Could not find {stable_diffusion_path}")
        return False
    
    try:
        # Read the file
        content = stable_diffusion_path.read_text()
        
        # Current endpoint pattern
        old_endpoint_pattern = r'self\.api_url\s*=\s*"https://api\.stability\.ai/v1/generation/[^"]+/text-to-image"'
        
        # New endpoint for stable-diffusion-v3
        new_endpoint = 'self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"'
        
        # Check if we need to update
        if re.search(old_endpoint_pattern, content):
            # Replace the endpoint
            updated_content = re.sub(old_endpoint_pattern, new_endpoint, content)
            
            # Write the updated file
            stable_diffusion_path.write_text(updated_content)
            
            logger.info("Successfully updated API endpoint in stable_diffusion.py")
            return True
        else:
            logger.info("API endpoint not found or already updated")
            return False
            
    except Exception as e:
        logger.error(f"Error updating API endpoint: {e}")
        return False

def main():
    """Main function to update the Stability AI API endpoint."""
    print("\n===== UPDATING STABILITY AI API ENDPOINT =====\n")
    
    success = update_api_endpoint()
    
    if success:
        print("\n✅ API endpoint updated successfully!")
    else:
        print("\n⚠️ API endpoint update failed or was not needed.")
    
    print("\nPlease run the following command to apply all fixes:")
    print("python create_better_fallback.py")
    print("\nThen restart your application with:")
    print("python run.py")

if __name__ == "__main__":
    main() 