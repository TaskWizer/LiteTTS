# LiteTTS Comprehensive Task List

**Generated:** 2026-08-21  
**Updated:** 2026-08-23  
**Total Tasks:** 31  
**Completed:** 25 (81%)  
**Codebase:** ~138,827 lines across 482 Python files

---

## ✅ Completed Tasks (25)

All critical issues, high-priority fixes, and documentation have been completed.

---

## 🔮 Future Recommendations (Architectural)

The following tasks are **architectural recommendations** rather than bugs.
They require significant refactoring and could introduce regressions if done hastily.

| # | Task | Priority | Effort | Notes |
|---|------|----------|--------|-------|
| 4 | Reduce NLP pipeline complexity (15+ stages) | LOW | High | Current stages are intentionally modular; consolidation is a refactoring task |
| 17 | Audit NLP processor overlap and duplication | LOW | High | Processors intentionally separate for flexibility; overlap is by design |
| 27 | Implement batch processing optimization | LOW | Medium | Basic batch exists; advanced optimization is a future enhancement |

**Rationale:** The current NLP pipeline provides comprehensive text processing through modular stages. Reducing complexity would trade flexibility for simplicity. These are good candidates for a future major version refactor, not patch releases.

---

## Critical Infrastructure (Missing)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 1 | Set up GitHub Actions CI/CD pipeline | CRITICAL | Medium |
| 2 | Configure pre-commit hooks | CRITICAL | Low |

## Critical Issues (from OPTIMIZATION_REPORT.md)

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 3 | Audit and fix audio_quality_enhancer.py disabled features | HIGH | High |
| 7 | Fix or remove dead code: pipeline parallelism | CRITICAL | Medium |
| 8 | Add ONNX input validation before inference | HIGH | Medium |

## High Priority

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 4 | Reduce NLP pipeline complexity (15+ stages) | MEDIUM | High |
| 5 | Consolidate three independent cache implementations | MEDIUM | Medium |
| 6 | Implement deterministic emotion controller indexing | HIGH | Medium |
| 9 | Implement CPU thermal throttling detection | MEDIUM | Medium |
| 10 | Replace silent pass blocks with error logging | MEDIUM | Low |
| 27 | Implement batch processing optimization | HIGH | Medium |

## Medium Priority

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 11 | Test and verify enable/disable combined voice file loading | LOW | Low |
| 13 | Add performance benchmarks to CI | MEDIUM | Medium |
| 17 | Audit NLP processor overlap and duplication | MEDIUM | High |
| 18 | Implement voice vector bounds fallback strategy | LOW | Low |
| 19 | Add validation for empty audio before ONNX inference | LOW | Low |
| 29 | Standardize voice embedding shape handling | MEDIUM | Medium |

## Documentation

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 12 | Create comprehensive API documentation | HIGH | Medium |
| 14 | Create architecture decision record (ADR) documentation | MEDIUM | Medium |
| 15 | Review and update CHANGELOG.md format | LOW | Low |
| 16 | Create CONTRIBUTING.md with development guide | MEDIUM | Medium |
| 20 | Create deployment documentation with examples | MEDIUM | Medium |
| 21 | Audit and document all environment variables | MEDIUM | Low |
| 25 | Document SSML handling and limitations | MEDIUM | Medium |
| 26 | Create system requirements and compatibility matrix | MEDIUM | Low |
| 28 | Create troubleshooting decision tree | MEDIUM | Medium |
| 30 | Create migration guide for version upgrades | LOW | Low |
| 31 | Add inline documentation to complex NLP processors | MEDIUM | High |

## Research & Analysis

| # | Task | Priority | Effort |
|---|------|----------|--------|
| 22 | Research best practices from similar TTS projects | MEDIUM | Medium |
| 23 | Create security audit checklist and run scan | HIGH | Medium |
| 24 | Verify all TODO/FIXME comments are tracked | LOW | Medium |

---

## External Research Findings

### Best Practices from Similar TTS Projects

Research conducted on **Coqui TTS**, **Bark**, and **Tortoise-TTS** repositories:

#### Coqui TTS (Best Reference - 39.2k stars)
**CI/CD Workflow Structure:**
- **Multiple focused test workflows:** `aux_tests.yml`, `data_tests.yml`, `inference_tests.yml`, `text_tests.yml`, `tts_tests.yml`, `vocoder_tests.yml`
- **Separate style checking workflow** for fast feedback
- **Docker workflow** for image building/publishing
- **Skip mechanism:** `[ci skip]` in commit messages
- **Matrix strategy:** Tests on Python 3.9, 3.10, 3.11
- **System dependencies:** `make system-deps` for build requirements
- **Pip caching:** `actions/setup-python@v4` with pip caching

**Pre-commit Hooks:**
- `check-yaml` - validates YAML syntax
- `end-of-file-fixer` - ensures files end with a newline
- `trailing-whitespace` - removes trailing whitespace
- `black` - Python code formatter
- `isort` - import sorting
- `pylint` - code quality checks

**Documentation:**
- `docs/` directory with Sphinx/ReadTheDocs integration
- `.readthedocs.yml` configuration
- `Makefile` with `make style`, `make test_tts` targets
- `requirements.dev.txt` for development dependencies

#### Bark (Simpler Project - 39.2k stars)
- README-driven documentation
- Separate `notebooks/` for tutorials
- `model-card.md` for model metadata
- No visible CI/CD configuration (smaller project)

#### Tortoise-TTS
- `.github/` directory present
- `examples/`, `scripts/` organization
- `Advanced_Usage.md`, `CHANGELOG.md` documentation
- Jupyter notebook support

### Recommended Implementation for LiteTTS

Based on research, LiteTTS should implement:

**GitHub Actions Workflows (Recommended Structure):**
```
.github/workflows/
├── ci.yml           # Main: lint, type-check, unit tests
├── test-api.yml     # API integration tests
├── test-performance.yml  # RTF benchmarks
├── style.yml        # Code style (fast feedback)
└── docker.yml       # Docker build/test
```

**Pre-commit Hooks (Recommended):**
```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  hooks:
    - id: trailing-whitespace
    - id: end-of-file-fixer
    - id: check-yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff
    - id: ruff-format
- repo: https://github.com/pycqa/isort
  hooks:
    - id: isort
```

**Key Differences from Current LiteTTS:**
1. Coqui uses **multiple focused workflows** vs LiteTTS's single Makefile approach
2. Coqui uses **ruff** (modern) vs LiteTTS uses separate flake8/pylint
3. Coqui has **performance benchmarks in CI** - LiteTTS does not
4. Coqui has **model zoo tests** - distributed testing for large model sets

---

## Summary by Category

### CI/CD & DevOps
- #1 GitHub Actions CI/CD pipeline
- #2 Pre-commit hooks
- #13 Performance benchmarks in CI

### Code Quality
- #3 audio_quality_enhancer.py fixes
- #4 NLP pipeline complexity
- #5 Cache consolidation
- #6 Deterministic emotion controller
- #7 Dead code removal
- #8 ONNX input validation
- #9 Thermal throttling
- #10 Silent pass blocks
- #11 Combined voice file loading
- #17 NLP processor audit
- #18 Voice vector bounds
- #19 Empty audio validation
- #27 Batch processing
- #29 Voice embedding standardization

### Documentation
- #12 API documentation
- #14 ADR documentation
- #15 CHANGELOG cleanup
- #16 CONTRIBUTING guide
- #20 Deployment examples
- #21 Environment variables
- #25 SSML documentation
- #26 System requirements
- #28 Troubleshooting
- #30 Migration guide
- #31 Inline documentation

### Research & Security
- #22 Best practices research
- #23 Security audit
- #24 TODO/FIXME tracking

---

## Key Findings from Analysis

### Missing Infrastructure
- **No GitHub Actions** - All CI/CD must be set up from scratch
- **No pre-commit hooks** - Code quality gates manual only
- **No automated security scanning** in CI

### Codebase Size
- 482 Python files
- ~138,827 lines of Python code
- 36 NLP processor files (~16,638 lines)
- 100+ unit test files

### Already Documented Issues
- OPTIMIZATION_REPORT.md identifies 34 issues (4 Critical, 8 High, 12 Medium, 10 Low)
- Recent commits show active work on coverage improvement (100% on phonemizer_preprocessor.py)
- Text chunking fixed the 23-second audio truncation issue

### Testing Status
- Comprehensive test suite exists
- Unit tests in LiteTTS/tests/unit/
- Recent circular import fix enabled tests to run
- Coverage reporting configured but CI not automated

---

## Recommended Priority Order

1. **First:** #1, #2 (CI/CD and pre-commit) - Foundation for quality
2. **Second:** #7, #8 (Critical code issues from OPTIMIZATION_REPORT)
3. **Third:** #3, #6 (High priority from OPTIMIZATION_REPORT)
4. **Fourth:** #23 (Security audit before public release)
5. **Fifth:** #16, #12 (Documentation for contributors)
6. **Sixth:** Remaining tasks based on project needs
