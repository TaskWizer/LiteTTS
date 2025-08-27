# advanced_abbreviation_handler.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Advanced abbreviation handler for TTS
Fixes ASAP pronunciation and implements configurable abbreviation processing


## Class: AbbreviationMode

Abbreviation processing modes

## Class: AdvancedAbbreviationHandler

Advanced abbreviation processing for natural TTS pronunciation

### __init__()

### _load_spell_out_abbreviations()

Load abbreviations that should be spelled out

### _load_expansion_abbreviations()

Load abbreviations that should be expanded

### _load_context_abbreviations()

Load context-dependent abbreviations

### _load_natural_abbreviations()

Load abbreviations that are naturally pronounced as words

### process_abbreviations()

Process abbreviations based on the specified mode

### _process_spell_out_mode()

Process abbreviations by spelling them out

### _process_expansion_mode()

Process abbreviations by expanding them

### _process_natural_mode()

Process abbreviations using natural pronunciations

### _process_hybrid_mode()

Process abbreviations using a hybrid approach

### _get_context_pronunciation()

Get context-dependent pronunciation

### analyze_abbreviations()

Analyze abbreviations in text

### add_abbreviation()

Add a new abbreviation to the appropriate dictionary

### set_configuration()

Set configuration options

### _process_contextual_units()

Process single-letter units only in proper measurement contexts

### get_supported_modes()

Get list of supported abbreviation processing modes

