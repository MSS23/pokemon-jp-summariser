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
            
            # CRITICAL FIXES: Missing Pokemon
            'オーロンゲ': 'Grimmsnarl',  # CRITICAL: Was completely missing
            
            # CALYREX FORMS - ULTRA-CRITICAL for restricted Pokemon identification
            'バドレックス': 'Calyrex',  # Base form
            'バドレックス-はくばじょう': 'Calyrex-Ice',   # Calyrex riding Glastrier (Ice horse)
            'バドレックス-こくばじょう': 'Calyrex-Shadow', # Calyrex riding Spectrier (Shadow horse)
            # Alternative spellings
            'はくばじょうバドレックス': 'Calyrex-Ice',
            'こくばじょうバドレックス': 'Calyrex-Shadow',
            '白馬': 'Calyrex-Ice',      # Short form meaning "White Horse"
            '黒馬': 'Calyrex-Shadow',   # Short form meaning "Black Horse"
            
            # KYUREM FORMS - CRITICAL to distinguish from Calyrex
            'キュレム': 'Kyurem',
            'キュレム-ホワイト': 'Kyurem-White',  # White Kyurem (NOT Calyrex-Ice!)
            'キュレム-ブラック': 'Kyurem-Black',  # Black Kyurem (NOT Calyrex-Shadow!)
            'ホワイトキュレム': 'Kyurem-White',
            'ブラックキュレム': 'Kyurem-Black',
            
            # Additional missing VGC Pokemon
            'イエッサン': 'Indeedee',
            'イエッサン♂': 'Indeedee-Male',
            'イエッサン♀': 'Indeedee-Female',
            'ドラパルト': 'Dragapult',
            'アーマーガア': 'Corviknight',
            'ミミッキュ': 'Mimikyu',
            'バンギラス': 'Tyranitar',
            'メタグロス': 'Metagross',
            'ボーマンダ': 'Salamence',
            
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
        
        # SIGNATURE MOVE VALIDATION DATABASE - ULTRA-CRITICAL for restricted Pokemon identification
        self.signature_moves = {
            # Calyrex Forms - CRITICAL to distinguish from Kyurem
            'Calyrex-Ice': {
                'signature_moves': ['Glacial Lance'],
                'japanese_names': ['ブリザードランス'],
                'alternative_names': ['Calyrex-White'],  # Common confusion
                'typing': ['Psychic', 'Ice'],
                'distinguishing_moves': ['Glacial Lance', 'Trick Room', 'Substitute']
            },
            'Calyrex-Shadow': {
                'signature_moves': ['Astral Barrage'],
                'japanese_names': ['アストラルビット'],
                'alternative_names': ['Calyrex-Black'],  # Common confusion
                'typing': ['Psychic', 'Ghost'],
                'distinguishing_moves': ['Astral Barrage', 'Nasty Plot', 'Substitute']
            },
            
            # Kyurem Forms - CRITICAL to distinguish from Calyrex
            'Kyurem-White': {
                'signature_moves': ['Ice Burn'],
                'japanese_names': ['アイスバーン', 'コールドフレア'],
                'alternative_names': ['White Kyurem'],
                'typing': ['Dragon', 'Ice'],
                'distinguishing_moves': ['Ice Burn', 'Fusion Flare', 'Blue Flare']
            },
            'Kyurem-Black': {
                'signature_moves': ['Freeze Shock'],
                'japanese_names': ['フリーズボルト'],
                'alternative_names': ['Black Kyurem'],
                'typing': ['Dragon', 'Ice'],
                'distinguishing_moves': ['Freeze Shock', 'Fusion Bolt', 'Bolt Strike']
            },
            
            # Other common restricted Pokemon
            'Koraidon': {
                'signature_moves': ['Collision Course'],
                'japanese_names': ['アクセルブレイク'],
                'typing': ['Fighting', 'Dragon'],
                'distinguishing_moves': ['Collision Course', 'Close Combat', 'Flare Blitz']
            },
            'Miraidon': {
                'signature_moves': ['Electro Drift'], 
                'japanese_names': ['イナズマドライブ'],
                'typing': ['Electric', 'Dragon'],
                'distinguishing_moves': ['Electro Drift', 'Draco Meteor', 'Dazzling Gleam']
            },
            'Zacian': {
                'signature_moves': ['Behemoth Blade'],
                'japanese_names': ['きょじゅうざん'],
                'typing': ['Fairy', 'Steel'],
                'distinguishing_moves': ['Behemoth Blade', 'Sacred Sword', 'Close Combat']
            },
            'Zamazenta': {
                'signature_moves': ['Behemoth Bash'],
                'japanese_names': ['きょじゅうだん'],
                'typing': ['Fighting', 'Steel'],
                'distinguishing_moves': ['Behemoth Bash', 'Body Press', 'Close Combat']
            },
            
            # Treasures of Ruin
            'Chi-Yu': {
                'signature_moves': ['Ruination'],
                'japanese_names': ['カタストロフィ'],
                'typing': ['Dark', 'Fire'],
                'distinguishing_moves': ['Ruination', 'Heat Wave', 'Dark Pulse']
            },
            'Chien-Pao': {
                'signature_moves': ['Ruination'],
                'japanese_names': ['カタストロフィ'],
                'typing': ['Dark', 'Ice'],
                'distinguishing_moves': ['Ruination', 'Icicle Crash', 'Sucker Punch']
            },
            'Ting-Lu': {
                'signature_moves': ['Ruination'],
                'japanese_names': ['カタストロフィ'],
                'typing': ['Dark', 'Ground'],
                'distinguishing_moves': ['Ruination', 'Earthquake', 'Stone Edge']
            },
            'Wo-Chien': {
                'signature_moves': ['Ruination'],
                'japanese_names': ['カタストロフィ'],
                'typing': ['Dark', 'Grass'],
                'distinguishing_moves': ['Ruination', 'Giga Drain', 'Leech Seed']
            }
        }
        
        # COMPREHENSIVE JAPANESE STAT ABBREVIATION DATABASE FOR STRATEGIC REASONING
        self.stat_abbreviations = {
            # Single stat abbreviations (most common)
            'H': 'HP',
            'A': 'Attack', 
            'B': 'Defense',
            'C': 'Special Attack',
            'D': 'Special Defense',
            'S': 'Speed',
            
            # Japanese full names
            'ＨＰ': 'HP',
            'HP': 'HP',
            'ヒットポイント': 'HP',
            '体力': 'HP',
            'こうげき': 'Attack',
            '攻撃': 'Attack', 
            'アタック': 'Attack',
            '物理攻撃': 'Attack',
            'ぼうぎょ': 'Defense',
            '防御': 'Defense',
            'ディフェンス': 'Defense',
            '物理防御': 'Defense',
            'とくこう': 'Special Attack',
            '特攻': 'Special Attack',
            '特殊攻撃': 'Special Attack',
            'とくしゅこうげき': 'Special Attack',
            'とくぼう': 'Special Defense',
            '特防': 'Special Defense',
            '特殊防御': 'Special Defense',
            'とくしゅぼうぎょ': 'Special Defense',
            'すばやさ': 'Speed',
            '素早さ': 'Speed',
            'スピード': 'Speed',
            '速さ': 'Speed',
            
            # Common stat combinations used in Japanese VGC
            'CS': 'Special Attack and Speed',
            'AS': 'Attack and Speed',
            'HA': 'HP and Attack',
            'HB': 'HP and Defense', 
            'HC': 'HP and Special Attack',
            'HD': 'HP and Special Defense',
            'HS': 'HP and Speed',
            'AB': 'Attack and Defense',
            'AC': 'Attack and Special Attack',
            'AD': 'Attack and Special Defense',
            'BC': 'Defense and Special Attack',
            'BD': 'Defense and Special Defense',
            'BS': 'Defense and Speed',
            'CD': 'Special Attack and Special Defense',
            
            # Technical terms with stats
            'H252': '252 HP',
            'A252': '252 Attack',
            'B252': '252 Defense', 
            'C252': '252 Special Attack',
            'D252': '252 Special Defense',
            'S252': '252 Speed',
            'H4': '4 HP',
            'A4': '4 Attack',
            'B4': '4 Defense',
            'C4': '4 Special Attack', 
            'D4': '4 Special Defense',
            'S4': '4 Speed',
            
            # Common EV amounts
            'H244': '244 HP',
            'H220': '220 HP',
            'H196': '196 HP',
            'H172': '172 HP',
            'H156': '156 HP',
            'H140': '140 HP',
            'H116': '116 HP',
            'H100': '100 HP',
            'H84': '84 HP',
            'H68': '68 HP',
            'H52': '52 HP',
            'H36': '36 HP',
            'H28': '28 HP',
            'H20': '20 HP',
            'H12': '12 HP',
            
            'B244': '244 Defense',
            'B220': '220 Defense',
            'B196': '196 Defense',
            'B172': '172 Defense',
            'B156': '156 Defense',
            'B140': '140 Defense',
            'B116': '116 Defense',
            'B100': '100 Defense',
            'B84': '84 Defense',
            'B68': '68 Defense',
            'B52': '52 Defense',
            'B36': '36 Defense',
            'B28': '28 Defense',
            'B20': '20 Defense',
            'B12': '12 Defense',
            
            'D244': '244 Special Defense',
            'D220': '220 Special Defense',
            'D196': '196 Special Defense',
            'D172': '172 Special Defense',
            'D156': '156 Special Defense',
            'D140': '140 Special Defense',
            'D116': '116 Special Defense',
            'D100': '100 Special Defense',
            'D84': '84 Special Defense',
            'D68': '68 Special Defense',
            'D52': '52 Special Defense',
            'D36': '36 Special Defense',
            'D28': '28 Special Defense',
            'D20': '20 Special Defense',
            'D12': '12 Special Defense',
            
            'S244': '244 Speed',
            'S220': '220 Speed',
            'S196': '196 Speed',
            'S172': '172 Speed',
            'S156': '156 Speed',
            'S140': '140 Speed',
            'S116': '116 Speed',
            'S100': '100 Speed',
            'S84': '84 Speed',
            'S68': '68 Speed',
            'S52': '52 Speed',
            'S36': '36 Speed',
            'S28': '28 Speed',
            'S20': '20 Speed',
            'S12': '12 Speed',
            
            # Max/min terminology
            'CS振り': 'Special Attack and Speed investment',
            'AS振り': 'Attack and Speed investment', 
            'CS極振り': 'max Special Attack and Speed',
            'AS極振り': 'max Attack and Speed',
            'H極振り': 'max HP',
            'B極振り': 'max Defense',
            'D極振り': 'max Special Defense',
            
            # Technical optimizations
            '11n': 'multiple of 11',
            '16n-1': '1 less than multiple of 16',
            '4n': 'multiple of 4',
            '8n': 'multiple of 8',
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
    
    def translate_strategic_reasoning_stats(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        ULTRA-CRITICAL: Translate Japanese stat abbreviations in strategic reasoning to English
        
        Converts abbreviated strategic reasoning like:
        "CS max. B investment was tested..."
        To:
        "Special Attack and Speed max. Defense investment was tested..."
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Updated result with translated stat abbreviations in ev_explanation fields
        """
        if not isinstance(result.get("pokemon_team"), list):
            return result
        
        translation_notes = []
        
        for i, pokemon in enumerate(result["pokemon_team"]):
            if isinstance(pokemon, dict) and "ev_explanation" in pokemon:
                original_explanation = pokemon["ev_explanation"]
                pokemon_name = pokemon.get('name', f'Pokemon {i+1}')
                
                
                if original_explanation and original_explanation not in ["Not specified", ""]:
                    translated_explanation = self._translate_stat_abbreviations(original_explanation)
                    
                    
                    if translated_explanation != original_explanation:
                        pokemon["ev_explanation"] = translated_explanation
                        translation_notes.append(f"Translated stat abbreviations for {pokemon_name}")
        
        # Add translation notes if any stat abbreviations were translated
        if translation_notes:
            existing_notes = result.get("translation_notes", "")
            stat_translation_text = " | ".join(translation_notes)
            if existing_notes:
                result["translation_notes"] = f"{existing_notes} | Stat Translation: {stat_translation_text}"
            else:
                result["translation_notes"] = f"Stat Translation: {stat_translation_text}"
        
        return result
    
    def _translate_stat_abbreviations(self, text: str) -> str:
        """
        Translate Japanese stat abbreviations in text to English
        
        Args:
            text: Text containing potential stat abbreviations
            
        Returns:
            Text with stat abbreviations translated to English
        """
        if not text:
            return text
        
        
        # Create a working copy of the text
        translated_text = text
        
        # Sort stat abbreviations by length (longest first) to avoid partial matches
        # E.g., "CS" should be matched before "C" or "S" individually
        sorted_abbreviations = sorted(self.stat_abbreviations.items(), key=lambda x: len(x[0]), reverse=True)
        
        import re
        
        changes_made = 0
        
        for japanese_term, english_term in sorted_abbreviations:
            # Skip very long terms that are unlikely to be abbreviations in this context
            if len(japanese_term) > 10:
                continue
            
            # Skip single letters that are likely common English words in certain contexts
            if len(japanese_term) == 1:
                # Check if this single letter appears in contexts that suggest it's not a stat
                common_english_contexts = [
                    rf'\b{japanese_term}\s+(?:lot|bit|few|many|good|bad|great|strong|weak|nice|cool)',
                    rf'\b(?:what|such|quite|very|really|pretty|rather)\s+{japanese_term}\s',
                    rf'\b{japanese_term}(?:bout|way|fter|gain|lso|ccording|bout|nd)\b',
                    rf'\b(?:as|is|was|am|are|be|an|or|of|to|in|on|at|by|for|with|about)\s+{japanese_term}\s+(?:and|or|the|a|an|of|to|in|on|at|by|for|with|about|but|so|if|when|where|while|because|though|although|since|unless|until|before|after|during)',
                ]
                # Skip if any common English pattern is found
                should_skip = any(re.search(pattern, translated_text, re.IGNORECASE) for pattern in common_english_contexts)
                if should_skip:
                    continue
                
            # Create patterns for different contexts where stat abbreviations appear
            patterns = [
                # Pattern 1: Stat abbreviation followed by colon (e.g., "S: Fastest Urshifu")
                rf'\b{re.escape(japanese_term)}:',
                # Pattern 2: Stat abbreviation with numbers (e.g., "H252", "B4")
                rf'\b{re.escape(japanese_term)}(?=\d)',
                # Pattern 3: Stat abbreviation followed by space and word (e.g., "CS max")
                rf'\b{re.escape(japanese_term)}(?=\s+(?:max|極|振り|投資|調整|意識))',
                # Pattern 4: Stat abbreviation in specific stat contexts - simplified
                rf'(?:lower|raise|invest)\s+{re.escape(japanese_term)}(?=\s|$|\.)',
                # Pattern 5: Stat abbreviation at start of sentence
                rf'^{re.escape(japanese_term)}(?=\s|:)',
                # Pattern 6: Stat abbreviation with Japanese particles
                rf'{re.escape(japanese_term)}(?=[をにはがと])',
                # Pattern 7: More conservative context matching for single letters
                rf'(?<=lower)\s+{re.escape(japanese_term)}(?=\s+(?:too|much))',
            ]
            
            for i, pattern in enumerate(patterns):
                # Check if pattern matches before trying to replace
                if re.search(pattern, translated_text, flags=re.IGNORECASE):
                    
                    # Replace the pattern with the English translation
                    def replace_func(match):
                        matched_text = match.group()
                        
                        # Preserve punctuation and formatting
                        if matched_text.endswith(':'):
                            return f"{english_term}:"
                        elif re.search(r'\d', matched_text):
                            # For patterns like H252, B4, etc., extract the number
                            number_match = re.search(r'\d+', matched_text)
                            if number_match:
                                number = number_match.group()
                                return f"{number} {english_term}"
                        elif i == 3:  # Pattern 4: context words like "lower H"
                            # Extract context word and preserve it
                            context_match = re.search(r'(lower|raise|invest)\s+', matched_text, re.IGNORECASE)
                            if context_match:
                                context_word = context_match.group(1)
                                return f"{context_word} {english_term}"
                            else:
                                return english_term
                        else:
                            return english_term
                    
                    old_text = translated_text
                    translated_text = re.sub(pattern, replace_func, translated_text, flags=re.IGNORECASE)
                    if translated_text != old_text:
                        changes_made += 1
        
        
        # Post-processing: Clean up common issues
        translated_text = self._clean_up_stat_translation(translated_text)
        
        return translated_text
    
    def _clean_up_stat_translation(self, text: str) -> str:
        """
        Clean up common translation artifacts and improve readability
        
        Args:
            text: Text that may have translation artifacts
            
        Returns:
            Cleaned up text
        """
        if not text:
            return text
        
        # Define cleanup patterns
        cleanup_patterns = [
            # Fix double spaces
            (r'\s+', ' '),
            # Fix spacing around punctuation
            (r'\s+([,.!?;:])', r'\1'),
            (r'([,.!?;:])\s*([a-zA-Z])', r'\1 \2'),
            # Capitalize first letter after periods
            (r'(\. )([a-z])', lambda m: m.group(1) + m.group(2).upper()),
            # Fix common word combinations
            (r'Special Attack and Speed max', 'max Special Attack and Speed'),
            (r'Attack and Speed max', 'max Attack and Speed'),
            (r'HP and Defense max', 'max HP and Defense'),
            # Fix "max" positioning
            (r'(\w+) max\.', r'max \1.'),
            # Standardize technical terms
            (r'multiple of 11 HP', 'HP multiple of 11'),
            (r'1 less than multiple of 16 HP', 'HP 1 less than multiple of 16'),
        ]
        
        cleaned_text = text
        for pattern, replacement in cleanup_patterns:
            if callable(replacement):
                cleaned_text = re.sub(pattern, replacement, cleaned_text)
            else:
                cleaned_text = re.sub(pattern, replacement, cleaned_text)
        
        return cleaned_text.strip()
    
    def validate_pokemon_moves_consistency(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        ULTRA-CRITICAL: Validate Pokemon identification using signature moves
        This prevents confusion between similar Pokemon like Calyrex vs Kyurem forms
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Updated result with move-based validation and corrections
        """
        if not isinstance(result.get("pokemon_team"), list):
            return result
        
        validation_notes = []
        corrections_made = []
        
        for pokemon in result["pokemon_team"]:
            if isinstance(pokemon, dict) and "name" in pokemon:
                pokemon_name = pokemon["name"]
                pokemon_moves = pokemon.get("moves", [])
                
                if pokemon_moves and pokemon_name in self.signature_moves:
                    # Check if signature moves match
                    expected_data = self.signature_moves[pokemon_name]
                    signature_moves = expected_data['signature_moves']
                    distinguishing_moves = expected_data.get('distinguishing_moves', [])
                    
                    # Check for signature move presence
                    has_signature = any(move in pokemon_moves for move in signature_moves)
                    has_distinguishing = any(move in pokemon_moves for move in distinguishing_moves)
                    
                    if has_signature:
                        validation_notes.append(f"{pokemon_name}: Confirmed by signature move")
                    elif not has_signature and not has_distinguishing:
                        # No signature or distinguishing moves - this might be misidentified
                        validation_notes.append(f"{pokemon_name}: WARNING - No signature moves detected")
                
                # CRITICAL: Check for potential Calyrex vs Kyurem confusion
                confusion_check = self._check_calyrex_kyurem_confusion(pokemon_name, pokemon_moves)
                if confusion_check:
                    validation_notes.append(confusion_check)
                    # Apply correction if confident
                    corrected_name = self._suggest_correct_identification(pokemon_name, pokemon_moves)
                    if corrected_name and corrected_name != pokemon_name:
                        corrections_made.append(f"Corrected {pokemon_name} → {corrected_name} based on moves")
                        pokemon["name"] = corrected_name
        
        # Add validation notes to result
        if validation_notes or corrections_made:
            existing_notes = result.get("translation_notes", "")
            all_notes = validation_notes + corrections_made
            validation_text = " | ".join(all_notes)
            if existing_notes:
                result["translation_notes"] = f"{existing_notes} | Move Validation: {validation_text}"
            else:
                result["translation_notes"] = f"Move Validation: {validation_text}"
        
        return result
    
    def _check_calyrex_kyurem_confusion(self, pokemon_name: str, moves: List[str]) -> str:
        """Check for specific Calyrex vs Kyurem confusion based on moves"""
        if not moves:
            return ""
        
        # Check Calyrex-Ice vs Kyurem-White confusion
        if pokemon_name in ['Calyrex-Ice', 'Kyurem-White']:
            if 'Glacial Lance' in moves:
                if pokemon_name == 'Kyurem-White':
                    return "CRITICAL: Pokemon has Glacial Lance but identified as Kyurem-White (should be Calyrex-Ice)"
            elif 'Ice Burn' in moves:
                if pokemon_name == 'Calyrex-Ice':
                    return "CRITICAL: Pokemon has Ice Burn but identified as Calyrex-Ice (should be Kyurem-White)"
        
        # Check Calyrex-Shadow vs Kyurem-Black confusion  
        if pokemon_name in ['Calyrex-Shadow', 'Kyurem-Black']:
            if 'Astral Barrage' in moves:
                if pokemon_name == 'Kyurem-Black':
                    return "CRITICAL: Pokemon has Astral Barrage but identified as Kyurem-Black (should be Calyrex-Shadow)"
            elif 'Freeze Shock' in moves:
                if pokemon_name == 'Calyrex-Shadow':
                    return "CRITICAL: Pokemon has Freeze Shock but identified as Calyrex-Shadow (should be Kyurem-Black)"
        
        return ""
    
    def _suggest_correct_identification(self, pokemon_name: str, moves: List[str]) -> str:
        """Suggest correct Pokemon identification based on signature moves"""
        if not moves:
            return pokemon_name
        
        # Check all signature moves for a match
        for correct_name, move_data in self.signature_moves.items():
            signature_moves = move_data['signature_moves']
            if any(move in moves for move in signature_moves):
                return correct_name
        
        return pokemon_name
    
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