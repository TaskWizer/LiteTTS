# System Requirements & Compatibility Matrix

**Date:** 2026-08-22

---

## Python Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| Python | 3.12 | 3.12+ | asyncio and type hints required |
| uv | 0.1.0 | Latest | Package manager |

---

## Hardware Requirements

### CPU-Only Inference

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| CPU | 4 cores | 8+ cores | Real-time TTS needs fast CPU |
| RAM | 4 GB | 8+ GB | Model loading + inference |
| Storage | 2 GB | 10+ GB | Models (~1GB) + voices |

### GPU Inference (Optional)

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| GPU | NVIDIA with 4GB VRAM | NVIDIA with 8GB+ VRAM | CUDA 11.8+ required |
| RAM | 8 GB | 16 GB | GPU + system |
| Storage | 2 GB | 10+ GB | Models + cache |

---

## Operating System Support

| OS | Status | Support Level | Notes |
|----|--------|--------------|-------|
| Linux (Ubuntu 20.04+) | ✅ Full | Primary | Best performance |
| Linux (Debian 11+) | ✅ Full | Supported | |
| macOS 12+ (Apple Silicon) | ✅ Full | Supported | May need Rosetta 2 |
| macOS 12+ (Intel) | ✅ Full | Supported | |
| Windows 10/11 | ✅ Full | Supported | WSL2 recommended |
| Docker | ✅ Full | Supported | CPU/GPU variants |

---

## Browser Support (Web Interface)

| Browser | Version | Status | Notes |
|---------|---------|--------|-------|
| Chrome | 90+ | ✅ Full | Primary testing target |
| Firefox | 90+ | ✅ Full | |
| Safari | 15+ | ✅ Full | |
| Edge | 90+ | ✅ Full | Chromium-based |

---

## Docker Support

| Docker Version | Status | Notes |
|---------------|--------|-------|
| 20.10+ | ✅ Full | |
| 24.0+ | ✅ Full | |
| Docker Compose | 2.0+ | ✅ Full |

---

## API Clients

| Client | Status | Library | Notes |
|--------|--------|---------|-------|
| cURL | ✅ Full | - | Command line testing |
| Python | ✅ Full | `httpx`, `requests` | SDK examples |
| JavaScript/Node | ✅ Full | `fetch`, `axios` | |
| Go | ✅ Full | - | |
| Rust | ✅ Full | - | |
| OpenAI SDK | ✅ Full | `openai` | OpenAI-compatible API |

---

## Dependency Versions

### Core Dependencies

| Package | Minimum | Recommended | Notes |
|---------|---------|-------------|-------|
| fastapi | 0.100+ | Latest | |
| uvicorn | 0.20+ | Latest | ASGI server |
| pydantic | 2.0+ | Latest | Validation |
| numpy | 1.24+ | Latest | Numerical operations |
| soundfile | 0.12+ | Latest | Audio I/O |

### ML/TTS Dependencies

| Package | Minimum | Recommended | Notes |
|---------|---------|-------------|-------|
| kokoro-onnx | 0.4.0 | Latest | TTS engine |
| onnxruntime | 1.15+ | Latest | ONNX inference |
| phonemizer-fork | 3.2+ | Latest | Text-to-phonemes |

### Optional Dependencies

| Package | Status | Notes |
|---------|--------|-------|
| faster-whisper | ✅ Available | Transcription fallback |
| torch | ✅ Available | GPU acceleration |
| mutagen | ✅ Available | Audio metadata |

---

## Environment Variables Reference

See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) for full documentation.

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Real-Time Factor (RTF) | < 0.5 | CPU-only |
| Latency (short text) | < 1s | First audio byte |
| Latency (long text) | < 5s | Chunked processing |
| Memory (idle) | < 500 MB | After startup |
| Memory (peak) | < 4 GB | Full inference |

---

## Installation Methods

### 1. Direct Installation

```bash
# Clone repository
git clone https://github.com/TaskWizer/LiteTTS.git
cd LiteTTS

# Install with uv
uv pip install -e .
```

### 2. Docker (CPU)

```bash
docker pull ghcr.io/taskwizer/litetts:cpu-latest
docker run -p 8354:8354 ghcr.io/taskwizer/litetts:cpu-latest
```

### 3. Docker Compose

```yaml
services:
  litetts:
    image: ghcr.io/taskwizer/litetts:cpu-latest
    ports:
      - "8354:8354"
```

---

## Quick Verification

### Check Installation

```bash
python -c "from app import KokoroTTSApplication; print('OK')"
```

### Run Health Check

```bash
curl http://localhost:8354/health
```

Expected response:
```json
{"status": "healthy", "voices": 54}
```
