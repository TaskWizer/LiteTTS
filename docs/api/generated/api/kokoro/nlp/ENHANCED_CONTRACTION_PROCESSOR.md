# enhanced_contraction_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Enhanced contraction processor for natural TTS pronunciation
Addresses specific contraction pronunciation issues like I'll→ill, you'll→yaw-wl, I'd→I-D


## Class: EnhancedContractionProcessor

Advanced contraction processing for natural TTS pronunciation

### __init__()

### _load_natural_contractions()

Load contractions that should be kept in natural form

### _load_problematic_contractions()

Load contractions that cause TTS pronunciation issues

### _load_phonetic_contractions()

Load phonetic representations for natural-sounding contractions

### process_contractions()

Process contractions based on the specified mode

### _normalize_apostrophes()

Normalize different apostrophe types to prevent pronunciation issues

### _process_natural_mode()

Keep contractions in natural form

### _process_phonetic_mode()

Use phonetic representations for better pronunciation

### _process_expanded_mode()

Expand all contractions to full forms

### _process_hybrid_mode()

Hybrid approach: expand problematic contractions, keep natural ones

### get_contraction_info()

Analyze contractions in text and return information

### set_mode()

Set the contraction processing mode

### get_supported_modes()

Get list of supported contraction processing modes

