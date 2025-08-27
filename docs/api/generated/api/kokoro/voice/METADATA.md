# metadata.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice metadata management and categorization


## Class: VoiceStats

Voice usage statistics

## Class: VoiceMetadataManager

Manages voice metadata and categorization

### __init__()

### load_metadata()

Load metadata from file

### save_metadata()

Save metadata to file

### _initialize_stats()

Initialize statistics for all voices

### get_voice_metadata()

Get metadata for a specific voice

### get_all_voices()

Get metadata for all voices

### filter_voices()

Filter voices by criteria

### get_voices_by_gender()

Get voices filtered by gender

### get_voices_by_quality()

Get voices with quality rating above threshold

### get_recommended_voices()

Get recommended voices based on quality and usage

### update_voice_stats()

Update usage statistics for a voice

### get_voice_stats()

Get usage statistics for a voice

### get_usage_summary()

Get overall usage summary

### add_custom_voice()

Add custom voice metadata

### remove_voice()

Remove voice metadata

### update_voice_metadata()

Update voice metadata fields

### get_voice_categories()

Get voices organized by categories

