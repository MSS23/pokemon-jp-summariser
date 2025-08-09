# 🔍 Feedback System Guide

## Overview

The experimental feedback system allows users to provide corrections to parsed Pokemon data while implementing comprehensive validation and anti-spam measures to ensure data quality.

## 🛡️ Anti-Spam & Validation Features

### 1. **Rate Limiting**
- **Hourly Limit**: Maximum 10 feedback submissions per hour per user
- **Session Limit**: Maximum 50 feedback submissions per session
- **Automatic Cleanup**: Old entries are automatically removed after 1 hour

### 2. **Content Validation**
- **Length Limits**: 
  - Original/Corrected values: Max 500 characters
  - Feedback notes: Max 1000 characters
- **Required Fields**: All fields must be provided and non-empty
- **Identical Values**: Original and corrected values cannot be identical

### 3. **Spam Detection**
- **Spam Keywords**: Detects common spam terms like "test", "fake", "spam", etc.
- **Suspicious Patterns**: 
  - Excessive consecutive caps (10+)
  - Excessive numbers (10+)
  - Excessive special characters (5+)
  - Repeated characters (6+)
- **Content Quality**: Checks for too few unique words or excessive special characters

### 4. **Pokemon-Specific Validation**
- **Names**: Must match Pokemon name patterns (letters, spaces, hyphens, apostrophes)
- **Moves**: Must match move name patterns
- **EV Spreads**: Must be numbers 0-252, 1-6 values
- **Natures**: Must be valid Pokemon natures from the official list

## 📊 Quality Monitoring

### Quality Score Calculation
The system calculates an overall quality score (0-100) based on:
- **Spam Penalty**: -50 points for each spam submission
- **Low Confidence Penalty**: -20 points for submissions with confidence ≤2
- **Base Score**: Starts at 100 points

### Quality Report Features
- **Overall Quality Score**: Visual indicator of feedback quality
- **Spam Indicators**: List of potential spam submissions with reasons
- **Rate Limit Violations**: Users who exceeded submission limits
- **Recommendations**: Suggestions for improving feedback quality

## 🔧 How to Monitor Feedback

### 1. **Check Quality Reports**
Navigate to the Experimental Prompts page → Feedback tab → Quality Report section

### 2. **Review Spam Indicators**
- Look for submissions flagged as spam
- Check the reasons provided
- Review user patterns

### 3. **Monitor Rate Limiting**
- Check for users exceeding hourly/session limits
- Review submission patterns over time

### 4. **Export Data for Analysis**
- Export feedback data as JSON
- Export quality reports for detailed analysis
- Use external tools for deeper analysis

## 🚨 Red Flags to Watch For

### High-Risk Patterns
1. **Rapid Submissions**: Multiple submissions in short time periods
2. **Identical Corrections**: Same correction submitted repeatedly
3. **Invalid Pokemon Data**: Corrections that don't match Pokemon standards
4. **Suspicious Content**: Contains spam keywords or patterns
5. **Low Confidence**: Users consistently rating confidence as 1-2

### Quality Indicators
- **Quality Score < 60**: Needs immediate attention
- **Spam Rate > 10%**: Consider stricter validation
- **Rate Limit Violations > 5**: May indicate automated submissions

## 🛠️ Configuration Options

### Rate Limiting Settings
```python
self.rate_limit_window = 3600  # 1 hour window
self.max_feedback_per_hour = 10  # Max per hour
self.max_feedback_per_session = 50  # Max per session
```

### Spam Detection Settings
```python
self.spam_keywords = ['spam', 'test', 'fake', ...]  # Customizable list
self.suspicious_patterns = [r'[A-Z]{10,}', ...]  # Regex patterns
```

## 📈 Best Practices

### For Users
1. **Provide Meaningful Corrections**: Only correct actual errors
2. **Use Appropriate Confidence**: Rate confidence accurately
3. **Add Helpful Notes**: Explain why the correction is needed
4. **Respect Limits**: Don't spam the system

### For Administrators
1. **Regular Monitoring**: Check quality reports weekly
2. **Review Spam Indicators**: Investigate flagged submissions
3. **Adjust Settings**: Modify limits based on usage patterns
4. **Export Data**: Keep backups of feedback data
5. **User Education**: Guide users on proper feedback submission

## 🔄 Integration with Model Improvement

The feedback system is designed to eventually integrate with model improvement:

1. **Data Collection**: Gather high-quality corrections
2. **Pattern Analysis**: Identify common parsing errors
3. **Prompt Refinement**: Use feedback to improve prompts
4. **Model Training**: Use validated corrections for fine-tuning

## 📞 Support

If you encounter issues with the feedback system:
1. Check the quality report for error indicators
2. Review validation error messages
3. Contact administrators for rate limit adjustments
4. Report suspicious activity patterns

---

**Remember**: The feedback system is designed to improve the overall parsing accuracy while maintaining data quality. Regular monitoring and user education are key to its success.
