"""
Shared utilities for Pokemon VGC Team Analyzer
Common functions used across different modules
"""

import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import Tuple, List
import streamlit as st

def strip_html_tags(text: str) -> str:
    """
    Strip HTML tags from text content
    
    Args:
        text (str): Text content that may contain HTML tags
        
    Returns:
        str: Clean text without HTML tags
    """
    try:
        # Use BeautifulSoup to parse and extract text
        soup = BeautifulSoup(text, 'html.parser')
        # Get text content, removing all HTML tags
        clean_text = soup.get_text()
        
        # Additional cleaning: remove extra whitespace
        lines = (line.strip() for line in clean_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = ' '.join(chunk for chunk in chunks if chunk)
        
        return clean_text
    except Exception as e:
        # If BeautifulSoup fails, fall back to regex
        import re
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text

def fetch_article_text_and_images(url: str) -> Tuple[str, List[str]]:
    """
    Fetch article content and extract images from a URL
    
    Args:
        url (str): Article URL to fetch
        
    Returns:
        tuple: (article_text, image_urls)
    """
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract images
        image_urls = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Convert relative URLs to absolute URLs
                absolute_url = urljoin(url, src)
                image_urls.append(absolute_url)
        
        # Filter for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        filtered_images = [
            img_url for img_url in image_urls 
            if any(ext in img_url.lower() for ext in image_extensions)
        ]
        
        return text, filtered_images
        
    except Exception as e:
        st.error(f"Failed to fetch article content: {str(e)}")
        return "", []

def extract_pokemon_names(summary: str) -> List[str]:
    """
    Extract Pokemon names from the summary text
    
    Args:
        summary (str): The summary text containing Pokemon information
        
    Returns:
        list: List of Pokemon names found in the summary
    """
    try:
        # Common Pokemon names pattern
        pokemon_pattern = r'Pokémon\s+\d+:\s*([A-Za-z\-\s]+?)(?:\n|$|\(|\[)'
        
        # Find all Pokemon names
        matches = re.findall(pokemon_pattern, summary, re.IGNORECASE)
        
        # Clean up the names
        pokemon_names = []
        for match in matches:
            name = match.strip()
            if name and len(name) > 1:  # Filter out empty or single character names
                pokemon_names.append(name)
        
        # If no Pokemon found with the pattern, try alternative patterns
        if not pokemon_names:
            # Look for Pokemon names in various formats
            alt_patterns = [
                r'([A-Z][a-z]+(?:\-[A-Z][a-z]+)*)',  # Capitalized words with possible hyphens
                r'([A-Za-z]+(?:\s+[A-Za-z]+)*)',     # General word patterns
            ]
            
            for pattern in alt_patterns:
                matches = re.findall(pattern, summary)
                for match in matches:
                    name = match.strip()
                    if name and len(name) > 2 and name.lower() not in ['the', 'and', 'with', 'for', 'from', 'this', 'that']:
                        pokemon_names.append(name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_names = []
        for name in pokemon_names:
            if name not in seen:
                seen.add(name)
                unique_names.append(name)
        
        return unique_names[:10]  # Limit to first 10 Pokemon names
        
    except Exception as e:
        st.error(f"Failed to extract Pokemon names: {str(e)}")
        return []

def extract_moves_from_text(text: str, pokemon_name: str = None) -> list:
    """
    Comprehensive move extraction from text with multiple fallback methods.
    Returns a list of detected moves.
    """
    if not text:
        return []
    
    text_lower = text.lower()
    moves = []
    
    # Method 1: Look for explicit "moves:" patterns with improved regex
    moves_patterns = [
        # Standard format: Moves: move1, move2, move3, move4
        r'moves?[:\s]+([^:\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
        r'moveset[:\s]+([^:\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
        # Dash format: - Moves: move1, move2, move3, move4
        r'- moves?[:\s]+([^:\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
        r'• moves?[:\s]+([^:\n]+?)(?=\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation))',
        # Newline format: Moves: move1, move2, move3, move4\n
        r'moves?[:\s]*([^:\n]+?)(?=\n\s*(?:[A-Z][a-z]+:|$))',
        r'moves?[:\s]*([^:\n]+?)(?=\n\s*-\s*[A-Z][a-z]+:|$)',
        # End of section format
        r'(?:moves?|moveset)[:\s]*([^:\n]+?)(?=\n\s*(?:[A-Z][a-z]+:|$))',
        r'(?:moves?|moveset)[:\s]*([^:\n]+?)(?=\n\s*-\s*[A-Z][a-z]+:|$)',
        # End of text format
        r'moves?[:\s]*([^:\n]+?)(?=\Z)',
        r'moves?[:\s]*([^:\n]+?)(?=\n\s*\n|\Z)',
        # More flexible patterns for various formats
        r'moves?[:\s]*([^:\n]+?)(?=\s*(?:tera|ev|nature|ability|item))',
        r'moves?[:\s]*([^:\n]+?)(?=\s*$)',
    ]
    
    for pattern in moves_patterns:
        match = re.search(pattern, text_lower)
        if match:
            moves_text = match.group(1).strip()
            moves = parse_moves_text(moves_text)
            if moves and len(moves) >= 4:
                print(f"DEBUG: Found moves with pattern '{pattern[:50]}...': {moves}")
                return moves
    
    # Method 2: Look for moves in parentheses or brackets
    bracket_patterns = [
        r'\(([^)]+)\)(?=.*?(?:ability|item|nature|tera|ev))',
        r'\[([^\]]+)\](?=.*?(?:ability|item|nature|tera|ev))',
    ]
    
    for pattern in bracket_patterns:
        match = re.search(pattern, text)
        if match:
            bracket_text = match.group(1).strip()
            moves = parse_moves_text(bracket_text)
            if moves and len(moves) >= 4:
                print(f"DEBUG: Found moves in brackets: {moves}")
                return moves
    
    # Method 3: Look for specific move patterns in the text with better regex
    specific_move_patterns = [
        # Comma-separated format: move1, move2, move3, move4
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Slash-separated format: move1 / move2 / move3 / move4
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\/\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\/\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\/\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Japanese bullet-separated format: move1・move2・move3・move4
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*・\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*・\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*・\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Space-separated format: move1 move2 move3 move4
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in specific_move_patterns:
        match = re.search(pattern, text)
        if match:
            moves = [move.strip() for move in match.groups() if move.strip()]
            if len(moves) == 4:
                print(f"DEBUG: Found moves with specific pattern: {moves}")
                return moves
    
    # Method 4: Look for 4 consecutive capitalized words that could be moves
    # This is more aggressive but can catch moves in various formats
    potential_moves = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text)
    
    # Filter potential moves based on common move characteristics and exclude non-move words
    non_move_words = {
        'ability', 'item', 'nature', 'tera', 'ev', 'spread', 'explanation', 'pokemon', 'team', 'member',
        'snow', 'warning', 'rough', 'skin', 'life', 'orb', 'clear', 'amulet', 'timid', 'jolly', 'ghost', 'fire',
        'hp', 'atk', 'def', 'spa', 'spd', 'spe', 'alolan', 'ninetales', 'garchomp', 'iron', 'valiant', 'zamazenta',
        'calyrex', 'shadow', 'rider', 'ice', 'chien', 'pao', 'chi', 'yu', 'amoonguss', 'dragonite', 'jugulis', 'crown',
        'miraidon', 'koraidon', 'urshifu', 'rillaboom', 'volcarona', 'held', 'type', 'effort', 'values'
    }
    
    filtered_moves = []
    for move in potential_moves:
        move_lower = move.lower()
        # Check if it's not a non-move word and has reasonable length
        if (move_lower not in non_move_words and 
            len(move) > 2 and 
            not move_lower.startswith('ev') and
            not move_lower.startswith('hp') and
            not move_lower.startswith('atk') and
            not move_lower.startswith('def') and
            not move_lower.startswith('spa') and
            not move_lower.startswith('spd') and
            not move_lower.startswith('spe')):
            filtered_moves.append(move)
    
    # Take first 4 unique moves
    unique_moves = []
    seen = set()
    for move in filtered_moves:
        if move not in seen and len(unique_moves) < 4:
            unique_moves.append(move)
            seen.add(move)
    
    if len(unique_moves) >= 4:
        print(f"DEBUG: Found moves with fallback method: {unique_moves}")
        return unique_moves
    
    return []

def parse_moves_text(moves_text: str) -> list:
    """
    Parse moves text into a list of individual moves.
    Handles various separators and formats.
    """
    if not moves_text:
        return []
    
    # Clean up the text
    moves_text = re.sub(r'\s*-\s*(?:ability|held item|item|nature|tera|ev spread|ev explanation).*', '', moves_text)
    moves_text = re.sub(r'\n.*', '', moves_text)
    
    # Handle different separators with improved logic
    if '/' in moves_text:
        moves_list = [move.strip().title() for move in moves_text.split('/')]
    elif ',' in moves_text:
        # Handle comma-separated moves more carefully
        moves_list = []
        for move in moves_text.split(','):
            move = move.strip()
            if move and len(move) > 1:
                # Clean up the move name
                move = re.sub(r'^\s*[-•]\s*', '', move)
                move = re.sub(r'\s+', ' ', move)
                move = move.strip()
                if move:
                    moves_list.append(move.title())
    elif '・' in moves_text:  # Japanese bullet point
        moves_list = [move.strip().title() for move in moves_text.split('・')]
    elif '、' in moves_text:  # Japanese comma
        moves_list = [move.strip().title() for move in moves_text.split('、')]
    elif ' ' in moves_text and len(moves_text.split()) <= 4:
        # Handle space-separated moves by recognizing common move patterns
        words = moves_text.split()
        moves_list = []
        
        # Common multi-word moves that should be kept together
        multi_word_moves = {
            'close combat', 'spirit break', 'aurora veil', 'fake out', 'u-turn', 'will-o-wisp',
            'stealth rock', 'dragon dance', 'swords dance', 'nasty plot', 'calm mind', 'bulk up',
            'stone edge', 'dragon claw', 'fire fang', 'ice fang', 'thunder fang', 'poison jab',
            'iron head', 'quick guard', 'wide guard', 'crafty shield', 'mat block', 'spiky shield',
            'king\'s shield', 'baneful bunker', 'behemoth bash', 'psychic fangs', 'wild charge',
            'baby-doll eyes', 'freeze-dry', 'weather ball', 'dazzling gleam', 'play rough',
            'knock off', 'rage powder', 'clear smog', 'foul play', 'dynamax cannon'
        }
        
        # Non-move words that should be excluded
        non_move_words = {
            'ability', 'item', 'nature', 'tera', 'ev', 'spread', 'explanation', 'pokemon', 'team', 'member',
            'snow', 'warning', 'rough', 'skin', 'life', 'orb', 'clear', 'amulet', 'timid', 'jolly', 'ghost', 'fire',
            'hp', 'atk', 'def', 'spa', 'spd', 'spe', 'alolan', 'ninetales', 'garchomp', 'iron', 'valiant', 'zamazenta',
            'calyrex', 'shadow', 'rider', 'ice', 'chien', 'pao', 'chi', 'yu', 'amoonguss', 'dragonite', 'jugulis', 'crown',
            'miraidon', 'koraidon', 'urshifu', 'rillaboom', 'volcarona', 'held', 'type', 'effort', 'values'
        }
        
        i = 0
        while i < len(words):
            # Try to find multi-word moves first
            found_multi = False
            for j in range(min(3, len(words) - i), 0, -1):  # Try 3, 2, then 1 word combinations
                potential_move = ' '.join(words[i:i+j]).lower()
                if potential_move in multi_word_moves:
                    moves_list.append(' '.join(words[i:i+j]).title())
                    i += j
                    found_multi = True
                    break
            
            if not found_multi:
                # Check if this word is a non-move word
                word_lower = words[i].lower()
                if word_lower not in non_move_words and len(words[i]) > 2:
                    # Single word move
                    moves_list.append(words[i].title())
                i += 1
        
        # Filter out any remaining non-move words and ensure we have exactly 4 moves
        filtered_moves = []
        for move in moves_list:
            move_lower = move.lower()
            if (move_lower not in non_move_words and 
                len(move) > 2 and 
                not move_lower.startswith('ev') and
                not move_lower.startswith('hp') and
                not move_lower.startswith('atk') and
                not move_lower.startswith('def') and
                not move_lower.startswith('spa') and
                not move_lower.startswith('spd') and
                not move_lower.startswith('spe')):
                filtered_moves.append(move)
        
        # Take first 4 unique moves
        unique_moves = []
        seen = set()
        for move in filtered_moves:
            if move not in seen and len(unique_moves) < 4:
                unique_moves.append(move)
                seen.add(move)
        
        if len(unique_moves) >= 4:
            return unique_moves[:4]
        elif len(unique_moves) > 0:
            return unique_moves
    else:
        moves_list = [moves_text.title()]
    
    # Clean up each move
    cleaned_moves = []
    for move in moves_list:
        move = move.strip()
        if move and len(move) > 1:
            # Remove common artifacts
            move = re.sub(r'^\s*[-•]\s*', '', move)
            move = re.sub(r'\s+', ' ', move)
            move = move.strip()
            if move:
                cleaned_moves.append(move)
    
    # Filter out abilities that might be incorrectly included
    ability_keywords = [
        'as one', 'unseen fist', 'grassy surge', 'regenerator', 'quark drive', 'drizzle',
        'sword of ruin', 'beads of ruin', 'snow warning', 'rough skin', 'dauntless shield'
    ]
    
    filtered_moves = []
    for move in cleaned_moves:
        if move.lower() not in ability_keywords:
            filtered_moves.append(move)
    
    # Ensure we have exactly 4 moves if possible
    if len(filtered_moves) > 4:
        filtered_moves = filtered_moves[:4]
    
    return filtered_moves

def validate_moves_against_pokemon(pokemon_name: str, moves: list) -> tuple[list, list]:
    """
    Validate moves against a specific Pokémon's known movepool.
    Returns (valid_moves, invalid_moves).
    """
    if not moves:
        return [], []
    
    # Pokémon-specific move validation
    pokemon_movepools = {
        'garchomp': {
            'valid_moves': {
                'stomping tantrum', 'protect', 'rock slide', 'earthquake', 'dragon claw', 'outrage',
                'stone edge', 'fire fang', 'poison jab', 'iron head', 'crunch', 'swords dance',
                'substitute', 'stealth rock', 'toxic', 'roar', 'bulldoze', 'dig', 'dragon rush',
                'dragon tail', 'flamethrower', 'fire blast', 'draco meteor', 'dragon pulse'
            },
            'invalid_moves': {
                'wide guard', 'quick guard', 'crafty shield', 'mat block', 'spiky shield',
                'king\'s shield', 'baneful bunker', 'obstruct'
            }
        },
        'iron valiant': {
            'valid_moves': {
                'close combat', 'spirit break', 'moonblast', 'protect', 'substitute', 'swords dance',
                'calm mind', 'psychic', 'psyshock', 'shadow ball', 'dark pulse', 'energy ball',
                'thunderbolt', 'ice beam', 'flamethrower', 'fire blast', 'dazzling gleam',
                'play rough', 'iron head', 'poison jab', 'knock off', 'u-turn', 'encore',
                'taunt', 'thunder wave', 'will-o-wisp', 'aurora veil', 'tailwind'
            }
        },
        'zamazenta': {
            'valid_moves': {
                'close combat', 'behemoth bash', 'wide guard', 'protect', 'substitute', 'swords dance',
                'iron head', 'crunch', 'psychic fangs', 'wild charge', 'stone edge', 'earthquake',
                'howl', 'work up', 'agility', 'coaching', 'helping hand', 'snarl', 'noble roar'
            }
        },
        'alolan ninetales': {
            'valid_moves': {
                'blizzard', 'moonblast', 'protect', 'aurora veil', 'freeze-dry', 'ice beam',
                'dazzling gleam', 'extrasensory', 'psyshock', 'shadow ball', 'dark pulse',
                'energy ball', 'solar beam', 'weather ball', 'hypnosis', 'encore', 'disable',
                'tailwind', 'charm', 'baby-doll eyes', 'agility', 'safeguard'
            }
        }
    }
    
    # Common VGC moves that most Pokémon can learn
    common_vgc_moves = {
        'protect', 'substitute', 'swords dance', 'nasty plot', 'calm mind', 'bulk up',
        'close combat', 'earthquake', 'rock slide', 'stone edge', 'dragon claw', 'outrage',
        'fire blast', 'flamethrower', 'ice beam', 'blizzard', 'thunderbolt', 'thunder',
        'psychic', 'shadow ball', 'dark pulse', 'sludge bomb', 'giga drain', 'energy ball',
        'u-turn', 'fake out', 'encore', 'taunt', 'thunder wave', 'will-o-wisp',
        'aurora veil', 'tailwind', 'rage powder', 'spore', 'clear smog', 'foul play',
        'wide guard', 'quick guard', 'crafty shield', 'mat block', 'spiky shield',
        'king\'s shield', 'baneful bunker', 'obstruct', 'max guard', 'dynamax cannon'
    }
    
    valid_moves = []
    invalid_moves = []
    
    # Check if we have specific movepool data for this Pokémon
    pokemon_lower = pokemon_name.lower()
    if pokemon_lower in pokemon_movepools:
        pokemon_data = pokemon_movepools[pokemon_lower]
        pokemon_valid_moves = pokemon_data['valid_moves']
        pokemon_invalid_moves = pokemon_data.get('invalid_moves', set())
        
        for move in moves:
            move_lower = move.lower()
            if move_lower in pokemon_valid_moves:
                valid_moves.append(move)
            elif move_lower in pokemon_invalid_moves:
                invalid_moves.append(f"{move} (cannot learn this move)")
            elif move_lower in common_vgc_moves:
                # Common VGC moves are generally valid unless specifically invalid
                valid_moves.append(move)
            else:
                # Mark as potentially invalid but don't be too strict
                invalid_moves.append(f"{move} (move not verified)")
    else:
        # Fallback to common VGC moves for unknown Pokémon
        for move in moves:
            move_lower = move.lower()
            if move_lower in common_vgc_moves:
                valid_moves.append(move)
            else:
                # Mark as potentially invalid
                invalid_moves.append(f"{move} (move not verified)")
    
    return valid_moves, invalid_moves
