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
    """Create hash for content caching"""
    return hashlib.sha256(content.encode()).hexdigest()


def ensure_cache_directory() -> str:
    """Ensure cache directory exists and return path"""
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


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
    Parse EV spread from various string formats

    Args:
        ev_string: EV spread in format like "252/0/0/252/4/0" or "H252 A0 B0 C252 D4 S0"

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

    # Try "Number StatName" format first (44 HP / 4 Def / 252 SpA / 28 SpD / 180 Spe)
    if any(stat in ev_string for stat in ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]):
        stat_name_patterns = {
            r"(\d+)\s*HP": "HP",
            r"(\d+)\s*Atk": "Atk",
            r"(\d+)\s*Def": "Def", 
            r"(\d+)\s*SpA": "SpA",
            r"(\d+)\s*SpD": "SpD",
            r"(\d+)\s*Spe": "Spe",
        }
        
        for pattern, stat in stat_name_patterns.items():
            matches = re.findall(pattern, ev_string, re.IGNORECASE)
            if matches:
                ev_dict[stat] = int(matches[0])
        
        # If we found any valid stats, return the result
        if any(v > 0 for v in ev_dict.values()):
            return validate_and_fix_evs(ev_dict)

    # Try slash-separated format (252/0/0/252/4/0)
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

    # Try format with stat labels (H252 A0 B0 C252 D4 S0)
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


def validate_and_fix_evs(ev_dict: Dict[str, int]) -> Tuple[Dict[str, int], str]:
    """
    Validate and fix EV spread

    Args:
        ev_dict: Dictionary of EV values

    Returns:
        Tuple of (validated EV dict, validation status)
    """
    total = sum(ev_dict.values())

    # Check if total is valid (should be <= 508 and each stat <= 252)
    for stat in ev_dict:
        if ev_dict[stat] > 252:
            ev_dict[stat] = 252

    if total > 508:
        # Scale down proportionally
        factor = 508 / total
        for stat in ev_dict:
            ev_dict[stat] = int(ev_dict[stat] * factor)
        return ev_dict, "adjusted_total"

    return ev_dict, "valid"


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
