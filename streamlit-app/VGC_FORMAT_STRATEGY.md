# VGC Format Handling Strategy

## Overview

This document outlines the comprehensive approach for handling multiple VGC Regulations/Formats in the Pokemon Team Analyzer application. The system uses a **hybrid approach** that combines user selection with AI auto-detection for maximum accuracy and future-proofing.

**IMPORTANT CORRECTION**: Regulations A-I are all Pokemon Scarlet and Violet rulesets, not tied to specific years. The year does not denote the regulation letter.

## Why Hybrid Approach is Optimal

### 1. **User Expertise + AI Intelligence**
- **Competitive players** often know their format and want control
- **AI auto-detection** handles cases where users aren't sure
- **Best of both worlds** - human knowledge + machine learning

### 2. **Future-Proof Architecture**
- **Easy to add new regulations** (J, K, L, etc.)
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
🏆 VGC Format I      ← Current competitive format (Scarlet/Violet)
🏆 VGC Format H      ← Previous format (Scarlet/Violet)
🏆 VGC Format G      ← Previous format (Scarlet/Violet)
📚 VGC Format F      ← Historical format (Scarlet/Violet)
📚 VGC Format A      ← Historical format (Scarlet/Violet)
⚙️ Custom Format                 ← User-defined rules
```

### Format Status System
- **Active**: Current competitive format (VGC Format I)
- **Historical**: Past formats (VGC Formats A-H)
- **Custom**: User-defined formats

## AI Auto-Detection Capabilities

### Detection Methods
1. **Mechanic Detection**
   - Tera Types → VGC Formats A-I (Scarlet/Violet Era)
- Dynamax → VGC Formats A-I (Dynamax Era)
- Z-Moves → VGC Formats A-I (Z-Move Era)
   - Mega Evolution → Not available in Sword/Shield or Scarlet/Violet

2. **Pokemon Availability**
   - Modern Pokemon (Gen 9) → VGC Formats A-I (Scarlet/Violet Era)
- Sword/Shield Pokemon → VGC Formats A-I (Sword/Shield Era)
   - Restricted Legendaries → Format-specific availability

3. **Move Legality**
   - Tera Blast → VGC Formats A-I (Scarlet/Violet Era)
- Max Moves → VGC Formats A-I (Dynamax Era)
   - Signature moves → Format-specific availability

### Detection Accuracy
- **High accuracy** for modern formats (2023-2025, Regulations G-I)
- **Good accuracy** for recent formats (2017-2022, Regulations A-F)
- **Fallback to manual selection** when unclear

## Future-Proofing Features

### 1. **Dynamic Format Management**
```python
# Easy to add new formats
from utils.vgc_format_config import add_new_format

vgc_j_data = {
    "name": "VGC Format J",
    "description": "Future VGC format",
    "mechanics": ["Tera Types", "4v4 Doubles", "New Mechanics", "Scarlet/Violet mechanics"],
    "regulation": "J",
    "status": "predicted"
}

add_new_format("vgc_j", vgc_j_data)
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
def add_j_format():
    vgc_j_data = {
        "name": "VGC Format J",
        "description": "Future VGC format with new mechanics",
        "mechanics": ["Tera Types", "4v4 Doubles", "New Mechanics", "Scarlet/Violet mechanics"],
        "restricted": ["TBD"],
        "key_features": ["Future format", "New Pokemon"],
        "regulation": "J",
        "status": "predicted"
    }
    return add_new_format("vgc_j", vgc_j_data)
```

### Step 2: Update Detection Patterns
```python
# In vgc_format_utils.py
detection_patterns = [
    # Add new mechanics
    (r"new_mechanic", "VGC Format J+ (New Mechanics)"),
    # Add new Pokemon
    (r"new_pokemon", "VGC Format J+ (New Pokemon)"),
    # Add new moves
    (r"new_move", "VGC Format J+ (New Moves)")
]
```

### Step 3: Update Prompts
```python
# In vgc_format_utils.py
def generate_future_proof_prompt(base_prompt, format_key, custom_format_name=None):
    if format_key == "vgc_j":
        return base_prompt + """
        **VGC Format J ANALYSIS:**
        - Focus on new mechanics and strategies
        - Consider meta evolution from Formats A-I
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

**Note**: Regulations A-I are all Pokemon Scarlet and Violet rulesets, with Tera mechanics. The year does not determine the regulation letter - they are separate progression systems.
