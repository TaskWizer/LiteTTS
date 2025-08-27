# cache.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice caching system with preloading capabilities


## Class: CacheEntry

Cache entry for voice embeddings

## Class: VoiceCache

Manages voice embedding caching with preloading

### __init__()

### _initialize_cache()

Initialize cache with preloaded voices

### get_voice_embedding()

Get voice embedding from cache or load if not cached

### _load_voice_to_cache()

Load voice embedding to cache

### _manage_cache_size()

Manage cache size by evicting least recently used entries

### _calculate_file_hash()

Calculate file hash for integrity checking

### preload_voice()

Preload a specific voice into cache

### preload_voices_batch()

Preload multiple voices

### is_voice_cached()

Check if voice is currently cached

### get_cached_voices()

Get list of currently cached voices

### evict_voice()

Manually evict a voice from cache

### clear_cache()

Clear cache, optionally keeping preloaded voices

### get_cache_stats()

Get cache statistics

### optimize_cache()

Optimize cache by reloading frequently used voices

### validate_cache_integrity()

Validate integrity of cached voice embeddings

