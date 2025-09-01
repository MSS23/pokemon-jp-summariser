#!/usr/bin/env python3
"""
Test script for Japanese stat abbreviation translation in strategic reasoning
Tests the critical fix to translate abbreviations like H, B, CS to full English terms
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.pokemon_validator import PokemonValidator

def test_stat_abbreviation_translation():
    """Test the stat abbreviation translation function with real examples"""
    print("=== TESTING STAT ABBREVIATION TRANSLATION ===")
    
    validator = PokemonValidator()
    
    # Test cases using real examples from our liberty-note.com results
    test_cases = [
        {
            "name": "Calyrex-Shadow",
            "original": "CS max. B investment was tested to be aware of scarf Suicune, but it was often barely survived because C was reduced, and since OTS can tell the type of Suicune, no adjustment was made.",
            "expected_translations": ["Special Attack and Speed", "Defense", "Special Attack"]
        },
        {
            "name": "Zamazenta", 
            "original": "S: Fastest Urshifu +2. To be faster than the opponent's Zamazenta, S was invested to be aware of Focus Sash Urshifu. For durability, I didn't want to lower H too much considering Life Orb Calyrex, so I had to lower B.",
            "expected_translations": ["Speed:", "Speed", "HP", "Defense"]
        },
        {
            "name": "Test Pokemon 1",
            "original": "H: 11n B: 252振り CS極振り for damage output",
            "expected_translations": ["HP: multiple of 11", "Defense: 252振り", "max Special Attack and Speed"]
        },
        {
            "name": "Test Pokemon 2", 
            "original": "AS max with H244 and D4 for bulk optimization",
            "expected_translations": ["Attack and Speed", "244 HP", "4 Special Defense"]
        },
        {
            "name": "Test Pokemon 3",
            "original": "HB投資でCS削った構成、Sライン調整済み",
            "expected_translations": ["HP and Defense", "Special Attack and Speed", "Speed"]
        }
    ]
    
    print("Testing stat abbreviation translation function...")
    all_passed = True
    
    for test_case in test_cases:
        pokemon_name = test_case["name"]
        original_text = test_case["original"]
        expected_translations = test_case["expected_translations"]
        
        print(f"\n--- {pokemon_name} ---")
        print(f"Original: {original_text}")
        
        # Test the translation function
        translated_text = validator._translate_stat_abbreviations(original_text)
        print(f"Translated: {translated_text}")
        
        # Check if expected translations are present
        translation_success = True
        for expected_term in expected_translations:
            if expected_term.lower() not in translated_text.lower():
                print(f"  MISSING: {expected_term}")
                translation_success = False
                all_passed = False
            else:
                print(f"  FOUND: {expected_term}")
        
        if translation_success:
            print("  RESULT: PASS")
        else:
            print("  RESULT: FAIL")
    
    print(f"\nStat abbreviation translation tests: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed

def test_full_pipeline_translation():
    """Test the full pipeline with stat abbreviation translation"""
    print("\n=== TESTING FULL PIPELINE STAT TRANSLATION ===")
    
    validator = PokemonValidator()
    
    # Create mock analysis result with stat abbreviations (like our real results)
    mock_result = {
        "pokemon_team": [
            {
                "name": "Calyrex-Shadow",
                "ev_explanation": "CS max. B investment was tested to be aware of scarf Suicune, but it was often barely survived because C was reduced, and since OTS can tell the type of Suicune, no adjustment was made.",
                "ev_spread": {"HP": 0, "Attack": 0, "Defense": 4, "Special Attack": 252, "Special Defense": 0, "Speed": 252, "total": 508}
            },
            {
                "name": "Zamazenta",
                "ev_explanation": "S: Fastest Urshifu +2. To be faster than the opponent's Zamazenta, S was invested to be aware of Focus Sash Urshifu. For durability, I didn't want to lower H too much considering Life Orb Calyrex, so I had to lower B.",
                "ev_spread": {"HP": 220, "Attack": 0, "Defense": 156, "Special Attack": 0, "Special Defense": 0, "Speed": 132, "total": 508}
            }
        ],
        "translation_notes": ""
    }
    
    print("Testing full pipeline translation...")
    
    # Apply the stat translation function
    translated_result = validator.translate_strategic_reasoning_stats(mock_result)
    
    # Check results
    pipeline_passed = True
    
    for i, pokemon in enumerate(translated_result["pokemon_team"]):
        pokemon_name = pokemon["name"]
        translated_explanation = pokemon["ev_explanation"]
        
        print(f"\n--- {pokemon_name} ---")
        print(f"Translated Explanation: {translated_explanation}")
        
        # Check for improvements
        if pokemon_name == "Calyrex-Shadow":
            expected_improvements = ["Special Attack and Speed", "Defense", "Special Attack"]
            for improvement in expected_improvements:
                if improvement.lower() in translated_explanation.lower():
                    print(f"  IMPROVED: Found '{improvement}' instead of abbreviation")
                else:
                    print(f"  MISSING: Expected '{improvement}' translation")
                    pipeline_passed = False
        
        elif pokemon_name == "Zamazenta":
            expected_improvements = ["Speed:", "HP", "Defense"]
            for improvement in expected_improvements:
                if improvement.lower() in translated_explanation.lower():
                    print(f"  IMPROVED: Found '{improvement}' instead of abbreviation")
                else:
                    print(f"  MISSING: Expected '{improvement}' translation")
                    pipeline_passed = False
    
    # Check translation notes
    translation_notes = translated_result.get("translation_notes", "")
    if "Stat Translation:" in translation_notes:
        print(f"\nTranslation notes: {translation_notes}")
        print("PASS: Translation notes added")
    else:
        print("FAIL: No translation notes added")
        pipeline_passed = False
    
    print(f"\nFull pipeline translation tests: {'ALL PASSED' if pipeline_passed else 'SOME FAILED'}")
    return pipeline_passed

def test_edge_cases():
    """Test edge cases and special formatting"""
    print("\n=== TESTING EDGE CASES ===")
    
    validator = PokemonValidator()
    
    edge_cases = [
        {
            "name": "Mixed Japanese/English",
            "input": "H252振りでCS極振り、B調整済み",
            "should_contain": ["HP", "Special Attack and Speed", "Defense"]
        },
        {
            "name": "Technical terms",
            "input": "H: 11n for recovery, B: 16n-1 optimization",
            "should_contain": ["HP: multiple of 11", "Defense: 1 less than multiple of 16"]
        },
        {
            "name": "Stat combinations",
            "input": "HB investment with CS削り and AS調整",
            "should_contain": ["HP and Defense", "Special Attack and Speed", "Attack and Speed"]
        },
        {
            "name": "Numbers with stats",
            "input": "H244 B100 D156で耐久重視",
            "should_contain": ["244 HP", "100 Defense", "156 Special Defense"]
        }
    ]
    
    edge_case_passed = True
    
    for test_case in edge_cases:
        name = test_case["name"]
        input_text = test_case["input"]
        should_contain = test_case["should_contain"]
        
        print(f"\n--- {name} ---")
        print(f"Input: {input_text}")
        
        translated = validator._translate_stat_abbreviations(input_text)
        print(f"Output: {translated}")
        
        case_passed = True
        for expected in should_contain:
            if expected.lower() in translated.lower():
                print(f"  PASS: Contains '{expected}'")
            else:
                print(f"  FAIL: Missing '{expected}'")
                case_passed = False
                edge_case_passed = False
        
        if case_passed:
            print("  RESULT: PASS")
        else:
            print("  RESULT: FAIL")
    
    print(f"\nEdge case tests: {'ALL PASSED' if edge_case_passed else 'SOME FAILED'}")
    return edge_case_passed

def main():
    """Run all stat abbreviation translation tests"""
    print("=== JAPANESE STAT ABBREVIATION TRANSLATION TESTS ===")
    print("Testing translation of H->HP, B->Defense, CS->Special Attack and Speed, etc.\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(test_stat_abbreviation_translation())
    test_results.append(test_full_pipeline_translation())
    test_results.append(test_edge_cases())
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS:")
    
    tests = [
        "Stat Abbreviation Translation Function",
        "Full Pipeline Integration",
        "Edge Cases and Special Formatting"
    ]
    
    all_passed = True
    for i, (test_name, result) in enumerate(zip(tests, test_results)):
        status = "PASSED" if result else "FAILED"
        print(f"{i+1}. {test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOVERALL: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nStat abbreviation translation system working correctly!")
        print("Strategic reasoning will now be clear and readable for English users!")
        print("H->HP, B->Defense, CS->Special Attack and Speed translations working!")
    else:
        print("\nSome issues remain - check failed tests above")

if __name__ == "__main__":
    main()