"""
Server-side Gemini API client with security and compliance features
API keys are NEVER exposed to frontend - server-side only
"""

import os
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
import time
import hashlib

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# For error handling and structured responses
from google.api_core.exceptions import ResourceExhausted, PermissionDenied, InvalidArgument

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors"""
    def __init__(self, message: str, error_type: str = "unknown", retry_after: int = None):
        super().__init__(message)
        self.error_type = error_type
        self.retry_after = retry_after

class GeminiClient:
    """
    Server-side Gemini API client with compliance and safety controls
    Handles all LLM interactions with proper safety settings and token management
    """

    def __init__(self):
        """Initialize the Gemini client with API key from environment"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required but not set. "
                "This key must be configured server-side only."
            )

        # Configure the Gemini client
        genai.configure(api_key=self.api_key)

        # Initialize the model with safety settings
        self.model_name = "gemini-1.5-flash"  # Using latest stable model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self._get_safety_settings()
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info(f"GeminiClient initialized with model: {self.model_name}")

    def _get_safety_settings(self) -> Dict[HarmCategory, HarmBlockThreshold]:
        """
        Get safety settings for Gemini API calls
        Using conservative settings to comply with Generative AI Prohibited Use Policy
        """
        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

    def _create_pokemon_analysis_prompt(self, content: str) -> str:
        """
        Create a focused prompt for Pokemon VGC analysis
        Ensures the AI stays within the intended scope
        """
        return f"""You are a Pokemon VGC (Video Game Championships) analysis expert. Your task is to analyze Japanese Pokemon tournament reports and team compositions.

SCOPE: Only analyze Pokemon VGC competitive content. If the content is not about Pokemon competitive play, return an error.

CONTENT TO ANALYZE:
{content}

INSTRUCTIONS:
1. Extract team information including Pokemon names, items, abilities, moves, and EV spreads
2. Translate Japanese Pokemon names to English using official names
3. Provide strategic analysis of the team composition
4. Format the response as structured JSON

SAFETY REQUIREMENTS:
- Only process Pokemon VGC content
- Do not process personal information, contact details, or unrelated content
- Focus solely on competitive Pokemon strategy and team analysis

Please provide a comprehensive analysis in the following JSON format:
{{
    "title": "Article title or team name",
    "regulation": "VGC regulation (Series 1, 2, etc.)",
    "pokemon_team": [
        {{
            "name": "Pokemon name in English",
            "item": "Item name",
            "ability": "Ability name",
            "nature": "Nature name",
            "ev_spread": {{
                "HP": 0,
                "Attack": 0,
                "Defense": 0,
                "Special Attack": 0,
                "Special Defense": 0,
                "Speed": 0
            }},
            "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
            "analysis": "Strategic role and explanation"
        }}
    ],
    "strategy_summary": "Overall team strategy and win conditions",
    "key_interactions": "Important Pokemon interactions and synergies",
    "tournament_results": "Tournament performance if mentioned"
}}"""

    def _extract_tokens_used(self, response) -> int:
        """Extract token usage from Gemini response metadata"""
        try:
            if hasattr(response, 'usage_metadata'):
                return (response.usage_metadata.prompt_token_count or 0) + (response.usage_metadata.candidates_token_count or 0)
            return 0
        except Exception:
            return 0

    def _handle_api_error(self, e: Exception) -> GeminiAPIError:
        """
        Convert Gemini API errors into user-friendly error messages
        """
        error_message = str(e).lower()

        if isinstance(e, ResourceExhausted):
            if "quota" in error_message or "limit" in error_message:
                return GeminiAPIError(
                    "API quota exceeded. Please try again later or contact support to upgrade your plan.",
                    error_type="quota_exceeded",
                    retry_after=3600  # Suggest 1 hour retry
                )
            else:
                return GeminiAPIError(
                    "Rate limit reached. Please wait a moment and try again.",
                    error_type="rate_limit",
                    retry_after=60  # Suggest 1 minute retry
                )

        elif isinstance(e, PermissionDenied):
            return GeminiAPIError(
                "API access denied. Please check your API key configuration or contact support.",
                error_type="permission_denied"
            )

        elif isinstance(e, InvalidArgument):
            return GeminiAPIError(
                "Invalid request. The content may be too long or contain unsupported characters.",
                error_type="invalid_request"
            )

        else:
            # Generic error handling
            return GeminiAPIError(
                f"API request failed: {str(e)}. Please try again or contact support if the issue persists.",
                error_type="api_error"
            )

    async def analyze(self, content: str, options: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Analyze Pokemon VGC content using Gemini AI

        Args:
            content: The content to analyze (after safety filtering and PII redaction)
            options: Analysis options from the request
            session_id: Session ID for request tracing (NOT PII)

        Returns:
            Dictionary with analysis results and metadata

        Raises:
            GeminiAPIError: For API-related errors with user-friendly messages
        """
        start_time = time.time()

        try:
            # Create the analysis prompt
            prompt = self._create_pokemon_analysis_prompt(content)

            # Add request headers for traceability (session ID only, no PII)
            request_headers = {
                "x-session-id": session_id,
                "x-request-timestamp": str(int(time.time())),
                "x-content-hash": hashlib.sha256(content.encode()).hexdigest()[:16]
            }

            self.logger.info(f"Starting Gemini analysis for session {session_id}")

            # Generate content with safety settings
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Low temperature for consistent, factual responses
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=4000,  # Reasonable limit for team analysis
                        response_mime_type="application/json"  # Request JSON format
                    )
                )
            )

            # Extract response text
            if not response.text:
                raise GeminiAPIError(
                    "Empty response from Gemini API. The content may have been filtered for safety.",
                    error_type="empty_response"
                )

            # Parse JSON response
            try:
                analysis_result = json.loads(response.text)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract content or return structured error
                self.logger.warning(f"JSON parsing failed: {e}, raw response: {response.text[:500]}")
                analysis_result = {
                    "error": "Response parsing failed",
                    "raw_content": response.text[:1000],  # Truncate for safety
                    "parsing_error": True
                }

            # Add metadata
            tokens_used = self._extract_tokens_used(response)
            processing_time = time.time() - start_time

            result = {
                **analysis_result,
                "tokens_used": tokens_used,
                "processing_time": processing_time,
                "model_used": self.model_name,
                "session_id": session_id  # For tracing, not PII
            }

            self.logger.info(
                f"Gemini analysis completed for session {session_id}: "
                f"{tokens_used} tokens, {processing_time:.2f}s"
            )

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(
                f"Gemini analysis failed for session {session_id}: {str(e)} "
                f"(processing time: {processing_time:.2f}s)"
            )

            # Convert to user-friendly error
            api_error = self._handle_api_error(e)
            raise api_error

    def health_check(self) -> Dict[str, Any]:
        """
        Check if the Gemini API is accessible and configured correctly

        Returns:
            Dictionary with health status information
        """
        try:
            # Simple test request to verify API access
            test_response = self.model.generate_content(
                "Respond with exactly: 'API_HEALTH_OK'",
                generation_config=genai.types.GenerationConfig(
                    temperature=0,
                    max_output_tokens=10
                )
            )

            if test_response.text and "API_HEALTH_OK" in test_response.text:
                return {
                    "status": "healthy",
                    "model": self.model_name,
                    "api_accessible": True,
                    "timestamp": int(time.time())
                }
            else:
                return {
                    "status": "degraded",
                    "model": self.model_name,
                    "api_accessible": True,
                    "issue": "Unexpected response format",
                    "timestamp": int(time.time())
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "model": self.model_name,
                "api_accessible": False,
                "error": str(e),
                "timestamp": int(time.time())
            }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Gemini model configuration

        Returns:
            Dictionary with model configuration details
        """
        return {
            "model_name": self.model_name,
            "safety_settings": {
                category.name: threshold.name
                for category, threshold in self._get_safety_settings().items()
            },
            "api_key_configured": bool(self.api_key),
            "api_key_prefix": self.api_key[:8] + "..." if self.api_key else "Not configured"
        }