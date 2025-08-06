"""
User preferences management for Pokémon VGC Summariser
Handles saving and loading user settings and preferences
"""

import json
import os
from typing import Dict, Any

PREFERENCES_PATH = "storage/user_preferences.json"

DEFAULT_PREFERENCES = {
    "theme": "light",
    "auto_cache": True,
    "show_debug_info": False,
    "preferred_model": "gemini",
    "language": "en",
    "max_cache_size": 100,
    "show_pokemon_images": True,
    "notification_sound": False,
    "auto_download": False,
    "summary_format": "detailed",  # detailed, compact, bullet_points
    "favorite_pokemon": [],
    "recent_searches": [],
    "max_recent_searches": 10
}

def load_preferences() -> Dict[str, Any]:
    """
    Load user preferences from file
    
    Returns:
        dict: User preferences with defaults for missing keys
    """
    try:
        if os.path.exists(PREFERENCES_PATH):
            with open(PREFERENCES_PATH, "r", encoding="utf-8") as f:
                saved_prefs = json.load(f)
            
            # Merge with defaults to ensure all keys exist
            preferences = DEFAULT_PREFERENCES.copy()
            preferences.update(saved_prefs)
            return preferences
        else:
            return DEFAULT_PREFERENCES.copy()
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_PREFERENCES.copy()

def save_preferences(preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to file
    
    Args:
        preferences (dict): User preferences to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(PREFERENCES_PATH), exist_ok=True)
        
        with open(PREFERENCES_PATH, "w", encoding="utf-8") as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def update_preference(key: str, value: Any) -> bool:
    """
    Update a single preference
    
    Args:
        key (str): Preference key to update
        value: New value for the preference
        
    Returns:
        bool: True if successful, False otherwise
    """
    preferences = load_preferences()
    preferences[key] = value
    return save_preferences(preferences)

def add_recent_search(search_term: str) -> bool:
    """
    Add a search term to recent searches
    
    Args:
        search_term (str): Search term to add
        
    Returns:
        bool: True if successful, False otherwise
    """
    preferences = load_preferences()
    recent = preferences.get("recent_searches", [])
    
    # Remove if already exists to avoid duplicates
    if search_term in recent:
        recent.remove(search_term)
    
    # Add to beginning
    recent.insert(0, search_term)
    
    # Limit size
    max_size = preferences.get("max_recent_searches", 10)
    recent = recent[:max_size]
    
    preferences["recent_searches"] = recent
    return save_preferences(preferences)

def get_recent_searches() -> list:
    """
    Get list of recent searches
    
    Returns:
        list: Recent search terms
    """
    preferences = load_preferences()
    return preferences.get("recent_searches", [])

def clear_recent_searches() -> bool:
    """
    Clear all recent searches
    
    Returns:
        bool: True if successful, False otherwise
    """
    return update_preference("recent_searches", [])

def add_favorite_pokemon(pokemon_name: str) -> bool:
    """
    Add a Pokémon to favorites
    
    Args:
        pokemon_name (str): Name of the Pokémon to add
        
    Returns:
        bool: True if successful, False otherwise
    """
    preferences = load_preferences()
    favorites = preferences.get("favorite_pokemon", [])
    
    if pokemon_name not in favorites:
        favorites.append(pokemon_name)
        preferences["favorite_pokemon"] = favorites
        return save_preferences(preferences)
    
    return True

def remove_favorite_pokemon(pokemon_name: str) -> bool:
    """
    Remove a Pokémon from favorites
    
    Args:
        pokemon_name (str): Name of the Pokémon to remove
        
    Returns:
        bool: True if successful, False otherwise
    """
    preferences = load_preferences()
    favorites = preferences.get("favorite_pokemon", [])
    
    if pokemon_name in favorites:
        favorites.remove(pokemon_name)
        preferences["favorite_pokemon"] = favorites
        return save_preferences(preferences)
    
    return True

def get_favorite_pokemon() -> list:
    """
    Get list of favorite Pokémon
    
    Returns:
        list: List of favorite Pokémon names
    """
    preferences = load_preferences()
    return preferences.get("favorite_pokemon", [])
