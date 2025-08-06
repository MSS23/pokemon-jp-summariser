import streamlit as st

def show_navigation(current_page: str, authenticated: bool = False, user_info: dict = None):
    """
    Render a professional navigation bar using Streamlit components.
    """
    # Define page options - simplified navigation
    page_options = [
        ("🏠 Main Summariser", "Summariser"),
        ("📖 Help & Guide", "Help & Guide"),
    ]

    # Find current page index
    page_labels = [label for label, _ in page_options]
    page_keys = [key for _, key in page_options]
    
    if current_page in page_keys:
        current_index = page_keys.index(current_page)
    elif current_page in page_labels:
        current_index = page_labels.index(current_page)
    else:
        current_index = 0

    # Professional navigation using Streamlit columns
    st.markdown("""
    <div class="vgc-navbar" style="margin-bottom: 2rem;">
        <span class="nav-logo">⚡ Pokemon Japanese VGC Summariser</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Create navigation buttons in columns
    cols = st.columns(len(page_options))
    for idx, (label, key) in enumerate(page_options):
        with cols[idx]:
            if st.button(
                label, 
                key=f"nav_{key}",
                use_container_width=True,
                help=f"Navigate to {label}"
            ):
                st.session_state["current_page"] = key
                st.rerun()
    
    # Simple footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem; margin-top: 2rem;">
        ⚡ Powered by Google Gemini AI
    </div>
    """, unsafe_allow_html=True)
