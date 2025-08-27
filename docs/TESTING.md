# 🧪 Testing Guide - LiteTTS API

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

**Comprehensive testing framework for ensuring quality and performance**

## 🎯 Overview

This guide covers testing procedures for the Kokoro ONNX TTS API, including unit tests, integration tests, performance tests, and quality assurance procedures.

## 🚀 Quick Test

### **Basic Functionality Test**
```bash
# Test zero-configuration startup
python -c "
from app import KokoroTTSApplication
app = KokoroTTSApplication()
print('✅ Application starts successfully')
print(f'Voices available: {len(app.available_voices)}')
"
```

### **API Endpoint Test**
```bash
# Start server and test
uv run uvicorn app:app &
sleep 10

# Test health endpoint
curl http://localhost:8354/health

# Test TTS endpoint
curl -X POST "http://localhost:8354/v1/audio/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Test message", "voice": "af_heart"}' \
  --output test.mp3

# Cleanup
pkill -f uvicorn
```

## 🔧 Running Tests

### **Unit Tests**
```bash
# Run all unit tests
python -m pytest kokoro/tests/ -v

# Run specific test module
python -m pytest kokoro/tests/test_text_processing.py -v

# Run with coverage
python -m pytest kokoro/tests/ --cov=kokoro --cov-report=html
```

### **Integration Tests**
```bash
# Run integration tests
python kokoro/run_tests.py

# Performance regression tests
python kokoro/benchmarks/run_performance_regression_tests.py
```

### **Voice System Tests**
```bash
# Test voice loading and mapping
python -c "
from kokoro.voice.dynamic_manager import dynamic_voice_manager
print(f'Voice mappings: {len(dynamic_voice_manager.voice_mappings)}')
print('✅ Voice system working')
"
```

## 📊 Performance Testing

### **Benchmark Tests**
```bash
# Quick benchmark
python kokoro/benchmarks/quick_benchmark.py

# Comprehensive performance analysis
python kokoro/benchmarks/performance_analysis.py

# RTF (Real-Time Factor) testing
python kokoro/scripts/performance/focused_rtf_audit.py
```

### **Load Testing**
```bash
# Install load testing tools
uv add locust

# Run load test
locust -f kokoro/tests/scripts/test_load_testing.py --host=http://localhost:8354
```

## 🎭 Voice Quality Testing

### **Voice Validation**
```bash
# Test all voices
python kokoro/scripts/documentation/generate_voice_showcase.py

# Pronunciation testing
python kokoro/scripts/monitoring/audit_contraction_preprocessing.py
```

### **Audio Quality Tests**
```bash
# Generate test samples
for voice in af_heart am_adam bf_alice bm_daniel; do
  curl -X POST "http://localhost:8354/v1/audio/speech" \
    -H "Content-Type: application/json" \
    -d "{\"input\": \"Quality test for voice $voice\", \"voice\": \"$voice\"}" \
    --output "test_$voice.mp3"
done
```

## 🔍 System Validation

### **Configuration Testing**
```bash
# Test zero-configuration
mv config.json config.json.backup
python -c "from kokoro.config import config; print('✅ Zero-config works')"
mv config.json.backup config.json

# Test configuration override
python -c "from kokoro.config import config; print(f'App: {config.application.name}')"
```

### **Contraction Processing Tests**
```bash
# Test enhanced contraction processor
python -c "
from kokoro.nlp.enhanced_contraction_processor import EnhancedContractionProcessor
processor = EnhancedContractionProcessor()
test_cases = ['I\\'ll be there', 'Don\\'t worry', 'You\\'re amazing']
for text in test_cases:
    result = processor.process_contractions(text)
    print(f'{text} → {result}')
print('✅ Contraction processing working')
"
```

## 🎯 Test Categories

### **1. Functional Tests**
- API endpoint functionality
- Voice loading and selection
- Text processing and normalization
- Audio generation and formats
- SSML processing
- Configuration management

### **2. Performance Tests**
- Response time measurements
- Memory usage monitoring
- CPU utilization tracking
- Cache performance validation
- Concurrent request handling

### **3. Quality Tests**
- Audio quality assessment
- Pronunciation accuracy
- Voice consistency
- SSML feature validation
- Error handling robustness

### **4. Integration Tests**
- OpenWebUI compatibility
- Docker deployment validation
- Network connectivity tests
- Multi-user scenarios
- Production environment simulation

## 📋 Test Checklist

### **Pre-Release Testing**
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance benchmarks meet targets
- [ ] Voice quality validated
- [ ] Documentation links verified
- [ ] Docker deployment tested
- [ ] OpenWebUI integration confirmed
- [ ] Zero-configuration startup works
- [ ] Configuration overrides function
- [ ] Error handling robust

### **Performance Targets**
- [ ] Startup time < 10 seconds
- [ ] First TTS request < 500ms
- [ ] Cached requests < 50ms
- [ ] RTF < 0.2 (5x faster than real-time)
- [ ] Memory usage < 200MB (steady state)
- [ ] 99% uptime in stress tests

### **Quality Targets**
- [ ] All 55+ voices load successfully
- [ ] Pronunciation accuracy > 95%
- [ ] Audio quality: 24kHz, clear output
- [ ] SSML features working correctly
- [ ] No audio artifacts or distortion

## 🛠️ Debugging Tests

### **Debug Mode Testing**
```bash
# Enable debug logging
export KOKORO_LOG_LEVEL=DEBUG
uv run uvicorn app:app --log-level debug
```

### **Memory Profiling**
```bash
# Install profiling tools
uv add memory-profiler psutil

# Profile memory usage
python -m memory_profiler kokoro/scripts/memory_profile_test.py
```

### **Performance Profiling**
```bash
# Profile performance
python -m cProfile -o profile_output.prof kokoro/scripts/performance_test.py
python -c "import pstats; pstats.Stats('profile_output.prof').sort_stats('cumulative').print_stats(20)"
```

## 🔄 Continuous Testing

### **Automated Testing Pipeline**
```bash
#!/bin/bash
# test_pipeline.sh

echo "🧪 Running test pipeline..."

# Unit tests
echo "Running unit tests..."
python -m pytest kokoro/tests/ -v || exit 1

# Integration tests
echo "Running integration tests..."
python kokoro/run_tests.py || exit 1

# Performance tests
echo "Running performance tests..."
python kokoro/benchmarks/quick_benchmark.py || exit 1

# Voice system tests
echo "Testing voice system..."
python -c "from kokoro.voice.dynamic_manager import dynamic_voice_manager; print('✅ Voice system OK')" || exit 1

echo "✅ All tests passed!"
```

### **Regression Testing**
```bash
# Run regression test suite
python kokoro/benchmarks/run_performance_regression_tests.py

# Compare with baseline
python kokoro/scripts/compare_performance_baseline.py
```

## 📊 Test Reporting

### **Generate Test Report**
```bash
# Comprehensive test report
python kokoro/scripts/generate_test_report.py

# Performance report
python kokoro/scripts/generate_performance_report.py
```

### **Coverage Report**
```bash
# Generate coverage report
python -m pytest kokoro/tests/ --cov=kokoro --cov-report=html --cov-report=term

# View coverage
open htmlcov/index.html
```

## 🔗 Related Resources

- [Performance Benchmarks](performance.md)
- [System Improvements](SYSTEM_IMPROVEMENTS_DOCUMENTATION.md)
- [Quick Start Guide](QUICK_START_COMMANDS.md)
- [API Reference](FEATURES.md)

---

**🎯 Comprehensive Testing** ensures the Kokoro ONNX TTS API maintains high quality and performance standards! 🧪✅
