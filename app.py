"""
Pokemon VGC Article Analyzer & Team Showcase
A single-page Streamlit application for analyzing Japanese VGC articles and showcasing teams
"""

import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Optional, Any, Tuple
import os
from urllib.parse import urlparse, urljoin
import base64
from io import BytesIO
from PIL import Image
import hashlib
from datetime import datetime, timedelta

try:
    from langchain_community.document_loaders import WebBaseLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# Import new modules
try:
    from database.models import init_database, get_session
    from database.crud import (
        TeamCRUD,
        BookmarkCRUD,
        SpeedTierCRUD,
        DamageCalculationCRUD,
    )
    from calculations.damage_calc import (
        DamageCalculator,
        PokemonStats,
        Move,
        DamageModifiers,
    )
    from calculations.speed_tiers import SpeedTierAnalyzer, SpeedTierEntry

    DATABASE_AVAILABLE = True
except ImportError as e:
    st.error(f"Database modules not available: {e}")
    DATABASE_AVAILABLE = False

# Item Translation Database
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

# Common VGC Items List for Vision Recognition
COMMON_VGC_ITEMS = [
    "Leftovers",
    "Focus Sash",
    "Mystic Water",
    "Life Orb",
    "Choice Band",
    "Choice Specs",
    "Choice Scarf",
    "Assault Vest",
    "Sitrus Berry",
    "Lum Berry",
    "Safety Goggles",
    "Booster Energy",
    "Clear Amulet",
    "Covert Cloak",
    "Rocky Helmet",
    "Mental Herb",
    "Wide Lens",
    "Mirror Herb",
    "Expert Belt",
    "Weakness Policy",
    "たべのこし",
    "きあいのタスキ",
    "しんぴのしずく",
    "いのちのたま",
]

# VGC Regulation Database (Scarlet & Violet Era)
VGC_REGULATIONS = {
    "A": {
        "period": "November 2022 - January 2023",
        "description": "Paldea Dex only, no legendaries/mythicals",
        "restricted": [],
        "banned": ["Legendaries", "Mythicals", "Paradox Pokemon"],
    },
    "B": {
        "period": "February 2023 - May 2023",
        "description": "Paldea Dex + Home transfer, no restricted",
        "restricted": [],
        "banned": ["Restricted Legendaries"],
    },
    "C": {
        "period": "May 2023 - September 2023",
        "description": "Series 1 with restricted legendaries allowed",
        "restricted": ["Koraidon", "Miraidon", "Box Legendaries"],
        "banned": [],
    },
    "D": {
        "period": "September 2023 - January 2024",
        "description": "Series 2 with expanded legendary pool",
        "restricted": [
            "Koraidon",
            "Miraidon",
            "Kyogre",
            "Groudon",
            "Dialga",
            "Palkia",
            "Giratina",
            "Reshiram",
            "Zekrom",
            "Kyurem",
            "Xerneas",
            "Yveltal",
            "Zygarde",
            "Cosmog",
            "Cosmoem",
            "Solgaleo",
            "Lunala",
            "Necrozma",
        ],
        "banned": [],
    },
    "E": {
        "period": "January 2024 - May 2024",
        "description": "Series 3 with Treasures of Ruin",
        "restricted": [
            "Koraidon",
            "Miraidon",
            "Chi-Yu",
            "Chien-Pao",
            "Ting-Lu",
            "Wo-Chien",
        ]
        + [
            "Kyogre",
            "Groudon",
            "Dialga",
            "Palkia",
            "Giratina",
            "Reshiram",
            "Zekrom",
            "Kyurem",
            "Xerneas",
            "Yveltal",
            "Zygarde",
            "Solgaleo",
            "Lunala",
            "Necrozma",
        ],
        "banned": [],
    },
    "F": {
        "period": "May 2024 - September 2024",
        "description": "Series 4 with DLC legendaries",
        "restricted": [
            "Koraidon",
            "Miraidon",
            "Kyogre",
            "Groudon",
            "Rayquaza",
            "Dialga",
            "Palkia",
            "Giratina",
            "Reshiram",
            "Zekrom",
            "Kyurem",
            "Xerneas",
            "Yveltal",
            "Zygarde",
            "Solgaleo",
            "Lunala",
            "Necrozma",
            "Calyrex",
            "Calyrex-Ice",
            "Calyrex-Shadow",
        ],
        "banned": [],
    },
    "G": {
        "period": "September 2024 - January 2025",
        "description": "Series 5 with expanded roster",
        "restricted": ["All Box Legendaries", "Calyrex forms", "Urshifu forms"],
        "banned": [],
    },
    "H": {
        "period": "January 2025 - May 2025",
        "description": "Series 6 current format",
        "restricted": ["All Previous Restricted Pokemon"],
        "banned": [],
    },
    "I": {
        "period": "May 2025 onwards",
        "description": "Series 7 upcoming format",
        "restricted": ["TBD"],
        "banned": [],
    },
}

# Regulation Detection Keywords
REGULATION_KEYWORDS = {
    "A": [
        "Paldea Dex",
        "no legendaries",
        "November 2022",
        "December 2022",
        "January 2023",
    ],
    "B": ["Home transfer", "February 2023", "March 2023", "April 2023", "May 2023"],
    "C": [
        "restricted legendaries",
        "Series 1",
        "Koraidon",
        "Miraidon",
        "May 2023",
        "June 2023",
    ],
    "D": [
        "expanded legendary",
        "Series 2",
        "September 2023",
        "October 2023",
        "November 2023",
        "December 2023",
    ],
    "E": [
        "Treasures of Ruin",
        "Series 3",
        "Chi-Yu",
        "Chien-Pao",
        "January 2024",
        "February 2024",
    ],
    "F": [
        "DLC legendaries",
        "Series 4",
        "Calyrex",
        "May 2024",
        "June 2024",
        "July 2024",
    ],
    "G": ["Series 5", "expanded roster", "September 2024", "October 2024"],
    "H": ["Series 6", "January 2025", "current format"],
    "I": ["Series 7", "May 2025", "upcoming"],
}

# Page configuration
st.set_page_config(
    page_title="Pokemon VGC Article Analyzer",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS for styling
st.markdown(
    """
<style>
    .main {
        padding-top: 1rem;
    }
    .stTitle {
        color: #1f4e79;
        font-weight: bold;
    }
    
    /* Pokemon Type Colors */
    .type-normal { --type-color: #A8A878; --type-bg: linear-gradient(135deg, #A8A878 0%, #9C9C7C 100%); }
    .type-fire { --type-color: #F08030; --type-bg: linear-gradient(135deg, #F08030 0%, #DD6610 100%); }
    .type-water { --type-color: #6890F0; --type-bg: linear-gradient(135deg, #6890F0 0%, #4A73C8 100%); }
    .type-electric { --type-color: #F8D030; --type-bg: linear-gradient(135deg, #F8D030 0%, #E6B800 100%); }
    .type-grass { --type-color: #78C850; --type-bg: linear-gradient(135deg, #78C850 0%, #5CA935 100%); }
    .type-ice { --type-color: #98D8D8; --type-bg: linear-gradient(135deg, #98D8D8 0%, #7BC5C5 100%); }
    .type-fighting { --type-color: #C03028; --type-bg: linear-gradient(135deg, #C03028 0%, #A01E18 100%); }
    .type-poison { --type-color: #A040A0; --type-bg: linear-gradient(135deg, #A040A0 0%, #822882 100%); }
    .type-ground { --type-color: #E0C068; --type-bg: linear-gradient(135deg, #E0C068 0%, #D4A74A 100%); }
    .type-flying { --type-color: #A890F0; --type-bg: linear-gradient(135deg, #A890F0 0%, #8A73C8 100%); }
    .type-psychic { --type-color: #F85888; --type-bg: linear-gradient(135deg, #F85888 0%, #E63F6B 100%); }
    .type-bug { --type-color: #A8B820; --type-bg: linear-gradient(135deg, #A8B820 0%, #8A9A0A 100%); }
    .type-rock { --type-color: #B8A038; --type-bg: linear-gradient(135deg, #B8A038 0%, #A0882A 100%); }
    .type-ghost { --type-color: #705898; --type-bg: linear-gradient(135deg, #705898 0%, #5A4470 100%); }
    .type-dragon { --type-color: #7038F8; --type-bg: linear-gradient(135deg, #7038F8 0%, #5A2AD6 100%); }
    .type-dark { --type-color: #705848; --type-bg: linear-gradient(135deg, #705848 0%, #5A4638 100%); }
    .type-steel { --type-color: #B8B8D0; --type-bg: linear-gradient(135deg, #B8B8D0 0%, #A0A0B8 100%); }
    .type-fairy { --type-color: #EE99AC; --type-bg: linear-gradient(135deg, #EE99AC 0%, #E87D94 100%); }
    
    /* Role-based accent colors */
    .role-physical-attacker { --role-accent: #FF6B6B; }
    .role-special-attacker { --role-accent: #4ECDC4; }
    .role-physical-wall { --role-accent: #45B7D1; }
    .role-special-wall { --role-accent: #96CEB4; }
    .role-support { --role-accent: #FECA57; }
    .role-speed-control { --role-accent: #FF9FF3; }
    .role-utility { --role-accent: #54A0FF; }
    
    .pokemon-card {
        background: var(--type-bg, linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%));
        border: 2px solid var(--type-color, #cbd5e1);
        border-radius: clamp(16px, 4vw, 20px);
        padding: clamp(16px, 4vw, 24px);
        margin: clamp(8px, 2vw, 12px) 0;
        color: #1e293b;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
    }
    
    .pokemon-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--role-accent, var(--type-color, #3b82f6));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .pokemon-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border-color: var(--role-accent, var(--type-color, #3b82f6));
    }
    
    .pokemon-card:hover::before {
        transform: scaleX(1);
    }
    .pokemon-info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: clamp(8px, 2vw, 12px);
        margin-top: 16px;
    }
    .info-item {
        background: rgba(255, 255, 255, 0.9);
        padding: clamp(10px, 2vw, 16px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        min-height: 60px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .info-item:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .info-label {
        font-size: clamp(10px, 2.5vw, 11px);
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .info-value {
        font-size: clamp(12px, 3vw, 14px);
        font-weight: 600;
        color: #1e293b;
        word-break: break-word;
        line-height: 1.3;
        overflow-wrap: anywhere;
    }
    
    /* EV Spread Visualization */
    .ev-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        margin-top: 16px;
        border: 2px solid var(--type-color, #e2e8f0);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .ev-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .ev-title {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .ev-total {
        font-size: 14px;
        font-weight: 600;
        color: var(--type-color, #3b82f6);
        background: rgba(59, 130, 246, 0.1);
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid var(--type-color, #3b82f6);
    }
    
    .ev-stats-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    
    .ev-stat {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px;
        border-radius: 8px;
        background: rgba(248, 250, 252, 0.8);
        transition: all 0.3s ease;
    }
    
    .ev-stat:hover {
        background: rgba(248, 250, 252, 1);
        transform: translateX(4px);
    }
    
    .ev-stat-icon {
        font-size: 18px;
        width: 24px;
        text-align: center;
    }
    
    .ev-stat-name {
        font-size: clamp(10px, 2vw, 12px);
        font-weight: 600;
        color: #64748b;
        min-width: 32px;
        text-transform: uppercase;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .ev-stat-bar-container {
        flex: 1;
        height: clamp(6px, 1.5vw, 8px);
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
        min-width: 60px;
    }
    
    .ev-stat-bar {
        height: 100%;
        border-radius: 4px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .ev-stat-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .ev-stat-value {
        font-size: clamp(11px, 2.5vw, 12px);
        font-weight: 700;
        color: #1e293b;
        min-width: 28px;
        text-align: right;
        white-space: nowrap;
    }
    
    /* Stat-specific colors */
    .ev-hp .ev-stat-bar { background: linear-gradient(90deg, #FF6B6B 0%, #FF5252 100%); }
    .ev-atk .ev-stat-bar { background: linear-gradient(90deg, #FFA726 0%, #FF9800 100%); }
    .ev-def .ev-stat-bar { background: linear-gradient(90deg, #42A5F5 0%, #2196F3 100%); }
    .ev-spa .ev-stat-bar { background: linear-gradient(90deg, #AB47BC 0%, #9C27B0 100%); }
    .ev-spd .ev-stat-bar { background: linear-gradient(90deg, #66BB6A 0%, #4CAF50 100%); }
    .ev-spe .ev-stat-bar { background: linear-gradient(90deg, #FFEE58 0%, #FFEB3B 100%); }
    
    /* EV Investment Highlighting System */
    
    /* Base class for any EV investment */
    .ev-stat.has-evs {
        border: 1px solid rgba(255, 193, 7, 0.4);
    }
    
    /* Small investment (1-31 EVs) - Light yellow */
    .ev-stat.small-investment {
        background: rgba(255, 248, 225, 0.8);
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .ev-stat.small-investment .ev-stat-value {
        color: #B8860B;
        font-weight: 600;
        background: rgba(255, 193, 7, 0.1);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Medium investment (32-100 EVs) - Medium yellow */
    .ev-stat.medium-investment {
        background: rgba(255, 235, 59, 0.25);
        border: 1px solid rgba(255, 193, 7, 0.5);
    }
    
    .ev-stat.medium-investment .ev-stat-value {
        color: #9A7B0A;
        font-weight: 700;
        background: rgba(255, 193, 7, 0.2);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Large investment (101-251 EVs) - Bright yellow */
    .ev-stat.large-investment {
        background: rgba(255, 235, 59, 0.4);
        border: 1px solid rgba(255, 193, 7, 0.7);
        box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
    }
    
    .ev-stat.large-investment .ev-stat-value {
        color: #7D6608;
        font-weight: 700;
        background: rgba(255, 193, 7, 0.3);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Maxed investment (252 EVs) - Gold highlighting */
    .ev-stat.maxed {
        background: rgba(255, 215, 0, 0.5);
        border: 2px solid #FFD700;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
    }
    
    .ev-stat.maxed .ev-stat-value {
        color: #B8860B;
        font-weight: 800;
        background: rgba(255, 215, 0, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid #DAA520;
    }
    
    /* Enhanced highlighting for all invested stats */
    .ev-stat.has-evs:hover {
        transform: translateX(6px);
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.2);
    }
    
    /* Tooltips and Interactive Elements */
    .tooltip {
        position: relative;
        cursor: help;
    }
    
    .tooltip::before {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 130%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        bottom: 120%;
        left: 50%;
        transform: translateX(-50%);
        border: 5px solid transparent;
        border-top-color: rgba(0, 0, 0, 0.9);
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }
    
    .tooltip:hover::before,
    .tooltip:hover::after {
        opacity: 1;
        visibility: visible;
    }
    
    /* Enhanced move styling */
    .moves-container {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid var(--type-color, #e2e8f0);
        border-radius: 16px;
        padding: 16px;
        margin-top: 16px;
        backdrop-filter: blur(10px);
    }
    
    .moves-title {
        font-size: clamp(14px, 3vw, 16px);
        font-weight: 700;
        color: #374151;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .move-item {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        padding: clamp(8px, 2vw, 16px) clamp(12px, 3vw, 16px);
        border-radius: clamp(8px, 2vw, 10px);
        margin: clamp(6px, 1.5vw, 8px) 0;
        font-size: clamp(12px, 3vw, 14px);
        font-weight: 600;
        color: #475569;
        border-left: 4px solid var(--type-color, #3b82f6);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        word-break: break-word;
    }
    
    .move-item::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.4) 50%, transparent 100%);
        transition: left 0.5s ease;
    }
    
    .move-item:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }
    
    .move-item:hover::before {
        left: 100%;
    }
    
    /* Enhanced scrollbar for translation */
    .summary-container::-webkit-scrollbar {
        width: clamp(6px, 1vw, 8px);
    }
    
    .summary-container::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 4px;
    }
    
    .summary-container::-webkit-scrollbar-thumb {
        background: var(--type-color, #3b82f6);
        border-radius: 4px;
    }
    
    .summary-container::-webkit-scrollbar-thumb:hover {
        background: var(--role-accent, var(--type-color, #2563eb));
    }
    
    /* Touch-friendly improvements */
    @media (hover: none) and (pointer: coarse) {
        .pokemon-card:hover {
            transform: none;
        }
        
        .ev-stat:hover {
            transform: none;
        }
        
        .info-item:hover {
            transform: none;
        }
        
        .move-item:hover {
            transform: none;
        }
        
        /* Increase touch targets */
        .pokemon-card {
            padding: clamp(20px, 5vw, 28px);
        }
        
        .info-item {
            min-height: 70px;
            padding: clamp(14px, 3vw, 18px);
        }
        
        .ev-stat {
            padding: clamp(12px, 3vw, 16px) clamp(8px, 2vw, 12px);
        }
    }
    
    /* Floating action effects */
    .pokemon-card {
        will-change: transform;
    }
    
    /* ========================================
       COMPREHENSIVE RESPONSIVE DESIGN
       ======================================== */
    
    /* Large Desktop (1200px+) - Enhanced layouts for wide screens */
    @media (min-width: 1200px) {
        .pokemon-info-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .ev-stats-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .pokemon-card {
            max-width: 1000px;
            margin: 12px auto;
        }
        
        .team-header h1 {
            font-size: clamp(2.5rem, 4vw, 3.5rem);
        }
    }
    
    /* Desktop/Tablet Landscape (900px - 1199px) - Optimal for half-screen */
    @media (max-width: 1199px) and (min-width: 900px) {
        .ev-stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        
        .pokemon-info-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        
        .pokemon-card {
            padding: 20px;
        }
        
        .team-header {
            padding: 28px;
        }
        
        .team-header h1 {
            font-size: clamp(2rem, 3.5vw, 2.5rem);
        }
    }
    
    /* Tablet Portrait / Small Desktop (600px - 899px) */
    @media (max-width: 899px) and (min-width: 600px) {
        .ev-stats-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .pokemon-info-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .ev-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
        }
        
        .ev-total {
            align-self: flex-end;
        }
        
        .pokemon-card {
            padding: 18px;
        }
        
        .pokemon-name {
            font-size: clamp(20px, 4vw, 24px);
        }
        
        .team-header {
            padding: 24px;
        }
        
        .team-header h1 {
            font-size: clamp(1.8rem, 5vw, 2.2rem);
        }
        
        .info-item {
            padding: 10px 14px;
        }
    }
    
    /* Large Mobile (480px - 599px) */
    @media (max-width: 599px) and (min-width: 480px) {
        .ev-stats-grid {
            grid-template-columns: 1fr;
            gap: 10px;
        }
        
        .pokemon-info-grid {
            grid-template-columns: 1fr;
            gap: 10px;
        }
        
        .ev-header {
            flex-direction: column;
            align-items: stretch;
            text-align: center;
        }
        
        .ev-stat {
            padding: 12px 8px;
        }
        
        .ev-stat-name {
            min-width: 40px;
            font-size: 11px;
        }
        
        .ev-stat-value {
            min-width: 32px;
            font-size: 13px;
        }
        
        .pokemon-card {
            padding: 16px;
            margin: 8px 0;
        }
        
        .pokemon-card:hover {
            transform: translateY(-4px) scale(1.01);
        }
        
        .pokemon-name {
            font-size: clamp(18px, 5vw, 22px);
        }
        
        .team-header {
            padding: 20px;
        }
        
        .team-header h1 {
            font-size: clamp(1.5rem, 6vw, 2rem);
        }
        
        .info-item {
            padding: 12px;
        }
        
        .info-label {
            font-size: 11px;
        }
        
        .info-value {
            font-size: 13px;
        }
    }
    
    /* Small Mobile (< 480px) */
    @media (max-width: 479px) {
        .ev-stats-grid {
            grid-template-columns: 1fr;
            gap: 8px;
        }
        
        .pokemon-info-grid {
            grid-template-columns: 1fr;
            gap: 8px;
        }
        
        .ev-header {
            flex-direction: column;
            align-items: stretch;
            text-align: center;
            gap: 12px;
        }
        
        .ev-title {
            font-size: 14px;
        }
        
        .ev-total {
            font-size: 12px;
            padding: 6px 10px;
        }
        
        .ev-stat {
            padding: 10px 6px;
            gap: 8px;
        }
        
        .ev-stat-icon {
            font-size: 16px;
            width: 20px;
        }
        
        .ev-stat-name {
            min-width: 35px;
            font-size: 10px;
        }
        
        .ev-stat-bar-container {
            height: 6px;
        }
        
        .ev-stat-value {
            min-width: 30px;
            font-size: 12px;
        }
        
        .pokemon-card {
            padding: 14px;
            margin: 6px 0;
            border-radius: 16px;
        }
        
        .pokemon-card:hover {
            transform: translateY(-2px) scale(1.005);
        }
        
        .pokemon-name {
            font-size: clamp(16px, 6vw, 20px);
            margin-bottom: 8px;
        }
        
        .team-header {
            padding: 18px;
            margin: 16px 0 24px 0;
        }
        
        .team-header h1 {
            font-size: clamp(1.3rem, 7vw, 1.8rem);
        }
        
        .team-header p {
            font-size: clamp(0.9rem, 4vw, 1rem);
        }
        
        .info-item {
            padding: 10px;
        }
        
        .info-label {
            font-size: 10px;
            font-weight: 700;
        }
        
        .info-value {
            font-size: 12px;
            line-height: 1.3;
        }
        
        .moves-container {
            padding: 12px;
        }
        
        .moves-title {
            font-size: 14px;
        }
        
        .move-item {
            padding: 8px 12px;
            font-size: 12px;
        }
    }
    
    /* Landscape orientation optimizations for mobile */
    @media (max-width: 899px) and (orientation: landscape) {
        .team-header {
            padding: clamp(16px, 3vw, 20px);
            margin: clamp(12px, 2vw, 16px) 0 clamp(16px, 3vw, 20px) 0;
        }
        
        .team-header h1 {
            font-size: clamp(1.5rem, 4vw, 1.8rem);
        }
        
        .pokemon-card {
            padding: clamp(14px, 3vw, 18px);
            margin: clamp(6px, 1vw, 8px) 0;
        }
        
        .pokemon-info-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: clamp(8px, 1.5vw, 10px);
        }
        
        .ev-stats-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: clamp(8px, 1.5vw, 10px);
        }
        
        .info-item {
            padding: clamp(8px, 2vw, 12px);
            min-height: 50px;
        }
        
        .ev-stat {
            padding: clamp(8px, 2vw, 10px) clamp(6px, 1vw, 8px);
            gap: clamp(6px, 1vw, 8px);
        }
    }
    
    /* Improved container flow */
    .stApp > div {
        max-width: 100%;
        overflow-x: hidden;
    }
    
    /* Better margin handling for small screens */
    @media (max-width: 480px) {
        .stApp {
            padding: 0 8px;
        }
    }
    .pokemon-name {
        font-size: clamp(20px, 5vw, 24px);
        font-weight: bold;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    .pokemon-info {
        font-size: clamp(13px, 3vw, 14px);
        line-height: 1.6;
    }
    .team-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: clamp(20px, 5vw, 32px);
        border-radius: clamp(12px, 3vw, 16px);
        text-align: center;
        margin: clamp(16px, 4vw, 24px) 0 clamp(24px, 6vw, 32px) 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    .team-header h1 {
        margin: 0 0 8px 0;
        font-size: clamp(2rem, 6vw, 2.5rem);
        font-weight: 700;
        line-height: 1.1;
    }
    .team-header p {
        margin: 0;
        font-size: clamp(1rem, 3vw, 1.1rem);
        opacity: 0.9;
        line-height: 1.4;
    }
    .ev-explanation {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        border-left: 4px solid #3b82f6;
        padding: 20px;
        margin: 16px 0;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        font-size: 14px;
        line-height: 1.6;
    }
    .main-section {
        margin: 32px 0;
    }
    .main-section h2 {
        color: #1e293b;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 24px;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    .url-input {
        border: 2px solid #007bff;
        border-radius: 8px;
    }
    .summary-container {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .summary-title {
        color: #1e293b;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .summary-content {
        color: #475569;
        font-size: 15px;
        line-height: 1.6;
        margin-bottom: 12px;
    }
    .strategy-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 20px;
    }
    .strategy-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .strategy-card-title {
        font-size: 16px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .strategy-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .strategy-item {
        background: #f1f5f9;
        padding: 10px 14px;
        border-radius: 8px;
        margin: 8px 0;
        color: #334155;
        font-size: 14px;
        border-left: 3px solid #3b82f6;
    }
    .meta-relevance {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        padding: 24px;
        margin-top: 24px;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
        font-size: 15px;
        line-height: 1.6;
    }
    .meta-relevance-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* EV Source Transparency Indicators */
    .ev-source-warning {
        margin-top: 12px;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        text-align: center;
        border: 1px solid;
    }
    
    .ev-source-default-calculated {
        background: rgba(255, 152, 0, 0.1);
        border-color: #ff9800;
        color: #e65100;
    }
    
    .ev-source-default-missing {
        background: rgba(244, 67, 54, 0.1);
        border-color: #f44336;
        color: #c62828;
    }
    
    .ev-source-default-invalid {
        background: rgba(156, 39, 176, 0.1);
        border-color: #9c27b0;
        color: #7b1fa2;
    }
    
    .ev-source-article {
        background: rgba(76, 175, 80, 0.1);
        border-color: #4caf50;
        color: #2e7d32;
    }
    
    .ev-container.has-warning {
        border-color: #ff9800;
        box-shadow: 0 4px 12px rgba(255, 152, 0, 0.2);
    }
</style>
""",
    unsafe_allow_html=True,
)


def safe_parse_ev_spread(ev_string: str) -> Tuple[Dict[str, int], str]:
    """Safe wrapper for parse_ev_spread that handles backwards compatibility

    Returns:
        tuple: (ev_dict, source) where source indicates data authenticity
    """
    try:
        result = parse_ev_spread(ev_string)
        if isinstance(result, tuple) and len(result) == 2:
            return result
        elif isinstance(result, dict):
            # Old format returned just the dict, assume it's from article
            return result, "article"
        else:
            # Unexpected format, return default
            return {
                "hp": 252,
                "atk": 0,
                "def": 4,
                "spa": 252,
                "spd": 0,
                "spe": 0,
            }, "default_missing"
    except Exception as e:
        # If parsing fails completely, return safe defaults
        return {
            "hp": 252,
            "atk": 0,
            "def": 4,
            "spa": 252,
            "spd": 0,
            "spe": 0,
        }, "default_missing"


def parse_ev_spread(ev_string: str) -> Tuple[Dict[str, int], str]:
    """Parse EV spread string into individual stat values, including Japanese formats

    Returns:
        tuple: (ev_dict, source) where source indicates data authenticity
    """
    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    ev_dict = {stat: 0 for stat in stat_names}

    if not ev_string or ev_string == "Not specified in article":
        return validate_and_fix_evs(ev_dict)

    try:
        import re

        # Handle standard format: "252/0/4/252/0/0"
        if "/" in ev_string and not any(
            c in ev_string
            for c in [
                "HP",
                "Atk",
                "Def",
                "SpA",
                "SpD",
                "Spe",
                "H",
                "A",
                "B",
                "C",
                "D",
                "S",
            ]
        ):
            values = [int(x.strip()) for x in ev_string.split("/")]
            # Early validation - if these look like calculated stats, skip parsing them
            if not is_calculated_stats(values[:6]):
                for i, value in enumerate(values[:6]):
                    if i < len(stat_names):
                        ev_dict[stat_names[i]] = value
                return ev_dict

        # Enhanced pattern matching for multiple formats
        patterns = {
            "hp": [
                r"(\d+)\s*HP",
                r"(\d+)\s*H(?![a-z])",  # H but not followed by lowercase (to avoid "Heavy")
                r"H(\d+)",
                r"(\d+)\s*(?:HP|ヒットポイント|体力)",
                r"HP\s*(\d+)",
                r"体力\s*(\d+)",
            ],
            "atk": [
                r"(\d+)\s*(?:Atk|Attack|A(?![a-z]))",
                r"(\d+)\s*(?:攻撃|こうげき)",
                r"A(\d+)",
                r"攻撃\s*(\d+)",
                r"(?:Atk|Attack)\s*(\d+)",
            ],
            "def": [
                r"(\d+)\s*(?:Def|Defense|B(?![a-z]))",
                r"(\d+)\s*(?:防御|ぼうぎょ)",
                r"B(\d+)",
                r"防御\s*(\d+)",
                r"(?:Def|Defense)\s*(\d+)",
            ],
            "spa": [
                r"(\d+)\s*(?:SpA|Sp\.?\s*A|Special\s*Attack|C(?![a-z]))",
                r"(\d+)\s*(?:特攻|とくこう|特殊攻撃)",
                r"C(\d+)",
                r"特攻\s*(\d+)",
                r"特殊攻撃\s*(\d+)",
                r"(?:SpA|Special\s*Attack)\s*(\d+)",
            ],
            "spd": [
                r"(\d+)\s*(?:SpD|Sp\.?\s*D|Special\s*Defense|D(?![a-z]))",
                r"(\d+)\s*(?:特防|とくぼう|特殊防御)",
                r"D(\d+)",
                r"特防\s*(\d+)",
                r"特殊防御\s*(\d+)",
                r"(?:SpD|Special\s*Defense)\s*(\d+)",
            ],
            "spe": [
                r"(\d+)\s*(?:Spe|Speed|S(?![a-z]))",
                r"(\d+)\s*(?:素早さ|すばやさ|速度)",
                r"S(\d+)",
                r"素早さ\s*(\d+)",
                r"速度\s*(\d+)",
                r"(?:Spe|Speed)\s*(\d+)",
            ],
        }

        # First check for calculated stats patterns (liberty-note.com format)
        # Pattern: H202, A205↑, B141, D106, S75 (comma-separated with nature indicators)
        calc_stats_patterns = [
            r"H(\d+),?\s*A(\d+)[↑↓]?,?\s*B(\d+),?\s*(?:C(\d+),?\s*)?D(\d+),?\s*S(\d+)",  # With nature indicators
            r"H(\d+),\s*A(\d+),\s*B(\d+),\s*D(\d+),\s*S(\d+)",  # Simple comma-separated (5 values, missing SpA)
            r"H(\d+),\s*A(\d+),\s*B(\d+),\s*C(\d+),\s*D(\d+),\s*S(\d+)",  # Simple comma-separated (6 values)
        ]

        for calc_pattern in calc_stats_patterns:
            calc_stats_match = re.search(calc_pattern, ev_string)
            if calc_stats_match:
                groups = calc_stats_match.groups()
                values = [int(g) if g else 0 for g in groups]
                # Insert 0 for missing SpA if pattern has only 5 values
                if len(values) == 5:  # Missing SpA
                    values.insert(3, 0)  # Insert 0 at position 3 (SpA)
                if is_calculated_stats(values):
                    # Don't return early - let validate_and_fix_evs handle the zeros
                    break  # Exit the pattern loop but continue to validation

        # Handle Japanese format with separators: H252-A0-B4-C252-D0-S0 or H252 A0 B4 C252 D0 S0
        japanese_format_patterns = [
            r"H(\d+)[-・\s]+A(\d+)[-・\s]+B(\d+)[-・\s]+C(\d+)[-・\s]+D(\d+)[-・\s]+S(\d+)",
            r"H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)",
            r"H(\d+)-A(\d+)-B(\d+)-C(\d+)-D(\d+)-S(\d+)",
            r"H(\d+)・A(\d+)・B(\d+)・C(\d+)・D(\d+)・S(\d+)",
            # Note.com specific patterns with extra spacing/formatting
            r"H\s*(\d+)\s*[-・\s]\s*A\s*(\d+)\s*[-・\s]\s*B\s*(\d+)\s*[-・\s]\s*C\s*(\d+)\s*[-・\s]\s*D\s*(\d+)\s*[-・\s]\s*S\s*(\d+)",
        ]

        for pattern in japanese_format_patterns:
            japanese_format_match = re.search(pattern, ev_string)
            if japanese_format_match:
                values = [int(x) for x in japanese_format_match.groups()]
                # Check if these are calculated stats instead of EVs
                if not is_calculated_stats(values):
                    for i, value in enumerate(values):
                        if i < len(stat_names):
                            ev_dict[stat_names[i]] = value
                    return ev_dict

        # Handle exact H/A/B/C/D/S pattern with word boundaries
        exact_pattern_match = re.search(
            r"\bH(\d+)\b.*?\bA(\d+)\b.*?\bB(\d+)\b.*?\bC(\d+)\b.*?\bD(\d+)\b.*?\bS(\d+)\b",
            ev_string,
        )
        if exact_pattern_match:
            values = [int(x) for x in exact_pattern_match.groups()]
            # Check if these are calculated stats instead of EVs
            if not is_calculated_stats(values):
                for i, value in enumerate(values):
                    if i < len(stat_names):
                        ev_dict[stat_names[i]] = value
                return ev_dict

        # Handle effort value prefix formats: 努力値: H252/A0/B4/C252/D0/S0
        effort_match = re.search(
            r"(?:努力値|EV|ev)[:：]\s*H(\d+)[-/・\s]A(\d+)[-/・\s]B(\d+)[-/・\s]C(\d+)[-/・\s]D(\d+)[-/・\s]S(\d+)",
            ev_string,
        )
        if effort_match:
            values = [int(x) for x in effort_match.groups()]
            # Even with EV prefix, validate the numbers
            if not is_calculated_stats(values):
                for i, value in enumerate(values):
                    if i < len(stat_names):
                        ev_dict[stat_names[i]] = value
                return ev_dict

        # Try all patterns for each stat
        for stat, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, ev_string, re.IGNORECASE)
                if match:
                    ev_dict[stat] = int(match.group(1))
                    break  # Use first match found for this stat

        # Handle Japanese descriptive format with mixed separators
        # Example: HP252・攻撃0・防御4・特攻252・特防0・素早さ0
        japanese_desc_patterns = [
            (r"HP(\d+)", "hp"),
            (r"攻撃(\d+)", "atk"),
            (r"防御(\d+)", "def"),
            (r"特攻(\d+)", "spa"),
            (r"特防(\d+)", "spd"),
            (r"素早さ(\d+)", "spe"),
            (r"体力(\d+)", "hp"),
            (r"こうげき(\d+)", "atk"),
            (r"ぼうぎょ(\d+)", "def"),
            (r"とくこう(\d+)", "spa"),
            (r"とくぼう(\d+)", "spd"),
            (r"すばやさ(\d+)", "spe"),
        ]

        for pattern, stat in japanese_desc_patterns:
            match = re.search(pattern, ev_string)
            if match:
                ev_dict[stat] = int(match.group(1))

    except:
        # If parsing fails, return zeros
        pass

    # Validate EV total and provide defaults if needed
    return validate_and_fix_evs(ev_dict)


def is_calculated_stats(numbers: List[int]) -> bool:
    """Detect if numbers appear to be calculated stats rather than EVs"""
    if not numbers or len(numbers) != 6:
        return False

    # Check for typical calculated stat patterns
    # Calculated stats are usually 100-400+ range at level 50
    # EVs are 0-252 per stat, total ≤508

    # If any individual stat is >252, it's likely calculated stats
    if any(num > 252 for num in numbers):
        return True

    # If total is way over 508, it's calculated stats
    total = sum(numbers)
    if total > 600:  # Much higher than max EV total
        return True

    # If all values are in typical calculated stat ranges (100-250)
    # and none are 0, 4, or other common EV values
    common_ev_values = {
        0,
        4,
        6,
        12,
        20,
        36,
        44,
        52,
        60,
        68,
        76,
        84,
        92,
        100,
        108,
        116,
        124,
        132,
        140,
        148,
        156,
        164,
        172,
        180,
        188,
        196,
        204,
        212,
        220,
        228,
        236,
        244,
        252,
    }
    uncommon_values = [
        num for num in numbers if num not in common_ev_values and num > 100
    ]

    # If most values are uncommon EV amounts and in calc stat range
    if len(uncommon_values) >= 4 and all(100 <= num <= 250 for num in uncommon_values):
        return True

    return False


def validate_and_fix_evs(ev_dict: Dict[str, int]) -> Tuple[Dict[str, int], str]:
    """Validate EV spread and provide reasonable defaults if incomplete

    Returns:
        tuple: (ev_dict, source) where source is one of:
        - 'article': EVs parsed from article content
        - 'default_calculated_stats': Default spread due to calculated stats detected
        - 'default_missing': Default spread due to missing/incomplete EVs
        - 'default_invalid': Default spread due to invalid EV total
    """
    values_list = list(ev_dict.values())

    # Check if these look like calculated stats instead of EVs
    if is_calculated_stats(values_list):
        # These appear to be calculated stats, not EVs
        # Return default competitive EV spread instead
        return {
            "hp": 252,
            "atk": 0,
            "def": 4,
            "spa": 252,
            "spd": 0,
            "spe": 0,
        }, "default_calculated_stats"

    total = sum(ev_dict.values())

    # If EVs total 0 or are clearly incomplete, provide reasonable defaults
    if total == 0:
        # Common competitive spread: 252/0/4/252/0/0 (HP/Atk/Def/SpA/SpD/Spe)
        return {
            "hp": 252,
            "atk": 0,
            "def": 4,
            "spa": 252,
            "spd": 0,
            "spe": 0,
        }, "default_missing"

    # If total is not 508 (max allowed), try to fix common issues
    if total != 508:
        # If close to 508, adjust the largest investment
        if 500 <= total <= 516:  # Close enough, minor adjustment needed
            diff = 508 - total
            # Find stat with largest investment to adjust
            max_stat = max(ev_dict.items(), key=lambda x: x[1])
            if max_stat[1] + diff >= 0:
                ev_dict[max_stat[0]] += diff
            return ev_dict, "article"  # Still from article, just adjusted

        # If significantly different, provide default
        elif total > 600 or total < 100:  # Clearly invalid
            return {
                "hp": 252,
                "atk": 0,
                "def": 4,
                "spa": 252,
                "spd": 0,
                "spe": 0,
            }, "default_invalid"

        # If moderately off but reasonable (partial data)
        else:
            return ev_dict, "article"  # Keep partial data from article

    # Valid total of 508, return as-is from article
    return ev_dict, "article"


def get_stat_icon(stat: str) -> str:
    """Get emoji icon for stat"""
    icons = {"hp": "❤️", "atk": "⚔️", "def": "🛡️", "spa": "🔮", "spd": "🔰", "spe": "⚡"}
    return icons.get(stat, "📊")


def get_pokemon_type_class(tera_type: str) -> str:
    """Get CSS class for Pokemon type"""
    if not tera_type or tera_type == "Not specified":
        return "type-normal"
    return f"type-{tera_type.lower()}"


def get_role_class(role: str) -> str:
    """Get CSS class for Pokemon role"""
    if not role or role == "Not specified":
        return "role-utility"

    role_lower = role.lower().replace(" ", "-")
    role_mappings = {
        "physical-attacker": "role-physical-attacker",
        "special-attacker": "role-special-attacker",
        "physical-wall": "role-physical-wall",
        "special-wall": "role-special-wall",
        "support": "role-support",
        "speed-control": "role-speed-control",
        "utility": "role-utility",
    }

    for key, class_name in role_mappings.items():
        if key in role_lower:
            return class_name

    return "role-utility"


def create_ev_visualization(ev_spread: str) -> str:
    """Create HTML for EV visualization with progress bars"""
    ev_dict, ev_source = safe_parse_ev_spread(ev_spread)
    total_evs = sum(ev_dict.values())

    # Check if total is reasonable (max 508)
    total_color = "#4CAF50" if total_evs <= 508 else "#FF5722"

    stats_html = ""
    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    stat_labels = ["HP", "ATK", "DEF", "SPA", "SPD", "SPE"]

    for i, stat in enumerate(stat_names):
        value = ev_dict[stat]
        percentage = min((value / 252) * 100, 100)  # Max 252 EVs per stat
        icon = get_stat_icon(stat)
        label = stat_labels[i]

        # Determine highlighting class based on EV investment
        if value == 0:
            investment_class = ""
        elif value >= 252:
            investment_class = "maxed has-evs"
        elif value >= 101:
            investment_class = "large-investment has-evs"
        elif value >= 32:
            investment_class = "medium-investment has-evs"
        else:  # 1-31 EVs (including 4 EVs)
            investment_class = "small-investment has-evs"
        # Escape quotes in tooltip text to prevent HTML issues
        tooltip_text = f"{label}: {value} EVs ({percentage:.1f}% of max)"
        if value >= 252:
            tooltip_text += " - MAXED OUT!"
        tooltip_text = tooltip_text.replace('"', "&quot;")

        stats_html += (
            f'<div class="ev-stat ev-{stat} {investment_class} tooltip" data-tooltip="{tooltip_text}">'
            f'<div class="ev-stat-icon">{icon}</div>'
            f'<div class="ev-stat-name">{label}</div>'
            f'<div class="ev-stat-bar-container">'
            f'<div class="ev-stat-bar" style="width: {percentage}%"></div>'
            f"</div>"
            f'<div class="ev-stat-value">{value}</div>'
            f"</div>"
        )

    # Create warning message based on EV source
    warning_html = ""
    container_class = "ev-container"

    if ev_source == "default_calculated_stats":
        warning_html = '<div class="ev-source-warning ev-source-default-calculated">⚠️ Default Spread - Calculated stats detected in article (NOT real EVs)</div>'
        container_class = "ev-container has-warning"
    elif ev_source == "default_missing":
        warning_html = '<div class="ev-source-warning ev-source-default-missing">⚠️ Default Spread - No EV data found in article</div>'
        container_class = "ev-container has-warning"
    elif ev_source == "default_invalid":
        warning_html = '<div class="ev-source-warning ev-source-default-invalid">⚠️ Default Spread - Invalid EV data in article</div>'
        container_class = "ev-container has-warning"
    elif ev_source == "article":
        warning_html = '<div class="ev-source-warning ev-source-article">✅ From Article - EV spread parsed from original content</div>'

    html = (
        f'<div class="{container_class}">'
        f'<div class="ev-header">'
        f'<div class="ev-title">📊 EV Spread</div>'
        f'<div class="ev-total" style="color: {total_color}; border-color: {total_color}">'
        f"{total_evs}/508 EVs"
        f"</div>"
        f"</div>"
        f'<div class="ev-stats-grid">'
        f"{stats_html}"
        f"</div>"
        f"{warning_html}"
        f"</div>"
    )

    return html


def format_moves_html(moves: List[str]) -> str:
    """Generate HTML for Pokemon moves"""
    if not moves:
        return '<div class="move-item">No moves specified</div>'

    move_html = ""
    for move in moves:
        if move and move != "Not specified in article":
            move_html += f'<div class="move-item">{move}</div>'

    return move_html if move_html else '<div class="move-item">No moves specified</div>'


def extract_images_from_url(url: str, max_images: int = 10) -> List[Dict[str, Any]]:
    """Extract images from webpage that might contain VGC data with note.com optimization"""
    images = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all images
        img_tags = soup.find_all("img")

        # Prioritize note.com team card images
        note_com_images = []
        other_images = []

        for img_tag in img_tags[: max_images * 2]:  # Check more images initially
            try:
                img_src = img_tag.get("src")
                if not img_src:
                    continue

                # Convert relative URLs to absolute
                img_url = urljoin(url, img_src)

                # Priority scoring for note.com team images
                is_note_com_asset = "assets.st-note.com" in img_url
                is_likely_team_card = False

                # Check for team card indicators in URL or context
                team_indicators = [
                    "team",
                    "pokemon",
                    "vgc",
                    "party",
                    "DvCIsNZXzyA2irhdlucjKOGR",
                ]
                url_lower = img_url.lower()
                alt_text = img_tag.get("alt", "").lower()
                title_text = img_tag.get("title", "").lower()

                for indicator in team_indicators:
                    if (
                        indicator.lower() in url_lower
                        or indicator in alt_text
                        or indicator in title_text
                    ):
                        is_likely_team_card = True
                        break

                # Skip very small images but be more lenient for note.com assets
                width = img_tag.get("width")
                height = img_tag.get("height")
                skip_small = False

                if width and height:
                    try:
                        w, h = int(width), int(height)
                        # For note.com assets, be more permissive
                        if is_note_com_asset:
                            if w < 300 or h < 200:  # More lenient for note.com
                                skip_small = True
                        else:
                            if w < 100 or h < 100:
                                skip_small = True
                    except:
                        pass

                if skip_small:
                    continue

                # Download and process image
                img_response = requests.get(img_url, headers=headers, timeout=15)
                if img_response.status_code == 200:
                    # Skip if too small in bytes (likely not a team card)
                    if len(img_response.content) < 5000:  # Less than 5KB
                        continue

                    # Convert to base64 for Gemini Vision
                    img_data = base64.b64encode(img_response.content).decode("utf-8")

                    # Get image info
                    try:
                        pil_img = Image.open(BytesIO(img_response.content))
                        img_format = pil_img.format
                        img_size = pil_img.size
                    except:
                        img_format = "unknown"
                        img_size = (0, 0)

                    image_info = {
                        "url": img_url,
                        "data": img_data,
                        "format": img_format,
                        "size": img_size,
                        "alt_text": img_tag.get("alt", ""),
                        "title": img_tag.get("title", ""),
                        "content_type": img_response.headers.get("content-type", ""),
                        "is_note_com_asset": is_note_com_asset,
                        "is_likely_team_card": is_likely_team_card,
                        "file_size": len(img_response.content),
                    }

                    # Prioritize note.com assets and likely team cards
                    if is_note_com_asset or is_likely_team_card:
                        note_com_images.append(image_info)
                    else:
                        other_images.append(image_info)

            except Exception as e:
                continue

        # Combine with priority: note.com assets first, then others
        priority_images = note_com_images + other_images
        images = priority_images[:max_images]

    except Exception as e:
        st.warning(f"Could not extract images: {str(e)}")

    return images


def is_potentially_vgc_image(image_info: Dict[str, Any]) -> bool:
    """Determine if an image might contain VGC-relevant data with note.com optimization"""
    # Priority 1: note.com assets are highly likely to be team cards
    if image_info.get("is_note_com_asset", False):
        # For note.com, any reasonably sized image is likely relevant
        width, height = image_info.get("size", (0, 0))
        file_size = image_info.get("file_size", 0)
        if width > 300 and height > 200 and file_size > 10000:  # 10KB+
            return True

    # Priority 2: Already flagged as likely team card
    if image_info.get("is_likely_team_card", False):
        return True

    # Check alt text and title for VGC keywords
    text_content = (
        image_info.get("alt_text", "") + " " + image_info.get("title", "")
    ).lower()

    vgc_keywords = [
        "pokemon",
        "team",
        "ev",
        "iv",
        "stats",
        "battle",
        "vgc",
        "party",
        "roster",
        "ポケモン",
        "チーム",
        "努力値",
        "個体値",
        "バトル",
        "パーティ",
        "構築",
        "育成論",
        "配分",
        "調整",
        "doubles",
        "tournament",
        "ranking",
    ]

    for keyword in vgc_keywords:
        if keyword in text_content:
            return True

    # Check image size - team cards tend to be larger and more rectangular
    width, height = image_info.get("size", (0, 0))
    file_size = image_info.get("file_size", 0)

    # Team summary cards tend to be:
    # - Wider than 600px and taller than 400px for full team displays
    # - Or smaller but still substantial (400x300+) for compact layouts
    if (width > 600 and height > 400) or (
        width > 400 and height > 300 and file_size > 20000
    ):
        return True

    # Check URL for VGC/Pokemon indicators
    url = image_info.get("url", "").lower()
    for keyword in vgc_keywords:
        if keyword in url:
            return True

    # Check file format - prefer PNG/JPEG for detailed team cards
    if image_info.get("format") in ["PNG", "JPEG", "JPG"] and file_size > 15000:
        return True

    return False


def encode_image_for_gemini(
    image_data: str, format_type: str = "jpeg"
) -> Dict[str, Any]:
    """Prepare image data for Gemini Vision API"""
    return {"mime_type": f"image/{format_type.lower()}", "data": image_data}


def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash for content to use as cache key"""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[
        :16
    ]  # Use first 16 chars for shorter keys


def ensure_cache_directory() -> str:
    """Create cache directory if it doesn't exist and return path"""
    cache_dir = os.path.join(os.getcwd(), "cache", "articles")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_cache_file_path(content_hash: str) -> str:
    """Get full path for cache file"""
    cache_dir = ensure_cache_directory()
    return os.path.join(cache_dir, f"{content_hash}.json")


def check_cache(content: str, url: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Check if content analysis exists in cache"""
    try:
        content_hash = generate_content_hash(content)
        cache_file = get_cache_file_path(content_hash)

        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if cache is still valid (optional: implement TTL)
            cache_timestamp = datetime.fromisoformat(
                cache_data.get("timestamp", "2000-01-01")
            )

            # Cache valid for 7 days (adjust as needed)
            if datetime.now() - cache_timestamp < timedelta(days=7):
                return cache_data.get("analysis_result")

        return None
    except Exception as e:
        # If cache read fails, return None (will trigger API call)
        return None


def save_to_cache(
    content: str, analysis_result: Dict[str, Any], url: Optional[str] = None
) -> None:
    """Save analysis result to cache"""
    try:
        content_hash = generate_content_hash(content)
        cache_file = get_cache_file_path(content_hash)

        cache_data = {
            "hash": content_hash,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "analysis_result": analysis_result,
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
        }

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        # If cache write fails, continue without caching (non-critical)
        pass


def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]

        total_size = 0
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            total_size += os.path.getsize(file_path)

        return {
            "cached_articles": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
    except:
        return {"cached_articles": 0, "total_size_mb": 0}


def clear_cache() -> bool:
    """Clear all cached articles"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]

        for file in cache_files:
            os.remove(os.path.join(cache_dir, file))

        return True
    except:
        return False


def format_strategy_list(items: List[str], list_type: str = "strength") -> str:
    """Generate HTML for strategy lists (strengths/weaknesses)"""
    if not items:
        return f'<div class="strategy-item">No {list_type}s specified</div>'

    html = ""
    for item in items:
        if item and item != "Not specified":
            html += f'<div class="strategy-item">{item}</div>'

    return (
        html if html else f'<div class="strategy-item">No {list_type}s specified</div>'
    )


def get_pokemon_sprite_url(pokemon_name: str) -> str:
    """Get Pokemon sprite URL from PokeAPI"""
    try:
        # Convert name to lowercase and handle special characters
        name = pokemon_name.lower().replace(" ", "-").replace("'", "").replace(".", "")

        # Handle Pokemon name variations and common mistranslations
        name_mapping = {
            # Common variations
            "nidoran-m": "nidoran-m",
            "nidoran-f": "nidoran-f",
            "mr-mime": "mr-mime",
            "farfetchd": "farfetchd",
            "ho-oh": "ho-oh",
            "jangmo-o": "jangmo-o",
            "hakamo-o": "hakamo-o",
            "kommo-o": "kommo-o",
            "tapu-koko": "tapu-koko",
            "tapu-lele": "tapu-lele",
            "tapu-bulu": "tapu-bulu",
            "tapu-fini": "tapu-fini",
            "type-null": "type-null",
            # Treasures of Ruin - Common mistranslations
            "chi-yu": "chi-yu",
            "chien-pao": "chien-pao",
            "ting-lu": "ting-lu",
            "wo-chien": "wo-chien",
            "pao-chien": "chien-pao",  # Common mistranslation
            "chien-pau": "chien-pao",  # Alternative spelling
            "chi-yu": "chi-yu",
            "ting-yu": "ting-lu",  # Common mistranslation
            "wo-chien": "wo-chien",
            # Paldean Pokemon
            "gimmighoul": "gimmighoul",
            "gholdengo": "gholdengo",
            "great-tusk": "great-tusk",
            "scream-tail": "scream-tail",
            "brute-bonnet": "brute-bonnet",
            "flutter-mane": "flutter-mane",
            "slither-wing": "slither-wing",
            "sandy-shocks": "sandy-shocks",
            "iron-treads": "iron-treads",
            "iron-bundle": "iron-bundle",
            "iron-hands": "iron-hands",
            "iron-jugulis": "iron-jugulis",
            "iron-moth": "iron-moth",
            "iron-thorns": "iron-thorns",
            "roaring-moon": "roaring-moon",
            "iron-valiant": "iron-valiant",
            "walking-wake": "walking-wake",
            "raging-bolt": "raging-bolt",
            "gouging-fire": "gouging-fire",
            "iron-leaves": "iron-leaves",
            "iron-boulder": "iron-boulder",
            "iron-crown": "iron-crown",
            # Legendary Pokemon
            "koraidon": "koraidon",
            "korraidon": "koraidon",  # Common misspelling
            "miraidon": "miraidon",
            "ogerpon": "ogerpon",
            "ogerpon-teal": "ogerpon-teal",
            "ogerpon-wellspring": "ogerpon-wellspring",
            "ogerpon-hearthflame": "ogerpon-hearthflame",
            "ogerpon-cornerstone": "ogerpon-cornerstone",
            "ogerpon-teal-mask": "ogerpon-teal",
            "ogerpon-wellspring-mask": "ogerpon-wellspring",
            "ogerpon-hearthflame-mask": "ogerpon-hearthflame",
            "ogerpon-cornerstone-mask": "ogerpon-cornerstone",
            "fezandipiti": "fezandipiti",
            "munkidori": "munkidori",
            "okidogi": "okidogi",
            "terapagos": "terapagos",
            # Regional forms
            "paldean-tauros": "tauros-paldea-combat",
            "paldean-wooper": "wooper-paldea",
            # Common misspellings and variations
            "incineroar": "incineroar",
            "inceneroar": "incineroar",  # Common misspelling
            "grimmsnarl": "grimmsnarl",
            "grimsnarl": "grimmsnarl",  # Common misspelling
            "landorus": "landorus-incarnate",
            "landorus-therian": "landorus-therian",
            "tornadus": "tornadus-incarnate",
            "tornadus-therian": "tornadus-therian",
            "thundurus": "thundurus-incarnate",
            "thundurus-therian": "thundurus-therian",
            # Generation IX Pokemon (Paldea)
            "kingambit": "kingambit",
            "baxcalibur": "baxcalibur",
            "bellibolt": "bellibolt",
            "pawmot": "pawmot",
            "squawkabilly": "squawkabilly",
            "armarouge": "armarouge",
            "ceruledge": "ceruledge",
            "flamigo": "flamigo",
            "clodsire": "clodsire",
            "arboliva": "arboliva",
            "palafin": "palafin",
            "veluza": "veluza",
            "dondozo": "dondozo",
            "tatsugiri": "tatsugiri",
            "cyclizar": "cyclizar",
            "bramblin": "bramblin",
            "brambleghast": "brambleghast",
            "gholdengo": "gholdengo",
            "gimmighoul": "gimmighoul",
            "garganacl": "garganacl",
            "tinkaton": "tinkaton",
            "tinkatu": "tinkatu",
            "tinkatuff": "tinkatuff",
            "tinkatu": "tinkatuff",  # Alternative spelling
            "annihilape": "annihilape",
            "camerupt": "camerupt",
            "dudunsparce": "dudunsparce",
            "kingambit": "kingambit",  # Critical fix for the main issue
            # Other common issues
            "mime-jr": "mime-jr",
            "porygon-z": "porygon-z",
            "porygon2": "porygon2",
        }

        api_name = name_mapping.get(name, name)

        # Get Pokemon data from PokeAPI
        response = requests.get(
            f"https://pokeapi.co/api/v2/pokemon/{api_name}", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data["sprites"]["front_default"]
        else:
            # Fallback to a default Pokemon image
            return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"

    except Exception:
        # Return a default Pokemon image on error
        return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"


class GeminiVGCAnalyzer:
    """Handles VGC article analysis using Google Gemini AI"""

    def __init__(self):
        self.api_key = self._get_api_key()
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            self.vision_model = genai.GenerativeModel(
                "gemini-2.0-flash-exp"
            )  # Same model handles vision
        else:
            st.error("⚠️ Google API key not found. Please set it in Streamlit secrets.")
            self.model = None
            self.vision_model = None

    def _get_api_key(self) -> Optional[str]:
        """Get API key from Streamlit secrets or environment"""
        try:
            return st.secrets.get("google_api_key") or os.getenv("GOOGLE_API_KEY")
        except:
            return os.getenv("GOOGLE_API_KEY")

    def scrape_article(self, url: str) -> Optional[str]:
        """Scrape article content from URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = "\n".join(line for line in lines if line)

            return text[:10000]  # Limit to first 10k characters

        except Exception as e:
            st.error(f"Error scraping article: {str(e)}")
            return None

    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible and appears to be a Pokemon/VGC article"""
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False

            # Check if URL is accessible
            response = requests.head(url, timeout=10)
            return response.status_code == 200

        except:
            return False

    def scrape_article_enhanced(
        self, url: str
    ) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Enhanced article scraping with image extraction and note.com handling"""
        try:
            # Extract images first
            images = extract_images_from_url(url)
            vgc_images = [img for img in images if is_potentially_vgc_image(img)]

            # Special handling for note.com articles
            if "note.com" in url:
                try:
                    content = self._scrape_note_com_article(url)
                    if content:
                        return content, vgc_images
                except Exception as e:
                    st.warning(f"note.com special handling failed: {str(e)}")

            # Enhanced text extraction with LangChain if available
            if LANGCHAIN_AVAILABLE:
                try:
                    loader = WebBaseLoader(url)
                    documents = loader.load()
                    if documents:
                        text_content = "\n".join(
                            [doc.page_content for doc in documents]
                        )
                        return (
                            text_content[:12000],
                            vgc_images,
                        )  # Increased limit for better content
                except Exception as e:
                    st.warning(f"LangChain extraction failed, using fallback: {str(e)}")

            # Fallback to original method
            content = self.scrape_article(url)
            return content, vgc_images

        except Exception as e:
            st.error(f"Enhanced scraping failed: {str(e)}")
            return None, []

    def _scrape_note_com_article(self, url: str) -> Optional[str]:
        """Specialized scraper for note.com articles"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for unwanted in soup(
                ["script", "style", "nav", "header", "footer", "aside", "noscript"]
            ):
                unwanted.decompose()

            # Try to find the main content area (note.com specific selectors)
            content_selectors = [
                # Modern note.com selectors
                '[data-testid="article-body"]',
                ".note-common-styles__textnote-body",
                ".p-article__body",
                ".note-body",
                "article",
                ".article-body",
                # Additional selectors for embedded content
                ".p-note__content",
                ".p-article__content-wrapper",
                ".c-article-body",
                ".note-content",
                # Fallback selectors
                "main",
                "#article-body",
            ]

            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if main_content:
                # Extract text while preserving structure
                text_content = main_content.get_text(separator="\n", strip=True)
            else:
                # Fallback to general content extraction
                text_content = soup.get_text(separator="\n", strip=True)

            # Clean up the text
            lines = []
            for line in text_content.splitlines():
                line = line.strip()
                if line and len(line) > 2:  # Skip very short lines
                    lines.append(line)

            final_content = "\n".join(lines)

            # Look for Pokemon-related sections specifically
            pokemon_keywords = [
                "ポケモン",
                "pokemon",
                "努力値",
                "EV",
                "チーム",
                "team",
                "パーティ",
                "party",
                "バトル",
                "battle",
                "ダブル",
                "double",
                "VGC",
                "vgc",
                "ランクバトル",
                "ranked",
                "トーナメント",
                "tournament",
                "シングル",
                "single",
                "ダブルバトル",
                "double battle",
                "反省",
                "reflection",
                "レート",
                "rating",
                "BO1",
                "BO3",
                "構築",
                "team building",
                "regulation",
                "series",
                "format",
            ]

            content_lower = final_content.lower()
            has_pokemon_content = any(
                keyword.lower() in content_lower for keyword in pokemon_keywords
            )

            # Enhanced extraction based on content relevance
            if has_pokemon_content:
                # Try to extract more content if it seems Pokemon-related
                return final_content[:15000]  # Increased limit for Pokemon content
            else:
                return final_content[:8000]  # Standard limit for general content

        except Exception as e:
            st.warning(f"note.com scraping error: {str(e)}")
            return None

    def analyze_images(self, images: List[Dict[str, Any]]) -> str:
        """Analyze images for VGC data using Gemini Vision"""
        if not self.vision_model or not images:
            return ""

        image_analysis_results = []

        for i, image in enumerate(
            images[:3]
        ):  # Limit to 3 images to avoid token limits
            try:
                st.info(f"🖼️ Analyzing image {i+1}/{min(len(images), 3)}...")

                # Prepare image for Gemini
                image_part = {
                    "mime_type": f'image/{image.get("format", "jpeg").lower()}',
                    "data": image["data"],
                }

                vision_prompt = """
                CRITICAL MISSION: Analyze this Pokemon VGC team image for COMPLETE EV spread extraction. This is likely a note.com team card format.

                **PRIMARY OBJECTIVE: EV SPREAD DETECTION**
                SCAN METHODICALLY for numerical EV patterns in these formats:
                - Standard: "252/0/4/252/0/0" or "252-0-4-252-0-0" (HP/Atk/Def/SpA/SpD/Spe)
                - Japanese: "H252 A0 B4 C252 D0 S0" or "ＨＰ252 こうげき0 ぼうぎょ4..."
                - Grid layout: Numbers in rows/columns next to stat abbreviations
                - Individual entries: "HP: 252", "Attack: 0", "Defense: 4"...
                - Compact: "252HP/4Def/252SpA" or "H252/B4/C252"
                - Note.com style: May use Japanese stat names with numbers

                **EV VALIDATION RULES:**
                - Total EVs must be ≤508 (if >508, these are likely actual stats, not EVs)
                - Valid individual values: 0, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252
                - Common patterns: 252/252/4, 252/0/0/252/4/0, 252/0/4/0/0/252

                **JAPANESE STAT TRANSLATIONS:**
                - ＨＰ/HP/H = HP
                - こうげき/攻撃/A = Attack  
                - ぼうぎょ/防御/B = Defense
                - とくこう/特攻/C = Special Attack
                - とくぼう/特防/D = Special Defense
                - すばやさ/素早/S = Speed

                **TEAM LAYOUT PARSING (Note.com Format):**
                1. Pokemon Name/Sprite (top of each card)
                2. Pokemon Types (colored type indicators)
                3. Ability (below name, before moves)
                4. Held Item (icon/text near sprite)
                5. Nature (stat arrows: ↑=boost, ↓=reduction)
                6. MOVES (exactly 4, listed vertically)
                7. **EV SPREAD** (most critical - look for number patterns)
                8. Tera Type (if shown)

                **EV EXTRACTION PRIORITY AREAS:**
                1. Dedicated EV section/table within each Pokemon card
                2. Numbers next to stat abbreviations (H/A/B/C/D/S)
                3. Small text below Pokemon data
                4. Side panels or secondary info areas
                5. Overlaid text on Pokemon cards
                6. Separate EV summary section

                **NATURE DETECTION - STAT ARROW ANALYSIS:**
                Look for colored arrows next to stat abbreviations:
                - RED/Pink arrows (↑) = stat INCREASE (+10%)
                - BLUE/Navy arrows (↓) = stat DECREASE (-10%)
                - Example: Blue "A" + Red "S" = Timid nature (-Attack, +Speed)

                **ITEM TRANSLATIONS (Japanese ↔ English):**
                - しんぴのしずく = Mystic Water, たべのこし = Leftovers
                - きあいのタスキ = Focus Sash, いのちのたま = Life Orb
                - こだわりハチマキ = Choice Band, こだわりメガネ = Choice Specs
                - こだわりスカーフ = Choice Scarf, とつげきチョッキ = Assault Vest
                - オボンのみ = Sitrus Berry, ラムのみ = Lum Berry

                **OUTPUT FORMAT (PRIORITY: EV SPREADS):**
                For each Pokemon, provide:
                ```
                POKEMON_1: [Name] | EV_SPREAD: [HP/Atk/Def/SpA/SpD/Spe] | ABILITY: [Ability] | ITEM: [Item] | NATURE: [Nature] | TERA: [Type] | MOVES: [Move1, Move2, Move3, Move4]
                POKEMON_2: [Name] | EV_SPREAD: [HP/Atk/Def/SpA/SpD/Spe] | ABILITY: [Ability] | ITEM: [Item] | NATURE: [Nature] | TERA: [Type] | MOVES: [Move1, Move2, Move3, Move4]
                [Continue for all Pokemon...]
                ```

                **CRITICAL SUCCESS CRITERIA:**
                - MUST extract EV spreads for ALL visible Pokemon
                - If EVs are partially visible, provide what you can see (e.g., "252/?/4/?/?/252")
                - If no EVs visible for a Pokemon, state "EV_SPREAD: Not visible in image"
                - Validate EV totals ≤508 and report any anomalies
                - Prioritize EV data extraction over all other information

                **SCAN METHODOLOGY:**
                1. First pass: Identify all Pokemon in the image
                2. Second pass: Focus EXCLUSIVELY on finding numerical EV patterns
                3. Third pass: Extract other Pokemon data (moves, items, abilities)
                4. Final validation: Confirm EV totals and format consistency

                **EV EXTRACTION VALIDATION:**
                EV_TOTALS: [Report total EVs for each Pokemon to verify ≤508]
                EV_COMPLETENESS: [Report which Pokemon have complete/incomplete EV data]
                EV_CONFIDENCE: [Rate confidence in EV extraction: High/Medium/Low for each Pokemon]
                PARSING_ERRORS: [Any issues with typing/ability confused as moves]
                EV_SPREAD_DATA: [All visible EV spreads, stat numbers, or effort value indicators]
                STAT_CALCULATIONS: [Any visible stat numbers that could indicate EV investments]
                ITEM_LOCATIONS: [Where items were visually positioned]
                IMAGE_TYPE: [team composition/battle screenshot/stats chart/other]
                LAYOUT_VALIDATION: [Confirm proper parsing order was followed: Name->Typing->Ability->Moves->Item]
                """

                response = self.vision_model.generate_content(
                    [vision_prompt, image_part]
                )
                if response and response.text:
                    image_analysis_results.append(
                        f"Image {i+1} Analysis:\n{response.text}\n"
                    )

            except Exception as e:
                st.warning(f"Could not analyze image {i+1}: {str(e)}")
                continue

        return "\n".join(image_analysis_results)

    def extract_ev_spreads_from_image_analysis(
        self, image_analysis: str
    ) -> Dict[str, str]:
        """Extract EV spreads from image analysis results"""
        ev_data = {}

        # Look for EV_SPREAD patterns in the image analysis
        import re

        # Pattern 1: POKEMON_X: Name | EV_SPREAD: HP/Atk/Def/SpA/SpD/Spe
        pattern1 = r"POKEMON_\d+:\s*([^|]+)\s*\|\s*EV_SPREAD:\s*([^|]+)"
        matches1 = re.findall(pattern1, image_analysis, re.IGNORECASE)

        for pokemon_name, ev_spread in matches1:
            pokemon_name = pokemon_name.strip()
            ev_spread = ev_spread.strip()
            if ev_spread and ev_spread != "Not visible in image":
                ev_data[pokemon_name] = ev_spread

        # Pattern 2: Look for direct EV spread mentions
        pattern2 = (
            r"([A-Za-z\s-]+).*?EV.*?(\d+[/\-]\d+[/\-]\d+[/\-]\d+[/\-]\d+[/\-]\d+)"
        )
        matches2 = re.findall(pattern2, image_analysis, re.IGNORECASE)

        for pokemon_name, ev_spread in matches2:
            pokemon_name = pokemon_name.strip()
            if pokemon_name and ev_spread:
                ev_data[pokemon_name] = ev_spread.replace("-", "/")

        # Pattern 3: Japanese format H252 A0 B4 etc.
        pattern3 = (
            r"([A-Za-z\s-]+).*?H(\d+)\s*A(\d+)\s*B(\d+)\s*C(\d+)\s*D(\d+)\s*S(\d+)"
        )
        matches3 = re.findall(pattern3, image_analysis, re.IGNORECASE)

        for match in matches3:
            pokemon_name = match[0].strip()
            ev_values = match[1:7]
            ev_spread = "/".join(ev_values)
            if pokemon_name and ev_spread:
                ev_data[pokemon_name] = ev_spread

        return ev_data

    def analyze_article(
        self,
        content: str,
        url: Optional[str] = None,
        images: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Analyze article content using Gemini AI with caching support and optional image analysis"""

        if not self.model:
            st.error("Gemini AI model not available")
            return None

        # Check cache first
        cached_result = check_cache(content, url)
        if cached_result:
            # Display cache hit indicator
            st.success("✅ Using cached analysis (no API call needed)")
            return cached_result

        # Analyze images if provided
        image_analysis = ""
        image_ev_data = {}
        if images and len(images) > 0:
            st.info(f"🖼️ Found {len(images)} potentially relevant images, analyzing...")
            image_analysis = self.analyze_images(images)
            if image_analysis:
                st.success(f"✅ Image analysis complete - extracted additional data!")
                # Extract EV spreads from image analysis
                image_ev_data = self.extract_ev_spreads_from_image_analysis(
                    image_analysis
                )
                if image_ev_data:
                    st.success(
                        f"🎯 Found EV spreads in images for {len(image_ev_data)} Pokemon!"
                    )

        # Combine text and image analysis
        combined_content = content
        if image_analysis:
            combined_content += f"\n\nIMAGE ANALYSIS RESULTS:\n{image_analysis}"

        # Enhanced multi-pass analysis prompt
        prompt = f"""
You are a professional Pokemon VGC (Video Game Championships) expert analyzer specializing in Japanese article translation and team analysis.

CRITICAL MISSION: Perform EXHAUSTIVE analysis to extract ALL Pokemon and EV data from this article.

ARTICLE CONTENT:
{combined_content[:12000]}

ANALYSIS METHODOLOGY:

🚨 CRITICAL POKEMON NAME TRANSLATION ALERT 🚨
- セグレイブ = "Baxcalibur" (Dragon/Ice, Generation IX) - NOT Glaceon!
- ドドゲザン = "Kingambit" (Dark/Steel, Generation IX) - NOT Glaceon!
- If you see these Japanese names, translate them correctly to avoid major errors!

**STEP 1: COMPREHENSIVE POKEMON DETECTION**
- Scan ENTIRE article for Pokemon names (Japanese and English)
- Check team lists, strategy sections, move descriptions, ability mentions
- Look for Pokemon in battle reports, example scenarios, comparisons
- Include Pokemon mentioned in passing or as counters/threats
- Cross-reference with moves/abilities to confirm Pokemon identity

**STEP 2: AGGRESSIVE EV DATA EXTRACTION**
- Search ALL text sections for numerical patterns that could be EVs
- Look in Pokemon descriptions, team summaries, separate EV sections
- Check battle calculations, stat references, benchmark mentions
- Scan for embedded tables, lists, or formatted stat data
- Include partial EV data even if incomplete

**STEP 3: IMAGE DATA INTEGRATION**
- If IMAGE ANALYSIS RESULTS are provided, prioritize visual data
- Combine Pokemon found in images with text-based detections
- Use image EV data to supplement or validate text-based EV spreads
- Cross-reference visual team compositions with article descriptions

**STEP 4: VGC REGULATION/FORMAT DETECTION & VALIDATION**
- Identify which VGC regulation this team is from (Regulation A through I)
- Look for regulation mentions, series numbers, or format references in the article
- Check article dates, tournament mentions, or specific format descriptions
- Validate Pokemon legality for the identified regulation
- Note any restricted Pokemon or format-specific rules
- Cross-reference team composition with regulation restrictions

**VGC REGULATION REFERENCE GUIDE (CRITICAL FOR ANALYSIS):**

**Regulation A (Dec 2022 - Jan 2023):**
- BANNED: All Legendaries, Paradox Pokemon, Treasures of Ruin, Koraidon, Miraidon
- ALLOWED: Only native Paldea Pokemon

**Regulation B (Feb - Mar 2023):**
- BANNED: All Legendaries, Treasures of Ruin, Koraidon, Miraidon
- ALLOWED: Paradox Pokemon introduced (Flutter Mane, Iron Bundle, etc.)

**Regulation C (Mar - May 2023):**
- BANNED: All Legendaries except Treasures of Ruin, Koraidon, Miraidon  
- ALLOWED: Treasures of Ruin (Chi-Yu, Chien-Pao, Ting-Lu, Wo-Chien)

**Regulation D (May 2023 - Jan 2024):**
- BANNED: Restricted Legendaries only
- ALLOWED: All Pokemon transferable via HOME (excluding restricted legends)
- KEY ADDITIONS: Incineroar, Rillaboom, Landorus-Therian, Tornadus, etc.

**Regulation E (Jan - Apr 2024):**
- BANNED: Restricted Legendaries only
- ALLOWED: All Pokemon + Teal Mask DLC Pokemon
- KEY ADDITIONS: Ogerpon forms, Bloodmoon Ursaluna, etc.

**Regulation F (Jan - Apr 2024):**
- BANNED: Restricted Legendaries only  
- ALLOWED: All Pokemon + Indigo Disk DLC Pokemon
- KEY ADDITIONS: Walking Wake, Raging Bolt, Gouging Fire, Iron Leaves, Iron Boulder, Iron Crown

**Regulation G (May - Aug 2024, Jan - Apr 2025):**
- BANNED: Mythical Pokemon only
- ALLOWED: ONE Restricted Legendary per team (Koraidon, Miraidon, Calyrex, etc.)
- FULL FORMAT: Most Pokemon available including all Legendaries

**Regulation H (Sep 2024 - Jan 2025) - "BACK TO BASICS":**
- BANNED: ALL Legendaries, ALL Paradox Pokemon, ALL Treasures of Ruin, Loyal Three
- SPECIFICALLY BANNED: Urshifu, Flutter Mane, Iron Bundle, Iron Hands, Chi-Yu, Chien-Pao, Ting-Lu, Wo-Chien, Ogerpon, Raging Bolt, Walking Wake, Gouging Fire, Iron Leaves, Iron Boulder, Iron Crown, Calyrex, Miraidon, Koraidon, Tornadus, Landorus, Thundurus, etc.
- ALLOWED: Only regular Pokemon (most restrictive format ever)

**Regulation I (May - Aug 2025):**
- BANNED: Mythical Pokemon only
- ALLOWED: TWO Restricted Legendaries per team (double restricted format)
- FULL FORMAT: Maximum Pokemon availability

**REGULATION-AWARE ANALYSIS REQUIREMENTS:**
1. **Identify Team Regulation**: Use article date, tournament context, or Pokemon composition
2. **Validate Pokemon Legality**: Flag any banned Pokemon for the identified regulation
3. **Provide Context**: Explain why certain threats aren't relevant (e.g., "Urshifu is banned in Regulation H")
4. **Meta Analysis**: Reference regulation-specific meta trends and viable strategies
5. **Threat Assessment**: Only mention legal threats for the regulation
6. **Historical Context**: Note if team was designed for a specific regulation era

**STEP 5: CONTEXTUAL DATA VALIDATION**
- Cross-reference Pokemon with their mentioned moves/abilities
- Validate EV totals and correct obvious errors (must total 508)
- Ensure exactly 4 moves per Pokemon (mandatory requirement)
- Infer missing team members from context clues
- Connect strategy descriptions to specific Pokemon
- Prioritize image data when conflicts exist between text and visual information

**STEP 6: DATA COMPLETENESS ENFORCEMENT (CRITICAL)**
- Every Pokemon MUST have exactly 4 moves (use "Unknown Move 1", "Unknown Move 2", etc. if needed)
- Every Pokemon MUST have an EV spread totaling 508 (use 252/0/4/252/0/0 as default if missing)
- Every Pokemon MUST have held_item, nature, ability (use "Unknown" if not specified)
- Validate all data completeness before output
- Flag any incomplete data and attempt to infer from context

**MOVE ENFORCEMENT RULES:**
- If fewer than 4 moves detected: Fill with "Unknown Move X" placeholders
- If more than 4 moves detected: Select the 4 most relevant/commonly used moves
- Cross-validate moves with Pokemon's type and role
- Prioritize image analysis move data over text when available

Provide your response in the following JSON format:
{{
    "title": "Translated article title (Japanese → English)",
    "summary": "Brief summary of the article's main points",
    "regulation_info": {{
        "regulation": "Regulation letter (A-I) or Unknown if not determinable",
        "format": "VGC format details and restrictions",
        "tournament_context": "Any specific tournament or ranking mentioned"
    }},
    "team_analysis": {{
        "strategy": "Overall team strategy and approach",
        "strengths": ["Team strength 1", "Team strength 2", "Team strength 3"],
        "weaknesses": ["Potential weakness 1", "Potential weakness 2"],
        "meta_relevance": "How this team fits in the current meta"
    }},
    "pokemon_team": [
        {{
            "name": "Pokemon name in English",
            "ability": "Ability name in English", 
            "held_item": "Item name in English",
            "tera_type": "Tera type in English",
            "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
            "ev_spread": "HP/Atk/Def/SpA/SpD/Spe format (e.g., 252/0/4/252/0/0) - ONLY if found in article. Use 'Not specified in article' if missing.",
            "nature": "Nature name in English",
            "role": "Role in the team (e.g., Physical Attacker, Special Wall, etc.)",
            "ev_explanation": "Detailed explanation of EV spread reasoning, including speed benchmarks, survival calculations, and strategic considerations mentioned in the article"
        }}
    ],
    "translated_content": "Full article translated to English, maintaining VGC terminology and strategic insights"
}}

CRITICAL POKEMON NAME TRANSLATION RULES:
**GENERATION IX POKEMON - JAPANESE NAME TRANSLATIONS (CRITICAL):**
- ドドゲザン → "Kingambit" (Dark/Steel, NOT Glaceon - common AI error!)
- セグレイブ → "Baxcalibur" (Dragon/Ice, NOT Glaceon - common AI error!)
- ハラバリー → "Bellibolt" (Electric)
- パーモット → "Pawmot" (Electric/Fighting)
- イキリンコ → "Squawkabilly" (Flying/Normal)
- グレンアルマ → "Armarouge" (Fire/Psychic)
- ソウブレイズ → "Ceruledge" (Fire/Ghost)
- カラミンゴ → "Flamigo" (Flying/Fighting)
- リククラゲ → "Clodsire" (Poison/Ground)
- オリーヴァ → "Arboliva" (Grass/Normal)
- イルカマン → "Palafin" (Water)
- ミガルーサ → "Veluza" (Water/Psychic)
- ヘイラッシャ → "Dondozo" (Water)
- シャリタツ → "Tatsugiri" (Dragon/Water)
- モトトカゲ → "Cyclizar" (Dragon/Normal)
- アノホラグサ → "Bramblin" (Grass/Ghost)
- アノクサ → "Brambleghast" (Grass/Ghost)
- ドロバンコ → "Sandygast" (Ghost/Ground)
- シロデスナ → "Palossand" (Ghost/Ground)
- キラフロル → "Florges" (Fairy)
- ドガース → "Koffing" (Poison)
- マタドガス → "Weezing" (Poison)
- デカヌチャン → "Tinkaton" (Fairy/Steel)
- カヌチャン → "Tinkaton" (Fairy/Steel)
- ナカヌチャン → "Tinkatu" (Fairy/Steel)
- カマスジョー → "Barraskewda" (Water)
- キョジオーン → "Garganacl" (Rock)
- ゴローン → "Graveler" (Rock/Ground)
- サーフゴー → "Gholdengo" (Steel/Ghost)
- コレクレー → "Gimmighoul" (Ghost)

**CRITICAL ICE-TYPE POKEMON DISAMBIGUATION (PREVENTS COMMON AI ERRORS):**
⚠️ セグレイブ (Seglaive) = "Baxcalibur" (Dragon/Ice, Generation IX pseudo-legendary)
⚠️ グレイシア (Gureishia) = "Glaceon" (Pure Ice, Eevee evolution from Generation IV)
⚠️ NEVER confuse these two Pokemon - they are completely different species!
⚠️ If you see セグレイブ in Japanese text, it is ALWAYS Baxcalibur, never Glaceon!

**TREASURES OF RUIN - COMMON MISTRANSLATIONS:**
- チイユウ/チーユー/Chi Yu → "Chi-Yu" (Fire/Dark, Beads of Ruin ability)
- パオジアン/パオチエン/Pao Chien → "Chien-Pao" (Ice/Dark, Sword of Ruin ability)
- ディンルー/Ting Yu → "Ting-Lu" (Dark/Ground, Vessel of Ruin ability)
- ウーラオス/Wo Chien → "Wo-Chien" (Dark/Grass, Tablets of Ruin ability)

**CRITICAL MOVE NAME TRANSLATIONS:**
**Electric-Type Move Translations (Critical for VGC):**
- 10まんボルト → "Thunderbolt" (standard 90 BP Electric move)
- じんらい → "Thunderclap" (Raging Bolt signature +1 priority move)
- かみなり → "Thunder" (120 BP, 70% accuracy Electric move)
- でんじは → "Thunder Wave" (status move, causes paralysis)
- ボルトチェンジ → "Volt Switch" (switching Electric move)
- ワイルドボルト → "Wild Charge" (physical Electric recoil move)

**Defensive Move Translations:**
- ニードルガード → "Spiky Shield" (Grass protect that damages contact)
- キングシールド → "King's Shield" (Steel protect that lowers Attack)
- まもる → "Protect" (standard protection move)
- みきり → "Detect" (Fighting-type protect equivalent)

**Common Move Translations:**
- バークアウト/Bark Out → "Snarl" (NOT Bark Out)
- いばる → "Swagger"  
- あまえる → "Baby-Doll Eyes"
- みがわり → "Substitute"
- このゆびとまれ → "Follow Me"
- いかりのまえば → "Super Fang"
- ねこだまし → "Fake Out"

**NATURE TRANSLATIONS (Critical for VGC):**
- ようき → "Jolly" (+Speed, -Special Attack)
- いじっぱり → "Adamant" (+Attack, -Special Attack)  
- おくびょう → "Timid" (+Speed, -Attack)
- ひかえめ → "Modest" (+Special Attack, -Attack)
- わんぱく → "Impish" (+Defense, -Special Attack)
- しんちょう → "Careful" (+Special Defense, -Special Attack)
- れいせい → "Quiet" (+Special Attack, -Speed)
- ゆうかん → "Brave" (+Attack, -Speed)

**ANCIENT PARADOX POKEMON IDENTIFICATION (CRITICAL - DLC Forms):**
- タケルライコ/Raging Bolt: Electric/Dragon, Protosynthesis ability, based on Raikou
- ウネルミナモ/Walking Wake: Water/Dragon, Protosynthesis ability, based on Suicune  
- グエンストーン/Gouging Fire: Fire/Fighting, Protosynthesis ability, based on Entei
- アラブルタケ/Great Tusk: Ground/Fighting, Protosynthesis ability, based on Donphan
- トドロクツキ/Roaring Moon: Dragon/Dark, Protosynthesis ability, based on Salamence
- ハバタクカミ/Flutter Mane: Ghost/Fairy, Protosynthesis ability, based on Misdreavus
- ウルガモス/Slither Wing: Bug/Fighting, Protosynthesis ability, based on Volcarona
- スナノケガワ/Sandy Shocks: Electric/Ground, Protosynthesis ability, based on Magneton
- アラマロス/Brute Bonnet: Grass/Dark, Protosynthesis ability, based on Amoonguss
- サケブシッポ/Scream Tail: Fairy/Psychic, Protosynthesis ability, based on Jigglypuff

**FUTURE PARADOX POKEMON IDENTIFICATION (Iron Series):**
- テツノカンムリ/Iron Crown: Steel/Psychic, Quark Drive ability, based on Cobalion
- テツノイワオ/Iron Boulder: Rock/Psychic, Quark Drive ability, based on Terrakion  
- テツノリーフ/Iron Leaves: Grass/Psychic, Quark Drive ability, based on Virizion
- テツノツツミ/Iron Bundle: Ice/Water, Quark Drive ability, based on Delibird
- テツノブジン/Iron Valiant: Fairy/Fighting, Quark Drive ability, based on Gardevoir/Gallade
- テツノカイナ/Iron Hands: Fighting/Electric, Quark Drive ability, based on Hariyama
- テツノドクガ/Iron Moth: Fire/Poison, Quark Drive ability, based on Volcarona
- テツノイワ/Iron Thorns: Rock/Electric, Quark Drive ability, based on Tyranitar
- テツノワダチ/Iron Treads: Ground/Steel, Quark Drive ability, based on Donphan
- テツノコウベ/Iron Jugulis: Dark/Flying, Quark Drive ability, based on Hydreigon

**CRITICAL WARNING - DLC PARADOX POKEMON CONFUSION:**
⚠️ NEVER confuse these similar Pokemon:
- タケルライコ = "Raging Bolt" (Electric/Dragon) ≠ ウネルミナモ "Walking Wake" (Water/Dragon)
- Both are Ancient forms but different types and based on different legendary beasts
- Raging Bolt has Electric moves (10まんボルト/Thunderbolt, じんらい/Thunderclap)
- Walking Wake has Water moves (ハイドロポンプ/Hydro Pump, しおまき/Flip Turn)

**OGERPON FORM IDENTIFICATION (Critical - Mask Forms):**
- いしずえのめん/Cornerstone Mask → "Ogerpon-Cornerstone" (Grass/Rock, Tera Rock, Sturdy ability)
- みどりのめん/Teal Mask → "Ogerpon-Teal" (Grass, Tera Grass, Defiant ability)
- いどのめん/Wellspring Mask → "Ogerpon-Wellspring" (Grass/Water, Tera Water, Water Absorb ability)
- かまどのめん/Hearthflame Mask → "Ogerpon-Hearthflame" (Grass/Fire, Tera Fire, Mold Breaker ability)
- オーガポン → "Ogerpon" (base form identification)

**ABILITY TRANSLATIONS (Critical for Paradox Pokemon):**
- こだいかっせい/古代活性 → "Protosynthesis" (Ancient Paradox ability)
- クォークチャージ → "Quark Drive" (Future Paradox ability)

**OTHER COMMON MISTRANSLATIONS:**
- Use official English spellings: "Calyrex-Shadow", "Zamazenta", "Urshifu", "Regieleki"
- Paldean forms: "Iron Valiant", "Roaring Moon", "Flutter Mane", "Iron Bundle"
- Always use hyphens for compound names: "Tapu-Koko", "Ultra-Necrozma", "Necrozma-Dusk-Mane"

**CRITICAL EV PARSING GUIDELINES:**

⚠️ **CALCULATED STATS vs EV SPREADS WARNING** ⚠️
**NEVER confuse calculated stats with EV spreads:**
- Calculated stats: H202, A205↑, B141, D106, S75 (actual in-game stats at level 50)
- EV spreads: H252, A0, B4, C252, D0, S0 (effort value investments 0-252)
- If numbers look like calculated stats (>252 individual values, or unusual ranges like 141, 205), REJECT and mark as "Not specified in article"

**TRANSPARENCY REQUIREMENT:**
- If no EV data found: Use "Not specified in article" (application will show appropriate warnings)
- If calculated stats detected: Use "Not specified in article" (application will warn users about default spreads)
- If incomplete EV data: Include what you found, even if partial

**Japanese EV Format Recognition (REAL EVs ONLY):**
- H252-A0-B4-C252-D0-S0 (H=HP, A=Attack, B=Defense, C=Special Attack, D=Special Defense, S=Speed)
- 努力値: H252/A0/B4/C252/D0/S0 (effort value prefix)
- HP252・攻撃0・防御4・特攻252・特防0・素早さ0 (full Japanese names)
- HP252 攻撃0 防御4 特攻252 特防0 素早さ0 (space separated)
- H252 A0 B4 C252 D0 S0 (simple abbreviation)

**ENHANCED EV DETECTION PATTERNS:**
1. **Direct EV Patterns**: H252, HP252, 攻撃252, A252, etc.
2. **Table/List Formats**: 
   - Vertical: HP 252, Atk 0, Def 4...
   - Horizontal: 252/0/4/252/0/0
   - Mixed: HP252 A0 B4 C252 D0 S0
3. **Embedded in Text**: "HP252振り", "攻撃252", "素早さ4"
4. **Battle Calc References**: "252振りで〜耐え", "最速252"
5. **Stat Benchmark Context**: "調整ライン", "実数値", specific speed/damage calculations

**COMPREHENSIVE EV EXTRACTION RULES:**
1. **Search Everywhere**: Pokemon sections, team summary, battle examples, calculations
2. **Number Recognition**: Any 6-number sequence that sums to ≤508 could be EVs
   ⚠️ **REJECT sequences with individual values >252 or totals >600 (these are calculated stats)**
3. **Context Clues**: Numbers near stat names, in Pokemon descriptions, adjustment explanations
4. **Partial Data**: Even incomplete EV info is valuable (e.g., "HP252振り" = at least HP has 252)
5. **Validation Priority**: When in doubt, use default EV spread rather than incorrect calculated stats
6. **Japanese Stat Mapping**: 
   - HP/体力/ヒットポイント/H → HP
   - 攻撃/こうげき/物理/A → Attack  
   - 防御/ぼうぎょ/物理耐久/B → Defense
   - 特攻/とくこう/特殊攻撃/特殊/C → Special Attack
   - 特防/とくぼう/特殊防御/特殊耐久/D → Special Defense
   - 素早さ/すばやさ/速度/S → Speed

**FALLBACK EV DETECTION:**
- If no standard EV format found, look for ANY numerical sequences
- Check stat calculations and damage calculations for embedded EV hints
- Look for phrases like "振り分け", "調整", "努力値配分"
- Extract from battle examples: "○○の攻撃を〜で耐える" (specific EV requirements)

**ENHANCED POKEMON RECOGNITION:**
- **Context Scanning**: Pokemon mentioned in move descriptions (e.g., "ランドロスの地震" = Landorus)
- **Ability References**: "威嚇" (Intimidate) → likely Landorus, Incineroar, etc.
- **Type Context**: "炎タイプ" + specific moves → identify Pokemon
- **Nickname Patterns**: Common Japanese nicknames for Pokemon
- **Strategy Context**: Pokemon mentioned as counters, threats, or synergies
- **Battle Examples**: Pokemon in damage calculations or scenario descriptions

**CRITICAL POKEMON IDENTIFICATION RULES:**
- **Incineroar vs Grimmsnarl Confusion Prevention**:
  - Incineroar (ガオガエン): Fire/Dark, Intimidate ability, learns Fake Out, Flare Blitz, U-turn
  - Grimmsnarl (ブリムオン): Fairy/Dark, Prankster ability, learns Thunder Wave, Reflect, Light Screen
  - If "威嚇" (Intimidate) mentioned → likely Incineroar (NOT Grimmsnarl)
  - If "いたずらごころ" (Prankster) mentioned → Grimmsnarl (NOT Incineroar)
  - If Fire-type moves mentioned → Incineroar
  - If support moves like Light Screen/Reflect → Grimmsnarl

**CRITICAL EXTRACTION REQUIREMENTS:**
1. **MAXIMUM EFFORT**: Extract EVERY possible Pokemon and EV data point
2. **Incomplete Data OK**: Partial EVs better than missing EVs
3. **Context Priority**: Even mentions of Pokemon in strategy count
4. **Multiple Sources**: Combine data from different article sections
5. **Confidence Scoring**: Note uncertainty when data is ambiguous

ENHANCED GUIDELINES:
1. **Pokemon Names**: Use ONLY official English Pokemon names. Expand search beyond team lists.
2. **Pokemon-Move Validation**: CRITICALLY IMPORTANT - Verify Pokemon can learn detected moves
   - If Iron Crown detected but has Dark/Flying moves → Change to Iron Jugulis
   - If "Bark Out" detected → Translate to "Snarl" and verify Pokemon compatibility
   - Cross-reference ALL moves with Pokemon learnsets for accuracy
3. **EV Spreads**: Extract from ANY source - tables, text, calculations, examples
4. **Data Completeness**: Prefer incomplete accurate data over "Not specified"
5. **EV Context**: Include reasoning from damage calcs, speed tiers, survival rates
6. **Team Expansion**: Include Pokemon mentioned as techs, alternatives, or meta threats
7. **Strategic Context**: Connect Pokemon roles to broader team strategy
8. **Numerical Validation**: Cross-check EV totals and flag inconsistencies
9. **Format Flexibility**: Handle non-standard article structures
10. **Type Consistency**: Ensure Pokemon types match detected moves/abilities

**TEAM VALIDATION REQUIREMENTS:**
- **NO DUPLICATE POKEMON**: Each Pokemon should appear exactly once in the team
- **Team Size**: Exactly 6 Pokemon (use "Unknown Pokemon" if fewer detected)
- **Cross-Reference Check**: Verify Pokemon names against sprites, moves, and abilities
- **Spelling Consistency**: Use official English Pokemon names only

**FINAL VERIFICATION CHECKLIST:**
✓ All Pokemon mentioned in article identified (not just team members)
✓ EV data extracted from ALL possible sources (text, calcs, examples)
✓ Partial data included rather than marked as "Not specified"
✓ Context preserved for ambiguous information
✓ Japanese terminology properly converted to English
✓ Strategic connections between Pokemon and team roles established
✓ **CRITICAL**: Pokemon-move compatibility verified (Iron Crown vs Iron Jugulis checked)
✓ **CRITICAL**: Move names correctly translated (Bark Out → Snarl)
✓ **CRITICAL**: Pokemon types match detected moves and abilities
✓ **CRITICAL**: Paradox Pokemon correctly distinguished by moveset/type
✓ **CRITICAL**: No duplicate Pokemon in team (each Pokemon appears exactly once)
✓ **CRITICAL**: Incineroar vs Grimmsnarl properly distinguished by abilities and moves

Respond only with the JSON, no additional text.
"""

        # Display API call indicator
        st.info("🔄 Analyzing with Gemini AI...")

        try:
            response = self.model.generate_content(prompt)
            if response and response.text:
                # Clean response text
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()

                result = json.loads(response_text)

                # Integrate image-extracted EV data with the analysis result
                if image_ev_data and result.get("pokemon_team"):
                    st.info("🔄 Integrating EV data from images...")

                    for pokemon in result["pokemon_team"]:
                        pokemon_name = pokemon.get("name", "")

                        # Try to find matching EV data from images
                        for img_pokemon_name, img_ev_spread in image_ev_data.items():
                            # Match by exact name or partial match
                            if (
                                pokemon_name.lower() in img_pokemon_name.lower()
                                or img_pokemon_name.lower() in pokemon_name.lower()
                            ):

                                # Validate EV format
                                try:
                                    ev_values = [
                                        int(x.strip()) for x in img_ev_spread.split("/")
                                    ]
                                    if len(ev_values) == 6 and sum(ev_values) <= 508:
                                        pokemon["ev_spread"] = img_ev_spread
                                        pokemon["ev_source"] = "image_extracted"
                                        st.success(
                                            f"✅ Updated {pokemon_name} with image EV data: {img_ev_spread}"
                                        )
                                        break
                                except:
                                    continue

                # Save to cache for future use
                save_to_cache(content, result, url)
                st.success("🆕 Analysis complete and cached!")

                return result
            else:
                st.error("No response from Gemini AI")
                return None

        except json.JSONDecodeError as e:
            st.error(f"Failed to parse AI response: {e}")
            return None
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            return None


def format_evs_for_pokepaste(ev_dict: Dict[str, int]) -> str:
    """Format EV dictionary into standard pokepaste format"""
    # Standard pokepaste stat order and abbreviations
    stat_order = [
        ("hp", "HP"),
        ("atk", "Atk"),
        ("def", "Def"),
        ("spa", "SpA"),
        ("spd", "SpD"),
        ("spe", "Spe"),
    ]

    # Collect non-zero EVs
    ev_parts = []
    for stat_key, stat_name in stat_order:
        if ev_dict.get(stat_key, 0) > 0:
            ev_parts.append(f"{ev_dict[stat_key]} {stat_name}")

    # Join with " / " separator as per pokepaste standard
    if ev_parts:
        return " / ".join(ev_parts)
    else:
        # Default spread if no EVs specified
        return "252 HP / 252 SpA / 4 SpD"


def create_pokepaste(
    pokemon_team: List[Dict[str, Any]], team_name: str = "VGC Team"
) -> str:
    """Generate clean pokepaste format for the team"""
    pokepaste_content = ""

    # Check if any Pokemon have default EVs to add disclaimer
    has_default_evs = False
    for pokemon in pokemon_team:
        if (
            pokemon.get("ev_spread")
            and pokemon["ev_spread"] != "Not specified in article"
        ):
            _, ev_source = safe_parse_ev_spread(pokemon["ev_spread"])
            if ev_source.startswith("default"):
                has_default_evs = True
                break

    if has_default_evs:
        pokepaste_content += f"// {team_name} - DISCLAIMER: Some EV spreads are defaults (not from article)\n"
        pokepaste_content += "// Check comments on individual Pokemon for details\n\n"

    for pokemon in pokemon_team:
        if not pokemon.get("name") or pokemon["name"] == "Not specified in article":
            continue

        # Pokemon name and held item
        pokepaste_content += f"{pokemon['name']}"
        if (
            pokemon.get("held_item")
            and pokemon["held_item"] != "Not specified in article"
        ):
            pokepaste_content += f" @ {pokemon['held_item']}"
        pokepaste_content += "\n"

        # Ability
        if pokemon.get("ability") and pokemon["ability"] != "Not specified in article":
            pokepaste_content += f"Ability: {pokemon['ability']}\n"

        # Tera Type
        if (
            pokemon.get("tera_type")
            and pokemon["tera_type"] != "Not specified in article"
        ):
            pokepaste_content += f"Tera Type: {pokemon['tera_type']}\n"

        # EVs (format: HP / Atk / Def / SpA / SpD / Spe)
        if (
            pokemon.get("ev_spread")
            and pokemon["ev_spread"] != "Not specified in article"
        ):
            # Parse the raw EV string and format it properly
            ev_dict, ev_source = safe_parse_ev_spread(pokemon["ev_spread"])
            formatted_evs = format_evs_for_pokepaste(ev_dict)

            if ev_source.startswith("default"):
                # Add disclaimer for default spreads
                if ev_source == "default_calculated_stats":
                    pokepaste_content += f"EVs: {formatted_evs}  // WARNING: Default spread - calculated stats detected in article\n"
                elif ev_source == "default_missing":
                    pokepaste_content += f"EVs: {formatted_evs}  // WARNING: Default spread - no EV data in article\n"
                elif ev_source == "default_invalid":
                    pokepaste_content += f"EVs: {formatted_evs}  // WARNING: Default spread - invalid EV data in article\n"
                else:
                    pokepaste_content += (
                        f"EVs: {formatted_evs}  // WARNING: Default spread applied\n"
                    )
            else:
                pokepaste_content += f"EVs: {formatted_evs}\n"

        # Nature
        if pokemon.get("nature") and pokemon["nature"] != "Not specified in article":
            pokepaste_content += f"{pokemon['nature']} Nature\n"

        # Moves
        if pokemon.get("moves"):
            for move in pokemon["moves"]:
                if move and move != "Not specified in article":
                    pokepaste_content += f"- {move}\n"

        pokepaste_content += "\n"

    return pokepaste_content


def render_team_strategy_section(
    team_analysis: Dict[str, Any], result: Dict[str, Any] = None
) -> None:
    """Render team strategy section with proper HTML"""
    st.markdown("### 🎯 Team Strategy")

    # Regulation information
    regulation_info = result.get("regulation_info", {}) if result else {}
    if regulation_info and regulation_info.get("regulation") != "Unknown":
        regulation = regulation_info.get("regulation", "Unknown")
        format_desc = regulation_info.get("format", "Not specified")
        tournament_context = regulation_info.get("tournament_context", "")

        st.markdown("#### 🏆 VGC Format Information")

        reg_color = {
            "A": "#FF6B6B",
            "B": "#4ECDC4",
            "C": "#45B7D1",
            "D": "#96CEB4",
            "E": "#FFEAA7",
            "F": "#DDA0DD",
            "G": "#98D8C8",
            "H": "#F7DC6F",
            "I": "#BB8FCE",
        }.get(regulation, "#95A5A6")

        st.markdown(
            f"""
        <div class="regulation-container" style="background: linear-gradient(135deg, {reg_color}20, {reg_color}10); border-left: 4px solid {reg_color}; padding: 15px; margin: 10px 0; border-radius: 8px;">
            <div style="font-weight: bold; color: {reg_color}; font-size: 1.1em;">
                📋 Regulation {regulation}
            </div>
            <div style="margin-top: 5px; color: #444;">
                {format_desc}
            </div>
            {f'<div style="margin-top: 5px; font-size: 0.9em; color: #666;"><strong>Tournament:</strong> {tournament_context}</div>' if tournament_context else ""}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Strategy overview
    strategy = team_analysis.get("strategy", "Not specified")
    st.markdown(
        f"""
    <div class="summary-container">
        <div class="summary-content">
            <strong>Overall Strategy:</strong><br>
            {strategy}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Strengths and Weaknesses in columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💪 Strengths")
        strengths = team_analysis.get("strengths", [])
        if strengths:
            for strength in strengths:
                if strength and strength != "Not specified":
                    st.markdown(
                        f"""
                    <div class="strategy-item">
                        {strength}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="strategy-item">No strengths specified</div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown("#### ⚠️ Weaknesses")
        weaknesses = team_analysis.get("weaknesses", [])
        if weaknesses:
            for weakness in weaknesses:
                if weakness and weakness != "Not specified":
                    st.markdown(
                        f"""
                    <div class="strategy-item">
                        {weakness}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
        else:
            st.markdown(
                '<div class="strategy-item">No weaknesses specified</div>',
                unsafe_allow_html=True,
            )

    # Meta relevance
    st.markdown("#### 🌟 Meta Relevance")
    meta_relevance = team_analysis.get("meta_relevance", "Not specified")
    st.markdown(
        f"""
    <div class="meta-relevance">
        {meta_relevance}
    </div>
    """,
        unsafe_allow_html=True,
    )


def get_cached_articles() -> List[Dict[str, Any]]:
    """Get list of all cached articles with metadata"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".json")]

        articles = []
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                articles.append(cache_data)
            except:
                continue

        # Sort by timestamp (newest first)
        articles.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return articles
    except:
        return []


def delete_cached_article(content_hash: str) -> bool:
    """Delete a specific cached article"""
    try:
        cache_file = get_cache_file_path(content_hash)
        if os.path.exists(cache_file):
            os.remove(cache_file)
            return True
        return False
    except:
        return False


def render_new_analysis_page():
    """Render the new analysis page (original functionality)"""
    # Header
    st.markdown(
        '<div class="team-header"><h1>⚔️ Pokemon VGC Article Analyzer</h1><p>Analyze Japanese VGC articles, showcase teams, and download results</p></div>',
        unsafe_allow_html=True,
    )

    # Initialize analyzer
    analyzer = GeminiVGCAnalyzer()

    # Main content area - Article Input Section
    st.markdown("## 📝 Article Analysis")

    # Input section in main area instead of sidebar
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        url = st.text_input(
            "Japanese VGC Article URL",
            placeholder="https://example.com/vgc-article",
            help="Enter the URL of a Japanese Pokemon VGC article",
        )

    with col2:
        # Cache status in header
        cache_stats = get_cache_stats()
        st.metric(
            "Cache",
            f"{cache_stats['cached_articles']} articles ({cache_stats['total_size_mb']} MB)",
        )

    with col3:
        if st.button(
            "🗑️ Clear", help="Clear cache", disabled=cache_stats["cached_articles"] == 0
        ):
            if clear_cache():
                st.success("Cache cleared!")
                st.rerun()

    # Manual text input
    manual_text = st.text_area(
        "Or paste Japanese article content directly:",
        height=150,
        placeholder="Paste Japanese article content here...",
    )

    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            enable_image_analysis = st.checkbox(
                "🖼️ Enable Image Analysis",
                value=True,
                help="Extract and analyze images from articles for additional Pokemon/EV data",
            )
        with col2:
            enable_langchain = st.checkbox(
                "🔗 Enhanced Text Extraction",
                value=LANGCHAIN_AVAILABLE,
                disabled=not LANGCHAIN_AVAILABLE,
                help="Use LangChain for better content extraction (requires additional dependencies)",
            )

    # Analyze button (disabled during processing)
    is_processing = st.session_state.get("is_processing", False)
    if st.button(
        "🔍 Analyze Article",
        type="primary",
        use_container_width=True,
        disabled=is_processing,
    ):
        if url or manual_text:
            # Set processing state
            st.session_state["is_processing"] = True
            with st.spinner("Analyzing article..."):
                content = None

                if url:
                    if analyzer.validate_url(url):
                        if enable_image_analysis:
                            # Use enhanced scraping with image extraction
                            content, images = analyzer.scrape_article_enhanced(url)
                            if images:
                                st.info(
                                    f"📸 Found {len(images)} images that may contain VGC data"
                                )
                        else:
                            # Use standard scraping without images
                            content = analyzer.scrape_article(url)
                            images = []
                    else:
                        st.error("Invalid or inaccessible URL")
                        content, images = None, []
                elif manual_text:
                    content = manual_text
                    images = []

                if content:
                    # Store content and trigger analysis (with or without images)
                    st.session_state["article_content"] = content
                    analysis_images = images if enable_image_analysis else []
                    st.session_state["analysis_result"] = analyzer.analyze_article(
                        content, url, analysis_images
                    )
                    # Clear processing state
                    st.session_state["is_processing"] = False
                    st.rerun()
                else:
                    st.error("Unable to extract content from the provided source")
                    # Clear processing state on error
                    st.session_state["is_processing"] = False
        else:
            st.warning("Please provide either a URL or paste article text")
            # Clear processing state if no input provided
            st.session_state["is_processing"] = False

    # Results Section
    if "analysis_result" in st.session_state and st.session_state["analysis_result"]:
        st.divider()
        result = st.session_state["analysis_result"]

        # Section 1: Article Summary
        st.markdown("## 📖 Article Summary")

        # Article title and summary
        title = result.get("title", "Article Title")
        summary = result.get("summary", "No summary available")

        st.markdown(
            f"""
        <div class="summary-container">
            <h3 style="color: #1e293b; margin-bottom: 16px;">{title}</h3>
            <div class="summary-content">{summary}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Section 2: Team Strategy Analysis
        if "team_analysis" in result:
            render_team_strategy_section(result["team_analysis"], result)
            st.divider()

        # Section 3: Downloads Section
        st.markdown("## 📥 Export & Downloads")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Translated article download
            if result.get("translated_content"):
                translated_text = f"Title: {result.get('title', 'VGC Article')}\n\n"
                translated_text += f"Summary: {result.get('summary', '')}\n\n"
                translated_text += f"Full Translation:\n{result['translated_content']}"

                st.download_button(
                    label="📄 Download Translation",
                    data=translated_text,
                    file_name="vgc_article_translation.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        with col2:
            # Pokepaste download
            if result.get("pokemon_team"):
                try:
                    pokepaste_content = create_pokepaste(
                        result["pokemon_team"], result.get("title", "VGC Team")
                    )
                except Exception as e:
                    st.error(f"Error creating pokepaste: {str(e)}")
                    pokepaste_content = f"// Error generating pokepaste: {str(e)}\n// Please try analyzing the article again"

                st.download_button(
                    label="🎮 Download Pokepaste",
                    data=pokepaste_content,
                    file_name="vgc_team_pokepaste.txt",
                    mime="text/plain",
                    use_container_width=True,
                )

        with col3:
            # Full translation view toggle
            if result.get("translated_content"):
                if st.button("📖 View Full Translation", use_container_width=True):
                    st.session_state["show_translation"] = not st.session_state.get(
                        "show_translation", False
                    )

        # Full Translation Section (read-only)
        if st.session_state.get("show_translation", False) and result.get(
            "translated_content"
        ):
            st.divider()
            st.markdown("## 📖 Full Article Translation")
            st.markdown(
                f"""
            <div class="summary-container" style="max-height: 400px; overflow-y: auto;">
                <div class="summary-content" style="white-space: pre-wrap; line-height: 1.6;">
                    {result['translated_content']}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Section 4: Team Showcase
        if result.get("pokemon_team"):
            st.markdown("## 🌟 Team Showcase")

            pokemon_team = result["pokemon_team"]

            # Create rows of 3 Pokemon each
            for i in range(0, len(pokemon_team), 3):
                cols = st.columns(3)

                for j, col in enumerate(cols):
                    if i + j < len(pokemon_team):
                        pokemon = pokemon_team[i + j]

                        with col:
                            if (
                                pokemon.get("name")
                                and pokemon["name"] != "Not specified in article"
                            ):
                                # Get Pokemon sprite
                                sprite_url = get_pokemon_sprite_url(pokemon["name"])

                                # Display Pokemon sprite
                                try:
                                    st.image(
                                        sprite_url, width=120, caption=pokemon["name"]
                                    )
                                except:
                                    st.markdown(f"**{pokemon['name']}**")

                                # Get styling classes
                                type_class = get_pokemon_type_class(
                                    pokemon.get("tera_type", "")
                                )
                                role_class = get_role_class(pokemon.get("role", ""))

                                # Pokemon basic info
                                st.markdown(
                                    f"""
                                <div class="pokemon-card {type_class} {role_class}">
                                    <div class="pokemon-info-grid">
                                        <div class="info-item">
                                            <div class="info-label">🎭 Role</div>
                                            <div class="info-value">{pokemon.get('role', 'Not specified')}</div>
                                        </div>
                                        <div class="info-item">
                                            <div class="info-label">⚡ Ability</div>
                                            <div class="info-value">{pokemon.get('ability', 'Not specified')}</div>
                                        </div>
                                        <div class="info-item">
                                            <div class="info-label">🎒 Held Item</div>
                                            <div class="info-value">{pokemon.get('held_item', 'Not specified')}</div>
                                        </div>
                                        <div class="info-item">
                                            <div class="info-label">💎 Tera Type</div>
                                            <div class="info-value">{pokemon.get('tera_type', 'Not specified')}</div>
                                        </div>
                                        <div class="info-item">
                                            <div class="info-label">🧬 Nature</div>
                                            <div class="info-value">{pokemon.get('nature', 'Not specified')}</div>
                                        </div>
                                    </div>
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                                # Enhanced EV Visualization
                                ev_spread = pokemon.get("ev_spread", "Not specified")
                                if ev_spread and ev_spread != "Not specified":
                                    try:
                                        st.markdown(
                                            create_ev_visualization(ev_spread),
                                            unsafe_allow_html=True,
                                        )
                                    except Exception as e:
                                        st.error(
                                            f"Error displaying EV spread: {str(e)}"
                                        )
                                        # Show basic fallback
                                        st.markdown(
                                            "⚠️ EV spread could not be displayed - using default competitive spread"
                                        )

                                # Moves section (separate to avoid HTML nesting issues)
                                st.markdown("**🎯 Moves:**")
                                moves = pokemon.get("moves", [])
                                if moves:
                                    for move in moves:
                                        if move and move != "Not specified in article":
                                            st.markdown(
                                                f"""
                                            <div class="move-item">
                                                {move}
                                            </div>
                                            """,
                                                unsafe_allow_html=True,
                                            )
                                else:
                                    st.markdown(
                                        '<div class="move-item">No moves specified</div>',
                                        unsafe_allow_html=True,
                                    )

                                # EV Explanation
                                if (
                                    pokemon.get("ev_explanation")
                                    and pokemon["ev_explanation"]
                                    != "Not specified in article"
                                ):
                                    with st.expander("📊 EV Strategy Details"):
                                        st.markdown(
                                            f'<div class="ev-explanation">{pokemon["ev_explanation"]}</div>',
                                            unsafe_allow_html=True,
                                        )

    else:
        # Welcome/instruction content
        st.markdown(
            """
        ## Welcome to the Pokemon VGC Article Analyzer! 🎮
        
        This tool helps you:
        - **Analyze Japanese VGC articles** with AI-powered translation
        - **Showcase Pokemon teams** with beautiful, clean layouts
        - **Understand EV strategies** with detailed explanations
        - **Download results** as text files and pokepaste format
        
        ### How to use:
        1. 📝 **Enter a Japanese VGC article URL** in the sidebar
        2. 🔍 **Click "Analyze Article"** to process the content
        3. 🌟 **View your team showcase** with detailed breakdowns
        4. 📥 **Download** translation and pokepaste files
        
        ### Features:
        - ✅ **Accurate translations** of Pokemon names, moves, and abilities
        - ✅ **EV spread analysis** with strategic explanations
        - ✅ **Team synergy insights** and meta relevance
        - ✅ **Clean, professional layouts** for team presentation
        - ✅ **Export functionality** for sharing and importing teams
        
        Ready to analyze your first article? Enter a URL above to get started! 🚀
        """
        )


def render_previous_articles_page():
    """Render the previously searched articles page"""
    st.markdown(
        '<div class="team-header"><h1>📚 Previously Searched Articles</h1><p>Browse and reload your cached VGC article analyses</p></div>',
        unsafe_allow_html=True,
    )

    # Get cached articles
    cached_articles = get_cached_articles()

    if not cached_articles:
        st.markdown(
            """
        ## No Articles Found 🔍
        
        You haven't analyzed any articles yet. Go to the **New Analysis** page to start analyzing Japanese VGC articles.
        
        Once you analyze articles, they'll appear here for quick access without needing to re-process them.
        """
        )
        return

    # Search and filter controls
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search articles",
            placeholder="Search by title, Pokemon names, or URL...",
        )

    with col2:
        sort_option = st.selectbox(
            "📅 Sort by", ["Newest First", "Oldest First", "Title A-Z"]
        )

    with col3:
        st.metric("Total Articles", len(cached_articles))

    # Filter articles based on search
    filtered_articles = cached_articles
    if search_query:
        search_lower = search_query.lower()
        filtered_articles = []
        for article in cached_articles:
            # Search in title, URL, and Pokemon names
            searchable_text = ""
            searchable_text += (
                article.get("analysis_result", {}).get("title", "").lower()
            )
            searchable_text += article.get("url", "").lower()
            searchable_text += article.get("content_preview", "").lower()

            # Search in Pokemon names
            pokemon_team = article.get("analysis_result", {}).get("pokemon_team", [])
            for pokemon in pokemon_team:
                searchable_text += pokemon.get("name", "").lower()

            if search_lower in searchable_text:
                filtered_articles.append(article)

    # Sort articles
    if sort_option == "Oldest First":
        filtered_articles.sort(key=lambda x: x.get("timestamp", ""))
    elif sort_option == "Title A-Z":
        filtered_articles.sort(
            key=lambda x: x.get("analysis_result", {}).get("title", "").lower()
        )

    st.markdown(f"## 📖 Articles ({len(filtered_articles)} found)")

    # Display articles
    for i, article in enumerate(filtered_articles):
        analysis_result = article.get("analysis_result", {})
        title = analysis_result.get("title", "Untitled Article")
        summary = analysis_result.get("summary", "No summary available")
        timestamp = article.get("timestamp", "")
        url = article.get("url", "No URL")
        pokemon_team = analysis_result.get("pokemon_team", [])

        # Format timestamp
        try:
            from datetime import datetime

            parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = timestamp

        # Create article card
        with st.container():
            st.markdown(
                f"""
            <div class="summary-container" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <h3 style="color: #1e293b; margin: 0; flex: 1;">{title}</h3>
                    <div style="color: #64748b; font-size: 14px; margin-left: 16px;">
                        {formatted_time}
                    </div>
                </div>
                <div class="summary-content" style="margin-bottom: 16px;">
                    {summary[:200]}{"..." if len(summary) > 200 else ""}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Pokemon team preview
            if pokemon_team:
                cols = st.columns(min(len(pokemon_team), 6))
                for j, pokemon in enumerate(pokemon_team[:6]):
                    if j < len(cols):
                        with cols[j]:
                            if (
                                pokemon.get("name")
                                and pokemon["name"] != "Not specified in article"
                            ):
                                sprite_url = get_pokemon_sprite_url(pokemon["name"])
                                try:
                                    st.image(
                                        sprite_url, width=60, caption=pokemon["name"]
                                    )
                                except:
                                    st.markdown(f"**{pokemon['name']}**")

            # Action buttons
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                if st.button(f"📖 View Analysis", key=f"view_{i}"):
                    # Load this analysis into session state and switch to new analysis page
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["article_content"] = article.get(
                        "content_preview", ""
                    )
                    st.session_state["current_page"] = "New Analysis"
                    st.rerun()

            with col2:
                if analysis_result.get("translated_content"):
                    translated_text = f"Title: {title}\n\nSummary: {summary}\n\nFull Translation:\n{analysis_result['translated_content']}"
                    st.download_button(
                        label="📄 Download Translation",
                        data=translated_text,
                        file_name=f"translation_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_trans_{i}",
                    )

            with col3:
                if pokemon_team:
                    try:
                        pokepaste_content = create_pokepaste(pokemon_team, title)
                    except Exception as e:
                        st.error(f"Error creating pokepaste: {str(e)}")
                        pokepaste_content = f"// Error generating pokepaste: {str(e)}\n// Please try re-analyzing the article"

                    st.download_button(
                        label="🎮 Download Pokepaste",
                        data=pokepaste_content,
                        file_name=f"team_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_paste_{i}",
                    )

            with col4:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this article"):
                    if delete_cached_article(article.get("hash", "")):
                        st.success("Article deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete article")

            st.divider()


def render_team_database_page():
    """Render the team database page"""
    st.markdown(
        '<div class="team-header"><h1>🏆 Team Database</h1><p>Browse and manage saved VGC teams</p></div>',
        unsafe_allow_html=True,
    )

    if not DATABASE_AVAILABLE:
        st.error(
            "Database functionality is not available. Please install required dependencies."
        )
        return

    # Initialize database
    try:
        init_database()
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        return

    # Search and filter controls
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        search_query = st.text_input(
            "🔍 Search teams",
            placeholder="Search by team name, Pokemon, or regulation...",
        )

    with col2:
        regulation_filter = st.selectbox(
            "🏅 Regulation", ["All", "A", "B", "C", "D", "E"]
        )

    with col3:
        if st.button("📊 Database Stats"):
            try:
                stats = TeamCRUD.get_team_statistics()
                st.metric("Total Teams", stats["total_teams"])
                st.metric("Total Pokemon", stats["total_pokemon"])

                if stats["popular_pokemon"]:
                    st.write("**Most Popular Pokemon:**")
                    for pokemon, count in list(stats["popular_pokemon"].items())[:5]:
                        st.write(f"• {pokemon}: {count} teams")
            except Exception as e:
                st.error(f"Failed to load stats: {e}")

    # Get teams from database
    try:
        if search_query or regulation_filter != "All":
            teams = TeamCRUD.search_teams(
                query=search_query,
                regulation=regulation_filter if regulation_filter != "All" else "",
                limit=50,
            )
        else:
            teams = TeamCRUD.get_all_teams(limit=50)

        st.markdown(f"## 📖 Teams ({len(teams)} found)")

        if not teams:
            st.info(
                "No teams found. Teams will appear here after you analyze articles."
            )

            # Add button to save current analysis if available
            if (
                "analysis_result" in st.session_state
                and st.session_state["analysis_result"]
            ):
                st.markdown("### Save Current Analysis")
                if st.button("💾 Save Current Team to Database"):
                    try:
                        saved_team = TeamCRUD.create_team_from_analysis(
                            st.session_state["analysis_result"]
                        )
                        st.success(f"Team '{saved_team.name}' saved to database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save team: {e}")
            return

        # Display teams
        for team in teams:
            with st.container():
                st.markdown(
                    f"""
                <div class="summary-container" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <h3 style="color: #1e293b; margin: 0; flex: 1;">{team.name}</h3>
                        <div style="color: #64748b; font-size: 14px; margin-left: 16px;">
                            {team.regulation if team.regulation else 'No Regulation'} | {team.created_at.strftime('%Y-%m-%d')}
                        </div>
                    </div>
                    <div class="summary-content" style="margin-bottom: 16px;">
                        {team.strategy_summary[:200] if team.strategy_summary else 'No strategy summary'}{"..." if team.strategy_summary and len(team.strategy_summary) > 200 else ""}
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Show Pokemon team
                if team.pokemon:
                    cols = st.columns(min(len(team.pokemon), 6))
                    for j, pokemon in enumerate(team.pokemon[:6]):
                        if j < len(cols):
                            with cols[j]:
                                sprite_url = get_pokemon_sprite_url(pokemon.name)
                                try:
                                    st.image(sprite_url, width=60, caption=pokemon.name)
                                except:
                                    st.markdown(f"**{pokemon.name}**")

                # Action buttons
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    if st.button(f"📊 View Details", key=f"view_team_{team.id}"):
                        st.session_state[f"show_team_details_{team.id}"] = (
                            not st.session_state.get(
                                f"show_team_details_{team.id}", False
                            )
                        )
                        st.rerun()

                with col2:
                    if st.button(f"📋 Compare", key=f"compare_team_{team.id}"):
                        if "comparison_teams" not in st.session_state:
                            st.session_state["comparison_teams"] = []
                        if team.id not in st.session_state["comparison_teams"]:
                            st.session_state["comparison_teams"].append(team.id)
                            st.success(f"Added {team.name} to comparison!")
                        else:
                            st.info("Team already in comparison list")

                with col3:
                    if st.button("🗑️", key=f"delete_team_{team.id}", help="Delete team"):
                        if TeamCRUD.delete_team(team.id):
                            st.success("Team deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete team")

                # Show details if expanded
                if st.session_state.get(f"show_team_details_{team.id}", False):
                    st.markdown("### Team Details")
                    for pokemon in team.pokemon:
                        with st.expander(
                            f"{pokemon.name} - {pokemon.role if pokemon.role else 'No role specified'}"
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(
                                    f"**Ability:** {pokemon.ability if pokemon.ability else 'Not specified'}"
                                )
                                st.write(
                                    f"**Item:** {pokemon.held_item if pokemon.held_item else 'Not specified'}"
                                )
                                st.write(
                                    f"**Nature:** {pokemon.nature if pokemon.nature else 'Not specified'}"
                                )
                                st.write(
                                    f"**Tera Type:** {pokemon.tera_type if pokemon.tera_type else 'Not specified'}"
                                )
                            with col2:
                                ev_spread = f"{pokemon.hp_ev}/{pokemon.atk_ev}/{pokemon.def_ev}/{pokemon.spa_ev}/{pokemon.spd_ev}/{pokemon.spe_ev}"
                                st.write(f"**EV Spread:** {ev_spread}")
                                if pokemon.moves:
                                    st.write(f"**Moves:** {', '.join(pokemon.moves)}")
                                if pokemon.ev_explanation:
                                    st.write(
                                        f"**EV Explanation:** {pokemon.ev_explanation}"
                                    )

                st.divider()

    except Exception as e:
        st.error(f"Failed to load teams: {e}")


def render_team_comparison_page():
    """Render the team comparison page"""
    st.markdown(
        '<div class="team-header"><h1>⚔️ Team Comparison</h1><p>Compare teams side-by-side</p></div>',
        unsafe_allow_html=True,
    )

    if not DATABASE_AVAILABLE:
        st.error(
            "Database functionality is not available. Please install required dependencies."
        )
        return

    # Get comparison teams from session state
    comparison_teams = st.session_state.get("comparison_teams", [])

    if len(comparison_teams) < 2:
        st.info(
            "Add teams to comparison from the Team Database page to start comparing."
        )

        # Show available teams for quick selection
        try:
            teams = TeamCRUD.get_all_teams(limit=20)
            if teams:
                st.markdown("### Quick Team Selection")
                cols = st.columns(2)
                for i, team in enumerate(teams[:10]):
                    with cols[i % 2]:
                        if st.button(f"Add {team.name}", key=f"quick_add_{team.id}"):
                            if "comparison_teams" not in st.session_state:
                                st.session_state["comparison_teams"] = []
                            if team.id not in st.session_state["comparison_teams"]:
                                st.session_state["comparison_teams"].append(team.id)
                                st.success(f"Added {team.name} to comparison!")
                                st.rerun()
        except Exception as e:
            st.error(f"Failed to load teams: {e}")
        return

    # Load team details
    teams_data = []
    for team_id in comparison_teams:
        try:
            team = TeamCRUD.get_team_by_id(team_id)
            if team:
                teams_data.append(team)
        except Exception as e:
            st.error(f"Failed to load team {team_id}: {e}")

    if not teams_data:
        st.error("Failed to load comparison teams")
        return

    # Comparison controls
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Comparing {len(teams_data)} teams**")
    with col2:
        if st.button("🗑️ Clear Comparison"):
            st.session_state["comparison_teams"] = []
            st.rerun()

    # Side-by-side comparison
    cols = st.columns(len(teams_data))

    for i, team in enumerate(teams_data):
        with cols[i]:
            st.markdown(f"### {team.name}")
            st.markdown(
                f"**Regulation:** {team.regulation if team.regulation else 'None'}"
            )
            st.markdown(
                f"**Archetype:** {team.archetype if team.archetype else 'Not specified'}"
            )

            # Team overview
            if team.strategy_summary:
                with st.expander("Strategy Summary"):
                    st.write(team.strategy_summary)

            # Pokemon list
            st.markdown("**Team Members:**")
            for pokemon in team.pokemon:
                with st.expander(f"{pokemon.name}"):
                    st.write(
                        f"Role: {pokemon.role if pokemon.role else 'Not specified'}"
                    )
                    st.write(
                        f"Ability: {pokemon.ability if pokemon.ability else 'Not specified'}"
                    )
                    st.write(
                        f"Item: {pokemon.held_item if pokemon.held_item else 'Not specified'}"
                    )
                    ev_spread = f"{pokemon.hp_ev}/{pokemon.atk_ev}/{pokemon.def_ev}/{pokemon.spa_ev}/{pokemon.spd_ev}/{pokemon.spe_ev}"
                    st.write(f"EVs: {ev_spread}")
                    if pokemon.moves:
                        st.write(f"Moves: {', '.join(pokemon.moves)}")

            # Remove from comparison
            if st.button(f"Remove {team.name}", key=f"remove_{team.id}"):
                st.session_state["comparison_teams"].remove(team.id)
                st.rerun()

    # Analysis section
    st.markdown("## 📊 Comparison Analysis")

    # Type coverage analysis
    st.markdown("### Type Coverage")
    type_coverage = {}
    for team in teams_data:
        team_types = set()
        for pokemon in team.pokemon:
            # This would need Pokemon type data - simplified for now
            team_types.add(pokemon.name)  # Placeholder
        type_coverage[team.name] = len(team_types)

    # Speed tier analysis
    if len(teams_data) >= 2:
        st.markdown("### Speed Comparison")
        try:
            for team in teams_data:
                team_speeds = []
                for pokemon in team.pokemon:
                    # Calculate speed stat (simplified)
                    if pokemon.spe_ev is not None:
                        base_speed = SpeedTierAnalyzer.VGC_POKEMON_BASE_SPEEDS.get(
                            pokemon.name, 80
                        )
                        nature_mod = (
                            1.1
                            if pokemon.nature and "speed" in pokemon.nature.lower()
                            else 1.0
                        )
                        speed_stat = SpeedTierAnalyzer.calculate_speed_stat(
                            base_speed, ev=pokemon.spe_ev, nature_modifier=nature_mod
                        )
                        team_speeds.append((pokemon.name, speed_stat))

                if team_speeds:
                    analysis = SpeedTierAnalyzer.generate_team_speed_analysis(
                        team_speeds
                    )
                    st.write(
                        f"**{team.name}** - Average Speed Coverage: {analysis['average_outspeed']}%"
                    )

        except Exception as e:
            st.error(f"Speed analysis failed: {e}")


def render_damage_calculator_page():
    """Render the damage calculator page"""
    st.markdown(
        '<div class="team-header"><h1>🧮 Damage Calculator</h1><p>Calculate damage for VGC scenarios</p></div>',
        unsafe_allow_html=True,
    )

    if not DATABASE_AVAILABLE:
        st.error(
            "Database functionality is not available. Please install required dependencies."
        )
        return

    # Calculator interface
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Attacker")
        attacker_name = st.selectbox(
            "Pokemon",
            list(DamageCalculator.COMMON_POKEMON_STATS.keys()),
            key="attacker_pokemon",
        )

        attacker_stats_dict = DamageCalculator.COMMON_POKEMON_STATS[attacker_name]

        # EV inputs
        st.markdown("**EV Spread:**")
        att_col1, att_col2, att_col3 = st.columns(3)
        with att_col1:
            hp_ev = st.number_input("HP", 0, 252, 0, 4, key="att_hp_ev")
            atk_ev = st.number_input("Atk", 0, 252, 252, 4, key="att_atk_ev")
        with att_col2:
            def_ev = st.number_input("Def", 0, 252, 0, 4, key="att_def_ev")
            spa_ev = st.number_input("SpA", 0, 252, 0, 4, key="att_spa_ev")
        with att_col3:
            spd_ev = st.number_input("SpD", 0, 252, 0, 4, key="att_spd_ev")
            spe_ev = st.number_input("Spe", 0, 252, 0, 4, key="att_spe_ev")

        # Calculate actual stats
        nature_modifier = st.selectbox(
            "Nature (Attack modifier)",
            [("Positive (+10%)", 1.1), ("Neutral", 1.0), ("Negative (-10%)", 0.9)],
            index=1,
            key="att_nature",
        )[1]

        attacker_stats = PokemonStats(
            hp=DamageCalculator.calculate_stat(
                attacker_stats_dict["hp"], 31, hp_ev, 50
            ),
            attack=DamageCalculator.calculate_stat(
                attacker_stats_dict["attack"], 31, atk_ev, 50, nature_modifier
            ),
            defense=DamageCalculator.calculate_stat(
                attacker_stats_dict["defense"], 31, def_ev, 50
            ),
            sp_attack=DamageCalculator.calculate_stat(
                attacker_stats_dict["sp_attack"], 31, spa_ev, 50
            ),
            sp_defense=DamageCalculator.calculate_stat(
                attacker_stats_dict["sp_defense"], 31, spd_ev, 50
            ),
            speed=DamageCalculator.calculate_stat(
                attacker_stats_dict["speed"], 31, spe_ev, 50
            ),
        )

        # Move selection
        move_name = st.selectbox(
            "Move", list(DamageCalculator.COMMON_MOVES.keys()), key="move_select"
        )

        move_data = DamageCalculator.COMMON_MOVES[move_name]
        move = Move(
            name=move_name,
            power=move_data["power"],
            type=move_data["type"],
            category=move_data["category"],
        )

    with col2:
        st.markdown("### Defender")
        defender_name = st.selectbox(
            "Pokemon",
            list(DamageCalculator.COMMON_POKEMON_STATS.keys()),
            key="defender_pokemon",
        )

        defender_stats_dict = DamageCalculator.COMMON_POKEMON_STATS[defender_name]

        # EV inputs
        st.markdown("**EV Spread:**")
        def_col1, def_col2, def_col3 = st.columns(3)
        with def_col1:
            def_hp_ev = st.number_input("HP", 0, 252, 252, 4, key="def_hp_ev")
            def_atk_ev = st.number_input("Atk", 0, 252, 0, 4, key="def_atk_ev")
        with def_col2:
            def_def_ev = st.number_input("Def", 0, 252, 252, 4, key="def_def_ev")
            def_spa_ev = st.number_input("SpA", 0, 252, 0, 4, key="def_spa_ev")
        with def_col3:
            def_spd_ev = st.number_input("SpD", 0, 252, 0, 4, key="def_spd_ev")
            def_spe_ev = st.number_input("Spe", 0, 252, 0, 4, key="def_spe_ev")

        def_nature_modifier = st.selectbox(
            "Nature (Defense modifier)",
            [("Positive (+10%)", 1.1), ("Neutral", 1.0), ("Negative (-10%)", 0.9)],
            index=1,
            key="def_nature",
        )[1]

        defender_stats = PokemonStats(
            hp=DamageCalculator.calculate_stat(
                defender_stats_dict["hp"], 31, def_hp_ev, 50
            ),
            attack=DamageCalculator.calculate_stat(
                defender_stats_dict["attack"], 31, def_atk_ev, 50
            ),
            defense=DamageCalculator.calculate_stat(
                defender_stats_dict["defense"],
                31,
                def_def_ev,
                50,
                def_nature_modifier if move.category == "Physical" else 1.0,
            ),
            sp_attack=DamageCalculator.calculate_stat(
                defender_stats_dict["sp_attack"], 31, def_spa_ev, 50
            ),
            sp_defense=DamageCalculator.calculate_stat(
                defender_stats_dict["sp_defense"],
                31,
                def_spd_ev,
                50,
                def_nature_modifier if move.category == "Special" else 1.0,
            ),
            speed=DamageCalculator.calculate_stat(
                defender_stats_dict["speed"], 31, def_spe_ev, 50
            ),
        )

    # Modifiers
    st.markdown("### Battle Conditions")
    mod_col1, mod_col2, mod_col3 = st.columns(3)

    with mod_col1:
        crit = st.checkbox("Critical Hit")
        burn = st.checkbox("Burn (Physical moves)")
        screens = st.checkbox("Light Screen/Reflect")

    with mod_col2:
        weather_mod = st.selectbox(
            "Weather",
            [
                ("None", 1.0),
                ("Rain (Water +50%)", 1.5),
                ("Sun (Fire +50%)", 1.5),
                ("Sun (Water -50%)", 0.5),
            ],
            key="weather",
        )[1]

        terrain_mod = st.selectbox(
            "Terrain",
            [
                ("None", 1.0),
                ("Electric (+30%)", 1.3),
                ("Psychic (+30%)", 1.3),
                ("Grassy (+30%)", 1.3),
            ],
            key="terrain",
        )[1]

    with mod_col3:
        item_mod = st.selectbox(
            "Attacker Item",
            [
                ("None", 1.0),
                ("Life Orb (+30%)", 1.3),
                ("Choice Band/Specs (+50%)", 1.5),
            ],
            key="item",
        )[1]

        multi_target = st.checkbox("Multi-target (Doubles)")
        friend_guard = st.checkbox("Friend Guard")

    # Calculate damage
    modifiers = DamageModifiers(
        weather=weather_mod,
        terrain=terrain_mod,
        item_attacker=item_mod,
        crit=crit,
        burn=burn,
        screens=screens,
        multi_target=multi_target,
        friend_guard=friend_guard,
    )

    # Results
    st.markdown("## 🎯 Damage Results")

    try:
        # Simplified type lists for demo
        attacker_types = ["Normal"]  # Would need Pokemon type data
        defender_types = ["Normal"]  # Would need Pokemon type data

        min_dmg, max_dmg, ko_chance = DamageCalculator.calculate_damage_range(
            attacker_stats,
            defender_stats,
            move,
            attacker_types,
            defender_types,
            modifiers,
        )

        min_pct = DamageCalculator.calculate_damage_percentage(
            min_dmg, defender_stats.hp
        )
        max_pct = DamageCalculator.calculate_damage_percentage(
            max_dmg, defender_stats.hp
        )

        # Display results
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Damage Range", f"{min_dmg} - {max_dmg}")

        with col2:
            st.metric("Percentage", f"{min_pct:.1f}% - {max_pct:.1f}%")

        with col3:
            st.metric("KO Chance", f"{ko_chance * 100:.1f}%")

        # Detailed breakdown
        with st.expander("Calculation Details"):
            st.write(f"**Attacker:** {attacker_name}")
            st.write(
                f"- {move.category} Attack Stat: {attacker_stats.attack if move.category == 'Physical' else attacker_stats.sp_attack}"
            )
            st.write(f"**Defender:** {defender_name}")
            st.write(f"- HP: {defender_stats.hp}")
            st.write(
                f"- {move.category} Defense Stat: {defender_stats.defense if move.category == 'Physical' else defender_stats.sp_defense}"
            )
            st.write(f"**Move:** {move.name} ({move.power} BP, {move.type} type)")

    except Exception as e:
        st.error(f"Calculation failed: {e}")


def render_speed_tiers_page():
    """Render the speed tiers page"""
    st.markdown(
        '<div class="team-header"><h1>⚡ Speed Tier Analysis</h1><p>Analyze speed benchmarks and tier positioning</p></div>',
        unsafe_allow_html=True,
    )

    # Speed benchmark calculator
    st.markdown("## 🎯 Speed Benchmark Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        target_speed = st.number_input(
            "Target Speed Stat",
            min_value=1,
            max_value=300,
            value=150,
            help="Enter a speed stat to see what it outspeeds",
        )

    with col2:
        regulation = st.selectbox("Regulation", ["A", "B", "C", "D", "E"])

    if st.button("🔍 Analyze Speed Benchmark"):
        try:
            analysis = SpeedTierAnalyzer.analyze_speed_benchmark(
                target_speed, regulation
            )

            # Results
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Speed Tier", analysis["speed_tier"])

            with col2:
                st.metric("Position", analysis["tier_position"])

            with col3:
                st.metric("Outspeed %", f"{analysis['outspeed_percentage']}%")

            # What it outspeeds
            if analysis["outspeeds"]:
                st.markdown("### 🏃‍♂️ Outspeeds:")
                for benchmark in analysis["outspeeds"][:10]:
                    st.write(f"• {benchmark}")

            # Recommendations
            if analysis["recommendations"]:
                st.markdown("### 💡 Recommendations:")
                for rec in analysis["recommendations"]:
                    st.write(f"• {rec}")

        except Exception as e:
            st.error(f"Analysis failed: {e}")

    # Speed tier table
    st.markdown("## 📊 Common Speed Benchmarks")

    # Show common benchmarks in a nice table
    import pandas as pd

    benchmark_data = []
    for name, speed in list(SpeedTierAnalyzer.COMMON_SPEED_BENCHMARKS.items())[:15]:
        benchmark_data.append(
            {
                "Pokemon": name.replace(" Max", ""),
                "Speed": speed,
                "Tier": SpeedTierAnalyzer._analyze_tier_cutoffs(speed, regulation)[
                    "tier"
                ],
            }
        )

    df = pd.DataFrame(benchmark_data)
    st.dataframe(df, use_container_width=True)

    # Pokemon speed calculator
    st.markdown("## 🧮 Pokemon Speed Calculator")

    col1, col2 = st.columns(2)

    with col1:
        pokemon_name = st.selectbox(
            "Pokemon",
            list(SpeedTierAnalyzer.VGC_POKEMON_BASE_SPEEDS.keys()),
            key="speed_calc_pokemon",
        )

        base_speed = SpeedTierAnalyzer.VGC_POKEMON_BASE_SPEEDS[pokemon_name]
        st.write(f"Base Speed: {base_speed}")

    with col2:
        speed_evs = st.number_input("Speed EVs", 0, 252, 252, 4)
        nature_mod = st.selectbox(
            "Nature",
            [("Positive (+10%)", 1.1), ("Neutral", 1.0), ("Negative (-10%)", 0.9)],
            index=0,
        )[1]

    calculated_speed = SpeedTierAnalyzer.calculate_speed_stat(
        base_speed, ev=speed_evs, nature_modifier=nature_mod
    )

    st.metric("Calculated Speed", calculated_speed)

    # EV suggestions
    if st.button("💡 Get Speed EV Suggestions"):
        try:
            suggestions = SpeedTierAnalyzer.suggest_speed_evs(
                pokemon_name, regulation=regulation
            )

            st.markdown("### 📋 EV Suggestions:")
            for suggestion in suggestions["suggestions"]:
                with st.expander(
                    f"{suggestion['description']} - {suggestion['resulting_speed']} Speed"
                ):
                    st.write(f"**EVs:** {suggestion['evs']}")
                    st.write(f"**Nature:** {suggestion['nature']}")
                    st.write(f"**Justification:** {suggestion['justification']}")

        except Exception as e:
            st.error(f"Failed to generate suggestions: {e}")


def main():
    """Main application with navigation"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")

        # Initialize current page in session state
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "New Analysis"

        # Navigation buttons
        if st.button(
            "📝 New Analysis",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "New Analysis"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "New Analysis"
            st.rerun()

        if st.button(
            "📚 Previous Articles",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "Previous Articles"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "Previous Articles"
            st.rerun()

        if st.button(
            "🏆 Team Database",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "Team Database"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "Team Database"
            st.rerun()

        if st.button(
            "⚔️ Team Comparison",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "Team Comparison"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "Team Comparison"
            st.rerun()

        if st.button(
            "🧮 Damage Calculator",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "Damage Calculator"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "Damage Calculator"
            st.rerun()

        if st.button(
            "⚡ Speed Tiers",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state["current_page"] == "Speed Tiers"
                else "secondary"
            ),
        ):
            st.session_state["current_page"] = "Speed Tiers"
            st.rerun()

        st.divider()

        # Cache stats
        cache_stats = get_cache_stats()
        st.metric("Cached Articles", cache_stats["cached_articles"])
        st.metric("Cache Size", f"{cache_stats['total_size_mb']} MB")

        if st.button(
            "🗑️ Clear All Cache",
            use_container_width=True,
            disabled=cache_stats["cached_articles"] == 0,
        ):
            if clear_cache():
                st.success("Cache cleared!")
                st.rerun()

    # Render the appropriate page
    if st.session_state["current_page"] == "New Analysis":
        render_new_analysis_page()
    elif st.session_state["current_page"] == "Previous Articles":
        render_previous_articles_page()
    elif st.session_state["current_page"] == "Team Database":
        render_team_database_page()
    elif st.session_state["current_page"] == "Team Comparison":
        render_team_comparison_page()
    elif st.session_state["current_page"] == "Damage Calculator":
        render_damage_calculator_page()
    elif st.session_state["current_page"] == "Speed Tiers":
        render_speed_tiers_page()


if __name__ == "__main__":
    main()
