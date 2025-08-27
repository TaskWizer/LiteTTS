# diphthong_fix_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Diphthong pronunciation fix processor for TTS
Fixes "joy" → "ju-ie" and similar diphthong pronunciation issues


## Class: DiphthongFixProcessor

Processor to fix diphthong pronunciation issues in TTS

### __init__()

### _load_diphthong_fixes()

Load diphthong pronunciation fixes

### _load_phonetic_overrides()

Load phonetic spelling overrides for problematic words

### _load_context_patterns()

Load context-based pronunciation patterns

### fix_diphthong_pronunciation()

Fix diphthong pronunciation issues in text

### _apply_context_patterns()

Apply context-based pronunciation patterns

### _apply_word_replacements()

Apply direct word-to-phonetic replacements

### _handle_special_cases()

Handle special pronunciation cases

### analyze_diphthong_issues()

Analyze text for potential diphthong pronunciation issues

