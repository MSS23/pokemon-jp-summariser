# Security Configuration

## Environment Setup

### React App
1. Copy `react-app/.env.example` to `react-app/.env`
2. Add your Google API key: `VITE_GOOGLE_API_KEY=your_actual_api_key`

### Streamlit App
1. Create `streamlit-app/.streamlit/secrets.toml` from the example file
2. Add your Google API key: `google_api_key = "your_actual_api_key"`

## Security Best Practices

- Never commit API keys to version control
- Use environment variables for all secrets
- Rotate API keys regularly
- Monitor API usage for unusual activity
- Use HTTPS in production
- Implement rate limiting for API endpoints

## Files to Keep Secure

- `react-app/.env`
- `streamlit-app/.streamlit/secrets.toml`
- `streamlit-app/storage/secret_key.txt`

These files are in .gitignore and should never be committed.