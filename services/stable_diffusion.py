"""
Stable Diffusion API client service for image generation.
"""

import os
import logging
import requests
import hashlib
import time
import base64
import io
import textwrap
import shutil
import json
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from config import APIConfig, IMAGE_CACHE_DIR
from utils.cache import disk_cache
from utils.helpers import sanitize_filename, iso_now

# Configure logging
logger = logging.getLogger(__name__)

class StableDiffusionClient:
    """
    Client for Stability AI's API for Stable Diffusion 3.5.
    
    This client manages:
    - Connection to Stability AI API
    - Prompt engineering for effective image generation
    - Caching of generated images
    - Image metadata
    """
    
    def __init__(
        self, 
        model_version: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Stable Diffusion client.
        
        Args:
            model_version: Version of Stable Diffusion being used
            api_key: Optional API key override (otherwise uses from config)
        """
        self.model_version = model_version or APIConfig.SD_MODEL_VERSION
        self.api_key = api_key or APIConfig.STABILITY_API_KEY
        self.endpoint = None  # Keep for backward compatibility
        
        # API endpoint for Stability AI - default to SDXL as it's widely supported
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        # Check if we should use a different model - make sure the model ID is valid
        # As of the current API, "stable-diffusion-3-large" is not valid, use SDXL instead
        if "3.5" in self.model_version:
            # For compatibility with future models, log a note
            logger.info(f"Note: Using SDXL model instead of {self.model_version} as it's not yet available in the API")
            self.model_version = "stable-diffusion-xl"
        
        # Ensure cache directory exists
        if not os.path.exists(IMAGE_CACHE_DIR):
            try:
                os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
                logger.info(f"Created image cache directory: {IMAGE_CACHE_DIR}")
            except Exception as e:
                logger.error(f"Failed to create image cache directory: {e}")
                
        # Create a placeholder/fallback image in static directory
        self._ensure_fallback_image()
        
        # Log API key status - don't log the actual key for security
        if not self.api_key:
            logger.warning("No Stability AI API key provided. Image generation will fall back to test images.")
        elif len(self.api_key) < 10:  # A simple check to see if the API key is too short
            logger.warning(f"Stability AI API key looks invalid (too short). Image generation may fail.")
        else:
            # Mask most of the API key for logging
            masked_key = self.api_key[:4] + "*" * (len(self.api_key) - 8) + self.api_key[-4:]
            logger.info(f"Stability AI client initialized with model: {self.model_version} and API key: {masked_key}")
    
    def _ensure_fallback_image(self):
        """Ensure a fallback image exists in the static directory with SDXL-compatible dimensions."""
        static_img_dir = Path("static/img")
        fallback_img = static_img_dir / "fallback.jpg"
        
        # Create static/img directory if it doesn't exist
        if not static_img_dir.exists():
            try:
                os.makedirs(static_img_dir, exist_ok=True)
                logger.info(f"Created static image directory: {static_img_dir}")
            except Exception as e:
                logger.error(f"Failed to create static image directory: {e}")
                return
                
        # Check if fallback image already exists
        if not fallback_img.exists():
            try:
                # Create a simple gradient background with SDXL-compatible dimensions
                width, height = 1344, 768  # SDXL-compatible dimensions (close to 16:9 ratio)
                image = Image.new('RGB', (width, height), (30, 30, 50))
                draw = ImageDraw.Draw(image)
                
                # Create a simple gradient background
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
                
                # Draw a simple text-like pattern (no font needed)
                for i in range(10):
                    y_pos = 350 + i * 15  # Adjusted spacing for 16:9
                    length = 100 + (i % 3) * 150  # Longer lines for wider image
                    draw.line(
                        (50, y_pos, 50 + length, y_pos),
                        fill=(220, 220, 240, 200),
                        width=4
                    )
                
                # Save the image
                image.save(fallback_img, "JPEG", quality=90)
                logger.info(f"Created 16:9 fallback image at {fallback_img}")
            except Exception as e:
                logger.error(f"Error creating fallback image: {e}")
                
                # Try an even simpler fallback if the gradient fails
                try:
                    # Create a solid color image as absolute fallback with SDXL-compatible dimensions
                    Image.new('RGB', (1344, 768), (50, 100, 150)).save(fallback_img, "JPEG")
                    logger.info("Created simple solid color fallback image with SDXL-compatible dimensions")
                except Exception as e2:
                    logger.error(f"Failed to create simple fallback image: {e2}")
                    return
                
        # Also copy to cache/images for easy access
        try:
            cache_dir = Path("cache/images")
            if not cache_dir.exists():
                os.makedirs(cache_dir, exist_ok=True)
            
            cache_fallback = cache_dir / "fallback.jpg"
            if not cache_fallback.exists() or not os.path.samefile(fallback_img, cache_fallback):
                shutil.copy(fallback_img, cache_fallback)
                logger.info(f"Copied fallback image to {cache_fallback}")
        except Exception as e:
            logger.warning(f"Could not copy fallback image to cache: {e}")
    
    def _hash_prompt(self, prompt: str, **params) -> str:
        """
        Generate a consistent hash for caching based on prompt and parameters.
        
        Args:
            prompt: The image generation prompt
            **params: Additional parameters that affect generation
            
        Returns:
            A hexadecimal string hash
        """
        # Combine prompt with relevant parameters
        hashable = prompt
        if params:
            # Add relevant parameters to the hash input
            relevant_params = {
                k: v for k, v in params.items() 
                if k in ['width', 'height', 'seed', 'negative_prompt', 'style', 'topic_id']
            }
            hashable += str(relevant_params)
            
        # Create a SHA-256 hash
        return hashlib.sha256(hashable.encode('utf-8')).hexdigest()
    
    def _cache_path(self, prompt_hash: str, variant: int = 1) -> Path:
        """
        Compute file path for a given prompt hash and variant number.
        
        Args:
            prompt_hash: Hash of the prompt and parameters
            variant: Image variant number
            
        Returns:
            Path to the cached image file
        """
        # Create the path using the hash and variant
        cache_path = IMAGE_CACHE_DIR / f"{prompt_hash}_v{variant}.png"
        
        # Log the cache path being generated
        logger.info(f"Generated cache path: {cache_path}")
        
        return cache_path
    
    def build_prompt(
        self,
        topic: str,
        context_text: str = "",
        style: str = "photorealistic",
        emotion: Optional[str] = None,
        headlines: Optional[List[str]] = None,
        tone: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Build a rich text prompt for Stable Diffusion.
        
        Args:
            topic: Main subject/topic
            context_text: Additional contextual information
            style: Artistic style (e.g., "oil painting", "watercolor")
            emotion: Emotional tone (e.g., "somber", "triumphant")
            headlines: List of news headlines for context
            tone: Narrative tone (e.g., "informative", "dramatic", "poetic")
            temperature: Creativity level (0.1-1.0, higher = more creative)
            
        Returns:
            Formatted prompt string
        """
        parts = [f"{topic}, {style}"]
        
        # Add emotion if provided
        if emotion:
            parts.append(f"evoking {emotion} emotion")
        
        # Add tone-specific elements to enhance image style
        if tone:
            tone_enhancements = {
                "dramatic": "high contrast, dramatic lighting, cinematic composition, evocative",
                "poetic": "soft lighting, ethereal atmosphere, dreamlike quality, artistic composition",
                "humorous": "vibrant colors, exaggerated features, playful elements, lighthearted",
                "technical": "precise details, clean lines, organized composition, technical accuracy",
                "simple": "clean background, minimal elements, clear focus, uncluttered",
                "informative": "clear details, balanced composition, realistic lighting, educational"
            }
            
            if tone.lower() in tone_enhancements:
                parts.append(tone_enhancements[tone.lower()])
        
        # Add minimal contextual cues from context text
        if context_text:
            # Limit context to avoid word salad
            parts.append(textwrap.shorten(context_text, width=100, placeholder="..."))
        
        # Include up to 3 headlines if provided
        if headlines:
            for h in headlines[:3]:
                parts.append(f"headline: {h}")
        
        # Add quality enhancers - updated for SD 3.5
        parts.append("masterpiece, detailed, high resolution, beautiful lighting")
        
        # Add temperature-based creative elements
        if temperature > 0.7:
            # High temperature - add more creative elements
            creative_elements = [
                "intricate details",
                "captivating composition", 
                "artistic vision", 
                "stunning",
                "award-winning photography"
            ]
            # Select a subset based on temperature
            num_to_add = min(5, int(2 + (temperature - 0.7) * 10))  # 2-5 elements
            parts.extend(creative_elements[:num_to_add])
        
        # Combine into final prompt
        return ", ".join(parts)
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted, disfigured, deformed, ugly, poor details, extra limbs, malformed hands, six fingers, extra fingers, fused fingers, mutated hands, bad anatomy, poorly drawn face, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad proportions, gross proportions",
        width: int = 1024,
        height: int = 576,  # Changed default from 1024 to 576 for 16:9 aspect ratio
        num_variants: int = 1,
        seed: Optional[int] = None,
        overwrite_cache: bool = False,
        topic_id: Optional[str] = None  # Added topic_id parameter for tracking current topic
    ) -> List[Dict[str, Any]]:
        """
        Generate one or more image variants for the given prompt using Stability AI API.
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Text to discourage in the generation
            width: Image width in pixels
            height: Image height in pixels
            num_variants: Number of image variants to generate
            seed: Random seed for reproducibility (None for random)
            overwrite_cache: Whether to overwrite cached images
            topic_id: Identifier for the current topic (used for tracking/display)
            
        Returns:
            List of dictionaries with image metadata
        """
        results = []
        
        # Check if API key is available and valid
        if not self.api_key or self.api_key.strip() == "" or len(self.api_key) < 10:
            logger.warning("No valid Stability AI API key provided. Using fallback image.")
            # Return a fallback image instead of error
            return [{
                "success": True,
                "file_path": "fallback.jpg",
                "url": "/images/fallback.jpg",  # Use direct static route
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "timestamp": iso_now(),
                "model_version": "fallback",
                "source": "fallback_no_api_key",
                "topic_id": topic_id  # Store topic ID in metadata
            }]
        
        # Enforce 16:9 aspect ratio if not already set (and make divisible by 8)
        if width / height != 16 / 9:
            # SDXL allowed dimensions that are approximately 16:9
            # Valid pairs are: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 640x1536, 768x1344, 832x1216, 896x1152
            # Choose closest to 16:9 ratio: 1344x768 or 1536x640
            if width >= 1536:
                width, height = 1536, 640
            else:
                width, height = 1344, 768
            
            logger.info(f"Adjusting dimensions to use SDXL-compatible aspect ratio: {width}x{height}")
        
        # Ensure dimensions are valid for SDXL
        # Valid pairs are: 1024x1024, 1152x896, 1216x832, 1344x768, 1536x640, 640x1536, 768x1344, 832x1216, 896x1152
        valid_dimensions = [
            (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640),
            (640, 1536), (768, 1344), (832, 1216), (896, 1152)
        ]
        
        # Find closest valid dimensions
        if (width, height) not in valid_dimensions:
            # Default to 1344x768 if not valid
            width, height = 1344, 768
            logger.info(f"Using default SDXL-compatible dimensions: {width}x{height}")
        
        # Ensure dimensions are multiples of 8 (required by Stability API)
        width = (width // 8) * 8
        height = (height // 8) * 8
        
        # Hash prompt and parameters for caching
        param_dict = {
            'width': width,
            'height': height,
            'negative_prompt': negative_prompt,
            'seed': seed,
            'topic_id': topic_id  # Include topic_id in hash to avoid mixing topics
        }
        prompt_hash = self._hash_prompt(prompt, **param_dict)
        
        # Check for existing cached images
        has_any_cached = False
        for i in range(1, num_variants + 1):
            cache_file = self._cache_path(prompt_hash, i)
            if cache_file.exists():
                has_any_cached = True
                break
        
        # Generate each variant
        for i in range(1, num_variants + 1):
            cache_file = self._cache_path(prompt_hash, i)
            
            # Check if cached version exists
            if cache_file.exists() and not overwrite_cache:
                logger.info(f"Loading cached image for variant {i}")
                results.append({
                    "success": True,
                    "file_path": str(cache_file),
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": width,
                    "height": height,
                    "timestamp": iso_now(),
                    "model_version": self.model_version,
                    "source": "cache",
                    "topic_id": topic_id  # Store topic ID in metadata
                })
                continue
            
            try:
                logger.info(f"Generating image variant {i} with Stability AI for prompt: {prompt[:50]}...")
                
                # Setup headers for Stability API
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                # Create payload for the request
                payload = {
                    "text_prompts": [
                        {"text": prompt, "weight": 1.0}
                    ],
                    "height": height,
                    "width": width,
                    "samples": 1,
                    "cfg_scale": 7.0,
                    "steps": 30
                }
                
                # Add negative prompts if provided
                if negative_prompt:
                    payload["text_prompts"].append({
                        "text": negative_prompt,
                        "weight": -1.0
                    })
                
                # Add seed if provided
                if seed is not None:
                    payload["seed"] = seed
                
                # Make the API request
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120  # 2 minute timeout
                )
                
                # Check for API error
                response.raise_for_status()
                
                # Parse the response
                data = response.json()
                
                # Check if the response contains artifacts
                if "artifacts" not in data or len(data["artifacts"]) == 0:
                    error_msg = data.get("message", "Unknown error from Stability API")
                    logger.error(f"Stability API error: {error_msg}")
                    results.append({
                        "success": False,
                        "error": f"Stability API error: {error_msg}",
                        "variant": i
                    })
                    continue
                
                # Get the generated image
                image_data = data["artifacts"][0]
                image_bytes = base64.b64decode(image_data["base64"])
                
                # Load image to validate and get dimensions
                image = Image.open(io.BytesIO(image_bytes))
                actual_width, actual_height = image.size
                
                # Save image to cache
                with open(cache_file, 'wb') as f:
                    f.write(image_bytes)
                
                logger.info(f"Saved image variant {i} to {cache_file}")
                
                # Add to results
                results.append({
                    "success": True,
                    "file_path": str(cache_file),
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "width": actual_width,
                    "height": actual_height,
                    "timestamp": iso_now(),
                    "model_version": self.model_version,
                    "source": "api",
                    "topic_id": topic_id,  # Store topic ID in metadata
                    "url": f"/images/{cache_file.name}"  # Add direct URL to make it easier to access
                })
                
                # Also save metadata to a separate JSON file for easier retrieval
                try:
                    metadata_file = Path(str(cache_file).replace('.png', '.json'))
                    with open(metadata_file, 'w') as f:
                        json.dump({
                            "prompt": prompt,
                            "timestamp": iso_now(),
                            "width": actual_width,
                            "height": actual_height,
                            "model_version": self.model_version,
                            "topic_id": topic_id
                        }, f, indent=2)
                    logger.info(f"Saved metadata to {metadata_file}")
                except Exception as e:
                    logger.error(f"Error saving metadata: {e}")
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"Stability AI API HTTP error: {str(e)}")
                
                # Check for insufficient balance error (status code 429)
                if hasattr(e, 'response') and e.response.status_code == 429:
                    try:
                        error_data = e.response.json()
                        if 'name' in error_data and error_data['name'] == 'insufficient_balance':
                            logger.warning("Insufficient balance in Stability AI account")
                            
                            # Create a special fallback for insufficient balance
                            results.append({
                                "success": True,
                                "file_path": "fallback.jpg",
                                "url": "/images/fallback.jpg",
                                "prompt": prompt,
                                "error_details": "Insufficient balance in Stability AI account. Please add credits to generate images.",
                                "width": width,
                                "height": height,
                                "timestamp": iso_now(),
                                "model_version": "fallback",
                                "source": "fallback_insufficient_balance",
                                "topic_id": topic_id  # Store topic ID in metadata
                            })
                            continue
                    except Exception:
                        pass
                
                # If we have cached images, use as fallback
                if has_any_cached:
                    for alt_i in range(1, num_variants + 1):
                        alt_cache = self._cache_path(prompt_hash, alt_i)
                        if alt_cache.exists():
                            logger.info(f"Using cached image variant {alt_i} as fallback")
                            results.append({
                                "success": True,
                                "file_path": str(alt_cache),
                                "prompt": prompt,
                                "note": "Fallback from cache due to API error",
                                "error_details": str(e),
                                "source": "cache_fallback",
                                "topic_id": topic_id  # Store topic ID in metadata
                            })
                            break
                else:
                    results.append({
                        "success": False,
                        "error": f"Stability AI API error: {str(e)}",
                        "variant": i
                    })
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Stability AI API request error: {str(e)}")
                
                # If we have cached images, use as fallback
                if has_any_cached:
                    for alt_i in range(1, num_variants + 1):
                        alt_cache = self._cache_path(prompt_hash, alt_i)
                        if alt_cache.exists():
                            logger.info(f"Using cached image variant {alt_i} as fallback")
                            results.append({
                                "success": True,
                                "file_path": str(alt_cache),
                                "prompt": prompt,
                                "note": "Fallback from cache due to API error",
                                "error_details": str(e),
                                "source": "cache_fallback",
                                "topic_id": topic_id  # Store topic ID in metadata
                            })
                            break
                else:
                    results.append({
                        "success": True,
                        "file_path": "fallback.jpg",
                        "url": "/images/fallback.jpg",
                        "prompt": prompt,
                        "error_details": str(e),
                        "width": width,
                        "height": height,
                        "timestamp": iso_now(),
                        "model_version": "fallback",
                        "source": "fallback_request_error",
                        "topic_id": topic_id  # Store topic ID in metadata
                    })
            except Exception as e:
                logger.error(f"Unexpected error during image generation: {str(e)}")
                results.append({
                    "success": True,
                    "file_path": "fallback.jpg",
                    "url": "/images/fallback.jpg",
                    "prompt": prompt,
                    "error_details": f"Unexpected error: {str(e)}",
                    "width": width,
                    "height": height,
                    "timestamp": iso_now(),
                    "model_version": "fallback",
                    "source": "fallback_unexpected_error",
                    "topic_id": topic_id  # Store topic ID in metadata
                })
        
        return results
    
    def get_styles(self) -> List[Dict[str, str]]:
        """
        Get available artistic styles for image generation.
        
        Returns:
            List of style dictionaries with name and description
        """
        return [
            {"name": "photorealistic", "description": "Highly detailed, lifelike images"},
            {"name": "oil painting", "description": "Rich, textured style reminiscent of traditional oil paintings"},
            {"name": "watercolor", "description": "Soft, flowing style with transparent colors"},
            {"name": "sketch", "description": "Black and white or colored sketch/drawing style"},
            {"name": "digital art", "description": "Clean, polished digital illustration style"},
            {"name": "comic book", "description": "Bold outlines and vibrant colors in comic style"},
            {"name": "pop art", "description": "Bright colors, bold patterns, popular culture inspired"},
            {"name": "impressionist", "description": "Emphasis on light, movement, and color over detail"},
            {"name": "surrealist", "description": "Dreamlike, fantastical imagery with unexpected elements"},
            {"name": "minimalist", "description": "Simple, clean style with limited elements"},
            {"name": "anime", "description": "Japanese animation inspired style"},
            {"name": "pixel art", "description": "Retro-style imagery composed of visible pixels"},
            {"name": "3D render", "description": "Photorealistic 3D rendered scene with realistic lighting and textures"},
            {"name": "cinematic", "description": "Movie-like composition with dramatic lighting and atmosphere"}
        ]


# Create a singleton instance
stable_diffusion_client = StableDiffusionClient() 