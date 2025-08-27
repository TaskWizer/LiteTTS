# engine.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../FEATURES.md) | [Configuration](../../../../../CONFIGURATION.md) | [Performance](../../../../../PERFORMANCE.md) | [Monitoring](../../../../../MONITORING.md) | [Testing](../../../../../TESTING.md) | [Troubleshooting](../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../API_REFERENCE.md) | [Development](../../../../../development/README.md) | [Voice System](../../../../../voices/README.md) | [Watermarking](../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../CHANGELOG.md) | [Roadmap](../../../../../ROADMAP.md) | [Contributing](../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../BETA_FEATURES.md)

---


Kokoro TTS engine wrapper with ONNX runtime integration


## Class: KokoroTTSEngine

Main TTS engine using Kokoro model with ONNX runtime

### __init__()

### _initialize_engine()

Initialize the TTS engine

### _load_onnx_model()

Load the ONNX model

### _load_tokenizer()

Load the tokenizer

### _create_simple_tokenizer()

Create a simple character-based tokenizer

### _setup_voice_system()

Setup the voice management system

### synthesize()

Synthesize text to audio

### _tokenize_text()

Tokenize input text

### _prepare_model_inputs()

Prepare inputs for the ONNX model

### _run_inference()

Run ONNX model inference

### _post_process_audio()

Post-process the generated audio

### _apply_speed_adjustment()

Apply speed adjustment to audio data

### load_voice()

Load a voice embedding

### get_available_voices()

Get list of available voices

### is_voice_available()

Check if a voice is available

### get_engine_info()

Get engine information

### preload_voice()

Preload a voice into cache

### preload_voices()

Preload multiple voices into cache

### get_voice_info()

Get detailed information about a voice

### estimate_synthesis_time()

Estimate synthesis time for given text

### synthesize_with_blended_voice()

Synthesize text using a blended voice

### create_voice_blend()

Create a blended voice from multiple voices

### get_blend_presets()

Get available voice blend presets

### synthesize_with_preset_blend()

Synthesize text using a preset voice blend

### cleanup()

Clean up engine resources

