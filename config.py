"""
Configuration management for Pokemon VGC Analysis application
"""

import os
import streamlit as st


class Config:
    """Application configuration management"""

    # API Configuration
    GOOGLE_API_KEY = None

    # Application Settings
    PAGE_TITLE = "Pokemon VGC Analysis"
    PAGE_ICON = "⚔️"
    LAYOUT = "wide"

    # Cache Settings
    CACHE_ENABLED = True
    CACHE_TTL_HOURS = 24

    # Logging Settings
    LOG_LEVEL = "INFO"
    LOG_DIR = "streamlit-app/logs"

    @classmethod
    def init_config(cls):
        """Initialize configuration from environment and Streamlit secrets"""
        try:
            # Try to get from Streamlit secrets first
            cls.GOOGLE_API_KEY = st.secrets.get("google_api_key")
        except (KeyError, FileNotFoundError):
            # Fall back to environment variable
            cls.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

        if not cls.GOOGLE_API_KEY:
            st.error(
                "❌ Google API key not found. "
                "Please set it in .streamlit/secrets.toml or environment variable."
            )
            st.stop()

    @classmethod
    def get_google_api_key(cls) -> str:
        """Get Google API key, initializing if needed"""
        if cls.GOOGLE_API_KEY is None:
            cls.init_config()
        return cls.GOOGLE_API_KEY

    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL"""
        return "sqlite:///vgc_analyzer.db"

    @classmethod
    def ensure_log_directory(cls):
        """Ensure log directory exists"""
        os.makedirs(cls.LOG_DIR, exist_ok=True)


# Translation mappings
ITEM_TRANSLATIONS = {
    # English to Japanese
    "leftovers": "たべのこし",
    "focus-sash": "きあいのタスキ",
    "mystic-water": "しんぴのしずく",
    "life-orb": "いのちのたま",
    "choice-band": "こだわりハチマキ",
    "choice-specs": "こだわりメガネ",
    "choice-scarf": "こだわりスカーフ",
    "assault-vest": "とつげきチョッキ",
    "sitrus-berry": "オボンのみ",
    "lum-berry": "ラムのみ",
    "safety-goggles": "ぼうじんゴーグル",
    "booster-energy": "ブーストエナジー",
    "clear-amulet": "クリアチャーム",
    "covert-cloak": "しんしょくオーブ",
    "rocky-helmet": "ゴツゴツメット",
    "mental-herb": "メンタルハーブ",
    "wide-lens": "こうかくレンズ",
    "mirror-herb": "ものまねハーブ",
    # Japanese to English (reverse mapping)
    "たべのこし": "leftovers",
    "きあいのタスキ": "focus-sash",
    "しんぴのしずく": "mystic-water",
    "いのちのたま": "life-orb",
    "こだわりハチマキ": "choice-band",
    "こだわりメガネ": "choice-specs",
    "こだわりスカーフ": "choice-scarf",
    "とつげきチョッキ": "assault-vest",
    "オボンのみ": "sitrus-berry",
    "ラムのみ": "lum-berry",
    "ぼうじんゴーグル": "safety-goggles",
    "ブーストエナジー": "booster-energy",
    "クリアチャーム": "clear-amulet",
    "しんしょくオーブ": "covert-cloak",
    "ゴツゴツメット": "rocky-helmet",
    "メンタルハーブ": "mental-herb",
    "こうかくレンズ": "wide-lens",
    "ものまねハーブ": "mirror-herb",
}

# Pokemon name translations (add more as needed)
POKEMON_NAME_TRANSLATIONS = {
    # Add common translations
    "リザードン": "Charizard",
    "カメックス": "Blastoise",
    "フシギバナ": "Venusaur",
    # Add more as needed...
}

# Move name translations (add more as needed)
MOVE_NAME_TRANSLATIONS = {
    "10まんボルト": "Thunderbolt",
    "かえんほうしゃ": "Flamethrower",
    "なみのり": "Surf",
    # Add more as needed...
}
