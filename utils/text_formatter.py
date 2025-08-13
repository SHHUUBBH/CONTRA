"""
Text formatting utilities for enhancing narrative presentation.
"""

import re
import string
from typing import List, Dict, Any, Optional, Tuple

def format_title(text: str) -> str:
    """
    Format text in proper title case with smart capitalization rules.
    
    Args:
        text: Input text to format
        
    Returns:
        Properly formatted title
    """
    if not text:
        return ""
    
    # Define words that should not be capitalized unless at beginning/end
    lowercase_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 
        'to', 'from', 'by', 'of', 'in', 'with', 'within', 'about', 'as'
    }
    
    # Split the title into words
    words = text.split()
    if not words:
        return ""
    
    # Always capitalize the first and last word
    words[0] = words[0].capitalize()
    if len(words) > 1:
        words[-1] = words[-1].capitalize()
    
    # Apply capitalization rules to the remaining words
    for i in range(1, len(words)-1):
        word = words[i]
        if word.lower() in lowercase_words:
            # Check if it follows punctuation that would start a new sentence
            if i > 0 and words[i-1][-1] in '.!?:;':
                words[i] = word.capitalize()
            else:
                words[i] = word.lower()
        else:
            words[i] = word.capitalize()
    
    return " ".join(words)

def enhance_narrative(narrative: str, topic: str, tone: str, temperature: float = 0.7, expertise_level: str = "intermediate") -> str:
    """
    Enhance a narrative with improved formatting, structure and presentation.
    The level of creative enhancement adapts to the temperature value.
    Uses accessible language and clear structure for better understanding.
    Adapts vocabulary complexity to the user's expertise level.
    
    Args:
        narrative: Original narrative text
        topic: The topic of the narrative
        tone: The narrative tone (e.g., informative, dramatic)
        temperature: Creativity level (0.1-1.0, higher = more creative formatting)
        expertise_level: Level of expertise (beginner, intermediate, advanced)
        
    Returns:
        Enhanced narrative text with user-friendly vocabulary
    """
    if not narrative:
        return ""
    
    # Ensure topic is properly capitalized in the text
    capitalized_topic = format_title(topic)
    
    # Replace instances of the topic with the properly capitalized version
    # Use regex to match case-insensitive and handle punctuation boundaries
    narrative = re.sub(r'(?<![a-zA-Z])' + re.escape(topic) + r'(?![a-zA-Z])', capitalized_topic, narrative, flags=re.IGNORECASE)
    
    # Split into paragraphs
    paragraphs = narrative.split('\n\n')
    enhanced_paragraphs = []
    
    # Get current year for humorous content references
    import datetime
    current_year = datetime.datetime.now().year
    
    # Process each paragraph
    for i, para in enumerate(paragraphs):
        if not para.strip():
            continue
            
        # Trim extra whitespace
        para = para.strip()
        
        # Apply vocabulary simplification based on expertise level
        if expertise_level == "beginner":
            # Maximum simplification for beginners
            para = simplify_vocabulary(para, simplification_level="high")
        elif expertise_level == "intermediate":
            # Moderate simplification for intermediate users
            para = simplify_vocabulary(para, simplification_level="medium")
        elif expertise_level == "advanced":
            # Minimal simplification for advanced users
            para = simplify_vocabulary(para, simplification_level="low")
        
        # Ensure first paragraph introduces the topic well with simple language
        if i == 0 and capitalized_topic not in para:
            # Add topic if it's not already mentioned
            para = f"{capitalized_topic} is {para[0].lower() + para[1:]}"
        
        # Apply tone-specific enhancements
        if tone.lower() == 'dramatic':
            # Add dramatic elements with emphasis on emotional impact
            if i == 0:  # First paragraph
                # Create a dramatic opening
                if temperature > 0.8:
                    para = f"In a world where {capitalized_topic} shapes our reality, {para.lower()}"
                elif temperature > 0.6:
                    para = f"The story of {capitalized_topic} begins with {para.lower()}"
            
            if i == len(paragraphs) - 1:  # Last paragraph
                # Add a dramatic conclusion
                if temperature > 0.8:
                    para += f" And thus, {capitalized_topic} continues to echo through time, leaving an indelible mark on our collective journey."
                elif temperature > 0.6:
                    para += f" The impact of {capitalized_topic} continues to resonate today, changing how we understand our world."
            
            # Add dramatic emphasis to important phrases
            emphasis_words = ["critical", "dramatic", "revolutionary", "extraordinary", "profound", "devastating", "remarkable"]
            for word in emphasis_words:
                if word in para.lower():
                    para = re.sub(r'(?i)\b' + re.escape(word) + r'\b', f"*{word}*", para)
        
        elif tone.lower() == 'poetic':
            # Transform into more poetic structure based on temperature
            if temperature > 0.8:
                # High creativity - create a more lyrical structure
                sentences = re.split(r'(?<=[.!?])\s+', para)
                
                # Add line breaks for poetic rhythm
                poetic_lines = []
                for j, sentence in enumerate(sentences):
                    # Break longer sentences at commas and other natural pauses
                    parts = re.split(r'(?<=[,;:])\s+', sentence)
                    
                    # Add poetic line breaks
                    if len(parts) > 1:
                        # Format with line breaks for poetic effect
                        for part in parts:
                            poetic_lines.append(part)
                    else:
                        poetic_lines.append(sentence)
                
                # Join with line breaks for stanza-like effect
                para = '\n'.join(poetic_lines)
                
                # Add poetic devices: enhance with alliteration and more metaphorical language
                para = enhance_poetic_language(para, temperature)
                
                # Add a poetic line at end of paragraphs
                if i == len(paragraphs) - 1 and expertise_level != "beginner":
                    para += f"\n\nLike whispers through time, {capitalized_topic} echoes in the chambers of our understanding."
            
            elif temperature > 0.6:
                # Moderate creativity - add some poetic elements
                sentences = re.split(r'(?<=[.!?])\s+', para)
                
                # Format with selective line breaks
                formatted = []
                for j, sentence in enumerate(sentences):
                    if j % 2 == 1:  # Every other sentence
                        formatted.append('\n' + sentence)
                    else:
                        formatted.append(sentence)
                
                para = ' '.join(formatted)
                
                # Add some poetic language enhancement
                para = enhance_poetic_language(para, temperature - 0.2)  # Less intense
        
        elif tone.lower() == 'humorous':
            # Add humor elements based on temperature and expertise level
            if temperature > 0.8:
                # High creativity humor
                
                # Add funny cultural references based on expertise level
                if expertise_level == "beginner":
                    # Kid-friendly humor
                    if i == 0:
                        para = f"OK kids, let's talk about {capitalized_topic}! It's like that time when your pet goldfish tried to explain quantum physics – complicated but fascinating! {para}"
                    elif i == len(paragraphs) - 1:
                        para += f" And that's {capitalized_topic} in a nutshell – or as my pet rock would say, 'That rocks!'"
                
                elif expertise_level == "intermediate":
                    # Teen/young adult humor with pop culture
                    if i == 0:
                        para = f"So {capitalized_topic} is trending harder than the latest TikTok dance challenge! {para}"
                    elif i == len(paragraphs) - 1:
                        para += f" In the immortal words of every superhero movie ever: 'With great knowledge of {capitalized_topic} comes great conversation starters at awkward parties.'"
                
                else:  # Advanced
                    # More sophisticated humor
                    if i == 0:
                        para = f"Welcome to {capitalized_topic} 101: where the facts are made up and the points don't matter! Just kidding – unlike your streaming service recommendations, this information is actually relevant. {para}"
                    elif i == len(paragraphs) - 1:
                        para += f" And there you have it! You're now officially overqualified to edit the Wikipedia page on {capitalized_topic}, but still underqualified to win an argument about it on Reddit."
                
                # Add funny similes and metaphors for all levels
                if i == len(paragraphs) // 2:  # Middle paragraph
                    funny_comparisons = [
                        f"Understanding {capitalized_topic} is like trying to fold a fitted sheet – theoretically possible, but rarely mastered.",
                        f"Explaining {capitalized_topic} at a party is like bringing a calculator to a dance-off – technically impressive but contextually questionable.",
                        f"{capitalized_topic} has changed more often than smartphone designs in {current_year} – constantly evolving but somehow always familiar."
                    ]
                    
                    # Choose a comparison based on expertise level
                    comparison_idx = min(int(expertise_level == "intermediate"), len(funny_comparisons) - 1)
                    if expertise_level == "advanced":
                        comparison_idx = 2
                        
                    para += f" {funny_comparisons[comparison_idx]}"
            
            elif temperature > 0.6:
                # Moderate humor
                if i == len(paragraphs) - 1:  # Last paragraph
                    para += f" And remember, knowing about {capitalized_topic} won't make you rich or famous, but it will make you that person who won't stop talking about {capitalized_topic} at dinner parties!"
        
        elif tone.lower() == 'technical':
            # For technical tone, replace complex terms with simpler ones for lower expertise levels
            if expertise_level != "advanced":
                para = add_simple_definitions(para)
            
            # Add technical structure elements
            if i == 0 and temperature > 0.7:
                # Add a technical overview label
                para = f"OVERVIEW: {para}"
            
            if i == len(paragraphs) - 1 and expertise_level == "beginner" and temperature > 0.7:
                # Add a simple summary for beginners
                simple_summary = f"\nSUMMARY: {capitalized_topic} affects many aspects of our world through the mechanisms described above. The key concepts introduced here provide a foundation for understanding this topic."
                para += simple_summary
        
        elif tone.lower() == 'simple':
            # For simple tone, focus on clarity and directness
            # Break up long sentences
            if len(para) > 200:
                sentences = re.split(r'(?<=[.!?])\s+', para)
                shorter_sentences = []
                
                for sentence in sentences:
                    if len(sentence) > 80:
                        # Try to split at commas
                        parts = re.split(r'(?<=,)\s+', sentence)
                        shorter_sentences.extend(parts)
                    else:
                        shorter_sentences.append(sentence)
                
                para = '. '.join(shorter_sentences)
            
            # For beginners, add extra explanations
            if expertise_level == "beginner" and temperature > 0.7:
                para = para.replace(".", ". ")  # Ensure space after periods
                
                # Add simple examples using "think of it like..."
                if i == 1:  # Second paragraph is a good place for examples
                    para += f" Think of {capitalized_topic} like building with blocks: you start with the basics and build up step by step."
        
        # Add paragraph to the list
        enhanced_paragraphs.append(para)
    
    # Apply additional formatting based on tone
    if tone.lower() == 'informative' and temperature > 0.7:
        # Add section headers for longer informative content
        if len(enhanced_paragraphs) >= 4:
            # Add headers to help organize content
            headers = ["Introduction", "Key Aspects", "Significance", "Conclusion"]
            for i in range(min(len(headers), len(enhanced_paragraphs))):
                enhanced_paragraphs[i] = f"## {headers[i]}\n{enhanced_paragraphs[i]}"
    
    # Final assembly with appropriate spacing
    if tone.lower() == 'poetic' and temperature > 0.7:
        # For poetic tone with high creativity, use single line breaks
        return '\n'.join(enhanced_paragraphs)
    else:
        # For other tones, use double line breaks
        return '\n\n'.join(enhanced_paragraphs)

def simplify_vocabulary(text: str, simplification_level: str = "medium") -> str:
    """
    Replace complex words with simpler alternatives to improve readability.
    
    Args:
        text: Original text
        simplification_level: Level of simplification (high, medium, low)
        
    Returns:
        Text with simplified vocabulary
    """
    # Dictionary of complex words and their simpler alternatives
    simplifications = {
        # Academic/complex terms
        r'\butilize\b': 'use',
        r'\bfacilitate\b': 'help',
        r'\bameliorate\b': 'improve',
        r'\bprocure\b': 'get',
        r'\bpurchase\b': 'buy',
        r'\bsubsequent\b': 'later',
        r'\bprior\b': 'before',
        r'\bcommence\b': 'begin',
        r'\bterminate\b': 'end',
        r'\bconclude\b': 'end',
        r'\binitiate\b': 'start',
        r'\bcontemplate\b': 'think about',
        r'\bconceive\b': 'think of',
        r'\bperceive\b': 'see',
        r'\butilization\b': 'use',
        r'\bimplementation\b': 'use',
        r'\bmodification\b': 'change',
        r'\bcognizant\b': 'aware',
        r'\bexacerbate\b': 'worsen',
        r'\balleviate\b': 'ease',
        r'\bconsequently\b': 'so',
        r'\bthus\b': 'so',
        r'\bhence\b': 'so',
        r'\bnevertheless\b': 'still',
        r'\bnotwithstanding\b': 'still',
        r'\bprocrastinate\b': 'delay',
        r'\bexpedite\b': 'speed up',
        r'\bsufficient\b': 'enough',
        r'\badequate\b': 'enough',
        r'\bsubstantial\b': 'large',
        r'\bnumerous\b': 'many',
        r'\bplethora\b': 'many',
        r'\bmyriad\b': 'many',
        r'\butilized\b': 'used',
        r'\bfacilitated\b': 'helped',
        r'\bimplemented\b': 'used',
        # Phrasal simplifications
        r'in order to': 'to',
        r'due to the fact that': 'because',
        r'with regard to': 'about',
        r'for the purpose of': 'for',
        r'in the event that': 'if',
        r'at this point in time': 'now',
        r'in spite of the fact that': 'although',
        r'in the vicinity of': 'near',
        r'it is often the case that': 'often',
        r'a significant number of': 'many',
        r'the vast majority of': 'most',
        r'on the grounds that': 'because',
        r'in view of the fact that': 'because',
    }
    
    # Additional complex terms for high simplification (beginners)
    high_simplifications = {
        r'\bobserve\b': 'see',
        r'\bpursue\b': 'follow',
        r'\bdevelop\b': 'grow',
        r'\bconstruct\b': 'build',
        r'\bmodify\b': 'change',
        r'\binitial\b': 'first',
        r'\bconcurrent\b': 'happening at the same time',
        r'\bcoordinate\b': 'organize',
        r'\bdelineate\b': 'describe',
        r'\bdetermine\b': 'decide',
        r'\bdisplay\b': 'show',
        r'\bpresent\b': 'show',
        r'\bdocument\b': 'record',
        r'\bexecute\b': 'do',
        r'\belaborate\b': 'explain more',
        r'\benhance\b': 'improve',
        r'\bevaluate\b': 'check',
        r'\bidentify\b': 'find',
        r'\billustrate\b': 'show',
        r'\binclude\b': 'have',
        r'\bmaintain\b': 'keep',
        r'\bprovide\b': 'give',
        r'\brequire\b': 'need',
        r'\bselect\b': 'choose',
        r'\btransform\b': 'change',
        r'\btransmit\b': 'send',
        r'\butilize\b': 'use',
        r'\bvariable\b': 'changing',
        r'\bsignificant\b': 'important',
        r'\bprimary\b': 'main',
        r'\bsecondary\b': 'less important',
        r'\bcorrelation\b': 'connection',
        r'\bcomplex\b': 'complicated',
        r'\bsimplify\b': 'make easier',
        r'\binteractive\b': 'works both ways',
        r'\bintegrate\b': 'combine',
        r'\boptimize\b': 'make better',
        r'\bgenerate\b': 'create',
        r'\bpopulate\b': 'fill',
        r'\bcalculate\b': 'figure out',
        r'\bperform\b': 'do',
        r'\bexamine\b': 'look at',
        r'\banalyze\b': 'study',
        r'\bdemonstrate\b': 'show',
        r'\bpreference\b': 'choice',
        r'\bmechanism\b': 'method',
        r'\binformation\b': 'details',
        r'\butilization\b': 'use',
        # More phrase substitutions
        r'as a consequence of': 'because of',
        r'for the most part': 'mostly',
        r'in the absence of': 'without',
        r'in conjunction with': 'with',
        r'take into consideration': 'consider',
        r'as a means of': 'to',
        r'in accordance with': 'following',
        r'within the realm of possibility': 'possible',
        r'on a regular basis': 'regularly',
        r'in a timely manner': 'quickly',
        r'in close proximity to': 'near',
    }
    
    # Medium-level simplifications are used by default (already defined in simplifications)
    
    # Only retain some simplifications for low level (advanced users)
    low_simplifications = {
        r'\bameliorate\b': 'improve',
        r'\bnotwithstanding\b': 'still',
        r'\bexacerbate\b': 'worsen',
        r'\balleviate\b': 'ease',
        r'\bplethora\b': 'many',
        r'\bmyriad\b': 'many',
        # Only replace the most complex phrases
        r'due to the fact that': 'because',
        r'in spite of the fact that': 'although',
        r'for the purpose of': 'for',
        r'at this point in time': 'now',
    }
    
    # Choose which simplifications to apply based on level
    replacements = {}
    if simplification_level == "high":
        # For beginners: apply both standard and additional simplifications
        replacements = {**simplifications, **high_simplifications}
    elif simplification_level == "medium":
        # For intermediate: apply standard simplifications
        replacements = simplifications
    elif simplification_level == "low":
        # For advanced: apply only minimal simplifications
        replacements = low_simplifications
    
    # Apply selected simplifications
    simplified_text = text
    for complex_pattern, simple_word in replacements.items():
        simplified_text = re.sub(complex_pattern, simple_word, simplified_text, flags=re.IGNORECASE)
    
    return simplified_text

def add_simple_definitions(text: str) -> str:
    """
    Add simple definitions after technical terms to make them more understandable.
    
    Args:
        text: Original technical text
        
    Returns:
        Text with simple definitions added for technical terms
    """
    # Dictionary of technical terms and their simple definitions
    tech_definitions = {
        # Technology
        r'\b(artificial intelligence|AI)\b': 'computers that can learn and think',
        r'\bmachine learning\b': 'technology that lets computers learn from examples',
        r'\bdeep learning\b': 'advanced computer learning using brain-like networks',
        r'\balgorithm\b': 'step-by-step instructions for computers',
        r'\bblockchain\b': 'a secure digital record system',
        r'\bcryptocurrency\b': 'digital money',
        r'\bquantum computing\b': 'super-powerful computing using physics',
        r'\bbig data\b': 'very large amounts of information',
        r'\bcloud computing\b': 'using computers on the internet instead of locally',
        r'\bvirtual reality\b': 'computer-created worlds you can see and interact with',
        r'\baugmented reality\b': 'adding computer images to what you see in real life',
        r'\binternet of things\b': 'everyday objects connected to the internet',
        r'\bcybersecurity\b': 'keeping computer systems safe from attacks',
        r'\bneural network\b': 'computer system inspired by the human brain',
        r'\bmicroprocessor\b': 'tiny computer brain that processes information',
        r'\bserver\b': 'powerful computer that provides services to other computers',
        r'\bencryption\b': 'code that keeps information secret and safe',
        r'\bprogramming language\b': 'special language used to give instructions to computers',
        
        # Science
        r'\bphoton\b': 'tiny particle of light',
        r'\bquantum physics\b': 'science of very tiny particles and how they behave',
        r'\bmolecule\b': 'tiny group of atoms joined together',
        r'\batom\b': 'tiny building block that makes up everything',
        r'\bgene\b': 'part of your DNA that determines your traits',
        r'\bDNA\b': 'molecule that contains instructions for how living things grow and function',
        r'\bgenome\b': 'complete set of genetic instructions in a living thing',
        r'\bprotein\b': 'important substance your body needs to work properly',
        r'\bcell\b': 'tiny building block of all living things',
        r'\bvirus\b': 'tiny germ that can make you sick',
        r'\bbacteria\b': 'very small living things, some cause illness, some are helpful',
        r'\becosystem\b': 'community of living things and their environment',
        r'\bclimate change\b': 'long-term changes in Earth\'s weather patterns',
        r'\brenewable energy\b': 'energy from sources that won\'t run out like sun and wind',
        r'\bfossil fuel\b': 'fuel made from ancient plants and animals, like oil and coal',
        
        # Medicine
        r'\bantibiotics\b': 'medicine that fights bacterial infections',
        r'\bvaccine\b': 'medicine that helps prevent diseases',
        r'\bimmune system\b': 'body\'s defense system against illness',
        r'\bpandemic\b': 'disease outbreak that spreads across many countries',
        r'\bviral\b': 'caused by a virus',
        r'\bchronic\b': 'lasting a long time or recurring often',
        
        # Business/Economics
        r'\binflation\b': 'rising prices and falling money value',
        r'\bgross domestic product\b': 'total value of goods and services a country produces',
        r'\bGDP\b': 'total value of goods and services a country produces',
        r'\bstock market\b': 'where people buy and sell shares in companies',
        r'\brecession\b': 'period when the economy slows down',
        r'\bunemployment\b': 'when people don\'t have jobs but are looking for work',
        r'\bsupply and demand\b': 'how available products and customer interest affect prices',
        r'\bcapitalism\b': 'economic system where private businesses and individuals own things',
        r'\bsocialism\b': 'economic system where the government owns or controls businesses',
        
        # History/Politics
        r'\bdemocracy\b': 'system where citizens vote to elect leaders',
        r'\bdictatorship\b': 'government ruled by one person with total power',
        r'\bconstitution\b': 'basic set of laws that defines how a country works',
        r'\blegislature\b': 'group of people who make laws',
        r'\bjudiciary\b': 'court system that interprets laws',
        r'\bexecutive branch\b': 'part of government that carries out laws',
        r'\bcolonialism\b': 'when one country takes control of another',
        r'\bimpact\b': 'strong effect or influence',
        r'\bconsequence\b': 'result of an action',
        
        # Arts/Humanities
        r'\brenaissance\b': 'period of new ideas and art in Europe from 14th to 17th century',
        r'\bmodernism\b': 'new and experimental ideas in art, music, and literature',
        r'\bpostmodernism\b': 'style that questions traditional ideas about art and culture',
        r'\bimperial\b': 'relating to an empire or emperor',
        r'\bmetaphor\b': 'describing something by comparing it to something else',
        
        # Mental concepts
        r'\bparadigm\b': 'way of thinking or pattern',
        r'\bcognitive\b': 'related to thinking and understanding',
        r'\bintrinsic\b': 'belonging naturally',
        r'\bextrinsic\b': 'coming from outside',
        r'\bphilosophy\b': 'study of ideas about knowledge, truth, and the meaning of life',
        r'\btheory\b': 'idea that explains something',
        r'\bhypothesis\b': 'idea or explanation that can be tested',
        
        # General academic terms
        r'\banalysis\b': 'careful study of something',
        r'\bframework\b': 'basic structure of ideas or facts',
        r'\bsynthesis\b': 'combining different ideas or things',
        r'\bmethodology\b': 'way of doing something',
        r'\bphenomenon\b': 'fact or event that can be observed',
        r'\bparadigm shift\b': 'major change in thinking or practice',
        r'\bconcept\b': 'idea or principle',
        r'\bcontext\b': 'circumstances or setting'
    }
    
    # Apply definitions but avoid repetition
    enhanced_text = text
    terms_added = set()
    
    for term_pattern, definition in tech_definitions.items():
        # Check if the term exists in the text (case insensitive)
        matches = re.finditer(term_pattern, enhanced_text, re.IGNORECASE)
        for match in matches:
            exact_match = match.group(0)
            if exact_match not in terms_added:
                # Only add the definition the first time the term appears
                terms_added.add(exact_match)
                # Replace with term + definition
                replacement = f"{exact_match} ({definition})"
                enhanced_text = enhanced_text[:match.start()] + replacement + enhanced_text[match.end():]
                # Fix the offset for future regex matches since we've modified the string
                break
    
    return enhanced_text

def format_bullet_points(bullets: str) -> str:
    """
    Format bullet points for better presentation.
    
    Args:
        bullets: Original bullet points text
        
    Returns:
        Formatted bullet points
    """
    if not bullets:
        return ""
    
    # Normalize bullet markers
    normalized = re.sub(r'^\s*[•\*\-]\s+', '• ', bullets, flags=re.MULTILINE)
    normalized = re.sub(r'^\s*(\d+)[\.\)]\s+', '• ', normalized, flags=re.MULTILINE)
    
    # Ensure each bullet point starts with a capital letter and ends with a period
    lines = normalized.strip().split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ensure proper bullet marker
        if not line.startswith('• '):
            line = '• ' + line
            
        # Ensure first letter after bullet is capitalized
        if len(line) > 2:
            line = line[:2] + line[2].upper() + line[3:]
            
        # Ensure line ends with proper punctuation
        if not line[-1] in '.!?':
            line += '.'
            
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def correct_spelling(text: str, known_words: List[str] = None) -> str:
    """
    Enhanced spelling correction for topics.
    
    Args:
        text: Text to correct
        known_words: List of known correct words to check against
        
    Returns:
        Corrected text
    """
    if not text or len(text.strip()) == 0:
        return text
        
    # First, handle common abbreviations and misspellings
    corrections = {
        # Common misspellings
        'ww2': 'World War II',
        'wwii': 'World War II',
        'ww1': 'World War I',
        'wwi': 'World War I',
        'usa': 'USA',
        'us': 'United States',
        'uk': 'United Kingdom',
        'ai': 'Artificial Intelligence',
        'ml': 'Machine Learning',
        'nft': 'NFT',
        'nfts': 'NFTs',
        'blockchain': 'Blockchain',
        'covid': 'COVID-19',
        'covid19': 'COVID-19',
        'covid-19': 'COVID-19',
        # Technology terms
        'iot': 'IoT',
        'ar': 'AR',
        'vr': 'VR',
        'xr': 'XR',
        'api': 'API',
        'apis': 'APIs',
        'saas': 'SaaS',
        'paas': 'PaaS',
        'iaas': 'IaaS',
        # Countries and regions
        'uae': 'UAE',
        'eu': 'EU',
        'un': 'UN',
        'nato': 'NATO',
        # Common abbreviations
        'vs': 'vs.',
        'e.g': 'e.g.',
        'i.e': 'i.e.',
        'etc': 'etc.',
    }
    
    # Check for exact lowercase matches
    lower_text = text.lower().strip()
    if lower_text in corrections:
        return corrections[lower_text]
        
    # Clean up text: remove multiple spaces, handle hyphenation
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix common capitalization issues in multi-word topics
    if ' ' in cleaned_text:
        words = cleaned_text.split(' ')
        # For titles/proper nouns, capitalize each word
        if len(words) <= 4:  # Apply only to short phrases
            properly_cased = []
            for word in words:
                # Don't capitalize certain words unless they're at the beginning
                if word.lower() in ['a', 'an', 'the', 'of', 'in', 'on', 'and', 'or', 'to', 'with']:
                    properly_cased.append(word.lower())
                else:
                    properly_cased.append(word.capitalize())
            # Always capitalize first word
            if properly_cased:
                properly_cased[0] = properly_cased[0].capitalize()
            return ' '.join(properly_cased)
    
    # For advanced spelling correction, we would use a library like pyspellchecker,
    # but for simplicity we're implementing some basic corrections
    # 1. Fix simple doubled letters: e.g., "appple" -> "apple"
    doubled_letter_pattern = re.compile(r'([a-zA-Z])\1{2,}')
    corrected = doubled_letter_pattern.sub(r'\1\1', cleaned_text)
    
    # 2. Fix simple missing vowels if it looks like they're missing
    vowel_pattern = re.compile(r'([bcdfghjklmnpqrstvwxyz]{3,})')
    
    def add_vowel(match):
        consonant_cluster = match.group(1)
        # Only do this for reasonable clusters that are likely missing a vowel
        if len(consonant_cluster) >= 3:
            # Insert 'e' as a default vowel
            middle = len(consonant_cluster) // 2
            return consonant_cluster[:middle] + 'e' + consonant_cluster[middle:]
        return consonant_cluster
    
    # Only apply advanced corrections if text doesn't match common patterns
    if corrected != cleaned_text:
        return corrected
    
    # If no other corrections applied, return the cleaned text
    return cleaned_text 

def enhance_poetic_language(text: str, temperature: float = 0.7) -> str:
    """
    Enhances text with poetic devices like alliteration, metaphors, and rhythm.
    
    Args:
        text: The text to enhance
        temperature: Creativity level (0.1-1.0)
        
    Returns:
        Poetically enhanced text
    """
    # Don't modify text if temperature is low
    if temperature < 0.6:
        return text
    
    # Replace some common phrases with more poetic alternatives
    poetic_substitutions = {
        r'\bin addition\b': 'like whispers on wind',
        r'\bfurthermore\b': 'as the story unfolds',
        r'\btherefore\b': 'thus, like rivers to sea',
        r'\bconsequently\b': 'and so, as fate would have it',
        r'\bhowever\b': 'yet, in contrast',
        r'\bfor example\b': 'imagine, if you will',
        r'\bsuch as\b': 'like',
        r'\bin conclusion\b': 'as our journey ends',
        r'\bfinally\b': 'at last, like dawn after night',
        r'\badditionally\b': 'dancing alongside this truth',
    }
    
    # Apply substitutions based on temperature
    substitution_count = 0
    max_substitutions = int(5 * temperature)  # Limit based on temperature
    
    for pattern, replacement in poetic_substitutions.items():
        if substitution_count >= max_substitutions:
            break
            
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE, count=1)
            substitution_count += 1
    
    return text 