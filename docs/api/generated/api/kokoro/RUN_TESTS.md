# run_tests.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../FEATURES.md) | [Configuration](../../../../CONFIGURATION.md) | [Performance](../../../../PERFORMANCE.md) | [Monitoring](../../../../MONITORING.md) | [Testing](../../../../TESTING.md) | [Troubleshooting](../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../DEPENDENCIES.md) | [Quick Start](../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../API_REFERENCE.md) | [Development](../../../../development/README.md) | [Voice System](../../../../voices/README.md) | [Watermarking](../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../CHANGELOG.md) | [Roadmap](../../../../ROADMAP.md) | [Contributing](../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../BETA_FEATURES.md)

---


Comprehensive Test Runner for Kokoro ONNX TTS API
Executes all test suites with proper reporting and configuration


## Class: TestRunner

Comprehensive test runner for Kokoro ONNX TTS API

### __init__()

### check_dependencies()

Check if required dependencies are available

### find_test_files()

Find all test files matching the given patterns

### run_test_suite()

Run a specific test suite

### _parse_test_result()

Parse test result from subprocess and JSON report

### run_all_tests()

Run all test suites or specified suites

### _generate_summary()

Generate test run summary

## Function: main()

Main function with argument parsing

