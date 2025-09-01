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
    render_team_showcase,
    render_pokemon_team,
    render_export_section,
    render_sidebar,
    apply_custom_css,
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

    def run(self):
        """Run the main application"""
        # Apply custom styling
        apply_custom_css()

        # Render sidebar
        render_sidebar()

        # Main content
        self.render_main_content()

    def render_main_content(self):
        """Render the main application content"""
        # Page header
        render_page_header()

        # Input section
        input_type, content = render_analysis_input()

        # Analysis button and processing
        if st.button("🔍 Analyze", type="primary", use_container_width=True):
            if content and content.strip():
                self.process_analysis(input_type, content)
            else:
                st.error("Please provide content to analyze!")

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

                # Perform analysis
                result = self.analyzer.analyze_article(
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

                    st.success("Analysis complete! 🎉")
                    st.experimental_rerun()
                else:
                    st.error(
                        "Analysis failed. Please try again with different content."
                    )

        except ValueError as e:
            st.error(f"Analysis error: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

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
        st.header("🔧 Additional Options")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 New Analysis", use_container_width=True):
                self.clear_analysis()
                st.experimental_rerun()

        with col2:
            if DATABASE_AVAILABLE and st.button(
                "📚 View Saved Teams", use_container_width=True
            ):
                self.show_saved_teams()

        with col3:
            if st.button("ℹ️ Analysis Info", use_container_width=True):
                self.show_analysis_info(result)

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
