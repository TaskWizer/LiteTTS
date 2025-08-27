# contraction_pronunciation_fix.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Contraction pronunciation fix processor for TTS
Fixes "I'm" → "im" instead of "I-m" and similar contraction issues


## Class: ContractionPronunciationFix

Processor to fix contraction pronunciation issues in TTS

### __init__()

### _load_contraction_fixes()

Load contraction pronunciation fixes

### _load_phonetic_contractions()

Load phonetic representations for contractions

### _load_problematic_patterns()

Load patterns for problematic contractions

### fix_contraction_pronunciation()

Fix contraction pronunciation issues

Args:
    text: Input text with contractions
    mode: "expand" (full expansion) or "phonetic" (phonetic spelling)

### _expand_problematic_contractions()

Expand contractions that cause pronunciation issues

### _apply_phonetic_contractions()

Apply phonetic spelling for contractions

### _hybrid_contraction_processing()

Hybrid approach: expand problematic, keep natural

### analyze_contraction_issues()

Analyze text for contraction pronunciation issues

### normalize_apostrophes()

Normalize apostrophes to prevent HTML entity pronunciation

