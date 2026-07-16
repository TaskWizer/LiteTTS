# Progress - TTS Pronunciation Fixes

## 2026-07-12
- [x] Created RESEARCH.md documenting issues
- [x] Created PLAN.md with implementation phases
- [x] Created TASKS.md with task breakdown
- [x] Task 1: Fix phonemizer_preprocessor.py - COMPLETED
- [x] Task 2: Remove fraction slash pattern - COMPLETED
- [x] Task 3: Add pronunciation fixes - COMPLETED
- [x] Task 4: Update slash handling - COMPLETED
- [x] Verification tests passed

## Summary of Changes

### Files Modified:
1. `LiteTTS/text/phonemizer_preprocessor.py`
   - Fixed acronym pattern to only match true acronyms (FBI, NASA) not natural words (Directions, Any, Know)
   - Removed fraction slash pattern
   - Removed '/' from symbol_words_map

2. `LiteTTS/nlp/clean_text_normalizer.py`
   - Added pronunciation fixes for: because, know, tests, Directions, any, their, there

3. `LiteTTS/nlp/text_normalizer.py`
   - Changed slash handling from " slash " to " " (space) - slashes now silent

### Verification Results:
- "Directions", "Any", "Know" no longer match acronym pattern ✓
- "FBI", "NASA" still correctly match acronym pattern ✓
- Slash "/" now replaced with space instead of "slash" ✓
- New pronunciation fixes loaded correctly ✓

## 2026-07-14
- [x] Created OPTIMIZATION_REPORT.md with comprehensive analysis
- [x] 34 issues identified across 4 severity levels
- [x] Deep analysis of Kokoro ONNX limitations
- [x] Testing gaps documented
- [x] Prioritized fix roadmap created

### Key Findings:
| Category | Count |
|----------|-------|
| Critical | 4 |
| High | 8 |
| Medium | 12 |
| Low | 10 |

### Top Immediate Actions:
1. Add ONNX input validation before inference
2. Fix tokenization cache key to include all parameters
3. Implement voice embedding cache eviction policy
4. Remove or fix pipeline parallelism dead code

## 2026-07-16
- [x] Systematic test coverage improvement for LiteTTS codebase
- [x] phonemizer_preprocessor.py: 94% → 98% coverage (272 tests)
- [x] Multiple exception handlers tested
- [x] Source code refactored for testability

### Current Coverage Status:
| Module | Coverage |
|--------|----------|
| phonemizer_preprocessor.py | 98% |
| downloader.py | 99% |
| error_handling.py | 99% |
| hardware_optimizer.py | 100% |
| **Overall (key modules)** | **98%+** |

### Remaining 11 Uncovered Lines (2%):
- Lines 21, 58-59: Module-level imports (can't test import success)
- Lines 831, 842, 856, 898: Inside nested functions (coverage.py limitation)
- Lines 1174-1176, 1213, 1278: Inside nested functions with exception handlers

### Testing Improvements:
- Refactored `problematic_contractions` and `problematic_symbols` to instance attributes
- Added `_safe_int()` wrapper method for testability
- Added 15+ new tests for exception handlers and edge cases
- 376 total tests passing across key modules

