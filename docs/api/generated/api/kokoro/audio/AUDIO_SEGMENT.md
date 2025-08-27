# audio_segment.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Enhanced AudioSegment class with format conversion and streaming support


## Class: AudioSegment

Enhanced audio data structure with processing capabilities

### __post_init__()

### from_bytes()

Create AudioSegment from raw audio bytes

### silence()

Create a silent audio segment

### to_bytes()

Convert audio data to bytes

### concatenate()

Concatenate with another audio segment

### trim()

Trim audio segment to specified time range

### fade_in()

Apply fade-in effect

### fade_out()

Apply fade-out effect

### adjust_volume()

Adjust volume by multiplier

### resample()

Resample audio to target sample rate

### get_chunks()

Split audio into chunks of specified duration

### validate()

Validate audio segment data

### get_info()

Get audio segment information

