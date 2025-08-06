"""
Google Gemini LLM integration for Pokémon article summarization
Provides cloud-based LLM processing with excellent Japanese translation capabilities
"""

import os
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
from utils.shared_utils import fetch_article_text_and_images
from .llm_summary import prompt_template, restricted_poke

def llm_summary_gemini(url):
    """
    Generate summary using Google Gemini LLM with enhanced EV extraction from images
    
    Args:
        url (str): Article URL to summarize
    
    Returns:
        str: Generated summary
    """
    try:
        # Load secrets
        import streamlit as st
        secrets = st.secrets
        
        # Fetch article content with enhanced image filtering
        article_text, image_urls = fetch_article_text_and_images(url)
        
        # Filter images for Pokemon team images (likely to contain EV data)
        filtered_images = image_urls  # Use all images for now to avoid function issues
        
        print(f"DEBUG - Found {len(image_urls)} total images, filtered to {len(filtered_images)} potential team images")
        
        # Create enhanced prompt with EV focus
        enhanced_prompt = prompt_template.format(restrict_poke=restricted_poke, text=article_text)
        
        # Initialize Gemini with optimal settings for image analysis
        chat = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=secrets["google_api_key"],
            temperature=0.0,  # Keep at 0 for consistent EV extraction
            max_tokens=6000   # Increased for detailed EV analysis
        )
        
        # Prepare content with enhanced image processing
        content_parts = wrap_prompt_and_image_urls_enhanced(enhanced_prompt, filtered_images)
        message = HumanMessage(content=content_parts)
        
        # Generate response
        print("DEBUG - Sending request to Gemini with enhanced EV extraction prompt...")
        response = chat.invoke([message])
        
        # Post-process response to ensure EV data is captured
        processed_response = str(response.content)
        
        return processed_response
        
    except Exception as e:
        raise Exception(f"Gemini LLM processing failed: {e}")

def wrap_prompt_and_image_urls_enhanced(prompt, image_urls):
    """
    Wrap prompt with image URLs for Gemini multimodal processing with enhanced image processing
    
    Args:
        prompt (str): Text prompt
        image_urls (list): List of image URLs
    
    Returns:
        list: Content parts for Gemini
    """
    content = [{"type": "text", "text": prompt}]
    for url in image_urls:
        if any(ext in url.lower() for ext in ["png", "jpg", "jpeg", "webp"]):
            content.append({
                "type": "image_url",
                "image_url": {"url": url}
            })
    return content

def filter_pokemon_team_images(image_urls):
    """
    Filter images to identify potential Pokemon team images that likely contain EV data
    
    Args:
        image_urls (list): List of image URLs from the article
    
    Returns:
        list: Filtered list of potential team images
    """
    if not image_urls:
        return []
    
    # Keywords that suggest Pokemon team images
    team_keywords = [
        'team', 'pokemon', 'pokémon', 'vgc', 'competitive', 'battle', 'strategy',
        'build', 'spread', 'ev', 'effort', 'stats', 'moves', 'ability', 'item',
        'tera', 'nature', 'pokemon', 'pokémon', 'team', 'build', 'spread'
    ]
    
    # File extensions for images
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.gif']
    
    filtered_images = []
    
    for url in image_urls:
        url_lower = url.lower()
        
        # Check if it's an image file
        is_image = any(ext in url_lower for ext in image_extensions)
        
        # Check if URL contains team-related keywords
        has_team_keywords = any(keyword in url_lower for keyword in team_keywords)
        
        # Include if it's an image and either has team keywords or we don't have many images
        if is_image and (has_team_keywords or len(image_urls) <= 5):
            filtered_images.append(url)
    
    # If no images were filtered, return all images (better to analyze all than none)
    if not filtered_images and image_urls:
        filtered_images = [url for url in image_urls if any(ext in url.lower() for ext in image_extensions)]
    
    return filtered_images

def create_ev_focused_prompt(article_text):
    """
    Create an enhanced prompt focused on EV extraction
    
    Args:
        article_text (str): Original article text
    
    Returns:
        str: Enhanced prompt with EV focus
    """
    # Use the existing prompt template but add EV-specific instructions
    enhanced_prompt = prompt_template.format(
        restrict_poke=restricted_poke,
        text=article_text
    )
    
    # Add additional EV-focused instructions
    ev_focus_addition = """
    
**CRITICAL EV EXTRACTION FOCUS:**
- **PRIORITIZE IMAGE ANALYSIS**: If team images are provided, analyze them FIRST for EV data
- **LOOK FOR STAT NUMBERS**: In images, look for numbers that could be EV values (0-252 in multiples of 4)
- **JAPANESE EV PATTERNS**: Search for patterns like "H244 A252 B4 D4 S4" or "努力値：H244 A252 B4 D4 S4"
- **ENGLISH EV PATTERNS**: Look for "252 HP EVs", "252 Attack EVs", etc.
- **CONSISTENT OUTPUT**: Always output EV Spread in format: "EV Spread: [HP] [Atk] [Def] [SpA] [SpD] [Spe]"
- **DEFAULT VALUES**: If no EVs found, use "EV Spread: 0 0 0 0 0 0"
- **VALIDATE TOTALS**: Ensure total EVs equal 508 (or less if some EVs are not invested)
"""
    
    return enhanced_prompt + ev_focus_addition

def post_process_ev_response(response_text):
    """
    Post-process the Gemini response to ensure EV data is properly formatted
    
    Args:
        response_text (str): Raw response from Gemini
    
    Returns:
        str: Processed response with improved EV formatting
    """
    if not response_text:
        return response_text
    
    # Ensure EV Spread lines are properly formatted
    lines = response_text.split('\n')
    processed_lines = []
    
    for line in lines:
        # Check if this line should contain EV Spread but doesn't have the right format
        if 'EV Spread:' in line:
            # Ensure it has the correct format
            if not re.search(r'EV Spread:\s*\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+', line):
                # Try to extract numbers and reformat
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 6:
                    # Ensure we have exactly 6 numbers
                    ev_values = numbers[:6]
                    # Ensure values are valid EV numbers (0-252, multiples of 4)
                    ev_values = [str(min(252, max(0, int(val) // 4 * 4))) for val in ev_values]
                    line = f"EV Spread: {' '.join(ev_values)}"
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def check_gemini_availability():
    """
    Check if Google Gemini is available (API key present)
    
    Returns:
        bool: True if Gemini is available
    """
    try:
        import streamlit as st
        secrets = st.secrets
        return "google_api_key" in secrets and bool(secrets["google_api_key"])
    except:
        return False 