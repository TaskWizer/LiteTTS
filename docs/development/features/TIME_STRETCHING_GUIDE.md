# Time-Stretching Optimization Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

## Overview

The Time-Stretching Optimization feature improves TTS generation performance by synthesizing audio at faster speeds and using advanced time-stretching algorithms to restore normal playback speed. This technique can achieve **40%+ RTF improvements** while maintaining excellent audio quality.

## How It Works

1. **Fast Generation**: TTS synthesizes audio at 1.1x to 2.0x speed
2. **Time Correction**: Advanced algorithms stretch the audio back to normal speed
3. **Quality Preservation**: Maintains pitch, tone, and naturalness of speech

## Quick Start

### 1. Install Dependencies

```bash
# Required for time-stretching
pip install librosa>=0.8.0 soundfile>=0.10.0

# Optional for highest quality
sudo apt install rubberband-cli
pip install pyrubberband>=0.3.0
```

### 2. Enable in Configuration

Edit `config.json`:
```json
{
  "text_processing": {
    "time_stretching_optimization": {
      "enabled": true,
      "compress_playback_rate": 30,
      "correction_quality": "medium"
    }
  }
}
```

### 3. Use via API

```bash
curl -X POST "http://localhost:8080/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello, this uses time-stretching optimization!",
    "voice": "af_heart",
    "time_stretching_enabled": true,
    "time_stretching_rate": 30
  }'
```

## Performance Results

Based on comprehensive benchmarking:

| Compression Rate | RTF Improvement | Quality Score | Recommended Use |
|------------------|-----------------|---------------|-----------------|
| 10% | 28.7% | 1.00 | Conservative |
| 20% | 36.2% | 1.00 | Balanced |
| **30%** | **42.6%** | **1.00** | **Optimal** |
| 40% | 48.1% | 0.90 | Aggressive |
| 50% | 52.9% | 0.90 | Maximum performance |

## Configuration Options

### Basic Settings

```json
{
  "enabled": true,                    // Enable/disable feature
  "compress_playback_rate": 30,       // Compression rate (10-100%)
  "correction_quality": "medium",     // Quality level: low/medium/high
  "auto_enable_threshold": 50,        // Auto-enable for texts longer than N chars
  "quality_fallback": true            // Fallback to lower quality if needed
}
```

### Advanced Settings

```json
{
  "max_rate": 100,                    // Maximum allowed compression rate
  "min_rate": 10,                     // Minimum allowed compression rate
  "benchmark_mode": false             // Enable detailed performance logging
}
```

## API Parameters

### Request Parameters

- `time_stretching_enabled` (boolean): Override config setting
- `time_stretching_rate` (integer): Compression rate 10-100%
- `time_stretching_quality` (string): Quality level

### Example Requests

**Basic usage:**
```json
{
  "input": "Your text here",
  "voice": "af_heart",
  "time_stretching_enabled": true
}
```

**Custom settings:**
```json
{
  "input": "Your text here",
  "voice": "am_adam",
  "time_stretching_enabled": true,
  "time_stretching_rate": 40,
  "time_stretching_quality": "high"
}
```

**Disable for specific request:**
```json
{
  "input": "Your text here",
  "voice": "af_bella",
  "time_stretching_enabled": false
}
```

## Quality Guidelines

### Recommended Rates by Use Case

- **Production/Customer-facing**: 20-30% (excellent quality)
- **Internal tools**: 30-40% (good quality, better performance)
- **Batch processing**: 40-50% (acceptable quality, maximum speed)
- **Testing/Development**: 50%+ (performance testing)

### Quality Assessment

- **Excellent (≥0.9)**: No perceptible quality loss
- **Good (≥0.8)**: Minor quality trade-offs, still professional
- **Acceptable (≥0.7)**: Noticeable but usable quality
- **Poor (<0.7)**: Significant quality degradation

## Troubleshooting

### Common Issues

**Feature not working:**
1. Check librosa installation: `python -c "import librosa; print('OK')"`
2. Verify configuration: `enabled: true` in config.json
3. Check logs for initialization messages

**Poor performance:**
1. Ensure librosa uses optimized BLAS libraries
2. Monitor CPU usage during synthesis
3. Consider reducing compression rate

**Audio artifacts:**
1. Reduce compression rate (try 20% instead of 50%)
2. Switch to "high" quality mode if pyrubberband is available
3. Enable quality_fallback in configuration

### Debug Mode

Enable detailed logging:
```json
{
  "time_stretching_optimization": {
    "benchmark_mode": true
  }
}
```

This provides metrics like:
- Generation speed multiplier
- Time-stretching processing time
- RTF improvements
- Quality scores

## Best Practices

### Production Deployment

1. **Start Conservative**: Begin with 20-30% compression
2. **Monitor Quality**: Use listening tests to validate output
3. **Measure Performance**: Track RTF improvements in your environment
4. **Gradual Optimization**: Increase rates based on quality acceptance

### Performance Optimization

1. **Text Length Consideration**: Longer texts benefit more from time-stretching
2. **Voice Selection**: Some voices may work better with time-stretching
3. **Batch Processing**: Higher rates acceptable for non-real-time use
4. **Caching**: Cache time-stretched results for repeated content

### Quality Assurance

1. **A/B Testing**: Compare time-stretched vs normal synthesis
2. **User Feedback**: Monitor customer satisfaction metrics
3. **Automated Testing**: Include time-stretching in CI/CD pipelines
4. **Fallback Strategy**: Disable feature if quality issues detected

## Technical Details

### Dependencies

- **librosa**: Core time-stretching functionality
- **pyrubberband**: High-quality time-stretching (optional)
- **soundfile**: Audio I/O operations
- **numpy**: Numerical computations

### Processing Overhead

- **CPU Impact**: <1% additional processing time
- **Memory Usage**: Minimal increase, no memory leaks
- **Latency**: Slight increase due to time-stretching correction
- **Quality**: Excellent preservation with proper settings

### Supported Formats

- **Input**: All TTS-supported text formats
- **Output**: MP3, WAV, OGG, FLAC
- **Streaming**: Full support for streaming endpoints
- **Voices**: Compatible with all voice models

## Examples

### Python Integration

```python
from kokoro.audio.time_stretcher import TimeStretcher, TimeStretchConfig

# Create optimized configuration
config = TimeStretchConfig(
    enabled=True,
    compress_playback_rate=30,
    correction_quality="medium"
)

stretcher = TimeStretcher(config)

# Check if feature is available
if stretcher.config.enabled:
    print(f"Time-stretching ready: {stretcher.get_generation_speed_multiplier()}x speed")
```

### Performance Testing

```python
# Benchmark different rates
rates = [10, 20, 30, 40, 50]
for rate in rates:
    config = TimeStretchConfig(enabled=True, compress_playback_rate=rate)
    stretcher = TimeStretcher(config)
    
    # Test with your audio
    corrected_audio, metrics = stretcher.stretch_audio_to_normal_speed(
        fast_audio, stretcher.get_generation_speed_multiplier()
    )
    
    print(f"Rate {rate}%: RTF improvement {metrics.rtf_improvement:.1%}")
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Test with different compression rates
4. Verify dependency installation

The time-stretching optimization feature is production-ready and provides significant performance improvements while maintaining excellent audio quality when properly configured.
