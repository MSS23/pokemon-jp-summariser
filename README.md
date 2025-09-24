# 🔒 Pokemon VGC Article Translator - Compliant Version 2.0

**AI-powered analysis platform for Japanese Pokemon VGC content with full Google Gemini API compliance**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Compliance](https://img.shields.io/badge/Compliance-Google%20Gemini%20API-success.svg)](https://ai.google.dev/)

## 🚨 Compliance Notice

This application has been **completely refactored** to comply with:
- **Google Gemini API Additional Terms**
- **Google APIs Terms of Service**
- **Generative AI Prohibited Use Policy**
- **COPPA (Children's Online Privacy Protection Act)**
- **Website robots.txt policies and crawling ethics**

## 🏗️ Architecture Overview

```
📁 app/
├── 🖥️ streamlit_app.py          # Clean frontend (no API keys)
├── ⚙️ backend/                  # FastAPI compliance server
│   ├── main.py                  # API routes & health checks
│   ├── gemini_client.py         # Server-side Gemini API calls
│   ├── compliance.py            # Domain allowlist + robots.txt
│   ├── safety.py                # Content moderation + PII redaction
│   ├── rate_limit.py            # Redis rate limiting
│   └── fetcher.py               # Safe HTML content extraction
├── 🔧 shared/                   # Shared models & utilities
│   ├── models.py                # Pydantic schemas
│   └── logging.py               # Structured compliance logging
├── 🔐 .env.example              # Environment configuration
├── 📦 pyproject.toml            # Modern Python dependencies
└── 📖 README.md                 # This file
```

## 🛡️ Compliance Features

### 1. **🔞 Age Verification (18+)**
- **Modal gate** blocks users under 18
- **24-hour persistence** via URL parameters
- **Session state management** for seamless UX
- **COPPA compliance** enforced at application level

### 2. **🔐 Server-Side API Key Protection**
- **Gemini API keys** never exposed to frontend
- **All LLM calls** processed server-side only
- **Environment-based configuration** with fallbacks
- **Provider enable/disable control** for graceful degradation

### 3. **🌐 Domain Allowlist & robots.txt Compliance**
- **Curated allowlist** of approved Pokemon community sites
- **Real-time robots.txt checking** with caching
- **Automatic blocking** of disallowed URLs
- **Paywall/login detection** heuristics

### 4. **🛡️ Content Safety & Moderation**
- **Scope validation**: Only Pokemon VGC content processed
- **PII redaction**: Emails, phones, addresses automatically removed
- **Prohibited content filtering**: Blocks harassment, NSFW, medical advice, etc.
- **Input sanitization**: HTML cleaning and text extraction

### 5. **⚡ Rate Limiting & Abuse Prevention**
- **5 analyses per hour** per IP address
- **1 concurrent request** limit per user
- **Redis-backed quotas** with in-memory fallback
- **Structured logging** of all rate limit violations

### 6. **📊 Comprehensive Audit Logging**
- **JSON structured logs** for compliance tracking
- **Request tracing** with hashed IPs (privacy-preserving)
- **Compliance decision logging** for all checks
- **Error tracking** with detailed context

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- **Google Gemini API key** ([Get yours here](https://aistudio.google.com/app/apikey))
- **Redis** (optional, for enhanced rate limiting)

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd pokemon-vgc-translator

# Install dependencies
pip install -e .

# Or with poetry
poetry install
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Required settings:**
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
PROVIDER_ENABLED_GEMINI=true
```

### 3. Start the Backend

```bash
# Development
uvicorn app.backend.main:app --reload --host 127.0.0.1 --port 8000

# Production
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 4. Start the Frontend

```bash
# In a new terminal
streamlit run app/streamlit_app.py
```

### 5. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📋 Compliance Checklist

### ✅ Google Gemini API Terms Compliance

- [x] **API keys server-side only** - Never exposed to client
- [x] **Proper error handling** - User-friendly error messages
- [x] **Rate limiting implemented** - Prevents quota abuse
- [x] **Content safety enforced** - Prohibited content blocked
- [x] **Age verification** - 18+ requirement enforced
- [x] **Request logging** - Full audit trail maintained

### ✅ Website Crawling Ethics

- [x] **robots.txt respected** - Automatic checking before crawl
- [x] **Domain allowlist** - Only approved community sites
- [x] **Rate limiting** - Prevents server overload
- [x] **Paywall detection** - Avoids gated content
- [x] **Content-type validation** - Only processes HTML

### ✅ Privacy & Security

- [x] **PII redaction** - Personal information automatically removed
- [x] **Session-only tracking** - No persistent user identification
- [x] **Secure headers** - HTTPS-ready deployment
- [x] **Input validation** - Prevents injection attacks
- [x] **Error sanitization** - No sensitive data in error messages

## 🔧 Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `PROVIDER_ENABLED_GEMINI` | ✅ Yes | `true` | Enable/disable AI features |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis connection for rate limiting |
| `ALLOWED_DOMAINS` | No | Built-in list | Comma-separated allowed domains |
| `RATE_LIMIT_PER_HOUR` | No | `5` | Max requests per hour per IP |
| `CONCURRENT_LIMIT` | No | `1` | Max concurrent requests per IP |
| `MAX_CONTENT_SIZE` | No | `3000000` | Max content size in bytes |
| `REQUEST_TIMEOUT` | No | `10` | Request timeout in seconds |
| `LOG_DIR` | No | `logs` | Directory for log files |

### Domain Allowlist (Default)

The application includes a comprehensive allowlist of Pokemon community sites:

**Official & Major Sites:**
- `pokemon.com`, `pokemon-gl.com`
- `smogon.com`, `bulbagarden.net`, `pkmn.news`
- `victoryroadvgc.com`, `trainertower.com`, `nuggetbridge.com`

**Japanese Pokemon Sites:**
- `note.com`, `liberty-note.com`
- `hatenablog.com`, `hatenablog.jp`, `hateblo.jp`
- Various Pokemon blogger domains

**Social/Community Platforms:**
- `youtube.com`, `youtu.be` (team showcases)
- `twitter.com`, `x.com` (VGC posts)
- `reddit.com` (Pokemon communities)

## 🚦 API Endpoints

### Backend Routes

**Health Check**
```http
GET /health
```
Returns provider status and system health.

**URL Compliance Check**
```http
POST /check
Content-Type: application/json

{
  "url": "https://note.com/example/pokemon-team"
}
```

**Content Analysis**
```http
POST /analyze
Content-Type: application/json

{
  "url": "https://note.com/example/pokemon-team",
  "options": {}
}
```

### Response Examples

**Compliance Check (Success)**
```json
{
  "status": "allowed",
  "step_failed": null,
  "reason": "All compliance checks passed",
  "domain": "note.com",
  "robots_allowed": true,
  "content_type": "text/html; charset=utf-8",
  "size_estimate": "15240"
}
```

**Analysis Result (Success)**
```json
{
  "status": "success",
  "analysis": {
    "title": "VGC World Championships Team",
    "regulation": "Series 1",
    "pokemon_team": [
      {
        "name": "Garchomp",
        "item": "Choice Scarf",
        "ability": "Rough Skin",
        "nature": "Jolly",
        "ev_spread": {
          "HP": 0,
          "Attack": 252,
          "Speed": 252
        },
        "moves": ["Dragon Claw", "Earthquake", "Rock Slide", "Protect"],
        "analysis": "Fast physical attacker with Choice Scarf for speed control"
      }
    ],
    "strategy_summary": "Aggressive team focused on early game pressure",
    "key_interactions": "Garchomp pairs well with Incineroar for Intimidate support"
  },
  "metadata": {
    "domain": "note.com",
    "processing_time": 12.34,
    "redaction_stats": {
      "total_redactions": 0
    }
  }
}
```

## 🚨 Error Handling

### Common Error Responses

**Rate Limited**
```json
{
  "error": true,
  "status_code": 429,
  "detail": "Rate limit exceeded. Maximum 5 analyses per hour per IP address."
}
```

**Provider Disabled**
```json
{
  "error": true,
  "status_code": 503,
  "detail": {
    "status": "provider_disabled",
    "message": "Gemini API is temporarily disabled. Please try again later."
  }
}
```

**Domain Not Allowed**
```json
{
  "error": true,
  "status_code": 403,
  "detail": "Domain not allowed - only approved Pokemon community sites permitted"
}
```

## 📊 Monitoring & Logging

### Log Files

The application generates structured JSON logs in the `logs/` directory:

- **`requests.jsonl`** - All incoming requests
- **`compliance.jsonl`** - Compliance decisions and checks
- **`errors.jsonl`** - Error occurrences and debugging info
- **`system.jsonl`** - System events and configuration changes

### Sample Log Entry

```json
{
  "request_id": "abc123-def456",
  "endpoint": "analyze",
  "hashed_ip": "a1b2c3d4e5f6g7h8",
  "session_id": "session-uuid",
  "timestamp": 1640995200,
  "decision": "allowed",
  "domain": "note.com",
  "processing_time": 12.34
}
```

## 🔍 Troubleshooting

### Common Issues

**❌ "Cannot connect to backend"**
- Ensure FastAPI server is running on port 8000
- Check CORS configuration if accessing from different origin

**❌ "Provider disabled"**
- Verify `PROVIDER_ENABLED_GEMINI=true` in .env
- Check Gemini API key is valid and has quota

**❌ "Rate limit exceeded"**
- Wait 1 hour for rate limit reset
- Check Redis connection for persistent rate limiting

**❌ "Domain not allowed"**
- Use approved Pokemon community sites only
- Check domain allowlist configuration

**❌ "robots.txt disallows crawling"**
- Respect website policies
- Try direct text input instead of URL

### Debug Mode

For detailed debugging:

```bash
# Enable debug logging
export ENVIRONMENT=development
export ENHANCED_LOGGING=true

# Run with verbose output
uvicorn app.backend.main:app --log-level debug
```

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run compliance tests only
pytest -m compliance
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## 📄 License & Legal

### Terms of Use

By using this application, you agree to:
1. **Age Requirement**: You are at least 18 years old
2. **Scope Limitation**: Use only for Pokemon VGC content analysis
3. **No Misuse**: Do not attempt to bypass safety controls
4. **Respect Policies**: Follow all applicable terms and policies

### Privacy Policy

**Data We Collect:**
- Session IDs (temporary, for rate limiting)
- Hashed IP addresses (privacy-preserving)
- Content processing metadata (no personal content stored)

**Data We Don't Collect:**
- Personal information
- Authentication credentials
- Persistent user tracking
- Content text (processed server-side, not stored)

**Data Retention:**
- Logs: 30 days maximum
- Session data: Cleared on browser close
- Rate limit data: 1 hour maximum

### Compliance Certifications

This application implements:
- ✅ **Google Gemini API Additional Terms** compliance
- ✅ **COPPA** (18+ age verification)
- ✅ **GDPR-ready** (minimal data collection)
- ✅ **Website robots.txt** respect
- ✅ **Ethical AI use** guidelines

## 🤝 Support & Contributing

### Getting Help

1. **Check this README** for common issues
2. **Review the logs** in `logs/` directory
3. **Open an issue** with detailed reproduction steps
4. **Contact support** at [support@example.com](mailto:support@example.com)

### Reporting Security Issues

🔒 **Security vulnerabilities** should be reported privately:
- Email: [security@example.com](mailto:security@example.com)
- Include detailed reproduction steps
- Allow 90 days for coordinated disclosure

### How to Appeal Suspensions

If your Google Gemini API project was suspended and you've implemented these compliance features:

1. **Document compliance** using this README as evidence
2. **Show implementation** of all required features
3. **Provide audit logs** demonstrating proper usage
4. **Submit appeal** through Google Cloud Console
5. **Reference this compliance implementation** in your appeal

### Contributing

We welcome contributions! Please:
1. **Fork** the repository
2. **Create** a feature branch
3. **Add tests** for new functionality
4. **Ensure compliance** with existing standards
5. **Submit** a pull request

---

## 📞 Contact Information

- **Project**: Pokemon VGC Article Translator
- **Version**: 2.0.0 (Compliance Compliant)
- **Support**: [support@example.com](mailto:support@example.com)
- **Security**: [security@example.com](mailto:security@example.com)
- **Repository**: [GitHub](https://github.com/your-org/pokemon-vgc-translator)

---

**Built with ❤️ for the Pokemon VGC community | Compliant with Google Gemini API Terms**