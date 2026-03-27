"""
Configuration management for Pokemon VGC Analysis application
"""

import os
import streamlit as st

# Re-export translations from centralized module for backward compatibility
from data.translations import (
    ITEM_TRANSLATIONS,
    POKEMON_NAME_TRANSLATIONS,
    MOVE_NAME_TRANSLATIONS,
    EV_STAT_TRANSLATIONS,
    NATURE_TRANSLATIONS,
    ABILITY_TRANSLATIONS,
)


def init_session_state():
    """Initialize all session state keys with defaults. Call once at app startup."""
    defaults = {
        "analysis_result": None,
        "current_url": None,
        "analysis_complete": False,
        "current_page": "Analysis Home",
        "user_api_key": None,
        "analyzer": None,
        "feedback_url": "",
        "feedback_description": "",
        "feedback_submitted": False,
        "analysis_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


class Config:
    """Application configuration management"""

    GOOGLE_API_KEY = None

    PAGE_TITLE = "Pokemon VGC Analysis"
    PAGE_ICON = "⚔️"
    LAYOUT = "wide"

    CACHE_ENABLED = True
    CACHE_TTL_HOURS = 24

    LOG_LEVEL = "INFO"
    LOG_DIR = "streamlit-app/logs"

    FEEDBACK_ENABLED = True

    @classmethod
    def init_config(cls, user_api_key: str = None):
        """Initialize configuration from user input, environment, or Streamlit secrets"""
        if user_api_key:
            cls.GOOGLE_API_KEY = user_api_key
            return

        try:
            cls.GOOGLE_API_KEY = st.secrets.get("google_api_key") or st.secrets.get("GOOGLE_API_KEY")
            if cls.GOOGLE_API_KEY:
                return
        except (KeyError, FileNotFoundError, AttributeError):
            pass

        cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    @classmethod
    def get_google_api_key(cls, user_api_key: str = None) -> str:
        """Get Google API key, initializing if needed"""
        if cls.GOOGLE_API_KEY is None or user_api_key:
            cls.init_config(user_api_key)
        return cls.GOOGLE_API_KEY

    @classmethod
    def ensure_log_directory(cls):
        """Ensure log directory exists"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)
