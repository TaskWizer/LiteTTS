# test_comprehensive.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Comprehensive Test Suite for Kokoro ONNX TTS API
Tests all API endpoints, performance optimizations, and production features


## Class: TestKokoroTTSAPI

Comprehensive test suite for Kokoro ONNX TTS API

### app()

Create TTS app instance for testing

### client()

Create test client

### test_health_endpoint()

Test health endpoint functionality

### test_v1_health_endpoint()

Test v1 health endpoint compatibility

### test_voices_endpoint()

Test voices listing endpoint

### test_v1_voices_endpoint()

Test v1 voices endpoint compatibility

### test_models_endpoint()

Test models listing endpoint

### test_tts_generation_basic()

Test basic TTS generation

### test_tts_generation_different_voices()

Test TTS generation with different voices

### test_tts_generation_different_formats()

Test TTS generation with different audio formats

### test_tts_generation_speed_control()

Test TTS generation with different speeds

### test_cache_performance()

Test cache hit performance

### test_performance_stats_endpoint()

Test performance monitoring endpoint

### test_preloader_stats_endpoint()

Test preloader statistics endpoint

### test_rtf_trend_endpoint()

Test RTF trend monitoring endpoint

### test_performance_export_endpoint()

Test performance metrics export

### test_error_handling_invalid_voice()

Test error handling for invalid voice

### test_error_handling_empty_text()

Test error handling for empty text

### test_error_handling_invalid_format()

Test error handling for invalid audio format

### test_error_handling_invalid_speed()

Test error handling for invalid speed

### test_long_text_generation()

Test generation with long text

### test_concurrent_requests()

Test handling of concurrent requests

### test_cache_endpoints()

Test cache management endpoints

