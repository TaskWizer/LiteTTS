# monitor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Performance monitoring system for TTS optimization
Tracks RTF, latency, cache performance, and system metrics


## Class: PerformanceMetric

Individual performance measurement

## Class: TTSPerformanceData

TTS-specific performance data

## Class: SystemMetrics

System resource metrics

## Class: PerformanceMonitor

Comprehensive performance monitoring for TTS API
Tracks RTF, latency, cache performance, and system resources

### __init__()

### start_monitoring()

Start system monitoring thread

### stop_monitoring()

Stop system monitoring

### record_tts_performance()

Record TTS performance metrics

### _update_rtf_stats()

Update RTF statistics

### _update_latency_stats()

Update latency statistics

### _update_voice_stats()

Update voice-specific statistics

### _update_length_analysis()

Update text length analysis

### _system_monitor_worker()

Background worker for system monitoring

### get_performance_summary()

Get comprehensive performance summary

### get_rtf_trend()

Get RTF trend over specified time period

### export_metrics()

Export performance metrics to JSON file

