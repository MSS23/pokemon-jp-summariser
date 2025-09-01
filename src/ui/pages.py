"""
Additional page methods for the VGC Analysis App
"""

def render_saved_teams_page(self):
    """Render the saved teams page"""
    st.header("📚 Saved Teams")
    
    if not DATABASE_AVAILABLE:
        st.warning("⚠️ Database not available. Teams cannot be saved or retrieved.")
        st.info("💡 Teams are still cached during your current session.")
        return
        
    try:
        teams = TeamCRUD.get_recent_teams(limit=20)
        if teams:
            st.success(f"Found {len(teams)} saved teams")
            
            for i, team in enumerate(teams):
                with st.expander(f"🏆 {team.name} - {team.created_at.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Regulation", team.regulation or "Not specified")
                        st.metric("Rating", f"{team.rating:.1f}/5.0" if team.rating else "Not rated")
                        
                    with col2:
                        if team.tournament_result:
                            st.write(f"**Result:** {team.tournament_result}")
                        if team.author:
                            st.write(f"**Author:** {team.author}")
                            
                    with col3:
                        if team.article_url:
                            st.write(f"**[View Original Article]({team.article_url})**")
                            
                    if team.strategy_summary:
                        st.write(f"**Strategy:** {team.strategy_summary}")
                        
                    # Show Pokemon names
                    pokemon_names = [p.name for p in team.pokemon]
                    if pokemon_names:
                        st.write(f"**Team:** {', '.join(pokemon_names)}")
        else:
            st.info("📝 No saved teams found. Analyze some articles to build your collection!")
            
    except Exception as e:
        st.error(f"Error loading saved teams: {e}")
        
def render_team_search_page(self):
    """Render the team search page"""
    st.header("🔍 Team Search")
    st.info("🚧 Team search functionality coming soon!")
    
    # Placeholder for future search functionality
    st.markdown(
        """
        **Planned Features:**
        - Search by Pokemon name
        - Filter by regulation (A, B, C)
        - Search by author
        - Filter by tournament results
        - Advanced team archetype filtering
        """
    )
    
def render_settings_page(self):
    """Render the settings page"""
    st.header("⚙️ Settings")
    
    # Cache settings
    st.subheader("💾 Cache Management")
    
    from utils import cache
    cache_stats = cache.get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cache Files", cache_stats['total_files'])
    with col2:
        st.metric("Valid Files", cache_stats['valid_files'])
    with col3:
        st.metric("Cache Size (MB)", cache_stats['total_size_mb'])
        
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Cache", use_container_width=True):
            cache.clear_all()
            st.success("Cache cleared successfully!")
            st.rerun()
            
    with col2:
        if st.button("🧹 Clear Expired Only", use_container_width=True):
            cleared = cache.clear_expired()
            st.success(f"Cleared {cleared} expired files!")
            st.rerun()
    
    # Display settings
    st.subheader("🎨 Display Preferences")
    st.info("🚧 Display preferences coming soon!")
    
def render_help_page(self):
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