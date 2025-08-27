# benchmark_models.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Comprehensive model benchmarking script to determine optimal model variant for RTF performance


## Class: ModelBenchmarkResult

Results for a single model benchmark

## Class: ModelBenchmarker

Comprehensive model benchmarking system

### __init__()

### discover_models()

Discover available ONNX models with their sizes

### benchmark_model()

Benchmark a single model variant

### run_comprehensive_benchmark()

Run comprehensive benchmark on all available models

### analyze_results()

Analyze benchmark results and provide recommendations

### save_results()

Save benchmark results to file

## Function: main()

