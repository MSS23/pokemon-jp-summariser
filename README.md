# Pokemon Translation Web App

A comprehensive web application for analyzing and translating Pokemon VGC team articles from Japanese to English, with both Streamlit and React frontends.

## 🏗️ Project Structure

```
Pokemon Translation Web App/
├── streamlit-app/          # Streamlit application
│   ├── Summarise_Article.py    # Main Streamlit app
│   ├── pokemon_card_display.py # Pokemon card display utilities
│   ├── requirements.txt        # Python dependencies
│   ├── style.css              # Custom styling
│   ├── components/            # Streamlit components
│   ├── pages/                 # Streamlit pages
│   ├── utils/                 # Utility functions
│   ├── storage/               # Data storage
│   └── static/               # Static assets
├── react-app/               # React application
│   ├── src/                 # React source code
│   ├── public/              # Public assets
│   ├── package.json          # Node.js dependencies
│   └── README.md            # React app documentation
├── llm_env/                 # Python virtual environment
├── GEMINI_SETUP.md          # Gemini API setup guide
└── README.md               # This file
```

## 🚀 Quick Start

### Streamlit Application

1. **Navigate to the Streamlit app directory:**
   ```bash
   cd streamlit-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Gemini API key:**
   - Create a `.streamlit/secrets.toml` file
   - Add your API key: `GOOGLE_API_KEY = "your-api-key-here"`

4. **Run the application:**
   ```bash
   streamlit run Summarise_Article.py
   ```

5. **Access the app:**
   - Open your browser and go to `http://localhost:8501`

### React Application

1. **Navigate to the React app directory:**
   ```bash
   cd react-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up your Gemini API key:**
   - Create a `.env` file in the `react-app` directory
   - Add your API key: `VITE_GOOGLE_API_KEY=your-api-key-here`

4. **Run the application:**
   ```bash
   npm start
   ```

5. **Access the app:**
   - Open your browser and go to `http://localhost:5173`

## 🎯 Features

### Both Applications
- **Article Analysis**: Extract Pokemon team information from Japanese articles
- **Team Composition**: Display Pokemon with moves, abilities, items, and EV spreads
- **Strengths & Weaknesses**: Analyze team strengths and weaknesses
- **Multi-language Support**: Handle Japanese and English content
- **Image Processing**: Extract and analyze images from articles

### Streamlit App
- **Multi-page Interface**: Analytics, Help, and Model Selection pages
- **User Authentication**: Login and registration system
- **Data Persistence**: Save and load analysis results
- **Advanced Analytics**: Performance metrics and usage statistics

### React App
- **Modern UI**: Clean, responsive interface with Tailwind CSS
- **Team Search**: Browse and search previously analyzed teams
- **Direct Text Input**: Fallback option when URL fetching fails
- **Real-time Updates**: Live analysis results

## 🔧 Configuration

### Gemini API Setup
Both applications require a Google Gemini API key. See `GEMINI_SETUP.md` for detailed setup instructions.

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `SECRET_KEY`: Secret key for session management (Streamlit)

## 📁 Key Files

### Streamlit App
- `Summarise_Article.py`: Main application with UI and analysis logic
- `pokemon_card_display.py`: Pokemon card rendering utilities
- `utils/llm_summary.py`: LLM prompt templates and analysis logic
- `components/`: Reusable Streamlit components
- `pages/`: Additional application pages

### React App
- `src/pages/Summarizer.tsx`: Main analysis page
- `src/pages/TeamSearch.tsx`: Team search and display page
- `src/services/geminiService.ts`: Gemini API integration
- `src/hooks/useGemini.ts`: Custom React hooks for Gemini
- `src/components/`: Reusable React components

## 🛠️ Development

### Adding New Features
1. **Streamlit**: Add new pages in `streamlit-app/pages/` or components in `streamlit-app/components/`
2. **React**: Add new pages in `react-app/src/pages/` or components in `react-app/src/components/`

### Code Style
- **Python**: Follow PEP 8 guidelines
- **TypeScript/React**: Use ESLint and Prettier configurations
- **Documentation**: Add docstrings and comments for complex functions

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Set environment variables in the Streamlit Cloud dashboard
4. Deploy

### Netlify (React)
1. Build the React app: `npm run build`
2. Deploy the `dist` folder to Netlify
3. Set environment variables in Netlify dashboard

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both applications
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the existing documentation
2. Review the setup guides
3. Open an issue on GitHub
