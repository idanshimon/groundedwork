# Design — core retrieval baseline

## Context

This is a retroactive baseline. The engine exists and is tested; this change writes down the contract it already honors so `openspec/specs/` reflects shipped reality. No design decisions are being made here that the code doesn't already embody — the "decisions" below are documentation of choices already implemented in v0.1.

## Goals / Non-Goals

**Goals:**
- A canonical spec of v0.1's shipped behavior, split into four capabilities.
- Each requirement maps to behavior the existing test suite already enforces.

**Non-Goals:**
- Any change to behavior, API, dependencies, or tests.
- Specifying roadmap features (hybrid embeddings, compaction, MCP, persistence) — those are separate changes.

## Decisions (as-built, documenting existing implementation)

1. **BM25 with k1=1.5, b=0.75, title weighted 2×.** The shipped scoring. Validated against the reference `rank_bm25` library (top-1 matches on all answerable queries in the 392-doc corpus).

2. **Relevance floor default min_score=0.5.** Corpus-size-robust: keeps real matches and abstains on junk at both 24-doc and 392-doc scale. (Lowered from an earlier 2.0 that was overfit to the toy corpus.)

3. **Grounded-by-default prompt + first-class abstention.** The default system prompt instructs answer-only-from-knowledge; `grounded` is a real return value; on a miss, no knowledge is injected and the caller can skip the model.

4. **Cache-aware assembly via messages().** Stable `[system + prefs]` prefix first, volatile retrieved knowledge last, so prompt-caching endpoints reuse the prefix.

5. **BYOM — never calls a generation model.** The library returns retrieval results and assembled prompts; the model call is the caller's.

6. **Cross-language parity enforced mechanically.** Python and TypeScript run the same `fixtures/nimbus.json`; `bench/parity.py` diffs their output to 9 decimal places against `bench/golden.json`.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Baseline spec drifts from code over time | The existing 73 tests are the live enforcement; the spec references them. Future behavior changes go through their own changes that MODIFY these capabilities. |
| Retroactive spec misstates shipped behavior | Each requirement was written against the actual code + passing tests, not from memory. |

## Open Questions

None — this documents shipped, tested behavior.
