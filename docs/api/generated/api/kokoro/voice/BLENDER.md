# blender.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Voice blending functionality for Kokoro TTS
Allows blending multiple voices with customizable weights


## Class: BlendConfig

Configuration for voice blending

## Class: VoiceBlender

Voice blending system for creating custom voice combinations

### __init__()

### blend_voices()

Blend multiple voices according to the configuration

Args:
    blend_config: Configuration specifying voices and blending parameters
    
Returns:
    VoiceEmbedding with blended voice data

### _weighted_average_blend()

Blend voices using weighted average

### _interpolation_blend()

Blend voices using smooth interpolation

### _style_mixing_blend()

Blend voices using style mixing (different parts of the embedding from different voices)

### _slerp_blend()

Spherical linear interpolation between two voices

### _preserve_energy()

Preserve the energy level of the original voice

### _create_blended_metadata()

Create metadata for the blended voice

### _generate_blend_name()

Generate a name for the blended voice

### get_supported_methods()

Get list of supported blending methods

### create_preset_blend()

Create a preset blend configuration

## Class: VoiceMetadata

## Class: VoiceEmbedding

