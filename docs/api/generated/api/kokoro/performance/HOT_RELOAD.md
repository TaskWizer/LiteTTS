# hot_reload.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Hot reload system for models and voices without server restart


## Class: ModelReloadHandler

File system event handler for model hot reloading

### __init__()

### on_modified()

### _delayed_reload()

Perform delayed reload to avoid rapid reloads

## Class: HotReloadManager

Manages hot reloading of models and voices

### __init__()

### register_model_reload()

Register a model for hot reloading

### register_voice_reload()

Register voices directory for hot reloading

### manual_reload()

Manually trigger a reload for a specific file

### reload_all()

Reload all registered files

### stop()

Stop all file watchers

### get_status()

Get hot reload status

## Class: PerformanceMonitor

Monitor performance metrics for optimization

### __init__()

### record_request()

Record a request with its response time

### record_cache_hit()

Record a cache hit

### record_cache_miss()

Record a cache miss

### record_model_load()

Record a model load

### record_voice_load()

Record a voice load

### get_metrics()

Get current performance metrics

### reset_metrics()

Reset all metrics

## Function: get_hot_reload_manager()

Get or create hot reload manager

## Function: get_performance_monitor()

Get performance monitor

