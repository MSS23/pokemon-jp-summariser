import json
import os
import sys
from typing import Any, Dict

from utils.logger import get_api_logger


def summarize_article(url: str) -> Dict[str, Any]:
    """
    Function to summarize an article from a given URL.
    This is a simplified version that can be called from the FastAPI backend.
    """
    try:
        # Import the Gemini summary function
        from gemini_summary import llm_summary_gemini

        # Call the Gemini summary function
        result = llm_summary_gemini(url)

        # Process and return the result in the expected format
        return {
            "title": result.get("title", "Translated Article"),
            "summary": result.get("summary", "No summary available"),
            "teams": result.get("teams", []),
            "original_text": result.get("original_text", ""),
            "translated_text": result.get("translated_text", ""),
            "confidence": result.get("confidence", 95),
            "processing_time": result.get("processing_time", 0),
        }

    except Exception as e:
        logger = get_api_logger()
        logger.error(f"Error in summarize_article: {str(e)}")
        return {
            "error": str(e),
            "title": "Error",
            "summary": f"An error occurred while processing the article: {str(e)}",
            "teams": [],
        }


# For testing
if __name__ == "__main__":
    test_url = "https://example.com/pokemon-article"
    result = summarize_article(test_url)
    print(json.dumps(result, indent=2))
