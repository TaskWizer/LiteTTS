# manager.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Main voice manager that orchestrates all voice operations


## Class: VoiceManager

Main voice manager that handles all voice operations

### __init__()

### get_voice_embedding()

Get voice embedding (from cache or load)

### download_voice()

Download a specific voice

### download_all_voices()

Download all available voices

### download_default_voices()

Download default voices

### validate_voice()

Validate a specific voice

### validate_all_voices()

Validate all downloaded voices

### get_available_voices()

Get list of available voices (downloaded and ready)

### is_voice_ready()

Check if voice is downloaded and valid

### get_voice_metadata()

Get metadata for a voice

### get_all_voice_metadata()

Get metadata for all voices

### filter_voices()

Filter voices by criteria

### get_recommended_voices()

Get recommended voices

### preload_voice()

Preload a voice into cache

### preload_voices()

Preload multiple voices into cache

### is_voice_cached()

Check if voice is currently cached

### get_cached_voices()

Get list of currently cached voices

### get_system_status()

Get comprehensive system status

### setup_system()

Set up the voice system (download, validate, cache)

### cleanup_system()

Clean up voice system resources

### repair_voice()

Attempt to repair a corrupted voice

### get_voice_info()

Get comprehensive information about a voice

### optimize_system()

Optimize the voice system performance

