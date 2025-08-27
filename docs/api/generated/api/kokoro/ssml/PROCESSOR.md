# processor.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


SSML Processor for Kokoro TTS

Processes SSML markup and integrates background noise with speech synthesis.


## Class: SSMLProcessor

SSML Processor that handles background noise integration

Processes SSML markup, generates background audio, and mixes it with speech.

### __init__()

### process_ssml()

Process SSML text and extract components

Args:
    ssml_text: SSML markup text
    
Returns:
    Tuple of (plain_text, background_config, processing_metadata)

### synthesize_with_background()

Mix speech audio with background noise

Args:
    speech_audio: Primary speech audio
    background_config: Background noise configuration
    
Returns:
    Mixed audio with background

### _mix_audio_with_background()

Mix speech and background audio with proper level balancing

Args:
    speech: Primary speech audio
    background: Background ambient audio
    config: Background configuration
    
Returns:
    Mixed audio segment

### _apply_background_compression()

Apply compression to background audio to maintain speech clarity

### _apply_speech_ducking()

Apply speech-aware ducking to background audio

### _apply_soft_limiting()

Apply soft limiting to prevent clipping

### validate_ssml()

Validate SSML markup

Args:
    ssml_text: SSML markup to validate
    
Returns:
    Validation result with errors and warnings

### get_supported_background_types()

Get list of supported background types

### create_background_example()

Create an example of a background type for testing/preview

Args:
    bg_type: Background type name
    duration: Duration in seconds
    
Returns:
    AudioSegment with example background audio

