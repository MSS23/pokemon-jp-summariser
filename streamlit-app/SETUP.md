# 🚀 Setup Guide - Pokemon VGC Team Analyzer

This guide will help you set up the Pokemon VGC Team Analyzer with either Google Gemini AI or Ollama local processing.

## 🔑 Option 1: Google Gemini AI (Recommended)

### Step 1: Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" to generate a new key
4. Copy the generated key (it should start with "AI" and be about 39 characters long)

### Step 2: Configure the App
1. Edit the file `.streamlit/secrets.toml`
2. Replace `"your_google_api_key_here"` with your actual API key
3. Save the file

**Example `secrets.toml`:**
```toml
google_api_key = "AIzaSyC..."  # Your actual API key here
```

### Step 3: Restart the App
- Stop the current Streamlit process (Ctrl+C)
- Run the app again: `streamlit run Summarise_Article.py`

## 🖥️ Option 2: Ollama (Local Processing - Free)

### Step 1: Install Ollama
1. Go to [ollama.ai](https://ollama.ai)
2. Download and install Ollama for your operating system
3. Start the Ollama service

### Step 2: Install a Model
Open terminal/command prompt and run:
```bash
ollama pull llama3.2:3b
```

**Recommended models:**
- `llama3.2:3b` - Fast, good for basic tasks
- `llama3.2:8b` - Better quality, moderate speed
- `mistral:7b` - Good multilingual support
- `mixtral:8x7b` - Excellent performance

### Step 3: Verify Installation
Run this command to check if Ollama is working:
```bash
ollama list
```

You should see your installed models.

## 🧪 Testing Your Setup

1. **Start the app:** `streamlit run Summarise_Article.py`
2. **Check the status:** You should see a green success message or blue info message
3. **Try an analysis:** Paste a Japanese Pokemon VGC article URL and click "Analyze"

## ❌ Troubleshooting

### "API key not valid" Error
- Ensure your API key starts with "AI"
- Check that you copied the entire key
- Verify the key is active in Google AI Studio

### "Ollama not found" Error
- Make sure Ollama is installed and running
- Check if the service is running: `ollama --version`
- Restart the Ollama service if needed

### "No LLM available" Error
- Check that either Gemini or Ollama is properly configured
- Review the setup steps above
- Check the app logs for detailed error messages

## 🔒 Security Notes

- **Never commit your API keys to version control**
- The `secrets.toml` file is already in `.gitignore`
- Keep your API keys secure and don't share them
- Monitor your API usage in Google AI Studio

## 📚 Additional Resources

- [Google AI Studio Documentation](https://ai.google.dev/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Streamlit Secrets Management](https://docs.streamlit.io/library/advanced-features/secrets-management)

## 🆘 Need Help?

If you're still having issues:
1. Check the app logs for error details
2. Verify your setup matches the examples above
3. Try restarting the app after configuration changes
4. Ensure you have the required Python packages installed

---

**Happy analyzing!** 🎉
