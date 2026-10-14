"""
API Status utility for monitoring the health of all external APIs and services
used in the CONTRA application.
"""

import os
import requests
from typing import Dict, List, Any, Optional
import logging

from config import APIConfig
from services.wikipedia_service import wikipedia_service
from services.dbpedia_service import dbpedia_service

logger = logging.getLogger(__name__)

def check_groq_api(api_key: Optional[str] = None) -> Dict[str, Any]:
    """Check if Groq API key is configured and working."""
    result = {
        "id": "groq",
        "name": "Groq LLaMA API",
        "status": "unknown",
        "available": False,
        "quota_over": False,
        "message": ""
    }
    
    key = (api_key or APIConfig.GROQ_API_KEY or '').strip()
    if not key or key in ("dummy_key_replace_with_real_one", "your_groq_api_key_here"):
        result["status"] = "missing"
        result["available"] = False
        result["quota_over"] = True
        result["message"] = "Groq LLaMA API key not configured. Bring your own Groq API key to test."
        return result
    
    try:
        # Test a simple completion request
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": APIConfig.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "ping"}
            ],
            "max_tokens": 5
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result["status"] = "ok"
            result["available"] = True
            result["message"] = f"API connection successful ({APIConfig.GROQ_MODEL})."
        elif response.status_code in (401, 403):
            result["status"] = "error"
            result["available"] = False
            result["quota_over"] = True
            result["message"] = "Invalid Groq API key or unauthorized."
        elif response.status_code == 429:
            result["status"] = "error"
            result["available"] = False
            result["quota_over"] = True
            result["message"] = "Groq LLaMA API quota or rate limit exceeded."
        else:
            result["status"] = "error"
            result["available"] = False
            result["message"] = f"API error: {response.status_code} - {response.text[:100]}"
    
    except Exception as e:
        result["status"] = "error"
        result["available"] = False
        result["message"] = f"Connection error: {str(e)}"
    
    return result

def check_stable_diffusion() -> Dict[str, Any]:
    """Check if Stability AI API key is configured and working."""
    result = {
        "id": "stability_ai",
        "name": "Stability AI API",
        "status": "unknown",
        "message": ""
    }
    
    key = (APIConfig.STABILITY_API_KEY or '').strip()
    if not key or key in ("your_stability_api_key_here", "dummy_key_replace_with_real_one"):
        result["status"] = "missing"
        result["message"] = "API key not configured in .env. Built-in fallback art generator is active."
        return result
    
    try:
        # Create API endpoint for engines list
        api_url = "https://api.stability.ai/v1/engines/list"
        
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            api_url,
            headers=headers,
            timeout=8
        )
        
        if response.status_code == 200:
            result["status"] = "ok"
            result["message"] = "Stability AI connection successful."
        elif response.status_code in (401, 403):
            result["status"] = "error"
            result["message"] = "Stability AI unauthorized or invalid key. Fallback art generator active."
        else:
            result["status"] = "error"
            result["message"] = f"Stability AI error: {response.status_code}."
    
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Connection error: {str(e)}"
    
    return result

def check_wikipedia() -> Dict[str, Any]:
    """Check if Wikipedia service is available and responding."""
    result = {
        "id": "wikipedia",
        "name": "Wikipedia Service",
        "status": "unknown",
        "message": ""
    }
    
    try:
        summary_res = wikipedia_service.get_summary("Artificial Intelligence")
        if summary_res.get("success"):
            result["status"] = "ok"
            result["message"] = "Wikipedia service operational and connected."
        else:
            result["status"] = "error"
            result["message"] = summary_res.get("error", "Wikipedia query failed.")
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"Wikipedia service error: {str(e)}"
        
    return result

def check_dbpedia() -> Dict[str, Any]:
    """Check if DBpedia SPARQL service is operational."""
    result = {
        "id": "dbpedia",
        "name": "DBpedia Service",
        "status": "unknown",
        "message": ""
    }
    
    try:
        res = dbpedia_service.get_data("Science")
        if res.get("success"):
            result["status"] = "ok"
            result["message"] = "DBpedia SPARQL endpoint operational."
        else:
            result["status"] = "error"
            result["message"] = res.get("error", "DBpedia service unavailable.")
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"DBpedia connection error: {str(e)}"
        
    return result

def check_news_api() -> Dict[str, Any]:
    """Check if News service is configured and working."""
    result = {
        "id": "news_api",
        "name": "News Service",
        "status": "unknown",
        "message": ""
    }
    
    try:
        from gnews import GNews
        gnews = GNews()
        gnews.max_results = 1
        gnews.language = 'en'
        articles = gnews.get_news('technology')
        
        if articles:
            result["status"] = "ok"
            result["message"] = "News service operational and retrieving feeds."
        else:
            result["status"] = "error"
            result["message"] = "No news articles returned from feed."
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"News service error: {str(e)}"
    
    return result

def get_all_api_statuses(groq_key: Optional[str] = None) -> Dict[str, Any]:
    """Get the status of all external services and APIs."""
    groq_status = check_groq_api(api_key=groq_key)
    stability_status = check_stable_diffusion()
    wikipedia_status = check_wikipedia()
    dbpedia_status = check_dbpedia()
    news_status = check_news_api()
    
    services = [
        groq_status,
        stability_status,
        wikipedia_status,
        dbpedia_status,
        news_status
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
        "groq": groq_status,
        "stability_ai": stability_status,
        "wikipedia": wikipedia_status,
        "dbpedia": dbpedia_status,
        "news_api": news_status,
        "summary": {
            "total": len(services),
            "ok": status_counts["ok"],
            "error": status_counts["error"],
            "missing": status_counts["missing"],
            "unknown": status_counts["unknown"]
        }
    }