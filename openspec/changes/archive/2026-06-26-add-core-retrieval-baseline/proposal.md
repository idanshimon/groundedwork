# Baseline: core retrieval, grounding, and cross-language parity

> **Note on retroactive filing.** This change documents behavior that was BUILT
> and SHIPPED in v0.1 BEFORE OpenSpec was adopted. OpenSpec was added later (the
> roadmap changes were authored first), which left `openspec/specs/` empty — the
> canonical record of "what the system does today" did not exist. This change
> backfills that baseline: it specs the existing, tested engine and is archived
> immediately so `specs/` reflects shipped reality. All implementation tasks are
> already complete (the code exists, 73 tests pass); they are marked `[x]`.

## Why

groundedwork's shipped v0.1 behavior — BM25 retrieval, the relevance floor,
grounding/abstention, cache-aware prompt assembly, and cross-language parity —
has no canonical spec. `openspec/specs/` is empty because the engine predates
OpenSpec adoption. Without a baseline, the four roadmap changes layer on top of
an undocumented foundation, and anyone asking "what does groundedwork actually
guarantee today?" has only the README and the tests, not a spec.

This change captures the as-built contract so the spec catalog is honest:
current behavior documented, roadmap on top of it.

## What Changes

- Document the SHIPPED behavior as four canonical capabilities. No code changes.
- Each requirement reflects what the engine already does and what the existing
  test suite already enforces (73 tests across Python + TypeScript + parity).

## Capabilities

### New Capabilities
- `core-retrieval`: BM25 keyword indexing and relevance-floored working-set retrieval.
- `grounding-abstention`: grounded-by-default prompting and first-class abstention when nothing clears the floor.
- `cache-aware-assembly`: stable `[system + prefs]` prefix first, volatile knowledge last, for prompt-cache reuse.
- `cross-language-parity`: Python and TypeScript produce identical retrieval behavior, enforced by a shared fixture and golden snapshot.

## Cross-language impact

Documentation only — no behavior changes. The capabilities describe behavior
that already lands identically in both languages and is already parity-tested.

## Invariant check

- Parity: this baseline DOCUMENTS the parity invariant; the `cross-language-parity` capability codifies it. ✔
- Safe by default: the `grounding-abstention` capability codifies the safe defaults already shipped. ✔
- BYOM: codified — the spec states groundedwork never calls a generation model. ✔
- Zero runtime dependency: codified in `core-retrieval`. ✔
- Small surface: documents the existing add / retrieve / prompt / messages / ask surface; adds none. ✔

## Impact

- `openspec/specs/{core-retrieval,grounding-abstention,cache-aware-assembly,cross-language-parity}/spec.md` created on archive.
- No source, test, or dependency changes.

## Non-goals

- NOT changing any behavior. This is a documentation baseline of shipped v0.1.
- NOT specifying roadmap features (those are their own changes).
