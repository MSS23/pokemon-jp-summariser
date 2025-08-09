# Pokemon Translation Backend API

A secure FastAPI backend that handles Google Gemini API calls for the Pokemon Translation Web App.

## 🔐 Security Features

- **API Key Protection**: Google Gemini API key stays on the server
- **Rate Limiting**: Prevents abuse with configurable limits
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Validates all incoming requests
- **Error Handling**: Graceful error responses

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### POST `/api/analyze`
Analyze a Pokemon article and extract team information.

**Request Body:**
```json
{
  "url": "https://example.com/pokemon-article",
  "direct_text": null
}
```

**Response:**
```json
{
  "title": "Article Title",
  "summary": "Article summary...",
  "teams": [
    {
      "name": "Pokemon Name",
      "ability": "Ability Name",
      "item": "Item Name",
      "tera_type": "Tera Type",
      "nature": "Nature",
      "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
      "evs": {
        "hp": 252,
        "attack": 0,
        "defense": 0,
        "spAtk": 252,
        "spDef": 0,
        "speed": 4
      },
      "ev_spread": "252 SpA / 252 HP / 4 Spe",
      "ev_explanation": "EV explanation..."
    }
  ],
  "strengths": ["Strength 1", "Strength 2"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "success": true,
  "error": null
}
```

### GET `/health`
Health check endpoint.

### GET `/api/usage/{client_ip}`
Get usage statistics for monitoring.

## 🔧 Configuration

### Rate Limiting
- Default: 10 requests per minute per IP
- Configurable in `server.py`

### CORS
- Configure `allow_origins` in production
- Currently allows all origins for development

## 🚀 Deployment

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `RATE_LIMIT`: Requests per minute (default: 10)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit API keys to version control
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure allowed origins properly
4. **Rate Limiting**: Implement appropriate limits
5. **Input Validation**: Validate all inputs
6. **Error Handling**: Don't expose sensitive information in errors

## 📊 Monitoring

The API includes basic monitoring:
- Request counts per IP
- Rate limit tracking
- Health check endpoint
- Error logging

## 🔄 Frontend Integration

Update your React app to call this API instead of using direct Gemini integration:

```typescript
// In your geminiService.ts
const API_BASE_URL = 'https://your-api-domain.com';

export class GeminiService {
  async summarizeArticle(url?: string, directText?: string) {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url,
        direct_text: directText
      })
    });
    
    return await response.json();
  }
}
``` 