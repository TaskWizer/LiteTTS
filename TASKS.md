# Tasks - TTS Pronunciation Fixes

## Task 1: Fix phonemizer_preprocessor.py problematic_patterns
**File:** `LiteTTS/text/phonemizer_preprocessor.py`
**Status:** IN PROGRESS
**Changes:**
- Remove the over-aggressive `(r'([A-Z]{2,})', ...)` pattern that spells out regular words
- Only convert true acronyms (all caps sequences like FBI, NASA)
- Preserve capitalized words like "Directions", "Any", "Know"

## Task 2: Remove fraction slash pattern
**File:** `LiteTTS/text/phonemizer_preprocessor.py`
**Status:** PENDING
**Changes:**
- Remove `(r'\b(\d+)/(\d+)\b', r'\1 slash \2', 'Fractions and dates')` pattern
- Let natural number processing handle fractions

## Task 3: Add pronunciation fixes to clean_text_normalizer.py
**File:** `LiteTTS/nlp/clean_text_normalizer.py`
**Status:** PENDING
**Changes:**
- Add "because": "because" (explicit - no change but prevents other rules from breaking it)
- Add "tests": "tests" (explicit preservation)
- Add "know": "know" (explicit preservation)

## Task 4: Update text_normalizer slash handling
**File:** `LiteTTS/nlp/text_normalizer.py`
**Status:** PENDING
**Changes:**
- Consider removing or modifying slash handling for cleaner speech
