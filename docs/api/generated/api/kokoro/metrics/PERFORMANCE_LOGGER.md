# performance_logger.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Performance metrics logging system for Kokoro TTS
Tracks token usage, latency, time to first token, and other performance metrics


## Class: PerformanceMetrics

Performance metrics for a single TTS request

## Class: PerformanceLogger

Centralized performance metrics logging and analysis

### __init__()

### start_request()

Start tracking a new request

### log_stage()

Log completion of a processing stage

### log_token_metrics()

Log token-related metrics

### log_audio_metrics()

Log audio output metrics

### finish_request()

Complete tracking and generate final metrics

### _get_gpu_memory_usage()

Get GPU memory usage if available

### _update_aggregates()

Update hourly and daily aggregates

### _write_to_file()

Write metrics to log file

### get_recent_stats()

Get statistics for recent requests

### export_metrics()

Export all metrics to file

