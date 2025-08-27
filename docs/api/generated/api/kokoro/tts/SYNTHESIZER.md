# synthesizer.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Main TTS synthesizer that orchestrates all TTS components


## Class: TTSSynthesizer

Main TTS synthesizer that coordinates all components

### __init__()

### _initialize_time_stretcher()

Initialize time-stretching feature from configuration

### synthesize()

Main synthesis method

### synthesize_simple()

Simple synthesis method with minimal parameters

### get_available_voices()

Get list of available voices

### get_time_stretching_metrics()

Get time-stretching performance metrics

### benchmark_time_stretching_rates()

Benchmark different time-stretching rates

### get_supported_emotions()

Get list of supported emotions

### get_voice_info()

Get detailed information about a voice

### get_emotion_info()

Get information about an emotion

### estimate_synthesis_time()

Estimate synthesis time

### validate_request()

Validate synthesis request

### preload_voice()

Preload a voice for faster synthesis

### preload_voices()

Preload multiple voices

### get_system_status()

Get comprehensive system status

### suggest_voice_for_text()

Suggest an appropriate voice based on text content

### suggest_emotion_for_text()

Suggest an appropriate emotion based on text content

### create_synthesis_profile()

Create a reusable synthesis profile

### synthesize_with_profile()

Synthesize using a predefined profile

### batch_synthesize()

Synthesize multiple texts in batch

### cleanup()

Clean up synthesizer resources

### get_synthesis_stats()

Get synthesis statistics

