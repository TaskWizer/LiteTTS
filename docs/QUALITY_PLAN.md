# LiteTTS Quality Improvement Plan

**Generated:** 2026-08-23
**Status:** In Progress

---

## Executive Summary

This document outlines a comprehensive plan to achieve 99% test coverage, highest code quality, and WCAG 2.1 AAA compliance for the LiteTTS codebase.

---

## Current State Analysis

### Quality Metrics (2026-08-23)

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Test Coverage | 99% | ~9-53%* | ~46-90% |
| Critical Lint Errors | 0 | 0 | ✅ Complete |
| WCAG 2.1 AAA | Full | ~80% | 20% |
| Documentation | 100% | ~85% | 15% |

*Coverage varies by measurement method and environment*

### Coverage by Module (Sample)

| Module | Coverage | Tests |
|--------|----------|-------|
| phonemizer_preprocessor.py | 92-97% | 272 tests |
| json_sanitizer.py | 21% | 0 dedicated tests |
| platform_emojis.py | 40% | 0 dedicated tests |
| Most NLP modules | 0% | No tests |
| Most voice modules | 0% | No tests |

---

## Gap Analysis

### 1. Test Coverage Gaps

**Root Cause:** Test suite is focused on phonemizer_preprocessor.py (272 tests) while most other modules lack dedicated tests.

**Modules Needing Tests:**
- LiteTTS/nlp/* (28 modules, 0% coverage)
- LiteTTS/voice/* (9 modules, 0% coverage)
- LiteTTS/tts/* (4 modules, 0% coverage)
- LiteTTS/utils/* (3 modules, 0-40% coverage)

### 2. Documentation Gaps

**Modules Missing Docstrings:**
- Internal functions (decorator, sync_wrapper, log_start, etc.)
- Some private methods in complex processors

### 3. Linting Gaps (Non-Critical)

| Error | Count | Intentional |
|-------|-------|-------------|
| BLE001 (blind-except) | 476 | Yes - Error handling |
| DTZ005 (datetime.now) | 62 | Yes - Timestamps |
| RUF013 (implicit-optional) | 109 | No - Minor style |
| EXE001 (shebang) | 400+ | Yes - Scripts |

---

## Implementation Plan

### Phase 1: Test Coverage (Week 1-2)

#### 1.1 Identify High-Priority Modules
Priority based on:
- Business criticality (synthesizer, engine, voice)
- Call frequency (router, cache, validation)
- Complexity (NLP processors, audio processing)

**Tier 1 (Critical):**
- [ ] LiteTTS/tts/synthesizer.py
- [ ] LiteTTS/tts/engine.py
- [ ] LiteTTS/voice/manager.py
- [ ] LiteTTS/api/router.py
- [ ] LiteTTS/validation.py

**Tier 2 (High):**
- [ ] LiteTTS/cache/manager.py
- [ ] LiteTTS/cache/interfaces.py
- [ ] LiteTTS/nlp/unified_text_processor.py
- [ ] LiteTTS/nlp/text_normalizer.py

**Tier 3 (Medium):**
- [ ] LiteTTS/voice/discovery.py
- [ ] LiteTTS/voice/loader.py
- [ ] LiteTTS/nlp/phonetic_processor.py

#### 1.2 Test Generation Strategy

1. **Unit Tests:** Mock external dependencies (torch, onnxruntime)
2. **Integration Tests:** Use test fixtures for voice files
3. **Property-Based Tests:** Use hypothesis for text processing

#### 1.3 Coverage Measurement

```bash
# Full coverage report
uv run pytest LiteTTS/tests/ --cov=LiteTTS --cov-report=term-missing --cov-report=html

# Per-module coverage
uv run pytest LiteTTS/tests/ --cov=LiteTTS/tts --cov-report=term
```

### Phase 2: Documentation (Week 2)

#### 2.1 Docstring Coverage

- [ ] All public classes and functions
- [ ] All exception classes
- [ ] All dataclasses and enums
- [ ] Complex algorithm explanations

#### 2.2 API Documentation

- [ ] OpenAPI schema completeness
- [ ] Example requests/responses
- [ ] Error code documentation

### Phase 3: Linting Cleanup (Week 3)

#### 3.1 Fixable Issues

| Error | Count | Fix Approach |
|-------|-------|-------------|
| RUF013 (implicit-optional) | 109 | Add explicit Optional[] |
| SIM102 (collapsible-if) | 36 | Combine conditions |
| SIM118 (in-dict-keys) | 18 | Use `in dict` directly |

#### 3.2 Intentional Patterns (Keep as-is)

- BLE001: Blind except for error handling
- DTZ005: datetime.now() for timestamps
- EXE001: Shebang in scripts

---

## Best Practices Research

### CI/CD Patterns (from Coqui TTS, Tortoise-TTS)

1. **Multiple Focused Workflows:**
   - `ci.yml`: Lint, type-check, unit tests
   - `test-api.yml`: Integration tests
   - `test-performance.yml`: RTF benchmarks
   - `docker.yml`: Image building

2. **Pre-commit Hooks:**
   - trailing-whitespace
   - end-of-file-fixer
   - check-yaml
   - ruff (format + lint)
   - isort

3. **Coverage Enforcement:**
   - Minimum 80% coverage required
   - Coverage reports in PR comments
   - Coverage tracking over time

### Documentation Patterns

1. **README Structure:**
   - Quick start (5 min)
   - Installation options
   - API reference
   - Examples
   - Troubleshooting

2. **Contributing Guide:**
   - Development setup
   - Code style
   - Test requirements
   - PR process

---

## Resource Requirements

### Time Estimate

| Phase | Effort | Duration |
|-------|--------|----------|
| Test Coverage | High | 2-3 weeks |
| Documentation | Medium | 1 week |
| Linting Cleanup | Low | 3-5 days |
| WCAG Completion | Low | 1-2 days |

### Tools Required

- pytest + pytest-cov
- hypothesis (property-based testing)
- ruff (linting)
- mypy (type checking)
- pdoc3 (API documentation)

---

## Success Criteria

1. **Test Coverage:** ≥99% on core modules, ≥80% overall
2. **Critical Lint:** 0 errors
3. **Documentation:** 100% public API documented
4. **WCAG:** Full 2.1 AAA compliance
5. **CI/CD:** All checks passing

---

## Next Steps (Immediate)

1. [ ] Set up CI pipeline with coverage tracking
2. [ ] Add tests for Tier 1 modules
3. [ ] Fix remaining RUF013 warnings
4. [ ] Complete API documentation
5. [ ] Final WCAG audit

---

## Appendix: Coverage Commands

```bash
# Measure coverage
uv run pytest LiteTTS/tests/ --cov=LiteTTS --cov-report=term-missing

# Generate HTML report
uv run pytest LiteTTS/tests/ --cov=LiteTTS --cov-report=html

# Coverage thresholds
uv run pytest --cov=LiteTTS --cov-fail-under=80
```
