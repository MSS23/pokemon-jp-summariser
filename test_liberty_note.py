#!/usr/bin/env python3
"""
Test script for liberty-note.com article EV detection
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer

def test_liberty_note():
    """Test the improved EV detection with liberty-note.com article"""
    url = "https://liberty-note.com/2025/07/31/teru-fes-viera-1st/"
    
    print("=== TESTING LIBERTY-NOTE.COM EV DETECTION ===")
    print(f"URL: {url}")
    print()
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        # Get content
        print("Scraping article content...")
        content = analyzer.scrape_article(url)
        print(f"Content length: {len(content)}")
        print()
        
        # Check for specific EV patterns in the raw content
        print("Checking for EV patterns in raw content...")
        
        # Look for Japanese EV keywords
        japanese_ev_keywords = ["努力値", "EV", "配分", "調整", "実数値"]
        found_keywords = []
        for keyword in japanese_ev_keywords:
            if keyword in content:
                count = content.count(keyword)
                found_keywords.append(f"{keyword}({count})")
        
        print(f"Found EV-related keywords: {len(found_keywords)} keywords found")
        
        # Look for numbers that could be EVs
        import re
        ev_numbers = ["252", "244", "236", "220", "196", "188", "172", "156", "140", "124", "116", "100", "84", "68", "52", "36", "28", "20", "12", "4"]
        found_numbers = []
        for num in ev_numbers:
            if num in content:
                found_numbers.append(num)
        
        print(f"Found potential EV numbers: {found_numbers}")
        
        # Check for specific EV patterns more explicitly
        ev_patterns_found = []
        if "努力値" in content:
            ev_patterns_found.append("Effort Values keyword found")
        if re.search(r"\d{1,3}/\d{1,3}/\d{1,3}/\d{1,3}/\d{1,3}/\d{1,3}", content):
            ev_patterns_found.append("Standard slash format pattern found")
        if re.search(r"H\d{1,3}", content):
            ev_patterns_found.append("H-stat pattern found")
        
        print(f"EV patterns found: {ev_patterns_found}")
        
        # Look for stat patterns
        stat_patterns = [
            r"H(\d{1,3})",  # H252
            r"A(\d{1,3})",  # A4
            r"B(\d{1,3})",  # B252
            r"C(\d{1,3})",  # C252
            r"D(\d{1,3})",  # D0
            r"S(\d{1,3})"   # S0
        ]
        
        found_stat_patterns = []
        for pattern in stat_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_stat_patterns.extend([f"{pattern[0]}{match}" for match in matches[:3]])  # Show first 3
        
        print(f"Found stat patterns: {found_stat_patterns}")
        print()
        
        # Run the full analysis with images
        print("Running full analysis with images...")
        result = analyzer.analyze_article_with_images(content, url)
        
        if result:
            # Save the result to examine
            with open("liberty_note_test_result.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            pokemon_team = result.get("pokemon_team", [])
            print(f"Analysis detected {len(pokemon_team)} Pokemon")
            print()
            
            # Check EV extraction results
            print("=== EV EXTRACTION RESULTS ===")
            for i, pokemon in enumerate(pokemon_team, 1):
                name = pokemon.get("name", "Unknown")
                evs = pokemon.get("evs", "Not found")
                ev_spread = pokemon.get("ev_spread", {})
                total = ev_spread.get("total", 0)
                ev_explanation = pokemon.get("ev_explanation", "No explanation")
                
                print(f"Pokemon {i}: {name}")
                print(f"  EVs: {evs}")
                print(f"  Total: {total}")
                print(f"  Explanation: {ev_explanation}")
                print()
            
            # Check translation notes for EV-related information
            translation_notes = result.get("translation_notes", "")
            if "EV" in translation_notes or "Image" in translation_notes:
                print("Translation notes (EV-related):")
                print(translation_notes)
                print()
        
        print("Test complete - check liberty_note_test_result.json for full analysis")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_liberty_note()