#!/usr/bin/env python3
"""
Debug image analysis for Note.com article
"""

import sys
from pathlib import Path
import json

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from utils.image_analyzer import extract_images_from_url, filter_vgc_images, analyze_image_with_vision, extract_ev_spreads_from_image_analysis

def debug_images():
    """Debug image analysis for Note.com article"""
    url = "https://note.com/bright_ixora372/n/nd5515195c993"
    
    print("=== IMAGE DEBUG FOR NOTE.COM ARTICLE ===")
    print(f"URL: {url}")
    
    try:
        # Extract images
        print("\n1. EXTRACTING IMAGES...")
        images = extract_images_from_url(url, max_images=15)
        print(f"Found {len(images)} total images")
        
        # Show all images found
        for i, img in enumerate(images):
            print(f"  Image {i+1}: {img['url']}")
            print(f"    Priority Score: {img.get('priority_score', 0)}")
            print(f"    Likely Team Card: {img.get('is_likely_team_card', False)}")
            print(f"    Note.com Asset: {'assets.st-note.com' in img['url']}")
        
        # Filter for VGC images
        print(f"\n2. FILTERING VGC IMAGES...")
        vgc_images = filter_vgc_images(images)
        print(f"Filtered to {len(vgc_images)} VGC images")
        
        for i, img in enumerate(vgc_images):
            print(f"  VGC Image {i+1}: {img['url']}")
            print(f"    Final Score: {img.get('final_score', 0)}")
        
        # Analyze each VGC image
        print(f"\n3. ANALYZING IMAGES FOR EV DATA...")
        all_ev_data = []
        
        for i, img in enumerate(vgc_images):
            print(f"\nAnalyzing VGC Image {i+1}...")
            print(f"URL: {img['url']}")
            
            try:
                # Analyze with vision
                analysis = analyze_image_with_vision(img['url'])
                
                if analysis:
                    print(f"Vision analysis length: {len(analysis)} chars")
                    
                    # Save analysis to file for inspection
                    with open(f"image_analysis_{i+1}.txt", 'w', encoding='utf-8') as f:
                        f.write(f"URL: {img['url']}\n\n")
                        f.write(analysis)
                    
                    # Check for EV-related content in analysis
                    ev_keywords = ["252", "244", "236", "EV", "H", "A", "B", "C", "D", "S"]
                    found_keywords = []
                    for keyword in ev_keywords:
                        if keyword in analysis:
                            count = analysis.count(keyword)
                            if count > 0:
                                found_keywords.append(f"{keyword}({count})")
                    
                    print(f"EV keywords found: {found_keywords}")
                    
                    # Extract EV spreads
                    ev_spreads = extract_ev_spreads_from_image_analysis(analysis)
                    print(f"Extracted {len(ev_spreads)} EV spreads")
                    
                    for j, spread in enumerate(ev_spreads):
                        print(f"  Spread {j+1}: Total {spread.get('total', 0)} - {spread.get('format', 'N/A')}")
                        all_ev_data.append(spread)
                    
                    # Save individual analysis
                    with open(f"image_ev_data_{i+1}.json", 'w', encoding='utf-8') as f:
                        json.dump({
                            "url": img['url'],
                            "analysis": analysis,
                            "ev_spreads": ev_spreads
                        }, f, indent=2, ensure_ascii=False)
                        
                else:
                    print("No vision analysis returned")
                    
            except Exception as e:
                print(f"Error analyzing image: {e}")
        
        print(f"\n4. SUMMARY")
        print(f"Total images found: {len(images)}")
        print(f"VGC images filtered: {len(vgc_images)}")
        print(f"EV spreads extracted: {len(all_ev_data)}")
        
        if all_ev_data:
            print("EV SPREADS FOUND IN IMAGES:")
            for i, spread in enumerate(all_ev_data):
                print(f"  {i+1}. Total: {spread.get('total', 0)} - Format: {spread.get('format', 'Unknown')}")
        else:
            print("NO EV SPREADS FOUND IN IMAGES")
        
        # Save comprehensive results
        result_data = {
            "url": url,
            "total_images": len(images),
            "vgc_images": len(vgc_images),
            "ev_spreads_found": len(all_ev_data),
            "all_ev_data": all_ev_data,
            "image_urls": [img['url'] for img in vgc_images]
        }
        
        with open("comprehensive_image_debug.json", 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nComprehensive results saved to comprehensive_image_debug.json")
        print(f"Individual image analyses saved as image_analysis_*.txt and image_ev_data_*.json")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_images()