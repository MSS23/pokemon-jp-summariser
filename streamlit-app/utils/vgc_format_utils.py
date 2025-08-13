"""
VGC Format Utilities for Pokemon Team Analysis
Handles format detection, prompt generation, and format-specific analysis
"""

import re
from typing import Dict, List, Tuple, Optional

# VGC Format Definitions
VGC_FORMATS = {
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

def get_format_info(format_key: str) -> Dict:
    """Get information about a specific VGC format"""
    if format_key == "custom":
        return {
            "name": "Custom Format",
            "description": "User-defined VGC format",
            "mechanics": ["Custom rules"],
            "restricted": [],
            "key_features": ["Custom format"],
            "year": None,
            "regulation": "Custom"
        }
    elif format_key == "auto":
        return {
            "name": "Auto-Detected Format",
            "description": "AI-detected VGC format from team analysis",
            "mechanics": ["Auto-detected"],
            "restricted": [],
            "key_features": ["Format detection"],
            "year": None,
            "regulation": "Auto"
        }
    
    return VGC_FORMATS.get(format_key, VGC_FORMATS["vgc_b"])

def generate_format_specific_prompt(base_prompt: str, format_key: str, custom_format_name: str = None) -> str:
    """Generate a format-specific prompt based on the selected VGC format"""
    
    if format_key == "auto":
        # For auto-detection, enhance the base prompt
        enhanced_prompt = base_prompt + f"""

**ENHANCED FORMAT DETECTION INSTRUCTIONS:**
- **ANALYZE TEAM COMPOSITION**: Look at Pokemon types, moves, and strategies
- **IDENTIFY MECHANICS**: Check for Dynamax, Tera types, or other format-specific features
- **CHECK POKEMON AVAILABILITY**: Determine which Pokemon are legal in this format
- **ANALYZE MOVE LEGALITY**: Ensure moves are available in the detected format
- **FORMAT-SPECIFIC ANALYSIS**: Provide detailed analysis for the detected format

**FORMAT DETECTION EXAMPLES:**
- If you see Tera types mentioned → VGC Formats A-I (Tera Types - Scarlet/Violet Era)
- If you see Dynamax mentioned → VGC Formats A-I (Dynamax Era)
- If you see restricted legendaries → VGC Formats A-I (Restricted Pokemon Era)
- If you see modern Pokemon (Gen 9) → VGC Formats A-I (Scarlet/Violet Era)
- If you see older Pokemon only → VGC Formats A-I (Legacy Era)
"""
        return enhanced_prompt
    
    elif format_key == "custom" and custom_format_name:
        # For custom formats, add custom instructions
        custom_prompt = base_prompt + f"""

**CUSTOM FORMAT ANALYSIS: {custom_format_name}**
- **CUSTOM RULES**: Analyze the team according to the custom format rules
- **FORMAT-SPECIFIC STRATEGIES**: Provide analysis relevant to this custom format
- **META POSITIONING**: Consider how the team fits in this custom meta
- **CUSTOM MECHANICS**: Identify any unique mechanics or rules for this format
"""
        return custom_prompt
    
    else:
        # For specific formats, add format-specific instructions
        format_info = get_format_info(format_key)
        format_prompt = base_prompt + f"""

**FORMAT-SPECIFIC ANALYSIS: {format_info['name']}**
- **FORMAT MECHANICS**: {', '.join(format_info['mechanics'])}
- **RESTRICTED POKEMON**: {', '.join(format_info['restricted']) if format_info['restricted'] else 'None'}
- **KEY FEATURES**: {', '.join(format_info['key_features'])}
- **FORMAT-SPECIFIC STRATEGIES**: Focus on strategies relevant to {format_info['name']}
- **META TRENDS**: Consider the meta trends and positioning for this specific format
- **FORMAT VIABILITY**: Assess team viability specifically for {format_info['name']}
"""
        return format_prompt

def detect_format_from_team(team_data: List[Dict], summary_text: str) -> str:
    """Attempt to detect VGC format from team composition and summary text"""
    
    summary_lower = summary_text.lower()
    
    # Enhanced detection patterns
    detection_patterns = [
            # Tera Types (VGC Formats A-I - Scarlet/Violet Era)
            (r"tera\s*type", "VGC Formats A-I (Tera Types - Scarlet/Violet Era)"),
            (r"tera\s*blast", "VGC Formats A-I (Tera Types - Scarlet/Violet Era)"),
            (r"tera\s*form", "VGC Formats A-I (Tera Types - Scarlet/Violet Era)"),
            
            # Specific Pokemon indicators (all from Scarlet/Violet era)
            (r"miraidon", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"koraidon", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"iron\s*[a-z]+", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"roaring\s*moon", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"flutter\s*mane", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"chien-pao", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"chi-yu", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"calyrex", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"zacian", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"zamazenta", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"eternatus", "VGC Formats A-I (Scarlet/Violet Era)"),
            
            # Move availability indicators (all from Scarlet/Violet era)
            (r"population\s*bomb", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"bitter\s*blade", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"torch\s*song", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"aqua\s*step", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"wave\s*crash", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"glaive\s*rush", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"order\s*up", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"spicy\s*extract", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"triple\s*arrows", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"ceaseless\s*edge", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"bleakwind\s*storm", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"wildbolt\s*storm", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"sandsear\s*storm", "VGC Formats A-I (Scarlet/Violet Era)"),
            (r"springtide\s*storm", "VGC Formats A-I (Scarlet/Violet Era)"),
        ]
    
    # Check for pattern matches
    for pattern, format_name in detection_patterns:
        if re.search(pattern, summary_lower):
            return format_name
    
    # Check team composition for Pokemon availability
    scarlet_violet_pokemon = ["miraidon", "koraidon", "iron", "roaring", "flutter", "chien-pao", "chi-yu", "tinkaton", "annihilape", "palafin", "calyrex", "zacian", "zamazenta", "eternatus", "urshifu", "regieleki", "regidrago"]
    
    team_text = " ".join([str(pokemon) for pokemon in team_data]).lower()
    
    # All Pokemon are from Scarlet/Violet era (Formats A-I)
    if any(pokemon in team_text for pokemon in scarlet_violet_pokemon):
        return "VGC Formats A-I (Scarlet/Violet Era)"
    
    # Check for specific mechanics in team data
    for pokemon in team_data:
        pokemon_str = str(pokemon).lower()
        
        # Check for Tera types in Pokemon data (all Formats A-I)
        if "tera" in pokemon_str:
            return "VGC Formats A-I (Tera Types - Scarlet/Violet Era)"
    
    # Default - all formats are Scarlet/Violet era with Tera mechanics
    return "VGC Formats A-I (Scarlet/Violet Era)"

def get_format_analysis_prompt(format_key: str, custom_format_name: str = None) -> str:
    """Get a prompt specifically for analyzing teams in a given format"""
    
    if format_key == "auto":
        return """
Analyze this Pokemon team and automatically detect the VGC format based on:
1. Team composition and Pokemon availability
2. Moves and abilities used
3. Strategies and mechanics mentioned
4. Overall meta positioning

Provide format-specific analysis for the detected regulation.
"""
    
    elif format_key == "custom" and custom_format_name:
        return f"""
Analyze this Pokemon team specifically for the custom format: {custom_format_name}

Consider:
1. How the team fits the custom format rules
2. Format-specific strategies and counters
3. Meta positioning within this custom format
4. Any unique advantages or disadvantages
"""
    
    else:
        format_info = get_format_info(format_key)
        return f"""
Analyze this Pokemon team specifically for {format_info['name']}.

Focus on:
1. {format_info['mechanics'][0]} strategies and optimization
2. Meta trends and positioning for this format
3. Team viability in {format_info['name']}
4. Format-specific counters and strategies
5. How the team leverages {format_info['key_features'][0]}
"""

def validate_format_compatibility(team_data: List[Dict], format_key: str) -> Tuple[bool, List[str]]:
    """Validate if a team is compatible with a specific VGC format"""
    
    if format_key == "auto":
        return True, ["Auto-detection mode - compatibility will be determined during analysis"]
    
    format_info = get_format_info(format_key)
    issues = []
    
    # Check for restricted Pokemon
    for pokemon in team_data:
        pokemon_name = str(pokemon.get('name', '')).lower()
        if any(restricted.lower() in pokemon_name for restricted in format_info.get('restricted', [])):
            issues.append(f"{pokemon.get('name', 'Unknown')} is restricted in {format_info['name']}")
    
    # Check for format-specific mechanics
    if "Tera Types" in format_info.get('mechanics', []):
        # VGC Formats A-I should have Tera types
        pass
    elif "Dynamax" in format_info.get('mechanics', []):
        # VGC Formats A-I should not have Tera types
        pass
    
    return len(issues) == 0, issues

def add_new_vgc_format(format_key: str, format_data: Dict) -> bool:
    """Dynamically add a new VGC format to the system"""
    try:
        if format_key not in VGC_FORMATS:
            VGC_FORMATS[format_key] = format_data
            return True
        return False
    except Exception as e:
        print(f"Error adding new VGC format: {e}")
        return False

def get_available_formats() -> List[Tuple[str, str]]:
    """Get list of available formats for UI dropdown"""
    formats = []
    
    # Add auto-detection first
    formats.append(("auto", "🤖 Auto-detect (Recommended)"))
    
    # Add active/predicted formats
    for key, info in VGC_FORMATS.items():
        if info.get("status") in ["active", "predicted"]:
            formats.append((key, f"🏆 {info['name']}"))
    
    # Add historical formats
    for key, info in VGC_FORMATS.items():
        if info.get("status") == "historical":
            formats.append((key, f"📚 {info['name']}"))
    
    # Add custom format option
    formats.append(("custom", "⚙️ Custom Format"))
    
    return formats

def get_format_status_info(format_key: str) -> Dict:
    """Get detailed status information for a format"""
    if format_key == "auto":
        return {
            "status": "auto",
            "status_text": "Auto-Detection Active",
            "description": "AI will automatically identify the VGC format from team composition, moves, and strategies",
            "color": "#0ea5e9",
            "icon": "🤖"
        }
    elif format_key == "custom":
        return {
            "status": "custom",
            "status_text": "Custom Format",
            "description": "User-defined VGC format with custom rules",
            "color": "#f59e0b",
            "icon": "⚙️"
        }
    
    format_info = get_format_info(format_key)
    status = format_info.get("status", "unknown")
    
    status_configs = {
        "active": {
            "status_text": "Active Format",
            "description": f"Current competitive format: {format_info['description']}",
            "color": "#10b981",
            "icon": "🏆"
        },
        "predicted": {
            "status_text": "Predicted Format",
            "description": f"Upcoming format: {format_info['description']}",
            "color": "#8b5cf6",
            "icon": "🔮"
        },
        "historical": {
            "status_text": "Historical Format",
            "description": f"Past format: {format_info['description']}",
            "color": "#6b7280",
            "icon": "📚"
        }
    }
    
    return {
        "status": status,
        **status_configs.get(status, status_configs["historical"])
    }

def generate_future_proof_prompt(base_prompt: str, format_key: str, custom_format_name: str = None) -> str:
    """Generate a future-proof prompt that adapts to any VGC format"""
    
    if format_key == "auto":
        enhanced_prompt = base_prompt + f"""

**ENHANCED FORMAT DETECTION INSTRUCTIONS:**
- **ANALYZE TEAM COMPOSITION**: Look at Pokemon types, moves, and strategies
- **IDENTIFY MECHANICS**: Check for Dynamax, Tera types, Z-Moves, Mega Evolution, or other format-specific features
- **CHECK POKEMON AVAILABILITY**: Determine which Pokemon are legal in this format
- **ANALYZE MOVE LEGALITY**: Ensure moves are available in the detected format
- **FORMAT-SPECIFIC ANALYSIS**: Provide detailed analysis for the detected format
- **META POSITIONING**: Consider how the team fits in the current meta for that format

        **FORMAT DETECTION EXAMPLES:**
        - If you see Tera types mentioned → VGC Formats A-I (Scarlet/Violet Era)
- If you see Scarlet/Violet Pokemon → VGC Formats A-I (Scarlet/Violet Era)
- If you see Miraidon/Koraidon → VGC Formats A-I (Scarlet/Violet Era)
- If you see Iron Pokemon → VGC Formats A-I (Scarlet/Violet Era)
- If you see Paradox Pokemon → VGC Formats A-I (Scarlet/Violet Era)
        - If you see restricted legendaries → Check specific regulations within A-I
        - All formats A-I are Scarlet/Violet era with Tera mechanics

**FUTURE-PROOF ANALYSIS:**
- Consider how the team might adapt to future regulations
- Identify core strategies that transcend specific formats
- Suggest potential adaptations for upcoming changes
"""
        return enhanced_prompt
    
    elif format_key == "custom" and custom_format_name:
        custom_prompt = base_prompt + f"""

**CUSTOM FORMAT ANALYSIS: {custom_format_name}**
- **CUSTOM RULES**: Analyze the team according to the custom format rules
- **FORMAT-SPECIFIC STRATEGIES**: Provide analysis relevant to this custom format
- **META POSITIONING**: Consider how the team fits in this custom meta
- **CUSTOM MECHANICS**: Identify any unique mechanics or rules for this format
- **ADAPTABILITY**: Consider how the team could adapt to other formats
"""
        return custom_prompt
    
    else:
        format_info = get_format_info(format_key)
        status_info = get_format_status_info(format_key)
        
        format_prompt = base_prompt + f"""

**FORMAT-SPECIFIC ANALYSIS: {format_info['name']}**
- **FORMAT STATUS**: {status_info['status_text']}
- **FORMAT MECHANICS**: {', '.join(format_info['mechanics'])}
- **RESTRICTED POKEMON**: {', '.join(format_info['restricted']) if format_info['restricted'] else 'None'}
- **KEY FEATURES**: {', '.join(format_info['key_features'])}
- **FORMAT-SPECIFIC STRATEGIES**: Focus on strategies relevant to {format_info['name']}
- **META TRENDS**: Consider the meta trends and positioning for this specific format
- **FORMAT VIABILITY**: Assess team viability specifically for {format_info['name']}

**FUTURE-PROOF CONSIDERATIONS:**
- How does this team's strategy translate to other formats?
- What core elements make this team adaptable?
- How might upcoming regulation changes affect this team?
"""
        return format_prompt
