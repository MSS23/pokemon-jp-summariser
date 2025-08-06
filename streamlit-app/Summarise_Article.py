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

# Import pokemon card display first to ensure it's available
from pokemon_card_display import display_pokemon_card_with_summary

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
    # Add shared directory to path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
    from utils.shared_utils import extract_pokemon_names
except ImportError as e:
    st.error(f"Failed to import shared utilities: {e}")
    def extract_pokemon_names(summary):
        return []

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
</style>
""", unsafe_allow_html=True)

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
    parsed_data = parse_summary(summary)
    
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

    tab1, tab2, tab3 = st.tabs(["Team Summary", "Pokémon Details", "Article Summary"])

    with tab1:
        display_team_summary(parsed_data)

    with tab2:
        display_pokemon_details(parsed_data)

    with tab3:
        display_article_summary(parsed_data, summary, url)

def display_team_summary(parsed_data):
    if parsed_data.get('title'):
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e4b8c 0%, #1a3a6a 100%); color: white; padding: 36px 32px; max-width: 1000px; margin: 0 auto 32px auto; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 120px; height: 120px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
            <h2 style="margin: 0 0 8px 0; font-size: 2rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">📰 {parsed_data['title']}</h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Analyzed with Google Gemini AI</p>
        </div>
        """, unsafe_allow_html=True)

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
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(30, 64, 175, 0.3);">
        <h3 style="margin: 0 0 8px 0; font-size: 1.5rem; font-weight: 700;">📰 {parsed_data.get('title', 'Pokemon VGC Team Analysis')}</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Source: {url}</p>
    </div>
    """, unsafe_allow_html=True)

    # Show team composition overview
    if parsed_data.get('pokemon'):
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚡ Team Composition</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Display team members in a grid
        team_cols = st.columns(3)
        for i, pokemon in enumerate(parsed_data['pokemon']):
            col_idx = i % 3
            with team_cols[col_idx]:
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
                </div>
                """, unsafe_allow_html=True)

    # Extract and display strengths and weaknesses
    strengths, weaknesses = extract_strengths_weaknesses(summary)
    
    # Display strengths
    if strengths:
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">✅ Team Strengths</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Format strengths as bullet points if they contain multiple points
        if ';' in strengths or ' and ' in strengths or ' but ' in strengths:
            # Split into bullet points
            points = re.split(r'[;]|(?:\s+and\s+)|(?:\s+but\s+)', strengths)
            points = [point.strip() for point in points if point.strip()]
            
            strengths_html = ""
            for point in points:
                if point:
                    strengths_html += f'<div style="margin-bottom: 8px;">• {point}</div>'
        else:
            strengths_html = f'<div style="line-height: 1.6;">{strengths}</div>'
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);">
            {strengths_html}
        </div>
        """, unsafe_allow_html=True)

    # Display weaknesses
    if weaknesses:
        st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚠️ Team Weaknesses</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Format weaknesses as bullet points if they contain multiple points
        if ';' in weaknesses or ' and ' in weaknesses or ' but ' in weaknesses:
            # Split into bullet points
            points = re.split(r'[;]|(?:\s+and\s+)|(?:\s+but\s+)', weaknesses)
            points = [point.strip() for point in points if point.strip()]
            
            weaknesses_html = ""
            for point in points:
                if point:
                    weaknesses_html += f'<div style="margin-bottom: 8px;">• {point}</div>'
        else:
            weaknesses_html = f'<div style="line-height: 1.6;">{weaknesses}</div>'
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3);">
            {weaknesses_html}
        </div>
        """, unsafe_allow_html=True)

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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.download_button(
                label="📄 Download as Text",
                data=comprehensive_summary,
                file_name=f"pokemon_analysis.txt",
                mime="text/plain",
            )
        with col2:
            json_data = {
                "title": parsed_data.get('title', 'Pokemon VGC Analysis'),
                "pokemon": parsed_data.get('pokemon', []),
                "conclusion": parsed_data.get('conclusion', ''),
                "url": url,
                "pokemon_count": len(parsed_data.get('pokemon', []))
            }
            st.download_button(
                label="📊 Download as JSON",
                data=json.dumps(json_data, indent=2, ensure_ascii=False),
                file_name=f"pokemon_analysis.json",
                mime="application/json",
            )
        with col3:
            teams_data = []
            for i, pokemon in enumerate(parsed_data.get('pokemon', []), 1):
                teams_data.append({
                    'Pokemon': pokemon.get('name', ''),
                    'Ability': pokemon.get('ability', ''),
                    'Item': pokemon.get('item', ''),
                    'Tera_Type': pokemon.get('tera_type', ''),
                    'Moves': ' / '.join(pokemon.get('moves', [])),
                    'Nature': pokemon.get('nature', ''),
                    'HP_EVs': pokemon.get('evs', {}).get('hp', 0),
                    'Atk_EVs': pokemon.get('evs', {}).get('atk', 0),
                    'Def_EVs': pokemon.get('evs', {}).get('def', 0),
                    'SpA_EVs': pokemon.get('evs', {}).get('spa', 0),
                    'SpD_EVs': pokemon.get('evs', {}).get('spd', 0),
                    'Spe_EVs': pokemon.get('evs', {}).get('spe', 0)
                })
            df = pd.DataFrame(teams_data)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📋 Download as CSV",
                data=csv_data,
                file_name=f"pokemon_team.csv",
                mime="text/csv",
            )
        with col4:
            compact_summary = f"Pokemon VGC Team Analysis\n\n"
            for i, pokemon in enumerate(parsed_data.get('pokemon', []), 1):
                compact_summary += f"{i}. {pokemon.get('name', 'Unknown')} - {pokemon.get('ability', 'N/A')} - {pokemon.get('item', 'N/A')}\n"
            st.download_button(
                label="📝 Download Compact",
                data=compact_summary,
                file_name=f"pokemon_team_compact.txt",
                mime="text/plain",
            )

def extract_strengths_weaknesses(summary):
    """Extract strengths and weaknesses from the LLM summary"""
    strengths = ""
    weaknesses = ""
    
    # Look for strengths and weaknesses in the summary
    summary_lower = summary.lower()
    
    # Common patterns for strengths
    strength_patterns = [
        r'strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)',
        r'team strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)',
        r'advantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\ndisadvantages?|$)',
        r'positive[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nnegative|$)',
        r'strong[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweak|$)'
    ]
    
    # Common patterns for weaknesses
    weakness_patterns = [
        r'weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)',
        r'team weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)',
        r'disadvantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nadvantages?|$)',
        r'negative[:\s]+(.*?)(?=\n\n|\n[A-Z]|\npositive|$)',
        r'weak[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrong|$)'
    ]
    
    # Extract strengths
    for pattern in strength_patterns:
        match = re.search(pattern, summary, re.IGNORECASE | re.DOTALL)
        if match:
            strengths = match.group(1).strip()
            break
    
    # Extract weaknesses
    for pattern in weakness_patterns:
        match = re.search(pattern, summary, re.IGNORECASE | re.DOTALL)
        if match:
            weaknesses = match.group(1).strip()
            break
    
    # If no specific sections found, try to extract from the conclusion
    if not strengths and not weaknesses:
        # Look for positive and negative language in the conclusion
        conclusion_match = re.search(r'conclusion[:\s]+(.*?)(?=\n\n|\Z)', summary, re.IGNORECASE | re.DOTALL)
        if conclusion_match:
            conclusion = conclusion_match.group(1).lower()
            
            # Extract positive statements
            positive_keywords = ['strong', 'advantage', 'effective', 'powerful', 'successful', 'good', 'excellent', 'outstanding']
            positive_sentences = []
            for sentence in re.split(r'[.!?]+', conclusion):
                if any(keyword in sentence for keyword in positive_keywords):
                    positive_sentences.append(sentence.strip())
            if positive_sentences:
                strengths = '. '.join(positive_sentences[:3])  # Limit to 3 sentences
            
            # Extract negative statements
            negative_keywords = ['weak', 'disadvantage', 'problem', 'issue', 'difficult', 'challenge', 'vulnerable']
            negative_sentences = []
            for sentence in re.split(r'[.!?]+', conclusion):
                if any(keyword in sentence for keyword in negative_keywords):
                    negative_sentences.append(sentence.strip())
            if negative_sentences:
                weaknesses = '. '.join(negative_sentences[:3])  # Limit to 3 sentences
    
    # Clean up the extracted text
    def clean_text(text):
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Remove code
        
        # Clean up bullet points and formatting
        text = re.sub(r'^\s*[-*•]\s*', '', text, flags=re.MULTILINE)  # Remove bullet points
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
        
        # Clean up extra whitespace and newlines
        text = re.sub(r'\n+', ' ', text)  # Replace multiple newlines with space
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.strip()
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        return text
    
    strengths = clean_text(strengths)
    weaknesses = clean_text(weaknesses)
    
    return strengths, weaknesses

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

def parse_summary(summary, images_data=None):
    # Debug: Print the first 500 characters of the summary to see the format
    print("DEBUG: Summary starts with:", summary[:500])
    
    parsed_data = {
        'title': 'Not specified',
        'pokemon': [],
        'conclusion': ''
    }

    # Try different title patterns
    title_patterns = [
        r'TITLE:\s*(.*?)(?=\n)',
        r'Title:\s*(.*?)(?=\n)',
        r'#\s*(.*?)(?=\n)',
        r'##\s*(.*?)(?=\n)'
    ]
    
    for pattern in title_patterns:
        title_match = re.search(pattern, summary)
        if title_match:
            parsed_data['title'] = title_match.group(1).strip()
            break

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
                'Miraidon', 'Koraidon', 'Urshifu', 'Rillaboom', 'Volcarona'
            ]
            for pokemon in common_pokemon:
                if pokemon.lower() in section.lower():
                    pokemon_name = pokemon
                    break
        
        if pokemon_name:
            pokemon_data['name'] = pokemon_name
            print(f"DEBUG: Found name: {pokemon_name}")
        else:
            print(f"DEBUG: No name found for Pokémon {i+1}")
            continue

        # Extract all data using comprehensive regex patterns
        section_lower = section.lower()
        
        # Extract Ability
        ability_patterns = [
            r'ability[:\s]+([^:\n]+)',
            r'abilities?[:\s]+([^:\n]+)',
            r'- ability[:\s]+([^:\n]+)',
            r'• ability[:\s]+([^:\n]+)'
        ]
        for pattern in ability_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data['ability'] = match.group(1).strip().title()
                print(f"DEBUG: Found ability: {pokemon_data['ability']}")
                break
        
        # Extract Item
        item_patterns = [
            r'item[:\s]+([^:\n]+)',
            r'held item[:\s]+([^:\n]+)',
            r'- item[:\s]+([^:\n]+)',
            r'• item[:\s]+([^:\n]+)'
        ]
        for pattern in item_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data['item'] = match.group(1).strip().title()
                print(f"DEBUG: Found item: {pokemon_data['item']}")
                break
        
        # Extract Nature
        nature_patterns = [
            r'nature[:\s]+([^:\n]+)',
            r'natures?[:\s]+([^:\n]+)',
            r'- nature[:\s]+([^:\n]+)',
            r'• nature[:\s]+([^:\n]+)',
            r'nature[:\s]*([a-z]+)',  # Just the nature name
            r'([a-z]+)\s+nature'  # Nature name before "nature"
        ]
        for pattern in nature_patterns:
            match = re.search(pattern, section_lower)
            if match:
                nature_text = match.group(1).strip().title()
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
                pokemon_data['nature'] = nature_mapping.get(nature_text, nature_text)
                print(f"DEBUG: Found nature: {pokemon_data['nature']}")
                break
        
        # Extract Tera Type
        tera_patterns = [
            r'tera[:\s]+([^:\n]+)',
            r'tera type[:\s]+([^:\n]+)',
            r'- tera[:\s]+([^:\n]+)',
            r'• tera[:\s]+([^:\n]+)'
        ]
        for pattern in tera_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data['tera_type'] = match.group(1).strip().title()
                print(f"DEBUG: Found tera: {pokemon_data['tera_type']}")
                break
        
        # Extract Moves
        moves_patterns = [
            r'moves?[:\s]+([^:\n]+)',
            r'moveset[:\s]+([^:\n]+)',
            r'- moves?[:\s]+([^:\n]+)',
            r'• moves?[:\s]+([^:\n]+)'
        ]
        for pattern in moves_patterns:
            match = re.search(pattern, section_lower)
            if match:
                moves_text = match.group(1).strip()
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
                    pokemon_data['moves'] = filtered_moves
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
                    # Standard format: 244 252 4 4 4 4 (space separated)
                    r'^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$',
                    r'(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)',
                    r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',
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
                            stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
                            for j, stat in enumerate(stats):
                                try:
                                    evs[stat] = int(ev_match.group(j + 1))
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
                pokemon_data['ev_explanation'] = match.group(1).strip()
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
            parsed_data['conclusion'] = conclusion_match.group(1).strip()
            break

    return parsed_data

def run_analysis(url, cache):
    st.session_state["summarising"] = True
    
    st.markdown("""
    <div class="modern-card">
        <h3 style="margin: 0 0 16px 0; color: var(--text-primary); font-size: 1.3rem; font-weight: 600;">
            🔄 Processing Article
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
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
            
            summary = llm_summary_gemini(url)
            if not isinstance(summary, str):
                summary = str(summary)

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
        st.markdown(f"""
        <div class="status-error">
            <strong>❌ Analysis Error</strong><br>
            {str(e)}
        </div>
        """, unsafe_allow_html=True)
        progress_bar.empty()
        status_text.empty()
    finally:
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

if __name__ == "__main__":
    main() 