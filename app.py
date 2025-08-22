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
    "ものまねハーブ": "mirror-herb"
}

# Common VGC Items List for Vision Recognition
COMMON_VGC_ITEMS = [
    "Leftovers", "Focus Sash", "Mystic Water", "Life Orb",
    "Choice Band", "Choice Specs", "Choice Scarf", "Assault Vest", 
    "Sitrus Berry", "Lum Berry", "Safety Goggles", "Booster Energy",
    "Clear Amulet", "Covert Cloak", "Rocky Helmet", "Mental Herb",
    "Wide Lens", "Mirror Herb", "Expert Belt", "Weakness Policy",
    "たべのこし", "きあいのタスキ", "しんぴのしずく", "いのちのたま"
]

# VGC Regulation Database (Scarlet & Violet Era)
VGC_REGULATIONS = {
    "A": {
        "period": "November 2022 - January 2023",
        "description": "Paldea Dex only, no legendaries/mythicals",
        "restricted": [],
        "banned": ["Legendaries", "Mythicals", "Paradox Pokemon"]
    },
    "B": {
        "period": "February 2023 - May 2023", 
        "description": "Paldea Dex + Home transfer, no restricted",
        "restricted": [],
        "banned": ["Restricted Legendaries"]
    },
    "C": {
        "period": "May 2023 - September 2023",
        "description": "Series 1 with restricted legendaries allowed",
        "restricted": ["Koraidon", "Miraidon", "Box Legendaries"],
        "banned": []
    },
    "D": {
        "period": "September 2023 - January 2024",
        "description": "Series 2 with expanded legendary pool",
        "restricted": ["Koraidon", "Miraidon", "Kyogre", "Groudon", "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem", "Xerneas", "Yveltal", "Zygarde", "Cosmog", "Cosmoem", "Solgaleo", "Lunala", "Necrozma"],
        "banned": []
    },
    "E": {
        "period": "January 2024 - May 2024",
        "description": "Series 3 with Treasures of Ruin",
        "restricted": ["Koraidon", "Miraidon", "Chi-Yu", "Chien-Pao", "Ting-Lu", "Wo-Chien"] + ["Kyogre", "Groudon", "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem", "Xerneas", "Yveltal", "Zygarde", "Solgaleo", "Lunala", "Necrozma"],
        "banned": []
    },
    "F": {
        "period": "May 2024 - September 2024",
        "description": "Series 4 with DLC legendaries",
        "restricted": ["Koraidon", "Miraidon", "Kyogre", "Groudon", "Rayquaza", "Dialga", "Palkia", "Giratina", "Reshiram", "Zekrom", "Kyurem", "Xerneas", "Yveltal", "Zygarde", "Solgaleo", "Lunala", "Necrozma", "Calyrex", "Calyrex-Ice", "Calyrex-Shadow"],
        "banned": []
    },
    "G": {
        "period": "September 2024 - January 2025",
        "description": "Series 5 with expanded roster", 
        "restricted": ["All Box Legendaries", "Calyrex forms", "Urshifu forms"],
        "banned": []
    },
    "H": {
        "period": "January 2025 - May 2025",
        "description": "Series 6 current format",
        "restricted": ["All Previous Restricted Pokemon"],
        "banned": []
    },
    "I": {
        "period": "May 2025 onwards",
        "description": "Series 7 upcoming format",
        "restricted": ["TBD"],
        "banned": []
    }
}

# Regulation Detection Keywords
REGULATION_KEYWORDS = {
    "A": ["Paldea Dex", "no legendaries", "November 2022", "December 2022", "January 2023"],
    "B": ["Home transfer", "February 2023", "March 2023", "April 2023", "May 2023"],
    "C": ["restricted legendaries", "Series 1", "Koraidon", "Miraidon", "May 2023", "June 2023"],
    "D": ["expanded legendary", "Series 2", "September 2023", "October 2023", "November 2023", "December 2023"],
    "E": ["Treasures of Ruin", "Series 3", "Chi-Yu", "Chien-Pao", "January 2024", "February 2024"],
    "F": ["DLC legendaries", "Series 4", "Calyrex", "May 2024", "June 2024", "July 2024"],
    "G": ["Series 5", "expanded roster", "September 2024", "October 2024"],
    "H": ["Series 6", "January 2025", "current format"],
    "I": ["Series 7", "May 2025", "upcoming"]
}

# Page configuration
st.set_page_config(
    page_title="Pokemon VGC Article Analyzer",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling
st.markdown("""
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
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        color: #1e293b;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
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
        gap: 12px;
        margin-top: 16px;
    }
    .info-item {
        background: rgba(255, 255, 255, 0.9);
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .info-item:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .info-label {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .info-value {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
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
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        min-width: 32px;
        text-transform: uppercase;
    }
    
    .ev-stat-bar-container {
        flex: 1;
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        position: relative;
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
        font-size: 12px;
        font-weight: 700;
        color: #1e293b;
        min-width: 28px;
        text-align: right;
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
        font-size: 16px;
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
        padding: 10px 16px;
        border-radius: 10px;
        margin: 8px 0;
        font-size: 14px;
        font-weight: 600;
        color: #475569;
        border-left: 4px solid var(--type-color, #3b82f6);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
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
        width: 8px;
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
    
    /* Floating action effects */
    .pokemon-card {
        will-change: transform;
    }
    
    @media (max-width: 768px) {
        .ev-stats-grid {
            grid-template-columns: 1fr;
        }
        
        .pokemon-info-grid {
            grid-template-columns: 1fr;
        }
        
        .pokemon-card:hover {
            transform: translateY(-4px) scale(1.01);
        }
    }
    .pokemon-name {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .pokemon-info {
        font-size: 14px;
        line-height: 1.6;
    }
    .team-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 32px;
        border-radius: 16px;
        text-align: center;
        margin: 24px 0 32px 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    .team-header h1 {
        margin: 0 0 8px 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .team-header p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
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
</style>
""", unsafe_allow_html=True)

def parse_ev_spread(ev_string: str) -> Dict[str, int]:
    """Parse EV spread string into individual stat values, including Japanese formats"""
    stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    ev_dict = {stat: 0 for stat in stat_names}
    
    if not ev_string or ev_string == "Not specified in article":
        return ev_dict
    
    try:
        import re
        
        # Handle standard format: "252/0/4/252/0/0"
        if '/' in ev_string and not any(c in ev_string for c in ['HP', 'Atk', 'Def', 'SpA', 'SpD', 'Spe', 'H', 'A', 'B', 'C', 'D', 'S']):
            values = [int(x.strip()) for x in ev_string.split('/')]
            for i, value in enumerate(values[:6]):
                if i < len(stat_names):
                    ev_dict[stat_names[i]] = value
            return ev_dict
        
        # Enhanced pattern matching for multiple formats
        patterns = {
            'hp': [
                r'(\d+)\s*HP',
                r'(\d+)\s*H(?![a-z])',  # H but not followed by lowercase (to avoid "Heavy")
                r'H(\d+)',
                r'(\d+)\s*(?:HP|ヒットポイント|体力)',
                r'HP\s*(\d+)',
                r'体力\s*(\d+)'
            ],
            'atk': [
                r'(\d+)\s*(?:Atk|Attack|A(?![a-z]))',
                r'(\d+)\s*(?:攻撃|こうげき)',
                r'A(\d+)',
                r'攻撃\s*(\d+)',
                r'(?:Atk|Attack)\s*(\d+)'
            ],
            'def': [
                r'(\d+)\s*(?:Def|Defense|B(?![a-z]))',
                r'(\d+)\s*(?:防御|ぼうぎょ)',
                r'B(\d+)',
                r'防御\s*(\d+)',
                r'(?:Def|Defense)\s*(\d+)'
            ],
            'spa': [
                r'(\d+)\s*(?:SpA|Sp\.?\s*A|Special\s*Attack|C(?![a-z]))',
                r'(\d+)\s*(?:特攻|とくこう|特殊攻撃)',
                r'C(\d+)',
                r'特攻\s*(\d+)',
                r'特殊攻撃\s*(\d+)',
                r'(?:SpA|Special\s*Attack)\s*(\d+)'
            ],
            'spd': [
                r'(\d+)\s*(?:SpD|Sp\.?\s*D|Special\s*Defense|D(?![a-z]))',
                r'(\d+)\s*(?:特防|とくぼう|特殊防御)',
                r'D(\d+)',
                r'特防\s*(\d+)',
                r'特殊防御\s*(\d+)',
                r'(?:SpD|Special\s*Defense)\s*(\d+)'
            ],
            'spe': [
                r'(\d+)\s*(?:Spe|Speed|S(?![a-z]))',
                r'(\d+)\s*(?:素早さ|すばやさ|速度)',
                r'S(\d+)',
                r'素早さ\s*(\d+)',
                r'速度\s*(\d+)',
                r'(?:Spe|Speed)\s*(\d+)'
            ]
        }
        
        # Handle Japanese format with separators: H252-A0-B4-C252-D0-S0 or H252 A0 B4 C252 D0 S0
        japanese_format_patterns = [
            r'H(\d+)[-・\s]+A(\d+)[-・\s]+B(\d+)[-・\s]+C(\d+)[-・\s]+D(\d+)[-・\s]+S(\d+)',
            r'H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)',
            r'H(\d+)-A(\d+)-B(\d+)-C(\d+)-D(\d+)-S(\d+)',
            r'H(\d+)・A(\d+)・B(\d+)・C(\d+)・D(\d+)・S(\d+)',
            # Note.com specific patterns with extra spacing/formatting
            r'H\s*(\d+)\s*[-・\s]\s*A\s*(\d+)\s*[-・\s]\s*B\s*(\d+)\s*[-・\s]\s*C\s*(\d+)\s*[-・\s]\s*D\s*(\d+)\s*[-・\s]\s*S\s*(\d+)'
        ]
        
        for pattern in japanese_format_patterns:
            japanese_format_match = re.search(pattern, ev_string)
            if japanese_format_match:
                values = [int(x) for x in japanese_format_match.groups()]
                for i, value in enumerate(values):
                    if i < len(stat_names):
                        ev_dict[stat_names[i]] = value
                return ev_dict
        
        # Handle exact H/A/B/C/D/S pattern with word boundaries
        exact_pattern_match = re.search(r'\bH(\d+)\b.*?\bA(\d+)\b.*?\bB(\d+)\b.*?\bC(\d+)\b.*?\bD(\d+)\b.*?\bS(\d+)\b', ev_string)
        if exact_pattern_match:
            values = [int(x) for x in exact_pattern_match.groups()]
            for i, value in enumerate(values):
                if i < len(stat_names):
                    ev_dict[stat_names[i]] = value
            return ev_dict
        
        # Handle effort value prefix formats: 努力値: H252/A0/B4/C252/D0/S0
        effort_match = re.search(r'(?:努力値|EV|ev)[:：]\s*H(\d+)[-/・\s]A(\d+)[-/・\s]B(\d+)[-/・\s]C(\d+)[-/・\s]D(\d+)[-/・\s]S(\d+)', ev_string)
        if effort_match:
            values = [int(x) for x in effort_match.groups()]
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
            (r'HP(\d+)', 'hp'),
            (r'攻撃(\d+)', 'atk'),
            (r'防御(\d+)', 'def'),
            (r'特攻(\d+)', 'spa'),
            (r'特防(\d+)', 'spd'),
            (r'素早さ(\d+)', 'spe'),
            (r'体力(\d+)', 'hp'),
            (r'こうげき(\d+)', 'atk'),
            (r'ぼうぎょ(\d+)', 'def'),
            (r'とくこう(\d+)', 'spa'),
            (r'とくぼう(\d+)', 'spd'),
            (r'すばやさ(\d+)', 'spe')
        ]
        
        for pattern, stat in japanese_desc_patterns:
            match = re.search(pattern, ev_string)
            if match:
                ev_dict[stat] = int(match.group(1))
    
    except:
        # If parsing fails, return zeros
        pass
    
    # Validate EV total and provide defaults if needed
    ev_dict = validate_and_fix_evs(ev_dict)
    return ev_dict

def validate_and_fix_evs(ev_dict: Dict[str, int]) -> Dict[str, int]:
    """Validate EV spread and provide reasonable defaults if incomplete"""
    total = sum(ev_dict.values())
    
    # If EVs total 0 or are clearly incomplete, provide reasonable defaults
    if total == 0:
        # Common competitive spread: 252/0/4/252/0/0 (HP/Atk/Def/SpA/SpD/Spe)
        return {'hp': 252, 'atk': 0, 'def': 4, 'spa': 252, 'spd': 0, 'spe': 0}
    
    # If total is not 508 (max allowed), try to fix common issues
    if total != 508:
        # If close to 508, adjust the largest investment
        if 500 <= total <= 516:  # Close enough, minor adjustment needed
            diff = 508 - total
            # Find stat with largest investment to adjust
            max_stat = max(ev_dict.items(), key=lambda x: x[1])
            if max_stat[1] + diff >= 0:
                ev_dict[max_stat[0]] += diff
        
        # If significantly different, note as potentially incomplete
        elif total < 400:  # Clearly incomplete
            # Keep what we have but note it's incomplete
            pass
    
    return ev_dict

def get_stat_icon(stat: str) -> str:
    """Get emoji icon for stat"""
    icons = {
        'hp': '❤️',
        'atk': '⚔️', 
        'def': '🛡️',
        'spa': '🔮',
        'spd': '🔰',
        'spe': '⚡'
    }
    return icons.get(stat, '📊')

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
        'physical-attacker': 'role-physical-attacker',
        'special-attacker': 'role-special-attacker', 
        'physical-wall': 'role-physical-wall',
        'special-wall': 'role-special-wall',
        'support': 'role-support',
        'speed-control': 'role-speed-control',
        'utility': 'role-utility'
    }
    
    for key, class_name in role_mappings.items():
        if key in role_lower:
            return class_name
    
    return "role-utility"

def create_ev_visualization(ev_spread: str) -> str:
    """Create HTML for EV visualization with progress bars"""
    ev_dict = parse_ev_spread(ev_spread)
    total_evs = sum(ev_dict.values())
    
    # Check if total is reasonable (max 508)
    total_color = "#4CAF50" if total_evs <= 508 else "#FF5722"
    
    stats_html = ""
    stat_names = ['hp', 'atk', 'def', 'spa', 'spd', 'spe']
    stat_labels = ['HP', 'ATK', 'DEF', 'SPA', 'SPD', 'SPE']
    
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
        tooltip_text = tooltip_text.replace('"', '&quot;')
        
        stats_html += (
            f'<div class="ev-stat ev-{stat} {investment_class} tooltip" data-tooltip="{tooltip_text}">'
            f'<div class="ev-stat-icon">{icon}</div>'
            f'<div class="ev-stat-name">{label}</div>'
            f'<div class="ev-stat-bar-container">'
            f'<div class="ev-stat-bar" style="width: {percentage}%"></div>'
            f'</div>'
            f'<div class="ev-stat-value">{value}</div>'
            f'</div>'
        )
    
    html = (
        f'<div class="ev-container">'
        f'<div class="ev-header">'
        f'<div class="ev-title">📊 EV Spread</div>'
        f'<div class="ev-total" style="color: {total_color}; border-color: {total_color}">'
        f'{total_evs}/508 EVs'
        f'</div>'
        f'</div>'
        f'<div class="ev-stats-grid">'
        f'{stats_html}'
        f'</div>'
        f'</div>'
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
    """Extract images from webpage that might contain VGC data"""
    images = []
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all images
        img_tags = soup.find_all('img')
        
        for img_tag in img_tags[:max_images]:
            try:
                img_src = img_tag.get('src')
                if not img_src:
                    continue
                
                # Convert relative URLs to absolute
                img_url = urljoin(url, img_src)
                
                # Skip very small images (likely icons/decorations)
                width = img_tag.get('width')
                height = img_tag.get('height')
                if width and height:
                    try:
                        if int(width) < 100 or int(height) < 100:
                            continue
                    except:
                        pass
                
                # Download and process image
                img_response = requests.get(img_url, headers=headers, timeout=15)
                if img_response.status_code == 200:
                    # Convert to base64 for Gemini Vision
                    img_data = base64.b64encode(img_response.content).decode('utf-8')
                    
                    # Get image info
                    try:
                        pil_img = Image.open(BytesIO(img_response.content))
                        img_format = pil_img.format
                        img_size = pil_img.size
                    except:
                        img_format = 'unknown'
                        img_size = (0, 0)
                    
                    images.append({
                        'url': img_url,
                        'data': img_data,
                        'format': img_format,
                        'size': img_size,
                        'alt_text': img_tag.get('alt', ''),
                        'title': img_tag.get('title', ''),
                        'content_type': img_response.headers.get('content-type', '')
                    })
                    
            except Exception as e:
                continue
                
    except Exception as e:
        st.warning(f"Could not extract images: {str(e)}")
    
    return images

def is_potentially_vgc_image(image_info: Dict[str, Any]) -> bool:
    """Determine if an image might contain VGC-relevant data"""
    # Check alt text and title for VGC keywords
    text_content = (image_info.get('alt_text', '') + ' ' + 
                   image_info.get('title', '')).lower()
    
    vgc_keywords = [
        'pokemon', 'team', 'ev', 'iv', 'stats', 'battle', 'vgc',
        'ポケモン', 'チーム', '努力値', '個体値', 'バトル',
        'doubles', 'tournament', 'ranking'
    ]
    
    for keyword in vgc_keywords:
        if keyword in text_content:
            return True
    
    # Check image size (VGC images are often screenshots)
    width, height = image_info.get('size', (0, 0))
    if width > 400 and height > 300:  # Reasonable screenshot size
        return True
    
    # Check file format
    if image_info.get('format') in ['PNG', 'JPEG', 'JPG']:
        return True
    
    return False

def encode_image_for_gemini(image_data: str, format_type: str = 'jpeg') -> Dict[str, Any]:
    """Prepare image data for Gemini Vision API"""
    return {
        'mime_type': f'image/{format_type.lower()}',
        'data': image_data
    }

def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash for content to use as cache key"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]  # Use first 16 chars for shorter keys

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
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (optional: implement TTL)
            cache_timestamp = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
            
            # Cache valid for 7 days (adjust as needed)
            if datetime.now() - cache_timestamp < timedelta(days=7):
                return cache_data.get('analysis_result')
        
        return None
    except Exception as e:
        # If cache read fails, return None (will trigger API call)
        return None

def save_to_cache(content: str, analysis_result: Dict[str, Any], url: Optional[str] = None) -> None:
    """Save analysis result to cache"""
    try:
        content_hash = generate_content_hash(content)
        cache_file = get_cache_file_path(content_hash)
        
        cache_data = {
            "hash": content_hash,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "analysis_result": analysis_result,
            "content_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # If cache write fails, continue without caching (non-critical)
        pass

def get_cache_stats() -> Dict[str, int]:
    """Get cache statistics"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        total_size = 0
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            total_size += os.path.getsize(file_path)
        
        return {
            "cached_articles": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    except:
        return {"cached_articles": 0, "total_size_mb": 0}

def clear_cache() -> bool:
    """Clear all cached articles"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
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
    
    return html if html else f'<div class="strategy-item">No {list_type}s specified</div>'

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
            "ting-yu": "ting-lu",     # Common mistranslation
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
            "miraidon": "miraidon",
            "ogerpon": "ogerpon",
            "ogerpon-teal": "ogerpon-teal-mask",
            "ogerpon-wellspring": "ogerpon-wellspring-mask", 
            "ogerpon-hearthflame": "ogerpon-hearthflame-mask",
            "ogerpon-cornerstone": "ogerpon-cornerstone-mask",
            "ogerpon-teal-mask": "ogerpon-teal-mask",
            "ogerpon-wellspring-mask": "ogerpon-wellspring-mask",
            "ogerpon-hearthflame-mask": "ogerpon-hearthflame-mask", 
            "ogerpon-cornerstone-mask": "ogerpon-cornerstone-mask",
            "fezandipiti": "fezandipiti",
            "munkidori": "munkidori",
            "okidogi": "okidogi",
            "terapagos": "terapagos",
            
            # Regional forms
            "paldean-tauros": "tauros-paldea-combat",
            "paldean-wooper": "wooper-paldea",
            
            # Other common issues
            "mime-jr": "mime-jr",
            "porygon-z": "porygon-z",
            "porygon2": "porygon2"
        }
        
        api_name = name_mapping.get(name, name)
        
        # Get Pokemon data from PokeAPI
        response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{api_name}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data['sprites']['front_default']
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
            self.vision_model = genai.GenerativeModel("gemini-2.0-flash-exp")  # Same model handles vision
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
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

    def scrape_article_enhanced(self, url: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Enhanced article scraping with image extraction and note.com handling"""
        try:
            # Extract images first
            images = extract_images_from_url(url)
            vgc_images = [img for img in images if is_potentially_vgc_image(img)]
            
            # Special handling for note.com articles
            if 'note.com' in url:
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
                        text_content = "\n".join([doc.page_content for doc in documents])
                        return text_content[:12000], vgc_images  # Increased limit for better content
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for unwanted in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
                unwanted.decompose()
            
            # Try to find the main content area (note.com specific selectors)
            content_selectors = [
                # Modern note.com selectors
                '[data-testid="article-body"]',
                '.note-common-styles__textnote-body',
                '.p-article__body',
                '.note-body',
                'article',
                '.article-body',
                # Additional selectors for embedded content
                '.p-note__content',
                '.p-article__content-wrapper',
                '.c-article-body',
                '.note-content',
                # Fallback selectors
                'main',
                '#article-body'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                # Extract text while preserving structure
                text_content = main_content.get_text(separator='\n', strip=True)
            else:
                # Fallback to general content extraction
                text_content = soup.get_text(separator='\n', strip=True)
            
            # Clean up the text
            lines = []
            for line in text_content.splitlines():
                line = line.strip()
                if line and len(line) > 2:  # Skip very short lines
                    lines.append(line)
            
            final_content = '\n'.join(lines)
            
            # Look for Pokemon-related sections specifically
            pokemon_keywords = [
                'ポケモン', 'pokemon', '努力値', 'EV', 'チーム', 'team', 'パーティ', 'party',
                'バトル', 'battle', 'ダブル', 'double', 'VGC', 'vgc', 
                'ランクバトル', 'ranked', 'トーナメント', 'tournament',
                'シングル', 'single', 'ダブルバトル', 'double battle',
                '反省', 'reflection', 'レート', 'rating', 'BO1', 'BO3', '構築', 'team building',
                'regulation', 'series', 'format'
            ]
            
            content_lower = final_content.lower()
            has_pokemon_content = any(keyword.lower() in content_lower for keyword in pokemon_keywords)
            
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
        
        for i, image in enumerate(images[:3]):  # Limit to 3 images to avoid token limits
            try:
                st.info(f"🖼️ Analyzing image {i+1}/{min(len(images), 3)}...")
                
                # Prepare image for Gemini
                image_part = {
                    'mime_type': f'image/{image.get("format", "jpeg").lower()}',
                    'data': image['data']
                }
                
                vision_prompt = """
                CRITICAL: Analyze this Pokemon VGC team image with EXTREME DETAIL. This is likely a note.com format with specific layout:

                **LAYOUT PARSING ORDER (TOP TO BOTTOM):**
                1. Pokemon Name/Sprite
                2. Typing (DO NOT count as move)
                3. Ability (DO NOT count as move) 
                4. EXACTLY 4 MOVES (below ability)
                5. Held Item (beside/near Pokemon sprite)

                **ITEM DETECTION - HELD ITEMS:**
                Look for items beside Pokemon sprites or in item slots:
                - Mystic Water, Leftovers, Focus Sash (specifically mentioned examples)
                - Life Orb, Choice Band/Specs/Scarf, Assault Vest, Rocky Helmet
                - Sitrus Berry, Lum Berry, Safety Goggles, Booster Energy, Clear Amulet
                - Covert Cloak, Mental Herb, Wide Lens, Mirror Herb, Expert Belt
                
                **ITEM TRANSLATIONS (Japanese ↔ English):**
                - しんぴのしずく = Mystic Water
                - たべのこし = Leftovers  
                - きあいのタスキ = Focus Sash
                - いのちのたま = Life Orb
                - こだわりハチマキ = Choice Band
                - こだわりメガネ = Choice Specs
                - こだわりスカーフ = Choice Scarf
                - とつげきチョッキ = Assault Vest
                - オボンのみ = Sitrus Berry
                - ラムのみ = Lum Berry

                **NATURE DETECTION - STAT ARROW ANALYSIS:**
                Look for colored arrows next to stat abbreviations (H/A/B/C/D/S):
                - BLUE arrows (↓) = stat DECREASE (-10%)
                - RED arrows (↑) = stat INCREASE (+10%)
                - Example: "A" with blue arrow + "S" with red arrow = Timid nature (-Attack, +Speed)
                
                **NATURE MAPPING:**
                - Blue A + Red S = Timid (-Atk, +Spe)
                - Blue S + Red A = Adamant (-SpA, +Atk)  
                - Blue A + Red D = Careful (-Atk, +SpD)
                - Blue S + Red C = Modest (-Atk, +SpA)
                - Blue C + Red A = Jolly (-SpA, +Spe)
                - Blue D + Red A = Brave (-Spe, +Atk)

                **TERA TYPE DETECTION:**
                - Look for Tera type indicators beside Pokemon
                - Specific examples: Water for Kyogre, Dragon for Calyrex, Fire for Rillaboom
                - Color coding: Blue=Water, Red=Fire, Green=Grass, Purple=Dragon, Yellow=Electric

                **MOVE PARSING VALIDATION (CRITICAL):**
                - MANDATORY: Each Pokemon MUST have EXACTLY 4 moves
                - DO NOT include typing as a move (e.g., "Water/Flying" is typing, not a move)
                - DO NOT include ability as a move (e.g., "Drizzle" is ability, not a move)
                - Moves are typically listed after ability in vertical order
                - If fewer than 4 moves visible, note as "INCOMPLETE - only X moves detected"
                - If more than 4 items listed, carefully distinguish moves from other elements
                - VALIDATION REQUIRED: Count moves multiple times to ensure accuracy

                **POKEMON IDENTIFICATION & MOVE COMPATIBILITY:**
                - Visual sprite recognition priority
                - Iron Crown vs Iron Jugulis: Crown=Psychic/Steel, Jugulis=Dark/Flying  
                - Move translation: "Bark Out" = "Snarl"
                - Validate move compatibility with Pokemon types/abilities

                **CRITICAL PARSING RULES:**
                1. EXACTLY 4 moves per Pokemon
                2. Separate typing from moves
                3. Separate ability from moves
                4. Identify held items clearly
                5. Use visual hierarchy for parsing order

                Provide response in this EXACT format:
                
                POKEMON_1: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions] 
                POKEMON_2: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions]
                POKEMON_3: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions]
                POKEMON_4: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions]
                POKEMON_5: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions]
                POKEMON_6: [Name] | TYPING: [Type1/Type2] | ABILITY: [Ability] | ITEM: [Held Item] | NATURE: [Nature] | TERA: [Tera Type] | MOVES: [Move1, Move2, Move3, Move4] | ARROWS: [positions]
                
                MOVE_COUNT_VALIDATION: [CRITICAL - Confirm exactly 4 moves per Pokemon: Pokemon1=4, Pokemon2=4, Pokemon3=4, Pokemon4=4, Pokemon5=4, Pokemon6=4]
                MOVE_COMPLETENESS: [Report any Pokemon with incomplete movesets and what was missing]
                PARSING_ERRORS: [Any issues with typing/ability confused as moves]
                EV_SPREAD_DATA: [All visible EV spreads, stat numbers, or effort value indicators]
                STAT_CALCULATIONS: [Any visible stat numbers that could indicate EV investments]
                ITEM_LOCATIONS: [Where items were visually positioned]
                IMAGE_TYPE: [team composition/battle screenshot/stats chart/other]
                LAYOUT_VALIDATION: [Confirm proper parsing order was followed: Name->Typing->Ability->Moves->Item]
                """
                
                response = self.vision_model.generate_content([vision_prompt, image_part])
                if response and response.text:
                    image_analysis_results.append(f"Image {i+1} Analysis:\n{response.text}\n")
                    
            except Exception as e:
                st.warning(f"Could not analyze image {i+1}: {str(e)}")
                continue
        
        return "\n".join(image_analysis_results)

    def analyze_article(self, content: str, url: Optional[str] = None, images: Optional[List[Dict[str, Any]]] = None) -> Optional[Dict[str, Any]]:
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
        if images and len(images) > 0:
            st.info(f"🖼️ Found {len(images)} potentially relevant images, analyzing...")
            image_analysis = self.analyze_images(images)
            if image_analysis:
                st.success(f"✅ Image analysis complete - extracted additional data!")
        
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

**STEP 4: VGC REGULATION/FORMAT DETECTION**
- Identify which VGC regulation this team is from (Regulation A through I)
- Look for regulation mentions, series numbers, or format references in the article
- Check article dates, tournament mentions, or specific format descriptions
- Validate Pokemon legality for the identified regulation
- Note any restricted Pokemon or format-specific rules
- Cross-reference team composition with regulation restrictions

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
            "ev_spread": "HP/Atk/Def/SpA/SpD/Spe format (e.g., 252/0/4/252/0/0)",
            "nature": "Nature name in English",
            "role": "Role in the team (e.g., Physical Attacker, Special Wall, etc.)",
            "ev_explanation": "Detailed explanation of EV spread reasoning, including speed benchmarks, survival calculations, and strategic considerations mentioned in the article"
        }}
    ],
    "translated_content": "Full article translated to English, maintaining VGC terminology and strategic insights"
}}

CRITICAL POKEMON NAME TRANSLATION RULES:
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

**ABILITY TRANSLATIONS (Critical for Paradox Pokemon):**
- こだいかっせい/古代活性 → "Protosynthesis" (Ancient Paradox ability)
- クォークチャージ → "Quark Drive" (Future Paradox ability)

**OTHER COMMON MISTRANSLATIONS:**
- Use official English spellings: "Calyrex-Shadow", "Zamazenta", "Urshifu", "Regieleki"
- Paldean forms: "Iron Valiant", "Roaring Moon", "Flutter Mane", "Iron Bundle"
- Always use hyphens for compound names: "Tapu-Koko", "Ultra-Necrozma", "Necrozma-Dusk-Mane"

**CRITICAL EV PARSING GUIDELINES:**
**Japanese EV Format Recognition:**
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
3. **Context Clues**: Numbers near stat names, in Pokemon descriptions, adjustment explanations
4. **Partial Data**: Even incomplete EV info is valuable (e.g., "HP252振り" = at least HP has 252)
5. **Japanese Stat Mapping**: 
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
        ('hp', 'HP'),
        ('atk', 'Atk'), 
        ('def', 'Def'),
        ('spa', 'SpA'),
        ('spd', 'SpD'),
        ('spe', 'Spe')
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

def create_pokepaste(pokemon_team: List[Dict[str, Any]], team_name: str = "VGC Team") -> str:
    """Generate clean pokepaste format for the team"""
    pokepaste_content = ""
    
    for pokemon in pokemon_team:
        if not pokemon.get('name') or pokemon['name'] == "Not specified in article":
            continue
            
        # Pokemon name and held item
        pokepaste_content += f"{pokemon['name']}"
        if pokemon.get('held_item') and pokemon['held_item'] != "Not specified in article":
            pokepaste_content += f" @ {pokemon['held_item']}"
        pokepaste_content += "\n"
        
        # Ability
        if pokemon.get('ability') and pokemon['ability'] != "Not specified in article":
            pokepaste_content += f"Ability: {pokemon['ability']}\n"
        
        # Tera Type
        if pokemon.get('tera_type') and pokemon['tera_type'] != "Not specified in article":
            pokepaste_content += f"Tera Type: {pokemon['tera_type']}\n"
        
        # EVs (format: HP / Atk / Def / SpA / SpD / Spe)
        if pokemon.get('ev_spread') and pokemon['ev_spread'] != "Not specified in article":
            # Parse the raw EV string and format it properly
            ev_dict = parse_ev_spread(pokemon['ev_spread'])
            formatted_evs = format_evs_for_pokepaste(ev_dict)
            pokepaste_content += f"EVs: {formatted_evs}\n"
        
        # Nature
        if pokemon.get('nature') and pokemon['nature'] != "Not specified in article":
            pokepaste_content += f"{pokemon['nature']} Nature\n"
        
        # Moves
        if pokemon.get('moves'):
            for move in pokemon['moves']:
                if move and move != "Not specified in article":
                    pokepaste_content += f"- {move}\n"
        
        pokepaste_content += "\n"
    
    return pokepaste_content

def render_team_strategy_section(team_analysis: Dict[str, Any], result: Dict[str, Any] = None) -> None:
    """Render team strategy section with proper HTML"""
    st.markdown("### 🎯 Team Strategy")
    
    # Regulation information
    regulation_info = result.get('regulation_info', {}) if result else {}
    if regulation_info and regulation_info.get('regulation') != 'Unknown':
        regulation = regulation_info.get('regulation', 'Unknown')
        format_desc = regulation_info.get('format', 'Not specified')
        tournament_context = regulation_info.get('tournament_context', '')
        
        st.markdown("#### 🏆 VGC Format Information")
        
        reg_color = {
            'A': '#FF6B6B', 'B': '#4ECDC4', 'C': '#45B7D1', 'D': '#96CEB4', 
            'E': '#FFEAA7', 'F': '#DDA0DD', 'G': '#98D8C8', 'H': '#F7DC6F', 'I': '#BB8FCE'
        }.get(regulation, '#95A5A6')
        
        st.markdown(f"""
        <div class="regulation-container" style="background: linear-gradient(135deg, {reg_color}20, {reg_color}10); border-left: 4px solid {reg_color}; padding: 15px; margin: 10px 0; border-radius: 8px;">
            <div style="font-weight: bold; color: {reg_color}; font-size: 1.1em;">
                📋 Regulation {regulation}
            </div>
            <div style="margin-top: 5px; color: #444;">
                {format_desc}
            </div>
            {f'<div style="margin-top: 5px; font-size: 0.9em; color: #666;"><strong>Tournament:</strong> {tournament_context}</div>' if tournament_context else ""}
        </div>
        """, unsafe_allow_html=True)
    
    # Strategy overview
    strategy = team_analysis.get('strategy', 'Not specified')
    st.markdown(f"""
    <div class="summary-container">
        <div class="summary-content">
            <strong>Overall Strategy:</strong><br>
            {strategy}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Strengths and Weaknesses in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💪 Strengths")
        strengths = team_analysis.get('strengths', [])
        if strengths:
            for strength in strengths:
                if strength and strength != "Not specified":
                    st.markdown(f"""
                    <div class="strategy-item">
                        {strength}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="strategy-item">No strengths specified</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚠️ Weaknesses")
        weaknesses = team_analysis.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                if weakness and weakness != "Not specified":
                    st.markdown(f"""
                    <div class="strategy-item">
                        {weakness}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="strategy-item">No weaknesses specified</div>', unsafe_allow_html=True)
    
    # Meta relevance
    st.markdown("#### 🌟 Meta Relevance")
    meta_relevance = team_analysis.get('meta_relevance', 'Not specified')
    st.markdown(f"""
    <div class="meta-relevance">
        {meta_relevance}
    </div>
    """, unsafe_allow_html=True)

def get_cached_articles() -> List[Dict[str, Any]]:
    """Get list of all cached articles with metadata"""
    try:
        cache_dir = ensure_cache_directory()
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        articles = []
        for file in cache_files:
            file_path = os.path.join(cache_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                articles.append(cache_data)
            except:
                continue
        
        # Sort by timestamp (newest first)
        articles.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
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
    st.markdown('<div class="team-header"><h1>⚔️ Pokemon VGC Article Analyzer</h1><p>Analyze Japanese VGC articles, showcase teams, and download results</p></div>', unsafe_allow_html=True)
    
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
            help="Enter the URL of a Japanese Pokemon VGC article"
        )
    
    with col2:
        # Cache status in header
        cache_stats = get_cache_stats()
        st.metric("Cache", f"{cache_stats['cached_articles']} articles ({cache_stats['total_size_mb']} MB)")
    
    with col3:
        if st.button("🗑️ Clear", help="Clear cache", disabled=cache_stats["cached_articles"] == 0):
            if clear_cache():
                st.success("Cache cleared!")
                st.rerun()
    
    # Manual text input
    manual_text = st.text_area(
        "Or paste Japanese article content directly:",
        height=150,
        placeholder="Paste Japanese article content here..."
    )
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            enable_image_analysis = st.checkbox(
                "🖼️ Enable Image Analysis", 
                value=True, 
                help="Extract and analyze images from articles for additional Pokemon/EV data"
            )
        with col2:
            enable_langchain = st.checkbox(
                "🔗 Enhanced Text Extraction", 
                value=LANGCHAIN_AVAILABLE, 
                disabled=not LANGCHAIN_AVAILABLE,
                help="Use LangChain for better content extraction (requires additional dependencies)"
            )
    
    # Analyze button (disabled during processing)
    is_processing = st.session_state.get('is_processing', False)
    if st.button("🔍 Analyze Article", type="primary", use_container_width=True, disabled=is_processing):
        if url or manual_text:
            # Set processing state
            st.session_state['is_processing'] = True
            with st.spinner("Analyzing article..."):
                content = None
                
                if url:
                    if analyzer.validate_url(url):
                        if enable_image_analysis:
                            # Use enhanced scraping with image extraction
                            content, images = analyzer.scrape_article_enhanced(url)
                            if images:
                                st.info(f"📸 Found {len(images)} images that may contain VGC data")
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
                    st.session_state['article_content'] = content
                    analysis_images = images if enable_image_analysis else []
                    st.session_state['analysis_result'] = analyzer.analyze_article(content, url, analysis_images)
                    # Clear processing state
                    st.session_state['is_processing'] = False
                    st.rerun()
                else:
                    st.error("Unable to extract content from the provided source")
                    # Clear processing state on error
                    st.session_state['is_processing'] = False
        else:
            st.warning("Please provide either a URL or paste article text")
            # Clear processing state if no input provided
            st.session_state['is_processing'] = False

    # Results Section
    if 'analysis_result' in st.session_state and st.session_state['analysis_result']:
        st.divider()
        result = st.session_state['analysis_result']
        
        # Section 1: Article Summary
        st.markdown("## 📖 Article Summary")
        
        # Article title and summary
        title = result.get('title', 'Article Title')
        summary = result.get('summary', 'No summary available')
        
        st.markdown(f"""
        <div class="summary-container">
            <h3 style="color: #1e293b; margin-bottom: 16px;">{title}</h3>
            <div class="summary-content">{summary}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Section 2: Team Strategy Analysis
        if 'team_analysis' in result:
            render_team_strategy_section(result['team_analysis'], result)
            st.divider()
        
        # Section 3: Downloads Section
        st.markdown("## 📥 Export & Downloads")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Translated article download
            if result.get('translated_content'):
                translated_text = f"Title: {result.get('title', 'VGC Article')}\n\n"
                translated_text += f"Summary: {result.get('summary', '')}\n\n"
                translated_text += f"Full Translation:\n{result['translated_content']}"
                
                st.download_button(
                    label="📄 Download Translation",
                    data=translated_text,
                    file_name="vgc_article_translation.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            # Pokepaste download
            if result.get('pokemon_team'):
                pokepaste_content = create_pokepaste(result['pokemon_team'], result.get('title', 'VGC Team'))
                
                st.download_button(
                    label="🎮 Download Pokepaste",
                    data=pokepaste_content,
                    file_name="vgc_team_pokepaste.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col3:
            # Full translation view toggle
            if result.get('translated_content'):
                if st.button("📖 View Full Translation", use_container_width=True):
                    st.session_state['show_translation'] = not st.session_state.get('show_translation', False)
        
        # Full Translation Section (read-only)
        if st.session_state.get('show_translation', False) and result.get('translated_content'):
            st.divider()
            st.markdown("## 📖 Full Article Translation")
            st.markdown(f"""
            <div class="summary-container" style="max-height: 400px; overflow-y: auto;">
                <div class="summary-content" style="white-space: pre-wrap; line-height: 1.6;">
                    {result['translated_content']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Section 4: Team Showcase
        if result.get('pokemon_team'):
            st.markdown("## 🌟 Team Showcase")
            
            pokemon_team = result['pokemon_team']
            
            # Create rows of 3 Pokemon each
            for i in range(0, len(pokemon_team), 3):
                cols = st.columns(3)
                
                for j, col in enumerate(cols):
                    if i + j < len(pokemon_team):
                        pokemon = pokemon_team[i + j]
                        
                        with col:
                            if pokemon.get('name') and pokemon['name'] != "Not specified in article":
                                # Get Pokemon sprite
                                sprite_url = get_pokemon_sprite_url(pokemon['name'])
                                
                                # Display Pokemon sprite
                                try:
                                    st.image(sprite_url, width=120, caption=pokemon['name'])
                                except:
                                    st.markdown(f"**{pokemon['name']}**")
                                
                                # Get styling classes
                                type_class = get_pokemon_type_class(pokemon.get('tera_type', ''))
                                role_class = get_role_class(pokemon.get('role', ''))
                                
                                # Pokemon basic info
                                st.markdown(f"""
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
                                """, unsafe_allow_html=True)
                                
                                # Enhanced EV Visualization
                                ev_spread = pokemon.get('ev_spread', 'Not specified')
                                if ev_spread and ev_spread != 'Not specified':
                                    st.markdown(create_ev_visualization(ev_spread), unsafe_allow_html=True)
                                
                                # Moves section (separate to avoid HTML nesting issues)
                                st.markdown("**🎯 Moves:**")
                                moves = pokemon.get('moves', [])
                                if moves:
                                    for move in moves:
                                        if move and move != "Not specified in article":
                                            st.markdown(f"""
                                            <div class="move-item">
                                                {move}
                                            </div>
                                            """, unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="move-item">No moves specified</div>', unsafe_allow_html=True)
                                
                                # EV Explanation
                                if pokemon.get('ev_explanation') and pokemon['ev_explanation'] != "Not specified in article":
                                    with st.expander("📊 EV Strategy Details"):
                                        st.markdown(f'<div class="ev-explanation">{pokemon["ev_explanation"]}</div>', unsafe_allow_html=True)
        
    
    else:
        # Welcome/instruction content
        st.markdown("""
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
        """)

def render_previous_articles_page():
    """Render the previously searched articles page"""
    st.markdown('<div class="team-header"><h1>📚 Previously Searched Articles</h1><p>Browse and reload your cached VGC article analyses</p></div>', unsafe_allow_html=True)
    
    # Get cached articles
    cached_articles = get_cached_articles()
    
    if not cached_articles:
        st.markdown("""
        ## No Articles Found 🔍
        
        You haven't analyzed any articles yet. Go to the **New Analysis** page to start analyzing Japanese VGC articles.
        
        Once you analyze articles, they'll appear here for quick access without needing to re-process them.
        """)
        return
    
    # Search and filter controls
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search articles", placeholder="Search by title, Pokemon names, or URL...")
    
    with col2:
        sort_option = st.selectbox("📅 Sort by", ["Newest First", "Oldest First", "Title A-Z"])
    
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
            searchable_text += article.get('analysis_result', {}).get('title', '').lower()
            searchable_text += article.get('url', '').lower()
            searchable_text += article.get('content_preview', '').lower()
            
            # Search in Pokemon names
            pokemon_team = article.get('analysis_result', {}).get('pokemon_team', [])
            for pokemon in pokemon_team:
                searchable_text += pokemon.get('name', '').lower()
            
            if search_lower in searchable_text:
                filtered_articles.append(article)
    
    # Sort articles
    if sort_option == "Oldest First":
        filtered_articles.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_option == "Title A-Z":
        filtered_articles.sort(key=lambda x: x.get('analysis_result', {}).get('title', '').lower())
    
    st.markdown(f"## 📖 Articles ({len(filtered_articles)} found)")
    
    # Display articles
    for i, article in enumerate(filtered_articles):
        analysis_result = article.get('analysis_result', {})
        title = analysis_result.get('title', 'Untitled Article')
        summary = analysis_result.get('summary', 'No summary available')
        timestamp = article.get('timestamp', '')
        url = article.get('url', 'No URL')
        pokemon_team = analysis_result.get('pokemon_team', [])
        
        # Format timestamp
        try:
            from datetime import datetime
            parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M")
        except:
            formatted_time = timestamp
        
        # Create article card
        with st.container():
            st.markdown(f"""
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
            """, unsafe_allow_html=True)
            
            # Pokemon team preview
            if pokemon_team:
                cols = st.columns(min(len(pokemon_team), 6))
                for j, pokemon in enumerate(pokemon_team[:6]):
                    if j < len(cols):
                        with cols[j]:
                            if pokemon.get('name') and pokemon['name'] != "Not specified in article":
                                sprite_url = get_pokemon_sprite_url(pokemon['name'])
                                try:
                                    st.image(sprite_url, width=60, caption=pokemon['name'])
                                except:
                                    st.markdown(f"**{pokemon['name']}**")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                if st.button(f"📖 View Analysis", key=f"view_{i}"):
                    # Load this analysis into session state and switch to new analysis page
                    st.session_state['analysis_result'] = analysis_result
                    st.session_state['article_content'] = article.get('content_preview', '')
                    st.session_state['current_page'] = "New Analysis"
                    st.rerun()
            
            with col2:
                if analysis_result.get('translated_content'):
                    translated_text = f"Title: {title}\n\nSummary: {summary}\n\nFull Translation:\n{analysis_result['translated_content']}"
                    st.download_button(
                        label="📄 Download Translation",
                        data=translated_text,
                        file_name=f"translation_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_trans_{i}"
                    )
            
            with col3:
                if pokemon_team:
                    pokepaste_content = create_pokepaste(pokemon_team, title)
                    st.download_button(
                        label="🎮 Download Pokepaste",
                        data=pokepaste_content,
                        file_name=f"team_{i+1}.txt",
                        mime="text/plain",
                        key=f"download_paste_{i}"
                    )
            
            with col4:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this article"):
                    if delete_cached_article(article.get('hash', '')):
                        st.success("Article deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete article")
            
            st.divider()

def main():
    """Main application with navigation"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        # Initialize current page in session state
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = "New Analysis"
        
        # Navigation buttons
        if st.button("📝 New Analysis", use_container_width=True, 
                    type="primary" if st.session_state['current_page'] == "New Analysis" else "secondary"):
            st.session_state['current_page'] = "New Analysis"
            st.rerun()
        
        if st.button("📚 Previous Articles", use_container_width=True,
                    type="primary" if st.session_state['current_page'] == "Previous Articles" else "secondary"):
            st.session_state['current_page'] = "Previous Articles"
            st.rerun()
        
        st.divider()
        
        # Cache stats
        cache_stats = get_cache_stats()
        st.metric("Cached Articles", cache_stats['cached_articles'])
        st.metric("Cache Size", f"{cache_stats['total_size_mb']} MB")
        
        if st.button("🗑️ Clear All Cache", use_container_width=True, disabled=cache_stats["cached_articles"] == 0):
            if clear_cache():
                st.success("Cache cleared!")
                st.rerun()
    
    # Render the appropriate page
    if st.session_state['current_page'] == "New Analysis":
        render_new_analysis_page()
    elif st.session_state['current_page'] == "Previous Articles":
        render_previous_articles_page()

if __name__ == "__main__":
    main()