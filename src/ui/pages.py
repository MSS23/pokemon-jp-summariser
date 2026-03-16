"""
Additional page functions for the VGC Analysis App
Neon Dex design system.
"""

import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd


def render_feedback_viewer():
    """Render the feedback viewer page"""
    st.header("Feedback Viewer")

    feedback_json = "feedback_data.json"
    feedback_txt = "feedback_log.txt"

    has_json = os.path.exists(feedback_json)
    has_txt = os.path.exists(feedback_txt)

    if not has_json and not has_txt:
        st.info("No feedback has been submitted yet.")
        st.markdown("When users submit feedback through the **Report Issue** section in the sidebar, it will appear here.")
        return

    # Statistics
    st.subheader("Feedback Statistics")

    if has_json:
        try:
            with open(feedback_json, "r", encoding="utf-8") as f:
                data = json.load(f)

            feedback_list = data.get("feedback", [])
            total_count = len(feedback_list)

            if total_count > 0:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Feedback", total_count)

                most_recent = max(feedback_list, key=lambda x: x["timestamp"])
                recent_date = datetime.strptime(most_recent["timestamp"], "%Y-%m-%d %H:%M:%S")
                days_ago = (datetime.now() - recent_date).days
                col2.metric("Most Recent", f"{days_ago} days ago" if days_ago > 0 else "Today")

                problem_types = {}
                for fb in feedback_list:
                    ptype = fb["problem_type"]
                    problem_types[ptype] = problem_types.get(ptype, 0) + 1

                most_common_type = max(problem_types, key=problem_types.get)
                col3.metric("Most Common Issue", most_common_type)
                col4.metric("Issue Types", len(problem_types))

                st.markdown("### Issue Types Distribution")
                df_problems = pd.DataFrame(list(problem_types.items()), columns=["Problem Type", "Count"])
                st.bar_chart(df_problems.set_index("Problem Type"))

        except Exception as e:
            st.warning(f"Could not load feedback statistics: {str(e)}")

    # View mode
    st.subheader("View Feedback")

    view_mode = st.radio(
        "Choose view format:",
        ["Structured View", "Raw Text View", "Export Data"],
        horizontal=True,
    )

    if view_mode == "Structured View" and has_json:
        render_structured_feedback(feedback_json)
    elif view_mode == "Raw Text View" and has_txt:
        render_raw_feedback(feedback_txt)
    elif view_mode == "Export Data" and has_json:
        render_export_feedback(feedback_json)
    else:
        st.error("Selected view format not available.")


def render_structured_feedback(feedback_json):
    """Render feedback in structured format"""
    try:
        with open(feedback_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        feedback_list = data.get("feedback", [])

        if not feedback_list:
            st.info("No feedback entries found.")
            return

        feedback_list.sort(key=lambda x: x["timestamp"], reverse=True)
        st.markdown(f"**Showing {len(feedback_list)} feedback entries:**")

        for i, feedback in enumerate(feedback_list):
            with st.expander(f"#{feedback['id']} - {feedback['problem_type']} - {feedback['timestamp']}", expanded=i == 0):
                st.markdown("**Article URL:**")
                st.markdown(f"[{feedback['url']}]({feedback['url']})")

                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown("**Problem Type:**")
                    st.code(feedback["problem_type"])
                with col2:
                    st.markdown("**Description:**")
                    st.markdown(feedback["description"])

                st.markdown(f"**Submitted:** {feedback['timestamp']}")

    except Exception as e:
        st.error(f"Error loading structured feedback: {str(e)}")


def render_raw_feedback(feedback_txt):
    """Render raw text feedback"""
    try:
        with open(feedback_txt, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            st.info("No feedback entries in text file.")
            return

        st.markdown("**Raw feedback log:**")
        st.text_area("Feedback Log", content, height=400)

        st.download_button(
            label="Download Text Log",
            data=content,
            file_name=f"feedback_log_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
        )

    except Exception as e:
        st.error(f"Error loading raw feedback: {str(e)}")


def render_export_feedback(feedback_json):
    """Render export options for feedback"""
    try:
        with open(feedback_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        feedback_list = data.get("feedback", [])

        if not feedback_list:
            st.info("No feedback entries to export.")
            return

        st.markdown("**Export Options:**")

        df = pd.DataFrame(feedback_list)
        csv = df.to_csv(index=False)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        with col2:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download as JSON",
                data=json_str,
                file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
            )

        st.markdown("**Data Preview:**")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error preparing export: {str(e)}")


def render_settings_page():
    """Render the settings page"""
    st.markdown(
        """
        <div class="page-hero" style="padding: var(--sp-8) 0 var(--sp-6);">
            <div class="hero-content">
                <h1 style="font-size: 2rem;">Settings</h1>
                <p class="hero-sub">Configure your analysis preferences</p>
            </div>
            <div class="hero-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-section">
            <h3>Display Preferences</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">
                Display preferences coming soon. Stay tuned for theme customization,
                default export formats, and analysis depth controls.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_help_page():
    """Render the help and guide page"""
    st.markdown(
        """
        <div class="page-hero" style="padding: var(--sp-8) 0 var(--sp-6);">
            <div class="hero-content">
                <h1 style="font-size: 2rem;">Help & Guide</h1>
                <p class="hero-sub">Everything you need to get started</p>
            </div>
            <div class="hero-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Getting started
    st.markdown(
        """
        <div class="page-section">
            <h3>Getting Started</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-card__num">00</div>
                <div class="step-card__title">API Key Setup</div>
                <div class="step-card__desc">Enter your Google Gemini API key in the sidebar. Get a free key from Google AI Studio.</div>
            </div>
            <div class="step-card">
                <div class="step-card__num">01</div>
                <div class="step-card__title">Input Content</div>
                <div class="step-card__desc">Paste a Japanese VGC article URL or copy-paste the article text directly.</div>
            </div>
            <div class="step-card">
                <div class="step-card__num">02</div>
                <div class="step-card__title">Analyze</div>
                <div class="step-card__desc">Click Analyze to start AI-powered translation and team extraction.</div>
            </div>
            <div class="step-card">
                <div class="step-card__num">03</div>
                <div class="step-card__title">Export</div>
                <div class="step-card__desc">View results, download Pokepaste format, or export raw data.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Supported sites
    st.markdown(
        """
        <div class="page-section" style="animation-delay: 0.1s;">
            <h3>Supported Sites</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
- **note.com** - Japanese VGC articles and team showcases
- **hatenablog.com / hatenablog.jp** - Japanese Pokemon blogs
- **Twitter/X** - Tweet threads with VGC content
- **Plain text** - Any Japanese VGC content pasted directly
""")

    # Tips
    st.markdown(
        """
        <div class="page-section" style="animation-delay: 0.2s;">
            <h3>Tips for Best Results</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
- Use URLs from reputable VGC content creators
- Ensure the content includes team information and EV spreads
- For text input, include complete team details
- Shorter articles use fewer API resources and process faster
""")

    # API Usage
    st.markdown(
        """
        <div class="page-section" style="animation-delay: 0.3s;">
            <h3>API Usage & Limits</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
This application uses Google's Gemini API for analysis.

**Rate Limits & Quotas:**
- **Free tier**: Limited requests per minute and per day
- **Rate limits reset**: Automatically after 1-2 minutes
- **Daily quotas reset**: At midnight Pacific Time
""")

    with st.expander("Common API Issues"):
        st.markdown("""
**Rate Limit Reached** - Wait 1-2 minutes and try again. Spread out your analyses.

**Quota Exceeded** - Wait until tomorrow for reset, or consider upgrading to a paid Google Cloud plan.

**Authentication Issues** - Check your API key in Google Cloud Console. Verify Gemini API permissions are enabled.
""")

    with st.expander("Troubleshooting"):
        st.markdown("""
**"Invalid URL" Error:** Ensure the URL is accessible and check for typos. Some sites may block automated access.

**"No Content Found" Error:** Article may be too short or not contain Pokemon team data. Try pasting the text directly instead.

**"Slow Analysis":** Large articles take longer to process. Check your internet connection.
""")


def render_switch_translation_page():
    """Render the Nintendo Switch team translation page"""
    st.markdown(
        """
        <div class="page-hero" style="padding: var(--sp-8) 0 var(--sp-6);">
            <div class="hero-content">
                <h1 style="font-size: 2rem;">Switch Translation</h1>
                <p class="hero-sub">Translate Nintendo Switch team screenshots</p>
            </div>
            <div class="hero-divider"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="page-section">
            <h3>Coming Soon</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="steps-grid">
            <div class="step-card">
                <div class="step-card__num">01</div>
                <div class="step-card__title">Upload</div>
                <div class="step-card__desc">Upload Nintendo Switch team screenshots</div>
            </div>
            <div class="step-card">
                <div class="step-card__num">02</div>
                <div class="step-card__title">Identify</div>
                <div class="step-card__desc">Automatic Pokemon identification from sprites</div>
            </div>
            <div class="step-card">
                <div class="step-card__num">03</div>
                <div class="step-card__title">Extract</div>
                <div class="step-card__desc">Team composition extraction and export</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="page-section">
            <h3>Upload Team Screenshot</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a Nintendo Switch screenshot...",
        type=["png", "jpg", "jpeg"],
        help="Upload a clear screenshot of your Pokemon team from Nintendo Switch",
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Team Screenshot", use_column_width=True)
        st.info("Image processing functionality will be implemented soon.")

    st.markdown(
        """
        <div class="info-block info-block--info" style="margin-top: var(--sp-6);">
            <h4>Tips for Best Results</h4>
            <div>
                Use high-resolution screenshots (1080p or higher)<br>
                Ensure Pokemon sprites are clearly visible<br>
                Avoid blurry or cropped images<br>
                Include the full team of 6 Pokemon when possible
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
