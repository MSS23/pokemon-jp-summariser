#!/usr/bin/env python3
"""
Simple debug script to check what's actually in the Note.com article
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer

def simple_debug():
    """Simple debug of Note.com article"""
    url = "https://note.com/bright_ixora372/n/nd5515195c993"
    
    print("=== SIMPLE NOTE.COM DEBUG ===")
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        # Get content
        content = analyzer.scrape_article(url)
        print(f"Content length: {len(content)}")
        
        # Check for specific EV patterns
        print("\nChecking for EV patterns...")
        
        # Check for numbers that could be EVs
        import re
        
        # Look for patterns like "252" or "244" or other EV values
        ev_numbers = ["252", "244", "236", "220", "196", "188", "156", "124", "116", "100", "68", "52", "36", "28", "20", "12", "4"]
        found_numbers = []
        for num in ev_numbers:
            if num in content:
                found_numbers.append(num)
        
        print(f"Found potential EV numbers: {found_numbers}")
        
        # Look for stat abbreviations
        stat_letters = ["H252", "A252", "B252", "C252", "D252", "S252"]
        found_stats = []
        for stat in stat_letters:
            if stat in content:
                found_stats.append(stat)
        
        print(f"Found stat patterns: {found_stats}")
        
        # Look for Japanese EV keywords
        japanese_keywords = []
        keywords_to_check = ["H", "A", "B", "C", "D", "S"]  # Simple ASCII letters
        for kw in keywords_to_check:
            count = content.count(kw)
            if count > 2:  # More than just a few mentions
                japanese_keywords.append(f"{kw}({count})")
        
        print(f"Letter frequency: {japanese_keywords}")
        
        # Check content without unicode issues
        ascii_content = ''.join(char if ord(char) < 128 else '?' for char in content)
        
        # Look for patterns in ASCII content
        patterns = [
            r"\d{1,3}[/-]\d{1,3}[/-]\d{1,3}[/-]\d{1,3}[/-]\d{1,3}[/-]\d{1,3}",  # EV spread pattern
            r"[HABCDS]\d{1,3}",  # Stat + number
            r"\d{3}",  # 3-digit numbers
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, ascii_content)
            if matches:
                print(f"Pattern {i+1} matches: {matches[:5]}")  # Show first 5 matches
        
        # Now do the actual analysis
        print("\nRunning full analysis...")
        result = analyzer.analyze_article_with_images(content, url)
        
        if result:
            # Save the result to examine
            with open("simple_debug_result.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            pokemon_team = result.get("pokemon_team", [])
            print(f"Analysis detected {len(pokemon_team)} Pokemon")
            
            # Check if there are any clues in the analysis about why EVs weren't found
            translation_notes = result.get("translation_notes", "")
            if "arbitrary" in translation_notes.lower() or "tekitou" in translation_notes.lower():
                print("FOUND CLUE: Author mentioned EVs were 'arbitrary' or 'tekitou'")
            
            # Check the content summary for clues
            summary = result.get("content_summary", "")
            if "retrospective" in summary.lower():
                print("FOUND CLUE: This appears to be a retrospective article, not a detailed team showcase")
        
        print("Debug complete - check simple_debug_result.json for full analysis")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_debug()