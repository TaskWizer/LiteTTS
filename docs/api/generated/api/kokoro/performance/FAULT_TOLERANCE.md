# fault_tolerance.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Fault tolerance and resilience features for Kokoro ONNX TTS API


## Class: CircuitBreaker

Circuit breaker pattern for fault tolerance

### __init__()

### __call__()

### _should_attempt_reset()

Check if enough time has passed to attempt reset

### _on_success()

Handle successful execution

### _on_failure()

Handle failed execution

## Class: RetryManager

Retry logic with exponential backoff

### retry_with_backoff()

Decorator for retry with exponential backoff

## Class: HealthChecker

Health checking system for components

### __init__()

### register_check()

Register a health check

### run_check()

Run a specific health check

### run_all_checks()

Run all health checks

### get_health_status()

Get overall health status

### enable_check()

Enable a health check

### disable_check()

Disable a health check

## Class: GracefulDegradation

Graceful degradation when components fail

### __init__()

### register_fallback()

Register a fallback function for a component

### mark_component_failed()

Mark a component as failed

### mark_component_healthy()

Mark a component as healthy

### is_component_healthy()

Check if a component is healthy

### get_fallback()

Get fallback function for a component

### execute_with_fallback()

Execute function with fallback if component is unhealthy

## Function: get_health_checker()

Get health checker instance

## Function: get_graceful_degradation()

Get graceful degradation instance

## Function: check_model_file_exists()

Health check for model file existence

## Function: check_voices_directory()

Health check for voices directory

## Function: check_disk_space()

Health check for available disk space

## Function: check_memory_usage()

Health check for memory usage

