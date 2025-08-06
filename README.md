# Pokemon Translation Web App

A modern web application for translating and analyzing Japanese Pokemon VGC articles using AI. Built with React and Streamlit.

## 🚀 Quick Start

### React App (Frontend)
```bash
cd react-app
npm install
npm run dev
```
Visit: http://localhost:5173

### Streamlit App (Alternative Interface)
```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run Summarise_Article.py
```
Visit: http://localhost:8501

## 📁 Project Structure

```
Pokemon Translation Web App/
├── react-app/          # React frontend with Gemini integration
├── streamlit-app/      # Streamlit alternative interface
├── shared/            # Shared utilities and constants
└── scripts/           # Utility scripts
```

## 🎯 Features

- **Japanese to English Translation**: Powered by Google Gemini AI
- **Pokemon Team Analysis**: Extract and analyze team compositions
- **Modern UI**: Clean, responsive React interface
- **Alternative Interface**: Streamlit app for different use cases
- **Real-time Processing**: Fast translation and analysis

## 🔧 Setup

### Prerequisites
- Node.js 18+ (for React app)
- Python 3.8+ (for Streamlit app)
- Google Gemini API key

### Environment Variables
Create `.env` file in `react-app/`:
```env
VITE_GOOGLE_API_KEY=your_google_api_key_here
```

## 🎨 Technologies Used

- **Frontend**: React, TypeScript, Tailwind CSS
- **AI**: Google Gemini 2.0 Flash
- **Alternative**: Streamlit
- **Styling**: Tailwind CSS, Framer Motion

## 📝 Usage

1. **Start the React app**: `npm run dev` in `react-app/`
2. **Enter a Japanese Pokemon VGC article URL**
3. **Get instant translation and team analysis**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
