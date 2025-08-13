"""
Data fetcher for retrieving and normalizing contextual data.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from models.data_model import TopicData, WikipediaData, DBpediaData, NewsArticle
from services.wikipedia_service import wikipedia_service
from services.dbpedia_service import dbpedia_service
from services.news_service import news_service
from utils.helpers import format_time_elapsed, iso_now

# Configure logging
logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Coordinates fetching data from multiple sources and normalizes the results.
    """
    
    def __init__(self):
        """Initialize services."""
        # Services are initialized as singletons in their respective modules
        pass
    
    def fetch_topic_data(self, topic: str) -> Dict[str, Any]:
        """
        Fetch data for a topic from all available sources.
        
        Args:
            topic: Topic keyword
            
        Returns:
            Dictionary with all fetched data and metadata
        """
        start_time = time.time()
        logger.info(f"Fetching data for topic: {topic}")
        
        # Track errors/failures
        errors = []
        
        # 1. Get Wikipedia summary
        wiki_data = self._fetch_wikipedia(topic)
        if not wiki_data.get("success", False):
            errors.append(wiki_data.get("error", "Unknown Wikipedia error"))
        
        # 2. Get DBpedia structured data
        dbpedia_data = self._fetch_dbpedia(topic)
        if not dbpedia_data.get("success", False):
            errors.append(dbpedia_data.get("error", "Unknown DBpedia error"))
        
        # 3. Get news articles
        news_data = self._fetch_news(topic)
        if not news_data.get("success", False):
            errors.append(news_data.get("error", "Unknown news API error"))
        
        # 4. Create a normalized topic data model
        try:
            topic_data = self._normalize_data(
                topic=topic,
                wiki_data=wiki_data,
                dbpedia_data=dbpedia_data,
                news_data=news_data
            )
            
            # 5. Return complete result
            elapsed_time = time.time() - start_time
            
            return {
                "success": len(errors) == 0,
                "topic": topic,
                "data": topic_data,  # Return the TopicData object directly
                "errors": errors if errors else None,
                "processing_time": format_time_elapsed(elapsed_time)
            }
        except Exception as e:
            logger.exception(f"Error in fetch_topic_data: {e}")
            # Return a minimal success response with error info
            elapsed_time = time.time() - start_time
            errors.append(f"Data normalization error: {str(e)}")
            
            # Create a minimal TopicData object with just Wikipedia data if available
            if wiki_data.get("success", False) and "summary" in wiki_data:
                from models.data_model import WikipediaData, DBpediaData
                minimal_topic_data = TopicData(
                    topic=topic,
                    wikipedia=WikipediaData(
                        summary=wiki_data.get("summary", f"Error fetching data for {topic}"),
                        url=wiki_data.get("url", "")
                    ),
                    dbpedia=DBpediaData()
                )
            else:
                from models.data_model import WikipediaData, DBpediaData
                minimal_topic_data = TopicData(
                    topic=topic,
                    wikipedia=WikipediaData(
                        summary=f"Error fetching data for {topic}",
                        url=""
                    ),
                    dbpedia=DBpediaData()
                )
            
            return {
                "success": False,
                "topic": topic,
                "data": minimal_topic_data,
                "errors": errors,
                "processing_time": format_time_elapsed(elapsed_time)
            }
    
    def _fetch_wikipedia(self, topic: str) -> Dict[str, Any]:
        """
        Fetch Wikipedia summary.
        
        Args:
            topic: Topic keyword
            
        Returns:
            Wikipedia API response
        """
        try:
            logger.info(f"Fetching Wikipedia data for: {topic}")
            return wikipedia_service.get_summary(topic)
        except Exception as e:
            logger.error(f"Wikipedia fetch error: {str(e)}")
            return {"success": False, "error": f"Wikipedia error: {str(e)}"}
    
    def _fetch_dbpedia(self, topic: str) -> Dict[str, Any]:
        """
        Fetch DBpedia structured data.
        
        Args:
            topic: Topic keyword
            
        Returns:
            DBpedia SPARQL query response
        """
        try:
            logger.info(f"Fetching DBpedia data for: {topic}")
            return dbpedia_service.get_data(topic)
        except Exception as e:
            logger.error(f"DBpedia fetch error: {str(e)}")
            return {"success": False, "error": f"DBpedia error: {str(e)}"}
    
    def _fetch_news(self, topic: str) -> Dict[str, Any]:
        """
        Fetch news articles.
        
        Args:
            topic: Topic keyword
            
        Returns:
            News API response
        """
        try:
            logger.info(f"Fetching news for: {topic}")
            news_result = news_service.get_news(topic)
            
            # Even if news API returns an error, return an empty success response
            # to allow the application to continue
            if not news_result.get("success", False):
                logger.warning(f"News API error: {news_result.get('error', 'Unknown error')}. Continuing with empty news data.")
                return {
                    "success": True,
                    "topic": topic,
                    "retrieved_at": iso_now(),
                    "count": 0,
                    "articles": []
                }
            return news_result
        except Exception as e:
            logger.error(f"News fetch error: {str(e)}")
            # Return empty news data instead of error
            return {
                "success": True,
                "topic": topic,
                "retrieved_at": iso_now(),
                "count": 0,
                "articles": []
            }
    
    def _normalize_data(
        self,
        topic: str,
        wiki_data: Dict[str, Any],
        dbpedia_data: Dict[str, Any],
        news_data: Dict[str, Any]
    ) -> TopicData:
        """
        Normalize data from different sources into a unified TopicData model.
        
        Args:
            topic: Topic keyword
            wiki_data: Wikipedia API response
            dbpedia_data: DBpedia API response
            news_data: News API response
            
        Returns:
            Normalized TopicData instance
        """
        # Create WikipediaData with safe defaults
        try:
            if wiki_data and wiki_data.get("success", False):
                wikipedia = WikipediaData(
                    summary=wiki_data.get("summary", ""),
                    url=wiki_data.get("url", "")
                )
            else:
                error_msg = wiki_data.get('error', 'Unknown error') if wiki_data else 'No Wikipedia data'
                wikipedia = WikipediaData(
                    summary=f"Information about {topic} is not available at this time.",
                    url=""
                )
                logger.warning(f"Using fallback Wikipedia data: {error_msg}")
        except Exception as e:
            logger.exception(f"Error processing Wikipedia data: {e}")
            wikipedia = WikipediaData(
                summary=f"Information about {topic} is not available at this time.",
                url=""
            )
        
        # Create DBpediaData with safe defaults
        try:
            if dbpedia_data and dbpedia_data.get("success", False):
                dbpedia = DBpediaData(
                    abstract=dbpedia_data.get("abstract", ""),
                    categories=dbpedia_data.get("categories", []),
                    resource_uri=dbpedia_data.get("resource_uri", "")
                )
            else:
                dbpedia = DBpediaData()
                logger.warning(f"Using empty DBpedia data")
        except Exception as e:
            logger.exception(f"Error processing DBpedia data: {e}")
            dbpedia = DBpediaData()
        
        # Create NewsArticle list with safe defaults
        news_articles = []
        try:
            if news_data and news_data.get("success", False) and "articles" in news_data:
                for article in news_data["articles"]:
                    try:
                        if article:
                            news_articles.append(NewsArticle.from_raw(article))
                    except Exception as article_err:
                        logger.warning(f"Error processing news article: {article_err}")
        except Exception as e:
            logger.exception(f"Error processing news data: {e}")
        
        # Create and return the TopicData
        try:
            return TopicData(
                topic=topic,
                wikipedia=wikipedia,
                dbpedia=dbpedia,
                news=news_articles
            )
        except Exception as e:
            logger.exception(f"Error creating TopicData: {e}")
            # Return the most minimal valid TopicData object possible
            return TopicData(
                topic=topic,
                wikipedia=WikipediaData(
                    summary=f"Information about {topic} is not available at this time.",
                    url=""
                ),
                dbpedia=DBpediaData(),
                news=[]
            )
    
    def get_related_topics(self, topic: str, max_results: int = 5) -> List[str]:
        """
        Get related topics for the given topic.
        
        Args:
            topic: Main topic
            max_results: Maximum number of related topics to return
            
        Returns:
            List of related topic strings
        """
        # Try to get related topics from Wikipedia
        wiki_related = wikipedia_service.get_related_topics(topic)
        
        # If DBpedia has a resource URI, also get related entities
        resource_uri = None
        dbp_data = dbpedia_service.get_data(topic)
        if dbp_data.get("success", False):
            resource_uri = dbp_data.get("resource_uri")
        
        dbp_related = []
        if resource_uri:
            related_entities = dbpedia_service.get_related_entities(resource_uri)
            dbp_related = [entity.get("label", "") for entity in related_entities if "label" in entity]
        
        # Combine and deduplicate
        all_related = list(set(wiki_related + dbp_related))
        return all_related[:max_results]


# Create a singleton instance
data_fetcher = DataFetcher() 