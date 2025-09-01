"""
Pokemon VGC Analysis Platform - Streamlit Cloud Entry Point

This is the main entry point for Streamlit Cloud deployment.
It imports and runs the modular application from the src/ directory.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Set working directory to project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Import the main application class
try:
    from src.app import VGCAnalysisApp
    
    # Initialize and run the application
    def main():
        """Main entry point for the application"""
        app = VGCAnalysisApp()
        app.run()
    
    # Run the app if this file is executed directly
    if __name__ == "__main__":
        main()
    else:
        # For Streamlit Cloud, just run directly
        app = VGCAnalysisApp()
        app.run()
        
except ImportError as e:
    import streamlit as st
    st.error(f"Failed to import application: {e}")
    st.error("Please check that all dependencies are installed correctly.")
    st.info("Run: pip install -r requirements.txt")
    st.stop()