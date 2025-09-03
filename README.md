# Pokemon VGC Analysis Platform

🎮 **AI-powered analysis platform for Japanese Pokemon VGC tournament reports and team compositions.**

## Overview

This application uses Google Gemini AI to analyze Japanese Pokemon VGC (Video Game Championships) articles, providing comprehensive team analysis, translations, and strategic insights. Built with modern Python technologies and designed for competitive Pokemon players and analysts.

## ✨ Key Features

- **🤖 Advanced AI Analysis**: Google Gemini 2.0 Flash integration with specialized 780+ line VGC prompts for accurate team analysis
- **🌐 Multi-Strategy Web Scraping**: Robust content extraction with multiple fallback strategies for Japanese sites (note.com, VGC community sites)
- **🔍 Enhanced Pokemon Recognition**: Gen 9 complete Pokemon identification including Ogerpon variants, Hisuian forms, Treasures of Ruin, and regional variants
- **📱 Modern Web Interface**: Professional Streamlit-based UI with custom CSS, responsive design, and real-time status updates
- **🖼️ Multi-Modal Analysis**: Integrated text analysis + Nintendo Switch screenshot recognition using Gemini Vision API
- **📊 Advanced EV Analysis**: Comprehensive EV spread extraction with strategic reasoning and competitive context
- **💾 Intelligent Caching System**: File-based performance optimization with automatic cache management and expiration
- **🎮 Switch Translation**: Dedicated Nintendo Switch screenshot translation for team cards and battle screens
- **📁 Export Functionality**: Multiple export formats including Pokepaste integration and JSON data export
- **🔧 Deployment Ready**: Streamlit Cloud optimized with environment detection and graceful error handling

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Python 3.11+ recommended for best performance)
- **Google Gemini API key** (Google AI Studio - free tier available)
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pokemon-vgc-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: Uses Streamlit Cloud optimized dependency versions*

3. **Configure API key**
   
   **Option A: Create secrets file (Recommended)**
   ```bash
   mkdir -p config/.streamlit
   ```
   Create `config/.streamlit/secrets.toml`:
   ```toml
   google_api_key = "your_gemini_api_key_here"
   ```
   
   **Option B: Environment variable**
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   The application will be available at `http://localhost:8501`

### Getting a Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key to your configuration

## 🏗️ Architecture

### Clean Modular Structure
```
pokemon-vgc-analyzer/
├── app.py                        # Main Streamlit application entry point
├── src/                          # Main application source
│   ├── core/                     # Core business logic
│   │   ├── analyzer.py           # Gemini VGC analysis engine (780+ line prompts)
│   │   ├── scraper.py           # Multi-strategy web scraping with fallbacks
│   │   └── pokemon_validator.py  # Enhanced Gen 9 Pokemon form validation
│   ├── ui/                       # User interface layer
│   │   ├── components.py         # Streamlit UI components & styling
│   │   └── pages.py             # Page routing & Switch translation
│   ├── utils/                    # Utility modules
│   │   ├── config.py            # Configuration & Pokemon translations
│   │   ├── cache_manager.py     # Intelligent file-based caching
│   │   ├── image_analyzer.py    # Vision API & screenshot analysis
│   │   └── utils.py             # Helper functions & data processing
│   └── vgc_analyzer.db          # SQLite database for team storage
├── requirements.txt              # Streamlit Cloud optimized dependencies
├── runtime.txt                   # Python version specification
├── packages.txt                  # System packages for deployment
└── config/                       # Configuration files
    └── .streamlit/               # Streamlit secrets & settings
        └── secrets.toml          # API keys (not in repository)
```

### Key Architecture Principles
- **Separation of Concerns**: Clear division between analysis, UI, and utilities
- **Gemini AI Integration**: Advanced prompt engineering for VGC-specific analysis
- **Multi-Modal Processing**: Text analysis + vision capabilities for screenshots
- **Robust Error Handling**: Graceful fallbacks for deployment environments
- **Performance Optimization**: Intelligent caching and async operations

## 🎯 Real-World Performance

Based on comprehensive testing with 8 diverse Japanese VGC articles:

- **✅ 62% Total Success Rate** (38% complete + 25% partial)
- **📊 25,601+ characters** of VGC content successfully extracted
- **🎯 340 average quality score** accurately reflecting VGC relevance
- **🔧 Zero UI contamination** on successful extractions

### Successful Site Types:
- ✅ **note.com** dynamic content (major improvement)
- ✅ **Tournament reports** with detailed team data
- ✅ **Player spotlights** and mixed content types
- ✅ **Team construction** articles with EV spreads

## 🛠️ Technologies Used

- **Backend**: Python 3.8+, Google Gemini 2.0 Flash AI SDK
- **Frontend**: Streamlit 1.28+ with custom CSS styling and responsive design
- **AI Models**: Google Gemini 2.0 Flash (text analysis & vision processing)
- **Web Scraping**: BeautifulSoup4, Requests, lxml with multi-strategy fallbacks
- **Database**: SQLite (vgc_analyzer.db) with SQLAlchemy ORM
- **Image Processing**: Pillow 10.0+, Google Gemini Vision API
- **Caching**: Custom intelligent file-based caching system
- **APIs**: Google Generative AI, PokeAPI for sprites
- **Data Processing**: Pandas 2.0+, aiohttp for async operations
- **Testing**: Comprehensive real-world validation with Japanese VGC sites

## 📖 Documentation

- **[Development Guide](docs/CLAUDE.md)**: Complete development setup and architecture
- **[API Documentation](docs/API.md)**: Detailed API reference
- **[Architecture Overview](docs/ARCHITECTURE.md)**: System design and patterns

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

### Test Coverage
- **Integration Tests**: End-to-end workflow validation
- **EV Extraction Tests**: Comprehensive EV spread parsing
- **Real-World Validation**: Tested against 8 diverse Japanese VGC sites

## 🚀 Deployment

### Streamlit Cloud Deployment
The application is optimized for Streamlit Cloud deployment:

1. **Fork the repository** on GitHub
2. **Connect to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your forked repository
3. **Configure secrets**:
   - In Streamlit Cloud dashboard, go to app settings
   - Add secret: `google_api_key = "your_api_key_here"`
4. **Deploy**: The app will automatically deploy with optimized settings

### Local Development
```bash
# Clone and setup
git clone <repository-url>
cd pokemon-vgc-analyzer
pip install -r requirements.txt

# Configure API key (choose one method)
echo 'google_api_key = "your_key_here"' > config/.streamlit/secrets.toml
# OR
export GOOGLE_API_KEY="your_key_here"

# Run locally
streamlit run app.py
```

## 🔧 Troubleshooting

### Common Issues

**❌ API Key Not Found**
- Ensure `config/.streamlit/secrets.toml` exists with correct format
- Or set `GOOGLE_API_KEY` environment variable
- Verify API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)

**❌ Import Errors**
- Run `pip install -r requirements.txt` to install dependencies
- Ensure Python 3.8+ is being used
- Try creating a virtual environment: `python -m venv venv && source venv/bin/activate`

**❌ Web Scraping Failures**
- Check internet connection and URL accessibility
- Some sites may block automated requests - this is expected behavior
- Try using the direct text input instead of URL analysis

**❌ Cache Issues**
- Clear cache through Settings page in the app
- Or manually delete cache files in the data directory
- Restart the application after clearing cache

**❌ Deployment Issues (Streamlit Cloud)**
- Verify all files are pushed to GitHub repository
- Check that requirements.txt includes all necessary dependencies
- Ensure secrets are properly configured in Streamlit Cloud dashboard
- Monitor deployment logs for specific error messages

### Performance Tips
- Use caching for repeated analyses of the same content
- Clear expired cache regularly through the Settings page
- For large images, compress before uploading to Switch translation feature
- Monitor API usage to stay within Google AI Studio quotas

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI team for powerful language models
- Pokemon VGC community for domain expertise
- Japanese Pokemon content creators for test data
- Streamlit team for the excellent web framework

## 🔗 Links

- [Live Demo](link-to-demo) (if applicable)
- [Documentation](docs/)
- [Issue Tracker](link-to-issues)

---

**Built with ❤️ for the Pokemon VGC community**