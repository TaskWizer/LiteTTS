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

## Task 6: Optimization Fixes Implemented
**Status:** COMPLETED
**Date:** 2026-07-15

### Completed Fixes:
1. **Tokenization cache key** (engine.py:299)
   - Changed from `f"{text}:{voice}"` to `f"{text}:{voice}:{speed}:{emotion}:{emotion_strength}"`

2. **LRU eviction for all caches** (synthesis_optimizer.py)
   - Added `max_voice_embedding_cache: int = 100`
   - Added `max_tokenization_cache: int = 1000`
   - Changed `voice_embedding_cache`, `tokenization_cache`, `fast_path_cache` from `dict` to `OrderedDict`
   - Implemented LRU eviction in `cache_voice_embedding()`, `cache_tokenization()`, `cache_fast_path_result()`
   - Cache access now calls `move_to_end()` for LRU tracking

3. **Emotion controller deterministic indexing** (emotion_controller.py:168-179)
   - Replaced `hash(weight_type) % len()` with `(idx * 37 + len(weight_type)) % len()`
   - Uses enumerate index for deterministic behavior

4. **Removed dead pipeline parallelism code** (engine.py:976-1090)
   - Removed `synthesize_with_pipeline_parallelism()` method
   - References non-existent `self.phonemizer`, `self.model`, `self.vocoder`

5. **Improved voice vector bounds handling** (patches.py:224-231)
   - Enhanced warning message to be more descriptive
   - Added validation that voice_size should be 510

6. **Enhanced ONNX input validation** (engine.py:439-482)
   - Added validation for empty/missing inputs before inference
   - Added dtype validation (must be numeric)
   - Added shape validation (cannot be scalar)
   - Improved error messages for different failure modes
   - Validates extra inputs (may indicate configuration issues)

## Task 7: Additional Optimization Fixes
**Status:** COMPLETED
**Date:** 2026-07-15

### Completed Fixes:
1. **Audio quality enhancer** (audio_quality_enhancer.py)
   - Reimplemented _apply_emotional_markers with safe <emphasis> tags
   - Reimplemented _apply_prosodic_markers with minimal safe marking
   - Disabled natural_pauses by default (Kokoro handles pauses naturally)
   - Uses word-boundary matching to avoid nested SSML corruption

2. **ThreadPoolExecutor ONNX contention** (engine.py)
   - Added `_inference_semaphore` to limit concurrent ONNX inference calls
   - Added `_inference_lock` for thread-safe state access
   - Semaphore limit based on CPU count: `max(2, cpu_count // 2)`

3. **Documented text processing pipeline** (unified_text_processor.py)
   - Added comprehensive docstring to `_process_enhanced()`
   - Explains Stage Group 1 (Enhanced Processors) vs Stage Group 2 (Core Processing)
   - Documents all 17+ stages and their ordering dependencies

4. **Replaced silent pass blocks** (cpu_optimizer.py)
   - Changed `except Exception: pass` to `except Exception as e: logger.warning(...)`
   - Improved error visibility for debugging

5. **CPU thermal throttling** (cpu_optimizer.py)
   - ALREADY IMPLEMENTED: `get_thermal_status()` method properly detects throttling
   - Uses psutil to get CPU temps, flags >85°C as throttling

6. **Standardized voice embedding shape handling** (engine.py)
   - Created `_normalize_voice_embedding_shape()` helper method
   - Extracted 6-case shape handling into well-documented method
   - Improved _prepare_model_inputs() to use the helper

7. **Type hints added** (engine.py)
   - Added return type hints to void methods: _initialize_chunked_generation,
     _initialize_engine, _load_onnx_model, _load_tokenizer, _init_misaki_g2p,
     _init_kokoro_tokenizer, _setup_voice_system, cleanup

8. **Cache consolidation documented** (synthesis_optimizer.py)
   - Added ARCHITECTURE NOTE documenting the three-cache duplication issue
   - Full consolidation would require significant refactoring

### Remaining Low-Priority Items:
- Combined voice file loading disabled (use_combined_file=False in config.py)
- Full type hint coverage (would require extensive effort across all classes)

## Task 8: Streaming Audio Implementation
**Status:** COMPLETED
**Date:** 2026-07-15

### Completed Implementation:
1. **Router streaming endpoint** (LiteTTS/api/router.py)
   - Added `_handle_streaming_synthesis()` method for low-latency playback
   - Returns `StreamingResponse` that yields audio chunks as they become available
   - Checks `request.stream` flag to enable streaming mode
   - Background caching of complete audio for future requests

2. **Synthesizer streaming method** (LiteTTS/tts/synthesizer.py)
   - Added `synthesize_streaming()` async method
   - Uses `ProgressiveAudioGenerator` for chunked audio generation
   - Yields `ChunkResult` objects with audio data and metadata
   - Falls back to standard synthesis if progressive generator unavailable

3. **Progressive generator fix** (LiteTTS/audio/progressive_generator.py)
   - Fixed `_sync_synthesize()` to pass correct parameters to engine
   - Changed from 4 args (text, voice, response_format, speed) to 3 args (text, voice, speed)

## Task 9: Test Coverage Improvement
**Status:** COMPLETED
**Date:** 2026-07-15

### Critical Bug Fix:
- **Fixed circular import** (LiteTTS/models/__init__.py)
  - Changed from `from models import ...` to dynamic import using importlib
  - This was blocking all unit tests from running

### Unit Tests Added:
| File | Tests | Coverage |
|------|-------|----------|
| test_validators.py | 15 | 100% on validators.py |
| test_phonemizer_preprocessor.py | 28 | 59% on phonemizer_preprocessor.py |
| test_chunking.py | 16 | 100% on chunking.py |
| test_progressive_generator.py | 15 | Tested |
| **Total** | **74** | **Significant improvement** |

### Bug Fixed in progressive_generator:
- Fixed `_should_use_chunking()` using wrong config attribute
- Changed `min_text_length_for_chunking` to `min_chunk_size` (correct attribute name)

