"""
Setup script for Pokemon VGC Analysis Platform
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True

def setup_config():
    """Set up configuration files"""
    print("⚙️ Setting up configuration...")
    
    config_dir = os.path.join('config', '.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    
    secrets_file = os.path.join(config_dir, 'secrets.toml')
    config_file = os.path.join(config_dir, 'config.toml')
    
    # Create secrets.toml template if it doesn't exist
    if not os.path.exists(secrets_file):
        with open(secrets_file, 'w') as f:
            f.write('''# API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
google_api_key = "your_gemini_api_key_here"
''')
        print(f"📝 Created {secrets_file}")
        print("⚠️  Please add your Google Gemini API key to config/.streamlit/secrets.toml")
    
    # Create config.toml if it doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            f.write('''[server]
port = 8501
address = "0.0.0.0"

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[browser]
gatherUsageStats = false
''')
        print(f"📝 Created {config_file}")
    
    return True

def create_data_directories():
    """Create necessary data directories"""
    print("📁 Creating data directories...")
    
    directories = [
        'data/cache',
        'data/databases',
        'data/logs'
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created {dir_path}")
    
    return True

def main():
    """Main setup routine"""
    print("🚀 Setting up Pokemon VGC Analysis Platform")
    print("=" * 50)
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Setup configuration
    if not setup_config():
        sys.exit(1)
    
    # Create directories
    if not create_data_directories():
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Add your Google Gemini API key to config/.streamlit/secrets.toml")
    print("2. Run: python run.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\n💡 For more information, see docs/README.md")

if __name__ == "__main__":
    main()