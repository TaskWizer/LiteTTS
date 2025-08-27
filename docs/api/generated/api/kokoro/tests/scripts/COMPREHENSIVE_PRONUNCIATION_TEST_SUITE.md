# comprehensive_pronunciation_test_suite.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Comprehensive Test Suite for Pronunciation Issues

This test suite validates all the pronunciation fixes implemented:
1. Quote character pronunciation bug (fixed)
2. Possessive contractions HTML entity issue (fixed)
3. Word truncation/phonetic mapping issues (investigated)
4. Text skipping/omission bug (investigated)

Usage:
    python kokoro/scripts/comprehensive_pronunciation_test_suite.py
    python kokoro/scripts/comprehensive_pronunciation_test_suite.py --api-test  # Include API tests
    python kokoro/scripts/comprehensive_pronunciation_test_suite.py --verbose   # Detailed output


## Class: PronunciationTestSuite

Comprehensive test suite for pronunciation issues

### __init__()

### log()

Log message with optional verbosity control

### test_quote_character_pronunciation()

Test quote character pronunciation fixes

### test_possessive_contractions_html_entities()

Test possessive contractions HTML entity fixes

### test_word_truncation_phonetic_mapping()

Test word truncation and phonetic mapping

### test_text_skipping_omission()

Test text skipping and omission issues

### test_regression_cases()

Test regression cases to ensure existing functionality works

### test_api_pronunciation()

Test pronunciation through the API

### run_all_tests()

Run all pronunciation tests

### generate_summary_report()

Generate a comprehensive summary report

## Function: main()

Main execution function

