"""
Groq LLaMA API client service for narrative generation.
"""

import os
import logging
import requests
import json
from typing import Dict, List, Any, Optional, Tuple

try:
    from config import APIConfig
except ImportError:
    # Fallback config if imports fail
    class APIConfig:
        GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
        GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

try:
    from utils.cache import disk_cache
except ImportError:
    # Fallback decorator if cache is not available
    def disk_cache(subdir=''):
        def decorator(func):
            return func
        return decorator

try:
    from utils.helpers import format_time_elapsed
except ImportError:
    # Fallback helper if not available
    def format_time_elapsed(seconds):
        return f"{seconds:.2f}s"

# Configure logging
logger = logging.getLogger(__name__)

class GroqClient:
    """
    Client for the Groq LLaMA API.
    
    Provides methods to generate text using Groq's API:
    https://console.groq.com/docs/quickstart
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Groq client.
        
        Args:
            api_key: Groq API key (defaults to APIConfig.GROQ_API_KEY)
            model: LLaMA model name (defaults to APIConfig.GROQ_MODEL)
        """
        self.api_key = api_key or APIConfig.GROQ_API_KEY
        self.model = model or APIConfig.GROQ_MODEL
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.models_url = "https://api.groq.com/openai/v1/models"
        
        if not self.api_key:
            logger.warning("No Groq API key provided. API calls will fail.")
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate a Groq API key by checking models or running a minimal query.
        Returns (is_valid, message).
        """
        if not api_key or not isinstance(api_key, str) or not api_key.strip():
            return False, "API key cannot be empty."
        
        key = api_key.strip()
        if key in ("your_groq_api_key_here", "dummy_key_replace_with_real_one"):
            return False, "This is a placeholder key. Please provide your actual Groq API key."
        
        try:
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            # Test chat completions with the LLaMA model
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 2
            }
            res = requests.post(self.api_url, headers=headers, json=payload, timeout=12)
            if res.status_code == 200:
                return True, f"API key is valid and working with LLaMA ({self.model})!"
            elif res.status_code == 401 or res.status_code == 403:
                return False, "Invalid Groq API key. Please check your key on the Groq Console."
            elif res.status_code == 429:
                return False, "Rate limit or quota exceeded for this API key on Groq."
            else:
                err_msg = res.text
                try:
                    err_json = res.json()
                    err_msg = err_json.get("error", {}).get("message", res.text)
                except Exception:
                    pass
                return False, f"Groq error ({res.status_code}): {err_msg}"
        except Exception as e:
            return False, f"Failed to connect to Groq API: {str(e)}"

    @disk_cache(subdir='groq')
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using the Groq LLaMA API.
        
        Args:
            prompt: The text prompt to generate from
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0-1.0, higher = more creative)
            top_p: Nucleus sampling parameter (0.0-1.0)
            stop: Optional list of strings that stop generation when encountered
            api_key: Optional override for Groq API key
            
        Returns:
            Dictionary containing generated text and metadata
        """
        import time
        start_time = time.time()
        
        active_key = (api_key or self.api_key or '').strip()
        logger.info(f"Generating text with Groq LLaMA (model={self.model})")
        
        if not active_key or active_key in ("your_groq_api_key_here", "dummy_key_replace_with_real_one"):
            return {
                "success": False,
                "error": "Groq LLaMA API key not configured or unavailable. Please bring your own key to test this project.",
                "requires_custom_key": True,
                "llama_quota_over": True,
                "text": ""
            }
        
        headers = {
            "Authorization": f"Bearer {active_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful, accurate, and creative assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        
        if stop:
            payload["stop"] = stop
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60  # 60-second timeout
            )
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            generation_time = time.time() - start_time
            
            # Extract the generated text
            if 'choices' in data and len(data['choices']) > 0:
                text = data['choices'][0]['message']['content'].strip()
                
                return {
                    "success": True,
                    "text": text,
                    "model": self.model,
                    "usage": data.get("usage", {}),
                    "generation_time": format_time_elapsed(generation_time)
                }
            else:
                logger.error(f"Unexpected Groq API response: {data}")
                return {
                    "success": False,
                    "error": "Unexpected API response format",
                    "text": "",
                    "raw_response": data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request error: {str(e)}")
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') and e.response is not None else None
            error_details = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    err_json = e.response.json()
                    error_details = err_json.get('error', {}).get('message', e.response.text)
                except Exception:
                    error_details = e.response.text
            
            err_lower = (str(error_details) + " " + str(e)).lower()
            is_quota_or_auth = (
                status_code in (401, 402, 403, 429) or
                any(k in err_lower for k in [
                    "quota", "rate limit", "tokens", "credits", "unauthorized",
                    "invalid api key", "exceeded", "resource_exhausted", "insufficient_quota"
                ])
            )
            
            msg = f"API request failed: {str(e)}"
            if is_quota_or_auth:
                if status_code == 429 or "rate" in err_lower or "quota" in err_lower:
                    msg = "Groq LLaMA API rate limit or quota exceeded. Please bring your own key to test this project."
                else:
                    msg = "Groq LLaMA API key unauthorized or invalid. Please bring your own key to test this project."
            
            return {
                "success": False,
                "error": msg,
                "requires_custom_key": is_quota_or_auth,
                "llama_quota_over": is_quota_or_auth,
                "status_code": status_code,
                "details": error_details,
                "text": ""
            }
        except Exception as e:
            logger.error(f"Groq API unexpected error: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "text": ""
            }
    
    def parse_structured_output(self, prompt: str, output_format: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate structured output by instructing the model to output in a specific format.
        
        Args:
            prompt: The input prompt
            output_format: Dictionary describing the expected output structure
            api_key: Optional Groq API key override
            
        Returns:
            Dictionary with parsed structured output or error
        """
        # Add format instructions to the prompt
        format_instr = f"Please respond with output in the following JSON format: {json.dumps(output_format, indent=2)}"
        full_prompt = f"{prompt}\n\n{format_instr}\n\nJSON response:"
        
        # Generate text
        result = self.generate_text(full_prompt, temperature=0.3, api_key=api_key)  # Lower temperature for more deterministic output
        
        if not result["success"]:
            return result
        
        # Try to parse the response as JSON
        try:
            # Look for JSON content within the response
            text = result["text"]
            
            # Try to find JSON block (sometimes models add extra text)
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = text[json_start:json_end]
                parsed = json.loads(json_text)
                
                return {
                    "success": True,
                    "data": parsed,
                    "model": result["model"]
                }
            else:
                logger.error(f"Could not locate JSON in response: {text}")
                return {
                    "success": False,
                    "error": "Could not locate JSON in model response",
                    "text": text
                }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from model response: {e}")
            return {
                "success": False,
                "error": f"Failed to parse JSON: {str(e)}",
                "text": result["text"]
            }
    
    def extract_bullet_points(self, text: str) -> Tuple[str, str]:
        """
        Extract bullet points and narrative sections from generated text.
        
        Args:
            text: Generated text from LLaMA
            
        Returns:
            Tuple of (bullet_points, narrative)
        """
        import re
        
        # Look for sections with bullet points
        bullet_markers = [
            r'^\s*•\s+',  # Bullet symbol
            r'^\s*\*\s+',  # Asterisk
            r'^\s*-\s+',   # Hyphen
            r'^\s*\d+\.\s+'  # Numbered list
        ]
        
        bullet_patterns = [re.compile(marker, re.MULTILINE) for marker in bullet_markers]
        
        # Check if any bullet pattern is found
        has_bullets = any(pattern.search(text) for pattern in bullet_patterns)
        
        if not has_bullets:
            # No bullet points found, try to create them by finding key sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) >= 3:
                # Take first 3 sentences as bullet points
                bullets = "\n".join(f"• {s.strip()}" for s in sentences[:3])
                narrative = text
            else:
                bullets = ""
                narrative = text
        else:
            # Try to split into bullet points and narrative sections
            # Look for common headers
            bullet_section = None
            narrative_section = None
            
            # Check for sections labeled explicitly
            bullet_headers = [
                r'(?:key\s+points|summary|bullet\s+points|main\s+points|highlights):?',
                r'(?:in\s+summary):?'
            ]
            narrative_headers = [
                r'(?:narrative|detailed\s+description|full\s+text|detailed\s+narrative):?',
                r'(?:in\s+detail):?'
            ]
            
            for header_pattern in bullet_headers:
                match = re.search(header_pattern, text, re.IGNORECASE)
                if match:
                    bullet_start = match.end()
                    # Find the next header or end of text
                    next_header = None
                    for nh in narrative_headers:
                        next_match = re.search(nh, text[bullet_start:], re.IGNORECASE)
                        if next_match:
                            next_header = bullet_start + next_match.start()
                            break
                    
                    bullet_section = text[bullet_start:next_header].strip() if next_header else text[bullet_start:].strip()
                    narrative_section = text[next_header:].strip() if next_header else ""
                    break
            
            if not bullet_section:
                # If no explicit sections found, use the first part with bullet points as the bullet section
                lines = text.split('\n')
                bullet_lines = []
                narrative_lines = []
                
                in_bullets = False
                for i, line in enumerate(lines):
                    is_bullet = any(pattern.search(line) for pattern in bullet_patterns)
                    
                    if is_bullet:
                        bullet_lines.append(line)
                        in_bullets = True
                    elif in_bullets and not line.strip():
                        # Empty line after bullets might indicate the end of bullet section
                        if i+1 < len(lines) and not any(pattern.search(lines[i+1]) for pattern in bullet_patterns):
                            in_bullets = False
                            narrative_lines.append(line)
                    else:
                        narrative_lines.append(line)
                
                bullet_section = '\n'.join(bullet_lines).strip()
                narrative_section = '\n'.join(narrative_lines).strip()
            
            # If splitting didn't work well, use the whole text as narrative
            if not bullet_section:
                bullets = ""
                narrative = text
            else:
                bullets = bullet_section
                narrative = narrative_section if narrative_section else text
        
        return bullets, narrative


# Create a singleton instance
groq_client = GroqClient() 