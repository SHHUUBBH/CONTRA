#!/usr/bin/env python
"""
Script to test Stability AI API connection with a minimal prompt.
"""

import os
import sys
import requests
import base64
from PIL import Image
import io
from pathlib import Path

# Add the parent directory to the path so we can import from the application
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Import configuration
from config import APIConfig

def test_stability_api():
    """Test if we can connect to the Stability API with minimal credit usage."""
    # Get API key
    api_key = APIConfig.STABILITY_API_KEY
    
    if not api_key:
        print("❌ No Stability API key found in environment")
        return False
    
    # Mask most of the API key for logging
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else api_key
    print(f"Testing Stability AI API with key: {masked_key}")
    
    # Test endpoint to check account balance (doesn't cost credits)
    api_url = "https://api.stability.ai/v1/user/balance"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        # Make a request to check the account balance
        response = requests.get(api_url, headers=headers, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            credits = data.get('credits', 0)
            print(f"✅ API connection successful! Account balance: {credits} credits")
            
            # Check if there are enough credits
            if float(credits) < 0.01:
                print("⚠️ Warning: Account has very low credit balance. Image generation may fail.")
                return False
            return True
        else:
            print(f"❌ API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def generate_minimal_test_image():
    """
    Generate a minimal test image to verify API functionality.
    Uses the smallest possible size and steps to minimize credit usage.
    """
    # Get API key
    api_key = APIConfig.STABILITY_API_KEY
    
    # API endpoint for image generation
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Minimal payload to use the least amount of credits
    # Note: SDXL supports 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 640x1536, 768x1344, 832x1216, 896x1152
    payload = {
        "text_prompts": [
            {"text": "A simple blue square", "weight": 1.0}
        ],
        "height": 1024,  # Valid SDXL size
        "width": 1024,   # Valid SDXL size
        "samples": 1,
        "cfg_scale": 7.0,
        "steps": 10     # Minimum steps to reduce credit usage
    }
    
    try:
        print("Generating minimal test image...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if "artifacts" in data and len(data["artifacts"]) > 0:
                # Save the test image
                output_dir = Path("static/img/test")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = output_dir / "minimal_test.png"
                
                # Decode and save the image
                image_data = data["artifacts"][0]
                image_bytes = base64.b64decode(image_data["base64"])
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                print(f"✅ Test image generated successfully and saved to {output_path}")
                return True
            else:
                print("❌ No image data found in response")
                print(f"Response data: {data}")
                return False
        else:
            print(f"❌ Image generation failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
                
                # Check for insufficient balance
                if response.status_code == 429 and "insufficient_balance" in str(error_data):
                    print("\n⚠️ Your Stability AI account has insufficient balance.")
                    print("Please add credits to your account at https://stability.ai/")
                
            except:
                print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating test image: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== TESTING STABILITY AI API CONNECTION =====\n")
    
    # Test API connection
    if test_stability_api():
        print("\n✅ API connection test successful!")
        
        # Try to generate a minimal image
        if generate_minimal_test_image():
            print("\n✅ Image generation successful! Your API key is working correctly.")
            print("\nNow restart your application with:")
            print("python run.py")
        else:
            print("\n❌ Image generation failed, but API connection works.")
            print("This might be due to insufficient credits or other API limitations.")
            print("Check your account balance and try again with a different API key if needed.")
    else:
        print("\n❌ API connection test failed.")
        print("Please check your API key and internet connection.")
    
    print("\n===== TESTING COMPLETED =====\n") 