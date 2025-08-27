# test_performance.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Performance-specific tests for Kokoro ONNX TTS API
Tests RTF, latency, caching, and optimization features


## Class: TestPerformanceMonitoring

Test performance monitoring system

### monitor()

Create performance monitor instance

### test_monitor_initialization()

Test monitor initialization

### test_record_tts_performance()

Test recording TTS performance data

### test_record_cache_hit()

Test recording cache hit performance

### test_performance_summary()

Test performance summary generation

### test_voice_specific_stats()

Test voice-specific performance tracking

## Class: TestCachePreloader

Test intelligent cache preloader system

### config()

Create preloader configuration

### mock_tts_app()

Create mock TTS app for testing

### test_preloader_initialization()

Test preloader initialization

### test_startup_warming_scheduling()

Test startup warming task scheduling

### test_cache_key_generation()

Test cache key generation

### test_request_tracking()

Test request tracking and statistics

### test_stats_generation()

Test statistics generation

## Class: TestPerformanceRegression

Test for performance regressions

### test_rtf_performance_threshold()

Test that RTF stays within acceptable bounds

### test_cache_hit_latency_threshold()

Test that cache hits stay within latency bounds

### test_memory_usage_threshold()

Test that memory usage stays within bounds

### test_startup_time_threshold()

Test that startup time is reasonable

## Class: TestConcurrencyAndStress

Test concurrent access and stress scenarios

### test_concurrent_cache_access()

Test concurrent access to cache system

### test_high_frequency_requests()

Test handling of high-frequency requests

## Class: MockTTSApp

### __init__()

## Class: MockModel

### create()

