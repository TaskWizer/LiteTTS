# downloader.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Dynamic voice model downloader with HuggingFace API integration


## Class: DownloadProgress

Download progress information

## Class: VoiceFileInfo

Information about a voice file from HuggingFace

## Class: VoiceDownloader

Downloads and manages voice models from HuggingFace with dynamic discovery

### __init__()

### _load_discovery_cache()

Load discovery cache from JSON file

### _save_discovery_cache()

Save discovery cache to JSON file

### _is_cache_expired()

Check if discovery cache is expired

### discover_voices_from_huggingface()

Discover ALL voice files from HuggingFace repository automatically

### get_available_voice_names()

Get list of all available voice names from HuggingFace

### download_voice()

Download a specific voice model (.bin file directly)

### download_all_voices()

Download all available voices

### download_default_voices()

Download default voices (backward compatibility) - now downloads ALL voices

### is_voice_downloaded()

Check if a voice is already downloaded

### get_downloaded_voices()

Get list of downloaded voices

### get_missing_voices()

Get list of voices that need to be downloaded

### _validate_file_integrity()

Validate file integrity against expected size and hash

### _calculate_file_hash()

Calculate SHA256 hash of a file

### get_voice_file_path()

Get local file path for a voice

### get_download_info()

Get download information for all voices

### cleanup_invalid_files()

Remove invalid or corrupted voice files

### refresh_discovery()

Force refresh of voice discovery from HuggingFace

### get_discovery_stats()

Get statistics about voice discovery

