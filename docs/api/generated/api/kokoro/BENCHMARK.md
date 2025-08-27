# benchmark.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Comprehensive Model Performance Benchmarking System for Kokoro TTS
Tests all available models with RTF, latency, memory, CPU, and quality metrics


## Class: BenchmarkResult

Individual benchmark result

## Class: SystemMonitor

Monitor system resources during benchmarking

### __init__()

### start_monitoring()

Start system monitoring

### stop_monitoring()

Stop monitoring and return peak/avg memory and CPU

### _monitor_worker()

Background worker for system monitoring

## Class: AudioQualityAnalyzer

Analyze audio quality metrics

### analyze_audio_quality()

Analyze audio quality and return a score (0-100)
Higher scores indicate better quality

## Class: ModelBenchmarker

Comprehensive model benchmarking system

### __init__()

### discover_models()

Discover all available ONNX models

### benchmark_model()

Benchmark a single model with all test cases

### _benchmark_single_case()

Benchmark a single test case

### run_full_benchmark()

Run comprehensive benchmark on all models

### _generate_summary()

Generate benchmark summary statistics

## Class: BenchmarkReporter

Generate reports from benchmark results

### generate_markdown_report()

Generate a comprehensive markdown report

### save_results()

Save benchmark results in multiple formats

## Function: main()

Main benchmarking function

