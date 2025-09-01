"""
Pokemon VGC Article Analyzer & Team Showcase
A clean, modular Streamlit application for analyzing Japanese VGC articles
"""

import streamlit as st
from typing import Dict, Any

# Import our modular components
from config import Config
from vgc_analyzer import GeminiVGCAnalyzer
from ui_components import (
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
    from database.models import init_database
    from database.crud import TeamCRUD

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
                else:
                    analysis_content = content
                    st.session_state.current_url = None

                # Perform enhanced analysis with images
                result = self.analyzer.analyze_article_with_images(
                    analysis_content, st.session_state.current_url
                )

                if result:
                    st.session_state.analysis_result = result
                    st.session_state.analysis_complete = True

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

        from cache_manager import cache
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