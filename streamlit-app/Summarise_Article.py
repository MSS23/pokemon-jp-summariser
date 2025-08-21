# -*- coding: utf-8 -*-
import hashlib
import html
import json
import os
import re
import sys
import time
import traceback
from datetime import datetime

import pandas as pd
import streamlit as st

# Import pokemon card display first to ensure it's available
from pokemon_card_display import display_pokemon_card_with_summary
from utils.error_handler import (
    APIError,
    ValidationError,
    error_boundary,
    handle_streamlit_error,
    safe_execute,
)

# Import logging and error handling utilities
from utils.logger import get_pokemon_parser_logger, pokemon_metrics

# Import progressive loading and UX enhancements
from utils.progressive_loading import (
    ProgressTracker,
    SmartCache,
    add_enhanced_css,
    create_enhanced_card,
    create_step_indicator,
    create_status_badge,
    show_feature_tour,
)

# Add error handling for imports
try:
    # Import LLM modules
    from utils.gemini_summary import check_gemini_availability, llm_summary_gemini

    GEMINI_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import LLM modules: {e}")
    GEMINI_AVAILABLE = False

# Import shared utilities
try:
    # Add parent directory to path to access shared package
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)

    from shared.validators.url_validator import (
        sanitize_url,
        validate_pokemon_article_url,
    )
    from shared.utils.shared_utils import extract_pokemon_names
    from shared.utils.llm_utils import (
        validate_ev_explanation,
        get_fallback_ev_explanation,
    )
except ImportError as e:
    st.error(f"Failed to import shared utilities: {e}")

    def extract_pokemon_names(summary):
        return []

    def validate_pokemon_article_url(url):
        return {"valid": True, "message": "Validation unavailable", "domain": None}

    def sanitize_url(url):
        return url.strip() if url else ""

    def validate_ev_explanation(explanation):
        return True  # Always return True if validation is unavailable

    def get_fallback_ev_explanation():
        return "I am unable to generate a meaningful insight about this Pokémon's EV spread based on the available information."


# Page configuration
st.set_page_config(
    page_title="Pokemon VGC Team Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add enhanced CSS and UX features
add_enhanced_css()

# Custom CSS for modern, professional styling
st.markdown(
    """
<style>
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --secondary: #f59e0b;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --border: #e5e7eb;
        --background: #ffffff;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    /* Main App Background */
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
    }

    .hero-section {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white !important;
        padding: 3rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 0 auto 2rem auto;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-lg);
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        color: white !important;
        line-height: 1.2;
        letter-spacing: -0.025em;
    }

    .hero-subtitle {
        font-size: 1.125rem;
        margin: 0 auto 2rem auto;
        max-width: 600px;
        line-height: 1.6;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9) !important;
        opacity: 0.9;
    }

    .feature-badges {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.75rem;
        margin: 0 auto;
        max-width: 800px;
    }

    .feature-badge {
        background: rgba(255, 255, 255, 0.15);
        color: white !important;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.2s ease;
        text-shadow: none;
    }

    .feature-badge:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-1px);
    }

    /* Modern Cards */
    .modern-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }

    .modern-card:hover {
        box-shadow: var(--shadow-lg);
    }

    /* Status Messages */
    .status-success {
        background: var(--gray-50);
        color: var(--success);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin: 1rem 0;
        border-left: 4px solid var(--success);
    }

    .status-error {
        background: var(--gray-50);
        color: var(--error);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(239, 68, 68, 0.2);
        margin: 1rem 0;
        border-left: 4px solid var(--error);
    }

    .status-info {
        background: var(--gray-50);
        color: var(--primary);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(37, 99, 235, 0.2);
        margin: 1rem 0;
        border-left: 4px solid var(--primary);
    }

    /* Modern Buttons */
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        font-size: 0.875rem;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
        min-width: 100px;
        height: 3rem;
    }

    .stButton > button:hover {
        background: var(--primary-light);
        box-shadow: var(--shadow-lg);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: var(--shadow);
    }

    /* Modern Text Inputs */
    .stTextInput > div > div > input {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.875rem;
        height: auto;
        min-height: 3rem;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
        background: white;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        outline: none;
    }

    /* Results Section */
    .results-section {
        margin: 0 auto 2rem auto;
        max-width: 1200px;
        padding: 0 1rem;
    }

    /* Pokemon Cards */
    .pokemon-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }

    .pokemon-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }

    .pokemon-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: -1.5rem -1.5rem 1.5rem -1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: var(--shadow);
    }

    .pokemon-name {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        color: white;
    }

    .pokemon-index {
        background: rgba(255, 255, 255, 0.2);
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.75rem;
        color: white;
    }

    /* EV Section */
    .ev-section {
        background: var(--gray-50);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid var(--border);
    }

    .ev-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 12px;
        margin-top: 12px;
    }

    .ev-item {
        background: white;
        padding: 0.75rem;
        border-radius: 6px;
        text-align: center;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
    }

    .ev-value {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.25rem;
    }

    .ev-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    /* Moves and Abilities */
    .moves-section {
        background: var(--gray-50);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid var(--border);
    }

    .move-item {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid var(--border);
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--text-primary);
        box-shadow: var(--shadow);
    }

    .ability-item {
        background: var(--primary);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-weight: 600;
    }

    /* Hide Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove padding from main container */
    .main > div {
        padding: 1rem 0 0 0;
    }
    
    /* Modern sidebar styling */
    .css-1d391kg {
        background: var(--gray-50);
        border-right: 1px solid var(--border);
    }
    
    /* Ensure sidebar is always visible */
    .css-1cypcdb {
        min-width: 280px !important;
    }
    
    /* Sidebar content styling */
    .css-12oz5g7 {
        padding: 1rem;
    }
    
    /* Fix sidebar toggle button */
    .css-1v0mbdj > button {
        display: none !important;
    }
    
    /* Additional sidebar fixes for different Streamlit versions */
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        background: var(--gray-50);
    }
    
    section[data-testid="stSidebar"] > div {
        min-width: 280px !important;
    }
    
    /* Hide sidebar collapse button - multiple selectors */
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Hide all sidebar toggle buttons */
    .css-vk3wp9 {
        display: none !important;
    }
    
    /* Hide sidebar controls */
    .css-1kyxreq {
        display: none !important;
    }
    
    /* Hide sidebar toggle with newer Streamlit versions */
    [data-testid="collapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    
    /* Hide any button that might be the sidebar toggle */
    .css-1rs6os.edgvbvh3 {
        display: none !important;
    }
    
    /* Hide header area completely if it contains toggle */
    .css-1y4p8pa {
        display: none !important;
    }
    
    /* Additional sidebar toggle hiding */
    .css-12ttj6m {
        display: none !important;
    }
    
    /* Hide sidebar toggle arrows and controls */
    .css-1kyxreq button {
        display: none !important;
    }
    
    /* Hide any SVG icons that might be toggles */
    .css-1y4p8pa svg {
        display: none !important;
    }
    
    /* Force sidebar to stay open */
    .css-1cypcdb {
        display: block !important;
        visibility: visible !important;
    }
</style>

<script>
    // JavaScript to disable sidebar toggle functionality
    function disableSidebarToggle() {
        // Find and disable all sidebar toggle buttons
        const toggleButtons = document.querySelectorAll('button[kind="header"]');
        toggleButtons.forEach(button => {
            button.style.display = 'none';
            button.disabled = true;
        });
        
        // Find sidebar toggle by data-testid
        const sidebarToggle = document.querySelector('[data-testid="collapsedControl"]');
        if (sidebarToggle) {
            sidebarToggle.style.display = 'none';
        }
        
        // Force sidebar to stay visible
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.visibility = 'visible';
            sidebar.style.minWidth = '280px';
        }
    }
    
    // Run on page load
    document.addEventListener('DOMContentLoaded', disableSidebarToggle);
    
    // Run periodically to catch dynamically created elements
    setInterval(disableSidebarToggle, 1000);
</script>

<style>
    
    /* Clean up expander styling */
    .streamlit-expanderHeader {
        background: var(--gray-50);
        border-radius: 8px;
        border: 1px solid var(--border);
        color: var(--text-primary);
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background: white;
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 8px 8px;
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
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "summarising" not in st.session_state:
    st.session_state["summarising"] = False
if "current_summary" not in st.session_state:
    st.session_state["current_summary"] = None
if "current_url" not in st.session_state:
    st.session_state["current_url"] = None
if "last_analysis_time" not in st.session_state:
    st.session_state["last_analysis_time"] = 0
if "loaded_summary" not in st.session_state:
    st.session_state["loaded_summary"] = None
if "loaded_url" not in st.session_state:
    st.session_state["loaded_url"] = None
if "show_cached_results" not in st.session_state:
    st.session_state["show_cached_results"] = False
if "cache_load_success" not in st.session_state:
    st.session_state["cache_load_success"] = False
if "reanalyze_requested" not in st.session_state:
    st.session_state["reanalyze_requested"] = False
if "reanalyze_url" not in st.session_state:
    st.session_state["reanalyze_url"] = None
if "force_reanalyze" not in st.session_state:
    st.session_state["force_reanalyze"] = False
if "immediate_display" not in st.session_state:
    st.session_state["immediate_display"] = False
if "test_flag" not in st.session_state:
    st.session_state["test_flag"] = False

# Enhanced caching system
from utils.cache import (
    cache_manager,
    get_cached_summary,
    set_cached_summary,
    display_cache_dashboard,
)

# Cache setup
CACHE_PATH = "storage/cache.json"
os.makedirs("storage", exist_ok=True)

# Legacy cache migration
try:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            legacy_cache = json.load(f)

        # Migrate legacy cache to new system
        for url, data in legacy_cache.items():
            if not cache_manager.get(url):
                cache_manager.set(url, data, ttl=7200)  # 2 hour TTL for migrated data

        # Backup and remove legacy cache
        backup_path = CACHE_PATH + ".backup"
        os.rename(CACHE_PATH, backup_path)

        cache = {}  # Empty for backward compatibility
    else:
        cache = {}
except json.JSONDecodeError:
    cache = {}

# Check Gemini availability
gemini_available = (
    GEMINI_AVAILABLE and check_gemini_availability() if GEMINI_AVAILABLE else False
)

# Check if any LLM is available - Allow app to run even without LLM for testing
any_llm_available = GEMINI_AVAILABLE


def display_fixed_sidebar():
    """Display custom fixed sidebar with navigation and help links"""
    # Create custom fixed sidebar using HTML/CSS
    st.markdown(
        """
    <!-- Sidebar Toggle Button -->
    <div id="sidebar-toggle" style="
        position: fixed;
        left: 10px;
        top: 10px;
        background: #007bff;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        z-index: 1000000;
        font-size: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        border: 2px solid #fff;
    " onclick="toggleSidebar()" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">☰</div>
    
    <div id="custom-sidebar" style="
        position: fixed;
        left: 0;
        top: 0;
        height: 100vh;
        width: 280px;
        background: #f8f9fa;
        border-right: 1px solid #e0e0e0;
        padding: 20px;
        overflow-y: auto;
        z-index: 999999;
        box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
        transform: translateX(-100%);
    ">
        <!-- Header with close button -->
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 20px;">
            <div style="text-align: center; flex-grow: 1;">
                <h2 style="margin: 0; color: #1f77b4; font-size: 1.3rem;">⚡ Pokemon VGC</h2>
                <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9rem;">Team Analyzer</p>
            </div>
            <button onclick="toggleSidebar()" style="
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 8px;
                cursor: pointer;
                font-size: 12px;
            ">✕</button>
        </div>
        
        <!-- Help & Resources -->
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; margin-bottom: 10px; font-size: 1rem;">📚 Help & Resources</h3>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="help-section" value="guide" onchange="showGuide()" style="margin-right: 8px;">
                📖 User Guide
            </label>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="help-section" value="setup" onchange="showSetup()" style="margin-right: 8px;">
                🚀 Setup Instructions
            </label>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="help-section" value="faq" onchange="showFAQ()" style="margin-right: 8px;">
                ❓ FAQ
            </label>
        </div>
        
        <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
        
        <!-- Quick Actions -->
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; margin-bottom: 10px; font-size: 1rem;">⚡ Quick Actions</h3>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="quick-actions" value="clear-cache" onchange="clearCache()" style="margin-right: 8px;">
                🗑️ Clear Cache
            </label>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="quick-actions" value="cache-stats" onchange="showCacheStats()" style="margin-right: 8px;">
                📊 Cache Statistics
            </label>
        </div>
        
        <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
        
        <!-- Application Info -->
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; margin-bottom: 10px; font-size: 1rem;">ℹ️ Application Info</h3>
            <div style="font-size: 0.85rem; color: #666;">
                <p><strong>Version:</strong> 2.0</p>
                <p><strong>AI Engine:</strong> Google Gemini</p>
                <p><strong>Supported:</strong> Japanese VGC Articles</p>
                <p><strong>Output:</strong> English Analysis</p>
                
                <p style="margin-top: 15px;"><strong>Supported Sources:</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>note.com</li>
                    <li>hatenablog.jp</li>
                    <li>liberty-note.com</li>
                    <li>Pokemon official sites</li>
                </ul>
            </div>
        </div>
        
        <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
        
        <!-- Recent Articles -->
        <div style="margin-bottom: 20px;">
            <h3 style="color: #333; margin-bottom: 10px; font-size: 1rem;">📚 Recent Articles</h3>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="recent-articles" value="view-recent" onchange="viewRecentArticles()" style="margin-right: 8px;">
                👁️ View Recent Articles
            </label>
            
            <label style="display: block; margin: 8px 0; cursor: pointer; padding: 8px; border-radius: 5px; background: #fff; border: 1px solid #ddd;">
                <input type="radio" name="recent-articles" value="refresh-cache" onchange="refreshCache()" style="margin-right: 8px;">
                🔄 Refresh Cache
            </label>
        </div>
        
        <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
        
        <!-- Footer -->
        <div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 20px;">
            Built with ❤️ using Streamlit<br>
            Powered by Google Gemini AI
        </div>
    </div>
    
    <!-- Adjust main content margin -->
    <style>
        .main .block-container {
            margin-left: 20px !important;
            max-width: calc(100% - 40px) !important;
        }
        
        /* Hide original sidebar completely */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Enhanced radio button styling */
        #custom-sidebar label {
            transition: all 0.2s ease;
            border: 1px solid #ddd !important;
        }
        
        #custom-sidebar label:hover {
            background: #e3f2fd !important;
            border-color: #2196f3 !important;
            transform: translateX(5px);
        }
        
        #custom-sidebar input[type="radio"]:checked + span {
            color: #1976d2;
            font-weight: bold;
        }
        
        /* Smooth transitions for sidebar */
        #custom-sidebar {
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Toggle button animations */
        #sidebar-toggle {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
    </style>
    
    <script>
        // Sidebar toggle functionality
        let sidebarCollapsed = true; // Start with sidebar collapsed
        
        function toggleSidebar() {
            const sidebar = document.getElementById('custom-sidebar');
            const mainContent = document.querySelector('.main .block-container');
            const toggleBtn = document.getElementById('sidebar-toggle');
            
            if (sidebarCollapsed) {
                // Show sidebar
                sidebar.style.transform = 'translateX(0)';
                if (mainContent) {
                    mainContent.style.marginLeft = '300px';
                    mainContent.style.maxWidth = 'calc(100% - 320px)';
                }
                toggleBtn.innerHTML = '✕';
                toggleBtn.style.background = '#dc3545';
                sidebarCollapsed = false;
            } else {
                // Hide sidebar
                sidebar.style.transform = 'translateX(-100%)';
                if (mainContent) {
                    mainContent.style.marginLeft = '20px';
                    mainContent.style.maxWidth = 'calc(100% - 40px)';
                }
                toggleBtn.innerHTML = '☰';
                toggleBtn.style.background = '#007bff';
                sidebarCollapsed = true;
            }
        }
        
        function showGuide() {
            // Find and click the hidden Streamlit button
            const guideBtn = document.querySelector('button[data-testid="baseButton-secondary"][title="User Guide"]');
            if (guideBtn) guideBtn.click();
            // Clear radio selection after action
            setTimeout(() => clearRadioSelection('help-section'), 500);
        }
        
        function showSetup() {
            const setupBtn = document.querySelector('button[data-testid="baseButton-secondary"][title="Setup"]');
            if (setupBtn) setupBtn.click();
            setTimeout(() => clearRadioSelection('help-section'), 500);
        }
        
        function showFAQ() {
            const faqBtn = document.querySelector('button[data-testid="baseButton-secondary"][title="FAQ"]');
            if (faqBtn) faqBtn.click();
            setTimeout(() => clearRadioSelection('help-section'), 500);
        }
        
        function clearCache() {
            const clearBtn = document.querySelector('button[data-testid="baseButton-secondary"][title="Clear Cache"]');
            if (clearBtn) clearBtn.click();
            setTimeout(() => clearRadioSelection('quick-actions'), 500);
        }
        
        function showCacheStats() {
            const statsBtn = document.querySelector('button[data-testid="baseButton-secondary"][title="Cache Stats"]');
            if (statsBtn) statsBtn.click();
            setTimeout(() => clearRadioSelection('quick-actions'), 500);
        }
        
        function clearRadioSelection(groupName) {
            const radios = document.querySelectorAll(`input[name="${groupName}"]`);
            radios.forEach(radio => radio.checked = false);
        }
        
        function viewRecentArticles() {
            // Scroll to recent articles section
            const recentSection = document.querySelector('[data-testid="stExpander"]');
            if (recentSection) {
                recentSection.scrollIntoView({ behavior: 'smooth' });
            }
            setTimeout(() => clearRadioSelection('recent-articles'), 500);
        }
        
        function refreshCache() {
            // Trigger a page refresh to update cache
            location.reload();
        }
    </script>
    """,
        unsafe_allow_html=True,
    )


def display_sidebar():
    """Display sidebar - now using custom fixed sidebar"""
    # Display the fixed sidebar
    display_fixed_sidebar()

    # Create hidden containers for button functionality
    st.markdown(
        """
    <style>
        .hidden-buttons {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            width: 0 !important;
            opacity: 0 !important;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="hidden-buttons">', unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])

        with col1:
            if st.button("📖", key="guide_btn", help="User Guide"):
                st.session_state["show_guide"] = True

        with col2:
            if st.button("🚀", key="setup_btn", help="Setup"):
                st.session_state["show_setup"] = True

        with col3:
            if st.button("❓", key="faq_btn", help="FAQ"):
                st.session_state["show_faq"] = True

        with col4:
            if st.button("🗑️", key="clear_btn", help="Clear Cache"):
                cache_manager.clear()
                st.success("Cache cleared!")
                st.rerun()

        with col5:
            if st.button("📊", key="stats_btn", help="Cache Stats"):
                st.session_state["show_cache_dashboard"] = not st.session_state.get(
                    "show_cache_dashboard", False
                )

        st.markdown("</div>", unsafe_allow_html=True)


def display_help_content():
    """Display help content based on session state"""
    if st.session_state.get("show_guide"):
        st.markdown("## 📖 User Guide")

        with st.expander("🎯 How to Use the Pokemon VGC Team Analyzer", expanded=True):
            st.markdown(
                """
            ### Step-by-Step Guide
            
            1. **Find a Japanese Pokemon VGC Article**
               - Look for articles on note.com, hatenablog.jp, or liberty-note.com
               - Make sure the article contains Pokemon team information
            
            2. **Copy the Article URL**
               - Copy the full URL from your browser
               - Supported formats: https://note.com/..., https://hatenablog.jp/...
            
            3. **Paste and Analyze**
               - Paste the URL in the input field
               - Click "🚀 Analyze Article"
               - Wait 30-45 seconds for AI analysis
            
            4. **View Results**
               - **Team Summary**: Overview of the team strategy
               - **Pokemon Details**: Individual Pokemon breakdowns
               - **Article Summary**: Comprehensive analysis with strengths/weaknesses
            
            5. **Download Results**
               - Text format for reading
               - PokePaste format for Pokemon Showdown
               - JSON format for data processing
               - CSV format for spreadsheets
            """
            )

        with st.expander("🔍 Understanding the Analysis", expanded=True):
            st.markdown(
                """
            ### What the AI Analyzes
            
            **Pokemon Information:**
            - Name and nickname
            - Ability and held item
            - Tera type and nature
            - Complete moveset
            - EV spreads with explanations
            
            **Team Strategy:**
            - Overall team concept
            - Pokemon roles and synergies
            - Strengths and weaknesses
            - Meta positioning
            
            **Additional Details:**
            - Lead combinations
            - Matchup strategies
            - Tournament results
            - Author's insights
            """
            )

        if st.button("Close Guide", key="close_guide"):
            st.session_state["show_guide"] = False
            st.rerun()

    if st.session_state.get("show_setup"):
        st.markdown("## 🚀 Setup Instructions")

        with st.expander("⚙️ Google Gemini API Setup", expanded=True):
            st.markdown(
                """
            ### Getting Your API Key
            
            1. **Visit Google AI Studio**
               - Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
               - Sign in with your Google account
            
            2. **Create API Key**
               - Click "Create API Key"
               - Copy the generated key (starts with "AIza...")
            
            3. **Configure the Application**
               - Edit `.streamlit/secrets.toml`
               - Add: `google_api_key = "your_key_here"`
               - Restart the application
            
            ### Example Configuration
            ```toml
            google_api_key = "AIzaSyC_your_actual_key_here"
            ```
            
            **Note**: Your API key should be about 39 characters long and start with "AIza"
            """
            )

        with st.expander("📦 Local Installation", expanded=True):
            st.markdown(
                """
            ### Requirements
            - Python 3.8 or higher
            - pip package manager
            - Internet connection
            
            ### Installation Steps
            ```bash
            # Clone or download the project
            cd pokemon-vgc-analyzer
            
            # Install dependencies
            pip install -r requirements.txt
            
            # Configure API key
            cp .streamlit/secrets.toml.example .streamlit/secrets.toml
            # Edit secrets.toml with your API key
            
            # Run the application
            streamlit run Summarise_Article.py
            ```
            """
            )

        if st.button("Close Setup", key="close_setup"):
            st.session_state["show_setup"] = False
            st.rerun()

    if st.session_state.get("show_faq"):
        st.markdown("## ❓ Frequently Asked Questions")

        with st.expander("🤖 About the AI Analysis", expanded=True):
            st.markdown(
                """
            **Q: How accurate is the AI translation?**  
            A: The Google Gemini AI provides highly accurate translations and Pokemon identification. It's specifically trained to understand Pokemon terminology and VGC concepts.
            
            **Q: Can it analyze English articles?**  
            A: Yes, but it's optimized for Japanese articles. English articles will work but may not provide as detailed analysis.
            
            **Q: What if the AI makes mistakes?**  
            A: The AI is very accurate but not perfect. Always double-check important details like EV spreads and Pokemon names.
            """
            )

        with st.expander("⚡ Performance and Usage", expanded=True):
            st.markdown(
                """
            **Q: Why does analysis take 30-45 seconds?**  
            A: The AI needs to download the article, translate Japanese text, identify Pokemon, and extract detailed information. This comprehensive analysis takes time.
            
            **Q: Are results cached?**  
            A: Yes! Once analyzed, articles are cached for 2 hours for instant access.
            
            **Q: Is there a usage limit?**  
            A: Google Gemini has free tier limits. Heavy usage may require a paid plan.
            """
            )

        with st.expander("🔧 Troubleshooting", expanded=True):
            st.markdown(
                """
            **Q: "No LLM available" error?**  
            A: Configure your Google Gemini API key in `.streamlit/secrets.toml`
            
            **Q: Analysis fails or returns empty results?**  
            A: Check that the URL is accessible and contains Pokemon VGC content. Some sites may block automated access.
            
            **Q: Quota exceeded error?**  
            A: You've reached your API limit. Wait for reset or upgrade your Google Cloud plan.
            """
            )

        if st.button("Close FAQ", key="close_faq"):
            st.session_state["show_faq"] = False
            st.rerun()


def display_hero_section():
    st.markdown(
        """
    <div class="hero-section">
        <h1 class="hero-title">⚡ Pokemon VGC Team Analyzer</h1>
        <p class="hero-subtitle">
            Transform Japanese Pokemon VGC articles into detailed English team analysis with AI-powered insights
        </p>
        <div class="feature-badges">
            <div class="feature-badge">
                🎯 Team Analysis
            </div>
            <div class="feature-badge">
                🤖 AI Powered
            </div>
            <div class="feature-badge">
                📊 EV Spreads
            </div>
            <div class="feature-badge">
                🌐 Translation
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Show LLM status with minimal styling
    if gemini_available:
        st.markdown(
            '<div class="status-success">✅ Google Gemini AI is ready</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-error">⚠️ Please configure Gemini to use the app</div>',
            unsafe_allow_html=True,
        )


def display_url_input(cache):
    st.markdown(
        create_enhanced_card(
            "Start Analyzing",
            """
        Paste a Japanese Pokemon VGC article URL below to get instant English analysis with detailed team breakdowns.
        <br><br>
        <strong>Supported Sources:</strong>
        <ul>
            <li>📝 note.com - Popular Japanese blogging platform</li>
            <li>📰 hatenablog.jp - Hatena blog articles</li>
            <li>🏆 liberty-note.com - VGC tournament reports</li>
            <li>🎮 Pokemon official sites and tournament coverage</li>
        </ul>
        """,
            "info",
            "🚀",
        ),
        unsafe_allow_html=True,
    )

    # Show recent URLs for quick access
    cached_urls = cache_manager.get_cached_urls()
    if cached_urls and len(cached_urls) > 0:
        with st.expander("📚 Recent Articles (Click to Re-analyze)", expanded=False):
            st.write(f"Debug: Found {len(cached_urls)} cached URLs")
            for i, cached_url in enumerate(cached_urls[:5]):  # Show last 5
                col1, col2 = st.columns([4, 1])
                with col1:
                    display_url = cached_url["url"]
                    if len(display_url) > 60:
                        display_url = display_url[:57] + "..."
                    st.markdown(f"**{display_url}**")
                    st.markdown(
                        f"*Cached: {cached_url['created_at'][:16]} • {cached_url['size_kb']:.1f} KB*"
                    )

                    # Debug: Show cache entry details
                    with st.expander(f"🔍 Debug Info for {i+1}", expanded=False):
                        st.write(f"**URL:** {cached_url['url']}")
                        st.write(f"**Created:** {cached_url['created_at']}")
                        st.write(f"**Expires:** {cached_url['expires_at']}")
                        st.write(f"**Size:** {cached_url['size_kb']:.1f} KB")
                        st.write(f"**In Memory:** {cached_url['in_memory']}")

                        # Test cache retrieval
                        test_data = cache_manager.get(cached_url["url"])
                        if test_data:
                            st.write(f"**Cache Data Type:** {type(test_data)}")
                            if isinstance(test_data, dict):
                                st.write(
                                    f"**Cache Data Keys:** {list(test_data.keys())}"
                                )
                                if "summary" in test_data:
                                    summary_preview = (
                                        test_data["summary"][:100] + "..."
                                        if len(str(test_data["summary"])) > 100
                                        else str(test_data["summary"])
                                    )
                                    st.write(f"**Summary Preview:** {summary_preview}")
                            else:
                                st.write(f"**Cache Data:** {str(test_data)[:200]}...")
                        else:
                            st.write("**Cache Retrieval Failed**")

                with col2:
                    # Create unique key using index, timestamp, URL hash, and current time to avoid duplicates
                    url_hash = hashlib.md5(cached_url["url"].encode()).hexdigest()[:8]
                    timestamp_hash = hashlib.md5(
                        cached_url["created_at"].encode()
                    ).hexdigest()[:8]
                    unique_key = f"reanalyze_{i}_{timestamp_hash}_{url_hash}_{int(time.time() * 1000) % 10000}"
                    if st.button(
                        "📖", key=unique_key, help="Load cached article and team"
                    ):
                        # Load cached data directly
                        st.write(f"🔍 Loading cache for: {cached_url['url']}")
                        st.write(f"🔍 Button clicked at: {time.strftime('%H:%M:%S')}")

                        cached_data = cache_manager.get(cached_url["url"])
                        st.write(f"📦 Cache data retrieved: {type(cached_data)}")

                        if cached_data:
                            # Check if summary exists in cache data
                            if (
                                isinstance(cached_data, dict)
                                and "summary" in cached_data
                            ):
                                st.write(f"✅ Found summary in cache data")
                                st.write(
                                    f"📝 Summary length: {len(str(cached_data['summary']))} characters"
                                )
                                st.write(
                                    f"🔑 Cache data keys: {list(cached_data.keys())}"
                                )

                                # Set session state variables
                                st.session_state["loaded_summary"] = cached_data[
                                    "summary"
                                ]
                                st.session_state["loaded_url"] = cached_url["url"]
                                st.session_state["show_cached_results"] = True
                                st.session_state["cache_load_success"] = True
                                st.session_state["immediate_display"] = (
                                    True  # Flag for immediate display
                                )

                                # Clear any previous analysis state to avoid conflicts
                                st.session_state.pop("analysis_complete", None)
                                st.session_state.pop("analysis_summary", None)

                                st.success("✅ Cache data loaded successfully!")
                                st.write("🔄 Session state updated successfully!")
                                st.write(f"🔍 Session state after update:")
                                st.write(
                                    f"  - loaded_summary: {type(st.session_state.get('loaded_summary'))}"
                                )
                                st.write(
                                    f"  - loaded_url: {st.session_state.get('loaded_url')}"
                                )
                                st.write(
                                    f"  - show_cached_results: {st.session_state.get('show_cached_results')}"
                                )
                                st.write(
                                    f"  - cache_load_success: {st.session_state.get('cache_load_success')}"
                                )
                                st.write(
                                    f"  - immediate_display: {st.session_state.get('immediate_display')}"
                                )

                                # Try to display results immediately
                                st.write("📖 **Cached Article Analysis**")
                                st.write(f"**Source:** {cached_url['url']}")
                                st.write(
                                    f"**Summary:** {str(cached_data['summary'])[:200]}..."
                                )

                                # Use st.experimental_rerun() as fallback if st.rerun() fails
                                try:
                                    st.rerun()
                                except Exception as rerun_error:
                                    st.error(
                                        f"Rerun failed: {rerun_error}. Please refresh the page manually."
                                    )
                                    st.write(
                                        "Session state has been updated. The cached results should appear below."
                                    )
                            else:
                                st.error(
                                    f"Cache data structure invalid. Expected 'summary' key, got: {list(cached_data.keys()) if isinstance(cached_data, dict) else type(cached_data)}"
                                )
                                st.session_state["cache_load_success"] = False
                        else:
                            st.error(
                                "Failed to load cached data. The cache entry may have expired."
                            )
                            st.session_state["cache_load_success"] = False

    # Display cached results if requested
    st.write("---")
    st.write("🔍 **DEBUG SECTION - Current Session State:**")
    st.write(
        f"🔍 show_cached_results = {st.session_state.get('show_cached_results', False)}"
    )
    st.write(f"🔍 loaded_summary = {type(st.session_state.get('loaded_summary'))}")
    st.write(f"🔍 loaded_url = {st.session_state.get('loaded_url')}")
    st.write(
        f"🔍 cache_load_success = {st.session_state.get('cache_load_success', False)}"
    )
    st.write(
        f"🔍 immediate_display = {st.session_state.get('immediate_display', False)}"
    )

    # Test button to verify session state updates work
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧪 Test Session State Update", key="test_session_update"):
            st.session_state["test_flag"] = True
            st.success("Test flag set to True!")
            st.rerun()

    with col2:
        if st.session_state.get("test_flag", False):
            st.success("✅ Test flag is working!")
            if st.button("🗑️ Clear Test Flag", key="clear_test_flag"):
                st.session_state["test_flag"] = False
                st.rerun()

    st.write("---")

    # Check if we should display cached results
    should_display = (
        st.session_state.get("show_cached_results", False)
        or st.session_state.get("cache_load_success", False)
        or st.session_state.get("immediate_display", False)
    )

    if should_display:
        st.write(f"✅ **DISPLAY CONDITION MET** - should_display = {should_display}")
        st.write(
            f"✅ **REASON:** show_cached_results={st.session_state.get('show_cached_results', False)}, cache_load_success={st.session_state.get('cache_load_success', False)}, immediate_display={st.session_state.get('immediate_display', False)}"
        )

        loaded_summary = st.session_state.get("loaded_summary")
        loaded_url = st.session_state.get("loaded_url")

        st.write(f"✅ Displaying cached results")
        st.write(f"📝 Summary type: {type(loaded_summary)}")
        st.write(f"🔗 URL: {loaded_url}")

        if loaded_summary and loaded_url:
            st.markdown("---")
            st.markdown("### 📖 Cached Article Analysis")

            # Show cached status
            cached_badge = create_status_badge("cached")
            st.markdown(
                create_enhanced_card(
                    "Loaded from Cache",
                    f"{cached_badge} **Instant Results**<br><br>Successfully loaded cached analysis results.<br>• **Source:** {loaded_url}<br>• **Processing time:** Instant load<br>• **Status:** Previously analyzed and cached",
                    "success",
                    "⚡",
                ),
                unsafe_allow_html=True,
            )

            # Display the results using the same function as normal analysis
            try:
                display_results(loaded_summary, loaded_url)
            except Exception as e:
                st.error(f"Error displaying cached results: {str(e)}")
                with st.expander("Debug Information"):
                    st.write(f"**Error Type:** {type(e).__name__}")
                    st.write(f"**Error Message:** {str(e)}")
                    st.write(f"**Summary Type:** {type(loaded_summary)}")
                    if isinstance(loaded_summary, str):
                        st.write(
                            f"**Summary Length:** {len(loaded_summary)} characters"
                        )
                        st.write("**Summary Preview:**")
                        st.text(
                            loaded_summary[:500] + "..."
                            if len(loaded_summary) > 500
                            else loaded_summary
                        )
                    else:
                        st.write("**Raw Summary Data:**")
                        st.json(loaded_summary)

            # Add buttons for actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Results", key="clear_cached_results"):
                    st.session_state["show_cached_results"] = False
                    st.session_state["loaded_summary"] = None
                    st.session_state["loaded_url"] = None
                    st.session_state["cache_load_success"] = False
                    st.session_state["immediate_display"] = False
                    st.rerun()

            with col2:
                if st.button("🔄 Re-analyze", key="reanalyze_cached"):
                    st.session_state["show_cached_results"] = False
                    st.session_state["immediate_display"] = False
                    st.session_state["loaded_summary"] = None
                    st.session_state["loaded_url"] = None
                    st.session_state["reanalyze_requested"] = True
                    st.session_state["reanalyze_url"] = loaded_url
                    st.rerun()
        else:
            st.error("Missing cached data. Please try loading again.")
            st.session_state["show_cached_results"] = False
            st.rerun()

    # Check if re-analyze was requested and pre-fill the URL
    default_url = ""
    if st.session_state.get("reanalyze_requested", False) and st.session_state.get(
        "reanalyze_url"
    ):
        default_url = st.session_state["reanalyze_url"]
        # Clear the reanalyze state after using it
        st.session_state["reanalyze_requested"] = False
        st.session_state["reanalyze_url"] = ""

    url_input = st.text_input(
        "Article URL",
        value=default_url,
        placeholder="https://note.com/user/n/example or https://hatenablog.jp/article",
        label_visibility="collapsed",
        help="Supported sources: note.com, hatenablog.jp, liberty-note.com, Pokemon official sites",
    )

    # Sanitize and validate URL
    url = sanitize_url(url_input) if url_input else ""
    validation_result = (
        validate_pokemon_article_url(url)
        if url
        else {"valid": False, "message": "", "domain": None}
    )

    valid_url = validation_result["valid"]

    if url and not valid_url:
        error_badge = create_status_badge("error")
        st.markdown(
            create_enhanced_card(
                "Invalid URL",
                f"{error_badge} <strong>URL Validation Failed</strong><br><br>{validation_result['message']}<br><br><strong>Please ensure:</strong><br>• URL is from a supported source<br>• URL is accessible and contains Pokemon VGC content<br>• URL format is correct (including http:// or https://)",
                "error",
                "❌",
            ),
            unsafe_allow_html=True,
        )

    # Show status based on URL validity with enhanced feedback
    if valid_url:
        domain = validation_result["domain"]

        # Check if URL is already cached
        is_cached = cache_manager.get(url) is not None
        cache_status = (
            create_status_badge("cached")
            if is_cached
            else create_status_badge("processing")
        )
        cache_info = (
            "⚡ Cached - instant results!"
            if is_cached
            else "🔄 Will be processed and cached"
        )

        st.markdown(
            create_enhanced_card(
                f"✅ Valid URL ({domain})",
                f"**URL Validated Successfully**<br><br>{cache_status} {cache_info}<br><br>**Ready for Analysis:**<br>• Supported domain ({domain})<br>• URL format validated<br>• Google Gemini AI ready<br>• {'Results cached' if is_cached else 'Will cache results'}",
                "success",
                "🎯",
            ),
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Enhanced button with processing state feedback and cooldown protection
        is_processing = st.session_state.get("summarising", False)

        # Add cooldown protection (3 seconds between analyses)
        current_time = time.time()
        last_analysis = st.session_state.get("last_analysis_time", 0)
        cooldown_remaining = max(0, 3 - (current_time - last_analysis))
        in_cooldown = cooldown_remaining > 0 and not is_processing

        button_disabled = not valid_url or is_processing or in_cooldown

        if is_processing:
            # Show processing state with animated loading
            processing_badge = create_status_badge("processing")
            st.markdown(
                create_enhanced_card(
                    "Processing in Progress",
                    f"{processing_badge} **Analysis in Progress**<br><br>🔄 AI is currently analyzing the article...<br><br>**Please wait:** Do not refresh the page or navigate away<br>**Status:** Processing with Google Gemini AI<br>**This will take:** ~30-45 seconds",
                    "warning",
                    "⏳",
                ),
                unsafe_allow_html=True,
            )

            # Disabled button with processing indicator
            analyze_button = st.button(
                "🔄 Processing... Please Wait",
                key="analyze_processing",
                disabled=True,
                use_container_width=True,
                help="Analysis is currently in progress. Please wait for completion.",
            )
        elif in_cooldown:
            # Show cooldown state
            warning_badge = create_status_badge("warning")
            st.markdown(
                create_enhanced_card(
                    "Cooldown Active",
                    f"{warning_badge} **Rate Limit Protection**<br><br>⏱️ Please wait {cooldown_remaining:.1f} seconds before starting another analysis.<br><br>**Why?** This prevents accidental duplicate analyses and reduces server load.",
                    "warning",
                    "⏱️",
                ),
                unsafe_allow_html=True,
            )

            # Disabled button with cooldown indicator
            analyze_button = st.button(
                f"⏱️ Please wait {cooldown_remaining:.1f}s",
                key="analyze_cooldown",
                disabled=True,
                use_container_width=True,
                help=f"Cooldown active. Please wait {cooldown_remaining:.1f} seconds.",
            )
        else:
            # Normal analyze button
            analyze_button = st.button(
                "🚀 Analyze Article",
                key="analyze_normal",
                disabled=button_disabled,
                use_container_width=True,
                help=(
                    "Click to start AI-powered analysis of the Pokemon VGC article"
                    if valid_url
                    else "Please enter a valid URL first"
                ),
            )

    if cache:
        st.markdown(
            """
        <div style="text-align: center; margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border);">
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "🗑️ Clear Cache",
                key="clear_cache_main",
                help="Clear all cached summaries",
                use_container_width=True,
            ):
                cache_manager.clear()
                st.success("✅ Cache cleared successfully!")
                st.rerun()

        with col2:
            if st.button(
                "📊 Cache Stats",
                key="cache_stats_main",
                help="View cache performance",
                use_container_width=True,
            ):
                st.session_state["show_cache_dashboard"] = not st.session_state.get(
                    "show_cache_dashboard", False
                )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    return url, valid_url, analyze_button


def display_results(summary, url):
    parsed_data = parse_summary(summary)

    st.markdown(
        """
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
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Team Summary", "Pokémon Details", "Article Summary"])

    with tab1:
        display_team_summary(parsed_data)

    with tab2:
        display_pokemon_details(parsed_data)

    with tab3:
        display_article_summary(parsed_data, summary, url)


def display_team_summary(parsed_data):
    if parsed_data.get("title"):
        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #1e4b8c 0%, #1a3a6a 100%); color: white; padding: 36px 32px; max-width: 1000px; margin: 0 auto 32px auto; border-radius: 16px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 120px; height: 120px; background: rgba(255, 255, 255, 0.08); border-radius: 50%;"></div>
            <h2 style="margin: 0 0 8px 0; font-size: 2rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">📰 {html.escape(parsed_data['title'])}</h2>
            <p style="margin: 0; font-size: 1.1rem; opacity: 0.9; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">Analyzed with Google Gemini AI</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    if parsed_data.get("conclusion"):
        st.markdown(
            f"""
        <div style="margin: 0 auto 32px auto; max-width: 1100px; padding: 0 16px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 32px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 100px; height: 100px; background: rgba(255, 255, 255, 0.1); border-radius: 50%;"></div>
                <h3 style="margin: 0 0 16px 0; font-size: 1.5rem; font-weight: 700; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">🎯 Team Strategy Summary</h3>
                <p style="margin: 0; font-size: 1.1rem; line-height: 1.6; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);">{html.escape(parsed_data['conclusion'])}</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_pokemon_details(parsed_data):
    if parsed_data.get("pokemon"):
        pokemon_list = parsed_data["pokemon"]

        st.markdown(
            f"""
        <div style="background: #e3f2fd; border: 1px solid #2196f3; border-radius: 8px; padding: 12px 16px; margin: 16px auto; max-width: 1100px; text-align: center; color: #1976d2; font-weight: 600;">
            Found {len(pokemon_list)} Pokemon in the team analysis
        </div>
        """,
            unsafe_allow_html=True,
        )

        for i in range(0, len(pokemon_list), 2):
            col1, col2 = st.columns(2, gap="large")

            with col1:
                display_pokemon_card_with_summary(pokemon_list[i], i + 1)

            with col2:
                if i + 1 < len(pokemon_list):
                    display_pokemon_card_with_summary(pokemon_list[i + 1], i + 2)
                else:
                    st.markdown(
                        "<div style='visibility: hidden; height: 1px;'></div>",
                        unsafe_allow_html=True,
                    )

            st.markdown("<div style='margin: 32px 0;'></div>", unsafe_allow_html=True)


def display_article_summary(parsed_data, summary, url):
    st.markdown(
        """
    <div style="margin-top: 48px; padding-top: 32px; border-top: 2px solid var(--border-color);">
        <h2 style="color: var(--text-primary); font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 24px;">📰 Overall Article Summary</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Show article title and source
    st.markdown(
        f"""
    <div style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: white; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(30, 64, 175, 0.3);">
        <h3 style="margin: 0 0 8px 0; font-size: 1.5rem; font-weight: 700;">📰 {html.escape(parsed_data.get('title', 'Pokemon VGC Team Analysis'))}</h3>
        <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Source: {url}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Show team composition overview
    if parsed_data.get("pokemon"):
        st.markdown(
            """
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚡ Team Composition</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Display team members in a grid
        team_cols = st.columns(3)
        for i, pokemon in enumerate(parsed_data["pokemon"]):
            col_idx = i % 3
            with team_cols[col_idx]:
                st.markdown(
                    f"""
                <div style="background: white; border: 2px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="background: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; margin-right: 8px;">{i+1}</div>
                        <h4 style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">{html.escape(pokemon.get('name', 'Unknown'))}</h4>
                    </div>
                    <div style="font-size: 0.9rem; color: #64748b;">
                        <div><strong>Ability:</strong> {html.escape(pokemon.get('ability', 'Not specified'))}</div>
                        <div><strong>Item:</strong> {html.escape(pokemon.get('item', 'Not specified'))}</div>
                        <div><strong>Tera:</strong> {html.escape(pokemon.get('tera_type', 'Not specified'))}</div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # Extract and display strengths and weaknesses
    strengths, weaknesses = extract_strengths_weaknesses(summary)

    # Display strengths
    if strengths:
        st.markdown(
            """
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">✅ Team Strengths</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Format strengths as bullet points if they contain multiple points
        if ";" in strengths or " and " in strengths or " but " in strengths:
            # Split into bullet points
            points = re.split(r"[;]|(?:\s+and\s+)|(?:\s+but\s+)", strengths)
            points = [point.strip() for point in points if point.strip()]

            strengths_html = ""
            for point in points:
                if point:
                    strengths_html += (
                        f'<div style="margin-bottom: 8px;">• {point}</div>'
                    )
        else:
            strengths_html = f'<div style="line-height: 1.6;">{strengths}</div>'

        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3);">
            {strengths_html}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Display weaknesses
    if weaknesses:
        st.markdown(
            """
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">⚠️ Team Weaknesses</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Format weaknesses as bullet points if they contain multiple points
        if ";" in weaknesses or " and " in weaknesses or " but " in weaknesses:
            # Split into bullet points
            points = re.split(r"[;]|(?:\s+and\s+)|(?:\s+but\s+)", weaknesses)
            points = [point.strip() for point in points if point.strip()]

            weaknesses_html = ""
            for point in points:
                if point:
                    weaknesses_html += (
                        f'<div style="margin-bottom: 8px;">• {point}</div>'
                    )
        else:
            weaknesses_html = f'<div style="line-height: 1.6;">{weaknesses}</div>'

        st.markdown(
            f"""
        <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(239, 68, 68, 0.3);">
            {weaknesses_html}
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Show comprehensive analysis
    if parsed_data.get("conclusion"):
        st.markdown(
            """
        <div style="margin-bottom: 24px;">
            <h3 style="color: var(--text-primary); font-size: 1.3rem; font-weight: 700; margin-bottom: 16px;">📊 Comprehensive Analysis</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
        <div style="background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; margin-bottom: 24px;">
            <div style="color: var(--text-secondary); line-height: 1.6;">
                {html.escape(parsed_data['conclusion'])}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Create comprehensive download content
    comprehensive_summary = create_comprehensive_summary(parsed_data, summary, url)

    with st.expander("📥 Download Results", expanded=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.download_button(
                label="📄 Download as Text",
                data=comprehensive_summary,
                file_name=f"pokemon_analysis.txt",
                mime="text/plain",
            )
        with col2:
            # Create PokePaste format for Showdown
            pokepaste_data = create_pokepaste_format(parsed_data)
            st.download_button(
                label="⚔️ Download PokePaste",
                data=pokepaste_data,
                file_name=f"pokemon_team_showdown.txt",
                mime="text/plain",
                help="Download in Pokemon Showdown format for easy team import",
            )
        with col3:
            json_data = {
                "title": parsed_data.get("title", "Pokemon VGC Analysis"),
                "pokemon": parsed_data.get("pokemon", []),
                "conclusion": parsed_data.get("conclusion", ""),
                "url": url,
                "pokemon_count": len(parsed_data.get("pokemon", [])),
            }
            st.download_button(
                label="📊 Download as JSON",
                data=json.dumps(json_data, indent=2, ensure_ascii=False),
                file_name=f"pokemon_analysis.json",
                mime="application/json",
            )
        with col4:
            teams_data = []
            for i, pokemon in enumerate(parsed_data.get("pokemon", []), 1):
                teams_data.append(
                    {
                        "Pokemon": pokemon.get("name", ""),
                        "Ability": pokemon.get("ability", ""),
                        "Item": pokemon.get("item", ""),
                        "Tera_Type": pokemon.get("tera_type", ""),
                        "Moves": " / ".join(pokemon.get("moves", [])),
                        "Nature": pokemon.get("nature", ""),
                        "HP_EVs": pokemon.get("evs", {}).get("hp", 0),
                        "Atk_EVs": pokemon.get("evs", {}).get("atk", 0),
                        "Def_EVs": pokemon.get("evs", {}).get("def", 0),
                        "SpA_EVs": pokemon.get("evs", {}).get("spa", 0),
                        "SpD_EVs": pokemon.get("evs", {}).get("spd", 0),
                        "Spe_EVs": pokemon.get("evs", {}).get("spe", 0),
                    }
                )
            df = pd.DataFrame(teams_data)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📋 Download as CSV",
                data=csv_data,
                file_name=f"pokemon_team.csv",
                mime="text/csv",
            )
        with col5:
            compact_summary = f"Pokemon VGC Team Analysis\n\n"
            for i, pokemon in enumerate(parsed_data.get("pokemon", []), 1):
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

    # Enhanced patterns for the new prompt format
    strength_patterns = [
        r"\*\*TEAM STRENGTHS:\*\*\s*(.*?)(?=\*\*TEAM WEAKNESSES:|\*\*FINAL|$)",
        r"TEAM STRENGTHS:\s*(.*?)(?=TEAM WEAKNESSES:|FINAL|$)",
        r"Team Strengths[:\s]+(.*?)(?=Team Weaknesses|Final|$)",
        r"strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)",
        r"team strengths?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweaknesses?|$)",
        r"advantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\ndisadvantages?|$)",
        r"positive[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nnegative|$)",
        r"strong[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nweak|$)",
    ]

    # Enhanced patterns for the new prompt format
    weakness_patterns = [
        r"\*\*TEAM WEAKNESSES:\*\*\s*(.*?)(?=\*\*FINAL|$)",
        r"TEAM WEAKNESSES:\s*(.*?)(?=FINAL|$)",
        r"Team Weaknesses[:\s]+(.*?)(?=Final|$)",
        r"weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)",
        r"team weaknesses?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrengths?|$)",
        r"disadvantages?[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nadvantages?|$)",
        r"negative[:\s]+(.*?)(?=\n\n|\n[A-Z]|\npositive|$)",
        r"weak[:\s]+(.*?)(?=\n\n|\n[A-Z]|\nstrong|$)",
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
        conclusion_match = re.search(
            r"conclusion[:\s]+(.*?)(?=\n\n|\Z)", summary, re.IGNORECASE | re.DOTALL
        )
        if conclusion_match:
            conclusion = conclusion_match.group(1).lower()

            # Extract positive statements
            positive_keywords = [
                "strong",
                "advantage",
                "effective",
                "powerful",
                "successful",
                "good",
                "excellent",
                "outstanding",
            ]
            positive_sentences = []
            for sentence in re.split(r"[.!?]+", conclusion):
                if any(keyword in sentence for keyword in positive_keywords):
                    positive_sentences.append(sentence.strip())
            if positive_sentences:
                strengths = ". ".join(positive_sentences[:3])  # Limit to 3 sentences

            # Extract negative statements
            negative_keywords = [
                "weak",
                "disadvantage",
                "problem",
                "issue",
                "difficult",
                "challenge",
                "vulnerable",
            ]
            negative_sentences = []
            for sentence in re.split(r"[.!?]+", conclusion):
                if any(keyword in sentence for keyword in negative_keywords):
                    negative_sentences.append(sentence.strip())
            if negative_sentences:
                weaknesses = ". ".join(negative_sentences[:3])  # Limit to 3 sentences

    # Clean up the extracted text
    def clean_text(text):
        if not text:
            return ""

        # Remove markdown formatting
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold
        text = re.sub(r"\*(.*?)\*", r"\1", text)  # Remove italic
        text = re.sub(r"`(.*?)`", r"\1", text)  # Remove code

        # Clean up bullet points and formatting
        text = re.sub(
            r"^\s*[-*•]\s*", "", text, flags=re.MULTILINE
        )  # Remove bullet points
        text = re.sub(
            r"^\s*\d+\.\s*", "", text, flags=re.MULTILINE
        )  # Remove numbered lists

        # Clean up extra whitespace and newlines
        text = re.sub(r"\n+", " ", text)  # Replace multiple newlines with space
        text = re.sub(r"\s+", " ", text)  # Replace multiple spaces with single space
        text = text.strip()

        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]

        return text

    strengths = clean_text(strengths)
    weaknesses = clean_text(weaknesses)

    return strengths, weaknesses


def create_pokepaste_format(parsed_data):
    """Create a PokePaste format (Showdown format) for the team"""
    pokepaste = ""

    for i, pokemon in enumerate(parsed_data.get("pokemon", []), 1):
        # Pokemon name and item
        name = pokemon.get("name", "Unknown")
        item = pokemon.get("item", "")
        if item and item.lower() != "not specified":
            pokepaste += f"{name} @ {item}\n"
        else:
            pokepaste += f"{name}\n"

        # Ability
        ability = pokemon.get("ability", "")
        if ability and ability.lower() != "not specified":
            pokepaste += f"Ability: {ability}\n"

        # Tera Type
        tera = pokemon.get("tera_type", "")
        if tera and tera.lower() != "not specified":
            pokepaste += f"Tera Type: {tera}\n"

        # EVs
        evs = pokemon.get("evs", {})
        if evs and any(evs.values()):
            ev_parts = []
            if evs.get("hp", 0) > 0:
                ev_parts.append(f"{evs['hp']} HP")
            if evs.get("attack", 0) > 0:
                ev_parts.append(f"{evs['attack']} Atk")
            if evs.get("defense", 0) > 0:
                ev_parts.append(f"{evs['defense']} Def")
            if evs.get("sp_attack", 0) > 0:
                ev_parts.append(f"{evs['sp_attack']} SpA")
            if evs.get("sp_defense", 0) > 0:
                ev_parts.append(f"{evs['sp_defense']} SpD")
            if evs.get("speed", 0) > 0:
                ev_parts.append(f"{evs['speed']} Spe")

            if ev_parts:
                pokepaste += f"EVs: {' / '.join(ev_parts)}\n"

        # Nature
        nature = pokemon.get("nature", "")
        if nature and nature.lower() != "not specified":
            pokepaste += f"{nature} Nature\n"

        # Moves
        moves = pokemon.get("moves", [])
        if moves:
            for move in moves:
                if move and move.lower() != "not specified":
                    pokepaste += f"- {move}\n"

        # Add spacing between Pokemon
        pokepaste += "\n"

    return pokepaste


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
    for i, pokemon in enumerate(parsed_data.get("pokemon", []), 1):
        comprehensive += f"""Pokemon {i}: {pokemon.get('name', 'Unknown')}
Ability: {pokemon.get('ability', 'Not specified')}
Held Item: {pokemon.get('item', 'Not specified')}
Tera Type: {pokemon.get('tera_type', 'Not specified')}
Nature: {pokemon.get('nature', 'Not specified')}
Moves: {' / '.join(pokemon.get('moves', [])) if pokemon.get('moves') else 'Not specified'}
EV Spread: {pokemon.get('evs', {}).get('hp', 0)} {pokemon.get('evs', {}).get('attack', 0)} {pokemon.get('evs', {}).get('defense', 0)} {pokemon.get('evs', {}).get('sp_attack', 0)} {pokemon.get('evs', {}).get('sp_defense', 0)} {pokemon.get('evs', {}).get('speed', 0)} (HP/Atk/Def/SpA/SpD/Spe)
Japanese Format: H{pokemon.get('evs', {}).get('hp', 0)} A{pokemon.get('evs', {}).get('attack', 0)} B{pokemon.get('evs', {}).get('defense', 0)} C{pokemon.get('evs', {}).get('sp_attack', 0)} D{pokemon.get('evs', {}).get('sp_defense', 0)} S{pokemon.get('evs', {}).get('speed', 0)}
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


@error_boundary
def parse_summary(summary, images_data=None):
    logger = get_pokemon_parser_logger()
    logger.debug(f"Starting summary parsing. Summary length: {len(summary)} characters")
    logger.debug(f"Summary preview: {summary[:500]}")

    parsed_data = {"title": "Not specified", "pokemon": [], "conclusion": ""}

    # Try different title patterns
    title_patterns = [
        r"TITLE:\s*(.*?)(?=\n)",
        r"Title:\s*(.*?)(?=\n)",
        r"#\s*(.*?)(?=\n)",
        r"##\s*(.*?)(?=\n)",
    ]

    for pattern in title_patterns:
        title_match = re.search(pattern, summary)
        if title_match:
            parsed_data["title"] = title_match.group(1).strip()
            break

    # Try different ways to split Pokémon sections
    pokemon_sections = []

    # Method 1: Look for numbered Pokémon entries (most common format)
    pokemon_numbered = re.findall(
        r"Pokémon\s*\d+[:\s]+(.*?)(?=Pokémon\s*\d+|CONCLUSION|FINAL|$)",
        summary,
        re.DOTALL | re.IGNORECASE,
    )
    if pokemon_numbered:
        pokemon_sections = pokemon_numbered
        logger.debug(f"Found {len(pokemon_sections)} Pokémon using numbered method")

    # Method 2: Look for Pokémon with dashes
    if not pokemon_sections:
        pokemon_dashed = re.split(r"\n\s*-\s*", summary)
        pokemon_sections = [
            section
            for section in pokemon_dashed
            if any(
                keyword in section.lower()
                for keyword in [
                    "ability:",
                    "item:",
                    "moves:",
                    "ev spread:",
                    "nature:",
                    "tera:",
                ]
            )
        ]
        logger.debug(f"Found {len(pokemon_sections)} Pokémon using dash method")

    # Method 3: Look for specific patterns
    if not pokemon_sections:
        split_patterns = [
            "**Pokémon",
            "**Pokemon",
            "Pokémon",
            "Pokemon",
            "Team Member",
            "Member",
        ]

        for pattern in split_patterns:
            if pattern in summary:
                pokemon_sections = summary.split(pattern)[1:]
                logger.debug(
                    f"Found {len(pokemon_sections)} Pokémon using pattern: {pattern}"
                )
                break

    # Method 4: Look for any section with Pokémon data
    if not pokemon_sections:
        # Split by double newlines and look for sections with Pokémon data
        sections = summary.split("\n\n")
        pokemon_sections = []
        for section in sections:
            if (
                any(
                    keyword in section.lower()
                    for keyword in [
                        "ability:",
                        "item:",
                        "moves:",
                        "ev spread:",
                        "nature:",
                        "tera:",
                    ]
                )
                and len(section.strip()) > 50
            ):
                pokemon_sections.append(section)
        logger.debug(f"Found {len(pokemon_sections)} Pokémon using section method")

    # Method 5: Last resort - look for any numbered entries
    if not pokemon_sections:
        pokemon_matches = re.findall(r"\d+[\.:]\s*([^\n]+)", summary)
        if pokemon_matches:
            pokemon_sections = [f"1: {name}" for name in pokemon_matches]
            logger.debug(f"Found {len(pokemon_matches)} Pokémon using numbered matches")

    logger.info(f"Total Pokémon sections found: {len(pokemon_sections)}")
    if pokemon_sections:
        logger.debug(f"First Pokémon section preview: {pokemon_sections[0][:200]}...")

    for i, section in enumerate(pokemon_sections):
        pokemon_data = {}
        logger.debug(f"Processing Pokémon {i+1}: {section[:200]}...")

        # Method 1: Extract name from the beginning of the section
        pokemon_name = None

        # Look for Pokémon name patterns
        name_patterns = [
            r"^([A-Z][a-z]+(?:[-\s]+[A-Z][a-z]+)*)",  # Capitalized words at start (includes hyphens)
            r"([A-Z][a-z]+(?:[-\s]+[A-Z][a-z]+)*)(?=\s*:)",  # Before colon
            r"([A-Z][a-z]+(?:[-\s]+[A-Z][a-z]+)*)(?=\s*-)",  # Before dash
            r"([A-Z][a-z]+(?:[-\s]+[A-Z][a-z]+)*)(?=\n)",  # Before newline
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",  # Capitalized words (fallback)
        ]

        for pattern in name_patterns:
            name_match = re.search(pattern, section)
            if name_match:
                pokemon_name = name_match.group(1).strip()
                break

        # Method 2: Look for common Pokémon names in the section
        if not pokemon_name:
            # Order by length (longest first) to match full names before partial ones
            common_pokemon = [
                "Calyrex Shadow Rider",
                "Calyrex Ice Rider",
                "Iron Valiant",
                "Flutter Mane",
                "Chien-Pao",
                "Chien Pao",
                "Chi-Yu",
                "Chi Yu",
                "Zamazenta",
                "Zacian",
                "Amoonguss",
                "Dragonite",
                "Miraidon",
                "Koraidon",
                "Urshifu",
                "Rillaboom",
                "Volcarona",
                "Grimmsnarl",
                "Incineroar",
            ]
            for pokemon in common_pokemon:
                if pokemon.lower() in section.lower():
                    pokemon_name = pokemon
                    break

        if pokemon_name:
            pokemon_data["name"] = pokemon_name
            logger.debug(f"Extracted Pokemon name: {pokemon_name}")
        else:
            logger.warning(f"No name found for Pokémon {i+1}")
            continue

        # Extract all data using comprehensive regex patterns
        section_lower = section.lower()

        # Extract Ability
        ability_patterns = [
            r"ability[:\s]+([^:\n]+)",
            r"abilities?[:\s]+([^:\n]+)",
            r"- ability[:\s]+([^:\n]+)",
            r"• ability[:\s]+([^:\n]+)",
        ]
        for pattern in ability_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data["ability"] = match.group(1).strip().title()
                logger.debug(f"Extracted ability: {pokemon_data['ability']}")
                break

        # Extract Item
        item_patterns = [
            r"item[:\s]+([^:\n]+)",
            r"held item[:\s]+([^:\n]+)",
            r"- item[:\s]+([^:\n]+)",
            r"• item[:\s]+([^:\n]+)",
        ]
        for pattern in item_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data["item"] = match.group(1).strip().title()
                logger.debug(f"Extracted item: {pokemon_data['item']}")
                break

        # Extract Nature
        nature_patterns = [
            r"nature[:\s]+([^:\n]+)",
            r"natures?[:\s]+([^:\n]+)",
            r"- nature[:\s]+([^:\n]+)",
            r"• nature[:\s]+([^:\n]+)",
            r"nature[:\s]*([a-z]+)",  # Just the nature name
            r"([a-z]+)\s+nature",  # Nature name before "nature"
        ]
        for pattern in nature_patterns:
            match = re.search(pattern, section_lower)
            if match:
                nature_text = match.group(1).strip().title()
                # Clean up common nature names
                nature_mapping = {
                    "Adamant": "Adamant",
                    "Jolly": "Jolly",
                    "Modest": "Modest",
                    "Timid": "Timid",
                    "Bold": "Bold",
                    "Impish": "Impish",
                    "Calm": "Calm",
                    "Careful": "Careful",
                    "Naive": "Naive",
                    "Hasty": "Hasty",
                    "Naughty": "Naughty",
                    "Lonely": "Lonely",
                    "Mild": "Mild",
                    "Quiet": "Quiet",
                    "Rash": "Rash",
                    "Brave": "Brave",
                    "Relaxed": "Relaxed",
                    "Sassy": "Sassy",
                    "Gentle": "Gentle",
                    "Lax": "Lax",
                }
                pokemon_data["nature"] = nature_mapping.get(nature_text, nature_text)
                logger.debug(f"Extracted nature: {pokemon_data['nature']}")
                break

        # Extract Tera Type
        tera_patterns = [
            r"tera type[:\s]+([a-z]+)",  # Match "tera type: water" - capture just the type
            r"tera[:\s]+type[:\s]+([a-z]+)",  # Match "tera: type: water"
            r"tera[:\s]+([a-z]+)(?=\s|$|\n)",  # Match "tera water" - lookahead to word boundary
            r"- tera type[:\s]+([a-z]+)",
            r"• tera type[:\s]+([a-z]+)",
            r"- tera[:\s]+([a-z]+)",
            r"• tera[:\s]+([a-z]+)",
            r"terastal[:\s]+type[:\s]+([a-z]+)",  # Alternative spelling
            r"terastallize[:\s]+([a-z]+)",  # Alternative spelling
        ]
        for pattern in tera_patterns:
            match = re.search(pattern, section_lower)
            if match:
                pokemon_data["tera_type"] = match.group(1).strip().title()
                logger.debug(f"Extracted tera type: {pokemon_data['tera_type']}")
                break

        # Extract Moves
        moves_patterns = [
            r"moves?[:\s]+([^:\n]+)",
            r"moveset[:\s]+([^:\n]+)",
            r"- moves?[:\s]+([^:\n]+)",
            r"• moves?[:\s]+([^:\n]+)",
        ]
        for pattern in moves_patterns:
            match = re.search(pattern, section_lower)
            if match:
                moves_text = match.group(1).strip()
                # Handle different separators
                if "/" in moves_text:
                    moves_list = [
                        move.strip().title() for move in moves_text.split("/")
                    ]
                elif "," in moves_text:
                    moves_list = [
                        move.strip().title() for move in moves_text.split(",")
                    ]
                else:
                    moves_list = [moves_text.title()]

                # Filter out abilities that might be incorrectly included in moves
                ability_keywords = [
                    "as one",
                    "unseen fist",
                    "grassy surge",
                    "regenerator",
                    "quark drive",
                    "drizzle",
                ]
                filtered_moves = []
                for move in moves_list:
                    if move.lower() not in ability_keywords:
                        filtered_moves.append(move)

                if filtered_moves:
                    pokemon_data["moves"] = filtered_moves
                    logger.debug(f"Extracted moves: {pokemon_data['moves']}")
                else:
                    logger.warning(f"No valid moves found after filtering")
                break

        # Extract EV Spread
        ev_patterns = [
            r"ev spread[:\s]+([^:\n]+)",
            r"evs?[:\s]+([^:\n]+)",
            r"effort values?[:\s]+([^:\n]+)",
            r"- ev spread[:\s]+([^:\n]+)",
            r"• ev spread[:\s]+([^:\n]+)",
            r"ev spread[:\s]*(\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+)",  # Direct number format
        ]
        for pattern in ev_patterns:
            match = re.search(pattern, section_lower)
            if match:
                ev_text = match.group(1).strip()
                logger.debug(f"Raw EV text extracted: '{ev_text}'")
                # Parse EV values
                evs = {
                    "hp": 0,
                    "attack": 0,
                    "defense": 0,
                    "sp_attack": 0,
                    "sp_defense": 0,
                    "speed": 0,
                }

                # Try different EV parsing patterns
                # Japanese format uses: H(HP) A(Attack) B(Defense) C(Special Attack) D(Special Defense) S(Speed)
                ev_parse_patterns = [
                    # Japanese format variations: H244 A252 B4 C4 D4 S4
                    r"H(\d+)\s+A(\d+)\s+B(\d+)\s+C(\d+)\s+D(\d+)\s+S(\d+)",
                    r"H(\d+)\s*A(\d+)\s*B(\d+)\s*C(\d+)\s*D(\d+)\s*S(\d+)",  # No spaces
                    r"H(\d+)\s+A(\d+)\s+B(\d+)\s+D(\d+)\s+S(\d+)",  # Missing C (SpA)
                    r"H(\d+)\s*A(\d+)\s*B(\d+)\s*D(\d+)\s*S(\d+)",  # Missing C, no spaces
                    # Japanese format with dashes: H244-A252-B4-C4-D4-S4
                    r"H(\d+)-A(\d+)-B(\d+)-C(\d+)-D(\d+)-S(\d+)",
                    r"H(\d+)-A(\d+)-B(\d+)-D(\d+)-S(\d+)",  # Missing C with dashes
                    # Japanese format with slashes: H244/A252/B4/C4/D4/S4
                    r"H(\d+)/A(\d+)/B(\d+)/C(\d+)/D(\d+)/S(\d+)",
                    r"H(\d+)/A(\d+)/B(\d+)/D(\d+)/S(\d+)",  # Missing C with slashes
                    # Standard numeric formats: 244 252 4 4 4 4 (space separated)
                    r"^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)$",
                    r"(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*/\s*(\d+)",
                    r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)",
                    # English format: HP:244 Atk:252 Def:4 SpA:4 SpD:4 Spe:4
                    r"HP:\s*(\d+).*?Atk:\s*(\d+).*?Def:\s*(\d+).*?SpA:\s*(\d+).*?SpD:\s*(\d+).*?Spe:\s*(\d+)",
                ]

                for i, ev_parse_pattern in enumerate(ev_parse_patterns):
                    ev_match = re.search(ev_parse_pattern, ev_text, re.IGNORECASE)
                    if ev_match:
                        logger.debug(f"EV pattern {i} matched: {ev_parse_pattern}")
                        logger.debug(f"EV match groups: {ev_match.groups()}")
                        # Handle Japanese format (H=HP, A=Attack, B=Defense, C=Special Attack, D=Special Defense, S=Speed)
                        if "H(" in ev_parse_pattern and "A(" in ev_parse_pattern:
                            # Japanese format variations
                            if len(ev_match.groups()) == 6:
                                # Full format: H244 A252 B4 C4 D4 S4
                                evs["hp"] = int(ev_match.group(1))  # H = HP
                                evs["attack"] = int(ev_match.group(2))  # A = Attack
                                evs["defense"] = int(ev_match.group(3))  # B = Defense
                                evs["sp_attack"] = int(
                                    ev_match.group(4)
                                )  # C = Special Attack
                                evs["sp_defense"] = int(
                                    ev_match.group(5)
                                )  # D = Special Defense
                                evs["speed"] = int(ev_match.group(6))  # S = Speed
                                logger.debug(
                                    f"Parsed Japanese EV format (6 values): H{evs['hp']} A{evs['attack']} B{evs['defense']} C{evs['sp_attack']} D{evs['sp_defense']} S{evs['speed']}"
                                )
                            elif len(ev_match.groups()) == 5:
                                # Missing C (Special Attack): H244 A252 B4 D4 S4
                                evs["hp"] = int(ev_match.group(1))  # H = HP
                                evs["attack"] = int(ev_match.group(2))  # A = Attack
                                evs["defense"] = int(ev_match.group(3))  # B = Defense
                                evs["sp_attack"] = 0  # C = Special Attack (missing)
                                evs["sp_defense"] = int(
                                    ev_match.group(4)
                                )  # D = Special Defense
                                evs["speed"] = int(ev_match.group(5))  # S = Speed
                                logger.debug(
                                    f"Parsed Japanese EV format (5 values, missing C): H{evs['hp']} A{evs['attack']} B{evs['defense']} C{evs['sp_attack']} D{evs['sp_defense']} S{evs['speed']}"
                                )
                        else:
                            # Standard format
                            stats = [
                                "hp",
                                "attack",
                                "defense",
                                "sp_attack",
                                "sp_defense",
                                "speed",
                            ]
                            for j, stat in enumerate(stats):
                                try:
                                    group_index = j + 1
                                    if group_index <= len(ev_match.groups()):
                                        group_value = ev_match.group(group_index)
                                        if group_value and group_value.isdigit():
                                            evs[stat] = int(group_value)
                                except (
                                    ValueError,
                                    IndexError,
                                    AttributeError,
                                    TypeError,
                                ):
                                    pass
                        break

                # Ensure EVs add up to 508 or less
                total_evs = sum(evs.values())
                if total_evs > 508 and total_evs > 0:
                    scale_factor = 508 / total_evs
                    for stat in evs:
                        evs[stat] = int(evs[stat] * scale_factor)

                pokemon_data["evs"] = evs
                logger.debug(f"Extracted EVs: {evs}")
                logger.debug(
                    f"EV breakdown - HP:{evs['hp']}, Atk:{evs['attack']}, Def:{evs['defense']}, SpA:{evs['sp_attack']}, SpD:{evs['sp_defense']}, Spe:{evs['speed']}"
                )
                break

        # Extract EV Explanation
        ev_explanation_patterns = [
            r"ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)",
            r"ev reasoning[:\s]+([^:\n]+(?:\n[^:\n]+)*)",
            r"- ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)",
            r"• ev explanation[:\s]+([^:\n]+(?:\n[^:\n]+)*)",
        ]
        for pattern in ev_explanation_patterns:
            match = re.search(pattern, section_lower)
            if match:
                raw_explanation = match.group(1).strip()
                # Validate and apply fallback if needed
                if validate_ev_explanation(raw_explanation):
                    pokemon_data["ev_explanation"] = raw_explanation
                else:
                    pokemon_data["ev_explanation"] = get_fallback_ev_explanation()
                logger.debug(
                    f"EV explanation: {pokemon_data['ev_explanation'][:100]}..."
                )
                break

        # Add fallback if no EV explanation was found
        if "ev_explanation" not in pokemon_data:
            pokemon_data["ev_explanation"] = get_fallback_ev_explanation()

        # Only add if we have at least a name
        if pokemon_data.get("name"):
            parsed_data["pokemon"].append(pokemon_data)
            pokemon_metrics.log_pokemon_details(i, pokemon_name, pokemon_data)
            logger.info(f"Successfully parsed Pokémon {i+1}: {pokemon_name}")
        else:
            logger.warning(f"Skipping Pokémon {i+1} - no name found")

    # Try different conclusion patterns
    conclusion_patterns = [
        r"Conclusion Summary:\s*(.*?)(?=\n\n|\Z)",
        r"Conclusion:\s*(.*?)(?=\n\n|\Z)",
        r"Summary:\s*(.*?)(?=\n\n|\Z)",
        r"Team Strategy:\s*(.*?)(?=\n\n|\Z)",
    ]

    for pattern in conclusion_patterns:
        conclusion_match = re.search(pattern, summary, re.DOTALL)
        if conclusion_match:
            parsed_data["conclusion"] = conclusion_match.group(1).strip()
            break

    return parsed_data


def run_analysis(url, cache, force_reanalyze=False):
    logger = get_pokemon_parser_logger()
    logger.info(f"Starting analysis for URL: {url}")
    pokemon_metrics.log_parsing_attempt(url)

    start_time = time.time()
    st.session_state["summarising"] = True
    st.session_state["last_analysis_time"] = start_time

    # Initialize enhanced progress tracker
    steps = [
        "Initializing",
        "Checking Cache",
        "Fetching Content",
        "AI Analysis",
        "Pokemon Extraction",
        "Saving Results",
    ]

    # Create step indicator container
    step_container = st.container()
    with step_container:
        st.markdown(
            create_enhanced_card(
                "Processing Article", create_step_indicator(steps, 0), "info", "🔄"
            ),
            unsafe_allow_html=True,
        )

    # Create progress tracker with detailed steps
    progress = ProgressTracker(total_steps=100, show_eta=True)

    try:
        # Step 1: Initialize
        progress.update(
            10, "Initializing Analysis", "Setting up AI processing pipeline..."
        )
        with step_container:
            st.markdown(
                create_enhanced_card(
                    "Processing Article", create_step_indicator(steps, 1), "info", "🔄"
                ),
                unsafe_allow_html=True,
            )
        time.sleep(0.3)

        # Step 2: Check enhanced cache first
        progress.update(
            20, "Checking Cache", "Looking for previously analyzed content..."
        )
        with step_container:
            st.markdown(
                create_enhanced_card(
                    "Processing Article", create_step_indicator(steps, 2), "info", "🔄"
                ),
                unsafe_allow_html=True,
            )
        cached_data = cache_manager.get(url) if not force_reanalyze else None

        if cached_data and not force_reanalyze:
            progress.update(
                100, "Loading from Cache", "Found cached results! Loading instantly..."
            )
            summary = cached_data["summary"]
            pokemon_names = cached_data.get("pokemon", [])

            # Show cache hit status with badge
            cached_badge = create_status_badge("cached")
            st.markdown(
                create_enhanced_card(
                    "Cache Hit!",
                    f"{cached_badge} **Instant Results Available**<br><br>This article was previously analyzed and cached for faster access.<br>* **Cached on:** {cached_data.get('analyzed_at', 'Unknown')}<br>* **Processing time saved:** ~30-45 seconds<br>* **Pokemon found:** {len(pokemon_names)} team members",
                    "success",
                    "⚡",
                ),
                unsafe_allow_html=True,
            )

            progress.complete("Loaded from Cache!", time.time() - start_time)
        else:
            # Show force reanalyze status if applicable
            if force_reanalyze:
                reanalyze_badge = create_status_badge("processing")
                st.markdown(
                    create_enhanced_card(
                        "Force Re-analyzing",
                        f"{reanalyze_badge} **Fresh Analysis Requested**<br><br>Bypassing cache and performing fresh analysis as requested.<br>• **Cache ignored:** Previous results will be overwritten<br>• **Processing time:** ~30-45 seconds<br>• **Result:** Latest analysis with current AI models",
                        "info",
                        "🔄",
                    ),
                    unsafe_allow_html=True,
                )
            # Step 3: Fetch content
            substeps = ["Downloading HTML", "Extracting text", "Processing images"]
            progress.update(
                30,
                "Fetching Content",
                "Downloading and processing article content...",
                substeps,
            )
            with step_container:
                st.markdown(
                    create_enhanced_card(
                        "Processing Article",
                        create_step_indicator(steps, 3),
                        "info",
                        "🔄",
                    ),
                    unsafe_allow_html=True,
                )

            # Step 4: AI Analysis
            if gemini_available:
                substeps = [
                    "Translating Japanese text",
                    "Analyzing team strategy",
                    "Extracting EV spreads",
                ]
                progress.update(
                    50,
                    "AI Analysis",
                    "Google Gemini is analyzing the article...",
                    substeps,
                )
                with step_container:
                    st.markdown(
                        create_enhanced_card(
                            "Processing Article",
                            create_step_indicator(steps, 4),
                            "info",
                            "🔄",
                        ),
                        unsafe_allow_html=True,
                    )
                try:
                    summary = llm_summary_gemini(url)
                except Exception as e:
                    if "quota exceeded" in str(e).lower():
                        # Use fallback parsing when quota is exceeded
                        progress.update(
                            60,
                            "Fallback Analysis",
                            "Using basic parsing due to API quota limit...",
                        )
                        from utils.llm_summary import fallback_basic_parsing
                        from shared.utils.shared_utils import (
                            fetch_article_text_and_images,
                        )

                        # Fetch article text for fallback parsing
                        article_text, _ = fetch_article_text_and_images(url)
                        summary = fallback_basic_parsing(article_text)

                        # Show quota warning
                        st.warning(
                            "⚠️ Your limit has been reached. Using basic parsing as fallback."
                        )
                    else:
                        raise e
            else:
                progress.cleanup()
                st.error("No LLM available for analysis. Please configure Gemini.")
                st.session_state["summarising"] = False
                st.stop()

            if not isinstance(summary, str):
                summary = str(summary)

            if not summary or summary.strip() == "":
                progress.cleanup()
                error_badge = create_status_badge("error")
                st.markdown(
                    create_enhanced_card(
                        "Analysis Failed",
                        f"{error_badge} **Unable to Generate Summary**<br><br>The AI analysis returned empty results. This could be due to:<br>* Invalid or inaccessible URL<br>* Content not compatible with Pokemon VGC analysis<br>* Temporary API issues<br><br>Please check the URL and try again.",
                        "error",
                        "❌",
                    ),
                    unsafe_allow_html=True,
                )
                st.session_state["summarising"] = False
                st.stop()

            # Step 5: Extract Pokemon data
            progress.update(
                75,
                "Extracting Pokemon",
                "Identifying Pokemon team members and stats...",
            )
            with step_container:
                st.markdown(
                    create_enhanced_card(
                        "Processing Article",
                        create_step_indicator(steps, 5),
                        "info",
                        "🔄",
                    ),
                    unsafe_allow_html=True,
                )
            pokemon_names = extract_pokemon_names(summary)

            # Step 6: Save results
            progress.update(90, "Saving Results", "Caching analysis for future use...")
            with step_container:
                st.markdown(
                    create_enhanced_card(
                        "Processing Article",
                        create_step_indicator(steps, 6),
                        "info",
                        "🔄",
                    ),
                    unsafe_allow_html=True,
                )

            # Save to enhanced cache
            cache_data = {
                "summary": summary,
                "pokemon": pokemon_names,
                "analyzed_at": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
            }
            cache_manager.set(url, cache_data, ttl=7200)  # 2 hour TTL

            # Complete with celebration
            processing_time = time.time() - start_time
            progress.complete(
                f"Analysis Complete! ({processing_time:.1f}s)", processing_time
            )

            # Show final step indicator
            with step_container:
                st.markdown(
                    create_enhanced_card(
                        "Processing Complete",
                        create_step_indicator(steps, 6),  # All steps completed
                        "success",
                        "✅",
                    ),
                    unsafe_allow_html=True,
                )

            # Show completion status
            llm_used = "Google Gemini AI"
            complete_badge = create_status_badge("complete")
            st.markdown(
                create_enhanced_card(
                    "Analysis Complete!",
                    f"""
                {complete_badge} <strong>Successfully Processed</strong>
                <br><br>
                • <strong>Processing time:</strong> {processing_time:.1f} seconds<br>
                • <strong>Pokemon found:</strong> {len(pokemon_names)} team members<br>
                • <strong>Analysis powered by:</strong> {llm_used}<br>
                • <strong>Cached for:</strong> 2 hours for faster future access
                """,
                    "success",
                    "🎉",
                ),
                unsafe_allow_html=True,
            )

        st.session_state["current_summary"] = summary
        st.session_state["current_url"] = url

        # Log successful completion
        processing_time = time.time() - start_time
        parsed_data = parse_summary(summary)
        pokemon_count = len(parsed_data.get("pokemon", []))
        pokemon_metrics.log_parsing_success(pokemon_count, processing_time)
        logger.info(
            f"Analysis completed successfully in {processing_time:.2f}s - found {pokemon_count} Pokemon"
        )

        display_results(summary, url)

    except Exception as e:
        # Log the error
        processing_time = time.time() - start_time
        error_msg = str(e)
        pokemon_metrics.log_parsing_failure(error_msg)
        logger.error(f"Analysis failed after {processing_time:.2f}s: {error_msg}")

        # Enhanced error display with cleanup
        progress.cleanup()

        # Check if it's a quota error and provide specific guidance
        if "quota exceeded" in error_msg.lower():
            from utils.error_handler import (
                handle_api_quota_error,
                create_quota_error_ui,
            )

            quota_error_info = handle_api_quota_error(error_msg)
            st.markdown(create_quota_error_ui(quota_error_info), unsafe_allow_html=True)
        else:
            try:
                error_badge = create_status_badge("error")
                error_details = str(e).replace(
                    '"', "'"
                )  # Replace quotes to avoid HTML issues
                st.markdown(
                    create_enhanced_card(
                        "Analysis Failed",
                        f"{error_badge} **Processing Error Occurred**<br><br>**Error Details:** {error_details}<br><br>**Possible Solutions:**<br>* Check your internet connection<br>* Verify the URL is accessible<br>* Try again in a few moments<br>* Contact support if the issue persists<br><br>**Processing Time:** {processing_time:.1f} seconds before failure",
                        "error",
                        "❌",
                    ),
                    unsafe_allow_html=True,
                )
            except Exception as html_error:
                # Fallback to simple error display if HTML rendering fails
                st.error(f"❌ **Analysis Failed**")
                st.error(f"**Error Details:** {str(e)}")
                st.error(
                    f"**Processing Time:** {processing_time:.1f} seconds before failure"
                )
                st.info("**Possible Solutions:**")
                st.info("• Check your internet connection")
                st.info("• Verify the URL is accessible")
                st.info("• Try again in a few moments")
                st.info("• Contact support if the issue persists")
    finally:
        st.session_state["summarising"] = False


# Main application
def main():
    # Display sidebar first
    display_sidebar()

    # Show help content if requested
    display_help_content()

    # Show feature tour for new users
    show_feature_tour()

    display_hero_section()

    # Display the main URL input interface
    cache = cache_manager
    url, valid_url, analyze_button = display_url_input(cache)

    # Check if re-analyze was requested from recent articles
    if url and valid_url and analyze_button:
        # Check if this is a re-analyze request
        if st.session_state.get("reanalyze_requested", False):
            # Clear the flags and run analysis
            force_reanalyze = st.session_state.get("force_reanalyze", False)
            st.session_state["reanalyze_requested"] = False
            st.session_state["force_reanalyze"] = False
            if not st.session_state.get("summarising", False):
                run_analysis(url, cache, force_reanalyze)
            else:
                st.warning(
                    "⚠️ Analysis already in progress. Please wait for the current analysis to complete."
                )
        else:
            # Normal analysis request
            if not st.session_state.get("summarising", False):
                run_analysis(url, cache, False)
            else:
                st.warning(
                    "⚠️ Analysis already in progress. Please wait for the current analysis to complete."
                )

    # Check LLM availability first
    if not any_llm_available:
        st.markdown(
            """
        <div class="status-error" style="padding: 20px; border-radius: 10px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;">
            <h3>❌ LLM API Not Available</h3>
            <p><strong>To use this app, you need to configure Google Gemini:</strong></p>
            
            <h4>Google Gemini Configuration</h4>
            <ol>
                <li><strong>Get your API key:</strong>
                    <ul>
                        <li>Go to <a href="https://makersuite.google.com/app/apikey" target="_blank">Google AI Studio</a></li>
                        <li>Sign in with your Google account</li>
                        <li>Create a new API key</li>
                    </ul>
                </li>
                <li><strong>Configure the app:</strong>
                    <ul>
                        <li>Edit <code>.streamlit/secrets.toml</code></li>
                        <li>Replace <code>"your_google_api_key_here"</code> with your actual API key</li>
                        <li>Save the file and restart the app</li>
                    </ul>
                </li>
            </ol>
            
            <p><strong>Example:</strong></p>
            <pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #dee2e6;">
google_api_key = "AIzaSyC..."</pre>
            
            <p><em>Your API key should start with "AI" and be about 39 characters long.</em></p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.stop()


if __name__ == "__main__":
    main()
