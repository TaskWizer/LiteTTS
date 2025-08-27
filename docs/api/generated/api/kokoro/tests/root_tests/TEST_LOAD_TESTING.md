# test_load_testing.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Load Testing for Kokoro ONNX TTS API
Tests system behavior under various load conditions and stress scenarios


## Class: TestBasicLoadHandling

Test basic load handling capabilities

### setup_method()

### _make_request()

Helper method for load testing requests

### test_light_load_5_concurrent()

Test light load with 5 concurrent requests

### test_medium_load_10_concurrent()

Test medium load with 10 concurrent requests

### test_heavy_load_20_concurrent()

Test heavy load with 20 concurrent requests

## Class: TestStressScenarios

Test stress scenarios and edge cases

### setup_method()

### test_rapid_fire_requests()

Test rapid consecutive requests without delay

### test_mixed_load_different_voices()

Test mixed load with different voices

### test_varying_text_lengths_under_load()

Test varying text lengths under concurrent load

## Class: TestResourceExhaustion

Test behavior under resource exhaustion scenarios

### setup_method()

### test_sustained_load_over_time()

Test sustained load over a longer period

### test_memory_pressure_simulation()

Test behavior under simulated memory pressure

