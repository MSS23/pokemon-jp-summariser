"""
Error recovery and retry mechanisms for Pokemon VGC Team Analysis
Provides robust error handling and automatic retry functionality
"""

import time
import logging
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
import streamlit as st
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential, 
    retry_if_exception_type,
    before_sleep_log
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorRecoveryManager:
    """Manages error recovery and retry logic for the application"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_error_time = {}
        self.retry_delays = {
            'api_timeout': 5,
            'network_error': 3,
            'rate_limit': 30,
            'server_error': 10,
            'general_error': 5
        }
    
    def classify_error(self, error: Exception) -> str:
        """Classify the type of error for appropriate handling"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'timed out' in error_str:
            return 'api_timeout'
        elif 'network' in error_str or 'connection' in error_str:
            return 'network_error'
        elif 'rate limit' in error_str or 'quota' in error_str:
            return 'rate_limit'
        elif 'server error' in error_str or '500' in error_str:
            return 'server_error'
        else:
            return 'general_error'
    
    def get_retry_delay(self, error_type: str) -> int:
        """Get the appropriate retry delay for an error type"""
        return self.retry_delays.get(error_type, 5)
    
    def should_retry(self, error: Exception, max_retries: int = 3) -> bool:
        """Determine if an operation should be retried"""
        error_type = self.classify_error(error)
        error_key = f"{error_type}_{time.time() // 3600}"  # Hourly bucket
        
        current_count = self.error_counts.get(error_key, 0)
        
        if current_count >= max_retries:
            return False
        
        self.error_counts[error_key] = current_count + 1
        return True
    
    def get_user_friendly_message(self, error: Exception) -> str:
        """Get a user-friendly error message"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str:
            return "The request took too long to complete. This might be due to high server load."
        elif 'network' in error_str or 'connection' in error_str:
            return "Network connection issue. Please check your internet connection and try again."
        elif 'rate limit' in error_str or 'quota' in error_str:
            return "API rate limit reached. Please wait a moment before trying again."
        elif 'server error' in error_str or '500' in error_str:
            return "Server is experiencing issues. Please try again in a few minutes."
        elif 'api key' in error_str or 'authentication' in error_str:
            return "Authentication error. Please check your API key configuration."
        else:
            return "An unexpected error occurred. Please try again or contact support if the issue persists."

def retry_with_exponential_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exceptions to retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise the exception
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    
                    # Log retry attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.1f} seconds..."
                    )
                    
                    # Show user feedback
                    if 'st' in globals():
                        st.warning(f"Attempt {attempt + 1} failed. Retrying in {delay:.1f} seconds...")
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def handle_api_error(error: Exception, operation: str = "API call") -> Dict[str, Any]:
    """
    Handle API errors and provide user-friendly feedback
    
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
    
    Returns:
        Dictionary with error information and recovery suggestions
    """
    error_manager = ErrorRecoveryManager()
    error_type = error_manager.classify_error(error)
    
    error_info = {
        'error_type': error_type,
        'message': error_manager.get_user_friendly_message(error),
        'operation': operation,
        'timestamp': time.time(),
        'retry_delay': error_manager.get_retry_delay(error_type),
        'should_retry': error_manager.should_retry(error)
    }
    
    # Log the error
    logger.error(f"{operation} failed: {error} (Type: {error_type})")
    
    return error_info

def display_error_with_recovery(error_info: Dict[str, Any], retry_callback: Optional[Callable] = None):
    """
    Display error information with recovery options
    
    Args:
        error_info: Error information from handle_api_error
        retry_callback: Optional callback function to retry the operation
    """
    st.error(f"**{error_info['operation']} Failed**")
    st.write(error_info['message'])
    
    # Show retry option if appropriate
    if error_info['should_retry'] and retry_callback:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("🔄 Retry", key=f"retry_{int(error_info['timestamp'])}"):
                with st.spinner("Retrying..."):
                    time.sleep(error_info['retry_delay'])
                    retry_callback()
        
        with col2:
            st.write(f"⏱️ Wait {error_info['retry_delay']} seconds before retrying")
    
    # Show troubleshooting tips
    st.info("""
    **Troubleshooting Tips:**
    - Check your internet connection
    - Verify your API key is correct
    - Try again in a few minutes
    - If the problem persists, contact support
    """)

def create_progress_with_error_handling():
    """
    Create a progress indicator with error handling capabilities
    
    Returns:
        Tuple of (progress_bar, status_text, error_container)
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    error_container = st.container()
    
    return progress_bar, status_text, error_container

def update_progress_with_error_handling(
    progress_bar, 
    status_text, 
    error_container, 
    progress: float, 
    message: str,
    error: Optional[Exception] = None
):
    """
    Update progress with error handling
    
    Args:
        progress_bar: Streamlit progress bar
        status_text: Streamlit status text element
        error_container: Streamlit container for errors
        progress: Progress value (0-100)
        message: Status message
        error: Optional error to display
    """
    try:
        progress_bar.progress(progress / 100)
        status_text.text(message)
        
        if error:
            with error_container:
                error_info = handle_api_error(error, "Analysis")
                display_error_with_recovery(error_info)
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

# Pre-configured retry decorators for common use cases
retry_api_call = retry_with_exponential_backoff(
    max_attempts=3,
    base_delay=2.0,
    max_delay=30.0,
    exceptions=(Exception,)
)

retry_network_call = retry_with_exponential_backoff(
    max_attempts=5,
    base_delay=1.0,
    max_delay=60.0,
    exceptions=(ConnectionError, TimeoutError, OSError)
)

retry_rate_limited = retry_with_exponential_backoff(
    max_attempts=2,
    base_delay=30.0,
    max_delay=120.0,
    exceptions=(Exception,)
)
