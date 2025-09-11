"""
Additional page functions for the VGC Analysis App
"""

import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd


def render_feedback_viewer():
    """Render the feedback viewer page"""
    st.header("📝 Feedback Viewer")
    
    feedback_json = "feedback_data.json"
    feedback_txt = "feedback_log.txt"
    
    # Check if feedback files exist
    has_json = os.path.exists(feedback_json)
    has_txt = os.path.exists(feedback_txt)
    
    if not has_json and not has_txt:
        st.info("📭 No feedback has been submitted yet.")
        st.markdown("When users submit feedback through the **Report Issue** section in the sidebar, it will appear here.")
        return
    
    # Statistics section
    st.subheader("📊 Feedback Statistics")
    
    if has_json:
        try:
            with open(feedback_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            feedback_list = data.get("feedback", [])
            total_count = len(feedback_list)
            
            if total_count > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                # Total feedback
                col1.metric("Total Feedback", total_count)
                
                # Most recent
                most_recent = max(feedback_list, key=lambda x: x["timestamp"])
                recent_date = datetime.strptime(most_recent["timestamp"], "%Y-%m-%d %H:%M:%S")
                days_ago = (datetime.now() - recent_date).days
                col2.metric("Most Recent", f"{days_ago} days ago" if days_ago > 0 else "Today")
                
                # Problem types breakdown
                problem_types = {}
                for fb in feedback_list:
                    ptype = fb["problem_type"]
                    problem_types[ptype] = problem_types.get(ptype, 0) + 1
                
                most_common_type = max(problem_types, key=problem_types.get)
                col3.metric("Most Common Issue", most_common_type)
                col4.metric("Issue Types", len(problem_types))
                
                # Problem types distribution
                st.markdown("### 📈 Issue Types Distribution")
                df_problems = pd.DataFrame(list(problem_types.items()), columns=["Problem Type", "Count"])
                st.bar_chart(df_problems.set_index("Problem Type"))
                
        except Exception as e:
            st.warning(f"Could not load feedback statistics: {str(e)}")
    
    # View mode selector
    st.subheader("👀 View Feedback")
    
    view_mode = st.radio(
        "Choose view format:",
        ["📋 Structured View", "📄 Raw Text View", "📊 Export Data"],
        horizontal=True
    )
    
    if view_mode == "📋 Structured View" and has_json:
        render_structured_feedback(feedback_json)
    elif view_mode == "📄 Raw Text View" and has_txt:
        render_raw_feedback(feedback_txt)
    elif view_mode == "📊 Export Data" and has_json:
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
        
        # Sort by timestamp (most recent first)
        feedback_list.sort(key=lambda x: x["timestamp"], reverse=True)
        
        st.markdown(f"**Showing {len(feedback_list)} feedback entries:**")
        
        for i, feedback in enumerate(feedback_list):
            with st.expander(f"**#{feedback['id']}** - {feedback['problem_type']} - {feedback['timestamp']}", expanded=i==0):
                
                # Article URL
                st.markdown("**🔗 Article URL:**")
                st.markdown(f"[{feedback['url']}]({feedback['url']})")
                
                # Problem details
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown("**📋 Problem Type:**")
                    st.code(feedback["problem_type"])
                
                with col2:
                    st.markdown("**📝 Description:**")
                    st.markdown(feedback["description"])
                
                # Timestamp
                st.markdown(f"**⏰ Submitted:** {feedback['timestamp']}")
                
                # Quick actions
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"🔗 Visit Article", key=f"visit_{feedback['id']}"):
                        st.markdown(f"[Open Article]({feedback['url']})")
                
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
        
        # Download button
        st.download_button(
            label="📥 Download Text Log",
            data=content,
            file_name=f"feedback_log_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
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
        
        # CSV export
        df = pd.DataFrame(feedback_list)
        csv = df.to_csv(index=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📊 Download as CSV",
                data=csv,
                file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON export
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="🔧 Download as JSON",
                data=json_str,
                file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        # Preview the data
        st.markdown("**Data Preview:**")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error preparing export: {str(e)}")


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