# LiteTTS Features

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [**Features**](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

LiteTTS is a high-performance text-to-speech API built on the Kokoro ONNX model, designed for production use with OpenWebUI compatibility and advanced features.

## ✨ Core Features

### 🚀 Performance
- **Lightning Fast**: 29ms cached responses, 0.15 RTF (6.7x faster than real-time)
- **Optimized Models**: Q4 quantized ONNX models for optimal performance/size balance
- **Intelligent Caching**: Multi-layer caching system with automatic optimization
- **Dynamic CPU Allocation**: Automatic CPU core optimization based on workload

### 🌍 Voice System
- **54+ Voices**: Multi-language support with comprehensive voice library
- **Voice Blending**: Mix multiple voices for unique audio characteristics
- **Dynamic Voice Loading**: Efficient individual voice loading strategy
- **Voice Discovery**: Automatic voice detection and management

### 🔌 API Compatibility
- **OpenAI Compatible**: Drop-in replacement for OpenAI TTS API
- **OpenWebUI Ready**: Works out-of-the-box with OpenWebUI without additional configuration
- **RESTful API**: Standard HTTP endpoints with comprehensive documentation
- **Streaming Support**: Real-time audio streaming capabilities

### 🎛️ Advanced Audio Processing
- **SSML Support**: Background noise synthesis and voice modulation
- **Audio Formats**: MP3, WAV, FLAC, OPUS support
- **Quality Control**: Configurable audio quality and bitrate settings
- **Time Stretching**: Beta feature for speed optimization

### 🔒 Security & Compliance
- **Perth Watermarking**: Responsible AI compliance with automatic audio watermarking
- **Content Authenticity**: Verify audio origin and detect AI-generated content
- **Security Hardening**: Non-root containers, read-only filesystems, resource limits
- **Rate Limiting**: Configurable request rate limiting and security controls

### 📊 Production Features
- **Health Monitoring**: Real-time component status and system health checks
- **Performance Metrics**: Response times, throughput, and resource utilization
- **Structured Logging**: JSON logs with correlation IDs and performance data
- **Dashboard**: Web-based monitoring interface at `/dashboard`
- **Fault Tolerance**: Circuit breakers, retry logic, and graceful degradation

### 🛠️ Development & Operations
- **Docker Support**: Multi-stage builds with development and production modes
- **Configuration Management**: Hierarchical configuration with hot reload
- **Testing Framework**: Comprehensive test suite with audio quality validation
- **Monitoring Integration**: Prometheus, Grafana, and custom metrics support

## 🎯 Use Cases

### Content Creation
- **Podcasts & Audiobooks**: High-quality voice synthesis for long-form content
- **Video Narration**: Professional voice-over for educational and marketing videos
- **Interactive Media**: Dynamic voice generation for games and applications

### Business Applications
- **Customer Service**: Automated voice responses and IVR systems
- **Accessibility**: Text-to-speech for visually impaired users
- **Multilingual Support**: Content localization across different languages

### Development Integration
- **Chatbots & AI Assistants**: Voice output for conversational AI systems
- **Mobile Applications**: Offline TTS capabilities for mobile apps
- **Web Applications**: Real-time voice synthesis for web platforms

## 🔧 Technical Specifications

### Model Information
- **Base Model**: Kokoro-82M ONNX optimized
- **Model Size**: ~200MB (Q4 quantized)
- **Languages**: English (primary), with multi-language expansion planned
- **Sample Rate**: 24kHz high-quality audio output

### Performance Targets
- **RTF (Real-Time Factor)**: < 0.25 (4x faster than real-time)
- **Memory Usage**: < 150MB additional overhead
- **Response Time**: < 100ms for cached requests
- **Throughput**: 100+ concurrent requests supported

### System Requirements
- **Memory**: 2GB RAM minimum (4GB+ recommended)
- **Storage**: 1GB free space for models and cache
- **CPU**: Modern multi-core processor (ARM64 and x86_64 supported)
- **Network**: Internet connection for initial model downloads

## 🚀 Getting Started

1. **Quick Start**: `git clone && cd LiteTTS && uv run python app.py`
2. **Docker**: `docker-compose up -d`
3. **API Test**: `curl -X POST "http://localhost:8354/v1/audio/speech" -H "Content-Type: application/json" -d '{"input": "Hello, world!", "voice": "af_heart"}'`

For detailed setup instructions, see the [Quick Start Guide](usage/QUICK_START_COMMANDS.md).

## 📚 Documentation

- **[Configuration Guide](CONFIGURATION.md)**: Complete configuration options
- **[Performance Guide](PERFORMANCE.md)**: Optimization and benchmarking
- **[API Reference](api/API_REFERENCE.md)**: Complete endpoint documentation
- **[Voice System](voices/README.md)**: Voice management and customization
- **[Monitoring](MONITORING.md)**: Production monitoring and observability