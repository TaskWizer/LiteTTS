# phonetic_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Phonetic processing and spell function handling for TTS


## Class: PhoneticProcessor

Handles custom pronunciation markers and phonetic processing

### __init__()

### _load_phonetic_alphabet()

Load phonetic alphabet mappings

### _load_ipa_mappings()

Load IPA (International Phonetic Alphabet) to readable mappings - Enhanced with RIME AI inspired phonetic alphabet

### process_phonetics()

Process custom pronunciation markers in text

### _process_curly_braces()

Process phonetic markers in curly braces {pronunciation}

### _process_ipa_notation()

Process IPA notation markers

### _process_phonetic_alphabet()

Process NATO phonetic alphabet markers

### _process_rime_style_phonetics()

Process RIME AI-style phonetic notation with stress markers

### _convert_rime_to_readable()

Convert RIME AI-style phonetic notation to readable text

### _convert_phonetic_to_readable()

Convert custom phonetic notation to readable text

### _convert_ipa_to_readable()

Convert IPA notation to readable pronunciation

