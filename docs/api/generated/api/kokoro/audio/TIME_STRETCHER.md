# time_stretcher.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Time-Stretching Optimization Module
Implements beta time-stretching feature for improved TTS latency


## Class: StretchQuality

Time-stretching quality levels

## Class: TimeStretchConfig

Configuration for time-stretching optimization

### __post_init__()

Validate configuration

## Class: StretchMetrics

Metrics for time-stretching performance

## Class: TimeStretcher

Time-stretching processor for TTS optimization

### __init__()

### should_apply_stretching()

Determine if time-stretching should be applied

### get_generation_speed_multiplier()

Get the speed multiplier for generation

### stretch_audio_to_normal_speed()

Stretch audio back to normal speed after fast generation

### _apply_time_stretch()

Apply time-stretching using the best available method

### _stretch_with_pyrubberband()

High-quality time-stretching using pyrubberband

### _stretch_with_librosa()

Medium-quality time-stretching using librosa

### _stretch_basic()

Basic time-stretching using linear interpolation (low quality)

### get_metrics_summary()

Get summary of time-stretching metrics

### benchmark_rates()

Benchmark different stretch rates for testing

