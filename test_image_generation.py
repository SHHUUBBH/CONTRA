#!/usr/bin/env python
"""
Test script to directly generate an image and ensure proper caching.
"""

import os
import sys
import requests
import base64
import hashlib
import time
from pathlib import Path
from PIL import Image
import io
from dotenv import load_dotenv

# Reload environment variables
load_dotenv(override=True)

def generate_test_image():
    """Generate a test image using the Stability API and save it to cache."""
    # Get API key from environment
    api_key = os.getenv("STABILITY_API_KEY")
    
    if not api_key:
        print("❌ No API key found in environment!")
        return False
    
    # Mask the key for logging
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else api_key
    print(f"Using API key: {masked_key}")
    
    # Create a test prompt
    test_prompt = "A beautiful landscape with mountains and lakes, digital art style"
    print(f"Using test prompt: '{test_prompt}'")
    
    # API endpoint for image generation
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Payload for the request
    payload = {
        "text_prompts": [
            {"text": test_prompt, "weight": 1.0}
        ],
        "height": 768,  # Using allowed SDXL dimensions that are close to 16:9 ratio
        "width": 1344,  # Using allowed SDXL dimensions that are close to 16:9 ratio
        "samples": 1,
        "cfg_scale": 7.0,
        "steps": 30
    }
    
    try:
        print("Sending request to Stability AI API...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # Check for errors
        if response.status_code != 200:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            return False
        
        # Parse the response
        data = response.json()
        
        # Check if the response contains artifacts
        if "artifacts" not in data or len(data["artifacts"]) == 0:
            print("❌ No artifacts found in response")
            print(f"Response data: {data}")
            return False
        
        # Get the generated image
        image_data = data["artifacts"][0]
        image_bytes = base64.b64decode(image_data["base64"])
        
        # Create a hash of the prompt for the filename
        prompt_hash = hashlib.sha256(test_prompt.encode('utf-8')).hexdigest()
        
        # Create paths for saving
        cache_dir = Path("cache/images")
        test_dir = Path("static/img/test")
        
        # Ensure directories exist
        cache_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Filenames
        cache_file = cache_dir / f"{prompt_hash}_test.png"
        test_file = test_dir / "direct_test_result.png"
        
        # Save to cache directory (for the app to find)
        with open(cache_file, 'wb') as f:
            f.write(image_bytes)
        print(f"✅ Saved image to cache at {cache_file}")
        
        # Also save to test directory (for inspection)
        with open(test_file, 'wb') as f:
            f.write(image_bytes)
        print(f"✅ Saved image to test directory at {test_file}")
        
        # Create a metadata file in the cache directory
        metadata_file = cache_dir / f"{prompt_hash}_test.json"
        import json
        metadata = {
            "prompt": test_prompt,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_url": api_url,
            "success": True
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Saved metadata to {metadata_file}")
        
        # Open the generated image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            print(f"✅ Generated image size: {width}x{height}")
        except Exception as e:
            print(f"❌ Error opening generated image: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function to test image generation."""
    print("\n===== TESTING IMAGE GENERATION =====\n")
    
    result = generate_test_image()
    
    if result:
        print("\n✅ Image generation successful!")
        print("\nYour API key is now working correctly and generating images.")
        print("The application should now be able to display generated images.")
        print("Refresh your browser and try generating content again.")
    else:
        print("\n❌ Image generation failed.")
        print("\nPlease check your API key and ensure:")
        print("1. The key is correctly formatted and valid")
        print("2. The account has sufficient credits")
        print("3. No other issues with the Stability AI API")
    
    print("\n===== TEST COMPLETED =====")

if __name__ == "__main__":
    main() 