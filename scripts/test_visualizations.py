#!/usr/bin/env python
"""
Script to test visualization generation.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import from the application
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import required modules
from models.data_model import TopicData, WikipediaData, DBpediaData, NewsArticle
from core.visualizer import visualizer

def create_sample_data(topic="Test Topic"):
    """Create sample topic data for testing."""
    # Create sample Wikipedia data
    wikipedia = WikipediaData(
        summary="""
        This is a test summary. In 1990, something happened. Then in 2000, 
        another important event occurred. By 2010, things had changed significantly.
        The events of 1850 are also notable, as are those from 1905.
        """,
        url=f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    )
    
    # Create sample DBpedia data
    dbpedia = DBpediaData(
        abstract="""
        This is a test abstract. The category includes important items.
        """,
        categories=[
            "Category:Test_Category",
            "Category:Sample_Data",
            "Category:Visualization_Testing",
            "Category:Mock_Data",
            "Category:Example_Categories"
        ],
        resource_uri=f"http://dbpedia.org/resource/{topic.replace(' ', '_')}"
    )
    
    # Create sample news articles
    news = [
        NewsArticle(
            title="Test News Article 1",
            url="https://example.com/news/1",
            publisher="Test Publisher",
            published_at="2023-01-15T12:00:00Z",
            description="This is a test news article."
        ),
        NewsArticle(
            title="Test News Article 2",
            url="https://example.com/news/2",
            publisher="Another Publisher",
            published_at="2023-02-20T15:30:00Z",
            description="This is another test news article."
        ),
        NewsArticle(
            title="Test News Article 3",
            url="https://example.com/news/3",
            publisher="Third Publisher",
            published_at="2023-03-10T09:45:00Z",
            description="This is a third test news article."
        )
    ]
    
    # Create the topic data
    topic_data = TopicData(
        topic=topic,
        wikipedia=wikipedia,
        dbpedia=dbpedia,
        news=news
    )
    
    return topic_data

def test_visualization_generation():
    """Test the visualization generation function."""
    # Create sample data
    topic_data = create_sample_data("World War II")
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    viz_result = visualizer.create_visualizations(topic_data)
    
    # Check the result
    if viz_result.get("success", False):
        logger.info("Visualization generation successful")
        
        visualizations = viz_result.get("visualizations", {})
        
        # Check timeline
        if visualizations.get("timeline"):
            logger.info("Timeline visualization created")
            timeline = visualizations["timeline"]
            logger.info(f"Timeline keys: {list(timeline.keys())}")
            if 'data' in timeline and 'layout' in timeline:
                logger.info(f"Timeline has proper Plotly format with {len(timeline['data'])} traces")
            else:
                logger.error(f"Timeline is missing data or layout keys")
        else:
            logger.warning("No timeline visualization created")
        
        # Check category bar
        if visualizations.get("category_bar"):
            logger.info("Category bar visualization created")
            category_bar = visualizations["category_bar"]
            logger.info(f"Category bar keys: {list(category_bar.keys())}")
            if 'data' in category_bar and 'layout' in category_bar:
                logger.info(f"Category bar has proper Plotly format with {len(category_bar['data'])} traces")
            else:
                logger.error(f"Category bar is missing data or layout keys")
        else:
            logger.warning("No category bar visualization created")
        
        # Check concept map
        if visualizations.get("concept_map"):
            logger.info("Concept map visualization created")
            concept_map = visualizations["concept_map"]
            logger.info(f"Concept map keys: {list(concept_map.keys())}")
            if 'nodes' in concept_map and 'links' in concept_map:
                logger.info(f"Concept map has {len(concept_map['nodes'])} nodes and {len(concept_map['links'])} links")
            else:
                logger.error(f"Concept map is missing nodes or links")
        else:
            logger.warning("No concept map visualization created")
        
        # Save the visualization data to a file for inspection
        output_dir = Path(__file__).resolve().parent.parent / "debug"
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / "viz_test_output.json"
        with open(output_file, 'w') as f:
            json.dump(viz_result, f, indent=2)
        
        logger.info(f"Visualization data saved to {output_file}")
    else:
        logger.error(f"Visualization generation failed: {viz_result.get('error', 'Unknown error')}")

def fix_visualization_output():
    """Check and fix the visualization output format."""
    # Create sample data
    topic_data = create_sample_data("World War II")
    
    # Test each visualization type directly
    logger.info("Testing individual visualization functions...")
    
    # 1. Timeline
    logger.info("Testing timeline generation...")
    timeline = visualizer.create_timeline(topic_data)
    
    if timeline:
        logger.info(f"Timeline keys: {list(timeline.keys())}")
        
        # Check if structure is proper for Plotly
        if 'data' not in timeline or 'layout' not in timeline:
            logger.error("Timeline doesn't have proper Plotly format")
            
            # If it's a raw figure, convert it properly
            import plotly.graph_objects as go
            from plotly.utils import PlotlyJSONEncoder
            import json
            
            # Create a simple figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 1, 1], mode='markers+lines'))
            fig.update_layout(title="Test Figure")
            
            # Output proper encoding
            json_fig = json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))
            logger.info(f"Properly encoded figure keys: {list(json_fig.keys())}")
            
            # Save example
            output_dir = Path(__file__).resolve().parent.parent / "debug"
            output_dir.mkdir(exist_ok=True)
            
            with open(output_dir / "plotly_example.json", 'w') as f:
                json.dump(json_fig, f, indent=2)
            
            logger.info(f"Example Plotly figure saved to {output_dir}/plotly_example.json")
        else:
            logger.info(f"Timeline has proper format with {len(timeline['data'])} traces")
    else:
        logger.warning("No timeline was generated")

    # 2. Category Bar
    logger.info("Testing category bar generation...")
    category_bar = visualizer.create_category_bar(topic_data)
    
    if category_bar:
        logger.info(f"Category bar keys: {list(category_bar.keys())}")
        
        # Check if structure is proper for Plotly
        if 'data' not in category_bar or 'layout' not in category_bar:
            logger.error("Category bar doesn't have proper Plotly format")
        else:
            logger.info(f"Category bar has proper format with {len(category_bar['data'])} traces")
    else:
        logger.warning("No category bar was generated")
        
    # 3. Concept Map
    logger.info("Testing concept map generation...")
    concept_map = visualizer.create_concept_map(topic_data)
    
    if concept_map:
        logger.info(f"Concept map keys: {list(concept_map.keys())}")
        
        # Check if structure is proper for D3.js
        if 'nodes' not in concept_map or 'links' not in concept_map:
            logger.error("Concept map doesn't have proper D3.js format")
        else:
            logger.info(f"Concept map has proper format with {len(concept_map['nodes'])} nodes and {len(concept_map['links'])} links")
    else:
        logger.warning("No concept map was generated")
    
    # Test full visualization process
    logger.info("Testing complete visualization generation...")
    viz_result = visualizer.create_visualizations(topic_data)
    
    if viz_result and viz_result.get('success', False):
        logger.info(f"Full visualization generation successful")
        
        # Save to debug directory for inspection
        output_dir = Path(__file__).resolve().parent.parent / "debug"
        output_dir.mkdir(exist_ok=True)
        
        import json  # Import json here to fix UnboundLocalError
        with open(output_dir / "full_viz_output.json", 'w') as f:
            json.dump(viz_result, f, indent=2)
        
        logger.info(f"Full visualization output saved to {output_dir}/full_viz_output.json")
    else:
        logger.error(f"Full visualization generation failed: {viz_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("\n===== TESTING VISUALIZATION GENERATION =====\n")
    
    # Test visualization generation
    test_visualization_generation()
    
    print("\n===== CHECKING AND FIXING VISUALIZATION FORMAT =====\n")
    
    # Check and fix visualization output format
    fix_visualization_output()
    
    print("\nVisualization tests completed.") 