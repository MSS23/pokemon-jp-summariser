"""
Core VGC analysis engine using Google Gemini AI.
"""

import json
import re
from typing import Dict, Optional, Any, List
import google.generativeai as genai

from ..utils.config import Config, POKEMON_NAME_TRANSLATIONS
from ..utils.cache_manager import cache
from .scraper import ArticleScraper
from .pokemon_validator import PokemonValidator
from ..utils.image_analyzer import (
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
                    if image_info.get('image_data') and image_info.get('format'):
                        # Analyze image with vision model
                        vision_analysis = analyze_image_with_vision(
                            image_info['image_data'], 
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
                
                # Determine if current EVs are inadequate
                needs_image_evs = any([
                    current_evs == "Not specified",
                    current_evs == "",
                    current_total <= 20,  # Very low total indicates failed detection
                    isinstance(current_evs, str) and "not found" in current_evs.lower(),
                    isinstance(current_evs, str) and len(current_evs) < 5,  # Too short to be real EV spread
                ])
                
                # Assign best available image EV spread
                if needs_image_evs and sorted_image_evs:
                    best_image_spread = sorted_image_evs.pop(0)  # Take highest confidence spread
                    
                    if best_image_spread.get("is_valid", False):
                        # Convert image EV spread to standard format
                        pokemon["evs"] = best_image_spread["format"]
                        pokemon["ev_spread"] = {
                            "hp": best_image_spread.get("hp", 0),
                            "attack": best_image_spread.get("attack", 0), 
                            "defense": best_image_spread.get("defense", 0),
                            "special_attack": best_image_spread.get("special_attack", 0),
                            "special_defense": best_image_spread.get("special_defense", 0),
                            "speed": best_image_spread.get("speed", 0),
                            "total": best_image_spread.get("total", 0),
                            "source": f"image_analysis_{best_image_spread.get('confidence', 'medium')}"
                        }
                        
                        # Update EV explanation
                        confidence = best_image_spread.get("confidence", "medium")
                        pokemon["ev_explanation"] = f"EV spread detected from team image ({confidence} confidence): {best_image_spread['format']}"
                        
                        ev_assignment_log.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): Assigned {confidence} confidence EVs from image")
                
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

🚨 ULTRA-CRITICAL EV DETECTION PRIORITY 🚨

**PRIMARY OBJECTIVE: EV SPREAD EXTRACTION (HIGHEST PRIORITY)**
Your most important task is finding EV spreads. EVERY Japanese VGC article contains EV data - you MUST find it using these exact patterns:

**🎯 COMPREHENSIVE JAPANESE EV FORMATS (2025 COMPLETE GUIDE):**

**FORMAT 1: Calculated Stat Format (ULTRA-COMMON in note.com)**
- Pattern: H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)
- Structure: [StatLetter][CalculatedValue]([EVValue])[NatureSymbol]
- ⚠️ EXTRACT ONLY THE PARENTHESES NUMBERS: (148), (124), (116), (4), (116)
- 🚨 IGNORE the first number (calculated stat), focus on parentheses
- Nature symbols: ↑ = boost, ↓ = reduce, × = neutral/no investment

**FORMAT 2: Standard Slash Format**
- Patterns: "252/0/4/252/0/0", "252-0-4-252-0-0", "H252/A0/B4/C252/D0/S0"
- Order: HP/Attack/Defense/SpA/SpD/Speed
- Look for exactly 6 numbers separated by slashes or dashes

**FORMAT 3: Japanese Grid Format (MOST COMMON in note.com team cards)**
```
ＨＰ: 252        こうげき: 0       ぼうぎょ: 4
とくこう: 252    とくぼう: 0      すばやさ: 0
```

**FORMAT 4: Vertical List Format**
```
HP: 252 (or ＨＰ：252)
Attack: 0 (or こうげき：0)  
Defense: 4 (or ぼうぎょ：4)
Sp. Atk: 252 (or とくこう：252)
Sp. Def: 0 (or とくぼう：0)
Speed: 0 (or すばやさ：0)
```

**FORMAT 5: Abbreviated Format**
- "H252 A0 B4 C252 D0 S0"
- "252HP 4Def 252SpA"
- Any stat letters (H/A/B/C/D/S) with numbers

**🔍 ULTRA-COMPREHENSIVE JAPANESE STAT VOCABULARY:**
- **HP**: ＨＰ, HP, H, ヒットポイント, 体力
- **Attack**: こうげき, 攻撃, A, アタック, 物理攻撃
- **Defense**: ぼうぎょ, 防御, B, ディフェンス, 物理防御  
- **Sp.Attack**: とくこう, 特攻, 特殊攻撃, C, とくしゅこうげき
- **Sp.Defense**: とくぼう, 特防, 特殊防御, D, とくしゅぼうぎょ
- **Speed**: すばやさ, 素早さ, S, スピード, 速さ

**🚨 EV DETECTION PROTOCOL:**
1. **SCAN METHODICALLY**: Check every paragraph for EV patterns
2. **MULTIPLE FORMATS**: Try ALL 5 formats for each Pokemon
3. **VALIDATE TOTALS**: EVs must total ≤508 (if >508, these are battle stats, not EVs)
4. **COMMON PATTERNS**: Look for 252/252/4, 252/0/0/252/4/0, 244/0/12/252/0/0
5. **NEVER GIVE UP**: If one format fails, try others - EVs are always present

**⚡ EV VALIDATION REQUIREMENTS:**
- Valid EV values: 0, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 100, 108, 116, 124, 132, 140, 148, 156, 164, 172, 180, 188, 196, 204, 212, 220, 228, 236, 244, 252
- Total EVs must be ≤508
- Individual stats must be ≤252
- Multiples of 4 are preferred (indicates proper EV allocation)

CRITICAL REQUIREMENTS:
1. ALWAYS provide a valid JSON response
2. Include EV spreads for ALL Pokemon - FIND THEM USING THE FORMATS ABOVE
3. Provide strategic explanations for EV choices
4. Translate all Japanese text to English with PERFECT Pokemon identification
5. Ensure team composition makes sense for VGC format
6. Use EXACT Pokemon names with proper forms and spellings
7. EXTRACT regulation information from the article content - DO NOT ASSUME

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