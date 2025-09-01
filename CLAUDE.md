# CLAUDE.md

This file provides guidance to Claude Code when working with this Pokemon VGC analysis application.

## Project Overview

This is a modular Pokemon VGC (Video Game Championships) article analysis application built with Streamlit. The application analyzes Japanese Pokemon VGC articles using Google Gemini AI to provide comprehensive team composition analysis, translations, EV explanations, and team showcases with Pokemon sprites.

## Development Commands

### Main Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# Code quality checks
python -m black .
python -m flake8 .
```

## Application Architecture

### Clean Modular Structure
```
Pokemon Translation Web App/
├── app.py                     # Main Streamlit application entry point
├── config.py                  # Configuration management
├── vgc_analyzer.py           # Core VGC analysis logic
├── ui_components.py          # Streamlit UI components
├── utils.py                  # Utility functions
├── cache_manager.py          # Caching functionality
├── requirements.txt          # Python dependencies
├── database/                 # Database models and operations
│   ├── models.py            # SQLAlchemy models
│   ├── crud.py              # Database operations
│   └── __init__.py
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # API keys and secrets
├── cache/                   # Analysis result cache
├── streamlit-app/logs/      # Application logs
└── CLAUDE.md               # Project documentation
```

### Key Features
- **Modular architecture**: Clean separation of concerns across multiple focused modules
- **Google Gemini AI integration**: Advanced VGC analysis with specialized prompts
- **Pokemon sprite display**: Automatic sprite fetching from PokeAPI
- **Clean UI components**: Professional team showcase with hover effects
- **Export functionality**: Download translations and pokepaste formats
- **Caching system**: Intelligent caching for improved performance
- **Database integration**: Optional SQLite database for team storage
- **Responsive design**: Works well on desktop and mobile

## Core Modules

### Main Application (app.py)
- `VGCAnalysisApp`: Main application class that orchestrates all functionality
- Clean, focused entry point with proper error handling
- Session state management for analysis results

### VGC Analyzer (vgc_analyzer.py)
- `GeminiVGCAnalyzer`: Core analysis engine using Google Gemini
- `scrape_article(url)`: Extracts content from Japanese VGC article URLs
- `validate_url(url)`: Validates article URLs before processing
- `analyze_article(content)`: Uses specialized VGC prompt for comprehensive analysis

### Configuration (config.py)
- `Config`: Centralized configuration management
- API key handling with fallbacks
- Translation dictionaries for Pokemon, moves, and items

### UI Components (ui_components.py)
- Modular Streamlit UI components for different sections
- Professional styling with custom CSS
- Export functionality for translations and pokepaste format

### Utilities (utils.py)
- Pokemon sprite fetching from PokeAPI
- EV spread parsing and validation
- Content hashing and validation functions

### Cache Manager (cache_manager.py)
- `CacheManager`: Intelligent caching system for analysis results
- TTL-based cache expiration
- Performance optimization for repeated analyses

### Helper Functions
- `get_pokemon_sprite_url(name)`: Fetches Pokemon sprites from PokeAPI
- `create_pokepaste(team, name)`: Generates pokepaste format for team export

## Environment Configuration

### Required Configuration
```bash
# Google API Key (Required)
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Streamlit Secrets (.streamlit/secrets.toml)
```toml
google_api_key = "your_api_key_here"
```

## Application Features

### 1. Article Analysis
- Japanese VGC article URL input
- Manual text input option
- Real-time content scraping and validation
- Comprehensive AI-powered analysis

### 2. Team Showcase
- Pokemon sprite display with PokeAPI integration
- Detailed team member cards with hover effects
- EV spread analysis with strategic explanations
- Move sets and item information

### 3. Export Functionality
- **Translation Download**: Complete article translation as .txt file
- **Pokepaste Export**: Team in standard pokepaste format for easy importing

### 4. EV Analysis Details
The application provides comprehensive EV explanations including:
- Speed benchmarks and tier positioning
- Survival calculations with specific percentages
- Damage output optimization
- Team synergy considerations
- Meta-specific reasoning

## AI Integration

### Specialized VGC Prompt
The application uses a comprehensive 380+ line prompt that includes:
- Japanese to English translation mappings for Pokemon, moves, abilities
- EV spread validation and explanation requirements
- Team composition analysis guidelines
- Meta relevance assessment criteria

### Gemini Model Configuration
- **Text Model**: `gemini-2.5-flash` (optimal balance: advanced quality + 5x higher quota than Pro)
- **Vision Model**: `gemini-2.5-flash-lite` (cost-effective for image processing)
- **Content Limit**: 8000 characters for analysis
- **Output Format**: Structured JSON with team data and translations

## Common Use Cases

### Analyzing Tournament Reports
1. Input Japanese tournament report URL
2. Receive English translation with team breakdowns
3. Download pokepaste for team importing
4. Study EV reasoning and strategy explanations

### Team Study and Research
1. Paste Japanese team building article text
2. Get detailed Pokemon role analysis
3. Understand EV investment strategies
4. Export for further analysis or sharing

## Troubleshooting

### API Key Issues
- Ensure Google API key is set in `.streamlit/secrets.toml`
- Verify Gemini API access and quota
- Check environment variable `GOOGLE_API_KEY` as fallback

### Pokemon Sprite Loading
- Application uses PokeAPI for sprite fetching
- Handles name variations and special characters
- Falls back to default image on API errors

### Article Scraping
- Supports most common Japanese Pokemon sites
- Handles dynamic content and various HTML structures
- Includes user agent headers for compatibility

## Development Notes

### Code Style
- Single-file architecture for simplicity
- Clear function separation and documentation
- Consistent error handling throughout
- Responsive UI design with CSS styling

### Extension Points
- Easy to add new Pokemon data sources
- Modular AI prompt system for customization
- Expandable export formats
- Additional language support capabilities

## Important Instructions
When working with this application:
1. **Always test URL validation** before processing articles
2. **Verify EV spread formats** (should be multiples of 4, totaling 508)
3. **Handle missing data gracefully** with "Not specified" fallbacks
4. **Maintain VGC terminology accuracy** in translations
5. **Test export functionality** for both translation and pokepaste outputs