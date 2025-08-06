#!/usr/bin/env python3

# Test script to debug Pokemon parsing

test_summary = """
TITLE: シーズン32ダブル最終14位ザマ黒馬チョッキパオカイ (Season 32 Doubles Final Rank 14 Zamazenta Black Rider Assault Vest Chien-Pao)

**Pokémon 1: Calyrex Ice Rider**
- Ability: As One
- Held Item: Focus Sash
- Tera Type: Ghost
- Moves: Astral Barrage / Psychic / Encore / Protect
- EV Spread: 4 Def / 252 SpA / 252 Spe
- Nature: Timid
- EV Explanation: The EV spread is 252 Special Attack, 252 Speed, and the remaining 4 EVs are in Defense. The article mentions that the Special Attack and Speed are maximised.

**Pokémon 2: Zamazenta**
- Ability: Dauntless Shield
- Held Item: Rusted Shield
- Tera Type: Fighting
- Moves: Body Press / Crunch / Protect / Wide Guard
- EV Spread: 252 HP / 4 Atk / 252 Def
- Nature: Impish
- EV Explanation: Maximum HP and Defense investment for bulk, with Impish nature to boost Defense further.

**Pokémon 3: Chien-Pao**
- Ability: Sword of Ruin
- Held Item: Assault Vest
- Tera Type: Ice
- Moves: Icicle Crash / Sucker Punch / Sacred Sword / Throat Chop
- EV Spread: 4 HP / 252 Atk / 252 Spe
- Nature: Jolly
- EV Explanation: Standard physical attacker spread with maximum Attack and Speed.

**Pokémon 4: Urshifu-Rapid-Strike**
- Ability: Unseen Fist
- Held Item: Choice Band
- Tera Type: Water
- Moves: Surging Strikes / Aqua Jet / Close Combat / U-turn
- EV Spread: 4 HP / 252 Atk / 252 Spe
- Nature: Jolly
- EV Explanation: Maximum Attack and Speed for optimal damage output.

**Pokémon 5: Rillaboom**
- Ability: Grassy Surge
- Held Item: Life Orb
- Tera Type: Grass
- Moves: Grassy Glide / Wood Hammer / U-turn / Fake Out
- EV Spread: 4 HP / 252 Atk / 252 Spe
- Nature: Adamant
- EV Explanation: Maximum Attack with Adamant nature for power, maximum Speed for priority.

**Pokémon 6: Amoonguss**
- Ability: Regenerator
- Held Item: Rocky Helmet
- Tera Type: Water
- Moves: Spore / Rage Powder / Pollen Puff / Protect
- EV Spread: 252 HP / 4 Def / 252 SpA
- Nature: Quiet
- EV Explanation: Maximum HP for bulk, some Special Attack investment for Pollen Puff damage.

## Team Strengths
- Strong offensive pressure with Chien-Pao and Urshifu
- Good defensive core with Zamazenta and Amoonguss
- Grassy Terrain support from Rillaboom
- Versatile Tera options for different matchups

## Notable Weaknesses
- Vulnerable to Flying-type attacks
- Limited special bulk outside of Zamazenta
- Reliant on positioning for optimal performance
"""

def parse_pokemon_alternative(summary):
    """Alternative parsing method for Pokemon data from Gemini output"""
    teams = []
    lines = summary.split('\n')
    current_pokemon = None
    print(f"DEBUG: Starting alternative parsing with {len(lines)} lines")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for the exact Gemini format: **Pokémon X: [Name]**
        if line.startswith('**Pokémon ') and ':' in line and line.endswith('**'):
            # Save previous pokemon
            if current_pokemon:
                teams.append(current_pokemon)
                print(f"DEBUG: Added Pokemon: {current_pokemon['name']}")
            
            # Extract pokemon name - format is **Pokémon 1: Name**
            name_part = line.split(':', 1)[1].strip().replace('**', '').strip()
            print(f"DEBUG: Found Pokemon: {name_part}")
            current_pokemon = {
                'name': name_part,
                'ability': 'Not specified',
                'item': 'Not specified',
                'tera_type': 'Not specified',
                'moves': [],
                'evs': {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
                'nature': 'Not specified',
                'ev_explanation': 'Not specified'
            }
            continue
            
        # Also try alternative formats in case the format varies
        alt_patterns = [
            line.startswith('**Pokemon ') and ':' in line,
            line.startswith('Pokemon ') and ':' in line,
            line.startswith('**') and 'Pokemon' in line and ':' in line
        ]
        
        if any(alt_patterns):
            # Save previous pokemon
            if current_pokemon:
                teams.append(current_pokemon)
                print(f"DEBUG: Added Pokemon (alt): {current_pokemon['name']}")
            
            # Extract pokemon name from various formats
            if ':' in line:
                name_part = line.split(':', 1)[1].strip().replace('**', '').strip()
            else:
                name_part = line.replace('**', '').replace('Pokemon ', '').replace('Pokémon ', '').strip()
            
            print(f"DEBUG: Found Pokemon (alt): {name_part}")
            current_pokemon = {
                'name': name_part,
                'ability': 'Not specified',
                'item': 'Not specified',
                'tera_type': 'Not specified',
                'moves': [],
                'evs': {'hp': 0, 'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0},
                'nature': 'Not specified',
                'ev_explanation': 'Not specified'
            }
            continue
            
        if current_pokemon:
            # Parse different fields exactly as Gemini outputs them
            if line.startswith('- Ability:'):
                current_pokemon['ability'] = line.replace('- Ability:', '').strip()
            elif line.startswith('- Held Item:'):
                current_pokemon['item'] = line.replace('- Held Item:', '').strip()
            elif line.startswith('- Tera Type:'):
                current_pokemon['tera_type'] = line.replace('- Tera Type:', '').strip()
            elif line.startswith('- Nature:'):
                current_pokemon['nature'] = line.replace('- Nature:', '').strip()
            elif line.startswith('- Moves:'):
                moves_text = line.replace('- Moves:', '').strip()
                if '/' in moves_text:
                    current_pokemon['moves'] = [move.strip() for move in moves_text.split('/') if move.strip()]
                elif ',' in moves_text:
                    current_pokemon['moves'] = [move.strip() for move in moves_text.split(',') if move.strip()]
                else:
                    current_pokemon['moves'] = [moves_text] if moves_text else []
            elif line.startswith('- EV Spread:'):
                ev_text = line.replace('- EV Spread:', '').strip()
                # Parse EV format like "252 0 4 252 0 0" (HP Atk Def SpA SpD Spe)
                ev_values = ev_text.split()
                if len(ev_values) >= 6:
                    try:
                        current_pokemon['evs'] = {
                            'hp': int(ev_values[0]),
                            'atk': int(ev_values[1]),
                            'def': int(ev_values[2]),
                            'spa': int(ev_values[3]),
                            'spd': int(ev_values[4]),
                            'spe': int(ev_values[5])
                        }
                    except (ValueError, IndexError):
                        pass
            elif line.startswith('- EV Explanation:'):
                # Collect multi-line explanation
                explanation_lines = [line.replace('- EV Explanation:', '').strip()]
                j = i + 1
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith('**Pokémon') and not lines[j].strip().startswith('- '):
                    explanation_lines.append(lines[j].strip())
                    j += 1
                current_pokemon['ev_explanation'] = ' '.join(explanation_lines)
    
    # Don't forget the last pokemon
    if current_pokemon:
        teams.append(current_pokemon)
        print(f"DEBUG: Added final Pokemon: {current_pokemon['name']}")
    
    print(f"DEBUG: Total teams found: {len(teams)}")
    return teams

if __name__ == "__main__":
    print("Testing Pokemon parsing...")
    teams = parse_pokemon_alternative(test_summary)
    print(f"\nFound {len(teams)} Pokemon:")
    for i, pokemon in enumerate(teams, 1):
        print(f"\n{i}. {pokemon['name']}")
        print(f"   Ability: {pokemon['ability']}")
        print(f"   Item: {pokemon['item']}")
        print(f"   Tera: {pokemon['tera_type']}")
        print(f"   Moves: {pokemon['moves']}")
        print(f"   EVs: {pokemon['evs']}")
        print(f"   Nature: {pokemon['nature']}")
