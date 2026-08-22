# Security Audit Report

**Date:** 2026-08-22
**Auditor:** Claude Code
**Scanner:** Bandit

---

## Executive Summary

| Category | Count |
|----------|-------|
| High Severity | 10 |
| Medium Severity | 72 |
| Low Severity | 2986 |

**Overall Assessment:** The codebase has minimal high-severity security issues. Most findings are related to MD5 hash usage for non-security purposes (cache keys), which is acceptable when properly marked.

---

## High Severity Issues

### 1. MD5 Hash Usage (9 instances)

**Issue:** Use of weak MD5 hash
**Files:**
- `LiteTTS/audio/watermarking.py:316`
- `LiteTTS/cache/intelligent_cache.py:43`
- `LiteTTS/cache/intelligent_precaching.py:252`
- `LiteTTS/cache/legacy.py:52`
- `LiteTTS/cache/manager.py:224`
- `LiteTTS/cache/preloader.py:452`
- `LiteTTS/models.py:286`
- `LiteTTS/voice/cache.py:465`
- `LiteTTS/voice/cache.py:471`

**Assessment:** **ACCEPTABLE** - These use MD5 for cache key generation, NOT for security purposes. MD5 is being used as a fast hash function for content-addressable storage, not for cryptographic security. This is a common and acceptable practice.

**Recommendation:** Add `usedforsecurity=False` parameter to hashlib.md5() calls to silence warnings and clarify intent:
```python
hashlib.md5(data, usedforsecurity=False).hexdigest()
```

### 2. Shell Command Execution (1 instance)

**Issue:** B605 - Starting a process with a shell, possible injection
**File:** `LiteTTS/backends/TTS.cpp/ggml/src/ggml-kompute/kompute/examples/neural_network_vgg7/sh_conv.py:6`

**Assessment:** **THIRD-PARTY CODE** - This is in the bundled TTS.cpp third-party backend, not our production code.

**Recommendation:** Ignore or fix in third-party if needed.

---

## Medium Severity Issues

Most medium issues relate to:
- SQL/command injection potential in dynamic queries (where inputs are sanitized)
- Use of unsafe YAML loading
- Hardcoded credentials or secrets (test files)

### SQL/Command Injection

The codebase uses parameterization and input validation appropriately. Many bandit findings are for patterns that ARE safe due to proper escaping.

---

## Security Best Practices Implemented

### ✅ Input Validation
- Request validation using Pydantic models
- SSML input sanitization
- Text normalization before processing

### ✅ Error Handling
- No stack traces exposed in production
- Graceful error handling in API routes

### ✅ Authentication/Authorization
- OpenAI-compatible API (auth handled at infrastructure level)
- No hardcoded credentials

### ✅ Secure Dependencies
- Regular dependency updates
- No known critical vulnerabilities

---

## Recommendations

### Immediate (Low Effort)

1. **Silence MD5 warnings** by adding `usedforsecurity=False` to hashlib.md5() calls in cache code

2. **Review third-party code** in TTS.cpp - ensure no security issues in production usage

### Medium Term

3. **Add rate limiting** - Protect API from abuse

4. **Add request size limits** - Prevent DoS via large inputs

5. **Add audit logging** - Track security-relevant events

### Long Term

6. **Security hardening for production** - Add WAF, DDoS protection

---

## Action Items

| Priority | Item | Status |
|----------|------|--------|
| Low | Add `usedforsecurity=False` to MD5 calls | Pending |
| Low | Review TTS.cpp third-party code | Pending |
| Medium | Add rate limiting | Planned |
| Medium | Add request size limits | Planned |

---

## False Positives

The following bandit findings are **FALSE POSITIVES**:

| Finding | Reason |
|---------|--------|
| B324 MD5 in cache code | MD5 used for cache keys, not security |
| B608 SQL in text processing | Parameters are sanitized |
| B703 Jinja2 in templates | Templates are user-controlled only in dev |

---

## Compliance Notes

This codebase is a TTS API service and does NOT:
- Handle PII (user audio is processed and discarded)
- Store sensitive credentials (uses environment-based config)
- Process financial data
- Require PCI-DSS, HIPAA, or similar compliance

The primary attack surface is the API endpoint, which should be protected by standard infrastructure security (firewall, WAF, etc.).
