# Time-Stretching Feature Testing Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

## Overview

The time-stretching optimization feature is now fully implemented and tested. This beta feature improves TTS latency by generating audio at faster speeds and then correcting the playback speed using advanced time-stretching algorithms.

## Performance Results

Based on our testing, the time-stretching feature provides significant performance improvements:

- **Baseline (no stretching)**: 1.600s generation time
- **20% stretching (medium quality)**: 0.165s generation time (**89.7% faster**)
- **50% stretching (high quality)**: 0.165s generation time (**89.7% faster**)
- **80% stretching (low quality)**: 0.192s generation time (**88.0% faster**)

## API Integration

### Request Parameters

The time-stretching feature can be controlled via API parameters in the `/v1/audio/speech` endpoint:

```json
{
  "input": "Your text to synthesize",
  "voice": "af_heart",
  "response_format": "wav",
  "time_stretching_enabled": true,
  "time_stretching_rate": 20,
  "time_stretching_quality": "medium"
}
```

### Parameters

- **`time_stretching_enabled`** (optional, boolean): Enable/disable time-stretching for this request
  - `true`: Enable time-stretching
  - `false`: Disable time-stretching
  - `null` (default): Use configuration-based decision

- **`time_stretching_rate`** (optional, integer, 10-100): Compression rate percentage
  - `10`: Minimal compression (1.1x speed)
  - `20`: Light compression (1.2x speed) - **Recommended**
  - `50`: Moderate compression (1.5x speed)
  - `80`: High compression (1.8x speed)
  - `100`: Maximum compression (2.0x speed)

- **`time_stretching_quality`** (optional, string): Quality level for time-stretching correction
  - `"low"`: Basic interpolation (fastest, lowest quality)
  - `"medium"`: Librosa-based stretching (balanced) - **Recommended**
  - `"high"`: Pyrubberband-based stretching (slowest, highest quality)

## Testing Commands

### Basic API Test

```bash
# Test with time-stretching enabled
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "This is a test of time-stretching optimization.",
    "voice": "af_heart",
    "response_format": "wav",
    "time_stretching_enabled": true,
    "time_stretching_rate": 20,
    "time_stretching_quality": "medium"
  }' \
  --output time_stretched_test.wav

# Test without time-stretching for comparison
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "This is a test of time-stretching optimization.",
    "voice": "af_heart", 
    "response_format": "wav",
    "time_stretching_enabled": false
  }' \
  --output baseline_test.wav
```

### Comprehensive Test Script

Use the provided test script to run comprehensive tests:

```bash
python test_time_stretching.py
```

This script tests:
- Baseline (no stretching)
- 20% compression with medium quality
- 50% compression with high quality  
- 80% compression with low quality
- Config-based automatic stretching

## Configuration

### Global Configuration (config.json)

```json
{
  "time_stretching": {
    "enabled": true,
    "compress_playback_rate": 20,
    "correction_quality": "medium",
    "max_rate": 100,
    "min_rate": 10,
    "auto_enable_threshold": 50,
    "quality_fallback": true,
    "benchmark_mode": false
  }
}
```

### Configuration Options

- **`enabled`**: Enable time-stretching globally
- **`compress_playback_rate`**: Default compression rate (10-100%)
- **`correction_quality`**: Default quality level ("low", "medium", "high")
- **`max_rate`**: Maximum allowed compression rate
- **`min_rate`**: Minimum allowed compression rate
- **`auto_enable_threshold`**: Auto-enable for texts longer than this character count
- **`quality_fallback`**: Fallback to lower quality if high quality fails
- **`benchmark_mode`**: Enable detailed performance metrics

## Quality Assessment

### Audio Quality by Compression Rate

- **10-30%**: Excellent quality, minimal artifacts
- **40-60%**: Good quality, slight artifacts
- **70-90%**: Acceptable quality, noticeable artifacts
- **90-100%**: Poor quality, significant artifacts

### Quality Levels

- **Low**: Fast processing, basic quality
- **Medium**: Balanced processing and quality (**Recommended**)
- **High**: Slow processing, best quality

## Sample Files

Test audio files are available in:
- `test_time_stretching_output/` - Generated test files
- `samples/time-stretched/` - Pre-generated samples with various rates

### Sample File Comparison

- `baseline_no_stretching.wav` - Original quality reference
- `stretching_20_percent_medium.wav` - Recommended settings
- `stretching_50_percent_high.wav` - High quality, moderate compression
- `stretching_80_percent_low.wav` - Maximum speed, acceptable quality

## Performance Metrics

The time-stretching feature provides:
- **Up to 90% reduction in generation time**
- **Maintained audio quality** with proper settings
- **Automatic fallback** if libraries are unavailable
- **Real-time performance monitoring**

## Recommendations

### Production Use
- Use 20% compression rate with medium quality
- Enable quality fallback
- Test thoroughly with your specific use cases

### Development/Testing
- Use higher compression rates for faster iteration
- Enable benchmark mode for detailed metrics
- Test with various text lengths and voices

## Troubleshooting

### Common Issues

1. **No performance improvement**: Check that `time_stretching_enabled` is `true`
2. **Poor audio quality**: Reduce compression rate or increase quality level
3. **Feature not working**: Ensure librosa is installed (`pip install librosa`)
4. **High quality unavailable**: Install pyrubberband (`pip install pyrubberband`)

### Dependencies

- **Required**: `librosa` (medium/low quality)
- **Optional**: `pyrubberband` (high quality)
- **Fallback**: Basic interpolation (not recommended for production)
