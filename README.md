# <img src="static/LiteTTS.svg" alt="LiteTTS" width="32" height="32" style="vertical-align: middle; filter: invert(100%)"/> LiteTTS

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![Performance](https://img.shields.io/badge/RTF-0.15-brightgreen.svg)](docs/PERFORMANCE.md)
[![Quality](https://img.shields.io/badge/Quality-Production%20Ready-green.svg)](docs/development/audits/SYSTEM_IMPROVEMENTS_DOCUMENTATION.md)

## ⚠️ **ALPHA SOFTWARE NOTICE**

**LiteTTS is currently in alpha development.** Core TTS synthesis works reliably, but advanced features have known limitations.

### 🚧 Work-in-Progress Features
The following features are under active development and may have bugs or inconsistent behavior:
- **Punctuation handling** - Some punctuation marks may not be processed naturally
- **Contraction pronunciation** - Contractions like "he'd", "she'd" may be mispronounced
- **Prosody control** - Sentence-level intonation and rhythm improvements ongoing
- **Currency processing** - Financial amounts and currency symbols processing
- **Emotional expression** - Voice emotion and style control features
- **Voice fluidity** - Natural speech flow and stress pattern optimization
- **Inflection rules** - Question vs statement intonation patterns

### 📋 User Expectations
- **Expect bugs and breaking changes** during alpha development
- **Core functionality is stable** - basic text-to-speech works reliably
- **Use in production at your own risk** - thorough testing recommended
- **Active development** - regular updates and improvements being made

---

**The fastest, most efficient Text-to-Speech API with near-instant response times** ⚡

*Built on the powerful Kokoro ONNX model - part of the TaskWizer framework*

## 💖 Support This Project

**This TTS API is completely free to use!** If you find it valuable for your projects, consider supporting its development:

**🎯 Goal**: Make enough money working on cool projects so I don't have to work a 9-to-5

- **💝 Sponsor on GitHub**: [Become a sponsor](https://github.com/sponsors/TaskWizer) for recurring support
- **☕ Buy me a coffee**: [One-time donation](https://ko-fi.com/TaskWizer) to fuel development
- **⭐ Star this repo**: Help others discover this project
- **🐛 Report issues**: Help improve the software for everyone
- **👊 Contribute**: Is there a feature you'd like to see? Submit a pull request!

Your support enables continued development of high-quality, open-source AI tools!

## ✨ Key Features

- **⚡ Lightning Fast**: 29ms cached responses, 0.15 RTF (6.7x faster than real-time)
- **🌍 54+ Voices**: Multi-language support with [voice showcase](docs/VOICES.md)
- **🔌 OpenAI Compatible**: Drop-in replacement for OpenAI TTS API
- **🌐 OpenWebUI Compatible**: Works out-of-the-box with OpenWebUI without additional configuration
- **🎛️ Advanced SSML**: Background noise synthesis and voice modulation
- **🔒 Perth Watermarking**: Responsible AI compliance with automatic audio watermarking
- **📊 Production Ready**: Comprehensive monitoring, caching, and error handling
- **🛡️ Security & Compliance**: Built-in ethical AI features and content authenticity verification
- **🐳 Easy Deployment**: Docker support with automatic model downloads

## 📢 Prerequisites

Before getting started, ensure your system meets these requirements:

**Hardware Requirements:**
- **Memory**: 4GB RAM minimum (8GB+ recommended for high concurrency)
- **Storage**: 4GB free space for model, voices, code, and cache
- **CPU**: Modern multi-core processor (ARM64 and x86_64 supported)
- **GPU**: Any CUDA-enabled GPU for optimal performance (optional)
- **Network**: Internet connection for initial model downloads

**Python Environment:**
- **Python 3.12+** (Required for optimal performance and latest features)
  - Python 3.10+ minimum supported, but 3.12+ recommended for production
  - Includes improved error handling and performance optimizations
- **uv 0.8.11+** (Recommended package manager)
  - Ultra-fast Python package installer and resolver with 
  - Automatic virtual environment management
  - See [Installation Guide](https://docs.astral.sh/uv/getting-started/installation)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/TaskWizer/LiteTTS.git
cd LiteTTS

# Option 1: Direct UV Python execution (recommended)
uv run python app.py

# Option 2: Docker container execution (production-ready with TLS)
cp .env.example .env  # Configure your deployment
docker-compose up -d

# Option 3: Manual installation with virtual environment (best practice)
python -m venv venv
source venv/bin/activate
uv pip install -r requirements.txt
python app.py
```

**That's it!** 🎉 The API will be available at `http://localhost:8354` (default configured port).

## 💪🏻 *Trust me bro*, oneliner
```bash
git clone https://github.com/TaskWizer/LiteTTS.git && cd LiteTTS && uv run python app.py
```

## 🚀 Getting Started Guides

**Detailed setup and usage guides:**

- **[Quick Start Commands](docs/usage/QUICK_START_COMMANDS.md)** - Detailed setup and installation guide
- **[Dependencies & Installation](docs/DEPENDENCIES.md)** - Complete dependency management and troubleshooting
- **[OpenWebUI Integration](docs/usage/OPENWEBUI-INTEGRATION.md)** - Complete OpenWebUI setup tutorial
- **[Docker Deployment](docs/usage/DOCKER-DEPLOYMENT.md)** - Containerized deployment guide

## 📚 Documentation

**Complete guides and references for setup, usage, and advanced features:**

### 📖 Usage & API
- **[API Documentation](docs/FEATURES.md)** - Complete endpoint reference and examples
- **[Voice Showcase](docs/VOICES.md)** - Browse all 54+ voices with audio samples
- **[SSML Guide](docs/usage/SSML-GUIDE.md)** - Advanced speech synthesis markup

### 🔧 Configuration & Optimization
- **[Configuration Guide](docs/CONFIGURATION.md)** - Complete configuration options and customization
- **[Watermarking Guide](docs/WATERMARKING.md)** - Perth watermarking system setup and usage
- **[Monitoring & Observability](docs/MONITORING.md)** - Production monitoring and health checks
- **[Performance Benchmarks](docs/PERFORMANCE.md)** - Optimization tips and metrics
- **[Comprehensive Benchmarking](docs/BENCHMARKING.md)** - Model comparison and performance analysis
- **[System Improvements](docs/development/audits/SYSTEM_IMPROVEMENTS_DOCUMENTATION.md)** - Latest enhancements and features

### 🛠️ Development & Troubleshooting
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Testing Guide](docs/TESTING.md)** - Running tests and validation
- **[Contributing Guide](docs/CONTRIBUTIONS.md)** - How to contribute to the project

### 📁 Project Structure
The project follows a clean, organized structure for maintainability and scalability:

```
LiteTTS/
├── LiteTTS/                   # Core TTS engine modules
│   ├── tests/                 # Test suite
│   ├── scripts/               # Utility scripts
│   ├── models/                # ONNX model files
│   ├── voices/                # Voice data files
│   ├── cache/                 # Runtime cache
│   └── ...                    # Core modules
├── docs/                      # Documentation
├── static/                    # Static web assets
├── config/                    # Configuration files
├── app.py                     # Main application entry point
├── docker-compose.yml         # Docker orchestration
└── Dockerfile                 # Container definition
```

### 📊 Project Information
- **[Development Roadmap](docs/ROADMAP.md)** - Future features and multi-language expansion plans
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates
- **[Production Guide](docs/development/audits/PRODUCTION_MVP_SUMMARY.md)** - Deployment best practices
- **[License](LICENSE)** - Apache 2.0 License details

---
### 📝 Server Startup Options

**Multiple ways to start the server:**

```bash
# Direct Python execution (recommended)
python app.py --host 0.0.0.0 --port 8354        # Override host and port
python app.py --reload --workers 1              # Development with specific workers

# Alternative startup methods
python -m LiteTTS.start_server                   # Module execution
uv run uvicorn app:app --port 8354              # Direct uvicorn (requires explicit port)
```
**Note** You can also modify the core `./config/settings.json` file directly, but it's not recommended as it will be overwritten on updates. Instead, use the [`override.json` method](docs/CONFIGURATION.md) to customize settings.

### 🔧 Configuration Hierarchy

Configuration precedence (highest to lowest priority):
1. **Command-line arguments** (`--port`, `--host`, `--workers`)
2. **Environment variables** (`PORT`, `API_HOST`, `WORKERS`)
3. **./config/override.json** (rename override.json.example to override.json for custom settings)
4. **./config/settings.json** (base defaults - port 8354)
5. **Default values** (Port 8354 represents "TTS" in English Gematria (an arbitrary, unused port)

### 🔄 Development Mode

For development with hot reload (detects changes and restarts automatically):
```bash
# Recommended: Direct Python execution with hot reload
python app.py --reload

# Alternative: uvicorn with explicit configuration
uv run uvicorn app:app --reload --host 0.0.0.0 --port 8354 --workers 1
```

*Note: The reload flag enables Hot Module Replacement (HMR) for automatic restarts on code changes.*

**📖 See the complete [Development Documentation](docs/DEVELOPMENT.md)**

### 📚 Advanced Usage

For advanced configuration options, see the [Configuration Guide](docs/CONFIGURATION.md) and [complete documentation](#-documentation).

### ⚡ Instant Test

```bash
# Test with a simple phrase (will be cached for instant future responses)
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3

# Test again - should respond in ~29ms! ⚡ (99x speedup from cache)
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello, world!", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello_cached.mp3 -w "Time: %{time_total}s\n"
```

An optimized model for your system is automatically downloaded on first run.

## 📦 Dependencies & Installation

LiteTTS requires Python 3.12+ and several core dependencies for optimal performance.

**Key Dependencies:**
- **Core**: FastAPI, uvicorn, soundfile, numpy, kokoro-onnx, onnxruntime
- **Optional**: Perth watermarking (`resemble-perth`), GPU acceleration
- **Development**: pytest, black, ruff for contributors

**📖 See the complete [Dependencies & Installation Guide](docs/DEPENDENCIES.md)**

## 💻 Future Development & Testing Roadmap

This project has an ambitious roadmap for cross-platform testing, performance optimization, and AI integration enhancements.

### Key Development Areas

- **🌍 Multi-Language Support**: Spanish, French, German, Japanese, Mandarin Chinese (2025)
- **⚡ Performance Optimization**: GPU acceleration, model quantization, edge computing
- **🤖 Advanced Features**: Voice cloning, emotion control, contextual awareness
- **🧪 Cross-Platform Testing**: macOS, Windows, Linux, mobile, cloud platforms
- **🤝 Community Contributions**: Voice donation program, quality assurance pipeline

**📖 See the complete [Development Roadmap](docs/ROADMAP.md)**

## 🔌 API Basic Usage

### OpenAI-Compatible API
```bash
# Basic text-to-speech
curl -X POST 'http://localhost:8354/v1/audio/speech' \
  -H 'Content-Type: application/json' \
  -d '{"input": "Hello world", "voice": "af_heart", "response_format": "mp3"}' \
  --output hello.mp3

# With SSML and background sounds
curl -X POST 'http://localhost:8354/v1/audio/speech' \
  -H 'Content-Type: application/json' \
  -d '{"input": "<speak><background type=\"rain\" volume=\"20\">It'\''s raining outside</background></speak>", "voice": "af_bella"}' \
  --output rain.mp3
```

**📖 See the complete *[Advanced API Usage](docs/usage/API-USAGE.md)* guide**

### OpenWebUI Integration
In OpenWebUI Settings → Audio:
- **TTS Engine**: `OpenAI`
- **API Base URL**: `http://YOUR_IP:8354/v1`
- **TTS Model**: `litetts`
- **TTS Voice**: `af_heart`

**📖 See the complete [OpenWebUI Integration](docs/usage/OPENWEBUI-INTEGRATION.md) guide**

## ⚙️ Configuration

LiteTTS uses a flexible configuration system that allows easy customization while maintaining sensible defaults.

### Quick Configuration

**Basic customization using `override.json`:**
```json
{
  "server": {
    "port": 9000,
    "host": "127.0.0.1"
  },
  "voice": {
    "default_voice": "af_bella"
  }
}
```

### Complete Configuration Guide

For comprehensive configuration options including:
- Server and performance settings
- Voice and audio customization
- Text processing features
- Caching and monitoring
- Beta features and advanced options

**📖 See the complete [Configuration Guide](docs/CONFIGURATION.md)**

## 🔒 Perth Watermarking System

LiteTTS includes an integrated Perth audio watermarking system for responsible AI compliance and content authenticity verification.

### Key Features

- **🛡️ Automatic Watermarking**: All generated TTS audio is automatically watermarked
- **🔍 Content Authenticity**: Verify audio origin and detect AI-generated content
- **⚖️ Ethical AI Compliance**: Transparent disclosure of AI-generated content
- **🚫 Deepfake Detection**: Support for identifying synthetic audio content
- **⚙️ Configurable Strength**: Adjustable watermark intensity (0.1-2.0)
- **✅ Production Ready**: Perth library installed and functional

**📖 See the complete [Watermarking Guide](docs/WATERMARKING.md)**

## 📊 Monitoring & Observability

LiteTTS includes comprehensive monitoring and observability features for production deployments.

### Key Features

- **Health Monitoring**: Real-time component status and system health checks
- **Performance Metrics**: Response times, throughput, and resource utilization
- **Fault Tolerance**: Circuit breakers, retry logic, and graceful degradation
- **Structured Logging**: JSON logs with correlation IDs and performance data
- **Production Dashboard**: Web-based monitoring interface at `/dashboard`

### Quick System Checks

```bash
# Check overall system health
curl http://localhost:8354/health

# Access monitoring dashboard
http://localhost:8354/dashboard

# Get performance metrics
curl http://localhost:8354/metrics
```

**📖 See the complete [Monitoring & Observability Guide](docs/MONITORING.md)**

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](docs/CONTRIBUTIONS.md) for details.

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## ⚠️ Ethical Use Disclaimer

**By using this model, you agree to uphold relevant legal standards and ethical responsibilities. This tool is not responsible for any misuse:**

- **🚫 Identity Misuse**: Do not produce audio resembling real individuals without explicit permission
- **🚫 Deceptive Content**: Do not use this model to generate misleading content (e.g., fake news, impersonation)
- **🚫 Illegal or Malicious Use**: Do not use this model for activities that are illegal or intended to cause harm

**We strongly encourage responsible AI practices and respect for individual privacy and consent.**

## 🌸 About "Kokoro"

**"Kokoro"** (心) is a Japanese word that encompasses a rich and complex meaning, often translated as "heart," but extending to include "mind," "spirit," "feeling," and even "essence" or "core". It's not just a physical organ or a simple emotion, but rather the seat of consciousness, thoughts, feelings, and will. This name reflects our commitment to creating TTS technology that captures not just the words, but the heart and spirit of human communication.

## 🙏 Acknowledgments

**LiteTTS is built on the excellent work of the Kokoro TTS project:**

- **[Hexgrad Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)** - Original Kokoro TTS model
- **[ONNX Community Kokoro-82M](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX)** - ONNX optimized model
- **[Kokoro ONNX](https://github.com/thewh1teagle/kokoro-onnx)** - Core TTS engine and inspiration
- **[StyleTTS](https://github.com/yl4579/StyleTTS)** - Advanced neural TTS research

**Additional acknowledgments:**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [OpenWebUI](https://openwebui.com/) - Integration target

*LiteTTS extends and optimizes the Kokoro model for production use as part of the TaskWizer framework, while maintaining full compatibility with the original Kokoro ecosystem.*

---

**Need help?** Check our [📚 Documentation](#-documentation) or [create an issue](https://github.com/TaskWizer/LiteTTS/issues)!

