#!/usr/bin/env python3
"""
Pokemon VGC Analysis Platform Launcher

Simple launcher script for the Streamlit application.
"""

import os
import sys
import subprocess

def main():
    """Launch the Streamlit application"""
    
    # Get the directory containing this script
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add src directory to Python path
    src_dir = os.path.join(app_dir, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Set working directory
    os.chdir(app_dir)
    
    # Launch Streamlit app
    app_file = os.path.join('src', 'app.py')
    
    print("🚀 Starting Pokemon VGC Analysis Platform...")
    print(f"📁 Working directory: {app_dir}")
    print(f"📄 App file: {app_file}")
    print("🌐 The app will open in your browser shortly...")
    print()
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 
            app_file, 
            '--server.address', '0.0.0.0',
            '--server.port', '8501',
            '--server.headless', 'false'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()