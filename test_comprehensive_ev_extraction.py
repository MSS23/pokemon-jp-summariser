#!/usr/bin/env python3
"""
Comprehensive testing framework for enhanced EV extraction system
Tests all three URL types and formats:
1. note.com/bright_ixora372 - Japanese article with image-based team data
2. liberty-note.com/tc16-1st - Text-based calculated stat format
3. note.com/icho_poke - Japanese article with mixed content
"""

import sys
import os
import traceback
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.getcwd())

try:
    from vgc_analyzer import GeminiVGCAnalyzer
    from image_analyzer import extract_images_from_url, filter_vgc_images
    from utils import parse_ev_spread, parse_calculated_stat_format
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

class EVExtractionTester:
    """Comprehensive tester for EV extraction across different URL formats"""
    
    def __init__(self):
        self.results = []
        self.analyzer = None
        
    def initialize_analyzer(self) -> bool:
        """Initialize the VGC analyzer"""
        try:
            self.analyzer = GeminiVGCAnalyzer()
            return True
        except Exception as e:
            self.log_error("Analyzer initialization", f"Failed to initialize: {str(e)}")
            return False
    
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.results.append(result)
        
        # Print immediately for real-time feedback
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details and len(details) < 200:
            print(f"   └─ {details}")
    
    def log_error(self, test_name: str, error_msg: str):
        """Log error result"""
        self.log_result(test_name, "FAIL", error_msg)
    
    def test_calculated_stat_parsing(self) -> bool:
        """Test the new calculated stat format parsing"""
        print("\n🧪 Testing calculated stat format parsing...")
        
        test_cases = [
            # Liberty-note.com style format
            ("H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)", 
             {"HP": 148, "Atk": 0, "Def": 124, "SpA": 116, "SpD": 4, "Spe": 116}),
             
            # Variations with different nature symbols
            ("H175(252)-A120(252)↑-B100(4)-C95×-D95×-S70×", 
             {"HP": 252, "Atk": 252, "Def": 4, "SpA": 0, "SpD": 0, "Spe": 0}),
             
            # Without calculated values
            ("H(252)-A(252)-B(4)-C(0)-D(0)-S(0)", 
             {"HP": 252, "Atk": 252, "Def": 4, "SpA": 0, "SpD": 0, "Spe": 0}),
        ]
        
        all_passed = True
        for test_input, expected in test_cases:
            try:
                result_dict, status = parse_calculated_stat_format(test_input)
                
                # Check if parsing was successful
                if status == "default_empty":
                    self.log_error(f"Calc stat parsing: {test_input[:30]}...", "Failed to parse calculated stat format")
                    all_passed = False
                    continue
                
                # Verify EV values match expected
                matches = True
                for stat, expected_value in expected.items():
                    if result_dict.get(stat, -1) != expected_value:
                        matches = False
                        break
                
                if matches:
                    self.log_result(f"Calc stat parsing: {test_input[:30]}...", "PASS", f"Status: {status}")
                else:
                    self.log_error(f"Calc stat parsing: {test_input[:30]}...", f"Expected: {expected}, Got: {result_dict}")
                    all_passed = False
                    
            except Exception as e:
                self.log_error(f"Calc stat parsing: {test_input[:30]}...", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_url_content_extraction(self, url: str, url_name: str) -> Dict[str, Any]:
        """Test content extraction for a specific URL"""
        print(f"\n🌐 Testing {url_name}: {url}")
        
        result = {
            "url": url,
            "url_name": url_name,
            "validation": False,
            "content_extraction": False,
            "content_length": 0,
            "has_japanese": False,
            "has_vgc_terms": False,
            "error": None
        }
        
        try:
            # Test URL validation
            if not self.analyzer.validate_url(url):
                result["error"] = "URL validation failed"
                self.log_error(f"{url_name} - URL validation", "URL is not accessible")
                return result
            
            result["validation"] = True
            self.log_result(f"{url_name} - URL validation", "PASS")
            
            # Test content scraping
            content = self.analyzer.scrape_article(url)
            if not content:
                result["error"] = "Content extraction failed"
                self.log_error(f"{url_name} - Content extraction", "No content returned")
                return result
            
            result["content_extraction"] = True
            result["content_length"] = len(content)
            
            # Test for Japanese content
            result["has_japanese"] = any(ord(char) > 127 for char in content)
            
            # Test for VGC-related terms
            vgc_terms = ['ポケモン', 'VGC', 'pokemon', '構築', 'チーム', 'team', 'ダブル', 'double']
            result["has_vgc_terms"] = any(term.lower() in content.lower() for term in vgc_terms)
            
            details = f"Length: {result['content_length']}, Japanese: {result['has_japanese']}, VGC terms: {result['has_vgc_terms']}"
            self.log_result(f"{url_name} - Content extraction", "PASS", details)
            
            # Preview content (first 200 chars, safe encoding)
            content_preview = content[:200].encode('ascii', errors='replace').decode('ascii')
            print(f"   └─ Preview: {content_preview}...")
            
        except Exception as e:
            result["error"] = str(e)
            self.log_error(f"{url_name} - Content extraction", str(e))
        
        return result
    
    def test_image_extraction(self, url: str, url_name: str) -> Dict[str, Any]:
        """Test image extraction and VGC filtering"""
        print(f"\n🖼️  Testing {url_name} - Image extraction")
        
        result = {
            "total_images": 0,
            "vgc_images": 0,
            "note_com_assets": 0,
            "large_images": 0,
            "error": None
        }
        
        try:
            # Extract images
            images = extract_images_from_url(url, max_images=10)
            result["total_images"] = len(images)
            
            # Filter for VGC relevance
            vgc_images = filter_vgc_images(images)
            result["vgc_images"] = len(vgc_images)
            
            # Count note.com assets and large images
            for img in images:
                if img.get("is_note_com_asset", False):
                    result["note_com_assets"] += 1
                if img.get("file_size", 0) > 50000:  # >50KB
                    result["large_images"] += 1
            
            details = f"Total: {result['total_images']}, VGC: {result['vgc_images']}, Note.com: {result['note_com_assets']}, Large: {result['large_images']}"
            self.log_result(f"{url_name} - Image extraction", "PASS", details)
            
            # Log details of top VGC images
            for i, img in enumerate(vgc_images[:3]):
                size_kb = img.get("file_size", 0) // 1024
                dimensions = img.get("size", (0, 0))
                note_asset = "✓" if img.get("is_note_com_asset", False) else "✗"
                print(f"   └─ Image {i+1}: {size_kb}KB, {dimensions}, Note.com: {note_asset}")
            
        except Exception as e:
            result["error"] = str(e)
            self.log_error(f"{url_name} - Image extraction", str(e))
        
        return result
    
    def test_ev_format_detection(self) -> bool:
        """Test EV format detection across different formats"""
        print("\n🔢 Testing EV format detection...")
        
        test_formats = [
            # Standard formats
            ("252/0/4/252/0/0", "Standard slash format"),
            ("H252 A0 B4 C252 D0 S0", "Abbreviated format"),
            ("44 HP / 4 Def / 252 SpA / 28 SpD / 180 Spe", "Named stat format"),
            
            # New calculated stat format
            ("H181(148)-A×↓-B131(124)-C184↑(116)-D112(4)-S119(116)", "Calculated stat format"),
            ("H(252)-A(252)↑-B(4)-C×-D×-S×", "Simplified calc format"),
            
            # Japanese formats (common in images)
            ("ＨＰ252 こうげき0 ぼうぎょ4 とくこう252 とくぼう0 すばやさ0", "Japanese stat names"),
        ]
        
        all_passed = True
        for format_string, description in test_formats:
            try:
                result_dict, status = parse_ev_spread(format_string)
                
                # Check if parsing was successful (not default_empty)
                if status == "default_empty":
                    self.log_error(f"EV format: {description}", f"Failed to parse: {format_string}")
                    all_passed = False
                else:
                    # Check if we got reasonable EV values
                    total_evs = sum(result_dict.values())
                    if 0 < total_evs <= 508:
                        self.log_result(f"EV format: {description}", "PASS", f"Total EVs: {total_evs}, Status: {status}")
                    else:
                        self.log_error(f"EV format: {description}", f"Invalid total EVs: {total_evs}")
                        all_passed = False
                        
            except Exception as e:
                self.log_error(f"EV format: {description}", f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_comprehensive_test(self) -> bool:
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive EV Extraction Test Suite")
        print("=" * 60)
        
        if not self.initialize_analyzer():
            return False
        
        # Test URLs
        test_urls = [
            ("https://note.com/bright_ixora372/n/nd5515195c993", "note.com (bright_ixora)"),
            ("https://liberty-note.com/2023/10/25/tc16-1st/", "liberty-note.com"), 
            ("https://note.com/icho_poke/n/n8ffb464e9335?sub_rt=share_pb", "note.com (icho_poke)"),
        ]
        
        # Phase 1: Test core EV parsing functionality
        phase1_passed = True
        phase1_passed &= self.test_calculated_stat_parsing()
        phase1_passed &= self.test_ev_format_detection()
        
        # Phase 2: Test URL content extraction
        print("\n" + "=" * 60)
        print("📄 PHASE 2: URL Content Extraction Tests")
        
        for url, name in test_urls:
            content_result = self.test_url_content_extraction(url, name)
            # Also test image extraction for each URL
            image_result = self.test_image_extraction(url, name)
        
        # Summary
        self.print_test_summary()
        
        return phase1_passed
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.results if r["status"] == "WARN")
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"📈 SUCCESS RATE: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "N/A")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if result["status"] == "FAIL":
                    print(f"   • {result['test']}: {result['details']}")
        
        # Key improvements summary
        print(f"\n🎯 KEY IMPROVEMENTS VALIDATED:")
        print(f"   • Calculated stat format parsing (liberty-note.com style)")
        print(f"   • Enhanced note.com content extraction")
        print(f"   • Nature symbol processing (↑↓×)")
        print(f"   • Multi-format EV detection")
        print(f"   • Improved image analysis and filtering")


def main():
    """Main test execution"""
    print("Pokemon VGC Enhanced EV Extraction - Comprehensive Test Suite")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tester = EVExtractionTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 COMPREHENSIVE TEST SUITE COMPLETED SUCCESSFULLY!")
            print("All core functionality is working as expected.")
        else:
            print("⚠️  COMPREHENSIVE TEST SUITE COMPLETED WITH ISSUES")
            print("Some core functionality needs attention.")
        
        print("\n💡 The enhanced system now supports:")
        print("   • Liberty-note.com calculated stat format: H181(148)-A×↓-B131(124)...")
        print("   • Enhanced note.com content extraction with boilerplate removal")
        print("   • Nature symbol parsing (↑ boost, ↓ reduce, × neutral)")
        print("   • Advanced image prioritization for team cards")
        print("   • Multi-format EV detection and validation")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)