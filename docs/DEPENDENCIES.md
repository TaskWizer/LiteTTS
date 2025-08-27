# Dependencies & Installation Guide

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

Complete guide for installing and managing dependencies for the Kokoro ONNX TTS API.

## Core Dependencies

### Required Dependencies (automatically installed)

```
fastapi>=0.95.0          # Modern web framework for APIs
uvicorn>=0.21.0          # Lightning-fast ASGI server
soundfile>=0.12.0        # Audio file I/O operations
numpy>=1.24.0            # Numerical computing for audio
kokoro-onnx>=0.4.9       # Core TTS engine
onnxruntime>=1.22.1      # ONNX model inference runtime
pydantic>=2.0.0          # Data validation and settings
psutil>=5.9.0            # System and process utilities
requests>=2.25.0         # HTTP library for downloads
jinja2>=3.1.6            # Template engine for web interface
mutagen>=1.47.0          # Audio metadata handling
```

## Optional Dependencies

### Perth Watermarking (✅ Installed)

```bash
uv add resemble-perth>=1.0.0  # Already installed in this system
```

- **Purpose**: Responsible AI compliance and content authenticity
- **Benefits**: Automatic watermarking, deepfake detection support
- **Status**: ✅ Installed and functional with DummyWatermarker
- **Fallback**: Mock watermarkers available if not installed

### GPU Acceleration (Optional)

```bash
# For NVIDIA GPUs with CUDA
uv add onnxruntime-gpu>=1.22.1

# For Apple Silicon Macs
uv add onnxruntime-silicon>=1.22.1
```

## Platform-Specific Installation

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip
sudo apt install libsndfile1 libsndfile1-dev  # For soundfile

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### macOS

```bash
# Install via Homebrew
brew install python@3.12
brew install libsndfile  # For soundfile

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
# Install Python 3.12 from python.org
# Install uv package manager
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Troubleshooting Common Issues

### Issue: `soundfile` installation fails

```bash
# Ubuntu/Debian
sudo apt install libsndfile1-dev

# macOS
brew install libsndfile

# Windows: Usually works out of the box
```

### Issue: `onnxruntime` performance issues

```bash
# Check if GPU version is installed when not needed
uv remove onnxruntime-gpu
uv add onnxruntime

# Or install CPU-optimized version
uv add onnxruntime>=1.22.1
```

### Issue: Perth watermarking not available

```bash
# Install Perth library
uv add resemble-perth

# Or disable watermarking for testing
export KOKORO_WATERMARKING_ENABLED=false
```

### Issue: Port 8354 already in use

```bash
# Use different port
python app.py --port 8355

# Or set environment variable
export PORT=8355
python app.py
```

## Development Dependencies

### For contributors and developers

```bash
# Install development dependencies
uv add --dev pytest>=7.0.0
uv add --dev pytest-asyncio>=0.21.0
uv add --dev httpx>=0.24.0
uv add --dev black>=23.0.0
uv add --dev ruff>=0.1.0

# Or install all at once
uv add -e ".[dev]"
```

## Installation Methods

### Method 1: Using uv (Recommended)

```bash
# Clone repository
git clone https://github.com/TaskWizer/LiteTTS.git
cd LiteTTS

# Install with uv (automatically manages virtual environment)
uv run python app.py
```

### Method 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/TaskWizer/LiteTTS.git
cd LiteTTS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Optional: Install Perth watermarking for production
uv add resemble-perth

# Run application
python app.py
```

### Method 3: Docker Installation

```bash
# Using Docker (all dependencies included)
docker run -p 8354:8354 kokoro-onnx-tts-api
```

## Dependency Management Best Practices

### Version Pinning

- **Production**: Use exact versions in `requirements.txt`
- **Development**: Use version ranges for flexibility
- **Security**: Regularly update dependencies for security patches

### Virtual Environments

- **Always use virtual environments** to avoid dependency conflicts
- **uv automatically manages** virtual environments
- **Manual setup** available for custom configurations

### Dependency Updates

```bash
# Check for outdated packages
uv pip list --outdated

# Update specific package
uv add --upgrade package-name

# Update all packages (use with caution)
uv pip install --upgrade -r requirements.txt
```

## System Requirements

### Minimum Requirements

- **Python**: 3.10+ (3.12+ recommended)
- **Memory**: 4GB RAM
- **Storage**: 2GB free space
- **CPU**: Modern multi-core processor

### Recommended Requirements

- **Python**: 3.12+
- **Memory**: 8GB+ RAM
- **Storage**: 5GB+ free space
- **CPU**: 8+ cores
- **GPU**: Optional for acceleration

## Support

For dependency-related issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Review [System Requirements](README.md#prerequisites)
3. Open an issue on [GitHub](https://github.com/TaskWizer/LiteTTS/issues)
