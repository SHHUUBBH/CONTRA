"""
Narrative generator for creating text narratives using the Groq LLaMA API.
"""

import logging
import time
import textwrap
from typing import Dict, List, Any, Optional

from models.data_model import Narrative, TopicData
from services.groq_client import groq_client
from config import ContentConfig
from utils.helpers import format_time_elapsed, clean_text, truncate_text
from utils.text_formatter import format_title, enhance_narrative, format_bullet_points, correct_spelling

# Configure logging
logger = logging.getLogger(__name__)

class NarrativeGenerator:
    """
    Generates narratives and structured text content using LLaMA.
    """
    
    def __init__(self):
        """Initialize the narrative generator."""
        # GroqClient is initialized as a singleton in its module
        pass
    
    def generate_narrative(
        self,
        topic_data: TopicData,
        tone: str = None,
        max_tokens: int = None,
        temperature: float = None,
        expertise_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Generate a narrative about a topic using available data.
        
        Args:
            topic_data: Normalized topic data from various sources
            tone: Narrative tone (e.g., "informative", "dramatic")
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            expertise_level: Target audience expertise level (beginner, intermediate, advanced)
            
        Returns:
            Dictionary with generated narrative and metadata
        """
        start_time = time.time()
        
        # Use defaults from config if not specified
        tone = tone or ContentConfig.DEFAULT_TONE
        max_tokens = max_tokens or ContentConfig.DEFAULT_MAX_LENGTH
        temperature = temperature or ContentConfig.DEFAULT_TEMPERATURE
        
        # Validate expertise level
        if expertise_level not in ["beginner", "intermediate", "advanced"]:
            logger.warning(f"Invalid expertise level: {expertise_level}. Using default: intermediate")
            expertise_level = "intermediate"
        
        # Correct potential misspellings in the topic
        corrected_topic = correct_spelling(topic_data.topic)
        
        # If topic was corrected, update it in the topic_data
        if corrected_topic != topic_data.topic:
            logger.info(f"Corrected topic from '{topic_data.topic}' to '{corrected_topic}'")
            topic_data.topic = corrected_topic
        
        # Format the topic with proper title case
        formatted_topic = format_title(topic_data.topic)
        logger.info(f"Generating narrative for topic: {formatted_topic} (tone={tone}, temperature={temperature}, expertise_level={expertise_level})")
        
        # Build the prompt for LLaMA with expertise level
        prompt = self._build_prompt(topic_data, tone, expertise_level)
        
        # Call the LLaMA API via Groq
        result = groq_client.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not result.get("success", False):
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "error": result.get("error", "Unknown error generating narrative"),
                "processing_time": format_time_elapsed(elapsed_time)
            }
        
        # Extract the generated text
        generated_text = result.get("text", "")
        
        # Split into bullets and narrative sections
        bullets, narrative = groq_client.extract_bullet_points(generated_text)
        
        # Enhance and format the narrative with expertise level
        enhanced_narrative = enhance_narrative(narrative, topic_data.topic, tone, temperature, expertise_level)
        
        # Format bullet points for better presentation
        formatted_bullets = format_bullet_points(bullets)
        
        # Create the Narrative model and include expertise level in the data
        narrative_model = Narrative(
            bullets=formatted_bullets,
            narrative=enhanced_narrative,
            prompt=prompt,
            model=result.get("model", ""),
            expertise_level=expertise_level  # Store expertise level in the narrative model
        )
        
        # Return the result
        elapsed_time = time.time() - start_time
        return {
            "success": True,
            "narrative": narrative_model.to_dict(),
            "processing_time": format_time_elapsed(elapsed_time)
        }
    
    def _build_prompt(self, topic_data: TopicData, tone: str, expertise_level: str = "intermediate") -> str:
        """
        Build a prompt for the LLaMA model that includes context from all data sources.
        Adjusts language complexity based on expertise level.
        
        Args:
            topic_data: Normalized topic data
            tone: Narrative tone
            expertise_level: Target audience expertise level (beginner, intermediate, advanced)
            
        Returns:
            Formatted prompt string
        """
        parts = []
        
        # Format topic with proper title case
        formatted_topic = format_title(topic_data.topic)
        
        # Instructions with tone, expertise level, and formatted topic
        parts.append(f"Write a {tone} narrative about '{formatted_topic}' for a {expertise_level}-level audience.")
        
        # Common instructions for all narratives with expertise level considerations
        parts.append("IMPORTANT GUIDELINES FOR ALL NARRATIVES:")
        
        # Expertise level specific instructions
        if expertise_level == "beginner":
            parts.append("BEGINNER LEVEL AUDIENCE GUIDELINES:")
            parts.append("- Use extremely simple, everyday language that young students can understand")
            parts.append("- Avoid technical jargon completely, or explain it immediately in very basic terms")
            parts.append("- Use short, simple sentences and short paragraphs")
            parts.append("- Include many concrete examples to illustrate abstract concepts")
            parts.append("- Focus on basic fundamental concepts only")
            parts.append("- Define all terms, even relatively common ones")
            parts.append("- Write at approximately a 5th-6th grade reading level")
            parts.append("- Use simple analogies to familiar everyday experiences")
        elif expertise_level == "intermediate":
            parts.append("INTERMEDIATE LEVEL AUDIENCE GUIDELINES:")
            parts.append("- Use clear language accessible to high school or undergraduate students")
            parts.append("- Explain necessary technical terms when first used")
            parts.append("- Balance depth with accessibility")
            parts.append("- Include some nuance and context, but maintain clarity")
            parts.append("- Write at approximately a high school reading level")
            parts.append("- Use moderately complex examples and applications")
        elif expertise_level == "advanced":
            parts.append("ADVANCED LEVEL AUDIENCE GUIDELINES:")
            parts.append("- Use precise, field-appropriate language for an educated audience")
            parts.append("- Technical terms can be used without extensive explanation")
            parts.append("- Include depth, nuance and complexity where appropriate")
            parts.append("- Discuss advanced concepts and their implications")
            parts.append("- Write at a college or professional reading level")
            parts.append("- Include sophisticated examples and applications")
            parts.append("- Still avoid unnecessarily obscure vocabulary or jargon")
        
        # General instructions for all levels
        parts.append("- Structure content with a clear introduction, main points, and conclusion")
        parts.append("- Explain ideas as if talking to someone at the appropriate level of familiarity with the topic")
        
        # Add tone-specific instructions with much more detail
        if tone.lower() == 'dramatic':
            parts.append("DRAMATIC TONE SPECIFIC GUIDELINES:")
            parts.append("- Create a narrative arc with rising tension and emotional resonance")
            parts.append("- Use vivid descriptive language to create scenes readers can visualize")
            parts.append("- Include emotional stakes and human elements that create connection")
            parts.append("- Structure content like a story with a beginning, middle, and climactic end")
            parts.append("- Use powerful, evocative words that create strong imagery and feelings")
            if expertise_level == "beginner":
                parts.append("- Keep dramatic language extremely simple and accessible while still being emotionally impactful")
            elif expertise_level == "intermediate":
                parts.append("- Balance dramatic elements with moderately sophisticated language and concepts")
            else:
                parts.append("- Create literary-quality dramatic narrative with sophisticated language and complex emotional themes")
        
        elif tone.lower() == 'poetic':
            parts.append("POETIC TONE SPECIFIC GUIDELINES:")
            parts.append("- Write in a genuine poetic style with rhythm, imagery, and metaphor")
            parts.append("- Use beautiful, lyrical language that focuses on sensory details")
            parts.append("- Include metaphors and similes that illuminate the topic in unexpected ways")
            parts.append("- Create a flow of ideas that follows poetic rather than purely logical structure")
            parts.append("- Incorporate literary techniques like alliteration, assonance, and consonance")
            parts.append("- Use line breaks and stanza-like paragraph structures for rhythmic effect")
            
            if expertise_level == "beginner":
                parts.append("- Create simple but beautiful poems with clear imagery children can understand")
                parts.append("- Use rhyming patterns and familiar metaphors to maintain engagement")
                parts.append("- Keep vocabulary simple while still being lyrical and beautiful")
            elif expertise_level == "intermediate":
                parts.append("- Create moderately complex poetry with accessible but rich imagery")
                parts.append("- Balance poetic expression with clarity of educational content")
                parts.append("- Use a mix of free verse and structured elements that engage young adults")
            else:
                parts.append("- Create sophisticated poetry that could appear in literary publications")
                parts.append("- Use complex poetic devices, extended metaphors, and rich symbolism")
                parts.append("- Incorporate poetic techniques from various traditions as appropriate")
        
        elif tone.lower() == 'humorous':
            parts.append("HUMOROUS TONE SPECIFIC GUIDELINES:")
            parts.append("- Make the content genuinely funny and entertaining while still being informative")
            parts.append("- Include clever jokes, wordplay, and humorous observations throughout")
            parts.append("- Reference recognizable current cultural trends and topics for relatable humor")
            parts.append("- Use comedic devices like exaggeration, ironic contrasts, and surprising comparisons")
            parts.append("- Include funny analogies that help explain complex concepts in an entertaining way")
            parts.append("- Maintain a light, conversational tone that feels like witty banter")
            parts.append("- Incorporate funny hypothetical scenarios to illustrate points")
            parts.append("- Make references to current events, popular culture, or universal experiences that most people would find relatable")
            
            if expertise_level == "beginner":
                parts.append("- Use simple, playful humor with puns and silly examples kids would enjoy")
                parts.append("- Include funny imagery that helps visualize concepts (like talking animals or familiar characters)")
                parts.append("- Use humor appropriate for younger audiences while avoiding purely adult references")
            elif expertise_level == "intermediate":
                parts.append("- Create moderately sophisticated humor with some cleverer wordplay and references")
                parts.append("- Balance humor with clear educational content that teens and young adults would appreciate")
                parts.append("- Include light satire and gentle parody to illuminate the topic")
            else:
                parts.append("- Use sophisticated wit, satire, and clever references for an educated audience")
                parts.append("- Create multi-layered humor that works on different levels of understanding")
                parts.append("- Include subtle jokes and references that reward the knowledgeable reader")
        
        elif tone.lower() == 'technical':
            parts.append("TECHNICAL TONE SPECIFIC GUIDELINES:")
            parts.append("- Use precise, accurate terminology and clear explanations of processes")
            parts.append("- Structure content in a logical progression that builds on previous concepts")
            parts.append("- Include specific details, measurable quantities, and technical specifications")
            parts.append("- Maintain objectivity and precision in descriptions and explanations")
            parts.append("- Use industry-standard formatting for technical concepts")
            
            if expertise_level == "beginner":
                parts.append("- Use technical structure but explain every term in extremely simple language")
                parts.append("- Include 'in other words' explanations after any necessary technical terms")
                parts.append("- Use simple diagrams and step-by-step explanations as if teaching a technical concept for the first time")
            elif expertise_level == "intermediate":
                parts.append("- Balance technical accuracy with accessibility for someone learning the field")
                parts.append("- Include brief definitions or context for moderately advanced terms")
                parts.append("- Use examples that connect technical concepts to practical applications")
            else:
                parts.append("- Use field-appropriate technical language assuming domain knowledge")
                parts.append("- Include advanced technical details, specifications, and sophisticated analysis")
                parts.append("- Reference related technical concepts and their interactions in the field")
        
        elif tone.lower() == 'simple':
            parts.append("SIMPLE TONE SPECIFIC GUIDELINES:")
            parts.append("- Use extremely clear, straightforward language with minimal complexity")
            parts.append("- Focus on core ideas without unnecessary details or tangents")
            parts.append("- Use short sentences and paragraphs with one main idea per paragraph")
            parts.append("- Explain concepts as if speaking to someone completely unfamiliar with the topic")
            parts.append("- Use concrete examples from everyday life to illustrate abstract ideas")
            
            if expertise_level == "beginner":
                parts.append("- Write as if explaining to very young students with no background knowledge")
                parts.append("- Use extremely basic vocabulary and sentence structure")
                parts.append("- Include fun, simple examples that children would understand and enjoy")
            elif expertise_level == "intermediate":
                parts.append("- Write clearly for a general audience with basic education but no specialized knowledge")
                parts.append("- Use approachable language while covering moderately complex ideas")
                parts.append("- Include relatable examples that teenagers and young adults would connect with")
            else:
                parts.append("- Explain sophisticated concepts in plain language without oversimplifying")
                parts.append("- Maintain depth of insight while using accessible explanations")
                parts.append("- Use the principle of 'explain like I'm five' but for complex topics")
        
        else:  # informative (default)
            parts.append("INFORMATIVE TONE SPECIFIC GUIDELINES:")
            parts.append("- Present balanced, objective information with well-structured arguments")
            parts.append("- Include key facts, statistics, and evidence to support main points")
            parts.append("- Organize content with clear sections covering different aspects of the topic")
            parts.append("- Maintain a neutral, educational tone that prioritizes accuracy")
            parts.append("- Include historical context and current understanding of the topic")
            
            if expertise_level == "beginner":
                parts.append("- Present information at an elementary school level with simple explanations")
                parts.append("- Include basic facts with extremely clear cause-and-effect relationships")
                parts.append("- Focus only on the most fundamental aspects of the topic")
            elif expertise_level == "intermediate":
                parts.append("- Present information at a high school level with some nuance and context")
                parts.append("- Balance breadth and depth appropriate for someone with general education")
                parts.append("- Include some analysis beyond just facts while maintaining clarity")
            else:
                parts.append("- Present information at a college level with substantial depth and analysis")
                parts.append("- Include nuanced perspectives, scholarly context, and sophisticated analysis")
                parts.append("- Cover specialized aspects of the topic that would interest a knowledgeable audience")
        
        # Add instructions for creating bullet points
        parts.append("\nCREATE A STRUCTURED NARRATIVE FOLLOWING THESE STEPS:")
        parts.append("1. Start with 3-5 bullet points that highlight the key aspects of the topic")
        parts.append("2. Follow with several paragraphs of narrative text that elaborate on these points")
        parts.append("3. Ensure the content is appropriate for the specified expertise level and tone")
        parts.append("4. Make the content engaging, accurate, and tailored to the unique requirements of the chosen tone")
        
        parts.append("Use the following context:")
        
        # Wikipedia content
        if topic_data.wikipedia.summary:
            parts.append("\nWIKIPEDIA SUMMARY:")
            parts.append(textwrap.fill(topic_data.wikipedia.summary, width=80))
            if topic_data.wikipedia.url:
                parts.append(f"URL: {topic_data.wikipedia.url}")
        
        # DBpedia content
        if topic_data.dbpedia.abstract:
            parts.append("\nDBPEDIA ABSTRACT:")
            parts.append(textwrap.fill(topic_data.dbpedia.abstract, width=80))
        
        if topic_data.dbpedia.categories:
            parts.append("\nDBPEDIA CATEGORIES: " + ", ".join(topic_data.dbpedia.categories[:10]))
        
        # News headlines
        if topic_data.news:
            parts.append("\nRECENT NEWS HEADLINES:")
            for i, article in enumerate(topic_data.news[:5], 1):
                if article.title:
                    parts.append(f"{i}. {article.title}")
                if article.description and i <= 3:  # Include descriptions for top 3 articles
                    parts.append(f"   {truncate_text(article.description, 100)}")
        
        # Output format instructions with more guidance for engaging, user-friendly content
        parts.append(
            "\nYOUR TASK:\n"
            "1. A concise bullet-point summary (3–5 points) using simple words that anyone could understand.\n"
            "2. A detailed narrative in 2–4 paragraphs that is accessible to all readers regardless of education level.\n"
            "3. Ensure all vocabulary is at approximately 5th-grade reading level."
        )
        
        # Add additional instructions for compelling yet simple narrative
        parts.append(
            "Make the narrative both compelling and easy to understand by:\n"
            "- Starting with a simple, clear introduction of what the topic is\n"
            "- Using concrete examples and comparisons to everyday things\n"
            "- Explaining one idea at a time in a logical order\n"
            "- Avoiding complicated sentences with multiple clauses\n"
            "- Concluding with a straightforward summary of why this matters to everyday people"
        )
        
        return "\n".join(parts)
    
    def generate_creative_story(
        self,
        topic_data: TopicData,
        style: str = "short story",
        genre: Optional[str] = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """
        Generate a creative story based on the topic data.
        
        Args:
            topic_data: Normalized topic data
            style: Story style (e.g., "short story", "poem", "script")
            genre: Optional genre (e.g., "mystery", "science fiction")
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0.1-1.0, higher = more creative)
            
        Returns:
            Dictionary with generated story and metadata
        """
        start_time = time.time()
        max_tokens = max_tokens or ContentConfig.DEFAULT_MAX_LENGTH
        
        # Set creativity temperature - use provided value or default to higher creative value
        if temperature is None:
            # Default to higher creativity for stories than regular narratives
            temperature = 0.8
        
        # Format topic properly
        formatted_topic = format_title(topic_data.topic)
        
        # Build creative prompt based on temperature level
        genre_str = f" in the {genre} genre" if genre else ""
        
        # Basic prompt at low temperature
        if temperature < 0.6:
            prompt = f"Write a clear and straightforward {style}{genre_str} inspired by '{formatted_topic}'.\n\n"
        # Medium creativity 
        elif temperature < 0.8:
            prompt = f"Write a creative {style}{genre_str} inspired by '{formatted_topic}'.\n\n"
        # High creativity
        else:
            prompt = f"Write a highly imaginative and creative {style}{genre_str} with unique perspectives and vivid imagery inspired by '{formatted_topic}'.\n\n"
        
        # Add context
        if topic_data.wikipedia.summary:
            prompt += f"Context: {truncate_text(topic_data.wikipedia.summary, 200)}\n\n"
        
        # Add specific instructions for the story style
        if style == "short story":
            prompt += "Write an engaging short story with a clear beginning, middle, and end.\n"
            if temperature > 0.7:
                prompt += "Include vivid descriptions, compelling characters, and an unexpected twist.\n"
        elif style == "poem":
            prompt += "Write a poem with vivid imagery and metaphors.\n"
            if temperature > 0.7:
                prompt += "Use rhythmic language, creative metaphors, and evocative emotional resonance.\n"
        elif style == "script":
            prompt += "Write a brief script with dialog between characters.\n"
            if temperature > 0.7:
                prompt += "Include dynamic character interactions and revealing dialog that shows rather than tells.\n"
        
        # Log the temperature being used
        logger.info(f"Generating creative story for '{formatted_topic}' with temperature={temperature}")
        
        # Call the LLaMA API
        result = groq_client.generate_text(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not result.get("success", False):
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "error": result.get("error", "Unknown error generating story"),
                "processing_time": format_time_elapsed(elapsed_time)
            }
        
        elapsed_time = time.time() - start_time
        return {
            "success": True,
            "story": result.get("text", ""),
            "style": style,
            "genre": genre,
            "model": result.get("model", ""),
            "processing_time": format_time_elapsed(elapsed_time)
        }
    
    def analyze_sentiment(self, topic_data: TopicData) -> Dict[str, Any]:
        """
        Analyze the sentiment around a topic based on available data.
        
        Args:
            topic_data: Normalized topic data
            
        Returns:
            Dictionary with sentiment analysis
        """
        # Format topic properly
        formatted_topic = format_title(topic_data.topic)
        
        # Create a structured output format for LLaMA
        output_format = {
            "sentiment": "string (positive, negative, or neutral)",
            "confidence": "number (0.0-1.0)",
            "analysis": "string (brief explanation)",
            "highlights": ["array of key points supporting the sentiment"]
        }
        
        # Build the prompt
        prompt = f"Analyze the sentiment around the topic '{formatted_topic}' based on the following data:\n\n"
        
        # Add news headlines
        if topic_data.news:
            prompt += "NEWS HEADLINES:\n"
            for article in topic_data.news[:5]:
                prompt += f"- {article.title}\n"
        
        # Add Wikipedia context if available
        if topic_data.wikipedia.summary:
            prompt += f"\nWIKIPEDIA CONTEXT:\n{truncate_text(topic_data.wikipedia.summary, 200)}\n"
        
        # Add instruction
        prompt += "\nBased on this information, analyze the overall sentiment around this topic. " \
                 "Is it mostly positive, negative, or neutral? Provide a brief explanation and key points."
        
        # Get structured output
        result = groq_client.parse_structured_output(prompt, output_format)
        
        if not result.get("success", False):
            return {
                "success": False,
                "error": result.get("error", "Unknown error analyzing sentiment")
            }
        
        return {
            "success": True,
            "sentiment_analysis": result.get("data", {})
        }

    def generate_conversation_response(
        self,
        topic: str,
        question: str,
        conversation_history: List[Dict[str, str]],
        topic_data: Optional[TopicData] = None,
        tone: str = "informative",
        temperature: float = None
    ) -> Dict[str, Any]:
        """
        Generate a conversational response to a user question about a topic.
        
        Args:
            topic: The main topic being discussed
            question: The user's question
            conversation_history: List of previous conversation messages
            topic_data: Optional topic data for additional context
            tone: Tone to use for response generation
            temperature: Creativity level (0.1-1.0, higher = more creative)
            
        Returns:
            Dictionary with response text and metadata
        """
        start_time = time.time()
        
        # Use defaults if not specified
        if temperature is None:
            temperature = ContentConfig.CONVERSATION_TEMPERATURE
            
        # Ensure temperature is within valid range
        temperature = max(0.1, min(1.0, temperature))
        
        # Validate tone
        if tone not in ContentConfig.VALID_TONES:
            tone = ContentConfig.DEFAULT_TONE
        
        try:
            # Format the conversation history for the LLM prompt
            formatted_history = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Limit to last 5 messages
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        formatted_history += f"User: {content}\n"
                    elif role == 'ai':
                        formatted_history += f"Assistant: {content}\n"
                    elif role == 'system':
                        formatted_history += f"# {content}\n"
            
            # Prepare context information
            context_text = ""
            if topic_data:
                # Add Wikipedia summary if available
                if hasattr(topic_data, 'wikipedia') and topic_data.wikipedia.summary:
                    context_text += f"Wikipedia: {topic_data.wikipedia.summary}\n\n"
                
                # Add DBpedia data if available
                if hasattr(topic_data, 'dbpedia') and topic_data.dbpedia.abstract:
                    context_text += f"DBpedia: {topic_data.dbpedia.abstract}\n\n"
                
                # Add relevant news headlines if available
                if hasattr(topic_data, 'news') and topic_data.news:
                    news_items = []
                    for article in topic_data.news[:3]:
                        if article.title:
                            news_items.append(f"- {article.title}")
                    if news_items:
                        context_text += "Recent news headlines:\n" + "\n".join(news_items) + "\n\n"
            
            # Craft the prompt for the LLM
            prompt = self._create_conversation_prompt(
                topic=topic,
                question=question,
                conversation_history=formatted_history,
                context_text=context_text,
                tone=tone
            )
            
            # Select the LLM to use
            llm_client = self._get_llm_client()
            if not llm_client:
                return {
                    "success": False,
                    "error": "No language model available for conversation"
                }
            
            # Generate the response
            result = llm_client.generate_text(
                prompt=prompt,
                max_tokens=ContentConfig.CONVERSATION_MAX_TOKENS,
                temperature=temperature
            )
            
            if not result.get("success", False):
                return {
                    "success": False,
                    "error": result.get("error", "Failed to generate response")
                }
            
            response_text = result.get("text", "").strip()
            
            # Extract references if included in the response
            references = []
            reference_section = ""
            
            if "REFERENCES:" in response_text:
                main_response, reference_section = response_text.split("REFERENCES:", 1)
                response_text = main_response.strip()
                
                # Process references
                if reference_section:
                    ref_lines = reference_section.strip().split("\n")
                    for line in ref_lines:
                        if line.strip():
                            references.append(line.strip())
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response_text,
                "references": references,
                "prompt": prompt,
                "model": llm_client.model_id if hasattr(llm_client, 'model_id') else "LLM",
                "processing_time": format_time_elapsed(elapsed_time)
            }
            
        except Exception as e:
            logger.exception(f"Error generating conversation response: {e}")
            return {
                "success": False,
                "error": f"Failed to generate conversation response: {str(e)}"
            }

    def _get_llm_client(self):
        """
        Get the LLM client for conversation.
        
        Returns:
            LLM client instance
        """
        # Return the groq client instance
        return groq_client

    def _create_conversation_prompt(
        self,
        topic: str,
        question: str,
        conversation_history: str,
        context_text: str,
        tone: str
    ) -> str:
        """
        Create a prompt for the conversation response.
        
        Args:
            topic: The main topic
            question: User's question
            conversation_history: Formatted conversation history
            context_text: Background information about the topic
            tone: Desired response tone
            
        Returns:
            Formatted prompt string
        """
        # Base system instruction
        system_instruction = f"""You are CONTRA AI, a friendly and helpful assistant specializing in educational content about "{topic}".
        
Your goal is to provide accurate, helpful responses that ANYONE can easily understand, regardless of their education level.

TOPIC: {topic}

TONE: {tone.capitalize()}

LANGUAGE REQUIREMENTS:
1. Use simple, everyday words instead of complex vocabulary
2. Use short sentences and paragraphs
3. Explain all technical terms or jargon in plain language
4. Use examples from daily life to illustrate complex concepts
5. Keep your explanations straightforward and direct
6. Aim for a 5th-grade reading level (10-11 year old child)
7. Use active voice rather than passive voice
8. Break down complex ideas into simpler parts
"""

        # Add tone-specific instructions
        if tone == "dramatic":
            system_instruction += """
For dramatic tone:
- Use simple words to create emotional impact
- Tell a story with everyday language
- Focus on relatable human elements
- Keep dramatic moments easy to understand
- Use clear cause and effect relationships
"""
        elif tone == "poetic":
            system_instruction += """
For poetic tone:
- Use simple but beautiful words
- Use imagery based on everyday experiences
- Create rhythm with short phrases
- Use familiar metaphors everyone would understand
- Express complex feelings with simple language
"""
        elif tone == "humorous":
            system_instruction += """
For humorous tone:
- Use simple jokes and humor
- Make comparisons to everyday situations
- Keep humor friendly and easy to understand
- Avoid complex wordplay or references
- Use light, conversational language
"""
        elif tone == "technical":
            system_instruction += """
For technical tone:
- Explain technical concepts using everyday language
- Define all specialized terms immediately
- Use simple step-by-step explanations
- Compare technical concepts to familiar objects or situations
- Avoid unnecessary jargon completely
"""
        elif tone == "simple":
            system_instruction += """
For simple tone:
- Use the simplest words possible
- Keep sentences very short and direct
- Focus only on the most important information
- Repeat key points using different simple words
- Use very concrete examples
"""
        else:  # informative (default)
            system_instruction += """
For informative tone:
- Present facts using common, everyday language
- Explain complex ideas with simple cause and effect
- Use real-life examples that anyone would understand
- Break information into small, digestible chunks
- Connect new information to things people already know
"""

        # Add contextual knowledge instructions
        system_instruction += f"""
BACKGROUND CONTEXT:
{context_text}

IMPORTANT GUIDELINES:
1. Stay on topic about "{topic}"
2. Admit when you don't know something
3. When citing facts, add a REFERENCES section with simple explanations of sources
4. Keep responses brief (2-3 paragraphs) and easy to read
5. Match your writing style to the {tone} tone while keeping language simple
6. Use everyday examples to make your points clear

READABILITY CHECKS:
- Would a 10-11 year old child understand your response?
- Have you avoided all specialized terminology?
- Are your sentences short and direct?
- Have you used concrete examples from everyday life?
- Have you removed unnecessary words and phrases?

You're chatting with a user who wants to learn more about {topic} in a way that's easy to understand.
"""

        # Add the conversation history and current question
        full_prompt = system_instruction + "\n\n"
        
        if conversation_history:
            full_prompt += "Previous conversation:\n" + conversation_history + "\n\n"
        
        full_prompt += f"User's new question: {question}\n\nYour response (use simple language a 10-11 year old would understand):"
        
        return full_prompt


# Create a singleton instance
narrative_generator = NarrativeGenerator() 