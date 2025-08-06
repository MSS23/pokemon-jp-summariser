"""
LLM Model Selection Page
Allows users to choose between different LLM models for Pokémon article summarization
"""

import streamlit as st
import json
import os
from pathlib import Path

# Import LLM functions
try:
    from utils.llm_summary import llm_summary
    from utils.ollama_summary import (
        llm_summary_ollama, 
        get_available_ollama_models, 
        check_ollama_installation,
        install_ollama_model
    )
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Cache path
CACHE_PATH = Path("storage/cache.json")

st.set_page_config(
    page_title="LLM Model Selection - Pokémon Translator",
    page_icon="🤖",
    layout="wide"
)

# Modern CSS styling
st.markdown("""
<style>
    .stApp {
        background: #fafbfc !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    .main {
        background: #fafbfc !important;
        padding: 2rem 1rem !important;
    }
    
    .page-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        color: white;
        margin: -1rem -1rem 3rem -1rem;
    }
    
    .page-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: white !important;
    }
    
    .page-header p {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: white !important;
    }
    
    .content-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        border: 1px solid #e1e5e9;
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .comparison-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .model-card {
        background: #f8fafc;
        border: 2px solid #e1e5e9;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .model-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
    }
    
    .model-card h3 {
        color: #1a202c !important;
        margin: 0 0 1rem 0 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    .model-card ul {
        color: #4a5568 !important;
        margin: 0 !important;
        padding-left: 1.2rem !important;
        line-height: 1.6 !important;
    }
    
    .requirements-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .requirement-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
    }
    
    .requirement-card h3 {
        color: #1a202c !important;
        margin: 0 0 1rem 0 !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .requirement-card ul {
        color: #4a5568 !important;
        margin: 0 !important;
        padding-left: 1.2rem !important;
        line-height: 1.6 !important;
    }
    
    [data-testid="stSidebar"] {
        background: white !important;
        border-right: 1px solid #e1e5e9 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #1a202c !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.875rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #e1e5e9 !important;
        border-radius: 8px !important;
        padding: 0.875rem 1rem !important;
        font-size: 1rem !important;
        background: white !important;
        color: #1a202c !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="success"] {
        background: #f0fff4 !important;
        border-left-color: #48bb78 !important;
        color: #2f855a !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="info"] {
        background: #ebf8ff !important;
        border-left-color: #4299e1 !important;
        color: #2b6cb0 !important;
    }
    
    .stAlert[data-baseweb="notification"][kind="error"] {
        background: #fed7d7 !important;
        border-left-color: #f56565 !important;
        color: #c53030 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    @media (max-width: 768px) {
        .comparison-grid {
            grid-template-columns: 1fr;
        }
        
        .requirements-grid {
            grid-template-columns: 1fr;
        }
        
        .page-header h1 {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
# (Removed stray header opening, moved actual header to Model Selection block below)

show_fixed_sidebar()

# Header
st.markdown("""
    <div class="page-header">
        <h1>🤖 LLM Model Selection</h1>
        <p>Choose the best AI model for your Pokémon translation needs</p>
    </div>
    """, unsafe_allow_html=True)

    # Model type selection
    model_type = st.selectbox(
        "Select LLM Provider",
        ["Google Gemini (Cloud)", "Ollama (Local)"],
        help="Choose between cloud-based Gemini or local Ollama models"
    )
    
    if model_type == "Google Gemini (Cloud)":
        st.info("🌐 **Google Gemini 2.0 Flash**")
        st.markdown("""
        **Pros:**
        - ✅ Excellent Japanese → English translation
        - ✅ Image processing capabilities
        - ✅ No setup required
        - ✅ Generous free tier (1500 requests/day)
        
        **Cons:**
        - ❌ Requires API key
        - ❌ Internet dependency
        - ❌ Potential rate limits
        """)
        
        # Check if API key is configured
        try:
            from utils.config_loader import load_config
            secrets = load_config()
            if "google_api_key" in secrets and secrets["google_api_key"]:
                st.success("✅ API Key configured")
            else:
                st.error("❌ API Key not found")
                st.markdown("Add your Google Gemini API key to `.streamlit/secrets.toml`")
        except:
            st.error("❌ Configuration error")
    
    elif model_type == "Ollama (Local)":
        st.info("🏠 **Ollama Local Models**")
        st.markdown("""
        **Pros:**
        - ✅ Completely free (no API costs)
        - ✅ No internet required after setup
        - ✅ No rate limits
        - ✅ Privacy (data stays local)
        
        **Cons:**
        - ❌ Requires local installation
        - ❌ Needs sufficient RAM/GPU
        - ❌ Initial model download time
        """)
        
        # Check Ollama installation
        if OLLAMA_AVAILABLE:
            if check_ollama_installation():
                st.success("✅ Ollama installed")
                
                # Model selection
                available_models = get_available_ollama_models()
                selected_model = st.selectbox(
                    "Select Ollama Model",
                    available_models,
                    help="Choose based on your hardware capabilities"
                )
                
                # Model recommendations
                if "3b" in selected_model:
                    st.info("💡 **Lightweight**: Good for basic tasks, fast processing")
                elif "7b" in selected_model:
                    st.info("⚖️ **Balanced**: Good quality-speed trade-off")
                elif "14b" in selected_model or "70b" in selected_model:
                    st.warning("🚀 **Heavy**: Best quality but requires more RAM/GPU")
                
                # Install model button
                if st.button("📥 Install Selected Model"):
                    with st.spinner(f"Installing {selected_model}..."):
                        if install_ollama_model(selected_model):
                            st.success(f"✅ {selected_model} installed successfully!")
                        else:
                            st.error(f"❌ Failed to install {selected_model}")
            else:
                st.error("❌ Ollama not installed")
                st.markdown("""
                **Installation Instructions:**
                1. Visit [ollama.ai](https://ollama.ai)
                2. Download and install Ollama
                3. Restart this app
                """)
        else:
            st.error("❌ Ollama dependencies not installed")
            st.markdown("Run: `pip install langchain-ollama`")

# Main content area
st.header("Model Comparison")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Cloud Models")
    st.markdown("""
    **Google Gemini 2.0 Flash**
    - **Cost**: Free tier (1500 requests/day)
    - **Quality**: Excellent for Japanese translation
    - **Speed**: Fast
    - **Setup**: API key required
    - **Best for**: Production use, high accuracy
    """)

with col2:
    st.subheader("🏠 Local Models")
    st.markdown("""
    **Ollama Models**
    - **Cost**: Completely free
    - **Quality**: Good to excellent (depends on model)
    - **Speed**: Variable (depends on hardware)
    - **Setup**: Local installation required
    - **Best for**: Privacy, unlimited usage
    """)

# Model recommendations based on use case
st.header("🎯 Recommendations for Pokémon Translation")

st.markdown("""
### For Best Translation Quality:
1. **Google Gemini 2.0 Flash** - Excellent Japanese → English translation
2. **Ollama: qwen2.5:14b** - Strong multilingual capabilities
3. **Ollama: mixtral:8x7b** - Excellent overall performance

### For Speed:
1. **Ollama: llama3.2:3b** - Very fast, decent quality
2. **Ollama: phi3:3.8b** - Fast with good quality
3. **Google Gemini 2.0 Flash** - Fast cloud processing

### For Privacy/Offline Use:
1. **Ollama: qwen2.5:7b** - Good balance of quality and resource usage
2. **Ollama: mistral:7b** - Excellent multilingual support
3. **Ollama: llama3.2:8b** - Reliable performance
""")

# Hardware requirements
st.header("💻 Hardware Requirements")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Lightweight Models (3B)")
    st.markdown("""
    - **RAM**: 4-8 GB
    - **GPU**: Optional
    - **Speed**: Very fast
    - **Quality**: Good for basic tasks
    """)

with col2:
    st.subheader("Balanced Models (7B-14B)")
    st.markdown("""
    - **RAM**: 8-16 GB
    - **GPU**: Recommended
    - **Speed**: Moderate
    - **Quality**: Excellent
    """)

with col3:
    st.subheader("Heavy Models (70B+)")
    st.markdown("""
    - **RAM**: 32+ GB
    - **GPU**: Required
    - **Speed**: Slower
    - **Quality**: Best available
    """)

# Test section
st.header("🧪 Test Your Model")

test_url = st.text_input(
    "Test URL",
    placeholder="Enter a Japanese Pokémon article URL to test",
    help="Test the selected model with a real article"
)

if test_url and st.button("🚀 Test Model"):
    if model_type == "Google Gemini (Cloud)":
        try:
            with st.spinner("Testing Google Gemini..."):
                result = llm_summary(test_url)
                st.success("✅ Test completed!")
                st.text_area("Result", result, height=400)
        except Exception as e:
            st.error(f"❌ Test failed: {e}")
    
    elif model_type == "Ollama (Local)" and OLLAMA_AVAILABLE:
        if 'selected_model' in locals():
            try:
                with st.spinner(f"Testing {selected_model}..."):
                    result = llm_summary_ollama(test_url, selected_model)
                    st.success("✅ Test completed!")
                    st.text_area("Result", result, height=400)
            except Exception as e:
                st.error(f" Test failed: {e}")
        else:
            st.error("Please select a model first")

# Footer
st.markdown("---")
st.markdown("""
** Tips:**
- Start with Google Gemini for immediate use
- Consider Ollama for long-term, cost-free usage
- Test different models to find your sweet spot
- Monitor your API usage if using cloud models
""") 