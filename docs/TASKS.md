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
