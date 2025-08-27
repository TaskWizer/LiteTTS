# test_openwebui_integration.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Test script to simulate OpenWebUI TTS requests and verify integration fixes
Tests various request patterns that OpenWebUI might send


## Function: log_test()

Log test result

## Function: test_openwebui_null_format()

Test OpenWebUI request with null response_format

## Function: test_openwebui_missing_format()

Test OpenWebUI request with missing response_format field

## Function: test_openwebui_empty_format()

Test OpenWebUI request with empty string response_format

## Function: test_openwebui_null_speed()

Test OpenWebUI request with null speed

## Function: test_openwebui_all_nulls()

Test OpenWebUI request with all optional fields as null

## Function: test_openwebui_valid_request()

Test normal OpenWebUI request with valid values

## Function: test_openwebui_edge_cases()

Test various edge cases that might occur with OpenWebUI

## Function: run_openwebui_tests()

Run all OpenWebUI integration tests

