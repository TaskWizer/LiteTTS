# homograph_resolver.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Homograph resolution system for disambiguating word pronunciations


## Class: HomographResolver

Resolves homograph pronunciations based on context and explicit markers

### __init__()

### _load_homograph_dictionary()

Load homograph dictionary with different pronunciations

### _compile_context_patterns()

Compile context patterns for automatic disambiguation

### resolve_homographs()

Main function to resolve homographs in text

### _process_explicit_markers()

Process explicit homograph markers like 'produce_noun'

### _process_simple_replacements()

Process simple word replacements for consistent pronunciation

### _resolve_by_context()

Resolve homographs using context patterns

### _find_noun_pronunciation()

Find the noun pronunciation for a word

### _find_verb_pronunciation()

Find the verb pronunciation for a word

### add_homograph()

Add a new homograph to the dictionary

### get_homograph_info()

Get pronunciation options for a homograph

### list_homographs()

Get list of all known homographs

### _apply_pronunciation_dictionary()

Apply comprehensive pronunciation dictionary to improve accuracy

