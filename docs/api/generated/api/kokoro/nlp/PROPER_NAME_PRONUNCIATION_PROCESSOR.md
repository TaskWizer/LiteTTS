# proper_name_pronunciation_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Proper Name and Word Pronunciation Processor for TTS
Fixes specific word mispronunciations like Elon→alon, Joy→joie, acquisition→ek-wah-zi·shn


## Class: ProperNamePronunciationProcessor

Processor for fixing specific proper name and word pronunciation issues

### __init__()

### _load_config()

Load configuration from config.json

### _is_enabled()

Check if proper name pronunciation fixes are enabled

### _load_proper_name_fixes()

Load proper name pronunciation fixes

### _load_word_pronunciation_fixes()

Load general word pronunciation fixes

### _load_context_sensitive_fixes()

Load context-sensitive pronunciation fixes

### process_proper_name_pronunciation()

Apply proper name and word pronunciation fixes

### _apply_proper_name_fixes()

Apply proper name pronunciation fixes

### _apply_word_pronunciation_fixes()

Apply general word pronunciation fixes

### _apply_context_sensitive_fixes()

Apply context-sensitive pronunciation fixes

### analyze_pronunciation_issues()

Analyze potential pronunciation issues in text

### add_pronunciation_fix()

Add a new pronunciation fix

### get_all_fixes()

Get all pronunciation fixes

