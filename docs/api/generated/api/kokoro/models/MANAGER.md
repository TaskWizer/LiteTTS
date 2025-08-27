# manager.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Model management system for Kokoro ONNX TTS API with multi-model support


## Class: ModelInfo

Information about a model variant

## Class: DownloadProgress

Download progress information

## Class: ModelManager

Manages ONNX model variants with dynamic discovery and caching

### __init__()

### _load_discovery_cache()

Load discovery cache from JSON file

### _save_discovery_cache()

Save discovery cache to JSON file

### _is_cache_expired()

Check if discovery cache is expired

### discover_models_from_huggingface()

Discover all model files from HuggingFace repository

### _determine_variant_type()

Determine the variant type from model filename

### _get_variant_description()

Get description for variant type

### get_available_models()

Get list of all available model names

### get_model_info()

Get information about a specific model

### is_model_downloaded()

Check if a model is already downloaded

### get_model_path()

Get local path for a model (default or specified)

### download_model()

Download a specific model

### _validate_file_integrity()

Validate file integrity against expected size and hash

### _calculate_file_hash()

Calculate SHA256 hash of a file

