# Pokemon Japanese Team Translator

A React application that translates Japanese VGC articles and extracts Pokemon team compositions using Google's Gemini AI.

## Features

- **Japanese Article Translation**: Translate Japanese VGC articles to English
- **Team Analysis**: Extract detailed Pokemon team compositions with EVs, moves, and stats
- **Real-time Processing**: Powered by Google Gemini AI
- **Professional UI**: Dark theme with purple accents
- **Responsive Design**: Works on desktop and mobile devices

## Setup

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Google Gemini API key

### Installation

1. **Clone the repository and navigate to the React app directory:**
   ```bash
   cd react-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up your Gemini API key:**
   Create a `.env` file in the root directory:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Start the backend server:**
   ```bash
   npm run server
   ```

5. **In a new terminal, start the React development server:**
   ```bash
   npm run dev
   ```

6. **Open your browser and navigate to:**
   ```
   http://localhost:5173
   ```

## Usage

1. **Enter a Japanese VGC article URL** in the translator
2. **Click "Translate Article"** to process the content
3. **View the results:**
   - Original Japanese text
   - English translation
   - Extracted Pokemon teams with detailed stats
   - Team strategy summary
   - List of mentioned Pokemon

## API Integration

The app uses Google's Gemini AI to:
- Translate Japanese text to English
- Extract Pokemon team compositions
- Analyze team strategies
- Identify Pokemon types, moves, and stats

## Project Structure

```
react-app/
├── src/
│   ├── components/     # React components
│   ├── pages/         # Page components
│   ├── context/       # React context providers
│   └── App.tsx        # Main app component
├── server.js          # Express backend server
├── vite.config.ts     # Vite configuration
└── package.json       # Dependencies
```

## Technologies Used

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Express.js, Node.js
- **AI**: Google Gemini API
- **Build Tool**: Vite
- **Routing**: React Router

## Development

- **Frontend**: `npm run dev` (runs on port 5173)
- **Backend**: `npm run server` (runs on port 3001)
- **Build**: `npm run build`

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Notes

- The web scraping functionality in `server.js` is currently a placeholder
- You'll need to implement proper web scraping based on the target websites
- Consider using libraries like Puppeteer or Cheerio for web scraping
- Ensure you comply with the target websites' terms of service

## License

This project is for educational and personal use only.
