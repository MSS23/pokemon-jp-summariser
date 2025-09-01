"""
Pokemon validation and name correction utilities.
"""

import re
from typing import Dict, Any, List

# Import Pokemon name translations (will need to update path)
# from ..utils.config import POKEMON_NAME_TRANSLATIONS


class PokemonValidator:
    """Handles Pokemon name validation, form correction, and translation"""
    
    def __init__(self):
        """Initialize the Pokemon validator"""
        # For now, we'll define some key translations here
        # This should ideally be loaded from the config file
        self.pokemon_name_translations = {
            # Generation 9 Priority Pokemon
            'サーフゴー': 'Gholdengo',
            'ガルデンゴ': 'Gholdengo',  # Alternative romanization
            'テツノカイナ': 'Iron Hands',
            'ハバタクカミ': 'Flutter Mane',
            'オーガポン': 'Ogerpon',
            'チオンジェン': 'Chi-Yu',
            'パオジアン': 'Chien-Pao',
            'ディンルー': 'Ting-Lu',
            'イーユイ': 'Wo-Chien',
            
            # Hisuian Forms
            'ヒスイウインディ': 'Arcanine-Hisui',
            'ヒスイゾロアーク': 'Zoroark-Hisui',
            'ヒスイガーディ': 'Growlithe-Hisui',
            'ヒスイバクフーン': 'Typhlosion-Hisui',
            
            # Forces of Nature
            'トルネロス': 'Tornadus-Incarnate',  # Default to Incarnate
            'ランドロス': 'Landorus-Therian',   # Usually Therian in VGC
            'ボルトロス': 'Thundurus-Therian',  # Usually Therian in VGC
            
            # Common VGC Pokemon
            'イルカマン': 'Palafin',
            'コライドン': 'Koraidon',
            'ミライドン': 'Miraidon',
            'ザシアン': 'Zacian',
            'ザマゼンタ': 'Zamazenta',
        }
        
        # Form correction patterns
        self.form_corrections = {
            # Ogerpon forms
            'オーガポン (いどのめん)': 'Ogerpon-Wellspring',
            'オーガポン (かまどのめん)': 'Ogerpon-Hearthflame',
            'オーガポン (いしずえのめん)': 'Ogerpon-Cornerstone',
            'オーガポン (みどりのめん)': 'Ogerpon',
            
            # Therian/Incarnate forms
            'トルネロス (れいじゅうフォルム)': 'Tornadus-Therian',
            'トルネロス (けしんフォルム)': 'Tornadus-Incarnate',
            'ランドロス (れいじゅうフォルム)': 'Landorus-Therian',
            'ランドロス (けしんフォルム)': 'Landorus-Incarnate',
            'ボルトロス (れいじゅうフォルム)': 'Thundurus-Therian',
            'ボルトロス (けしんフォルム)': 'Thundurus-Incarnate',
        }
        
        # Paradox Pokemon that should NEVER have form suffixes
        self.paradox_pokemon = {
            'Iron Valiant', 'Flutter Mane', 'Iron Hands', 'Iron Moth',
            'Sandy Shocks', 'Roaring Moon', 'Great Tusk', 'Scream Tail',
            'Brute Bonnet', 'Iron Treads', 'Iron Bundle', 'Iron Jugulis'
        }

    def fix_pokemon_name_translations(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix Pokemon name translations in the analysis result
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Updated result with corrected Pokemon names
        """
        if not isinstance(result.get("pokemon_team"), list):
            return result
        
        for pokemon in result["pokemon_team"]:
            if isinstance(pokemon, dict) and "name" in pokemon:
                original_name = pokemon["name"]
                corrected_name = self._correct_pokemon_name(original_name)
                
                if corrected_name != original_name:
                    pokemon["name"] = corrected_name
                    # Add note about the correction
                    translation_notes = result.get("translation_notes", "")
                    if f"Corrected {original_name} → {corrected_name}" not in translation_notes:
                        translation_notes += f" | Corrected {original_name} → {corrected_name}"
                        result["translation_notes"] = translation_notes.strip(" |")
        
        return result
    
    def apply_pokemon_validation(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply comprehensive Pokemon validation checks
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Updated result with validation applied
        """
        if not isinstance(result.get("pokemon_team"), list):
            return result
        
        validation_notes = []
        
        for pokemon in result["pokemon_team"]:
            if isinstance(pokemon, dict) and "name" in pokemon:
                pokemon_name = pokemon["name"]
                
                # Check for invalid Paradox Pokemon forms
                validation_issue = self._validate_paradox_forms(pokemon_name)
                if validation_issue:
                    validation_notes.append(validation_issue)
                    # Correct the name
                    pokemon["name"] = self._fix_paradox_form(pokemon_name)
                
                # Check for proper regional form formatting
                validation_issue = self._validate_regional_forms(pokemon_name)
                if validation_issue:
                    validation_notes.append(validation_issue)
                    # Correct the formatting
                    pokemon["name"] = self._fix_regional_form(pokemon_name)
                
                # Validate EV spreads
                ev_issue = self._validate_ev_spread(pokemon.get("ev_spread", {}))
                if ev_issue:
                    validation_notes.append(f"{pokemon_name}: {ev_issue}")
        
        # Add validation notes if any issues were found
        if validation_notes:
            existing_notes = result.get("translation_notes", "")
            validation_text = " | ".join(validation_notes)
            if existing_notes:
                result["translation_notes"] = f"{existing_notes} | Validation: {validation_text}"
            else:
                result["translation_notes"] = f"Validation: {validation_text}"
        
        return result
    
    def _correct_pokemon_name(self, name: str) -> str:
        """
        Correct a single Pokemon name using translation dictionary and form rules
        
        Args:
            name: Original Pokemon name
            
        Returns:
            Corrected Pokemon name
        """
        # Handle None or empty names
        if not name or name in ["Unknown", "Unknown Pokemon"]:
            return name
        
        # First check exact form matches
        if name in self.form_corrections:
            return self.form_corrections[name]
        
        # Check direct translations
        if name in self.pokemon_name_translations:
            return self.pokemon_name_translations[name]
        
        # Handle partial matches and common errors
        name_lower = name.lower()
        
        # Fix common Gholdengo variations
        if any(variant in name_lower for variant in ['gholdengo', 'ガルデンゴ', 'サーフゴー']):
            return 'Gholdengo'
        
        # Fix Treasures of Ruin confusions
        if 'chi-yu' in name_lower or 'チオンジェン' in name:
            return 'Chi-Yu'
        if 'chien-pao' in name_lower or 'パオジアン' in name:
            return 'Chien-Pao'
        if 'ting-lu' in name_lower or 'ディンルー' in name:
            return 'Ting-Lu'
        if 'wo-chien' in name_lower or 'イーユイ' in name:
            return 'Wo-Chien'
        
        # Fix Ogerpon forms
        if 'ogerpon' in name_lower:
            if 'wellspring' in name_lower or 'いどのめん' in name:
                return 'Ogerpon-Wellspring'
            elif 'hearthflame' in name_lower or 'かまどのめん' in name:
                return 'Ogerpon-Hearthflame'
            elif 'cornerstone' in name_lower or 'いしずえのめん' in name:
                return 'Ogerpon-Cornerstone'
            else:
                return 'Ogerpon'  # Base form
        
        # Fix Forces of Nature forms
        if 'tornadus' in name_lower or 'トルネロス' in name:
            if 'therian' in name_lower or 'れいじゅうフォルム' in name:
                return 'Tornadus-Therian'
            else:
                return 'Tornadus-Incarnate'  # Default
        
        if 'landorus' in name_lower or 'ランドロス' in name:
            if 'incarnate' in name_lower or 'けしんフォルム' in name:
                return 'Landorus-Incarnate'
            else:
                return 'Landorus-Therian'  # Default for VGC
        
        if 'thundurus' in name_lower or 'ボルトロス' in name:
            if 'incarnate' in name_lower or 'けしんフォルム' in name:
                return 'Thundurus-Incarnate'
            else:
                return 'Thundurus-Therian'  # Default for VGC
        
        # Fix Hisuian forms
        if 'hisui' in name_lower or 'ヒスイ' in name:
            if 'arcanine' in name_lower or 'ウインディ' in name:
                return 'Arcanine-Hisui'
            elif 'zoroark' in name_lower or 'ゾロアーク' in name:
                return 'Zoroark-Hisui'
            elif 'growlithe' in name_lower or 'ガーディ' in name:
                return 'Growlithe-Hisui'
            elif 'typhlosion' in name_lower or 'バクフーン' in name:
                return 'Typhlosion-Hisui'
        
        # If no corrections needed, return original
        return name
    
    def _validate_paradox_forms(self, pokemon_name: str) -> str:
        """Check for invalid Paradox Pokemon forms"""
        base_name = pokemon_name.split('-')[0] if '-' in pokemon_name else pokemon_name
        
        if base_name in self.paradox_pokemon and '-' in pokemon_name:
            suffix = pokemon_name.split('-', 1)[1]
            if suffix not in ['Therian', 'Incarnate']:  # These aren't Paradox forms anyway
                return f"Removed invalid form suffix from Paradox Pokemon: {pokemon_name}"
        
        return ""
    
    def _fix_paradox_form(self, pokemon_name: str) -> str:
        """Remove invalid form suffixes from Paradox Pokemon"""
        base_name = pokemon_name.split('-')[0] if '-' in pokemon_name else pokemon_name
        
        if base_name in self.paradox_pokemon:
            return base_name
        
        return pokemon_name
    
    def _validate_regional_forms(self, pokemon_name: str) -> str:
        """Check for proper regional form formatting"""
        if '-' in pokemon_name:
            parts = pokemon_name.split('-')
            if len(parts) == 2:
                base, form = parts
                
                # Check for proper regional form names
                valid_regions = ['Hisui', 'Galar', 'Alola', 'Therian', 'Incarnate', 
                               'Wellspring', 'Hearthflame', 'Cornerstone']
                
                if form not in valid_regions:
                    # Check for common misspellings
                    if form.lower() in ['hisuian', 'galarian', 'alolan']:
                        return f"Fixed regional form format: {pokemon_name}"
                    elif form.lower() in ['t', 'therian-forme', 'incarnate-forme']:
                        return f"Fixed forme format: {pokemon_name}"
        
        return ""
    
    def _fix_regional_form(self, pokemon_name: str) -> str:
        """Fix regional form formatting"""
        if '-' in pokemon_name:
            parts = pokemon_name.split('-')
            if len(parts) == 2:
                base, form = parts
                
                # Fix common regional form issues
                if form.lower() == 'hisuian':
                    return f"{base}-Hisui"
                elif form.lower() == 'galarian':
                    return f"{base}-Galar"
                elif form.lower() == 'alolan':
                    return f"{base}-Alola"
                elif form.lower() in ['t', 'therian-forme']:
                    return f"{base}-Therian"
                elif form.lower() in ['i', 'incarnate-forme']:
                    return f"{base}-Incarnate"
        
        return pokemon_name
    
    def _validate_ev_spread(self, ev_spread: Dict) -> str:
        """Validate EV spread values"""
        if not isinstance(ev_spread, dict):
            return "Invalid EV spread format"
        
        # Check if EVs are valid numbers
        ev_stats = ['HP', 'Attack', 'Defense', 'Special Attack', 'Special Defense', 'Speed']
        total = 0
        
        for stat in ev_stats:
            ev_value = ev_spread.get(stat, 0)
            
            # Check if it's a valid number
            try:
                ev_value = int(ev_value)
            except (ValueError, TypeError):
                return f"Invalid EV value for {stat}: {ev_value}"
            
            # Check if EVs are in valid range (0-252)
            if ev_value < 0 or ev_value > 252:
                return f"EV value out of range for {stat}: {ev_value}"
            
            # Check if EVs are multiples of 4 (efficient allocation)
            if ev_value > 0 and ev_value % 4 != 0:
                return f"Inefficient EV allocation for {stat}: {ev_value} (not divisible by 4)"
            
            total += ev_value
        
        # Check total EVs
        if total > 508:
            return f"Total EVs exceed maximum: {total}/508"
        
        # Update the total in the EV spread
        ev_spread['total'] = total
        
        return ""
    
    def get_pokemon_suggestions(self, partial_name: str) -> List[str]:
        """
        Get Pokemon name suggestions based on partial input
        
        Args:
            partial_name: Partial Pokemon name
            
        Returns:
            List of suggested Pokemon names
        """
        suggestions = []
        partial_lower = partial_name.lower()
        
        # Search through Japanese names
        for japanese, english in self.pokemon_name_translations.items():
            if partial_lower in japanese.lower() or partial_lower in english.lower():
                suggestions.append(english)
        
        # Search through form corrections
        for form_jp, form_en in self.form_corrections.items():
            if partial_lower in form_jp.lower() or partial_lower in form_en.lower():
                suggestions.append(form_en)
        
        return list(set(suggestions))  # Remove duplicates
    
    def is_valid_pokemon_name(self, name: str) -> bool:
        """
        Check if a Pokemon name is valid
        
        Args:
            name: Pokemon name to check
            
        Returns:
            True if name appears valid, False otherwise
        """
        if not name or name in ["Unknown", "Unknown Pokemon", "Not specified"]:
            return False
        
        # Check if it's in our translation dictionaries
        if name in self.pokemon_name_translations.values():
            return True
        
        if name in self.form_corrections.values():
            return True
        
        # Check if it follows valid naming patterns
        if '-' in name:
            parts = name.split('-')
            if len(parts) == 2:
                base, form = parts
                valid_forms = ['Hisui', 'Galar', 'Alola', 'Therian', 'Incarnate', 
                              'Wellspring', 'Hearthflame', 'Cornerstone']
                return form in valid_forms
        
        # For now, assume other names might be valid (we don't have complete database)
        return True