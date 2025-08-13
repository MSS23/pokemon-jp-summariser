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
import streamlit.components.v1 as components
try:
    import streamlit_authenticator as stauth
except Exception:
    stauth = None

# Import pokemon card display first to ensure it's available
from pokemon_card_display import display_pokemon_card_with_summary
from utils.workspace import (
    compute_summary_id,
    log_view,
    log_download,
    upsert_summary,
)
from utils.permalinks import compute_team_fingerprint, build_permalink
from utils.vgc_format_utils import get_available_formats, get_format_status_info, get_format_info
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
    from utils.shared_utils import extract_pokemon_names, strip_html_tags, fetch_article_text_and_images, extract_moves_from_text
except ImportError as e:
    st.error(f"Failed to import shared utilities: {e}")
    def extract_pokemon_names(summary):
        return []
    def strip_html_tags(text):
        return text
    def fetch_article_text_and_images(url: str):
        return "", []
    def extract_moves_from_text(text: str, pokemon_name: str = None):
        return []



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
    body {
        background-color: #f0f2f6;
    }
    .main-container {
        padding: 0 1rem; /* Remove padding for full-width hero */
    }
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
        text-align: center;
        margin: 0 -2rem 3rem -2rem; /* Extend to full width */
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        margin: 0 0 1rem 0;
        color: white !important;
        line-height: 1.1;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }

    .hero-subtitle {
        font-size: 1.25rem;
        margin: 0 auto;
        max-width: 600px;
        line-height: 1.6;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.8) !important;
    }

    .input-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: -8rem auto 2rem auto; /* Overlap with hero */
        max-width: 700px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
        border: 1px solid var(--border);
        position: relative;
        z-index: 10;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #1f77b4 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 14px 24px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(31, 119, 180, 0.3);
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

    /* Mobile tweaks */
    @media (max-width: 640px) {
        .hero-title { font-size: 2.2rem; }
        .hero-subtitle { font-size: 1rem; }
        .main-container {
            padding: 0;
        }
        .hero-section {
            margin: 0 0 2rem 0;
            border-radius: 0;
        }
        .input-card {
            margin: -4rem auto 2rem auto;
            border-radius: 16px;
            width: calc(50% - 2px); 
            margin-bottom: 6px; 
            font-size: 0.75rem !important;
            padding: 4px 6px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Simple login gate using custom authentication (avoiding streamlit-authenticator issues)
AUTH_REQUIRED = True
if AUTH_REQUIRED:
    try:
        credentials = st.secrets["credentials"]
        # Check if user is already authenticated
        if "authenticated" not in st.session_state:
            st.session_state["authenticated"] = False
        
        if not st.session_state["authenticated"]:
            st.title("🔐 Login Required")
            st.write("Please log in to access the Pokemon Translation Web App.")
            
            # Simple login form
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if username in credentials["usernames"]:
                        user_data = credentials["usernames"][username]
                        
                        # Hash the entered password to compare with stored hash
                        import hashlib
                        entered_password_hash = hashlib.sha256(password.encode()).hexdigest()
                        
                        if user_data["password"] == entered_password_hash:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.session_state["user_name"] = user_data["name"]
                            st.success(f"Welcome back, {user_data['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid password")
                    else:
                        st.error("User not found")
            
            st.stop()
        else:
            # User is authenticated, show logout option
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"Welcome back, {st.session_state['user_name']}!")
            with col2:
                if st.button("Logout"):
                    st.session_state["authenticated"] = False
                    st.session_state["username"] = None
                    st.session_state["user_name"] = None
                    st.rerun()
    except Exception as e:
        st.error(f"Authentication configuration error: {str(e)}")
        st.info("Please check your secrets.toml configuration.")
        st.stop()

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
    
    # VGC Format Selection
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3 style="margin: 0 0 12px 0; color: var(--text-primary); font-size: 1.2rem; font-weight: 600;">
            🏆 VGC Regulation/Format
        </h3>
        <p style="color: var(--text-secondary); margin-bottom: 16px; font-size: 0.9rem;">
            Choose a specific VGC format or let AI auto-detect from the team composition
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Format selection with auto-detect as default
    if "vgc_format" not in st.session_state:
        st.session_state["vgc_format"] = "auto"
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Use dynamic format list from utilities
        available_formats = get_available_formats()
        vgc_format = st.selectbox(
            "VGC Format",
            options=available_formats,
            format_func=lambda x: x[1],
            key="vgc_format_select",
            help="Select the VGC regulation/format for accurate team analysis. Auto-detect is recommended for most cases."
        )
        
        # Extract the format key
        selected_format = vgc_format[0] if isinstance(vgc_format, tuple) else vgc_format
        st.session_state["vgc_format"] = selected_format
        
        # Show custom format input if selected
        if selected_format == "custom":
            custom_format = st.text_input(
                "Custom Format Name",
                value=st.session_state.get("custom_format_name", ""),
                placeholder="e.g., VGC Format I, Custom Tournament Rules, Regional Format",
                help="Enter a custom VGC format name for specialized analysis"
            )
            st.session_state["custom_format_name"] = custom_format
    
    with col2:
        # Show enhanced format info using new status system
        status_info = get_format_status_info(selected_format)
        
        if selected_format == "auto":
            st.markdown(f"""
            <div style="background: {status_info['color']}20; border: 2px solid {status_info['color']}; border-radius: 12px; padding: 16px; margin-top: 20px;">
                <div style="font-size: 0.9rem; color: {status_info['color']}; margin-bottom: 8px;">
                    <strong>{status_info['icon']} {status_info['status_text']}</strong>
                </div>
                <div style="font-size: 0.8rem; color: {status_info['color']}; line-height: 1.4;">
                    {status_info['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif selected_format == "custom" and st.session_state.get("custom_format_name"):
            st.markdown(f"""
            <div style="background: {status_info['color']}20; border: 2px solid {status_info['color']}; border-radius: 12px; padding: 16px; margin-top: 20px;">
                <div style="font-size: 0.9rem; color: {status_info['color']}; margin-bottom: 8px;">
                    <strong>{status_info['icon']} {status_info['status_text']}</strong>
                </div>
                <div style="font-size: 0.8rem; color: {status_info['color']}; line-height: 1.4;">
                    {st.session_state.get("custom_format_name", "Custom Format")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            format_info = get_format_info(selected_format)
            
            st.markdown(f"""
            <div style="background: {status_info['color']}20; border: 2px solid {status_info['color']}; border-radius: 12px; padding: 16px; margin-top: 20px;">
                <div style="font-size: 0.9rem; color: {status_info['color']}; margin-bottom: 8px;">
                    <strong>{status_info['icon']} {status_info['status_text']}</strong>
                </div>
                <div style="font-size: 0.8rem; color: {status_info['color']}; line-height: 1.4;">
                    {format_info['description']}
                </div>
                <div style="font-size: 0.7rem; color: {status_info['color']}; margin-top: 8px; opacity: 0.8;">
                    Mechanics: {', '.join(format_info['mechanics'][:2])}...
                </div>
            </div>
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

def display_results(summary, parsed_data, url):
    parsed_data = parse_summary(summary, url=url)
    # Store parsed_data in session state for feedback system
    st.session_state["parsed_data"] = parsed_data
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
        upsert_summary(summary_id, url or '', parsed_data.get('title') or 'VGC Team Analysis', team_names, tournament_guess)
    except Exception:
        pass
    
    st.markdown("""
    <div class="results-section" style="margin: 0 auto 48px auto; max-width: 1100px; padding: 0 16px;">
        <div style="background: linear-gradient(135deg, #1a365d 0%, #2a4365 100%); border-radius: 16px; padding: 32px; margin: 0 auto; text-align: center; position: relative; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="position: absolute; top: -20px; right: -20px; width: 120px; height: 120px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <div style="background: rgba(255, 255, 255, 0.2); width: 64px; height: 64px; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 24px; backdrop-filter: blur(8px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"><span style="font-size: 2rem;">🎯</span></div>
                <h1 style="margin: 0 0 16px 0; color: #ffffff; font-size: 2.5rem; font-weight: 900; letter-spacing: -0.5px; line-height: 1.2; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">Team Analysis Results</h1>
                <p style="color: #ffffff; font-size: 1.15rem; margin: 0 auto; max-width: 700px; line-height: 1.6; font-weight: 500; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Detailed breakdown of the Pokémon team composition, battle strategies, and recommended movesets</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Modern tab-style navigation
    nav_options = ["Team Summary", "Pokémon Details", "Article Summary", "Side-by-Side"]
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "Team Summary"

    cols = st.columns(len(nav_options))
    for i, option in enumerate(nav_options):
        with cols[i]:
            if st.button(option, key=f"nav_{option}", use_container_width=True):
                st.session_state["active_view"] = option

    # Display the active view
    active_view = st.session_state["active_view"]
    if active_view == "Team Summary":
        display_team_summary(parsed_data, summary)
    elif active_view == "Pokémon Details":
        display_pokemon_details(parsed_data, summary, cache)
    elif active_view == "Article Summary":
        display_article_summary(parsed_data, summary, url)
    elif active_view == "Side-by-Side":
        display_side_by_side_translation(parsed_data, summary, url)


    
    # Show file size information
    st.markdown("""
    <div style="margin-top: 16px; text-align: center; color: #6b7280; font-size: 0.85rem;">
        💡 <strong>Tip:</strong> JSON and CSV are best for data analysis, Excel for detailed spreadsheets, and PDF for sharing reports
    </div>
    """, unsafe_allow_html=True)

def show_corrections_summary(parsed_data):
    """Display a comprehensive summary of corrections made to the Pokemon data"""
    try:
        if 'corrections_made' not in st.session_state:
            return
        
        corrections = st.session_state.get('corrections_made', [])
        if not corrections:
            return
        
        st.markdown("""
        <div style="margin: 24px 0;">
            <h3 style="color: #1e293b; font-size: 1.4rem; font-weight: 700; margin-bottom: 16px;">🔧 Corrections Made</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Group corrections by Pokemon
        pokemon_corrections = {}
        for correction in corrections:
            pokemon_name = correction.get('pokemon_name', 'Unknown')
            if pokemon_name not in pokemon_corrections:
                pokemon_corrections[pokemon_name] = []
            pokemon_corrections[pokemon_name].append(correction)
        
        # Display corrections grouped by Pokemon
        for pokemon_name, pokemon_corr_list in pokemon_corrections.items():
            st.markdown(f"""
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 16px;
            ">
                <div style="color: #1e293b; font-size: 1.2rem; font-weight: 700; margin-bottom: 16px; display: flex; align-items: center;">
                    🎯 {pokemon_name}
                </div>
            """, unsafe_allow_html=True)
            
            for correction in pokemon_corr_list:
                field = correction.get('field', 'Unknown')
                old_value = correction.get('old_value', 'Unknown')
                new_value = correction.get('new_value', 'Unknown')
                timestamp = correction.get('timestamp', '')
                correction_id = correction.get('correction_id', '')
                
                # Format timestamp
                try:
                    if timestamp:
                        dt = datetime.fromisoformat(timestamp)
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = "Unknown"
                except:
                    formatted_time = "Unknown"
                
                st.markdown(f"""
                <div style="
                    background: #f0fdf4;
                    border: 1px solid #22c55e;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                        <div style="color: #15803d; font-size: 1rem; font-weight: 600;">
                            {field.title()}
                        </div>
                        <div style="color: #16a34a; font-size: 0.8rem; font-style: italic;">
                            {formatted_time}
                        </div>
                    </div>
                    <div style="color: #15803d; font-size: 0.9rem; margin-bottom: 8px;">
                        <strong>Before:</strong> {old_value}<br>
                        <strong>After:</strong> {new_value}
                    </div>
                    <div style="color: #16a34a; font-size: 0.8rem; margin-top: 8px; font-style: italic;">
                        ✅ Corrected and saved for all users
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Add a summary section
        total_corrections = len(corrections)
        unique_pokemon = len(pokemon_corrections)
        
        st.markdown(f"""
        <div style="
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
        ">
            <div style="color: #0369a1; font-size: 1rem; font-weight: 600; text-align: center;">
                📊 Summary: {total_corrections} corrections made across {unique_pokemon} Pokemon
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Clear corrections after displaying (optional - you can remove this if you want to keep them)
        # st.session_state['corrections_made'] = []
        
    except Exception as e:
        st.warning(f"Could not display corrections summary: {e}")

def extract_detected_vgc_format(parsed_data: dict, summary: str) -> str:
    """Extract the detected VGC format from the analysis summary"""
    try:
        # Look for VGC format in the summary
        if summary:
            # Check for format indicators in the summary
            summary_lower = summary.lower()
            
            # Look for VGC format patterns with improved detection
            vgc_patterns = [
                r"vgc\s*(\d{4})",
                r"regulation\s*([a-f])",
                r"format:\s*([^\\n]+)",
                r"vgc\s*format:\s*([^\\n]+)",
                r"vgc\s*format\s*([a-i])",
                r"format\s*([a-i])"
            ]
            
            for pattern in vgc_patterns:
                match = re.search(pattern, summary_lower)
                if match:
                    if pattern.startswith("vgc\\s*(\\d{4})"):
                        year = match.group(1)
                        # Map year to letter format
                        year_to_letter = {
                            "2025": "I", "2024": "H", "2023": "G", "2022": "F", 
                            "2021": "E", "2020": "D", "2019": "C", "2018": "B", "2017": "A"
                        }
                        letter = year_to_letter.get(year, year)
                        return f"VGC Format {letter} (Regulation {letter}) - Detected from Analysis"
                    elif pattern.startswith("regulation\\s*([a-f])") or pattern.startswith("format\\s*([a-i])"):
                        reg = match.group(1).upper()
                        return f"VGC Format {reg} (Regulation {reg}) - Detected from Analysis"
                    elif pattern.startswith("vgc\\s*format\\s*([a-i])"):
                        reg = match.group(1).upper()
                        return f"VGC Format {reg} (Regulation {reg}) - Detected from Analysis"
                    else:
                        return f"{match.group(1).title()} - Detected from Analysis"
            
            # Check for specific mechanics and map to specific formats
            if "tera" in summary_lower:
                # Tera types are in Formats A-I (Scarlet/Violet era)
                return "VGC Format I (Regulation I) - Tera Types Era - Detected from Analysis"
            elif "dynamax" in summary_lower:
                # Dynamax is in Formats A-E (Sword/Shield era)
                return "VGC Format E (Regulation E) - Dynamax Era - Detected from Analysis"
            elif "z-move" in summary_lower or "z-moves" in summary_lower:
                # Z-moves are in Formats A-C (Sun/Moon era)
                return "VGC Format C (Regulation C) - Z-Move Era - Detected from Analysis"
            elif "mega evolution" in summary_lower or "mega" in summary_lower:
                # Mega Evolution is in Formats A-B (X/Y era)
                return "VGC Format B (Regulation B) - Mega Evolution Era - Detected from Analysis"
        
        # Fallback: check parsed data for format information
        if parsed_data.get('vgc_format'):
            format_info = get_format_info(parsed_data['vgc_format'])
            if format_info:
                return f"{format_info['name']} - From Team Data"
            return parsed_data['vgc_format']
        
        return None
        
    except Exception as e:
        print(f"Error extracting VGC format: {e}")
        return None

def display_team_summary(parsed_data, summary=None):
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
        <div style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: white; padding: 36px 32px; max-width: 1000px; margin: 0 auto 32px auto; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="position: absolute; top: -20px; right: -20px; width: 120px; height: 120px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <div style="background: rgba(255, 255, 255, 0.2); width: 64px; height: 64px; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 24px; backdrop-filter: blur(8px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"><span style="font-size: 2rem;">🎯</span></div>
                <h1 style="margin: 0 0 16px 0; color: #ffffff; font-size: 2.5rem; font-weight: 900; letter-spacing: -0.5px; line-height: 1.2; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">Team Analysis Results</h1>
                <p style="color: #ffffff; font-size: 1.15rem; margin: 0 auto; max-width: 700px; line-height: 1.6; font-weight: 500; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Detailed breakdown of the Pokémon team composition, battle strategies, and recommended movesets</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    # Modern tab-style navigation
    nav_options = ["Team Summary", "Pokémon Details", "Article Summary", "Side-by-Side"]
    if "active_view" not in st.session_state:
        st.session_state["active_view"] = "Team Summary"

    cols = st.columns(len(nav_options))
    for i, option in enumerate(nav_options):
        with cols[i]:
            if st.button(option, key=f"nav_{option}", use_container_width=True):
                st.session_state["active_view"] = option

    # Display the active view
    active_view = st.session_state["active_view"]
    if active_view == "Team Summary":
        display_team_summary(parsed_data, summary)
    elif active_view == "Pokémon Details":
        display_pokemon_details(parsed_data, summary, cache)
    elif active_view == "Article Summary":
        display_article_summary(parsed_data, summary, url)
    elif active_view == "Side-by-Side":
        display_side_by_side_translation(parsed_data, summary, url)


    
    # Show file size information
    st.markdown("""
    <div style="margin-top: 16px; text-align: center; color: #6b7280; font-size: 0.85rem;">
        💡 <strong>Tip:</strong> JSON and CSV are best for data analysis, Excel for detailed spreadsheets, and PDF for sharing reports
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

def build_ev_block_html(evs: dict | None, ev_text: str | None = None, ev_explanation: str | None = None) -> str:
    # Stat order and colors
    stat_order = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
    stat_colors = {
        "HP": ("#ef4444", "#dc2626"), "Atk": ("#f97316", "#ea580c"), "Def": ("#eab308", "#ca8a04"),
        "SpA": ("#8b5cf6", "#7c3aed"), "SpD": ("#3b82f6", "#2563eb"), "Spe": ("#ec4899", "#db2777")
    }
    
    ev_spread_html = ''
    if evs:
        bars_html = ""
        # Ensure evs is a dictionary
        evs_dict = evs if isinstance(evs, dict) else {}
        for stat in stat_order:
            value = evs_dict.get(stat, 0)
            try:
                value = int(value)
            except (ValueError, TypeError):
                value = 0
            
            percentage = (value / 252) * 100 if value > 0 else 0
            color_start, color_end = stat_colors.get(stat, ("#6b7280", "#4b5563"))

            bars_html += f'''
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                        border: 1px solid #e2e8f0; 
                        border-radius: 8px; 
                        padding: 8px 12px; 
                        margin-bottom: 6px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                    <span style="font-weight: 600; color: #374151; font-size: 0.8rem;">{stat}</span>
                    <span style="font-weight: 700; color: {color_start}; font-size: 0.85rem;">{value}</span>
                </div>
                <div style="width: 100%; height: 8px; background: #f1f5f9; border-radius: 8px; overflow: hidden;">
                    <div style="height: 100%; background: linear-gradient(90deg, {color_start} 0%, {color_end} 100%); width: {percentage}%; border-radius: 6px;"></div>
                </div>
            </div>
            '''
        ev_spread_html = bars_html

    elif ev_text:
        # We still escape this since it's user-provided text, not pre-formatted HTML
        ev_spread_html = f"<p style='margin: 0 0 16px 0; font-family: monospace; background: #f8fafc; padding: 12px; border-radius: 8px;'>{html_escape(ev_text)}</p>"

    explanation_html = ''
    if ev_explanation:
        # We also escape the explanation for security
        explanation_html = f"<p style='margin-top: 12px; font-style: italic; color: #4b5563; font-size: 0.85rem;'>{html_escape(ev_explanation)}</p>"

    if not ev_spread_html and not explanation_html:
        return ""

    # The main container is now a raw string that includes the unescaped HTML
    return f'''
    <div style="background: #f0f9ff; border: 1px solid #e0f2fe; border-radius: 12px; padding: 16px; margin-top: 16px;">
        <h5 style="font-weight: 700; color: #0c4a6e; margin: 0 0 12px 0; font-size: 0.95rem;">EV Strategy</h5>
        {ev_spread_html}
        {explanation_html}
    </div>
    '''

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
    <div style="background: linear-gradient(135deg, #1e4b8c 0%, #1a3a6a 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(30, 64, 175, 0.3);">
        <h3 style="margin: 0 0 8px 0; font-size: 1.5rem; font-weight: 700;">📰 {article_block_title or 'Pokemon VGC Team Analysis'}</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Source: {url}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show corrections summary if any exist
    show_corrections_summary(parsed_data)

    # Share controls (copy to clipboard + quick share links) - Fixed layout
    st.markdown("### 📤 Share This Analysis")
    
    team_list_for_share = parsed_data.get('pokemon', []) or []
    fp_share = compute_team_fingerprint(team_list_for_share, parsed_data.get('title'), url)
    base_url_share = st.session_state.get("_base_url", "http://localhost:8501")
    permalink_share = build_permalink(base_url_share, fp_share)
    safe_title = article_block_title or 'Pokemon VGC Team Analysis'
    import json as _json
    title_js = _json.dumps(safe_title)
    link_js = _json.dumps(permalink_share)
    
    # Create a more compact and responsive share bar that won't get cut off
    components.html(
        """
        <style>
        #share-bar {
            display: flex;
            gap: 6px;
            align-items: center;
            flex-wrap: wrap;
            justify-content: flex-start;
            width: 100%;
            max-width: 100%;
            padding: 8px 0;
        }
        #share-bar button {
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.85rem;
            white-space: nowrap;
            min-width: fit-content;
            transition: all 0.2s ease;
        }
        #share-bar button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        #share-bar a {
            text-decoration: none;
        }
        @media (max-width: 768px) {
            #share-bar {
                gap: 4px;
            }
            #share-bar button {
                padding: 5px 8px;
                font-size: 0.8rem;
            }
        }
        </style>
        <div id="share-bar">
          <button id="copy-link" style="background:#0ea5e9;color:white;">🔗 Copy Link</button>
          <button id="copy-md" style="background:#6366f1;color:white;">📋 Copy Markdown</button>
          <a id="wa" href="#" target="_blank">
            <button style="background:#22c55e;color:white;">🟢 WhatsApp</button>
          </a>
          <a id="tg" href="#" target="_blank">
            <button style="background:#0ea5e9;color:white;">🔵 Telegram</button>
          </a>
          <a id="tw" href="#" target="_blank">
            <button style="background:#1d9bf0;color:white;">𝕏 Share</button>
          </a>
        </div>
        <script>
          const title = """ + title_js + """;
          const link = """ + link_js + """;
          const copyText = async (text, el, label) => {
            try { 
              await navigator.clipboard.writeText(text); 
              el.textContent = '✅ Copied!'; 
              setTimeout(()=>el.textContent=label,1500);
            } catch(e){ 
              el.textContent = 'Copy failed'; 
            }
          };
          document.getElementById('copy-link').onclick = () => copyText(link, document.getElementById('copy-link'), '🔗 Copy Link');
          document.getElementById('copy-md').onclick = () => copyText('[' + title + '] (' + link + ')', document.getElementById('copy-md'), '📋 Copy Markdown');
          const encoded = encodeURIComponent(title + ' — ' + link);
          document.getElementById('wa').href = 'https://wa.me/?text=' + encoded;
          document.getElementById('tg').href = 'https://t.me/share/url?url=' + encodeURIComponent(link) + '&text=' + encodeURIComponent(title);
          document.getElementById('tw').href = 'https://twitter.com/intent/tweet?text=' + encodeURIComponent(title) + '&url=' + encodeURIComponent(link);
        </script>
        """,
        height=80,
    )

    # Show team composition overview
    if parsed_data.get('pokemon'):
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚡ Team Composition</h3>
        </div>
        """, unsafe_allow_html=True)

        team = parsed_data.get('pokemon', [])
        if team:
            team_cols = st.columns(3)
            for i, pokemon in enumerate(team):
                col_idx = i % 3
                with team_cols[col_idx]:
                    pokemon_evs = pokemon.get('evs')
                    pokemon_ev_spread = pokemon.get('ev_spread')
                    pokemon_ev_explanation = pokemon.get('ev_explanation')
                    ev_spread_html = build_ev_block_html(pokemon_evs, pokemon_ev_spread, pokemon_ev_explanation)
                    
                    # Simplified card display
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; height: 100%;">
                        <h4 style="font-weight: 700; color: #1e293b; margin-bottom: 12px;">{pokemon.get('name', 'Unknown')}</h4>
                        <p style="font-size: 0.9rem; color: #4b5563;"><strong>Item:</strong> {pokemon.get('item', 'N/A')}</p>
                        <p style="font-size: 0.9rem; color: #4b5563;"><strong>Ability:</strong> {pokemon.get('ability', 'N/A')}</p>
                        <p style="font-size: 0.9rem; color: #4b5563;"><strong>Tera:</strong> {pokemon.get('tera_type', 'N/A')}</p>
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

def build_structured_summary_html(parsed_data: dict) -> str:
    # Helper to safely escape HTML content
    def h(text):
        return html.escape(str(text)) if text is not None else ''

    # Title and VGC format
    title = h(parsed_data.get('title', ''))
    vgc_format = h(parsed_data.get('vgc_format', ''))
    html_content = f"""
    <div style="padding: 8px; font-family: sans-serif; color: var(--text-color);">
        <p style="font-size: 0.9rem; color: #64748b; margin:0;"><strong>VGC FORMAT:</strong> {vgc_format}</p>
        <h4 style="font-size: 1.2rem; font-weight: 700; margin-top: 4px;">{title}</h4>
        <div style="border-bottom: 1px solid var(--border-color); margin: 12px 0;"></div>
    """

    # Pokémon details
    pokemon_list = parsed_data.get('pokemon', [])
    for i, p in enumerate(pokemon_list):
        moves = p.get('moves', [])
        moves_html = "".join([f"<li style='margin-bottom: 4px;'>{h(move)}</li>" for move in moves if move])
        
        html_content += f"""
        <div style="margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color);">
            <h5 style="font-size: 1.1rem; font-weight: 600; color: var(--text-primary); margin-bottom: 8px;">
                Pokémon {i+1}: {h(p.get('name', ''))}
            </h5>
            <ul style="list-style: none; padding-left: 0; font-size: 0.9rem; color: #4b5563;">
                <li style="margin-bottom: 4px;"><strong>Ability:</strong> {h(p.get('ability', 'N/A'))}</li>
                <li style="margin-bottom: 4px;"><strong>Item:</strong> {h(p.get('item', 'N/A'))}</li>
                <li style="margin-bottom: 4px;"><strong>Tera Type:</strong> {h(p.get('tera_type', 'N/A'))}</li>
                <li style="margin-bottom: 4px;"><strong>Nature:</strong> {h(p.get('nature', 'N/A'))}</li>
            </ul>
            <div style="margin-top: 10px;">
                <h6 style="font-weight: 600; margin-bottom: 6px;">Moves:</h6>
                <ul style="list-style-type: disc; padding-left: 20px; font-size: 0.9rem;">{moves_html}</ul>
            </div>
            <div style="margin-top: 10px;">
                <h6 style="font-weight: 600; margin-bottom: 6px;">EV Spread:</h6>
                <p style="font-family: monospace; background: var(--secondary-bg); padding: 8px; border-radius: 6px; font-size: 0.85rem;">{h(p.get('ev_spread', 'N/A'))}</p>
                <p style="font-style: italic; font-size: 0.85rem; color: #64748b; margin-top: 6px;">{h(p.get('ev_explanation', ''))}</p>
            </div>
        </div>
        """

    html_content += "</div>"
    return html_content

def display_side_by_side_translation(parsed_data: dict, english_summary: str, url: str):
    st.markdown("""
    <style>
    /* Disable link clicks inside the side-by-side region to prevent accidental navigation */
    #sbs-container a { pointer-events: none !important; text-decoration: none !important; color: inherit !important; }
    /* Also disable any anchor/link interactions in the cross-reference area */
    #xref-container a { pointer-events: none !important; text-decoration: none !important; color: inherit !important; }
    
    /* Dark mode text readability improvements */
    .side-by-side-panel {
        background: var(--background-color, #ffffff) !important;
        border: 1px solid var(--border-color, #e5e7eb) !important;
        border-radius: 10px !important;
        padding: 12px !important;
        height: 420px !important;
        overflow: auto !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        color: var(--text-color, #1f2937) !important;
    }
    
    /* Ensure highlighted terms are visible in both light and dark modes */
    .side-by-side-panel mark.term {
        background-color: #fbbf24 !important;
        color: #1f2937 !important;
        padding: 2px 4px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
    }
    
    /* Dark mode specific overrides */
    @media (prefers-color-scheme: dark) {
        .side-by-side-panel {
            background: #1e293b !important;
            border-color: #475569 !important;
            color: #f1f5f9 !important;
        }
        
        .side-by-side-panel mark.term {
            background-color: #fbbf24 !important;
            color: #1f2937 !important;
        }
    }
    
    /* Streamlit dark mode detection */
    [data-testid="stAppViewContainer"] .side-by-side-panel {
        background: #1e293b !important;
        border-color: #475569 !important;
        color: #f1f5f9 !important;
    }
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
        st.markdown("<div style='font-weight:700; color:var(--text-color, #334155); margin-bottom:8px;'>🇯🇵 Original</div>", unsafe_allow_html=True)
        left_html = highlight_text_html(article_text or "", terms)
        st.markdown(f"<div class='side-by-side-panel'>{left_html}</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div style='font-weight:700; color:var(--text-color, #334155); margin-bottom:8px;'>🇬🇧 English (AI Summary)</div>", unsafe_allow_html=True)
        structured_summary_html = build_structured_summary_html(parsed_data)
        right_html = highlight_text_html(structured_summary_html, terms)
        st.markdown(f"<div class='side-by-side-panel'>{right_html}</div>", unsafe_allow_html=True)

    # Word mapping helper: select an English term and show likely Japanese variants
    st.markdown("<div id='xref-container' style='margin-top:16px; font-weight:700; color:var(--text-color, #334155);'>🔎 Cross-reference terms</div>", unsafe_allow_html=True)
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

    st.markdown("<div style='margin-top:8px; font-weight:700; color:var(--text-color, #334155);'>🔄 Reverse lookup (Japanese → English)</div>", unsafe_allow_html=True)
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
Moves: {' / '.join(pokemon.get('moves', []) or []) if pokemon.get('moves') else 'Not specified'}
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

    
    # Method 2: Look for Pokémon with dashes
    if not pokemon_sections:
        pokemon_dashed = re.split(r'\n\s*-\s*', summary)
        pokemon_sections = [section for section in pokemon_dashed if any(keyword in section.lower() for keyword in ['ability:', 'item:', 'moves:', 'ev spread:', 'nature:', 'tera:'])]

    
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
        
                break
    
    # Method 4: Look for any section with Pokémon data
    if not pokemon_sections:
        # Split by double newlines and look for sections with Pokémon data
        sections = summary.split('\n\n')
        pokemon_sections = []
        for section in sections:
            if any(keyword in section.lower() for keyword in ['ability:', 'item:', 'moves:', 'ev spread:', 'nature:', 'tera:']) and len(section.strip()) > 50:
                pokemon_sections.append(section)

    
    # Method 5: Last resort - look for any numbered entries
    if not pokemon_sections:
        pokemon_matches = re.findall(r'\d+[\.:]\s*([^\n]+)', summary)
        if pokemon_matches:
            pokemon_sections = [f"1: {name}" for name in pokemon_matches]
    
    

    if pokemon_sections:
        for i, section in enumerate(pokemon_sections):
            pokemon_data = {}


            
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
    
            else:
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
                    break
        
            # Use the improved move extraction function
            moves = extract_moves_from_text(section, pokemon_data.get('name'))
            
            if moves:
                pokemon_data['moves'] = moves
            else:
                pokemon_data['moves'] = []

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
                        r'HP:\s*(\d+).*?Atk:\s*(\d+).*?Def:\s*(\d+).*?SpD:\s*(\d+).*?Spe:\s*(\d+)'
                    ]
                
                    for i, ev_parse_pattern in enumerate(ev_parse_patterns):
                        ev_match = re.search(ev_parse_pattern, ev_text, re.IGNORECASE)
                        if ev_match:
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
                    break
        
            # Extract EV Explanation - Enhanced to capture comprehensive explanations
            ev_explanation_patterns = [
                r'ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)',
                r'ev reasoning[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)',
                r'- ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)',
                r'• ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)',
                r'ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\nPokémon|$)',
                r'ev reasoning[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\nPokémon|$)',
                r'説明[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)',
                r'努力値説明[:\s]+([^:\n]+(?:\n[^:\n]+)*?)(?=\n\n|\n[A-Z][a-z]+:|$)'
            ]
            for pattern in ev_explanation_patterns:
                match = re.search(pattern, section_lower)
                if match:
                    pokemon_data['ev_explanation'] = strip_html_tags(match.group(1).strip())
                    break

            # Only add if we have at least a name
            if pokemon_data.get('name'):
                parsed_data['pokemon'].append(pokemon_data)


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

def run_analysis(url, vgc_format):
    """Run new analysis and update session state."""
    summary, parsed_data = analyse_article(url, vgc_format)
    if summary and parsed_data:
        st.session_state['summary'] = summary
        st.session_state['parsed_data'] = parsed_data
        st.session_state['url_to_analyse'] = url
        st.session_state['analysis_triggered'] = False # Reset trigger
        st.rerun()

def analyse_article(url, vgc_format):
    if not url:
        st.warning("Please enter a URL.")
        return None, None

    cache = load_cache()
    if url in cache:
        st.toast("Previously cached summary used.")
        cached_entry = cache[url]
        # Ensure parsed_data exists from cache
        if "parsed_data" not in cached_entry:
            cached_entry["parsed_data"] = parse_summary(cached_entry["summary"])
        return cached_entry.get("summary"), cached_entry.get("parsed_data")

    with st.spinner("Fetching and analyzing article..."):
        try:
            # This function should call the LLM and then parse the summary
            summary_text, _ = get_gemini_summary(url, vgc_format)
            
            if not summary_text or summary_text.strip() == "":
                st.error("Analysis failed: Generated summary is empty.")
                return None, None

            # Parse the summary to get structured data
            parsed_data = parse_summary(summary_text, url=url)

            # Cache both the raw summary and the parsed data
            cache[url] = {
                "summary": summary_text,
                "parsed_data": parsed_data,
                "timestamp": datetime.now().isoformat()
            }
            save_cache(cache)
            st.success("Analysis complete!")
            return summary_text, parsed_data

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            st.exception(e)
            return None, None



# Main application
def main():
    try:
        st.markdown('<div class="main-container">', unsafe_allow_html=True)

        # Redesigned Hero Section
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">Pokémon VGC Team Analyzer</h1>
            <p class="hero-subtitle">Transform Japanese Pokémon VGC articles into detailed English team analysis with AI-powered insights.</p>
        </div>
        """, unsafe_allow_html=True)

        # Consolidated Input Card
        with st.container():
            st.markdown('<div class="input-card">', unsafe_allow_html=True)

            if not GEMINI_AVAILABLE:
                st.markdown("""
                <div class="status-error">
                    <strong>❌ Gemini API Not Available</strong><br>
                    Please check your API key configuration in <code>.streamlit/secrets.toml</code>
                </div>
                """, unsafe_allow_html=True)
                st.stop()

            url = st.text_input(
                "Enter the URL of the VGC team report article",
                placeholder="e.g., https://victoryroadvgc.com/2023-worlds-teams/",
                key="url_input",
                label_visibility="collapsed"
            )

            cols = st.columns([3, 1])
            with cols[0]:
                available_formats = get_available_formats()
                selected_format = st.selectbox(
                    "VGC Format",
                    options=["Auto-detect"] + available_formats,
                    index=0,
                    help="Selecting a format can improve accuracy if auto-detection fails.",
                    label_visibility="collapsed"
                )
            
            with cols[1]:
                analyze_button = st.button("Analyze Article", use_container_width=True)

            if analyze_button:
                if url:
                    st.session_state['analysis_triggered'] = True
                    st.session_state['url_to_analyse'] = url
                    st.session_state['selected_format'] = selected_format
                else:
                    st.warning("Please enter a URL to analyse.")

            st.markdown('</div>', unsafe_allow_html=True)

        # Analysis and Results Display Logic (remains the same)
        if st.session_state.get('analysis_triggered', False):
            url_to_analyse = st.session_state.get('url_to_analyse', '')
            format_to_analyse = st.session_state.get('selected_format', 'Auto-detect')
            if url_to_analyse:
                run_analysis(url_to_analyse, format_to_analyse)

        if 'summary' in st.session_state and 'parsed_data' in st.session_state:
            display_results(st.session_state['summary'], st.session_state['parsed_data'], st.session_state.get('url_to_analyse', ''))

    finally:
        st.markdown('</div>', unsafe_allow_html=True) # Close main-container

if __name__ == "__main__":
    main() 