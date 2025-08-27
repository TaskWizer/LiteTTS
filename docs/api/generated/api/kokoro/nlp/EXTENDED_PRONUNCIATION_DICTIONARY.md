# extended_pronunciation_dictionary.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Extended pronunciation dictionary for TTS accuracy
Includes word-specific pronunciation fixes and context-aware pronunciations


## Class: ExtendedPronunciationDictionary

Extended pronunciation dictionary with context-aware pronunciations

### __init__()

### _load_word_pronunciations()

Load word-specific pronunciation fixes

### _load_context_pronunciations()

Load context-dependent pronunciations for homographs

### _load_homograph_rules()

Load rules for detecting homograph context

### _load_phonetic_overrides()

Load phonetic spelling overrides for difficult words

### get_pronunciation()

Get the correct pronunciation for a word, considering context

### _get_context_pronunciation()

Get context-dependent pronunciation using rules

### process_text_pronunciations()

Process entire text for pronunciation fixes

### add_pronunciation()

Add a new pronunciation to the dictionary

### analyze_pronunciations()

Analyze text for words with known pronunciation issues

### export_pronunciations()

Export pronunciations to JSON file

### import_pronunciations()

Import pronunciations from JSON file

### set_configuration()

Set configuration options

