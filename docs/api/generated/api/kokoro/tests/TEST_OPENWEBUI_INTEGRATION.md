# test_openwebui_integration.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


OpenWebUI Integration Testing for Kokoro ONNX TTS API
Tests all endpoints and compatibility routes for OpenWebUI integration


## Class: OpenWebUIIntegrationTester

Comprehensive OpenWebUI integration testing class

### __init__()

### test_standard_speech_endpoint()

Test standard OpenAI-compatible /v1/audio/speech endpoint

### test_streaming_endpoint()

Test streaming /v1/audio/stream endpoint

### test_openwebui_compatibility_route()

Test OpenWebUI compatibility route /v1/audio/stream/audio/speech

### test_voices_endpoint()

Test voices listing endpoint

### test_different_voices()

Test different voice options

### test_openwebui_configuration_scenarios()

Test different OpenWebUI configuration scenarios

### run_comprehensive_test()

Run all OpenWebUI integration tests

### print_summary()

Print test summary

## Function: main()

Main function

