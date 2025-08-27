# unified_pronunciation_fix.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Unified pronunciation fix processor for TTS
Integrates all pronunciation fixes: comma handling, diphthongs, contractions, and interjections


## Class: PronunciationFixResult

Result of pronunciation fix processing

## Class: UnifiedPronunciationFix

Unified processor for all pronunciation fixes

### __init__()

### process_pronunciation_fixes()

Apply all pronunciation fixes to text

Args:
    text: Input text to process
    enable_comma: Override comma fix setting
    enable_diphthong: Override diphthong fix setting
    enable_contraction: Override contraction fix setting
    enable_interjection: Override interjection fix setting
    contraction_mode: Override contraction processing mode

### analyze_all_issues()

Analyze text for all types of pronunciation issues

### configure_fixes()

Configure which fixes to apply

### get_fix_statistics()

Get statistics about potential fixes for text

