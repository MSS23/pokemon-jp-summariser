"""
Utility functions for Pokemon VGC Analysis application
"""

import hashlib
import os
import re
import requests
from typing import Dict, List, Tuple
from urllib.parse import urlparse
import streamlit as st


def create_content_hash(content: str) -> str:
    """Create hash for content caching with validation version"""
    # Add validation version to cache key to invalidate old results
    validation_version = "v2.1.0"  # Updated after validation improvements
    versioned_content = f"{content}|validation_version:{validation_version}"
    return hashlib.sha256(versioned_content.encode()).hexdigest()



def get_pokemon_sprite_url(pokemon_name: str, form: str = None, use_cache: bool = True) -> str:
    """
    Enhanced Pokemon sprite fetching with comprehensive form handling and caching

    Args:
        pokemon_name: Name of the Pokemon
        form: Form variant (optional)
        use_cache: Whether to use cached sprite URLs

    Returns:
        URL to Pokemon sprite or placeholder if not found
    """
    # Simple in-memory cache for sprite URLs
    if not hasattr(get_pokemon_sprite_url, "_cache"):
        get_pokemon_sprite_url._cache = {}
    
    cache_key = f"{pokemon_name.lower()}_{form or 'default'}"
    
    if use_cache and cache_key in get_pokemon_sprite_url._cache:
        return get_pokemon_sprite_url._cache[cache_key]
    
    try:
        # Enhanced name cleaning and normalization
        sprite_url = _fetch_pokemon_sprite_with_fallbacks(pokemon_name, form)
        
        # Cache successful results
        if use_cache and sprite_url and "placeholder" not in sprite_url:
            get_pokemon_sprite_url._cache[cache_key] = sprite_url
            
        return sprite_url

    except Exception as e:
        # Less intrusive error handling - only log to console, don't show user warnings
        placeholder = _create_pokemon_placeholder(pokemon_name)
        if use_cache:
            get_pokemon_sprite_url._cache[cache_key] = placeholder
        return placeholder


def _fetch_pokemon_sprite_with_fallbacks(pokemon_name: str, form: str = None) -> str:
    """
    Attempt to fetch Pokemon sprite with multiple fallback strategies
    
    Args:
        pokemon_name: Name of the Pokemon
        form: Form variant (optional)
        
    Returns:
        URL to Pokemon sprite or placeholder
    """
    # Strategy 1: Try exact name with form handling
    sprite_url = _try_fetch_sprite(_normalize_pokemon_name(pokemon_name, form))
    if sprite_url:
        return sprite_url
    
    # Strategy 2: Try with common name fixes
    fixed_name = _apply_pokeapi_name_fixes(pokemon_name, form)
    if fixed_name != _normalize_pokemon_name(pokemon_name, form):
        sprite_url = _try_fetch_sprite(fixed_name)
        if sprite_url:
            return sprite_url
    
    # Strategy 3: Try without form for Pokemon with complex forms
    if form or "-" in pokemon_name:
        base_name = pokemon_name.split("-")[0].lower().replace(" ", "-")
        sprite_url = _try_fetch_sprite(base_name)
        if sprite_url:
            return sprite_url
    
    # Strategy 4: Try with alternative form naming
    if form:
        alt_forms = _get_alternative_form_names(pokemon_name, form)
        for alt_name in alt_forms:
            sprite_url = _try_fetch_sprite(alt_name)
            if sprite_url:
                return sprite_url
    
    # Strategy 5: Final fallback to placeholder
    return _create_pokemon_placeholder(pokemon_name)


def _normalize_pokemon_name(pokemon_name: str, form: str = None) -> str:
    """
    Normalize Pokemon name for PokeAPI compatibility
    
    Args:
        pokemon_name: Pokemon name to normalize
        form: Form variant
        
    Returns:
        Normalized Pokemon name
    """
    # Clean base name
    name = pokemon_name.lower().strip()
    name = name.replace(" ", "-").replace(".", "").replace("'", "").replace(":", "")
    
    # Handle form integration
    if form and form.lower() not in ["normal", "default", "not specified"]:
        form_clean = form.lower().replace(" ", "-").replace(".", "")
        
        # Don't add form if it's already in the name
        if form_clean not in name:
            name = f"{name}-{form_clean}"
    
    return name


def _apply_pokeapi_name_fixes(pokemon_name: str, form: str = None) -> str:
    """
    Apply PokeAPI-specific name fixes and mappings
    
    Args:
        pokemon_name: Original Pokemon name
        form: Form variant
        
    Returns:
        Fixed Pokemon name for PokeAPI
    """
    name_lower = pokemon_name.lower()
    
    # Comprehensive PokeAPI name mappings
    pokeapi_mappings = {
        # Nidoran variants
        "nidoran-f": "nidoran-female",
        "nidoran-m": "nidoran-male",
        "nidoran♀": "nidoran-female", 
        "nidoran♂": "nidoran-male",
        
        # Mr./Ms. Pokemon
        "mr-mime": "mr-mime",
        "mr-rime": "mr-rime", 
        "mime-jr": "mime-jr",
        
        # Legendary variants
        "ho-oh": "ho-oh",
        
        # Treasures of Ruin (common issues)
        "chien-pao": "chien-pao",
        "chi-yu": "chi-yu",
        "ting-lu": "ting-lu", 
        "wo-chien": "wo-chien",
        
        # Paradox Pokemon
        "flutter-mane": "flutter-mane",
        "iron-moth": "iron-moth",
        "sandy-shocks": "sandy-shocks",
        "roaring-moon": "roaring-moon",
        "brute-bonnet": "brute-bonnet",
        
        # Genie forms
        "landorus-therian": "landorus-therian",
        "thundurus-therian": "thundurus-therian", 
        "tornadus-therian": "tornadus-therian",
        "landorus-t": "landorus-therian",
        "thundurus-t": "thundurus-therian",
        "tornadus-t": "tornadus-therian",
        
        # Calyrex forms  
        "calyrex-shadow": "calyrex-shadow",
        "calyrex-ice": "calyrex-ice",
        "calyrex-shadow-rider": "calyrex-shadow",
        "calyrex-ice-rider": "calyrex-ice",
        
        # Urshifu forms
        "urshifu-rapid-strike": "urshifu-rapid-strike",
        "urshifu-single-strike": "urshifu-single-strike",
        "urshifu-rapid": "urshifu-rapid-strike",
        "urshifu-single": "urshifu-single-strike",
        
        # Rotom forms
        "rotom-heat": "rotom-heat",
        "rotom-wash": "rotom-wash",
        "rotom-frost": "rotom-frost", 
        "rotom-fan": "rotom-fan",
        "rotom-mow": "rotom-mow",
        "rotom-h": "rotom-heat",
        "rotom-w": "rotom-wash",
        "rotom-f": "rotom-frost",
        "rotom-s": "rotom-fan", 
        "rotom-c": "rotom-mow",
        
        # Regional forms
        "zapdos-galar": "zapdos-galar",
        "moltres-galar": "moltres-galar",
        "articuno-galar": "articuno-galar",
        "marowak-alola": "marowak-alola",
        "slowking-galar": "slowking-galar",
        "zoroark-hisui": "zoroark-hisui",
        "samurott-hisui": "samurott-hisui",
        "arcanine-hisui": "arcanine-hisui",
        
        # Indeedee forms
        "indeedee-female": "indeedee-female",
        "indeedee-male": "indeedee-male", 
        "indeedee-f": "indeedee-female",
        "indeedee-m": "indeedee-male",
        
        # Type: Null and Silvally
        "type-null": "type-null",
        "type:-null": "type-null",
        
        # Flabébé line
        "flabebe": "flabebe",
        "floette": "floette",
        "florges": "florges",
        
        # Tapu Pokemon
        "tapu-koko": "tapu-koko",
        "tapu-lele": "tapu-lele",
        "tapu-bulu": "tapu-bulu",
        "tapu-fini": "tapu-fini",
        
        # Common abbreviations
        "lando": "landorus-therian",
        "thundy": "thundurus-therian",
        "torn": "tornadus-therian",
    }
    
    # Check for direct mapping
    if name_lower in pokeapi_mappings:
        return pokeapi_mappings[name_lower]
    
    # Apply form-specific handling
    normalized_name = _normalize_pokemon_name(pokemon_name, form)
    if normalized_name in pokeapi_mappings:
        return pokeapi_mappings[normalized_name]
    
    return normalized_name


def _get_alternative_form_names(pokemon_name: str, form: str) -> list:
    """
    Get alternative form name combinations to try
    
    Args:
        pokemon_name: Base Pokemon name
        form: Form variant
        
    Returns:
        List of alternative names to try
    """
    alternatives = []
    base_name = pokemon_name.lower().split("-")[0]
    form_lower = form.lower() if form else ""
    
    # Try different form combinations
    form_alternatives = {
        "therian": ["therian", "t"],
        "shadow": ["shadow", "shadow-rider"],
        "ice": ["ice", "ice-rider"],
        "rapid": ["rapid-strike", "rapid"],
        "single": ["single-strike", "single"],
        "galar": ["galar", "galarian"],
        "alola": ["alola", "alolan"], 
        "hisui": ["hisui", "hisuian"],
    }
    
    for key, variants in form_alternatives.items():
        if key in form_lower:
            for variant in variants:
                alternatives.append(f"{base_name}-{variant}")
    
    return alternatives


def _try_fetch_sprite(pokemon_name: str) -> str:
    """
    Try to fetch sprite from PokeAPI for a specific name
    
    Args:
        pokemon_name: Normalized Pokemon name
        
    Returns:
        Sprite URL if successful, None otherwise
    """
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            
            # Priority order for sprite sources
            sprite_sources = [
                # Official artwork (highest quality)
                lambda d: d.get("sprites", {}).get("other", {}).get("official-artwork", {}).get("front_default"),
                # Dream World artwork
                lambda d: d.get("sprites", {}).get("other", {}).get("dream_world", {}).get("front_default"),
                # Home artwork
                lambda d: d.get("sprites", {}).get("other", {}).get("home", {}).get("front_default"),
                # Standard front sprite
                lambda d: d.get("sprites", {}).get("front_default"),
            ]
            
            for get_sprite in sprite_sources:
                sprite_url = get_sprite(data)
                if sprite_url:
                    return sprite_url
                    
    except Exception:
        pass
    
    return None


def _create_pokemon_placeholder(pokemon_name: str) -> str:
    """
    Create a styled placeholder image URL for Pokemon
    
    Args:
        pokemon_name: Pokemon name for placeholder
        
    Returns:
        Placeholder image URL
    """
    # Create abbreviated name for placeholder (first 3-4 chars)
    abbrev = pokemon_name[:4].upper() if len(pokemon_name) >= 4 else pokemon_name.upper()
    
    # Color-coded placeholders based on first letter
    color_map = {
        'A': 'ff6b6b', 'B': '4ecdc4', 'C': '45b7d1', 'D': '96ceb4', 'E': 'feca57',
        'F': 'ff9ff3', 'G': '54a0ff', 'H': '5f27cd', 'I': '00d2d3', 'J': 'ff9f43',
        'K': 'ee5253', 'L': '0abde3', 'M': '10ac84', 'N': 'f368e0', 'O': 'feca57',
        'P': 'ff6348', 'Q': '2f3542', 'R': 'ff4757', 'S': '2d3436', 'T': '74b9ff',
        'U': 'a29bfe', 'V': '6c5ce7', 'W': 'fd79a8', 'X': 'fdcb6e', 'Y': 'e17055',
        'Z': '81ecec'
    }
    
    bg_color = color_map.get(abbrev[0], '95a5a6')
    text_color = 'ffffff'
    
    return f"https://via.placeholder.com/180x180/{bg_color}/{text_color}?text={abbrev}"


def safe_parse_ev_spread(ev_string: str) -> Tuple[Dict[str, int], str]:
    """
    Safely parse EV spread from string format

    Args:
        ev_string: EV spread string (e.g., "252/0/0/252/4/0")

    Returns:
        Tuple of (EV dict, source indicator)
    """
    try:
        return parse_ev_spread(ev_string)
    except Exception:
        # Return default spread if parsing fails
        return {
            "HP": 0,
            "Atk": 0,
            "Def": 0,
            "SpA": 0,
            "SpD": 0,
            "Spe": 0,
        }, "default_error"


def parse_ev_spread(ev_string: str) -> Tuple[Dict[str, int], str]:
    """
    Parse EV spread from various string formats including calculated stat formats

    Args:
        ev_string: EV spread in format like "252/0/0/252/4/0" or "H252 A0 B0 C252 D4 S0" or "H181(148)-A×↓-B131(124)"

    Returns:
        Tuple of (EV dictionary, source type)
    """
    if not ev_string or ev_string.strip() == "":
        return {
            "HP": 0,
            "Atk": 0,
            "Def": 0,
            "SpA": 0,
            "SpD": 0,
            "Spe": 0,
        }, "default_empty"

    ev_dict = {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0}

    # PRIORITY 1: Try Japanese grid format (most common in note.com team cards)
    japanese_grid_result = parse_japanese_grid_format(ev_string)
    if japanese_grid_result[1] != "default_empty":
        return japanese_grid_result

    # PRIORITY 2: Try calculated stat format (H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116))
    calculated_format_result = parse_calculated_stat_format(ev_string)
    if calculated_format_result[1] != "default_empty":
        return calculated_format_result

    # PRIORITY 3: Try "Number StatName" format (44 HP / 4 Def / 252 SpA / 28 SpD / 180 Spe)
    # Enhanced with Japanese stat names
    stat_name_indicators = [
        "HP", "Atk", "Def", "SpA", "SpD", "Spe", 
        "ＨＰ", "こうげき", "ぼうぎょ", "とくこう", "とくぼう", "すばやさ"
    ]
    
    if any(stat in ev_string for stat in stat_name_indicators):
        stat_name_patterns = {
            r"(\d+)\s*(?:HP|ＨＰ)": "HP",
            r"(\d+)\s*(?:Atk|こうげき|攻撃)": "Atk",
            r"(\d+)\s*(?:Def|ぼうぎょ|防御)": "Def", 
            r"(\d+)\s*(?:SpA|とくこう|特攻|特殊攻撃)": "SpA",
            r"(\d+)\s*(?:SpD|とくぼう|特防|特殊防御)": "SpD",
            r"(\d+)\s*(?:Spe|すばやさ|素早さ|Speed)": "Spe",
        }
        
        for pattern, stat in stat_name_patterns.items():
            matches = re.findall(pattern, ev_string, re.IGNORECASE | re.UNICODE)
            if matches:
                try:
                    value = int(matches[0])
                    if 0 <= value <= 252:
                        ev_dict[stat] = value
                except ValueError:
                    continue
        
        # If we found any valid stats, return the result
        if any(v > 0 for v in ev_dict.values()):
            return validate_and_fix_evs(ev_dict)

    # PRIORITY 4: Try slash-separated format (252/0/0/252/4/0)
    if "/" in ev_string:
        parts = ev_string.split("/")
        if len(parts) == 6:
            try:
                stats = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                for i, value in enumerate(parts):
                    # Clean the value - remove any non-numeric characters except leading/trailing spaces
                    clean_value = re.sub(r'[^\d]', '', value.strip())
                    if clean_value:
                        ev_dict[stats[i]] = int(clean_value)
                return validate_and_fix_evs(ev_dict)
            except ValueError:
                pass

    # PRIORITY 5: Try format with stat labels (H252 A0 B0 C252 D4 S0)
    stat_patterns = {
        r"H(\d+)": "HP",
        r"A(\d+)": "Atk",
        r"B(\d+)": "Def",
        r"C(\d+)": "SpA",
        r"D(\d+)": "SpD",
        r"S(\d+)": "Spe",
    }

    for pattern, stat in stat_patterns.items():
        matches = re.findall(pattern, ev_string, re.IGNORECASE)
        if matches:
            ev_dict[stat] = int(matches[0])

    return validate_and_fix_evs(ev_dict)


def parse_calculated_stat_format(ev_string: str) -> Tuple[Dict[str, int], str]:
    """
    ULTRA-ENHANCED calculated stat format parser for note.com and Japanese VGC articles
    
    Supported Formats:
    - H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116) (note.com standard)
    - H(148)-A×-B(124)-C(116)-D(4)-S(116) (compact)
    - H148↑-A0×-B124-C116↑-D4-S116 (without parentheses)
    - H148 A0 B124 C116 D4 S116 (space separated)
    
    Args:
        ev_string: EV string in calculated stat format
        
    Returns:
        Tuple of (EV dictionary, source type)
    """
    if not ev_string or ev_string.strip() == "":
        return {
            "HP": 0,
            "Atk": 0,
            "Def": 0,
            "SpA": 0,
            "SpD": 0,
            "Spe": 0,
        }, "default_empty"

    ev_dict = {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0}
    nature_info = {"boosts": [], "reductions": []}
    
    # ULTRA-ENHANCED regex patterns for all calculated stat variations
    calc_patterns = [
        # PRIORITY 1: Note.com standard format with parentheses
        r'([HABCDS])(?:\d{2,3})?\((\d{1,3})\)([↑↓×]?)',  # H181(148)↑
        
        # PRIORITY 2: Compact format with parentheses
        r'([HABCDS])\((\d{1,3})\)([↑↓×]?)',  # H(148)×
        
        # PRIORITY 3: Without parentheses but with nature symbols
        r'([HABCDS])(\d{1,3})([↑↓×]+)',  # H148↑
        
        # PRIORITY 4: Simple letter + number format
        r'([HABCDS])(\d{1,3})(?:\s|$|[^0-9])',  # H148 (followed by space or end)
        
        # PRIORITY 5: Space-separated format
        r'([HABCDS])\s*(\d{1,3})(?:\s+|$)',  # H 148 or H148 
    ]
    
    matches = []
    best_pattern_matches = None
    best_match_count = 0
    
    # Try all patterns and use the one with most matches
    for pattern in calc_patterns:
        pattern_matches = re.findall(pattern, ev_string, re.UNICODE | re.IGNORECASE)
        if len(pattern_matches) > best_match_count:
            best_match_count = len(pattern_matches)
            best_pattern_matches = pattern_matches
    
    matches = best_pattern_matches or []
    
    # If no matches with strict patterns, try ultra-flexible patterns
    if not matches:
        # Try to find any H/A/B/C/D/S followed by numbers
        ultra_flexible_pattern = r'([HABCDS])[^\d]*?(\d{1,3})'
        matches = re.findall(ultra_flexible_pattern, ev_string, re.UNICODE | re.IGNORECASE)
    
    if matches:
        stat_mapping = {
            'H': 'HP',
            'A': 'Atk', 
            'B': 'Def',
            'C': 'SpA',
            'D': 'SpD',
            'S': 'Spe'
        }
        
        found_stats = 0
        total_ev_value = 0
        
        for match_data in matches:
            if len(match_data) >= 2:
                stat_letter = match_data[0].upper()
                ev_value_str = match_data[1]
                nature_symbol = match_data[2] if len(match_data) > 2 else ''
                
                if stat_letter in stat_mapping:
                    try:
                        ev_int = int(ev_value_str)
                        
                        # Ultra-enhanced validation
                        if 0 <= ev_int <= 252:
                            ev_dict[stat_mapping[stat_letter]] = ev_int
                            found_stats += 1
                            total_ev_value += ev_int
                            
                            # Process nature symbols
                            if '↑' in nature_symbol:
                                nature_info["boosts"].append(stat_mapping[stat_letter])
                            elif '↓' in nature_symbol:
                                nature_info["reductions"].append(stat_mapping[stat_letter])
                        elif ev_int > 252:
                            # This might be a calculated stat value, try to infer EV
                            # Common calculated stat ranges for level 50 Pokemon
                            if 100 <= ev_int <= 200:
                                # Rough estimation: calculated stat to EV
                                estimated_ev = min(252, max(0, (ev_int - 80) * 8))
                                if estimated_ev % 4 == 0:  # Prefer multiples of 4
                                    ev_dict[stat_mapping[stat_letter]] = estimated_ev
                                    found_stats += 1
                                    total_ev_value += estimated_ev
                                    
                    except ValueError:
                        continue
        
        # Enhanced success criteria
        success_criteria = [
            found_stats >= 4,  # Found at least 4 stats
            found_stats >= 6 and total_ev_value <= 508,  # All stats and valid total
            found_stats >= 3 and total_ev_value >= 400,  # Reasonable investment pattern
        ]
        
        if any(success_criteria):
            # Additional validation for calculated stat format
            validated_evs, status = validate_and_fix_evs(ev_dict)
            confidence = "high" if found_stats >= 5 else "medium" if found_stats >= 4 else "low"
            return validated_evs, f"calculated_stat_{confidence}_{status}"
    
    # No matches found
    return {
        "HP": 0,
        "Atk": 0,
        "Def": 0,
        "SpA": 0,
        "SpD": 0,
        "Spe": 0,
    }, "default_empty"


def parse_japanese_grid_format(text: str) -> Tuple[Dict[str, int], str]:
    """
    Parse Japanese grid/table format commonly used in note.com team cards
    
    Format examples:
    ＨＰ: 252    こうげき: 0     ぼうぎょ: 4
    とくこう: 252  とくぼう: 0   すばやさ: 0
    
    Args:
        text: Text containing Japanese EV spread
        
    Returns:
        Tuple of (EV dictionary, source type)
    """
    ev_dict = {"HP": 0, "Atk": 0, "Def": 0, "SpA": 0, "SpD": 0, "Spe": 0}
    
    # Japanese stat name mappings (comprehensive)
    japanese_stat_patterns = {
        'HP': [r'(?:ＨＰ|HP|H|ヒットポイント|体力)[:\s]*(\d{1,3})', r'HP[:\s]*(\d{1,3})'],
        'Atk': [r'(?:こうげき|攻撃|A|アタック|物理攻撃)[:\s]*(\d{1,3})', r'(?:Attack|ATK)[:\s]*(\d{1,3})'],
        'Def': [r'(?:ぼうぎょ|防御|B|ディフェンス|物理防御)[:\s]*(\d{1,3})', r'(?:Defense|DEF)[:\s]*(\d{1,3})'],
        'SpA': [r'(?:とくこう|特攻|特殊攻撃|C|とくしゅこうげき)[:\s]*(\d{1,3})', r'(?:Sp\.?\s*A|Special\s*Attack)[:\s]*(\d{1,3})'],
        'SpD': [r'(?:とくぼう|特防|特殊防御|D|とくしゅぼうぎょ)[:\s]*(\d{1,3})', r'(?:Sp\.?\s*D|Special\s*Defense)[:\s]*(\d{1,3})'],
        'Spe': [r'(?:すばやさ|素早さ|素早|S|スピード|速さ)[:\s]*(\d{1,3})', r'(?:Speed|SPE)[:\s]*(\d{1,3})']
    }
    
    found_stats = 0
    
    for stat, patterns in japanese_stat_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.UNICODE)
            for match in matches:
                try:
                    value = int(match.group(1))
                    if 0 <= value <= 252:
                        ev_dict[stat] = value
                        found_stats += 1
                        break  # Take first valid match for this stat
                except (ValueError, IndexError):
                    continue
    
    if found_stats >= 4:  # Need at least 4 stats for success
        validated_evs, status = validate_and_fix_evs(ev_dict)
        confidence = "high" if found_stats >= 6 else "medium" if found_stats >= 5 else "low"
        return validated_evs, f"japanese_grid_{confidence}_{status}"
    
    return {
        "HP": 0,
        "Atk": 0,
        "Def": 0,
        "SpA": 0,
        "SpD": 0,
        "Spe": 0,
    }, "default_empty"


def validate_and_fix_evs(ev_dict: Dict[str, int]) -> Tuple[Dict[str, int], str]:
    """
    Enhanced EV spread validation with confidence scoring and competitive analysis

    Args:
        ev_dict: Dictionary of EV values

    Returns:
        Tuple of (validated EV dict, validation status with confidence)
    """
    original_total = sum(ev_dict.values())
    validation_issues = []
    confidence_score = 100  # Start with perfect confidence

    # PHASE 1: Basic value validation
    for stat in ev_dict:
        # Check for negative values
        if ev_dict[stat] < 0:
            ev_dict[stat] = 0
            validation_issues.append(f"negative_{stat}")
            confidence_score -= 15

        # Check for values too high (> 252)
        if ev_dict[stat] > 252:
            ev_dict[stat] = 252
            validation_issues.append(f"capped_{stat}")
            confidence_score -= 10

    # PHASE 2: Total EV validation
    current_total = sum(ev_dict.values())
    
    if original_total > 508:
        if original_total > 600:
            # Likely these are actual stats, not EVs
            validation_issues.append("likely_stats_not_evs")
            confidence_score -= 50
        
        # Scale down proportionally but preserve investment patterns
        factor = 508 / original_total
        for stat in ev_dict:
            if ev_dict[stat] > 0:  # Only scale non-zero values
                ev_dict[stat] = max(4, int(ev_dict[stat] * factor))
        
        validation_issues.append("scaled_total")
        confidence_score -= 20
        
    elif current_total < 100:
        # Very low total EVs - might be incomplete data
        validation_issues.append("low_total")
        confidence_score -= 25
    
    # PHASE 3: EV multiple validation (should be multiples of 4)
    for stat, value in ev_dict.items():
        if value > 0 and value % 4 != 0:
            # Round to nearest multiple of 4
            ev_dict[stat] = (value // 4) * 4 + (4 if value % 4 >= 2 else 0)
            validation_issues.append(f"rounded_{stat}")
            confidence_score -= 5

    # PHASE 4: Competitive pattern analysis
    final_total = sum(ev_dict.values())
    competitive_patterns = analyze_competitive_ev_pattern(ev_dict, final_total)
    
    if competitive_patterns["is_common_pattern"]:
        confidence_score += 10
    if competitive_patterns["has_max_investments"]:
        confidence_score += 5
    if competitive_patterns["reasonable_distribution"]:
        confidence_score += 5
    else:
        confidence_score -= 10

    # PHASE 5: Determine validation status
    confidence_level = "high" if confidence_score >= 80 else "medium" if confidence_score >= 50 else "low"
    
    if not validation_issues:
        status = f"valid_{confidence_level}"
    elif len(validation_issues) == 1 and validation_issues[0].startswith("rounded"):
        status = f"minor_fixes_{confidence_level}"
    elif any(issue in validation_issues for issue in ["likely_stats_not_evs", "low_total"]):
        status = f"questionable_{confidence_level}"
    else:
        status = f"adjusted_{confidence_level}"

    return ev_dict, status


def analyze_competitive_ev_pattern(ev_dict: Dict[str, int], total: int) -> Dict[str, bool]:
    """
    Analyze EV spread for competitive patterns
    
    Args:
        ev_dict: Dictionary of EV values
        total: Total EV investment
        
    Returns:
        Analysis of competitive patterns
    """
    analysis = {
        "is_common_pattern": False,
        "has_max_investments": False,
        "reasonable_distribution": False
    }
    
    ev_values = list(ev_dict.values())
    non_zero_values = [v for v in ev_values if v > 0]
    max_investments = sum(1 for v in ev_values if v >= 252)
    
    # Check for max investments (common in competitive play)
    analysis["has_max_investments"] = max_investments >= 1
    
    # Check for common competitive patterns
    common_totals = [508, 504, 500, 496, 492]  # Common total investments
    if total in common_totals and len(non_zero_values) >= 2:
        analysis["is_common_pattern"] = True
    
    # Check for reasonable distribution
    if len(non_zero_values) >= 2 and len(non_zero_values) <= 4:
        # Most competitive builds invest in 2-4 stats
        analysis["reasonable_distribution"] = True
    
    # Special patterns
    if max_investments == 2 and total >= 500:  # 252/252/4 style builds
        analysis["is_common_pattern"] = True
        
    if max_investments == 1 and 200 <= total <= 400:  # Bulky builds
        analysis["reasonable_distribution"] = True
    
    return analysis


def is_calculated_stats(numbers: List[int]) -> bool:
    """
    Check if numbers look like calculated stats rather than EVs

    Args:
        numbers: List of 6 numbers

    Returns:
        True if they look like calculated stats
    """
    if len(numbers) != 6:
        return False

    # Calculated stats are typically in range 50-200+ for level 50
    # EVs are 0-252 and often include many zeros
    zero_count = numbers.count(0)
    high_values = sum(1 for n in numbers if n > 252)
    moderate_values = sum(1 for n in numbers if 100 <= n <= 252)

    # If more than 2 values are > 252, likely calculated stats
    if high_values > 2:
        return True

    # If no zeros and most values are moderate/high, likely calculated stats
    if zero_count == 0 and moderate_values >= 4:
        return True

    return False


def get_stat_icon(stat: str) -> str:
    """Get emoji icon for stat"""
    icons = {"HP": "❤️", "Atk": "⚔️", "Def": "🛡️", "SpA": "✨", "SpD": "💫", "Spe": "💨"}
    return icons.get(stat, "📊")


def get_pokemon_type_class(tera_type: str) -> str:
    """Get CSS class for Pokemon type"""
    type_classes = {
        "Normal": "type-normal",
        "Fire": "type-fire",
        "Water": "type-water",
        "Electric": "type-electric",
        "Grass": "type-grass",
        "Ice": "type-ice",
        "Fighting": "type-fighting",
        "Poison": "type-poison",
        "Ground": "type-ground",
        "Flying": "type-flying",
        "Psychic": "type-psychic",
        "Bug": "type-bug",
        "Rock": "type-rock",
        "Ghost": "type-ghost",
        "Dragon": "type-dragon",
        "Dark": "type-dark",
        "Steel": "type-steel",
        "Fairy": "type-fairy",
    }
    return type_classes.get(tera_type, "type-normal")


def get_role_class(role: str) -> str:
    """Get CSS class for Pokemon role"""
    role_classes = {
        "Physical Attacker": "role-physical",
        "Special Attacker": "role-special",
        "Tank": "role-tank",
        "Support": "role-support",
        "Speed Control": "role-speed",
        "Trick Room": "role-trick-room",
    }

    for key, class_name in role_classes.items():
        if key.lower() in role.lower():
            return class_name

    return "role-default"


def create_pokepaste(pokemon_team: List[Dict], team_name: str = "VGC Team") -> str:
    """
    Create pokepaste format string from team data

    Args:
        pokemon_team: List of Pokemon data dictionaries
        team_name: Name for the team

    Returns:
        Pokepaste formatted string
    """
    pokepaste_lines = [f"=== [{team_name}] ===", ""]

    for pokemon in pokemon_team:
        lines = []

        # Pokemon name and item
        name = pokemon.get("name", "Unknown")
        item = pokemon.get("held_item", "")
        if item:
            lines.append(f"{name} @ {item}")
        else:
            lines.append(name)

        # Ability
        ability = pokemon.get("ability", "")
        if ability:
            lines.append(f"Ability: {ability}")

        # Tera Type
        tera_type = pokemon.get("tera_type", "")
        if tera_type:
            lines.append(f"Tera Type: {tera_type}")

        # EVs
        evs = pokemon.get("evs", "")
        if evs and evs != "Not specified":
            ev_parts = []
            
            # Handle EVs whether they're stored as string or dictionary
            if isinstance(evs, str):
                # Parse EV string format like "252/0/0/252/4/0"
                try:
                    ev_dict, _ = safe_parse_ev_spread(evs)
                    for stat, value in ev_dict.items():
                        if value > 0:
                            ev_parts.append(f"{value} {stat}")
                except:
                    # If parsing fails, try to extract numbers directly
                    if "/" in evs:
                        try:
                            ev_values = [int(x.strip()) for x in evs.split("/")]
                            if len(ev_values) == 6:
                                stats = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                                for stat, value in zip(stats, ev_values):
                                    if value > 0:
                                        ev_parts.append(f"{value} {stat}")
                        except ValueError:
                            pass
            elif isinstance(evs, dict):
                # Handle dictionary format
                for stat, value in evs.items():
                    if value > 0:
                        ev_parts.append(f"{value} {stat}")
                        
            if ev_parts:
                lines.append(f"EVs: {' / '.join(ev_parts)}")

        # Nature
        nature = pokemon.get("nature", "")
        if nature:
            lines.append(f"{nature} Nature")

        # Moves
        moves = pokemon.get("moves", [])
        for move in moves[:4]:  # Max 4 moves
            if move:
                lines.append(f"- {move}")

        pokepaste_lines.extend(lines)
        pokepaste_lines.append("")  # Empty line between Pokemon

    return "\n".join(pokepaste_lines)


def format_moves_html(moves: List[str]) -> str:
    """Format moves list as HTML"""
    if not moves:
        return "<em>No moves specified</em>"

    formatted_moves = []
    for move in moves[:4]:  # Limit to 4 moves
        if move:
            formatted_moves.append(f'<span class="move-name">{move}</span>')

    return " • ".join(formatted_moves)


def validate_url(url: str) -> bool:
    """
    Validate if URL is properly formatted

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
