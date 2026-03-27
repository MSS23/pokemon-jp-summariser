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

# --- Sidebar: API Key ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Google Gemini API Key")
st.sidebar.markdown("Enter your API key to use this application:")

api_key_input = st.sidebar.text_input(
    "API Key",
    type="password",
    value=st.session_state.user_api_key if st.session_state.user_api_key else "",
    help="Get your free API key from https://aistudio.google.com/app/apikey",
    placeholder="Enter your Google Gemini API key..."
)

if st.sidebar.button("Set API Key", type="primary"):
    if api_key_input and api_key_input.strip():
        st.session_state.user_api_key = api_key_input.strip()
        st.session_state.analyzer = None
        st.sidebar.success("API Key saved")
        st.rerun()
    else:
        st.sidebar.error("Please enter a valid API key")

if st.session_state.user_api_key:
    st.sidebar.success("API Key configured")
    if st.sidebar.button("Clear API Key"):
        st.session_state.user_api_key = None
        st.session_state.analyzer = None
        st.rerun()
else:
    st.sidebar.warning("No API key configured")
    st.sidebar.info("[Get a free API key](https://aistudio.google.com/app/apikey)")

st.sidebar.markdown("---")

# --- Sidebar: Navigation ---
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


def process_analysis(input_type: str, content: str):
    """Process analysis request"""
    analyzer = get_analyzer()
    if not analyzer:
        st.error("Please configure your Google Gemini API key in the sidebar to use analysis features.")
        st.info("Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
        return

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
                has_recovery_flag = result.get("recovery_successful", False)
                has_parsing_error = result.get("parsing_error", False)

                if pokemon_team or has_recovery_flag:
                    st.session_state.analysis_result = result
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

                    if pokemon_team and not has_parsing_error:
                        status.update(label=f"Complete - {len(pokemon_team)} Pokemon extracted", state="complete")
                    elif pokemon_team and has_parsing_error:
                        if len(pokemon_team) >= 3:
                            status.update(label=f"Complete - {len(pokemon_team)} Pokemon extracted", state="complete")
                        else:
                            status.update(label="Complete - team data may be incomplete", state="complete")
                    elif has_recovery_flag:
                        status.update(label="Partial analysis recovered", state="complete")
                    else:
                        status.update(label="Analysis complete", state="complete")

                    st.rerun()
                else:
                    status.update(label="No team data found", state="error")
                    st.error("No team data found. Please check your content and try again.")
                    if has_parsing_error:
                        st.info("Try using the 'Article Text' input method instead of URL.")
                    if input_type == "url":
                        with st.expander("Diagnostic Information"):
                            scraped_len = len(scraped_content) if scraped_content else 0
                            st.write(f"**Scraped content length:** {scraped_len} characters")
                            if scraped_content:
                                st.write("**Content preview (first 500 chars):**")
                                st.code(scraped_content[:500], language=None)
                    error_details = result.get("error_details")
                    if error_details:
                        with st.expander("Error Details"):
                            st.text(error_details)
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
    else:
        input_type, content = render_analysis_input()

        if st.button("Analyze", type="primary", use_container_width=True):
            if content and content.strip():
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
