"""
VGC Analysis module for Pokemon team analysis using Google Gemini
"""

import json
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any
import google.generativeai as genai

from config import Config, POKEMON_NAME_TRANSLATIONS
from cache_manager import cache
from utils import validate_url
from image_analyzer import (
    extract_images_from_url,
    filter_vgc_images,
    analyze_image_with_vision,
    extract_ev_spreads_from_image_analysis
)


class GeminiVGCAnalyzer:
    """Pokemon VGC analyzer using Google Gemini AI"""

    def __init__(self):
        """Initialize the analyzer with Gemini configuration"""
        self.api_key = Config.get_google_api_key()
        genai.configure(api_key=self.api_key)

        # Configure the text model with Gemini 2.5 Flash (optimal balance: advanced quality + 5x higher quota)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Configure the vision model with Flash-Lite (cost-effective for image processing)
        self.vision_model = genai.GenerativeModel("gemini-2.5-flash-lite")

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
        """Get the comprehensive VGC analysis prompt with enhanced Pokemon identification"""
        return '''
You are a Pokemon VGC expert analyst with extensive knowledge of Pokemon identification and naming conventions.
Your task is to analyze Japanese Pokemon VGC articles and provide comprehensive analysis including team composition, strategy explanation, and accurate translations.

CRITICAL REQUIREMENTS:
1. ALWAYS provide a valid JSON response
2. Include EV spreads for ALL Pokemon (use "Not specified" if missing)
3. Provide strategic explanations for EV choices
4. Translate all Japanese text to English with PERFECT Pokemon identification
5. Ensure team composition makes sense for VGC format
6. Use EXACT Pokemon names with proper forms and spellings
7. EXTRACT regulation information from the article content - DO NOT ASSUME

POKEMON IDENTIFICATION REQUIREMENTS:
CRITICAL: You must be extremely careful with Pokemon identification. Here are common errors to avoid:

DO NOT CONFUSE THESE POKEMON:
- Zamazenta ≠ Zacian (ザマゼンタ = Zamazenta, ザシアン = Zacian)
- Chi-Yu ≠ Chien-Pao (チオンジェン = Chi-Yu, パオジアン = Chien-Pao)
- Ting-Lu ≠ Wo-Chien (ディンルー = Ting-Lu, イーユイ = Wo-Chien)

CORRECT POKEMON FORMS:
- Landorus-Therian (not "Landorus-T" or "Landorus T")
- Thundurus-Therian (not "Thundurus-T" or "Thundurus T")  
- Tornadus-Therian (not "Tornadus-T" or "Tornadus T")
- Calyrex-Shadow (not "Shadow Calyrex" or "Calyrex Shadow")
- Calyrex-Ice (not "Ice Calyrex" or "Calyrex Ice")
- Urshifu-Rapid-Strike (not "Urshifu Rapid" or "Rapid Strike Urshifu")
- Urshifu-Single-Strike (not "Urshifu Single" or "Single Strike Urshifu")

PARADOX POKEMON - CRITICAL NAMING:
- Iron Valiant (NEVER "Iron-Valiant-Therian", "Iron-Valian-Therian", "Iron Valian", or "Iron-Valian")
- Flutter Mane (not "Flutter-Mane")
- Iron Moth (not "Iron-Moth")
- Sandy Shocks (not "Sandy-Shocks")
- Roaring Moon (not "Roaring-Moon")

TREASURES OF RUIN - CORRECT NAMES:
- Chien-Pao (パオジアン) - The cat-like legendary
- Chi-Yu (チオンジェン) - The fish-like legendary  
- Ting-Lu (ディンルー) - The deer-like legendary
- Wo-Chien (イーユイ) - The snail-like legendary

REGIONAL FORMS:
- Use format: "Pokemon-Region" (e.g., "Zapdos-Galar", "Marowak-Alola")
- For Hisuian forms: "Pokemon-Hisui" (e.g., "Zoroark-Hisui")

REGULATION DETECTION REQUIREMENTS:
ULTRA CRITICAL: Extract the VGC regulation ONLY and EXCLUSIVELY from the article text content. DO NOT INFER OR GUESS based on team composition.

**STRICT ARTICLE-ONLY DETECTION:**
You MUST only look for explicit regulation mentions in the article text. Look for:

**Japanese Regulation Terms (only if explicitly stated in text):**
- "レギュレーション" (Regulation) + letter/number
- "ルール" (Rules) + regulation identifier
- "シリーズ" (Series) + number
- "シーズン" (Season) + identifier

**English Regulation Indicators (only if explicitly stated in text):**
- "Regulation A", "Regulation B", "Regulation C", etc.
- "Series 1", "Series 2", etc.
- "VGC 2024", "VGC 2025" + regulation
- Tournament format mentions with specific regulation

**FORBIDDEN - DO NOT DO THESE:**
- DO NOT infer regulation from team composition
- DO NOT guess based on restricted legendary count
- DO NOT assume regulation from Pokemon availability
- DO NOT use team analysis to determine regulation
- DO NOT make educated guesses about regulation

**REQUIRED BEHAVIOR:**
- If no explicit regulation is mentioned in the article text: return "Not specified"
- If regulation terms appear without clear identifier: return "Not specified"  
- Only return a specific regulation (A, B, C, etc.) if it is EXPLICITLY stated in the article
- When in doubt, always return "Not specified"

RESPONSE FORMAT (MUST BE VALID JSON):
{
  "title": "English translation of article title",
  "author": "Author name if available",
  "tournament_context": "Tournament or context information",
  "overall_strategy": "Main team strategy and approach",
  "regulation": "VGC regulation (A, B, C, etc.)",
  "pokemon_team": [
    {
      "name": "EXACT Pokemon Name with proper form",
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
- Translate Pokemon names to English using EXACT official spellings
- Translate move names to English
- Translate item names to English
- Keep ability names in standard English format
- Preserve strategic terminology accurately
- Double-check Pokemon identification before finalizing

VALIDATION CHECKLIST:
Before responding, verify:
1. All Pokemon names are spelled correctly with proper forms
2. No confusion between similar Pokemon (especially Zamazenta/Zacian)
3. Forms are properly indicated with hyphens (e.g., "-Therian", "-Shadow")
4. Team composition is realistic for VGC (2-6 Pokemon)
5. JSON format is valid and complete

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
            
            # Fix Pokemon name translations
            result = self.fix_pokemon_name_translations(result)
            
            # Apply comprehensive Pokemon validation
            result = self._apply_pokemon_validation(result)

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

        # CRITICAL: Validate regulation field follows article-only requirement
        if "regulation" in result:
            regulation = result["regulation"]
            
            # If regulation looks like it was inferred rather than explicit from article
            suspicious_patterns = [
                "likely", "probably", "appears to be", "based on", "seems to be",
                "inferred", "guessing", "estimated", "assumed", "2 restricted",
                "1 restricted", "0 restricted", "legendary count", "team composition"
            ]
            
            if any(pattern in regulation.lower() for pattern in suspicious_patterns):
                result["regulation"] = "Not specified"
                
            # Only allow specific regulation formats or "Not specified"
            valid_regulations = [
                "Not specified", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                "Regulation A", "Regulation B", "Regulation C", "Regulation D",
                "Regulation E", "Regulation F", "Regulation G", "Regulation H", 
                "Regulation I", "Regulation J", "Series 1", "Series 2", "Series 3",
                "VGC 2024", "VGC 2025"
            ]
            
            if regulation not in valid_regulations:
                # If it's not in valid list, check if it's a simple letter/number
                if not (len(regulation.strip()) <= 2 and regulation.strip().upper() in "ABCDEFGHIJ"):
                    result["regulation"] = "Not specified"
        else:
            result["regulation"] = "Not specified"

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

    def fix_pokemon_name_translations(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply post-processing to fix Pokemon name translations
        
        Args:
            result: Analysis result to fix
            
        Returns:
            Result with corrected Pokemon names
        """
        if "pokemon_team" in result:
            for pokemon in result["pokemon_team"]:
                if "name" in pokemon:
                    original_name = pokemon["name"]
                    
                    # Check direct translation mapping
                    if original_name in POKEMON_NAME_TRANSLATIONS:
                        pokemon["name"] = POKEMON_NAME_TRANSLATIONS[original_name]
                    else:
                        # Check for partial matches and common variations
                        for japanese_name, english_name in POKEMON_NAME_TRANSLATIONS.items():
                            if japanese_name.lower() in original_name.lower() or original_name.lower() in japanese_name.lower():
                                pokemon["name"] = english_name
                                break
                        
                        # Fix common AI translation errors
                        fixed_name = self._fix_common_name_errors(original_name)
                        if fixed_name != original_name:
                            pokemon["name"] = fixed_name
        
        return result
    
    def _fix_common_name_errors(self, name: str) -> str:
        """
        Enhanced Pokemon name fixing with fuzzy matching and comprehensive error correction
        
        Args:
            name: Pokemon name to fix
            
        Returns:
            Corrected Pokemon name
        """
        # First check direct mapping
        if name in POKEMON_NAME_TRANSLATIONS:
            return POKEMON_NAME_TRANSLATIONS[name]
        
        # Check case-insensitive exact match
        for key, value in POKEMON_NAME_TRANSLATIONS.items():
            if key.lower() == name.lower():
                return value
                
        # Apply fuzzy matching for similar names
        return self._apply_fuzzy_name_matching(name)
    
    def _apply_fuzzy_name_matching(self, name: str) -> str:
        """
        Apply fuzzy matching to find the most likely correct Pokemon name
        
        Args:
            name: Input Pokemon name
            
        Returns:
            Best matching Pokemon name or original if no good match
        """
        name_lower = name.lower().strip()
        best_match = name
        best_score = 0
        
        # Check for partial matches and common patterns
        for translation_key, correct_name in POKEMON_NAME_TRANSLATIONS.items():
            key_lower = translation_key.lower()
            
            # Direct substring match (high priority)
            if name_lower in key_lower or key_lower in name_lower:
                if len(key_lower) >= len(name_lower) * 0.7:  # At least 70% of original length
                    return correct_name
            
            # Check for word-based matching
            name_words = set(name_lower.replace('-', ' ').split())
            key_words = set(key_lower.replace('-', ' ').split())
            
            if name_words and key_words:
                # Calculate word overlap ratio
                overlap = len(name_words & key_words)
                total_words = len(name_words | key_words)
                
                if total_words > 0:
                    score = overlap / total_words
                    
                    # Bonus for exact word matches
                    if overlap > 0 and score > 0.5:
                        score += 0.2
                    
                    if score > best_score and score > 0.6:
                        best_score = score
                        best_match = correct_name
        
        # Special pattern matching for common errors
        best_match = self._apply_pattern_fixes(best_match)
        
        return best_match
    
    def _apply_pattern_fixes(self, name: str) -> str:
        """
        Apply pattern-based fixes for systematic naming errors
        
        Args:
            name: Pokemon name to check
            
        Returns:
            Fixed Pokemon name
        """
        # ULTRA COMPREHENSIVE Iron Valiant fixes - catch EVERY possible variation
        # Apply Iron Valiant fixes first with maximum priority
        name = self._fix_iron_valiant_variants(name)
        
        # Common form notation fixes
        form_fixes = [
            # Paradox Pokemon should NEVER have forms - catch any remaining cases
            (r'\bFlutter[\s\-]*Mane[\s\-]*(?:Therian|Form|Forme)\b', 'Flutter Mane'),
            (r'\bIron[\s\-]*Moth[\s\-]*(?:Therian|Form|Forme)\b', 'Iron Moth'),
            (r'\bSandy[\s\-]*Shocks[\s\-]*(?:Therian|Form|Forme)\b', 'Sandy Shocks'),
            (r'\bRoaring[\s\-]*Moon[\s\-]*(?:Therian|Form|Forme)\b', 'Roaring Moon'),
            (r'\bBrute[\s\-]*Bonnet[\s\-]*(?:Therian|Form|Forme)\b', 'Brute Bonnet'),
            
            # Therian forms (ONLY for Pokemon that actually have Therian forms)
            (r'\b(Landorus)[\s\-]*T\b', r'\1-Therian'),
            (r'\b(Thundurus)[\s\-]*T\b', r'\1-Therian'),  
            (r'\b(Tornadus)[\s\-]*T\b', r'\1-Therian'),
            (r'\b(Landorus)[\s\-]*Therian\b', r'\1-Therian'),
            (r'\b(Thundurus)[\s\-]*Therian\b', r'\1-Therian'),
            (r'\b(Tornadus)[\s\-]*Therian\b', r'\1-Therian'),
            
            # Shadow/Ice Calyrex
            (r'\bCalyrex[\s\-]*Shadow\b', 'Calyrex-Shadow'),
            (r'\bCalyrex[\s\-]*Ice\b', 'Calyrex-Ice'),
            (r'\bShadow[\s\-]*Calyrex\b', 'Calyrex-Shadow'),
            (r'\bIce[\s\-]*Calyrex\b', 'Calyrex-Ice'),
            
            # Urshifu forms  
            (r'\bUrshifu[\s\-]*Rapid\b', 'Urshifu-Rapid-Strike'),
            (r'\bUrshifu[\s\-]*Single\b', 'Urshifu-Single-Strike'),
            (r'\bRapid[\s\-]*Strike[\s\-]*Urshifu\b', 'Urshifu-Rapid-Strike'),
            (r'\bSingle[\s\-]*Strike[\s\-]*Urshifu\b', 'Urshifu-Single-Strike'),
            
            # Treasures of Ruin common errors
            (r'\b(?:Pao|Kai)[\s\-]*(?:Kai|Pao)\b', 'Chien-Pao'),
            (r'\bChien[\s\-]*Pao\b', 'Chien-Pao'),
            (r'\bChi[\s\-]*Yu\b', 'Chi-Yu'),
            (r'\bTing[\s\-]*Lu\b', 'Ting-Lu'),
            (r'\bWo[\s\-]*Chien\b', 'Wo-Chien'),
            
            # Regional forms
            (r'\bGalarian[\s\-]*(\w+)', r'\1-Galar'),
            (r'\bAlolan[\s\-]*(\w+)', r'\1-Alola'),
            (r'\bHisuian[\s\-]*(\w+)', r'\1-Hisui'),
            
            # Specific space to hyphen fixes for known compound Pokemon names
            (r'\bIron[\s]+Valiant\b', 'Iron Valiant'),  # Keep Iron Valiant as is
            (r'\bFlutter[\s]+Mane\b', 'Flutter Mane'),   # Keep Flutter Mane as is
            (r'\bIron[\s]+Moth\b', 'Iron Moth'),         # Keep Iron Moth as is
        ]
        
        import re
        
        fixed_name = name
        for pattern, replacement in form_fixes:
            fixed_name = re.sub(pattern, replacement, fixed_name, flags=re.IGNORECASE)
            
        return fixed_name
    
    def _fix_iron_valiant_variants(self, name: str) -> str:
        """
        Ultra-comprehensive Iron Valiant variant fixing
        
        Args:
            name: Pokemon name to fix
            
        Returns:
            Fixed name with Iron Valiant corrections
        """
        import re
        
        # ULTRA PRIORITY: Iron Valiant fixes - catch EVERY possible variation
        iron_valiant_patterns = [
            # Main variations with Therian (most common error)
            (r'\bIron[\s\-]*Valiant[\s\-]*Therian\b', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valian[\s\-]*Therian\b', 'Iron Valiant'), 
            (r'\bIron[\s\-]*Valien[\s\-]*Therian\b', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valliant[\s\-]*Therian\b', 'Iron Valiant'),  # Common typo
            (r'\bIron[\s\-]*Valient[\s\-]*Therian\b', 'Iron Valiant'),   # Common typo
            
            # Just the misspelled base names (without Therian)
            (r'\bIron[\s\-]*Valian\b(?![\s\-]*Valiant)', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valien\b(?![\s\-]*Valiant)', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valliant\b(?![\s\-]*Valiant)', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valient\b(?![\s\-]*Valiant)', 'Iron Valiant'),
            
            # Partial matches (just the wrong part with Therian)
            (r'\bValian[\s\-]*Therian\b', 'Iron Valiant'),
            (r'\bValien[\s\-]*Therian\b', 'Iron Valiant'),
            (r'\bValliant[\s\-]*Therian\b', 'Iron Valiant'),
            (r'\bValient[\s\-]*Therian\b', 'Iron Valiant'),
            
            # With other incorrect form suffixes
            (r'\bIron[\s\-]*Valiant[\s\-]*(?:Forme?|Form)\b', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valian[\s\-]*(?:Forme?|Form)\b', 'Iron Valiant'),
            (r'\bIron[\s\-]*Valien[\s\-]*(?:Forme?|Form)\b', 'Iron Valiant'),
            
            # Catch any remaining variations with common errors
            (r'\bIron[\s\-]*V[aeiou][lL][lia][eaio]?n[ts]?[\s\-]*(?:Therian|T|Form|Forme)\b', 'Iron Valiant'),
        ]
        
        fixed_name = name
        for pattern, replacement in iron_valiant_patterns:
            fixed_name = re.sub(pattern, replacement, fixed_name, flags=re.IGNORECASE)
            
        return fixed_name

    def _apply_pokemon_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply comprehensive Pokemon validation to ensure data quality
        
        Args:
            result: Analysis result to validate
            
        Returns:
            Validated and corrected result
        """
        if "pokemon_team" not in result:
            return result
            
        validated_team = []
        validation_warnings = []
        
        for i, pokemon in enumerate(result["pokemon_team"]):
            try:
                validated_pokemon = self._validate_individual_pokemon(pokemon, i)
                if validated_pokemon:
                    validated_team.append(validated_pokemon)
                    
                    # Check for validation warnings
                    warnings = self._check_pokemon_warnings(validated_pokemon, i)
                    validation_warnings.extend(warnings)
                    
            except Exception as e:
                # Log validation error but don't fail the entire analysis
                validation_warnings.append(f"Pokemon #{i+1} validation failed: {str(e)}")
                # Keep the original Pokemon data if validation fails
                validated_team.append(pokemon)
        
        result["pokemon_team"] = validated_team
        
        # Apply team-level validation
        team_warnings = self._validate_team_composition(validated_team)
        validation_warnings.extend(team_warnings)
        
        # Add validation notes if any warnings exist
        if validation_warnings:
            existing_notes = result.get("translation_notes", "")
            warning_text = " | ".join(validation_warnings[:3])  # Limit to top 3 warnings
            result["translation_notes"] = f"{existing_notes} Validation: {warning_text}".strip()
            
        return result
    
    def _validate_individual_pokemon(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Validate individual Pokemon data
        
        Args:
            pokemon: Pokemon data to validate
            index: Pokemon index in team
            
        Returns:
            Validated Pokemon data
        """
        validated = pokemon.copy()
        
        # Validate Pokemon name
        validated = self._validate_pokemon_name(validated, index)
        
        # Validate abilities
        validated = self._validate_pokemon_ability(validated, index)
        
        # Validate moves
        validated = self._validate_pokemon_moves(validated, index)
        
        # Validate items
        validated = self._validate_pokemon_item(validated, index)
        
        # Validate EV spreads
        validated = self._validate_pokemon_evs(validated, index)
        
        # Validate natures
        validated = self._validate_pokemon_nature(validated, index)
        
        return validated
    
    def _validate_pokemon_name(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Enhanced Pokemon name validation with form checking"""
        name = pokemon.get("name", "")
        
        if not name or name in ["Unknown", "Unknown Pokemon", "Not specified"]:
            pokemon["name"] = "Unknown Pokemon"
            return pokemon
            
        # First apply form validation to prevent incorrect forms
        validated_name = self._validate_pokemon_forms(name)
        
        # Check if name exists in our translations (indicates it's a known Pokemon)
        name_lower = validated_name.lower()
        known_pokemon = set(POKEMON_NAME_TRANSLATIONS.values()) | set(POKEMON_NAME_TRANSLATIONS.keys())
        
        # Add common VGC Pokemon
        common_vgc_pokemon = {
            "garchomp", "incineroar", "landorus-therian", "amoonguss", "whimsicott",
            "grimmsnarl", "dragapult", "flutter-mane", "iron-moth", "chien-pao",
            "chi-yu", "koraidon", "miraidon", "calyrex-shadow", "urshifu-rapid-strike",
            "zamazenta", "zacian", "dragonite", "charizard", "salamence", "metagross",
            "tyranitar", "excadrill", "ferrothorn", "rotom-heat", "rotom-wash",
            "indeedee", "arcanine", "torkoal", "venusaur", "rillaboom", "iron-valiant"
        }
        
        all_known_pokemon = known_pokemon | common_vgc_pokemon
        
        # Check if name is in known Pokemon (case-insensitive)
        for known_name in all_known_pokemon:
            if known_name.lower() == name_lower:
                pokemon["name"] = known_name.title().replace("-", "-")
                return pokemon
                
        # If not found, apply additional fuzzy validation
        best_match = self._find_best_pokemon_match(validated_name, all_known_pokemon)
        if best_match:
            pokemon["name"] = best_match
        else:
            pokemon["name"] = validated_name
        
        return pokemon
    
    def _validate_pokemon_forms(self, name: str) -> str:
        """
        Validate and correct Pokemon forms to prevent incorrect form application
        
        Args:
            name: Pokemon name to validate
            
        Returns:
            Corrected Pokemon name with proper forms
        """
        name_lower = name.lower()
        
        # CRITICAL PRIORITY: Handle Paradox Pokemon FIRST (before general form validation)
        paradox_pokemon_map = {
            'iron-valiant': 'Iron Valiant',
            'iron-moth': 'Iron Moth', 
            'flutter-mane': 'Flutter Mane',
            'sandy-shocks': 'Sandy Shocks',
            'roaring-moon': 'Roaring Moon',
            'brute-bonnet': 'Brute Bonnet',
            'great-tusk': 'Great Tusk',
            'scream-tail': 'Scream Tail',
            'iron-treads': 'Iron Treads',
            'iron-bundle': 'Iron Bundle',
            'iron-hands': 'Iron Hands',
            'iron-jugulis': 'Iron Jugulis',
            'iron-thorns': 'Iron Thorns',
            'slither-wing': 'Slither Wing',
            'walking-wake': 'Walking Wake',
            'iron-leaves': 'Iron Leaves'
        }
        
        # ULTRA PRIORITY: Iron Valiant specific check (most common error)
        if 'iron' in name_lower and any(variant in name_lower for variant in ['valiant', 'valian', 'valien']):
            # Remove any form suffix from Iron Valiant variants
            if any(form in name_lower for form in ['therian', 'shadow', 'galar', 'alola', 'hisui', 'form', 'forme']):
                # Debug print
                # print(f"DEBUG: Iron Valiant form detected, returning 'Iron Valiant' for input: {name}")
                return 'Iron Valiant'
        
        for paradox_key, correct_name in paradox_pokemon_map.items():
            paradox_spaced = paradox_key.replace('-', ' ')
            # Check if this name contains the paradox Pokemon (with any form suffix)
            if (paradox_key in name_lower or paradox_spaced.lower() in name_lower or 
                name_lower.startswith(paradox_key) or name_lower.startswith(paradox_spaced.lower())):
                # Remove any incorrectly applied forms from Paradox Pokemon
                if any(form in name_lower for form in ['therian', 'shadow', 'galar', 'alola', 'hisui', 'form', 'forme']):
                    return correct_name
                # Even if no form detected, return correct name if it's hyphenated (should be spaced)  
                elif '-' in name and paradox_key in name_lower:
                    return correct_name
        
        # GENERAL FORM VALIDATION (after paradox Pokemon handling)
        # Define Pokemon that can have specific forms
        valid_forms = {
            # Therian forms (only these 3 Pokemon can have Therian forms)
            'therian': ['landorus', 'thundurus', 'tornadus'],
            
            # Shadow/Ice forms (only Calyrex)
            'shadow': ['calyrex'],
            'ice': ['calyrex'],
            
            # Strike forms (only Urshifu)
            'rapid-strike': ['urshifu'],
            'single-strike': ['urshifu'],
            
            # Regional forms
            'galar': ['zapdos', 'moltres', 'articuno', 'slowking', 'slowbro', 'mr-mime', 
                     'ponyta', 'rapidash', 'farfetchd', 'weezing', 'corsola', 'zigzagoon',
                     'linoone', 'darumaka', 'darmanitan', 'yamask', 'stunfisk'],
            'alola': ['rattata', 'raticate', 'raichu', 'sandshrew', 'sandslash', 'vulpix',
                     'ninetales', 'diglett', 'dugtrio', 'meowth', 'persian', 'geodude',
                     'graveler', 'golem', 'grimer', 'muk', 'exeggutor', 'marowak'],
            'hisui': ['growlithe', 'arcanine', 'voltorb', 'electrode', 'typhlosion', 
                     'qwilfish', 'sneasel', 'samurott', 'lilligant', 'zorua', 'zoroark',
                     'braviary', 'sliggoo', 'goodra', 'avalugg', 'decidueye'],
            
            # Other forms
            'heat': ['rotom'], 'wash': ['rotom'], 'frost': ['rotom'], 'fan': ['rotom'], 'mow': ['rotom'],
            'crowned': ['zacian', 'zamazenta']
        }
        
        # Check for incorrect form applications
        for form_name, valid_pokemon in valid_forms.items():
            if form_name in name_lower or f'-{form_name}' in name_lower:
                # Extract base Pokemon name
                base_name = name_lower.replace(f'-{form_name}', '').replace(f' {form_name}', '').strip()
                
                # Check if this Pokemon can actually have this form
                if base_name not in valid_pokemon:
                    # Remove the invalid form
                    corrected_name = name.replace(f'-{form_name.title()}', '').replace(f' {form_name.title()}', '').strip()
                    corrected_name = corrected_name.replace(f'-{form_name}', '').replace(f' {form_name}', '').strip()
                    return corrected_name
        
        return name
    
    def _validate_pokemon_ability(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate Pokemon ability"""
        ability = pokemon.get("ability", "")
        
        if not ability or ability == "Not specified":
            return pokemon
            
        # Common ability corrections
        ability_fixes = {
            "intimadate": "Intimidate",
            "protean": "Protean", 
            "libero": "Libero",
            "prankster": "Prankster",
            "drought": "Drought",
            "drizzle": "Drizzle",
            "sand stream": "Sand Stream",
            "snow warning": "Snow Warning",
            "levitate": "Levitate",
            "magic guard": "Magic Guard",
            "regenerator": "Regenerator",
            "natural cure": "Natural Cure",
            "serene grace": "Serene Grace",
            "technician": "Technician",
            "adaptability": "Adaptability",
            "multiscale": "Multiscale",
            "marvel scale": "Marvel Scale",
            "huge power": "Huge Power",
            "pure power": "Pure Power"
        }
        
        ability_lower = ability.lower()
        for key, correct_ability in ability_fixes.items():
            if key in ability_lower:
                pokemon["ability"] = correct_ability
                break
                
        return pokemon
    
    def _validate_pokemon_moves(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate Pokemon moves"""
        moves = pokemon.get("moves", [])
        
        if not moves:
            pokemon["moves"] = ["Not specified", "Not specified", "Not specified", "Not specified"]
            return pokemon
            
        # Ensure exactly 4 moves
        if len(moves) < 4:
            moves.extend(["Not specified"] * (4 - len(moves)))
        elif len(moves) > 4:
            moves = moves[:4]
            
        # Common move name corrections
        move_fixes = {
            "earthquake": "Earthquake",
            "dragon claw": "Dragon Claw", 
            "flamethrower": "Flamethrower",
            "ice beam": "Ice Beam",
            "thunderbolt": "Thunderbolt",
            "psychic": "Psychic",
            "shadow ball": "Shadow Ball",
            "energy ball": "Energy Ball",
            "air slash": "Air Slash",
            "rock slide": "Rock Slide",
            "iron head": "Iron Head",
            "u-turn": "U-turn",
            "volt switch": "Volt Switch",
            "fake out": "Fake Out",
            "protect": "Protect",
            "substitute": "Substitute",
            "roost": "Roost",
            "will-o-wisp": "Will-O-Wisp",
            "thunder wave": "Thunder Wave",
            "toxic": "Toxic",
            "stealth rock": "Stealth Rock"
        }
        
        corrected_moves = []
        for move in moves:
            if not move or move == "Not specified":
                corrected_moves.append("Not specified")
                continue
                
            move_lower = move.lower()
            corrected = move
            
            for key, correct_move in move_fixes.items():
                if key in move_lower:
                    corrected = correct_move
                    break
                    
            corrected_moves.append(corrected)
            
        pokemon["moves"] = corrected_moves
        return pokemon
    
    def _validate_pokemon_item(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate Pokemon held item"""
        item = pokemon.get("held_item", "")
        
        if not item or item == "Not specified":
            return pokemon
            
        # Common item corrections
        item_fixes = {
            "leftovers": "Leftovers",
            "focus sash": "Focus Sash",
            "life orb": "Life Orb",
            "choice band": "Choice Band",
            "choice specs": "Choice Specs", 
            "choice scarf": "Choice Scarf",
            "assault vest": "Assault Vest",
            "rocky helmet": "Rocky Helmet",
            "safety goggles": "Safety Goggles",
            "booster energy": "Booster Energy",
            "clear amulet": "Clear Amulet",
            "covert cloak": "Covert Cloak",
            "sitrus berry": "Sitrus Berry",
            "lum berry": "Lum Berry",
            "mental herb": "Mental Herb",
            "wide lens": "Wide Lens"
        }
        
        item_lower = item.lower()
        for key, correct_item in item_fixes.items():
            if key in item_lower:
                pokemon["held_item"] = correct_item
                break
                
        return pokemon
    
    def _validate_pokemon_evs(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate Pokemon EV spread"""
        evs = pokemon.get("evs", "")
        
        if not evs or evs == "Not specified":
            return pokemon
            
        # Try to parse and validate EV format
        if "/" in str(evs):
            try:
                ev_parts = [int(x.strip()) for x in str(evs).split("/")]
                if len(ev_parts) == 6:
                    total_evs = sum(ev_parts)
                    
                    # Check for valid EV total (should be <= 508)
                    if total_evs > 508:
                        # Scale down proportionally
                        scale_factor = 508 / total_evs
                        ev_parts = [int(ev * scale_factor) for ev in ev_parts]
                    
                    # Check for valid individual EVs (should be <= 252)
                    ev_parts = [min(252, max(0, ev)) for ev in ev_parts]
                    
                    # Reconstruct EV string
                    pokemon["evs"] = "/".join(map(str, ev_parts))
                    
            except (ValueError, AttributeError):
                # Keep original if parsing fails
                pass
                
        return pokemon
    
    def _validate_pokemon_nature(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate Pokemon nature"""
        nature = pokemon.get("nature", "")
        
        if not nature or nature == "Not specified":
            return pokemon
            
        # Common nature corrections
        nature_fixes = {
            "adamant": "Adamant",
            "jolly": "Jolly", 
            "timid": "Timid",
            "modest": "Modest",
            "bold": "Bold",
            "impish": "Impish",
            "calm": "Calm",
            "careful": "Careful",
            "brave": "Brave",
            "quiet": "Quiet",
            "relaxed": "Relaxed",
            "sassy": "Sassy"
        }
        
        nature_lower = nature.lower()
        for key, correct_nature in nature_fixes.items():
            if key in nature_lower:
                pokemon["nature"] = correct_nature
                break
                
        return pokemon
    
    def _check_pokemon_warnings(self, pokemon: Dict[str, Any], index: int) -> list:
        """Check for potential issues with Pokemon data"""
        warnings = []
        name = pokemon.get("name", "")
        
        # Check for suspicious combinations
        if "Unknown" in name:
            warnings.append(f"Pokemon #{index+1} name uncertain")
            
        # Check EV spread validity
        evs = pokemon.get("evs", "")
        if evs != "Not specified" and "/" in str(evs):
            try:
                ev_parts = [int(x.strip()) for x in str(evs).split("/")]
                total = sum(ev_parts)
                if total > 508:
                    warnings.append(f"Pokemon #{index+1} EV total exceeds 508")
            except:
                warnings.append(f"Pokemon #{index+1} EV format invalid")
                
        return warnings
    
    def _validate_team_composition(self, team: list) -> list:
        """Validate overall team composition"""
        warnings = []
        
        if len(team) < 1:
            warnings.append("No Pokemon found in team")
        elif len(team) > 6:
            warnings.append("Team exceeds 6 Pokemon limit")
            
        # Check for duplicate Pokemon
        names = [p.get("name", "").lower() for p in team if p.get("name")]
        duplicates = [name for name in set(names) if names.count(name) > 1]
        if duplicates:
            warnings.append(f"Duplicate Pokemon detected: {', '.join(duplicates)}")
            
        return warnings
    
    def _find_best_pokemon_match(self, name: str, known_pokemon: set) -> str:
        """Find the best matching Pokemon name from known list"""
        name_lower = name.lower()
        
        # Try exact substring matches first
        for known in known_pokemon:
            known_lower = known.lower()
            if name_lower in known_lower or known_lower in name_lower:
                if abs(len(known_lower) - len(name_lower)) <= 3:  # Similar length
                    return known.title().replace("-", "-")
        
        return name  # Return original if no good match found

    def extract_and_analyze_images(self, url: str) -> Dict[str, Any]:
        """
        Extract images from URL and analyze them for VGC content
        
        Args:
            url: URL to extract images from
            
        Returns:
            Dictionary containing image analysis results
        """
        try:
            # Extract images from URL
            all_images = extract_images_from_url(url)
            if not all_images:
                return {"images_found": 0, "analysis": "No images found"}
                
            # Filter for VGC-relevant images
            vgc_images = filter_vgc_images(all_images)
            if not vgc_images:
                return {
                    "images_found": len(all_images), 
                    "vgc_images": 0,
                    "analysis": "No VGC-relevant images found"
                }
            
            # Analyze images with vision model
            image_analyses = []
            for i, image in enumerate(vgc_images[:3]):  # Limit to 3 images
                analysis = analyze_image_with_vision(
                    image["data"], 
                    image.get("format", "jpeg"), 
                    self.vision_model
                )
                
                image_analyses.append({
                    "image_index": i,
                    "image_url": image["url"],
                    "image_size": image["size"],
                    "file_size": image["file_size"],
                    "is_note_com_asset": image.get("is_note_com_asset", False),
                    "analysis": analysis,
                    "ev_spreads": extract_ev_spreads_from_image_analysis(analysis)
                })
            
            return {
                "images_found": len(all_images),
                "vgc_images": len(vgc_images),
                "analyzed_images": len(image_analyses),
                "image_analyses": image_analyses,
                "success": True
            }
            
        except Exception as e:
            return {
                "images_found": 0,
                "error": str(e),
                "success": False
            }

    def analyze_article_with_images(self, content: str, url: str = None) -> Dict[str, Any]:
        """
        Enhanced analysis combining text and image analysis
        
        Args:
            content: Article content to analyze
            url: Optional URL for image extraction
            
        Returns:
            Combined analysis result
        """
        # First perform standard text analysis
        text_result = self.analyze_article(content, url)
        
        # If URL provided, also analyze images
        if url:
            try:
                image_result = self.extract_and_analyze_images(url)
                
                # Merge image analysis into text result
                text_result["image_analysis"] = image_result
                
                # If we found additional Pokemon or EV data in images, note it
                if image_result.get("success") and image_result.get("image_analyses"):
                    additional_info = []
                    for img_analysis in image_result["image_analyses"]:
                        if img_analysis.get("ev_spreads"):
                            additional_info.append(f"Found {len(img_analysis['ev_spreads'])} EV spreads in image")
                    
                    if additional_info:
                        if "translation_notes" not in text_result:
                            text_result["translation_notes"] = ""
                        text_result["translation_notes"] += f" Image analysis: {'; '.join(additional_info)}"
                        
            except Exception as e:
                text_result["image_analysis"] = {
                    "error": f"Image analysis failed: {str(e)}",
                    "success": False
                }
        
        return text_result
