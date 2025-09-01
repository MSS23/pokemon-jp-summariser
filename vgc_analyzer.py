"""
VGC Analysis module for Pokemon team analysis using Google Gemini
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
import google.generativeai as genai

from config import Config
from cache_manager import cache
from utils import validate_url


class GeminiVGCAnalyzer:
    """Pokemon VGC analyzer using Google Gemini AI"""

    def __init__(self):
        """Initialize the analyzer with Gemini configuration"""
        self.api_key = Config.get_google_api_key()
        genai.configure(api_key=self.api_key)

        # Configure the model
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Generation config for consistent output
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8000,
        }

    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is accessible and potentially contains VGC content

        Args:
            url: URL to validate

        Returns:
            True if URL appears valid for analysis
        """
        if not validate_url(url):
            return False

        try:
            # Check if URL is accessible
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def scrape_article(self, url: str) -> Optional[str]:
        """
        Scrape article content from URL

        Args:
            url: URL to scrape

        Returns:
            Article content as string or None if failed
        """
        if not self.validate_url(url):
            raise ValueError("Invalid or inaccessible URL")

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/91.0.4472.124 Safari/537.36"
                )
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Remove unwanted elements
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside"]
            ):
                element.decompose()

            # Try to find main content
            main_content = None
            content_selectors = [
                "main",
                "article",
                ".content",
                ".post-content",
                ".entry-content",
                "#content",
                ".main-content",
                ".article-body",
                ".post-body",
            ]

            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break

            if not main_content:
                main_content = soup.find("body")

            if main_content:
                text = main_content.get_text(separator=" ", strip=True)
                # Clean up excessive whitespace
                text = re.sub(r"\s+", " ", text)
                return text[:8000]  # Limit content length

        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch article: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to parse article: {str(e)}")

        return None

    def _get_analysis_prompt(self) -> str:
        """Get the comprehensive VGC analysis prompt"""
        return '''
You are a Pokemon VGC expert analyst.
Your task is to analyze Japanese Pokemon VGC articles and provide
comprehensive analysis including team composition, strategy explanation,
and accurate translations.

CRITICAL REQUIREMENTS:
1. ALWAYS provide a valid JSON response
2. Include EV spreads for ALL Pokemon (use "Not specified" if missing)
3. Provide strategic explanations for EV choices
4. Translate all Japanese text to English
5. Ensure team composition makes sense for VGC format

RESPONSE FORMAT (MUST BE VALID JSON):
{
  "title": "English translation of article title",
  "author": "Author name if available",
  "tournament_context": "Tournament or context information",
  "overall_strategy": "Main team strategy and approach",
  "regulation": "VGC regulation (A, B, C, etc.)",
  "pokemon_team": [
    {
      "name": "Pokemon Name",
      "ability": "Ability Name",
      "held_item": "Item Name",
      "tera_type": "Type",
      "nature": "Nature Name",
      "evs": "252/0/0/252/4/0 format or descriptive text",
      "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
      "role": "Role description",
      "ev_explanation": "Detailed explanation of EV spread reasoning"
    }
  ],
  "team_synergy": "How the team works together",
  "strengths": ["Strength 1", "Strength 2", "Strength 3"],
  "weaknesses": ["Weakness 1", "Weakness 2"],
  "meta_relevance": "Relevance to current VGC meta",
  "translation_notes": "Any important translation notes"
}

EV ANALYSIS REQUIREMENTS:
- Always provide EV spreads in 252/0/0/252/4/0 format when possible
- If exact numbers aren't given, provide reasonable estimates
- Explain speed benchmarks (e.g., "outspeeds base 100 Pokemon")
- Mention survival calculations (e.g., "survives 85% damage from X")
- Include offensive benchmarks (e.g., "guaranteed 2HKO on Y")
- Use "Not specified" only if absolutely no EV information is available

TRANSLATION GUIDELINES:
- Translate Pokemon names to English
- Translate move names to English
- Translate item names to English
- Keep ability names in standard English format
- Preserve strategic terminology accurately

Please analyze the following content and provide your response in the exact JSON format specified above:
'''

    def analyze_article(self, content: str, url: str = None) -> Dict[str, Any]:
        """
        Analyze article content using Gemini AI

        Args:
            content: Article content to analyze
            url: Optional URL for context

        Returns:
            Analysis result as dictionary
        """
        if not content or len(content.strip()) < 50:
            raise ValueError(
                "Content too short or empty for meaningful analysis"
            )

        # Check cache first
        cached_result = cache.get(content, url)
        if cached_result:
            return cached_result

        try:
            prompt = self._get_analysis_prompt()
            full_prompt = f"{prompt}\n\nCONTENT TO ANALYZE:\n{content}"

            # Generate response
            response = self.model.generate_content(
                full_prompt, generation_config=self.generation_config
            )

            if not response.text:
                raise ValueError("Empty response from Gemini API")

            # Parse JSON response
            result = self._parse_response(response.text)

            # Validate and clean the result
            result = self._validate_and_clean_result(result)

            # Cache the result
            cache.set(content, result, url)

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {str(e)}")
        except Exception as e:
            raise ValueError(f"Analysis failed: {str(e)}")

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini"""
        # Clean the response text
        response_text = response_text.strip()

        # Find JSON content (handle cases where AI adds extra text)
        json_match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON block without markdown
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text

        return json.loads(json_text)

    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the analysis result"""
        # Ensure required fields exist
        required_fields = ["title", "pokemon_team", "overall_strategy"]

        for field in required_fields:
            if field not in result:
                result[field] = "Not specified"

        # Clean and validate Pokemon team
        if "pokemon_team" in result:
            cleaned_team = []
            for pokemon in result["pokemon_team"]:
                cleaned_pokemon = self._clean_pokemon_data(pokemon)
                if cleaned_pokemon:
                    cleaned_team.append(cleaned_pokemon)
            result["pokemon_team"] = cleaned_team[:6]  # Max 6 Pokemon

        # Ensure lists exist
        for list_field in ["strengths", "weaknesses"]:
            if list_field not in result or not isinstance(result[list_field], list):
                result[list_field] = []

        return result

    def _clean_pokemon_data(self, pokemon: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate individual Pokemon data"""
        if not pokemon.get("name"):
            return None

        # Set defaults for missing fields
        defaults = {
            "name": "Unknown Pokemon",
            "ability": "Not specified",
            "held_item": "Not specified",
            "tera_type": "Not specified",
            "nature": "Not specified",
            "evs": "Not specified",
            "moves": [],
            "role": "Not specified",
            "ev_explanation": "Not specified",
        }

        # Apply defaults
        for key, default_value in defaults.items():
            if key not in pokemon or not pokemon[key]:
                pokemon[key] = default_value

        # Ensure moves is a list with max 4 moves
        if not isinstance(pokemon["moves"], list):
            pokemon["moves"] = []
        pokemon["moves"] = pokemon["moves"][:4]

        # Pad moves list to 4 if needed
        while len(pokemon["moves"]) < 4:
            pokemon["moves"].append("Not specified")

        return pokemon
