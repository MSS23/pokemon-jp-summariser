#!/usr/bin/env python3
"""
Test script for Pokemon identification improvements
Tests the critical fixes for Grimmsnarl, Calyrex vs Kyurem forms, and signature move validation
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.pokemon_validator import PokemonValidator

def test_pokemon_translations():
    """Test the updated Pokemon translation database"""
    print("=== TESTING POKEMON TRANSLATION DATABASE ===")
    
    validator = PokemonValidator()
    
    # Test critical missing Pokemon
    test_cases = [
        # Grimmsnarl (was completely missing)
        ('オーロンゲ', 'Grimmsnarl'),
        
        # Calyrex forms
        ('バドレックス-はくばじょう', 'Calyrex-Ice'),
        ('バドレックス-こくばじょう', 'Calyrex-Shadow'),
        ('はくばじょうバドレックス', 'Calyrex-Ice'),
        ('こくばじょうバドレックス', 'Calyrex-Shadow'),
        ('白馬', 'Calyrex-Ice'),
        ('黒馬', 'Calyrex-Shadow'),
        
        # Kyurem forms (to distinguish from Calyrex)
        ('キュレム-ホワイト', 'Kyurem-White'),
        ('キュレム-ブラック', 'Kyurem-Black'),
        ('ホワイトキュレム', 'Kyurem-White'),
        ('ブラックキュレム', 'Kyurem-Black'),
        
        # Other missing Pokemon
        ('ドラパルト', 'Dragapult'),
        ('アーマーガア', 'Corviknight'),
        ('ミミッキュ', 'Mimikyu'),
    ]
    
    print("Testing Pokemon name translations...")
    all_passed = True
    
    for japanese_name, expected_english in test_cases:
        corrected_name = validator._correct_pokemon_name(japanese_name)
        if corrected_name == expected_english:
            print(f"PASS: JP_NAME -> {corrected_name}")
        else:
            print(f"FAIL: JP_NAME -> {corrected_name} (expected: {expected_english})")
            all_passed = False
    
    print(f"\nTranslation tests: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed

def test_signature_move_validation():
    """Test signature move validation system"""
    print("\n=== TESTING SIGNATURE MOVE VALIDATION ===")
    
    validator = PokemonValidator()
    
    # Test cases with potential confusion
    test_teams = [
        {
            "name": "Calyrex vs Kyurem Confusion Test",
            "pokemon_team": [
                {
                    "name": "Calyrex-Ice",
                    "moves": ["Glacial Lance", "Trick Room", "Protect", "Substitute"],
                    "expected_validation": "Confirmed by signature move"
                },
                {
                    "name": "Kyurem-White",
                    "moves": ["Ice Burn", "Earth Power", "Focus Blast", "Protect"],
                    "expected_validation": "Confirmed by signature move"
                },
                {
                    "name": "Calyrex-Shadow",
                    "moves": ["Astral Barrage", "Psychic", "Nasty Plot", "Protect"],
                    "expected_validation": "Confirmed by signature move"
                },
                {
                    "name": "Kyurem-Black",
                    "moves": ["Freeze Shock", "Fusion Bolt", "Ice Beam", "Protect"],
                    "expected_validation": "Confirmed by signature move"
                }
            ]
        },
        {
            "name": "Misidentification Detection Test",
            "pokemon_team": [
                {
                    "name": "Kyurem-White",
                    "moves": ["Glacial Lance", "Trick Room", "Protect", "Substitute"],
                    "expected_correction": "Calyrex-Ice"
                },
                {
                    "name": "Calyrex-Ice", 
                    "moves": ["Ice Burn", "Earth Power", "Focus Blast", "Protect"],
                    "expected_correction": "Kyurem-White"
                },
                {
                    "name": "Kyurem-Black",
                    "moves": ["Astral Barrage", "Psychic", "Nasty Plot", "Protect"],
                    "expected_correction": "Calyrex-Shadow"
                },
                {
                    "name": "Calyrex-Shadow",
                    "moves": ["Freeze Shock", "Fusion Bolt", "Ice Beam", "Protect"],
                    "expected_correction": "Kyurem-Black"
                }
            ]
        }
    ]
    
    print("Testing signature move validation...")
    validation_passed = True
    
    for test_case in test_teams:
        print(f"\n--- {test_case['name']} ---")
        
        # Create mock result for testing
        mock_result = {
            "pokemon_team": test_case["pokemon_team"],
            "translation_notes": ""
        }
        
        # Apply signature move validation
        validated_result = validator.validate_pokemon_moves_consistency(mock_result)
        
        # Check results
        for i, pokemon in enumerate(validated_result["pokemon_team"]):
            original_pokemon = test_case["pokemon_team"][i]
            
            if "expected_validation" in original_pokemon:
                # Should confirm the Pokemon is correct
                if original_pokemon["expected_validation"] in validated_result.get("translation_notes", ""):
                    print(f"PASS: {pokemon['name']}: Correctly confirmed")
                else:
                    print(f"FAIL: {pokemon['name']}: Failed to confirm")
                    validation_passed = False
            
            elif "expected_correction" in original_pokemon:
                # Should correct the misidentified Pokemon
                expected_name = original_pokemon["expected_correction"]
                if pokemon["name"] == expected_name:
                    print(f"PASS: {original_pokemon['name']} -> {pokemon['name']}: Correctly corrected")
                else:
                    print(f"FAIL: {original_pokemon['name']} -> {pokemon['name']}: Should be {expected_name}")
                    validation_passed = False
    
    print(f"\nSignature move validation tests: {'ALL PASSED' if validation_passed else 'SOME FAILED'}")
    return validation_passed

def test_comprehensive_identification():
    """Test comprehensive Pokemon identification with real scenarios"""
    print("\n=== TESTING COMPREHENSIVE IDENTIFICATION ===")
    
    validator = PokemonValidator()
    
    # Test realistic team scenarios that might cause confusion
    test_scenarios = [
        {
            "scenario": "Japanese VGC article with restricted Pokemon",
            "mock_analysis": {
                "pokemon_team": [
                    {"name": "オーロンゲ", "moves": ["Light Screen", "Reflect", "Spirit Break", "Thunder Wave"]},
                    {"name": "バドレックス-はくばじょう", "moves": ["Glacial Lance", "Trick Room", "Protect", "Substitute"]},
                    {"name": "ガブリアス", "moves": ["Earthquake", "Dragon Claw", "Stone Edge", "Protect"]},
                    {"name": "ランドロス", "moves": ["Earthquake", "Rock Slide", "U-turn", "Protect"]},
                    {"name": "イーユイ", "moves": ["Ruination", "Overheat", "Dark Pulse", "Protect"]},
                    {"name": "モロバレル", "moves": ["Spore", "Rage Powder", "Pollen Puff", "Protect"]}
                ],
                "translation_notes": ""
            }
        }
    ]
    
    comprehensive_passed = True
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['scenario']} ---")
        
        mock_result = scenario["mock_analysis"]
        
        # Apply all validations
        validated_result = validator.fix_pokemon_name_translations(mock_result)
        validated_result = validator.apply_pokemon_validation(validated_result)
        validated_result = validator.validate_pokemon_moves_consistency(validated_result)
        
        print("Final team composition:")
        for pokemon in validated_result["pokemon_team"]:
            print(f"  - {pokemon['name']}")
        
        # Check that critical Pokemon were translated correctly
        team_names = [p["name"] for p in validated_result["pokemon_team"]]
        
        expected_translations = {
            "Grimmsnarl": "オーロンゲ should translate to Grimmsnarl",
            "Calyrex-Ice": "バドレックス-はくばじょう should translate to Calyrex-Ice",
            "Garchomp": "ガブリアス should translate to Garchomp",
            "Landorus-Therian": "ランドロス should translate to Landorus-Therian",
            "Wo-Chien": "イーユイ should translate to Wo-Chien", 
            "Amoonguss": "モロバレル should translate to Amoonguss"
        }
        
        for expected_name, description in expected_translations.items():
            if expected_name in team_names:
                print(f"PASS: {description}")
            else:
                print(f"FAIL: {description}")
                comprehensive_passed = False
        
        print(f"\nValidation notes: {validated_result.get('translation_notes', 'None')}")
    
    print(f"\nComprehensive identification tests: {'ALL PASSED' if comprehensive_passed else 'SOME FAILED'}")
    return comprehensive_passed

def main():
    """Run all Pokemon identification tests"""
    print("=== TESTING POKEMON IDENTIFICATION IMPROVEMENTS ===")
    print("Testing fixes for: Grimmsnarl, Calyrex vs Kyurem confusion, signature moves\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(test_pokemon_translations())
    test_results.append(test_signature_move_validation())
    test_results.append(test_comprehensive_identification())
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS:")
    
    tests = [
        "Pokemon Translation Database",
        "Signature Move Validation", 
        "Comprehensive Identification"
    ]
    
    all_passed = True
    for i, (test_name, result) in enumerate(zip(tests, test_results)):
        status = "PASSED" if result else "FAILED"
        print(f"{i+1}. {test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOVERALL: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nPokemon identification system is working correctly!")
        print("Grimmsnarl, Calyrex vs Kyurem forms, and signature move validation all fixed!")
    else:
        print("\nSome issues remain - check failed tests above")

if __name__ == "__main__":
    main()