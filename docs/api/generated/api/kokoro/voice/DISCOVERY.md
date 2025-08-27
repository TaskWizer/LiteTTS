# discovery.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice discovery and caching system for individual .bin files


## Class: VoiceInfo

Information about a discovered voice

## Class: VoiceDiscovery

Discovers and manages individual voice files with caching

### __init__()

### _load_cache()

Load voice cache from JSON file

### _save_cache()

Save voice cache to JSON file

### _calculate_checksum()

Calculate SHA256 checksum of a file

### discover_voices()

Discover voice files in the voices directory

### get_available_voices()

Get list of available voice names

### get_voice_info()

Get information for a specific voice

### is_voice_available()

Check if a voice is available locally

### load_voice_data()

Load a voice file into memory

### get_voice_stats()

Get statistics about available voices

### filter_voices()

Filter voices by criteria

### clear_loaded_voices()

Clear all loaded voice data from memory

### invalidate_cache()

Invalidate the cache and rediscover voices

