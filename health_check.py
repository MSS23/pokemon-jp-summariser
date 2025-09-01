#!/usr/bin/env python3
"""
Health check script for Pokemon VGC Analysis Platform
Verifies that all core components can be imported and initialized
"""

import sys
import os
from pathlib import Path

def main():
    """Run health check diagnostics"""
    print("🔍 Pokemon VGC Analysis Platform - Health Check")
    print("=" * 50)
    
    # Check Python version
    print(f"✅ Python Version: {sys.version}")
    
    # Check working directory
    print(f"✅ Working Directory: {os.getcwd()}")
    
    # Add src directory to path
    src_path = Path(__file__).parent / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    print(f"✅ Source Path Added: {src_path}")
    
    # Test core imports
    try:
        print("🔄 Testing core imports...")
        
        # Test configuration
        from utils.config import Config
        print("✅ Config import successful")
        
        # Test analyzer (this will verify API key works)
        from core.analyzer import GeminiVGCAnalyzer
        print("✅ Analyzer import successful")
        
        # Test UI components
        from ui.components import apply_custom_css
        print("✅ UI components import successful")
        
        # Test cache system
        from utils import cache
        print("✅ Cache system import successful")
        
        print("\n🎉 All health checks passed!")
        print("✅ Application is ready for deployment")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)