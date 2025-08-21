"""
Shared LLM utilities for Pokémon VGC analysis
Common functions used by both Streamlit and React applications
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional, Any

# Import shared utilities
from .shared_utils import fetch_article_text_and_images

def extract_pokemon_names(summary: str) -> List[str]:
    """
    Extract Pokémon names from summary text
    
    Args:
        summary (str): Generated summary text
    
    Returns:
        list: List of Pokémon names
    """
    lines = summary.splitlines()
    pokemon_names = []

    # Method 1: Try 1. to 6. pattern
    numbered = [
        re.sub(r"^\d+\.\s+", "", line).strip()
        for line in lines if re.match(r"^\d+\.\s+", line)
    ]
    if len(numbered) == 6:
        pokemon_names = numbered

    # Method 2: Name: entries
    if not pokemon_names:
        pokemon_names = [
            line.replace("Name:", "").strip()
            for line in lines if line.strip().startswith("Name:")
        ]

    return pokemon_names

def parse_gemini_response(text: str) -> Dict[str, Any]:
    """
    Parse Gemini response into structured format
    
    Args:
        text (str): Raw Gemini response text
    
    Returns:
        dict: Structured response with teams and metadata
    """
    try:
        # Extract title
        title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', text)
        title = title_match.group(1).strip() if title_match else 'Not specified'

        # Extract Pokemon teams
        pokemon_sections = re.split(r'\*\*Pokémon \d+:', text)
        teams = []

        for i in range(1, min(len(pokemon_sections), 7)):  # Max 6 Pokemon
            section = pokemon_sections[i]
            lines = section.split('\n')
            
            # Extract Pokemon name
            name_match = re.search(r'\[([^\]]+)\]', lines[0])
            pokemon_name = name_match.group(1).strip() if name_match else 'Unknown Pokemon'
            
            # Extract other details
            ability_match = re.search(r'Ability:\s*(.+?)(?:\n|$)', section)
            item_match = re.search(r'Held Item:\s*(.+?)(?:\n|$)', section)
            tera_match = re.search(r'Tera Type:\s*(.+?)(?:\n|$)', section)
            moves_match = re.search(r'Moves:\s*(.+?)(?:\n|$)', section)
            ev_match = re.search(r'EV Spread:\s*(.+?)(?:\n|$)', section)
            nature_match = re.search(r'Nature:\s*(.+?)(?:\n|$)', section)
            ev_explanation_match = re.search(r'EV Explanation:\s*([\s\S]*?)(?:\*\*Pokémon|\*\*Conclusion|$)', section)

            team = {
                "pokemon": pokemon_name,
                "level": 50,
                "hp": {"current": 100, "max": 150},
                "status": "Healthy",
                "teraType": tera_match.group(1).strip() if tera_match else "Not specified",
                "types": [],  # Will be populated based on Pokemon name
                "item": item_match.group(1).strip() if item_match else "Not specified",
                "ability": ability_match.group(1).strip() if ability_match else "Not specified",
                "nature": nature_match.group(1).strip() if nature_match else "Not specified",
                "moves": moves_match.group(1).split('/').map(lambda move: {
                    "name": move.strip(),
                    "bp": 0,
                    "checked": True
                }) if moves_match else [],
                "stats": {
                    "hp": {"base": 100, "evs": 0, "ivs": 31, "final": 150},
                    "attack": {"base": 100, "evs": 0, "ivs": 31, "final": 100},
                    "defense": {"base": 100, "evs": 0, "ivs": 31, "final": 100},
                    "spAtk": {"base": 100, "evs": 0, "ivs": 31, "final": 100},
                    "spDef": {"base": 100, "evs": 0, "ivs": 31, "final": 100},
                    "speed": {"base": 100, "evs": 0, "ivs": 31, "final": 100}
                },
                "bst": 600,
                "remainingEvs": 508,
                "strategy": ""  # Will be set after validation
            }

            # Parse EV spread if available
            if ev_match:
                ev_values = ev_match.group(1).strip().split()
                if len(ev_values) >= 6:
                    team["stats"]["hp"]["evs"] = int(ev_values[0]) if ev_values[0].isdigit() else 0
                    team["stats"]["attack"]["evs"] = int(ev_values[1]) if ev_values[1].isdigit() else 0
                    team["stats"]["defense"]["evs"] = int(ev_values[2]) if ev_values[2].isdigit() else 0
                    team["stats"]["spAtk"]["evs"] = int(ev_values[3]) if ev_values[3].isdigit() else 0
                    team["stats"]["spDef"]["evs"] = int(ev_values[4]) if ev_values[4].isdigit() else 0
                    team["stats"]["speed"]["evs"] = int(ev_values[5]) if ev_values[5].isdigit() else 0
                    
                    # Calculate remaining EVs
                    total_evs = (team["stats"]["hp"]["evs"] + team["stats"]["attack"]["evs"] + 
                                team["stats"]["defense"]["evs"] + team["stats"]["spAtk"]["evs"] + 
                                team["stats"]["spDef"]["evs"] + team["stats"]["speed"]["evs"])
                    team["remainingEvs"] = 508 - total_evs

            # Validate and set EV explanation with fallback
            raw_explanation = ev_explanation_match.group(1).strip() if ev_explanation_match else "Not specified"
            if validate_ev_explanation(raw_explanation):
                team["strategy"] = raw_explanation
            else:
                team["strategy"] = get_fallback_ev_explanation()

            teams.append(team)

        # Extract mentioned Pokemon
        mentioned_pokemon = []
        pokemon_names = [team["pokemon"] for team in teams]
        mentioned_pokemon.extend(pokemon_names)

        return {
            "originalText": text,
            "translatedText": text,  # The response is already in English
            "summary": text,
            "teams": teams,
            "mentionedPokemon": mentioned_pokemon,
            "translationConfidence": 95,
            "processingTime": 2.3
        }
    except Exception as e:
        raise Exception(f'Failed to parse AI response: {str(e)}')

def validate_ev_spread(ev_values: List[int]) -> bool:
    """
    Validate EV spread values
    
    Args:
        ev_values (list): List of EV values [HP, Atk, Def, SpA, SpD, Spe]
    
    Returns:
        bool: True if valid EV spread
    """
    if len(ev_values) != 6:
        return False
    
    # Check if all values are multiples of 4 and within range
    for ev in ev_values:
        if not isinstance(ev, int) or ev < 0 or ev > 252 or ev % 4 != 0:
            return False
    
    # Check total EVs
    total_evs = sum(ev_values)
    if total_evs > 508:
        return False
    
    return True

def validate_ev_explanation(explanation: str) -> bool:
    """
    Validate if EV explanation contains meaningful insights
    
    Args:
        explanation (str): EV explanation text
    
    Returns:
        bool: True if explanation contains meaningful insights
    """
    if not explanation or explanation.strip() in ["Not specified", "Not specified in the article", ""]:
        return False
    
    # Check for meaningful indicators
    meaningful_indicators = [
        # Specific percentages and survival rates
        r'\d+(?:\.\d+)?%',  # Matches percentages like "93.6%" or "87%"
        # Speed benchmarks and numerical targets
        r'(?:outspeeds?|faster than|slower than|reaches?|survives?)\s+\w+',
        # Damage calculations
        r'(?:OHKO|2HKO|KO|damage|survives?)\s+\w+',
        # Specific stat numbers
        r'\b(?:1\d\d|2\d\d)\s+(?:speed|attack|defense|hp)\b',
        # EV reasoning keywords
        r'(?:bulk|offensive|defensive|speed control|priority|benchmark)',
        # Team synergy indicators
        r'(?:supports?|enables?|synergy|team|meta)',
        # Item interactions
        r'(?:with\s+\w+\s+(?:band|vest|sash|berry))',
        # Nature considerations
        r'(?:modest|timid|adamant|jolly|bold|impish)\s+nature',
    ]
    
    explanation_lower = explanation.lower()
    
    # Count meaningful indicators found
    meaningful_count = sum(1 for pattern in meaningful_indicators 
                         if re.search(pattern, explanation_lower, re.IGNORECASE))
    
    # Check for generic/useless phrases that indicate poor explanation
    generic_phrases = [
        "standard spread",
        "common distribution",
        "typical setup",
        "balanced stats",
        "general purpose",
        "default configuration",
        "basic allocation",
        "no specific reason",
        "arbitrary distribution"
    ]
    
    has_generic = any(phrase in explanation_lower for phrase in generic_phrases)
    
    # Consider meaningful if:
    # - Has at least 2 meaningful indicators AND no generic phrases, OR
    # - Has at least 3 meaningful indicators (even with some generic phrases), OR
    # - Explanation is reasonably long (>100 chars) with at least 1 meaningful indicator
    if (meaningful_count >= 2 and not has_generic) or \
       (meaningful_count >= 3) or \
       (len(explanation) > 100 and meaningful_count >= 1):
        return True
    
    return False

def get_fallback_ev_explanation() -> str:
    """
    Get fallback message for when meaningful EV insights cannot be generated
    
    Returns:
        str: Fallback explanation message
    """
    return ("I am unable to generate a meaningful insight about this Pokémon's EV spread "
            "based on the available information. The article may not contain sufficient "
            "detail about the strategic reasoning behind the EV distribution, or the "
            "explanation may require more context about specific matchups and calculations "
            "that aren't clearly provided in the source material.")

def clean_article_text(text: str) -> str:
    """
    Clean and normalize article text
    
    Args:
        text (str): Raw article text
    
    Returns:
        str: Cleaned text
    """
    # Remove special characters
    text = re.sub(r'[\u200b\xa0\u200e\u200f]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters
    text = re.sub(r'[^\w\s\-\.\,\!\?\:\;\(\)\[\]\{\}\/\@\#\$\%\&\*\+\=\|\~\`\'\"]', '', text)
    return text.strip()

def extract_team_from_text(text: str) -> Dict[str, Any]:
    """
    Extract team information from text using regex patterns
    
    Args:
        text (str): Article text
    
    Returns:
        dict: Extracted team information
    """
    # This is a simplified extraction - the main analysis is done by Gemini
    # but we can extract basic patterns here for validation
    
    pokemon_patterns = [
        r'(\w+)\s*\((\w+)\)',  # Pokemon (Type)
        r'(\w+)\s*@\s*(\w+)',  # Pokemon @ Item
        r'(\w+)\s*Ability:\s*(\w+)',  # Pokemon Ability: X
    ]
    
    extracted_info = {
        "pokemon_mentions": [],
        "items_mentioned": [],
        "abilities_mentioned": []
    }
    
    for pattern in pokemon_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match[0] not in extracted_info["pokemon_mentions"]:
                extracted_info["pokemon_mentions"].append(match[0])
    
    return extracted_info 