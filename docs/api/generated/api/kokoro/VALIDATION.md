# validation.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Input validation and sanitization for Kokoro ONNX TTS API
Comprehensive validation for all user inputs and system parameters


## Class: ValidationResult

Result of input validation

### __post_init__()

## Class: InputValidator

Comprehensive input validation and sanitization

### validate_text()

Validate and sanitize text input

### validate_voice()

Validate voice selection

### validate_format()

Validate audio format with OpenWebUI compatibility

### validate_speed()

Validate speech speed with OpenWebUI compatibility

### validate_tts_request()

Validate complete TTS request

### _has_phonemizer_issues()

Check if text might cause phonemizer issues

## Class: SecurityValidator

Security-focused validation

### validate_file_path()

Validate file paths to prevent directory traversal

### validate_api_key()

Validate API key format

## Function: validate_request()

Convenience function for request validation
Returns: (is_valid, sanitized_data_or_error_message, warnings)

