[🏠 Home](../README.md) | [📖 Documentation](README.md) | [🚀 Quick Start](usage/QUICK_START_COMMANDS.md) | [🔧 Configuration](CONFIGURATION.md) | [📊 Performance](PERFORMANCE.md) | [🐛 Troubleshooting](TROUBLESHOOTING.md)

# Configuration Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

This document provides comprehensive configuration options for LiteTTS. The system uses a flexible configuration hierarchy that allows for easy customization while maintaining sensible defaults.

## Configuration Hierarchy

Configuration precedence (highest to lowest priority):
1. **Command-line arguments** (`--port`, `--host`, `--workers`)
2. **Environment variables** (`PORT`, `API_HOST`, `WORKERS`)
3. **override.json** (user overrides)
4. **./config/settings.json** (base defaults - port 8354)
5. **Default values** (Port 8354 represents "TTS" in English Gematria - an arbitrary, unused port)

## Default Configuration

The API uses `./config/settings.json` for default settings. This file contains all the standard configuration options and should not be modified directly.

## Custom Configuration Override

For user-specific settings, create an `override.json` file in the project root. This file will override any settings from the default configuration while preserving unspecified defaults.

### Example `override.json`

```json
{
  "server": {
    "port": 9000,
    "host": "127.0.0.1"
  },
  "voice": {
    "default_voice": "am_adam",
    "download_all_on_startup": false
  },
  "performance": {
    "cache_enabled": false,
    "chunk_size": 200
  }
}
```

## Configuration Sections

### Server Configuration

**Change Default Port:**
```json
{
  "server": {
    "port": 9000,
    "host": "0.0.0.0",
    "workers": 1,
    "environment": "production"
  }
}
```

### Voice Settings

**Customize Voice Settings:**
```json
{
  "voice": {
    "default_voice": "af_bella",
    "download_all_on_startup": false,
    "default_voices": ["af_heart", "am_adam", "af_bella"],
    "auto_discovery": true,
    "preload_default_voices": true
  }
}
```

### Performance Tuning

**Performance Optimization:**
```json
{
  "performance": {
    "cache_enabled": true,
    "chunk_size": 150,
    "max_text_length": 10000,
    "timeout_seconds": 60,
    "preload_models": true,
    "max_retry_attempts": 3
  }
}
```

### Audio Format Settings

**Audio Configuration:**
```json
{
  "audio": {
    "default_format": "wav",
    "default_speed": 1.2,
    "sample_rate": 22050,
    "mp3_bitrate": 128,
    "streaming_chunk_duration": 0.8,
    "supported_formats": ["mp3", "wav", "flac", "opus"]
  }
}
```

### Text Processing Features

**Advanced Text Processing:**
```json
{
  "text_processing": {
    "enabled": true,
    "natural_speech": true,
    "pronunciation_fixes": true,
    "expand_contractions": false,
    "preserve_word_count": true
  },
  "symbol_processing": {
    "enabled": true,
    "fix_asterisk_pronunciation": true,
    "normalize_quotation_marks": true,
    "natural_ampersand_pronunciation": true
  },
  "pronunciation_dictionary": {
    "enabled": true,
    "use_context_awareness": true,
    "ticker_symbol_processing": true,
    "proper_name_pronunciation": true
  }
}
```

### Caching Configuration

**Cache Settings:**
```json
{
  "caching": {
    "enabled": true,
    "components": {
      "tts_synthesis": true,
      "voice_embeddings": true,
      "phonemization": true,
      "audio_processing": true
    },
    "cache_sizes": {
      "max_synthesis_cache": 200,
      "max_voice_cache": 100,
      "max_phoneme_cache": 500
    },
    "testing_mode": false
  }
}
```

### Beta Features

**Experimental Features:**
```json
{
  "beta_features": {
    "enabled": true,
    "time_stretching_optimization": {
      "enabled": true,
      "generation_speed_boost": 30,
      "correction_quality": "medium"
    },
    "voice_modulation": {
      "enabled": true,
      "parenthetical_whisper": true,
      "dynamic_emotion": true
    }
  }
}
```

### Monitoring and Logging

**System Monitoring:**
```json
{
  "monitoring": {
    "enabled": true,
    "log_level": "INFO",
    "performance_tracking": true,
    "error_tracking": true,
    "system_metrics": true,
    "log_rotation": {
      "max_size": "10MB",
      "backup_count": 5
    }
  }
}
```

## Getting Started with Override Configuration

1. **Copy the example file:**
   ```bash
   cp override.json.example override.json
   ```

2. **Edit `override.json`** to include only the settings you want to change

3. **Remove the example comments** (`_comment` and `_instructions` sections)

4. **Restart the server** to apply your override settings

## Command-Line Configuration

You can also use command-line arguments to override configuration:

```bash
# Override server settings
python app.py --host 0.0.0.0 --port 8354 --workers 1

# Development mode with reload
python app.py --reload

# Custom configuration file
python kokoro/start_server.py --config custom_config.json
```

## Environment Variables

Set environment variables to override configuration:

```bash
export PORT=9000
export API_HOST=127.0.0.1
export WORKERS=2
python app.py
```

## Configuration Notes

- `override.json` is automatically ignored by git
- Only specify the settings you want to change
- Nested objects are merged, not replaced entirely
- Invalid configurations will fall back to defaults with warnings
- See `override.json.example` for a comprehensive example
- Configuration changes require a server restart to take effect

## Troubleshooting Configuration

### Common Issues

1. **Port Already in Use**: Change the port in your override.json or use `--port` flag
2. **Invalid JSON**: Validate your override.json syntax
3. **Missing Voices**: Ensure voice names match available voices from `/v1/voices`
4. **Performance Issues**: Adjust cache settings and chunk sizes

### Validation

Test your configuration with:
```bash
# Check current configuration
curl http://localhost:8354/health

# Validate voice settings
curl http://localhost:8354/v1/voices

# Test performance
curl http://localhost:8354/performance/stats
```

For more detailed troubleshooting, see the [Troubleshooting Guide](troubleshooting.md).
