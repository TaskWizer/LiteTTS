# 🚀 Quick Start Commands - LiteTTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../FEATURES.md) | [Configuration](../CONFIGURATION.md) | [Performance](../PERFORMANCE.md) | [Monitoring](../MONITORING.md) | [Testing](../TESTING.md) | [Troubleshooting](../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../DEPENDENCIES.md) | [Quick Start](QUICK_START_COMMANDS.md) | [Docker Deployment](DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../api/API_REFERENCE.md) | [Development](../development/README.md) | [Voice System](../voices/README.md) | [Watermarking](../WATERMARKING.md)

**Project:** [Changelog](../CHANGELOG.md) | [Roadmap](../ROADMAP.md) | [Contributing](../CONTRIBUTIONS.md) | [Beta Features](../BETA_FEATURES.md)

---

**Get up and running with the fastest TTS API in under 2 minutes!**

## ⚡ Ultra-Quick Start (30 seconds)

```bash
# Clone and run in one go
git clone https://github.com/TaskWizer/LiteTTS.git && \
cd kokoro_onnx_tts_api && \
python app.py
```

**That's it!** 🎉 Your TTS API is now running at `http://localhost:8354`

## 📋 Step-by-Step Installation

### 1. **Clone the Repository**
```bash
git clone https://github.com/TaskWizer/LiteTTS.git
cd kokoro_onnx_tts_api
```

### 2. **Start the Server**
```bash
# Direct Python execution (recommended)
python app.py

# Alternative: Zero-configuration with uv
uv run python app.py
```

### 3. **Verify Installation**
```bash
# Test the API
curl http://localhost:8354/health
```

## 🎯 First TTS Request

### Basic Text-to-Speech
```bash
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3
```

### Play the Result
```bash
# Linux/WSL
mpv hello.mp3

# macOS
afplay hello.mp3

# Windows
start hello.mp3
```

## ⚙️ Server Configuration

### Default Configuration
The server starts with these defaults:
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8354` (TTS in English Gematria)
- **Workers**: `1` (optimal for TTS)
- **Format**: `mp3`
- **Voice**: `af_heart`

### Custom Configuration
```bash
# Custom port
python app.py --port 8080

# Custom host (localhost only)
python app.py --host 127.0.0.1

# Development mode with auto-reload
python app.py --reload

# Production mode with multiple workers
python app.py --workers 4

# Combined options
python app.py --reload --host 0.0.0.0 --port 8080

# Alternative: uvicorn with explicit configuration
uv run uvicorn app:app --port 8354 --reload
```

## 🔧 Development Setup

### Hot Reload Development
```bash
# Automatically restart on code changes (recommended)
python app.py --reload

# Alternative: uvicorn with reload
uv run uvicorn app:app --reload --port 8354
```

### Debug Mode
```bash
# Enable debug logging
python app.py --log-level debug

# Alternative: uvicorn with debug
uv run uvicorn app:app --log-level debug --port 8354
```

### Custom Configuration File
```bash
# Use custom config (optional)
cp config.json my_config.json
# Edit my_config.json as needed
# The system works without any config file!
```

## 🧪 Testing Commands

### Health Check
```bash
curl http://localhost:8354/health
```

### List Available Voices
```bash
curl http://localhost:8354/v1/voices | jq
```

### Performance Test
```bash
# Test response time
time curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Speed test", "voice": "af_heart"}' \
  --output speed_test.mp3
```

### Cache Performance Test
```bash
# First request (uncached)
time curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Cache test", "voice": "af_heart"}' \
  --output cache_test1.mp3

# Second request (cached - should be ~29ms!)
time curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Cache test", "voice": "af_heart"}' \
  --output cache_test2.mp3
```

## 🌐 API Endpoints

### Core Endpoints
```bash
# Root endpoint
curl http://localhost:8354/

# Health check
curl http://localhost:8354/health

# Voice list
curl http://localhost:8354/v1/voices

# Text-to-speech
curl -X POST http://localhost:8354/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Your text here", "voice": "af_heart"}'
```

### Dashboard
```bash
# Open analytics dashboard
open http://localhost:8354/dashboard
```

## 🐳 Docker Quick Start

### Using Docker Compose
```bash
# Start with Docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Manual Docker
```bash
# Build image
docker build -t kokoro-tts .

# Run container
docker run -p 8354:8354 kokoro-tts
```

## 🔌 Integration Examples

### OpenWebUI Integration
```bash
# OpenWebUI Settings → Audio:
# TTS Engine: OpenAI
# API Base URL: http://YOUR_IP:8354/v1
# TTS Model: kokoro
# TTS Voice: af_heart
```

### Python Integration
```python
import requests

response = requests.post(
    "http://localhost:8354/v1/audio/speech",
    json={
        "input": "Hello from Python!",
        "voice": "af_heart",
        "response_format": "mp3"
    }
)

with open("python_tts.mp3", "wb") as f:
    f.write(response.content)
```

### JavaScript Integration
```javascript
const response = await fetch('http://localhost:8354/v1/audio/speech', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: 'Hello from JavaScript!',
    voice: 'af_heart',
    response_format: 'mp3'
  })
});

const audioBlob = await response.blob();
const audioUrl = URL.createObjectURL(audioBlob);
const audio = new Audio(audioUrl);
audio.play();
```

## 🎛️ Advanced Features

### SSML Support
```bash
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "<speak><background type=\"rain\" volume=\"20\">It'\''s raining outside</background></speak>", "voice": "af_bella"}' \
  --output rain.mp3
```

### Speed Control
```bash
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "This is fast speech", "voice": "af_heart", "speed": 1.5}' \
  --output fast.mp3
```

### Multiple Formats
```bash
# WAV format
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "WAV format test", "voice": "af_heart", "response_format": "wav"}' \
  --output test.wav

# FLAC format
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "FLAC format test", "voice": "af_heart", "response_format": "flac"}' \
  --output test.flac
```

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8354
lsof -i :8354

# Use different port
python app.py --port 8355

# Alternative: uvicorn with different port
uv run uvicorn app:app --port 8355
```

#### Permission Denied
```bash
# Install uv if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or use pip
pip install uv
```

#### Slow First Request
```bash
# First request downloads models (~100MB)
# Subsequent requests are instant!
# Check download progress in logs
```

### Performance Optimization
```bash
# Preload models for faster startup
export KOKORO_PRELOAD_MODELS=true
python app.py

# Enable intelligent caching
export KOKORO_CACHE_ENABLED=true
python app.py

# Alternative: with uvicorn
export KOKORO_PRELOAD_MODELS=true
uv run uvicorn app:app --port 8354
```

## 📊 Performance Metrics

### Expected Performance
- **Startup Time**: ~6 seconds (with model download)
- **First Request**: ~300ms (model loading)
- **Cached Requests**: ~29ms (99x speedup!)
- **RTF (Real-Time Factor)**: ~0.15 (6.7x faster than real-time)
- **Memory Usage**: ~150MB (after initialization)

### Benchmarking
```bash
# Run performance benchmark
python kokoro/benchmarks/quick_benchmark.py

# Detailed performance analysis
python kokoro/benchmarks/performance_analysis.py
```

## 🔗 Next Steps

1. **Explore Voices**: [Voice Showcase](voices/README.md)
2. **OpenWebUI Setup**: [Integration Guide](usage/OPENWEBUI-INTEGRATION.md)
3. **Advanced Features**: [SSML Guide](usage/SSML-GUIDE.md)
4. **Production Deployment**: [Docker Guide](usage/DOCKER-DEPLOYMENT.md)
5. **API Reference**: [Complete API Docs](FEATURES.md)

---

**🎉 Congratulations!** You now have the fastest TTS API running. Enjoy near-instant voice synthesis! 🚀
