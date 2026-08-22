# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for LiteTTS.

## About ADRs

ADRs document significant architectural decisions, including:
- The context and problem being addressed
- The decision that was made
- The rationale behind the decision
- The consequences (positive and negative)

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| ADR-001 | Multi-Stage Text Processing Pipeline | Accepted | 2026-07-15 |
| ADR-002 | Caching Strategy | Accepted | 2026-07-15 |
| ADR-003 | Voice Embedding Format | Accepted | 2026-07-15 |

## Creating New ADRs

1. Copy `ADR-XXX-template.md` to `ADR-XXX-title.md`
2. Fill in the template
3. Update this index

## ADR Template

```markdown
# ADR-XXX: Title

**Status:** Proposed|Accepted|Deprecated|Superceded
**Date:** YYYY-MM-DD

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that is being proposed?

## Rationale
Why is this decision being made?

## Consequences
What becomes easier or more difficult because of this change?
```

---

For questions about ADRs, please open a discussion on GitHub.
