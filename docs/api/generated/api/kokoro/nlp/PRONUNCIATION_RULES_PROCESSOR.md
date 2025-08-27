# pronunciation_rules_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Pronunciation Rules Processor for TTS
Handles natural contraction pronunciation without expansion


## Class: PronunciationRulesProcessor

Processor for applying pronunciation rules to maintain natural speech

### __init__()

### _load_config()

Load configuration from config.json

### _is_enabled()

Check if pronunciation rules are enabled

### _load_contraction_rules()

Load contraction pronunciation rules from config

### process_pronunciation_rules()

Apply pronunciation rules to text without expanding contractions

### _apply_contraction_rules()

Apply pronunciation rules for contractions

### analyze_contractions()

Analyze contractions in text and suggest pronunciation fixes

### add_pronunciation_rule()

Add a new pronunciation rule

### remove_pronunciation_rule()

Remove a pronunciation rule

### get_pronunciation_rules()

Get all current pronunciation rules

### test_pronunciation_rule()

Test a pronunciation rule on sample text

### validate_config()

Validate the current configuration

## Function: create_pronunciation_rules_processor()

Factory function to create a pronunciation rules processor

