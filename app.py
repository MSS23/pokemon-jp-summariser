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
import time
from datetime import datetime
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
    )

    DATABASE_AVAILABLE = True
except ImportError as e:
    # Database modules not available, will use fallback functionality
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
    
    /* Ultra-Wide Desktop (1400px+) - Maximum layout for full-screen */
    @media (min-width: 1400px) {
        .pokemon-info-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .ev-stats-grid {
            grid-template-columns: repeat(6, 1fr);
            gap: 16px;
        }
        
        .pokemon-card {
            max-width: 1200px;
            margin: 16px auto;
            padding: 28px;
        }
        
        .team-header h1 {
            font-size: clamp(2.8rem, 4vw, 4rem);
        }
        
        .ev-stat {
            flex-direction: column;
            text-align: center;
            padding: 12px 8px;
        }
        
        .ev-stat-name {
            font-size: 10px;
            margin-bottom: 4px;
        }
        
        .ev-stat-value {
            font-size: 16px;
            font-weight: 700;
        }
    }

    /* Large Desktop (1101px - 1399px) - Enhanced layouts for wide screens */
    @media (max-width: 1399px) and (min-width: 1101px) {
        .pokemon-info-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
        }
        
        .ev-stats-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }
        
        .pokemon-card {
            max-width: 1000px;
            margin: 12px auto;
            padding: 24px;
        }
        
        .team-header h1 {
            font-size: clamp(2.5rem, 4vw, 3.5rem);
        }
    }
    
    /* Half-Screen Chrome Optimization (950px - 1100px) - Perfect for split-screen */
    @media (max-width: 1100px) and (min-width: 950px) {
        .ev-stats-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: clamp(14px, 2vw, 18px);
        }
        
        .pokemon-info-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: clamp(16px, 2.5vw, 20px);
        }
        
        .pokemon-card {
            padding: clamp(20px, 3vw, 24px);
            margin: clamp(10px, 1.5vw, 14px) 0;
        }
        
        .ev-stat {
            padding: clamp(10px, 1.5vw, 12px) clamp(8px, 1.2vw, 10px);
            justify-content: center;
            text-align: center;
        }
        
        .ev-stat-name {
            font-size: clamp(10px, 1.2vw, 11px);
            font-weight: 600;
            min-width: unset;
        }
        
        .ev-stat-value {
            font-size: clamp(13px, 1.5vw, 15px);
            font-weight: 700;
            min-width: unset;
        }
        
        .move-item {
            padding: clamp(10px, 1.5vw, 12px) clamp(14px, 2vw, 16px);
            font-size: clamp(13px, 1.3vw, 14px);
            margin: clamp(4px, 0.8vw, 6px) 0;
        }
        
        .info-item {
            padding: clamp(12px, 1.8vw, 14px) clamp(14px, 2vw, 16px);
            min-height: 60px;
        }
        
        .info-label {
            font-size: clamp(11px, 1.2vw, 12px);
        }
        
        .info-value {
            font-size: clamp(13px, 1.4vw, 14px);
        }
        
        .team-header {
            padding: clamp(24px, 3vw, 30px);
        }
        
        .team-header h1 {
            font-size: clamp(2rem, 3.5vw, 2.3rem);
        }
        
        .pokemon-name {
            font-size: clamp(22px, 3vw, 26px);
        }
        
        .ev-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: clamp(12px, 1.8vw, 16px);
            flex-wrap: wrap;
            gap: clamp(8px, 1.2vw, 12px);
        }
        
        .ev-title {
            font-size: clamp(15px, 1.6vw, 18px);
            font-weight: 700;
        }
        
        .ev-total {
            font-size: clamp(12px, 1.3vw, 14px);
            padding: clamp(4px, 0.8vw, 6px) clamp(10px, 1.5vw, 14px);
        }
        
        /* Enhanced moves container for half-screen */
        .moves-container {
            margin-top: clamp(16px, 2vw, 20px);
        }
        
        .moves-title {
            font-size: clamp(15px, 1.6vw, 18px);
            font-weight: 700;
            margin-bottom: clamp(10px, 1.5vw, 14px);
            color: var(--type-color, #1e293b);
        }
    }

    /* Desktop/Tablet Landscape (900px - 949px) - Standard responsive */
    @media (max-width: 949px) and (min-width: 900px) {
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
    """Enhanced VGC image detection with 2025 improvements"""
    
    # Enhanced scoring system for better accuracy
    relevance_score = 0
    
    # Priority 1: note.com assets (highest priority)
    if image_info.get("is_note_com_asset", False):
        width, height = image_info.get("size", (0, 0))
        file_size = image_info.get("file_size", 0)
        if width > 300 and height > 200 and file_size > 10000:  # 10KB+
            relevance_score += 8  # Very high score for note.com assets
    
    # Priority 2: Image dimensions analysis
    width, height = image_info.get("size", (0, 0))
    if width > 600 and height > 400:  # Team card likely dimensions
        relevance_score += 3
    elif width > 800 and height > 600:  # Screenshot dimensions
        relevance_score += 4
    elif width > 1200:  # Wide format (rental team screenshots)
        relevance_score += 5

    # Priority 3: File size indicators
    file_size = image_info.get("file_size", 0)
    if file_size > 50000:  # Large images likely contain detailed data
        relevance_score += 2
    elif file_size > 100000:  # Very large images
        relevance_score += 3

    # Priority 4: Already flagged as likely team card
    if image_info.get("is_likely_team_card", False):
        relevance_score += 6

    # Priority 5: Text content analysis (enhanced keywords)
    text_content = (
        image_info.get("alt_text", "") + " " + image_info.get("title", "") + " " + image_info.get("src", "")
    ).lower()

    enhanced_vgc_keywords = [
        # English keywords
        "pokemon", "vgc", "team", "ev", "iv", "stats", "competitive", "doubles", "battle",
        "rental", "pokepaste", "regulation", "tournament", "worlds", "regional", "championship",
        "movesets", "nature", "ability", "item", "tera", "sprite", "showdown",
        # Japanese keywords  
        "ポケモン", "チーム", "ダブル", "バトル", "大会", "構築", "調整", "技構成", "持ち物",
        "性格", "特性", "テラス", "ランクマ", "レンタル", "努力値", "個体値",
        # Common Pokemon names that indicate team content
        "ガブリアス", "ガオガエン", "ウインディ", "モロバレル", "エルフーン", "ランドロス",
        "カイリュー", "ハリテヤマ", "クレッフィ", "トリトドン", "ニンフィア", "リザードン"
    ]

    # Enhanced keyword scoring
    high_value_keywords = ["pokemon", "ポケモン", "vgc", "team", "チーム", "rental", "レンタル"]
    medium_value_keywords = ["ev", "努力値", "battle", "バトル", "regulation", "tournament"]
    
    for keyword in enhanced_vgc_keywords:
        if keyword in text_content:
            if keyword in high_value_keywords:
                relevance_score += 3
            elif keyword in medium_value_keywords:
                relevance_score += 2
            else:
                relevance_score += 1

    # Priority 6: URL-based detection
    src_url = image_info.get("src", "").lower()
    if any(domain in src_url for domain in ["note.com", "assets.st-note.com", "pbs.twimg.com"]):
        relevance_score += 2

    # Priority 7: File format preferences
    if src_url.endswith((".png", ".jpg", ".jpeg")):
        relevance_score += 1

    # Return True if score meets threshold (adjustable based on testing)  
    return relevance_score >= 5  # Threshold for "potentially VGC-relevant"


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
            # WCS2023 Team specific mappings
            "hisuian-arcanine": "arcanine-hisui",
            "urshifu-dark": "urshifu-single-strike",
            "urshifu-water": "urshifu-rapid-strike",
            "urshifu-single-strike": "urshifu-single-strike",
            "urshifu-rapid-strike": "urshifu-rapid-strike",
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
                🎯 ENHANCED 2025 POKEMON VGC IMAGE ANALYSIS MISSION:
                Perform comprehensive Pokemon team identification and data extraction with confidence scoring.

                **MULTI-OBJECTIVE ANALYSIS (Execute ALL):**
                
                **OBJECTIVE 1: POKEMON SPRITE IDENTIFICATION & VALIDATION**
                - Identify each Pokemon by visual appearance (sprites, artwork, models)
                - Cross-reference visual identification with any text labels
                - Note Pokemon forms, regional variants, shiny status if visible
                - Rate identification confidence for each Pokemon (High/Medium/Low)
                - Flag any Pokemon that are visually ambiguous or unclear

                **OBJECTIVE 2: POKEMON NAME VALIDATION**  
                - Look for Japanese Pokemon names in text labels
                - Cross-reference with comprehensive name database
                - Validate sprite matches expected Pokemon name
                - Flag any mismatches between visual and textual identification

                **OBJECTIVE 3: EV SPREAD DETECTION (Enhanced)**
                SCAN METHODICALLY for numerical EV patterns in ALL these formats:
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

                **ENHANCED OUTPUT FORMAT (2025 STANDARDS):**
                Provide detailed analysis for each Pokemon found:
                
                ```
                === POKEMON ANALYSIS SUMMARY ===
                Total Pokemon Identified: X
                Data Quality Score: X/10
                Overall Confidence: High/Medium/Low
                
                === INDIVIDUAL POKEMON DATA ===
                
                **POKEMON 1:**
                - Visual_ID: [Pokemon name from sprite recognition]
                - Text_Label: [Japanese name if visible] → [English translation]
                - ID_Confidence: High/Medium/Low
                - Validation_Status: Match/Mismatch/Unclear
                - Form_Notes: [Regional form, shiny, gender differences, etc.]
                - EV_Spread: [HP/Atk/Def/SpA/SpD/Spe] (Source: Visual/Text)
                - EV_Confidence: High/Medium/Low
                - Ability: [Ability name]
                - Item: [Held item]
                - Nature: [Nature]
                - Tera_Type: [Tera type]
                - Moves: [Move1, Move2, Move3, Move4]
                - Data_Quality: [Notes on data completeness/clarity]
                
                **POKEMON 2:**
                [Same format as above]
                
                [Continue for all Pokemon...]
                
                === VALIDATION SUMMARY ===
                - Sprite_Text_Matches: X/Y Pokemon have matching visual and text identification
                - EV_Data_Found: X/Y Pokemon have complete EV spreads
                - Potential_Issues: [List any concerns, mismatches, or unclear data]
                - Confidence_Distribution: X High, Y Medium, Z Low confidence identifications
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

    def detect_regulation_from_date(self, url: Optional[str] = None, content: str = "") -> Optional[str]:
        """Detect VGC regulation based on article date or URL"""
        try:
            from datetime import datetime, date
            import re
            
            # Regulation date ranges for SV VGC
            regulation_dates = {
                "A": (date(2022, 11, 18), date(2023, 1, 31)),  # Series 1
                "B": (date(2023, 2, 1), date(2023, 3, 31)),    # Series 2  
                "C": (date(2023, 4, 1), date(2023, 6, 30)),    # Series 3 - Treasures allowed
                "D": (date(2023, 7, 1), date(2023, 9, 30)),    # Series 4 - HOME integration
                "E": (date(2023, 10, 1), date(2023, 12, 31)),  # Series 5 - Teal Mask
                "F": (date(2024, 1, 1), date(2024, 3, 31)),    # Series 6 - Indigo Disk
                "G": (date(2024, 4, 1), date(2024, 6, 30)),    # Series 7 - Restricted Singles
                "H": (date(2024, 7, 1), date(2024, 9, 30)),    # Series 8 - Back to Basics
                "I": (date(2024, 10, 1), date(2025, 1, 31)),   # Series 9 - Double Restricted
            }
            
            article_date = None
            
            # Try to extract date from URL first
            if url:
                # Common date patterns in URLs: /2023/09/16/, /2023-09-16, etc.
                date_patterns = [
                    r'/(\d{4})/(\d{1,2})/(\d{1,2})/',
                    r'/(\d{4})-(\d{1,2})-(\d{1,2})/',
                    r'(\d{4})-(\d{2})-(\d{2})',
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, url)
                    if match:
                        year, month, day = map(int, match.groups())
                        article_date = date(year, month, day)
                        break
            
            # If no date in URL, try to find it in content
            if not article_date and content:
                # Look for date patterns in content
                date_patterns = [
                    r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})',
                    r'(\d{1,2})[月/-](\d{1,2})[日/-](\d{4})',
                    r'(\d{4})-(\d{2})-(\d{2})',
                ]
                
                for pattern in date_patterns:
                    matches = re.findall(pattern, content[:1000])  # Check first 1000 chars
                    if matches:
                        try:
                            if len(matches[0]) == 3:
                                if len(matches[0][0]) == 4:  # Year first
                                    year, month, day = map(int, matches[0])
                                else:  # Day first
                                    month, day, year = map(int, matches[0])
                                article_date = date(year, month, day)
                                break
                        except:
                            continue
            
            # Map date to regulation
            if article_date:
                for regulation, (start_date, end_date) in regulation_dates.items():
                    if start_date <= article_date <= end_date:
                        st.info(f"📅 **Date-based Detection**: Article date {article_date} → Regulation {regulation}")
                        return regulation
            
            return None
        except Exception as e:
            st.warning(f"Date-based regulation detection failed: {str(e)}")
            return None

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

        # Enhanced 2025 AI prompt with structured output and validation
        prompt = f"""
You are a professional Pokemon VGC (Video Game Championships) expert analyzer specializing in Japanese article translation and team analysis. You will use Chain-of-Thought reasoning and self-validation to ensure 95%+ accuracy.

🎯 CRITICAL MISSION: Perform EXHAUSTIVE multi-stage analysis to extract ALL Pokemon and EV data from this article with confidence scoring.

📋 STRUCTURED OUTPUT SCHEMA REQUIREMENT:
You MUST output your response as a valid JSON object matching this exact schema. Use temperature 0.1 for structured consistency.

ARTICLE CONTENT:
{combined_content[:12000]}

🧠 CHAIN-OF-THOUGHT ANALYSIS METHODOLOGY (Execute each step):

**STEP 0: SELF-ASSESSMENT PREPARATION**
- Rate the article content quality (1-10)
- Identify potential language barriers or OCR artifacts
- Note any missing or unclear sections that might affect analysis

**STEP 1: PRELIMINARY SCAN & CONFIDENCE SCORING**
- Perform initial read-through to understand article context
- Identify article type (tournament report, team building guide, analysis, etc.)
- Estimate data completeness percentage (Pokemon: %, EV data: %, Move data: %)

🚨 CRITICAL POKEMON NAME TRANSLATION ALERT 🚨
- セグレイブ = "Baxcalibur" (Dragon/Ice, Generation IX) - NOT Glaceon!
- ドドゲザン = "Kingambit" (Dark/Steel, Generation IX) - NOT Glaceon!
- トリトドン = "Gastrodon" (Water/Ground) - NOT Tatsugiri!
- シャリタツ = "Tatsugiri" (Dragon/Water) - NOT Gastrodon!
- ヒスイウインディ = "Hisuian Arcanine" (Fire/Rock) - NOT regular Arcanine!
- 悪ウーラオス = "Urshifu-Dark" or "Urshifu (Single Strike)" - NOT regular Urshifu!
- 水ウーラオス = "Urshifu-Water" or "Urshifu (Rapid Strike)" - NOT regular Urshifu!
- NEVER output duplicate Pokemon names (e.g., "3x Tornadus") - this indicates analysis failure!
- If you see these Japanese names, translate them correctly to avoid major errors!

**STEP 1: CORE TEAM COMPOSITION DETECTION (MAX 6 POKEMON)**
🎯 **PRIMARY OBJECTIVE**: Identify the main 6-Pokemon competitive team, NOT all mentioned Pokemon

**PRIORITY DETECTION HIERARCHY:**
1. **Core Team Members** (TOP PRIORITY):
   - Pokemon with complete data: EV spreads, movesets, items, abilities, natures
   - Pokemon in structured team sections or numbered lists
   - Pokemon with detailed individual analysis sections
   
2. **Team Structure Indicators**:
   - Look for team composition sections, roster lists, "my team" descriptions
   - Prioritize Pokemon with battle role explanations
   - Focus on Pokemon with specific build details (not just names)

3. **EXCLUDE from main team**:
   - Pokemon mentioned only as examples ("like Garchomp...")  
   - Pokemon mentioned as counters or threats ("watch out for Landorus")
   - Pokemon in meta discussion or comparison contexts
   - Pokemon mentioned without specific build details
   
4. **VALIDATION RULES**:
   - **MAXIMUM 6 Pokemon per team** (VGC standard rule)
   - **NO DUPLICATE POKEMON** - Each Pokemon name must be unique (e.g., never "3x Tornadus")
   - If >6 Pokemon detected, prioritize those with most complete data
   - Must have at least move/ability/item data to qualify as main team member
   - **FINAL CHECK**: Count unique Pokemon names - must equal exactly 6 different Pokemon

**STEP 2: AGGRESSIVE EV DATA EXTRACTION**
- Search ALL text sections for numerical patterns that could be EVs
- Look in Pokemon descriptions, team summaries, separate EV sections
- Check battle calculations, stat references, benchmark mentions
- Scan for embedded tables, lists, or formatted stat data
- Include partial EV data even if incomplete

**STEP 3: IMAGE DATA INTEGRATION & POKEMON VISUAL VALIDATION**
- If IMAGE ANALYSIS RESULTS are provided, prioritize visual data over text interpretation
- Combine Pokemon found in images with text-based detections
- Use image EV data to supplement or validate text-based EV spreads
- Cross-reference visual team compositions with article descriptions
- **CRITICAL: Use Pokemon sprites/images to validate text-based identifications**
- If image shows Zapdos sprite but text analysis suggests Thundurus, prioritize visual evidence
- Look for Pokemon team screenshots, rental team images, or battle replays
- Validate Pokemon forms (e.g., Ogerpon masks, Therian formes) through visual cues

**STEP 4: ADVANCED REGULATION DETECTION & MULTI-LAYER VALIDATION**

🔍 **REGULATION IDENTIFICATION METHODOLOGY (2025 ENHANCED):**

**Primary Detection Methods (Use ALL simultaneously):**
1. **Date-Based Inference**: Match article publication date with regulation timeline
2. **Pokemon Composition Analysis**: Analyze team for regulation-specific indicators
3. **Tournament Context Clues**: Look for series mentions, tournament names, format descriptions
4. **Explicit Regulation References**: Direct mentions of "Regulation X" or "Series Y"
5. **Meta Context Validation**: Cross-reference with known meta trends per regulation

**Secondary Validation Checks:**
- **Ban List Cross-Reference**: Validate all Pokemon against regulation ban lists
- **Restricted Count Validation**: Count restricted legendaries (0, 1, or 2 allowed)
- **DLC Content Availability**: Check if Pokemon require specific DLC releases
- **Generation Mix Analysis**: Older gens suggest Regulation D+, Paldea-only suggests A/B

**VGC REGULATION DATABASE (COMPLETE REFERENCE - A through J):**

**🗓️ Regulation A (Dec 1, 2022 - Jan 31, 2023) - "PALDEA PREVIEW":**
- **Context**: Launch regulation, Paldea Pokemon only
- **Date Range**: 2022-12-01 to 2023-01-31
- **BANNED**: ALL Legendaries, ALL Paradox Pokemon, ALL Treasures of Ruin, Koraidon, Miraidon
- **ALLOWED**: Only native Paldea Pokemon from base game
- **Key Indicators**: Pure Paldea teams, no legendaries, basic movepools
- **Meta Context**: Gimmighoul, Annihilape, Armarouge, Gholdengo dominance

**🗓️ Regulation B (Feb 1, 2023 - Apr 30, 2023) - "PARADOX UNLEASHED":**
- **Context**: First major expansion, Paradox Pokemon introduced
- **Date Range**: 2023-02-01 to 2023-04-30
- **BANNED**: ALL Legendaries, ALL Treasures of Ruin, Koraidon, Miraidon
- **ALLOWED**: All Paldea + ALL Paradox Pokemon
- **Key Additions**: Flutter Mane, Iron Bundle, Great Tusk, Iron Treads, etc.
- **Meta Context**: Flutter Mane + Iron Bundle dominance, Paradox cores

**🗓️ Regulation C (May 1, 2023 - Dec 31, 2023) - "TREASURES EMERGE":**
- **Context**: Treasures of Ruin introduced, first legendary expansion
- **Date Range**: 2023-05-01 to 2023-12-31
- **BANNED**: ALL Legendaries EXCEPT Treasures of Ruin, Koraidon, Miraidon
- **ALLOWED**: All previous + Chi-Yu, Chien-Pao, Ting-Lu, Wo-Chien
- **Key Indicators**: Presence of Treasures of Ruin but no other legendaries
- **Meta Context**: Chi-Yu dominance, Chien-Pao cores, Ting-Lu walls

**🗓️ Regulation D (Jan 1, 2024 - Apr 30, 2024) - "HOME INTEGRATION":**
- **Context**: Pokemon HOME compatibility, massive roster expansion
- **Date Range**: 2024-01-01 to 2024-04-30
- **BANNED**: Only Restricted Legendaries (Box art legends, creation trio, etc.)
- **ALLOWED**: All transferable Pokemon via HOME (900+ species)
- **Key Additions**: Incineroar, Rillaboom, Landorus-T, Amoonguss, Garchomp
- **Meta Context**: Return of VGC classics, Landorus-T + Incineroar cores
- **Restricted Ban List**: Dialga, Palkia, Giratina, Reshiram, Zekrom, Kyurem, Xerneas, Yveltal, Zygarde, Cosmog line, Necrozma, Solgaleo, Lunala, Zacian, Zamazenta, Eternatus, Calyrex, Koraidon, Miraidon

**🗓️ Regulation E (May 1, 2024 - Aug 31, 2024) - "TEAL MASK EXPANSION":**
- **Context**: The Teal Mask DLC integration
- **Date Range**: 2024-05-01 to 2024-08-31
- **BANNED**: Only Restricted Legendaries
- **ALLOWED**: All previous + Teal Mask DLC Pokemon
- **Key Additions**: Ogerpon (all forms), Bloodmoon Ursaluna, Loyal Three
- **Meta Context**: Ogerpon form diversity, Bloodmoon Ursaluna impact

**🗓️ Regulation F (Sep 1, 2024 - Dec 31, 2024) - "INDIGO DISK COMPLETE":**
- **Context**: The Indigo Disk DLC integration, full roster available
- **Date Range**: 2024-09-01 to 2024-12-31
- **BANNED**: Only Restricted Legendaries
- **ALLOWED**: ALL Pokemon (except restricted legendaries)
- **Key Additions**: Walking Wake, Raging Bolt, Gouging Fire, Iron Leaves, Iron Boulder, Iron Crown
- **Meta Context**: Complete competitive roster, DLC legendaries impact

**🗓️ Regulation G (Jan 1, 2025 - Apr 30, 2025) - "RESTRICTED SINGLES":**
- **Context**: One restricted legendary allowed per team
- **Date Range**: 2025-01-01 to 2025-04-30
- **BANNED**: Only Mythical Pokemon
- **ALLOWED**: ONE Restricted Legendary per team + all other Pokemon
- **Restricted Legends**: Koraidon, Miraidon, Calyrex (all forms), Zacian, Zamazenta, etc.
- **Meta Context**: Calyrex-Shadow dominance, legendary + support cores

**🗓️ Regulation H (Sep 2024 - Jan 2025, May 1, 2025 - Aug 31, 2025) - "BACK TO BASICS":**
- **Context**: Most restrictive format ever, removes all "problematic" Pokemon
- **Date Range**: 2024-09-01 to 2025-01-31, 2025-05-01 to 2025-08-31
- **BANNED**: ALL Legendaries, ALL Paradox Pokemon, ALL Treasures of Ruin, ALL Mythicals
- **COMPREHENSIVE BAN LIST**:
  - **Legendaries**: Articuno, Zapdos, Moltres, Mewtwo, Mew, Raikou, Entei, Suicune, Lugia, Ho-Oh, Celebi, Regirock, Regice, Registeel, Latias, Latios, Kyogre, Groudon, Rayquaza, Jirachi, Deoxys, Dialga, Palkia, Heatran, Regigigas, Giratina, Cresselia, Phione, Manaphy, Darkrai, Shaymin, Arceus, Victini, Cobalion, Terrakion, Virizion, Tornadus, Thundurus, Reshiram, Zekrom, Landorus, Kyurem, Keldeo, Meloetta, Genesect, Xerneas, Yveltal, Zygarde, Diancie, Hoopa, Volcanion, Cosmog, Cosmoem, Solgaleo, Lunala, Necrozma, Magearna, Marshadow, Zeraora, Meltan, Melmetal, Zacian, Zamazenta, Eternatus, Kubfu, Urshifu, Regieleki, Regidrago, Glastrier, Spectrier, Calyrex, Enamorus, Koraidon, Miraidon
  - **Paradox Pokemon**: Great Tusk, Scream Tail, Brute Bonnet, Flutter Mane, Slither Wing, Sandy Shocks, Roaring Moon, Walking Wake, Iron Treads, Iron Bundle, Iron Hands, Iron Jugulis, Iron Moth, Iron Thorns, Iron Valiant, Raging Bolt, Gouging Fire, Iron Leaves, Iron Boulder, Iron Crown
  - **Treasures of Ruin**: Chi-Yu, Chien-Pao, Ting-Lu, Wo-Chien
  - **Loyal Three**: Okidogi, Munkidori, Fezandipiti
  - **Other Bans**: Ogerpon (all forms), Bloodmoon Ursaluna
- **ALLOWED**: Only regular Pokemon (base forms, regional variants, regular evolutions)
- **Meta Context**: Most balanced format, focus on traditional VGC Pokemon

**🗓️ Regulation I (Sep 1, 2025 - Dec 31, 2025) - "DOUBLE RESTRICTED":**
- **Context**: Two restricted legendaries allowed per team
- **Date Range**: 2025-09-01 to 2025-12-31
- **BANNED**: Only Mythical Pokemon
- **ALLOWED**: UP TO TWO Restricted Legendaries per team + all other Pokemon
- **Meta Context**: Ultra-powerful teams, dual legendary cores, maximum diversity

**🗓️ Regulation J (Jan 1, 2026 - Apr 30, 2026) - "FUTURE FORMAT":**
- **Context**: Next generation format (projected)
- **Date Range**: 2026-01-01 to 2026-04-30
- **Status**: Future format, rules TBD
- **Expected**: New generation integration or format innovation

**🔍 ENHANCED REGULATION ANALYSIS REQUIREMENTS (2025 STANDARDS):**

**Multi-Step Regulation Detection Process:**
1. **Date Analysis**: Extract publication date and match to regulation timeline
2. **Pokemon Composition Scan**: Identify regulation indicators (legendaries, paradox, etc.)
3. **Tournament Context**: Look for explicit format mentions, series references
4. **Cross-Validation**: Confirm regulation through multiple evidence sources
5. **Confidence Scoring**: Rate detection confidence (High/Medium/Low)

**Comprehensive Validation Checks:**
1. **Ban List Validation**: Check every Pokemon against regulation-specific ban lists
2. **Restricted Count**: Verify legendary count (0 for A-F,H vs 1 for G vs 2 for I)
3. **DLC Availability**: Validate Pokemon availability based on regulation timeline
4. **Form Legality**: Check regional forms, alternate forms, and evolution availability
5. **Move Pool Validation**: Ensure moves are learnable in the regulation period

**Regulation-Specific Analysis Output:**
- **Identified Regulation**: Clear statement with confidence level
- **Legal/Illegal Pokemon**: Explicitly flag banned Pokemon with explanations
- **Meta Context**: Reference regulation-specific strategies and trends
- **Threat Assessment**: Only discuss legal threats and counters for the format
- **Historical Context**: Note if team is era-appropriate or uses legacy strategies
- **Format Restrictions**: Explain any unique rules or limitations

**Error Handling for Regulation Detection:**
- If multiple regulations possible: List all candidates with evidence
- If no clear regulation: Mark as "Unknown" but provide best guess with reasoning
- If conflicting evidence: Prioritize explicit mentions > date > Pokemon composition
- Always explain the reasoning behind regulation identification

**STEP 5: CONTEXTUAL DATA VALIDATION**
- Cross-reference Pokemon with their mentioned moves/abilities
- Validate EV totals and correct obvious errors (must total 508)
- Ensure exactly 4 moves per Pokemon (mandatory requirement)
- Infer missing team members from context clues
- Connect strategy descriptions to specific Pokemon
- Prioritize image data when conflicts exist between text and visual information

**STEP 6: ENHANCED DATA VALIDATION & SELF-CORRECTION (2025 STANDARDS)**
- **Pokemon Validation**: Cross-reference each Pokemon with comprehensive Japanese name database
- **Confidence Assignment**: Rate each Pokemon identification (High/Medium/Low/Unknown)
- **EV Validation**: Ensure all spreads total 508, flag invalid patterns, correct obvious errors
- **Move Pool Checking**: Validate move compatibility with identified Pokemon
- **Ability Consistency**: Verify abilities match Pokemon and their available ability sets
- **Form Validation**: Check for regional forms, alternate forms, and gender differences
- **Regulation Compliance**: Validate all Pokemon against detected regulation ban lists

**STEP 7: SELF-VALIDATION & QUALITY CONTROL**
- **Team Size Check**: CRITICAL - Ensure exactly ≤6 Pokemon in team (VGC rule)
- **Core Team Validation**: Verify these are main team members, not example mentions
- **Data Quality Scoring**: Prioritize Pokemon with complete movesets, EVs, items, abilities
- **Internal Consistency Check**: Do Pokemon, moves, abilities, and items all align logically?
- **Meta Reasonableness**: Does this team make sense for the identified regulation/format?
- **Data Completeness**: Are all required fields filled? Any obvious gaps?
- **Confidence Assessment**: Rate overall analysis confidence (1-10) with justification
- **Error Detection**: Flag any potential issues, conflicts, or low-confidence identifications
- **Final Review**: Re-examine any Pokemon with <80% confidence for possible corrections
- **Team Composition Logic**: Does this look like a real competitive team or random Pokemon mentions?

**STEP 8: STRUCTURED OUTPUT GENERATION**
- Generate final JSON following exact schema below
- Include confidence scores for all major identifications
- Provide reasoning for any uncertain or low-confidence detections
- Flag potential issues for human review if necessary

**MANDATORY DATA COMPLETENESS RULES:**
- Every Pokemon MUST have exactly 4 moves (use "Unknown Move 1", "Unknown Move 2", etc. if needed)
- Every Pokemon MUST have an EV spread totaling 508 (use default 252/0/4/252/0/0 if missing)
- Every Pokemon MUST have held_item, nature, ability (use "Unknown" if not specified)
- All fields must be populated - no null or empty values allowed
- Flag any incomplete data and attempt to infer from context

**MOVE ENFORCEMENT RULES:**
- If fewer than 4 moves detected: Fill with "Unknown Move X" placeholders
- If more than 4 moves detected: Select the 4 most relevant/commonly used moves
- Cross-validate moves with Pokemon's type and role
- Prioritize image analysis move data over text when available

📋 ENHANCED 2025 OUTPUT SCHEMA (Must include confidence scoring and validation):

{{
    "title": "Translated article title (Japanese → English)",
    "summary": "Brief summary of the article's main points",
    "analysis_metadata": {{
        "content_quality_score": 8,
        "data_completeness_pokemon": "85%",
        "data_completeness_evs": "70%", 
        "data_completeness_moves": "90%",
        "overall_confidence": 8.5,
        "potential_issues": ["Issue 1 if any", "Issue 2 if any"],
        "analysis_notes": "Important notes about analysis process or data quality"
    }},
    "regulation_info": {{
        "regulation": "A, B, C, D, E, F, G, H, I, or Unknown",
        "confidence": "High/Medium/Low",
        "detection_method": "Date-based/Pokemon-composition/Explicit-mention/Tournament-context",
        "format": "VGC format description with key restrictions",
        "tournament_context": "Tournament or series context if mentioned",
        "ban_list_validated": true,
        "reasoning": "Detailed explanation of regulation determination"
    }},
    "team_analysis": {{
        "strategy": "Overall team strategy and approach",
        "strengths": ["Team strength 1", "Team strength 2", "Team strength 3"],
        "weaknesses": ["Potential weakness 1", "Potential weakness 2"],
        "meta_relevance": "How this team fits in the current meta",
        "regulation_compliance": "Compliance status with identified regulation"
    }},
    "pokemon_team": [
        {{
            "name": "Pokemon name in English",
            "confidence": "High/Medium/Low/Unknown",
            "detection_method": "Japanese-name-match/Context-clues/Image-confirmation/Inference",
            "japanese_name_found": "Original Japanese name if detected or null",
            "ability": "Ability name in English",
            "held_item": "Item name in English", 
            "tera_type": "Tera type in English - MUST be one of: Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy. Use 'Not specified in article' if unknown.",
            "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
            "ev_spread": "HP/Atk/Def/SpA/SpD/Spe format (e.g., 252/0/4/252/0/0) - Use 'Not specified in article' if missing",
            "ev_source": "article/image/calculated/default",
            "nature": "Nature name in English",
            "role": "Role in the team (e.g., Physical Attacker, Special Wall, etc.)",
            "ev_explanation": "Detailed explanation of EV spread reasoning with speed benchmarks and survival calculations",
            "validation_notes": "Notes about data quality or potential issues",
            "regulation_legal": true
        }}
        // CRITICAL: MAXIMUM 6 Pokemon (VGC standard). Focus on core team members with complete data, NOT example mentions
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

**OLDER GENERATION POKEMON - CRITICAL JAPANESE NAME TRANSLATIONS:**

**LEGENDARY ELECTRIC POKEMON (COMMONLY CONFUSED - CRITICAL):**
⚠️ サンダー → "Zapdos" (Electric/Flying, Kanto legendary bird, Generation I)
⚠️ ボルトロス → "Thundurus" (Electric/Flying, Forces of Nature trio, Generation V)
⚠️ NEVER confuse Zapdos (サンダー) with Thundurus (ボルトロス) - completely different legendaries!
⚠️ Context clues: Zapdos = Original Kanto legendary, often in older teams/formats
⚠️ Context clues: Thundurus = Has Prankster ability, Incarnate/Therian forms

**GENERATION I-V LEGENDARIES (CRITICAL MAPPINGS):**
- フリーザー → "Articuno" (Ice/Flying, Kanto legendary bird)
- ファイヤー → "Moltres" (Fire/Flying, Kanto legendary bird)
- ミュウツー → "Mewtwo" (Psychic, Kanto legendary)
- ミュウ → "Mew" (Psychic, Kanto mythical)
- ライコウ → "Raikou" (Electric, Johto legendary beast)
- エンテイ → "Entei" (Fire, Johto legendary beast) 
- スイクン → "Suicune" (Water, Johto legendary beast)
- ルギア → "Lugia" (Psychic/Flying, Johto legendary)
- ホウオウ → "Ho-Oh" (Fire/Flying, Johto legendary)
- レジロック → "Regirock" (Rock, Hoenn legendary titan)
- レジアイス → "Regice" (Ice, Hoenn legendary titan)
- レジスチル → "Registeel" (Steel, Hoenn legendary titan)
- ラティアス → "Latias" (Dragon/Psychic, Hoenn legendary)
- ラティオス → "Latios" (Dragon/Psychic, Hoenn legendary)
- カイオーガ → "Kyogre" (Water, Hoenn weather legendary)
- グラードン → "Groudon" (Ground, Hoenn weather legendary)
- レックウザ → "Rayquaza" (Dragon/Flying, Hoenn weather legendary)
- トルネロス → "Tornadus" (Flying, Forces of Nature trio)
- ランドロス → "Landorus" (Ground/Flying, Forces of Nature trio)

**GENERATION VI-VIII LEGENDARIES:**
- ザシアン → "Zacian" (Fairy/Steel, Galar legendary)
- ザマゼンタ → "Zamazenta" (Fighting/Steel, Galar legendary)
- コライドン → "Koraidon" (Fighting/Dragon, Paldea legendary)
- ミライドン → "Miraidon" (Electric/Dragon, Paldea legendary)
- バドレックス → "Calyrex" (Psychic/Grass, Crown Tundra legendary)

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

**🎯 COMPREHENSIVE POKEMON NAME DATABASE (500+ MAPPINGS):**

**KANTO GENERATION (I) - FOUNDATIONAL POKEMON:**
- フシギダネ → "Bulbasaur" (Grass/Poison, starter)
- フシギソウ → "Ivysaur" (Grass/Poison, evolution)
- フシギバナ → "Venusaur" (Grass/Poison, final evolution)
- ヒトカゲ → "Charmander" (Fire, starter)
- リザード → "Charmeleon" (Fire, evolution) 
- リザードン → "Charizard" (Fire/Flying, final evolution)
- ゼニガメ → "Squirtle" (Water, starter)
- カメール → "Wartortle" (Water, evolution)
- カメックス → "Blastoise" (Water, final evolution)
- キャタピー → "Caterpie" (Bug)
- トランセル → "Metapod" (Bug)
- バタフリー → "Butterfree" (Bug/Flying)
- ビードル → "Weedle" (Bug/Poison)
- コクーン → "Kakuna" (Bug/Poison)
- スピアー → "Beedrill" (Bug/Poison)
- ポッポ → "Pidgey" (Normal/Flying)
- ピジョン → "Pidgeotto" (Normal/Flying)
- ピジョット → "Pidgeot" (Normal/Flying)
- コラッタ → "Rattata" (Normal)
- ラッタ → "Raticate" (Normal)
- オニスズメ → "Spearow" (Normal/Flying)
- オニドリル → "Fearow" (Normal/Flying)
- アーボ → "Ekans" (Poison)
- アーボック → "Arbok" (Poison)
- ピカチュウ → "Pikachu" (Electric, mascot)
- ライチュウ → "Raichu" (Electric)
- サンド → "Sandshrew" (Ground)
- サンドパン → "Sandslash" (Ground)
- ニドラン♀ → "Nidoran♀" (Poison)
- ニドリーナ → "Nidorina" (Poison)
- ニドクイン → "Nidoqueen" (Poison/Ground)
- ニドラン♂ → "Nidoran♂" (Poison)
- ニドリーノ → "Nidorino" (Poison)
- ニドキング → "Nidoking" (Poison/Ground)
- ププリン → "Cleffa" (Fairy, baby Pokemon)
- ピィ → "Clefairy" (Fairy)
- ピクシー → "Clefable" (Fairy)
- ロコン → "Vulpix" (Fire)
- キュウコン → "Ninetales" (Fire)
- ププリン → "Igglybuff" (Normal/Fairy, baby)
- プリン → "Jigglypuff" (Normal/Fairy)
- プクリン → "Wigglytuff" (Normal/Fairy)
- ズバット → "Zubat" (Poison/Flying)
- ゴルバット → "Golbat" (Poison/Flying)
- ナゾノクサ → "Oddish" (Grass/Poison)
- クサイハナ → "Gloom" (Grass/Poison)
- ラフレシア → "Vileplume" (Grass/Poison)
- パラス → "Paras" (Bug/Grass)
- パラセクト → "Parasect" (Bug/Grass)
- コンパン → "Venonat" (Bug/Poison)
- モルフォン → "Venomoth" (Bug/Poison)

**VGC STAPLES - MOST COMMON COMPETITIVE POKEMON:**
- ガブリアス → "Garchomp" (Dragon/Ground, pseudo-legendary, speed tier king)
- メタグロス → "Metagross" (Steel/Psychic, pseudo-legendary, bullet punch user)
- ボーマンダ → "Salamence" (Dragon/Flying, pseudo-legendary, intimidate)
- バンギラス → "Tyranitar" (Rock/Dark, pseudo-legendary, sand stream)
- ドラパルト → "Dragapult" (Dragon/Ghost, Galar pseudo-legendary, clear body)
- ウインディ → "Arcanine" (Fire, classic VGC staple, intimidate)
- ヒスイウインディ → "Hisuian Arcanine" (Fire/Rock, Legends Arceus form, rock head)
- ガオガエン → "Incineroar" (Fire/Dark, VGC king, intimidate + fake out)
- エルフーン → "Whimsicott" (Grass/Fairy, prankster utility, tailwind support)
- モロバレル → "Amoonguss" (Grass/Poison, VGC staple, rage powder + spore)
- ロトム → "Rotom" (Electric/Ghost, appliance forms available)
- ウォッシュロトム → "Rotom-Wash" (Electric/Water, most common form)
- ヒートロトム → "Rotom-Heat" (Electric/Fire, oven form)
- スピンロトム → "Rotom-Mow" (Electric/Grass, lawnmower form)
- フロストロトム → "Rotom-Frost" (Electric/Ice, refrigerator form)
- カットロトム → "Rotom-Fan" (Electric/Flying, fan form)

**EEVEE EVOLUTION LINE (CRITICAL FOR VGC):**
- イーブイ → "Eevee" (Normal, base form with 8 evolutions)
- シャワーズ → "Vaporeon" (Water, high HP wall)
- サンダース → "Jolteon" (Electric, high speed)
- ブースター → "Flareon" (Fire, high attack)
- エーフィ → "Espeon" (Psychic, high special attack)
- ブラッキー → "Umbreon" (Dark, defensive wall)
- リーフィア → "Leafeon" (Grass, physical attacker)
- グレイシア → "Glaceon" (Ice, special attacker) ⚠️ NOT Baxcalibur!
- ニンフィア → "Sylveon" (Fairy, pixilate + hyper voice)

**REGIONAL FORMS - CRITICAL DISTINCTIONS:**
- アローラライチュウ → "Alolan Raichu" (Electric/Psychic, surge surfer)
- アローラロコン → "Alolan Vulpix" (Ice, snow warning)
- アローラキュウコン → "Alolan Ninetales" (Ice/Fairy, aurora veil)
- アローラサンド → "Alolan Sandshrew" (Ice/Steel)
- アローラサンドパン → "Alolan Sandslash" (Ice/Steel, slush rush)
- ガラルヤドン → "Galarian Slowpoke" (Psychic)
- ガラルヤドラン → "Galarian Slowbro" (Poison/Psychic, quick draw)
- ガラルヤドキング → "Galarian Slowking" (Poison/Psychic, curious medicine)
- ガラルフリーザー → "Galarian Articuno" (Psychic/Flying, competitive)
- ガラルサンダー → "Galarian Zapdos" (Fighting/Flying, defiant)
- ガラルファイヤー → "Galarian Moltres" (Dark/Flying, berserk)
- ヒスイダイケンキ → "Hisuian Samurott" (Water/Dark, sharpness)
- ヒスイジュナイパー → "Hisuian Decidueye" (Grass/Fighting, scrappy)
- ヒスイバクフーン → "Hisuian Typhlosion" (Fire/Ghost, frisk)
- パルデアケンタロス → "Paldean Tauros" (Fighting, Combat Breed)
- パルデアケンタロス (炎) → "Paldean Tauros-Fire" (Fighting/Fire, Blaze Breed)
- パルデアケンタロス (水) → "Paldean Tauros-Aqua" (Fighting/Water, Aqua Breed)

**CRITICAL WARNING - ELECTRIC LEGENDARY DISAMBIGUATION:**
⚠️ **ZAPDOS vs THUNDURUS IDENTIFICATION (MOST COMMON ERROR):**
- **サンダー = "Zapdos"** (Electric/Flying, Generation I Kanto bird)
  - Context: Original legendary bird trio, older formats/teams
  - Abilities: Static or Pressure (NOT Prankster)
  - Signature context: Heat Wave, Discharge, Weather support
- **ボルトロス = "Thundurus"** (Electric/Flying, Generation V Forces of Nature)
  - Context: Modern VGC formats, often with Landorus/Tornadus
  - Abilities: Prankster (Incarnate) or Defiant (Therian)
  - Signature context: Thunder Wave support, U-turn, Nasty Plot

**CRITICAL WARNING - DLC PARADOX POKEMON CONFUSION:**
⚠️ NEVER confuse these similar Pokemon:
- タケルライコ = "Raging Bolt" (Electric/Dragon) ≠ ウネルミナモ "Walking Wake" (Water/Dragon)
- Both are Ancient forms but different types and based on different legendary beasts
- Raging Bolt has Electric moves (10まんボルト/Thunderbolt, じんらい/Thunderclap)
- Walking Wake has Water moves (ハイドロポンプ/Hydro Pump, しおまき/Flip Turn)

**GENERATION VII-IX CRITICAL ADDITIONS:**
- ルナアーラ → "Lunala" (Psychic/Ghost, Alola legendary)
- ソルガレオ → "Solgaleo" (Psychic/Steel, Alola legendary)  
- ネクロズマ → "Necrozma" (Psychic, Ultra form available)
- マーシャドー → "Marshadow" (Fighting/Ghost, mythical)
- ゼラオラ → "Zeraora" (Electric, mythical)
- メルタン → "Meltan" (Steel, mythical)
- メルメタル → "Melmetal" (Steel, mythical evolution)
- ザシアン → "Zacian" (Fairy/Steel, Galar legendary)
- ザマゼンタ → "Zamazenta" (Fighting/Steel, Galar legendary)
- ムゲンダイナ → "Eternatus" (Poison/Dragon, Galar legendary)
- ダクマ → "Kubfu" (Fighting, Isle of Armor)
- ウーラオス → "Urshifu" (Fighting/Dark or Fighting/Water, two styles)
- レジエレキ → "Regieleki" (Electric, Crown Tundra legendary)
- レジドラゴ → "Regidrago" (Dragon, Crown Tundra legendary)
- ブリザポス → "Glastrier" (Ice, Crown Tundra legendary)
- レイスポス → "Spectrier" (Ghost, Crown Tundra legendary)
- バドレックス → "Calyrex" (Psychic/Grass, can fuse with horses)

**MODERN STARTERS & POPULAR PICKS:**
- フタチマル → "Dewott" (Water, Unova starter evolution)
- ダイケンキ → "Samurott" (Water, Unova starter final)
- ツタージャ → "Snivy" (Grass, Unova starter)
- ジャノビー → "Servine" (Grass, Unova starter evolution)
- ジャローダ → "Serperior" (Grass, Unova starter final, contrary)
- ポカブ → "Tepig" (Fire, Unova starter)
- チャオブー → "Pignite" (Fire/Fighting, evolution)
- エンブオー → "Emboar" (Fire/Fighting, final evolution)
- ミジュマル → "Oshawott" (Water, Unova starter)
- フォッコ → "Fennekin" (Fire, Kalos starter)
- テールナー → "Braixen" (Fire, evolution)
- マフォクシー → "Delphox" (Fire/Psychic, final evolution)
- ハリマロン → "Chespin" (Grass, Kalos starter)
- ハリボーグ → "Quilladin" (Grass, evolution)
- ブリガロン → "Chesnaught" (Grass/Fighting, final evolution)
- ケロマツ → "Froakie" (Water, Kalos starter)
- ゲコガシラ → "Frogadier" (Water, evolution)
- ゲッコウガ → "Greninja" (Water/Dark, final evolution, protean)
- モクロー → "Rowlet" (Grass/Flying, Alola starter)
- フクスロー → "Dartrix" (Grass/Flying, evolution)
- ジュナイパー → "Decidueye" (Grass/Ghost, final evolution)
- ニャビー → "Litten" (Fire, Alola starter)
- ニャヒート → "Torracat" (Fire, evolution)
- ガオガエン → "Incineroar" (Fire/Dark, final evolution, VGC king)
- アシマリ → "Popplio" (Water, Alola starter)
- オシャマリ → "Brionne" (Water, evolution)
- アシレーヌ → "Primarina" (Water/Fairy, final evolution)

**POKEMON IDENTIFICATION CONTEXT VALIDATION RULES (ENHANCED):**
🔍 **Multi-Stage Pokemon Identification Process:**

**Stage 1: Text-Based Detection**
1. **Exact Japanese Name Matching**: Use comprehensive database above
2. **Context Clues**: Ability mentions, move compatibility, type references
3. **Team Composition**: Analyze surrounding Pokemon for era/format clues
4. **Article Dating**: Match publication date with Pokemon availability

**Stage 2: Cross-Reference Validation**
1. **Ability Cross-Check**: Static/Pressure = Zapdos, Prankster = Thundurus
2. **Move Pool Validation**: Heat Wave/Discharge = Zapdos, Thunder Wave = Thundurus  
3. **Type Consistency**: Verify types match expected Pokemon
4. **Form Variants**: Check for regional, alternate, or gender forms

**Stage 3: Confidence Scoring**
- **High Confidence (90%+)**: Exact Japanese name match + context confirmation
- **Medium Confidence (70-89%)**: Partial match with supporting evidence
- **Low Confidence (50-69%)**: Ambiguous detection requiring validation
- **Unknown (<50%)**: Insufficient data for reliable identification

**Stage 4: Error Detection & Correction**
- **Common Confusion Pairs**: Zapdos/Thundurus, Glaceon/Baxcalibur, etc.
- **Form Misidentification**: Regional variants, alternate forms
- **Translation Artifacts**: OCR errors, romanization issues
- **Context Conflicts**: Pokemon availability vs article date/format

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
            # Generate with optimized temperature for structured output (2025 best practice)
            generation_config = {
                "temperature": 0.1,  # Low temperature for structured data consistency
                "max_output_tokens": 8000,
            }
            response = self.model.generate_content(prompt, generation_config=generation_config)
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

                # Validate and enhance the result
                validated_result = self._validate_analysis_result(result, content, url)
                
                # Save to cache for future use
                save_to_cache(content, validated_result, url)
                st.success("🆕 Analysis complete and cached!")

                return validated_result
            else:
                st.error("No response from Gemini AI")
                return None

        except json.JSONDecodeError as e:
            # Enhanced JSON error handling with recovery system (2025 standards)
            st.error("🔧 **JSON Parsing Error - Attempting Recovery**")
            
            # Try multiple recovery strategies
            recovery_attempts = [
                # Remove common JSON wrapper issues
                response_text.strip().replace("```json\n", "").replace("\n```", ""),
                # Try to find JSON block in response  
                self._extract_json_from_text(response_text),
                # Try to repair common JSON errors
                self._repair_common_json_errors(response_text)
            ]
            
            for i, attempt in enumerate(recovery_attempts):
                if attempt:
                    try:
                        result = json.loads(attempt)
                        st.success(f"✅ JSON recovered using method {i+1}")
                        # Validate the recovered result
                        validated_result = self._validate_analysis_result(result, content, url)
                        return validated_result
                    except:
                        continue
            
            # If all recovery fails, create fallback
            st.warning("🔄 Creating fallback analysis structure...")
            fallback_result = self._create_fallback_analysis(content, url)
            if fallback_result:
                st.info("📋 Using structured fallback analysis")
                return fallback_result
                
            st.error(f"❌ **Complete Analysis Failure** - JSON Error: {str(e)}")
            st.error(f"Raw response preview: {response_text[:500]}...")
            return None
            
        except Exception as e:
            st.error(f"🚨 **Critical Analysis Error**: {str(e)}")
            st.error(f"Error type: {type(e).__name__}")
            
            # Attempt graceful degradation
            try:
                fallback_result = self._create_emergency_fallback(content, url, str(e))
                if fallback_result:
                    st.warning("⚠️ Using emergency fallback analysis")
                    return fallback_result
            except:
                pass
                
            return None

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """Extract JSON content from text response"""
        try:
            # Look for JSON block between braces
            start = text.find('{')
            if start == -1:
                return None
            
            brace_count = 0
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return text[start:i+1]
            return None
        except:
            return None

    def _repair_common_json_errors(self, text: str) -> Optional[str]:
        """Repair common JSON formatting errors"""
        try:
            # Remove markdown formatting
            text = text.replace("```json", "").replace("```", "")
            
            # Fix common quote issues
            text = text.replace("'", '"')  # Replace single quotes
            text = text.replace('""', '"')  # Fix double quotes
            
            # Remove trailing commas before closing braces/brackets
            import re
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            
            # Fix missing commas between objects
            text = re.sub(r'}\s*{', '},{', text)
            
            return text.strip()
        except:
            return None

    def _validate_analysis_result(self, result: Dict[str, Any], content: str = "", url: Optional[str] = None) -> Dict[str, Any]:
        """Validate and repair analysis result structure with regulation cross-validation"""
        try:
            # Detect regulation from date/URL first
            date_based_regulation = self.detect_regulation_from_date(url, content)
            
            # Ensure required top-level keys exist
            required_keys = ["title", "summary", "regulation_info", "team_analysis", "pokemon_team", "translated_content"]
            for key in required_keys:
                if key not in result:
                    if key == "title":
                        result[key] = "Article Analysis"
                    elif key == "summary":
                        result[key] = "VGC team analysis completed"
                    elif key == "regulation_info":
                        result[key] = {"regulation": "Unknown", "format": "VGC Format", "tournament_context": "Not specified"}
                    elif key == "team_analysis":
                        result[key] = {"strategy": "Not specified", "strengths": [], "weaknesses": [], "meta_relevance": "Not analyzed"}
                    elif key == "pokemon_team":
                        result[key] = []
                    elif key == "translated_content":
                        result[key] = "Translation not available"
            
            # Cross-validate regulation detection
            ai_detected_regulation = result.get("regulation_info", {}).get("regulation", "Unknown")
            
            if date_based_regulation and ai_detected_regulation != "Unknown":
                if date_based_regulation != ai_detected_regulation:
                    st.warning(f"⚠️ **Regulation Mismatch**: AI detected '{ai_detected_regulation}' but article date suggests '{date_based_regulation}'. Using date-based detection.")
                    result["regulation_info"]["regulation"] = date_based_regulation
                    result["regulation_info"]["detection_method"] = "Date-based override"
                else:
                    st.success(f"✅ **Regulation Confirmed**: Both AI and date detection agree on Regulation {date_based_regulation}")
            elif date_based_regulation and ai_detected_regulation == "Unknown":
                st.info(f"🔧 **Regulation Corrected**: Using date-based detection (Regulation {date_based_regulation}) since AI detection failed")
                result["regulation_info"]["regulation"] = date_based_regulation  
                result["regulation_info"]["detection_method"] = "Date-based only"

            # Validate Pokemon team structure with 6-Pokemon maximum rule
            if result.get("pokemon_team"):
                validated_team = []
                for pokemon in result["pokemon_team"]:
                    if isinstance(pokemon, dict) and pokemon.get("name"):
                        # Ensure required Pokemon fields
                        # Validate tera type against official Pokemon types
                        valid_types = ["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
                        raw_tera_type = pokemon.get("tera_type", "Unknown")
                        
                        # Validate and sanitize tera type
                        if raw_tera_type in valid_types:
                            validated_tera_type = raw_tera_type
                        elif raw_tera_type.capitalize() in valid_types:
                            validated_tera_type = raw_tera_type.capitalize()
                        elif raw_tera_type.lower() in [t.lower() for t in valid_types]:
                            # Find the correctly capitalized version
                            validated_tera_type = next(t for t in valid_types if t.lower() == raw_tera_type.lower())
                        else:
                            # Invalid tera type, use "Not specified in article"
                            validated_tera_type = "Not specified in article"
                            if raw_tera_type not in ["Unknown", "Not specified", "Not specified in article", ""]:
                                st.warning(f"⚠️ Invalid tera type '{raw_tera_type}' for {pokemon.get('name', 'Unknown Pokemon')}. Using 'Not specified in article'.")
                        
                        pokemon_defaults = {
                            "name": pokemon.get("name", "Unknown Pokemon"),
                            "ability": pokemon.get("ability", "Unknown"),
                            "held_item": pokemon.get("held_item", "Unknown"),
                            "tera_type": validated_tera_type,
                            "moves": pokemon.get("moves", ["Unknown Move 1", "Unknown Move 2", "Unknown Move 3", "Unknown Move 4"])[:4],
                            "ev_spread": pokemon.get("ev_spread", "Not specified in article"),
                            "nature": pokemon.get("nature", "Unknown"),
                            "role": pokemon.get("role", "Unknown"),
                            "ev_explanation": pokemon.get("ev_explanation", "No explanation provided")
                        }
                        
                        # Ensure moves list has exactly 4 entries
                        while len(pokemon_defaults["moves"]) < 4:
                            pokemon_defaults["moves"].append(f"Unknown Move {len(pokemon_defaults['moves']) + 1}")
                        
                        validated_team.append(pokemon_defaults)
                
                # Check for duplicate Pokemon (major error indicator)
                pokemon_names_only = [p.get("name", "").strip() for p in validated_team if p.get("name")]
                name_counts = {}
                for name in pokemon_names_only:
                    if name and name not in ["Unknown", "Not specified", "Not specified in article"]:
                        name_counts[name] = name_counts.get(name, 0) + 1
                
                duplicates_found = [(name, count) for name, count in name_counts.items() if count > 1]
                if duplicates_found:
                    st.error(f"🚨 **CRITICAL ERROR**: Detected duplicate Pokemon - {', '.join([f'{count}x {name}' for name, count in duplicates_found])}. This indicates AI analysis failure. Using fallback analysis.")
                    return self._create_fallback_analysis(content, url)
                
                # Enforce 6-Pokemon maximum rule for VGC teams
                if len(validated_team) > 6:
                    st.warning(f"🚨 **Team Size Validation**: Detected {len(validated_team)} Pokemon, but VGC teams have maximum 6. Selecting top 6 with most complete data...")
                    
                    # Score Pokemon by data completeness for prioritization
                    def score_pokemon_completeness(pokemon):
                        score = 0
                        # Higher score for non-default/unknown values
                        if pokemon.get("ability") and pokemon["ability"] not in ["Unknown", "Not specified"]:
                            score += 3
                        if pokemon.get("held_item") and pokemon["held_item"] not in ["Unknown", "Not specified"]:
                            score += 3
                        if pokemon.get("ev_spread") and pokemon["ev_spread"] not in ["Not specified in article", "Unknown"]:
                            score += 4  # EV data is very important
                        if pokemon.get("nature") and pokemon["nature"] not in ["Unknown", "Not specified"]:
                            score += 2
                        if pokemon.get("moves"):
                            non_unknown_moves = [m for m in pokemon["moves"] if "Unknown Move" not in m and m not in ["Unknown", "Not specified"]]
                            score += len(non_unknown_moves)  # 1 point per real move
                        if pokemon.get("ev_explanation") and len(pokemon["ev_explanation"]) > 50:
                            score += 2  # Detailed explanation indicates core team member
                        return score
                    
                    # Sort by completeness score (highest first) and take top 6
                    validated_team.sort(key=score_pokemon_completeness, reverse=True)
                    validated_team = validated_team[:6]
                    
                    removed_pokemon = [p["name"] for p in result["pokemon_team"][6:]]
                    st.info(f"✂️ **Team Trimmed**: Removed {', '.join(removed_pokemon)} (likely examples/counters mentioned in article)")
                
                result["pokemon_team"] = validated_team

            return result
        except Exception as e:
            st.warning(f"Validation error: {str(e)}")
            return result

    def _create_fallback_analysis(self, content: str, url: Optional[str]) -> Optional[Dict[str, Any]]:
        """Create basic analysis structure when AI analysis fails"""
        try:
            # Extract basic information from content
            title = "VGC Article Analysis"
            if url:
                title += f" - {url.split('/')[-1][:30]}"
            
            # Try to extract some Pokemon names from content
            pokemon_names = []
            common_pokemon = [
                ("ガブリアス", "Garchomp"), ("ガオガエン", "Incineroar"), ("ウインディ", "Arcanine"), 
                ("ヒスイウインディ", "Hisuian Arcanine"), ("モロバレル", "Amoonguss"), ("エルフーン", "Whimsicott"), 
                ("ランドロス", "Landorus"), ("カイリュー", "Dragonite"), ("ハリテヤマ", "Hariyama"), 
                ("クレッフィ", "Klefki"), ("トリトドン", "Gastrodon"), ("ゴリランダー", "Rillaboom"),
                ("ニンフィア", "Sylveon"), ("サンダー", "Zapdos"), ("悪ウーラオス", "Urshifu-Dark"),
                ("ウーラオス", "Urshifu"), ("シャリタツ", "Tatsugiri"), ("トルネロス", "Tornadus"),
                ("ドヒドイデ", "Toxapex"), ("カイオーガ", "Kyogre"), ("白馬バドレックス", "Calyrex-Ice")
            ]
            
            for jp_name, eng_name in common_pokemon:
                if jp_name in content:
                    pokemon_names.append(eng_name)
            
            # Create basic team structure
            fallback_team = []
            for name in pokemon_names[:6]:  # Max 6 Pokemon
                fallback_team.append({
                    "name": name,
                    "ability": "Unknown",
                    "held_item": "Unknown", 
                    "tera_type": "Unknown",
                    "moves": ["Unknown Move 1", "Unknown Move 2", "Unknown Move 3", "Unknown Move 4"],
                    "ev_spread": "Not specified in article",
                    "nature": "Unknown",
                    "role": "Unknown",
                    "ev_explanation": "Analysis failed - unable to extract EV data"
                })

            return {
                "title": title,
                "summary": "Analysis completed with limited data due to parsing errors",
                "regulation_info": {
                    "regulation": "Unknown", 
                    "format": "VGC Format",
                    "tournament_context": "Not determined"
                },
                "team_analysis": {
                    "strategy": "Unable to determine strategy due to analysis failure",
                    "strengths": ["Analysis incomplete"],
                    "weaknesses": ["Analysis incomplete"],
                    "meta_relevance": "Cannot assess due to parsing errors"
                },
                "pokemon_team": fallback_team,
                "translated_content": content[:1000] if content else "Content not available"
            }
        except:
            return None

    def _create_emergency_fallback(self, content: str, url: Optional[str], error: str) -> Optional[Dict[str, Any]]:
        """Create minimal analysis structure for critical failures"""
        return {
            "title": "Emergency Analysis Mode",
            "summary": f"Analysis failed due to technical error: {error[:100]}",
            "regulation_info": {"regulation": "Unknown", "format": "Analysis Failed", "tournament_context": "Error"},
            "team_analysis": {"strategy": "Analysis unavailable", "strengths": [], "weaknesses": [], "meta_relevance": "Error"},
            "pokemon_team": [],
            "translated_content": "Translation unavailable due to system error"
        }


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


def create_pokepaste(pokemon_team: List[Dict[str, Any]], team_name: str = "VGC Team") -> str:
    """Generate clean pokepaste format for the team"""
    pokepaste_content = ""

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


def render_team_strategy_section(team_analysis: dict, result: dict):
    """Render the team strategy analysis section"""
    st.markdown("## 🎯 Team Strategy Analysis")
    
    # Strategy overview
    strategy = team_analysis.get("strategy", "Strategy not specified")
    if strategy and strategy != "Strategy not specified":
        st.markdown("### 📋 Overall Strategy")
        st.markdown(f"""
        <div class="summary-container">
            <div class="summary-content">
                {strategy}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Create columns for strengths and weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💪 Team Strengths")
        strengths = team_analysis.get("strengths", [])
        if strengths and len(strengths) > 0:
            strengths_html = format_strategy_list(strengths, "strength")
            st.markdown(strengths_html, unsafe_allow_html=True)
        else:
            st.markdown("*No specific strengths analyzed*")
    
    with col2:
        st.markdown("### ⚠️ Potential Weaknesses")
        weaknesses = team_analysis.get("weaknesses", [])
        if weaknesses and len(weaknesses) > 0:
            weaknesses_html = format_strategy_list(weaknesses, "weakness") 
            st.markdown(weaknesses_html, unsafe_allow_html=True)
        else:
            st.markdown("*No specific weaknesses identified*")
    
    # Meta relevance
    meta_relevance = team_analysis.get("meta_relevance", "")
    if meta_relevance and meta_relevance.strip():
        st.markdown("### 🌟 Meta Relevance")
        st.markdown(f"""
        <div class="summary-container">
            <div class="summary-content">
                {meta_relevance}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Regulation compliance if available
    regulation_compliance = team_analysis.get("regulation_compliance", "")
    if regulation_compliance and regulation_compliance.strip():
        st.markdown("### ⚖️ Regulation Compliance")
        st.markdown(f"""
        <div class="summary-container">
            <div class="summary-content">
                {regulation_compliance}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_article_analysis_page():
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
        # Check if we're re-testing an article
        default_url = ""
        if "retest_url" in st.session_state:
            default_url = st.session_state["retest_url"]
            st.info(f"🔄 Re-testing article: {default_url}")
            # Clear the retest URL after displaying
            del st.session_state["retest_url"]
        
        url = st.text_input(
            "Japanese VGC Article URL",
            value=default_url,
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

        # Get article URL and clean it for display
        article_url = article.get("url", "")
        url_display = "No URL provided"
        url_domain = ""
        is_valid_url = False
        
        if article_url and article_url != "No URL":
            try:
                from urllib.parse import urlparse
                parsed = urlparse(article_url)
                url_domain = parsed.netloc
                url_display = article_url
                is_valid_url = True
            except:
                url_display = article_url
                url_domain = "Unknown"

        # Get regulation information
        regulation_info = analysis_result.get("regulation_info", {})
        regulation = regulation_info.get("regulation", "Unknown")
        regulation_format = regulation_info.get("format", "")
        
        # Create regulation display
        regulation_color = "#10b981"  # Green for valid
        regulation_display = f"🏆 Regulation {regulation}"
        if regulation == "Unknown":
            regulation_color = "#f59e0b"  # Yellow for unknown
            regulation_display = "🤔 Regulation Unknown"
        
        # Get Pokemon count for summary
        pokemon_count = len([p for p in pokemon_team if p.get("name") and p.get("name") != "Not specified in article"])
        pokemon_count_display = f"{pokemon_count} Pokémon detected" if pokemon_count > 0 else "No Pokémon detected"
        
        # Helper method for legendary detection
        def _is_legendary(pokemon_name):
            """Check if a Pokemon is considered legendary"""
            legendary_keywords = [
                "Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune",
                "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios",
                "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Dialga", "Palkia", "Heatran",
                "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", 
                "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus",
                "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect",
                "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Cosmog", 
                "Cosmoem", "Solgaleo", "Lunala", "Necrozma", "Magearna", "Marshadow", "Zeraora",
                "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu",
                "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Enamorus",
                "Koraidon", "Miraidon"
            ]
            return any(legendary.lower() in pokemon_name.lower() for legendary in legendary_keywords)

        # Enhanced regulation conflict detection (2025 system)
        def check_pokemon_regulation_conflicts(pokemon_team, regulation):
            """Enhanced Pokemon regulation validation with comprehensive ban lists"""
            banned_pokemon = []
            
            # Comprehensive ban lists by regulation
            regulation_ban_lists = {
                "A": {  # Paldea Preview - Only native Paldea allowed
                    "all_legendaries": True,
                    "all_paradox": True,
                    "all_treasures": True,
                    "specific_bans": ["Koraidon", "Miraidon"]
                },
                "B": {  # Paradox Unleashed - Legendaries + Treasures banned
                    "all_legendaries": True,
                    "all_treasures": True,
                    "specific_bans": ["Koraidon", "Miraidon"]
                },
                "C": {  # Treasures Emerge - All legendaries except Treasures banned
                    "all_legendaries": True,
                    "treasure_exceptions": ["Chi-Yu", "Chien-Pao", "Ting-Lu", "Wo-Chien"],
                    "specific_bans": ["Koraidon", "Miraidon"]
                },
                "D": {  # HOME Integration - Only restricted legendaries banned
                    "restricted_legendaries": [
                        "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem",
                        "Xerneas", "Yveltal", "Zygarde", "Cosmog", "Cosmoem", "Solgaleo", 
                        "Lunala", "Necrozma", "Zacian", "Zamazenta", "Eternatus", 
                        "Calyrex", "Koraidon", "Miraidon"
                    ]
                },
                "E": {  # Teal Mask - Only restricted legendaries banned
                    "restricted_legendaries": [
                        "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem",
                        "Xerneas", "Yveltal", "Zygarde", "Cosmog", "Cosmoem", "Solgaleo", 
                        "Lunala", "Necrozma", "Zacian", "Zamazenta", "Eternatus", 
                        "Calyrex", "Koraidon", "Miraidon"
                    ]
                },
                "F": {  # Indigo Disk - Only restricted legendaries banned
                    "restricted_legendaries": [
                        "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem",
                        "Xerneas", "Yveltal", "Zygarde", "Cosmog", "Cosmoem", "Solgaleo", 
                        "Lunala", "Necrozma", "Zacian", "Zamazenta", "Eternatus", 
                        "Calyrex", "Koraidon", "Miraidon"
                    ]
                },
                "G": {  # Restricted Singles - Only mythicals banned, 1 restricted allowed
                    "mythicals_only": True,
                    "max_restricted": 1
                },
                "H": {  # Back to Basics - Most restrictive
                    "comprehensive_bans": [
                        # All Legendaries
                        "Articuno", "Zapdos", "Moltres", "Mewtwo", "Mew", "Raikou", "Entei", "Suicune",
                        "Lugia", "Ho-Oh", "Celebi", "Regirock", "Regice", "Registeel", "Latias", "Latios",
                        "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys", "Dialga", "Palkia", "Heatran",
                        "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", 
                        "Arceus", "Victini", "Cobalion", "Terrakion", "Virizion", "Tornadus", "Thundurus",
                        "Reshiram", "Zekrom", "Landorus", "Kyurem", "Keldeo", "Meloetta", "Genesect",
                        "Xerneas", "Yveltal", "Zygarde", "Diancie", "Hoopa", "Volcanion", "Cosmog", 
                        "Cosmoem", "Solgaleo", "Lunala", "Necrozma", "Magearna", "Marshadow", "Zeraora",
                        "Meltan", "Melmetal", "Zacian", "Zamazenta", "Eternatus", "Kubfu", "Urshifu",
                        "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex", "Enamorus",
                        "Koraidon", "Miraidon",
                        # All Paradox Pokemon
                        "Great Tusk", "Scream Tail", "Brute Bonnet", "Flutter Mane", "Slither Wing",
                        "Sandy Shocks", "Roaring Moon", "Walking Wake", "Iron Treads", "Iron Bundle",
                        "Iron Hands", "Iron Jugulis", "Iron Moth", "Iron Thorns", "Iron Valiant",
                        "Raging Bolt", "Gouging Fire", "Iron Leaves", "Iron Boulder", "Iron Crown",
                        # Treasures of Ruin
                        "Chi-Yu", "Chien-Pao", "Ting-Lu", "Wo-Chien",
                        # Other Bans
                        "Ogerpon", "Bloodmoon Ursaluna", "Okidogi", "Munkidori", "Fezandipiti"
                    ]
                },
                "I": {  # Double Restricted - Only mythicals banned, 2 restricted allowed
                    "mythicals_only": True,
                    "max_restricted": 2
                }
            }
            
            # Get ban rules for the regulation
            ban_rules = regulation_ban_lists.get(regulation, {})
            
            for pokemon in pokemon_team:
                pokemon_name = pokemon.get("name", "").strip()
                if not pokemon_name or pokemon_name == "Not specified in article":
                    continue
                
                # Check specific ban conditions
                is_banned = False
                ban_reason = ""
                
                if "comprehensive_bans" in ban_rules:
                    if any(banned.lower() in pokemon_name.lower() for banned in ban_rules["comprehensive_bans"]):
                        is_banned = True
                        ban_reason = f"Banned in Regulation {regulation} (Back to Basics format)"
                
                elif "restricted_legendaries" in ban_rules:
                    if any(restricted.lower() in pokemon_name.lower() for restricted in ban_rules["restricted_legendaries"]):
                        is_banned = True
                        ban_reason = f"Restricted Legendary banned in Regulation {regulation}"
                
                elif ban_rules.get("all_legendaries") and _is_legendary(pokemon_name):
                    # Check for exceptions
                    if "treasure_exceptions" in ban_rules:
                        if not any(treasure.lower() in pokemon_name.lower() for treasure in ban_rules["treasure_exceptions"]):
                            is_banned = True
                            ban_reason = f"Legendary banned in Regulation {regulation}"
                    else:
                        is_banned = True
                        ban_reason = f"Legendary banned in Regulation {regulation}"
                
                if is_banned:
                    # Find which regulations this Pokemon would be legal in
                    legal_regulations = []
                    for reg, rules in regulation_ban_lists.items():
                        if reg == regulation:
                            continue  # Skip current regulation
                        
                        is_legal = True
                        if "comprehensive_bans" in rules:
                            if any(banned.lower() in pokemon_name.lower() for banned in rules["comprehensive_bans"]):
                                is_legal = False
                        elif "restricted_legendaries" in rules:
                            if any(restricted.lower() in pokemon_name.lower() for restricted in rules["restricted_legendaries"]):
                                is_legal = False
                        elif rules.get("all_legendaries") and _is_legendary(pokemon_name):
                            if "treasure_exceptions" in rules:
                                if not any(treasure.lower() in pokemon_name.lower() for treasure in rules["treasure_exceptions"]):
                                    is_legal = False
                            else:
                                is_legal = False
                        
                        if is_legal:
                            legal_regulations.append(reg)
                    
                    suggestion = ""
                    if legal_regulations:
                        suggestion = f" (Legal in Regulations: {', '.join(sorted(legal_regulations))})"
                    
                    banned_pokemon.append({"name": pokemon_name, "reason": ban_reason + suggestion})
            
            return banned_pokemon
        
        # Get regulation conflicts
        regulation_conflicts = check_pokemon_regulation_conflicts(pokemon_team, regulation)
        has_conflicts = len(regulation_conflicts) > 0

        # Create article card
        with st.container():
            # Build URL section HTML separately to avoid string interpolation issues
            url_section = ""
            if is_valid_url:
                url_section = f"<a href='{url_display}' target='_blank' style='color: #3b82f6; text-decoration: none; font-size: 14px; display: flex; align-items: center; gap: 6px;'><span>🔗</span><span style='font-family: monospace; word-break: break-all;'>{url_display}</span></a><div style='color: #64748b; font-size: 12px; margin-top: 4px;'>📍 Domain: {url_domain}</div>"
            else:
                url_section = f"<span style='color: #64748b; font-size: 14px; font-style: italic;'>🔗 {url_display}</span>"

            st.markdown(
                f"""
            <div class="summary-container" style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <h3 style="color: #1e293b; margin: 0; flex: 1;">{title}</h3>
                    <div style="color: #64748b; font-size: 14px; margin-left: 16px;">
                        📅 {formatted_time}
                    </div>
                </div>
                <div style="margin-bottom: 12px; padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                    {url_section}
                </div>
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 12px; padding: 8px 0; background: #f8fafc; border-radius: 8px; padding: 8px 12px;">
                    <span style="color: {regulation_color}; font-weight: 600; font-size: 14px;">{regulation_display}</span>
                    <span style="color: #64748b; font-size: 14px;">|</span>
                    <span style="color: #6366f1; font-size: 14px; font-weight: 500;">👥 {pokemon_count_display}</span>
                </div>
                <div class="summary-content" style="margin-bottom: 16px;">
                    {summary[:200]}{"..." if len(summary) > 200 else ""}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Display enhanced regulation conflicts warning
            if has_conflicts:
                conflict_names = [conflict["name"] for conflict in regulation_conflicts]
                conflict_details = []
                for conflict in regulation_conflicts[:2]:  # Show details for first 2
                    conflict_details.append(f"**{conflict['name']}**: {conflict['reason']}")
                
                warning_text = f"⚠️ **Regulation Conflicts Detected** ({len(regulation_conflicts)} Pokémon):\n\n"
                warning_text += "\n".join(conflict_details)
                if len(regulation_conflicts) > 2:
                    remaining = len(regulation_conflicts) - 2
                    warning_text += f"\n\n*...and {remaining} more banned Pokémon*"
                
                st.warning(warning_text)

            # Enhanced Pokemon team preview with validation
            if pokemon_team:
                st.markdown("**Team Pokémon:**")
                
                # Create Pokemon badges with identification status
                pokemon_badges = []
                for pokemon in pokemon_team[:8]:  # Show up to 8 Pokemon
                    pokemon_name = pokemon.get("name", "")
                    if pokemon_name and pokemon_name != "Not specified in article":
                        is_banned = any(conflict["name"] == pokemon_name for conflict in regulation_conflicts)
                        
                        # Check for potential translation issues
                        potential_issues = []
                        if "Glaceon" in pokemon_name:
                            potential_issues.append("Possible mistranslation (Baxcalibur/Kingambit?)")
                        if pokemon_name == "Not specified in article":
                            potential_issues.append("Unknown Pokemon")
                        if len(pokemon_name) < 3:
                            potential_issues.append("Short name - check translation")
                        
                        # Determine badge status
                        if is_banned:
                            badge_color = "#ef4444"
                            badge_icon = "⚠️"
                            status = "BANNED"
                        elif potential_issues:
                            badge_color = "#f59e0b" 
                            badge_icon = "❓"
                            status = "CHECK"
                        else:
                            badge_color = "#10b981"
                            badge_icon = "✅"
                            status = "OK"
                        
                        tooltip = f"Status: {status}"
                        if potential_issues:
                            tooltip += f" - {'; '.join(potential_issues)}"
                        
                        pokemon_badges.append(
                            f'<span style="background: {badge_color}15; color: {badge_color}; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500; margin: 2px; display: inline-block;" title="{tooltip}">{badge_icon} {pokemon_name}</span>'
                        )
                
                if pokemon_badges:
                    st.markdown(
                        f'<div style="margin: 8px 0;">{"".join(pokemon_badges)}</div>',
                        unsafe_allow_html=True
                    )
                
                # Traditional sprite preview (condensed)
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
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

            with col1:
                if st.button(f"📖 View Analysis", key=f"view_{i}"):
                    # Load this analysis into session state and switch to new analysis page
                    st.session_state["analysis_result"] = analysis_result
                    st.session_state["article_content"] = article.get(
                        "content_preview", ""
                    )
                    st.session_state["current_page"] = "New Analysis"
                    st.rerun()

            # Re-test button (insert before other buttons)
            with col2:
                if is_valid_url:
                    if st.button(
                        "🔄 Re-test", 
                        key=f"retest_{i}",
                        help="Re-analyze this article with current Pokemon detection improvements"
                    ):
                        # Clear cache for this article and set URL for re-testing
                        if delete_cached_article(article.get("hash", "")):
                            st.session_state["retest_url"] = article_url
                            st.session_state["current_page"] = "New Analysis" 
                            st.success(f"🔄 Re-testing article! Switching to analysis page...")
                            st.rerun()
                        else:
                            st.error("Failed to clear cache for re-testing")

            with col3:
                if analysis_result.get("translated_content"):
                    translated_text = f"Title: {title}\n\nSummary: {summary}\n\nFull Translation:\n{analysis_result['translated_content']}"
                    st.download_button(
                        label="📄 Translation",
                        data=translated_text,
                        file_name=f"translation_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_trans_{i}",
                    )

            with col4:
                if pokemon_team:
                    try:
                        pokepaste_content = create_pokepaste(pokemon_team, title)
                    except Exception as e:
                        st.error(f"Error creating pokepaste: {str(e)}")
                        pokepaste_content = f"// Error generating pokepaste: {str(e)}\n// Please try re-analyzing the article"

                    st.download_button(
                        label="🎮 Pokepaste",
                        data=pokepaste_content,
                        file_name=f"team_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_paste_{i}",
                    )

            with col5:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this article"):
                    if delete_cached_article(article.get("hash", "")):
                        st.success("Article deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete article")

            st.divider()


def main():
    """Main application function"""
    st.set_page_config(
        page_title="Pokemon VGC Analysis",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .pokemon-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .pokemon-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    .team-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏆 Pokemon VGC Analysis")
    
    # Determine default page based on session state
    default_page = "🏠 Article Analysis"
    if "current_page" in st.session_state:
        if st.session_state["current_page"] == "New Analysis":
            default_page = "🏠 Article Analysis"
            # Clear the override after using it
            del st.session_state["current_page"]
    
    # Always show the selectbox with appropriate default
    options = ["🏠 Article Analysis", "📚 Previous Articles"]
    default_index = options.index(default_page)
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        options,
        index=default_index
    )
    
    if page == "🏠 Article Analysis":
        render_article_analysis_page()
    elif page == "📚 Previous Articles":
        render_previous_articles_page()


if __name__ == "__main__":
    main()
