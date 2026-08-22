# ADR-001: Multi-Stage Text Processing Pipeline

**Status:** Accepted
**Date:** 2026-07-15

## Context

LiteTTS uses a 15+ stage text processing pipeline to normalize and prepare text for TTS synthesis. This includes:

1. Phase6 text processing
2. Pronunciation rules
3. Interjection fixes
4. Ticker symbols
5. Proper name handling
6. Phonemizer preprocessing
7. Currency processing
8. Date/time processing
9. Symbol processing
10. ESpeak processing
11. Spell processing
12. Phonetic processing
13. Homograph resolution
14. Normalization
15. Prosody analysis
16. Clean normalization

## Decision

We keep the multi-stage pipeline architecture but document each stage's purpose and ordering constraints.

## Rationale

**Pros:**
- Separation of concerns allows independent testing and modification
- Each stage can be optimized or replaced independently
- Complex text transformations are broken into manageable pieces

**Cons:**
- Complexity makes debugging difficult
- Ordering dependencies create unpredictable behavior
- Some stages may undo work of previous stages

## Consequences

### Positive
- Modular design allows component replacement
- Individual stages can be tested in isolation

### Negative
- Debugging requires understanding full pipeline
- Performance overhead from multiple passes
- Risk of stages interfering with each other

## Recommendations

1. Document each stage's purpose and ordering constraints
2. Add logging to track text transformations
3. Consider consolidating to fewer stages (<10)
4. Add integration tests for pipeline ordering

---

## Related

- [ADR-002: Caching Strategy](./ADR-002-caching.md)
- [ADR-003: Voice Embedding Format](./ADR-003-voice-embedding.md)
