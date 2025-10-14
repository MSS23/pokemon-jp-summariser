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
    
    # Try to import the API error handling components with fallback
    try:
        from core.analyzer import APILimitError, get_user_friendly_api_error_message
    except ImportError:
        # Fallback implementations for deployment compatibility
        class APILimitError(Exception):
            """Fallback API limit error class"""
            def __init__(self, message: str, error_type: str = "unknown", retry_after: int = None):
                super().__init__(message)
                self.error_type = error_type
                self.retry_after = retry_after
        
        def get_user_friendly_api_error_message(error: APILimitError):
            """Fallback user-friendly error message function"""
            return {
                "icon": "⚠️",
                "title": "API Error",
                "message": f"An API error occurred: {str(error)}\n\nPlease try again in a moment.",
                "tips": ["Try again in a few moments", "Check your internet connection"]
            }
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
    from ui.pages import render_switch_translation_page, render_settings_page, render_feedback_viewer
    from utils.config import Config
    
    # Force cache invalidation for deployment (v2.0.1 - deployment optimized)
    try:
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        if hasattr(st, 'cache_resource'):  
            st.cache_resource.clear()
    except Exception as e:
        logging.warning(f"Cache clearing failed: {e}")
    
    # Initialize session state
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "current_url" not in st.session_state:
        st.session_state.current_url = None
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "🏠 Analysis Home"
    if "user_api_key" not in st.session_state:
        st.session_state.user_api_key = None
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None


    # Apply custom styling
    apply_custom_css()

    # API Key Input Section (Priority UI Element)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔑 Google Gemini API Key")
    st.sidebar.markdown("Enter your own API key to use this application:")

    # API key input field (password type for security)
    api_key_input = st.sidebar.text_input(
        "API Key",
        type="password",
        value=st.session_state.user_api_key if st.session_state.user_api_key else "",
        help="Get your free API key from https://makersuite.google.com/app/apikey",
        placeholder="Enter your Google Gemini API key..."
    )

    # Button to set/update API key
    if st.sidebar.button("Set API Key", type="primary"):
        if api_key_input and api_key_input.strip():
            st.session_state.user_api_key = api_key_input.strip()
            # Clear the analyzer so it will be re-initialized with the new key
            st.session_state.analyzer = None
            st.sidebar.success("✅ API Key saved!")
            st.rerun()
        else:
            st.sidebar.error("❌ Please enter a valid API key")

    # Show API key status
    if st.session_state.user_api_key:
        st.sidebar.success("✅ API Key configured")
        if st.sidebar.button("Clear API Key"):
            st.session_state.user_api_key = None
            st.session_state.analyzer = None
            st.rerun()
    else:
        st.sidebar.warning("⚠️ No API key configured")
        st.sidebar.info("👉 [Get a free API key](https://makersuite.google.com/app/apikey)")

    st.sidebar.markdown("---")

    # Render sidebar and get current page
    current_page = render_sidebar()
    st.session_state.current_page = current_page

    # Initialize analyzer with user's API key
    def get_analyzer():
        """Get or create analyzer instance with user's API key"""
        if not st.session_state.user_api_key:
            return None

        # Only create new analyzer if it doesn't exist or API key changed
        if st.session_state.analyzer is None:
            try:
                st.session_state.analyzer = GeminiVGCAnalyzer(api_key=st.session_state.user_api_key)
            except Exception as e:
                st.error(f"⚠️ Failed to initialize analyzer: {str(e)}")
                return None

        return st.session_state.analyzer

    # Check for admin access (with fallback for compatibility)
    is_admin = False
    try:
        # Use modern st.query_params (st.experimental_get_query_params deprecated after 2024-04-11)
        if hasattr(st, 'query_params'):
            query_params = st.query_params
            is_admin = query_params.get("admin", [False])[0] in ["true", "1", "yes"] if isinstance(query_params, dict) else False
        # Fallback for older Streamlit versions (legacy support)
        elif hasattr(st, 'experimental_get_query_params'):
            query_params = st.experimental_get_query_params()
            is_admin = query_params.get("admin", [False])[0] in ["true", "1", "yes"]
        # Fallback: check URL manually if available
        else:
            # Admin features disabled for this Streamlit version
            is_admin = False
    except Exception as e:
        # If admin access fails, just disable it - don't break the app
        is_admin = False
    
    # Route to appropriate page
    def process_analysis(input_type: str, content: str):
        """Process analysis request"""
        # Get analyzer instance
        analyzer = get_analyzer()
        if not analyzer:
            st.error("⚠️ Please configure your Google Gemini API key in the sidebar to use analysis features.")
            st.info("👉 Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
            return

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

                # Enhanced result validation to handle partial results
                if result and isinstance(result, dict):
                    pokemon_team = result.get("pokemon_team", [])
                    has_recovery_flag = result.get("recovery_successful", False)
                    has_parsing_error = result.get("parsing_error", False)
                    
                    # Accept results with Pokemon team OR successful partial recovery
                    if pokemon_team or has_recovery_flag:
                        st.session_state.analysis_result = result
                        st.session_state.analysis_complete = True
                        
                        # Provide appropriate success message based on result quality (enhanced messaging)
                        if pokemon_team and not has_parsing_error:
                            st.success("✅ Analysis complete! Full team analysis extracted successfully.")
                        elif pokemon_team and has_parsing_error:
                            # Only show warning if it's truly problematic
                            if len(pokemon_team) >= 3:  # Good team size despite minor issues
                                st.success(f"✅ Analysis complete! {len(pokemon_team)} Pokemon team successfully analyzed.")
                                st.info("ℹ️ Minor formatting issues were automatically resolved.")
                            else:
                                st.warning("⚠️ Analysis completed but team data may be incomplete. Consider trying again if results seem limited.")
                        elif has_recovery_flag:
                            # More specific messaging for recovery scenarios
                            if pokemon_team:
                                st.success(f"✅ Analysis successful! {len(pokemon_team)} Pokemon team recovered and analyzed.")
                                st.info("ℹ️ Analysis recovered successfully from response formatting issues.")
                            else:
                                st.info("ℹ️ Partial analysis recovered. Some information may be missing.")
                        else:
                            st.success("✅ Analysis complete! Results displayed below.")
                            
                        st.rerun()
                    else:
                        # No meaningful data found
                        st.error("❌ Analysis failed or no team data found. Please check your content and try again.")
                        
                        # Provide helpful diagnostics if available (improved messaging)
                        if has_parsing_error:
                            st.info("💡 **Tip**: If you're having issues, try using the 'Article Text' input method instead of URL, or ensure the article contains clear Pokemon team information.")
                        
                        # Show any error details for debugging
                        error_details = result.get("error_details")
                        if error_details:
                            with st.expander("🔍 Error Details"):
                                st.text(error_details)
                else:
                    st.error("❌ Analysis failed - invalid result format. Please try again.")

        except APILimitError as e:
            # Handle API limit errors with user-friendly messages
            error_info = get_user_friendly_api_error_message(e)
            
            # Display the error with proper formatting
            st.error(f"{error_info['icon']} **{error_info['title']}**")
            
            # Show the detailed message in an expandable section
            with st.expander("📖 **What does this mean and how to fix it**", expanded=True):
                st.markdown(error_info['message'])
                
                # Show helpful tips
                if error_info.get('tips'):
                    st.markdown("**💡 Pro Tips:**")
                    for tip in error_info['tips']:
                        st.markdown(f"• {tip}")
            
            # Show retry suggestion for rate limits
            if e.error_type == "rate_limit":
                retry_time = e.retry_after or 60
                if retry_time <= 120:  # Less than 2 minutes
                    st.info(f"⏰ Try again in about {retry_time // 60 if retry_time > 60 else 1} minute{'s' if retry_time > 60 else ''}. The rate limit will reset automatically.")
                    
        except Exception as e:
            # Handle other types of errors with the original simple message
            st.error(f"❌ Analysis error: {str(e)}")
            
            # Provide generic troubleshooting help
            with st.expander("🔍 Troubleshooting Help"):
                st.markdown("""
                **Common solutions:**
                • **Check your internet connection** - API calls require stable connectivity
                • **Try shorter content** - Very long articles can cause processing issues  
                • **Refresh the page** - Sometimes a clean start resolves temporary issues
                • **Try the 'Article Text' input** instead of URL if you used a link
                
                If the problem persists, the error details above can help with troubleshooting.
                """)

    def display_analysis_results():
        """Display analysis results"""
        result = st.session_state.analysis_result
        
        if not result:
            return

        # Article summary (always render as it handles missing fields gracefully)
        render_article_summary(result)

        # Team showcase
        if result.get("pokemon_team"):
            render_team_showcase(result)
            render_pokemon_team(result.get("pokemon_team"))

        # Export section
        render_export_section(result)

    # Admin-only access to feedback viewer (with error handling)
    admin_page_rendered = False
    if is_admin:
        try:
            # Safely check for page parameter
            page_param = ""
            if hasattr(st, 'query_params') and hasattr(st.query_params, 'get'):
                page_param = st.query_params.get("page", [""])[0]
            elif hasattr(st, 'experimental_get_query_params'):
                page_param = st.experimental_get_query_params().get("page", [""])[0]
                
            if page_param == "feedback":
                render_feedback_viewer()
                st.sidebar.markdown("---")
                st.sidebar.markdown("**🔒 Admin Mode Active**")
                st.sidebar.markdown("[📝 View Feedback](?admin=true&page=feedback)")
                st.sidebar.markdown("[🏠 Back to App](?)")
                admin_page_rendered = True
        except Exception as e:
            # If admin features fail, show error but continue with main app
            st.error("Admin features unavailable in this deployment environment.")
            admin_page_rendered = False
    
    # Page routing (only if admin page wasn't rendered)
    if not admin_page_rendered:
        if current_page == "🏠 Analysis Home":
            # Main analysis page
            render_page_header()

            # Show API key setup message if not configured
            if not st.session_state.user_api_key:
                st.warning("⚠️ **API Key Required**: Please enter your Google Gemini API key in the sidebar to use analysis features.")
                st.info("""
                **How to get your free API key:**
                1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
                2. Sign in with your Google account
                3. Click "Create API Key"
                4. Copy the key and paste it in the sidebar

                **Why do I need my own API key?**
                - Google Gemini API requires each user to have their own key
                - This prevents shared quota issues and API bans
                - Free tier includes generous usage limits
                - Your key is stored only in your browser session
                """)
            
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

        ### Step 0: Setup Your API Key (Required)
        - **Enter your API key** in the sidebar (password-protected field)
        - Get a free key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        - Click "Set API Key" to activate it
        - Your key is stored only in your browser session for security

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
        
        ## 🔧 API Usage & Limits
        
        This application uses Google's Gemini API for analysis. Here's what you need to know:
        
        ### Rate Limits & Quotas
        - **Free tier**: Limited requests per minute and per day
        - **Rate limits reset**: Automatically after 1-2 minutes  
        - **Daily quotas reset**: At midnight Pacific Time
        - **Tip**: Shorter articles use fewer API resources
        
        ### Common API Issues
        **⏱️ Rate Limit Reached**
        - Wait 1-2 minutes and try again
        - Use shorter content to reduce processing time
        - Spread out your analyses
        
        **📊 Quota Exceeded** 
        - Wait until tomorrow for reset
        - Consider upgrading to paid Google Cloud plan
        - Your session data stays until page refresh
        
        **🔐 Authentication Issues**
        - Check API key in Google Cloud Console
        - Verify Gemini API permissions are enabled
        
        ## ❓ Need Help?
        If you encounter issues, try:
        1. Check that the URL is accessible
        2. Verify the content contains VGC team information
        3. Use the Switch Translation feature for team screenshots
        4. Wait a moment and retry if you see API limit messages
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