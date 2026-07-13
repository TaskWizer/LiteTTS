# TTS Pronunciation Fixes - Implementation Plan

## Phase 1: Fix Acronym/Spelling Issues
- [ ] Modify `phonemizer_preprocessor.py` problematic_patterns to preserve natural capitalized words
- [ ] Add explicit pronunciation rules for common mispronounced words
- [ ] Test fixes with problematic words

## Phase 2: Fix Slash Handling
- [ ] Remove fraction slash pattern from problematic_patterns
- [ ] Adjust text_normalizer slash handling to be less aggressive
- [ ] Add slash removal option for cleaner speech

## Phase 3: Add Pronunciation Fixes
- [ ] Add fixes for "because", "tests", "know" to clean_text_normalizer
- [ ] Add homograph context for there/their/they're
- [ ] Test all pronunciation fixes

## Phase 4: Verification
- [ ] Run TTS with test sentences
- [ ] Verify audio output quality
