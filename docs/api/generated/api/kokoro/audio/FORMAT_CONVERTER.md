# format_converter.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Audio format conversion utilities


## Class: AudioFormatConverter

Handles conversion between different audio formats

### __init__()

### convert_to_wav()

Convert audio data to WAV format

### convert_to_mp3()

Convert audio data to MP3 format (requires pydub/ffmpeg)

### convert_to_ogg()

Convert audio data to OGG format (requires pydub/ffmpeg)

### convert_format()

Convert audio to specified format

### get_content_type()

Get MIME content type for audio format

### get_file_extension()

Get file extension for audio format

### is_format_supported()

Check if format is supported

### get_format_info()

Get information about audio format

