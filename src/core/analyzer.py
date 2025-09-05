"""
Core VGC analysis engine using Google Gemini AI.
"""

import json
import re
import logging
from typing import Dict, Optional, Any, List
import google.generativeai as genai

from utils.config import Config, POKEMON_NAME_TRANSLATIONS, MOVE_NAME_TRANSLATIONS
from utils.cache_manager import cache
from core.scraper import ArticleScraper
from core.pokemon_validator import PokemonValidator
from utils.image_analyzer import (
    extract_images_from_url,
    filter_vgc_images,
    analyze_image_with_vision,
    extract_ev_spreads_from_image_analysis
)

# Configure logging for analysis pipeline debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiVGCAnalyzer:
    """Pokemon VGC analyzer using Google Gemini AI"""

    def __init__(self):
        """Initialize the analyzer with Gemini configuration"""
        logger.info("Initializing GeminiVGCAnalyzer")
        
        try:
            self.api_key = Config.get_google_api_key()
            if not self.api_key:
                logger.error("No Google API key found")
                raise ValueError("Google API key is required for analysis")
                
            logger.info("API key found, configuring Gemini")
            genai.configure(api_key=self.api_key)

            # Configure the text model with Gemini 2.5 Flash (latest model)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini analyzer: {str(e)}")
            raise
        
        # Configure the vision model with 2.5 Flash for enhanced image processing
        self.vision_model = genai.GenerativeModel("gemini-2.5-flash")

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

        # Check cache first
        cached_result = cache.get(content, url)
        if cached_result:
            return cached_result

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
            
            # ULTRA-CRITICAL: Apply validation pipeline including stat abbreviation translation
            text_result = self._validate_and_enhance_result(text_result, content, url)

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
                        # Analyze image with vision model
                        vision_analysis = analyze_image_with_vision(
                            image_info['data'], 
                            image_info['format'], 
                            self.vision_model
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
        logger.info("Making standard API call to Gemini")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        try:
            response = self.model.generate_content(
                prompt, generation_config=self.generation_config
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
            # Enhanced error logging for different API failure types
            error_msg = str(e).lower()
            if 'api key' in error_msg or 'authentication' in error_msg:
                logger.error(f"API authentication error: {str(e)}")
                raise ValueError("API authentication failed. Please check your Google API key.")
            elif 'quota' in error_msg or 'rate' in error_msg:
                logger.error(f"API quota/rate limit error: {str(e)}")
                raise ValueError("API quota exceeded. Please try again later.")
            elif 'service_disabled' in error_msg or 'has not been used' in error_msg:
                logger.error(f"API service disabled: {str(e)}")
                raise ValueError("Gemini API service is disabled or not enabled for this project. Please enable the Generative Language API in Google Cloud Console and try again.")
            else:
                logger.error(f"General API error: {str(e)}")
                raise ValueError(f"API call failed: {str(e)}")
    
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
        """Get the comprehensive VGC analysis prompt with enhanced Pokemon identification"""
        return '''
You are a Pokemon VGC expert analyst with extensive knowledge of Pokemon identification and naming conventions.
Your task is to analyze Japanese Pokemon VGC articles and provide comprehensive analysis including team composition, strategy explanation, and accurate translations.

🚨 ULTRA-CRITICAL EV DETECTION PRIORITY - EXTRACTION ONLY, NO GENERATION 🚨

**PRIMARY OBJECTIVE: EV SPREAD EXTRACTION (HIGHEST PRIORITY)**
**CRITICAL RULE: ONLY extract EVs that are EXPLICITLY present in the article text. DO NOT generate, infer, or create EV spreads.**
**If no EV data is found in the text, you MUST return EV spread values of 0 for all stats.**

Your most important task is finding EV spreads that are ACTUALLY written in the article. Scan methodically for these exact patterns:

**🎯 COMPREHENSIVE JAPANESE EV FORMATS (2025 COMPLETE GUIDE):**

**FORMAT 1: Calculated Stat Format (ULTRA-COMMON in note.com)**
- Pattern: H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)
- Structure: [StatLetter][CalculatedValue]([EVValue])[NatureSymbol]
- ⚠️ EXTRACT ONLY THE PARENTHESES NUMBERS: (148), (124), (116), (4), (116)
- 🚨 IGNORE the first number (calculated stat), focus on parentheses
- Nature symbols: ↑ = boost, ↓ = reduce, × = neutral/no investment

**FORMAT 2: Japanese Direct EV Format (ULTIMATE PRIORITY - CHECK FIRST!)**
- Pattern: "努力値:236-0-36-196-4-36" or "努力値: 252-0-4-252-0-0"
- Structure: 努力値: [HP]-[Attack]-[Defense]-[SpA]-[SpD]-[Speed]
- 🚨 MOST COMMON IN JAPANESE VGC ARTICLES - SCAN EVERY LINE FOR THIS!
- 🔥 EXPANDED Keywords to Check (ULTRA-COMPREHENSIVE):
  * Primary: "努力値:", "努力値：", "努力値 :", "努力値 ："
  * Secondary: "個体値調整:", "EV配分:", "振り分け:", "調整:", "ステータス:"
  * Technical: "EV値:", "EV:", "努力:", "個体値:", "配分:"
  * Context: "実数値:" followed by "努力値:" (common pattern)
- 🎯 EXACT EXAMPLES FROM REAL ARTICLES:
  * "努力値:236-0-36-196-4-36" (Miraidon example)
  * "努力値: 252-0-4-252-0-0" (Standard format)
  * "個体値調整: 244-0-12-252-0-0" (Alternative format)

**FORMAT 3: Standard Slash Format**
- Patterns: "252/0/4/252/0/0", "252-0-4-252-0-0", "H252/A0/B4/C252/D0/S0"
- Order: HP/Attack/Defense/SpA/SpD/Speed
- Look for exactly 6 numbers separated by slashes or dashes

**FORMAT 4: Japanese Grid Format (MOST COMMON in note.com team cards)**
```
ＨＰ: 252        こうげき: 0       ぼうぎょ: 4
とくこう: 252    とくぼう: 0      すばやさ: 0
```

**FORMAT 5: Vertical List Format**
```
HP: 252 (or ＨＰ：252)
Attack: 0 (or こうげき：0)  
Defense: 4 (or ぼうぎょ：4)
Sp. Atk: 252 (or とくこう：252)
Sp. Def: 0 (or とくぼう：0)
Speed: 0 (or すばやさ：0)
```

**FORMAT 6: Abbreviated Format (ENHANCED FOR JAPANESE HYBRID)**
- "H252 A0 B4 C252 D0 S0"
- "252HP 4Def 252SpA"
- 🚨 **CRITICAL HYBRID FORMAT**: "努力値：H252 A4 B156 D68 S28" (Japanese prefix + abbreviated stats)
- 🔥 **ULTRA-PRIORITY PATTERNS**:
  * "努力値：B4 C252 S252" (Defense 4, Special Attack 252, Speed 252)
  * "努力値：H252 A4 B156 D68 S28" (HP 252, Attack 4, Defense 156, Special Defense 68, Speed 28)
  * "個体値調整：H244 B12 C252 S4" (alternative Japanese prefix)
- Any stat letters (H/A/B/C/D/S) with numbers, with or without Japanese prefixes

**FORMAT 7: Technical Calculation Format (ULTRA-ENHANCED - Common in competitive analysis)**
- Pattern: "実数値:205-x-125-198-136-160" followed by "努力値:236-0-36-196-4-36"
- 🎯 EXACT SEQUENCE RECOGNITION:
  * Line 1: "実数値:" with actual battle stats (includes 'x' for unused Attack)
  * Line 2: "努力値:" with EV distribution (EXTRACT THIS!)
- 🔍 ENHANCED Context Patterns:
  * Damage calculations: "H-B:白馬A220のブリランダブルダメ乱数1発(12.5%)"
  * Equivalent calcs: "＝陽気パオジアンA172のつららおとし乱数1発(12.5%)"
  * Speed benchmarks: "S:最速90族＋4", "S:準速100族", "S:4振り○○"
  * Optimization notes: "C:11n", "H:16n-1"
- 🚨 CRITICAL: When you see "実数値:" IMMEDIATELY scan next 2-3 lines for "努力値:"

**🔍 ULTRA-COMPREHENSIVE JAPANESE STAT VOCABULARY:**
- **HP**: ＨＰ, HP, H, ヒットポイント, 体力
- **Attack**: こうげき, 攻撃, A, アタック, 物理攻撃
- **Defense**: ぼうぎょ, 防御, B, ディフェンス, 物理防御  
- **Sp.Attack**: とくこう, 特攻, 特殊攻撃, C, とくしゅこうげき
- **Sp.Defense**: とくぼう, 特防, 特殊防御, D, とくしゅぼうぎょ
- **Speed**: すばやさ, 素早さ, S, スピード, 速さ

**🚨 ULTRA-ENHANCED EV DETECTION PROTOCOL - EXTRACTION ONLY (2025 COMPLETE):**
1. **SCAN METHODICALLY**: Check every paragraph, sentence, and line for EV patterns IN THE PROVIDED TEXT ONLY
2. **ABSOLUTE PRIORITY**: Check Format 2 (努力値:) FIRST AND FOREMOST
3. **MULTIPLE FORMATS**: Try ALL 7 formats for each Pokemon systematically
4. **CONTEXT AWARENESS**: Scan near these indicator words:
   * Speed tiers: "最速90族", "準速100族", "4振り", "無振り", "準速", "最速"
   * Calculations: "乱数1発", "確定1発", "乱数2発", "耐え", "抜き"
   * Optimization: "11n", "16n-1", "調整", "ライン", "意識"
5. **VALIDATE TOTALS**: EVs must total ≤508 (if >508, these are battle stats, not EVs)
6. **CRITICAL - NO GENERATION**: If you cannot find explicit EV spreads in the text, return all zeros (0/0/0/0/0/0)
7. **NO ASSUMPTIONS**: Do not assume standard spreads like 252/252/4 unless explicitly written
8. **SEQUENTIAL SEARCH**: When you find "実数値:", immediately search next 3 lines for EV data
9. **AUTHOR'S STATEMENT OVERRIDE**: If author says EVs are "適当" (arbitrary) or "詳細なし" (no details), return 0s unless actual numbers are provided

**🧠 STRATEGIC REASONING EXTRACTION (ULTRA-CRITICAL FOR EV EXPLANATIONS):**

**PRIMARY OBJECTIVE**: For EVERY Pokemon with EV spreads, extract the EXACT strategic reasoning from the article text.

**SCAN FOR THESE STRATEGIC PATTERNS:**

1. **Damage Calculations (最重要 - Most Important)**:
   - "確定1発" = "guaranteed OHKO" 
   - "乱数1発" = "random OHKO" 
   - "確定2発" = "guaranteed 2HKO"
   - "乱数2発" = "random 2HKO"
   - "耐え" = "survives" (e.g., "特化ランドロスの地震を耐え")
   - Specific damage ranges: "75%で1発" = "75% chance to OHKO"

2. **Speed Benchmarks**:
   - "最速○族抜き" = "outspeeds max speed base [X]"
   - "準速○族抜き" = "outspeeds neutral nature base [X]"
   - "4振り○○抜き" = "outspeeds 4 EV [Pokemon name]"
   - "最速○○-1" = "1 point slower than max speed [Pokemon]"
   - "トリックルーム下で最遅" = "slowest for Trick Room"

3. **Defensive Benchmarks**:
   - "特化○○のx確定耐え" = "survives [specific attack] from max [stat] [Pokemon]"
   - "眼鏡○○のx乱数耐え" = "survives [move] from Choice Specs [Pokemon] [percentage]%"
   - "ダメージ○○%" = "[X]% damage taken"

4. **Technical Optimizations**:
   - "11n" = "multiple of 11 (for Substitute/recovery)"
   - "16n-1" = "1 less than multiple of 16 (for weather damage)"
   - "砂嵐ダメ調整" = "sandstorm damage adjustment"
   - "きのみ発動調整" = "berry activation threshold"

5. **Role-Based Reasoning**:
   - "サポート型なので耐久重視" = "support role, focuses on bulk"
   - "先制技意識" = "priority move consideration" 
   - "カウンター意識" = "Counter move consideration"
   - "起点作り" = "setup support role"

**EXTRACTION PROTOCOL**:
1. **Find EV spread first**, then scan surrounding 3-5 lines for reasoning
2. **Look for specific numerical targets** (base stats, damage amounts, percentages)
3. **Extract original Japanese phrases** and translate them accurately
4. **Include specific Pokemon/move names** mentioned in calculations
5. **If no strategic reasoning found**, use "EV reasoning not specified in article"
6. **Never make up strategic reasoning** - only use what's actually written

**🚨 ULTRA-CRITICAL STAT ABBREVIATION TRANSLATION PROTOCOL:**

**PRIMARY RULE**: ALWAYS translate Japanese stat abbreviations to full English terms in ev_explanation field.

**STAT ABBREVIATION MAPPING:**
- H = HP (Hit Points)
- A = Attack  
- B = Defense
- C = Special Attack
- D = Special Defense
- S = Speed
- CS = Special Attack and Speed
- AS = Attack and Speed
- HB = HP and Defense

**CRITICAL TRANSLATION EXAMPLES:**

**Japanese Strategic Reasoning → English Translation:**

1. **Basic Stat References:**
   - "CS振り" → "Special Attack and Speed investment"  
   - "H252 B4" → "252 HP, 4 Defense"
   - "S調整" → "Speed adjustment"
   - "B極振り" → "max Defense"

2. **Technical Explanations:**
   - "CS max. B investment was tested..." → "max Special Attack and Speed. Defense investment was tested..."
   - "S: 最速90族+2" → "Speed: outspeeds max speed base 90 +2"  
   - "H: 11n" → "HP: multiple of 11"
   - "B4 D252残り" → "4 Defense, 252 Special Defense remaining"

3. **Complex Strategic Reasoning:**
   - "S最速ウーラオス+2を意識してH調整、Bは削った" → "Speed: considering fastest Urshifu +2, HP adjusted, Defense reduced"
   - "CS極振りでHBは耐久重視" → "max Special Attack and Speed with HP and Defense focusing on bulk"

**TRANSLATION PROTOCOL:**
1. **Extract strategic reasoning first** in Japanese abbreviated form
2. **Immediately translate all stat abbreviations** to full English terms  
3. **Preserve technical accuracy** while making it readable for English speakers
4. **Use "HP" not "H", "Defense" not "B", "Special Attack" not "C"**, etc.

**FORBIDDEN**: Never leave stat abbreviations untranslated in the final ev_explanation field.

**TRANSLATION EXAMPLES FOR DAMAGE CALCULATIONS:**
- "陽気ガブリアスの地震確定耐え" → "Survives Earthquake from Jolly Garchomp"
- "最速100族抜き" → "Outspeeds max speed base 100 Pokemon"  
- "特化珠フラッターのシャドボ乱数耐え" → "Survives Shadow Ball from Choice Specs Flutter Mane with some probability"

**⚡ EV VALIDATION REQUIREMENTS (JAPANESE VGC OPTIMIZED):**
- Valid EV values: 0, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252
- Total EVs must be ≤508 (Accept totals 468-508 as valid competitive spreads)
- Individual stats must be ≤252
- Common Japanese competitive patterns:
  * 236/0/36/196/4/36 = 468 total ✓ (Miraidon technical spread)
  * 252/252/4/0/0/0 = 508 total ✓ (Standard offensive)
  * 244/0/12/252/0/0 = 508 total ✓ (Bulky special attacker)
- Multiples of 4 are preferred but accept technical optimizations (11n, 16n-1)

🏆 **REGULATION DETECTION PROTOCOL (ULTRA-CRITICAL)** 🏆

**ALWAYS SCAN FOR THESE REGULATION PATTERNS:**
1. **Series/シリーズ Patterns:**
   - "シリーズ13", "Series 13", "S13", "シリーズ14", "Series 14"
   - "シリーズ12", "Series 12", "S12" (previous regulations)
   
2. **Regulation Letter Patterns:**
   - "レギュレーション A", "Regulation A", "レギュA", "Reg A"
   - "レギュレーション B", "Regulation B", "レギュB", "Reg B" 
   - "レギュレーション C", "Regulation C", "レギュC", "Reg C"
   - "レギュレーション D", "Regulation D", "レギュD", "Reg D"
   - "レギュレーション E", "Regulation E", "レギュE", "Reg E"

3. **Season/時期 Indicators:**
   - "2024年", "2025年" followed by month indicators
   - "WCS2024", "WCS2025", "世界大会"
   - "リージョナル", "Regional", "地域大会"
   - "ナショナル", "National", "国内大会"

4. **Rule Format Patterns:**
   - "ダブルバトル", "Double Battle", "VGC"
   - "伝説2体", "2 Legendaries", "restricted"
   - "伝説1体", "1 Legendary" 
   - "伝説なし", "No Legendaries"

**REGULATION EXTRACTION PRIORITY:**
1. Look for explicit regulation mentions in title/headers
2. Check for tournament context clues
3. Analyze team composition for regulation hints
4. NEVER assume - extract from content only

⚡ **TECHNICAL VGC DATA PARSING (DAMAGE CALCS & SPEED TIERS)** ⚡

**DAMAGE CALCULATION PATTERNS:**
1. **Standard Calc Format:**
   - "H-B:白馬A220のブリランダブルダメ乱数1発(12.5%)"
   - Pattern: [DefensiveStats]:[AttackerName][Attack][MoveName][Result]([Percentage])
   - Extract: Attacker, move, damage range, percentage

2. **Comparative Calc Format:**
   - "＝陽気パオジアンA172のつららおとし乱数1発(12.5%)"
   - Shows equivalent damage calculations for benchmarking

3. **Speed Tier Patterns:**
   - "S:最速90族＋4" = Speed to outrun max speed base 90 + 4 EVs
   - "S:準速100族" = Speed to match neutral nature base 100
   - "S:最速○族" = Max speed to outrun base speed tier
   - "S:4振り○○" = Speed to outrun 4 EV investment in specific Pokemon

4. **Technical Abbreviations:**
   - "11n" = Multiple of 11 (often HP for Substitute/recovery optimization)
   - "16n-1" = 1 less than multiple of 16 (weather damage optimization)
   - "乱数1発" = Random 1-shot (OHKO range)
   - "確定1発" = Guaranteed 1-shot (100% OHKO)
   - "乱数2発" = Random 2-shot (2HKO range)

5. **Nature Indicators in Calcs:**
   - "陽気" = Jolly (+Speed, -SpA)
   - "いじっぱり" = Adamant (+Attack, -SpA)
   - "控え目" = Modest (+SpA, -Attack)
   - "臆病" = Timid (+Speed, -Attack)

**TECHNICAL DATA EXTRACTION PROTOCOL:**
1. Always extract actual stats (実数値) when provided
2. Parse damage calculations for defensive/offensive benchmarks
3. Identify speed tier targets and reasoning
4. Extract nature implications from calculations
5. Note any optimization patterns (11n, 16n-1, etc.)

CRITICAL REQUIREMENTS:
1. ALWAYS provide a valid JSON response
2. **NEVER GENERATE EV SPREADS** - Only extract what is explicitly in the text
3. If no EV data is found, use 0 for all EV values and explain in ev_explanation
4. If author mentions "適当" (arbitrary) or similar, use 0s unless actual numbers are provided
5. Provide strategic explanations for EV choices ONLY if mentioned in the article
6. Translate all Japanese text to English with PERFECT Pokemon identification
7. Ensure team composition makes sense for VGC format
8. Use EXACT Pokemon names with proper forms and spellings
9. EXTRACT regulation information from the article content - DO NOT ASSUME
10. **VALIDATION**: If all Pokemon end up with identical EV totals (like 508), this indicates generation rather than extraction - recheck for actual text-based EVs

🚨 ULTRA-COMPREHENSIVE POKEMON IDENTIFICATION (2025 COMPLETE DATABASE) 🚨

**PRIMARY POKEMON IDENTIFICATION PROTOCOL:**
1. **READ JAPANESE NAMES**: Look for Japanese Pokemon names in katakana
2. **CROSS-REFERENCE**: Match with comprehensive database below  
3. **VALIDATE**: Ensure Pokemon makes sense in VGC context
4. **NEVER GUESS**: If uncertain, state multiple possibilities

**🎯 ULTRA-COMPREHENSIVE JAPANESE POKEMON DATABASE:**

**GENERATION 9 PRIORITY POKEMON (Often Found in VGC):**
These are CRITICAL to identify correctly as they appear frequently in competitive play:

**🚨 ULTRA-CRITICAL POKEMON (High Misidentification Risk):**
- テツノブジン = Iron Valiant (Fairy/Fighting paradox) - NEVER "Iron Shaman"
- ザマゼンタ = Zamazenta (Fighting/Steel legendary with shield) - NEVER confuse with Zacian  
- ザシアン = Zacian (Fairy/Steel legendary with sword)
- ハバタクカミ = Flutter Mane (Ghost/Fairy paradox) - NEVER "Flatter Mane"
- サーフゴー = Gholdengo (Ghost/Steel - surfboard-like golden Pokemon)

**🔥 CRITICAL MISSING POKEMON - FREQUENTLY MISIDENTIFIED:**
- オーロンゲ = Grimmsnarl (Dark/Fairy - NEVER "Ooronge")

**⚠️ CALYREX vs KYUREM FORMS - ULTRA-CRITICAL DISTINCTION:**
🚨 **NEVER CONFUSE THESE RESTRICTED POKEMON** 🚨

**CALYREX FORMS (Psychic type base):**
- バドレックス-はくばじょう = Calyrex-Ice (Psychic/Ice - riding Glastrier)
  * Signature Move: ブリザードランス = Glacial Lance
  * Alternative names: はくばじょうバドレックス, 白馬 (White Horse)
- バドレックス-こくばじょう = Calyrex-Shadow (Psychic/Ghost - riding Spectrier)  
  * Signature Move: アストラルビット = Astral Barrage
  * Alternative names: こくばじょうバドレックス, 黒馬 (Black Horse)

**KYUREM FORMS (Dragon/Ice type):**
- キュレム-ホワイト = Kyurem-White (Dragon/Ice - WHITE KYUREM, NOT CALYREX!)
  * Signature Move: アイスバーン = Ice Burn
  * Alternative names: ホワイトキュレム
- キュレム-ブラック = Kyurem-Black (Dragon/Ice - BLACK KYUREM, NOT CALYREX!)
  * Signature Move: フリーズボルト = Freeze Shock  
  * Alternative names: ブラックキュレム

**🎯 SIGNATURE MOVE IDENTIFICATION PROTOCOL:**
When you see these moves, you can be 100% certain of the Pokemon:
- Glacial Lance (ブリザードランス) = ALWAYS Calyrex-Ice
- Astral Barrage (アストラルビット) = ALWAYS Calyrex-Shadow
- Ice Burn (アイスバーン) = ALWAYS Kyurem-White
- Freeze Shock (フリーズボルト) = ALWAYS Kyurem-Black

**GENERATION 9 META STAPLES:**
- コライドン = Koraidon (Fighting/Dragon legendary - orange)
- ミライドン = Miraidon (Electric/Dragon legendary - purple)  
- テツノカイナ = Iron Hands (Fighting/Electric paradox)
- イーユイ = Wo-Chien (Dark/Grass Ruin legendary)
- パオジアン = Chien-Pao (Dark/Ice Ruin legendary)
- チオンジェン = Chi-Yu (Dark/Fire Ruin legendary)
- ディンルー = Ting-Lu (Dark/Ground Ruin legendary)

**OGERPON FORMS - CRITICAL IDENTIFICATION:**
- オーガポン (いどのめん) = Ogerpon-Wellspring (Water/Grass with Wellspring Mask)
- オーガポン (かまどのめん) = Ogerpon-Hearthflame (Fire/Grass with Hearthflame Mask)
- オーガポン (いしずえのめん) = Ogerpon-Cornerstone (Rock/Grass with Cornerstone Mask)
- オーガポン = Ogerpon-Teal (Grass type, base form)

**PARADOX POKEMON (ULTRA-COMMON):**
- テツノドクガ = Iron Moth (Fire/Poison future paradox)
- テツノツツミ = Iron Bundle (Ice/Water future paradox)  
- テツノワダチ = Iron Treads (Ground/Steel future paradox)
- アラブルタケ = Brute Bonnet (Grass/Dark ancient paradox)
- スナノケガワ = Sandy Shocks (Electric/Ground ancient paradox)
- トドロクツキ = Roaring Moon (Dragon/Dark ancient paradox)

**ULTRA-POPULAR VGC POKEMON:**
- ガブリアス = Garchomp (Dragon/Ground - land shark)
- ランドロス = Landorus-Therian (Ground/Flying - orange genie)  
- ガオガエン = Incineroar (Fire/Dark - tiger wrestler)
- エルフーン = Whimsicott (Grass/Fairy - white cotton Pokemon)
- モロバレル = Amoonguss (Grass/Poison - mushroom Pokemon)
- リザードン = Charizard (Fire/Flying - orange dragon)
- カイリュー = Dragonite (Dragon/Flying - orange friendly dragon)
- ニンフィア = Sylveon (Fairy - pink ribbon Eevee evolution)
- ウインディ = Arcanine (Fire - orange dog/tiger Pokemon)
- ハリテヤマ = Hariyama (Fighting - sumo wrestler Pokemon)
- クレッフィ = Klefki (Steel/Fairy - key ring Pokemon)
- トリトドン = Gastrodon (Water/Ground - sea slug Pokemon)

**REGIONAL VARIANTS & SPECIAL FORMS:**
- ガラルサンダー = Zapdos-Galar (Fighting/Flying - orange bird)
- ガラルファイヤー = Moltres-Galar (Dark/Flying - purple bird)
- ガラルフリーザー = Articuno-Galar (Psychic/Flying - purple bird)
- ヒスイゾロアーク = Zoroark-Hisui (Normal/Ghost - white fox)
- アローラガラガラ = Marowak-Alola (Fire/Ghost - bone wielder)

**RECENT ADDITIONS (DLC Pokemon):**
- イルカマン = Palafin (Water - dolphin with Zero to Hero ability)
- ウネルミナモ = Walking Wake (Water/Dragon - blue dinosaur paradox)
- ライド = Raging Bolt (Electric/Dragon - long-necked paradox)

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
- テツノブジン = Iron Valiant (Fairy/Fighting paradox)
- ハバタクカミ = Flutter Mane (Ghost/Fairy paradox)
- コライドン = Koraidon (Fighting/Dragon legendary)
- ミライドン = Miraidon (Electric/Dragon legendary)
- イルカマン = Palafin (Water type with Zero to Hero)

**COMMON IDENTIFICATION ERRORS TO AVOID:**

DO NOT CONFUSE THESE POKEMON:

🚨 ULTRA CRITICAL - LEGENDARY DOG DISTINCTION: 🚨
- ザマゼンタ = Zamazenta (Shield legendary, often abbreviated as "ザマ")
- ザシアン = Zacian (Sword legendary)
NEVER confuse "ザマ" mentions with Zacian - "ザマ" ALWAYS refers to Zamazenta!

- Chi-Yu ≠ Chien-Pao (チオンジェン = Chi-Yu, パオジアン = Chien-Pao)
- Ting-Lu ≠ Wo-Chien (ディンルー = Ting-Lu, イーユイ = Wo-Chien)
- Tornadus-Incarnate ≠ Tornadus-Therian (different forms, different stats)

CRITICAL: テツノブジン = Iron Valiant (NEVER "Iron Shaman" or any other name)

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

**CRITICAL EV AND EXPLANATION EXTRACTION REQUIREMENTS:**
1. **EV Values**: Replace "EXTRACTED_FROM_ARTICLE" with actual numerical values found in the article. If no EVs found for a Pokemon, use 0.
2. **EV Format**: Fill "evs" field with standard format like "252/0/4/252/0/0" based on extracted values.
3. **Strategic Reasoning**: Replace the ev_explanation placeholder with ACTUAL strategic text from the article:
   - Look for damage calculations (e.g., "survives X's move", "OHKOs Y Pokemon")  
   - Look for speed benchmarks (e.g., "outspeeds base 100", "underspeed for Trick Room")
   - Look for defensive benchmarks (e.g., "survives Choice Band attack")
   - Look for technical explanations (e.g., "16n-1 for weather", "11n for Substitute")
   - Translate Japanese strategic text to English
   - If no strategic reasoning found, use "EV reasoning not specified in article"

**🎯 MOVE NAME TRANSLATION DATABASE:**

**CRITICAL MOVE TRANSLATIONS (2025 Update):**
- マジカルシャイン = Dazzling Gleam (Fairy-type spread move)
- アクセルブレイク = Flame Charge (Fire-type speed boosting move, also known as Accel Break)
- ニトロチャージ = Flame Charge (Alternative Japanese name)
- フレイムチャージ = Flame Charge (Alternative Japanese name) 
- カタストロフィ = Ruination (Dark-type signature move of Treasures of Ruin)
- ワイドブレイカー = Breaking Swipe (Dragon-type attack lowering move)
- アストラルビット = Astral Barrage (Psychic-type signature move of Calyrex-Shadow)
- ブリザードランス = Glacial Lance (Ice-type signature move of Calyrex-Ice)
- テラバースト = Tera Blast (Normal-type move that changes with Tera type)
- 10まんボルト = Thunderbolt
- かえんほうしゃ = Flamethrower
- なみのり = Surf
- じしん = Earthquake
- まもる = Protect
- ねこだまし = Fake Out
- とんぼがえり = U-turn
- ボルトチェンジ = Volt Switch
- いわなだれ = Rock Slide
- エアスラッシュ = Air Slash
- アイアンヘッド = Iron Head
- ヘビーボンバー = Heavy Slam
- インファイト = Close Combat
- フレアドライブ = Flare Blitz
- ムーンフォース = Moonblast
- じゃれつく = Play Rough
- ワイドガード = Wide Guard
- このゆびとまれ = Follow Me
- いかりのこな = Rage Powder
- キノコのほうし = Spore
- おいかぜ = Tailwind
- トリックルーム = Trick Room

**MOVE TRANSLATION PROTOCOL:**
1. Always use exact English move names from official Pokemon translations
2. Never leave Japanese move names untranslated in the final output
3. If uncertain about a move name, use context clues from Pokemon and strategy
4. For signature moves, cross-reference with Pokemon to ensure accuracy

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
        "HP": "EXTRACTED_FROM_ARTICLE",
        "Attack": "EXTRACTED_FROM_ARTICLE", 
        "Defense": "EXTRACTED_FROM_ARTICLE",
        "Special Attack": "EXTRACTED_FROM_ARTICLE",
        "Special Defense": "EXTRACTED_FROM_ARTICLE",
        "Speed": "EXTRACTED_FROM_ARTICLE",
        "total": "SUM_OF_ABOVE_VALUES"
      },
      "evs": "HP/Attack/Defense/SpA/SpD/Speed format (e.g., 252/0/4/252/0/0)",
      "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
      "ev_explanation": "EXACT strategic reasoning for EV distribution as mentioned in the article, translated to English with ALL stat abbreviations converted to full English terms (H→HP, B→Defense, C→Special Attack, etc.). Include damage calcs, speed benchmarks, defensive benchmarks, or other tactical reasoning found in the text.",
      "role_in_team": "Pokemon's strategic role"
    }
  ],
  "overall_strategy": "Comprehensive team strategy and approach - analyze the core gameplan, win conditions, and tactical approach described in the article",
  "team_strengths": "Detailed analysis of team strengths - what makes this team effective, key advantages, favorable matchups, powerful combinations, and strategic assets mentioned in the article",
  "team_weaknesses": "Detailed analysis of team weaknesses - vulnerabilities, problematic matchups, gaps in coverage, potential counters, and strategic limitations mentioned in the article",
  "team_synergies": "How team members work together - core interactions, support relationships, combo strategies, and synergistic elements described in the article", 
  "meta_analysis": "Analysis of how this team fits in the current meta, what it's designed to counter, and its positioning in the competitive landscape as described in the article",
  "tournament_context": "Tournament or competitive context if mentioned - results, placement, tournament format, notable wins/losses",
  "full_translation": "COMPLETE English translation of the entire article content - translate ALL Japanese text to natural, fluent English while preserving technical VGC terminology. This should be a comprehensive translation of the entire article, not just a summary.",
  "translation_notes": "Any translation notes, uncertainties, or technical clarifications",
  "content_summary": "Brief summary of the article's main points and structure"
}

Please analyze the following content and provide your response in the exact JSON format specified above:
'''

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Enhanced JSON response parsing with comprehensive error recovery"""
        logger.info("Starting JSON parsing of API response")
        logger.debug(f"Response text length: {len(response_text)} chars")
        
        # Try multiple parsing strategies
        strategies = [
            self._parse_direct_json,
            self._parse_cleaned_json,
            self._parse_extracted_json,
            self._parse_partial_json,
            self._create_fallback_result
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                logger.debug(f"Trying parsing strategy {i+1}: {strategy.__name__}")
                result = strategy(response_text)
                if result and isinstance(result, dict):
                    logger.info(f"JSON parsing successful with strategy: {strategy.__name__}")
                    pokemon_team_count = len(result.get('pokemon_team', []))
                    logger.info(f"Parsed result contains {pokemon_team_count} Pokemon")
                    return result
                else:
                    logger.debug(f"Strategy {strategy.__name__} returned invalid result")
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        # If all strategies fail, create minimal fallback
        logger.warning("All JSON parsing strategies failed, returning minimal fallback")
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
        """Attempt to parse partial or malformed JSON with advanced recovery"""
        logger.debug("Attempting partial JSON recovery")
        
        # Try to find and extract key-value pairs using regex
        extracted_data = {}
        
        # Extract title
        title_match = re.search(r'"title"\s*:\s*"([^"]*)"', text)
        if title_match:
            extracted_data["title"] = title_match.group(1)
            
        # Extract regulation 
        regulation_match = re.search(r'"regulation"\s*:\s*"([^"]*)"', text)
        if regulation_match:
            extracted_data["regulation"] = regulation_match.group(1)
            
        # Extract overall strategy
        strategy_match = re.search(r'"overall_strategy"\s*:\s*"([^"]*)"', text)
        if strategy_match:
            extracted_data["overall_strategy"] = strategy_match.group(1)
            
        # Try to extract pokemon team array with balanced bracket matching
        team_start_match = re.search(r'"pokemon_team"\s*:\s*\[', text, re.DOTALL)
        if team_start_match:
            try:
                start_pos = team_start_match.start()
                bracket_start = text.find('[', team_start_match.end() - 1)
                
                # Find matching closing bracket with proper nesting
                bracket_count = 0
                bracket_end = -1
                for i in range(bracket_start, len(text)):
                    if text[i] == '[':
                        bracket_count += 1
                    elif text[i] == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            bracket_end = i
                            break
                
                if bracket_end != -1:
                    team_json = text[bracket_start:bracket_end + 1]
                    logger.debug(f"Extracted pokemon_team JSON fragment: {team_json[:200]}...")
                    
                    # Enhanced cleanup for common issues
                    team_json = re.sub(r',\s*}', '}', team_json)  # Remove trailing commas from objects
                    team_json = re.sub(r',\s*]', ']', team_json)  # Remove trailing commas from arrays
                    team_json = re.sub(r'}\s*{', '},{', team_json)  # Fix missing commas between objects
                    
                    pokemon_team = json.loads(team_json)
                    
                    # Validate and enhance Pokemon team structure
                    validated_team = self._validate_pokemon_team_structure(pokemon_team)
                    extracted_data["pokemon_team"] = validated_team
                    
                    # Run comprehensive validation
                    validation_report = self._validate_extraction_completeness(validated_team)
                    cross_validation_warnings = self._cross_validate_team_data(validated_team)
                    
                    complete_pokemon = len([p for p in validated_team if self._is_complete_pokemon(p)])
                    logger.info(f"Successfully recovered {len(validated_team)} Pokemon from partial JSON ({complete_pokemon} complete)")
                    logger.info(f"Extraction quality: {validation_report['overall_quality']} (score: {validation_report['completeness_score']:.2f})")
                    
                    if validation_report["warnings"] or cross_validation_warnings:
                        all_warnings = validation_report["warnings"] + cross_validation_warnings
                        logger.warning(f"Validation warnings: {all_warnings[:3]}")  # Log first 3 warnings
                else:
                    logger.debug("Could not find matching closing bracket for pokemon_team")
                    extracted_data["pokemon_team"] = []
            except (json.JSONDecodeError, ValueError) as e:
                logger.debug(f"Failed to parse pokemon_team from partial JSON: {e}")
                extracted_data["pokemon_team"] = []
        else:
            logger.debug("No pokemon_team field found in partial JSON")
            extracted_data["pokemon_team"] = []
        
        # Try to extract other analysis fields with enhanced validation
        analysis_fields = {
            "team_strengths": r'"team_strengths"\s*:\s*"([^"]{30,})"',  # Minimum 30 chars for meaningful content
            "team_weaknesses": r'"team_weaknesses"\s*:\s*"([^"]{30,})"', 
            "team_synergies": r'"team_synergies"\s*:\s*"([^"]{30,})"',
            "meta_analysis": r'"meta_analysis"\s*:\s*"([^"]{30,})"',
            "full_translation": r'"full_translation"\s*:\s*"([^"]{50,})"',  # Higher threshold for translations
        }
        
        for field_name, pattern in analysis_fields.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Additional validation to avoid extracting generic/template content
                if (content and 
                    not content.lower().startswith(('analysis', 'recovered', 'not available', 'error')) and
                    len(content.split()) >= 5):  # At least 5 words for meaningful content
                    extracted_data[field_name] = content
                    logger.debug(f"Recovered {field_name} from partial JSON ({len(content)} chars)")
            
        # If we got some meaningful data, return it
        if extracted_data and (extracted_data.get("title") or extracted_data.get("pokemon_team")):
            # Assess the quality of recovered data to determine if this is truly partial
            pokemon_team = extracted_data.get("pokemon_team", [])
            has_title = bool(extracted_data.get("title"))
            has_strategy = bool(extracted_data.get("overall_strategy"))
            has_regulation = bool(extracted_data.get("regulation"))
            
            # Consider recovery "successful" if we have Pokemon team + substantial analysis content
            has_analysis_content = any(extracted_data.get(field) for field in ["team_strengths", "team_weaknesses", "team_synergies", "meta_analysis", "full_translation"])
            is_substantial_recovery = pokemon_team and (has_title or has_strategy or has_analysis_content)
            
            # Fill in missing required fields, using extracted content where available
            result = {
                "title": extracted_data.get("title", "VGC Team Analysis"),
                "pokemon_team": pokemon_team,
                "overall_strategy": extracted_data.get("overall_strategy", "Team strategy analysis recovered"),
                "regulation": extracted_data.get("regulation", "Not specified"),
                "team_strengths": extracted_data.get("team_strengths", "Team strengths analysis not available"),
                "team_weaknesses": extracted_data.get("team_weaknesses", "Team weaknesses analysis not available"), 
                "team_synergies": extracted_data.get("team_synergies", "Team synergies analysis not available"),
                "meta_analysis": extracted_data.get("meta_analysis", "Meta analysis not available"),
                "tournament_context": "Not specified",
                "full_translation": extracted_data.get("full_translation", "Full translation not available"),
                "translation_notes": f"JSON parsing recovered successfully with {len(pokemon_team)} Pokemon",
                "content_summary": "Successfully recovered from minor JSON formatting issues",
                "parsing_error": not is_substantial_recovery,  # Only flag as error if recovery is truly minimal
                "recovery_successful": True
            }
            
            if is_substantial_recovery:
                logger.info(f"Substantial JSON recovery successful - {len(pokemon_team)} Pokemon recovered")
            else:
                logger.info("Minimal JSON recovery - some data may be incomplete")
            return result
        
        # If no meaningful data recovered, raise error to try next strategy
        logger.debug("No meaningful data recovered in partial JSON parsing")
        raise ValueError("Partial JSON recovery failed")
    
    def _clean_json_text(self, text: str) -> str:
        """Enhanced JSON cleaning to catch more formatting issues before partial recovery"""
        # Remove markdown formatting
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```', '', text)
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^[^{]*(\{)', r'\1', text)
        text = re.sub(r'(\})[^}]*$', r'\1', text)
        
        # Fix common JSON formatting issues that Gemini creates
        # Remove trailing commas in objects and arrays (more comprehensive)
        text = re.sub(r',(\s*[}\]])', r'\1', text)  # Remove comma before closing brace or bracket
        
        # Fix missing quotes around keys (only when clearly needed)
        # This is safer - only fix obvious cases where keys are missing quotes
        text = re.sub(r'([{,]\s*)([a-zA-Z_]\w*)(\s*:\s*)', r'\1"\2"\3', text)
        
        # Fix single quotes to double quotes
        text = re.sub(r"'([^']*)'(\s*:\s*)", r'"\1"\2', text)
        text = re.sub(r"(\s*:\s*)'([^']*)'", r'\1"\2"', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
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
                        "role_in_team": "Not specified"
                    }
                    
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