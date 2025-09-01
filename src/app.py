"""
Pokemon VGC Article Analyzer & Team Showcase
A clean, modular Streamlit application for analyzing Japanese VGC articles
"""

import streamlit as st
from typing import Dict, Any, Optional

# Import our modular components
from src.utils.config import Config
from src.core.analyzer import GeminiVGCAnalyzer
from src.ui.components import (
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

# Import database components if available
try:
    from src.database.models import init_database
    from src.database.crud import TeamCRUD

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class VGCAnalysisApp:
    """Main application class for VGC Analysis"""

    def __init__(self):
        """Initialize the application"""
        self.analyzer = GeminiVGCAnalyzer()
        self.setup_page_config()

        # Initialize database if available
        if DATABASE_AVAILABLE:
            try:
                init_database()
            except Exception as e:
                st.warning(f"Database initialization failed: {e}")

        # Initialize session state
        self.init_session_state()

    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            page_icon=Config.PAGE_ICON,
            layout=Config.LAYOUT,
            initial_sidebar_state="expanded",
        )

    def init_session_state(self):
        """Initialize session state variables"""
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None
        if "current_url" not in st.session_state:
            st.session_state.current_url = None
        if "analysis_complete" not in st.session_state:
            st.session_state.analysis_complete = False
        if "current_page" not in st.session_state:
            st.session_state.current_page = "🏠 Analysis Home"
        if "saved_teams" not in st.session_state:
            st.session_state.saved_teams = []

    def run(self):
        """Run the main application"""
        # Apply custom styling
        apply_custom_css()

        # Render sidebar and get current page
        current_page = render_sidebar()
        st.session_state.current_page = current_page

        # Route to appropriate page
        self.route_page(current_page)

    def route_page(self, page: str):
        """Route to the appropriate page based on selection"""
        if page == "🏠 Analysis Home":
            self.render_analysis_page()
        elif page == "🎮 Switch Translation":
            self.render_switch_translation_page()
        elif page == "📚 Saved Teams":
            self.render_saved_teams_page()
        elif page == "🔍 Team Search":
            self.render_team_search_page()
        elif page == "⚙️ Settings":
            self.render_settings_page()
        elif page == "📖 Help & Guide":
            self.render_help_page()
        else:
            self.render_analysis_page()

    def render_analysis_page(self):
        """Render the main analysis page"""
        # Page header
        render_page_header()

        # Input section
        input_type, content = render_analysis_input()

        # Analysis button and processing
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if content and content.strip():
                self.process_analysis(input_type, content)
            else:
                st.warning("⚠️ Please provide a URL or paste article text to analyze!")

        # Display results if available
        if st.session_state.analysis_result:
            self.display_analysis_results()

    def process_analysis(self, input_type: str, content: str):
        """
        Process the analysis request

        Args:
            input_type: 'url' or 'text'
            content: URL or text content to analyze
        """
        try:
            with st.spinner("Analyzing content... This may take a moment."):
                if input_type == "url":
                    # Validate and scrape URL
                    if not self.analyzer.validate_url(content):
                        st.error(
                            "Invalid or inaccessible URL. "
                            "Please check the URL and try again."
                        )
                        return

                    # Scrape content from URL
                    scraped_content = self.analyzer.scrape_article(content)
                    if not scraped_content:
                        st.error(
                            "Failed to extract content from URL. "
                            "The page may be inaccessible or have no readable content."
                        )
                        return

                    analysis_content = scraped_content
                    st.session_state.current_url = content
                    
                    # Perform enhanced analysis with images
                    result = self.analyzer.analyze_article_with_images(
                        analysis_content, st.session_state.current_url
                    )
                
                else:  # text input
                    analysis_content = content
                    st.session_state.current_url = None
                    
                    # Perform enhanced analysis with images
                    result = self.analyzer.analyze_article_with_images(
                        analysis_content, st.session_state.current_url
                    )

                if result:
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True

                    # Save team to session state for search functionality
                    self.save_team_to_session(result, content, st.session_state.current_url)

                    # Save to database if available
                    if DATABASE_AVAILABLE and st.session_state.current_url:
                        self.save_analysis_to_database(
                            result, st.session_state.current_url
                        )

                    # Success message is now handled in the team showcase
                    st.rerun()
                else:
                    st.error(
                        "❌ Analysis failed. Please check your content and try again, or contact support if the issue persists."
                    )

        except ValueError as e:
            st.error(f"⚠️ **Content Issue:** {str(e)}")
            st.info("💡 **Tip:** Try pasting the article text directly instead of using the URL.")
        except Exception as e:
            st.error("❌ **Something went wrong.** Please try again or contact support if the problem persists.")
            with st.expander("Technical Details (for support)"):
                st.code(f"Error: {str(e)}")

    def save_analysis_to_database(self, result: Dict[str, Any], url: str):
        """
        Save analysis result to database

        Args:
            result: Analysis result dictionary
            url: Source URL
        """
        try:
            team = TeamCRUD.create_team_from_analysis(result, url)
            if team:
                st.info("Team saved to database for future reference!")
        except Exception as e:
            st.warning(f"Could not save to database: {e}")

    def save_team_to_session(self, result: Dict[str, Any], content: str, url: Optional[str] = None):
        """
        Save team to session state for search functionality
        
        Args:
            result: Analysis result dictionary
            content: Original content analyzed
            url: Optional source URL
        """
        from datetime import datetime
        import uuid
        
        # Create team entry for session state
        team_entry = {
            "id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "team_name": result.get("team_name", "Unnamed Team"),
            "regulation": result.get("regulation", "Unknown"),
            "pokemon_team": result.get("pokemon_team", []),
            "strategy_summary": result.get("strategy_summary", ""),
            "author": result.get("author", "Unknown"),
            "tournament_result": result.get("tournament_result", ""),
            "url": url,
            "pokemon_names": [p.get("name", "Unknown") for p in result.get("pokemon_team", [])],
            "analysis_result": result  # Store full result for display
        }
        
        # Add to saved teams (newest first)
        st.session_state.saved_teams.insert(0, team_entry)
        
        # Limit to 50 teams to prevent excessive memory usage
        if len(st.session_state.saved_teams) > 50:
            st.session_state.saved_teams = st.session_state.saved_teams[:50]

    def display_analysis_results(self):
        """Display the analysis results"""
        result = st.session_state.analysis_result

        # Article summary section - NEW!
        render_article_summary(result)

        # Team showcase section
        render_team_showcase(result)

        st.divider()

        # Pokemon team section
        pokemon_team = result.get("pokemon_team", [])
        if pokemon_team:
            render_pokemon_team(pokemon_team)
        else:
            st.warning("No Pokemon team data found in analysis.")

        st.divider()

        # Image analysis section
        render_image_analysis_section(result)

        st.divider()

        # Export section
        render_export_section(result)

        # Additional options
        self.render_additional_options(result)

    def render_additional_options(self, result: Dict[str, Any]):
        """
        Render additional options and actions

        Args:
            result: Analysis result
        """
        st.header("🔄 What's Next?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Analyze Another Team", type="primary", use_container_width=True):
                self.clear_analysis()
                st.rerun()

        with col2:
            st.markdown("**Ready to build?** Use the export options above to get your team ready for Pokemon Showdown or competitive play!")

    def clear_analysis(self):
        """Clear current analysis from session state"""
        st.session_state.analysis_result = None
        st.session_state.current_url = None
        st.session_state.analysis_complete = False

    def show_saved_teams(self):
        """Show saved teams from database"""
        if not DATABASE_AVAILABLE:
            st.warning("Database not available")
            return

        try:
            teams = TeamCRUD.get_recent_teams(limit=10)
            if teams:
                st.subheader("📚 Recently Analyzed Teams")
                for team in teams:
                    with st.expander(
                        f"{team.name} - {team.created_at.strftime('%Y-%m-%d')}"
                    ):
                        st.write(f"**Regulation:** {team.regulation}")
                        st.write(f"**Strategy:** {team.strategy_summary}")
                        if team.article_url:
                            st.write(f"**Source:** {team.article_url}")
            else:
                st.info("No saved teams found")
        except Exception as e:
            st.error(f"Error loading saved teams: {e}")

    def show_analysis_info(self, result: Dict[str, Any]):
        """
        Show detailed analysis information

        Args:
            result: Analysis result
        """
        st.subheader("📊 Analysis Details")

        # Analysis metadata
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Pokemon Analyzed", len(result.get("pokemon_team", [])))
            st.metric("Regulation", result.get("regulation", "Not specified"))

        with col2:
            if st.session_state.current_url:
                st.write(f"**Source URL:** {st.session_state.current_url}")

            tournament_context = result.get("tournament_context", "")
            if tournament_context:
                st.write(f"**Tournament:** {tournament_context}")

        # Translation notes if available
        translation_notes = result.get("translation_notes", "")
        if translation_notes:
            st.write(f"**Translation Notes:** {translation_notes}")

    def render_switch_translation_page(self):
        """Render the dedicated Switch screenshot translation page"""
        # Custom header for Switch translation
        st.markdown(
            """
            <div style="text-align: center; padding: 2.5rem 0;
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border-radius: 20px; margin-bottom: 2rem; 
            box-shadow: 0 8px 32px rgba(79, 70, 229, 0.3);">
                <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700; 
                          text-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                    🎮 Switch Screenshot Translator
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: 1rem 0 0 0; 
                          font-size: 1.2rem; font-weight: 300;">
                    Instant Japanese → English Pokemon Team Translation
                </p>
                <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; 
                          font-size: 1rem; background: rgba(255,255,255,0.1); 
                          padding: 0.5rem 1rem; border-radius: 25px; display: inline-block;">
                    Upload Switch Screenshot → Get Pokepaste
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        # Instructions section
        with st.expander("📋 How to Use Switch Translation", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    """
                    **✅ Perfect Screenshots:**
                    • Nintendo Switch team builder screen
                    • Blue background with 6 Pokemon
                    • Japanese Pokemon names clearly visible
                    • Held item icons visible
                    • Good lighting and focus
                    """
                )
            
            with col2:
                st.markdown(
                    """
                    **⚡ What You'll Get:**
                    • Japanese → English name translation
                    • Held item identification
                    • Instant pokepaste download
                    • Team ready for Pokemon Showdown
                    • Basic team composition analysis
                    """
                )

        st.divider()

        # Upload section
        st.header("📷 Upload Your Switch Screenshot")
        
        uploaded_file = st.file_uploader(
            "Choose your Nintendo Switch team screenshot",
            type=['png', 'jpg', 'jpeg'],
            help="Nintendo Switch screenshots work best! Make sure Japanese Pokemon names are clearly visible."
        )

        if uploaded_file is not None:
            # Display the uploaded image
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)
            
            st.success(f"✅ Screenshot uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")

            # Analyze button
            if st.button("🔍 Translate Team", type="primary", use_container_width=True):
                self.process_switch_translation(uploaded_file)

        # Display results if available
        if st.session_state.get("switch_translation_result"):
            self.display_switch_translation_results()

    def process_switch_translation(self, uploaded_file):
        """Process the Switch screenshot translation"""
        try:
            with st.spinner("🎯 Analyzing Switch screenshot... This may take a moment."):
                # Convert uploaded file to format needed for analysis
                import base64
                file_bytes = uploaded_file.getvalue()
                encoded_image = base64.b64encode(file_bytes).decode('utf-8')
                
                # Get image format
                image_format = uploaded_file.type.split('/')[-1] if uploaded_file.type else 'png'
                
                # Analyze screenshot directly
                result = self.analyzer.analyze_screenshot(
                    encoded_image, image_format, uploaded_file.name
                )

                if result and result.get("success"):
                    st.session_state.switch_translation_result = result
                    st.success("✅ Translation completed successfully!")
                    st.rerun()
                else:
                    error_msg = result.get("error", "Unknown error occurred")
                    st.error(f"❌ Translation failed: {error_msg}")
                    st.info("💡 **Tips:**\n- Make sure this is a Nintendo Switch team screenshot\n- Ensure Japanese text is clear and readable\n- Try a different screenshot if this one doesn't work")

        except Exception as e:
            st.error(f"❌ **Something went wrong:** {str(e)}")
            st.info("💡 **Try:**\n- Checking your screenshot format (PNG, JPG)\n- Using a clearer screenshot\n- Refreshing the page and trying again")

    def display_switch_translation_results(self):
        """Display the Switch translation results"""
        result = st.session_state.switch_translation_result
        
        st.header("🎯 Translation Results")
        
        pokemon_team = result.get("pokemon_team", [])
        
        if not pokemon_team:
            st.warning("⚠️ No Pokemon were detected in the screenshot. Please try a different image.")
            return
        
        # Display confidence and summary
        confidence = result.get("screenshot_analysis", {}).get("extraction_confidence", "medium")
        pokemon_count = len(pokemon_team)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pokemon Detected", f"{pokemon_count}/6")
        with col2:
            st.metric("Confidence", confidence.title())
        with col3:
            st.metric("Status", "✅ Ready" if pokemon_count >= 4 else "⚠️ Partial")

        st.divider()

        # Translation mapping display
        st.subheader("🔄 Japanese → English Translation")
        
        for i, pokemon in enumerate(pokemon_team, 1):
            name = pokemon.get("name", "Unknown")
            held_item = pokemon.get("held_item", "Not specified")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.markdown(f"**#{i}** 🎌 *Japanese Name*")
            with col2:
                st.markdown(f"**→ {name}**")
            with col3:
                if held_item != "Not specified":
                    st.markdown(f"🎒 *{held_item}*")
                else:
                    st.markdown("🎒 *No item detected*")

        st.divider()

        # Export section
        st.subheader("💾 Download Your Team")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate pokepaste
            try:
                from utils import create_pokepaste
                pokepaste_content = create_pokepaste(
                    pokemon_team, 
                    result.get("team_name", "Switch Screenshot Team")
                )
                
                st.download_button(
                    label="📥 Download Pokepaste",
                    data=pokepaste_content,
                    file_name=f"switch_team_{result.get('filename', 'screenshot')}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error generating pokepaste: {str(e)}")
        
        with col2:
            # Clear results button
            if st.button("🔄 Translate Another Screenshot", use_container_width=True):
                if "switch_translation_result" in st.session_state:
                    del st.session_state.switch_translation_result
                st.rerun()

        # Raw analysis details (collapsible)
        with st.expander("🔍 Technical Details", expanded=False):
            raw_output = result.get("screenshot_analysis", {}).get("raw_vision_output", "No details available")
            st.text_area("Raw Vision Analysis", raw_output, height=200)

    def render_saved_teams_page(self):
        """Render the saved teams page using session state"""
        st.header("📚 Saved Teams")

        # Check if there are saved teams
        if not st.session_state.saved_teams:
            st.info("📝 No saved teams yet. Analyze some articles to build your collection!")
            st.markdown(
                """
                **How to save teams:**
                1. Go to Analysis Home
                2. Analyze Japanese VGC articles
                3. Teams are automatically saved here
                4. Use Team Search to find specific teams
                """
            )
            return

        st.success(f"🏆 Found {len(st.session_state.saved_teams)} saved teams")
        
        # Add management options
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**📋 Recent Teams (newest first):**")
        with col2:
            if st.button("🗑️ Clear All Teams", help="Remove all saved teams"):
                st.session_state.saved_teams = []
                st.success("All teams cleared!")
                st.rerun()

        st.markdown("---")

        # Display saved teams
        for i, team in enumerate(st.session_state.saved_teams):
            with st.expander(
                f"🏆 {team.get('team_name', 'Unnamed Team')} - "
                f"{team.get('regulation', 'Unknown')} - "
                f"{team.get('timestamp', '')[:10]}"
            ):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("📊 Regulation", team.get('regulation', 'Unknown'))
                    st.metric("⚔️ Pokemon", len(team.get('pokemon_names', [])))

                with col2:
                    if team.get("tournament_result"):
                        st.write(f"**🏆 Result:** {team.get('tournament_result')}")
                    if team.get("author"):
                        st.write(f"**👤 Author:** {team.get('author')}")

                with col3:
                    st.write(f"**📅 Saved:** {team.get('timestamp', '')[:16]}")
                    if team.get("url"):
                        st.write(f"**🔗 [View Original]({team.get('url')})**")

                if team.get("strategy_summary"):
                    st.write(f"**🎯 Strategy:** {team.get('strategy_summary')}")

                # Show Pokemon names
                pokemon_names = team.get("pokemon_names", [])
                if pokemon_names:
                    st.write(f"**⚔️ Team:** {' • '.join(pokemon_names)}")

                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📖 View Analysis", key=f"view_{team.get('id')}"):
                        st.session_state.analysis_result = team.get("analysis_result")
                        st.session_state.current_url = team.get("url")
                        st.session_state.analysis_complete = True
                        st.session_state.current_page = "🏠 Analysis Home"
                        st.rerun()
                
                with col2:
                    if st.button(f"🗑️ Delete Team", key=f"delete_{team.get('id')}"):
                        st.session_state.saved_teams.remove(team)
                        st.success("Team deleted!")
                        st.rerun()

    def render_team_search_page(self):
        """Render the team search page with full functionality"""
        st.header("🔍 Team Search")
        
        # Check if there are saved teams
        if not st.session_state.saved_teams:
            st.info("📝 No saved teams yet. Analyze some articles to build your team collection!")
            st.markdown(
                """
                **How to build your collection:**
                1. Go to Analysis Home
                2. Input a Japanese VGC article URL or text
                3. Teams will automatically be saved here for searching
                """
            )
            return
        
        st.success(f"🏆 Found {len(st.session_state.saved_teams)} saved teams")
        
        # Search and filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input(
                "🔍 Search Pokemon/Team Name",
                placeholder="Enter Pokemon name...",
                help="Search for specific Pokemon in teams"
            )
        
        with col2:
            regulations = ["All"] + list(set([
                team.get("regulation", "Unknown") 
                for team in st.session_state.saved_teams
            ]))
            selected_regulation = st.selectbox("📊 Filter by Regulation", regulations)
        
        with col3:
            authors = ["All"] + list(set([
                team.get("author", "Unknown") 
                for team in st.session_state.saved_teams
            ]))
            selected_author = st.selectbox("👤 Filter by Author", authors)
        
        # Apply filters
        filtered_teams = self.filter_teams(
            st.session_state.saved_teams, 
            search_term, 
            selected_regulation, 
            selected_author
        )
        
        st.markdown("---")
        
        if not filtered_teams:
            st.warning("🔍 No teams found matching your search criteria.")
            return
        
        st.markdown(f"**📋 Showing {len(filtered_teams)} teams:**")
        
        # Display filtered teams
        for i, team in enumerate(filtered_teams):
            self.render_search_result(team, i)
    
    def filter_teams(self, teams, search_term, regulation, author):
        """Filter teams based on search criteria"""
        filtered = teams
        
        # Filter by search term (Pokemon names)
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                team for team in filtered
                if any(search_lower in pokemon.lower() for pokemon in team.get("pokemon_names", []))
                or search_lower in team.get("team_name", "").lower()
            ]
        
        # Filter by regulation
        if regulation != "All":
            filtered = [
                team for team in filtered
                if team.get("regulation", "Unknown") == regulation
            ]
        
        # Filter by author
        if author != "All":
            filtered = [
                team for team in filtered
                if team.get("author", "Unknown") == author
            ]
        
        return filtered
    
    def render_search_result(self, team, index):
        """Render a single team search result"""
        with st.expander(
            f"🏆 {team.get('team_name', 'Unnamed Team')} - {team.get('regulation', 'Unknown')} "
            f"({len(team.get('pokemon_names', []))} Pokemon)"
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Team info
                st.markdown(f"**📊 Regulation:** {team.get('regulation', 'Unknown')}")
                st.markdown(f"**👤 Author:** {team.get('author', 'Unknown')}")
                
                if team.get("tournament_result"):
                    st.markdown(f"**🏆 Result:** {team.get('tournament_result')}")
                
                if team.get("strategy_summary"):
                    st.markdown(f"**🎯 Strategy:** {team.get('strategy_summary')[:200]}...")
                
                # Pokemon team
                pokemon_names = team.get("pokemon_names", [])
                if pokemon_names:
                    st.markdown(f"**⚔️ Team:** {' • '.join(pokemon_names)}")
            
            with col2:
                # Actions
                st.markdown(f"**📅 Saved:** {team.get('timestamp', '')[:10]}")
                
                if team.get("url"):
                    st.markdown(f"**🔗 [View Original]({team.get('url')})**")
                
                # Load team button
                if st.button(f"📖 View Full Analysis", key=f"load_team_{team.get('id')}"):
                    st.session_state.analysis_result = team.get("analysis_result")
                    st.session_state.current_url = team.get("url")
                    st.session_state.analysis_complete = True
                    st.session_state.current_page = "🏠 Analysis Home"
                    st.rerun()

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

        # Getting Started
        st.subheader("🚀 Getting Started")
        st.markdown(
            """
            **Step 1:** Find a Japanese VGC article or tournament report
            **Step 2:** Copy the article URL or paste the text content
            **Step 3:** Click Analyze to get instant translations and team analysis
            **Step 4:** Export your results for team building or research
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


def main():
    """Main application entry point"""
    try:
        # Initialize configuration
        Config.init_config()

        # Create and run the application
        app = VGCAnalysisApp()
        app.run()

    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please check your configuration and try again.")


if __name__ == "__main__":
    main()