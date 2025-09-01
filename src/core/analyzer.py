"""
Core VGC analysis engine using Google Gemini AI.
"""

import json
import re
from typing import Dict, Optional, Any
import google.generativeai as genai

from ..utils.config import Config, POKEMON_NAME_TRANSLATIONS
from ..utils.cache_manager import cache
from .scraper import ArticleScraper
from .pokemon_validator import PokemonValidator


class GeminiVGCAnalyzer:
    """Pokemon VGC analyzer using Google Gemini AI"""

    def __init__(self):
        """Initialize the analyzer with Gemini configuration"""
        self.api_key = Config.get_google_api_key()
        genai.configure(api_key=self.api_key)

        # Configure the text model with Gemini 2.5 Flash lite (optimal balance: advanced quality + 5x higher quota)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        
        # Configure the vision model with Flash-Lite (cost-effective for image processing)
        self.vision_model = genai.GenerativeModel("gemini-2.5-flash-lite")

        # Generation config for consistent output
        self.generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8000,
        }
        
        # Initialize helper components
        self.scraper = ArticleScraper()
        self.pokemon_validator = PokemonValidator()

    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible and potentially contains VGC content"""
        return self.scraper.validate_url(url)

    def scrape_article(self, url: str) -> Optional[str]:
        """Scrape article content from URL with enhanced Japanese text handling"""
        return self.scraper.scrape_article(url)

    def analyze_article(self, content: str, url: str = None) -> Dict[str, Any]:
        """
        Enhanced article analysis with comprehensive error handling and fallbacks

        Args:
            content: Article content to analyze
            url: Optional URL for context

        Returns:
            Analysis result as dictionary
        """
        # Enhanced content validation with more helpful messages
        if not content:
            raise ValueError(
                "No content provided for analysis. Please check that the article was successfully extracted."
            )
        
        content_length = len(content.strip())
        if content_length < 50:
            raise ValueError(
                f"Content too short for meaningful analysis ({content_length} characters). "
                f"Please provide more substantial content or try a different article."
            )
        
        # Check for likely extraction failures (mostly UI elements)
        ui_ratio = self.scraper.calculate_ui_content_ratio(content)
        if ui_ratio > 0.7:
            raise ValueError(
                "Content appears to be mostly navigation/UI elements. "
                "The article content may not have loaded properly. "
                "Try refreshing the page or using the 'Article Text' input method instead."
            )

        # Check cache first
        cached_result = cache.get(content, url)
        if cached_result:
            return cached_result

        try:
            # Enhanced content preprocessing for better analysis
            processed_content = self._preprocess_content_for_analysis(content)
            
            prompt = self._get_analysis_prompt()
            full_prompt = f"{prompt}\n\nCONTENT TO ANALYZE:\n{processed_content}"

            # Generate response with retry logic
            result = self._generate_with_fallbacks(full_prompt, content, url)

            # Enhanced validation with confidence scoring
            result = self._validate_and_enhance_result(result, content, url)

            # Cache the result
            cache.set(content, result, url)

            return result

        except json.JSONDecodeError as e:
            # Provide more helpful JSON error guidance
            raise ValueError(
                f"The AI response could not be parsed as valid JSON. "
                f"This may indicate the content was too complex or fragmented. "
                f"Error: {str(e)}. Try using simpler or more focused content."
            )
        except Exception as e:
            # Enhanced error context
            error_context = self._generate_error_context(content, url, str(e))
            raise ValueError(f"Analysis failed: {str(e)}. {error_context}")
    
    def _preprocess_content_for_analysis(self, content: str) -> str:
        """Preprocess content to improve analysis accuracy"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        
        # Prioritize content with VGC/Pokemon indicators
        lines = content.split('\n')
        priority_lines = []
        other_lines = []
        
        vgc_indicators = [
            'ポケモン', '構築', 'VGC', 'ダブル', 'バトル', '調整', '努力値',
            'pokemon', 'team', 'battle', 'regulation', 'tournament'
        ]
        
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in vgc_indicators):
                priority_lines.append(line)
            else:
                other_lines.append(line)
        
        # Prioritize VGC content, but include other content if space allows
        result = '\n'.join(priority_lines)
        if len(result) < 6000:  # Leave room for additional context
            remaining_space = 6000 - len(result)
            additional_content = '\n'.join(other_lines)[:remaining_space]
            result += '\n' + additional_content
        
        return result
    
    def _generate_with_fallbacks(self, prompt: str, original_content: str, url: str = None) -> Dict[str, Any]:
        """Generate analysis with multiple fallback strategies"""
        strategies = [
            self._generate_standard,
            self._generate_with_reduced_content,
            self._generate_with_simplified_prompt
        ]
        
        last_error = None
        for strategy in strategies:
            try:
                return strategy(prompt, original_content)
            except Exception as e:
                last_error = e
                continue
        
        # All strategies failed, raise the last error
        raise last_error
    
    def _generate_standard(self, prompt: str, content: str) -> Dict[str, Any]:
        """Standard generation approach"""
        response = self.model.generate_content(
            prompt, generation_config=self.generation_config
        )

        if not response.text:
            raise ValueError("Empty response from Gemini API")

        return self._parse_json_response(response.text)
    
    def _generate_with_reduced_content(self, prompt: str, content: str) -> Dict[str, Any]:
        """Fallback with reduced content size"""
        # Reduce content to most relevant parts
        reduced_content = content[:4000]  # Smaller chunk
        reduced_prompt = prompt.replace(content, reduced_content)
        
        response = self.model.generate_content(
            reduced_prompt, generation_config=self.generation_config
        )

        if not response.text:
            raise ValueError("Empty response from Gemini API")

        result = self._parse_json_response(response.text)
        # Mark as partial analysis
        result["translation_notes"] = result.get("translation_notes", "") + " | Partial content analysis due to size constraints"
        return result
    
    def _generate_with_simplified_prompt(self, prompt: str, content: str) -> Dict[str, Any]:
        """Fallback with simplified prompt for complex content"""
        simple_prompt = """
        Analyze this Pokemon VGC content and extract team information. Focus on Pokemon names and return valid JSON:
        {
          "title": "extracted title",
          "pokemon_team": [{"name": "Pokemon Name", "ability": "ability", "held_item": "item", "moves": []}],
          "overall_strategy": "strategy",
          "regulation": "Not specified"
        }
        
        Content: """ + content[:3000]
        
        response = self.model.generate_content(
            simple_prompt, generation_config=self.generation_config
        )

        if not response.text:
            raise ValueError("Empty response from Gemini API")

        result = self._parse_json_response(response.text)
        # Mark as simplified analysis
        result["translation_notes"] = result.get("translation_notes", "") + " | Simplified analysis due to content complexity"
        return result
    
    def _validate_and_enhance_result(self, result: Dict[str, Any], content: str, url: str = None) -> Dict[str, Any]:
        """Enhanced validation with confidence scoring and improvements"""
        # Apply original validation
        result = self._validate_and_clean_result(result)
        result = self.pokemon_validator.fix_pokemon_name_translations(result)
        result = self.pokemon_validator.apply_pokemon_validation(result)
        
        # Add confidence scoring
        confidence_score = self._calculate_analysis_confidence(result, content)
        result["analysis_confidence"] = confidence_score
        
        # Add helpful context for low confidence
        if confidence_score < 0.6:
            guidance = self._generate_low_confidence_guidance(result, content)
            result["user_guidance"] = guidance
        
        # Enhance error messages
        if result.get("parsing_error"):
            result["user_guidance"] = (
                "The analysis encountered parsing difficulties. This may be due to complex content structure. "
                "Try using the 'Article Text' input method if you used a URL, or provide more focused content."
            )
        
        return result
    
    def _calculate_analysis_confidence(self, result: Dict[str, Any], content: str) -> float:
        """Calculate confidence score for the analysis"""
        confidence = 0.5  # Base confidence
        
        # Pokemon team quality
        pokemon_team = result.get("pokemon_team", [])
        if pokemon_team:
            confidence += 0.2
            
            # Check for meaningful Pokemon names
            valid_names = sum(1 for p in pokemon_team 
                            if p.get("name", "Unknown") not in ["Unknown", "Unknown Pokemon", "Not specified"])
            if valid_names > 0:
                confidence += 0.2 * (valid_names / len(pokemon_team))
        
        # Content indicators in original text
        vgc_terms = ['ポケモン', '構築', 'pokemon', 'vgc', 'team', 'battle']
        found_terms = sum(1 for term in vgc_terms if term in content.lower())
        if found_terms > 0:
            confidence += 0.1
        
        # JSON parsing success
        if not result.get("parsing_error"):
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_low_confidence_guidance(self, result: Dict[str, Any], content: str) -> str:
        """Generate user guidance for low confidence analyses"""
        issues = []
        
        if not result.get("pokemon_team"):
            issues.append("No Pokemon team detected")
        elif len(result.get("pokemon_team", [])) < 2:
            issues.append("Only partial team detected")
        
        if result.get("parsing_error"):
            issues.append("JSON parsing difficulties")
        
        if len(content.strip()) < 500:
            issues.append("Limited content available")
        
        guidance = "Analysis confidence is low. "
        if issues:
            guidance += "Issues detected: " + ", ".join(issues) + ". "
        
        guidance += ("Try providing more detailed content, using the 'Article Text' method instead of URL, "
                    "or ensuring the article contains substantial Pokemon team information.")
        
        return guidance
    
    def _generate_error_context(self, content: str, url: str, error: str) -> str:
        """Generate helpful context for errors"""
        context_parts = []
        
        if url and "note.com" in url:
            context_parts.append("Note.com articles sometimes require specific handling")
        
        if len(content.strip()) < 200:
            context_parts.append("Content appears very short")
        
        if "json" in error.lower():
            context_parts.append("Try using the 'Article Text' input method")
        
        if context_parts:
            return "Context: " + "; ".join(context_parts) + "."
        
        return ""

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

🚨 ULTRA-ENHANCED POKEMON IDENTIFICATION REQUIREMENTS 🚨

**GENERATION 9 PRIORITY POKEMON (Often Found in VGC):**
These are CRITICAL to identify correctly as they appear frequently in competitive play:

OGERPON FORMS - CRITICAL IDENTIFICATION:
- オーガポン (いどのめん) = Ogerpon-Wellspring (Water/Grass with Wellspring Mask)
- オーガポン (かまどのめん) = Ogerpon-Hearthflame (Fire/Grass with Hearthflame Mask)  
- オーガポン (いしずえのめん) = Ogerpon-Cornerstone (Rock/Grass with Cornerstone Mask)
- オーガポン (みどりのめん) = Ogerpon (Base form, Grass type with Teal Mask)
- オーガポン = Ogerpon (when no specific form mentioned, assume base form)

HISUIAN REGIONAL FORMS - CRITICAL FOR VGC:
- ヒスイウインディ = Arcanine-Hisui (Fire/Rock type, NOT regular Arcanine)
- ヒスイゾロア = Zorua-Hisui
- ヒスイゾロアーク = Zoroark-Hisui
- ヒスイガーディ = Growlithe-Hisui
- ヒスイバクフーン = Typhlosion-Hisui

TREASURES OF RUIN - EXACT IDENTIFICATION:
- チオンジェン = Chi-Yu (Fire/Dark - goldfish-like legendary)
- パオジアン = Chien-Pao (Dark/Ice - cat-like legendary)
- ディンルー = Ting-Lu (Dark/Ground - deer-like legendary) 
- イーユイ = Wo-Chien (Dark/Grass - snail-like legendary)

FORME IDENTIFICATION - THERIAN vs INCARNATE:
- トルネロス (れいじゅうフォルム) = Tornadus-Therian (Flying/Flying)
- トルネロス (けしんフォルム) = Tornadus-Incarnate (Flying type, humanoid form)
- トルネロス = Tornadus-Incarnate (when no form specified, default to Incarnate)
- ランドロス (れいじゅうフォルム) = Landorus-Therian 
- ランドロス (けしんフォルム) = Landorus-Incarnate
- ボルトロス (れいじゅうフォルム) = Thundurus-Therian
- ボルトロス (けしんフォルム) = Thundurus-Incarnate

GENERATION 9 POKEMON - COMMON VGC NAMES:
- サーフゴー = Gholdengo (Ghost/Steel)
- テツノカイナ = Iron Hands (Fighting/Electric paradox)
- ハバタクカミ = Flutter Mane (Ghost/Fairy paradox)
- コライドン = Koraidon (Fighting/Dragon legendary)
- ミライドン = Miraidon (Electric/Dragon legendary)
- イルカマン = Palafin (Water type with Zero to Hero)

**COMMON IDENTIFICATION ERRORS TO AVOID:**

DO NOT CONFUSE THESE POKEMON:
- Zamazenta ≠ Zacian (ザマゼンタ = Zamazenta, ザシアン = Zacian)
- Chi-Yu ≠ Chien-Pao (チオンジェン = Chi-Yu, パオジアン = Chien-Pao)
- Ting-Lu ≠ Wo-Chien (ディンルー = Ting-Lu, イーユイ = Wo-Chien)
- Tornadus-Incarnate ≠ Tornadus-Therian (different forms, different stats)

PARADOX POKEMON - NEVER HAVE REGIONAL FORMS:
- Iron Valiant (NEVER "Iron-Valiant-Therian" or any other form suffix)
- Flutter Mane (NEVER "Flutter-Mane-Therian")
- Iron Hands (NEVER "Iron-Hands-Hisui")
- Iron Moth, Sandy Shocks, Roaring Moon (NO form variations exist)

REGIONAL FORMS FORMAT:
- Use format: "Pokemon-Region" (e.g., "Arcanine-Hisui", "Zapdos-Galar")
- For Hisuian: ALWAYS use "Pokemon-Hisui" format
- For Galarian: "Pokemon-Galar" 
- For Alolan: "Pokemon-Alola"

🎯 ENHANCED ANALYSIS STRATEGIES FOR DIFFICULT CONTENT 🎯

**PARTIAL CONTENT HANDLING:**
If you encounter incomplete or fragmented content:
1. Focus on extracting Pokemon names even from minimal mentions
2. Use context clues to infer likely team compositions
3. If only partial team is mentioned, still provide complete analysis for available Pokemon
4. Mark uncertain identifications in translation_notes
5. Prioritize accuracy over completeness

**DYNAMIC CONTENT FALLBACKS:**
For content that seems incomplete or contains mostly UI elements:
1. Look for any Pokemon name mentions, even scattered ones
2. Search for katakana patterns that might be Pokemon names
3. Extract any visible move names, items, or abilities as clues
4. Use "Not specified" generously rather than guessing
5. Provide confidence levels in your analysis

**CONTENT VALIDATION CHECKS:**
Before finalizing your response:
1. Verify each Pokemon name against the forms list above
2. Ensure no Paradox Pokemon have incorrect form suffixes
3. Check that Hisuian forms use "-Hisui" format correctly
4. Confirm Treasures of Ruin are correctly distinguished
5. Double-check Tornadus/Landorus/Thundurus forme assignments

REGULATION DETECTION REQUIREMENTS:
ULTRA CRITICAL: Extract the VGC regulation ONLY and EXCLUSIVELY from the article text content. DO NOT INFER OR GUESS based on team composition.

**STRICT ARTICLE-ONLY DETECTION:**
You MUST only look for explicit regulation mentions in the article text. Look for:
- レギュレーション + letter/number (e.g., "レギュレーションG")
- Regulation + letter/number (e.g., "Regulation G")
- Series + number (e.g., "Series 13")
- シリーズ + number (e.g., "シリーズ13")

If NO explicit regulation is mentioned in the text, you MUST use "Not specified" - DO NOT guess.

RESPONSE FORMAT:
Provide your response in this EXACT JSON structure:
{
  "title": "Article title or summary",
  "author": "Author name or 'Not specified'",
  "regulation": "ONLY if explicitly mentioned in text, otherwise 'Not specified'",
  "pokemon_team": [
    {
      "name": "EXACT Pokemon name with correct form",
      "ability": "Pokemon ability or 'Not specified'",
      "held_item": "Item name or 'Not specified'", 
      "tera_type": "Tera type or 'Not specified'",
      "nature": "Pokemon nature or 'Not specified'",
      "ev_spread": {
        "HP": 0,
        "Attack": 0,
        "Defense": 0,
        "Special Attack": 0,
        "Special Defense": 0,
        "Speed": 0,
        "total": 0
      },
      "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
      "ev_explanation": "Strategic reasoning for EV distribution",
      "role_in_team": "Pokemon's strategic role"
    }
  ],
  "overall_strategy": "Team's overall strategy and synergies",
  "tournament_context": "Tournament or competitive context if mentioned",
  "translation_notes": "Any translation notes or uncertainties",
  "content_summary": "Brief summary of the article content"
}

Please analyze the following content and provide your response in the exact JSON format specified above:
'''

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Enhanced JSON response parsing with comprehensive error recovery"""
        # Try multiple parsing strategies
        strategies = [
            self._parse_direct_json,
            self._parse_cleaned_json,
            self._parse_extracted_json,
            self._parse_partial_json,
            self._create_fallback_result
        ]
        
        for strategy in strategies:
            try:
                result = strategy(response_text)
                if result:
                    return result
            except Exception:
                continue
        
        # If all strategies fail, create minimal fallback
        return self._create_minimal_fallback()
    
    def _parse_direct_json(self, text: str) -> Dict[str, Any]:
        """Direct JSON parsing"""
        return json.loads(text.strip())
    
    def _parse_cleaned_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON after cleaning"""
        cleaned = self._clean_json_text(text)
        return json.loads(cleaned)
    
    def _parse_extracted_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from markdown or other formats"""
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        # Try finding JSON block
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        
        raise ValueError("No JSON found")
    
    def _parse_partial_json(self, text: str) -> Dict[str, Any]:
        """Attempt to parse partial or malformed JSON"""
        # Implementation for partial JSON recovery
        # This is a simplified version - could be more sophisticated
        return {"parsing_error": "Partial JSON recovery attempted"}
    
    def _clean_json_text(self, text: str) -> str:
        """Clean text for better JSON parsing"""
        # Remove markdown formatting
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```', '', text)
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^[^{]*(\{)', r'\1', text)
        text = re.sub(r'(\})[^}]*$', r'\1', text)
        
        return text.strip()
    
    def _create_fallback_result(self, response_text: str) -> Dict[str, Any]:
        """Create fallback result when JSON parsing fails"""
        return {
            "title": "Analysis Error",
            "parsing_error": True,
            "error_details": "JSON parsing failed",
            "pokemon_team": [],
            "overall_strategy": "Unable to extract due to parsing error",
            "regulation": "Not specified",
            "translation_notes": "Analysis failed due to response parsing issues"
        }
    
    def _create_minimal_fallback(self) -> Dict[str, Any]:
        """Create minimal fallback when all parsing fails"""
        return {
            "title": "Parsing Failed",
            "pokemon_team": [],
            "overall_strategy": "Unable to analyze",
            "regulation": "Not specified"
        }
    
    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the analysis result"""
        # Ensure required fields exist
        required_fields = ["title", "pokemon_team", "overall_strategy", "regulation"]
        for field in required_fields:
            if field not in result:
                result[field] = "Not specified"
        
        # Validate Pokemon team structure
        if isinstance(result.get("pokemon_team"), list):
            cleaned_team = []
            for pokemon in result["pokemon_team"]:
                if isinstance(pokemon, dict):
                    # Ensure required Pokemon fields
                    pokemon_fields = {
                        "name": "Unknown Pokemon",
                        "ability": "Not specified",
                        "held_item": "Not specified",
                        "tera_type": "Not specified",
                        "nature": "Not specified",
                        "moves": [],
                        "ev_spread": {
                            "HP": 0, "Attack": 0, "Defense": 0,
                            "Special Attack": 0, "Special Defense": 0, "Speed": 0,
                            "total": 0
                        },
                        "ev_explanation": "Not specified",
                        "role_in_team": "Not specified"
                    }
                    
                    for field, default in pokemon_fields.items():
                        if field not in pokemon:
                            pokemon[field] = default
                    
                    cleaned_team.append(pokemon)
            
            result["pokemon_team"] = cleaned_team
        
        return result