# optimized_processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Audio Processing Optimizations for RTF Improvement


## Class: OptimizedAudioProcessor

Optimized audio processor with RTF improvements

### __init__()

### process_audio_optimized()

Process audio with RTF optimizations

Args:
    audio_data: Raw audio data
    sample_rate: Audio sample rate
    optimize_for_rtf: Enable RTF optimizations
    
Returns:
    Processed audio data

### _fast_normalize()

Fast audio normalization using numpy vectorization

### _efficient_resample()

Efficient resampling with minimal quality loss

### _minimal_processing()

Apply only essential audio processing

### _update_processing_stats()

Update processing statistics

### get_performance_stats()

Get current performance statistics

## Function: get_optimized_audio_processor()

Get the global optimized audio processor instance

