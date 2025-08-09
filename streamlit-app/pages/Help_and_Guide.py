# pages/Help_and_Guide.py
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Help & Guide - Pokémon VGC Summariser",
    page_icon="📚",
    layout="wide"
)

# Import navigation component
try:
    from components.navigation import show_navigation
    show_navigation(current_page='Help & Guide')
except ImportError:
    st.warning("Navigation component not available.")

# Add custom CSS for help cards
st.markdown("""
<style>
.help-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.help-card h3 {
    color: #2d3748;
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.25rem;
    font-weight: 600;
}

.help-card p {
    color: #4a5568;
    line-height: 1.6;
    margin-bottom: 1rem;
}

.help-card ul, .help-card ol {
    color: #4a5568;
    line-height: 1.6;
    padding-left: 1.5rem;
}

.help-card li {
    margin-bottom: 0.5rem;
}

.help-card strong {
    color: #2d3748;
    font-weight: 600;
}

.keyboard-shortcut {
    background: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 0.25rem 0.5rem;
    font-family: monospace;
    font-size: 0.875rem;
    color: #4a5568;
}

.gradient-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
    padding: 2rem;
    margin-bottom: 2rem;
    text-align: center;
}

.gradient-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    color: white;
}

.gradient-header p {
    font-size: 1rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="gradient-header">
    <h1>📚 Help & Guide</h1>
    <p>Learn how to use the Pokémon VGC Summariser effectively</p>
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
        <li><strong>👤 User Profile</strong> - Manage your account and view personal statistics</li>
        <li><strong>🤖 Model Selection</strong> - Configure AI model settings and preferences</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Keyboard Shortcuts
st.markdown("""
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
        <li><strong>HTML Tags in Output</strong> - The app automatically strips HTML tags, but if you see any, try refreshing</li>
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
