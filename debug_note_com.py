#!/usr/bin/env python3
"""
Debug script to examine Note.com article content and EV detection
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.analyzer import GeminiVGCAnalyzer
from utils.image_analyzer import extract_images_from_url, filter_vgc_images, analyze_image_with_vision

def debug_note_com_article():
    """Debug the Note.com article that's failing EV detection"""
    url = "https://note.com/bright_ixora372/n/nd5515195c993"
    
    print("=== DEBUGGING NOTE.COM ARTICLE EV DETECTION ===")
    print(f"URL: {url}")
    
    try:
        analyzer = GeminiVGCAnalyzer()
        
        print("\n1. CONTENT SCRAPING DEBUG")
        print("-" * 50)
        content = analyzer.scrape_article(url)
        print(f"Scraped content length: {len(content)} characters")
        print(f"Content preview (first 500 chars):")
        print(repr(content[:500]))
        print(f"Content preview (readable):")
        print(content[:500])
        
        # Look for EV-related keywords in the content
        print(f"\n2. EV KEYWORD DETECTION IN SCRAPED CONTENT")
        print("-" * 50)
        ev_keywords = [
            "努力値", "EV", "個体値", "調整", "実数値", 
            "252", "244", "236", "188", "156", "124",
            "H", "A", "B", "C", "D", "S"
        ]
        
        for keyword in ev_keywords:
            count = content.count(keyword)
            if count > 0:
                print(f"Found '{keyword}': {count} times")
                
                # Show context around the keyword
                import re
                matches = list(re.finditer(re.escape(keyword), content))
                for i, match in enumerate(matches[:3]):  # Show first 3 matches
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].replace('\n', '\\n')
                    print(f"  Context {i+1}: ...{context}...")
        
        print(f"\n3. IMAGE EXTRACTION DEBUG")
        print("-" * 50)
        images = extract_images_from_url(url)
        print(f"Extracted {len(images)} images")
        
        for i, img in enumerate(images[:5]):  # Show first 5 images
            print(f"  Image {i+1}:")
            print(f"    URL: {img['url'][:100]}...")
            print(f"    Priority Score: {img.get('priority_score', 'N/A')}")
            print(f"    Likely Team Card: {img.get('is_likely_team_card', False)}")
        
        # Filter VGC images
        vgc_images = filter_vgc_images(images)
        print(f"Filtered to {len(vgc_images)} VGC-relevant images")
        
        print(f"\n4. IMAGE ANALYSIS DEBUG")
        print("-" * 50)
        if vgc_images:
            for i, img in enumerate(vgc_images[:2]):  # Analyze first 2 images
                print(f"Analyzing image {i+1}...")
                analysis = analyze_image_with_vision(img['url'])
                print(f"Analysis length: {len(analysis) if analysis else 0} characters")
                if analysis:
                    print(f"Analysis preview:")
                    print(analysis[:300])
                    print("...")
                    
                    # Check for EV keywords in image analysis
                    ev_found = any(keyword in analysis for keyword in ev_keywords)
                    print(f"Contains EV-related content: {ev_found}")
        else:
            print("No VGC images to analyze")
        
        print(f"\n5. FULL ANALYSIS DEBUG")
        print("-" * 50)
        result = analyzer.analyze_article_with_images(content, url)
        
        if result:
            pokemon_team = result.get("pokemon_team", [])
            print(f"Detected {len(pokemon_team)} Pokemon")
            
            for i, pokemon in enumerate(pokemon_team, 1):
                name = pokemon.get('name', 'Unknown')
                ev_spread = pokemon.get('ev_spread', {})
                ev_total = ev_spread.get('total', 0)
                
                print(f"  Pokemon {i}: {name}")
                print(f"    EV Total: {ev_total}")
                print(f"    EV Spread: {ev_spread}")
                print(f"    Item: {pokemon.get('held_item', pokemon.get('item', 'None'))}")
                print(f"    Moves: {len(pokemon.get('moves', []))} moves")
                
                # Show EV explanation if available
                ev_explanation = pokemon.get('ev_explanation', '')
                if ev_explanation and ev_explanation != "Not specified":
                    print(f"    EV Explanation: {ev_explanation[:100]}...")
        else:
            print("ERROR: No analysis result returned")
        
        # Save detailed debug data
        debug_data = {
            "url": url,
            "content_length": len(content),
            "content_preview": content[:1000],
            "images_found": len(images),
            "vgc_images": len(vgc_images),
            "analysis_result": result
        }
        
        with open("debug_note_com_results.json", 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, indent=2, ensure_ascii=False)
        print(f"\nDebug data saved to: debug_note_com_results.json")
        
    except Exception as e:
        print(f"ERROR during debug: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_note_com_article()