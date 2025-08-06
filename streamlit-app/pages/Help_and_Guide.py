# pages/Help_and_Guide.py
import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.auth import auth_manager
    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Help & Guide - Pokémon VGC Summariser",
    page_icon="📚",
    layout="wide"
)

# --- NAVIGATION & SIDEBAR STRUCTURE UPDATED: Unified navigation bar and fixed sidebar ---
try:
    from components.navigation import show_navigation
except ImportError:
    def show_navigation(*args, **kwargs):
        st.warning("Navigation component missing.")
current_user = auth_manager.get_current_user() if AUTH_AVAILABLE and 'auth_manager' in globals() else None
show_navigation(current_page='Help & Guide', authenticated=bool(current_user))

# --- Fixed Sidebar: Single Block Pattern ---
def show_fixed_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding:0.5rem 0;'>
            <h2 style='margin:0; font-size:1.25rem;'>⚡ Pokémon VGC Summariser</h2>
            <hr style='margin:0.5rem 0 1rem 0;'/>
        </div>
        """, unsafe_allow_html=True)
        st.info("Quick Actions:")
        nav = st.radio(
            "Go to:",
            [
                "🏠 Main Summariser",
                "🔍 Team Search",
                "📊 Analytics Dashboard",
                "📖 Help & Guide"
            ],
            index=3,  # Set default index for current page
            label_visibility="collapsed"
        )
        st.markdown("---")
        st.markdown("**Tip:** Use the navigation bar above to explore all features!")
        st.markdown("---")
        st.markdown("**Feedback?** Reach out via the Help & Guide page.")
    return nav

show_fixed_sidebar()

# --- Fixed Sidebar CSS & JS ---
st.markdown("""
<style>
    /* Fixed Sidebar styling */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        overflow-y: auto !important;
        z-index: 1000 !important;
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1) !important;
    }
    [data-testid="stSidebar"] > div {
        height: 100% !important;
        overflow-y: auto !important;
        padding: 1rem !important;
    }
    .main .block-container {
        margin-left: 320px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: none !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important;
        top: 1rem !important;
        left: 310px !important;
        z-index: 1001 !important;
        background: #667eea !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
    }
    .css-1d391kg {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 300px !important;
        z-index: 1000 !important;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stButton,
    [data-testid="stSidebar"] .stInfo {
        margin-bottom: 1rem !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 0.5rem !important;
        background: #667eea !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #5a67d8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3) !important;
    }
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            position: fixed !important;
            top: 0 !important;
            left: -300px !important;
            width: 280px !important;
            min-width: 280px !important;
            max-width: 280px !important;
            transition: left 0.3s ease !important;
            z-index: 2000 !important;
        }
        [data-testid="stSidebar"].sidebar-open {
            left: 0 !important;
        }
        .main .block-container {
            margin-left: 0 !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            position: fixed !important;
            top: 1rem !important;
            left: 1rem !important;
            z-index: 2001 !important;
        }
    }
</style>
<script>
// Mobile sidebar functionality
function initMobileSidebar() {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const toggleButton = document.querySelector('[data-testid="stSidebarCollapseButton"]');
    if (sidebar && toggleButton) {
        // Handle sidebar toggle
        toggleButton.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('sidebar-open');
            }
        });
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768 && 
                !sidebar.contains(e.target) && 
                !toggleButton.contains(e.target) &&
                sidebar.classList.contains('sidebar-open')) {
                sidebar.classList.remove('sidebar-open');
            }
        });
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                sidebar.classList.remove('sidebar-open');
            }
        });
    }
}
window.addEventListener('load', initMobileSidebar);
document.addEventListener('DOMContentLoaded', initMobileSidebar);
</script>
""", unsafe_allow_html=True)



# Main content
st.markdown("""
<div style="text-align: center; margin-bottom: 3rem; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white; margin: -1rem -1rem 3rem -1rem;">
    <h1 style="font-size: 2.2rem; font-weight: 700; margin: 0; color: white;">📚 Help & Guide</h1>
    <p style="font-size: 1rem; margin: 0.5rem 0 0 0; opacity: 0.9; color: white;">Learn how to use the Pokémon VGC Summariser effectively</p>
</div>
""", unsafe_allow_html=True)

# Getting Started
st.markdown("""
<div class="help-card">
    <h3>🚀 Getting Started</h3>
    <p>The Pokémon VGC Summariser helps you translate and analyze Japanese Pokémon VGC articles. Here's how to get started:</p>
    <ol>
        <li><strong>Find a Japanese Pokémon article</strong> - Look for VGC team reports, strategy guides, or tournament coverage</li>
        <li><strong>Copy the URL</strong> - Make sure it starts with http:// or https://</li>
        <li><strong>Paste it in the Main Summariser</strong> - The tool will automatically detect if it's cached</li>
        <li><strong>Click Summarise</strong> - Google Gemini AI will translate and analyze the content</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# Features Overview
st.markdown("""
<div class="help-card">
    <h3>✨ Features Overview</h3>
    <ul>
        <li><strong>🏠 Main Summariser</strong> - Translate Japanese articles into detailed English summaries</li>
        <li><strong>🔍 Team Search</strong> - Search through cached summaries to find specific Pokémon teams</li>
        <li><strong>📊 Analytics Dashboard</strong> - View trending Pokémon and usage statistics (requires login)</li>
        <li><strong>👤 User Profile</strong> - Manage your account and view personal statistics (requires login)</li>
        <li><strong>🤖 Model Selection</strong> - Configure AI model settings and preferences</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Keyboard Shortcuts
st.markdown(f"""
<div class="help-card">
    <h3>⌨️ Keyboard Shortcuts</h3>
    <ul>
        <li><span class="keyboard-shortcut">Ctrl + Enter</span> - Trigger summarization on the main page</li>
        <li><span class="keyboard-shortcut">Ctrl + K</span> - Focus the URL input field</li>
        <li><span class="keyboard-shortcut">Escape</span> - Clear input fields</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Supported Sources
st.markdown("""
<div class="help-card">
    <h3>🌐 Supported Sources</h3>
    <p>The summariser works best with these types of Japanese Pokémon content:</p>
    <ul>
        <li><strong>VGC Team Reports</strong> - Detailed team analyses and tournament reports</li>
        <li><strong>Strategy Guides</strong> - In-depth Pokémon strategy discussions</li>
        <li><strong>Tournament Coverage</strong> - Event summaries and player interviews</li>
        <li><strong>Blog Posts</strong> - Personal experiences and team building guides</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Export Options
st.markdown("""
<div class="help-card">
    <h3>💾 Export Options</h3>
    <p>After generating a summary, you can export it in multiple formats:</p>
    <ul>
        <li><strong>📄 Detailed Text</strong> - Complete summary with all details and metadata</li>
        <li><strong>📝 Compact Text</strong> - Key information only (titles, Pokémon, abilities, moves)</li>
        <li><strong>🔧 JSON Data</strong> - Structured data format for developers</li>
        <li><strong>📊 CSV Team List</strong> - Simple spreadsheet format with Pokémon data</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Tips and Tricks
st.markdown("""
<div class="help-card">
    <h3>💡 Tips and Tricks</h3>
    <ul>
        <li><strong>Cache System</strong> - Previously summarized articles load instantly</li>
        <li><strong>Search Multiple Terms</strong> - Use commas to search for multiple Pokémon at once</li>
        <li><strong>Quick Pokémon Lookup</strong> - Click any Pokémon in the grid for instant team results</li>
        <li><strong>Recent Searches</strong> - Your recent searches are saved for quick access</li>
        <li><strong>Mobile Friendly</strong> - The app works great on phones and tablets</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Troubleshooting
st.markdown("""
<div class="help-card">
    <h3>🔧 Troubleshooting</h3>
    <p>If you encounter issues:</p>
    <ul>
        <li><strong>Invalid URL Error</strong> - Make sure the URL starts with http:// or https://</li>
        <li><strong>Summarization Fails</strong> - Try refreshing the page and trying again</li>
        <li><strong>Empty Results</strong> - The article might not contain Pokémon team information</li>
        <li><strong>Slow Loading</strong> - Large articles may take longer to process</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Contact and Support
st.markdown("""
<div class="help-card">
    <h3>📞 Need More Help?</h3>
    <p>If you need additional assistance or have suggestions for improvement, feel free to reach out through the feedback options in the app.</p>
    <p><strong>Remember:</strong> This tool is designed to help you understand Japanese Pokémon content more easily. The AI does its best to provide accurate translations, but always verify important details when possible.</p>
</div>
""", unsafe_allow_html=True)
