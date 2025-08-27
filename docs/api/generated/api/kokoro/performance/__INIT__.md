# __init__.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Kokoro TTS Performance Package

This package provides performance enhancement features for the Kokoro ONNX TTS API,
including hot reload capabilities, fault tolerance mechanisms, and performance
monitoring tools.

Features:
- Hot reload for models and voices without server restart
- Circuit breaker pattern for fault tolerance
- Retry logic with exponential backoff
- Health checking system for components
- Performance monitoring and metrics collection
- Graceful degradation mechanisms

Available modules:
- hot_reload: HotReloadManager and PerformanceMonitor classes
- fault_tolerance: CircuitBreaker, RetryManager, HealthChecker, and GracefulDegradation classes


