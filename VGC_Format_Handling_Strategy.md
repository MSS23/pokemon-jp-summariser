# VGC Format Handling Strategy

## IMPORTANT CORRECTION
**Regulations A to I are all Pokemon Scarlet and Violet rulesets, not tied to specific years. The year does not denote the regulation letter for example Regulation A-I are all Pokemon Scarlet and Violet rulesets.**

## Overview
This document outlines the strategy for handling multiple VGC (Video Game Championships) Regulations/Formats within the Pokemon Translation Web App. The approach is designed to be future-proof and adaptable to new regulations as they are announced.

## Current VGC Format Support

### Available Formats in UI
- **Auto-Detect Format**: AI automatically detects the VGC format
- **VGC 2025 - Regulation I**: Current active format (Scarlet/Violet)
- **VGC 2024 - Regulation H**: Historical format (Scarlet/Violet)
- **VGC 2023 - Regulation G**: Historical format (Scarlet/Violet)
- **VGC 2022 - Regulation F**: Historical format (Scarlet/Violet)
- **VGC 2021 - Regulation E**: Historical format (Scarlet/Violet)
- **VGC 2020 - Regulation D**: Historical format (Scarlet/Violet)
- **VGC 2019 - Regulation C**: Historical format (Scarlet/Violet)
- **VGC 2018 - Regulation B**: Historical format (Scarlet/Violet)
- **VGC 2017 - Regulation A**: Historical format (Scarlet/Violet)
- **Custom Format**: User-defined format with custom rules

### Format Status System
- **Active**: VGC 2025 - Regulation I (Current competitive format)
- **Historical**: VGC 2017-2024 (Past formats, all Scarlet/Violet era)
- **Auto**: AI auto-detection mode
- **Custom**: User-defined formats

## Hybrid Approach: User Selection + AI Enhancement

### 1. User Control via Dropdown
- Users can manually select their preferred VGC format
- Clear labeling with regulation letters and years
- Status indicators (active, historical, predicted)
- Custom format option for special cases

### 2. Enhanced AI Auto-Detection
- **Tera Types Detection**: VGC 2017-2025+ (Regulations A-I, all Scarlet/Violet)
- **Scarlet/Violet Pokemon Detection**: All formats A-I support Scarlet/Violet Pokemon
- **Mechanics Recognition**: Focuses on Tera mechanics (all regulations A-I)
- **Fallback Logic**: Defaults to Scarlet/Violet era if unclear

### 3. Dynamic Format Management
- JSON-based configuration (`vgc_formats.json`)
- Easy addition of new formats without code changes
- Centralized format definitions and metadata
- Status tracking for active/historical formats

## Detection Methods

### Primary Detection Patterns
1. **Tera Mechanics**: All regulations A-I use Tera Types
2. **Pokemon Availability**: Scarlet/Violet era Pokemon across all regulations
3. **Move Legality**: Scarlet/Violet era moves and abilities
4. **Strategy Patterns**: Format-specific meta strategies

### Detection Accuracy
- **High Accuracy**: Tera types, Scarlet/Violet Pokemon, modern moves
- **Medium Accuracy**: Team composition analysis
- **Fallback**: Defaults to Scarlet/Violet era (Regulations A-I)

## Prompt Engineering Strategy

### Format-Specific Prompts
- **Auto-Detection**: Enhanced instructions for format identification
- **Specific Formats**: Tailored analysis for each regulation
- **Custom Formats**: Flexible analysis for user-defined rules
- **Future-Proofing**: Adaptable prompts for new regulations

### Dynamic Prompt Generation
- Base prompt + format-specific instructions
- Mechanics-specific analysis requirements
- Meta positioning and viability assessment
- Future adaptation considerations

## Implementation Details

### File Structure
```
streamlit-app/
├── utils/
│   ├── vgc_format_utils.py      # Core format logic
│   ├── vgc_format_config.py     # Format definitions
│   └── gemini_summary.py        # LLM integration
├── Summarise_Article.py         # Main Streamlit app
└── vgc_formats.json            # Format configuration
```

### Key Functions
- `detect_format_from_team()`: AI format detection
- `get_available_formats()`: UI format options
- `generate_future_proof_prompt()`: Dynamic prompt generation
- `get_format_status_info()`: Status display

## Future-Proofing Features

### 1. Easy Format Addition
```python
# Example: Adding VGC 2026
def add_2026_format():
    new_format = {
        "name": "VGC 2026 - Regulation J",
        "description": "Future VGC format with potential new mechanics",
        "mechanics": "Tera Types, potential new mechanics",
        "restricted_pokemon": "To be determined",
        "status": "predicted"
    }
    DEFAULT_VGC_FORMATS["vgc2026"] = new_format
```

### 2. Adaptive Prompt Generation
- Automatically incorporates new format mechanics
- Maintains consistency across all formats
- Scales with regulation complexity

### 3. Backward Compatibility
- Historical formats remain accessible
- Consistent analysis methodology
- Gradual deprecation support

## Benefits of This Approach

### For Users
- **Flexibility**: Choose specific format or auto-detect
- **Accuracy**: AI-enhanced format recognition
- **Clarity**: Clear format status and descriptions
- **Future-Ready**: Supports upcoming regulations

### For Developers
- **Maintainable**: Centralized format management
- **Extensible**: Easy addition of new formats
- **Consistent**: Unified analysis methodology
- **Scalable**: Handles increasing regulation complexity

## Usage Examples

### 1. Auto-Detection Mode
```python
# User selects "Auto-Detect Format"
# AI analyzes team and determines format
# Format-specific analysis is generated
```

### 2. Specific Format Selection
```python
# User selects "VGC 2025 - Regulation I"
# Analysis focuses on current meta and strategies
# Tera mechanics optimization emphasized
```

### 3. Custom Format
```python
# User defines custom rules
# Analysis adapts to custom mechanics
# Flexible evaluation criteria
```

## Conclusion

This hybrid approach provides the best of both worlds:
- **User Control**: Manual selection when needed
- **AI Enhancement**: Automatic detection and analysis
- **Future-Proof**: Adaptable to new regulations
- **Maintainable**: Easy to update and extend

The system is designed to handle the complexity of multiple VGC regulations while maintaining simplicity for users and developers alike.

## Final Note
**Regulations A-I are all Pokemon Scarlet and Violet rulesets, with Tera mechanics. The year does not determine the regulation letter - they are separate progression systems. This app focuses exclusively on Scarlet and Violet era formats and does not support Sword and Shield article translation.**
