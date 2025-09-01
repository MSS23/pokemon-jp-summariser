#!/usr/bin/env python3
"""
Integration test script for Pokemon VGC Analysis application
Tests that all modules load correctly and basic functionality works
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported successfully"""
    print("Testing module imports...")
    
    try:
        from config import Config
        print("+ Config module imported")
        
        from vgc_analyzer import GeminiVGCAnalyzer
        print("+ VGC Analyzer module imported")
        
        from image_analyzer import (
            extract_images_from_url,
            filter_vgc_images,
            analyze_image_with_vision,
            extract_ev_spreads_from_image_analysis
        )
        print("+ Image Analyzer module imported")
        
        from ui_components import (
            render_page_header,
            render_analysis_input,
            render_team_showcase,
            render_pokemon_team,
            render_export_section,
            render_image_analysis_section,
            render_sidebar,
            apply_custom_css
        )
        print("+ UI Components module imported")
        
        from utils import validate_url, get_pokemon_sprite_url
        print("+ Utils module imported")
        
        from utils import cache
        print("+ Cache Manager module imported")
        
        return True
        
    except Exception as e:
        print(f"- Import failed: {str(e)}")
        return False

def test_analyzer_initialization():
    """Test that the analyzer can be initialized"""
    print("\nTesting analyzer initialization...")
    
    try:
        from vgc_analyzer import GeminiVGCAnalyzer
        
        # Test initialization (this should work even without API key for structure test)
        analyzer = GeminiVGCAnalyzer()
        print("+ Analyzer initialized successfully")
        
        # Test that it has the expected methods
        assert hasattr(analyzer, 'analyze_article'), "Missing analyze_article method"
        assert hasattr(analyzer, 'analyze_article_with_images'), "Missing analyze_article_with_images method"
        assert hasattr(analyzer, 'extract_and_analyze_images'), "Missing extract_and_analyze_images method"
        print("+ All expected methods present")
        
        return True
        
    except Exception as e:
        print(f"- Analyzer initialization failed: {str(e)}")
        return False

def test_image_analyzer_functions():
    """Test image analyzer functions"""
    print("\nTesting image analyzer functions...")
    
    try:
        from image_analyzer import is_potentially_vgc_image, get_vision_analysis_prompt
        
        # Test VGC image detection with mock data
        mock_image = {
            "url": "https://assets.st-note.com/img/pokemon_team.jpg",
            "size": (800, 600),
            "file_size": 75000,
            "is_note_com_asset": True,
            "is_likely_team_card": True,
            "alt_text": "pokemon team vgc"
        }
        
        result = is_potentially_vgc_image(mock_image)
        assert result == True, "Should detect VGC image"
        print("+ VGC image detection working")
        
        # Test prompt generation
        prompt = get_vision_analysis_prompt()
        assert len(prompt) > 1000, "Prompt should be comprehensive"
        assert "POKEMON" in prompt.upper(), "Prompt should mention Pokemon"
        print("+ Vision analysis prompt generation working")
        
        return True
        
    except Exception as e:
        print(f"- Image analyzer test failed: {str(e)}")
        return False

def test_url_validation():
    """Test URL validation functionality"""
    print("\nTesting URL validation...")
    
    try:
        from utils import validate_url
        
        # Test valid URLs
        assert validate_url("https://note.com/test") == True, "Should validate note.com URLs"
        assert validate_url("https://example.com") == True, "Should validate basic HTTPS URLs"
        
        # Test invalid URLs  
        assert validate_url("not-a-url") == False, "Should reject invalid URLs"
        assert validate_url("") == False, "Should reject empty URLs"
        
        print("+ URL validation working correctly")
        return True
        
    except Exception as e:
        print(f"- URL validation test failed: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print("Starting Pokemon VGC Analysis Integration Tests\n")
    
    tests = [
        test_imports,
        test_analyzer_initialization,
        test_image_analyzer_functions,
        test_url_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("Continuing with remaining tests...\n")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All integration tests PASSED! The application is ready to use.")
        return 0
    else:
        print("WARNING: Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())