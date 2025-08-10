"""
VGC Format Utilities for Pokemon Team Analysis
Handles format detection, prompt generation, and format-specific analysis
"""

import re
from typing import Dict, List, Tuple, Optional

# VGC Format Definitions
VGC_FORMATS = {
    "vgc2025": {
        "name": "VGC 2025 - Regulation G (Predicted)",
        "description": "Upcoming VGC format with potential new mechanics and Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "Potential New Mechanics"],
        "restricted": ["Miraidon", "Koraidon", "Calyrex", "Zacian", "Zamazenta"],
        "key_features": ["Future format", "Potential new Pokemon", "Meta evolution"],
        "year": 2025,
        "regulation": "G",
        "status": "predicted"
    },
    "vgc2024": {
        "name": "VGC 2024 - Regulation F",
        "description": "Latest VGC format with Tera mechanics and new Pokemon",
        "mechanics": ["Tera Types", "4v4 Doubles", "No Dynamax"],
        "restricted": ["Miraidon", "Koraidon", "Calyrex", "Zacian", "Zamazenta"],
        "key_features": ["Tera Type changes", "Scarlet/Violet Pokemon", "Modern meta strategies"],
        "year": 2024,
        "regulation": "F",
        "status": "active"
    },
    "vgc2023": {
        "name": "VGC 2023 - Regulation E", 
        "description": "Previous year's format with Tera mechanics",
        "mechanics": ["Tera Types", "4v4 Doubles", "No Dynamax"],
        "restricted": ["Miraidon", "Koraidon", "Calyrex", "Zacian", "Zamazenta"],
        "key_features": ["Tera Type changes", "Scarlet/Violet Pokemon", "Established meta"],
        "year": 2023,
        "regulation": "E",
        "status": "historical"
    },
    "vgc2022": {
        "name": "VGC 2022 - Regulation D",
        "description": "Format with Dynamax mechanics",
        "mechanics": ["Dynamax", "4v4 Doubles", "No Tera Types"],
        "restricted": ["Calyrex", "Zacian", "Zamazenta", "Eternatus"],
        "key_features": ["Dynamax strategies", "Sword/Shield Pokemon", "Max moves"],
        "year": 2022,
        "regulation": "D",
        "status": "historical"
    },
    "vgc2021": {
        "name": "VGC 2021 - Regulation C",
        "description": "Format with Dynamax mechanics",
        "mechanics": ["Dynamax", "4v4 Doubles", "No Tera Types"],
        "restricted": ["Calyrex", "Zacian", "Zamazenta", "Eternatus"],
        "key_features": ["Dynamax strategies", "Sword/Shield Pokemon", "Max moves"],
        "year": 2021,
        "regulation": "C",
        "status": "historical"
    },
    "vgc2020": {
        "name": "VGC 2020 - Regulation B",
        "description": "Format with Dynamax mechanics",
        "mechanics": ["Dynamax", "4v4 Doubles", "No Tera Types"],
        "restricted": ["Calyrex", "Zacian", "Zamazenta", "Eternatus"],
        "key_features": ["Dynamax strategies", "Sword/Shield Pokemon", "Max moves"],
        "year": 2020,
        "regulation": "B",
        "status": "historical"
    },
    "vgc2019": {
        "name": "VGC 2019 - Regulation A",
        "description": "Format with Dynamax mechanics",
        "mechanics": ["Dynamax", "4v4 Doubles", "No Tera Types"],
        "restricted": ["Calyrex", "Zacian", "Zamazenta", "Eternatus"],
        "key_features": ["Dynamax strategies", "Sword/Shield Pokemon", "Max moves"],
        "year": 2019,
        "regulation": "A",
        "status": "historical"
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
    
    return VGC_FORMATS.get(format_key, VGC_FORMATS["vgc2024"])

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
- If you see Tera types mentioned → VGC 2023-2024
- If you see Dynamax mentioned → VGC 2019-2022  
- If you see restricted legendaries → Check specific years
- If you see modern Pokemon (Gen 9) → VGC 2023-2024
- If you see older Pokemon only → VGC 2019-2022
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
        # Tera Types (VGC 2023-2024+)
        (r"tera\s*type", "VGC 2023-2024+ (Tera Types)"),
        (r"tera\s*blast", "VGC 2023-2024+ (Tera Types)"),
        (r"tera\s*form", "VGC 2023-2024+ (Tera Types)"),
        
        # Dynamax (VGC 2019-2022)
        (r"dynamax", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*move", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*knuckle", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*flare", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*quake", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*geyser", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*lightning", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*starfall", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*phantasm", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*wyrmwind", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*ooze", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*steelspike", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*flutterby", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*airstream", "VGC 2019-2022 (Dynamax)"),
        (r"max\s*guard", "VGC 2019-2022 (Dynamax)"),
        
        # Z-Moves (VGC 2017-2018)
        (r"z-move", "VGC 2017-2018 (Z-Moves)"),
        (r"z\s*move", "VGC 2017-2018 (Z-Moves)"),
        (r"z\s*crystal", "VGC 2017-2018 (Z-Moves)"),
        
        # Mega Evolution (VGC 2014-2016)
        (r"mega\s*evolution", "VGC 2014-2016 (Mega Evolution)"),
        (r"mega\s*[a-z]+", "VGC 2014-2016 (Mega Evolution)"),
        
        # Specific Pokemon indicators
        (r"miraidon", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"koraidon", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"iron\s*[a-z]+", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"roaring\s*moon", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"flutter\s*mane", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"chien-pao", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"chi-yu", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"calyrex", "VGC 2019-2022 (Sword/Shield)"),
        (r"zacian", "VGC 2019-2022 (Sword/Shield)"),
        (r"zamazenta", "VGC 2019-2022 (Sword/Shield)"),
        (r"eternatus", "VGC 2019-2022 (Sword/Shield)"),
        
        # Move availability indicators
        (r"tera\s*blast", "VGC 2023-2024+ (Tera Types)"),
        (r"population\s*bomb", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"bitter\s*blade", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"torch\s*song", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"aqua\s*step", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"wave\s*crash", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"glaive\s*rush", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"order\s*up", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"spicy\s*extract", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"triple\s*arrows", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"ceaseless\s*edge", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"bleakwind\s*storm", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"wildbolt\s*storm", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"sandsear\s*storm", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"springtide\s*storm", "VGC 2023-2024+ (Scarlet/Violet)"),
        (r"freezing\s*glare", "VGC 2020-2022 (Sword/Shield)"),
        (r"thunderous\s*kick", "VGC 2020-2022 (Sword/Shield)"),
        (r"fiery\s*wrath", "VGC 2020-2022 (Sword/Shield)"),
        (r"wicked\s*blow", "VGC 2020-2022 (Sword/Shield)"),
    ]
    
    # Check for pattern matches
    for pattern, format_name in detection_patterns:
        if re.search(pattern, summary_lower):
            return format_name
    
    # Check team composition for Pokemon availability
    modern_pokemon = ["miraidon", "koraidon", "iron", "roaring", "flutter", "chien-pao", "chi-yu", "tinkaton", "annihilape", "palafin"]
    sword_shield_pokemon = ["calyrex", "zacian", "zamazenta", "eternatus", "urshifu", "regieleki", "regidrago"]
    
    team_text = " ".join([str(pokemon) for pokemon in team_data]).lower()
    
    # Count modern vs older Pokemon
    modern_count = sum(1 for pokemon in modern_pokemon if pokemon in team_text)
    sword_shield_count = sum(1 for pokemon in sword_shield_pokemon if pokemon in team_text)
    
    if modern_count > sword_shield_count and modern_count > 0:
        return "VGC 2023-2024+ (Modern Pokemon Detected)"
    elif sword_shield_count > 0:
        return "VGC 2019-2022 (Sword/Shield Era)"
    
    # Check for specific mechanics in team data
    for pokemon in team_data:
        pokemon_str = str(pokemon).lower()
        
        # Check for Tera types in Pokemon data
        if "tera" in pokemon_str:
            return "VGC 2023-2024+ (Tera Types)"
        
        # Check for Dynamax indicators
        if any(term in pokemon_str for term in ["dynamax", "max", "gigantamax"]):
            return "VGC 2019-2022 (Dynamax)"
    
    # Default based on most recent format if unclear
    return "VGC 2024 (Format Unclear - Manual Selection Recommended)"

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
        # VGC 2023-2024 should have Tera types
        pass
    elif "Dynamax" in format_info.get('mechanics', []):
        # VGC 2019-2022 should not have Tera types
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
- If you see Tera types mentioned → VGC 2023-2024+
- If you see Dynamax mentioned → VGC 2019-2022  
- If you see Z-Moves mentioned → VGC 2017-2018
- If you see Mega Evolution mentioned → VGC 2014-2016
- If you see restricted legendaries → Check specific years
- If you see modern Pokemon (Gen 9) → VGC 2023-2024+
- If you see older Pokemon only → VGC 2019-2022 or earlier

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
