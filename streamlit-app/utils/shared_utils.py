"""
Shared utilities for Pokemon VGC Team Analyzer
Common functions used across different modules
"""

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Tuple, List
import streamlit as st

def strip_html_tags(text: str) -> str:
    """
    Strip HTML tags from text content
    
    Args:
        text (str): Text content that may contain HTML tags
        
    Returns:
        str: Clean text without HTML tags
    """
    try:
        # Use BeautifulSoup to parse and extract text
        soup = BeautifulSoup(text, 'html.parser')
        # Get text content, removing all HTML tags
        clean_text = soup.get_text()
        
        # Additional cleaning: remove extra whitespace
        lines = (line.strip() for line in clean_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        return clean_text
    except Exception as e:
        # If BeautifulSoup fails, fall back to regex
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text

def fetch_article_text_and_images(url: str) -> Tuple[str, List[str]]:
    """
    Fetch article content and extract images from a URL
    
    Args:
        url (str): Article URL to fetch
        
    Returns:
        tuple: (article_text, image_urls)
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract images
        image_urls = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(url, src)
                image_urls.append(absolute_url)
        
        # Filter for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        filtered_images = [
            img_url for img_url in image_urls 
            if any(ext in img_url.lower() for ext in image_extensions)
        ]
        
        return text, filtered_images
        
    except Exception as e:
        st.error(f"Failed to fetch article content: {str(e)}")
        return "", []

def extract_pokemon_names(summary: str) -> List[str]:
    """
    Extract Pokemon names from the summary text
    
    Args:
        summary (str): The summary text containing Pokemon information
        
    Returns:
        list: List of Pokemon names found in the summary
    """
    try:
        # Common Pokemon names pattern
        pokemon_pattern = r'Pokémon\s+\d+:\s*([A-Za-z\-\s]+?)(?:\n|$|\(|\[)'
        
        # Find all Pokemon names
        matches = re.findall(pokemon_pattern, summary, re.IGNORECASE)
        
        # Clean up the names
        pokemon_names = []
        for match in matches:
            name = match.strip()
            if name and len(name) > 1:  # Filter out empty or single character names
                pokemon_names.append(name)
        
        # If no Pokemon found with the pattern, try alternative patterns
        if not pokemon_names:
            # Look for Pokemon names in various formats
            alt_patterns = [
                r'([A-Z][a-z]+(?:\-[A-Z][a-z]+)*)',  # Capitalized words with possible hyphens
                r'([A-Za-z]+(?:\s+[A-Za-z]+)*)',     # General word patterns
            ]
            
            for pattern in alt_patterns:
                matches = re.findall(pattern, summary)
                for match in matches:
                    name = match.strip()
                    if name and len(name) > 2 and name.lower() not in ['the', 'and', 'with', 'for', 'from', 'this', 'that']:
                        pokemon_names.append(name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in pokemon_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        
        return unique_names[:10]  # Limit to first 10 Pokemon names
        
    except Exception as e:
        st.error(f"Failed to extract Pokemon names: {str(e)}")
        return []
