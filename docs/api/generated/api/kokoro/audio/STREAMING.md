# streaming.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Audio streaming utilities for chunked responses


## Class: StreamChunk

Represents a chunk of streaming audio data

## Class: AudioStreamer

Handles streaming audio responses

### __init__()

### stream_audio_sync()

Stream audio synchronously in chunks

### create_streaming_response_headers()

Create headers for streaming audio response

### estimate_stream_size()

Estimate the total size of the streaming response

### create_sse_stream()

Create Server-Sent Events stream for audio data

## Class: RealTimeStreamer

Handles real-time audio streaming as it's being generated

### __init__()

### is_buffer_empty()

Check if the streaming buffer is empty

