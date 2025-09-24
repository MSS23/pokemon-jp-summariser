"""
Pokemon VGC Article Translator - Streamlit Frontend
Compliant with Google Gemini API Terms & Generative AI Policy
Features: 18+ age gate, backend proxy, provider status monitoring
"""

import streamlit as st
import requests
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"  # FastAPI backend URL
AGE_VERIFICATION_EXPIRY_HOURS = 24
SESSION_COOKIE_NAME = "pokemon_vgc_session"

# Set page configuration
st.set_page_config(
    page_title="Pokemon VGC Article Translator",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': 'mailto:support@example.com',
        'About': "Pokemon VGC Article Translator - Compliant AI-powered analysis for Pokemon competitive content"
    }
)

def generate_session_id() -> str:
    """Generate a unique session ID"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def check_backend_health() -> Dict[str, Any]:
    """
    Check if backend is available and get provider status
    """
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}

def is_age_verified() -> bool:
    """
    Check if user has verified they are 18+ within the last 24 hours
    Uses both session state and browser cookies for persistence
    """
    # Check session state first (faster)
    if st.session_state.get("age_verified"):
        verification_time = st.session_state.get("age_verification_time")
        if verification_time:
            hours_since = (datetime.now() - verification_time).total_seconds() / 3600
            if hours_since < AGE_VERIFICATION_EXPIRY_HOURS:
                return True

    # Check query params for cookie-like persistence (Streamlit limitation workaround)
    query_params = st.query_params
    if query_params.get("age_verified") == "true":
        verification_timestamp = query_params.get("age_timestamp")
        if verification_timestamp:
            try:
                verification_time = datetime.fromtimestamp(float(verification_timestamp))
                hours_since = (datetime.now() - verification_time).total_seconds() / 3600
                if hours_since < AGE_VERIFICATION_EXPIRY_HOURS:
                    # Update session state
                    st.session_state.age_verified = True
                    st.session_state.age_verification_time = verification_time
                    return True
            except (ValueError, TypeError):
                pass

    return False

def set_age_verified():
    """
    Mark user as age verified in session and create persistent link
    """
    verification_time = datetime.now()
    st.session_state.age_verified = True
    st.session_state.age_verification_time = verification_time

    # Create URL with verification params for persistence
    current_time = int(verification_time.timestamp())
    verification_url = f"?age_verified=true&age_timestamp={current_time}"

    st.success("✅ Age verification complete! You can bookmark this URL to avoid re-verification for 24 hours.")
    st.info(f"📌 **Bookmark this link**: {st.secrets.get('app_url', 'your-app-url')}{verification_url}")

def show_age_gate():
    """
    Display 18+ age verification modal
    """
    st.markdown("---")

    # Age gate styling
    st.markdown("""
        <div style="
            background-color: #f0f2f6;
            border: 2px solid #ff6b6b;
            border-radius: 10px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
        ">
            <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🔞 Age Verification Required</h2>
            <p style="font-size: 1.1em; margin-bottom: 1rem;">
                This application uses AI services that require users to be 18 or older in compliance
                with Google's Generative AI terms and content policies.
            </p>
            <p style="margin-bottom: 1.5rem;">
                By continuing, you confirm that you are at least 18 years of age.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🔓 I am 18 or older - Continue", type="primary", use_container_width=True):
            set_age_verified()
            st.rerun()

        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: #666; font-size: 0.9em;">
                <p><strong>Why is age verification required?</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Compliance with Google Gemini API Additional Terms</li>
                    <li>Protection of minors from AI-generated content</li>
                    <li>Adherence to Generative AI Prohibited Use Policy</li>
                    <li>Legal requirements for AI service usage</li>
                </ul>
                <p style="margin-top: 1rem;">
                    <strong>Privacy:</strong> Your age verification is stored locally only and expires after 24 hours.
                </p>
            </div>
        """, unsafe_allow_html=True)

def make_backend_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Make a request to the FastAPI backend with proper error handling

    Args:
        endpoint: API endpoint (e.g., "/check", "/analyze")
        method: HTTP method ("GET", "POST")
        data: Request data for POST requests

    Returns:
        Tuple of (success, response_data)
    """
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "X-Session-ID": generate_session_id()
        }

        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=120)  # Longer timeout for analysis
        else:
            return False, {"error": f"Unsupported method: {method}"}

        if response.status_code == 200:
            return True, response.json()
        else:
            try:
                error_data = response.json()
                return False, error_data
            except:
                return False, {"error": f"HTTP {response.status_code}: {response.text}"}

    except requests.exceptions.Timeout:
        return False, {"error": "Request timeout - the backend may be overloaded"}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend - please check if the API server is running"}
    except Exception as e:
        return False, {"error": f"Request failed: {str(e)}"}

def render_provider_status_banner(health_data: Dict[str, Any]):
    """
    Render provider status banner at the top of the page
    """
    if not health_data.get("provider_enabled", False):
        st.error("🚫 **AI Analysis Temporarily Disabled** - The Gemini AI provider is currently disabled. Analysis features are unavailable.")
        st.info("💡 You can still use the URL compliance checker to validate Pokemon community sites.")
        return False

    if not health_data.get("gemini_available", False):
        st.warning("⚠️ **AI Service Issues** - There may be issues with the AI analysis service. Some features may be limited.")
        return False

    if health_data.get("status") != "healthy":
        st.warning("⚠️ **Service Status** - Backend service status is not optimal. Analysis may be slower than usual.")

    return True

def render_compliance_info():
    """
    Render compliance and policy information panel
    """
    with st.expander("📋 Compliance & Policy Information", expanded=False):
        st.markdown("""
        ### 🔒 Content Safety & Compliance

        This application is fully compliant with:
        - **Google Gemini API Additional Terms**
        - **Google APIs Terms of Service**
        - **Generative AI Prohibited Use Policy**
        - **COPPA** (18+ age verification required)
        - **Website robots.txt policies**

        ### 🛡️ Safety Features
        - ✅ **Age Gate**: 18+ verification required
        - ✅ **Domain Allowlist**: Only approved Pokemon community sites
        - ✅ **robots.txt Compliance**: Respects website crawling policies
        - ✅ **Content Filtering**: Pokemon VGC content scope only
        - ✅ **Rate Limiting**: 5 analyses per hour per user
        - ✅ **PII Protection**: Automatic redaction of personal information
        - ✅ **Server-side API Keys**: Never exposed to your browser

        ### 📊 How It Works
        1. **URL Validation**: Checks domain allowlist and robots.txt
        2. **Content Safety**: Validates Pokemon VGC scope and filters prohibited content
        3. **Secure Processing**: All AI requests handled server-side only
        4. **Structured Logging**: Full compliance audit trail maintained

        ### 🚨 Report Misuse
        If you encounter inappropriate content or misuse, please report it:
        **[Report Issues](mailto:support@example.com)**
        """)

def render_url_input() -> Optional[str]:
    """
    Render URL input field with validation
    """
    st.markdown("### 🔗 Pokemon VGC Article URL")

    url = st.text_input(
        "Enter the URL of a Pokemon VGC article or team showcase:",
        placeholder="https://note.com/example/pokemon-vgc-team-2024",
        help="Only URLs from approved Pokemon community sites are allowed"
    )

    if url and url.strip():
        # Basic URL format validation
        if not url.startswith(('http://', 'https://')):
            st.error("❌ Please enter a valid URL starting with http:// or https://")
            return None

        return url.strip()

    return None

def render_check_results(check_data: Dict[str, Any]):
    """
    Render URL compliance check results
    """
    st.markdown("### ✅ Compliance Check Results")

    if check_data["status"] == "allowed":
        st.success("🟢 **All compliance checks passed!** This URL is safe to analyze.")

        # Show detailed compliance info
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Domain Status", "✅ Approved")
            st.metric("robots.txt", "✅ Allowed" if check_data.get("robots_allowed") else "❓ Unknown")

        with col2:
            st.metric("Content Type", check_data.get("content_type", "Unknown"))
            st.metric("Size Estimate", check_data.get("size_estimate", "Unknown"))

    else:
        st.error(f"🔴 **Compliance Check Failed**: {check_data['reason']}")

        # Show which step failed
        failed_step = check_data.get("step_failed")
        if failed_step:
            st.info(f"**Failed at**: {failed_step}")

        # Show domain info if available
        domain = check_data.get("domain")
        if domain:
            st.info(f"**Domain**: {domain}")

        # Provide guidance
        st.markdown("""
        **Why was this blocked?**
        - Only approved Pokemon community sites are allowed
        - The website's robots.txt may disallow crawling
        - Content may be behind a paywall or login wall
        - The link may not point to HTML content

        **Try instead:**
        - Use official Pokemon community sites (note.com, smogon.com, etc.)
        - Ensure the content is publicly accessible
        - Copy and paste the article text directly if the URL doesn't work
        """)

def render_analysis_results(analysis_data: Dict[str, Any]):
    """
    Render analysis results with metadata
    """
    st.markdown("### 🎯 Analysis Results")

    if analysis_data["status"] == "success":
        analysis = analysis_data["analysis"]
        metadata = analysis_data["metadata"]

        # Show processing metadata
        with st.expander("📊 Processing Information", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Original Size", f"{metadata['original_size']:,} bytes")
                st.metric("Processed Size", f"{metadata['processed_size']:,} chars")

            with col2:
                st.metric("Processing Time", f"{metadata['processing_time']:.2f}s")
                redaction_stats = metadata.get("redaction_stats", {})
                total_redactions = redaction_stats.get("total_redactions", 0)
                st.metric("PII Redactions", total_redactions)

            with col3:
                st.metric("Domain", metadata["domain"])
                st.metric("robots.txt", "✅ Allowed" if metadata["robots_allowed"] else "❌ Blocked")

        # Show analysis content
        if "title" in analysis:
            st.markdown(f"**Title:** {analysis['title']}")

        if "regulation" in analysis:
            st.markdown(f"**Regulation:** {analysis['regulation']}")

        # Pokemon team
        if "pokemon_team" in analysis and analysis["pokemon_team"]:
            st.markdown("#### 🎮 Pokemon Team")

            for i, pokemon in enumerate(analysis["pokemon_team"]):
                with st.expander(f"{i+1}. {pokemon.get('name', 'Unknown Pokemon')}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Item:** {pokemon.get('item', 'None')}")
                        st.write(f"**Ability:** {pokemon.get('ability', 'Unknown')}")
                        st.write(f"**Nature:** {pokemon.get('nature', 'Unknown')}")

                    with col2:
                        ev_spread = pokemon.get('ev_spread', {})
                        if ev_spread:
                            st.write("**EV Spread:**")
                            for stat, value in ev_spread.items():
                                if value > 0:
                                    st.write(f"- {stat}: {value}")

                    moves = pokemon.get('moves', [])
                    if moves:
                        st.write(f"**Moves:** {', '.join(moves)}")

                    analysis_text = pokemon.get('analysis', '')
                    if analysis_text:
                        st.write(f"**Analysis:** {analysis_text}")

        # Strategy summary
        if "strategy_summary" in analysis:
            st.markdown("#### 🧠 Strategy Summary")
            st.write(analysis["strategy_summary"])

        # Key interactions
        if "key_interactions" in analysis:
            st.markdown("#### ⚡ Key Interactions")
            st.write(analysis["key_interactions"])

        # Tournament results
        if "tournament_results" in analysis:
            st.markdown("#### 🏆 Tournament Results")
            st.write(analysis["tournament_results"])

        # Export options
        st.markdown("#### 💾 Export")
        export_col1, export_col2 = st.columns(2)

        with export_col1:
            if st.button("📋 Copy JSON"):
                st.code(json.dumps(analysis, indent=2, ensure_ascii=False), language="json")

        with export_col2:
            if st.button("🔗 Generate Pokepaste"):
                st.info("Pokepaste generation feature coming soon!")

    else:
        st.error(f"❌ **Analysis Failed**: {analysis_data.get('detail', 'Unknown error')}")

def main():
    """
    Main application entry point
    """
    # Generate session ID
    session_id = generate_session_id()

    # Check backend health
    health_data = check_backend_health()

    # Page header
    st.title("⚔️ Pokemon VGC Article Translator")
    st.markdown("AI-powered analysis and translation of Japanese Pokemon VGC content")

    # Provider status banner
    provider_available = render_provider_status_banner(health_data)

    # Age gate check
    if not is_age_verified():
        show_age_gate()
        return  # Stop here until age is verified

    # Compliance info panel
    render_compliance_info()

    # Report misuse link (prominent)
    st.markdown("🚨 [**Report Misuse or Issues**](mailto:support@example.com)")

    st.markdown("---")

    # Main functionality
    url = render_url_input()

    if url:
        # URL compliance check
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("🔍 Check URL Compliance", type="secondary", use_container_width=True):
                with st.spinner("Checking URL compliance..."):
                    success, check_data = make_backend_request("/check", "POST", {"url": url})

                if success:
                    st.session_state.last_check_result = check_data
                    st.session_state.last_checked_url = url
                else:
                    st.error(f"❌ Check failed: {check_data.get('error', 'Unknown error')}")

        with col2:
            # Only show analyze button if provider is available and URL passes checks
            can_analyze = (
                provider_available and
                st.session_state.get("last_check_result", {}).get("status") == "allowed" and
                st.session_state.get("last_checked_url") == url
            )

            analyze_button_text = "🤖 Analyze with AI" if can_analyze else "🤖 Analyze (Check URL First)"

            if st.button(analyze_button_text, type="primary", disabled=not can_analyze, use_container_width=True):
                if not can_analyze:
                    st.warning("⚠️ Please run URL compliance check first and ensure it passes")
                else:
                    with st.spinner("Analyzing content... This may take up to 2 minutes."):
                        success, analysis_data = make_backend_request(
                            "/analyze",
                            "POST",
                            {"url": url, "options": {}}
                        )

                    if success:
                        st.session_state.last_analysis_result = analysis_data
                    else:
                        error_detail = analysis_data.get("detail", "Unknown error")

                        # Handle specific error types
                        if "rate limit" in error_detail.lower():
                            st.error("⏱️ **Rate Limit Reached**: You've reached the maximum of 5 analyses per hour. Please try again later.")
                            st.info("💡 **Tip**: Rate limits reset automatically after 1 hour.")
                        elif "provider_disabled" in str(analysis_data):
                            st.error("🚫 **AI Service Disabled**: The Gemini AI service is currently disabled.")
                        elif "concurrent" in error_detail.lower():
                            st.error("⚠️ **Too Many Requests**: Please wait for your current analysis to complete.")
                        else:
                            st.error(f"❌ Analysis failed: {error_detail}")

    # Show previous results
    if "last_check_result" in st.session_state:
        render_check_results(st.session_state.last_check_result)

    if "last_analysis_result" in st.session_state:
        render_analysis_results(st.session_state.last_analysis_result)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8em;">
            <p>Pokemon VGC Article Translator v2.0 - Compliant with Google Gemini API Terms</p>
            <p>Built with ❤️ for the Pokemon VGC community |
               <a href="https://github.com/your-org/pokemon-vgc-translator">Open Source</a> |
               <a href="mailto:support@example.com">Report Issues</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()