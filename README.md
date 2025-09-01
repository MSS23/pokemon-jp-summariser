# Pokemon VGC Article Analyzer 🎮⚔️

A powerful Streamlit application for analyzing Japanese Pokemon VGC (Video Game Championships) articles with AI-powered translation, team showcase, and export functionality.

## Features ✨

- 🔍 **Japanese Article Analysis**: Scrape and analyze VGC articles from URLs or text input
- 🤖 **AI-Powered Translation**: Google Gemini AI provides accurate translations with VGC terminology
- 🌟 **Beautiful Team Showcase**: Pokemon sprites, detailed stats, and professional layouts
- 📊 **EV Strategy Analysis**: Comprehensive explanations of EV spreads and strategic decisions
- 📥 **Export Functionality**: Download translations (.txt) and pokepaste files
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile

## Quick Start 🚀

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Set your Google Gemini API key in `.streamlit/secrets.toml`:

```toml
google_api_key = "your_api_key_here"
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## How to Use 📖

### Analyzing an Article

1. **Enter URL**: Paste a Japanese VGC article URL in the sidebar
2. **Or Paste Text**: Manually paste article content in the text area
3. **Click Analyze**: Hit the "🔍 Analyze Article" button
4. **View Results**: See the translated content and team showcase

### Understanding the Results

- **Article Summary**: Main points and strategy overview
- **Team Analysis**: Strengths, weaknesses, and meta relevance
- **Pokemon Showcase**: Individual cards with sprites, stats, and moves
- **EV Explanations**: Detailed reasoning for stat investments

### Exporting Data

- **📄 Translation**: Download complete article translation as .txt file
- **🎮 Pokepaste**: Export team in standard pokepaste format for easy importing

## Features in Detail 🔧

### AI-Powered Analysis
- Uses Google Gemini 2.5 Pro for VGC analysis (premium quality) and Flash-Lite for vision tasks (cost-effective)
- Accurate translation of Pokemon names, moves, and abilities
- EV spread validation and explanation
- Team composition and meta analysis

### Pokemon Showcase
- Automatic sprite fetching from PokeAPI
- Hover effects and professional styling
- Detailed move sets and item information
- Expandable EV strategy explanations

### Export Capabilities
- **Translation Files**: Complete article translations with formatting
- **Pokepaste Format**: Standard format compatible with Pokemon Showdown and other tools

## Supported Content 📚

- Japanese VGC tournament reports
- Team building articles and guides
- Pokemon competitive analysis posts
- Strategy discussions and meta reports

## Technical Details ⚙️

### Dependencies
- Streamlit 1.28+
- Google Generative AI 0.3+
- Requests, BeautifulSoup4, PIL
- PokeAPI integration for sprites

### Architecture
- Single-file application for simplicity
- Modular function design
- Error handling and fallbacks
- Responsive CSS styling

## Troubleshooting 🔧

### Common Issues

**API Key Problems**
- Ensure your Google API key is correctly set in `.streamlit/secrets.toml`
- Verify Gemini API access and quota limits

**Pokemon Sprites Not Loading**
- Check internet connection to PokeAPI
- Application provides fallbacks for missing sprites

**Article Scraping Issues**
- Some sites may block automated requests
- Try the manual text input option instead

### Getting Help

If you encounter issues:
1. Check the console for error messages
2. Verify all dependencies are installed
3. Ensure your API key has proper permissions

## Example Workflow 💡

1. **Find a Japanese VGC article** from sites like Pokestats, notes, or tournament reports
2. **Copy the URL** and paste it into the application sidebar
3. **Click "Analyze Article"** and wait for processing (typically 10-30 seconds)
4. **Review the results**: translated content, team breakdown, and EV explanations
5. **Download files**: save translation and pokepaste for future reference
6. **Share or study**: use the exported data for team building or research

## Contributing 🤝

This is a single-file application designed for simplicity and ease of use. Contributions and improvements are welcome!

### Areas for Enhancement
- Additional language support
- More export formats
- Enhanced UI components
- Integration with other Pokemon databases

## License 📄

This project is for educational and research purposes. Pokemon is a trademark of Nintendo/Game Freak/Creatures Inc.

---

Enjoy analyzing VGC teams! 🎉
