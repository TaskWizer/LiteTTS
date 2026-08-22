# ADR-003: Voice Embedding Format

**Status:** Accepted
**Date:** 2026-07-15

## Context

Kokoro TTS engine uses voice embeddings to control voice characteristics. The embedding format has evolved and there are multiple shape handling cases in the code.

## Decision

Standardize on VoiceEmbedding class with guaranteed shape contract.

## Current State

The code handles 6 different voice embedding shapes:
1. `(1, 256)` - Standard format
2. `(256,)` - Flattened
3. `(1, 512)` - Double width
4. `(2, 256)` - Two voices
5. `(n, 256)` - Multiple voices
6. Other - Fallback

## Target State

```python
@dataclass
class VoiceEmbedding:
    embedding_data: np.ndarray  # Shape: (1, 256)
    voice_name: str
    metadata: Dict[str, Any]

    @property
    def shape(self) -> Tuple[int, int]:
        return (1, 256)
```

## Rationale

**Pros:**
- Clear contract for callers
- Easier debugging
- Type safety

**Cons:**
- Refactoring effort
- May break existing code

## Consequences

### Breaking Change
This is a v2.0 change that requires:
1. Update all callers to use new interface
2. Add deprecation warnings
3. Migration guide

---

## Related

- [ADR-002: Caching Strategy](./ADR-002-caching.md)
