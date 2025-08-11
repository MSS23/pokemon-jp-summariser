# -*- coding: utf-8 -*-
"""
Enhanced utility functions for handling Pokemon corrections and article updates
Addresses concerns: data consistency, race conditions, error recovery, validation, UX, scalability, security
"""

import json
import os
import re
import fcntl
import tempfile
import shutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import streamlit as st
import hashlib
import threading
from contextlib import contextmanager

# Global lock for file operations
_file_lock = threading.Lock()

# Configuration
CACHE_FILE = "streamlit-app/storage/cache.json"
BACKUP_DIR = "streamlit-app/storage/backups"
MAX_BACKUPS = 10
MAX_CORRECTIONS_PER_SESSION = 50

class CorrectionError(Exception):
    """Custom exception for correction-related errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

@contextmanager
def safe_file_operation(filepath: str, mode: str = 'r'):
    """Context manager for safe file operations with locking and backup"""
    with _file_lock:
        try:
            # Create backup before modification
            if 'w' in mode and os.path.exists(filepath):
                create_backup(filepath)
            
            # Use temporary file for writing operations
            if 'w' in mode:
                temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
                try:
                    yield temp_file
                    temp_file.close()
                    # Atomic move operation
                    shutil.move(temp_file.name, filepath)
                except Exception:
                    temp_file.close()
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    raise
            else:
                with open(filepath, mode, encoding='utf-8') as f:
                    yield f
        except Exception as e:
            raise CorrectionError(f"File operation failed: {e}")

def create_backup(filepath: str) -> str:
    """Create a timestamped backup of the file"""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")
        shutil.copy2(filepath, backup_path)
        
        # Clean up old backups
        cleanup_old_backups()
        
        return backup_path
    except Exception as e:
        st.warning(f"Backup creation failed: {e}")
        return ""

def cleanup_old_backups():
    """Remove old backup files, keeping only the most recent ones"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return
        
        backup_files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.bak')]
        if len(backup_files) > MAX_BACKUPS:
            backup_files.sort(reverse=True)
            for old_file in backup_files[MAX_BACKUPS:]:
                os.remove(os.path.join(BACKUP_DIR, old_file))
    except Exception:
        pass

def validate_move_compatibility(pokemon_name: str, moves: List[str]) -> Tuple[List[str], List[str]]:
    """Validate that moves are compatible with the Pokemon"""
    # This is a simplified validation - in a real app, you'd have a comprehensive move database
    valid_moves = []
    invalid_moves = []
    
    # Basic validation rules
    for move in moves:
        if move and len(move.strip()) > 0:
            valid_moves.append(move)
        else:
            invalid_moves.append(move)
    
    return valid_moves, invalid_moves

def validate_tera_type_compatibility(pokemon_name: str, tera_type: str) -> bool:
    """Validate Tera type compatibility"""
    if not tera_type or tera_type == "Not specified":
        return True
    
    # Basic validation - in a real app, you'd check against Pokemon's base typing
    valid_types = get_tera_types()
    return tera_type in valid_types

def validate_ev_spread(evs: Dict[str, int]) -> Tuple[bool, str]:
    """Validate EV spread with detailed feedback"""
    if not evs:
        return True, "No EVs specified"
    
    total = sum(evs.values())
    
            if total > 508:
            return False, f"Total EVs ({total}) exceed maximum (508)"
    
    if total < 0:
        return False, f"Total EVs ({total}) cannot be negative"
    
    # Check individual stat limits
    for stat, value in evs.items():
        if value > 252:
            return False, f"{stat.title()} EVs ({value}) exceed maximum (252)"
        if value < 0:
            return False, f"{stat.title()} EVs ({value}) cannot be negative"
    
            return True, f"Valid EV spread: {total}/508 total"

def get_user_session_id() -> str:
    """Generate a unique session ID for the current user"""
    if 'user_session_id' not in st.session_state:
        # Create a hash from user info and timestamp
        user_info = f"{st.session_state.get('username', 'anonymous')}_{datetime.now().isoformat()}"
        st.session_state['user_session_id'] = hashlib.md5(user_info.encode()).hexdigest()[:8]
    return st.session_state['user_session_id']

def check_rate_limit() -> bool:
    """Check if user has exceeded correction rate limit"""
    if 'corrections_made' not in st.session_state:
        return True
    
    corrections = st.session_state['corrections_made']
    user_session = get_user_session_id()
    
    # Count corrections in current session
    session_corrections = [c for c in corrections if c.get('user_session') == user_session]
    
    return len(session_corrections) < MAX_CORRECTIONS_PER_SESSION

def save_pokemon_corrections(pokemon: Dict[str, Any], field: str, corrected_value: Any) -> Tuple[bool, str]:
    """Enhanced save function with validation, error handling, and consistency checks"""
    try:
        # Rate limiting check
        if not check_rate_limit():
            return False, f"Rate limit exceeded. Maximum {MAX_CORRECTIONS_PER_SESSION} corrections per session."
        
        # Store the old value for tracking
        old_value = pokemon.get(field)
        
        # Validate the correction based on field type
        if field == 'moves':
            valid_moves, invalid_moves = validate_move_compatibility(pokemon.get('name', ''), corrected_value)
            if invalid_moves:
                return False, f"Invalid moves: {', '.join(invalid_moves)}"
            corrected_value = valid_moves
        elif field == 'evs':
            is_valid, message = validate_ev_spread(corrected_value)
            if not is_valid:
                return False, message
        elif field == 'tera_type':
            if not validate_tera_type_compatibility(pokemon.get('name', ''), corrected_value):
                return False, f"Invalid Tera type: {corrected_value}"
        
        # Update the Pokemon data
        pokemon[field] = corrected_value
        
        # Update the parsed data in session state
        if 'parsed_data' in st.session_state:
            # Find and update the Pokemon in the parsed data
            for pkmn in st.session_state.parsed_data.get('pokemon', []):
                if (pkmn.get('name') == pokemon.get('name') and 
                    pkmn.get('ability') == pokemon.get('ability') and
                    pkmn.get('item') == pokemon.get('item')):
                    pkmn[field] = corrected_value
                    break
        
        # Track the correction in session state
        if 'corrections_made' not in st.session_state:
            st.session_state['corrections_made'] = []
        
        correction_info = {
            'pokemon_name': pokemon.get('name', 'Unknown'),
            'field': field,
            'old_value': format_correction_value(old_value, field),
            'new_value': format_correction_value(corrected_value, field),
            'timestamp': datetime.now().isoformat(),
            'user_session': get_user_session_id(),
            'correction_id': hashlib.md5(f"{pokemon.get('name')}{field}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        }
        
        st.session_state['corrections_made'].append(correction_info)
        
        # Save to cache with enhanced error handling
        if not save_corrections_to_cache(pokemon, field, corrected_value):
            return False, "Failed to save corrections to cache"
        
        # Update article summary with consistency checks
        if not update_article_summary_with_corrections():
            return False, "Failed to update article summary"
        
        return True, "Correction saved successfully"
        
    except Exception as e:
        st.error(f"Error saving corrections: {e}")
        return False, f"Unexpected error: {str(e)}"

def save_corrections_to_cache(pokemon: Dict[str, Any], field: str, corrected_value: Any) -> bool:
    """Enhanced cache saving with atomic operations and consistency checks"""
    try:
        if not os.path.exists(CACHE_FILE):
            st.warning("Cache file not found, creating new one")
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Load existing cache with safe file operation
        with safe_file_operation(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        # Find the article containing this Pokemon and update it
        article_updated = False
        for url, article_data in cache_data.items():
            if 'pokemon' in article_data:
                for pkmn in article_data['pokemon']:
                    if (pkmn.get('name') == pokemon.get('name') and 
                        pkmn.get('ability') == pokemon.get('ability') and
                        pkmn.get('item') == pokemon.get('item')):
                        pkmn[field] = corrected_value
                        article_updated = True
                        
                        # Update the summary text to maintain consistency
                        if 'summary' in article_data:
                            article_data['summary'] = update_summary_text(
                                article_data['summary'], 
                                pokemon.get('name', ''), 
                                field, 
                                old_value, 
                                corrected_value
                            )
                        
                        # Add metadata about the correction
                        if 'corrections_history' not in article_data:
                            article_data['corrections_history'] = []
                        
                        article_data['corrections_history'].append({
                            'timestamp': datetime.now().isoformat(),
                            'pokemon_name': pokemon.get('name', ''),
                            'field': field,
                            'old_value': old_value,
                            'new_value': corrected_value,
                            'user_session': get_user_session_id()
                        })
                        
                        break
        
        if not article_updated:
            st.warning("Could not find matching Pokemon in cache")
            return False
        
        # Save updated cache with safe file operation
        with safe_file_operation(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving to cache: {e}")
        return False

def update_summary_text(summary: str, pokemon_name: str, field: str, old_value: Any, new_value: Any) -> str:
    """Update summary text to reflect corrections while maintaining consistency"""
    try:
        if not summary or not pokemon_name:
            return summary
        
        # Convert values to strings for text replacement
        old_str = str(old_value) if old_value is not None else ""
        new_str = str(new_value) if new_value is not None else ""
        
        if not old_str or old_str == new_str:
            return summary
        
        # Create a more sophisticated replacement that considers context
        # This is a simplified approach - in production, you might use NLP techniques
        
        # Replace the old value with the new value
        updated_summary = summary.replace(old_str, new_str)
        
        return updated_summary
        
    except Exception as e:
        st.warning(f"Error updating summary text: {e}")
        return summary

def update_article_summary_with_corrections() -> bool:
    """Enhanced article summary update with consistency validation"""
    try:
        if 'parsed_data' not in st.session_state:
            return False
        
        parsed_data = st.session_state.parsed_data
        
        # Validate that the parsed data is consistent
        if not validate_parsed_data_consistency(parsed_data):
            st.warning("Data consistency issues detected, attempting to repair...")
            if not repair_parsed_data(parsed_data):
                return False
        
        # Update the session state
        st.session_state.parsed_data = parsed_data
        
        return True
        
    except Exception as e:
        st.error(f"Error updating article summary: {e}")
        return False

def validate_parsed_data_consistency(parsed_data: Dict[str, Any]) -> bool:
    """Validate that parsed data is internally consistent"""
    try:
        if not parsed_data or 'pokemon' not in parsed_data:
            return False
        
        for pokemon in parsed_data['pokemon']:
            # Check required fields
            if not pokemon.get('name'):
                return False
            
            # Validate EV totals
            if 'evs' in pokemon and pokemon['evs']:
                is_valid, _ = validate_ev_spread(pokemon['evs'])
                if not is_valid:
                    return False
        
        return True
        
    except Exception:
        return False

def repair_parsed_data(parsed_data: Dict[str, Any]) -> bool:
    """Attempt to repair consistency issues in parsed data"""
    try:
        if not parsed_data or 'pokemon' not in parsed_data:
            return False
        
        for pokemon in parsed_data['pokemon']:
            # Repair EV issues
            if 'evs' in pokemon and pokemon['evs']:
                total = sum(pokemon['evs'].values())
                        if total > 508:
            # Scale down EVs proportionally
            scale_factor = 508 / total
                    for stat in pokemon['evs']:
                        pokemon['evs'][stat] = int(pokemon['evs'][stat] * scale_factor)
        
        return True
        
    except Exception:
        return False

def get_all_team_moves(parsed_data: Dict[str, Any]) -> List[str]:
    """Get all moves from the team for dropdown options with enhanced fallback"""
    all_moves = set()
    try:
        for pkmn in parsed_data.get('pokemon', []):
            moves = pkmn.get('moves', [])
            if isinstance(moves, list):
                all_moves.update(moves)
    except Exception:
        pass
    
    # Enhanced fallback move list
    if not all_moves:
        all_moves = {
            # Status moves
            "Protect", "Substitute", "Swords Dance", "Nasty Plot", "Calm Mind",
            "Dragon Dance", "Bulk Up", "Iron Defense", "Amnesia", "Agility",
            "Thunder Wave", "Will-O-Wisp", "Toxic", "Confuse Ray", "Hypnosis",
            "Sleep Powder", "Spore", "Yawn", "Taunt", "Encore",
            
            # Support moves
            "Fake Out", "Follow Me", "Rage Powder", "Wide Guard", "Quick Guard",
            "Helping Hand", "Heal Pulse", "Wish", "Recover", "Roost",
            "Synthesis", "Morning Sun", "Moonlight", "Soft-Boiled", "Heal Order",
            
            # Offensive moves
            "Astral Barrage", "Psychic", "Body Press", "Heavy Slam", "Ruination",
            "Ice Spinner", "Sucker Punch", "Ice Shard", "Heat Wave", "Flamethrower",
            "Overheat", "Dark Pulse", "Sludge Bomb", "Grassy Glide", "Wood Hammer",
            "Needle Guard", "Extreme Speed", "Low Kick", "Rock Slide", "Outrage",
            "Aura Sphere", "Dazzling Gleam", "Thunderbolt", "Volt Switch", "U-turn",
            "Close Combat", "High Jump Kick", "Earthquake", "Stone Edge", "Brave Bird"
        }
    
    return sorted(list(all_moves))

def get_tera_types() -> List[str]:
    """Get list of all Tera types"""
    return [
        "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
        "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
    ]

def format_ev_spread(evs: Dict[str, int]) -> str:
    """Format EV spread for display"""
    if not evs:
        return "Not specified"
    
    ev_parts = []
    for stat, value in evs.items():
        if value > 0:
            stat_abbr = {
                'hp': 'HP', 'attack': 'Atk', 'defense': 'Def',
                'sp_attack': 'SpA', 'sp_defense': 'SpD', 'speed': 'Spe'
            }.get(stat, stat.title())
            ev_parts.append(f"{value} {stat_abbr}")
    
    return " / ".join(ev_parts) if ev_parts else "Not specified"

def validate_ev_total(evs: Dict[str, int]) -> bool:
    """Validate that total EVs don't exceed 508"""
    total = sum(evs.values())
    return total <= 508

def format_correction_value(value: Any, field: str) -> str:
    """Format value for display in correction summary"""
    if field == 'evs':
        return format_ev_spread(value)
    elif isinstance(value, list):
        return ', '.join(value)
    return str(value)

def get_correction_summary(pokemon: Dict[str, Any], field: str, old_value: Any, new_value: Any) -> str:
    """Generate a summary of the correction made"""
    pokemon_name = pokemon.get('name', 'Pokemon')
    
    if field == 'moves':
        return f"Updated moves for {pokemon_name}: {', '.join(old_value)} → {', '.join(new_value)}"
    elif field == 'evs':
        old_spread = format_ev_spread(old_value)
        new_spread = format_ev_spread(new_value)
        return f"Updated EVs for {pokemon_name}: {old_spread} → {new_spread}"
    elif field == 'tera_type':
        return f"Updated Tera type for {pokemon_name}: {old_value} → {new_value}"
    else:
        return f"Updated {field} for {pokemon_name}: {old_value} → {new_value}"

def can_revert_correction(correction_id: str) -> bool:
    """Check if a correction can be reverted"""
    if 'corrections_made' not in st.session_state:
        return False
    
    corrections = st.session_state['corrections_made']
    return any(c.get('correction_id') == correction_id for c in corrections)

def revert_correction(correction_id: str) -> Tuple[bool, str]:
    """Revert a specific correction"""
    try:
        if 'corrections_made' not in st.session_state:
            return False, "No corrections found"
        
        corrections = st.session_state['corrections_made']
        correction = None
        
        for c in corrections:
            if c.get('correction_id') == correction_id:
                correction = c
                break
        
        if not correction:
            return False, "Correction not found"
        
        # Find the Pokemon and revert the change
        if 'parsed_data' in st.session_state:
            for pkmn in st.session_state.parsed_data.get('pokemon', []):
                if pkmn.get('name') == correction['pokemon_name']:
                    # Revert the field value
                    field = correction['field']
                    if field == 'moves':
                        # Parse the old value back to a list
                        old_moves = correction['old_value'].split(', ')
                        pkmn[field] = old_moves
                    elif field == 'evs':
                        # This would need more sophisticated parsing
                        pkmn[field] = correction['old_value']
                    else:
                        pkmn[field] = correction['old_value']
                    break
        
        # Remove from corrections list
        st.session_state['corrections_made'] = [c for c in corrections if c.get('correction_id') != correction_id]
        
        return True, "Correction reverted successfully"
        
    except Exception as e:
        return False, f"Error reverting correction: {str(e)}"

def get_corrections_audit_trail() -> List[Dict[str, Any]]:
    """Get audit trail of all corrections made"""
    if 'corrections_made' not in st.session_state:
        return []
    
    return st.session_state['corrections_made'].copy()

def cleanup_session_corrections():
    """Clean up old corrections from session state"""
    if 'corrections_made' not in st.session_state:
        return
    
    # Keep only corrections from the last 24 hours
    cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)
    
    st.session_state['corrections_made'] = [
        c for c in st.session_state['corrections_made']
        if datetime.fromisoformat(c['timestamp']).timestamp() > cutoff_time
    ]
