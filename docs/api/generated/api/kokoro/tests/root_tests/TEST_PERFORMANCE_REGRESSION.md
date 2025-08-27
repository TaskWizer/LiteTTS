# test_performance_regression.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Performance regression testing for TTS pronunciation fixes
Ensures that new fixes don't break existing functionality or degrade performance


## Class: PerformanceBenchmark

Performance benchmarking utility

### __init__()

### time_function()

Time a function execution

### memory_usage()

Measure memory usage of a function

## Class: TestPerformanceRegression

Test performance regression for all new components

### setUp()

### _load_test_texts()

Load test texts of various sizes and complexities

### test_contraction_processing_performance()

Test contraction processing performance

### test_symbol_processing_performance()

Test symbol processing performance

### test_pronunciation_dictionary_performance()

Test pronunciation dictionary performance

### test_datetime_processing_performance()

Test date/time processing performance

### test_abbreviation_handling_performance()

Test abbreviation handling performance

### test_emotion_intonation_performance()

Test emotion/intonation processing performance

### test_voice_modulation_performance()

Test voice modulation performance

### test_integrated_processing_performance()

Test integrated processing performance

### test_comparison_with_existing_components()

Compare performance with existing components

### test_memory_usage()

Test memory usage of new components

### test_correctness_preservation()

Test that new components preserve correctness of existing functionality

