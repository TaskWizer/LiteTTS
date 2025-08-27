# dynamic_manager.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Dynamic voice manager with HuggingFace integration and smart caching


## Class: VoiceEmbedding

Voice embedding data structure

## Class: DynamicVoiceManager

Dynamic voice manager with HuggingFace integration and smart caching

### __init__()

### _initialize_voice_system()

Initialize the voice system with discovery and mapping generation

### _generate_voice_mappings()

Generate short name mappings for all available voices

### _load_voice_mappings()

Load voice mappings from cache

### _save_voice_mappings()

Save voice mappings to cache

### get_available_voices()

Get list of all available voice names (both full and short names)

### resolve_voice_name()

Resolve a voice name (short or full) to the full voice name

### is_voice_available()

Check if a voice is available (either downloaded or can be downloaded)

### ensure_voice_downloaded()

Ensure a voice is downloaded, downloading if necessary

### get_voice_embedding()

Get voice embedding, downloading if necessary

### _load_voice_data()

Load voice data from file

### download_all_voices()

Download all available voices from HuggingFace

### get_download_status()

Get download status for all voices

### refresh_discovery()

Refresh voice discovery from HuggingFace

### get_voice_mappings()

Get current voice mappings (short -> full name)

