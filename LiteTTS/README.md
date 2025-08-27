# Kokoro TTS Core Engine

Core TTS engine implementation with ONNX runtime, voice management, and audio processing.

## Architecture

The Kokoro TTS engine is organized into modular components:
- **Audio Processing** - Audio format conversion, streaming, and effects
- **Voice Management** - Voice loading, caching, and blending
- **Text Processing** - NLP pipeline with pronunciation fixes
- **TTS Engine** - Core synthesis with ONNX runtime
- **Configuration** - Centralized configuration management
- **Models** - Data structures and model definitions

## Directory Contents

- **__init__.py** - Package initialization
- **__pycache__/** - Project directory
- **api/** - API components
- **audio/** - Audio processing components
- **benchmark.py** - Python module
- **benchmarks/** - Benchmark code
- **cache/** - Cache storage
- **config/** - Configuration files
- **config.py** - Configuration management
- **debug_kokoro_onnx.py** - Python module
- **debug_voice_format.py** - Python module
- **downloader.py** - Python module
- **error_handling.py** - Python module
- **exceptions.py** - Custom exceptions
- **logging_config.py** - Logging configuration
- **metrics/** - Project directory
- **models/** - Data models and ML models
- **models.py** - Data models and structures
- **monitoring/** - Monitoring and metrics
- **nlp/** - Natural language processing
- **optimization/** - Project directory
- **patches.py** - Python module
- **performance/** - Performance optimization
- **run_tests.py** - Python module
- **kokoro/scripts/** - Utility scripts
- **ssml/** - Project directory
- **start_server.py** - Python module
- **startup.py** - Application startup logic
- **tests/** - Test suite
- **text/** - Project directory
- **tts/** - Text-to-speech engine
- **validation.py** - Input validation
- **voice/** - Voice management system
- **voices/** - Project directory

## Navigation

- [← Back to Main README](../README.md)
- [📚 Documentation](../docs/README.md)
- [🎵 Voice Samples](../static/samples/README.md)
- [💡 Examples](../static/examples/README.md)
