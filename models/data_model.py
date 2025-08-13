"""
Data models for the CONTRA application.
Uses dataclasses for typed, structured data representation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

from utils.helpers import iso_now, create_wikipedia_url

@dataclass
class WikipediaData:
    """Wikipedia data model."""
    summary: str
    url: str
    retrieved_at: str = field(default_factory=iso_now)
    
    @classmethod
    def from_raw(cls, summary: str, topic: str) -> 'WikipediaData':
        """Create from raw Wikipedia summary."""
        return cls(
            summary=summary,
            url=create_wikipedia_url(topic)
        )


@dataclass
class DBpediaData:
    """DBpedia data model."""
    abstract: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    retrieved_at: str = field(default_factory=iso_now)
    resource_uri: Optional[str] = None
    
    @classmethod
    def from_raw(cls, data: Dict[str, Any]) -> 'DBpediaData':
        """Create from raw DBpedia data."""
        return cls(
            abstract=data.get("abstract"),
            categories=data.get("categories", []),
            resource_uri=data.get("resource_uri")
        )


@dataclass
class NewsArticle:
    """News article model."""
    title: str
    url: str
    publisher: str = ""
    published_at: str = ""
    description: str = ""
    source: str = "gnews"
    
    @classmethod
    def from_raw(cls, article: Dict[str, Any]) -> 'NewsArticle':
        """Create from raw news article data."""
        publisher = article.get("publisher", "")
        if isinstance(publisher, dict):
            publisher = publisher.get("name", "")
            
        return cls(
            title=article.get("title", ""),
            url=article.get("url", ""),
            publisher=publisher,
            published_at=article.get("published_date") or article.get("publishedAt") or "",
            description=article.get("description", "")
        )


@dataclass
class TopicData:
    """Combined topic data model."""
    topic: str
    wikipedia: WikipediaData
    dbpedia: DBpediaData
    news: List[NewsArticle] = field(default_factory=list)
    created_at: str = field(default_factory=iso_now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "wikipedia": {
                "summary": self.wikipedia.summary,
                "url": self.wikipedia.url,
                "retrieved_at": self.wikipedia.retrieved_at
            },
            "dbpedia": {
                "abstract": self.dbpedia.abstract,
                "categories": self.dbpedia.categories,
                "resource_uri": self.dbpedia.resource_uri,
                "retrieved_at": self.dbpedia.retrieved_at
            },
            "news": [
                {
                    "title": article.title,
                    "url": article.url,
                    "publisher": article.publisher,
                    "published_at": article.published_at,
                    "description": article.description,
                    "source": article.source
                }
                for article in self.news
            ],
            "created_at": self.created_at
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Narrative:
    """Narrative model."""
    bullets: str
    narrative: str
    prompt: str
    model: str = ""
    expertise_level: str = "intermediate"
    created_at: str = field(default_factory=iso_now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bullets": self.bullets,
            "narrative": self.narrative,
            "prompt": self.prompt,
            "model": self.model,
            "expertise_level": self.expertise_level,
            "created_at": self.created_at
        }


@dataclass
class Image:
    """Image model."""
    file_path: str
    prompt: str
    model_version: str = ""
    timestamp: str = field(default_factory=iso_now)
    style: str = "photorealistic"
    width: int = 512
    height: int = 512
    url: str = ""
    topic_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "prompt": self.prompt,
            "model_version": self.model_version,
            "timestamp": self.timestamp,
            "style": self.style,
            "width": self.width,
            "height": self.height,
            "url": self.url,
            "topic_id": self.topic_id
        }


@dataclass
class Visualization:
    """Visualization model."""
    timeline: Optional[Dict[str, Any]] = None
    category_bar: Optional[Dict[str, Any]] = None
    concept_map: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timeline": self.timeline,
            "category_bar": self.category_bar,
            "concept_map": self.concept_map
        }


@dataclass
class GenerationResult:
    """Complete generation result."""
    topic: str
    data: TopicData
    narrative: Narrative
    images: List[Image] = field(default_factory=list)
    visualizations: Visualization = field(default_factory=Visualization)
    processing_time: float = 0.0
    created_at: str = field(default_factory=iso_now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "topic": self.topic,
            "data": self.data.to_dict(),
            "narrative": self.narrative.to_dict(),
            "images": [img.to_dict() for img in self.images],
            "visualizations": self.visualizations.to_dict(),
            "processing_time": self.processing_time,
            "created_at": self.created_at
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2) 