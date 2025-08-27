# test_phonetic_contraction_fixes.py

---
**📚 LiteTTS Documentation Navigation**

**Core Documentation:** [Features](../../../../../../FEATURES.md) | [Configuration](../../../../../../CONFIGURATION.md) | [Performance](../../../../../../PERFORMANCE.md) | [Monitoring](../../../../../../MONITORING.md) | [Testing](../../../../../../TESTING.md) | [Troubleshooting](../../../../../../TROUBLESHOOTING.md)

**Setup & Usage:** [Dependencies](../../../../../../DEPENDENCIES.md) | [Quick Start](../../../../../../usage/QUICK_START_COMMANDS.md) | [Docker Deployment](../../../../../../usage/DOCKER-DEPLOYMENT.md) | [OpenWebUI Integration](../../../../../../usage/OPENWEBUI-INTEGRATION.md)

**Advanced:** [API Reference](../../../../../API_REFERENCE.md) | [Development](../../../../../../development/README.md) | [Voice System](../../../../../../voices/README.md) | [Watermarking](../../../../../../WATERMARKING.md)

**Project:** [Changelog](../../../../../../CHANGELOG.md) | [Roadmap](../../../../../../ROADMAP.md) | [Contributing](../../../../../../CONTRIBUTIONS.md) | [Beta Features](../../../../../../BETA_FEATURES.md)

---


Test suite for phonetic contraction pronunciation fixes
Validates fixes for wasn't→wAHz-uhnt, I'll→ill, you'll→yaw-wl, etc.


## Class: TestPhoneticContractionFixes

Test phonetic contraction pronunciation fixes

### setUp()

### test_critical_pronunciation_fixes()

Test the most critical pronunciation issues identified by user

### test_negative_contractions()

Test negative contractions (wasn't, weren't, isn't, etc.)

### test_will_contractions()

Test 'll contractions (I'll, you'll, etc.)

### test_would_contractions()

Test 'd contractions (I'd, you'd, etc.)

### test_context_sensitive_contractions()

Test context-sensitive contractions ('d and 's)

### test_case_preservation()

Test that original case is preserved

### test_phonetic_representations()

Test phonetic representations of contractions

### test_analysis_functionality()

Test contraction analysis functionality

## Function: run_comprehensive_contraction_tests()

Run all contraction tests and provide summary

