# voice_modulation_system.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice modulation system for TTS
Implements whisper/quiet mode for parenthetical text and other voice effects


## Class: VoiceModulation

Voice modulation parameters

## Class: ModulationSegment

Text segment with voice modulation

## Class: VoiceModulationSystem

Advanced voice modulation system for natural TTS expression

### __init__()

### _load_modulation_patterns()

Load text patterns that trigger voice modulation

### _load_voice_profiles()

Load predefined voice profiles

### _load_ssml_markers()

Load SSML-like markers for voice modulation

### process_voice_modulation()

Process text for voice modulation and return processed text with modulation segments

### _convert_ssml_markers()

Convert SSML-like markers to internal format

### _find_modulation_segments()

Find all text segments that need voice modulation

### _remove_modulation_markers()

Remove modulation markers from text, leaving only the content

### generate_ssml_with_modulation()

Generate SSML with voice modulation markers

### _create_ssml_segment()

Create SSML for a modulated segment

### analyze_modulation_opportunities()

Analyze text for potential voice modulation opportunities

### create_voice_profile()

Create a custom voice profile

### set_configuration()

Set configuration options

### get_voice_profiles()

Get all available voice profiles

