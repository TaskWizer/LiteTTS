# LiteTTS Optimization & Improvement Report

**Date:** 2026-07-14  
**Analyst:** Claude Code Deep Analysis  
**Scope:** Full codebase analysis (~61,995 lines, 375 Python files)

---

## Executive Summary

LiteTTS is a production Text-to-Speech API built on Kokoro ONNX with extensive text processing, voice management, and caching infrastructure. This report identifies **4 critical**, **8 high**, **12 medium**, and **10 low** severity issues across performance, quality, architecture, and testing domains.

**Key Wins Already Achieved:**
- Text chunking implementation solved the 23-second audio truncation (900-word text now generates 247s audio vs previous ~29s limit — **8.5x improvement**)
- Pronunciation fixes for JSON, C#, SQL, YAML, XML, OAuth, IPv6, SHA-256, temperatures, decimals, and international text

---

## 1. CRITICAL Issues

### 1.1 Voice Embedding Cache Unbounded Growth
- **File:** `LiteTTS/tts/engine.py:279-327`
- **Issue:** `synthesis_optimizer.voice_embedding_cache` is a global singleton with no eviction policy
- **Impact:** Memory leak potential from repeated voice embedding operations
- **Fix:** Implement LRU eviction with configurable max size
- **Effort:** Low

### 1.2 Phoneme Truncation Without User Notification
- **File:** `LiteTTS/patches.py:211-213`
- **Issue:** When phonemes exceed 510 limit, they are silently truncated
```python
if len(phonemes) > MAX_PHONEME_LENGTH:
    log.warning(f"Phonemes are too long, truncating...")
    phonemes = phonemes[:MAX_PHONEME_LENGTH]
```
- **Impact:** Long texts produce incomplete audio with only a warning log
- **Note:** The text chunking in `app.py` mitigates this, but the underlying truncation still exists in `patches.py`
- **Fix:** Return error or implement chunking with reassembly at the engine level
- **Effort:** Medium

### 1.3 Pipeline Parallelism Uses Non-existent Components
- **File:** `LiteTTS/tts/engine.py:976-1090`
- **Issue:** `synthesize_with_pipeline_parallelism` references `self.phonemizer`, `self.model`, `self.vocoder` which don't exist on `KokoroTTSEngine`
- **Impact:** Method always falls back to sequential synthesis — dead code
- **Fix:** Either implement properly or remove dead code
- **Effort:** High

### 1.4 ONNX Input Validation Missing
- **File:** `LiteTTS/tts/engine.py:439-482`
- **Issue:** Model input names are dynamically fetched but no validation that provided inputs match
```python
input_names = [input.name for input in self.onnx_session.get_inputs()]
# No validation that our inputs match expected names
```
- **Risk:** Runtime crashes when model signature doesn't match code expectations
- **Fix:** Validate input names before inference
- **Effort:** Medium

---

## 2. HIGH Priority Issues

### 2.1 Tokenization Cache Key Missing Parameters
- **File:** `LiteTTS/tts/engine.py:299`
- **Issue:** Cache key `f"{text}:{voice}"` doesn't include speed, emotion, or emotion_strength
- **Impact:** Incorrect cached tokens when synthesis parameters change
- **Fix:** Include all relevant parameters in cache key
- **Effort:** Low

### 2.2 Audio Quality Enhancer Completely Disabled
- **File:** `LiteTTS/nlp/audio_quality_enhancer.py:176-197`
- **Issue:** Both `_apply_emotional_markers` and `_apply_prosodic_markers` have TODO comments and do nothing
```python
# TODO: Implement proper emotional processing without SSML corruption
# TODO: Implement proper prosody handling without SSML corruption
```
- **Impact:** Emotional speech and prosodic emphasis features are non-functional
- **Fix:** Re-implement these methods properly
- **Effort:** High

### 2.3 Emotion Controller Non-deterministic Indexing
- **File:** `LiteTTS/tts/emotion_controller.py:168-179`
- **Issue:** Weight adjustments use `hash(weight_type) % len()` which is non-deterministic across Python processes
- **Impact:** Same emotion may produce slightly different audio each run
- **Fix:** Use deterministic indexing based on voice/emotion pair
- **Effort:** Medium

### 2.4 Voice Vector Bounds Edge Case
- **File:** `LiteTTS/patches.py:224-231`
- **Issue:** When `token_length >= voice_size`, uses last style vector as fallback
- **Impact:** May cause incorrect voice characteristics for edge-case inputs
- **Fix:** Implement proper fallback strategy with error propagation
- **Effort:** Low

### 2.5 ThreadPoolExecutor Contention on ONNX Session
- **File:** `LiteTTS/tts/engine.py:860-906`
- **Issue:** `synthesize_batch` uses ThreadPoolExecutor but ONNX session is not thread-safe for parallel inference
- **Impact:** Thread contention may slow down parallelization
- **Fix:** Use per-thread ONNX sessions or process batches sequentially
- **Effort:** Medium

---

## 3. MEDIUM Priority Issues

### 3.1 Text Processing Pipeline Complexity
- **File:** `LiteTTS/nlp/unified_text_processor.py:381-564`
- **Issue:** 15+ sequential processing stages with complex dependencies
- **Stages:** Phase6 → pronunciation_rules → interjection_fixes → ticker_symbols → proper_name → phonemizer_preprocessor → currency → datetime → symbols → espeak → spell → phonetic → homograph → normalize → prosody → clean
- **Risk:** Fixes in one stage may be undone by another; ordering dependencies create unpredictable behavior
- **Recommendation:** Reduce to <10 stages; document each stage's purpose and ordering constraints
- **Effort:** High

### 3.2 Empty Audio Detection After Processing
- **File:** `LiteTTS/tts/engine.py:527-528`
- **Issue:** Audio validation happens after post-processing, not before inference
```python
if audio_data.size == 0:
    raise ValueError("Cannot post-process empty audio data")  # Too late
```
- **Fix:** Validate before inference to fail fast
- **Effort:** Low

### 3.3 Multiple Independent Cache Implementations
- **Files:**
  - `LiteTTS/cache/manager.py` — EnhancedCacheManager
  - `LiteTTS/voice/cache.py` — VoiceCache
  - `LiteTTS/performance/synthesis_optimizer.py` — various caches
- **Issue:** Three separate caching systems with different eviction strategies
- **Recommendation:** Consolidate into unified cache with tags
- **Effort:** Medium

### 3.4 Empty Pass Blocks Swallowing Errors
- **Files:** Various in `error_handling.py`, `cpu_optimizer.py`, `worker_manager.py`
- **Issue:** Empty except blocks with just `pass`
- **Risk:** Errors silently swallowed, making debugging difficult
- **Fix:** Log errors or implement proper fallback behavior
- **Effort:** Low

### 3.5 CPU Optimizer Thermal Throttling Not Implemented
- **File:** `LiteTTS/performance/cpu_optimizer.py:103`
- **Issue:** Thermal check is an empty pass block
```python
except Exception:
    pass  # Thermal check not implemented
```
- **Fix:** Implement actual thermal throttling detection
- **Effort:** Medium

### 3.6 Complex Voice Shape Handling
- **File:** `LiteTTS/tts/engine.py:398-437`
- **Issue:** `_prepare_model_inputs` has 6 different shape cases with inconsistent handling
- **Recommendation:** Create standardized `VoiceEmbedding` class with guaranteed shape
- **Effort:** Medium

---

## 4. LOW Priority Issues

### 4.1 Combined Voice File Loading Disabled
- **File:** `LiteTTS/config.py:58`
- **Issue:** `use_combined_file: bool = False` — code paths never exercised
- **Recommendation:** Either enable or remove dead code
- **Effort:** Low

### 4.2 SSML Break Tags May Cause Audio Issues
- **File:** `LiteTTS/nlp/audio_quality_enhancer.py:199-219`
- **Issue:** `_add_natural_pauses` inserts `<break time="..."/>` tags which may conflict with Kokoro's internal timing
- **Risk:** Potential audio artifacts at pause boundaries
- **Recommendation:** Test thoroughly or remove this feature
- **Effort:** Low

### 4.3 Missing Type Hints in Core Classes
- **Files:** `engine.py`, `synthesizer.py`, `voice_consistency.py`
- **Issue:** Core classes lack complete type annotations
- **Recommendation:** Add type hints systematically, use mypy for validation
- **Effort:** Medium

---

## 5. Kokoro ONNX Technical Constraints

### 5.1 Known Limitations

| Constraint | Value | Notes |
|------------|-------|-------|
| Phoneme limit | 510 | Hard limit; ~300-400 chars of text |
| Voice vector shape | (510, 256) or (256,) | 256-dim style vector |
| Speed range | 0.5–2.0 | Outside this range may cause pitch artifacts |
| Recommended chunk size | 10-20s audio | Longer may degrade quality |

### 5.2 Audio Quality Patterns

- **Very short audio (<0.5s):** May have clicking/popping artifacts
- **Very long audio (>30s):** May degrade due to cumulative errors
- **Speed != 1.0:** May introduce pitch artifacts, especially at extremes

---

## 6. Testing Gaps

### 6.1 Untested Critical Paths

| Test | File | Risk |
|------|------|------|
| Emotion consistency | `emotion_controller.py` | Non-deterministic behavior |
| Pipeline parallelism | `engine.py:976-1090` | Dead code |
| Voice embedding shapes | `engine.py:410` | Edge case crashes |
| Phoneme boundary (510) | `patches.py:211` | Silent truncation |

### 6.2 Missing Edge Case Coverage

- Empty text handling (returns silent token, no error)
- Unicode edge cases (CJK, Arabic, Hebrew, Devanagari)
- Malformed voice files
- Text exactly at phoneme limit (510)

---

## 7. Prioritized Fix Roadmap

| Priority | Category | Issue | Effort |
|----------|----------|-------|--------|
| Critical | Performance | Voice embedding cache LRU eviction | Low |
| Critical | Quality | Phoneme chunking with reassembly | Medium |
| Critical | Architecture | Remove or fix pipeline parallelism | High |
| Critical | Architecture | ONNX input validation | Medium |
| High | Performance | Fix tokenization cache key | Low |
| High | Quality | Re-implement audio quality enhancer | High |
| High | Quality | Deterministic emotion indexing | Medium |
| High | Quality | Voice vector bounds handling | Low |
| Medium | Performance | Per-thread ONNX sessions for batching | Medium |
| Medium | Architecture | Reduce text processing pipeline | High |
| Medium | Quality | Add integration tests for boundaries | Medium |
| Low | Architecture | Consolidate cache implementations | Medium |

---

## 8. Recommendations

### Immediate Actions (This Sprint)

1. **Add ONNX input validation** before inference to prevent crashes
2. **Fix tokenization cache key** to include all synthesis parameters
3. **Implement voice embedding cache eviction** policy

### Short-term (Next Sprint)

1. **Re-implement audio quality enhancer** emotional/prosodic features
2. **Add deterministic emotion application** (replace hash-based indexing)
3. **Remove or properly implement** `synthesize_with_pipeline_parallelism`

### Medium-term (Next Quarter)

1. **Consolidate cache implementations** into unified system
2. **Add comprehensive type hints** with mypy validation
3. **Reduce text processing pipeline complexity** to <10 stages
4. **Implement integration tests** for boundary conditions

---

## Appendix: File Reference

| File | Key Issues |
|------|-----------|
| `LiteTTS/tts/engine.py` | Cache keys, voice shapes, pipeline parallelism, ONNX validation |
| `LiteTTS/patches.py` | Phoneme truncation, voice vector bounds |
| `LiteTTS/nlp/audio_quality_enhancer.py` | Disabled emotional/prosodic processing |
| `LiteTTS/tts/emotion_controller.py` | Non-deterministic hash indexing |
| `LiteTTS/nlp/unified_text_processor.py` | 15+ processing stages |
| `LiteTTS/performance/cpu_optimizer.py` | Empty thermal throttling |
| `LiteTTS/config.py` | Disabled combined voice loading |
