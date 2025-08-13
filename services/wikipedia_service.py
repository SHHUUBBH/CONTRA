"""
Wikipedia API service for fetching article summaries.
Uses wikipediaapi library for clean access to Wikipedia content.
"""

import logging
import wikipediaapi
from typing import Dict, Any, Optional, List, Tuple

from config import ContentConfig
from utils.cache import disk_cache
from utils.helpers import truncate_text

# Configure logging
logger = logging.getLogger(__name__)

class WikipediaService:
    """
    Service for accessing Wikipedia content.
    Uses disk-based caching to reduce API calls for previously requested topics.
    """
    
    def __init__(self):
        """Initialize the Wikipedia service with a custom user agent."""
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='CONTRA-Backend/1.0 (contact@example.com)',
            language='en'
        )
    
    @disk_cache(subdir='wikipedia')
    def get_summary(self, topic: str) -> Dict[str, Any]:
        """
        Retrieve the summary of a Wikipedia page for the given topic.
        
        Args:
            topic: Title or search term for the Wikipedia page
            
        Returns:
            Dictionary with the results or error message
        """
        logger.info(f"Fetching Wikipedia summary for: {topic}")
        
        try:
            # Validate topic input
            if not topic or len(topic.strip()) == 0:
                return {
                    "success": False,
                    "error": "Empty search topic"
                }
            
            # Get Wikipedia page
            page = self.wiki.page(topic)
            
            # Check if page exists
            if not page.exists():
                # Try similar pages
                try:
                    similar_pages = self._find_similar_pages(topic)
                    if similar_pages:
                        # Return the first similar page instead
                        alt_page = self.wiki.page(similar_pages[0])
                        if alt_page.exists():
                            logger.info(f"Using similar page '{alt_page.title}' for topic '{topic}'")
                            return {
                                "success": True,
                                "summary": alt_page.summary,
                                "title": alt_page.title,
                                "url": alt_page.fullurl,
                                "categories": list(alt_page.categories.keys()),
                                "note": f"Using similar topic: {alt_page.title}"
                            }
                except Exception as e:
                    logger.warning(f"Error finding similar pages: {e}")
                
                # No similar pages found or error occurred
                return {
                    "success": False,
                    "error": f"Wikipedia page for '{topic}' not found.",
                    "title": topic,
                    "url": ""
                }
            
            # Get summary (and truncate if necessary)
            summary = page.summary
            if not summary:
                # If summary is empty but page exists, return a minimal summary from the first section
                sections = list(page.sections)
                if sections:
                    first_section = page.section(sections[0])
                    if first_section:
                        summary = first_section
                    else:
                        summary = f"Wikipedia page for '{topic}' exists but contains no summary."
                else:
                    summary = f"Wikipedia page for '{topic}' exists but contains no summary."
            
            # Truncate if configured
            max_length = ContentConfig.WIKIPEDIA_SUMMARY_LENGTH
            truncated = truncate_text(summary, max_length=max_length)
            
            # Return successful result
            return {
                "success": True,
                "summary": truncated,
                "title": page.title,
                "url": page.fullurl,
                "categories": list(page.categories.keys())
            }
            
        except Exception as e:
            logger.error(f"Wikipedia API error: {str(e)}")
            return {
                "success": False,
                "error": f"Wikipedia API error: {str(e)}",
                "fallback_summary": f"Information about {topic} is currently unavailable."
            }
    
    @disk_cache(subdir='wikipedia')
    def search(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Search Wikipedia for related pages.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of dictionaries with title and snippet
        """
        # Note: Direct search is not supported by wikipediaapi
        # This is a placeholder - in a real implementation you would use
        # another library like 'wikipedia' or MediaWiki API
        
        logger.info(f"Searching Wikipedia for: {query}")
        
        # Mock implementation (would be replaced with actual search)
        page = self.wiki.page(query)
        if page.exists():
            return [{
                "title": page.title,
                "url": page.fullurl,
                "snippet": truncate_text(page.summary, 100)
            }]
        else:
            return []
    
    def get_related_topics(self, topic: str) -> List[str]:
        """
        Get related topics by examining categories and links.
        
        Args:
            topic: Main topic
            
        Returns:
            List of related topic strings
        """
        page = self.wiki.page(topic)
        if not page.exists():
            return []
        
        # Extract category names (remove 'Category:' prefix)
        categories = [
            cat.split(':', 1)[1] if ':' in cat else cat 
            for cat in page.categories.keys()
        ]
        
        # Get a sample of links
        links = list(page.links.keys())[:10]
        
        # Combine unique results
        related = list(set(categories + links))
        
        # Filter out non-content categories
        filtered = [
            rel for rel in related 
            if not any(x in rel.lower() for x in ['stub', 'wikify', 'articles', 'pages'])
        ]
        
        return filtered[:5]  # Return up to 5 related topics

    def _find_similar_pages(self, topic: str, limit: int = 3) -> List[str]:
        """
        Find similar Wikipedia pages when the exact topic is not found.
        
        Args:
            topic: The original topic
            limit: Maximum number of suggestions
            
        Returns:
            List of similar page titles
        """
        # This is a mock implementation since wikipediaapi doesn't support search
        # In a real implementation, you might use the MediaWiki API or another library
        similar = []
        
        # Try variations of the topic
        variations = [
            topic.lower(),
            topic.title(),
            topic.upper(),
            topic + "s",  # Plural
            topic.rstrip("s"),  # Singular
            " ".join([w.capitalize() for w in topic.split()])  # Title case each word
        ]
        
        # Try each variation
        for variant in variations:
            if variant != topic:  # Skip the original topic
                try:
                    page = self.wiki.page(variant)
                    if page.exists():
                        similar.append(variant)
                        if len(similar) >= limit:
                            break
                except:
                    continue
        
        return similar


# Create a singleton instance
wikipedia_service = WikipediaService() 