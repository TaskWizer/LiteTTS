# prosody_analyzer.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Prosody analysis system for natural speech patterns


## Class: ProsodyMarker

Represents a prosody marker in text

## Class: ProsodyAnalyzer

Analyzes text for prosody control based on punctuation and conversational markers

### __init__()

### _compile_punctuation_patterns()

Compile punctuation patterns with pause durations and intonation markers

### _compile_conversational_patterns()

Compile conversational marker patterns

### analyze_prosody()

Analyze text and return prosody markers

### _analyze_punctuation()

Analyze punctuation for prosody markers with enhanced intonation handling

### _analyze_conversational_markers()

Analyze conversational markers

### _get_marker_duration()

Get duration for different marker types

### process_conversational_features()

Process and enhance conversational features in text

### _process_false_starts()

Process false starts for natural speech

### _process_filler_words()

Add natural pauses around filler words

### _process_action_tokens()

Process action tokens like *breathes*, *laughs*

### get_prosody_info()

Get detailed prosody information

### enhance_intonation_markers()

Add intonation markers to text for better TTS processing

### process_conversational_intonation()

Process text to enhance conversational intonation patterns

