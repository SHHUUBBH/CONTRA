"""
Visualizer for creating interactive data visualizations.
"""

import logging
import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple

import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

from models.data_model import TopicData, Visualization
from config import ContentConfig
from utils.helpers import format_time_elapsed, extract_dates_from_text

# Configure logging
logger = logging.getLogger(__name__)

class Visualizer:
    """
    Creates interactive visualizations of topic data using Plotly.
    """
    
    def __init__(self):
        """Initialize the visualizer."""
        self.theme = ContentConfig.DEFAULT_VIZ_THEME
    
    def create_visualizations(self, topic_data: TopicData) -> Dict[str, Any]:
        """
        Create a set of visualizations based on topic data.
        
        Args:
            topic_data: Normalized topic data
            
        Returns:
            Dictionary with visualization data and metadata
        """
        start_time = time.time()
        logger.info(f"Creating visualizations for topic: {topic_data.topic}")
        
        try:
            # Create individual visualizations
            timeline = self.create_timeline(topic_data)
            category_bar = self.create_category_bar(topic_data)
            concept_map = self.create_concept_map(topic_data)
            
            # Log status of each visualization
            logger.info(f"Timeline: {'Created' if timeline else 'None'}")
            logger.info(f"Category Bar: {'Created' if category_bar else 'None'}")
            logger.info(f"Concept Map: {'Created' if concept_map else 'None'}")
            
            # Create visualization model
            visualizations = Visualization(
                timeline=timeline,
                category_bar=category_bar,
                concept_map=concept_map
            )
            
            # Convert to dictionary using to_dict
            viz_dict = visualizations.to_dict()
            
            # Return the result
            elapsed_time = time.time() - start_time
            return {
                "success": True,
                "visualizations": viz_dict,
                "processing_time": format_time_elapsed(elapsed_time)
            }
        except Exception as e:
            logger.exception(f"Error creating visualizations: {str(e)}")
            # Return empty visualizations on error rather than failing the entire request
            return {
                "success": True,
                "visualizations": {
                    "timeline": None,
                    "category_bar": None,
                    "concept_map": None,
                    "error": str(e)
                },
                "processing_time": format_time_elapsed(time.time() - start_time)
            }
    
    def _safe_json_encode(self, fig) -> Optional[Dict[str, Any]]:
        """Safely encode Plotly figure to JSON."""
        try:
            # Ensure we're working with the PlotlyJSONEncoder which properly formats the figure
            result = json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
            
            # Verify the structure is correct for frontend display
            if not result or 'data' not in result or 'layout' not in result:
                logger.error(f"Invalid figure structure - missing 'data' or 'layout' keys")
                return None
            
            # Add debugging to check structure
            logger.info(f"Encoded JSON has keys: {list(result.keys())}")
            logger.info(f"Figure data has {len(result['data'])} traces")
            logger.info(f"Figure layout has {len(result['layout'])} properties")
            
            return result
        except Exception as e:
            logger.error(f"JSON encoding error for Plotly figure: {str(e)}")
            return None
    
    def create_timeline(self, topic_data: TopicData) -> Optional[Dict[str, Any]]:
        """
        Create a timeline visualization from news dates or extracted years.
        
        Args:
            topic_data: Normalized topic data
            
        Returns:
            Plotly JSON figure for timeline chart
        """
        try:
            events = []
            
            # Method 1: Extract dates from news articles
            for article in topic_data.news:
                if article.published_at:
                    try:
                        date_parts = article.published_at.split("T")[0].split("-")
                        if len(date_parts) >= 3:
                            year = int(date_parts[0])
                            events.append({
                                "year": year,
                                "event": article.title,
                                "source": "news"
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing date from news article: {e}")
            
            # Method 2: Extract years from Wikipedia text
            if topic_data.wikipedia.summary:
                dates_from_text = extract_dates_from_text(topic_data.wikipedia.summary)
                for date in dates_from_text:
                    events.append({
                        "year": date["year"],
                        "event": date["event"],
                        "source": "wikipedia"
                    })
            
            # Method 3: Extract years from DBpedia abstract
            if topic_data.dbpedia.abstract:
                dates_from_dbpedia = extract_dates_from_text(topic_data.dbpedia.abstract)
                for date in dates_from_dbpedia:
                    events.append({
                        "year": date["year"],
                        "event": date["event"],
                        "source": "dbpedia"
                    })
            
            # Log how many events we found
            logger.info(f"Found {len(events)} timeline events for topic: {topic_data.topic}")
            
            # If we have enough events, create the visualization
            if len(events) >= 2:
                # Sort by year
                events = sorted(events, key=lambda e: e["year"])
                
                # Limit to a reasonable number
                max_events = ContentConfig.TIMELINE_MAX_EVENTS
                if len(events) > max_events:
                    events = events[:max_events]
                
                # Extract data for plotting
                years = [e["year"] for e in events]
                labels = [e["event"] for e in events]
                sources = [e["source"] for e in events]
                
                # Create color map for sources
                source_colors = {
                    "news": "cyan",
                    "wikipedia": "yellow",
                    "dbpedia": "magenta"
                }
                colors = [source_colors.get(s, "gray") for s in sources]
                
                # Create the figure
                fig = go.Figure()
                
                # Add the main timeline
                fig.add_trace(
                    go.Scatter(
                        x=years,
                        y=[1] * len(years),  # Single line timeline
                        mode="markers+lines",
                        marker=dict(
                            size=12,
                            color=colors,
                            line=dict(width=2, color="DarkSlateGrey")
                        ),
                        line=dict(color="gray", dash="dash"),
                        text=labels,
                        hovertemplate="<b>%{text}</b><br>Year: %{x}<extra></extra>"
                    )
                )
                
                # Set layout options
                fig.update_layout(
                    title=f"Timeline: {topic_data.topic}",
                    xaxis=dict(
                        title="Year",
                        showgrid=True,
                        zeroline=False,
                        dtick=5  # Show tick marks every 5 years
                    ),
                    yaxis=dict(
                        visible=False  # Hide the y-axis
                    ),
                    margin=dict(l=20, r=20, t=30, b=20),
                    showlegend=False,
                    template=self.theme,
                    height=250,  # Smaller height for the timeline
                    plot_bgcolor="rgba(0,0,0,0)"  # Transparent background
                )
                
                # Test if the figure is valid
                if fig.data and fig.layout:
                    logger.info(f"Created valid timeline figure with {len(fig.data)} traces")
                else:
                    logger.warning("Created figure has no data or layout")
                
                # Convert to JSON and return
                result = self._safe_json_encode(fig)
                if result:
                    # Ensure it has the required structure
                    if 'data' in result and 'layout' in result:
                        return result
                    else:
                        logger.error("Timeline figure missing required keys")
                        return None
                else:
                    logger.error("Failed to encode timeline figure to JSON")
                    return None
            else:
                logger.info(f"Not enough timeline events ({len(events)}) to create visualization for {topic_data.topic}")
            
            return None
        except Exception as e:
            logger.error(f"Error creating timeline: {str(e)}")
            return None
    
    def create_category_bar(self, topic_data: TopicData) -> Optional[Dict[str, Any]]:
        """
        Create a bar chart of categories from DBpedia.
        
        Args:
            topic_data: Normalized topic data
            
        Returns:
            Plotly JSON figure for bar chart
        """
        try:
            if not topic_data.dbpedia.categories or len(topic_data.dbpedia.categories) < 2:
                return None
            
            # Count occurrences if there are duplicates
            category_counts = {}
            for cat in topic_data.dbpedia.categories:
                # Clean up category names (remove prefix/unwanted text)
                clean_cat = re.sub(r'^Category:', '', cat)
                # Split into words and capitalize each
                clean_cat = ' '.join(word.capitalize() for word in clean_cat.split('_'))
                
                category_counts[clean_cat] = category_counts.get(clean_cat, 0) + 1
            
            # Sort by count (descending)
            sorted_categories = sorted(
                category_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Limit to top 10 categories
            if len(sorted_categories) > 10:
                sorted_categories = sorted_categories[:10]
            
            # Prepare data for plotting
            categories = [cat for cat, _ in sorted_categories]
            counts = [count for _, count in sorted_categories]
            
            # Create the figure
            fig = go.Figure()
            
            # Add the bar chart
            fig.add_trace(
                go.Bar(
                    x=counts,
                    y=categories,
                    orientation='h',
                    marker=dict(
                        color='rgba(50, 171, 96, 0.7)',
                        line=dict(color='rgba(50, 171, 96, 1.0)', width=2)
                    )
                )
            )
            
            # Set layout options
            fig.update_layout(
                title=f"Categories: {topic_data.topic}",
                xaxis=dict(
                    title="Count",
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    title="Category",
                    autorange="reversed"  # Display in descending order
                ),
                margin=dict(l=20, r=20, t=30, b=20),
                template=self.theme,
                height=400,
                plot_bgcolor="rgba(0,0,0,0)"  # Transparent background
            )
            
            # Convert to JSON and validate structure before returning
            result = self._safe_json_encode(fig)
            if result:
                # Ensure it has the required structure for frontend display
                if 'data' in result and 'layout' in result:
                    logger.info(f"Created valid category bar chart with {len(result['data'])} traces")
                    return result
                else:
                    logger.error("Category bar chart missing required keys")
                    return None
            else:
                logger.error("Failed to encode category bar chart to JSON")
                return None
        except Exception as e:
            logger.error(f"Error creating category bar chart: {str(e)}")
            return None
    
    def create_concept_map(self, topic_data: TopicData) -> Optional[Dict[str, Any]]:
        """
        Create a concept map (network graph) visualization.
        
        Args:
            topic_data: Normalized topic data
            
        Returns:
            Data for D3.js or Plotly network visualization
        """
        try:
            # Need DBpedia categories or Wikipedia data to create a concept map
            if (not topic_data.dbpedia.categories and not topic_data.wikipedia.summary) or not topic_data.topic:
                logger.info(f"Not enough data to create concept map for {topic_data.topic}")
                return None
            
            # Create nodes and links
            nodes = [{"id": topic_data.topic, "group": 1}]
            links = []
            
            # Track how many elements we've added
            categories_added = 0
            news_added = 0
            
            # Add categories as nodes
            for idx, category in enumerate(topic_data.dbpedia.categories[:8]):
                # Clean up category name
                clean_cat = re.sub(r'^Category:', '', category)
                clean_cat = ' '.join(word.capitalize() for word in clean_cat.split('_'))
                
                # Add as node
                nodes.append({"id": clean_cat, "group": 2})
                
                # Add link to main topic
                links.append({
                    "source": topic_data.topic,
                    "target": clean_cat,
                    "value": 1
                })
                
                categories_added += 1
            
            # If we have news articles, add top headlines
            for idx, article in enumerate(topic_data.news[:5]):
                if article.title:
                    # Truncate title if too long
                    short_title = article.title[:30] + "..." if len(article.title) > 30 else article.title
                    
                    # Add as node
                    nodes.append({"id": short_title, "group": 3})
                    
                    # Add link to main topic
                    links.append({
                        "source": topic_data.topic,
                        "target": short_title,
                        "value": 1
                    })
                    
                    news_added += 1
            
            # Add interconnections between some nodes (for a more interesting graph)
            if len(nodes) >= 5:
                # Add some random connections
                import random
                secondary_nodes = [n["id"] for n in nodes[1:]]
                
                # Add up to 3 additional connections
                connections_added = 0
                for _ in range(min(3, len(secondary_nodes) // 2)):
                    if len(secondary_nodes) >= 2:
                        choices = random.sample(secondary_nodes, 2)
                        links.append({
                            "source": choices[0],
                            "target": choices[1],
                            "value": 0.5  # Weaker connection
                        })
                        connections_added += 1
                
                logger.info(f"Added {connections_added} interconnections to concept map")
            
            logger.info(f"Created concept map with {len(nodes)} nodes ({categories_added} categories, {news_added} news articles) and {len(links)} links")
            
            # Return in the expected format for D3.js
            return {
                "title": f"Concept Map: {topic_data.topic}",
                "nodes": nodes,
                "links": links
            }
        except Exception as e:
            logger.error(f"Error creating concept map: {str(e)}")
            return None
    
    def create_sentiment_chart(self, sentiment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a sentiment visualization from sentiment analysis data.
        
        Args:
            sentiment_data: Sentiment analysis data
            
        Returns:
            Plotly JSON figure for sentiment chart
        """
        if not sentiment_data or "sentiment" not in sentiment_data:
            return None
        
        try:
            # Extract sentiment value
            sentiment = sentiment_data["sentiment"].lower()
            confidence = sentiment_data.get("confidence", 0.5)
            
            # Map sentiment to numeric value
            sentiment_value = {
                "positive": 1,
                "neutral": 0,
                "negative": -1
            }.get(sentiment, 0)
            
            # Adjusted value based on confidence
            adjusted_value = sentiment_value * confidence
            
            # Create a gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=adjusted_value,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Sentiment Analysis"},
                gauge={
                    "axis": {"range": [-1, 1]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [-1, -0.3], "color": "firebrick"},
                        {"range": [-0.3, 0.3], "color": "gray"},
                        {"range": [0.3, 1], "color": "forestgreen"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": adjusted_value
                    }
                }
            ))
            
            # Set layout options
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=50, b=20),
                template=self.theme
            )
            
            # Convert to JSON and validate structure before returning
            result = self._safe_json_encode(fig)
            if result:
                # Ensure it has the required structure for frontend display
                if 'data' in result and 'layout' in result:
                    logger.info(f"Created valid sentiment chart with {len(result['data'])} traces")
                    return result
                else:
                    logger.error("Sentiment chart missing required keys")
                    return None
            else:
                logger.error("Failed to encode sentiment chart to JSON")
                return None
        except Exception as e:
            logger.error(f"Error creating sentiment chart: {str(e)}")
            return None


# Create a singleton instance
visualizer = Visualizer() 