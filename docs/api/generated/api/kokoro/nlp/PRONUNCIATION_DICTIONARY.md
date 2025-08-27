# pronunciation_dictionary.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Comprehensive pronunciation dictionary for Kokoro TTS system
Contains common mispronounced words and their correct pronunciations


## Class: PronunciationDictionary

Comprehensive pronunciation dictionary for TTS accuracy

### __init__()

### _load_common_mispronunciations()

Load commonly mispronounced words with correct pronunciations

### _load_technical_terms()

Load technical terms and their pronunciations

### _load_proper_nouns()

Load proper nouns and their pronunciations

### _load_foreign_words()

Load foreign words commonly used in English

### get_pronunciation()

Get the correct pronunciation for a word if available

### has_pronunciation()

Check if a pronunciation is available for a word

### get_all_words()

Get all words that have pronunciation entries

### get_statistics()

Get statistics about the pronunciation dictionary

