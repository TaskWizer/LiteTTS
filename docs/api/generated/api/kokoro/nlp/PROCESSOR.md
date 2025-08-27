# processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Main NLP processor that combines all text processing components


## Class: ProsodyInfo

Prosody analysis information

## Class: NormalizationOptions

Text normalization configuration

## Class: NLPProcessor

Main NLP processor that orchestrates all text processing

### __init__()

Initialize NLP processor with all components

Args:
    enable_advanced_features: Enable emotion detection, context adaptation, and naturalness enhancement

### process_text()

Process text through the complete NLP pipeline

### normalize_text()

Normalize input text

### resolve_homographs()

Resolve homograph pronunciations

### process_phonetics()

Process phonetic markers

### analyze_prosody()

Analyze text for prosody information

### spell_word()

Spell out a word letter by letter

### add_homograph()

Add a custom homograph

### process_text_enhanced()

Enhanced text processing with human-likeness features

Args:
    text: Input text to process
    context_metadata: Optional context information (audience, register, etc.)
    options: Text normalization options

Returns:
    Dictionary containing processed text and enhancement data

### detect_emotion()

Detect emotional context in text

Args:
    text: Text to analyze
    conversation_history: Optional conversation history for context

Returns:
    Emotion profile or None if advanced features disabled

### adapt_for_context()

Analyze and adapt for speech context

Args:
    text: Text to analyze
    metadata: Optional context metadata

Returns:
    Speech context or None if advanced features disabled

### enhance_naturalness()

Apply naturalness enhancements to text

Args:
    text: Text to enhance
    context: Optional context information

Returns:
    Naturalness profile or None if advanced features disabled

### get_processing_stats()

Get processing statistics

