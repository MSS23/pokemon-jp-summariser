# -*- coding: utf-8 -*-
"""
Data validation, consistency checks, and data integrity monitoring
Addresses concerns: data validation, consistency, integrity, move compatibility
"""

import re
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import streamlit as st

class PokemonDataValidator:
    """Validate Pokemon data for consistency and correctness"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.validation_errors = []
        self.validation_warnings = []
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules from configuration"""
        # This would ideally come from a database or configuration file
        # For now, we'll define basic rules
        return {
            'moves': {
                'max_count': 4,
                'min_count': 1,
                'required_fields': ['name'],
                'forbidden_moves': ['', 'None', 'null', 'undefined']
            },
            'evs': {
                'max_total': 510,
                'max_per_stat': 252,
                'min_per_stat': 0,
                'valid_stats': ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
            },
            'tera_types': [
                "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
                "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"
            ],
            'natures': [
                "Hardy", "Lonely", "Brave", "Adamant", "Naughty", "Bold", "Docile", "Relaxed",
                "Impish", "Lax", "Timid", "Hasty", "Serious", "Jolly", "Naive", "Modest",
                "Mild", "Quiet", "Bashful", "Rash", "Calm", "Gentle", "Sassy", "Careful",
                "Quirky"
            ]
        }
    
    def validate_pokemon(self, pokemon: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate a single Pokemon's data"""
        self.validation_errors = []
        self.validation_warnings = []
        
        # Basic required fields
        if not pokemon.get('name'):
            self.validation_errors.append("Pokemon name is required")
        
        # Validate moves
        self._validate_moves(pokemon)
        
        # Validate EVs
        self._validate_evs(pokemon)
        
        # Validate Tera type
        self._validate_tera_type(pokemon)
        
        # Validate nature
        self._validate_nature(pokemon)
        
        # Validate ability and item (basic checks)
        self._validate_ability_item(pokemon)
        
        # Check for strategic consistency
        self._validate_strategic_consistency(pokemon)
        
        is_valid = len(self.validation_errors) == 0
        
        return is_valid, self.validation_errors, self.validation_warnings
    
    def _validate_moves(self, pokemon: Dict[str, Any]):
        """Validate Pokemon moves"""
        moves = pokemon.get('moves', [])
        
        if not moves:
            self.validation_errors.append("Pokemon must have at least one move")
            return
        
        if not isinstance(moves, list):
            self.validation_errors.append("Moves must be a list")
            return
        
        if len(moves) > self.validation_rules['moves']['max_count']:
            self.validation_errors.append(f"Pokemon cannot have more than {self.validation_rules['moves']['max_count']} moves")
        
        if len(moves) < self.validation_rules['moves']['min_count']:
            self.validation_errors.append(f"Pokemon must have at least {self.validation_rules['moves']['min_count']} move")
        
        # Check for invalid moves
        for move in moves:
            if move in self.validation_rules['moves']['forbidden_moves']:
                self.validation_errors.append(f"Invalid move: {move}")
            elif not move or not move.strip():
                self.validation_errors.append("Move cannot be empty")
        
        # Check for duplicate moves
        if len(moves) != len(set(moves)):
            self.validation_warnings.append("Pokemon has duplicate moves")
    
    def _validate_evs(self, pokemon: Dict[str, Any]):
        """Validate Pokemon EVs"""
        evs = pokemon.get('evs', {})
        
        if not evs:
            self.validation_warnings.append("No EVs specified")
            return
        
        if not isinstance(evs, dict):
            self.validation_errors.append("EVs must be a dictionary")
            return
        
        total_evs = 0
        valid_stats = self.validation_rules['evs']['valid_stats']
        
        for stat, value in evs.items():
            if stat not in valid_stats:
                self.validation_warnings.append(f"Unknown EV stat: {stat}")
                continue
            
            if not isinstance(value, (int, float)):
                self.validation_errors.append(f"EV value for {stat} must be a number")
                continue
            
            value = int(value)
            if value < self.validation_rules['evs']['min_per_stat']:
                self.validation_errors.append(f"EV value for {stat} cannot be negative")
            elif value > self.validation_rules['evs']['max_per_stat']:
                self.validation_errors.append(f"EV value for {stat} cannot exceed {self.validation_rules['evs']['max_per_stat']}")
            
            total_evs += value
        
        if total_evs > self.validation_rules['evs']['max_total']:
            self.validation_errors.append(f"Total EVs ({total_evs}) exceed maximum ({self.validation_rules['evs']['max_total']})")
        elif total_evs == 0:
            self.validation_warnings.append("No EVs invested")
        elif total_evs < self.validation_rules['evs']['max_total']:
            remaining = self.validation_rules['evs']['max_total'] - total_evs
            self.validation_warnings.append(f"Unused EVs: {remaining} remaining")
    
    def _validate_tera_type(self, pokemon: Dict[str, Any]):
        """Validate Pokemon Tera type"""
        tera_type = pokemon.get('tera_type')
        
        if not tera_type or tera_type == 'Not specified':
            self.validation_warnings.append("No Tera type specified")
            return
        
        if tera_type not in self.validation_rules['tera_types']:
            self.validation_errors.append(f"Invalid Tera type: {tera_type}")
    
    def _validate_nature(self, pokemon: Dict[str, Any]):
        """Validate Pokemon nature"""
        nature = pokemon.get('nature')
        
        if not nature or nature == 'Not specified':
            self.validation_warnings.append("No nature specified")
            return
        
        if nature not in self.validation_rules['natures']:
            self.validation_warnings.append(f"Unknown nature: {nature}")
    
    def _validate_ability_item(self, pokemon: Dict[str, Any]):
        """Validate Pokemon ability and item"""
        ability = pokemon.get('ability')
        item = pokemon.get('item')
        
        if not ability or ability == 'Not specified':
            self.validation_warnings.append("No ability specified")
        
        if not item or item == 'Not specified':
            self.validation_warnings.append("No item specified")
    
    def _validate_strategic_consistency(self, pokemon: Dict[str, Any]):
        """Validate strategic consistency of the Pokemon"""
        moves = pokemon.get('moves', [])
        evs = pokemon.get('evs', {})
        tera_type = pokemon.get('tera_type')
        
        # Check for physical/special move consistency with EVs
        if moves and evs:
            physical_moves = self._get_physical_moves(moves)
            special_moves = self._get_special_moves(moves)
            
            attack_evs = evs.get('attack', 0)
            sp_attack_evs = evs.get('sp_attack', 0)
            
            if physical_moves and attack_evs == 0 and sp_attack_evs > 0:
                self.validation_warnings.append("Physical moves detected but no Attack EVs invested")
            
            if special_moves and sp_attack_evs == 0 and attack_evs > 0:
                self.validation_warnings.append("Special moves detected but no Special Attack EVs invested")
    
    def _get_physical_moves(self, moves: List[str]) -> List[str]:
        """Get physical moves from the move list"""
        # This is a simplified list - in a real app, you'd have a comprehensive move database
        physical_moves = [
            "Body Press", "Heavy Slam", "Close Combat", "High Jump Kick", "Earthquake",
            "Stone Edge", "Brave Bird", "Wood Hammer", "Extreme Speed", "Low Kick",
            "Rock Slide", "Outrage", "U-turn", "Fake Out", "Follow Me", "Rage Powder"
        ]
        
        return [move for move in moves if move in physical_moves]
    
    def _get_special_moves(self, moves: List[str]) -> List[str]:
        """Get special moves from the move list"""
        # This is a simplified list - in a real app, you'd have a comprehensive move database
        special_moves = [
            "Astral Barrage", "Psychic", "Heat Wave", "Flamethrower", "Overheat",
            "Dark Pulse", "Sludge Bomb", "Grassy Glide", "Aura Sphere", "Dazzling Gleam",
            "Thunderbolt", "Volt Switch", "Ice Spinner", "Sucker Punch", "Ice Shard"
        ]
        
        return [move for move in moves if move in special_moves]

class TeamDataValidator:
    """Validate team-level data consistency"""
    
    def __init__(self):
        self.validator = PokemonDataValidator()
        self.team_errors = []
        self.team_warnings = []
    
    def validate_team(self, team_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Validate entire team data"""
        self.team_errors = []
        self.team_warnings = []
        
        if not team_data or 'pokemon' not in team_data:
            self.team_errors.append("Team data is missing or invalid")
            return False, self.team_errors, self.team_warnings
        
        pokemon_list = team_data['pokemon']
        if not isinstance(pokemon_list, list):
            self.team_errors.append("Team must contain a list of Pokemon")
            return False, self.team_errors, self.team_warnings
        
        if len(pokemon_list) == 0:
            self.team_errors.append("Team must contain at least one Pokemon")
            return False, self.team_errors, self.team_warnings
        
        if len(pokemon_list) > 6:
            self.team_errors.append("Team cannot have more than 6 Pokemon")
            return False, self.team_errors, self.team_warnings
        
        # Validate each Pokemon
        valid_pokemon_count = 0
        for i, pokemon in enumerate(pokemon_list):
            is_valid, errors, warnings = self.validator.validate_pokemon(pokemon)
            
            if is_valid:
                valid_pokemon_count += 1
            
            # Add Pokemon index to error messages
            for error in errors:
                self.team_errors.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): {error}")
            
            for warning in warnings:
                self.team_warnings.append(f"Pokemon {i+1} ({pokemon.get('name', 'Unknown')}): {warning}")
        
        # Team-level validations
        self._validate_team_composition(team_data)
        self._validate_team_strategy(team_data)
        
        is_valid = len(self.team_errors) == 0
        
        return is_valid, self.team_errors, self.team_warnings
    
    def _validate_team_composition(self, team_data: Dict[str, Any]):
        """Validate team composition and balance"""
        pokemon_list = team_data['pokemon']
        
        # Check for duplicate Pokemon
        pokemon_names = [p.get('name', 'Unknown') for p in pokemon_list]
        if len(pokemon_names) != len(set(pokemon_names)):
            self.team_warnings.append("Team contains duplicate Pokemon")
        
        # Check for type diversity
        tera_types = [p.get('tera_type', 'Unknown') for p in pokemon_list if p.get('tera_type') and p.get('tera_type') != 'Not specified']
        if len(set(tera_types)) < len(tera_types) * 0.5:  # Less than 50% unique types
            self.team_warnings.append("Team has limited type diversity")
    
    def _validate_team_strategy(self, team_data: Dict[str, Any]):
        """Validate team strategy consistency"""
        pokemon_list = team_data['pokemon']
        
        # Check for support Pokemon
        support_moves = ["Follow Me", "Rage Powder", "Wide Guard", "Quick Guard", "Helping Hand", "Heal Pulse"]
        support_count = 0
        
        for pokemon in pokemon_list:
            moves = pokemon.get('moves', [])
            if any(move in support_moves for move in moves):
                support_count += 1
        
        if support_count == 0:
            self.team_warnings.append("Team has no support Pokemon")
        elif support_count > len(pokemon_list) * 0.5:
            self.team_warnings.append("Team may be too support-heavy")

class DataConsistencyChecker:
    """Check data consistency across different sources"""
    
    def __init__(self):
        self.consistency_issues = []
    
    def check_consistency(self, parsed_data: Dict[str, Any], summary_text: str) -> List[str]:
        """Check consistency between parsed data and summary text"""
        self.consistency_issues = []
        
        if not parsed_data or not summary_text:
            return self.consistency_issues
        
        # Check Pokemon names consistency
        self._check_pokemon_names_consistency(parsed_data, summary_text)
        
        # Check moves consistency
        self._check_moves_consistency(parsed_data, summary_text)
        
        # Check EVs consistency
        self._check_evs_consistency(parsed_data, summary_text)
        
        # Check Tera types consistency
        self._check_tera_types_consistency(parsed_data, summary_text)
        
        return self.consistency_issues
    
    def _check_pokemon_names_consistency(self, parsed_data: Dict[str, Any], summary_text: str):
        """Check if Pokemon names in parsed data match summary text"""
        if 'pokemon' not in parsed_data:
            return
        
        summary_lower = summary_text.lower()
        for pokemon in parsed_data['pokemon']:
            name = pokemon.get('name', '')
            if name and name.lower() not in summary_lower:
                self.consistency_issues.append(f"Pokemon name '{name}' not found in summary text")
    
    def _check_moves_consistency(self, parsed_data: Dict[str, Any], summary_text: str):
        """Check if moves in parsed data match summary text"""
        if 'pokemon' not in parsed_data:
            return
        
        summary_lower = summary_text.lower()
        for pokemon in parsed_data['pokemon']:
            moves = pokemon.get('moves', [])
            name = pokemon.get('name', 'Unknown')
            
            for move in moves:
                if move and move.lower() not in summary_lower:
                    self.consistency_issues.append(f"Move '{move}' for {name} not found in summary text")
    
    def _check_evs_consistency(self, parsed_data: Dict[str, Any], summary_text: str):
        """Check if EVs in parsed data match summary text"""
        if 'pokemon' not in parsed_data:
            return
        
        summary_lower = summary_text.lower()
        for pokemon in parsed_data['pokemon']:
            evs = pokemon.get('evs', {})
            name = pokemon.get('name', 'Unknown')
            
            for stat, value in evs.items():
                if value > 0:
                    # Look for EV mentions in summary
                    ev_pattern = rf"{value}\s*{stat.replace('_', r'\s*')}"
                    if not re.search(ev_pattern, summary_lower, re.IGNORECASE):
                        self.consistency_issues.append(f"EV spread {value} {stat} for {name} not clearly mentioned in summary")
    
    def _check_tera_types_consistency(self, parsed_data: Dict[str, Any], summary_text: str):
        """Check if Tera types in parsed data match summary text"""
        if 'pokemon' not in parsed_data:
            return
        
        summary_lower = summary_text.lower()
        for pokemon in parsed_data['pokemon']:
            tera_type = pokemon.get('tera_type', '')
            name = pokemon.get('name', 'Unknown')
            
            if tera_type and tera_type != 'Not specified':
                if tera_type.lower() not in summary_lower:
                    self.consistency_issues.append(f"Tera type '{tera_type}' for {name} not found in summary text")

def validate_and_repair_data(parsed_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """Validate and attempt to repair data issues"""
    validator = TeamDataValidator()
    is_valid, errors, warnings = validator.validate_team(parsed_data)
    
    repaired_data = parsed_data.copy()
    repair_notes = []
    
    if not is_valid:
        # Attempt basic repairs
        repaired_data, repair_notes = _attempt_data_repairs(repaired_data, errors)
    
    return repaired_data, errors, warnings + repair_notes

def _attempt_data_repairs(data: Dict[str, Any], errors: List[str]) -> Tuple[Dict[str, Any], List[str]]:
    """Attempt to repair common data issues"""
    repaired_data = data.copy()
    repair_notes = []
    
    if 'pokemon' not in repaired_data:
        return repaired_data, repair_notes
    
    for pokemon in repaired_data['pokemon']:
        # Repair EV issues
        if 'evs' in pokemon and pokemon['evs']:
            total = sum(pokemon['evs'].values())
            if total > 510:
                # Scale down EVs proportionally
                scale_factor = 510 / total
                for stat in pokemon['evs']:
                    pokemon['evs'][stat] = int(pokemon['evs'][stat] * scale_factor)
                repair_notes.append(f"Scaled down EVs for {pokemon.get('name', 'Unknown')} to fit 510 limit")
        
        # Repair empty moves
        if 'moves' in pokemon and pokemon['moves']:
            pokemon['moves'] = [move for move in pokemon['moves'] if move and move.strip()]
            if not pokemon['moves']:
                pokemon['moves'] = ['Tackle']  # Default move
                repair_notes.append(f"Added default move for {pokemon.get('name', 'Unknown')}")
    
    return repaired_data, repair_notes

def display_validation_results(is_valid: bool, errors: List[str], warnings: List[str]):
    """Display validation results in Streamlit"""
    if is_valid and not warnings:
        st.success("✅ All data validation checks passed!")
        return
    
    if not is_valid:
        st.error("❌ Data validation failed")
        st.markdown("**Errors:**")
        for error in errors:
            st.markdown(f"- {error}")
    
    if warnings:
        st.warning("⚠️ Data validation warnings")
        st.markdown("**Warnings:**")
        for warning in warnings:
            st.markdown(f"- {warning}")
    
    if not is_valid:
        st.info("💡 Some issues were automatically repaired. Please review the corrected data.")
