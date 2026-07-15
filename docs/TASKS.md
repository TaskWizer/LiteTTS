# Tasks - TTS Pronunciation Fixes

## Task 1: Fix phonemizer_preprocessor.py problematic_patterns
**File:** `LiteTTS/text/phonemizer_preprocessor.py`
**Status:** COMPLETED
**Changes:**
- Removed the over-aggressive `(r'([A-Z]{2,})', ...)` pattern that spells out regular words
- Only converts true acronyms (all caps sequences like FBI, NASA)
- Preserves capitalized words like "Directions", "Any", "Know"

## Task 2: Remove fraction slash pattern
**File:** `LiteTTS/text/phonemizer_preprocessor.py`
**Status:** COMPLETED
**Changes:**
- Removed `(r'\b(\d+)/(\d+)\b', r'\1 slash \2', 'Fractions and dates')` pattern
- Let natural number processing handle fractions

## Task 3: Add pronunciation fixes to clean_text_normalizer.py
**File:** `LiteTTS/nlp/clean_text_normalizer.py`
**Status:** COMPLETED
**Changes:**
- Added "because": "be-CAUZ" - prevents "be-swah-s-e" pronunciation
- Added "know": "NOH" - prevents confusion with "now"
- Added "tests": "TESTS" - preserves 'e', prevents "tess"
- Added "Directions": "di-REK-shuns" - prevents letter-by-letter spelling
- Added "any": "EN-ee" - prevents "e-n-turn-v" pronunciation
- Added "their"/"there": "THAIR" - distinct pronunciations

## Task 4: Update text_normalizer slash handling
**File:** `LiteTTS/nlp/text_normalizer.py`
**Status:** COMPLETED
**Changes:**
- Changed slash handling from " slash " to " " (space) - slashes are now silent
- Removed '/' from symbol_words_map in phonemizer_preprocessor.py

## Task 5: Optimization Analysis
**File:** `docs/OPTIMIZATION_REPORT.md`
**Status:** COMPLETED
**Changes:**
- Created comprehensive analysis report with 34 identified issues
- 4 critical, 8 high, 12 medium, 10 low severity
- Covers: performance, quality, architecture, testing gaps
- Kokoro ONNX limitations documented

### Critical Issues Identified:
1. Voice embedding cache unbounded growth (engine.py:279-327)
2. Phoneme truncation without notification (patches.py:211-213)
3. Pipeline parallelism dead code (engine.py:976-1090)
4. ONNX input validation missing (engine.py:439-482)

### High Priority Issues:
1. Tokenization cache key missing parameters (engine.py:299)
2. Audio quality enhancer disabled (audio_quality_enhancer.py:176-197)
3. Emotion controller non-deterministic indexing (emotion_controller.py:168-179)
4. Voice vector bounds edge case (patches.py:224-231)
5. ThreadPoolExecutor contention on ONNX (engine.py:885)
