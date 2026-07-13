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
