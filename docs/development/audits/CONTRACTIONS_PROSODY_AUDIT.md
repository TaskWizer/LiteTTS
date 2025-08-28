# Contractions and Prosody Handling Audit

## Executive Summary

This audit examines the current text processing system for natural contractions, prosody, and intonation handling. The analysis reveals several configuration conflicts and opportunities for improvement to address user-reported pronunciation issues.

## Current Issues Identified

### 1. Configuration Conflicts

**Problem**: Multiple conflicting configuration sources for contraction handling:
- `config/settings.json`: `"expand_contractions": false`
- `LiteTTS/config.py`: `expand_contractions: bool = True`
- `LiteTTS/config/internal_config.py`: `"expand_contractions": False`

**Impact**: Inconsistent behavior depending on which config is loaded first.

### 2. Contraction Pronunciation Issues

**User-Reported Problems**:
- "wasn't" → "waaasant" (unnatural pronunciation)
- "hmm" → "hum" (incorrect interjection)
- "I'll" → sounds like "ill" instead of "I will"
- "that's" → "hit that" (misprocessing)

**Root Cause**: Current system preserves contractions in natural form but doesn't handle phonetic pronunciation issues at the TTS model level.

### 3. Prosody and Intonation Gaps

**Current State**:
- Question marks detected: ✅ (intensity: 1.2, rising intonation)
- Exclamation marks detected: ✅ (intensity: 1.3, emphasis)
- Hesitation markers detected: ✅ ("hmm" gets hesitation marker)

**Issues**:
- Prosody markers are generated but may not be effectively applied to TTS output
- No validation that intonation changes are audible in generated speech

## Current System Analysis

### Text Processing Pipeline

1. **Phonemizer Preprocessor** (`LiteTTS/text/phonemizer_preprocessor.py`)
   - Handles HTML entities and basic normalization
   - Config: `expand_contractions = False` (preserves natural speech)

2. **Enhanced Contraction Processor** (`LiteTTS/nlp/enhanced_contraction_processor.py`)
   - Supports multiple modes: natural, phonetic, expanded, hybrid
   - Currently defaults to 'hybrid' mode
   - Preserves natural contractions, expands problematic ones

3. **Prosody Analyzer** (`LiteTTS/nlp/prosody_analyzer.py`)
   - Detects punctuation-based prosody (questions, exclamations)
   - Identifies conversational markers (hesitation, breathing)
   - Generates markers but unclear how they affect TTS output

### Configuration Hierarchy

```
Priority Order:
1. config/settings.json (user config)
2. LiteTTS/config.py (performance config)
3. LiteTTS/config/internal_config.py (fallback)
```

## Recommendations

### 1. Resolve Configuration Conflicts

**Action**: Standardize contraction handling configuration
- Use single source of truth in `config/settings.json`
- Remove conflicting settings from other config files
- Implement proper config validation

### 2. Improve Contraction Handling

**Strategy**: Implement selective expansion based on pronunciation quality
- Keep natural contractions that pronounce well: "don't", "can't", "won't"
- Expand problematic contractions: "wasn't" → "was not", "I'll" → "I will"
- Add phonetic spelling for edge cases

### 3. Enhance Prosody Application

**Improvements**:
- Validate that prosody markers actually affect TTS output
- Add prosody strength configuration
- Implement intonation testing framework

### 4. Add Interjection Processing

**Fix for "hmm" → "hum"**:
- Implement interjection-specific processing
- Map "hmm" → "hmmm" (extended form for natural pronunciation)
- Handle other interjections: "uh" → "uhh", "ah" → "ahh"

## Implementation Plan

### Phase 1: Configuration Cleanup (High Priority)
- [ ] Consolidate contraction settings to single config source
- [ ] Remove conflicting configuration entries
- [ ] Add config validation

### Phase 2: Contraction Improvements (High Priority)
- [ ] Update problematic contractions list based on user feedback
- [ ] Implement selective expansion strategy
- [ ] Add pronunciation testing for contractions

### Phase 3: Prosody Enhancement (Medium Priority)
- [ ] Validate prosody marker application to TTS
- [ ] Add configurable prosody strength
- [ ] Implement intonation quality testing

### Phase 4: Interjection Processing (Medium Priority)
- [ ] Add interjection-specific processor
- [ ] Handle "hmm", "uh", "ah" and similar sounds
- [ ] Test natural pronunciation of interjections

## Testing Strategy

### Automated Testing
- Unit tests for each contraction type
- Prosody marker validation
- Configuration consistency checks

### Manual Validation
- Generate audio samples for problematic cases
- A/B testing of different processing modes
- User feedback collection

## Success Metrics

- Contraction pronunciation accuracy > 95%
- Question intonation detection rate > 90%
- Exclamation emphasis detection rate > 90%
- Zero configuration conflicts
- User satisfaction with natural speech patterns

## Next Steps

1. **Immediate**: Fix configuration conflicts
2. **Short-term**: Implement selective contraction expansion
3. **Medium-term**: Enhance prosody application validation
4. **Long-term**: Comprehensive pronunciation quality framework
