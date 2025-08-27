# response_formatter.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Response formatting for TTS API


## Class: ResponseFormatter

Formats API responses for different output types

### __init__()

### _create_audio_headers()

Create headers for audio response

### _create_audio_stream()

Create streaming iterator for audio data

### _create_streaming_headers()

Create headers for streaming audio response

### format_json_response()

Format JSON response with metadata

### format_error_response()

Format error response

### format_health_response()

Format health check response

### format_voice_list_response()

Format voice list response

### format_stats_response()

Format statistics response

### create_sse_response()

Create Server-Sent Events response for real-time streaming

### create_download_response()

Create downloadable file response

### _get_timestamp()

Get current timestamp

### get_supported_formats()

Get list of supported audio formats

### validate_format()

Validate if format is supported

