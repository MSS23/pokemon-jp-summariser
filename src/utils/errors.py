"""
Custom exceptions and user-friendly error messages for the Pokemon VGC Analysis app.
"""

from typing import Dict, Optional


class APILimitError(Exception):
    """Custom exception for API rate limit and quota errors"""
    def __init__(self, message: str, error_type: str = "unknown", retry_after: Optional[int] = None):
        super().__init__(message)
        self.error_type = error_type  # 'rate_limit', 'quota_exceeded', 'service_disabled', etc.
        self.retry_after = retry_after


def get_user_friendly_api_error_message(error: APILimitError) -> Dict[str, str]:
    """
    Convert API limit errors into user-friendly messages with clear guidance

    Returns:
        Dict with 'title', 'message', 'icon', and 'tips' keys
    """
    if error.error_type == "rate_limit":
        retry_minutes = (error.retry_after or 60) // 60
        retry_text = f"{retry_minutes} minute{'s' if retry_minutes != 1 else ''}" if retry_minutes > 0 else "a moment"

        return {
            "icon": "⏱️",
            "title": "API Rate Limit Reached",
            "message": f"""You've made too many requests in a short time. The Google Gemini API has limits to ensure fair usage for everyone.

**What happened?** The API temporarily blocked new requests to prevent overload.

**What you can do:**
- **Wait {retry_text}** and try again - the limit resets automatically
- **Use shorter articles** to reduce processing time per request
- **Spread out your analyses** rather than doing many at once

This is completely normal with API usage - just take a quick break and try again!""",
            "tips": [
                "Rate limits reset automatically after a short wait",
                "Shorter content = faster processing = fewer API calls",
                "Free tier has stricter limits than paid accounts"
            ]
        }

    elif error.error_type == "quota_exceeded":
        return {
            "icon": "📊",
            "title": "API Limit Reached",
            "message": """**You've hit your daily API limit!** The Google Gemini free tier allows 250 requests per day for VGC analysis.

**What this means:**
- You've successfully analyzed many Pokemon articles today
- Your daily quota is now used up (this is normal with heavy usage)
- The limit automatically resets at midnight Pacific Time

**What you can do right now:**
- **Wait until tomorrow** - your quota resets automatically
- **Save any current analysis** - your results stay until page refresh
- **Try again in a few hours** if it's late in the day

**For more analysis capacity:**
- Upgrade to a paid Google Cloud plan for thousands of daily requests
- Shorter articles use less quota, so focus on concise content

Don't worry - this just means you've been actively using the analysis tool!""",
            "tips": [
                "Free tier = 250 requests daily (plenty for most users)",
                "Quota resets automatically at midnight Pacific",
                "Paid plans offer 50,000+ daily requests",
                "Your current session data is safely preserved"
            ]
        }

    elif error.error_type == "authentication":
        return {
            "icon": "🔐",
            "title": "API Key Authentication Failed",
            "message": """There's an issue with your Google API key configuration.

**What happened?** The API key couldn't be verified or is invalid.

**What you can do:**
- **Check your API key** in the Google Cloud Console
- **Verify the key has permissions** for the Gemini API
- **Make sure it's correctly set** in your environment or configuration
- **Try regenerating the key** if the issue persists

Contact support if you continue having authentication issues.""",
            "tips": [
                "API keys must have Gemini API permissions enabled",
                "Keys can expire or be revoked in Google Cloud Console",
                "Environment variables need to be set correctly"
            ]
        }

    elif error.error_type == "service_disabled":
        return {
            "icon": "🔧",
            "title": "Gemini API Service Not Enabled",
            "message": """The Gemini API service isn't enabled for your Google Cloud project.

**What happened?** The API needs to be activated in your Google Cloud Console.

**What you can do:**
- **Go to Google Cloud Console** -> APIs & Services -> Library
- **Search for "Gemini API"** or "Generative Language API"
- **Click "Enable"** on the API service
- **Wait a few minutes** for the service to activate
- **Try your analysis again**

This is a one-time setup step for new projects.""",
            "tips": [
                "API enablement is required once per Google Cloud project",
                "Changes can take a few minutes to take effect",
                "Free tier includes generous Gemini API usage"
            ]
        }

    else:
        return {
            "icon": "⚠️",
            "title": "API Error Occurred",
            "message": f"""An unexpected API error occurred: {str(error)}

**What you can do:**
- **Try again** in a moment - temporary issues often resolve quickly
- **Check your internet connection**
- **Try with shorter content** if the article was very long
- **Contact support** if the issue persists

The error details have been logged for troubleshooting.""",
            "tips": [
                "Many API errors are temporary and resolve quickly",
                "Network issues can cause API failures",
                "Shorter content is more reliable to process"
            ]
        }
