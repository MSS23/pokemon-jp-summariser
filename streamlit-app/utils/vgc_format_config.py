"""
VGC Format Configuration File
Easy management of VGC formats and future updates
"""

import json
import os
from typing import Dict, List, Optional

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "vgc_formats.json")

# Default VGC format definitions
DEFAULT_VGC_FORMATS = {
    "auto": {
        "name": "Auto-Detect Format",
        "description": "AI automatically detects the VGC format based on team composition and article content",
        "mechanics": "Auto-detected",
        "restricted_pokemon": "Auto-detected",
        "status": "auto"
    },
    "vgc_a": {
        "name": "VGC Format A",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "active"
    },
    "vgc_b": {
        "name": "VGC Format B",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_c": {
        "name": "VGC Format C",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_d": {
        "name": "VGC Format D",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_e": {
        "name": "VGC Format E",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_f": {
        "name": "VGC Format F",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_g": {
        "name": "VGC Format G",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_h": {
        "name": "VGC Format H",
        "description": "Pokemon Scarlet and Violet - Competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "historical"
    },
    "vgc_i": {
        "name": "VGC Format I",
        "description": "Pokemon Scarlet and Violet - Latest competitive format with Tera Types",
        "mechanics": "Tera Types, Scarlet/Violet mechanics",
        "restricted_pokemon": "Pokemon available in Scarlet/Violet",
        "status": "active"
    },
    "custom": {
        "name": "Custom Format",
        "description": "User-defined VGC format with custom rules",
        "mechanics": "Custom",
        "restricted_pokemon": "Custom",
        "status": "custom"
    }
}

def load_vgc_formats() -> Dict:
    """Load VGC formats from configuration file or use defaults"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default config file
            save_vgc_formats(DEFAULT_VGC_FORMATS)
            return DEFAULT_VGC_FORMATS
    except Exception as e:
        print(f"Error loading VGC formats: {e}")
        return DEFAULT_VGC_FORMATS

def save_vgc_formats(formats: Dict) -> bool:
    """Save VGC formats to configuration file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(formats, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving VGC formats: {e}")
        return False

def add_new_format(format_key: str, format_data: Dict) -> bool:
    """Add a new VGC format to the configuration"""
    try:
        formats = load_vgc_formats()
        formats[format_key] = format_data
        return save_vgc_formats(formats)
    except Exception as e:
        print(f"Error adding new format: {e}")
        return False

def update_format(format_key: str, format_data: Dict) -> bool:
    """Update an existing VGC format"""
    try:
        formats = load_vgc_formats()
        if format_key in formats:
            formats[format_key].update(format_data)
            return save_vgc_formats(formats)
        return False
    except Exception as e:
        print(f"Error updating format: {e}")
        return False

def remove_format(format_key: str) -> bool:
    """Remove a VGC format from the configuration"""
    try:
        formats = load_vgc_formats()
        if format_key in formats:
            del formats[format_key]
            return save_vgc_formats(formats)
        return False
    except Exception as e:
        print(f"Error removing format: {e}")
        return False

def get_format_by_year(year: int) -> Optional[Dict]:
    """Get VGC format by year"""
    formats = load_vgc_formats()
    for key, data in formats.items():
        if data.get('year') == year:
            return data
    return None

def get_formats_by_status(status: str) -> List[Dict]:
    """Get VGC formats by status (active, historical, predicted)"""
    formats = load_vgc_formats()
    return [data for data in formats.values() if data.get('status') == status]

def export_formats_to_json(filepath: str) -> bool:
    """Export VGC formats to a JSON file"""
    try:
        formats = load_vgc_formats()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(formats, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error exporting formats: {e}")
        return False

def import_formats_from_json(filepath: str) -> bool:
    """Import VGC formats from a JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            formats = json.load(f)
        return save_vgc_formats(formats)
    except Exception as e:
        print(f"Error importing formats: {e}")
        return False

# Example usage for future format updates
def add_j_format():
    """Example function to add VGC Format J when it becomes available"""
    vgc_j_data = {
        "name": "VGC Format J",
        "description": "Future VGC format with potential new mechanics and Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "Potential New Mechanics", "Scarlet/Violet mechanics"],
        "restricted": ["TBD"],
        "key_features": ["Future format", "Potential new Pokemon", "Meta evolution"],
        "regulation": "J",
        "status": "predicted",
        "meta_notes": "Format details will be updated as information becomes available"
    }
    return add_new_format("vgc_j", vgc_j_data)

if __name__ == "__main__":
    # Test the configuration system
    formats = load_vgc_formats()
    print(f"Loaded {len(formats)} VGC formats")
    
    # Example: Add a new format
    # add_2026_format()
