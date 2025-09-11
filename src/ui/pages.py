"""
Additional page functions for the VGC Analysis App
"""

import streamlit as st


def render_settings_page():
    """Render the settings page"""
    st.header("⚙️ Settings")
    
    
    # Display settings
    st.subheader("🎨 Display Preferences")
    st.info("🚧 Display preferences coming soon!")
    
def render_help_page():
    """Render the help and guide page"""
    st.header("📖 Help & User Guide")
    
    # Quick start guide
    st.subheader("🚀 Quick Start")
    st.markdown(
        """
        1. **📝 Input**: Paste a Japanese VGC article URL or text
        2. **🔍 Analyze**: Click the Analyze button to process
        3. **👀 Review**: Examine the translated team and analysis
        4. **💾 Export**: Download translations or pokepaste format
        """
    )
    
    # Supported formats
    st.subheader("📄 Supported Article Formats")
    st.markdown(
        """
        **✅ Supported Sites:**
        - note.com articles
        - Most Japanese Pokemon blogs
        - Tournament reports with team lists
        
        **🔍 What We Extract:**
        - Pokemon names, abilities, items
        - Move sets and EV spreads  
        - Strategic explanations
        - Tournament context
        """
    )
    
    # Sample URLs
    st.subheader("🌟 Sample Analysis")
    st.markdown(
        """
        Try analyzing this sample article featuring:
        - 🛡️ Zamazenta-Crowned
        - ⚔️ Iron Valiant
        - ⚡ Pawmot
        
        **Sample URL:** `https://note.com/icho_poke/n/n8ffb464e9335`
        """
    )
    
    # Troubleshooting
    st.subheader("🔧 Troubleshooting")
    with st.expander("Common Issues"):
        st.markdown(
            """
            **"Invalid URL" Error:**
            - Ensure the URL is accessible
            - Check for typos in the URL
            - Some sites may block automated access
            
            **"No Content Found" Error:**
            - Article may be too short
            - Content might not contain Pokemon team data
            - Try pasting the text directly instead
            
            **Slow Analysis:**
            - Large articles take longer to process
            - First analysis may take longer (caching helps)
            - Check your internet connection
            """
        )


def render_switch_translation_page():
    """Render the Nintendo Switch team translation page"""
    st.header("🎮 Switch Team Translation")
    
    st.info("🚧 Nintendo Switch team screenshot translation functionality coming soon!")
    
    st.markdown(
        """
        **Planned Features:**
        - Upload Nintendo Switch team screenshots
        - Automatic Pokemon identification from sprites
        - Team composition extraction
        - Export to analysis format
        
        **Supported Screenshots:**
        - Team builder screens
        - Battle box displays
        - Rental team views
        - Tournament team cards
        """
    )
    
    # Placeholder upload section
    st.subheader("📤 Upload Team Screenshot")
    
    uploaded_file = st.file_uploader(
        "Choose a Nintendo Switch screenshot...",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear screenshot of your Pokemon team from Nintendo Switch"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Team Screenshot", use_column_width=True)
        st.info("🔧 Image processing functionality will be implemented soon!")
        
    st.markdown("---")
    st.markdown("**💡 Tips for Best Results:**")
    st.markdown(
        """
        - Use high-resolution screenshots (1080p or higher)
        - Ensure Pokemon sprites are clearly visible
        - Avoid blurry or cropped images
        - Include the full team of 6 Pokemon when possible
        """
    )