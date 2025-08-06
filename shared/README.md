# Shared Utilities

This directory contains utilities, configurations, and models that are shared between the Streamlit and React versions of the Pokemon VGC Summariser application.

## 📁 Structure

```
shared/
├── utils/              # Common utility functions
│   └── shared_utils.py # Shared utility functions
├── config/             # Shared configuration
│   └── config_loader.py # Configuration management
└── models/             # Shared data models
    └── (future models) # Data structures and types
```

## 🔧 Usage

### Python (Streamlit)
```python
import sys
sys.path.append('../shared')
from utils.shared_utils import extract_pokemon_names
from config.config_loader import load_config
```

### JavaScript/TypeScript (React)
```typescript
// Import shared utilities
import { extractPokemonNames } from '../shared/utils/shared_utils';
import { loadConfig } from '../shared/config/config_loader';
```

## 📦 Shared Components

### Utilities (`utils/`)
- **Pokemon Name Extraction**: Extract Pokémon names from text
- **Text Processing**: Common text manipulation functions
- **Data Validation**: Shared validation logic
- **Format Conversion**: Data format utilities

### Configuration (`config/`)
- **API Configuration**: Shared API settings
- **Environment Variables**: Common environment setup
- **Feature Flags**: Shared feature toggles
- **Constants**: Shared application constants

### Models (`models/`)
- **Data Types**: Shared TypeScript/Python types
- **Interfaces**: Common data structures
- **Schemas**: Data validation schemas

## 🔄 Synchronization

When updating shared utilities:
1. Update the shared file
2. Test in both Streamlit and React versions
3. Ensure backward compatibility
4. Update documentation

## 🛠️ Development

### Adding New Shared Utilities
1. Create the utility in the appropriate shared directory
2. Add proper documentation and type hints
3. Test with both applications
4. Update this README

### Best Practices
- Keep utilities pure and stateless
- Use clear, descriptive function names
- Add comprehensive documentation
- Include type hints for better IDE support
- Write tests for critical utilities

## 📝 Examples

### Shared Utility Function
```python
# shared/utils/shared_utils.py
def extract_pokemon_names(text: str) -> List[str]:
    """
    Extract Pokémon names from text using regex patterns.
    
    Args:
        text (str): Input text to search
        
    Returns:
        List[str]: List of found Pokémon names
    """
    # Implementation here
    pass
```

### Shared Configuration
```python
# shared/config/config_loader.py
def load_config() -> Dict[str, Any]:
    """
    Load shared configuration for both applications.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    """
    # Implementation here
    pass
```

## 🔗 Integration

Both applications should import from the shared directory to maintain consistency and reduce code duplication. This ensures that:

- **Consistency**: Both apps use the same logic
- **Maintainability**: Single source of truth for shared code
- **Testing**: Shared utilities can be tested once
- **Performance**: No code duplication

---

**Note**: Keep shared utilities focused on core business logic that doesn't depend on specific UI frameworks or technologies. 