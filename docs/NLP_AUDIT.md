# NLP Processor Audit - Overlap and Duplication Analysis

**Date:** 2026-08-23
**Purpose:** Document NLP processor overlap and identify consolidation opportunities

---

## Identified Processor Groups with Overlap

### 1. Contraction Processors (3 overlapping)

| Processor | Purpose | Status |
|-----------|---------|--------|
| `enhanced_contraction_processor` | Standard contraction expansion | Legacy |
| `enhanced_contraction_processor_v2` | Improved contraction expansion | Active |
| `contraction_pronunciation_fix` | Fixes "I'm" → "im" pronunciation issue | Active |

**Recommendation:** Keep `enhanced_contraction_processor_v2` as primary, merge `contraction_pronunciation_fix` logic into it since the pronunciation fix is a subset of contraction handling.

### 2. Symbol Processors (2 overlapping)

| Processor | Purpose | Status |
|-----------|---------|--------|
| `advanced_symbol_processor` | Standard symbol processing | Active |
| `espeak_enhanced_symbol_processor` | eSpeak-enhanced symbol processing | Beta |

**Recommendation:** `espeak_enhanced_symbol_processor` extends `advanced_symbol_processor`. Since espeak is optional, keep both but ensure `advanced_symbol_processor` works as fallback.

### 3. Interjection Processors (2 overlapping)

| Processor | Purpose | Status |
|-----------|---------|--------|
| `interjection_processor` | Basic interjection handling | Legacy |
| `interjection_fix_processor` | Fixes interjection pronunciation | Active |

**Recommendation:** Merge `interjection_processor` into `interjection_fix_processor` since the fix processor provides superset of functionality.

### 4. Date/Time Processors (2)

| Processor | Purpose | Status |
|-----------|---------|--------|
| `enhanced_datetime_processor` | Comprehensive datetime handling | Active |
| `dynamic_emotion_intonation` | Adds emotion to datetime references | Active |

**Note:** These are complementary, not overlapping. `enhanced_datetime_processor` handles parsing, `dynamic_emotion_intonation` handles prosody.

### 5. Pronunciation Dictionaries (3)

| Processor | Purpose | Status |
|-----------|---------|--------|
| `pronunciation_dictionary` | Basic pronunciation lookup | Active |
| `extended_pronunciation_dictionary` | Extended lookup with IPA | Active |
| `phonetic_dictionary_manager` | Manages multiple dictionaries | Active |

**Recommendation:** `phonetic_dictionary_manager` is the orchestrator. `extended_pronunciation_dictionary` extends `pronunciation_dictionary`. This is intentional layering, not duplication.

---

## Processor Categories

### Text Normalization (Core)
- `text_normalizer` - Main text normalization
- `clean_text_normalizer` - Post-processing cleanup
- `context_adapter` - Context-aware normalization

### Contraction Handling
- `enhanced_contraction_processor_v2` - Primary (recommended)
- `contraction_pronunciation_fix` - Pronunciation-specific (subset)

### Symbol Processing
- `advanced_symbol_processor` - Standard symbols
- `espeak_enhanced_symbol_processor` - eSpeak-enhanced (optional)

### Interjection/Filler
- `interjection_fix_processor` - Primary (recommended)
- `interjection_processor` - Legacy, can be deprecated

### Date/Time
- `enhanced_datetime_processor` - Primary datetime handling

### Currency/Financial
- `advanced_currency_processor` - Primary financial processing

### Phonetic/IPA
- `phonetic_processor` - Phonetic alphabet and IPA
- `advanced_phonetic_mapping` - Extended phonetic mapping
- `homograph_resolver` - Disambiguates homographs

### Proper Names
- `proper_name_pronunciation_processor` - Name pronunciation

### Ticker Symbols
- `ticker_symbol_processor` - Stock symbol handling

### Spell Processing
- `spell_processor` - Spell-out mode for abbreviations

### Prosody/Emotion
- `dynamic_emotion_intonation` - Emotion-based intonation
- `prosody_analyzer` - Prosody analysis
- `emotion_detector` - Emotion detection
- `voice_modulation_system` - Voice quality modulation

### Context Analysis
- `llm_context_analyzer` - LLM-based context (optional)

---

## Consolidation Plan

### Phase 1: Deprecate Legacy Processors (Low Risk)
1. Mark `interjection_processor` as deprecated, redirect to `interjection_fix_processor`
2. Mark `enhanced_contraction_processor` as deprecated, redirect to `enhanced_contraction_processor_v2`

### Phase 2: Merge Contraction Logic (Medium Risk)
1. Merge `contraction_pronunciation_fix` into `enhanced_contraction_processor_v2`
2. Update `unified_text_processor` to use only `enhanced_contraction_processor_v2`

### Phase 3: Symbol Processor Integration (Medium Risk)
1. Ensure `advanced_symbol_processor` can work standalone
2. Make `espeak_enhanced_symbol_processor` additive when available

---

## Files to Modify for Consolidation

1. `LiteTTS/nlp/interjection_processor.py` - Add deprecation warning, delegate to `interjection_fix_processor`
2. `LiteTTS/nlp/enhanced_contraction_processor.py` - Add deprecation warning, delegate to `v2`
3. `LiteTTS/nlp/contraction_pronunciation_fix.py` - Merge logic into `enhanced_contraction_processor_v2`
4. `LiteTTS/nlp/unified_text_processor.py` - Update imports to use consolidated processors

---

## Risk Assessment

| Change | Risk | Reason |
|--------|------|--------|
| Deprecate interjection_processor | Low | Simple delegation |
| Deprecate enhanced_contraction_processor | Low | Simple delegation |
| Merge contraction_pronunciation_fix | Medium | Could change behavior |
| Merge interjection processors | Medium | Could change behavior |

**Recommendation:** Execute Phase 1 (deprecations) now. Schedule Phase 2-3 for after testing.
