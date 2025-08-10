# VGC Format Handling Strategy

## Overview

This document outlines the comprehensive approach for handling multiple VGC Regulations/Formats in the Pokemon Team Analyzer application. The system uses a **hybrid approach** that combines user selection with AI auto-detection for maximum accuracy and future-proofing.

## Why Hybrid Approach is Optimal

### 1. **User Expertise + AI Intelligence**
- **Competitive players** often know their format and want control
- **AI auto-detection** handles cases where users aren't sure
- **Best of both worlds** - human knowledge + machine learning

### 2. **Future-Proof Architecture**
- **Easy to add new regulations** (2025, 2026, etc.)
- **Dynamic format management** through configuration files
- **Extensible prompt system** that adapts to any format

### 3. **Flexibility for Different Use Cases**
- **Tournament analysis** - specific format selection
- **Historical research** - past format analysis
- **Custom formats** - regional or tournament-specific rules
- **Future planning** - upcoming regulation preparation

## Current Implementation

### Format Selection UI
```
🤖 Auto-detect (Recommended)     ← AI automatically identifies format
🏆 VGC 2024 - Regulation F      ← Current competitive format
🏆 VGC 2023 - Regulation E      ← Recent format
📚 VGC 2022 - Regulation D      ← Historical format
📚 VGC 2019 - Regulation A      ← Historical format
⚙️ Custom Format                 ← User-defined rules
```

### Format Status System
- **Active**: Current competitive format (VGC 2024)
- **Predicted**: Upcoming formats (VGC 2025)
- **Historical**: Past formats (VGC 2019-2023)
- **Custom**: User-defined formats

## AI Auto-Detection Capabilities

### Detection Methods
1. **Mechanic Detection**
   - Tera Types → VGC 2023-2024+
   - Dynamax → VGC 2019-2022
   - Z-Moves → VGC 2017-2018
   - Mega Evolution → VGC 2014-2016

2. **Pokemon Availability**
   - Modern Pokemon (Gen 9) → VGC 2023-2024+
   - Sword/Shield Pokemon → VGC 2019-2022
   - Restricted Legendaries → Format-specific years

3. **Move Legality**
   - Tera Blast → VGC 2023-2024+
   - Max Moves → VGC 2019-2022
   - Signature moves → Format-specific availability

### Detection Accuracy
- **High accuracy** for modern formats (2023-2024)
- **Good accuracy** for recent formats (2019-2022)
- **Moderate accuracy** for older formats (pre-2019)
- **Fallback to manual selection** when unclear

## Future-Proofing Features

### 1. **Dynamic Format Management**
```python
# Easy to add new formats
from utils.vgc_format_config import add_new_format

vgc2026_data = {
    "name": "VGC 2026 - Regulation H",
    "description": "Future VGC format",
    "mechanics": ["Tera Types", "4v4 Doubles", "New Mechanics"],
    "year": 2026,
    "regulation": "H",
    "status": "predicted"
}

add_new_format("vgc2026", vgc2026_data)
```

### 2. **Adaptive Prompt System**
- **Format-specific instructions** for each regulation
- **Future-proof analysis** that considers adaptability
- **Meta positioning** for current and upcoming formats
- **Cross-format strategy** analysis

### 3. **Configuration Files**
- **JSON-based format definitions** for easy updates
- **External format management** without code changes
- **Import/export capabilities** for format sharing
- **Version control** for format evolution

## Adding New VGC Formats

### Step 1: Update Configuration
```python
# In vgc_format_config.py
def add_2026_format():
    vgc2026_data = {
        "name": "VGC 2026 - Regulation H",
        "description": "Future VGC format with new mechanics",
        "mechanics": ["Tera Types", "4v4 Doubles", "New Mechanics"],
        "restricted": ["TBD"],
        "key_features": ["Future format", "New Pokemon"],
        "year": 2026,
        "regulation": "H",
        "status": "predicted"
    }
    return add_new_format("vgc2026", vgc2026_data)
```

### Step 2: Update Detection Patterns
```python
# In vgc_format_utils.py
detection_patterns = [
    # Add new mechanics
    (r"new_mechanic", "VGC 2026+ (New Mechanics)"),
    # Add new Pokemon
    (r"new_pokemon", "VGC 2026+ (New Pokemon)"),
    # Add new moves
    (r"new_move", "VGC 2026+ (New Moves)")
]
```

### Step 3: Update Prompts
```python
# In vgc_format_utils.py
def generate_future_proof_prompt(base_prompt, format_key, custom_format_name=None):
    if format_key == "vgc2026":
        return base_prompt + """
        **VGC 2026 ANALYSIS:**
        - Focus on new mechanics and strategies
        - Consider meta evolution from 2024-2025
        - Analyze team adaptability to new rules
        """
```

## Best Practices

### 1. **Always Default to Auto-Detection**
- Users can override if they know the format
- AI provides intelligent fallback
- Reduces user errors

### 2. **Provide Clear Format Information**
- Show format status (Active/Historical/Predicted)
- Display key mechanics and restrictions
- Include meta notes and trends

### 3. **Support Custom Formats**
- Allow tournament-specific rules
- Enable regional format variations
- Support experimental formats

### 4. **Maintain Backward Compatibility**
- Keep historical format support
- Preserve old team analysis capabilities
- Maintain format transition guides

## Comparison with Alternative Approaches

### ❌ **Pure AI Detection Only**
- **Pros**: Fully automatic, no user input needed
- **Cons**: Less accurate, no user control, harder to debug

### ❌ **Pure User Selection Only**
- **Pros**: User control, predictable results
- **Cons**: Requires user knowledge, prone to errors, not future-proof

### ✅ **Hybrid Approach (Current)**
- **Pros**: Best of both worlds, future-proof, user-friendly
- **Cons**: Slightly more complex implementation

## Conclusion

The hybrid approach provides the optimal balance of:
- **User control** for experienced players
- **AI assistance** for format detection
- **Future-proofing** for new regulations
- **Flexibility** for custom formats
- **Maintainability** for developers

This system will continue to work effectively as new VGC regulations are introduced, requiring minimal updates while maintaining high accuracy and user satisfaction.
