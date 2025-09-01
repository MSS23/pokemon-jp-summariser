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


def get_pokemon_sprite_url(pokemon_name: str, form: str = None) -> str:
    """
    Get Pokemon sprite URL from PokeAPI

    Args:
        pokemon_name: Name of the Pokemon
        form: Form variant (optional)

    Returns:
        URL to Pokemon sprite or placeholder if not found
    """
    try:
        # Clean and format Pokemon name
        name = pokemon_name.lower().replace(" ", "-").replace(".", "")

        # Handle common name variations
        name_mappings = {
            "nidoran-f": "nidoran-female",
            "nidoran-m": "nidoran-male",
            "mr-mime": "mr-mime",
            "mime-jr": "mime-jr",
            "ho-oh": "ho-oh",
        }
        name = name_mappings.get(name, name)

        # Add form if specified
        if form and form.lower() not in ["normal", "default"]:
            form_clean = form.lower().replace(" ", "-")
            name = f"{name}-{form_clean}"

        # Fetch from PokeAPI
        url = f"https://pokeapi.co/api/v2/pokemon/{name}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            # Try to get official artwork first, fall back to front default
            sprite_url = (
                data.get("sprites", {})
                .get("other", {})
                .get("official-artwork", {})
                .get("front_default")
            )

            if not sprite_url:
                sprite_url = data.get("sprites", {}).get("front_default")

            return sprite_url or "https://via.placeholder.com/150?text=Pokemon"
        else:
            return "https://via.placeholder.com/150?text=Pokemon"

    except Exception as e:
        st.warning(f"Could not fetch sprite for {pokemon_name}: {str(e)}")
        return "https://via.placeholder.com/150?text=Pokemon"


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

    # Try slash-separated format first (252/0/0/252/4/0)
    if "/" in ev_string:
        parts = ev_string.split("/")
        if len(parts) == 6:
            try:
                stats = ["HP", "Atk", "Def", "SpA", "SpD", "Spe"]
                for i, value in enumerate(parts):
                    ev_dict[stats[i]] = int(value.strip())
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
        evs = pokemon.get("evs", {})
        if evs:
            ev_parts = []
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
