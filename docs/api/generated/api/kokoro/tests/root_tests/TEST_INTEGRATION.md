# test_integration.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Integration Tests for Kokoro ONNX TTS API
Tests integration with external services, OpenWebUI compatibility, and real-world scenarios


## Class: TestOpenWebUIIntegration

Test OpenWebUI compatibility and integration

### setup_method()

### test_openwebui_models_endpoint()

Test OpenWebUI models endpoint compatibility

### test_openwebui_speech_endpoint()

Test OpenWebUI speech endpoint compatibility

### test_openwebui_compatibility_routes()

Test OpenWebUI compatibility routes for malformed URLs

### test_openwebui_voice_parameter_variations()

Test various voice parameter formats that OpenWebUI might send

## Class: TestExternalAPICompatibility

Test compatibility with external API standards

### setup_method()

### test_openai_api_compatibility()

Test OpenAI API compatibility

### test_content_type_variations()

Test different content type headers

### test_user_agent_variations()

Test different User-Agent headers

## Class: TestRealWorldScenarios

Test real-world usage scenarios

### setup_method()

### test_chatbot_integration_scenario()

Test typical chatbot integration scenario

### test_multilingual_content_scenario()

Test multilingual content handling

### test_educational_content_scenario()

Test educational content with various text types

## Class: TestPerformanceIntegration

Test performance in integration scenarios

### setup_method()

### test_cache_behavior_in_integration()

Test cache behavior in realistic usage patterns

### test_mixed_voice_performance()

Test performance with mixed voice usage

