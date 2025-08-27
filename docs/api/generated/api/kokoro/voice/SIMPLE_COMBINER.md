# simple_combiner.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Simplified voice combiner for Kokoro ONNX TTS API
Creates a combined voices file from individual .bin files for kokoro_onnx compatibility


## Class: SimplifiedVoiceCombiner

Simplified voice combiner that creates combined voices file from individual .bin files

### __init__()

### _load_individual_voice()

Load an individual voice file

### _get_available_voices()

Get list of available voice files

### create_combined_file()

Create combined voices file from individual .bin files

### ensure_combined_file()

Ensure combined voices file exists and is current

### get_voice_list()

Get list of voices in the combined file

### get_voice_count()

Get number of voices in the combined file

