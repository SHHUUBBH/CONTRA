#!/usr/bin/env python
"""
Script to test the newly provided Stability AI API key directly.
"""

import requests
import base64
from PIL import Image
import io
from pathlib import Path

# The new API key to test
API_KEY = "sk-5pGu99fDGJYnBRGhb59wQ7jfQFaNs10ZMqpNWn4PRVFFoQw0"

def test_api_connection():
    """Test connection to the Stability API with the new key."""
    # Mask most of the API key for logging
    masked_key = API_KEY[:4] + "*" * (len(API_KEY) - 8) + API_KEY[-4:] if len(API_KEY) > 8 else API_KEY
    print(f"Testing Stability AI API with key: {masked_key}")
    
    # API endpoint to check account balance
    api_url = "https://api.stability.ai/v1/user/balance"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
    """Generate a minimal test image to verify API functionality."""
    # API endpoint for image generation
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Minimal payload to use the least amount of credits
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
                
                output_path = output_dir / "direct_test.png"
                
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
            except:
                print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating test image: {str(e)}")
        return False

def main():
    """Main function to test the API key."""
    print("\n===== TESTING NEW STABILITY AI API KEY =====\n")
    
    # Test API connection
    if test_api_connection():
        print("\n✅ API connection successful!")
        
        # Try to generate a minimal image
        if generate_minimal_test_image():
            print("\n✅ Image generation successful! Your new API key is working correctly.")
            print("\nNow restart your application with:")
            print("python run.py")
        else:
            print("\n❌ Image generation failed, but API connection works.")
            print("This might be due to insufficient credits or other API limitations.")
    else:
        print("\n❌ API connection test failed.")
        print("Please check your API key and internet connection.")
    
    print("\n===== TESTING COMPLETED =====\n")

if __name__ == "__main__":
    main() 