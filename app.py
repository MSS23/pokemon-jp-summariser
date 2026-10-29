"""
Pokemon VGC Analysis Platform - Streamlit App
Simple, direct entry point for Streamlit Cloud deployment
"""

import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.WARNING)

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

st.set_page_config(
    page_title="VGC Team Analyzer",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "VGC Team Analyzer - AI-powered Japanese VGC article translation"
    }
)

# Import application components - protected to show a useful error on failure
try:
    from core.analyzer import GeminiVGCAnalyzer, APILimitError, get_user_friendly_api_error_message
    from ui.components import (
        render_page_header,
        render_onboarding,
        render_analysis_input,
        render_article_summary,
        render_team_showcase,
        render_pokemon_team,
        render_export_section,
        render_image_analysis_section,
        render_sidebar,
        apply_custom_css
    )
    from ui.pages import render_switch_translation_page, render_settings_page, render_help_page
    from utils.config import Config, init_session_state
    from utils.utils import create_content_hash
except Exception as e:
    st.error("Application failed to load. Please check that all dependencies are installed.")
    st.info("Try running: `pip install -r requirements.txt`")
    with st.expander("Diagnostic Information"):
        st.write(f"- Python Version: {sys.version}")
        st.write(f"- Working Directory: {os.getcwd()}")
        st.write(f"- Source Path: {src_path}")
        st.exception(e)
    st.stop()

# Initialize all session state keys in one place
init_session_state()

# Apply custom styling
apply_custom_css()

# --- Sidebar: Navigation (renders header, nav, API key, history, feedback) ---
current_page = render_sidebar()
st.session_state.current_page = current_page


# --- Helper functions ---

def get_analyzer():
    """Get or create analyzer instance with user's API key"""
    if not st.session_state.user_api_key:
        return None
    if st.session_state.analyzer is None:
        try:
            st.session_state.analyzer = GeminiVGCAnalyzer(api_key=st.session_state.user_api_key)
        except Exception as e:
            st.error(f"Failed to initialize analyzer: {str(e)}")
            return None
    return st.session_state.analyzer


@st.cache_resource
def _result_cache() -> dict:
    """Process-wide cache of successful analyses, keyed by model + input (URL or pasted text)."""
    # ponytail: in-memory, lost on restart and capped at 100 entries; move to disk/DB if reuse across restarts matters
    return {}


def process_analysis(input_type: str, content: str):
    """Process analysis request"""
    analyzer = get_analyzer()
    if not analyzer:
        st.error("Please configure your Google Gemini API key in the sidebar to use analysis features.")
        st.info("Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
        return

    cache = _result_cache()
    cache_key = create_content_hash(f"{analyzer.model_name}|{input_type}|{content.strip()}")
    if cache_key in cache:
        st.session_state.analysis_result = {**cache[cache_key], "is_cached_result": True}
        st.session_state.current_url = content if input_type == "url" else None
        st.session_state.analysis_complete = True
        st.rerun()

    try:
        with st.status("Analyzing content...", expanded=True) as status:
            if input_type == "url":
                status.update(label="Scraping article...", state="running")
                st.write("Fetching and extracting article content...")
                scraped_content = analyzer.scrape_article(content)
                if not scraped_content:
                    status.update(label="Scraping failed", state="error")
                    st.error("Failed to extract content from URL. The page may be inaccessible or have no readable content.")
                    return

                st.write(f"Extracted {len(scraped_content):,} characters of content.")
                status.update(label="Analyzing with Gemini AI...", state="running")
                st.write("Translating and extracting team data...")
                result = analyzer.analyze_article_with_images(scraped_content, content)
                st.session_state.current_url = content
            else:
                status.update(label="Analyzing with Gemini AI...", state="running")
                st.write("Translating and extracting team data...")
                result = analyzer.analyze_article(content)
                st.session_state.current_url = None

            status.update(label="Validating results...", state="running")
            st.write("Checking extracted team data...")

            # Validate and store results
            if result and isinstance(result, dict):
                pokemon_team = result.get("pokemon_team", [])

                if pokemon_team:
                    st.session_state.analysis_result = result
                    cache[cache_key] = result
                    if len(cache) > 100:
                        cache.pop(next(iter(cache)))
                    st.session_state.analysis_complete = True

                    # Save to history
                    from datetime import datetime
                    history_entry = {
                        "title": result.get("title", "Untitled"),
                        "author": result.get("author", "Unknown"),
                        "pokemon_count": len(pokemon_team),
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "url": st.session_state.current_url,
                        "result": result,
                    }
                    history = st.session_state.get("analysis_history", [])
                    # Avoid duplicate consecutive entries
                    if not history or history[-1].get("title") != history_entry["title"]:
                        history.append(history_entry)
                        st.session_state.analysis_history = history[-10:]  # Keep last 10

                    status.update(label=f"Complete - {len(pokemon_team)} Pokemon extracted", state="complete")

                    st.rerun()
                else:
                    status.update(label="No team data found", state="error")
                    st.error("No team data found. Please check your content and try again.")
                    if input_type == "url":
                        with st.expander("Diagnostic Information"):
                            scraped_len = len(scraped_content) if scraped_content else 0
                            st.write(f"**Scraped content length:** {scraped_len} characters")
                            if scraped_content:
                                st.write("**Content preview (first 500 chars):**")
                                st.code(scraped_content[:500], language=None)
            else:
                status.update(label="Analysis failed", state="error")
                st.error("Analysis failed - invalid result format. Please try again.")

    except APILimitError as e:
        error_info = get_user_friendly_api_error_message(e)
        st.error(f"**{error_info['title']}**")
        with st.expander("What does this mean and how to fix it", expanded=True):
            st.markdown(error_info['message'])
            if error_info.get('tips'):
                st.markdown("**Tips:**")
                for tip in error_info['tips']:
                    st.markdown(f"- {tip}")

    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        with st.expander("Troubleshooting Help"):
            st.markdown("""
**Common solutions:**
- Check your internet connection
- Try shorter content
- Refresh the page
- Try the 'Article Text' input instead of URL
""")


def display_analysis_results():
    """Display analysis results"""
    result = st.session_state.analysis_result
    if not result:
        return

    if result.get("is_cached_result"):
        st.caption("Served from cache: this input was already analysed on this server, so no Gemini call was made.")
    render_article_summary(result)

    if result.get("pokemon_team"):
        render_team_showcase(result)
        render_pokemon_team(result.get("pokemon_team"))

    # Show image analysis insights if available
    render_image_analysis_section(result)

    render_export_section(result)


# --- Page routing ---

if current_page == "Analysis Home":
    render_page_header()

    if not st.session_state.user_api_key:
        render_onboarding()

    input_type, content = render_analysis_input()

    if st.button("Analyze", type="primary", width="stretch"):
        if not st.session_state.user_api_key:
            st.warning("Please set your Google Gemini API key in the sidebar first.")
        elif content and content.strip():
            process_analysis(input_type, content)
        else:
            st.warning("Please provide a URL or paste article text to analyze.")

    if st.session_state.analysis_result:
        display_analysis_results()

elif current_page == "Switch Translation":
    render_switch_translation_page()

elif current_page == "Settings":
    render_settings_page()

elif current_page == "Help":
    render_help_page()
