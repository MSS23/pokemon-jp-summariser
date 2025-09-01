#!/usr/bin/env python3
"""
Simple test for stat abbreviation translation - ASCII only
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.pokemon_validator import PokemonValidator

def main():
    print("=== STAT ABBREVIATION TRANSLATION TEST ===")
    
    validator = PokemonValidator()
    
    # Test cases
    test_cases = [
        "CS max. B investment was tested",
        "S: Fastest Urshifu +2",
        "I didn't want to lower H too much",
        "so I had to lower B",
        "H252 B4 D156 distribution",
        "AS max with HB focus",
    ]
    
    print("\nTesting individual cases:")
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n{i}. Input:  '{test_input}'")
        translated = validator._translate_stat_abbreviations(test_input)
        print(f"   Output: '{translated}'")
        
        if translated != test_input:
            print("   Status: TRANSLATED")
        else:
            print("   Status: NO CHANGE")
    
    # Test full pipeline
    print("\n=== TESTING FULL PIPELINE ===")
    
    mock_result = {
        "pokemon_team": [
            {
                "name": "Test Pokemon",
                "ev_explanation": "CS max. B investment was tested. S: Fastest base 100. I didn't want to lower H too much, so I had to lower B."
            }
        ],
        "translation_notes": ""
    }
    
    print(f"\nOriginal explanation: {mock_result['pokemon_team'][0]['ev_explanation']}")
    
    translated_result = validator.translate_strategic_reasoning_stats(mock_result)
    final_explanation = translated_result['pokemon_team'][0]['ev_explanation']
    
    print(f"Final explanation:    {final_explanation}")
    
    # Check what translations occurred
    expected_translations = {
        "CS": "Special Attack and Speed",
        "B": "Defense", 
        "S:": "Speed:",
        "H": "HP"
    }
    
    print("\nTranslation check:")
    for abbrev, full_term in expected_translations.items():
        if full_term in final_explanation:
            print(f"  PASS: {abbrev} -> {full_term}")
        else:
            print(f"  FAIL: {abbrev} -> {full_term} (not found)")
    
    # Show translation notes
    notes = translated_result.get("translation_notes", "")
    if notes:
        print(f"\nTranslation notes: {notes}")
    else:
        print("\nNo translation notes generated")

if __name__ == "__main__":
    main()