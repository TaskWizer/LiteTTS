# models.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Core data models and type definitions for Kokoro ONNX TTS API


## Class: TTSConfiguration

System configuration settings

## Class: VoiceMetadata

Voice metadata and categorization

## Class: VoiceEmbedding

Voice embedding data structure

## Class: AudioSegment

Audio data structure

### __post_init__()

## Class: NormalizationOptions

Text normalization configuration

## Class: TTSRequest

Comprehensive TTS request model

## Class: TTSResponse

TTS response metadata

## Class: ProcessingMetrics

Performance and processing metrics

## Class: ProsodyInfo

Prosody analysis information

## Class: TTSEngineProtocol

Interface for TTS engines

### synthesize()

Synthesize text to audio

### load_voice()

Load a voice embedding

### get_available_voices()

Get list of available voices

## Class: NLPProcessorProtocol

Interface for NLP processors

### normalize_text()

Normalize input text

### resolve_homographs()

Resolve homograph pronunciations

### process_phonetics()

Process phonetic markers

### analyze_prosody()

Analyze text for prosody information

## Class: CacheManagerProtocol

Interface for cache management

### get_cached_audio()

Get cached audio segment

### cache_audio()

Cache audio segment

### get_voice_embedding()

Get cached voice embedding

### preload_voices()

Preload voice embeddings

## Class: TTSError

Base TTS error

### __init__()

## Class: VoiceNotFoundError

Voice not found error

### __init__()

## Class: ModelLoadError

Model loading error

### __init__()

## Class: AudioGenerationError

Audio generation error

### __init__()

## Function: parse_voice_attributes()

Parse voice attributes from voice name using naming convention.

Voice naming convention: [region][gender]_[name]
- First character: region (A=American, B=British, J=Japanese, Z=Chinese, S=Spanish, F=French, H=Hindi, I=Italian, P=Portuguese)
- Second character: gender (f=female, m=male)

Examples:
- af_heart → American Female
- am_adam → American Male
- bf_alice → British Female
- bm_daniel → British Male

## Function: create_voice_metadata()

Create voice metadata from voice name

## Function: generate_cache_key()

Generate cache key for audio segments

## Function: validate_tts_request()

Validate TTS request and return list of errors

