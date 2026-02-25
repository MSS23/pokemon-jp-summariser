"""
Sidebar rendering and feedback form for the Pokemon VGC Analysis Platform.
Extracted from components.py for maintainability.
"""

import streamlit as st
from typing import Dict, Any
from datetime import datetime


def render_sidebar():
    """Clean and user-friendly sidebar with essential navigation"""
    with st.sidebar:
        # Clean sidebar header
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; margin: -1rem -1rem 1.5rem -1rem; border-radius: 0 0 15px 15px;">
                <h2 style="color: white; margin: 0; text-align: center; font-size: 1.5rem;">
                    ⚔️ VGC Analyzer
                </h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center; font-size: 0.95rem;">
                    Pokemon Team Analysis
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Clean navigation
        page = st.selectbox(
            "**Navigate to:**",
            [
                "🏠 Analysis Home",
                "🎮 Switch Translation",
                "⚙️ Settings",
                "📖 Help & Guide"
            ],
            index=0
        )
        
        st.markdown("---")
        
        # Essential actions only
        if st.button("🆕 New Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_result = None
            st.session_state.current_url = None
            st.session_state.analysis_complete = False
            st.rerun()
        
        # Current analysis status (only if available)
        if st.session_state.get("analysis_result"):
            st.markdown("---")
            result = st.session_state.analysis_result
            pokemon_count = len(result.get("pokemon_team", []))
            regulation = result.get("regulation", "Unknown")
            
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                           padding: 1rem; border-radius: 10px; border-left: 4px solid #0ea5e9; margin: 0.5rem 0;">
                    <div style="font-size: 0.9rem; color: #0f172a;">
                        <strong>📊 Current Team</strong><br>
                        🏆 {pokemon_count} Pokemon<br>
                        📋 Regulation {regulation}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Minimal about section
        st.markdown("---")
        st.markdown(
            """
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; text-align: center;">
                <small style="color: #64748b;">
                    <strong>✨ VGC Analysis Tool</strong><br>
                    Powered by Google Gemini 2.5<br><br>
                    🎯 Instant Japanese Translation<br>
                    📊 Professional Team Analysis<br>
                    📋 Export Ready Formats
                </small>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Feedback Section
        st.markdown("---")
        with st.expander("📝 **Report Issue**", expanded=False):
            st.markdown("**Help us improve!** Report analysis issues with specific examples.")
            st.markdown("<small>Both URL and detailed description are required. Feedback is logged for developer review.</small>", unsafe_allow_html=True)
            
            # URL Input with validation
            feedback_url = st.text_input(
                "Article URL *", 
                value=st.session_state.feedback_url,
                placeholder="https://liberty-note.com/article-url",
                help="Paste the URL of the article that had analysis issues",
                key="feedback_url_input"
            )
            
            # Real-time URL validation
            url_valid = feedback_url and (feedback_url.startswith("http://") or feedback_url.startswith("https://"))
            if feedback_url and not url_valid:
                st.markdown("❌ <small style='color: #ef4444;'>Please enter a valid URL starting with http:// or https://</small>", unsafe_allow_html=True)
            elif url_valid:
                st.markdown("✅ <small style='color: #22c55e;'>Valid URL format</small>", unsafe_allow_html=True)
            
            # Problem category
            problem_type = st.selectbox(
                "Issue Type",
                ["Analysis Quality", "Missing Pokemon", "Wrong Strategy", "Translation Error", "App Bug", "Other"],
                help="Select the category that best describes your issue"
            )
            
            # Problem description with validation
            feedback_description = st.text_area(
                "Describe the Problem *",
                value=st.session_state.feedback_description,
                placeholder="Please describe exactly what was wrong with the analysis. Be specific about what you expected vs what you got. Example: 'The analysis said the team had 5 Pokemon but I counted 6, and it missed the Garchomp completely.'",
                help="Minimum 20 characters required. The more detail, the better we can help!",
                key="feedback_description_input",
                height=80
            )
            
            # Real-time description validation
            description_valid = feedback_description and len(feedback_description.strip()) >= 20
            current_length = len(feedback_description.strip()) if feedback_description else 0
            
            if feedback_description:
                if description_valid:
                    st.markdown(f"✅ <small style='color: #22c55e;'>{current_length} characters (minimum met)</small>", unsafe_allow_html=True)
                else:
                    remaining = 20 - current_length
                    st.markdown(f"❌ <small style='color: #ef4444;'>{current_length}/20 characters (need {remaining} more)</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small style='color: #6b7280;'>0/20 characters</small>", unsafe_allow_html=True)
            
            # Update session state
            st.session_state.feedback_url = feedback_url
            st.session_state.feedback_description = feedback_description
            
            # Submission button with validation
            can_submit = url_valid and description_valid
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📤 Submit Feedback", 
                           disabled=not can_submit,
                           use_container_width=True,
                           type="primary" if can_submit else "secondary"):
                    
                    # Submit the feedback
                    success = log_user_feedback(feedback_url, problem_type, feedback_description)
                    
                    if success:
                        st.session_state.feedback_submitted = True
                        st.success("✅ Feedback submitted successfully!")
                        st.info("📝 Your feedback has been recorded and will be reviewed by the development team.")
                        st.info("🙏 Thank you for helping us improve the analysis quality!")
                        
                        # Clear the form
                        st.session_state.feedback_url = ""
                        st.session_state.feedback_description = ""
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit feedback. Please try again.")
            
            with col2:
                if st.button("🗑️ Clear Form", use_container_width=True):
                    st.session_state.feedback_url = ""
                    st.session_state.feedback_description = ""
                    st.rerun()
            
            # Show submission requirements if form is incomplete
            if not can_submit:
                st.markdown("---")
                st.markdown("<small>**Requirements to submit:**</small>", unsafe_allow_html=True)
                url_icon = "✅" if url_valid else "❌"
                desc_icon = "✅" if description_valid else "❌"
                st.markdown(f"<small>{url_icon} Valid article URL</small>", unsafe_allow_html=True)
                st.markdown(f"<small>{desc_icon} Problem description (20+ characters)</small>", unsafe_allow_html=True)
        
        # Add session reset section
        st.markdown("---")
        st.markdown("**🛠️ Troubleshooting**")
        
        if st.button("🔄 Reset Session", 
                    use_container_width=True, 
                    help="Clear current analysis results and reset the application."):
            
            # Clear session state
            st.session_state.clear()
            
            # Show success message
            st.success("✅ Session reset complete!")
            st.info("📝 The page will refresh to start fresh.")
            
            # Force rerun to reset everything
            st.rerun()
        
        return page


def render_image_analysis_section(analysis_result: Dict[str, Any]):
    """Render consumer-friendly image analysis insights"""
    image_analysis = analysis_result.get("image_analysis")
    
    if not image_analysis or not image_analysis.get("success", False):
        return
        
    # Count total EV spreads found across all images
    total_ev_spreads = 0
    image_analyses = image_analysis.get("image_analyses", [])
    
    for img_analysis in image_analyses:
        total_ev_spreads += len(img_analysis.get("ev_spreads", []))
    
    # Only show if we found additional EV data from images
    if total_ev_spreads > 0:
        st.success(f"🎯 Enhanced Analysis: Found {total_ev_spreads} additional EV spread{'s' if total_ev_spreads != 1 else ''} from team images!")
        
        # Show the EV spreads in a clean format
        with st.expander("📊 View Additional EV Spreads", expanded=False):
            for i, img_analysis in enumerate(image_analyses):
                ev_spreads = img_analysis.get("ev_spreads", [])
                if ev_spreads:
                    st.write(f"**From Image {i+1}:**")
                    for j, ev_spread in enumerate(ev_spreads):
                        spread_format = ev_spread.get('format', 'Unknown')
                        st.code(f"{spread_format} (Total: {ev_spread.get('total', 'Unknown')} EVs)")
                    st.divider()
    else:
        # Just show a subtle indicator that image analysis was performed
        st.info("🔍 Team images analyzed for additional details")


