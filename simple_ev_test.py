#!/usr/bin/env python3
"""
Simple EV detection test - Windows compatible
"""

import sys
from pathlib import Path
import json
import os

# Set UTF-8 encoding for output
os.environ["PYTHONIOENCODING"] = "utf-8"

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer

def test_single_url(url, description):
    """Test a single URL"""
    print(f"\n===== TESTING {description} =====")
    print(f"URL: {url}")
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        # Validate and scrape
        if not analyzer.validate_url(url):
            print("ERROR: URL validation failed")
            return False
            
        scraped_content = analyzer.scrape_article(url)
        if not scraped_content:
            print("ERROR: Content scraping failed")
            return False
            
        print(f"SUCCESS: Scraped {len(scraped_content)} characters")
        
        # Analyze (skip content preview to avoid Unicode issues)
        result = analyzer.analyze_article_with_images(scraped_content, url)
        
        if not result:
            print("ERROR: Analysis failed")
            return False
            
        print("SUCCESS: Analysis completed")
        
        # Check Pokemon team
        pokemon_team = result.get("pokemon_team", [])
        print(f"Pokemon found: {len(pokemon_team)}")
        
        if not pokemon_team:
            print("ERROR: No Pokemon detected")
            return False
            
        # Check each Pokemon
        complete_count = 0
        for i, pokemon in enumerate(pokemon_team, 1):
            name = pokemon.get('name', 'Unknown')
            
            # Check EV spread
            ev_spread = pokemon.get('ev_spread', {})
            has_evs = ev_spread and any(v > 0 for v in ev_spread.values() if isinstance(v, int))
            
            # Check other data
            has_item = pokemon.get('item') and pokemon.get('item') != "Unknown"
            has_moves = len(pokemon.get('moves', [])) >= 4
            has_ability = pokemon.get('ability') and pokemon.get('ability') != "Unknown"
            
            ev_total = sum(v for v in ev_spread.values() if isinstance(v, int)) if ev_spread else 0
            
            print(f"  Pokemon {i}: {name}")
            print(f"    EV Spread: {has_evs} (Total: {ev_total})")
            print(f"    Item: {has_item} ({pokemon.get('item', 'None')})")
            print(f"    Moves: {has_moves} ({len(pokemon.get('moves', []))} moves)")
            print(f"    Ability: {has_ability} ({pokemon.get('ability', 'None')})")
            
            if has_evs and has_item and has_moves and has_ability:
                complete_count += 1
                print(f"    Status: COMPLETE")
            else:
                print(f"    Status: INCOMPLETE")
        
        # Save results
        filename = f"test_{description.lower().replace(' ', '_')}_results.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        success_rate = complete_count / len(pokemon_team) * 100
        print(f"\nRESULT: {complete_count}/{len(pokemon_team)} complete ({success_rate:.1f}%)")
        print(f"Saved to: {filename}")
        
        return complete_count == len(pokemon_team)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return False

def main():
    print("=== POKEMON VGC EV DETECTION TEST ===")
    
    # Test the two URLs
    results = []
    
    # Test 1: Hatenablog
    success1 = test_single_url(
        "https://yunu.hatenablog.jp/entry/2025/06/03/205211",
        "Hatenablog Article"
    )
    results.append(("Hatenablog", success1))
    
    # Test 2: Note.com
    success2 = test_single_url(
        "https://note.com/bright_ixora372/n/nd5515195c993", 
        "Note.com Article"
    )
    results.append(("Note.com", success2))
    
    # Summary
    print(f"\n===== FINAL RESULTS =====")
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, success in results if success)
    print(f"Overall: {passed}/{len(results)} passed")
    
    if passed == len(results):
        print("SUCCESS: All tests passed!")
    else:
        print("WARNING: Some tests failed")

if __name__ == "__main__":
    main()