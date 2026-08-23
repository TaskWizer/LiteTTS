# Migration Guide

This guide helps users migrate between LiteTTS versions.

---

## Upgrading to v1.1.0

### Python Version Requirement

LiteTTS now requires **Python 3.10+** (previously 3.8+). If you're using Python 3.8 or 3.9, upgrade before running LiteTTS.

```bash
python --version  # Verify you have Python 3.10+
```

### Configuration Changes

#### Voice Cache Settings

The voice caching system has been improved. If you have custom cache settings:

**Before (legacy format):**
```json
{
  "voice_cache_size": 10
}
```

**After (new format):**
```json
{
  "voice": {
    "cache_size": 10,
    "use_combined_file": false
  }
}
```

#### ONNX Runtime Providers

The ONNX provider configuration now uses a list format:

**Before:**
```json
{
  "onnx_provider": "CPU"
}
```

**After:**
```json
{
  "onnx_providers": ["CPU"]
}
```

### API Changes

#### Text Input Validation

Empty text strings now raise a `ValueError` with a descriptive message instead of returning silent audio. If you have error handling for empty text:

**Before:**
```python
# Empty text would return silent audio
result = synthesizer.synthesize("")
```

**After:**
```python
# Empty text now raises ValueError
try:
    result = synthesizer.synthesize("")
except ValueError as e:
    print(f"Invalid input: {e}")
```

### File Location Changes

| Component | Old Location | New Location |
|-----------|--------------|--------------|
| Voice files | `voices/` | `LiteTTS/voices/` |
| Model files | `models/` | `LiteTTS/models/` |
| Cache | `cache/` | `cache/` (unchanged) |

---

## Upgrading to v1.0.0

### Environment Variable Prefix

All environment variables now use the `LitetTS_` prefix consistently:

| Old | New |
|-----|-----|
| `PORT` | `LitetTS_PORT` |
| `HOST` | `LitetTS_HOST` |
| `LOG_LEVEL` | `LitetTS_LOG_LEVEL` |

### Removed Deprecated Features

- `LiteTTS_old_cache_path` - Removed, use `LitetTS_CACHE_DIR`
- `enable_debug_mode` flag - Removed, use `LitetTS_LOG_LEVEL=DEBUG`

### Command-Line Arguments

Some CLI arguments have been renamed for consistency:

| Old | New |
|-----|-----|
| `--dev` | `--reload` |
| `--voice-dir` | `--voices-path` |
| `--model-dir` | `--models-path` |

---

## Voice File Migration

If you have custom voice files from an older installation:

1. **Backup your voice files:**
   ```bash
   cp -r LiteTTS/voices/*.bin /backup/voices/
   ```

2. **Update voice metadata:**
   ```bash
   # Regenerate combined voices file
   curl -X POST http://localhost:8354/v1/voices/reload
   ```

3. **Verify voice loading:**
   ```bash
   curl http://localhost:8354/v1/voices
   ```

---

## Troubleshooting

### Voice Not Found Errors

If you see `VoiceNotFoundError` after upgrading:

1. Check voice file exists:
   ```bash
   ls LiteTTS/voices/*.bin | head
   ```

2. Reload voices API:
   ```bash
   curl -X POST http://localhost:8354/v1/voices/reload
   ```

3. Check combined_voices.npz is valid:
   ```bash
   python -c "import numpy as np; data = np.load('LiteTTS/voices/combined_voices.npz'); print(list(data.keys())[:5])"
   ```

### Import Errors

If you encounter `ModuleNotFoundError: No module named 'kokoro_onnx'`:

1. Reinstall dependencies:
   ```bash
   uv pip install --force-reinstall kokoro-onnx
   ```

2. Or use the automatic setup:
   ```bash
   python app.py --setup
   ```

### ONNX Inference Errors

If ONNX inference fails after upgrading:

1. Verify model files are complete:
   ```bash
   ls -la LiteTTS/models/
   ```

2. Check ONNX provider availability:
   ```bash
   python -c "import onnxruntime as ort; print(ort.get_available_providers())"
   ```

3. Fall back to CPU if CUDA has issues:
   ```bash
   export LitetTS_ONNX_PROVIDERS='["CPU"]'
   ```

---

## Getting Help

If you encounter migration issues not covered here:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/TaskWizer/LiteTTS/issues)
3. File a [new issue](https://github.com/TaskWizer/LiteTTS/issues/new) with:
   - LiteTTS version (`pip show litetts`)
   - Python version (`python --version`)
   - Error message and stack trace
   - Steps to reproduce
