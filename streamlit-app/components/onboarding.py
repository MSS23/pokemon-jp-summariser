"""
Onboarding component for new users
Shows helpful tips and guidance for first-time users
"""

import streamlit as st

def show_onboarding_guide():
    """
    Display an onboarding guide for new users
    """
    if st.session_state.get("show_onboarding", True):
        with st.expander("🚀 **New User Guide** - Click to learn how to use this app!", expanded=False):
            st.markdown("""
            ### Welcome to Pokémon VGC Summariser! 🎉
            
            This app helps you translate and analyze Japanese Pokémon VGC articles using Google Gemini AI.
            
            #### 📋 **Quick Start Guide:**
            
            1. **🔗 Paste a URL**: Copy the URL of a Japanese Pokémon article into the input field
            2. **✅ Verify**: The app will validate your URL and show if it's cached
            3. **🚀 Summarize**: Click the "Summarise with Gemini" button (or press Ctrl+Enter)
            4. **📊 Review**: Read the translated summary with team details
            5. **📊 Review**: Analyze the team composition and strategy
            
            #### ⌨️ **Keyboard Shortcuts:**
            - `Ctrl + Enter`: Start summarization
            - `Ctrl + K`: Focus on URL input
            - `Escape`: Clear current input
            
            #### 🎯 **What You'll Get:**
            - **Full Translation**: Japanese to English article translation
            - **Team Analysis**: Pokémon names, abilities, moves, EV spreads
            - **Tera Types**: Tera type information for each Pokémon
            - **Strategy Insights**: Team strengths, weaknesses, and meta relevance
            - **Team Analysis**: Detailed breakdown of each Pokémon's role
            
            #### 🔍 **Pro Tips:**
            - Use the **Search** page to find teams with specific Pokémon
            - Check **History** to revisit previous summaries
            - Visit **Settings** for model configuration options
            - Articles are automatically cached for faster access
            
            #### 🤖 **AI Model:**
            - **Google Gemini 2.0 Flash**: Excellent Japanese translation with image processing
            - **Free Tier**: 1500 requests per day
            - **High Accuracy**: Specialized for Pokémon content and VGC terminology
            
            ---
            
            **Ready to start?** Paste a Japanese Pokémon article URL above! 🎮
            """)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("✅ Got it! Don't show this again", use_container_width=True):
                    st.session_state["show_onboarding"] = False
                    st.rerun()

def show_quick_tips():
    """
    Show quick tips in a sidebar or info box
    """
    st.info("""
    💡 **Quick Tips:**
    - Press `Ctrl+Enter` to summarize
    - Use `Ctrl+K` to focus URL input
    - Check cache stats above for insights
    - Visit Search page to find specific Pokémon
    """)

def show_feature_highlight(feature_name: str, description: str, icon: str = "✨"):
    """
    Highlight a new or important feature
    
    Args:
        feature_name (str): Name of the feature
        description (str): Description of the feature
        icon (str): Icon to display
    """
    st.success(f"""
    {icon} **New Feature: {feature_name}**
    
    {description}
    """)

def show_keyboard_shortcuts():
    """
    Display available keyboard shortcuts
    """
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown("""
        | Shortcut | Action |
        |----------|--------|
        | `Ctrl + Enter` | Start summarization |
        | `Ctrl + K` | Focus URL input |
        | `Escape` | Clear current input |
        | `Tab` | Navigate between elements |
        | `Space` | Activate buttons |
        """)

def show_supported_sources():
    """
    Display information about supported article sources
    """
    with st.expander("📚 Supported Article Sources", expanded=False):
        st.markdown("""
        ### ✅ **Supported Sources:**
        - Japanese Pokémon blogs and websites
        - VGC team reports and analyses
        - Tournament coverage and results
        - Strategy guides and tutorials
        - Player interviews and team showcases
        
        ### 🎯 **Best Results With:**
        - Articles containing team lists (1-6 format)
        - Detailed Pokémon information
        - Strategy discussions
        - Tournament reports
        
        ### ⚠️ **May Not Work Well With:**
        - Video-only content
        - Image-heavy pages without text
        - Login-required content
        - Non-Pokémon related articles
        """)
