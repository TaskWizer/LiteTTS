# validators.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Request validation for TTS API


## Class: RequestValidator

Validates TTS API requests

### __init__()

### validate_request()

Validate a TTS request and return list of errors

### _validate_text()

Validate input text

### _validate_voice()

Validate voice parameter

### _validate_speed()

Validate speed parameter

### _validate_format()

Validate response format

### _validate_volume()

Validate volume multiplier

### _validate_emotion()

Validate emotion parameter

### _validate_emotion_strength()

Validate emotion strength parameter

### _validate_language_code()

Validate language code

### _has_excessive_repetition()

Check for excessive character or word repetition

### _has_valid_characters()

Check if text contains only valid characters

### validate_batch_request()

Validate a batch synthesis request

### get_validation_rules()

Get current validation rules

