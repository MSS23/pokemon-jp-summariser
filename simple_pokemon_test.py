#!/usr/bin/env python3
"""
Simple test for Pokemon identification improvements - Unicode-safe
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.pokemon_validator import PokemonValidator

def main():
    print("=== POKEMON IDENTIFICATION TEST RESULTS ===")
    
    validator = PokemonValidator()
    
    # Test critical fixes
    print("\n1. Grimmsnarl Translation:")
    result = validator._correct_pokemon_name("オーロンゲ")
    print(f"   Result: {result} {'PASS' if result == 'Grimmsnarl' else 'FAIL'}")
    
    print("\n2. Calyrex Forms:")
    calyrex_ice = validator._correct_pokemon_name("バドレックス-はくばじょう")
    calyrex_shadow = validator._correct_pokemon_name("バドレックス-こくばじょう")
    print(f"   Calyrex-Ice: {calyrex_ice} {'PASS' if calyrex_ice == 'Calyrex-Ice' else 'FAIL'}")
    print(f"   Calyrex-Shadow: {calyrex_shadow} {'PASS' if calyrex_shadow == 'Calyrex-Shadow' else 'FAIL'}")
    
    print("\n3. Kyurem Forms (distinct from Calyrex):")
    kyurem_white = validator._correct_pokemon_name("キュレム-ホワイト")
    kyurem_black = validator._correct_pokemon_name("キュレム-ブラック")
    print(f"   Kyurem-White: {kyurem_white} {'PASS' if kyurem_white == 'Kyurem-White' else 'FAIL'}")
    print(f"   Kyurem-Black: {kyurem_black} {'PASS' if kyurem_black == 'Kyurem-Black' else 'FAIL'}")
    
    print("\n4. Signature Move Validation:")
    test_result = {
        "pokemon_team": [
            {"name": "Calyrex-Shadow", "moves": ["Astral Barrage", "Psychic", "Protect", "Substitute"]},
            {"name": "Kyurem-White", "moves": ["Ice Burn", "Earth Power", "Focus Blast", "Protect"]}
        ],
        "translation_notes": ""
    }
    
    validated = validator.validate_pokemon_moves_consistency(test_result)
    signature_validation_works = "Confirmed by signature move" in validated.get("translation_notes", "")
    print(f"   Signature moves detected: {'PASS' if signature_validation_works else 'FAIL'}")
    
    # Summary
    all_tests = [
        result == 'Grimmsnarl',
        calyrex_ice == 'Calyrex-Ice',
        calyrex_shadow == 'Calyrex-Shadow', 
        kyurem_white == 'Kyurem-White',
        kyurem_black == 'Kyurem-Black',
        signature_validation_works
    ]
    
    print(f"\n=== SUMMARY ===")
    print(f"Tests passed: {sum(all_tests)}/{len(all_tests)}")
    print(f"Status: {'ALL SYSTEMS WORKING' if all(all_tests) else 'ISSUES DETECTED'}")
    
    if all(all_tests):
        print("\nPokemon identification system successfully enhanced!")
        print("Grimmsnarl now properly identified")
        print("Calyrex vs Kyurem forms properly distinguished")  
        print("Signature move validation prevents misidentification")

if __name__ == "__main__":
    main()