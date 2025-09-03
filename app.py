"""
Pokemon VGC Analysis Platform - Streamlit App
Simple, direct entry point for Streamlit Cloud deployment
Version 2.0.1 - Deployment Optimized
"""

import sys
import os
from pathlib import Path
import logging

# Configure logging for deployment debugging
logging.basicConfig(level=logging.WARNING)

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Deployment environment detection
IS_STREAMLIT_CLOUD = os.getenv("STREAMLIT_CLOUD", "false").lower() == "true"
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

import streamlit as st

# Set page config immediately for deployment stability
st.set_page_config(
    page_title="Pokemon VGC Analysis Platform",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Pokemon VGC Analysis Platform - Translate and analyze Japanese VGC content"
    }
)

# Direct imports to avoid complex import chains
try:    
    # Import the application components with enhanced error handling
    from core.analyzer import GeminiVGCAnalyzer
    from ui.components import (
        render_page_header,
        render_analysis_input,
        render_article_summary,
        render_team_showcase,
        render_pokemon_team,
        render_export_section,
        render_image_analysis_section,
        render_sidebar,
        apply_custom_css
    )
    from ui.pages import render_switch_translation_page, render_settings_page
    from utils import cache
    from utils.config import Config
    
    # Force cache invalidation for deployment (v2.0.1 - deployment optimized)
    try:
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        if hasattr(st, 'cache_resource'):  
            st.cache_resource.clear()
    except Exception as e:
        logging.warning(f"Cache clearing failed: {e}")
    
    # Initialize the analyzer with error handling
    try:
        analyzer = GeminiVGCAnalyzer()
    except Exception as e:
        st.error("⚠️ Application initialization failed. Please check your API key configuration.")
        if not IS_PRODUCTION:
            st.exception(e)
        st.stop()
    
    # Initialize session state
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "current_url" not in st.session_state:
        st.session_state.current_url = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Analysis Home"


    # Apply custom styling
    apply_custom_css()

    # Render sidebar and get current page
    current_page = render_sidebar()
    st.session_state.current_page = current_page

    # Route to appropriate page
    def process_analysis(input_type: str, content: str):
        """Process analysis request"""
        try:
            with st.spinner("Analyzing content... This may take a moment."):
                if input_type == "url":
                    if not analyzer.validate_url(content):
                        st.error("Invalid or inaccessible URL. Please check the URL and try again.")
                        return

                    scraped_content = analyzer.scrape_article(content)
                    if not scraped_content:
                        st.error("Failed to extract content from URL. The page may be inaccessible or have no readable content.")
                        return

                    # Analyze with enhanced image analysis
                    result = analyzer.analyze_article_with_images(scraped_content, content)
                    st.session_state.current_url = content

                else:  # text input
                    result = analyzer.analyze_article(content)
                    st.session_state.current_url = None

                if result and result.get("pokemon_team"):
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete! Results displayed below.")
                    st.rerun()
                else:
                    st.error("❌ Analysis failed or no team data found. Please check your content and try again.")

        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")

    def display_analysis_results():
        """Display analysis results"""
        result = st.session_state.analysis_result
        
        if not result:
            return

        # Article summary
        if result.get("article_summary"):
            render_article_summary(result)

        # Team showcase
        if result.get("pokemon_team"):
            render_team_showcase(result)
            render_pokemon_team(result.get("pokemon_team"))

        # Export section
        render_export_section(result)

    # Page routing
    if current_page == "🏠 Analysis Home":
        # Main analysis page
        render_page_header()
        
        input_type, content = render_analysis_input()
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if content and content.strip():
                process_analysis(input_type, content)
            else:
                st.warning("⚠️ Please provide a URL or paste article text to analyze!")
        
        if st.session_state.analysis_result:
            display_analysis_results()
            
    elif current_page == "🎮 Switch Translation":
        render_switch_translation_page()
        
    elif current_page == "⚙️ Settings":  
        render_settings_page()
        
    elif current_page == "📖 Help & Guide":
        st.header("📖 Help & User Guide")
        
        st.markdown("""
        ## 🚀 Getting Started
        
        ### Step 1: Input Your Content
        - **URL Analysis**: Paste a link to a Japanese VGC article or team showcase
        - **Direct Text**: Copy and paste article content directly
        
        ### Step 2: Analyze
        Click the "🔍 Analyze" button to start the analysis process.
        
        ### Step 3: View Results
        - **Team Summary**: See the overall strategy and regulation
        - **Pokemon Details**: Individual Pokemon with EV spreads, movesets, and explanations
        - **Export Options**: Download as Pokepaste or view raw JSON data
        
        ## 🎯 Supported Sites
        - **note.com** - Japanese VGC articles and team showcases
        - **Twitter/X** - Tweet threads with VGC content  
        - **Plain text** - Any Japanese VGC content
        
        ## 💡 Tips for Best Results
        - Use URLs from reputable VGC content creators
        - Ensure the content includes team information and EV spreads
        - For text input, include complete team details
        
        ## 🔧 Features
        - **Smart Translation**: Accurate Pokemon name translation
        - **EV Detection**: Automatic EV spread extraction  
        - **Image Analysis**: Team cards and screenshots
        - **Export Tools**: Pokepaste format support
        
        ## ❓ Need Help?
        If you encounter issues, try:
        1. Check that the URL is accessible
        2. Verify the content contains VGC team information
        3. Use the Switch Translation feature for team screenshots
        """)
        
    else:
        # Default to analysis home
        render_page_header()
        input_type, content = render_analysis_input()
        
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if content and content.strip():
                process_analysis(input_type, content)
            else:
                st.warning("⚠️ Please provide a URL or paste article text to analyze!")
        
        if st.session_state.analysis_result:
            display_analysis_results()

except Exception as e:
    st.error(f"⚠️ Application Startup Failed")
    st.error("There was an issue initializing the Pokemon VGC Analysis Platform.")
    
    # Provide different error messages based on environment
    if IS_STREAMLIT_CLOUD:
        st.error("🔄 **Deployment Issue Detected**")
        st.info("If this persists, the deployment may need to be restarted. Please try:")
        st.info("1. Refresh the page in a few moments")
        st.info("2. Clear your browser cache")
        st.info("3. Try accessing the app in an incognito/private window")
    else:
        st.error("Please check that all dependencies are installed correctly.")
        st.info("Try running: `pip install -r requirements.txt`")
    
    # Deployment diagnostic info
    with st.expander("🔍 Diagnostic Information"):
        st.write("**Environment:**")
        st.write(f"- Streamlit Cloud: {IS_STREAMLIT_CLOUD}")
        st.write(f"- Production: {IS_PRODUCTION}")
        st.write(f"- Python Version: {sys.version}")
        st.write(f"- Working Directory: {os.getcwd()}")
        st.write(f"- Source Path: {src_path}")
        
    # Show debug info in development
    if not IS_PRODUCTION and st.checkbox("Show debug information"):
        st.exception(e)
        
    # Log error for debugging
    logging.error(f"Application initialization failed: {e}", exc_info=True)