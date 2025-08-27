# internal_config.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Internal Configuration System for Kokoro TTS
Contains technical defaults and advanced settings not exposed to end users


## Class: InternalConfig

Internal configuration system for technical settings

### __init__()

### _get_pronunciation_rules()

Internal pronunciation rules configuration

### _get_acronym_handling()

Internal acronym handling configuration

### _get_text_processing_defaults()

Internal text processing defaults

### _get_performance_defaults()

Internal performance optimization defaults

### _get_cache_defaults()

Internal cache optimization defaults

### get_config_section()

Get a specific configuration section

### override_setting()

Override a specific setting (for advanced users)

### load_overrides_from_env()

Load configuration overrides from environment variables

### get_all_config()

Get all internal configuration

## Function: get_internal_config()

Get the global internal configuration instance

## Function: reload_internal_config()

Reload the internal configuration

