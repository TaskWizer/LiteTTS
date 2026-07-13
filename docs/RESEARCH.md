# TTS Pronunciation Issues - Research

## Issues Reported

1. **"Directions" spelled out as "D-I-R-E-C-shaw-N-S"** - letters being spelled out instead of pronounced as word
2. **"any" as "E-N-turn-V"** - same issue
3. **"know" as "now"** - phonemizer confusion
4. **"tests" as "tess"** - missing schwa sound
5. **"because" wrong pronunciation** - phonemizer issue
6. **"God-n-mit" instead of "God Damn It"** - incorrect contraction processing
7. **Slash "/" read as "slash"** - too aggressive symbol handling
8. **Poor sentence pacing** - prosody issues
9. **there/their wrong inflection** - homograph context insufficient

## Root Causes

### 1. Over-aggressive acronym pattern
**File:** `LiteTTS/text/phonemizer_preprocessor.py` line 284
```python
(r'([A-Z]{2,})', lambda m: ' '.join(m.group(1).lower()), 'Acronyms')
```
This converts ANY 2+ uppercase letter sequence to space-separated lowercase letters, including:
- "Directions" → "d i r e c t i o n s" 
- "Any" → "a n y"
- "Know" → "k n o w"

### 2. Fraction slash handling
**File:** `LiteTTS/text/phonemizer_preprocessor.py` line 280
```python
(r'\b(\d+)/(\d+)\b', r'\1 slash \2', 'Fractions and dates')
```
This converts "1/2" to "1 slash 2" instead of natural pronunciation.

### 3. Slash symbol conversion
**File:** `LiteTTS/nlp/text_normalizer.py` line 132
```python
(r'(?<!w)\s*/\s*', ' slash ')
```
Converts "/" to "slash" in most contexts.

### 4. Missing pronunciation fixes
No explicit rules for common problematic words like:
- "because" - often mispronounced
- "tests" - 'e' dropped
- "know" - confused with "now"

## Affected Components

1. `LiteTTS/text/phonemizer_preprocessor.py` - problematic_patterns
2. `LiteTTS/nlp/text_normalizer.py` - symbol_patterns
3. `LiteTTS/nlp/clean_text_normalizer.py` - pronunciation_fixes
4. `LiteTTS/nlp/homograph_resolver.py` - context patterns

## Severity Assessment

- **Critical**: Acronym pattern is breaking common words like "Directions", "Any"
- **High**: Slash handling is too aggressive
- **Medium**: Missing pronunciation fixes for common words
- **Low**: Prosody/pacing issues
