# Enhanced Text Processing Integration Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

## Overview

The Kokoro ONNX TTS API includes comprehensive enhanced text processing features that are fully implemented but not yet integrated into the main TTS pipeline. This guide shows how to enable these features.

## Current State

### ✅ What's Implemented
- **Advanced Currency Processing**: Converts $1,234.56 to natural language
- **Enhanced DateTime Processing**: Converts 2024-12-25 to "December twenty-fifth, twenty twenty-four"
- **Smart Contraction Handling**: Intelligent contraction processing with multiple modes
- **Abbreviation Processing**: Context-aware acronym and abbreviation handling
- **Unified Processing Pipeline**: Integrated system with multiple quality modes

### 🔧 What Needs Integration
The enhanced processors exist in `kokoro/nlp/` but are not connected to the main TTS pipeline in `app.py`.

## Quick Integration Example

### Option 1: Simple Integration (Recommended for immediate use)

Add enhanced text processing to the main TTS endpoint in `app.py`:

```python
# Add this import at the top of app.py
from kokoro.nlp.unified_text_processor import UnifiedTextProcessor, ProcessingOptions, ProcessingMode

# Add this to the TTSAPIServer.__init__ method
self.enhanced_text_processor = UnifiedTextProcessor()

# Replace the basic preprocessing in _generate_speech_internal with:
def _enhanced_preprocess_text(self, text: str) -> str:
    """Enhanced text preprocessing with all advanced features"""
    try:
        options = ProcessingOptions(
            mode=ProcessingMode.ENHANCED,
            use_advanced_currency=True,
            use_enhanced_datetime=True,
            use_pronunciation_rules=True,
            use_advanced_symbols=True
        )
        
        result = self.enhanced_text_processor.process_text(text, options)
        self.logger.debug(f"Enhanced processing applied: {result.changes_made}")
        return result.processed_text
        
    except Exception as e:
        self.logger.warning(f"Enhanced processing failed, falling back to basic: {e}")
        # Fallback to existing preprocessing
        preprocessing_result = phonemizer_preprocessor.preprocess_text(
            text, aggressive=False, preserve_word_count=True
        )
        return preprocessing_result.processed_text

# Then in _generate_speech_internal, replace:
preprocessing_result = phonemizer_preprocessor.preprocess_text(...)
processed_text = preprocessing_result.processed_text

# With:
processed_text = self._enhanced_preprocess_text(request.input)
```

### Option 2: Configuration-Based Integration

Add enhanced processing options to `config.json`:

```json
{
  "text_processing": {
    "mode": "enhanced",
    "enable_currency_processing": true,
    "enable_datetime_processing": true,
    "enable_contraction_processing": true,
    "enable_abbreviation_processing": true,
    "contraction_mode": "hybrid"
  }
}
```

## Testing the Integration

### Test Cases

1. **Currency Processing**:
   - Input: "The price is $1,234.56"
   - Expected: "The price is one thousand two hundred thirty four dollars and fifty six cents"

2. **DateTime Processing**:
   - Input: "Meeting on 2024-12-25 at 14:30"
   - Expected: "Meeting on December twenty-fifth, twenty twenty-four at half past two PM"

3. **Contraction Processing**:
   - Input: "I'm going and I'll be back"
   - Expected: "I'm going and I will be back" (hybrid mode - keeps natural, expands problematic)

4. **Abbreviation Processing**:
   - Input: "The CEO of NASA announced"
   - Expected: "The C E O of NASA announced"

### Validation Script

```python
#!/usr/bin/env python3
"""Test enhanced text processing integration"""

import requests
import json

def test_enhanced_processing():
    """Test the enhanced text processing via TTS API"""
    
    test_cases = [
        {
            "name": "Currency Processing",
            "input": "The price is $1,234.56 and approximately ~$500",
            "voice": "af_heart"
        },
        {
            "name": "DateTime Processing", 
            "input": "The meeting is on 2024-12-25 at 14:30",
            "voice": "af_heart"
        },
        {
            "name": "Mixed Processing",
            "input": "I'm buying $1,000 worth of stocks on 2024-12-25. The CEO said it's good!",
            "voice": "af_heart"
        }
    ]
    
    for test in test_cases:
        print(f"Testing: {test['name']}")
        print(f"Input: {test['input']}")
        
        response = requests.post("http://localhost:8354/v1/audio/speech", 
                               json={
                                   "input": test["input"],
                                   "voice": test["voice"],
                                   "response_format": "mp3"
                               })
        
        if response.status_code == 200:
            print("✅ TTS generation successful")
            # Save audio file for manual verification
            with open(f"test_{test['name'].lower().replace(' ', '_')}.mp3", "wb") as f:
                f.write(response.content)
        else:
            print(f"❌ TTS generation failed: {response.status_code}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_enhanced_processing()
```

## Performance Considerations

### Processing Modes

The unified text processor supports multiple modes:

- **BASIC**: Minimal processing, fastest
- **STANDARD**: Standard phonemizer preprocessing
- **ENHANCED**: All advanced features enabled (recommended)
- **PREMIUM**: Maximum quality with all features

### Caching

Enhanced text processing results can be cached:

```python
# Add to configuration
"text_processing": {
    "enable_caching": true,
    "cache_size": 1000,
    "cache_ttl_hours": 24
}
```

## Benefits of Integration

### Improved Speech Quality
- Natural pronunciation of currency amounts
- Proper date and time reading
- Better handling of contractions and abbreviations
- Context-aware text processing

### User Experience
- More natural-sounding speech
- Consistent pronunciation across different text types
- Reduced need for manual text formatting

### Production Readiness
- Comprehensive text handling for real-world content
- Configurable processing levels
- Fallback mechanisms for reliability

## Next Steps

1. **Implement Integration**: Choose Option 1 for quick implementation
2. **Test Thoroughly**: Use the validation script to verify functionality
3. **Configure Appropriately**: Adjust processing modes based on performance requirements
4. **Monitor Performance**: Track processing times and quality improvements
5. **Document Changes**: Update API documentation with new capabilities

## Conclusion

The enhanced text processing features are production-ready and will significantly improve the TTS quality. Integration is straightforward and can be implemented incrementally with proper fallback mechanisms.
