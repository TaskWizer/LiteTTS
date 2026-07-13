# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LiteTTS is a high-performance, lightweight Text-to-Speech API built on the Kokoro ONNX model. It provides an OpenAI-compatible TTS API with 54+ voices, multi-language support, caching, and production-ready features.

**Default port:** 8354

## Common Commands

```bash
# Run the server (recommended)
uv run python app.py

# Or with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8354

# Development with hot reload
python app.py --reload

# Run tests
pytest LiteTTS/tests/ -v
pytest LiteTTS/tests/ -v -k "test_name"  # Run specific test

# Lint and format
make lint      # flake8, pylint
make format   # black, isort
make check-format

# Type checking
make type-check

# Security checks
make security

# All quality checks
make all
```

## Architecture

```
Request → app.py (LiteTTSApplication)
        → LiteTTS/api/router.py (TTSAPIRouter)
        → LiteTTS/tts/synthesizer.py (TTSSynthesizer)
        → LiteTTS/tts/engine.py (KokoroTTSEngine)
        → ONNX Runtime → Audio Output
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `LiteTTSApplication` | `app.py` | Main FastAPI application factory |
| `TTSAPIRouter` | `LiteTTS/api/router.py` | OpenAI-compatible REST endpoints |
| `TTSSynthesizer` | `LiteTTS/tts/synthesizer.py` | Orchestrates TTS pipeline |
| `KokoroTTSEngine` | `LiteTTS/tts/engine.py` | Core ONNX-based TTS inference |
| `VoiceManager` | `LiteTTS/voice/manager.py` | Voice loading and management |
| `EnhancedCacheManager` | `LiteTTS/cache/manager.py` | Multi-layer caching |
| `UnifiedTextProcessor` | `LiteTTS/nlp/unified_text_processor.py` | Text normalization |

### Core Package Structure

- `LiteTTS/api/` - FastAPI routers and request handling
- `LiteTTS/tts/` - TTS engine and synthesis
- `LiteTTS/voice/` - Voice management and discovery
- `LiteTTS/text/` - Text processing and phonemization
- `LiteTTS/nlp/` - Advanced NLP (normalization, contractions)
- `LiteTTS/ssml/` - SSML parsing and processing
- `LiteTTS/cache/` - Multi-layer caching system
- `LiteTTS/performance/` - CPU, memory, SIMD optimizations
- `LiteTTS/backends/` - Whisper fallback for transcription
- `LiteTTS/audio/` - Audio processing utilities

## Configuration

Configuration follows precedence (highest to lowest):
1. Command-line arguments (`--port`, `--host`)
2. Environment variables (`PORT`, `API_HOST`)
3. `config/override.json` (rename from `override.json.example`)
4. `config/settings.json` (base defaults)

Models download automatically from HuggingFace on first run.

## Development Notes

- **Python 3.12+** required
- Uses `uv` as package manager (faster than pip)
- ONNX models stored in `LiteTTS/models/`
- Voices stored in `LiteTTS/voices/`
- Runtime cache in `cache/` directory
- Uses `kokoro-onnx` package for TTS engine
