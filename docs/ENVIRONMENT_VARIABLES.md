# Environment Variables Reference

**Date:** 2026-08-22

LiteTTS supports extensive environment variable configuration for Docker deployments, performance tuning, and production deployments.

---

## Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PORT` | int | 8354 | Server port |
| `API_HOST` | string | 0.0.0.0 | Server bind address |
| `WORKERS` | int | 1 | Number of worker processes |
| `ENVIRONMENT` | string | production | Runtime environment |
| `MAX_PORT_ATTEMPTS` | int | 10 | Max attempts to find available port |

---

## Model Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KOKORO_MODEL_NAME` | string | (from config) | Model name to load |
| `KOKORO_MODEL_VARIANT` | string | (from config) | Model variant (af, bf, etc.) |
| `KOKORO_MODEL_AUTO_DISCOVERY` | bool | true | Auto-discover model files |
| `KOKORO_CACHE_MODELS` | bool | true | Cache downloaded models |

---

## Voice Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KOKORO_DEFAULT_VOICE` | string | af_heart | Default voice |
| `KOKORO_VOICE_AUTO_DISCOVERY` | bool | true | Auto-discover voices |
| `DOWNLOAD_ALL_VOICES` | bool | false | Download all voices on startup |
| `KOKORO_CACHE_DISCOVERY` | bool | true | Cache voice discovery |
| `KOKORO_DISCOVERY_CACHE_HOURS` | int | 24 | Voice cache TTL in hours |

---

## Audio Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KOKORO_DEFAULT_FORMAT` | string | mp3 | Default audio format |
| `KOKORO_SAMPLE_RATE` | int | 24000 | Audio sample rate |

---

## Performance Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `KOKORO_HOT_RELOAD` | bool | false | Enable config hot reload |
| `CACHE_ENABLED` | bool | true | Enable caching |
| `KOKORO_PRELOAD_MODELS` | bool | true | Preload models on startup |
| `KOKORO_CHUNK_SIZE` | int | (from config) | Text chunk size |
| `MAX_TEXT_LENGTH` | int | (from config) | Maximum text length |
| `KOKORO_TIMEOUT` | int | 300 | Request timeout in seconds |

---

## Repository Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LITETTS_HF_REPO` | string | (from config) | HuggingFace repository |
| `LITETTS_BASE_URL` | string | (from config) | Base URL for downloads |

---

## Threading (set by Environment Bridge)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OMP_NUM_THREADS` | int | (auto) | OpenMP thread count |
| `MKL_NUM_THREADS` | int | (auto) | Intel MKL thread count |
| `OPENBLAS_NUM_THREADS` | int | (auto) | OpenBLAS thread count |
| `VECLIB_MAXIMUM_THREADS` | int | (auto) | macOS Accelerate thread count |

---

## ONNX Runtime Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ORT_DISABLE_ALL_OPTIMIZATION` | bool | false | Disable all ONNX optimizations |
| `ORT_ENABLE_CPU_FP16_OPS` | bool | true | Enable CPU FP16 operations |
| `ORT_GRAPH_OPTIMIZATION_LEVEL` | string | all | Graph optimization level |
| `ORT_EXECUTION_MODE` | string | parallel | Execution mode (parallel/sequential) |
| `ORT_ENABLE_MEM_PATTERN` | bool | true | Enable memory pattern optimization |
| `ORT_ENABLE_CPU_MEM_ARENA` | bool | true | Enable CPU memory arena |
| `ORT_ENABLE_MEM_REUSE` | bool | true | Enable memory reuse |

---

## Memory Allocation (Linux/macOS)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MALLOC_ARENA_MAX` | int | 4 | Maximum memory arenas |
| `MALLOC_MMAP_THRESHOLD_` | int | 131072 | mmap threshold |
| `MALLOC_TRIM_THRESHOLD_` | int | 131072 | trim threshold |
| `MALLOC_TOP_PAD_` | int | 131072 | top padding |
| `MALLOC_MMAP_MAX_` | int | 65536 | maximum mmap count |

---

## Performance Optimization

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_PERFORMANCE_OPTIMIZATION` | bool | true | Enable performance optimizations |
| `MAX_MEMORY_MB` | int | 4096 | Memory limit in MB |
| `TARGET_RTF` | float | 0.25 | Target Real-Time Factor |

---

## Dynamic CPU Allocation

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DYNAMIC_CPU_ALLOCATION_ENABLED` | bool | true | Enable dynamic CPU allocation |
| `CPU_TARGET` | float | 75.0 | Target CPU usage percentage |
| `AGGRESSIVE_MODE` | bool | true | Enable aggressive optimization |
| `THERMAL_PROTECTION` | bool | true | Enable thermal throttling protection |
| `ONNX_INTEGRATION` | bool | true | Enable ONNX integration |
| `UPDATE_ENVIRONMENT` | bool | true | Update environment variables |

---

## Voice Cloning

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `VOICE_CLONING_ENHANCED_MODE` | bool | true | Enable enhanced voice cloning mode |
| `VOICE_CLONING_MAX_DURATION` | int | (varies) | Maximum audio duration for cloning |

---

## Whisper (Transcription)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WHISPER_MODEL` | string | base | Whisper model size |
| `WHISPER_CPU_THREADS` | int | (auto) | Whisper CPU thread count |

---

## Python Runtime

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PYTHONIOENCODING` | string | utf-8 | Python stdout/stderr encoding |
| `ONNX_DISABLE_SPARSE_TENSORS` | string | 1 | Disable sparse tensor optimization |

---

## Examples

### Docker Deployment

```bash
# Minimal Docker deployment
docker run -e PORT=8354 -e KOKORO_DEFAULT_VOICE=af_heart ...

# Production with performance tuning
docker run \
  -e ENVIRONMENT=production \
  -e CACHE_ENABLED=true \
  -e KOKORO_PRELOAD_MODELS=true \
  -e MAX_MEMORY_MB=8192 \
  -e TARGET_RTF=0.25 \
  -e THERMAL_PROTECTION=true \
  -e OMP_NUM_THREADS=8 \
  ...

# Development
docker run -e ENVIRONMENT=development -e KOKORO_HOT_RELOAD=true ...
```

### Docker Compose

```yaml
services:
  litetts:
    environment:
      - PORT=8354
      - ENVIRONMENT=production
      - KOKORO_DEFAULT_VOICE=af_heart
      - CACHE_ENABLED=true
      - MAX_MEMORY_MB=4096
      - TARGET_RTF=0.25
      - THERMAL_PROTECTION=true
    deploy:
      resources:
        limits:
          memory: 4G
```

---

## Configuration Precedence

Environment variables override settings.json but are overridden by command-line arguments.

```
Command-line args > Environment variables > config/override.json > config/settings.json
```
