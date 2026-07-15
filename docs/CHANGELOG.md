# 📋 Changelog

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

## [Unreleased] - 2026-07-15

### 🛠️ Pronunciation Fixes

| Issue | Before | After |
|-------|--------|-------|
| JSON | Spell-out J-S-O-N | "Jason" |
| C# | "C hash" | "C sharp" |
| F# | "F hash" | "F sharp" |
| SQL | Spell-out | "sequel" |
| YAML | "Y-A-M-L" | "yam-el" |
| XML | Spell-out | "eks-em-el" |
| OAuth | Spell-out | "OAuth" |
| IPv6 | Spell-out | "I-P-V-six" |
| SHA-256 | Spell-out | "SHA two fifty six" |
| Bass player | "bass" (rhymes with mass) | "BASE" (musical) |
| Lead singer | Ambiguous | "LEED" (verb pronunciation) |
| Emily Zhang | Unknown | Name preserved |
| qa-test@email.com | Skipped "qa-" | "Q-A dash test at example dot com" |
| -17.4°C | "one seven point four" | "minus seventeen point four" |
| 3.75 hours | "three seventy five" | "three point seven five" |
| señor, Grüß | Mangled | Preserved correctly |
| 日本語, 한국어 | Pronounced wrongly | "international text" placeholder |

### 🔧 Audio Generation Fixes

- **Text Chunking**: Implemented automatic text chunking for long-form audio
  - Kokoro has 510-phoneme limit causing truncation at ~23 seconds
  - New `_split_text_for_synthesis()` chunks at sentence boundaries
  - **Result**: 900-word text now generates 247s audio (was 29s) - **8.5x improvement**

- **Streaming Audio**: Implemented low-latency streaming for faster playback start
  - Audio chunks are yielded as they become available
  - Clients can start playback within seconds instead of waiting for entire generation
  - Falls back to standard synthesis when streaming not requested
  - Background caching of complete audio for future non-streaming requests

### 📊 Analysis & Reports

- **Optimization Report**: Created comprehensive `docs/OPTIMIZATION_REPORT.md`
  - 4 critical, 8 high, 12 medium, 10 low severity issues identified
  - Covers performance bottlenecks, quality improvements, architecture gaps, testing gaps
  - Kokoro ONNX limitations documented with recommended mitigations

### 🐛 Bug Fixes

- Fixed regex for C# (and F#, D#, A#, G#) - `#` is not a word character
- Fixed email regex to use match.group() instead of raw string
- Fixed YAML pronunciation using misaki-compatible lowercase "yam-el"
- Fixed NFKC unicode normalization breaking fractions (½ → 21⁄2)
- Fixed temperature handling with proper whole-number words

### 📝 Documentation

- Comprehensive pronunciation handling documented
- Text preprocessing pipeline explained
- Kokoro limitations and workarounds documented

### ✅ Testing

- **Fixed critical circular import** in models/__init__.py
  - Was preventing all unit tests from running
  - Changed to dynamic import using importlib.util

- **Added comprehensive unit tests** (74 tests now passing):
  - test_validators.py: 15 tests for API validation
  - test_phonemizer_preprocessor.py: 28 tests for text preprocessing
  - test_chunking.py: 16 tests for text chunking
  - test_progressive_generator.py: 15 tests for progressive audio

## [1.0.0] - 2025-08-16

### Added
- ✨ **Time-Stretching Optimization** - Beta feature for improved latency
- 📝 **Comprehensive Text Processing Configuration** - Expanded config.json with detailed options
- 🗂️ **Repository Structure Reorganization** - Production-ready directory structure
- 📚 **Documentation Cleanup** - Consolidated and organized all documentation
- 📋 **Comprehensive README Files** - Added README files for all directories
- 🤝 **CONTRIBUTIONS.md** - Contributing guidelines for developers
- 📄 **LICENSE** - MIT license for open source distribution

### Changed
- 🔄 **Merged test directories** - Consolidated tests into kokoro/tests/
- 📁 **Moved voice samples** - Relocated to samples/ directory with clean naming
- ⚙️ **Centralized JSON configs** - Moved all configs to kokoro/config/
- 🧹 **Cleaned documentation** - Removed outdated and redundant files

### Technical Improvements
- 🎯 **Enhanced phonetic processing** - RIME AI integration and pronunciation fixes
- 🔧 **Advanced symbol processing** - Improved handling of punctuation and special characters
- 💬 **Better contraction handling** - Natural pronunciation rules for contractions
- 🌐 **Improved URL processing** - Natural web address pronunciation
- 💰 **Enhanced currency processing** - Better financial data pronunciation
- 📅 **Advanced date/time processing** - Natural date and time pronunciation

### Performance
- ⚡ **Time-stretching optimization** - Experimental feature for reduced latency
- 📊 **Performance regression testing** - Automated testing framework
- 🧪 **Comprehensive test suite** - Extensive validation and edge case testing


## [2.0.0] - 2024-12-19 - Major Enhancement Release

### 🆕 New Features

#### SSML Background Noise Enhancement
- **Background Audio Synthesis**: Added `<background>` SSML tag support
- **5 Ambient Sound Types**: nature, rain, coffee_shop, office, wind
- **Volume Control**: Configurable volume levels (1-100)
- **Audio Mixing**: Intelligent speech/background balance with ducking

#### Interactive Voice Showcase
- **54+ Voice Samples**: Comprehensive showcase with audio samples
- **Organized Categories**: Grouped by language, accent, and gender
- **Direct Comparison**: HTML5 audio controls for immediate playback
- **Voice Descriptions**: Detailed characteristics and use case recommendations

#### Real-Time Analytics Dashboard
- **Performance Metrics**: RTF tracking, response times, throughput
- **Usage Statistics**: Requests per minute/hour, voice popularity
- **System Health**: Memory usage, cache hit rates, error monitoring
- **Concurrency Tracking**: Active connections and queue status

#### RTF Performance Optimization
- **Excellent Performance**: Average RTF 0.197 (5x faster than real-time)
- **Intelligent Caching**: LRU cache with TTL and pre-warming
- **Vectorized Audio Processing**: Optimized numpy operations
- **Enhanced Monitoring**: Real-time RTF tracking with percentiles

### 🔧 Improvements

#### Pronunciation Accuracy Enhancements
- **Quote Character Fix**: Proper silent quote processing
- **Contraction Handling**: Natural possessive form pronunciation
- **Phonetic Mapping**: Improved consonant cluster handling
- **HTML Entity Decoding**: Fixed apostrophe and special character issues

#### Configuration System
- **Port Configuration**: Fixed uvicorn port setting from config.json
- **Centralized Config**: Moved config.json to project root
- **Environment Support**: Production and development configurations

#### Code Quality & Organization
- **Project Structure**: Reorganized files for better maintainability
- **Test Coverage**: 95.8% pronunciation accuracy with comprehensive tests
- **Documentation**: Complete API reference, guides, and troubleshooting
- **Performance Monitoring**: Built-in RTF and system metrics

### 📊 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Average RTF | 0.25 | 0.197 | 21% faster |
| Cache Hit Response | 200ms | 29ms | 99x speedup |
| Memory Footprint | 60MB | 44.5MB | 26% reduction |
| Test Success Rate | 85% | 95.8% | 13% improvement |

### 🐛 Bug Fixes

#### Critical Fixes
- **Text Truncation**: Fixed quote character corruption causing truncated audio
- **Pronunciation Regressions**: Resolved word skipping and phonetic mapping issues
- **HTML Entity Handling**: Fixed possessive contractions pronunciation
- **Cache Consistency**: Improved caching reliability and performance

#### Minor Fixes
- **Error Handling**: Better validation and error messages
- **Memory Leaks**: Improved memory management in audio processing
- **Configuration Loading**: Fixed config.json parsing and validation
- **Voice Loading**: Optimized voice file discovery and caching

### 📚 Documentation

#### New Documentation
- **[SSML Guide](docs/ssml_guide.md)**: Comprehensive SSML usage with examples
- **[API Reference](docs/API_REFERENCE.md)**: Complete endpoint documentation
- **[Performance Guide](docs/performance_guide.md)**: Optimization and monitoring
- **[Troubleshooting Guide](docs/troubleshooting_guide.md)**: Common issues and solutions
- **[Voice Showcase](docs/voices/README.md)**: Interactive voice comparison

#### Updated Documentation
- **README.md**: Added new features, troubleshooting, and performance benchmarks
- **Configuration**: Updated setup and deployment instructions
- **Testing**: Comprehensive test suite documentation

### 🧪 Testing

#### New Test Suites
- **Comprehensive Test Suite**: 31 tests covering all functionality (93.5% success rate)
- **SSML Background Tests**: Validation of all background types and volume levels
- **Performance Regression Tests**: RTF and response time monitoring
- **Pronunciation Accuracy Tests**: Specific test cases for fixed issues

#### Test Coverage
- **Basic API**: 100% (3/3 tests passed)
- **SSML Background**: 100% (6/6 tests passed)
- **Voice Showcase**: 100% (3/3 tests passed)
- **Pronunciation**: 100% (5/5 tests passed)
- **Performance**: 100% (2/2 tests passed)

### 🔄 Migration Guide

#### From v1.x to v2.0

1. **Update Configuration**
   ```bash
   # Move config.json to project root if not already there
   mv kokoro/config.json ./config.json
   ```

2. **Update API Calls**
   ```bash
   # Port changed from 8000 to 8354
   # Update your API calls accordingly
   curl http://localhost:8354/v1/audio/speech
   ```

3. **SSML Usage**
   ```xml
   <!-- New SSML background feature -->
   <speak>
     <background type="rain" volume="20">
       Your text with ambient rain sounds
     </background>
   </speak>
   ```

4. **Voice Showcase**
   ```bash
   # Browse new voice showcase
   open docs/voices/README.md
   ```

### 🚀 Deployment

#### Production Readiness
- **Docker Support**: Updated Dockerfile and docker-compose.yml
- **Environment Configuration**: Production and development settings
- **Health Checks**: Built-in monitoring and diagnostics
- **Performance Monitoring**: Real-time metrics and alerting

#### Scaling Recommendations
- **Single Instance**: 4+ CPU cores, 8GB+ RAM
- **Multi-Instance**: Load balancing with sticky sessions
- **Monitoring**: Use `/dashboard` for performance tracking

---

## [1.0.0] - 2024-11-15 - Initial Release

### Features
- Basic TTS synthesis with Kokoro ONNX
- 18 high-quality voices
- OpenAI-compatible API
- FastAPI web server
- Basic caching system

### Voices
- American English (male/female)
- British English (male/female)
- Basic voice selection

### Performance
- Real-time synthesis
- Basic error handling
- Simple configuration

---

*For detailed information about any release, see the corresponding documentation in the `docs/` directory.*
