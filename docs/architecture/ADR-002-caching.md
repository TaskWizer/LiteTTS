# ADR-002: Caching Strategy

**Status:** Accepted
**Date:** 2026-07-15

## Context

LiteTTS has three independent cache implementations:
1. `LiteTTS/cache/manager.py` - EnhancedCacheManager
2. `LiteTTS/voice/cache.py` - VoiceCache
3. `LiteTTS/performance/synthesis_optimizer.py` - Various caches

## Decision

Maintain three caches for now but document the consolidation plan for future refactoring.

## Rationale

**Current State:**
- Each cache serves a specific purpose (voice, synthesis, general)
- Separation provides isolation
- Consolidating requires significant refactoring

**Future State:**
- Unified cache interface with tags
- Shared eviction policies
- Better memory management

## Cache Inventory

| Cache | Purpose | Eviction | Key |
|-------|---------|----------|-----|
| Voice Embedding | Store computed voice embeddings | LRU (100) | voice_name |
| Tokenization | Pre-processed text tokens | LRU (1000) | text:voice |
| Audio | Generated audio | LRU | text:voice:speed |
| Voice Discovery | Voice metadata | Time-based | - |

## Consequences

### Current Limitations
- No unified cache invalidation
- Memory unbounded if not properly configured
- Multiple cache keys for same data

### Future Improvements
- Single eviction policy
- Unified metrics
- Better resource management

## Recommendations

1. Add cache metrics to monitoring dashboard
2. Implement cache size limits for all caches
3. Consider consolidating in v2.0

---

## Related

- [ADR-001: Text Processing Pipeline](./ADR-001-text-processing-pipeline.md)
