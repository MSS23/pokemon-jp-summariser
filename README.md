# Pokemon VGC Analysis Platform

🎮 **AI-powered analysis platform for Japanese Pokemon VGC tournament reports and team compositions.**

## Overview

This application uses Google Gemini AI to analyze Japanese Pokemon VGC (Video Game Championships) articles, providing comprehensive team analysis, translations, and strategic insights. Built with modern Python technologies and designed for competitive Pokemon players and analysts.

## ✨ Key Features

- **🤖 Advanced AI Analysis**: Google Gemini SDK integration with specialized 780+ line VGC prompts
- **🌐 Multi-Strategy Web Scraping**: Robust content extraction from Japanese sites (note.com, specialized VGC sites)
- **🔍 Pokemon Form Recognition**: Enhanced Gen 9 Pokemon identification including Ogerpon variants, Hisuian forms, Treasures of Ruin
- **📱 Modern Web Interface**: Clean Streamlit-based UI with responsive design
- **🖼️ Multi-Modal Analysis**: Text analysis + Nintendo Switch screenshot recognition
- **📊 EV Spread Analysis**: Comprehensive EV explanations with strategic reasoning
- **💾 Intelligent Caching**: Performance-optimized with smart content caching
- **📁 Export Functionality**: Download translations and pokepaste formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pokemon-vgc-analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Configure API key**
   Create `config/.streamlit/secrets.toml`:
   ```toml
   google_api_key = "your_gemini_api_key_here"
   ```

4. **Run the application**
   ```bash
   streamlit run src/app.py
   ```

## 🏗️ Architecture

### Clean Modular Structure
```
pokemon-vgc-analyzer/
├── src/                          # Main application source
│   ├── core/                     # Core business logic
│   │   ├── analyzer.py           # VGC analysis engine
│   │   ├── scraper.py           # Multi-strategy web scraping
│   │   └── pokemon_validator.py  # Pokemon form validation
│   ├── ui/                       # User interface
│   │   ├── components.py         # Streamlit UI components
│   │   └── pages.py             # Page routing logic
│   ├── utils/                    # Utilities
│   │   ├── config.py            # Configuration management
│   │   ├── cache_manager.py     # Caching system
│   │   └── image_analyzer.py    # Image analysis utilities
│   └── database/                 # Database models
├── tests/                        # Test suite
├── docs/                         # Documentation
├── config/                       # Configuration files
└── data/                         # Data storage
```

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

- **Backend**: Python 3.8+, Google Gemini AI SDK
- **Frontend**: Streamlit with custom CSS styling
- **Web Scraping**: BeautifulSoup4, Requests with multi-strategy fallbacks
- **Database**: SQLAlchemy with SQLite
- **Caching**: Custom intelligent caching system
- **APIs**: Google Gemini, PokeAPI for sprites
- **Testing**: Comprehensive real-world validation

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