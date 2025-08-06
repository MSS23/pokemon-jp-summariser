"""
Shared utilities for Pokémon article summarization
Common functions used by both Gemini and Ollama integrations
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Import the prompt template and restricted Pokémon list
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'streamlit-app', 'utils'))
from llm_summary import prompt_template, restricted_poke

def fetch_article_text_and_images(url):
    """
    Fetch article text and images from a given URL
    
    Args:
        url (str): Article URL to fetch
    
    Returns:
        tuple: (article_text, image_urls)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        
        if response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()

        main_content = None
        content_selectors = [
            'main', 'article', '.content', '.post-content', '.entry-content',
            '.article-content', '.main-content', '#content', '#main',
            '.post', '.entry', '.blog-post', '.article'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body if soup.body else soup

        paragraphs = [p.get_text(separator=" ", strip=True) for p in main_content.find_all("p")]
        headings = [h.get_text(separator=" ", strip=True) for h in main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        
        div_texts = []
        for div in main_content.find_all("div"):
            text = div.get_text(separator=" ", strip=True)
            if len(text) > 50 and not any(skip in text.lower() for skip in ['menu', 'navigation', 'sidebar', 'footer', 'header', 'advertisement']):
                div_texts.append(text)
        
        all_text_parts = []
        if headings:
            all_text_parts.append("HEADINGS:\n" + "\n".join(headings))
        if paragraphs:
            all_text_parts.append("CONTENT:\n" + "\n".join(paragraphs))
        if div_texts:
            all_text_parts.append("ADDITIONAL CONTENT:\n" + "\n".join(div_texts[:5]))
        
        all_text = "\n\n".join(all_text_parts)

        clean_text = re.sub(r'[\u200b\xa0\u200e\u200f]', ' ', all_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\/\@\#\$\%\&\*\+\=\|\~\`\'\"]', '', clean_text)
        clean_text = clean_text.strip()

        image_tags = soup.find_all("img")
        image_urls = []
        for img in image_tags:
            src = img.get("src")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    base_url = url.split("//")[0] + "//" + url.split("/")[2]
                    src = base_url + src
                elif not src.startswith("http"):
                    base_url = "/".join(url.split("/")[:-1]) + "/"
                    src = base_url + src
                
                if not any(skip in src.lower() for skip in ['logo', 'icon', 'avatar', 'banner', 'ad', 'ads']):
                    image_urls.append(src)

        return clean_text, image_urls
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch article: {e}")
    except Exception as e:
        raise Exception(f"Error processing article: {e}")

def extract_pokemon_names(summary):
    """
    Extract Pokémon names from summary text
    
    Args:
        summary (str): Generated summary text
    
    Returns:
        list: List of Pokémon names
    """
    lines = summary.splitlines()
    pokemon_names = []

    # Method 1: Try 1. to 6. pattern
    numbered = [
        re.sub(r"^\d+\.\s+", "", line).strip()
        for line in lines if re.match(r"^\d+\.\s+", line)
    ]
    if len(numbered) == 6:
        pokemon_names = numbered

    # Method 2: Name: entries
    if not pokemon_names:
        pokemon_names = [
            line.replace("Name:", "").strip()
            for line in lines if line.strip().startswith("Name:")
        ]

    return pokemon_names 