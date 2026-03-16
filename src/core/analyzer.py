"""
Core VGC analysis engine using Google Gemini AI.
"""

import json
import re
import logging
from typing import Dict, Optional, Any, List
from google import genai
from google.genai import types
import streamlit as st

from utils.config import Config, POKEMON_NAME_TRANSLATIONS, MOVE_NAME_TRANSLATIONS
from utils.errors import APILimitError, get_user_friendly_api_error_message
from core.scraper import ArticleScraper
from core.pokemon_validator import PokemonValidator
from core.prompts import ANALYSIS_PROMPT
from utils.image_analyzer import (
    extract_images_from_url,
    filter_vgc_images,
    analyze_image_with_vision,
    extract_ev_spreads_from_image_analysis
)

# Configure logging for analysis pipeline debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Re-export for backward compatibility (app.py imports these from here)
__all__ = ["GeminiVGCAnalyzer", "APILimitError", "get_user_friendly_api_error_message"]


@st.cache_data
def get_pokemon_name_translations() -> Dict[str, str]:
    """Get Pokemon name translations (cached for performance)"""
    return POKEMON_NAME_TRANSLATIONS


@st.cache_data
def get_move_name_translations() -> Dict[str, str]:
    """Get move name translations (cached for performance)"""
    return MOVE_NAME_TRANSLATIONS


@st.cache_resource
def initialize_gemini_client(api_key: str):
    """Initialize Gemini client (cached as resource for all users)"""
    return genai.Client(api_key=api_key)


class GeminiVGCAnalyzer:
    """Pokemon VGC analyzer using Google Gemini AI"""

    def __init__(self, api_key: str = None):
        """
        Initialize the analyzer with Gemini configuration

        Args:
            api_key: Optional Google Gemini API key. If not provided, will try to get from config.
        """
        logger.info("Initializing GeminiVGCAnalyzer")

        try:
            # Get API key from parameter or config
            self.api_key = api_key or Config.get_google_api_key()
            if not self.api_key:
                logger.error("No Google API key found")
                raise ValueError("Google API key is required for analysis")

            logger.info("API key found, initializing cached client")
            # Use cached client initialization
            self.client = initialize_gemini_client(self.api_key)
            self.model_name = "gemini-2.5-flash"
            logger.info("Gemini client initialized successfully via cache")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini analyzer: {str(e)}")
            raise

        # Generation config for consistent output
        self.generation_config = types.GenerateContentConfig(
            temperature=0.1,
            top_p=0.8,
            top_k=40,
            max_output_tokens=16000,
            response_mime_type="application/json",
        )
        
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
        # Enhanced content validation with comprehensive logging
        logger.info(f"Starting analysis for content of length {len(content) if content else 0} chars")
        logger.info(f"URL: {url if url else 'Direct text input'}")
        
        if not content:
            logger.error("No content provided for analysis")
            raise ValueError(
                "No content provided for analysis. Please check that the article was successfully extracted."
            )
        
        content_length = len(content.strip())
        logger.info(f"Content length: {content_length} characters")
        
        if content_length < 50:
            logger.error(f"Content too short: {content_length} chars")
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


        try:
            # Enhanced content preprocessing for better analysis
            processed_content = self._preprocess_content_for_analysis(content)
            
            # Detect content formats for intelligent extraction
            detected_formats = self._detect_content_formats(content)
            logger.info(f"Format detection scores: {detected_formats}")
            
            # Create format-aware prompt with extraction hints
            prompt = self._get_analysis_prompt()
            if any(score > 0.3 for score in detected_formats.values()):
                format_hints = self._create_format_hints(detected_formats)
                prompt = f"{prompt}\n\n{format_hints}"
            full_prompt = f"{prompt}\n\nCONTENT TO ANALYZE:\n{processed_content}"

            # Generate response with retry logic
            result = self._generate_with_fallbacks(full_prompt, content, url)

            # Enhanced validation with confidence scoring
            result = self._validate_and_enhance_result(result, content, url)

            # Add fresh analysis metadata
            from datetime import datetime
            result["is_cached_result"] = False
            result["analysis_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")


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

    def analyze_article_with_images(self, content: str, url: str = None) -> Dict[str, Any]:
        """
        Enhanced article analysis combining text and image analysis
        
        Args:
            content: Article content to analyze
            url: Optional URL for image extraction and context
            
        Returns:
            Analysis result combining text and image data
        """
        try:
            # Start with text-only analysis
            text_result = self.analyze_article(content, url)
            
            # If URL is provided, attempt image analysis
            if url:
                try:
                    # Extract and analyze images
                    image_analysis = self._analyze_images_from_url(url)
                    
                    # Merge image data into text analysis
                    if image_analysis:
                        text_result = self._merge_text_and_image_analysis(text_result, image_analysis)
                        
                        # Add image analysis notes
                        existing_notes = text_result.get("translation_notes", "")
                        image_notes = f"Enhanced with image analysis from {len(image_analysis.get('analyzed_images', []))} images"
                        text_result["translation_notes"] = f"{existing_notes} | {image_notes}".strip(" |")
                        
                except Exception as e:
                    # Image analysis failed, add note but continue with text analysis
                    existing_notes = text_result.get("translation_notes", "")
                    failure_note = f"Image analysis failed: {str(e)}"
                    text_result["translation_notes"] = f"{existing_notes} | {failure_note}".strip(" |")
            
            # Note: validation already applied inside analyze_article() — do not call again

            # Add fresh analysis metadata
            from datetime import datetime
            text_result["is_cached_result"] = False
            text_result["analysis_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
            return text_result
            
        except Exception as e:
            # If text analysis also fails, re-raise the error
            raise e
    
    def _analyze_images_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract and analyze images from URL for VGC content
        
        Args:
            url: URL to extract images from
            
        Returns:
            Dictionary containing image analysis results or None if failed
        """
        try:
            # Extract images from URL
            all_images = extract_images_from_url(url, max_images=10)
            
            if not all_images:
                return None
                
            # Filter for VGC-relevant images
            vgc_images = filter_vgc_images(all_images)
            
            if not vgc_images:
                # If no VGC-specific images found, try a few of the best general images
                vgc_images = all_images[:3]
            
            analyzed_images = []
            extracted_data = {
                "pokemon_team": [],
                "ev_spreads": [],
                "strategy_insights": []
            }
            
            # Analyze each image
            for image_info in vgc_images:
                try:
                    if image_info.get('data') and image_info.get('format'):
                        # Analyze image with vision client
                        vision_analysis = analyze_image_with_vision(
                            image_info['data'],
                            image_info['format'],
                            self.client,
                            self.model_name
                        )
                        
                        if vision_analysis:
                            analyzed_images.append({
                                'url': image_info.get('url', ''),
                                'analysis': vision_analysis,
                                'confidence': image_info.get('confidence_score', 0.5)
                            })
                            
                            # Extract EV spreads from analysis
                            ev_spreads = extract_ev_spreads_from_image_analysis(vision_analysis)
                            if ev_spreads:
                                extracted_data["ev_spreads"].extend(ev_spreads)
                                
                except Exception as img_error:
                    # Skip this image but continue with others
                    continue
            
            if analyzed_images:
                extracted_data["analyzed_images"] = analyzed_images
                return extracted_data
                
            return None
            
        except Exception as e:
            # Return None to indicate image analysis failed
            return None
    
    def _merge_text_and_image_analysis(self, text_result: Dict[str, Any], image_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ULTRA-ENHANCED text and image analysis integration for note.com articles
        Prioritizes image EV spreads when text analysis fails to detect them
        
        Args:
            text_result: Result from text-only analysis
            image_data: Result from image analysis
            
        Returns:
            Merged analysis result with intelligent EV integration
        """
        merged_result = text_result.copy()
        
        # Extract EV spreads and Pokemon data from images
        image_ev_spreads = image_data.get("ev_spreads", [])
        analyzed_images = image_data.get("analyzed_images", [])
        
        # Enhance Pokemon team data with image information
        pokemon_team = merged_result.get("pokemon_team", [])
        
        # PRIORITY SYSTEM: Image EVs take precedence when text EVs are poor
        if image_ev_spreads and pokemon_team:
            
            # Sort image EV spreads by confidence (high confidence first)
            sorted_image_evs = sorted(image_ev_spreads, 
                                    key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("confidence", "low"), 0), 
                                    reverse=True)
            
            ev_assignment_log = []
            
            for i, pokemon in enumerate(pokemon_team):
                # Analyze current EV situation for this Pokemon
                current_evs = pokemon.get("evs", "Not specified")
                current_spread = pokemon.get("ev_spread", {})
                current_total = current_spread.get("total", 0) if isinstance(current_spread, dict) else 0
                
                # ULTRA-STRICT: Only use image EVs if text analysis completely failed (enhanced for Japanese VGC)
                needs_image_evs = any([
                    current_evs == "Not specified",
                    current_evs == "",
                    current_total <= 0,  # Only if completely no data
                    isinstance(current_evs, str) and "not found" in current_evs.lower(),
                    isinstance(current_evs, str) and "not specified" in current_evs.lower(),
                    isinstance(current_evs, str) and len(current_evs) < 3,  # Too short to be real EV spread
                ])
                
                # ULTRA-STRICT: Assign image EV spread with validation against generation
                if needs_image_evs and sorted_image_evs:
                    best_image_spread = sorted_image_evs.pop(0)  # Take highest confidence spread
                    
                    # Additional validation to prevent AI generation
                    spread_total = best_image_spread.get("total", 0)
                    
                    if (best_image_spread.get("is_valid", False) and 
                        spread_total > 0 and spread_total <= 508 and
                        not (spread_total == 508 and len([p for p in pokemon_team if p.get("ev_spread", {}).get("total", 0) == 508]) >= 2)):  # Prevent multiple 508s
                        
                        # Convert image EV spread to standard format
                        pokemon["evs"] = best_image_spread["format"]
                        pokemon["ev_spread"] = {
                            "HP": best_image_spread.get("hp", 0),
                            "Attack": best_image_spread.get("attack", 0), 
                            "Defense": best_image_spread.get("defense", 0),
                            "Special Attack": best_image_spread.get("special_attack", 0),
                            "Special Defense": best_image_spread.get("special_defense", 0),
                            "Speed": best_image_spread.get("speed", 0),
                            "total": spread_total,
                            "source": f"image_analysis_{best_image_spread.get('confidence', 'medium')}"
                        }
                        
                        # Preserve existing strategic reasoning from article text
                        existing_explanation = pokemon.get("ev_explanation", "")
                        has_meaningful_explanation = self._has_meaningful_strategic_reasoning(existing_explanation)
                        
                        confidence = best_image_spread.get("confidence", "medium")
                        
                        if has_meaningful_explanation:
                            # Preserve article reasoning, just note EV source confirmation
                            pokemon["ev_explanation"] = f"{existing_explanation} (EVs confirmed from image analysis)"
                            logger.debug(f"Preserved article reasoning for Pokemon {i+1}, added image confirmation")
                        else:
                            # No meaningful reasoning from text, use image-based description as fallback
                            pokemon["ev_explanation"] = f"EV spread detected from team image ({confidence} confidence): {best_image_spread['format']}"
                            logger.debug(f"Used image-based EV description for Pokemon {i+1} (no article reasoning found)")
                        
                        ev_assignment_log.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): Assigned {confidence} confidence EVs from image")
                    else:
                        # Image EV failed validation - preserve existing reasoning if meaningful
                        existing_explanation = pokemon.get("ev_explanation", "")
                        has_meaningful_explanation = self._has_meaningful_strategic_reasoning(existing_explanation)
                        
                        if has_meaningful_explanation:
                            # Keep the meaningful article reasoning, note image validation failure
                            pokemon["ev_explanation"] = f"{existing_explanation} (Note: Image EV data failed validation)"
                            logger.debug(f"Preserved article reasoning for Pokemon {i+1} despite image validation failure")
                        else:
                            # No meaningful reasoning to preserve, use validation failure message
                            pokemon["ev_explanation"] = "Image EV data failed validation (potential AI generation detected)"
                        
                        ev_assignment_log.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): Image EVs rejected due to suspicious pattern")
                
                # Even if we don't replace EVs, log the decision
                elif not needs_image_evs:
                    ev_assignment_log.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): Kept text EVs (total: {current_total})")
            
            # Add diagnostic information
            if ev_assignment_log:
                existing_notes = merged_result.get("translation_notes", "")
                ev_notes = " | ".join(ev_assignment_log)
                merged_result["translation_notes"] = f"{existing_notes} | EV Integration: {ev_notes}".strip(" |")
        
        # ENHANCEMENT: Cross-validate Pokemon identifications
        # If image analysis identified Pokemon differently than text, note the discrepancy
        if analyzed_images and pokemon_team:
            for img_analysis in analyzed_images:
                if "POKEMON" in img_analysis.get("analysis", "").upper():
                    # This is a basic cross-validation - a more sophisticated approach would parse the image analysis
                    existing_notes = merged_result.get("translation_notes", "")
                    img_note = f"Cross-referenced with {len(analyzed_images)} team images"
                    merged_result["translation_notes"] = f"{existing_notes} | {img_note}".strip(" |")
                    break
        
        # ENHANCEMENT: Boost confidence if both text and image agree on Pokemon
        if "analysis_confidence" in merged_result:
            # Boost confidence based on image analysis quality
            image_boost = 0
            if len(image_ev_spreads) >= len(pokemon_team) / 2:  # Images provided substantial EV data
                image_boost = 0.15
            elif len(analyzed_images) > 0:  # At least some image analysis
                image_boost = 0.1
                
            merged_result["analysis_confidence"] = min(1.0, merged_result["analysis_confidence"] + image_boost)
            
            if image_boost > 0:
                existing_notes = merged_result.get("translation_notes", "")
                confidence_note = f"Confidence boosted by image analysis (+{int(image_boost*100)}%)"
                merged_result["translation_notes"] = f"{existing_notes} | {confidence_note}".strip(" |")
        
        return merged_result
    
    def _detect_content_formats(self, content: str) -> Dict[str, float]:
        """
        Intelligent format detection to determine EV extraction strategy
        
        Returns:
            Dictionary of format types with confidence scores (0.0-1.0)
        """
        format_scores = {
            "image_stats": 0.0,          # H177 +252 format from images
            "japanese_direct": 0.0,      # 努力値:252-0-4-252-0-0
            "abbreviated_hybrid": 0.0,   # 努力値：H252 A4 S252  
            "technical_calc": 0.0,       # 実数値: followed by 努力値:
            "japanese_grid": 0.0,        # ＨＰ: 252  こうげき: 0
            "standard_slash": 0.0,       # HP: 252 / Attack: 0
            "written_format": 0.0        # HP252振り, すばやさ252
        }
        
        # Count occurrences of each format pattern
        
        # Image stats format detection
        image_patterns = [
            r'[HABCDS]\d{3}\s*\+\d{1,3}',  # H177 +252
            r'\d{3}\s*\+\d{1,3}',          # 177 +252
            r'\(\d{1,3}\)',                # (252) in parentheses
        ]
        for pattern in image_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["image_stats"] += matches * 0.2
        
        # Japanese direct format (highest priority)
        japanese_direct_patterns = [
            r'努力値\s*[:：]\s*\d+-\d+-\d+-\d+-\d+-\d+',
            r'個体値調整\s*[:：]\s*\d+-\d+-\d+-\d+-\d+-\d+',
            r'EV配分\s*[:：]\s*\d+-\d+-\d+-\d+-\d+-\d+',
        ]
        for pattern in japanese_direct_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["japanese_direct"] += matches * 0.5
        
        # Abbreviated hybrid format
        hybrid_patterns = [
            r'努力値\s*[:：]\s*[HABCDS]\d+\s+[HABCDS]\d+',
            r'個体値調整\s*[:：]\s*[HABCDS]\d+',
            r'[HABCDS]\d{1,3}\s+[HABCDS]\d{1,3}',  # H252 A4 pattern
        ]
        for pattern in hybrid_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["abbreviated_hybrid"] += matches * 0.3
        
        # Technical calculation format
        if re.search(r'実数値\s*[:：]', content):
            # Look for 努力値: within next few lines after 実数値:
            tech_matches = len(re.findall(r'実数値.*?努力値', content, re.DOTALL))
            format_scores["technical_calc"] += tech_matches * 0.4
        
        # Japanese grid format
        grid_patterns = [
            r'ＨＰ\s*[:：]\s*\d+',
            r'こうげき\s*[:：]\s*\d+',
            r'とくこう\s*[:：]\s*\d+',
            r'すばやさ\s*[:：]\s*\d+',
        ]
        for pattern in grid_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["japanese_grid"] += matches * 0.2
        
        # Standard slash format
        slash_patterns = [
            r'HP\s*[:：]\s*\d+\s*/\s*Attack',
            r'\d+/\d+/\d+/\d+/\d+/\d+',  # Standard 6-number format
        ]
        for pattern in slash_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["standard_slash"] += matches * 0.3
        
        # Written format (HP252振り style)
        written_patterns = [
            r'[ＨHP]\d+振り',
            r'すばやさ\d+',
            r'特攻\d+',
            r'物理耐久',
            r'特殊耐久',
        ]
        for pattern in written_patterns:
            matches = len(re.findall(pattern, content))
            format_scores["written_format"] += matches * 0.2
        
        # Normalize scores (cap at 1.0)
        for format_type in format_scores:
            format_scores[format_type] = min(1.0, format_scores[format_type])
        
        # Log detected formats for debugging
        detected_formats = [f for f, score in format_scores.items() if score > 0.1]
        if detected_formats:
            logger.info(f"Detected EV formats: {detected_formats}")
        
        return format_scores
    
    def _create_format_hints(self, detected_formats: Dict[str, float]) -> str:
        """
        Create format-specific extraction hints based on detected formats
        
        Args:
            detected_formats: Dictionary of format types with confidence scores
            
        Returns:
            String with specific extraction instructions for detected formats
        """
        hints = []
        sorted_formats = sorted(detected_formats.items(), key=lambda x: x[1], reverse=True)
        
        for format_type, score in sorted_formats:
            if score < 0.3:
                continue
                
            if format_type == "japanese_direct":
                hints.append("""
🚨 HIGH PRIORITY: Japanese Direct EV Format Detected (努力値:252-0-4-252-0-0)
- Look specifically for patterns like "努力値:252-0-4-252-0-0" or "個体値調整:244-0-12-252-0-0"
- These are in HP/Attack/Defense/SpA/SpD/Speed order
- This format has HIGHEST extraction priority - scan every line for these patterns""")
            
            elif format_type == "abbreviated_hybrid":
                hints.append("""
🎯 HYBRID FORMAT DETECTED: Japanese prefix + abbreviated stats (努力値：H252 A4 S252)  
- Look for patterns like "努力値：H252 A4 B156 D68 S28"
- Convert stat letters: H=HP, A=Attack, B=Defense, C=Special Attack, D=Special Defense, S=Speed
- May have Japanese prefixes followed by abbreviated English stats""")
            
            elif format_type == "technical_calc":
                hints.append("""
⚙️ TECHNICAL CALCULATION FORMAT DETECTED: 実数値: followed by 努力値:
- Look for "実数値:" lines followed by "努力値:" within 2-3 lines  
- The second line contains the actual EV distribution to extract
- May include speed benchmarks and damage calculations nearby""")
            
            elif format_type == "image_stats":
                hints.append("""
📊 IMAGE STATS FORMAT DETECTED: Calculated stats with EV indicators
- Look for patterns like "H177 +252" or "177 +252" or "(252)"
- Numbers in parentheses are usually EV values
- Numbers with + signs may indicate EV investments""")
            
            elif format_type == "japanese_grid":
                hints.append("""
📋 JAPANESE GRID FORMAT DETECTED: Full stat names with values
- Look for "ＨＰ: 252", "こうげき: 0", "とくこう: 252" patterns
- Extract values after colons for each Japanese stat name
- May be arranged in table/grid layout""")
        
        # Add move extraction guidance for all formats
        hints.append("""
🎮 ADVANCED MOVE EXTRACTION PROTOCOL:
**Primary Strategy**: Look for structured move lists
- "わざ1:", "わざ2:", "わざ3:", "わざ4:" (highest priority)
- "技:" sections with move names listed
- Move names near Pokemon names in context

**Secondary Strategy**: Context-based detection
- Damage calculation mentions (e.g., "イカサマで確定1発")
- Strategic discussions mentioning specific moves
- Signature move references that identify Pokemon

**Tertiary Strategy**: Pattern recognition
- Japanese move names followed by explanations
- Move effects described in strategic context
- Type effectiveness discussions

**Validation Requirements**:
- Each Pokemon must have exactly 4 moves
- Move names must be translated to official English names
- Flag incomplete movesets for manual review""")
        
        if hints:
            return f"**INTELLIGENT EXTRACTION SYSTEM - DETECTED FORMATS & PROTOCOLS:**\n" + "\n".join(hints)
        return ""

    def _preprocess_content_for_analysis(self, content: str) -> str:
        """Preprocess content to improve analysis accuracy.

        Gemini 2.5 Flash has a 1M token context window (~4M chars),
        so we clean noise but preserve all article content to avoid
        dropping Pokemon data from the end of longer articles.
        """
        # Remove excessive whitespace but preserve newlines for structure
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[^\S\n]+', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Filter out obvious noise lines (very short non-content, pure URLs, etc.)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue
            # Skip lines that are just URLs, pure symbols, or very short noise
            if re.match(r'^https?://\S+$', line):
                continue
            if len(line) < 3 and not re.search(r'[\u3040-\u9fff]', line):
                continue
            cleaned_lines.append(line)

        result = '\n'.join(cleaned_lines).strip()

        # Safety cap: truncate only truly enormous pages (well within Gemini limits)
        max_chars = 30000
        if len(result) > max_chars:
            # Try to cut at a paragraph boundary
            truncated = result[:max_chars]
            last_break = truncated.rfind('\n\n')
            if last_break > max_chars * 0.8:
                result = truncated[:last_break]
            else:
                result = truncated

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
        logger.info("Making standard API call to Gemini")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name, contents=prompt, config=self.generation_config
            )
            logger.info("Gemini API call successful")
            
            if not response or not hasattr(response, 'text'):
                logger.error("Invalid response object from Gemini API")
                raise ValueError("Invalid response from Gemini API")
                
            if not response.text:
                logger.error("Empty response text from Gemini API")
                raise ValueError("Empty response from Gemini API")

            logger.info(f"Received response: {len(response.text)} chars")
            logger.debug(f"Response preview: {response.text[:200]}...")
            
            return self._parse_json_response(response.text)
            
        except Exception as e:
            # Enhanced error detection for different API failure types
            error_msg = str(e).lower()
            original_error = str(e)
            
            # Detect API authentication errors
            if ('api key' in error_msg or 'authentication' in error_msg or 
                'unauthorized' in error_msg or 'invalid_api_key' in error_msg):
                logger.error(f"API authentication error: {original_error}")
                raise APILimitError(
                    "API authentication failed. Please check your Google API key.",
                    error_type="authentication"
                )
            
            # Detect rate limiting errors (requests per minute/second)
            elif (('429' in error_msg or 'rate' in error_msg or 'requests per minute' in error_msg or
                   'rate_limit_exceeded' in error_msg or 'too many requests' in error_msg) and
                  'quota' not in error_msg):
                logger.error(f"API rate limit error: {original_error}")
                # Try to extract retry-after time if available
                retry_after = 60  # Default to 1 minute
                import re
                retry_match = re.search(r'retry.after[:\s]+(\d+)', error_msg)
                if retry_match:
                    retry_after = int(retry_match.group(1))
                    
                raise APILimitError(
                    "API rate limit exceeded. Too many requests in a short time.",
                    error_type="rate_limit",
                    retry_after=retry_after
                )
            
            # Detect quota exceeded errors (daily/monthly limits) - Enhanced patterns for Google API
            elif ('quota' in error_msg or 'resource has been exhausted' in error_msg or
                  'quota exceeded for quota metric' in error_msg or 'resource_exhausted' in error_msg or
                  'exceeded your current quota' in error_msg or 'billing details' in error_msg or
                  'quota_metric' in error_msg or 'violations' in error_msg or 
                  ('429' in error_msg and ('quota' in error_msg or 'exceeded' in error_msg))):
                logger.error(f"API quota exceeded: {original_error}")
                
                # Try to extract retry delay from Google API error response
                retry_after = None
                import re
                retry_match = re.search(r'retry_delay.*?seconds[:\s]+(\d+)', original_error)
                if retry_match:
                    retry_after = int(retry_match.group(1))
                
                raise APILimitError(
                    "API quota exceeded. You've reached your daily or monthly limit.",
                    error_type="quota_exceeded",
                    retry_after=retry_after
                )
            
            # Detect model not found errors
            elif ('not found' in error_msg and 'model' in error_msg) or 'models/' in error_msg and '404' in error_msg:
                logger.error(f"Model not found: {original_error}")
                raise APILimitError(
                    f"Model '{self.model_name}' is not available for your API key. "
                    f"Your account may not have access to this model yet. "
                    f"Try checking available models at https://aistudio.google.com.",
                    error_type="model_not_found"
                )

            # Detect service disabled errors
            elif ('service_disabled' in error_msg or 'has not been used' in error_msg or
                  'api has not been used' in error_msg or 'enable the api' in error_msg):
                logger.error(f"API service disabled: {original_error}")
                raise APILimitError(
                    "Gemini API service is disabled or not enabled for this project. Please enable the Generative Language API in Google Cloud Console.",
                    error_type="service_disabled"
                )

            # Generic API errors
            else:
                logger.error(f"General API error: {original_error}")
                raise ValueError(f"API call failed: {original_error}")
    
    def _generate_with_reduced_content(self, prompt: str, content: str) -> Dict[str, Any]:
        """Fallback with reduced content size"""
        # Rebuild prompt with reduced content instead of string replace
        # (replace won't match because prompt was built with processed_content, not raw content)
        reduced_content = content[:4000]
        analysis_prompt = self._get_analysis_prompt()
        reduced_prompt = f"{analysis_prompt}\n\nCONTENT TO ANALYZE:\n{reduced_content}"
        
        response = self.client.models.generate_content(
            model=self.model_name, contents=reduced_prompt, config=self.generation_config
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
        
        response = self.client.models.generate_content(
            model=self.model_name, contents=simple_prompt, config=self.generation_config
        )

        if not response.text:
            raise ValueError("Empty response from Gemini API")

        result = self._parse_json_response(response.text)
        # Mark as simplified analysis
        result["translation_notes"] = result.get("translation_notes", "") + " | Simplified analysis due to content complexity"
        return result
    
    def _validate_and_enhance_result(self, result: Dict[str, Any], content: str, url: str = None) -> Dict[str, Any]:
        """Enhanced validation with confidence scoring and improvements"""
        # CRITICAL FIX: Validate that result is a dictionary before processing
        if not isinstance(result, dict):
            print(f"Warning: _validate_and_enhance_result received non-dict type: {type(result)}")
            return {
                "title": "Type Error in Validation",
                "pokemon_team": [],
                "overall_strategy": "Unable to process due to type error in validation",
                "regulation": "Not specified",
                "translation_notes": f"Validation error: expected dict, got {type(result).__name__}",
                "analysis_confidence": 0.0,
                "parsing_error": True
            }
        
        # Apply original validation
        result = self._validate_and_clean_result(result)
        result = self.pokemon_validator.fix_pokemon_name_translations(result)
        result = self.pokemon_validator.apply_pokemon_validation(result)
        
        # ULTRA-CRITICAL: Validate Pokemon identification using signature moves
        result = self.pokemon_validator.validate_pokemon_moves_consistency(result)
        
        # ULTRA-CRITICAL: Translate Japanese stat abbreviations in strategic reasoning
        result = self.pokemon_validator.translate_strategic_reasoning_stats(result)
        
        # Add confidence scoring
        confidence_score = self._calculate_analysis_confidence(result, content)
        result["analysis_confidence"] = confidence_score
        
        # Add helpful context for genuinely low confidence (lowered threshold)
        if confidence_score < 0.4:
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
        """Calculate confidence score for the analysis (improved to be less conservative)"""
        confidence = 0.6  # Increased base confidence (was 0.5)
        
        # Pokemon team quality (more generous scoring)
        pokemon_team = result.get("pokemon_team", [])
        if pokemon_team:
            confidence += 0.15  # Bonus for having any Pokemon team
            
            # Check for meaningful Pokemon names (more generous)
            valid_names = sum(1 for p in pokemon_team 
                            if p.get("name", "Unknown") not in ["Unknown", "Unknown Pokemon", "Not specified", ""])
            if valid_names > 0:
                # More generous calculation - even 1 valid Pokemon gets good score
                name_ratio = valid_names / len(pokemon_team)
                if name_ratio >= 0.8:  # Most Pokemon identified
                    confidence += 0.15
                elif name_ratio >= 0.5:  # At least half identified
                    confidence += 0.1
                elif name_ratio > 0:  # Some identified
                    confidence += 0.05
        
        # Content indicators in original text (expanded terms)
        vgc_terms = ['ポケモン', '構築', 'pokemon', 'vgc', 'team', 'battle', '努力値', 'evs', '技', 'moves', '特性', 'ability']
        found_terms = sum(1 for term in vgc_terms if term in content.lower())
        if found_terms >= 3:
            confidence += 0.1  # Strong VGC content
        elif found_terms > 0:
            confidence += 0.05  # Some VGC content
        
        # JSON parsing success (less penalty for minor issues)
        if not result.get("parsing_error"):
            confidence += 0.05  # Small bonus for perfect parsing
        elif result.get("recovery_successful"):
            confidence += 0.02  # Small bonus for successful recovery
        
        # Bonus for having strategy or regulation info
        if result.get("overall_strategy") and result.get("overall_strategy") not in ["Not specified", ""]:
            confidence += 0.05
        if result.get("regulation") and result.get("regulation") not in ["Not specified", ""]:
            confidence += 0.05
            
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
        """Get the VGC analysis prompt. See core/prompts.py for the full text."""
        return ANALYSIS_PROMPT

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini API.

        With response_mime_type="application/json", Gemini returns valid JSON directly.
        We keep a lightweight fallback for edge cases (network issues, truncation).
        """
        logger.info("Starting JSON parsing of API response")
        logger.debug(f"Response text length: {len(response_text)} chars")

        text = response_text.strip()

        # Strategy 1: direct parse (expected path with response_mime_type)
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                logger.info(f"JSON parsed directly - {len(result.get('pokemon_team', []))} Pokemon")
                return result
        except json.JSONDecodeError:
            logger.debug("Direct JSON parse failed, trying extraction")

        # Strategy 2: extract JSON object from surrounding text (rare)
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if isinstance(result, dict):
                    logger.info("JSON extracted from surrounding text")
                    return result
            except json.JSONDecodeError:
                pass

        logger.warning("All JSON parsing strategies failed, returning fallback")
        return self._create_fallback_result(response_text)
    
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
    
    def _validate_pokemon_team_structure(self, pokemon_team: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and enhance Pokemon team structure"""
        if not isinstance(pokemon_team, list):
            logger.warning(f"Pokemon team is not a list: {type(pokemon_team)}")
            return []
        
        validated_team = []
        for i, pokemon in enumerate(pokemon_team):
            if not isinstance(pokemon, dict):
                logger.warning(f"Pokemon {i} is not a dict: {type(pokemon)}")
                continue
            
            # Ensure required fields exist with defaults
            validated_pokemon = {
                "name": pokemon.get("name", f"Unknown Pokemon {i+1}"),
                "ability": pokemon.get("ability", "Not specified"),
                "held_item": pokemon.get("held_item", pokemon.get("item", "Not specified")),
                "nature": pokemon.get("nature", "Not specified"),
                "tera_type": pokemon.get("tera_type", pokemon.get("teratype", "Unknown")),
                "role": pokemon.get("role", "Not specified"),
                "moves": pokemon.get("moves", []),
                "evs": self._normalize_ev_format(pokemon.get("evs", "Not specified")),
                "ev_explanation": pokemon.get("ev_explanation", "No explanation provided")
            }
            
            validated_team.append(validated_pokemon)
            
        return validated_team
    
    def _normalize_ev_format(self, evs) -> str:
        """Normalize EV format to HP/Atk/Def/SpA/SpD/Spe"""
        if evs == "Not specified" or not evs:
            return "Not specified"
        
        # If it's already in string format, return as-is
        if isinstance(evs, str):
            # Check if it matches expected format (6 numbers separated by /)
            if "/" in evs and len(evs.split("/")) == 6:
                return evs
            return evs  # Return as-is for now, let rendering handle it
        
        # If it's a dict, convert to string format
        if isinstance(evs, dict):
            stat_order = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]
            ev_values = []
            for stat in stat_order:
                # Try different possible key names
                value = evs.get(stat, evs.get(stat.replace("_", ""), evs.get(stat[:3], 0)))
                ev_values.append(str(value))
            return "/".join(ev_values)
        
        return str(evs)
    
    def _is_complete_pokemon(self, pokemon: Dict[str, Any]) -> bool:
        """Check if a Pokemon has complete information for rendering"""
        required_fields = ["name", "ability", "held_item", "moves", "evs"]
        has_essential_data = all(
            pokemon.get(field) and pokemon.get(field) != "Not specified" 
            for field in ["name", "moves"]
        )
        has_some_stats = pokemon.get("evs") != "Not specified" or len(pokemon.get("moves", [])) > 0
        return has_essential_data and has_some_stats
    
    def _validate_extraction_completeness(self, pokemon_team: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Comprehensive validation of extraction completeness with cross-reference checks
        
        Args:
            pokemon_team: List of Pokemon data
            
        Returns:
            Dictionary with validation results and recommendations
        """
        validation_report = {
            "overall_quality": "high",
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "completeness_score": 1.0,
            "pokemon_reports": []
        }
        
        if not pokemon_team:
            validation_report["overall_quality"] = "failed"
            validation_report["issues"].append("No Pokemon team found")
            validation_report["completeness_score"] = 0.0
            return validation_report
        
        total_quality_score = 0
        for i, pokemon in enumerate(pokemon_team):
            pokemon_report = self._validate_single_pokemon(pokemon, i)
            validation_report["pokemon_reports"].append(pokemon_report)
            total_quality_score += pokemon_report["quality_score"]
            
            # Collect issues and warnings
            validation_report["issues"].extend(pokemon_report["issues"])
            validation_report["warnings"].extend(pokemon_report["warnings"])
        
        # Calculate overall completeness
        avg_quality = total_quality_score / len(pokemon_team)
        validation_report["completeness_score"] = avg_quality
        
        # Determine overall quality
        if avg_quality >= 0.8:
            validation_report["overall_quality"] = "high"
        elif avg_quality >= 0.6:
            validation_report["overall_quality"] = "medium"
        elif avg_quality >= 0.3:
            validation_report["overall_quality"] = "low"
        else:
            validation_report["overall_quality"] = "failed"
        
        # Generate recommendations
        if validation_report["issues"]:
            validation_report["recommendations"].append("Consider manual review of Pokemon with critical issues")
        if avg_quality < 0.7:
            validation_report["recommendations"].append("Extraction may be incomplete - verify source article format")
        
        return validation_report
    
    def _validate_single_pokemon(self, pokemon: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate a single Pokemon's data completeness and consistency"""
        report = {
            "pokemon_index": index,
            "name": pokemon.get("name", f"Pokemon {index+1}"),
            "quality_score": 1.0,
            "issues": [],
            "warnings": [],
            "missing_fields": []
        }
        
        # Check required fields
        required_fields = ["name", "ability", "held_item", "moves", "evs"]
        missing_count = 0
        
        for field in required_fields:
            value = pokemon.get(field)
            if not value or value == "Not specified":
                report["missing_fields"].append(field)
                missing_count += 1
        
        # Check move count
        moves = pokemon.get("moves", [])
        if len(moves) == 0:
            report["issues"].append(f"Pokemon {index+1}: No moves found")
            report["quality_score"] -= 0.3
        elif len(moves) < 4:
            report["warnings"].append(f"Pokemon {index+1}: Only {len(moves)}/4 moves found")
            report["quality_score"] -= 0.1 * (4 - len(moves))
        
        # Check EV validity
        evs = pokemon.get("evs", "Not specified")
        if evs == "Not specified":
            report["warnings"].append(f"Pokemon {index+1}: No EV spread found")
            report["quality_score"] -= 0.2
        else:
            ev_validation = self._validate_ev_spread(evs)
            if not ev_validation["valid"]:
                report["issues"].append(f"Pokemon {index+1}: Invalid EV spread - {ev_validation['reason']}")
                report["quality_score"] -= 0.2
        
        # Penalize for missing critical fields
        if missing_count > 2:
            report["quality_score"] -= 0.3
        elif missing_count > 0:
            report["quality_score"] -= 0.1 * missing_count
        
        # Ensure score doesn't go below 0
        report["quality_score"] = max(0.0, report["quality_score"])
        
        return report
    
    def _validate_ev_spread(self, evs: str) -> Dict[str, Any]:
        """Validate EV spread format and values"""
        if evs == "Not specified":
            return {"valid": False, "reason": "No EV spread provided"}
        
        # Check if it's in standard format (e.g., "252/0/4/252/0/0")
        if "/" in evs:
            try:
                ev_values = [int(x.strip()) for x in evs.split("/")]
                if len(ev_values) != 6:
                    return {"valid": False, "reason": f"Expected 6 EV values, got {len(ev_values)}"}
                
                total_evs = sum(ev_values)
                if total_evs > 508:
                    return {"valid": False, "reason": f"EV total {total_evs} exceeds maximum of 508"}
                
                # Check individual values
                if any(ev > 252 for ev in ev_values):
                    return {"valid": False, "reason": "Individual EV values cannot exceed 252"}
                
                if any(ev < 0 for ev in ev_values):
                    return {"valid": False, "reason": "EV values cannot be negative"}
                
                return {"valid": True, "total": total_evs, "values": ev_values}
                
            except ValueError:
                return {"valid": False, "reason": "EV values contain non-numeric data"}
        
        # For other formats, just check it's not empty
        return {"valid": True if evs.strip() else False, "reason": "Non-standard EV format"}
    
    def _cross_validate_team_data(self, pokemon_team: List[Dict[str, Any]]) -> List[str]:
        """Cross-validate team data for consistency and competitive viability"""
        warnings = []
        
        # Check for duplicate Pokemon (except legitimate forms)
        pokemon_names = [p.get("name", "") for p in pokemon_team]
        duplicates = [name for name in set(pokemon_names) if pokemon_names.count(name) > 1 and name != ""]
        if duplicates:
            warnings.append(f"Duplicate Pokemon detected: {duplicates}")
        
        # Check EV distribution patterns
        ev_totals = []
        for pokemon in pokemon_team:
            evs = pokemon.get("evs", "Not specified")
            if "/" in evs:
                try:
                    total = sum(int(x.strip()) for x in evs.split("/"))
                    ev_totals.append(total)
                except ValueError:
                    continue
        
        if len(ev_totals) > 1:
            # Check for suspiciously similar totals (might indicate AI generation)
            if len(set(ev_totals)) == 1 and ev_totals[0] == 508:
                warnings.append("All Pokemon have identical maximum EV totals - verify authenticity")
        
        return warnings
    
    def _has_meaningful_strategic_reasoning(self, explanation: str) -> bool:
        """
        Determine if an EV explanation contains meaningful strategic reasoning from article text
        
        Args:
            explanation: The ev_explanation string to evaluate
            
        Returns:
            True if the explanation contains meaningful strategic reasoning from article text
        """
        if not explanation or not isinstance(explanation, str):
            return False
        
        explanation_lower = explanation.lower().strip()
        
        # Generic/empty explanations that should be replaced
        generic_phrases = [
            "no explanation provided",
            "not specified", 
            "ev reasoning not specified in article",
            "not available",
            "no strategic reasoning found",
            "no explanation available",
            "",
        ]
        
        # Check if explanation exactly matches generic phrases (not just contains)
        if explanation_lower in generic_phrases or explanation_lower.strip() == "":
            return False
        
        # Too short to be meaningful (less than 20 characters)
        if len(explanation) < 20:
            return False
        
        # Indicators of meaningful strategic reasoning from articles
        meaningful_indicators = [
            # Damage calculations
            "survives", "ohko", "2hko", "確定", "乱数", "耐え",
            
            # Speed benchmarks  
            "outspeeds", "outspeed", "faster than", "slower than", "speed tier",
            "最速", "準速", "抜き", "base", "族",
            
            # Defensive benchmarks
            "bulk", "tanky", "defensive", "special defense", "physical defense",
            "物理耐久", "特殊耐久", "耐久",
            
            # Technical optimization
            "16n-1", "11n", "substitute", "weather", "残飯", "leftovers",
            
            # Specific Pokemon/move names
            "garchomp", "landorus", "earthquake", "flamethrower", "thunderbolt",
            "ガブリアス", "ランドロス", "じしん", "かえんほうしゃ", "10まんボルト",
            
            # Competitive terms
            "choice", "scarf", "band", "specs", "assault vest", "life orb",
            "こだわり", "スカーフ", "ハチマキ", "メガネ", "とつげきチョッキ", "いのちのたま",
        ]
        
        # Check for meaningful indicators
        meaningful_count = sum(1 for indicator in meaningful_indicators 
                             if indicator in explanation_lower)
        
        # Consider meaningful if it has strategic indicators or is substantial
        # Lowered thresholds to catch more genuine strategic reasoning
        return (meaningful_count >= 1 or  # Even one strategic indicator is meaningful
                len(explanation) >= 60)   # Or if it's quite long and detailed

    def _validate_and_clean_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the analysis result"""
        # Ensure required fields exist
        required_fields = [
            "title", "pokemon_team", "overall_strategy", "regulation", 
            "team_strengths", "team_weaknesses", "team_synergies", 
            "meta_analysis", "full_translation", "translation_notes", "content_summary"
        ]
        for field in required_fields:
            if field not in result:
                result[field] = "Not specified"
        
        # Validate Pokemon team structure
        if isinstance(result.get("pokemon_team"), list):
            cleaned_team = []
            for pokemon in result["pokemon_team"]:
                if isinstance(pokemon, dict):
                    # Ensure required Pokemon fields (preserving extracted EV data)
                    pokemon_defaults = {
                        "name": "Unknown Pokemon",
                        "ability": "Not specified",
                        "held_item": "Not specified",
                        "tera_type": "Not specified",
                        "nature": "Not specified",
                        "moves": [],
                        "ev_explanation": "Not specified",
                        "role": "Not specified"
                    }

                    # Map role_in_team -> role (prompt uses role_in_team, UI uses role)
                    if "role_in_team" in pokemon and "role" not in pokemon:
                        pokemon["role"] = pokemon.pop("role_in_team")

                    # Apply defaults only for missing basic fields
                    for field, default in pokemon_defaults.items():
                        if field not in pokemon:
                            pokemon[field] = default
                    
                    # Handle EV spread specially - preserve extracted data or create proper defaults
                    if "ev_spread" not in pokemon:
                        pokemon["ev_spread"] = {
                            "HP": 0, "Attack": 0, "Defense": 0,
                            "Special Attack": 0, "Special Defense": 0, "Speed": 0,
                            "total": 0
                        }
                    else:
                        # Validate and fix extracted EV spread
                        ev_spread = pokemon["ev_spread"]
                        if isinstance(ev_spread, dict):
                            # Ensure all required EV fields exist and are numeric
                            ev_fields = ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
                            for field in ev_fields:
                                if field not in ev_spread:
                                    ev_spread[field] = 0
                                elif not isinstance(ev_spread[field], int):
                                    try:
                                        ev_spread[field] = int(ev_spread[field]) if ev_spread[field] not in ["EXTRACTED_FROM_ARTICLE", ""] else 0
                                    except (ValueError, TypeError):
                                        ev_spread[field] = 0
                            
                            # Calculate and set total
                            ev_spread["total"] = sum(ev_spread[field] for field in ev_fields)
                            
                            # Create standard EVs string format if missing
                            if "evs" not in pokemon:
                                ev_values = [ev_spread[field] for field in ev_fields]
                                pokemon["evs"] = "/".join(map(str, ev_values))
                    
                    cleaned_team.append(pokemon)
            
            result["pokemon_team"] = cleaned_team
        
        return result