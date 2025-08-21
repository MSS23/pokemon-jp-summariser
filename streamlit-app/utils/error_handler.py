"""
Comprehensive error handling utilities for the Pokemon Translation app
"""

import json
import logging
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd
import streamlit as st

from .logger import get_api_logger


class ApplicationError(Exception):
    """Base application error with context"""

    def __init__(
        self, message: str, error_code: str = None, context: Dict[str, Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()


class APIError(ApplicationError):
    """API-related errors"""

    def __init__(
        self, message: str, status_code: int = None, response_data: Any = None
    ):
        super().__init__(
            message,
            "API_ERROR",
            {"status_code": status_code, "response_data": response_data},
        )


class ValidationError(ApplicationError):
    """Data validation errors"""

    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class ParsingError(ApplicationError):
    """Pokemon parsing errors"""

    def __init__(self, message: str, url: str = None, stage: str = None):
        super().__init__(message, "PARSING_ERROR", {"url": url, "parsing_stage": stage})


def log_error(error: Exception, context: Dict[str, Any] = None) -> str:
    """Log error with context and return error ID"""
    logger = get_api_logger()
    error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"

    error_info = {
        "error_id": error_id,
        "error_type": type(error).__name__,
        "message": str(error),
        "timestamp": datetime.now().isoformat(),
        "context": context or {},
        "traceback": traceback.format_exc(),
    }

    logger.error(f"Error {error_id}: {error_info}")
    return error_id


def handle_streamlit_error(error: Exception, user_message: str = None) -> None:
    """Display user-friendly error in Streamlit with error ID"""
    error_id = log_error(error)

    if user_message is None:
        if isinstance(error, APIError):
            user_message = "API service is temporarily unavailable. Please try again in a few minutes."
        elif isinstance(error, ValidationError):
            user_message = f"Invalid input: {error.message}"
        elif isinstance(error, ParsingError):
            user_message = "Unable to parse the article content. Please check the URL and try again."
        else:
            user_message = "An unexpected error occurred. Our team has been notified."

    st.markdown(
        f"""
    <div style="
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #f87171;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    ">
        <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 24px; margin-right: 12px;">⚠️</span>
            <h3 style="margin: 0; color: #dc2626; font-size: 1.2rem; font-weight: 600;">
                Something went wrong
            </h3>
        </div>
        <p style="margin: 0 0 12px 0; color: #7f1d1d; font-size: 1rem; line-height: 1.5;">
            {user_message}
        </p>
        <details style="margin-top: 12px;">
            <summary style="cursor: pointer; color: #991b1b; font-size: 0.9rem;">
                Error Details (Error ID: {error_id})
            </summary>
            <div style="
                background: #ffffff;
                border-radius: 6px;
                padding: 12px;
                margin-top: 8px;
                font-family: monospace;
                font-size: 0.8rem;
                color: #374151;
                max-height: 200px;
                overflow-y: auto;
            ">
                <strong>Type:</strong> {type(error).__name__}<br>
                <strong>Message:</strong> {str(error)}<br>
                <strong>Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            </div>
        </details>
    </div>
    """,
        unsafe_allow_html=True,
    )


def error_boundary(func: Callable) -> Callable:
    """Decorator to wrap functions with error handling"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApplicationError as e:
            handle_streamlit_error(e)
            return None
        except Exception as e:
            handle_streamlit_error(e)
            return None

    return wrapper


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator to retry functions with exponential backoff"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)
                        logger = get_api_logger()
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}"
                        )
                        import time

                        time.sleep(delay)
                    else:
                        logger = get_api_logger()
                        logger.error(f"All {max_retries} attempts failed: {e}")

            # If we get here, all retries failed
            raise last_exception

        return wrapper

    return decorator


class ErrorReporter:
    """Collect and report error statistics"""

    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 100

    def record_error(self, error: Exception, context: Dict[str, Any] = None):
        """Record an error for statistics"""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        error_record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": str(error),
            "context": context or {},
        }

        self.recent_errors.append(error_record)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)

    def get_error_summary(self) -> Dict[str, Any]:
        """Get error statistics summary"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts.copy(),
            "recent_errors_count": len(self.recent_errors),
            "most_common_error": (
                max(self.error_counts.items(), key=lambda x: x[1])[0]
                if self.error_counts
                else None
            ),
        }

    def display_error_dashboard(self):
        """Display error dashboard in Streamlit"""
        if not self.error_counts:
            st.success("🎉 No errors recorded!")
            return

        summary = self.get_error_summary()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Errors", summary["total_errors"])

        with col2:
            st.metric("Error Types", len(summary["error_types"]))

        with col3:
            if summary["most_common_error"]:
                st.metric("Most Common", summary["most_common_error"])

        # Error type breakdown
        if summary["error_types"]:
            st.subheader("Error Breakdown")
            error_df = pd.DataFrame(
                list(summary["error_types"].items()), columns=["Error Type", "Count"]
            )
            st.bar_chart(error_df.set_index("Error Type"))

        # Recent errors
        if self.recent_errors:
            st.subheader("Recent Errors")
            recent_df = pd.DataFrame(self.recent_errors[-10:])  # Last 10 errors
            st.dataframe(recent_df)


# Global error reporter instance
error_reporter = ErrorReporter()


def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely execute a function and handle any errors"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_reporter.record_error(
            e, {"function": func.__name__, "args": str(args)[:100]}
        )
        handle_streamlit_error(e)
        return None


def handle_api_quota_error(error_msg: str, retry_count: int = 0) -> dict:
    """
    Handle API quota exceeded errors with helpful suggestions and fallback options

    Args:
        error_msg: The error message from the API
        retry_count: Current retry attempt number

    Returns:
        dict: Error handling result with suggestions and fallback options
    """
    if "quota exceeded" in error_msg.lower() or "quota" in error_msg.lower():
        # Check if it's a daily quota limit
        if "daily" in error_msg.lower() or "per day" in error_msg.lower():
            return {
                "error_type": "daily_quota_exceeded",
                "message": "Your daily limit has been reached",
                "suggestions": [
                    "Wait until tomorrow when your limit resets",
                    "Upgrade to a paid plan for higher limits",
                    "Use cached results if available",
                    "Try a different article URL",
                ],
                "fallback_options": [
                    "Check cache for previous analyses",
                    "Use basic text parsing without AI analysis",
                    "Wait for limit reset",
                ],
                "retry_after": "24 hours",
                "can_retry": False,
            }

        # Check if it's a rate limit (can retry)
        elif (
            "rate limit" in error_msg.lower()
            or "too many requests" in error_msg.lower()
        ):
            return {
                "error_type": "rate_limit",
                "message": "Rate limit exceeded",
                "suggestions": [
                    "Wait a few minutes before trying again",
                    "Reduce the frequency of requests",
                ],
                "fallback_options": [
                    "Wait and retry",
                    "Check cache for previous results",
                ],
                "retry_after": "5-10 minutes",
                "can_retry": True,
            }

        # Generic quota error
        else:
            return {
                "error_type": "quota_exceeded",
                "message": "Your limit has been reached",
                "suggestions": [
                    "Check your usage limits",
                    "Upgrade your plan if needed",
                    "Wait before making more requests",
                ],
                "fallback_options": [
                    "Use cached results",
                    "Try basic parsing",
                    "Wait and retry later",
                ],
                "retry_after": "1 hour",
                "can_retry": True,
            }

    return {
        "error_type": "unknown",
        "message": "Unknown error occurred",
        "suggestions": ["Check the error details above"],
        "fallback_options": ["Try again later"],
        "retry_after": "Unknown",
        "can_retry": False,
    }


def create_quota_error_ui(error_info: dict) -> str:
    """
    Create a user-friendly UI for quota exceeded errors

    Args:
        error_info: Error information from handle_api_quota_error

    Returns:
        str: HTML formatted error message with suggestions
    """
    suggestions_html = "".join(
        [f"<li>{suggestion}</li>" for suggestion in error_info["suggestions"]]
    )
    fallback_html = "".join(
        [f"<li>{option}</li>" for option in error_info["fallback_options"]]
    )

    # Create HTML content without problematic newlines
    html_content = (
        f'<div class="quota-error-card" style="padding: 20px; border-radius: 10px; '
        f"background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); "
        f'border: 2px solid #ffc107; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">'
        f'<h3 style="color: #856404; margin-top: 0;">🚫 {error_info["message"]}</h3>'
        f'<div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">'
        f'<h4 style="color: #856404; margin-top: 0;">💡 Suggestions:</h4>'
        f'<ul style="margin: 10px 0; padding-left: 20px;">{suggestions_html}</ul>'
        f"</div>"
        f'<div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">'
        f'<h4 style="color: #856404; margin-top: 0;">🔄 Fallback Options:</h4>'
        f'<ul style="margin: 10px 0; padding-left: 20px;">{fallback_html}</ul>'
        f"</div>"
        f'<div style="background: #e3f2fd; padding: 10px; border-radius: 5px; '
        f'border-left: 4px solid #2196f3; margin-top: 15px;">'
        f'<strong>⏰ Retry After:</strong> {error_info["retry_after"]}'
    )

    # Add conditional retry information
    if "can_retry" in error_info:
        html_content += f'<br><strong>🔄 Can Retry:</strong> {"Yes" if error_info["can_retry"] else "No"}'

    html_content += "</div></div>"

    return html_content


def create_simple_test_html() -> str:
    """
    Create a simple test HTML to verify basic rendering works

    Returns:
        str: Simple test HTML
    """
    return '<div style="background: #e3f2fd; padding: 20px; border-radius: 10px; border: 2px solid #2196f3;"><h3 style="color: #1976d2;">Test HTML</h3><p>This is a simple test to verify HTML rendering works.</p></div>'


def create_minimal_test_html() -> str:
    """
    Create a minimal test HTML with very basic styling

    Returns:
        str: Minimal test HTML
    """
    return (
        '<div style="background: red; color: white; padding: 10px;">MINIMAL TEST</div>'
    )


def validate_html_content(html_content: str) -> dict:
    """
    Validate HTML content for potential issues

    Args:
        html_content: HTML string to validate

    Returns:
        dict: Validation results
    """
    import re

    results = {
        "length": len(html_content),
        "contains_newlines": "\n" in html_content,
        "contains_tabs": "\t" in html_content,
        "contains_special_chars": any(ord(c) > 127 for c in html_content),
        "starts_with_div": html_content.strip().startswith("<div"),
        "ends_with_div": html_content.strip().endswith("</div>"),
        "balanced_tags": html_content.count("<div") == html_content.count("</div>"),
        "has_style_attr": "style=" in html_content,
        "clean_length": len(
            re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", html_content)
        ),
    }

    return results
