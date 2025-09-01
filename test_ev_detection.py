#!/usr/bin/env python3
"""
Test script to verify enhanced Japanese VGC EV detection
Tests the specific URLs provided by the user to demonstrate functionality
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer

def test_url_analysis(url: str, description: str):
    """Test analysis of a specific URL"""
    print(f"\n{'='*80}")
    print(f"TESTING: {description}")
    print(f"URL: {url}")
    print('='*80)
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        # Validate URL
        print("Step 1: URL Validation...")
        if not analyzer.validate_url(url):
            print("ERROR: URL validation failed")
            return False
        print("SUCCESS: URL is valid and accessible")
        
        # Scrape content
        print("\nStep 2: Content Scraping...")
        scraped_content = analyzer.scrape_article(url)
        if not scraped_content:
            print("ERROR: Content scraping failed")
            return False
        
        print(f"SUCCESS: Scraped content ({len(scraped_content)} characters)")
        print(f"Content preview: {scraped_content[:200]}...")
        
        # Analyze with images
        print("\nStep 3: Analysis with Image Enhancement...")
        result = analyzer.analyze_article_with_images(scraped_content, url)
        
        if not result:
            print("ERROR: Analysis failed - no result returned")
            return False
        
        print("SUCCESS: Analysis completed successfully!")
        
        # Check for Pokemon team
        pokemon_team = result.get("pokemon_team")
        if not pokemon_team:
            print("ERROR: No Pokemon team detected")
            return False
            
        print(f"Pokemon Team Detected: {len(pokemon_team)} Pokemon")
        
        # Detailed Pokemon analysis
        print("\nStep 4: Detailed Pokemon Data Verification...")
        for i, pokemon in enumerate(pokemon_team, 1):
            print(f"\nPokemon {i}: {pokemon.get('name', 'Unknown')}")
            
            # Check EV spread (most important)
            ev_spread = pokemon.get('ev_spread')
            if ev_spread and any(v > 0 for v in ev_spread.values() if isinstance(v, int)):
                print(f"  SUCCESS EV Spread: {ev_spread}")
            else:
                print(f"  ERROR EV Spread: Missing or empty ({ev_spread})")
            
            # Check other required data
            item = pokemon.get('item')
            if item and item != "Unknown":
                print(f"  SUCCESS Item: {item}")
            else:
                print(f"  ERROR Item: Missing ({item})")
            
            moves = pokemon.get('moves', [])
            if moves and len(moves) >= 4:
                print(f"  SUCCESS Moves: {len(moves)} moves - {', '.join(moves[:4])}")
            else:
                print(f"  ERROR Moves: Incomplete ({len(moves)} moves) - {moves}")
            
            ability = pokemon.get('ability')
            if ability and ability != "Unknown":
                print(f"  SUCCESS Ability: {ability}")
            else:
                print(f"  ERROR Ability: Missing ({ability})")
        
        # Summary
        complete_pokemon = []
        for pokemon in pokemon_team:
            ev_spread = pokemon.get('ev_spread')
            has_evs = ev_spread and any(v > 0 for v in ev_spread.values() if isinstance(v, int))
            has_item = pokemon.get('item') and pokemon.get('item') != "Unknown"
            has_moves = pokemon.get('moves') and len(pokemon.get('moves', [])) >= 4
            has_ability = pokemon.get('ability') and pokemon.get('ability') != "Unknown"
            
            if has_evs and has_item and has_moves and has_ability:
                complete_pokemon.append(pokemon.get('name', 'Unknown'))
        
        print(f"\nSUMMARY:")
        print(f"  Total Pokemon: {len(pokemon_team)}")
        print(f"  Complete Pokemon (EV+Item+4Moves+Ability): {len(complete_pokemon)}")
        print(f"  Success Rate: {len(complete_pokemon)}/{len(pokemon_team)} ({100*len(complete_pokemon)/len(pokemon_team):.1f}%)")
        
        if complete_pokemon:
            print(f"  Complete Pokemon: {', '.join(complete_pokemon)}")
        
        # Save detailed results
        output_file = f"test_results_{description.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Detailed results saved to: {output_file}")
        
        return len(complete_pokemon) == len(pokemon_team)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("POKEMON VGC EV DETECTION TEST")
    print("Testing enhanced Japanese VGC analysis capabilities")
    
    # Test URLs provided by user
    test_urls = [
        ("https://yunu.hatenablog.jp/entry/2025/06/03/205211", "Hatenablog VGC Article"),
        ("https://note.com/bright_ixora372/n/nd5515195c993", "Note.com VGC Article")
    ]
    
    results = []
    for url, description in test_urls:
        success = test_url_analysis(url, description)
        results.append((description, success))
    
    # Final summary
    print(f"\n{'='*80}")
    print("FINAL TEST RESULTS")
    print('='*80)
    
    for description, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{status} {description}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\nOverall Success Rate: {total_success}/{len(results)} ({100*total_success/len(results):.1f}%)")
    
    if total_success == len(results):
        print("ALL TESTS PASSED! EV detection is working perfectly!")
    else:
        print("Some tests failed. Review the detailed output above.")

if __name__ == "__main__":
    main()