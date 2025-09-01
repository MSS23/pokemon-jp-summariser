# API Documentation

## Core Classes

### GeminiVGCAnalyzer

**Location**: `src/core/analyzer.py`

The main analysis engine that orchestrates VGC content analysis using Google Gemini AI.

#### Constructor

```python
analyzer = GeminiVGCAnalyzer()
```

Initializes the analyzer with:
- Gemini API configuration
- Text and vision models (gemini-2.5-flash-lite)
- Generation config optimized for VGC analysis
- Helper components (scraper, validator)

#### Methods

##### `analyze_article(content: str, url: str = None) -> Dict[str, Any]`

Analyzes VGC article content and returns comprehensive team analysis.

**Parameters:**
- `content` (str): Article text to analyze
- `url` (str, optional): Source URL for context and caching

**Returns:**
```python
{
    "title": "Article title or summary",
    "author": "Author name or 'Not specified'",
    "regulation": "VGC regulation (e.g., 'Regulation G') or 'Not specified'",
    "pokemon_team": [
        {
            "name": "Pokemon name with correct form",
            "ability": "Pokemon ability",
            "held_item": "Item name",
            "tera_type": "Tera type",
            "nature": "Pokemon nature",
            "ev_spread": {
                "HP": 252,
                "Attack": 0,
                "Defense": 0,
                "Special Attack": 252,
                "Special Defense": 4,
                "Speed": 0,
                "total": 508
            },
            "moves": ["Move 1", "Move 2", "Move 3", "Move 4"],
            "ev_explanation": "Strategic reasoning for EV distribution",
            "role_in_team": "Pokemon's strategic role"
        }
    ],
    "overall_strategy": "Team strategy and synergies",
    "tournament_context": "Tournament context if mentioned",
    "translation_notes": "Translation notes and corrections",
    "content_summary": "Brief summary of article content",
    "analysis_confidence": 0.85,  # Confidence score (0.0-1.0)
    "user_guidance": "Guidance for low confidence analyses"
}
```

**Raises:**
- `ValueError`: For invalid content, failed extraction, or analysis errors

##### `scrape_article(url: str) -> Optional[str]`

Scrapes article content from URL using multi-strategy approach.

**Parameters:**
- `url` (str): URL to scrape

**Returns:**
- `str`: Extracted article content
- `None`: If extraction fails

**Raises:**
- `ValueError`: For invalid URLs or extraction failures

##### `validate_url(url: str) -> bool`

Validates if URL is accessible.

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `bool`: True if accessible, False otherwise

---

### ArticleScraper

**Location**: `src/core/scraper.py`

Handles robust web scraping with multiple fallback strategies.

#### Methods

##### `scrape_article(url: str) -> Optional[str]`

Multi-strategy article scraping with enhanced Japanese site support.

**Strategies:**
1. Standard headers with comprehensive browser simulation
2. Mobile headers for mobile-optimized content
3. Japanese-specific headers for better site compatibility
4. Session-based retry with dynamic content delays

**Parameters:**
- `url` (str): URL to scrape

**Returns:**
- `str`: Extracted content
- `None`: If all strategies fail

##### `calculate_ui_content_ratio(content: str) -> float`

Calculates ratio of UI/navigation content to actual content.

**Parameters:**
- `content` (str): Content to analyze

**Returns:**
- `float`: UI ratio (0.0-1.0, lower is better)

---

### PokemonValidator

**Location**: `src/core/pokemon_validator.py`

Handles Pokemon name validation, form correction, and translation.

#### Methods

##### `fix_pokemon_name_translations(result: Dict[str, Any]) -> Dict[str, Any]`

Corrects Pokemon names in analysis results using translation dictionary.

**Features:**
- Generation 9 Pokemon priority (Gholdengo, Ogerpon forms, etc.)
- Hisuian form corrections (Arcanine-Hisui, etc.)
- Treasures of Ruin distinction (Chi-Yu vs Chien-Pao)
- Forces of Nature forme handling (Tornadus-Incarnate vs Tornadus-Therian)

##### `apply_pokemon_validation(result: Dict[str, Any]) -> Dict[str, Any]`

Applies comprehensive validation checks:
- Invalid Paradox Pokemon forms (removes incorrect suffixes)
- Regional form formatting (Hisui, Galar, Alola)
- EV spread validation (0-252 range, divisible by 4, ≤508 total)

##### `is_valid_pokemon_name(name: str) -> bool`

Checks if a Pokemon name appears valid.

##### `get_pokemon_suggestions(partial_name: str) -> List[str]`

Returns Pokemon name suggestions for partial input.

---

## Configuration

### Config Class

**Location**: `src/utils/config.py`

Manages application configuration and API keys.

#### Methods

##### `get_google_api_key() -> str`

Retrieves Google Gemini API key from environment or secrets.

**Priority:**
1. `GOOGLE_API_KEY` environment variable
2. Streamlit secrets (`st.secrets.google_api_key`)

**Raises:**
- `ValueError`: If no API key found

---

### CacheManager

**Location**: `src/utils/cache_manager.py`

Intelligent caching system for analysis results.

#### Methods

##### `get(content: str, url: str = None) -> Optional[Dict]`

Retrieves cached analysis result.

##### `set(content: str, result: Dict, url: str = None)`

Stores analysis result with TTL-based expiration.

**Features:**
- Content hashing for duplicate detection
- TTL-based cache expiration
- URL-based cache keys for context

---

## Error Handling

### Exception Types

#### `ValueError`
Raised for:
- Invalid or empty content
- URL validation failures
- JSON parsing errors
- API authentication failures

### Error Context

Enhanced error messages provide:
- Specific failure reasons
- Suggested remediation steps
- Context about content type or site
- Alternative input methods

### Example Error Handling

```python
try:
    result = analyzer.analyze_article(content, url)
except ValueError as e:
    if "content too short" in str(e):
        # Handle short content
        pass
    elif "json" in str(e).lower():
        # Handle parsing errors
        pass
    elif "extraction failed" in str(e):
        # Handle scraping failures
        pass
```

---

## Performance Considerations

### Caching Strategy
- Content-based hashing prevents duplicate analyses
- TTL expiration ensures fresh results
- URL context for cache invalidation

### API Optimization
- Gemini 2.5 Flash Lite for optimal speed/quality balance
- Content preprocessing prioritizes VGC-relevant text
- Fallback strategies reduce API calls

### Memory Management
- Content truncation at 8000 characters
- Smart content filtering removes UI elements
- Efficient Pokemon name translation dictionaries

---

## Rate Limits

### Google Gemini API
- Model: `gemini-2.5-flash-lite`
- Higher quota than Pro models
- Configurable generation parameters

### Recommended Usage
- Implement request throttling for batch processing
- Use caching to minimize redundant API calls
- Monitor API quotas in production

---

## Testing

### Unit Tests
Located in `tests/` directory:
- `test_integration.py`: End-to-end workflow tests
- `test_comprehensive_ev.py`: EV extraction validation

### Real-World Validation
Comprehensive testing against 8 diverse Japanese VGC articles:
- note.com dynamic content
- Tournament reports
- Team construction articles
- Player spotlights