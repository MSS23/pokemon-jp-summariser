# Pokemon VGC Summariser - Streamlit Version

A Streamlit-based web application for translating and analyzing Japanese Pokémon VGC articles using AI-powered analysis.

## 🚀 Quick Start

```bash
cd streamlit-app
python -m streamlit run Summarise_Article.py --server.port 8501
```

## 📁 Structure

```
streamlit-app/
├── Summarise_Article.py      # Main application file
├── components/               # UI components
│   ├── auth_ui.py           # Authentication UI
│   ├── global_styles.py     # Global CSS styles
│   ├── navigation.py        # Navigation component
│   └── onboarding.py        # Onboarding guide
├── pages/                   # Streamlit pages
│   ├── Analytics_Dashboard.py
│   ├── Help_and_Guide.py
│   ├── LLM_Model_Selection.py
│   ├── Login.py
│   ├── Pokémon_Team_and_Summary_Search.py
│   ├── Register.py
│   └── User_Profile.py
├── utils/                   # Utilities
│   ├── analytics.py         # Analytics tracking
│   ├── auth.py             # Authentication system
│   ├── gemini_summary.py   # Gemini AI integration
│   ├── llm_summary.py      # LLM processing
│   ├── ollama_summary.py   # Ollama integration
│   └── user_preferences.py # User preferences
├── static/                  # Static assets
├── storage/                 # Data storage
└── .streamlit/             # Streamlit configuration
```

## 🔧 Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key (optional - can use Ollama for local processing)

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Create `.streamlit/secrets.toml`:
```toml
google_api_key = "your_gemini_api_key_here"
```

## 🎯 Features

### Core Functionality
- **Japanese Translation**: AI-powered translation using Gemini or Ollama
- **Team Analysis**: Extract Pokémon teams, abilities, moves, and Tera types
- **Caching System**: Avoid redundant API calls with intelligent caching
- **Export Options**: Multiple formats (Text, JSON, CSV)

### User Management
- **Authentication**: Secure user registration and login
- **User Profiles**: Personal statistics and activity tracking
- **Session Management**: Secure token-based authentication
- **Preferences**: Customizable themes and settings

### Analytics
- **Usage Tracking**: Monitor user activity and search patterns
- **Team Analytics**: Track popular teams and strategies
- **Personal Stats**: Individual user statistics

## 🎨 UI Features

- **Clean Design**: Minimal, professional interface
- **Responsive Layout**: Works on desktop and mobile
- **Navigation**: Top navbar with easy page switching
- **User Experience**: Intuitive workflow and feedback

## 🚀 Deployment

### Local Development
```bash
python -m streamlit run Summarise_Article.py --server.port 8501
```

### Streamlit Cloud
```bash
streamlit deploy Summarise_Article.py
```

## 🔐 Test Account

For testing purposes, a default account is created:
- **Username**: `testuser`
- **Password**: `testpass123`

## 📊 Analytics Dashboard

Track your usage with:
- Total searches performed
- Teams viewed
- Articles summarized
- Login statistics
- Recent activity timeline

## 🛠️ Technologies

- **Streamlit**: Web application framework
- **Google Gemini**: AI translation and analysis
- **Ollama**: Local AI processing (free alternative)
- **BeautifulSoup**: Web scraping
- **JSON**: Data storage and caching

## 🆘 Support

- Check the Help & Guide section in the app
- Review the documentation
- Create an issue on GitHub

---

**Ready to start?** Run the app and begin analyzing Japanese Pokémon VGC articles! 