# config_manager.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Configuration Manager for Kokoro TTS
Bridges user-friendly config.json with internal technical configuration


## Class: ConfigManager

Manages both user-facing and internal configuration

### __init__()

### _load_user_config()

Load user-facing configuration from config.json

### _get_default_user_config()

Get default user configuration

### _merge_configs()

Merge user config with internal config based on user preferences

### get()

Get a configuration value

### get_user_config()

Get the user-facing configuration

### get_internal_config()

Get the internal configuration

### get_merged_config()

Get the merged configuration

### update_user_config()

Update user configuration and save to file

### _save_user_config()

Save user configuration to file

### override_internal_setting()

Override an internal setting (for advanced users)

### is_feature_enabled()

Check if a feature is enabled

### get_processing_options()

Get processing options for the unified text processor

### validate_config()

Validate the current configuration

## Function: get_config_manager()

Get the global configuration manager instance

## Function: reload_config()

Reload the configuration

