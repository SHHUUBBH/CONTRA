"""
API Status utility for monitoring the health of all external APIs
used in the CONTRA application.
"""

import os
import requests
from typing import Dict, List, Any
import logging

from config import APIConfig
from services.groq_client import GroqClient

logger = logging.getLogger(__name__)

def check_groq_api() -> Dict[str, Any]:
    """Check if Groq API key is configured and working."""
    result = {
        "name": "Groq LLaMA API",
        "status": "unknown",
        "message": ""
    }
    
    if not APIConfig.GROQ_API_KEY or APIConfig.GROQ_API_KEY == "dummy_key_replace_with_real_one":
        result["status"] = "missing"
        result["message"] = "API key not configured. Update GROQ_API_KEY in .env file."
        return result
    
    try:
        # Test a simple completion request
        headers = {
            "Authorization": f"Bearer {APIConfig.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": APIConfig.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result["status"] = "ok"
            result["message"] = "API connection successful."
        else:
            result["status"] = "error"
            result["message"] = f"API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Connection error: {str(e)}"
    
    return result

def check_stable_diffusion() -> Dict[str, Any]:
    """Check if Stability AI API key is configured and working."""
    result = {
        "name": "Stability AI API",
        "status": "unknown",
        "message": ""
    }
    
    if not APIConfig.STABILITY_API_KEY or APIConfig.STABILITY_API_KEY == "":
        result["status"] = "missing"
        result["message"] = "API key not configured. Update STABILITY_API_KEY in .env file."
        return result
    
    try:
        # Create API endpoint for models list
        api_url = "https://api.stability.ai/v1/engines/list"
        
        # Setup headers for Stability API
        headers = {
            "Authorization": f"Bearer {APIConfig.STABILITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Test connection to API
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result["status"] = "ok"
            result["message"] = "API connection successful."
        else:
            result["status"] = "error"
            result["message"] = f"API error: {response.status_code} - {response.text}"
    
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Connection error: {str(e)}"
    
    return result

def check_news_api() -> Dict[str, Any]:
    """Check if News API key is configured and working."""
    result = {
        "name": "News API",
        "status": "unknown",
        "message": ""
    }
    
    if not APIConfig.NEWS_API_KEY or APIConfig.NEWS_API_KEY == "dummy_key_replace_with_real_one":
        result["status"] = "missing"
        result["message"] = "API key not configured. Update NEWS_API_KEY in .env file."
        return result
    
    try:
        # Use the gnews library to check if we can fetch news
        from gnews import GNews
        
        gnews = GNews()
        gnews.max_results = 1
        gnews.language = 'en'
        
        # Try to get a single news article as a test
        articles = gnews.get_news('test')
        
        if articles:
            result["status"] = "ok"
            result["message"] = "API connection successful."
        else:
            result["status"] = "error"
            result["message"] = "No articles returned from API."
    
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Connection error: {str(e)}"
    
    return result

def get_all_api_statuses() -> Dict[str, Any]:
    """Get the status of all external APIs."""
    services = [
        check_groq_api(),
        check_stable_diffusion(),
        check_news_api()
    ]
    
    # Count services by status
    status_counts = {"ok": 0, "error": 0, "missing": 0, "unknown": 0}
    for service in services:
        status = service.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Determine overall status
    overall_status = "ok"
    if status_counts["error"] > 0:
        overall_status = "degraded"
    if status_counts["missing"] > 0:
        overall_status = "incomplete"
    if status_counts["ok"] == 0:
        overall_status = "down"
    
    return {
        "overall_status": overall_status,
        "services": services,
        "summary": {
            "total": len(services),
            "ok": status_counts["ok"],
            "error": status_counts["error"],
            "missing": status_counts["missing"],
            "unknown": status_counts["unknown"]
        }
    } 