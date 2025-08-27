# health_monitor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Comprehensive health monitoring system for Kokoro ONNX TTS API


## Class: HealthStatus

Health status for a component

## Class: SystemHealth

Overall system health status

## Class: HealthMonitor

Comprehensive health monitoring system

### __init__()

### register_health_checker()

Register a health checker function

### start_monitoring()

Start background health monitoring

### stop_monitoring_service()

Stop background health monitoring

### _monitoring_loop()

Background monitoring loop

### perform_health_check()

Perform comprehensive health check

### _get_system_metrics()

Get current system metrics

### _determine_overall_status()

Determine overall system health status

### get_health_status()

Get current health status

### get_health_summary()

Get simplified health summary

### export_health_history()

Export health history to file

## Function: check_model_health()

Check if TTS model is loaded and functional

## Function: check_disk_space()

Check available disk space

