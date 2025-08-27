# validator.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice model validator for integrity checking


## Class: ValidationResult

Voice validation result

## Class: VoiceValidator

Validates voice model files for integrity and compatibility

### __init__()

### validate_voice()

Validate a single voice model file

### _validate_model_structure()

Validate the structure of the loaded model

### _validate_embedding_data()

Validate embedding data within the model

### _perform_additional_checks()

Perform additional validation checks

### validate_all_voices()

Validate all voice files in a directory

### get_validation_summary()

Get summary of validation results

### repair_voice_file()

Attempt to repair a corrupted voice file

### check_compatibility()

Check compatibility with target device and system

