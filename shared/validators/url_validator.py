"""
Shared URL validation utilities for both Streamlit and React applications.
"""

import re
from urllib.parse import urlparse
from typing import List, Optional

# Supported domains for Pokemon articles
SUPPORTED_DOMAINS = [
    "note.com",
    "pokemon.co.jp", 
    "pokemon.com",
    "serebii.net",
    "bulbapedia.bulbagarden.net",
    "smogon.com",
    "pokemondb.net",
    "pokemoncentral.it",
    "pokemon.com.br",
    "pokemon.co.kr"
]

# URL patterns for different article types
URL_PATTERNS = {
    "note.com": r"https?://note\.com/[^/]+/n/[a-zA-Z0-9]+",
    "pokemon.co.jp": r"https?://www\.pokemon\.co\.jp/.*",
    "pokemon.com": r"https?://www\.pokemon\.com/.*",
    "serebii.net": r"https?://www\.serebii\.net/.*",
    "bulbapedia": r"https?://bulbapedia\.bulbagarden\.net/.*",
    "smogon.com": r"https?://www\.smogon\.com/.*",
    "pokemondb.net": r"https?://pokemondb\.net/.*"
}

def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid and properly formatted.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Remove whitespace
    url = url.strip()
    
    # Check if URL starts with http or https
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme)
    except Exception:
        return False

def is_supported_domain(url: str) -> bool:
    """
    Check if the URL is from a supported domain.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if domain is supported, False otherwise
    """
    if not is_valid_url(url):
        return False
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain in SUPPORTED_DOMAINS
    except Exception:
        return False

def extract_domain(url: str) -> Optional[str]:
    """
    Extract the domain from a URL.
    
    Args:
        url (str): URL to extract domain from
        
    Returns:
        Optional[str]: Domain name or None if invalid
    """
    if not is_valid_url(url):
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return domain
    except Exception:
        return None

def validate_pokemon_article_url(url: str) -> dict:
    """
    Comprehensive validation for Pokemon article URLs.
    
    Args:
        url (str): URL to validate
        
    Returns:
        dict: Validation result with status and message
    """
    if not url:
        return {
            "valid": False,
            "message": "URL is required",
            "domain": None
        }
    
    if not is_valid_url(url):
        return {
            "valid": False,
            "message": "Invalid URL format",
            "domain": None
        }
    
    domain = extract_domain(url)
    if not domain:
        return {
            "valid": False,
            "message": "Could not extract domain from URL",
            "domain": None
        }
    
    if not is_supported_domain(url):
        return {
            "valid": False,
            "message": f"Domain '{domain}' is not supported. Supported domains: {', '.join(SUPPORTED_DOMAINS)}",
            "domain": domain
        }
    
    return {
        "valid": True,
        "message": "URL is valid",
        "domain": domain
    }

def sanitize_url(url: str) -> str:
    """
    Sanitize a URL by removing extra whitespace and normalizing.
    
    Args:
        url (str): URL to sanitize
        
    Returns:
        str: Sanitized URL
    """
    if not url:
        return ""
    
    # Remove whitespace
    url = url.strip()
    
    # Ensure protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def get_url_type(url: str) -> Optional[str]:
    """
    Determine the type of URL based on domain and pattern.
    
    Args:
        url (str): URL to analyze
        
    Returns:
        Optional[str]: URL type or None if unknown
    """
    if not is_valid_url(url):
        return None
    
    domain = extract_domain(url)
    if not domain:
        return None
    
    # Check specific patterns
    for pattern_name, pattern in URL_PATTERNS.items():
        if re.match(pattern, url, re.IGNORECASE):
            return pattern_name
    
    # Return domain as fallback
    return domain

def is_japanese_article(url: str) -> bool:
    """
    Check if the URL likely points to a Japanese article.
    
    Args:
        url (str): URL to check
        
    Returns:
        bool: True if likely Japanese article
    """
    japanese_domains = [
        "note.com",
        "pokemon.co.jp"
    ]
    
    domain = extract_domain(url)
    return domain in japanese_domains 