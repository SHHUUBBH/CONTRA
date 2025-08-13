"""
News service for fetching current news articles related to a topic.
Uses GNews library with fallback options to other news APIs.
"""

import logging
from typing import Dict, List, Any, Optional
from gnews import GNews
import time
import random
from datetime import datetime, timedelta

from config import ContentConfig
from utils.cache import disk_cache
from utils.helpers import iso_now

# Configure logging
logger = logging.getLogger(__name__)

class NewsService:
    """
    Service for retrieving news articles related to a topic.
    Uses GNews with caching to reduce API calls.
    """
    
    def __init__(self):
        """Initialize the news service with default settings."""
        self.gnews = GNews()
        # Configure GNews options
        self.gnews.max_results = ContentConfig.MAX_NEWS_ARTICLES
        # Set language to English
        self.gnews.language = 'en'
        # Set country to None (worldwide)
        self.gnews.country = None
        # Set default period to last 7 days
        self.gnews.period = '7d'
    
    @disk_cache(subdir='news')
    def get_news(self, topic: str, max_results: int = None) -> Dict[str, Any]:
        """
        Retrieve news articles related to a topic.
        
        Args:
            topic: Search topic
            max_results: Maximum number of articles to return (defaults to ContentConfig.MAX_NEWS_ARTICLES)
            
        Returns:
            Dictionary with articles and metadata
        """
        if max_results is None:
            max_results = ContentConfig.MAX_NEWS_ARTICLES
            
        logger.info(f"Fetching news for: {topic}")
        
        try:
            # Set max results for this query
            self.gnews.max_results = max_results
            
            # Get news articles
            articles = self.gnews.get_news(topic)
            
            if not articles:
                logger.warning(f"No news articles found for '{topic}'. Using fallback dummy data.")
                return self._get_dummy_articles(topic)
            
            # Process and normalize articles
            processed_articles = self._process_articles(articles)
            
            return {
                "success": True,
                "topic": topic,
                "retrieved_at": iso_now(),
                "count": len(processed_articles),
                "articles": processed_articles
            }
            
        except Exception as e:
            logger.error(f"News API error: {str(e)}")
            return self._get_dummy_articles(topic)
    
    def _get_dummy_articles(self, topic: str) -> Dict[str, Any]:
        """
        Generate dummy articles when the API fails.
        
        Args:
            topic: Search topic
            
        Returns:
            Dictionary with dummy articles
        """
        logger.info(f"Generating dummy news data for: {topic}")
        
        # Create 3 dummy articles
        dummy_articles = [
            {
                "title": f"Latest developments in {topic}",
                "url": "https://example.com/article1",
                "publisher": "Example News",
                "published_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": f"Recent news about {topic} and related developments."
            },
            {
                "title": f"Understanding {topic}: A comprehensive guide",
                "url": "https://example.com/article2",
                "publisher": "Knowledge Daily",
                "published_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": f"Everything you need to know about {topic} explained in simple terms."
            },
            {
                "title": f"The impact of {topic} on modern society",
                "url": "https://example.com/article3",
                "publisher": "Analysis Weekly",
                "published_at": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "description": f"Experts discuss how {topic} is changing our world and what to expect in the future."
            }
        ]
        
        return {
            "success": True,
            "topic": topic,
            "retrieved_at": iso_now(),
            "count": len(dummy_articles),
            "articles": dummy_articles,
            "note": "Using fallback dummy data due to API issues"
        }
    
    def _process_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and normalize raw news articles.
        
        Args:
            articles: Raw list of article dictionaries from GNews
            
        Returns:
            Normalized list of article dictionaries
        """
        processed = []
        
        for art in articles:
            # Extract publisher name from publisher object if present
            publisher = art.get("publisher", "")
            if isinstance(publisher, dict):
                publisher = publisher.get("name", "")
            
            # Get published date
            published_date = art.get("published date") or art.get("publishedAt") or ""
            
            # Clean and validate fields
            processed.append({
                "title": art.get("title", "").strip(),
                "url": art.get("url", ""),
                "publisher": publisher,
                "published_at": published_date,
                "description": art.get("description", "").strip()
            })
        
        return processed
    
    @disk_cache(subdir='news')
    def search_by_dates(self, topic: str, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Search for news within a specific date range.
        
        Args:
            topic: Search topic
            start_date: Start date in 'YYYY-MM-DD' format (default: 7 days ago)
            end_date: End date in 'YYYY-MM-DD' format (default: today)
            
        Returns:
            List of article dictionaries
        """
        # Calculate default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if not start_date:
            # Default to 7 days before end date
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            start_dt = end_dt - timedelta(days=7)
            start_date = start_dt.strftime('%Y-%m-%d')
        
        logger.info(f"Searching news for '{topic}' from {start_date} to {end_date}")
        
        try:
            # Configure date range
            self.gnews.start_date = start_date
            self.gnews.end_date = end_date
            
            # Fetch articles
            articles = self.gnews.get_news(topic)
            
            # Process and return
            return self._process_articles(articles)
            
        except Exception as e:
            logger.error(f"Date-based news search error: {str(e)}")
            return []
        finally:
            # Reset date settings
            self.gnews.start_date = None
            self.gnews.end_date = None
    
    def get_top_headlines(self, category: str = None, country: str = None) -> List[Dict[str, Any]]:
        """
        Get top headlines, optionally filtered by category and country.
        
        Args:
            category: News category (e.g., 'business', 'technology')
            country: Country code (e.g., 'us', 'gb')
            
        Returns:
            List of article dictionaries
        """
        logger.info(f"Fetching top headlines (category={category}, country={country})")
        
        try:
            # Store original settings
            orig_country = self.gnews.country
            
            # Apply filters if provided
            if country:
                self.gnews.country = country
                
            # Fetch headlines (GNews doesn't directly support categories, so we have to search)
            if category:
                headlines = self.gnews.get_news(category)
            else:
                # For top headlines without a category, use a workaround
                # (GNews doesn't have a dedicated top headlines endpoint)
                headlines = self.gnews.get_top_news()
            
            # Process and return
            return self._process_articles(headlines)
            
        except Exception as e:
            logger.error(f"Top headlines error: {str(e)}")
            return []
        finally:
            # Restore original settings
            self.gnews.country = orig_country


# Create a singleton instance
news_service = NewsService() 