"""
Main Flask application for the CONTRA Data-Driven Art Generator & Visual Storytelling Platform.
"""

import os
import logging
import time
import re
from flask import Flask, Blueprint, request, jsonify, render_template, send_from_directory, abort
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import json

from config import FlaskConfig, BASE_DIR, APIConfig, ContentConfig, IMAGE_CACHE_DIR
from models.data_model import GenerationResult, TopicData, WikipediaData, DBpediaData, NewsArticle, Image, Narrative, Visualization
from core.data_fetcher import data_fetcher
from core.narrative_generator import narrative_generator
from core.image_generator import image_generator
from core.visualizer import visualizer
from utils.validators import validate_input, validate_topic
from utils.helpers import format_time_elapsed
from utils.api_status import get_all_api_statuses
from utils.text_formatter import correct_spelling, format_title

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug information about environment variables
stability_key = APIConfig.STABILITY_API_KEY
if stability_key:
    masked_key = stability_key[:4] + "*" * (len(stability_key) - 8) + stability_key[-4:] if len(stability_key) > 8 else "INVALID"
    logger.info(f"Stability API Key loaded: {masked_key} (length: {len(stability_key)})")
else:
    logger.warning("No Stability API Key found in environment")

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create static file blueprint for serving generated images
images_bp = Blueprint('images', __name__, url_prefix='/images')

@images_bp.route('/<path:filename>')
def serve_image(filename):
    """Serve generated images from cache directory."""
    try:
        # Get the topic ID from the query string if provided
        topic_id = request.args.get('topic_id', '')
        logger.info(f"Serving image {filename} with topic_id: {topic_id}")
        
        # Check for fallback image first
        if filename == 'fallback.jpg':
            fallback_path = os.path.join(BASE_DIR, 'static', 'img', 'fallback.jpg')
            if os.path.exists(fallback_path):
                logger.info("Serving fallback image from static/img")
                return send_from_directory(os.path.join(BASE_DIR, 'static', 'img'), 'fallback.jpg')
        
        # Check for image_placeholder.png
        if filename == 'image_placeholder.png':
            placeholder_path = os.path.join(BASE_DIR, 'static', 'img', 'image_placeholder.png')
            if os.path.exists(placeholder_path):
                return send_from_directory(os.path.join(BASE_DIR, 'static', 'img'), 'image_placeholder.png')
        
        # Ensure the image cache directory exists
        if not os.path.exists(IMAGE_CACHE_DIR):
            os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
            logger.warning(f"Created missing image cache directory: {IMAGE_CACHE_DIR}")
            
        # Check if the requested file exists
        file_path = os.path.join(IMAGE_CACHE_DIR, filename)
        logger.info(f"Looking for image at path: {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"Requested image not found: {filename}")
            # Return fallback image instead of 404
            fallback_path = os.path.join(BASE_DIR, 'static', 'img', 'fallback.jpg')
            if os.path.exists(fallback_path):
                return send_from_directory(os.path.join(BASE_DIR, 'static', 'img'), 'fallback.jpg')
            else:
                # Return 404 - Image Not Found
                return jsonify({
                    "success": False,
                    "error": "Image not found",
                    "details": f"The requested image {filename} does not exist"
                }), 404
        
        # If topic_id is provided but empty, still serve the image (don't filter by topic)
        if not topic_id:
            logger.info(f"No topic_id provided, serving image directly: {filename}")
            return send_from_directory(IMAGE_CACHE_DIR, filename)
        
        # If topic_id is provided, verify this image belongs to that topic
        # Find the metadata file for this image
        meta_filename = filename.replace('.png', '.json')
        if not meta_filename.endswith('.json'):
            meta_filename += '.json'
        
        meta_path = os.path.join(IMAGE_CACHE_DIR, meta_filename)
        
        # If metadata file doesn't exist, still serve the image
        if not os.path.exists(meta_path):
            logger.warning(f"Metadata file not found for {filename}, serving image anyway")
            return send_from_directory(IMAGE_CACHE_DIR, filename)
            
        try:
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            # Check if the metadata contains topic_id and it matches
            if 'topic_id' in metadata:
                logger.info(f"Metadata topic_id: {metadata['topic_id']}, Requested topic_id: {topic_id}")
                
                # If the topic_id starts with the same prefix, consider it a match
                # This handles the timestamp part of the topic_id which might differ
                metadata_topic_prefix = metadata['topic_id'].split('_')[0:2]
                requested_topic_prefix = topic_id.split('_')[0:2]
                
                if metadata_topic_prefix != requested_topic_prefix and topic_id != metadata['topic_id']:
                    logger.warning(f"Topic mismatch: {metadata['topic_id']} vs {topic_id}")
                    # Topic IDs don't match, but we'll still serve the image and log the warning
                    # return send_from_directory(os.path.join(BASE_DIR, 'static', 'img'), 'fallback.jpg')
            
            # If we get here, either the topic matches or we're being lenient
            return send_from_directory(IMAGE_CACHE_DIR, filename)
                
        except Exception as e:
            logger.error(f"Error reading metadata for {filename}: {str(e)}")
            # Continue serving the image even if metadata check fails
            return send_from_directory(IMAGE_CACHE_DIR, filename)
        
        return send_from_directory(IMAGE_CACHE_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        # Try to serve the fallback image
        try:
            fallback_path = os.path.join(BASE_DIR, 'static', 'img', 'fallback.jpg')
            if os.path.exists(fallback_path):
                return send_from_directory(os.path.join(BASE_DIR, 'static', 'img'), 'fallback.jpg')
        except Exception:
            pass
        abort(404)

@api_bp.route('/generate', methods=['POST'])
def generate():
    """
    Generate narrative content, data visualizations, and images for a given topic.
    
    Expects:
    {
        "topic": "Topic string",
        "tone": "Optional tone string",
        "variants": "Optional number of image variants",
        "expertise_level": "Optional expertise level (beginner, intermediate, advanced)"
    }
    
    Returns JSON with narrative, images, visualizations and raw data.
    """
    # Extract request parameters
    try:
        data = request.get_json(silent=True)
        
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid request data"
            }), 400
            
        # Required parameter
        topic = data.get('topic', '').strip()
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
        
        # Optional parameters with defaults
        try:
            tone = data.get('tone', ContentConfig.DEFAULT_TONE)
            variants = int(data.get('variants', ContentConfig.DEFAULT_NUM_VARIANTS))
            max_length = int(data.get('max_length', ContentConfig.DEFAULT_MAX_LENGTH))
            expertise_level = data.get('expertise_level', 'intermediate')
            
            # Validate expertise level
            if expertise_level not in ['beginner', 'intermediate', 'advanced']:
                logger.warning(f"Invalid expertise level: {expertise_level}, using default")
                expertise_level = 'intermediate'
            
            # Handle temperature parameter safely
            temp_value = data.get('temperature')
            if temp_value is None:
                temperature = ContentConfig.DEFAULT_TEMPERATURE
            else:
                try:
                    temperature = float(temp_value)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid temperature value: {temp_value}, using default")
                    temperature = ContentConfig.DEFAULT_TEMPERATURE
            
            # Ensure temperature is within valid range
            temperature = max(0.1, min(1.0, temperature))
            
            logger.info(f"Using parameters: tone={tone}, variants={variants}, max_length={max_length}, temperature={temperature}, expertise_level={expertise_level}")
        except (ValueError, TypeError) as e:
            logger.error(f"Parameter conversion error: {e}")
            return jsonify({
                "success": False,
                "error": f"Invalid parameter value: {str(e)}"
            }), 400
        
        # Validate topic
        is_valid, error = validate_topic(topic)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": error
            }), 400
        
        # Apply text formatting to the topic
        corrected_topic = correct_spelling(topic)
        formatted_topic = format_title(corrected_topic)
        
        logger.info(f"Generating content for topic: '{formatted_topic}' (original: '{topic}')")
        
        # Use the corrected and formatted topic for all further processing
        if formatted_topic != topic:
            logger.info(f"Topic reformatted from '{topic}' to '{formatted_topic}'")
            topic = formatted_topic
        
        # Start processing pipeline
        response_data = {
            "success": True,
            "topic": topic,  # Use the formatted topic in response
            "processing_time": {
                "total": None,
                "data": None,
                "narrative": None,
                "images": None,
                "visualizations": None
            }
        }
        
        # Store expertise level in the response data for client-side use
        response_data["expertise_level"] = expertise_level
        
        pipeline_start = time.time()
        
        # 1. Gather topic data
        logger.info("Step 1: Gathering data...")
        data_result = None
        try:
            data_result = data_fetcher.fetch_topic_data(topic)
            
            if not data_result.get('success', False):
                logger.error(f"Data retrieval failed: {data_result.get('error', 'Unknown error')}")
                # Instead of returning an error, continue with whatever data we have
                logger.warning("Continuing with partial or fallback data")
            
            response_data["processing_time"]["data"] = data_result.get('processing_time', 'unknown')
        except Exception as e:
            logger.exception(f"Data retrieval error: {str(e)}")
            # Create minimal data result to continue the process
            data_result = {
                "success": False,
                "data": TopicData(
                    topic=topic,
                    wikipedia=WikipediaData(
                        summary=f"Information about {topic} is currently unavailable. Please try again later.",
                        url=""
                    ),
                    dbpedia=DBpediaData(),
                    news=[]
                ),
                "error": f"Failed to retrieve data: {str(e)}",
                "processing_time": "unknown"
            }
            response_data["processing_time"]["data"] = "error"
        
        # Extract topic data
        try:
            # Get topic data - should already be a TopicData object
            topic_data = data_result.get('data')
            # Validate that it's the correct type
            if not isinstance(topic_data, TopicData):
                logger.error(f"Received incorrect data type: {type(topic_data)}")
                # If it's still a dict, convert it
                try:
                    if isinstance(topic_data, dict):
                        topic_data = TopicData(
                            topic=topic,
                            wikipedia=topic_data.get('wikipedia', WikipediaData(summary="", url="")),
                            dbpedia=topic_data.get('dbpedia', DBpediaData()),
                            news=topic_data.get('news', [])
                        )
                        logger.info("Successfully converted dict to TopicData model")
                    else:
                        logger.error(f"Cannot convert data of type {type(topic_data)} to TopicData")
                        # Create a minimal TopicData object
                        topic_data = TopicData(
                            topic=topic,
                            wikipedia=WikipediaData(
                                summary=f"Information about {topic} is currently unavailable.",
                                url=""
                            ),
                            dbpedia=DBpediaData(),
                            news=[]
                        )
                except Exception as conversion_error:
                    logger.exception(f"Error converting to TopicData: {conversion_error}")
                    # Create a minimal TopicData object
                    topic_data = TopicData(
                        topic=topic,
                        wikipedia=WikipediaData(
                            summary=f"Information about {topic} is currently unavailable.",
                            url=""
                        ),
                        dbpedia=DBpediaData(),
                        news=[]
                    )
            
            # Ensure the topic is using the formatted version
            topic_data.topic = topic
                
            logger.info("Successfully created TopicData model")
        except Exception as e:
            logger.exception(f"Error creating TopicData model: {e}")
            # Create a minimal TopicData object
            topic_data = TopicData(
                topic=topic,
                wikipedia=WikipediaData(
                    summary=f"Information about {topic} is currently unavailable.",
                    url=""
                ),
                dbpedia=DBpediaData(),
                news=[]
            )
        
        # 2. Generate narrative
        logger.info("Step 2: Generating narrative...")
        narrative_result = None
        try:
            narrative_result = narrative_generator.generate_narrative(
                topic_data=topic_data,
                tone=tone,
                max_tokens=max_length,
                temperature=temperature,
                expertise_level=expertise_level
            )
            
            if not narrative_result.get('success', False):
                logger.warning(f"Narrative generation failed: {narrative_result.get('error')}")
                # Create a simple fallback narrative if API fails
                narrative_result = {
                    "success": True,
                    "narrative": {
                        "bullets": f"• Information about {topic}\n• Based on available data",
                        "narrative": topic_data.wikipedia.summary if hasattr(topic_data, 'wikipedia') and hasattr(topic_data.wikipedia, 'summary') else f"Information about {topic} could not be generated.",
                        "prompt": f"Fallback content for {topic}",
                        "model": "fallback",
                        "expertise_level": expertise_level
                    }
                }
        except Exception as e:
            logger.exception(f"Narrative generation error: {str(e)}")
            # Create a simple fallback narrative
            narrative_result = {
                "success": True,
                "narrative": {
                    "bullets": f"• Information about {topic}\n• Based on available data",
                    "narrative": topic_data.wikipedia.summary if hasattr(topic_data, 'wikipedia') and hasattr(topic_data.wikipedia, 'summary') else f"Information about {topic} could not be generated.",
                    "prompt": f"Fallback content for {topic}",
                    "model": "fallback",
                    "expertise_level": expertise_level
                }
            }
        
        # Add the narrative to the response
        if narrative_result and narrative_result.get('narrative'):
            response_data["narrative"] = narrative_result["narrative"]
            response_data["processing_time"]["narrative"] = narrative_result.get('processing_time', 'unknown')
        
        # 3. Generate images
        logger.info("Step 3: Generating images...")
        narrative_text = narrative_result['narrative']['narrative'] if narrative_result and 'narrative' in narrative_result else None
        
        image_result = None
        image_success = False
        try:
            # Only request images if we have a valid narrative
            if narrative_text and len(narrative_text.strip()) > 50:
                # Use the proper parameters for image generation
                image_result = image_generator.generate_images(
                    topic_data=topic_data,
                    narrative_text=narrative_text,
                    num_variants=variants,
                    tone=tone,
                    temperature=temperature
                )
                
                if image_result and image_result.get('success', False):
                    image_success = True
                    logger.info(f"Image generation successful: {len(image_result.get('images', []))} images created")
                    # Log more details about the images
                    for i, img in enumerate(image_result.get('images', [])):
                        logger.info(f"Image {i+1}: {img.get('file_path', 'No path')} - URL: {img.get('url', 'No URL')}")
                else:
                    logger.warning(f"Image generation failed: {image_result.get('error', 'Unknown error')}")
                    if image_result and "fallback" in image_result and image_result["fallback"]:
                        logger.info(f"Using fallback image: {image_result.get('fallback_reason', 'Unknown reason')}")
                        # Mark as success since we have a fallback
                        image_success = True
            else:
                logger.warning("Skipping image generation due to insufficient narrative")
        except Exception as e:
            logger.exception(f"Image generation error: {str(e)}")
        
        # 4. Generate visualizations
        logger.info("Step 4: Generating visualizations...")
        viz_result = None
        viz_success = False
        try:
            # Generate visualizations from the topic data
            viz_result = visualizer.create_visualizations(topic_data)
            
            if viz_result and viz_result.get('success', False):
                viz_success = True
                logger.info(f"Visualization generation successful")
                # Log which visualizations were generated
                if 'visualizations' in viz_result:
                    viz_data = viz_result['visualizations']
                    logger.info(f"Timeline: {'Created' if viz_data.get('timeline') else 'None'}")
                    logger.info(f"Category Bar: {'Created' if viz_data.get('category_bar') else 'None'}")
                    logger.info(f"Concept Map: {'Created' if viz_data.get('concept_map') else 'None'}")
            else:
                logger.warning(f"Visualization generation failed: {viz_result.get('error', 'Unknown error')}")
        except Exception as e:
            logger.exception(f"Visualization generation error: {str(e)}")
        
        # Calculate elapsed time
        elapsed_time = time.time() - pipeline_start
        
        # Create the complete result
        try:
            from models.data_model import GenerationResult, Narrative
            
            # First create the narrative object
            narrative_data = narrative_result['narrative']
            narrative = Narrative(
                bullets=narrative_data.get('bullets', ''),
                narrative=narrative_data.get('narrative', ''),
                prompt=narrative_data.get('prompt', ''),
                model=narrative_data.get('model', '')
            )
            
            result = GenerationResult(
                topic=topic,
                data=topic_data,
                narrative=narrative,
                images=[],
                processing_time=format_time_elapsed(elapsed_time)
            )
            
            # Add images if successful
            if image_result and image_success and 'images' in image_result:
                # Set images URLs relative to server
                images = []
                
                # Generate a clean topic identifier for the current topic
                current_topic_id = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())
                current_topic_id = f"topic_{current_topic_id}"
                logger.info(f"Current topic ID prefix: {current_topic_id}")
                
                for img in image_result['images']:
                    # Get topic_id from the image metadata or from the image result
                    topic_id = img.get('topic_id', image_result.get('topic_id', ''))
                    
                    if 'file_path' in img:
                        # Extract just the filename from the path
                        from pathlib import Path
                        filename = Path(img['file_path']).name
                        
                        # Check if this is a fallback image or a generated image
                        if 'fallback' in image_result and image_result['fallback']:
                            # Use the images endpoint for fallback images
                            img['url'] = f"/images/{filename}?topic_id={topic_id}"
                        else:
                            # Use the images endpoint for generated images - include topic_id
                            img['url'] = f"/images/{filename}?topic_id={topic_id}"
                    
                    # Make sure the image has a valid URL
                    if 'url' not in img:
                        # Provide a fallback URL if none exists
                        img['url'] = f"/images/fallback.jpg?topic_id={topic_id}"
                    
                    # Create proper Image objects instead of using dictionaries
                    image_obj = Image(
                        file_path=img.get('file_path', ''),
                        prompt=img.get('prompt', ''),
                        model_version=img.get('model_version', ''),
                        style=img.get('style', 'photorealistic'),
                        width=img.get('width', 512),
                        height=img.get('height', 512),
                        url=img.get('url', '/images/fallback.jpg'),  # URL with topic_id 
                        topic_id=topic_id  # Store the topic_id in the image object
                    )
                    images.append(image_obj)
                result.images = images
            
            # Add visualizations if available
            if viz_result and viz_success and 'visualizations' in viz_result:
                # Create a Visualization object from the dict
                viz_data = viz_result['visualizations']
                visualization = Visualization(
                    timeline=viz_data.get('timeline'),
                    category_bar=viz_data.get('category_bar'),
                    concept_map=viz_data.get('concept_map')
                )
                result.visualizations = visualization
            
            # Return the full result
            result_dict = result.to_dict()
            logger.info(f"Generation successful for topic: {topic}")
            
            # Log result size
            import sys
            import json
            result_json = json.dumps(result_dict)
            result_size = sys.getsizeof(result_json)
            logger.info(f"Result size: {result_size} bytes")
            
            response_data["result"] = result_dict
            response_data["processing_time"]["total"] = format_time_elapsed(elapsed_time)
            
            return jsonify(response_data)
        except Exception as e:
            logger.exception(f"Error serializing result: {e}")
            # Return a simplified result instead of failing
            return jsonify({
                "success": True,
                "result": {
                    "topic": topic,
                    "message": "Content generated but could not be fully serialized",
                    "narrative": narrative_result['narrative']['narrative'] if narrative_result and 'narrative' in narrative_result else f"Information about {topic}"
                }
            })
        
    except Exception as e:
        logger.exception(f"Unexpected error during generation: {str(e)}")
        
        # Get traceback
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Traceback: {tb}")
        
        return jsonify({
            "success": False,
            "error": "Server error",
            "details": str(e)
        }), 500


@api_bp.route('/styles', methods=['GET'])
def get_styles():
    """Get available image generation styles."""
    styles = image_generator.get_available_styles()
    return jsonify({
        "success": True,
        "styles": styles
    })


@api_bp.route('/related', methods=['GET'])
def get_related_topics():
    """Get related topics for a given topic."""
    topic = request.args.get('topic')
    if not topic:
        return jsonify({
            "success": False,
            "error": "Missing 'topic' parameter"
        }), 400
    
    # Validate topic
    valid, error = validate_topic(topic)
    if not valid:
        return jsonify({
            "success": False,
            "error": error
        }), 400
    
    related = data_fetcher.get_related_topics(topic)
    return jsonify({
        "success": True,
        "topic": topic,
        "related_topics": related
    })


@api_bp.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    """Analyze sentiment for a topic."""
    data = request.get_json(silent=True)
    if not data or 'topic' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'topic' field"
        }), 400

    topic = data['topic']
    
    # Fetch topic data
    data_result = data_fetcher.fetch_topic_data(topic)
    if not data_result.get('success', False):
        return jsonify({
            "success": False,
            "error": "Failed to fetch topic data"
        }), 500
    
    # Get topic data from result
    from models.data_model import TopicData
    topic_data = data_result.get('data')
    if not isinstance(topic_data, TopicData):
        return jsonify({
            "success": False,
            "error": "Invalid topic data format"
        }), 500

    # Analyze sentiment
    sentiment_result = narrative_generator.analyze_sentiment(topic_data)
    
    if not sentiment_result.get('success', False):
        return jsonify({
            "success": False,
            "error": "Failed to analyze sentiment"
        }), 500
    
    return jsonify({
        "success": True,
        "topic": topic,
        "sentiment": sentiment_result['sentiment_analysis']
    })


@api_bp.route('/story', methods=['POST'])
def generate_story():
    """Generate a creative story for a topic."""
    data = request.get_json(silent=True)
    if not data or 'topic' not in data:
        return jsonify({
            "success": False,
            "error": "Missing 'topic' field"
        }), 400
    
    topic = data['topic']
    style = data.get('style', 'short story')
    genre = data.get('genre')
    
    # Get temperature parameter with default if not provided
    try:
        temperature = float(data.get('temperature', ContentConfig.DEFAULT_TEMPERATURE))
    except (ValueError, TypeError):
        temperature = ContentConfig.DEFAULT_TEMPERATURE
    
    # Ensure temperature is in valid range
    temperature = max(0.1, min(1.0, temperature))
    
    # Fetch topic data
    data_result = data_fetcher.fetch_topic_data(topic)
    if not data_result.get('success', False):
        return jsonify({
            "success": False,
            "error": "Failed to fetch topic data"
        }), 500
    
    # Get topic data from result
    from models.data_model import TopicData
    topic_data = data_result.get('data')
    if not isinstance(topic_data, TopicData):
        return jsonify({
            "success": False,
            "error": "Invalid topic data format"
        }), 500

    # Generate creative story
    story_result = narrative_generator.generate_creative_story(
        topic_data=topic_data,
        style=style,
        genre=genre,
        temperature=temperature
    )
    
    if not story_result.get('success', False):
        return jsonify({
            "success": False,
            "error": "Failed to generate story"
        }), 500
    
    return jsonify({
        "success": True,
        "topic": topic,
        "style": style,
        "genre": genre,
        "story": story_result['story']
    })


@api_bp.route('/conversation', methods=['POST'])
def conversation():
    """
    Handle conversational questions about the generated topic.
    
    Expects:
    {
        "topic": "Topic string",
        "question": "User's question",
        "conversation_history": [{"role": "user|ai|system", "content": "message text"}],
        "tone": "Optional tone string"
    }
    
    Returns JSON with AI response and relevant context.
    """
    # Extract request parameters
    try:
        data = request.get_json(silent=True)
        
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "error": "Invalid request data"
            }), 400
            
        # Required parameters
        topic = data.get('topic', '').strip()
        question = data.get('question', '').strip()
        
        if not topic:
            return jsonify({
                "success": False,
                "error": "Topic is required"
            }), 400
            
        if not question:
            return jsonify({
                "success": False,
                "error": "Question is required"
            }), 400
        
        # Optional parameters
        conversation_history = data.get('conversation_history', [])
        tone = data.get('tone', ContentConfig.DEFAULT_TONE)
        
        # Handle temperature parameter safely
        temp_value = data.get('temperature')
        if temp_value is None:
            temperature = ContentConfig.DEFAULT_TEMPERATURE
        else:
            try:
                temperature = float(temp_value)
            except (ValueError, TypeError):
                logger.warning(f"Invalid temperature value: {temp_value}, using default")
                temperature = ContentConfig.DEFAULT_TEMPERATURE
        
        # Ensure temperature is within valid range
        temperature = max(0.1, min(1.0, temperature))
        
        # Validate conversation history format
        if not isinstance(conversation_history, list):
            conversation_history = []
        
        # Log request
        logger.info(f"Conversation request for topic: '{topic}', question: '{question}', tone: '{tone}'")
        
        # Fetch topic data if we need additional context
        topic_data = None
        try:
            # Get topic data for context
            data_result = data_fetcher.fetch_topic_data(topic)
            if data_result.get('success', False):
                topic_data = data_result.get('data')
        except Exception as e:
            logger.warning(f"Error fetching topic data for conversation: {e}")
            # Continue without topic data - we'll use what's available
        
        # Generate the AI response
        try:
            # Use the narrative generator to create a conversation response
            response_result = narrative_generator.generate_conversation_response(
                topic=topic,
                question=question,
                conversation_history=conversation_history,
                topic_data=topic_data,
                tone=tone,
                temperature=temperature
            )
            
            if not response_result.get('success', False):
                return jsonify({
                    "success": False,
                    "error": response_result.get('error', 'Failed to generate response')
                }), 500
            
            # Return the successful response
            return jsonify({
                "success": True,
                "topic": topic,
                "response": response_result.get('response', ''),
                "references": response_result.get('references', []),
                "processing_time": response_result.get('processing_time', '')
            })
            
        except Exception as e:
            logger.exception(f"Error generating conversation response: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    except Exception as e:
        logger.exception(f"Unexpected error during conversation: {e}")
        return jsonify({
            "success": False,
            "error": "Server error",
            "details": str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint with detailed status information."""
    version = "1.0.0"
    api_status = get_all_api_statuses()
    response = {
        "success": True,
        "status": api_status["overall_status"],
        "version": version,
        "apis": api_status["services"],
        "summary": api_status["summary"]
    }
    status_code = 200
    if api_status["overall_status"] == "degraded":
        status_code = 207  # Multi-Status
    elif api_status["overall_status"] == "incomplete":
        status_code = 424  # Failed Dependency
    elif api_status["overall_status"] == "down":
        status_code = 503  # Service Unavailable
    return jsonify(response), status_code


@api_bp.route('/status', methods=['GET'])
def api_status():
    """API status endpoint for compatibility with frontend checks (returns same as /api/health)."""
    version = "1.0.0"
    api_status = get_all_api_statuses()
    response = {
        "success": True,
        "status": api_status["overall_status"],
        "version": version,
        "apis": api_status["services"],
        "summary": api_status["summary"]
    }
    status_code = 200
    if api_status["overall_status"] == "degraded":
        status_code = 207  # Multi-Status
    elif api_status["overall_status"] == "incomplete":
        status_code = 424  # Failed Dependency
    elif api_status["overall_status"] == "down":
        status_code = 503  # Service Unavailable
    return jsonify(response), status_code


# Error handlers
@api_bp.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions."""
    logger.exception(e)
    
    # If it's an HTTP exception, use its error code
    if isinstance(e, HTTPException):
        response = jsonify({
            "success": False,
            "error": e.description
        })
        response.status_code = e.code
        return response
    
    # Otherwise return a 500 error
    return jsonify({
        "success": False,
        "error": "Server error",
        "details": str(e)
    }), 500


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Apply configuration
    app.config['SECRET_KEY'] = FlaskConfig.SECRET_KEY
    app.config['DEBUG'] = FlaskConfig.DEBUG
    
    # Ensure required directories exist
    ensure_directories()
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(images_bp)
    
    # Add direct route for static files - especially for images
    @app.route('/direct-static/<path:filename>')
    def direct_static(filename):
        """Serve static files directly."""
        return send_from_directory(os.path.join(BASE_DIR, 'static'), filename)
    
    # Root route
    @app.route('/')
    def index():
        """Render the main application page."""
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """Render the about page."""
        return render_template('about.html')
    
    @app.route('/status')
    def status():
        """Render the status page."""
        # Get API status information
        api_status = get_all_api_statuses()
        
        return render_template(
            'status.html',
            status=api_status["overall_status"],
            apis=api_status["services"],
            summary=api_status["summary"]
        )
    
    # Handle 404 errors
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            # Return JSON for API routes
            return jsonify({
                "success": False,
                "error": "Endpoint not found"
            }), 404
        # Return HTML for other routes
        return render_template('404.html'), 404
    
    # Register global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all exceptions."""
        logger.exception(e)
        
        # If it's an HTTP exception, use its error code
        if isinstance(e, HTTPException):
            if request.path.startswith('/api/'):
                # Return JSON for API routes
                response = jsonify({
                    "success": False,
                    "error": e.description
                })
                response.status_code = e.code
                return response
            # Return HTML for other routes
            return render_template('error.html', error=e), e.code
        
        # Otherwise return a 500 error
        if request.path.startswith('/api/'):
            # Return JSON for API routes
            return jsonify({
                "success": False,
                "error": "Server error",
                "details": str(e)
            }), 500
        # Return HTML for other routes
        return render_template('error.html', error=e), 500

    @app.route('/AI')
    def ai_page():
        return render_template('index.html')

    return app

def ensure_directories():
    """Ensure all required directories exist and create fallback images."""
    try:
        # Ensure directories exist
        directories = [
            os.path.join(BASE_DIR, 'static/img'),
            IMAGE_CACHE_DIR
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
        
        # Create fallback image if it doesn't exist
        from services.stable_diffusion import stable_diffusion_client
        stable_diffusion_client._ensure_fallback_image()
        
        # Create placeholder image
        placeholder_path = os.path.join(BASE_DIR, 'static/img/image_placeholder.png')
        if not os.path.exists(placeholder_path):
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (512, 512), color=(40, 40, 40))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple image icon
            icon_size = 200
            x_center, y_center = 256, 256
            
            # Draw frame
            draw.rectangle(
                (x_center - icon_size//2, y_center - icon_size//2, 
                 x_center + icon_size//2, y_center + icon_size//2),
                outline=(200, 200, 200),
                width=4
            )
            
            # Draw mountain icon
            points = [
                (x_center - icon_size//2 + 20, y_center + icon_size//2 - 20),  # Bottom left
                (x_center, y_center - icon_size//4),                         # Middle peak
                (x_center + icon_size//4, y_center + icon_size//4),           # Small peak
                (x_center + icon_size//2 - 20, y_center + icon_size//2 - 20)   # Bottom right
            ]
            draw.polygon(points, fill=(100, 100, 100))
            
            # Draw sun
            sun_radius = 30
            draw.ellipse(
                (x_center - icon_size//4 - sun_radius, y_center - icon_size//4 - sun_radius,
                 x_center - icon_size//4 + sun_radius, y_center - icon_size//4 + sun_radius),
                fill=(180, 180, 100)
            )
            
            img.save(placeholder_path, "PNG")
            logger.info(f"Created placeholder image at {placeholder_path}")
            
    except Exception as e:
        logger.error(f"Error ensuring directories and files: {e}")
        # Continue even if there's an error - the application should still run


if __name__ == '__main__':
    flask_app = create_app()
    port = FlaskConfig.PORT
    flask_app.run(host='0.0.0.0', port=port)
