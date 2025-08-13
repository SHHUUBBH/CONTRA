#!/usr/bin/env python
"""
Script to test Stability AI API connectivity.
This helps debug whether the API key is working correctly.
"""

import os
import sys
import logging
import requests
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import from the application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import configuration
from config import APIConfig

def test_stability_api():
    """Test if we can connect to the Stability AI API."""
    # Get API key
    api_key = APIConfig.STABILITY_API_KEY
    
    if not api_key:
        logger.error("No Stability API key found in environment")
        return False
        
    if len(api_key) < 10:
        logger.error(f"API key seems too short ({len(api_key)} chars): {api_key[:3]}...")
        return False
        
    # Mask most of the API key for logging
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    logger.info(f"Testing Stability AI API with key: {masked_key}")
    
    # Test endpoint
    api_url = "https://api.stability.ai/v1/user/balance"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        # Make a simple request to check the account balance
        response = requests.get(api_url, headers=headers, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            logger.info(f"API connection successful! Account balance: {data.get('credits')} credits")
            return True
        else:
            logger.error(f"API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {error_data}")
            except:
                logger.error(f"Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def try_sample_generation():
    """Attempt to generate a simple test image."""
    # Get API key
    api_key = APIConfig.STABILITY_API_KEY
    
    if not api_key:
        logger.error("No Stability API key found in environment")
        return False
    
    # API endpoint for image generation
    api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Simple payload
    payload = {
        "text_prompts": [
            {"text": "Test image: a beautiful landscape, digital art", "weight": 1.0}
        ],
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "cfg_scale": 7.0,
        "steps": 30
    }
    
    try:
        logger.info("Attempting to generate a test image...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if "artifacts" in data and len(data["artifacts"]) > 0:
                # Save the test image
                import base64
                from PIL import Image
                import io
                
                output_dir = Path(__file__).resolve().parent.parent / "static" / "img" / "test"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = output_dir / "stability_test.png"
                
                # Decode and save the image
                image_data = data["artifacts"][0]
                image_bytes = base64.b64decode(image_data["base64"])
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                logger.info(f"Test image generated successfully and saved to {output_path}")
                return True
            else:
                logger.error("No artifacts found in response")
                logger.error(f"Response data: {data}")
                return False
        else:
            logger.error(f"Image generation failed with status {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {error_data}")
            except:
                logger.error(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error generating test image: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== TESTING STABILITY AI API CONNECTION =====\n")
    
    print("1. Checking environment variables...")
    stability_key = APIConfig.STABILITY_API_KEY
    if stability_key:
        masked_key = stability_key[:4] + "*" * (len(stability_key) - 8) + stability_key[-4:] if len(stability_key) > 8 else "INVALID"
        print(f"✓ Stability API Key found: {masked_key} (length: {len(stability_key)})")
    else:
        print("✗ No Stability API Key found in environment")
        print("  Please check your .env file or environment variables")
        sys.exit(1)
    
    print("\n2. Testing API connectivity...")
    if test_stability_api():
        print("✓ API connection successful!")
    else:
        print("✗ API connection failed")
        print("  Please check your API key and internet connection")
        sys.exit(1)
    
    print("\n3. Testing image generation...")
    if try_sample_generation():
        print("✓ Test image generated successfully!")
        print("  Your Stability AI API key is working correctly")
    else:
        print("✗ Test image generation failed")
        print("  API connectivity works but image generation failed")
        sys.exit(1)
    
    print("\n===== ALL TESTS PASSED SUCCESSFULLY =====")
    print("\nYour Stability AI API integration should be working correctly.")
    print("If you're still seeing fallback images, please restart your application")
    print("and check the logs for any other errors.") 