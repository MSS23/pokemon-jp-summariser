# 🧪 Experimental Prompting Features

This document describes the experimental prompting features implemented in the Pokemon VGC Team Analysis application.

## Overview

The experimental prompting system implements advanced AI prompting techniques to improve parsing accuracy and provide better insights into the analysis process. These features are designed to work alongside the existing proven parsing system without affecting its functionality.

## Features Implemented

### 1. 🔄 Error Recovery Prompts
When parsing fails, specialized prompts are used to extract specific missing information.

**How it works:**
- Detects missing fields in the initial parsing
- Uses targeted prompts for each missing field type
- Applies corrections based on common patterns
- Provides reasoning for each correction made

**Example:**
```
Missing Fields: ['ev_spread', 'ability']
→ Specialized EV extraction prompt
→ Specialized ability identification prompt
→ Apply corrections (e.g., "Iron Crown" → "Iron Jugulis")
```

### 2. 📝 Multi-Step Prompting
Breaks down analysis into smaller, more focused prompts for better accuracy.

**Steps:**
1. **Initial Reasoning**: Analyze content type and structure
2. **Section Extraction**: Extract individual Pokemon sections
3. **Individual Parsing**: Parse each Pokemon with detailed reasoning
4. **Error Recovery**: Fill in missing information
5. **Confidence Assessment**: Calculate overall confidence scores

### 3. 🤔 Chain-of-Thought Prompts
Asks the model to explain its reasoning before providing the final analysis.

**Features:**
- Step-by-step reasoning for each field
- Confidence scores (1-5 scale) for each extraction
- Detailed explanations of parsing decisions
- Transparency in the analysis process

**Example Output:**
```
REASONING:
1. This appears to be a VGC team analysis article
2. I can see 3 Pokemon mentioned with clear formatting
3. Each Pokemon has ability, item, nature, moves, and EV information

CONFIDENCE ASSESSMENT:
Name: 5 - Clear Pokemon name mentioned
Ability: 4 - Ability name is standard format
Item: 3 - Item name could be abbreviated
...
```

### 4. 💬 User Feedback System
Allows users to rate analysis accuracy and provide corrections.

**Features:**
- Rate confidence in corrections (1-5 scale)
- Submit feedback for any parsed field
- Track most common corrections
- Export feedback data for analysis
- Statistics on parsing accuracy

## How to Use

### Option 1: Experimental Page
1. Navigate to "🧪 Experimental Prompts" in the navigation
2. **Option A**: Enter an article URL (same as main app)
3. **Option B**: Paste your article text directly
4. Click "🧪 Run Experimental Analysis"
5. Review results in the detailed tabs
6. Provide feedback on any corrections needed

### Option 2: Test Script
Run the standalone test script:
```bash
cd streamlit-app
python test_experimental.py
```

The test script will:
1. Test with sample article text
2. Optionally prompt for a URL to test URL-based analysis
3. Test the user feedback system
4. Export feedback data

### Option 3: Main Application Toggle
1. Enable "🧪 Experimental Mode" checkbox in the main interface
2. Run analysis as normal
3. Experimental features will be used in the background

## Files Structure

```
streamlit-app/
├── utils/
│   └── experimental_prompts.py      # Core experimental system
├── pages/
│   └── Experimental_Prompts.py      # Streamlit page for testing
├── test_experimental.py             # Standalone test script
└── EXPERIMENTAL_FEATURES.md         # This documentation
```

## Key Classes

### `ExperimentalPromptManager`
Main class that handles all experimental prompting features.

**Methods:**
- `analyze_team_with_chain_of_thought()`: Main analysis method for text
- `analyze_team_with_chain_of_thought_from_url()`: URL-based analysis using same langchain backbone
- `submit_user_feedback()`: Submit user corrections
- `get_feedback_statistics()`: Get feedback analytics
- `export_feedback_data()`: Export feedback to JSON

### `ParsingResult`
Data class containing analysis results with metadata.

**Fields:**
- `success`: Whether parsing was successful
- `data`: Parsed Pokemon data
- `confidence`: Overall confidence score (0.0-1.0)
- `reasoning`: Model's reasoning process
- `missing_fields`: List of fields that couldn't be parsed
- `corrections_applied`: List of corrections made
- `timestamp`: When analysis was performed

### `UserFeedback`
Data class for storing user feedback.

**Fields:**
- `team_id`: Identifier for the team
- `field_name`: Which field was corrected
- `original_value`: Original parsed value
- `corrected_value`: User's correction
- `confidence_rating`: User's confidence (1-5)
- `feedback_notes`: Additional notes
- `timestamp`: When feedback was submitted

## Benefits

### 1. Improved Accuracy
- Multi-step analysis catches more information
- Error recovery fills in missing data
- Chain-of-thought reduces parsing errors

### 2. Transparency
- See exactly how the model reasons
- Understand confidence levels
- Track what corrections were made

### 3. Continuous Improvement
- User feedback improves future parsing
- Track common error patterns
- Export data for analysis

### 4. Safety
- Experimental features don't affect main system
- Can be enabled/disabled easily
- Separate testing environment

## Limitations

1. **Performance**: Multi-step prompting takes longer than single-step
2. **Complexity**: More complex system with more moving parts
3. **API Costs**: Multiple API calls per analysis
4. **Experimental**: May not always improve results

## Future Enhancements

1. **Learning System**: Use feedback to improve prompts automatically
2. **Confidence Thresholds**: Adjust parsing based on confidence scores
3. **Batch Processing**: Handle multiple teams efficiently
4. **Custom Prompts**: Allow users to customize prompting strategies

## Testing

To test the experimental features:

1. **Basic Test**: Use the test script with sample data
2. **Real Data Test**: Use the experimental page with real articles
3. **Feedback Test**: Submit corrections and review statistics
4. **Comparison Test**: Compare results with main system

## Support

If you encounter issues with the experimental features:

1. Check the console output for detailed error messages
2. Verify that all dependencies are installed
3. Ensure the Gemini API is properly configured
4. Try the standalone test script for debugging

The experimental features are designed to be safe and non-intrusive, so you can always fall back to the main system if needed.
