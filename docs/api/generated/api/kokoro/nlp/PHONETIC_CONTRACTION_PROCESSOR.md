# phonetic_contraction_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Phonetic Contraction Processor
Handles contraction pronunciation issues with proper phonetic mapping
Fixes issues like wasn't→wAHz-uhnt, I'll→ill, you'll→yaw-wl, etc.


## Class: ContractionFix

Represents a contraction pronunciation fix

## Class: PhoneticContractionProcessor

Advanced contraction processor with phonetic awareness

### __init__()

### _load_contraction_fixes()

Load comprehensive contraction fixes with phonetic mappings

### _load_phonetic_mappings()

Load IPA to readable phonetic mappings

### _load_context_patterns()

Load context patterns for context-sensitive contractions

### _compile_patterns()

Compile regex patterns for efficiency

### process_contractions()

Process contractions with phonetic awareness

Args:
    text: Input text with contractions
    mode: "phonetic_expansion" (default), "simple_expansion", "phonetic_only"

### _phonetic_expansion()

Expand contractions with phonetic guidance

### _simple_expansion()

Simple contraction expansion without phonetic processing

### _phonetic_only()

Apply phonetic representations without expansion

### _resolve_context_sensitive()

Resolve context-sensitive contractions like 'd and 's

### analyze_contractions()

Analyze text for contraction processing opportunities

### get_phonetic_representation()

Get phonetic representation of a contraction

