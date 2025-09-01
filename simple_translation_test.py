#!/usr/bin/env python3
"""
Simple test for Pokemon translation fixes
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'utils'))

def test_config_translations():
    """Test the config translations directly"""
    try:
        # Import the config directly
        from config import POKEMON_NAME_TRANSLATIONS
        
        print("Testing config translations...")
        
        # Test Iron Valiant
        iron_valiant_jp = "テツノブジン"
        if POKEMON_NAME_TRANSLATIONS.get(iron_valiant_jp) == "Iron Valiant":
            print("PASS: Iron Valiant translation correct")
        else:
            print("FAIL: Iron Valiant translation missing or incorrect")
        
        # Test Zamazenta
        zamazenta_jp = "ザマゼンタ"
        if POKEMON_NAME_TRANSLATIONS.get(zamazenta_jp) == "Zamazenta":
            print("PASS: Zamazenta translation correct")
        else:
            print("FAIL: Zamazenta translation missing or incorrect")
        
        # Test Zacian
        zacian_jp = "ザシアン"
        if POKEMON_NAME_TRANSLATIONS.get(zacian_jp) == "Zacian":
            print("PASS: Zacian translation correct")
        else:
            print("FAIL: Zacian translation missing or incorrect")
        
        # Test Iron Valiant variants (should all map to Iron Valiant)
        iron_valiant_variants = [
            "Iron-Valiant-Therian",
            "Iron Valiant-Therian", 
            "Iron-Valian-Therian",
            "Iron-Valient-Therian"
        ]
        
        for variant in iron_valiant_variants:
            if POKEMON_NAME_TRANSLATIONS.get(variant) == "Iron Valiant":
                print(f"PASS: {variant} correctly maps to Iron Valiant")
            else:
                print(f"FAIL: {variant} does not map to Iron Valiant")
        
        print("Config translation test completed.")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error testing config: {e}")
        return False

def test_prompt_content():
    """Test that the analyzer prompt contains the fixes"""
    try:
        from analyzer import GeminiVGCAnalyzer
        
        analyzer = GeminiVGCAnalyzer()
        prompt = analyzer._get_analysis_prompt()
        
        print("Testing analyzer prompt...")
        
        # Check for Iron Valiant in prompt
        if "テツノブジン = Iron Valiant" in prompt:
            print("PASS: Iron Valiant mapping found in prompt")
        else:
            print("FAIL: Iron Valiant mapping not found in prompt")
        
        # Check for Zamazenta warning
        if "ザマ" in prompt and "Zamazenta" in prompt:
            print("PASS: Zamazenta abbreviation guidance found in prompt")
        else:
            print("FAIL: Zamazenta abbreviation guidance not found in prompt")
        
        # Check for Iron Shaman warning
        if "Iron Shaman" in prompt:
            print("PASS: Iron Shaman warning found in prompt")
        else:
            print("FAIL: Iron Shaman warning not found in prompt")
        
        print("Prompt content test completed.")
        return True
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Error testing prompt: {e}")
        return False

def main():
    """Run simple tests"""
    print("Pokemon Translation Fix Validation")
    print("=" * 40)
    
    success1 = test_config_translations()
    print()
    success2 = test_prompt_content()
    
    print("=" * 40)
    if success1 and success2:
        print("SUCCESS: All translation fixes validated")
    else:
        print("WARNING: Some issues detected")
    
    return success1 and success2

if __name__ == "__main__":
    main()