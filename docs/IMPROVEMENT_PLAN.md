# LiteTTS Improvement Plan

**Generated:** 2026-07-17  
**Status:** IN PROGRESS

---

## Executive Summary

This plan addresses gaps, issues, and improvements identified through comprehensive audit.

### Priority Matrix
| Priority | Count | Description |
|----------|-------|-------------|
| CRITICAL | 4 | Must fix immediately |
| HIGH | 8 | Important for stability |
| MEDIUM | 12 | Enhancement opportunities |
| LOW | 10 | Nice to have |

---

## 🔴 CRITICAL Issues

### 1. SSE Streaming Audio Quality
- **Issue:** WAV streaming produces garbled/static audio
- **Root Cause:** Improper WAV header construction for streaming
- **Current State:** Reverted to standard TTS endpoint (no streaming)
- **Fix Needed:** Either fix WAV streaming or implement proper chunked streaming
- **Status:** WORKAROUND in place (standard endpoint works)

### 2. Voice Embedding Cache Unbounded Growth
- **File:** `LiteTTS/tts/engine.py:279-327`
- **Issue:** Global singleton with no eviction policy
- **Impact:** Memory leak potential
- **Fix:** Implement LRU eviction with configurable max size
- **Effort:** Low
- **Status:** ✅ ALREADY FIXED - has LRU eviction with max 100 in synthesis_optimizer.py

### 3. Pipeline Parallelism Dead Code
- **File:** `LiteTTS/tts/engine.py:976-1090`
- **Issue:** References non-existent `self.phonemizer`, `self.vocoder`
- **Impact:** Method always falls back to sequential synthesis
- **Fix:** Remove dead code or implement properly
- **Effort:** Medium
- **Status:** ✅ ALREADY FIXED - no references to non-existent components found

### 4. ONNX Input Validation Missing
- **File:** `LiteTTS/tts/engine.py:439-482`
- **Issue:** No validation that inputs match model requirements
- **Impact:** Potential crashes on invalid input
- **Fix:** Add input validation before inference
- **Effort:** Medium
- **Status:** ✅ ALREADY FIXED - validation exists at lines 473-489

---

## 🟠 HIGH Priority Issues

### 5. Real-time Word Highlighting
- **Issue:** Dashboard uses estimated timing, not actual word timestamps
- **Current:** Word highlighting based on progress percentage
- **Desired:** Actual per-word timing from TTS engine
- **Feasibility:** Kokoro doesn't provide per-word timing natively
- **Workaround:** Use estimated timing (current implementation)

### 6. Test Coverage Gaps
- **Coverage:** 272 phonemizer tests, 6 API tests
- **Missing:** Streaming tests, integration tests, E2E tests
- **Fix:** Add test cases for all major code paths
- **Effort:** Medium

### 7. Cache Hit Rate 0%
- **Issue:** `cache_hit_rate_percent: 0.0` in performance stats
- **Root Cause:** Bug in app.py middleware - `cache_hit` is hardcoded to False and never set to True when cache hits occur
- **Location:** `app.py:450` - `cache_hit = False` is never updated
- **Note:** Audio caching itself IS working (router.py properly caches), but analytics don't record hits
- **Fix:** Pass cache_hit status from router to analytics middleware
- **Effort:** Low
- **Status:** ✅ FIXED - Added X-Cache-Hit header to response_formatter, router passes cache_hit, middleware reads header

### 8. Error Handling Inconsistencies
- **Issue:** Some endpoints return JSON errors, others return plain text
- **Fix:** Standardize error response format
- **Effort:** Low

---

## 🟡 MEDIUM Priority Improvements

### 9. Dashboard UX Enhancement
- **Current:** Basic word highlighting, progress bar
- **Missing:** Better visualizations, voice preview, SSML support
- **Fix:** Add voice preview buttons, SSML input option
- **Effort:** Medium

### 10. Performance Monitoring
- **Current:** Basic RTF and latency tracking
- **Missing:** Memory monitoring, GPU monitoring, trend analysis
- **Fix:** Enhance metrics collection
- **Effort:** Medium

### 11. Documentation
- **Issue:** Some endpoints not documented
- **Fix:** Update API docs
- **Effort:** Low

### 12. Opus Format Not Supported
- **Issue:** Request for `opus` returns validation error
- **Note:** Listed as supported in OpenAI API but not implemented
- **Fix:** Map `opus` to `ogg` internally or implement proper opus support
- **Effort:** Low

---

## 🟢 LOW Priority / Technical Debt

### 13. Code Organization
- **Issue:** `app.py` is 157KB with mixed concerns
- **Fix:** Extract routers into separate modules
- **Effort:** High

### 14. Logging Verbosity
- **Issue:** Some logs too verbose, others missing
- **Fix:** Review and adjust log levels
- **Effort:** Low

### 15. Configuration Management
- **Issue:** Multiple config sources (env, json, cli)
- **Fix:** Consolidate into single source
- **Effort:** Medium

---

## 📋 Implementation Phases

### Phase 1: Critical Fixes (1-2 days)
- [ ] Fix/remove dead code (pipeline parallelism)
- [ ] Add ONNX input validation
- [ ] Implement voice embedding cache eviction
- [ ] Verify and fix cache implementation

### Phase 2: Quality Improvements (2-3 days)
- [ ] Add comprehensive test coverage
- [ ] Standardize error responses
- [ ] Fix Opus format handling
- [ ] Enhance performance monitoring

### Phase 3: Feature Enhancements (3-5 days)
- [ ] Improve dashboard UX
- [ ] Add voice preview functionality
- [ ] Implement proper streaming (if Kokoro supports)
- [ ] Add SSML support

### Phase 4: Polish (2-3 days)
- [ ] Documentation updates
- [ ] Code organization/refactoring
- [ ] Logging review
- [ ] Configuration consolidation

---

## ✅ Completed Work

### Audio Quality
- [x] MP3 format: Working (64kbps, 24kHz)
- [x] WAV format: Working (PCM 16-bit, 24kHz)
- [x] OGG format: Working (Vorbis)
- [x] FLAC format: Working

### API Endpoints
- [x] Health check: Working
- [x] TTS generation: Working
- [x] Voice listing: Working (55 voices)
- [x] Models listing: Working

### Testing
- [x] Phonemizer tests: 272 passing
- [x] API tests: 6 passing

---

## 📊 Metrics Targets

| Metric | Current | Target |
|--------|---------|--------|
| Cache Hit Rate | 0% | >50% |
| Avg RTF | 1.021 | <0.5 |
| Test Coverage | ~60% | >80% |
| API Tests | 6 | >50 |
