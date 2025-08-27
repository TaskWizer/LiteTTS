# exceptions.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Custom exceptions for Kokoro ONNX TTS API with enhanced error handling


## Class: KokoroError

Base exception for Kokoro ONNX TTS API with enhanced error context

### __init__()

### to_dict()

Convert exception to dictionary for API responses

### __str__()

## Class: ModelError

Raised when there are issues with the TTS model

### __init__()

## Class: VoiceError

Raised when there are issues with voice processing

### __init__()

## Class: AudioError

Raised when there are issues with audio processing

### __init__()

## Class: ValidationError

Raised when input validation fails

### __init__()

## Class: CacheError

Raised when there are caching issues

### __init__()

## Class: ConfigurationError

Raised when there are configuration issues

### __init__()

## Class: DownloadError

Raised when model/voice downloads fail

### __init__()

## Class: RateLimitError

Raised when rate limits are exceeded

### __init__()

## Class: AuthenticationError

Raised when authentication fails

### __init__()

## Class: TextProcessingError

Raised when text processing fails

### __init__()

## Function: get_http_status()

Get appropriate HTTP status code for an exception

