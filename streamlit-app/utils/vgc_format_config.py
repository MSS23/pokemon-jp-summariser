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
    "vgc2025": {
        "name": "VGC 2025 - Regulation G (Predicted)",
        "description": "Upcoming VGC format with potential new mechanics and Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "Potential New Mechanics"],
        "restricted": ["Miraidon", "Koraidon", "Calyrex", "Zacian", "Zamazenta"],
        "key_features": ["Future format", "Potential new Pokemon", "Meta evolution"],
        "year": 2025,
        "regulation": "G",
        "status": "predicted",
        "meta_notes": "Format details will be updated as information becomes available"
    },
    "vgc2024": {
        "name": "VGC 2024 - Regulation F",
        "description": "Latest VGC format with Tera mechanics and new Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "No Dynamax"],
        "restricted": ["Miraidon", "Koraidon", "Calyrex", "Zacian", "Zamazenta"],
        "key_features": ["Tera Type changes", "Scarlet/Violet Pokemon", "Modern meta strategies"],
        "year": 2024,
        "regulation": "F",
        "status": "active",
        "meta_notes": "Current competitive format with established meta"
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
def add_2026_format():
    """Example function to add VGC 2026 format when it becomes available"""
    vgc2026_data = {
        "name": "VGC 2026 - Regulation H",
        "description": "Future VGC format with new mechanics and Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "New Mechanics"],
        "restricted": ["TBD"],
        "key_features": ["Future format", "New Pokemon", "Meta evolution"],
        "year": 2026,
        "regulation": "H",
        "status": "predicted",
        "meta_notes": "Format details will be updated as information becomes available"
    }
    return add_new_format("vgc2026", vgc2026_data)

if __name__ == "__main__":
    # Test the configuration system
    formats = load_vgc_formats()
    print(f"Loaded {len(formats)} VGC formats")
    
    # Example: Add a new format
    # add_2026_format()
