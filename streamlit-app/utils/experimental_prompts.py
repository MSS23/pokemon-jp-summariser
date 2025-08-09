"""
Experimental Prompting System for Pokemon Team Analysis
This module implements advanced prompting techniques while preserving the current working system.
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import json
from datetime import datetime

@dataclass
class ParsingResult:
    """Container for parsing results with confidence scores and metadata."""
    success: bool
    data: Dict[str, Any]
    confidence: float
    reasoning: str
    missing_fields: List[str]
    corrections_applied: List[str]
    timestamp: datetime

@dataclass
class UserFeedback:
    """Container for user feedback on parsing accuracy."""
    team_id: str
    field_name: str
    original_value: str
    corrected_value: str
    confidence_rating: int  # 1-5 scale
    feedback_notes: str
    timestamp: datetime
    user_ip: str = ""  # For spam detection
    session_id: str = ""  # For session tracking
    
    def __post_init__(self):
        """Validate feedback data after initialization."""
        # Validate confidence rating
        if not 1 <= self.confidence_rating <= 5:
            raise ValueError("Confidence rating must be between 1 and 5")
        
        # Validate field name
        valid_fields = ['name', 'ability', 'item', 'nature', 'tera', 'moves', 'ev_spread', 'ev_explanation']
        if self.field_name not in valid_fields:
            raise ValueError(f"Invalid field name. Must be one of: {valid_fields}")
        
        # Validate string lengths
        if len(self.original_value) > 500:
            raise ValueError("Original value too long (max 500 characters)")
        if len(self.corrected_value) > 500:
            raise ValueError("Corrected value too long (max 500 characters)")
        if len(self.feedback_notes) > 1000:
            raise ValueError("Feedback notes too long (max 1000 characters)")
        
        # Validate team_id format
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.team_id):
            raise ValueError("Team ID contains invalid characters")

class ExperimentalPromptManager:
    """Advanced prompting system with error recovery and multi-step analysis."""
    
    def __init__(self, llm_model_func):
        """Initialize the experimental prompt manager."""
        self.llm_model_func = llm_model_func
        self.feedback_database = []
        
        # Initialize Gemini model for direct calls
        try:
            import streamlit as st
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage
            import os
            
            api_key = os.getenv('GOOGLE_API_KEY') or st.secrets.get('google_api_key', '')
            if api_key:
                self.gemini_model = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=api_key,
                    temperature=0.1,
                    max_output_tokens=8192
                )
                self.human_message = HumanMessage
            else:
                self.gemini_model = None
                self.human_message = None
        except Exception as e:
            print(f"⚠️ Could not initialize Gemini model: {e}")
            self.gemini_model = None
            self.human_message = None
        
        # Anti-spam and validation settings
        self.rate_limit_window = 3600  # 1 hour
        self.max_feedback_per_hour = 10
        self.max_feedback_per_session = 50
        self.feedback_history = {}  # Track feedback by IP/session
        self.parsing_history = []  # Track parsing results for analysis
        self.spam_keywords = [
            'spam', 'test', 'fake', 'nonsense', 'garbage', 'trash', 'invalid',
            'random', 'asdf', 'qwerty', '123456', 'password', 'admin'
        ]

    def analyze_team_from_structured_data(self, structured_data: dict, progress_callback=None):
        """Analyze team from structured data (like from an image)"""
        if progress_callback:
            progress_callback("🖼️ Analyzing team from structured data...")
        
        try:
            # Convert structured data to the expected format
            pokemon_list = []
            
            for pokemon_data in structured_data.get('pokemon', []):
                pokemon = {
                    'name': pokemon_data.get('name', ''),
                    'ability': pokemon_data.get('ability', ''),
                    'item': pokemon_data.get('item', ''),
                    'tera_type': pokemon_data.get('tera_type', ''),
                    'nature': pokemon_data.get('nature', ''),
                    'moves': pokemon_data.get('moves', []),
                    'ev_spread': pokemon_data.get('ev_spread', [0, 0, 0, 0, 0, 0]),
                    'ev_explanation': pokemon_data.get('ev_explanation', ''),
                    'types': pokemon_data.get('types', [])
                }
                pokemon_list.append(pokemon)
            
            # Create a successful result
            result_data = {
                'pokemon': pokemon_list,
                'title': structured_data.get('title', 'Team Analysis'),
                'summary': structured_data.get('summary', 'Team analyzed from structured data'),
                'strengths': structured_data.get('strengths', []),
                'weaknesses': structured_data.get('weaknesses', [])
            }
            
            if progress_callback:
                progress_callback("✅ Successfully analyzed team from structured data")
            
            return ParsingResult(
                success=True,
                data=result_data,
                confidence=0.95,  # High confidence for structured data
                reasoning="Team analyzed from structured data source",
                missing_fields=[],
                corrections_applied=[],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return ParsingResult(
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Error analyzing structured data: {str(e)}",
                missing_fields=[],
                corrections_applied=[],
                timestamp=datetime.now()
            )
        self.suspicious_patterns = [
            r'[A-Z]{10,}',  # Too many consecutive caps
            r'[0-9]{10,}',  # Too many consecutive numbers
            r'[!@#$%^&*]{5,}',  # Too many special characters
            r'(.)\1{5,}',  # Repeated characters
        ]
        
    def analyze_team_with_chain_of_thought(self, article_text: str, progress_callback=None) -> ParsingResult:
        """
        Multi-step analysis using chain-of-thought prompting.
        """
        if progress_callback:
            progress_callback("🔍 Starting experimental chain-of-thought analysis...")
        print("🔍 Starting experimental chain-of-thought analysis...")
        
        # Step 1: Initial reasoning about the content
        if progress_callback:
            progress_callback("🤔 Step 1/4: Analyzing article content and structure...")
        
        reasoning_prompt = f"""
        You are analyzing a Pokemon VGC team article. Before providing the final analysis, please think through this step by step:

        ARTICLE TEXT:
        {article_text[:2000]}...

        Please explain your reasoning:
        1. What type of content is this? (tournament report, team share, analysis, etc.)
        2. How many Pokemon teams are mentioned?
        3. What format is this team for? (VGC, Smogon, etc.)
        4. What key information patterns do you see?
        5. What might be challenging to parse accurately?
        6. Is there Japanese text that needs translation to English?
        7. What Pokemon names, abilities, items, moves, and other details can you identify?

        IMPORTANT: If you see Japanese text, note what needs to be translated to English equivalents.
        Provide your reasoning in a clear, structured format.
        """
        
        if self.gemini_model:
            message = self.human_message(content=reasoning_prompt)
            response = self.gemini_model.invoke([message])
            reasoning_response = str(response.content)
        else:
            # Fallback to function-based approach
            reasoning_response = "Experimental analysis not available - Gemini model not initialized"
        
        if progress_callback:
            progress_callback(f"✅ Step 1 complete: {reasoning_response[:100]}...")
        print(f"🤔 Reasoning: {reasoning_response[:200]}...")
        
        # Step 2: Extract Pokemon sections
        if progress_callback:
            progress_callback("📝 Step 2/4: Extracting Pokemon information and translating Japanese text...")
        
        extraction_prompt = f"""
        Based on your reasoning, extract each Pokemon's information section by section.
        
        REASONING: {reasoning_response}
        ARTICLE: {article_text}
        
        CRITICAL INSTRUCTIONS:
        - Look for exactly 6 Pokemon in the team (VGC teams have 6 Pokemon)
        - Focus on the "個体紹介" (Pokemon introduction) section if present
        - TRANSLATE ALL JAPANESE TEXT TO ENGLISH for the extracted fields
        - Pay special attention to Japanese patterns like:
          * 特性 (ability) → translate to English ability name
          * 持ち物 (held item) → translate to English item name
          * 性格 (nature) → translate to English nature name
          * テラスタル (Tera) → translate to English type name
          * 技 (moves) → translate to English move names
          * 努力値 (EVs) → translate to English explanation
        - Extract the raw text section for each Pokemon that contains:
          * Pokemon name (English)
          * Ability (English)
          * Held item (English)
          * Nature (English)
          * Tera type (English)
          * Moves (English)
          * EV spread (numbers)
          * EV explanation (English)
        
        IMPORTANT: 
        - Translate Japanese terms to English equivalents:
          * 特性 (ability) → English ability name
          * 持ち物 (held item) → English item name
          * 性格 (nature) → English nature name
          * テラスタル (Tera) → English type name
          * 技 (moves) → English move names
          * 努力値 (EVs) → English explanation
        - Look for Pokemon names, abilities, items, natures, Tera types, moves, and EV information in the text
        - If you find Pokemon information, extract it clearly in English
        - If you don't find structured Pokemon data, try to identify any Pokemon mentioned and their details
        - Pay attention to Japanese text that might contain Pokemon information and translate it
        
        Format as:
        POKEMON 1: [raw text section with Pokemon details in English]
        POKEMON 2: [raw text section with Pokemon details in English]
        POKEMON 3: [raw text section with Pokemon details in English]
        POKEMON 4: [raw text section with Pokemon details in English]
        POKEMON 5: [raw text section with Pokemon details in English]
        POKEMON 6: [raw text section with Pokemon details in English]
        
        If you can't find clear Pokemon sections, try to extract any Pokemon-related information you can find.
        Make sure to extract exactly 6 Pokemon sections if possible.
        """
        
        if self.gemini_model:
            message = self.human_message(content=extraction_prompt)
            response = self.gemini_model.invoke([message])
            extraction_response = str(response.content)
        else:
            extraction_response = "Experimental analysis not available - Gemini model not initialized"
        
        if progress_callback:
            progress_callback(f"✅ Step 2 complete: Extracted {len(extraction_response)} characters of Pokemon data")
        print(f"📝 Extracted sections: {len(extraction_response)} characters")
        
        # Step 3: Parse each Pokemon individually
        if progress_callback:
            progress_callback("🔍 Step 3/4: Parsing individual Pokemon details...")
        
        pokemon_data = []
        missing_fields = []
        corrections_applied = []
        
        # Split into individual Pokemon sections
        pokemon_sections = self._extract_pokemon_sections(extraction_response)
        
        if progress_callback:
            progress_callback(f"📊 Found {len(pokemon_sections)} Pokemon sections to parse")
        
        for i, section in enumerate(pokemon_sections):
            if progress_callback:
                progress_callback(f"🔍 Parsing Pokemon {i+1}/{len(pokemon_sections)}: {section[:50]}...")
            print(f"🔍 Parsing Pokemon {i+1}...")
            
            # Individual Pokemon parsing with detailed reasoning
            pokemon_result = self._parse_single_pokemon_with_reasoning(section, i+1)
            
            if pokemon_result.success:
                pokemon_data.append(pokemon_result.data)
                if progress_callback:
                    progress_callback(f"✅ Pokemon {i+1} parsed successfully: {pokemon_result.data.get('name', 'Unknown')}")
            else:
                print(f"❌ Failed to parse Pokemon {i+1}: {pokemon_result.reasoning}")
                if progress_callback:
                    progress_callback(f"❌ Pokemon {i+1} parsing failed: {pokemon_result.reasoning[:100]}...")
            
            missing_fields.extend(pokemon_result.missing_fields)
            corrections_applied.extend(pokemon_result.corrections_applied)
        
        # Step 4: If experimental parsing failed, try main app's parsing as ultimate fallback
        if len(pokemon_data) < 6 or not pokemon_data:
            if progress_callback:
                progress_callback("🔄 Experimental parsing incomplete, trying main app's parsing as fallback...")
            print("🔄 Experimental parsing incomplete, trying main app's parsing as fallback")
            try:
                from utils.gemini_summary import llm_summary_gemini
                main_result = llm_summary_gemini(article_text)
                if main_result and 'pokemon' in main_result:
                    print(f"✅ Main app parsing found {len(main_result['pokemon'])} Pokemon")
                    if progress_callback:
                        progress_callback(f"✅ Main app fallback successful: Found {len(main_result['pokemon'])} Pokemon")
                    pokemon_data = main_result['pokemon']
                    # Reset missing fields and corrections for main app data
                    missing_fields = []
                    corrections_applied = []
            except Exception as e:
                print(f"❌ Main app fallback also failed: {e}")
                if progress_callback:
                    progress_callback(f"❌ Main app fallback failed: {str(e)[:100]}...")
        
        # Step 5: Error recovery for missing fields
        if missing_fields:
            if progress_callback:
                progress_callback(f"⚠️ Step 4/4: Error recovery for {len(missing_fields)} missing fields...")
            print(f"⚠️ Missing fields detected: {missing_fields}")
            recovery_result = self._error_recovery_prompt(article_text, missing_fields, pokemon_data)
            pokemon_data = recovery_result.data
            corrections_applied.extend(recovery_result.corrections_applied)
            if progress_callback:
                progress_callback("✅ Error recovery completed successfully")
        
        # Step 6: Calculate overall confidence
        if progress_callback:
            progress_callback("📊 Calculating final results and confidence...")
        
        confidence = self._calculate_confidence(pokemon_data, missing_fields)
        
        result = ParsingResult(
            success=len(pokemon_data) > 0,
            data={"pokemon": pokemon_data, "reasoning": reasoning_response},
            confidence=confidence,
            reasoning=reasoning_response,
            missing_fields=missing_fields,
            corrections_applied=corrections_applied,
            timestamp=datetime.now()
        )
        
        if progress_callback:
            progress_callback(f"🎉 Analysis complete! Found {len(pokemon_data)} Pokemon with {confidence:.1%} confidence")
        
        self.parsing_history.append(result)
        return result
    
    def analyze_team_with_chain_of_thought_from_url(self, url: str, progress_callback=None) -> ParsingResult:
        """
        Analyze a Pokemon team from a URL using the same langchain backbone as the main app.
        
        Args:
            url (str): Article URL to analyze
            progress_callback (callable): Optional callback for progress updates
            
        Returns:
            ParsingResult: Structured result with confidence scores and metadata
        """
        try:
            if progress_callback:
                progress_callback(f"🔗 Starting URL-based experimental analysis for: {url}")
            print(f"🔗 Starting URL-based experimental analysis for: {url}")
            
            # Use the same langchain backbone as the main app
            from utils.shared_utils import fetch_article_text_and_images
            
            if progress_callback:
                progress_callback("📄 Fetching article content from URL...")
            
            # Fetch article content
            article_text, image_urls = fetch_article_text_and_images(url)
            print(f"📄 Fetched article text ({len(article_text)} characters) and {len(image_urls)} images")
            
            if progress_callback:
                progress_callback(f"✅ Fetched {len(article_text)} characters and {len(image_urls)} images")
            
            # Now apply experimental prompting techniques to the fetched content
            return self.analyze_team_with_chain_of_thought(article_text, progress_callback)
            
        except Exception as e:
            error_msg = f"Error during URL analysis: {str(e)}"
            print(f"❌ {error_msg}")
            if progress_callback:
                progress_callback(f"❌ {error_msg}")
            return ParsingResult(
                success=False,
                data={'pokemon': []},
                confidence=0.0,
                reasoning=error_msg,
                missing_fields=[],
                corrections_applied=[],
                timestamp=datetime.now()
            )
    
    def _parse_single_pokemon_with_reasoning(self, section: str, pokemon_num: int) -> ParsingResult:
        """
        Parse a single Pokemon with detailed reasoning and confidence assessment.
        """
        reasoning_prompt = f"""
        Analyze this Pokemon section step by step:

        SECTION: {section}

        Think through this carefully:
        1. What is the Pokemon's name? (be very careful with similar names like Iron Crown vs Iron Jugulis)
        2. What ability does it have? (look for ability names or descriptions, translate Japanese if needed)
        3. What item is it holding? (look for item names or descriptions, translate Japanese if needed)
        4. What nature does it have? (look for nature names, translate Japanese if needed)
        5. What Tera type is it? (look for Tera type mentions, translate Japanese if needed)
        6. What moves does it have? (look for move names, be careful with move name variations, translate Japanese if needed)
        7. What is the EV spread? (look for numbers that add up to 510 or less)
        8. What is the EV explanation? (look for explanations of the EV choices, translate Japanese if needed)

        IMPORTANT: If you see Japanese text, translate it to English equivalents:
        - 特性 (ability) → English ability name
        - 持ち物 (held item) → English item name  
        - 性格 (nature) → English nature name
        - テラスタル (Tera) → English type name
        - 技 (moves) → English move names
        - 努力値 (EVs) → English explanation

        For each field, explain your reasoning and confidence level (1-5):
        - 1: Very uncertain, multiple possibilities
        - 3: Somewhat confident, but could be wrong
        - 5: Very confident, clear evidence

        Format your response as:
        REASONING:
        [Your step-by-step reasoning]

        CONFIDENCE ASSESSMENT:
        Name: [confidence] - [reasoning]
        Ability: [confidence] - [reasoning]
        Item: [confidence] - [reasoning]
        Nature: [confidence] - [reasoning]
        Tera: [confidence] - [reasoning]
        Moves: [confidence] - [reasoning]
        EV Spread: [confidence] - [reasoning]
        EV Explanation: [confidence] - [reasoning]

        EXTRACTED DATA:
        [JSON format with the extracted data in English]
        """
        
        if self.gemini_model:
            message = self.human_message(content=reasoning_prompt)
            response = self.gemini_model.invoke([message])
            response = str(response.content)
        else:
            response = "Experimental analysis not available - Gemini model not initialized"
        
        # Parse the response to extract data and confidence
        try:
            # Extract JSON data
            json_match = re.search(r'EXTRACTED DATA:\s*(\{.*\})', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Fallback to regex parsing
                data = self._fallback_parsing(section)
            
            # Extract confidence scores
            confidence_scores = self._extract_confidence_scores(response)
            avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 3.0
            
            # Apply corrections based on known patterns
            corrections = self._apply_known_corrections(data)
            
            return ParsingResult(
                success=True,
                data=data,
                confidence=avg_confidence,
                reasoning=response,
                missing_fields=[],
                corrections_applied=corrections,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Error parsing Pokemon {pokemon_num}: {e}")
            
            # Try to use the main app's parsing logic as a fallback
            try:
                from utils.llm_summary import parse_summary
                # Create a mock summary with just this section
                mock_summary = f"Pokemon {pokemon_num}: {section}"
                parsed_data = parse_summary(mock_summary)
                
                if parsed_data.get('pokemon') and len(parsed_data['pokemon']) > 0:
                    pokemon_data = parsed_data['pokemon'][0]
                    return ParsingResult(
                        success=True,
                        data=pokemon_data,
                        confidence=0.5,  # Lower confidence for fallback
                        reasoning=f"Used main app parsing as fallback: {str(e)}",
                        missing_fields=[],
                        corrections_applied=[],
                        timestamp=datetime.now()
                    )
            except Exception as fallback_error:
                print(f"❌ Fallback parsing also failed: {fallback_error}")
            
            return ParsingResult(
                success=False,
                data={},
                confidence=0.0,
                reasoning=f"Error: {str(e)}",
                missing_fields=["all"],
                corrections_applied=[],
                timestamp=datetime.now()
            )
    
    def _error_recovery_prompt(self, article_text: str, missing_fields: List[str], existing_data: List[Dict]) -> ParsingResult:
        """
        Specialized prompts to recover missing information.
        """
        print(f"🔄 Running error recovery for: {missing_fields}")
        
        recovery_prompt = f"""
        The initial parsing missed some information. Please focus specifically on extracting the missing fields.

        MISSING FIELDS: {missing_fields}
        EXISTING DATA: {json.dumps(existing_data, indent=2)}
        ARTICLE TEXT: {article_text}

        For each missing field, use a specialized approach:
        
        - For Pokemon names: Look for capitalized names, check for similar names (Iron Crown vs Iron Jugulis)
        - For moves: Look for move names, check for variations (Bark Out vs Snarl)
        - For items: Look for item names, check for common abbreviations
        - For EV spreads: Look for numbers that could be EV values
        - For abilities: Look for ability names or descriptions
        
        Provide the missing information in JSON format:
        {{
            "missing_data": {{
                "pokemon_index": {{
                    "field_name": "corrected_value"
                }}
            }},
            "reasoning": "Why this correction was made"
        }}
        """
        
        if self.gemini_model:
            message = self.human_message(content=recovery_prompt)
            response = self.gemini_model.invoke([message])
            recovery_response = str(response.content)
        else:
            recovery_response = "Experimental analysis not available - Gemini model not initialized"
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', recovery_response, re.DOTALL)
            if json_match:
                recovery_data = json.loads(json_match.group(0))
                
                # Apply the recovered data to existing data
                updated_data = existing_data.copy()
                if "missing_data" in recovery_data:
                    for pokemon_idx, fields in recovery_data["missing_data"].items():
                        idx = int(pokemon_idx)
                        if idx < len(updated_data):
                            updated_data[idx].update(fields)
                
                return ParsingResult(
                    success=True,
                    data={"pokemon": updated_data},
                    confidence=0.7,  # Lower confidence for recovered data
                    reasoning=recovery_response,
                    missing_fields=[],
                    corrections_applied=list(recovery_data.get("missing_data", {}).values()),
                    timestamp=datetime.now()
                )
        except Exception as e:
            print(f"❌ Error in recovery: {e}")
        
        return ParsingResult(
            success=False,
            data={"pokemon": existing_data},
            confidence=0.0,
            reasoning=f"Recovery failed: {str(e)}",
            missing_fields=missing_fields,
            corrections_applied=[],
            timestamp=datetime.now()
        )
    
    def _extract_pokemon_sections(self, extraction_response: str) -> List[str]:
        """Extract individual Pokemon sections from the LLM response."""
        print(f"🔍 Extracting Pokemon sections from response ({len(extraction_response)} chars)")
        print(f"📄 Response preview: {extraction_response[:500]}...")
        
        sections = []
        
        # Method 1: Look for "POKEMON X:" format
        pokemon_pattern = r'POKEMON\s+\d+:\s*(.*?)(?=POKEMON\s+\d+:|$)'
        matches = re.findall(pokemon_pattern, extraction_response, re.DOTALL | re.IGNORECASE)
        if matches:
            sections = [match.strip() for match in matches if match.strip()]
            print(f"✅ Found {len(sections)} sections using POKEMON pattern")
        
        # Method 2: If no POKEMON format, look for numbered sections
        if not sections:
            numbered_pattern = r'\d+\.\s*(.*?)(?=\d+\.|$)'
            matches = re.findall(numbered_pattern, extraction_response, re.DOTALL)
            if matches:
                sections = [match.strip() for match in matches if match.strip()]
                print(f"✅ Found {len(sections)} sections using numbered pattern")
        
        # Method 3: Look for Pokemon names followed by details
        if not sections:
            # Common Pokemon names that might appear in the text
            pokemon_names = [
                r'Calyrex', r'Iron\s+Valiant', r'Iron\s+Jugulis', r'Rillaboom', 
                r'Urshifu', r'Incineroar', r'Zamazenta', r'Zacian', r'Kyogre',
                r'Groudon', r'Rayquaza', r'Charizard', r'Venusaur', r'Blastoise'
            ]
            
            for name_pattern in pokemon_names:
                name_sections = re.split(f'({name_pattern})', extraction_response, flags=re.IGNORECASE)
                if len(name_sections) > 1:
                    # Reconstruct sections with Pokemon names
                    temp_sections = []
                    for i in range(1, len(name_sections), 2):  # Skip empty parts
                        if i < len(name_sections) - 1:
                            section = name_sections[i] + name_sections[i + 1]
                            if section.strip():
                                temp_sections.append(section.strip())
                    if temp_sections:
                        sections = temp_sections
                        print(f"✅ Found {len(sections)} sections using Pokemon name pattern")
                        break
        
        # Method 4: Split by double newlines or major separators
        if not sections:
            # Split by double newlines or major separators
            potential_sections = re.split(r'\n\s*\n|\n\s*[-=*]\s*\n', extraction_response)
            if len(potential_sections) > 1:
                sections = [s.strip() for s in potential_sections if s.strip() and len(s.strip()) > 50]
                print(f"✅ Found {len(sections)} sections using separator pattern")
        
        # Method 5: Last resort - split by lines and group
        if not sections:
            lines = extraction_response.split('\n')
            current_section = ""
            for line in lines:
                if line.strip() and (line.strip().startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.')) or 
                                   any(name.lower() in line.lower() for name in ['calyrex', 'iron', 'rillaboom', 'urshifu', 'incineroar'])):
                    if current_section:
                        sections.append(current_section.strip())
                    current_section = line
                else:
                    current_section += '\n' + line
            
            if current_section:
                sections.append(current_section.strip())
            
            if sections:
                print(f"✅ Found {len(sections)} sections using line grouping")
        
        # If still no sections, treat the entire response as one section
        if not sections:
            sections = [extraction_response.strip()]
            print(f"⚠️ No sections found, treating entire response as one section")
        
        # Limit to 6 Pokemon maximum (VGC teams have 6 Pokemon)
        if len(sections) > 6:
            print(f"⚠️ Found {len(sections)} sections, limiting to first 6")
            sections = sections[:6]
        
        print(f"📊 Final sections count: {len(sections)}")
        for i, section in enumerate(sections):
            print(f"  Section {i+1}: {section[:100]}...")
        
        return sections
    
    def _extract_confidence_scores(self, response: str) -> Dict[str, int]:
        """Extract confidence scores from the reasoning response."""
        confidence_scores = {}
        
        # Look for confidence patterns
        confidence_pattern = r'(\w+):\s*(\d+)\s*-\s*(.+)'
        matches = re.findall(confidence_pattern, response)
        
        for field, score, reasoning in matches:
            try:
                confidence_scores[field.lower()] = int(score)
            except ValueError:
                continue
        
        return confidence_scores
    
    def _fallback_parsing(self, section: str) -> Dict[str, Any]:
        """Enhanced fallback parsing using regex patterns with better Japanese support."""
        print(f"🔍 Enhanced fallback parsing section: {section[:200]}...")
        data = {}
        
        # Enhanced patterns with better Japanese support and more robust matching
        patterns = {
            'name': [
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Capitalized words (Pokemon names)
                r'([A-Z][A-Z\s]+)',  # All caps (like POKEMON)
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[-:]\s*',  # Name followed by dash or colon
            ],
            'ability': [
                r'ability[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy ability
                r'特性[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: 特性 (ability)
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+ability',
                r'ability\s*[-:]\s*([A-Za-z\s]+?)(?=\n|$)',  # Ability: format
            ],
            'item': [
                r'item[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy item
                r'持ち物[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: 持ち物 (held item)
                r'holding[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',
                r'item\s*[-:]\s*([A-Za-z\s]+?)(?=\n|$)',  # Item: format
            ],
            'nature': [
                r'nature[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy nature
                r'性格[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: 性格 (nature)
                r'([A-Z][a-z]+)\s+nature',
                r'nature\s*[-:]\s*([A-Za-z\s]+?)(?=\n|$)',  # Nature: format
            ],
            'tera': [
                r'tera[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy tera
                r'テラスタル[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: テラスタル (Tera)
                r'tera\s+type[:\s]*([A-Za-z\s]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',
                r'tera\s*[-:]\s*([A-Za-z\s]+?)(?=\n|$)',  # Tera: format
            ],
            'moves': [
                r'moves[:\s]*([A-Za-z\s\/\,]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy moves
                r'技[:\s]*([A-Za-z\s\/\,]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: 技 (moves)
                r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*/\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'moves\s*[-:]\s*([A-Za-z\s\/\,]+?)(?=\n|$)',  # Moves: format
            ],
            'ev_spread': [
                r'ev\s+spread[:\s]*(\d+(?:\s+\d+)*)',  # Numbers only
                r'(\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+)',  # 6 numbers
                r'(\d+\s+\d+\s+\d+\s+\d+\s+\d+)',  # 5 numbers
                r'努力値[:\s]*(\d+(?:\s+\d+)*)',  # Japanese: 努力値 (EVs) - numbers only
                r'ev\s*[-:]\s*(\d+(?:\s+\d+)*)',  # EV: format
            ],
            'ev_explanation': [
                r'ev\s+explanation[:\s]*([^.]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Non-greedy explanation
                r'説明[:\s]*([^.]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',  # Japanese: 説明 (explanation)
                r'explanation[:\s]*([^.]+?)(?=\n|Ability:|Item:|Nature:|Tera:|Moves:|EV Spread:|EV Explanation:|特性:|持ち物:|性格:|テラスタル:|技:|努力値:|説明:|$|\Z)',
                r'explanation\s*[-:]\s*([^.]+?)(?=\n|$)',  # Explanation: format
            ]
        }
        
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    if field == 'moves' and len(match.groups()) > 1:
                        # Handle multiple moves
                        moves = [match.group(i) for i in range(1, len(match.groups()) + 1)]
                        data[field] = ' / '.join(moves)
                    else:
                        data[field] = match.group(1).strip()
                    print(f"✅ Found {field}: {data[field]}")
                    break  # Use first match found
        
        # If no name found, try to extract any capitalized word that might be a Pokemon name
        if 'name' not in data or not data['name']:
            # Look for potential Pokemon names (capitalized words)
            name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', section)
            if name_match:
                data['name'] = name_match.group(1)
                print(f"✅ Found name (fallback): {data['name']}")
        
        # If still no data found, try to extract any information
        if not data:
            print(f"⚠️ No data extracted from section")
            # Try to extract any numbers that might be EVs
            ev_numbers = re.findall(r'\d+', section)
            if ev_numbers:
                data['ev_spread'] = ' '.join(ev_numbers[:6])  # Take first 6 numbers
                print(f"✅ Found EV numbers: {data['ev_spread']}")
            
            # Try to extract any capitalized words that might be moves or Pokemon
            capitalized_words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', section)
            if capitalized_words:
                data['name'] = capitalized_words[0]  # First capitalized word as name
                if len(capitalized_words) > 1:
                    data['moves'] = ' / '.join(capitalized_words[1:5])  # Next few as moves
                print(f"✅ Found name and moves from capitalized words")
        
        print(f"📊 Final parsed data: {data}")
        return data
    
    def _apply_known_corrections(self, data: Dict[str, Any]) -> List[str]:
        """Apply known corrections based on common patterns."""
        corrections = []
        
        # Pokemon name corrections
        pokemon_corrections = {
            'Iron Crown': 'Iron Jugulis',
            'iron crown': 'Iron Jugulis'
        }
        
        # Move corrections
        move_corrections = {
            'Bark Out': 'Snarl',
            'bark out': 'Snarl'
        }
        
        # Item corrections
        item_corrections = {
            'Choice Band': 'Assault Vest',
            'choice band': 'Assault Vest'
        }
        
        # Apply corrections
        if 'name' in data:
            for wrong, correct in pokemon_corrections.items():
                if wrong in data['name']:
                    data['name'] = data['name'].replace(wrong, correct)
                    corrections.append(f"Pokemon name: {wrong} → {correct}")
        
        if 'moves' in data:
            for wrong, correct in move_corrections.items():
                if wrong in data['moves']:
                    data['moves'] = data['moves'].replace(wrong, correct)
                    corrections.append(f"Move: {wrong} → {correct}")
        
        if 'item' in data:
            for wrong, correct in item_corrections.items():
                if wrong in data['item']:
                    data['item'] = data['item'].replace(wrong, correct)
                    corrections.append(f"Item: {wrong} → {correct}")
        
        return corrections
    
    def _calculate_confidence(self, pokemon_data: List[Dict], missing_fields: List[str]) -> float:
        """Calculate overall confidence score."""
        if not pokemon_data:
            return 0.0
        
        # Base confidence on number of Pokemon found
        base_confidence = min(len(pokemon_data) / 6.0, 1.0)  # Assuming 6 Pokemon team
        
        # Penalty for missing fields
        missing_penalty = len(missing_fields) * 0.1
        
        # Bonus for complete data
        complete_bonus = 0.0
        for pokemon in pokemon_data:
            required_fields = ['name', 'ability', 'item', 'nature', 'tera', 'moves', 'ev_spread']
            if all(field in pokemon for field in required_fields):
                complete_bonus += 0.1
        
        confidence = base_confidence - missing_penalty + complete_bonus
        return max(0.0, min(1.0, confidence))
    
    def submit_user_feedback(self, team_id: str, field_name: str, original_value: str, 
                           corrected_value: str, confidence_rating: int, feedback_notes: str = "",
                           user_ip: str = "", session_id: str = "") -> Dict[str, Any]:
        """
        Submit user feedback for parsing accuracy with comprehensive validation.
        Returns a dictionary with success status and any validation messages.
        """
        validation_result = self._validate_feedback(
            team_id, field_name, original_value, corrected_value, 
            confidence_rating, feedback_notes, user_ip, session_id
        )
        
        if not validation_result['valid']:
            return validation_result
        
        try:
            feedback = UserFeedback(
                team_id=team_id,
                field_name=field_name,
                original_value=original_value,
                corrected_value=corrected_value,
                confidence_rating=confidence_rating,
                feedback_notes=feedback_notes,
                timestamp=datetime.now(),
                user_ip=user_ip,
                session_id=session_id
            )
            
            self.feedback_database.append(feedback)
            self._update_feedback_history(user_ip, session_id)
            
            print(f"✅ Feedback submitted: {field_name} correction for team {team_id}")
            return {"valid": True, "message": "Feedback submitted successfully"}
            
        except ValueError as e:
            return {"valid": False, "error": f"Invalid feedback data: {e}"}
        except Exception as e:
            return {"valid": False, "error": f"Error submitting feedback: {e}"}
    
    def _validate_feedback(self, team_id: str, field_name: str, original_value: str, 
                          corrected_value: str, confidence_rating: int, feedback_notes: str,
                          user_ip: str, session_id: str) -> Dict[str, Any]:
        """Comprehensive validation of feedback data."""
        
        # Basic validation
        if not all([team_id, field_name, original_value, corrected_value]):
            return {"valid": False, "error": "All required fields must be provided"}
        
        # Rate limiting check
        rate_limit_result = self._check_rate_limit(user_ip, session_id)
        if not rate_limit_result['allowed']:
            return {"valid": False, "error": f"Rate limit exceeded: {rate_limit_result['message']}"}
        
        # Content validation
        content_result = self._validate_content(original_value, corrected_value, feedback_notes)
        if not content_result['valid']:
            return {"valid": False, "error": f"Content validation failed: {content_result['error']}"}
        
        # Spam detection
        spam_result = self._detect_spam(original_value, corrected_value, feedback_notes)
        if spam_result['is_spam']:
            return {"valid": False, "error": f"Spam detected: {spam_result['reason']}"}
        
        # Pokemon-specific validation
        pokemon_result = self._validate_pokemon_data(field_name, original_value, corrected_value)
        if not pokemon_result['valid']:
            return {"valid": False, "error": f"Pokemon data validation failed: {pokemon_result['error']}"}
        
        return {"valid": True}
    
    def _check_rate_limit(self, user_ip: str, session_id: str) -> Dict[str, Any]:
        """Check if user has exceeded rate limits."""
        current_time = datetime.now()
        user_key = user_ip or session_id
        
        if user_key not in self.feedback_history:
            self.feedback_history[user_key] = []
        
        # Remove old entries (older than 1 hour)
        self.feedback_history[user_key] = [
            timestamp for timestamp in self.feedback_history[user_key]
            if (current_time - timestamp).seconds < self.rate_limit_window
        ]
        
        # Check hourly limit
        if len(self.feedback_history[user_key]) >= self.max_feedback_per_hour:
            return {
                "allowed": False,
                "message": f"Maximum {self.max_feedback_per_hour} feedback submissions per hour exceeded"
            }
        
        # Check session limit
        session_feedback = [f for f in self.feedback_database if f.session_id == session_id]
        if len(session_feedback) >= self.max_feedback_per_session:
            return {
                "allowed": False,
                "message": f"Maximum {self.max_feedback_per_session} feedback submissions per session exceeded"
            }
        
        return {"allowed": True}
    
    def _validate_content(self, original_value: str, corrected_value: str, feedback_notes: str) -> Dict[str, Any]:
        """Validate content quality and length."""
        
        # Check for empty or whitespace-only values
        if not original_value.strip() or not corrected_value.strip():
            return {"valid": False, "error": "Original and corrected values cannot be empty"}
        
        # Check length limits
        if len(original_value) > 500:
            return {"valid": False, "error": "Original value too long (max 500 characters)"}
        if len(corrected_value) > 500:
            return {"valid": False, "error": "Corrected value too long (max 500 characters)"}
        if len(feedback_notes) > 1000:
            return {"valid": False, "error": "Feedback notes too long (max 1000 characters)"}
        
        # Check for identical values
        if original_value.strip().lower() == corrected_value.strip().lower():
            return {"valid": False, "error": "Original and corrected values cannot be identical"}
        
        return {"valid": True}
    
    def _detect_spam(self, original_value: str, corrected_value: str, feedback_notes: str) -> Dict[str, Any]:
        """Detect potential spam or malicious content."""
        
        # Check for spam keywords
        all_text = f"{original_value} {corrected_value} {feedback_notes}".lower()
        for keyword in self.spam_keywords:
            if keyword in all_text:
                return {"is_spam": True, "reason": f"Contains spam keyword: {keyword}"}
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if re.search(pattern, all_text):
                return {"is_spam": True, "reason": f"Matches suspicious pattern: {pattern}"}
        
        # Check for excessive repetition
        if len(set(all_text.split())) < 3:  # Too few unique words
            return {"is_spam": True, "reason": "Too few unique words"}
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', all_text)) / len(all_text)
        if special_char_ratio > 0.3:  # More than 30% special characters
            return {"is_spam": True, "reason": "Excessive special characters"}
        
        return {"is_spam": False}
    
    def _validate_pokemon_data(self, field_name: str, original_value: str, corrected_value: str) -> Dict[str, Any]:
        """Validate Pokemon-specific data."""
        
        # Pokemon name validation
        if field_name == 'name':
            # Check for valid Pokemon name patterns
            if not re.match(r'^[A-Za-z\s\-\.\']+$', corrected_value):
                return {"valid": False, "error": "Invalid Pokemon name format"}
            
            # Check for reasonable length
            if len(corrected_value) < 2 or len(corrected_value) > 50:
                return {"valid": False, "error": "Pokemon name length must be between 2 and 50 characters"}
        
        # Move validation
        elif field_name == 'moves':
            # Check for valid move name patterns
            if not re.match(r'^[A-Za-z\s\-\.\']+$', corrected_value):
                return {"valid": False, "error": "Invalid move name format"}
        
        # EV spread validation
        elif field_name == 'ev_spread':
            # Check for valid EV format (numbers separated by spaces)
            if not re.match(r'^(\d+\s+)*\d+$', corrected_value):
                return {"valid": False, "error": "EV spread must be numbers separated by spaces"}
            
            # Check for reasonable EV values
            ev_values = [int(x) for x in corrected_value.split()]
            if not (1 <= len(ev_values) <= 6):
                return {"valid": False, "error": "EV spread must have 1-6 values"}
            
            for ev in ev_values:
                if not (0 <= ev <= 252):
                    return {"valid": False, "error": "EV values must be between 0 and 252"}
        
        # Nature validation
        elif field_name == 'nature':
            valid_natures = [
                'Hardy', 'Lonely', 'Brave', 'Adamant', 'Naughty', 'Bold', 'Docile', 'Relaxed',
                'Impish', 'Lax', 'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive', 'Modest',
                'Mild', 'Quiet', 'Bashful', 'Rash', 'Calm', 'Gentle', 'Sassy', 'Careful',
                'Quirky'
            ]
            if corrected_value not in valid_natures:
                return {"valid": False, "error": f"Invalid nature: {corrected_value}"}
        
        return {"valid": True}
    
    def _update_feedback_history(self, user_ip: str, session_id: str):
        """Update feedback history for rate limiting."""
        user_key = user_ip or session_id
        if user_key not in self.feedback_history:
            self.feedback_history[user_key] = []
        
        self.feedback_history[user_key].append(datetime.now())
    
    def get_feedback_quality_report(self) -> Dict[str, Any]:
        """Generate a quality report for feedback data."""
        if not self.feedback_database:
            return {"message": "No feedback data available"}
        
        total_feedback = len(self.feedback_database)
        
        # Calculate quality metrics
        avg_confidence = sum(f.confidence_rating for f in self.feedback_database) / total_feedback
        
        # Check for potential spam
        spam_indicators = []
        for feedback in self.feedback_database:
            spam_result = self._detect_spam(
                feedback.original_value, 
                feedback.corrected_value, 
                feedback.feedback_notes
            )
            if spam_result['is_spam']:
                spam_indicators.append({
                    'team_id': feedback.team_id,
                    'field': feedback.field_name,
                    'reason': spam_result['reason']
                })
        
        # Rate limiting violations
        rate_limit_violations = []
        for user_key, timestamps in self.feedback_history.items():
            if len(timestamps) > self.max_feedback_per_hour:
                rate_limit_violations.append({
                    'user': user_key,
                    'submissions': len(timestamps)
                })
        
        return {
            "total_feedback": total_feedback,
            "average_confidence": avg_confidence,
            "spam_indicators": spam_indicators,
            "rate_limit_violations": rate_limit_violations,
            "quality_score": self._calculate_quality_score(),
            "recommendations": self._generate_quality_recommendations()
        }
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall feedback quality score (0-100)."""
        if not self.feedback_database:
            return 0.0
        
        score = 100.0
        
        # Penalize for spam
        spam_count = 0
        for feedback in self.feedback_database:
            spam_result = self._detect_spam(
                feedback.original_value, 
                feedback.corrected_value, 
                feedback.feedback_notes
            )
            if spam_result['is_spam']:
                spam_count += 1
        
        spam_penalty = (spam_count / len(self.feedback_database)) * 50
        score -= spam_penalty
        
        # Penalize for low confidence ratings
        low_confidence_count = sum(1 for f in self.feedback_database if f.confidence_rating <= 2)
        confidence_penalty = (low_confidence_count / len(self.feedback_database)) * 20
        score -= confidence_penalty
        
        return max(0.0, score)
    
    def _generate_quality_recommendations(self) -> List[str]:
        """Generate recommendations for improving feedback quality."""
        recommendations = []
        
        if not self.feedback_database:
            return ["No feedback data available for analysis"]
        
        # Check for spam
        spam_count = 0
        for feedback in self.feedback_database:
            spam_result = self._detect_spam(
                feedback.original_value, 
                feedback.corrected_value, 
                feedback.feedback_notes
            )
            if spam_result['is_spam']:
                spam_count += 1
        
        if spam_count > 0:
            recommendations.append(f"Review {spam_count} potential spam submissions")
        
        # Check for low confidence
        low_confidence_count = sum(1 for f in self.feedback_database if f.confidence_rating <= 2)
        if low_confidence_count > len(self.feedback_database) * 0.3:  # More than 30%
            recommendations.append("Consider improving feedback collection process")
        
        # Check for rate limiting
        if any(len(timestamps) > self.max_feedback_per_hour for timestamps in self.feedback_history.values()):
            recommendations.append("Implement stricter rate limiting")
        
        if not recommendations:
            recommendations.append("Feedback quality appears good")
        
        return recommendations
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Get statistics from user feedback."""
        if not self.feedback_database:
            return {"total_feedback": 0}
        
        total_feedback = len(self.feedback_database)
        avg_confidence = sum(f.confidence_rating for f in self.feedback_database) / total_feedback
        
        # Most common corrections
        corrections = {}
        for feedback in self.feedback_database:
            key = f"{feedback.field_name}: {feedback.original_value} → {feedback.corrected_value}"
            corrections[key] = corrections.get(key, 0) + 1
        
        most_common = sorted(corrections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_feedback": total_feedback,
            "average_confidence": avg_confidence,
            "most_common_corrections": most_common,
            "recent_feedback": [
                {
                    "field": f.field_name,
                    "correction": f"{f.original_value} → {f.corrected_value}",
                    "rating": f.confidence_rating,
                    "timestamp": f.timestamp.isoformat()
                }
                for f in self.feedback_database[-10:]  # Last 10 feedback entries
            ]
        }
    
    def export_feedback_data(self, filename: str = "feedback_data.json") -> None:
        """Export feedback data to JSON file."""
        data = {
            "feedback_entries": [
                {
                    "team_id": f.team_id,
                    "field_name": f.field_name,
                    "original_value": f.original_value,
                    "corrected_value": f.corrected_value,
                    "confidence_rating": f.confidence_rating,
                    "feedback_notes": f.feedback_notes,
                    "timestamp": f.timestamp.isoformat()
                }
                for f in self.feedback_database
            ],
            "statistics": self.get_feedback_statistics()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📊 Feedback data exported to {filename}")

# Example usage function
def test_experimental_prompts(llm_model_func, article_text: str) -> ParsingResult:
    """
    Test function to demonstrate the experimental prompting system.
    """
    prompt_manager = ExperimentalPromptManager(llm_model_func)
    
    print("🧪 Testing Experimental Prompting System")
    print("=" * 50)
    
    # Run the experimental analysis
    result = prompt_manager.analyze_team_with_chain_of_thought(article_text)
    
    print(f"\n📊 Results:")
    print(f"Success: {result.success}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Pokemon Found: {len(result.data.get('pokemon', []))}")
    print(f"Missing Fields: {result.missing_fields}")
    print(f"Corrections Applied: {result.corrections_applied}")
    
    return result
