"""
Ollama LLM integration for Pokémon article summarization
Provides free, local LLM processing as an alternative to Google Gemini
"""

import os
from langchain_ollama import Ollama
from langchain_core.messages import HumanMessage
from .shared_utils import fetch_article_text_and_images
from .llm_summary import prompt_template, restricted_poke

def llm_summary_ollama(url, model_name="llama3.2:3b"):
    """
    Generate summary using Ollama local LLM
    
    Args:
        url (str): Article URL to summarize
        model_name (str): Ollama model to use (default: llama3.2:3b)
    
    Returns:
        str: Generated summary
    """
    try:
        # Fetch article content
        article_text, image_urls = fetch_article_text_and_images(url)
        
        # Create prompt
        prompt = prompt_template.format(restrict_poke=restricted_poke, text=article_text)
        
        # Initialize Ollama
        llm = Ollama(
            model=model_name,
            temperature=0.0,
            num_ctx=8192,  # Context window
            num_predict=4000,  # Max tokens to generate
            repeat_penalty=1.1,  # Reduce repetition
            top_k=40,
            top_p=0.9
        )
        
        # Generate response
        response = llm.invoke(prompt)
        return str(response)
        
    except Exception as e:
        raise Exception(f"Ollama LLM processing failed: {e}")

def get_available_ollama_models():
    """
    Get list of recommended Ollama models for this use case
    
    Returns:
        list: Available model names
    """
    return [
        "llama3.2:3b",      # Fast, good for basic tasks
        "llama3.2:8b",      # Better quality, moderate speed
        "llama3.2:70b",     # Best quality, slower
        "mistral:7b",       # Good multilingual support
        "mixtral:8x7b",     # Excellent performance
        "qwen2.5:7b",       # Good multilingual capabilities
        "qwen2.5:14b",      # Better quality
        "codellama:7b",     # Good for structured output
        "phi3:3.8b",        # Fast, good quality
        "gemma2:2b",        # Very fast, basic quality
        "gemma2:9b",        # Good balance
    ]

def check_ollama_installation():
    """
    Check if Ollama is installed and running
    
    Returns:
        bool: True if Ollama is available
    """
    try:
        import subprocess
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_ollama_model(model_name):
    """
    Install an Ollama model
    
    Args:
        model_name (str): Model to install
    """
    try:
        import subprocess
        subprocess.run(['ollama', 'pull', model_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False 