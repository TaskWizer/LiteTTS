# error_handling.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Comprehensive error handling and graceful degradation for Kokoro ONNX TTS API


## Class: ErrorSeverity

Error severity levels

## Class: ErrorContext

Context information for error handling

### __post_init__()

## Class: TTSError

Base TTS error with context

### __init__()

## Class: ModelLoadError

Error loading TTS model

## Class: VoiceNotFoundError

Voice not available

## Class: AudioGenerationError

Error generating audio

## Class: ValidationError

Input validation error

## Class: SystemResourceError

System resource exhaustion

## Class: ErrorHandler

Comprehensive error handling system

### __init__()

### handle_error()

Handle error with appropriate response

### _determine_severity()

Determine error severity

### _log_error()

Log error with appropriate level

### _track_error()

Track error for pattern analysis

### _should_circuit_break()

Check if circuit breaker should activate

### _circuit_breaker_response()

Generate circuit breaker response

### _generate_error_response()

Generate appropriate error response

## Function: error_handler()

Decorator for automatic error handling

## Class: GracefulDegradation

Graceful degradation strategies

### fallback_voice()

Find fallback voice if requested voice unavailable

### fallback_format()

Find fallback audio format

### simplify_text()

Simplify text if generation fails

