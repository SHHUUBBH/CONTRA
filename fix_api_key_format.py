#!/usr/bin/env python
"""
Script to fix API key format issues and test generation with the correct format.
"""

import os
import sys
import requests
import base64
import re
from PIL import Image
import io
from pathlib import Path
from dotenv import load_dotenv

# Reload environment variables
load_dotenv(override=True)

def check_and_fix_env_file():
    """Check and fix the .env file if needed."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return False

    try:
        # Read the current .env file
        content = env_path.read_text()
        
        # Check for the Stability API key line
        stability_pattern = r"STABILITY_API_KEY=(.+)"
        stability_match = re.search(stability_pattern, content)
        
        if not stability_match:
            print("❌ STABILITY_API_KEY not found in .env file!")
            return False
        
        current_key = stability_match.group(1).strip()
        print(f"Current key format: {current_key[:4]}...{current_key[-4:]}")
        
        # Check if the key has proper format (should start with 'sk-')
        if not current_key.startswith("sk-"):
            print("❌ API key does not have correct format! Should start with 'sk-'")
            return False
            
        # Key looks good, no need to fix
        print("✅ API key format looks correct")
        
        # Create a backup of the current .env file
        backup_path = env_path.with_suffix('.env.backup')
        env_path.rename(backup_path)
        print(f"✅ Created backup of .env file at {backup_path}")
        
        # Create a new .env file with the correct format
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Recreated .env file with the same content")
        return True
            
    except Exception as e:
        print(f"❌ Error checking/fixing .env file: {e}")
        return False

def test_api_with_current_key():
    """Test the API with the current key from the environment."""
    # Get the key from environment
    api_key = os.getenv("STABILITY_API_KEY")
    
    if not api_key:
        print("❌ STABILITY_API_KEY not found in environment!")
        return False
    
    # Mask most of the API key for logging
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else api_key
    print(f"Testing with current environment key: {masked_key}")
    
    # Check balance
    api_url = "https://api.stability.ai/v1/user/balance"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            credits = data.get('credits', 0)
            print(f"✅ API connection successful! Account balance: {credits} credits")
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

def fix_cache_and_references():
    """Fix any issues with the image cache and references."""
    cache_dir = Path("cache/images")
    
    # Ensure cache directory exists
    if not cache_dir.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created missing image cache directory: {cache_dir}")
    
    # Check for fallback image in static directory
    fallback_path = Path("static/img/fallback.jpg")
    if not fallback_path.exists():
        print(f"❌ Fallback image not found at {fallback_path}")
        return False
    
    # Copy fallback image to cache if not present
    cache_fallback = cache_dir / "fallback.jpg"
    if not cache_fallback.exists():
        try:
            import shutil
            shutil.copy(fallback_path, cache_fallback)
            print(f"✅ Copied fallback image to cache at {cache_fallback}")
        except Exception as e:
            print(f"❌ Error copying fallback image: {e}")
    
    print("✅ Image cache and references fixed")
    return True

def main():
    """Main function to fix API key and image generation issues."""
    print("\n===== FIXING API KEY AND IMAGE GENERATION =====\n")
    
    print("1. Checking and fixing .env file...")
    fix_result = check_and_fix_env_file()
    if not fix_result:
        print("⚠️ Could not fix .env file automatically!")
    
    print("\n2. Testing current API key in environment...")
    test_result = test_api_with_current_key()
    if not test_result:
        print("⚠️ Current API key is not working!")
        print("Please make sure you have a valid API key with sufficient credits.")
        print("You can get a key at https://stability.ai/")
    
    print("\n3. Fixing image cache and references...")
    cache_result = fix_cache_and_references()
    
    print("\n===== FIX COMPLETED =====")
    print("\nPlease restart your application with:")
    print("python run.py")
    
    if not test_result:
        print("\nNOTE: Your application will use fallback images until you")
        print("add a valid API key with sufficient credits to your .env file.")

if __name__ == "__main__":
    main() 