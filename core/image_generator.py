"""
Image generator for creating images using Stable Diffusion.
"""

import logging
import time
import re
from typing import Dict, List, Any, Optional, Tuple

from models.data_model import TopicData, Image
from services.stable_diffusion import stable_diffusion_client
from config import ContentConfig
from utils.helpers import format_time_elapsed, truncate_text, iso_now

# Configure logging
logger = logging.getLogger(__name__)

class ImageGenerator:
    """
    Generates images using Stable Diffusion based on topic data.
    """
    
    def __init__(self):
        """Initialize the image generator."""
        # StableDiffusionClient is initialized as a singleton in its module
        pass
    
    def generate_images(
        self,
        topic_data: Optional[TopicData] = None,
        narrative_text: Optional[str] = None,
        num_variants: int = None,
        width: int = None,
        height: int = None,
        topic: Optional[str] = None,
        context: Optional[str] = None,
        tone: Optional[str] = None,
        temperature: float = None,
        overwrite_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Generate images for a topic using available data.
        Automatically determines appropriate style and emotion based on the topic, context and tone.
        
        Args:
            topic_data: Normalized topic data
            narrative_text: Optional narrative text to include in prompt
            num_variants: Number of image variants to generate
            width: Image width in pixels
            height: Image height in pixels
            topic: Alternative way to specify the topic (for backward compatibility)
            context: Alternative way to specify the context text (for backward compatibility)
            tone: Narrative tone (e.g., "informative", "dramatic", "poetic") to match image style
            temperature: Creativity level for image generation (0.1-1.0)
            overwrite_cache: Whether to force recreation of images
            
        Returns:
            Dictionary with generated images and metadata
        """
        start_time = time.time()
        
        # Handle backward compatibility with topic and context parameters
        if not topic_data and topic:
            # Create a simple TopicData object from the topic string
            from models.data_model import WikipediaData, DBpediaData
            topic_data = TopicData(
                topic=topic,
                wikipedia=WikipediaData(summary=context if context else "", url=""),
                dbpedia=DBpediaData(),
                news=[]
            )
            logger.info(f"Created TopicData from topic string: {topic}")
            
        # Use context if narrative_text is not provided
        if not narrative_text and context:
            narrative_text = context
        
        # Ensure we have topic_data
        if not topic_data:
            logger.error("No topic data provided for image generation")
            return {
                "success": False,
                "error": "No topic data provided for image generation"
            }
        
        # Extract the topic for use as topic_id
        current_topic = topic_data.topic
        
        # Create a unique topic_id by sanitizing the topic name
        topic_id = re.sub(r'[^a-zA-Z0-9]', '_', current_topic.lower())
        topic_id = f"topic_{topic_id}_{int(time.time())}"
        
        # Use defaults from config if not specified - default to 16:9 aspect ratio
        num_variants = num_variants or ContentConfig.DEFAULT_NUM_VARIANTS
        width = width or ContentConfig.DEFAULT_IMAGE_WIDTH
        height = height or int(width * 9 / 16)  # Default to 16:9 ratio
        temperature = temperature or ContentConfig.DEFAULT_TEMPERATURE
        
        # Build context text from Wikipedia and/or DBpedia
        context_text = ""
        if topic_data.wikipedia.summary:
            context_text = topic_data.wikipedia.summary
        elif topic_data.dbpedia.abstract:
            context_text = topic_data.dbpedia.abstract
        
        # Include narrative text if provided (it might have better context)
        if narrative_text:
            context_text = narrative_text
        
        # Automatically determine style and emotion based on the topic, context and tone
        style, emotion = self._analyze_topic_for_style_and_emotion(topic_data.topic, context_text, tone)
        
        logger.info(f"Generating images for topic: {topic_data.topic} (tone={tone}, style={style}, emotion={emotion}, variants={num_variants}, temperature={temperature})")
        
        # Get news headlines
        headlines = []
        for article in topic_data.news[:3]:
            if article.title:
                headlines.append(article.title)
        
        # Build the prompt
        prompt = stable_diffusion_client.build_prompt(
            topic=topic_data.topic,
            context_text=context_text,
            style=style,
            emotion=emotion,
            headlines=headlines,
            tone=tone,  # Pass tone to prompt builder
            temperature=temperature  # Pass temperature to prompt builder
        )
        
        # Check if we have a valid Stability API key instead of checking for endpoint
        if not stable_diffusion_client.api_key or stable_diffusion_client.api_key.strip() == "":
            logger.warning("No Stability AI API key configured. Using fallback image.")
            # Create a fallback image result
            return {
                "success": True,
                "images": [{
                    "file_path": "fallback.jpg",
                    "url": "/images/fallback.jpg",  # Use updated image path
                    "prompt": prompt,
                    "model_version": "fallback",
                    "timestamp": iso_now(),
                    "style": style,
                    "width": width,
                    "height": height,
                    "topic_id": topic_id
                }],
                "prompt": prompt,
                "style": style,
                "emotion": emotion,
                "processing_time": format_time_elapsed(time.time() - start_time),
                "fallback": True,
                "fallback_reason": "No Stability AI API key configured",
                "topic_id": topic_id
            }
        
        # Generate images
        try:
            result = stable_diffusion_client.generate_image(
                prompt=prompt,
                width=width,
                height=height,
                num_variants=num_variants,
                overwrite_cache=overwrite_cache,
                topic_id=topic_id  # Pass the topic ID to avoid mixing images from different topics
            )
            
            if not result or any(not r.get("success", False) for r in result):
                # If any image generation failed
                elapsed_time = time.time() - start_time
                
                # If all failed, check if we have any partial results
                if all(not r.get("success", False) for r in result):
                    # No successful images generated
                    logger.error("All image generation attempts failed")
                    # Return a fallback response
                    return {
                        "success": True,
                        "images": [{
                            "file_path": "fallback.jpg",
                            "url": "/images/fallback.jpg",  # Use updated image path
                            "prompt": prompt,
                            "model_version": "fallback",
                            "timestamp": iso_now(),
                            "style": style,
                            "width": width,
                            "height": height,
                            "topic_id": topic_id
                        }],
                        "prompt": prompt,
                        "style": style,
                        "emotion": emotion,
                        "processing_time": format_time_elapsed(elapsed_time),
                        "fallback": True,
                        "fallback_reason": "Image generation failed",
                        "details": result,
                        "topic_id": topic_id
                    }
                else:
                    # Some images were generated successfully
                    return {
                        "success": False,
                        "error": "Failed to generate one or more images",
                        "partial_results": result,
                        "processing_time": format_time_elapsed(elapsed_time),
                        "topic_id": topic_id
                    }
            
            # Create image models
            images = []
            for img_data in result:
                if img_data.get("success", False):
                    # Make sure URL is set
                    if "url" not in img_data and "file_path" in img_data:
                        from pathlib import Path
                        filename = Path(img_data["file_path"]).name
                        img_data["url"] = f"/images/{filename}"
                        
                    images.append(Image(
                        file_path=img_data.get("file_path", ""),
                        prompt=img_data.get("prompt", ""),
                        model_version=img_data.get("model_version", ""),
                        timestamp=img_data.get("timestamp", ""),
                        style=style,
                        width=img_data.get("width", width),
                        height=img_data.get("height", height),
                        url=img_data.get("url", "/static/img/fallback.jpg"),  # Ensure URL is set
                        topic_id=topic_id
                    ))
            
            # Return the result
            elapsed_time = time.time() - start_time
            return {
                "success": True,
                "images": [img.to_dict() for img in images],
                "prompt": prompt,
                "style": style,
                "emotion": emotion,
                "processing_time": format_time_elapsed(elapsed_time),
                "topic_id": topic_id
            }
        except Exception as e:
            # Handle any unexpected errors
            logger.exception(f"Unexpected error during image generation: {str(e)}")
            elapsed_time = time.time() - start_time
            
            # Return a fallback image
            return {
                "success": True,
                "images": [{
                    "file_path": "fallback.jpg",
                    "url": "/images/fallback.jpg",  # Use updated image path
                    "prompt": prompt,
                    "model_version": "fallback",
                    "timestamp": iso_now(),
                    "style": style,
                    "width": width,
                    "height": height,
                    "topic_id": topic_id
                }],
                "prompt": prompt,
                "style": style,
                "emotion": emotion,
                "processing_time": format_time_elapsed(elapsed_time),
                "fallback": True,
                "fallback_reason": f"Error: {str(e)}",
                "topic_id": topic_id
            }
    
    def _analyze_topic_for_style_and_emotion(self, topic: str, context_text: str, tone: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Analyze the topic and context to determine the most appropriate art style and emotion.
        
        Args:
            topic: The main topic
            context_text: Additional context information
            tone: Narrative tone (e.g., "informative", "dramatic", "poetic") to match image style
            
        Returns:
            Tuple of (style, emotion)
        """
        # Use LLaMA if available, otherwise use rule-based approach
        try:
            from services.groq_client import groq_client
            
            # Try to use LLaMA for more intelligent analysis
            if groq_client.api_key:
                return self._analyze_with_llama(topic, context_text, tone)
        except Exception as e:
            logger.warning(f"Could not use LLaMA for style analysis: {e}")
        
        # Fallback to rule-based approach
        return self._analyze_with_rules(topic, context_text, tone)
    
    def _analyze_with_llama(self, topic: str, context_text: str, tone: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Use LLaMA to determine style and emotion.
        
        Args:
            topic: The main topic
            context_text: Additional context information
            tone: Narrative tone to match image style
            
        Returns:
            Tuple of (style, emotion)
        """
        from services.groq_client import groq_client
        
        # Create a prompt for LLaMA to determine style and emotion
        prompt = f"""
        Based on the topic "{topic}" and the following context, determine the most appropriate art style and emotional tone for an image generation.
        
        CONTEXT:
        {truncate_text(context_text, 500)}
        
        {"NARRATIVE TONE: " + tone if tone else ""}
        
        Choose from the following styles:
        - photorealistic
        - oil painting
        - watercolor
        - digital art
        - pencil sketch
        - pop art
        - abstract art
        - cinematic
        - anime
        - cartoon
        - nature photography
        - scientific illustration
        - minimalist
        - artistic
        
        Return ONLY a JSON object with two fields:
        1. "style": The chosen art style
        2. "emotion": A single word or short phrase describing the emotional tone (e.g., "serene", "energetic", "melancholic")
        
        The style and emotion should make sense together and be appropriate for the topic.
        """
        
        try:
            # Get structured output from LLaMA
            result = groq_client.parse_structured_output(prompt, {"style": "string", "emotion": "string"})
            
            if result.get("success", False) and "data" in result:
                data = result["data"]
                style = data.get("style", "photorealistic").lower()
                emotion = data.get("emotion", None)
                
                # Validate the style
                valid_styles = ["photorealistic", "oil painting", "watercolor", "digital art", 
                                "pencil sketch", "pop art", "abstract art", "cinematic", "anime", 
                                "cartoon", "nature photography", "scientific illustration", 
                                "minimalist", "artistic"]
                
                if style not in valid_styles:
                    logger.warning(f"LLaMA returned invalid style: {style}. Using default.")
                    style = "photorealistic"
                
                return style, emotion
            else:
                logger.warning("Failed to get valid style/emotion from LLaMA")
        except Exception as e:
            logger.warning(f"Error using LLaMA for style analysis: {e}")
        
        # Fallback to rule-based approach
        return self._analyze_with_rules(topic, context_text, tone)
    
    def _analyze_with_rules(self, topic: str, context_text: str, tone: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Use rule-based approach to determine style and emotion.
        
        Considers the specified tone to match image style with narrative tone.
        
        Args:
            topic: The main topic
            context_text: Additional context information
            tone: Narrative tone (e.g., "informative", "dramatic", "poetic")
            
        Returns:
            Tuple of (style, emotion)
        """
        # Prioritize tone-based style selection if tone is provided
        if tone:
            # Map narrative tones to appropriate image styles and emotions
            tone_style_map = {
                "dramatic": ("cinematic", "intense"),
                "poetic": ("artistic", "contemplative"),
                "humorous": ("cartoon", "playful"),
                "technical": ("digital art", "precise"),
                "simple": ("minimalist", "calm"),
                "informative": ("realistic", "neutral")
            }
            
            # If tone is in our mapping, use the predefined style and emotion
            if tone.lower() in tone_style_map:
                return tone_style_map[tone.lower()]
        
        # If no tone provided or not in our mapping, continue with regular analysis
        
        # Make text lowercase for easier matching
        topic_lower = topic.lower()
        context_lower = context_text.lower() if context_text else ""
        
        # Historical content tends to work better with traditional art styles
        historical_keywords = ['ancient', 'medieval', 'history', 'historical', 'century', 'war', 'empire',
                               'kingdom', 'dynasty', 'revolution', 'civilization']
        
        # Scientific content tends to work better with precise or digital styles
        scientific_keywords = ['science', 'physics', 'chemistry', 'biology', 'mathematics',
                               'quantum', 'molecular', 'scientific', 'theory', 'experiment']
        
        # Technological content tends to work better with digital or futuristic styles
        tech_keywords = ['technology', 'computer', 'digital', 'internet', 'software', 'hardware',
                         'algorithm', 'data', 'artificial intelligence', 'machine learning']
        
        # Natural subjects tend to work better with photographic styles
        nature_keywords = ['nature', 'animal', 'plant', 'forest', 'ocean', 'mountain', 'landscape',
                           'wildlife', 'ecosystem', 'environment', 'biology']
        
        # Abstract concepts tend to work better with abstract or surrealist styles
        abstract_keywords = ['idea', 'concept', 'philosophy', 'abstract', 'theory', 'consciousness',
                            'emotion', 'feeling', 'dream', 'perception', 'reality']
        
        # Determine if topic matches any of our categories
        is_historical = any(keyword in topic_lower or keyword in context_lower for keyword in historical_keywords)
        is_scientific = any(keyword in topic_lower or keyword in context_lower for keyword in scientific_keywords)
        is_tech = any(keyword in topic_lower or keyword in context_lower for keyword in tech_keywords)
        is_nature = any(keyword in topic_lower or keyword in context_lower for keyword in nature_keywords)
        is_abstract = any(keyword in topic_lower or keyword in context_lower for keyword in abstract_keywords)
        
        # Choose a style based on the topic categorization
        if is_historical:
            style = "oil painting"
            emotion = "nostalgic"
        elif is_scientific:
            style = "scientific illustration"
            emotion = "curious"
        elif is_tech:
            style = "digital art"
            emotion = "futuristic"
        elif is_nature:
            style = "nature photography"
            emotion = "serene"
        elif is_abstract:
            style = "abstract art"
            emotion = "contemplative"
        else:
            # Default to photorealistic as it tends to work well with many topics
            style = "photorealistic"
            emotion = None
        
        return style, emotion
    
    def enhance_image_prompt(self, topic: str, context_text: str) -> str:
        """
        Enhance an image generation prompt with additional details.
        
        Uses the LLaMA model to expand a simple topic into a detailed
        image generation prompt.
        
        Args:
            topic: Topic string
            context_text: Additional context text
            
        Returns:
            Enhanced prompt string
        """
        from services.groq_client import groq_client
        
        # Create prompt for LLaMA
        llama_prompt = f"""
        Create a detailed Stable Diffusion prompt for an image about "{topic}".
        
        Context information: {truncate_text(context_text, 300)}
        
        Your prompt should:
        1. Include specific visual details that would make an interesting image
        2. Specify style, lighting, mood, and composition
        3. Be formatted as a comma-separated list of descriptors
        4. Be around 40-60 words in length
        
        Stable Diffusion Prompt:
        """
        
        # Generate enhanced prompt
        result = groq_client.generate_text(
            prompt=llama_prompt,
            max_tokens=100,
            temperature=0.7
        )
        
        if not result.get("success", False):
            # If generation failed, return a basic prompt
            return f"{topic}, detailed, high quality"
        
        return result.get("text", "").strip()
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """
        Get available artistic styles for image generation.
        
        Returns:
            List of style dictionaries with name and description
        """
        return stable_diffusion_client.get_styles()


# Create a singleton instance
image_generator = ImageGenerator() 