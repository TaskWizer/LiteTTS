# 📊 Performance Benchmarks

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](FEATURES.md) | [Configuration](CONFIGURATION.md) | [Performance](PERFORMANCE.md) | [Monitoring](MONITORING.md) | [Testing](TESTING.md) | [Troubleshooting](TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](DEPENDENCIES.md) | [Quick Start](usage/QUICK_START_COMMANDS.md) | [Docker Deployment](usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](api/API_REFERENCE.md) | [Development](development/README.md) | [Voice System](voices/README.md) | [Watermarking](WATERMARKING.md)

**Project:** [Changelog](CHANGELOG.md) | [Roadmap](ROADMAP.md) | [Contributing](CONTRIBUTIONS.md) | [Beta Features](BETA_FEATURES.md)

---

This document provides detailed performance metrics and optimization guidelines for the Kokoro ONNX TTS API.

## Real-Time Factor (RTF) Measurements

**RTF = Generation Time / Audio Duration** (lower is better, <1.0 = faster than real-time)

| Text Length | Average RTF | Min RTF | Max RTF | Performance Rating |
|-------------|-------------|---------|---------|-------------------|
| Short (11 chars) | 0.215 | 0.008 | 0.629 | 🟢 Excellent |
| Medium (61 chars) | 0.160 | 0.012 | 0.446 | 🟢 Excellent |
| Long (224 chars) | 0.150 | 0.004 | 0.440 | 🟢 Excellent |
| **Overall Average** | **0.197** | **0.004** | **0.629** | **🟢 Excellent** |

## Response Time Analysis

| Scenario | Response Time | RTF | Cache Status |
|----------|---------------|-----|--------------|
| First Request | ~1.2s | 0.25 | Miss |
| Cached Request | ~29ms | 0.006 | Hit |
| Background SSML | ~0.8s | 0.18 | Miss |
| Voice Loading | ~0.2s | 0.05 | Cached |

## System Resource Usage

| Metric | Value | Rating |
|--------|-------|--------|
| Memory Footprint | 44.5 MB RSS | 🟢 Very Efficient |
| CPU Impact | +0.1% during synthesis | 🟢 Minimal |
| Cache Hit Rate | 85-95% (typical) | 🟢 Excellent |
| Throughput | 15-25 RPS | 🟢 High |

## Performance Optimization Guidelines

### 1. Cache Optimization
- Enable intelligent pre-caching for common phrases
- Monitor cache hit rates via dashboard
- Adjust cache TTL based on usage patterns

### 2. RTF Optimization
- Use shorter text chunks for better parallelization
- Leverage SSML for complex audio requirements
- Monitor RTF trends via `/dashboard`

### 3. Memory Management
- Regular cache cleanup for long-running instances
- Monitor memory usage patterns
- Adjust cache size based on available RAM

### 4. Concurrency Tuning
- Optimal performance at 5-10 concurrent requests
- Use request queuing for higher loads
- Monitor active connections via dashboard

## Benchmark Test Commands

```bash
# Run performance audit
python kokoro/scripts/rtf_optimization_audit.py

# Test SSML background functionality
python kokoro/scripts/test_ssml_background.py

# Generate voice showcase with timing
python kokoro/scripts/generate_voice_showcase.py

# Focused RTF audit
python kokoro/scripts/focused_rtf_audit.py
```

## Performance Monitoring

### Dashboard Metrics
Access real-time performance metrics at `http://localhost:8354/dashboard`:

- **RTF Trends**: Real-time factor over time
- **Cache Performance**: Hit rates and efficiency
- **Memory Usage**: Current and peak memory consumption
- **Request Patterns**: Concurrent requests and queue status

### Key Performance Indicators (KPIs)

| Metric | Target | Excellent | Good | Needs Attention |
|--------|--------|-----------|------|-----------------|
| RTF | < 0.3 | < 0.2 | 0.2-0.5 | > 0.5 |
| Cache Hit Rate | > 80% | > 90% | 70-90% | < 70% |
| Response Time | < 1s | < 500ms | 500ms-2s | > 2s |
| Memory Usage | < 100MB | < 50MB | 50-100MB | > 100MB |

## Optimization Tips

### For High-Volume Applications
1. **Pre-warm cache** with common phrases
2. **Use connection pooling** for multiple concurrent requests
3. **Monitor memory usage** and restart periodically if needed
4. **Implement request queuing** for burst traffic

### For Low-Latency Applications
1. **Enable aggressive caching** for repeated content
2. **Use shorter text chunks** when possible
3. **Pre-load frequently used voices**
4. **Monitor RTF metrics** continuously

### For Resource-Constrained Environments
1. **Adjust cache size** based on available memory
2. **Use fewer concurrent workers**
3. **Implement request throttling**
4. **Monitor system resources** closely

## Troubleshooting Performance Issues

### High RTF (> 0.5)
- Check system CPU usage
- Verify model loading is complete
- Monitor memory availability
- Consider reducing concurrent requests

### Low Cache Hit Rate (< 70%)
- Review caching configuration
- Check cache TTL settings
- Monitor request patterns
- Consider pre-warming cache

### High Memory Usage (> 100MB)
- Check for memory leaks
- Review cache size settings
- Monitor garbage collection
- Consider restarting service

## Additional Resources

- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [Configuration Guide](../config.json) - Performance-related settings
- [API Documentation](FEATURES.md) - Endpoint reference and usage
