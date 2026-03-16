"""
Sidebar rendering and feedback form for the Pokemon VGC Analysis Platform.
Neon Dex design system.
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime


def render_sidebar():
    """Sidebar with navigation, status, and feedback."""
    with st.sidebar:
        # Header
        st.markdown(
            """
            <div class="sidebar-header">
                <h2>VGC Analyzer</h2>
                <p>AI-Powered Team Analysis</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Navigation
        page = st.selectbox(
            "Navigate to:",
            [
                "Analysis Home",
                "Switch Translation",
                "Settings",
                "Help",
            ],
            index=0,
        )

        st.markdown("---")

        # New analysis button
        if st.button("New Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_result = None
            st.session_state.current_url = None
            st.session_state.analysis_complete = False
            st.rerun()

        # Current analysis status
        if st.session_state.get("analysis_result"):
            result = st.session_state.analysis_result
            pokemon_count = len(result.get("pokemon_team", []))
            regulation = result.get("regulation", "Unknown")

            st.markdown(
                f"""
                <div class="sidebar-status">
                    <strong>Current Team</strong><br>
                    {pokemon_count} Pokemon &middot; Regulation {regulation}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # About
        st.markdown(
            """
            <div class="sidebar-about">
                <strong>VGC Analysis Tool</strong><br>
                Powered by Google Gemini 2.5<br><br>
                Instant Japanese Translation<br>
                Professional Team Analysis<br>
                Export Ready Formats
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Feedback section
        st.markdown("---")
        with st.expander("Report Issue", expanded=False):
            st.markdown("Help us improve! Report analysis issues with specific examples.")
            st.caption("Both URL and detailed description are required.")

            feedback_url = st.text_input(
                "Article URL",
                value=st.session_state.feedback_url,
                placeholder="https://example.com/article-url",
                help="Paste the URL of the article that had issues",
                key="feedback_url_input",
            )

            url_valid = feedback_url and (
                feedback_url.startswith("http://") or feedback_url.startswith("https://")
            )
            if feedback_url and not url_valid:
                st.caption("Please enter a valid URL starting with http:// or https://")
            elif url_valid:
                st.caption("Valid URL format")

            problem_type = st.selectbox(
                "Issue Type",
                [
                    "Analysis Quality",
                    "Missing Pokemon",
                    "Wrong Strategy",
                    "Translation Error",
                    "App Bug",
                    "Other",
                ],
                help="Select the category that best describes your issue",
            )

            feedback_description = st.text_area(
                "Describe the Problem",
                value=st.session_state.feedback_description,
                placeholder="Describe what was wrong with the analysis...",
                help="Minimum 20 characters required",
                key="feedback_description_input",
                height=80,
            )

            description_valid = feedback_description and len(feedback_description.strip()) >= 20
            current_length = len(feedback_description.strip()) if feedback_description else 0

            if feedback_description:
                if description_valid:
                    st.caption(f"{current_length} characters (minimum met)")
                else:
                    st.caption(f"{current_length}/20 characters (need {20 - current_length} more)")
            else:
                st.caption("0/20 characters")

            st.session_state.feedback_url = feedback_url
            st.session_state.feedback_description = feedback_description

            can_submit = url_valid and description_valid

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(
                    "Submit Feedback",
                    disabled=not can_submit,
                    use_container_width=True,
                    type="primary" if can_submit else "secondary",
                ):
                    from ui.components import log_user_feedback
                    success = log_user_feedback(feedback_url, problem_type, feedback_description)
                    if success:
                        st.session_state.feedback_submitted = True
                        st.success("Feedback submitted successfully!")
                        st.session_state.feedback_url = ""
                        st.session_state.feedback_description = ""
                        st.rerun()
                    else:
                        st.error("Failed to submit feedback. Please try again.")

            with col2:
                if st.button("Clear Form", use_container_width=True):
                    st.session_state.feedback_url = ""
                    st.session_state.feedback_description = ""
                    st.rerun()

            if not can_submit:
                st.markdown("---")
                st.caption("Requirements to submit:")
                url_icon = "+" if url_valid else "-"
                desc_icon = "+" if description_valid else "-"
                st.caption(f"[{url_icon}] Valid article URL")
                st.caption(f"[{desc_icon}] Problem description (20+ characters)")

        # Troubleshooting
        st.markdown("---")
        st.markdown("**Troubleshooting**")

        if st.button(
            "Reset Session",
            use_container_width=True,
            help="Clear current analysis results and reset the application.",
        ):
            st.session_state.clear()
            st.success("Session reset complete!")
            st.rerun()

        return page


def render_image_analysis_section(analysis_result: Dict[str, Any]):
    """Render image analysis insights."""
    image_analysis = analysis_result.get("image_analysis")

    if not image_analysis or not image_analysis.get("success", False):
        return

    total_ev_spreads = 0
    image_analyses = image_analysis.get("image_analyses", [])

    for img_analysis in image_analyses:
        total_ev_spreads += len(img_analysis.get("ev_spreads", []))

    if total_ev_spreads > 0:
        st.success(
            f"Enhanced Analysis: Found {total_ev_spreads} additional EV spread{'s' if total_ev_spreads != 1 else ''} from team images"
        )
        with st.expander("View Additional EV Spreads", expanded=False):
            for i, img_analysis in enumerate(image_analyses):
                ev_spreads = img_analysis.get("ev_spreads", [])
                if ev_spreads:
                    st.write(f"**From Image {i+1}:**")
                    for ev_spread in ev_spreads:
                        spread_format = ev_spread.get("format", "Unknown")
                        st.code(f"{spread_format} (Total: {ev_spread.get('total', 'Unknown')} EVs)")
                    st.divider()
    else:
        st.info("Team images analyzed for additional details")
