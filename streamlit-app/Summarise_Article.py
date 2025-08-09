# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import re
import sys
import traceback
from datetime import datetime
import time
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup

# Import pokemon card display first to ensure it's available
from pokemon_card_display import display_pokemon_card_with_summary
from utils.workspace import (
    compute_summary_id,
    log_view,
    log_download,
)
from utils.permalinks import compute_team_fingerprint, build_permalink
import streamlit.components.v1 as components

# Add error handling for imports
try:
    # Import LLM modules
    from utils.gemini_summary import llm_summary_gemini, check_gemini_availability
    GEMINI_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import Gemini module: {e}")
    GEMINI_AVAILABLE = False

# Import shared utilities
try:
    from utils.shared_utils import extract_pokemon_names, strip_html_tags, fetch_article_text_and_images
except ImportError as e:
    st.error(f"Failed to import shared utilities: {e}")
    def extract_pokemon_names(summary):
        return []
    def strip_html_tags(text):
        return text
    def fetch_article_text_and_images(url: str):
        return "", []



# Import error recovery utilities
try:
    from utils.error_recovery import (
        handle_api_error, 
        display_error_with_recovery, 
        create_progress_with_error_handling,
        retry_api_call
    )
    ERROR_RECOVERY_AVAILABLE = True
except ImportError as e:
    st.warning(f"Error recovery functionality not available: {e}")
    ERROR_RECOVERY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Pokemon VGC Team Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern, professional styling
st.markdown("""
<style>
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --warning: #d62728;
        --info: #17a2b8;
        --light: #f8f9fa;
        --dark: #343a40;
        --text-primary: #2c3e50;
        --text-secondary: #6c757d;
        --border: #dee2e6;
        --background: #ffffff;
    }

    .hero-section {
        background: linear-gradient(135deg, #0f2a4a 0%, #1a3a6a 100%);
        color: white !important;
        padding: 4rem 2rem;
        border-radius: 24px;
        text-align: center;
        margin: 0 auto 3rem auto;
        max-width: 1200px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        margin: 0 0 2rem 0;
        color: white !important;
        line-height: 1.1;
        text-shadow: 0 3px 12px rgba(0, 0, 0, 0.5);
        letter-spacing: -1px;
        padding: 0 1rem;
        text-align: center;
    }

    .hero-subtitle {
        font-size: 1.6rem;
        margin: 0 auto 4rem auto;
        max-width: 800px;
        line-height: 1.6;
        font-weight: 500;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        color: white !important;
    }

    .feature-badges {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 1.5rem;
        margin: 0 auto;
        max-width: 1000px;
        padding: 0 1rem;
    }

    .feature-badge {
        background: rgba(255, 255, 255, 0.25);
        color: white !important;
        padding: 1rem 1.8rem;
        border-radius: 32px;
        font-size: 1.1rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 0.8rem;
        backdrop-filter: blur(8px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.2);
        min-width: 160px;
        justify-content: center;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }

    .feature-badge:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.3);
        background: rgba(255, 255, 255, 0.35);
    }

    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 32px;
        margin: 24px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border);
    }

    .status-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #c3e6cb;
        margin: 16px 0;
    }

    .status-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #f5c6cb;
        margin: 16px 0;
    }

    .status-info {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #bee5eb;
        margin: 16px 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-width: 120px;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.2);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);
    }

    .stTextInput > div > div > input {
        border: 2px solid var(--border);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 1rem;
        height: auto;
        min-height: 48px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        outline: none;
    }

    .results-section {
        margin: 0 auto 48px auto;
        max-width: 1100px;
        padding: 0 16px;
    }

    .pokemon-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .pokemon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.15);
    }

    .pokemon-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 12px;
        margin: -24px -24px 24px -24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .pokemon-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }

    .pokemon-index {
        background: rgba(255, 255, 255, 0.2);
        padding: 8px 12px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .ev-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        border: 1px solid #e9ecef;
    }

    .ev-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 12px;
        margin-top: 12px;
    }

    .ev-item {
        background: white;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #dee2e6;
    }

    .ev-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--primary);
        margin-bottom: 4px;
    }

    .ev-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .moves-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        border: 1px solid #e9ecef;
    }

    .move-item {
        background: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }

    .ability-item {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        font-weight: 600;
    }

    .item-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
        font-weight: 600;
    }

    .tera-section {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
        font-weight: 600;
    }
    mark.term {
        background: #fde68a;
        color: #1f2937;
        padding: 0 2px;
        border-radius: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Accessibility controls defaults
if "a11y_font_px" not in st.session_state:
    st.session_state["a11y_font_px"] = 16
if "a11y_high_contrast" not in st.session_state:
    st.session_state["a11y_high_contrast"] = False
if "a11y_reduce_motion" not in st.session_state:
    st.session_state["a11y_reduce_motion"] = False

def show_accessibility_controls():
    with st.expander("♿ Accessibility & Display", expanded=False):
        st.session_state["a11y_font_px"] = st.slider("Base text size", 14, 20, st.session_state["a11y_font_px"], help="Adjust overall font size for readability")
        st.session_state["a11y_high_contrast"] = st.checkbox("High contrast mode", value=st.session_state["a11y_high_contrast"])    
        st.session_state["a11y_reduce_motion"] = st.checkbox("Reduce motion/animations", value=st.session_state["a11y_reduce_motion"])    

def render_dynamic_accessibility_css():
    base_px = st.session_state.get("a11y_font_px", 16)
    high = st.session_state.get("a11y_high_contrast", False)
    reduce = st.session_state.get("a11y_reduce_motion", False)
    css = [
        f"html, body, .stApp {{ font-size: {base_px}px; }}",
    ]
    if high:
        css.append(
            """
            .hero-section, .pokemon-header { background:#0f172a !important; color:#fff !important; }
            .modern-card, .pokemon-card, .results-section > div { border-color:#111827 !important; }
            .status-success { background:#dcfce7 !important; color:#166534 !important; }
            .status-error { background:#fee2e2 !important; color:#991b1b !important; }
            .status-info { background:#e0f2fe !important; color:#075985 !important; }
            """
        )
    if reduce:
        css.append(
            """
            * { transition:none !important; animation:none !important; }
            .feature-badge:hover, .pokemon-card:hover { transform:none !important; box-shadow:none !important; }
            """
        )
    st.markdown(f"<style>{''.join(css)}</style>", unsafe_allow_html=True)

# Lightweight bilingual dictionary for common VGC terms (expandable)
EN_TO_JP = {
    # Moves
    'Trick Room': ['トリックルーム'],
    'Tailwind': ['おいかぜ'],
    'Protect': ['まもる'],
    'Encore': ['アンコール'],
    'Wide Guard': ['ワイドガード'],
    'Quick Guard': ['ファストガード'],
    'Rage Powder': ['いかりのこな'],
    'Follow Me': ['このゆびとまれ'],
    'Spore': ['キノコのほうし'],
    'Thunder Wave': ['でんじは'],
    'Icy Wind': ['こごえるかぜ'],
    'Dazzling Gleam': ['マジカルシャイン'],
    'Astral Barrage': ['アストラルビット','アストラルバレッジ'],
    'Body Press': ['ボディプレス'],
    'Heavy Slam': ['ヘビーボンバー'],
    'Ice Spinner': ['アイススピナー'],
    'Sucker Punch': ['ふいうち'],
    'Ice Shard': ['こおりのつぶて'],
    'Extreme Speed': ['しんそく'],
    'Low Kick': ['けたぐり'],
    'Rock Slide': ['いわなだれ'],
    'Outrage': ['げきりん'],
    'Aura Sphere': ['はどうだん'],
    'Dazzling Gleam': ['マジカルシャイン'],

    # Items
    'Focus Sash': ['きあいのタスキ'],
    'Rusted Shield': ['くちたたて'],
    'Assault Vest': ['とつげきチョッキ'],
    'Mental Herb': ['メンタルハーブ'],
    'Booster Energy': ['ブーストエナジー'],

    # Abilities
    'Dauntless Shield': ['ふくつのたて'],
    'As One (Spectrier)': ['じんばいったい（レイスポス）','じんばいったい'],
    'Regenerator': ['さいせいりょく'],
    'Quark Drive': ['クォークチャージ'],
    'Sword of Ruin': ['わざわいのつるぎ'],

    # Pokémon
    'Calyrex Shadow Rider': ['バドレックス','こくばじょうのすがた'],
    'Zamazenta': ['ザマゼンタ'],
    'Chien-Pao': ['パオジアン'],
    'Dragonite': ['カイリュー'],
    'Iron Valiant': ['テツノブジン'],
    'Amoonguss': ['モロバレル'],
}

# Build reverse mapping
JP_TO_EN = {}
for en, jps in EN_TO_JP.items():
    for jp in jps:
        JP_TO_EN.setdefault(jp, set()).add(en)
JP_TO_EN = {k: sorted(list(v)) for k, v in JP_TO_EN.items()}

# Initialize session state
if "summarising" not in st.session_state:
    st.session_state["summarising"] = False
if "current_summary" not in st.session_state:
    st.session_state["current_summary"] = None
if "current_url" not in st.session_state:
    st.session_state["current_url"] = None

# Cache setup
CACHE_PATH = "storage/cache.json"
os.makedirs("storage", exist_ok=True)

try:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            cache = json.load(f)
    else:
        cache = {}
except json.JSONDecodeError:
    cache = {}

# Check Gemini availability
gemini_available = GEMINI_AVAILABLE and check_gemini_availability() if GEMINI_AVAILABLE else False

def display_hero_section():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">⚡ Pokemon VGC Team Analyzer</h1>
        <p class="hero-subtitle">
            Transform Japanese Pokemon VGC articles into detailed English team analysis with AI-powered insights
        </p>
        <div class="feature-badges">
            <div class="feature-badge">
                <span style="font-size: 1.3rem; margin-right: 8px;">🎯</span>
                <span style="font-weight: 700; font-size: 1.1rem;">Team Analysis</span>
            </div>
            <div class="feature-badge">
                <span style="font-size: 1.3rem; margin-right: 8px;">🤖</span>
                <span style="font-weight: 700; font-size: 1.1rem;">AI Powered</span>
            </div>
            <div class="feature-badge">
                <span style="font-size: 1.3rem; margin-right: 8px;">📊</span>
                <span style="font-weight: 700; font-size: 1.1rem;">EV Spreads</span>
            </div>
            <div class="feature-badge">
                <span style="font-size: 1.3rem; margin-right: 8px;">🌐</span>
                <span style="font-weight: 700; font-size: 1.1rem;">Japanese Translation</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    show_accessibility_controls()
    render_dynamic_accessibility_css()

def display_url_input(cache):
    st.markdown("""
    <div class="modern-card">
        <h2 style="margin: 0 0 16px 0; color: var(--text-primary); font-size: 1.5rem; font-weight: 600;">
            🚀 Start Analyzing
        </h2>
        <p style="color: var(--text-secondary); margin-bottom: 24px; font-size: 1rem;">
            Paste a Japanese Pokemon VGC article URL below to get instant English analysis with detailed team breakdowns
        </p>
    """, unsafe_allow_html=True)
    


    url = st.text_input(
        "Article URL",
        value=st.session_state.get("prefill_url", ""),
        placeholder="https://example.com/pokemon-vgc-article",
        label_visibility="collapsed",
        help="Supported sources: Japanese Pokemon blogs, VGC team reports, strategy guides, and tournament coverage"
    )

    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    # Validate URL
    valid_url = bool(url and re.match(url_pattern, url))
    
    if url and not valid_url:
        st.error("❌ Please enter a valid URL starting with http:// or https://")
    
    # Show status based on URL validity
    if valid_url:
        st.markdown("""
        <div class="status-success">
            <strong>✅ Valid URL</strong><br>
            Ready to analyze with Google Gemini AI
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Analyze Article",
            disabled=not valid_url or st.session_state["summarising"],
            use_container_width=True
        )

    if cache:
        st.markdown("""
        <div style="text-align: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Cache", help="Clear all cached summaries", use_container_width=False):
            cache.clear()
            with open(CACHE_PATH, "w") as f:
                json.dump(cache, f)
            st.success("✅ Cache cleared successfully!")
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    return url, valid_url, analyze_button

def display_results(summary, url):
    parsed_data = parse_summary(summary, url=url)
    # Compute a stable id for logging and sharing
    summary_id = compute_summary_id(url, parsed_data.get('title'), summary)
    st.session_state["current_summary_id"] = summary_id
    # Log view
    try:
        log_view(url or "", parsed_data.get('title') or "VGC Team Analysis", summary_id)
        # Enrich workspace summary metadata
        team_names = [p.get('name') for p in parsed_data.get('pokemon', []) if p.get('name')]
        tournament_guess = ''
        if 'world' in (parsed_data.get('title','').lower()):
            tournament_guess = 'Worlds'
        from utils.workspace import upsert_summary
        upsert_summary(summary_id, url or '', parsed_data.get('title') or 'VGC Team Analysis', team_names, tournament_guess)
    except Exception:
        pass
    
    st.markdown("""
    <div class="results-section" style="margin: 0 auto 48px auto; max-width: 1100px; padding: 0 16px;">
        <div style="background: linear-gradient(135deg, #1a365d 0%, #2a4365 100%); border-radius: 16px; padding: 32px; margin: 0 auto; text-align: center; position: relative; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255, 255, 255, 0.05); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <div style="background: rgba(255, 255, 255, 0.2); width: 64px; height: 64px; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 24px; backdrop-filter: blur(8px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"><span style="font-size: 2rem;">🎯</span></div>
                <h1 style="margin: 0 0 16px 0; color: #ffffff; font-size: 2.5rem; font-weight: 900; letter-spacing: -0.5px; line-height: 1.2; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">Team Analysis Results</h1>
                <p style="color: #ffffff; font-size: 1.15rem; margin: 0 auto; max-width: 700px; line-height: 1.6; font-weight: 500; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Detailed breakdown of the Pokémon team composition, battle strategies, and recommended movesets</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Persistent navigation control (persists across reruns such as downloads)
    nav_options = ["Team Summary", "Pokémon Details", "Article Summary", "Side-by-Side"]
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "Team Summary"
    view = st.radio(
        "View",
        nav_options,
        horizontal=True,
        index=nav_options.index(st.session_state.get("active_view", "Team Summary")),
        key="active_view",
    )

    if view == "Team Summary":
        display_team_summary(parsed_data)
    elif view == "Pokémon Details":
        display_pokemon_details(parsed_data)
    elif view == "Article Summary":
        display_article_summary(parsed_data, summary, url)
    elif view == "Side-by-Side":
        display_side_by_side_translation(parsed_data, summary, url)


    
    # Show file size information
    st.markdown("""
    <div style="margin-top: 16px; text-align: center; color: #6b7280; font-size: 0.85rem;">
        💡 <strong>Tip:</strong> JSON and CSV are best for data analysis, Excel for detailed spreadsheets, and PDF for sharing reports
    </div>
    """, unsafe_allow_html=True)

def display_team_summary(parsed_data):
    # Ensure we never show a placeholder title
    resolved_title = parsed_data.get('title') or 'Team Analysis'
    if not resolved_title or resolved_title.strip().lower() == 'not specified':
        resolved_title = compute_fallback_title(parsed_data, st.session_state.get("current_url"))
    # Force English letters for known JP titles via dictionary reverse mapping
    for jp, ens in JP_TO_EN.items():
        if jp in resolved_title and ens:
            resolved_title = ens[0]
    # If still Japanese, build an English title from Pokémon names
    if contains_japanese(resolved_title):
        built = build_english_title_from_parsed(parsed_data)
        if built:
            resolved_title = built

    if resolved_title:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e4b8c 0%, #1a3a6a 100%); color: white; padding: 36px 32px; max-width: 1000px; margin: 0 auto 32px auto; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 120px; height: 120px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
            <h2 style="margin: 0 0 8px 0; font-size: 2rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">📰 {resolved_title}</h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Analyzed with Google Gemini AI</p>
        </div>
        """, unsafe_allow_html=True)

        # Team archetype meta tagging removed per request

    if parsed_data.get('conclusion'):
        st.markdown(f"""
        <div style="margin: 0 auto 32px auto; max-width: 1100px; padding: 0 16px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 32px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: rgba(255, 255, 255, 0.1); border-radius: 50%;"></div>
                <h3 style="margin: 0 0 16px 0; font-size: 1.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">🎯 Team Strategy Summary</h3>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">{parsed_data['conclusion']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)




def display_pokemon_details(parsed_data):
    if parsed_data.get('pokemon'):
        pokemon_list = parsed_data['pokemon']
        
        st.markdown(f"""
        <div style="background: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 12px 16px; margin: 16px auto; max-width: 1100px; text-align: center; color: #1976d2; font-weight: 600;">
            Found {len(pokemon_list)} Pokemon in the team analysis
        </div>
        """, unsafe_allow_html=True)
        
        for i in range(0, len(pokemon_list), 2):
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                display_pokemon_card_with_summary(pokemon_list[i], i + 1)
            
            with col2:
                if i + 1 < len(pokemon_list):
                    display_pokemon_card_with_summary(pokemon_list[i + 1], i + 2)
                else:
                    st.markdown("<div style='visibility: hidden; height: 1px;'></div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)


def display_article_summary(parsed_data, summary, url):
    st.markdown("""
    <div style="margin-top: 48px; padding-top: 32px; border-top: 2px solid var(--border-color);">
        <h2 style="color: var(--text-primary); font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 24px;">📰 Overall Article Summary</h2>
    </div>
    """, unsafe_allow_html=True)

    # Show article title and source
    # Also ensure title in Article Summary block is not 'Not specified'
    article_block_title = parsed_data.get('title')
    if not article_block_title or article_block_title.strip().lower() == 'not specified':
        article_block_title = compute_fallback_title(parsed_data, url)
    # Ensure English title
    for jp, ens in JP_TO_EN.items():
        if article_block_title and jp in article_block_title and ens:
            article_block_title = ens[0]
    if contains_japanese(article_block_title):
        built = build_english_title_from_parsed(parsed_data)
        if built:
            article_block_title = built

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(30, 64, 175, 0.3);">
        <h3 style="margin: 0 0 8px 0; font-size: 1.5rem; font-weight: 700;">📰 {article_block_title or 'Pokemon VGC Team Analysis'}</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Source: {url}</p>
    </div>
    """, unsafe_allow_html=True)

    # Share controls (copy to clipboard + quick share links)
    share_col, _ = st.columns([1, 3])
    with share_col:
        team_list_for_share = parsed_data.get('pokemon', []) or []
        fp_share = compute_team_fingerprint(team_list_for_share, parsed_data.get('title'), url)
        base_url_share = st.session_state.get("_base_url", "http://localhost:8501")
        permalink_share = build_permalink(base_url_share, fp_share)
        safe_title = article_block_title or 'Pokemon VGC Team Analysis'
        import json as _json
        title_js = _json.dumps(safe_title)
        link_js = _json.dumps(permalink_share)
        components.html(
            f"""
            <div id=\"share-bar\" style=\"display:flex;gap:8px;align-items:center;\">
              <button id=\"copy-link\" style=\"padding:8px 12px;border-radius:10px;border:1px solid #cbd5e1;background:#0ea5e9;color:white;font-weight:600;cursor:pointer;\">🔗 Copy Link</button>
              <button id=\"copy-md\" style=\"padding:8px 12px;border-radius:10px;border:1px solid #cbd5e1;background:#6366f1;color:white;font-weight:600;cursor:pointer;\">📋 Copy Markdown</button>
              <a id=\"wa\" href=\"#\" target=\"_blank\" style=\"text-decoration:none;\"><button style=\"padding:8px 12px;border-radius:10px;border:1px solid #cbd5e1;background:#22c55e;color:white;font-weight:600;cursor:pointer;\">🟢 WhatsApp</button></a>
              <a id=\"tg\" href=\"#\" target=\"_blank\" style=\"text-decoration:none;\"><button style=\"padding:8px 12px;border-radius:10px;border:1px solid #cbd5e1;background:#0ea5e9;color:white;font-weight:600;cursor:pointer;\">🔵 Telegram</button></a>
              <a id=\"tw\" href=\"#\" target=\"_blank\" style=\"text-decoration:none;\"><button style=\"padding:8px 12px;border-radius:10px;border:1px solid #cbd5e1;background:#1d9bf0;color:white;font-weight:600;cursor:pointer;\">𝕏 Share</button></a>
            </div>
            <script>
              const title = {title_js};
              const link = {link_js};
              const copyText = async (text, el, label) => {
                try { await navigator.clipboard.writeText(text); el.textContent = '✅ Copied!'; setTimeout(()=>el.textContent=label,1500);} catch(e){ el.textContent = 'Copy failed'; }
              };
              document.getElementById('copy-link').onclick = () => copyText(link, document.getElementById('copy-link'), '🔗 Copy Link');
              document.getElementById('copy-md').onclick = () => copyText(`[${'{'}title{'}'}] (${ '{'}link{'}'})`, document.getElementById('copy-md'), '📋 Copy Markdown');
              const encoded = encodeURIComponent(`${'{'}title{'}'} — ${'{'}link{'}'}`);
              document.getElementById('wa').href = `https://wa.me/?text=${'{'}encoded{'}'}`;
              document.getElementById('tg').href = `https://t.me/share/url?url=${'{'}encodeURIComponent(link){'}'}&text=${'{'}encodeURIComponent(title){'}'}`;
              document.getElementById('tw').href = `https://twitter.com/intent/tweet?text=${'{'}encodeURIComponent(title){'}'}&url=${'{'}encodeURIComponent(link){'}'}`;
            </script>
            """,
            height=56,
        )

    # Show team composition overview
    if parsed_data.get('pokemon'):
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚡ Team Composition</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Helper to render EV section without markdown code formatting
        def build_ev_block_html(evs: dict | None, ev_text: str | None = None) -> str:
            if evs:
                hp = evs.get('hp', 0); atk = evs.get('attack', 0); deff = evs.get('defense', 0)
                spa = evs.get('sp_attack', 0); spd = evs.get('sp_defense', 0); spe = evs.get('speed', 0)
                return (
                    '<div style="margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;">'
                    '<div style="font-size:0.8rem;color:#64748b;margin-bottom:4px;"><strong>EV Spread:</strong></div>'
                    f'<div style="font-size:0.75rem;color:#64748b;line-height:1.3;">'
                    f'HP: {hp} | Atk: {atk} | Def: {deff} '
                    f'| SpA: {spa} | SpD: {spd} | Spe: {spe}'
                    '</div></div>'
                )
            if ev_text:
                return (
                    '<div style="margin-top:8px;padding-top:8px;border-top:1px solid #e2e8f0;">'
                    '<div style="font-size:0.8rem;color:#64748b;margin-bottom:4px;"><strong>EV Spread:</strong></div>'
                    f'<div style="font-size:0.75rem;color:#64748b;line-height:1.3;">{ev_text}</div>'
                    '</div>'
                )
            return ''

        # Display team members in a grid
        team_cols = st.columns(3)
        for i, pokemon in enumerate(parsed_data['pokemon']):
            col_idx = i % 3
            with team_cols[col_idx]:
                # Prepare EV spread display
                ev_spread_html = build_ev_block_html(pokemon.get('evs'), pokemon.get('ev_spread'))
                
                st.markdown(f"""
                <div style="background: white; border: 2px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="background: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; margin-right: 8px;">{i+1}</div>
                        <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">{pokemon.get('name', 'Unknown')}</h4>
                    </div>
                    <div style="font-size: 0.9rem; color: #64748b;">
                        <div><strong>Ability:</strong> {pokemon.get('ability', 'Not specified')}</div>
                        <div><strong>Item:</strong> {pokemon.get('item', 'Not specified')}</div>
                        <div><strong>Tera:</strong> {pokemon.get('tera_type', 'Not specified')}</div>
                    </div>
                    {ev_spread_html}
                </div>
                """, unsafe_allow_html=True)

    # Extract and display strengths and weaknesses
    strengths, weaknesses = extract_strengths_weaknesses(summary)

    def polish_english(text: str) -> str:
        if not text:
            return ""
        # Basic cleanup
        t = re.sub(r"\s+%", "%", text)
        t = re.sub(r"\s+\.", ".", t)
        t = re.sub(r"\s+,", ",", t)
        t = re.sub(r"\*{1,3}", "", t)
        # Normalize common terms
        replacements = {
            'evs': 'EVs', 'hp': 'HP', 'atk': 'Attack', 'def': 'Defense',
            'spa': 'Special Attack', 'sp.a': 'Special Attack', 'spd': 'Special Defense', 'sp.d': 'Special Defense',
            'spe': 'Speed', 'ko': 'KO', 'ohko': 'OHKO', '2hko': '2HKO', '3hko': '3HKO',
            'pokemon': 'Pokémon'
        }
        for k, v in replacements.items():
            t = re.sub(rf"(?i)\b{k}\b", v, t)
        # Sentence case and ensure periods
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n|;", t) if s.strip()]
        cleaned = []
        for s in sentences:
            s = s[0].upper() + s[1:] if len(s) > 1 else s.upper()
            if s and s[-1] not in '.!?':
                s += '.'
            cleaned.append(s)
        return cleaned

    def render_points(title_html: str, color_box_css: str, text: str):
        points = polish_english(text)
        if not points:
            return
        st.markdown(title_html, unsafe_allow_html=True)
        items = ''.join([f'<div style="margin-bottom: 8px; line-height:1.6;">• {p}</div>' for p in points])
        st.markdown(f"""
        <div style="{color_box_css}">
            {items}
        </div>
        """, unsafe_allow_html=True)

    # Display strengths
    if strengths:
        render_points(
            """
            <div style="margin-bottom: 24px;">
                <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">✅ Team Strengths</h3>
            </div>
            """,
            "background:#ecfdf5;border:1px solid #a7f3d0;color:#065f46;padding:16px;border-radius:12px;",
            strengths,
        )

    # Display weaknesses
    if weaknesses:
        render_points(
            """
            <div style="margin-bottom: 24px;">
                <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚠️ Team Weaknesses</h3>
            </div>
            """,
            "background:#fef2f2;border:1px solid #fecaca;color:#7f1d1d;padding:16px;border-radius:12px;",
            weaknesses,
        )

    # Show comprehensive analysis
    if parsed_data.get('conclusion'):
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">📊 Comprehensive Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
            <div style="color: var(--text-secondary); line-height: 1.6;">
                {parsed_data['conclusion']}
            </div>
        </div>
        """, unsafe_allow_html=True)



    # Create comprehensive download content
    comprehensive_summary = create_comprehensive_summary(parsed_data, summary, url)

    with st.expander("📥 Download Results", expanded=True):
        # Prepare team list once
        team_list = parsed_data.get('pokemon', [])

        # Helper: Showdown format
        def format_evs_showdown(evs: dict) -> str:
            if not evs:
                return ''
            order = [('hp','HP'), ('attack','Atk'), ('defense','Def'), ('sp_attack','SpA'), ('sp_defense','SpD'), ('speed','Spe')]
            parts = []
            for key, label in order:
                val = int(evs.get(key, 0) or 0)
                if val > 0:
                    parts.append(f"{val} {label}")
            return f"EVs: {' / '.join(parts)}" if parts else ''

        def convert_to_showdown_format(team: list) -> str:
            lines = []
            for p in team:
                name = p.get('name', 'Unknown')
                item = p.get('item')
                header = name + (f" @ {item}" if item and item != 'Not specified' else '')
                lines.append(header)
                ability = p.get('ability')
                if ability and ability != 'Not specified':
                    lines.append(f"Ability: {ability}")
                tera = p.get('tera_type')
                if tera and tera != 'Not specified':
                    lines.append(f"Tera Type: {tera}")
                ev_line = format_evs_showdown(p.get('evs') or {})
                if ev_line:
                    lines.append(ev_line)
                nature = p.get('nature')
                if nature and nature != 'Not specified':
                    lines.append(f"{nature} Nature")
                for m in p.get('moves', []) or []:
                    if m:
                        lines.append(f"- {m}")
                lines.append("")
            return "\n".join(lines)

        # Helper: CSV/Excel DataFrame
        def build_team_dataframe(team: list) -> pd.DataFrame:
            rows = []
            for p in team:
                evs = p.get('evs') or {}
                rows.append({
                    'Pokemon': p.get('name',''),
                    'Ability': p.get('ability',''),
                    'Item': p.get('item',''),
                    'Nature': p.get('nature',''),
                    'Tera_Type': p.get('tera_type',''),
                    'Moves': ' / '.join(p.get('moves', []) or []),
                    'Roles': ' | '.join(p.get('roles', []) or []),
                    'HP_EVs': evs.get('hp', 0),
                    'Atk_EVs': evs.get('attack', 0),
                    'Def_EVs': evs.get('defense', 0),
                    'SpA_EVs': evs.get('sp_attack', 0),
                    'SpD_EVs': evs.get('sp_defense', 0),
                    'Spe_EVs': evs.get('speed', 0),
                    'EV_Explanation': p.get('ev_explanation','')
                })
            return pd.DataFrame(rows)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.download_button(
                label="📄 Download as Text",
                data=comprehensive_summary,
                file_name=f"pokemon_analysis.txt",
                mime="text/plain",
                key="dl_text",
            )
            log_download(st.session_state.get("current_summary_id", ""), "txt")
        with col2:
            programmatic_json = {
                "title": parsed_data.get('title', 'Pokemon VGC Analysis'),
                "url": url,
                "archetype_tags": parsed_data.get('archetype_tags', []),
                "team": team_list,
                "conclusion": parsed_data.get('conclusion', '')
            }
            st.download_button(
                label="🧩 Download JSON",
                data=json.dumps(programmatic_json, indent=2, ensure_ascii=False),
                file_name=f"pokemon_team.json",
                mime="application/json",
                key="dl_json",
            )
            log_download(st.session_state.get("current_summary_id", ""), "json")
        with col3:
            showdown_text = convert_to_showdown_format(team_list)
            st.download_button(
                label="🗂️ Showdown Format",
                data=showdown_text,
                file_name=f"pokemon_team_showdown.txt",
                mime="text/plain",
                key="dl_showdown",
            )
            log_download(st.session_state.get("current_summary_id", ""), "showdown")
        with col4:
            df = build_team_dataframe(team_list)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📋 Download CSV",
                data=csv_data,
                file_name=f"pokemon_team.csv",
                mime="text/csv",
                key="dl_csv",
            )
            log_download(st.session_state.get("current_summary_id", ""), "csv")
        with col5:
            df = build_team_dataframe(team_list)
            buffer = io.BytesIO()
            excel_data = None
            try:
                # Prefer openpyxl (commonly present with pandas)
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Team')
                excel_data = buffer.getvalue()
            except Exception:
                # Fallback to xlsxwriter if available
                try:
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Team')
                    excel_data = buffer.getvalue()
                except Exception:
                    excel_data = None
            if excel_data:
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"pokemon_team.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_xlsx",
                )
                log_download(st.session_state.get("current_summary_id", ""), "xlsx")
            else:
                st.info("Excel export requires 'openpyxl' or 'xlsxwriter'. Please install one to enable Excel downloads.")

    # Personal Workspace expander removed; dedicated page now handles history/reading list

    # Social & Sharing: permalink
    # (removed global-share block; share shown on Article Summary page only)

def extract_strengths_weaknesses(summary: str) -> tuple[str, str]:
    """Extract strengths and weaknesses blocks robustly from the LLM output."""
    strengths_block = ""
    weaknesses_block = ""

    # Prefer explicit labeled blocks first (all caps and normal)
    labeled_patterns = [
        (r"\*\*TEAM STRENGTHS\*\*[:\s]*([\s\S]*?)(?=\*\*TEAM WEAKNESSES\*\*|\*\*CONCLUSION\*\*|\Z)", 'strengths'),
        (r"\*\*Strengths\*\*[:\s]*([\s\S]*?)(?=\*\*Weaknesses\*\*|\*\*Conclusion\*\*|\Z)", 'strengths'),
        (r"TEAM STRENGTHS[:\s]*([\s\S]*?)(?=TEAM WEAKNESSES|CONCLUSION|$)", 'strengths'),
        (r"Strengths[:\s]*([\s\S]*?)(?=Weaknesses|Conclusion|$)", 'strengths'),
        (r"\*\*TEAM WEAKNESSES\*\*[:\s]*([\s\S]*?)(?=\*\*CONCLUSION\*\*|\Z)", 'weaknesses'),
        (r"\*\*Weaknesses\*\*[:\s]*([\s\S]*?)(?=\*\*Conclusion\*\*|\Z)", 'weaknesses'),
        (r"TEAM WEAKNESSES[:\s]*([\s\S]*?)(?=TEAM STRENGTHS|CONCLUSION|$)", 'weaknesses'),
        (r"Weaknesses[:\s]*([\s\S]*?)(?=Strengths|Conclusion|$)", 'weaknesses')
    ]

    for pattern, kind in labeled_patterns:
        m = re.search(pattern, summary, re.IGNORECASE)
        if m and not (strengths_block if kind == 'strengths' else weaknesses_block):
            if kind == 'strengths':
                strengths_block = m.group(1).strip()
            else:
                weaknesses_block = m.group(1).strip()

    # Fallback: mine sentences with positive/negative cues from conclusion
    if not strengths_block or not weaknesses_block:
        concl = re.search(r"CONCLUSION[:\s]*([\s\S]*?)(?=\n\n|\Z)", summary, re.IGNORECASE)
        if concl:
            text = concl.group(1)
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
            pos_keys = ["strong","advantage","effective","powerful","successful","good","excellent","outstanding","favorable","synergy","consistent"]
            neg_keys = ["weak","disadvantage","problem","issue","difficult","challenge","vulnerable","struggle","inconsistent","risky"]
            pos = [s for s in sentences if any(k in s.lower() for k in pos_keys)]
            neg = [s for s in sentences if any(k in s.lower() for k in neg_keys)]
            strengths_block = strengths_block or " ".join(pos[:5])
            weaknesses_block = weaknesses_block or " ".join(neg[:5])

    def clean(text: str) -> str:
        if not text:
            return ""
        # Strip markdown
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"`(.*?)`", r"\1", text)
        # Remove bullet markers and extra whitespace
        text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s+", " ", text).strip()
        # Keep short, readable length
        return text

    return clean(strengths_block), clean(weaknesses_block)

def build_highlight_terms(parsed_data: dict) -> list:
    terms = set()
    for p in parsed_data.get('pokemon', []) or []:
        name = p.get('name')
        if name:
            terms.add(name)
        for m in p.get('moves', []) or []:
            if m:
                terms.add(m)
        for key in ('item', 'ability', 'tera_type'):
            val = p.get(key)
            if val and isinstance(val, str):
                terms.add(val)
    # Sort by length desc to avoid partial overlaps first
    return sorted(list(terms), key=lambda x: len(x), reverse=True)

def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

def highlight_text_html(text: str, terms: list) -> str:
    if not text:
        return ""
    safe = html_escape(text)
    # Replace terms (case-insensitive) with <mark>
    for term in terms:
        if not term or not isinstance(term, str):
            continue
        try:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            safe = pattern.sub(lambda m: f"<mark class=\"term\">{html_escape(m.group(0))}</mark>", safe)
        except re.error:
            continue
    # Convert newlines to <br>
    return safe.replace("\n", "<br>")

def display_side_by_side_translation(parsed_data: dict, english_summary: str, url: str):
    st.markdown("""
    <style>
    /* Disable link clicks inside the side-by-side region to prevent accidental navigation */
    #sbs-container a { pointer-events: none !important; text-decoration: none !important; color: inherit !important; }
    /* Also disable any anchor/link interactions in the cross-reference area */
    #xref-container a { pointer-events: none !important; text-decoration: none !important; color: inherit !important; }
    </style>
    <div id="sbs-container" style="margin-top: 24px;">
        <h3 style="color: var(--text-primary); font-size: 1.4rem; font-weight: 700; text-align: center;">🧭 Side-by-Side Translation (Original vs English)</h3>
        <p style="text-align:center; color:#64748b;">Original article text on the left, AI English summary on the right. Key Pokémon, moves, items, and Tera types are highlighted.</p>
    </div>
    """, unsafe_allow_html=True)

    # Fetch original article text (Japanese)
    article_text, _ = fetch_article_text_and_images(url)
    if not article_text:
        st.info("Could not fetch the original article text due to site restrictions. You can paste the Japanese text manually here:")
        article_text = st.text_area("Original Article Text (Japanese)", height=240, label_visibility="collapsed")

    terms = build_highlight_terms(parsed_data)
    left, right = st.columns(2)
    with left:
        st.markdown("<div style='font-weight:700; color:#334155; margin-bottom:8px;'>🇯🇵 Original</div>", unsafe_allow_html=True)
        left_html = highlight_text_html(article_text or "", terms)
        st.markdown(f"<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:12px; height:420px; overflow:auto; font-size:0.95rem; line-height:1.6;'>{left_html}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div style='font-weight:700; color:#334155; margin-bottom:8px;'>🇬🇧 English (AI Summary)</div>", unsafe_allow_html=True)
        right_html = highlight_text_html(english_summary or "", terms)
        st.markdown(f"<div style='background:#ffffff; border:1px solid #e5e7eb; border-radius:10px; padding:12px; height:420px; overflow:auto; font-size:0.95rem; line-height:1.6;'>{right_html}</div>", unsafe_allow_html=True)

    # Word mapping helper: select an English term and show likely Japanese variants
    st.markdown("<div id='xref-container' style='margin-top:16px; font-weight:700; color:#334155;'>🔎 Cross-reference terms</div>", unsafe_allow_html=True)
    english_options = sorted(set([t for t in terms if t in EN_TO_JP]))
    # Guard: ensure options list is stable to avoid UI reselection causing reruns to jump
    if "xref_en_options" not in st.session_state:
        st.session_state["xref_en_options"] = english_options
    else:
        st.session_state["xref_en_options"] = english_options
    # Ensure selectbox changes do not reset results; keep state keys stable and avoid rerun side effects
    selected = st.selectbox(
        "Choose an English term to see Japanese candidates",
        english_options,
        index=0 if english_options else None,
        key="xref_en_to_jp",
    )

    if selected:
        candidates = EN_TO_JP.get(selected, [])
        if candidates:
            st.write("Japanese candidates:", ", ".join(candidates))
        else:
            st.write("No mapping available yet; copy a Japanese token from the left and we will enhance mappings.")

    st.markdown("<div style='margin-top:8px; font-weight:700; color:#334155;'>🔄 Reverse lookup (Japanese → English)</div>", unsafe_allow_html=True)
    jp_selected = st.text_input(
        "Paste a Japanese term to see common English equivalents",
        value=st.session_state.get("xref_jp_to_en", ""),
        key="xref_jp_to_en",
    )
    if jp_selected:
        ens = JP_TO_EN.get(jp_selected.strip(), [])
        if ens:
            st.write("English equivalents:", ", ".join(ens))
        else:
            st.write("No match in the built-in dictionary. We'll add it in future.")

def create_comprehensive_summary(parsed_data, summary, url):
    """Create a comprehensive summary for download with all team details"""
    
    comprehensive = f"""POKEMON VGC TEAM ANALYSIS
{'='*50}

TITLE: {parsed_data.get('title', 'Pokemon VGC Team Analysis')}
SOURCE: {url}
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*50}
TEAM COMPOSITION
{'='*50}

"""
    
    # Add detailed Pokémon information
    for i, pokemon in enumerate(parsed_data.get('pokemon', []), 1):
        comprehensive += f"""Pokemon {i}: {pokemon.get('name', 'Unknown')}
Ability: {pokemon.get('ability', 'Not specified')}
Held Item: {pokemon.get('item', 'Not specified')}
Tera Type: {pokemon.get('tera_type', 'Not specified')}
Nature: {pokemon.get('nature', 'Not specified')}
Moves: {' / '.join(pokemon.get('moves', [])) if pokemon.get('moves') else 'Not specified'}
EV Spread: {pokemon.get('evs', {}).get('hp', 0)} {pokemon.get('evs', {}).get('attack', 0)} {pokemon.get('evs', {}).get('defense', 0)} {pokemon.get('evs', {}).get('sp_attack', 0)} {pokemon.get('evs', {}).get('sp_defense', 0)} {pokemon.get('evs', {}).get('speed', 0)} (HP/Atk/Def/SpA/SpD/Spe)
EV Explanation: {pokemon.get('ev_explanation', 'Not specified')}

"""
    
    # Add comprehensive conclusion based on author's analysis
    comprehensive += f"""{'='*50}
COMPREHENSIVE TEAM ANALYSIS
{'='*50}

{parsed_data.get('conclusion', 'No detailed analysis available.')}

{'='*50}
ORIGINAL LLM OUTPUT
{'='*50}

{summary}

{'='*50}
END OF ANALYSIS
{'='*50}
"""
    
    return comprehensive

def parse_summary(summary, images_data=None, url: str | None = None):
    # Debug: Print the first 500 characters of the summary to see the format
    print("DEBUG: Summary starts with:", summary[:500])
    
    parsed_data = {
        'title': 'Not specified',
        'pokemon': [],
        'conclusion': ''
    }

    # Try different title patterns (handle markdown bold and brackets)
    title_patterns = [
        r'TITLE:\s*\[(.*?)\]',
        r'(?:\*\*)?TITLE:\s*(.*?)(?:\*\*)?(?=\n)',
        r'(?:\*\*)?Title:\s*(.*?)(?:\*\*)?(?=\n)',
        r'#\s*(.*?)(?=\n)',
        r'##\s*(.*?)(?=\n)'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, summary)
        if title_match:
            raw_title = title_match.group(1).strip()
            # Clean markdown and stray asterisks/brackets
            raw_title = re.sub(r'^\*+|\*+$', '', raw_title)
            raw_title = re.sub(r'^\[|\]$', '', raw_title)
            # Remove any residual markdown
            raw_title = re.sub(r'\*\*(.*?)\*\*', r'\1', raw_title)
            parsed_data['title'] = raw_title.strip()
            break

    # Fallback: derive from page HTML title if still unspecified
    if parsed_data['title'] == 'Not specified' and url:
        page_title = get_page_title(url)
        if page_title:
            parsed_data['title'] = page_title

    # Try different ways to split Pokémon sections
    pokemon_sections = []
    
    # Method 1: Look for numbered Pokémon entries (most common format)
    pokemon_numbered = re.findall(r'Pokémon\s*\d+[:\s]+(.*?)(?=Pokémon\s*\d+|CONCLUSION|FINAL|$)', summary, re.DOTALL | re.IGNORECASE)
    if pokemon_numbered:
        pokemon_sections = pokemon_numbered
        print(f"DEBUG: Found {len(pokemon_sections)} Pokémon using numbered method")
    
    # Method 2: Look for Pokémon with dashes
    if not pokemon_sections:
        pokemon_dashed = re.split(r'\n\s*-\s*', summary)
        pokemon_sections = [section for section in pokemon_dashed if any(keyword in section.lower() for keyword in ['ability:', 'item:', 'moves:', 'ev spread:', 'nature:', 'tera:'])]
        print(f"DEBUG: Found {len(pokemon_sections)} Pokémon using dash method")
    
    # Method 3: Look for specific patterns
    if not pokemon_sections:
        split_patterns = [
            '**Pokémon',
            '**Pokemon',
            'Pokémon',
            'Pokemon',
            'Team Member',
            'Member'
        ]
        
        for pattern in split_patterns:
            if pattern in summary:
                pokemon_sections = summary.split(pattern)[1:]
                print(f"DEBUG: Found {len(pokemon_sections)} Pokémon using pattern: {pattern}")
                break
    
    # Method 4: Look for any section with Pokémon data
    if not pokemon_sections:
        # Split by double newlines and look for sections with Pokémon data
        sections = summary.split('\n\n')
        pokemon_sections = []
        for section in sections:
            if any(keyword in section.lower() for keyword in ['ability:', 'item:', 'moves:', 'ev spread:', 'nature:', 'tera:']) and len(section.strip()) > 50:
                pokemon_sections.append(section)
        print(f"DEBUG: Found {len(pokemon_sections)} Pokémon using section method")
    
    # Method 5: Last resort - look for any numbered entries
    if not pokemon_sections:
        pokemon_matches = re.findall(r'\d+[\.:]\s*([^\n]+)', summary)
        if pokemon_matches:
            pokemon_sections = [f"1: {name}" for name in pokemon_matches]
            print(f"DEBUG: Found {len(pokemon_matches)} Pokémon using numbered matches")
    
    print(f"DEBUG: Total Pokémon sections found: {len(pokemon_sections)}")
    if pokemon_sections:
        print(f"DEBUG: First Pokémon section: {pokemon_sections[0][:200]}...")

    for i, section in enumerate(pokemon_sections):
        pokemon_data = {}
        print(f"DEBUG: Processing Pokémon {i+1}")
        print(f"DEBUG: Section preview: {section[:200]}...")
        
        # Method 1: Extract name from the beginning of the section
        pokemon_name = None
        
        # Look for Pokémon name patterns
        name_patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Capitalized words at start
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*:)',  # Before colon
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\s*-)',  # Before dash
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?=\n)',    # Before newline
        ]
        
        for pattern in name_patterns:
            name_match = re.search(pattern, section)
            if name_match:
                pokemon_name = name_match.group(1).strip()
                break
        
        # Method 2: Look for common Pokémon names in the section
        if not pokemon_name:
            common_pokemon = [
                'Calyrex Shadow Rider', 'Calyrex Ice Rider', 'Zamazenta', 'Zacian',
                'Chien-Pao', 'Chi-Yu', 'Amoonguss', 'Dragonite', 'Iron Valiant',
                'Iron Jugulis', 'Iron Crown', 'Miraidon', 'Koraidon', 'Urshifu', 
                'Rillaboom', 'Volcarona'
            ]
            for pokemon in common_pokemon:
                if pokemon.lower() in section.lower():
                    pokemon_name = pokemon
                    break
        
        if pokemon_name:
            # Apply Pokemon name corrections
            corrected_name = strip_html_tags(pokemon_name)
            pokemon_corrections = {
                'Iron Crown': 'Iron Jugulis',
                'iron crown': 'Iron Jugulis'
            }
            corrected_name = pokemon_corrections.get(corrected_name, corrected_name)
            pokemon_data['name'] = corrected_name
            print(f"DEBUG: Found name: {pokemon_data['name']}")
        else:
            print(f"DEBUG: No name found for Pokémon {i+1}")
            continue

        # Extract all data using comprehensive regex patterns
        section_lower = section.lower()
        
        # Extract Ability - improved to stop at next section
        ability_patterns = [
            r'ability[:\s]+([^-•\n]+?)(?=\s*-\s*(?:held item|item|nature|tera|moves|ev spread|ev explanation))',
            r'abilities?[:\s]+([^-•\n]+?)(?=\s*-\s*(?:held item|item|nature|tera|moves|ev spread|ev explanation))',
            r'- ability[:\s]+([^-•\n]+?)(?=\s*-\s*(?:held item|item|nature|tera|moves|ev spread|ev explanation))',
            r'• ability[:\s]+([^-•\n]+?)(?=\s*-\s*(?:held item|item|nature|tera|moves|ev spread|ev explanation))'
        ]
        for pattern in ability_patterns:
            match = re.search(pattern, section_lower)
            if match:
                ability_text = match.group(1).strip()
                # Clean up common ability names and remove extra text
                ability_text = re.sub(r'\s*-\s*(?:held item|item|nature|tera|moves|ev spread|ev explanation).*', '', ability_text)
                pokemon_data['ability'] = strip_html_tags(ability_text.title())
                print(f"DEBUG: Found ability: {pokemon_data['ability']}")
                break
        
        # Extract Item - improved to stop at next section
        item_patterns = [
            r'(?:held\s+)?item[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|nature|tera|moves|ev spread|ev explanation))',
            r'- (?:held\s+)?item[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|nature|tera|moves|ev spread|ev explanation))',
            r'• (?:held\s+)?item[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|nature|tera|moves|ev spread|ev explanation))'
        ]
        for pattern in item_patterns:
            match = re.search(pattern, section_lower)
            if match:
                item_text = match.group(1).strip()
                # Clean up common item names and remove extra text
                item_text = re.sub(r'\s*-\s*(?:ability|nature|tera|moves|ev spread|ev explanation).*', '', item_text)
                # Apply item corrections
                corrected_item = strip_html_tags(item_text.title())
                item_corrections = {
                    'Choice Band': 'Assault Vest',  # Rillaboom correction
                    'choice band': 'Assault Vest',
                    'CHOICE BAND': 'Assault Vest'
                }
                corrected_item = item_corrections.get(corrected_item, corrected_item)
                pokemon_data['item'] = corrected_item
                print(f"DEBUG: Found item: {pokemon_data['item']}")
                break
        
        # Extract Nature - improved to stop at next section
        nature_patterns = [
            r'nature[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|tera|moves|ev spread|ev explanation))',
            r'natures?[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|tera|moves|ev spread|ev explanation))',
            r'- nature[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|tera|moves|ev spread|ev explanation))',
            r'• nature[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|tera|moves|ev spread|ev explanation))'
        ]
        for pattern in nature_patterns:
            match = re.search(pattern, section_lower)
            if match:
                nature_text = match.group(1).strip()
                # Clean up common nature names and remove extra text
                nature_text = re.sub(r'\s*-\s*(?:ability|held item|item|tera|moves|ev spread|ev explanation).*', '', nature_text)
                # Clean up common nature names
                nature_mapping = {
                    'Adamant': 'Adamant',
                    'Jolly': 'Jolly', 
                    'Modest': 'Modest',
                    'Timid': 'Timid',
                    'Bold': 'Bold',
                    'Impish': 'Impish',
                    'Calm': 'Calm',
                    'Careful': 'Careful',
                    'Naive': 'Naive',
                    'Hasty': 'Hasty',
                    'Naughty': 'Naughty',
                    'Lonely': 'Lonely',
                    'Mild': 'Mild',
                    'Quiet': 'Quiet',
                    'Rash': 'Rash',
                    'Brave': 'Brave',
                    'Relaxed': 'Relaxed',
                    'Sassy': 'Sassy',
                    'Gentle': 'Gentle',
                    'Lax': 'Lax'
                }
                pokemon_data['nature'] = strip_html_tags(nature_mapping.get(nature_text.title(), nature_text.title()))
                print(f"DEBUG: Found nature: {pokemon_data['nature']}")
                break
        
        # Extract Tera Type - improved to stop at next section
        tera_patterns = [
            r'tera[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|moves|ev spread|ev explanation))',
            r'tera type[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|moves|ev spread|ev explanation))',
            r'- tera[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|moves|ev spread|ev explanation))',
            r'• tera[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|moves|ev spread|ev explanation))'
        ]
        for pattern in tera_patterns:
            match = re.search(pattern, section_lower)
            if match:
                tera_text = match.group(1).strip()
                # Clean up tera type and remove extra text
                tera_text = re.sub(r'\s*-\s*(?:ability|held item|item|nature|moves|ev spread|ev explanation).*', '', tera_text)
                # Remove accidental leading 'type:' captured from 'Tera Type:'
                tera_text = re.sub(r'^type:\s*', '', tera_text, flags=re.IGNORECASE)
                pokemon_data['tera_type'] = strip_html_tags(tera_text.title())
                print(f"DEBUG: Found tera: {pokemon_data['tera_type']}")
                break
        
        # Extract Moves - improved to stop at next section
        moves_patterns = [
            r'moves?[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
            r'moveset[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
            r'- moves?[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
            r'• moves?[:\s]+([^-•\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))'
        ]
        for pattern in moves_patterns:
            match = re.search(pattern, section_lower)
            if match:
                moves_text = match.group(1).strip()
                # Clean up moves and remove extra text
                moves_text = re.sub(r'\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation).*', '', moves_text)
                # Handle different separators
                if '/' in moves_text:
                    moves_list = [move.strip().title() for move in moves_text.split('/')]
                elif ',' in moves_text:
                    moves_list = [move.strip().title() for move in moves_text.split(',')]
                else:
                    moves_list = [moves_text.title()]
                
                # Filter out abilities that might be incorrectly included in moves
                ability_keywords = ['as one', 'unseen fist', 'grassy surge', 'regenerator', 'quark drive', 'drizzle']
                filtered_moves = []
                for move in moves_list:
                    if move.lower() not in ability_keywords:
                        filtered_moves.append(move)
                
                if filtered_moves:
                    # Apply move name corrections
                    corrected_moves = []
                    for move in filtered_moves:
                        corrected_move = strip_html_tags(move)
                        # Move name corrections
                        move_corrections = {
                            'Bark Out': 'Snarl',
                            'Bark out': 'Snarl',
                            'bark out': 'Snarl'
                        }
                        corrected_move = move_corrections.get(corrected_move, corrected_move)
                        corrected_moves.append(corrected_move)
                    
                    pokemon_data['moves'] = corrected_moves
                    print(f"DEBUG: Found moves: {pokemon_data['moves']}")
                else:
                    print(f"DEBUG: No valid moves found after filtering")
                break
        
        # Extract EV Spread
        ev_patterns = [
            r'ev spread[:\s]+([^:\n]+)',
            r'evs?[:\s]+([^:\n]+)',
            r'effort values?[:\s]+([^:\n]+)',
            r'- ev spread[:\s]+([^:\n]+)',
            r'• ev spread[:\s]+([^:\n]+)',
            r'ev spread[:\s]*(\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+)'  # Direct number format
        ]
        for pattern in ev_patterns:
            match = re.search(pattern, section_lower)
            if match:
                ev_text = match.group(1).strip()
                print(f"DEBUG: Raw EV text extracted: '{ev_text}'")
                # Parse EV values
                evs = {'hp': 0, 'attack': 0, 'defense': 0, 'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
                
                # Try different EV parsing patterns
                ev_parse_patterns = [
                    # Japanese format: H244 A252 B4 D4 S4
                    r'H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)',
                    r'H(\d+)\s+A(\d+)\s+B(\d+)\s+D(\d+)\s+S(\d+)',  # Missing C (SpA)
                    # Standard format: 244 252 4 4 4 4 (space separated) - 6 numbers
                    r'^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$',
                    r'(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)',
                    r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
                    # 5-number format: 44 4 252 28 180 (HP, Def, SpA, SpD, Spe) - Attack assumed 0
                    r'^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$',
                    r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
                    r'HP:\s*(\d+).*?Atk:\s*(\d+).*?Def:\s*(\d+).*?SpA:\s*(\d+).*?SpD:\s*(\d+).*?Spe:\s*(\d+)'
                ]
                
                for i, ev_parse_pattern in enumerate(ev_parse_patterns):
                    ev_match = re.search(ev_parse_pattern, ev_text, re.IGNORECASE)
                    if ev_match:
                        print(f"DEBUG: EV pattern {i} matched: {ev_parse_pattern}")
                        print(f"DEBUG: EV match groups: {ev_match.groups()}")
                        # Handle Japanese format (H=HP, A=Attack, B=Defense, C=SpA, D=SpD, S=Speed)
                        if ev_parse_pattern.startswith(r'H(\d+)'):
                            # Japanese format
                            if len(ev_match.groups()) == 6:
                                # Full format: H244 A252 B4 C4 D4 S4
                                evs['hp'] = int(ev_match.group(1))
                                evs['attack'] = int(ev_match.group(2))
                                evs['defense'] = int(ev_match.group(3))
                                evs['sp_attack'] = int(ev_match.group(4))
                                evs['sp_defense'] = int(ev_match.group(5))
                                evs['speed'] = int(ev_match.group(6))
                            elif len(ev_match.groups()) == 5:
                                # Missing C (SpA): H244 A252 B4 D4 S4
                                evs['hp'] = int(ev_match.group(1))
                                evs['attack'] = int(ev_match.group(2))
                                evs['defense'] = int(ev_match.group(3))
                                evs['sp_attack'] = 0  # Missing C
                                evs['sp_defense'] = int(ev_match.group(4))
                                evs['speed'] = int(ev_match.group(5))
                        else:
                            # Standard format
                            if len(ev_match.groups()) == 6:
                                # 6-number format: HP, Atk, Def, SpA, SpD, Spe
                                stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
                                for j, stat in enumerate(stats):
                                    try:
                                        evs[stat] = int(ev_match.group(j + 1))
                                    except (ValueError, IndexError):
                                        pass
                            elif len(ev_match.groups()) == 5:
                                # 5-number format: HP, Def, SpA, SpD, Spe (Attack assumed 0)
                                # Based on the Iron Valiant example: 44 4 252 28 180
                                try:
                                    evs['hp'] = int(ev_match.group(1))
                                    evs['attack'] = 0  # Assumed 0 for 5-number format
                                    evs['defense'] = int(ev_match.group(2))
                                    evs['sp_attack'] = int(ev_match.group(3))
                                    evs['sp_defense'] = int(ev_match.group(4))
                                    evs['speed'] = int(ev_match.group(5))
                                except (ValueError, IndexError):
                                    pass
                        break
                
                # Ensure EVs add up to 508 or less
                total_evs = sum(evs.values())
                if total_evs > 508 and total_evs > 0:
                    scale_factor = 508 / total_evs
                    for stat in evs:
                        evs[stat] = int(evs[stat] * scale_factor)
                
                pokemon_data['evs'] = evs
                print(f"DEBUG: Found EVs: {evs}")
                print(f"DEBUG: EV parsing breakdown - HP:{evs['hp']}, Atk:{evs['attack']}, Def:{evs['defense']}, SpA:{evs['sp_attack']}, SpD:{evs['sp_defense']}, Spe:{evs['speed']}")
                break
        
        # Extract EV Explanation
        ev_explanation_patterns = [
            r'ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)',
            r'ev reasoning[:\s]+([^:\n]+(?:\n[^:\n]+)*)',
            r'- ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)',
            r'• ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)'
        ]
        for pattern in ev_explanation_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data['ev_explanation'] = strip_html_tags(match.group(1).strip())
                print(f"DEBUG: Found EV explanation: {pokemon_data['ev_explanation'][:100]}...")
                break

        # Only add if we have at least a name
        if pokemon_data.get('name'):
            parsed_data['pokemon'].append(pokemon_data)
            print(f"DEBUG: Added Pokémon {i+1}: {pokemon_data}")
        else:
            print(f"DEBUG: Skipping Pokémon {i+1} - no name found")

    # Try different conclusion patterns
    conclusion_patterns = [
        r'Conclusion Summary:\s*(.*?)(?=\n\n|\Z)',
        r'Conclusion:\s*(.*?)(?=\n\n|\Z)',
        r'Summary:\s*(.*?)(?=\n\n|\Z)',
        r'Team Strategy:\s*(.*?)(?=\n\n|\Z)'
    ]
    
    for pattern in conclusion_patterns:
        conclusion_match = re.search(pattern, summary, re.DOTALL)
        if conclusion_match:
            parsed_data['conclusion'] = strip_html_tags(conclusion_match.group(1).strip())
            break

    # Compute archetype tags
    parsed_data['archetype_tags'] = compute_archetype_tags(parsed_data, summary)

    # Assign roles per Pokémon
    for p in parsed_data.get('pokemon', []):
        p['roles'] = detect_pokemon_roles(p, summary)

    return parsed_data

def get_page_title(url: str) -> str | None:
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        if not resp.ok:
            return None
        soup = BeautifulSoup(resp.content, 'html.parser')
        # Try <title>
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        # Try common meta tags
        for sel in ['meta[property="og:title"]', 'meta[name="twitter:title"]']:
            tag = soup.select_one(sel)
            if tag and tag.get('content'):
                return tag['content'].strip()
        return None
    except Exception:
        return None

def compute_fallback_title(parsed_data: dict, url: str | None) -> str:
    # Try page title first
    if url:
        title = get_page_title(url)
        if title:
            return title
    # Construct from Pokémon names
    names = [p.get('name') for p in parsed_data.get('pokemon', []) if p.get('name')]
    if names:
        head = ', '.join(names[:3])
        suffix = ' +' + str(max(0, len(names) - 3)) if len(names) > 3 else ''
        return f"Team featuring {head}{suffix}"
    # Domain fallback
    if url:
        try:
            from urllib.parse import urlparse
            netloc = urlparse(url).netloc.replace('www.', '')
            return f"VGC Team Analysis • {netloc}"
        except Exception:
            pass
    return "VGC Team Analysis"

def contains_japanese(text: str | None) -> bool:
    if not text:
        return False
    # Hiragana, Katakana, Kanji ranges
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text))

def build_english_title_from_parsed(parsed_data: dict) -> str | None:
    names = [p.get('name') for p in (parsed_data.get('pokemon') or []) if p.get('name')]
    names = [n for n in names if isinstance(n, str) and n.strip()]
    if not names:
        return None
    # Use up to three names for readability
    if len(names) == 1:
        joined = names[0]
    elif len(names) == 2:
        joined = f"{names[0]} + {names[1]}"
    else:
        joined = f"{names[0]} + {names[1]} + {names[2]}"
    return f"{joined} | Team Analysis"

def compute_archetype_tags(parsed_data: dict, full_summary: str) -> list:
    """Infer archetype tags from team and summary text."""
    tags = set()
    team = parsed_data.get('pokemon', []) or []
    text = (full_summary or '').lower()

    def has_move(name: str) -> bool:
        n = name.lower()
        for p in team:
            for m in p.get('moves', []) or []:
                if n in (m or '').lower():
                    return True
        return False

    def has_any_move(names: list) -> bool:
        return any(has_move(n) for n in names)

    def has_item(name: str) -> bool:
        n = name.lower()
        for p in team:
            if n in (p.get('item') or '').lower():
                return True
        return False

    def has_ability(name: str) -> bool:
        n = name.lower()
        for p in team:
            if n in (p.get('ability') or '').lower():
                return True
        return False

    # Trick Room
    if 'trick room' in text or has_move('trick room'):
        tags.add('Trick Room')

    # Tailwind
    if 'tailwind' in text or has_move('tailwind'):
        tags.add('Tailwind')

    # Stall
    stall_signals = (
        has_any_move(['protect','leech seed','recover','roost','strength sap','substitute','iron defense','calm mind','toxic']) or
        has_item('leftovers') or
        has_ability('regenerator') or
        'stall' in text
    )
    if stall_signals:
        tags.add('Stall')

    # Hyper Offense
    offense_signals = (
        has_any_move(['swords dance','nasty plot','dragon dance','belly drum','tailwind']) or
        has_item('choice band') or has_item('choice specs') or has_item('life orb') or
        'hyper offense' in text
    )
    if offense_signals:
        tags.add('Hyper Offense')

    # Balance (default if none detected or explicitly mentioned)
    if 'balance' in text or not tags:
        tags.add('Balance')

    order = ['Trick Room','Tailwind','Balance','Hyper Offense','Stall']
    return [t for t in order if t in tags]

def detect_pokemon_roles(pokemon: dict, full_summary: str) -> list:
    """Detect roles for an individual Pokémon using moves, ability, item, and EVs."""
    roles = set()
    moves = [m.lower() for m in (pokemon.get('moves') or []) if m]
    ability = (pokemon.get('ability') or '').lower()
    item = (pokemon.get('item') or '').lower()
    evs = pokemon.get('evs') or {}
    atk = int(evs.get('attack') or 0)
    spa = int(evs.get('sp_attack') or 0)
    hp = int(evs.get('hp') or 0)
    defn = int(evs.get('defense') or 0)
    spd = int(evs.get('sp_defense') or 0)

    text = (full_summary or '').lower()

    # Speed Control
    speed_moves = {'tailwind','trick room','icy wind','electroweb','thunder wave','bulldoze','sticky web'}
    if any(m in speed_moves for m in moves) or 'trick room' in text:
        roles.add('Speed Control')

    # Support
    support_moves = {
        'fake out','follow me','rage powder','reflect','light screen','aurora veil','helping hand',
        'wide guard','quick guard','snarl','parting shot','will-o-wisp','taunt','encore','ally switch','pollen puff'
    }
    if any(m in support_moves for m in moves) or ability in {'intimidate','prankster'}:
        roles.add('Support')

    # Physical Sweeper
    phys_boost = {'swords dance','dragon dance','bulk up','trailblaze','agility'}
    phys_attacks_common = {'close combat','flare blitz','play rough','earthquake','ice spinner','shadow sneak','aqua jet','extreme speed','knock off'}
    if atk >= max(180, spa) or any(m in phys_boost for m in moves) or sum(1 for m in moves if m in phys_attacks_common) >= 2:
        roles.add('Physical Sweeper')

    # Special Sweeper
    spec_boost = {'nasty plot','calm mind','quiver dance','tail glow','agility'}
    spec_attacks_common = {'hydro pump','shadow ball','moonblast','draco meteor','thunderbolt','heat wave','dazzling gleam','hurricane','overheat'}
    if spa >= max(180, atk) or any(m in spec_boost for m in moves) or sum(1 for m in moves if m in spec_attacks_common) >= 2:
        roles.add('Special Sweeper')

    # Tank / Utility
    tank_moves = {'will-o-wisp','leech seed','strength sap','recover','roost','protect','substitute','iron defense','calm mind','snarl','parting shot','body press','drain punch'}
    defensive_investment = hp + defn + spd
    if any(m in tank_moves for m in moves) or ability in {'intimidate','regenerator','thick fat'} or defensive_investment >= 300:
        roles.add('Tank / Utility')

    # Resolve potential overlaps: keep both sweepers if ambiguous; Support and Speed Control can co-exist
    # Return in a stable order
    order = ['Speed Control','Support','Physical Sweeper','Special Sweeper','Tank / Utility']
    return [r for r in order if r in roles]

def run_analysis(url, cache):
    st.session_state["summarising"] = True
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin: 0 0 16px 0; color: var(--text-primary); font-size: 1.3rem; font-weight: 600;">
            🔄 Processing Article
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Use error recovery system if available
    if ERROR_RECOVERY_AVAILABLE:
        progress_bar, status_text, error_container = create_progress_with_error_handling()
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_container = st.container()
    
    try:
        def perform_analysis():
            """Inner function to perform the actual analysis with retry capability"""
            try:
                if url in cache:
                    status_text.text("📋 Loading from cache...")
                    progress_bar.progress(100)
                    summary = cache[url]["summary"]
                    pokemon_names = cache[url]["pokemon"]
                    st.markdown("""
                    <div class="status-success">
                        <strong>✅ Loaded from Cache</strong><br>
                        Instant results from previously analyzed article
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    status_text.text("🌐 Fetching article content...")
                    progress_bar.progress(25)
                    time.sleep(0.5)
                    
                    status_text.text("🤖 Analyzing with Google Gemini AI...")
                    progress_bar.progress(50)
                    time.sleep(0.5)
                    
                    # Use retry decorator if available
                    if ERROR_RECOVERY_AVAILABLE:
                        summary = retry_api_call(llm_summary_gemini)(url)
                    else:
                        summary = llm_summary_gemini(url)
                    
                    if not isinstance(summary, str):
                        summary = str(summary)
                    
                    # Strip HTML tags from the LLM response
                    summary = strip_html_tags(summary)

                    if not summary or summary.strip() == "":
                        st.markdown("""
                        <div class="status-error">
                            <strong>❌ Analysis Failed</strong><br>
                            Generated summary is empty. Please check the URL and try again.
                        </div>
                        """, unsafe_allow_html=True)
                        progress_bar.empty()
                        status_text.empty()
                        st.session_state["summarising"] = False
                        st.stop()

                    status_text.text("📊 Extracting Pokemon data...")
                    progress_bar.progress(75)
                    time.sleep(0.5)
                    
                    pokemon_names = extract_pokemon_names(summary)

                    status_text.text("💾 Saving to cache...")
                    progress_bar.progress(90)
                    time.sleep(0.5)

                    cache[url] = {
                        "summary": summary,
                        "pokemon": pokemon_names
                    }

                    with open(CACHE_PATH, "w") as f:
                        json.dump(cache, f)

                    progress_bar.progress(100)
                    status_text.text("✅ Analysis Complete!")
                    time.sleep(0.5)
                    
                    progress_bar.empty()
                    status_text.empty()
                    st.markdown("""
                    <div class="status-success">
                        <strong>🎉 Analysis Complete!</strong><br>
                        Powered by Google Gemini AI
                    </div>
                    """, unsafe_allow_html=True)

                st.session_state["current_summary"] = summary
                st.session_state["current_url"] = url
                
                progress_bar.empty()
                status_text.empty()
                
                display_results(summary, url)
                
            except Exception as e:
                if ERROR_RECOVERY_AVAILABLE:
                    error_info = handle_api_error(e, "Article Analysis")
                    with error_container:
                        display_error_with_recovery(error_info, perform_analysis)
                else:
                    st.markdown(f"""
                    <div class="status-error">
                        <strong>❌ Analysis Error</strong><br>
                        {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Start the analysis
        perform_analysis()
        
    finally:
        progress_bar.empty()
        status_text.empty()
        st.session_state["summarising"] = False

# Main application
def main():
    display_hero_section()

    if not gemini_available:
        st.markdown("""
        <div class="status-error">
            <strong>❌ Gemini API Not Available</strong><br>
            Please check your API key configuration in <code>.streamlit/secrets.toml</code>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    url, valid_url, analyze_button = display_url_input(cache)

    if analyze_button and valid_url:
        run_analysis(url, cache)
    else:
        # Persist previously analyzed results across reruns (e.g., after downloads)
        prev_summary = st.session_state.get("current_summary")
        prev_url = st.session_state.get("current_url")
        if prev_summary:
            display_results(prev_summary, prev_url)

if __name__ == "__main__":
    main() 