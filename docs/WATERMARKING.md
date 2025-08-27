# Perth Audio Watermarking System

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

The Kokoro ONNX TTS API includes an integrated Perth audio watermarking system for responsible AI compliance and content authenticity verification.

## Overview

The Perth watermarking system automatically embeds imperceptible watermarks into all generated TTS audio, enabling:

- **Ethical AI Compliance**: Automatic marking of AI-generated content
- **Content Authenticity**: Verification of audio origin and integrity
- **Deepfake Detection**: Support for identifying synthetic audio content
- **Responsible AI**: Transparent disclosure of AI-generated content

## Features

### Automatic Watermarking
- All TTS-generated audio is automatically watermarked
- Imperceptible to human listeners
- Robust against common audio transformations
- Configurable strength and quality settings

### Detection Capabilities
- Watermark detection and verification
- Confidence scoring for detection results
- Support for batch processing
- Real-time detection capabilities

### Multiple Watermarking Techniques
- **Perth Implicit Watermarker**: Neural network-based approach (requires Perth library)
- **Dummy Watermarker**: Testing and development fallback
- **Mock Watermarkers**: Built-in testing support when Perth is unavailable

## Configuration

### Basic Configuration

```json
{
  "audio": {
    "watermarking_enabled": true,
    "watermark_strength": 1.0,
    "watermark_detection_enabled": true,
    "use_dummy_watermarker": false,
    "device": "cpu",
    "quality_threshold": 0.8,
    "max_processing_time_ms": 1000.0
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `watermarking_enabled` | boolean | `true` | Enable/disable watermarking |
| `watermark_strength` | float | `1.0` | Watermark strength (0.0-2.0) |
| `watermark_detection_enabled` | boolean | `true` | Enable watermark detection |
| `use_dummy_watermarker` | boolean | `false` | Use dummy watermarker for testing |
| `device` | string | `"cpu"` | Processing device (`cpu` or `cuda`) |
| `quality_threshold` | float | `0.8` | Minimum quality threshold |
| `max_processing_time_ms` | float | `1000.0` | Maximum processing time limit |

### Environment Variables

```bash
# Enable/disable watermarking
export KOKORO_WATERMARKING_ENABLED=true

# Set watermark strength
export KOKORO_WATERMARK_STRENGTH=1.0

# Use GPU acceleration
export KOKORO_WATERMARK_DEVICE=cuda

# Enable dummy watermarker for testing
export KOKORO_USE_DUMMY_WATERMARKER=true
```

## Installation

### Perth Library (Recommended)

For production use, install the Perth watermarking library:

```bash
pip install resemble-perth
```

### Fallback Mode

If Perth is not available, the system automatically uses mock watermarkers for testing and development.

## Usage

### Automatic Integration

Watermarking is automatically applied to all TTS-generated audio when enabled:

```python
from kokoro.tts import TTSEngine

# Initialize TTS engine (watermarking is automatic)
tts = TTSEngine()

# Generate audio (automatically watermarked)
audio = tts.synthesize("Hello, this is watermarked audio!")
```

### Manual Watermarking

For custom audio processing:

```python
from kokoro.audio import get_audio_watermarker
import numpy as np

# Get watermarker instance
watermarker = get_audio_watermarker()

# Apply watermark to audio
audio = np.random.randn(24000).astype(np.float32)
result = watermarker.apply_watermark(audio, sample_rate=24000)

if result.success:
    print(f"Watermark applied: {result.watermark_id}")
    print(f"Quality metrics: {result.quality_metrics}")
    watermarked_audio = result.watermarked_audio
```

### Watermark Detection

```python
from kokoro.audio import get_audio_watermarker

# Get watermarker instance
watermarker = get_audio_watermarker()

# Detect watermark in audio
detection_result = watermarker.detect_watermark(audio, sample_rate=24000)

if detection_result.success:
    print(f"Watermark detected: {detection_result.watermark_detected}")
    print(f"Watermark ID: {detection_result.watermark_id}")
    print(f"Confidence: {detection_result.confidence_score}")
```

## Quality Metrics

The system provides comprehensive quality metrics for watermarked audio:

### Signal Quality Metrics
- **SNR (Signal-to-Noise Ratio)**: Measures signal quality in dB
- **PSNR (Peak Signal-to-Noise Ratio)**: Peak signal quality measurement
- **MSE (Mean Squared Error)**: Average squared difference
- **Max Difference**: Maximum absolute difference between original and watermarked audio

### Example Quality Report
```python
{
    'snr_db': 46.54,
    'psnr_db': 49.56,
    'mse': 9.97e-07,
    'max_difference': 0.004
}
```

## Performance Monitoring

### Statistics Tracking

```python
# Get watermarking statistics
stats = watermarker.get_statistics()

print(f"Total watermarked: {stats['total_watermarked']}")
print(f"Success rate: {stats['watermark_success_rate']:.2%}")
print(f"Average processing time: {stats['average_processing_time_ms']:.2f}ms")
```

### Performance Optimization

- **GPU Acceleration**: Set `device: "cuda"` for faster processing
- **Batch Processing**: Process multiple files together
- **Quality Thresholds**: Adjust quality vs. speed trade-offs
- **Timeout Limits**: Configure maximum processing time

## API Integration

### REST API Endpoints

The watermarking system integrates seamlessly with the TTS API:

```bash
# Generate watermarked audio
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Hello world",
    "voice": "af_heart",
    "watermark": true
  }'

# Detect watermark in audio
curl -X POST "http://localhost:8354/v1/audio/detect" \
  -F "audio=@audio_file.wav"
```

### Response Headers

Watermarked audio includes metadata headers:

```
X-Watermark-Applied: true
X-Watermark-ID: kokoro_abc123def456
X-Watermark-Quality: 0.95
X-Processing-Time-Ms: 45.2
```

## Security Considerations

### Watermark Robustness
- Survives common audio transformations
- Resistant to compression and resampling
- Maintains integrity through format conversion
- Robust against noise addition

### Privacy Protection
- Watermarks contain no personal information
- Only system-generated identifiers
- No tracking or user identification
- Compliant with privacy regulations

## Troubleshooting

### Common Issues

**Watermarking Disabled**
```
Error: Watermarking disabled or not available
Solution: Check configuration and Perth library installation
```

**Poor Quality Metrics**
```
Warning: Low SNR detected (< 40dB)
Solution: Reduce watermark strength or check audio quality
```

**Slow Processing**
```
Warning: Processing time exceeded threshold
Solution: Enable GPU acceleration or increase timeout
```

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger('kokoro.audio.watermarking').setLevel(logging.DEBUG)
```

## Best Practices

### Production Deployment
1. Install Perth library for optimal performance
2. Use GPU acceleration when available
3. Monitor quality metrics regularly
4. Set appropriate timeout limits
5. Enable performance monitoring

### Development and Testing
1. Use dummy watermarker for unit tests
2. Test with various audio formats
3. Validate quality metrics
4. Monitor processing times
5. Test detection accuracy

### Compliance and Ethics
1. Always disclose AI-generated content
2. Maintain watermark integrity
3. Provide detection capabilities
4. Document watermarking policies
5. Regular system audits

## Support

For issues related to the Perth watermarking system:

1. Check the [Perth GitHub repository](https://github.com/resemble-ai/Perth)
2. Review configuration settings
3. Enable debug logging
4. Monitor system performance
5. Contact support with detailed logs

## License

The Perth watermarking integration is provided under the MIT License. The Perth library itself is subject to its own licensing terms.
