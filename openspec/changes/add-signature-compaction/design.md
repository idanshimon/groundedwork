# Design — signature compaction

## Context

A code knowledge base is a poor fit for BM25-over-whole-files: bodies dominate the token count and the retrieval signal lives in names (classes, functions, imports). ContextForge solved this for generation by compacting files to signatures. We want the same shrink for retrieval/context, reimplemented cleanly in both our languages.

The hard constraint is the one that governs the whole project: whatever `compact()` does, Python and TypeScript must produce the **same** skeleton for the same input, or the parity harness fails. That rules out leaning on each language's native AST (Python `ast` vs a TS parser would produce different shapes and drag in a dependency). v1 is therefore a shared, heuristic, line-classification algorithm both languages implement identically.

## Goals / Non-Goals

**Goals:**
- A pure, dependency-free `compact(text, lang)` that strips function/method bodies and keeps the structural skeleton.
- Byte-identical output across Python and TypeScript, enforced by a shared fixture.
- Useful on Python and TS/JS source in v1.

**Non-Goals:**
- Semantic correctness of a real parser. Heuristic is acceptable; occasional imperfect strips are fine for a retrieval-context aid.
- AST mode (would be language-specific and dependency-bearing) — explicitly deferred to a possible opt-in extra.
- Any model involvement.

## Decisions

1. **Heuristic line-classification, not AST.** Classify each line as: import, decorator, class/def signature, docstring-first-line, or body. Keep the first four; replace contiguous body runs with a single `...` placeholder line at the body's indentation. Chosen because it is (a) trivially portable to both languages identically, (b) zero-dependency, (c) good enough for the retrieval-context goal. AST would break parity and add deps.

2. **Indentation/brace heuristic for body detection.** Python: a `def`/`class` header line ending in `:` opens a block; deeper-indented lines are body. TS/JS: a signature line ending in `{` opens a block; lines until the matching close are body. v1 uses an indentation+brace-depth counter, not a real tokenizer (strings containing braces are a known v1 imperfection, documented).

3. **`compact()` is a free function / static-style method**, not state on the index. It transforms text. Whether a doc is stored compacted is the caller's choice (or a future `add(..., compact=True)` flag — kept out of v1 scope to stay minimal).

4. **Shared fixture drives parity.** `fixtures/compaction.json`: a list of `{lang, source, expected_skeleton}`. Both test suites assert `compact(source, lang) == expected_skeleton`. The parity emitter is extended so `bench/parity.py` diffs compaction output across languages to byte-equality, same as retrieval.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Heuristic mis-strips edge cases (braces in strings, multiline signatures) | Document as a known v1 limitation; the fixture encodes the supported shapes explicitly; AST mode is the future opt-in fix. |
| Python and TS heuristics drift | The shared fixture + parity harness fail loudly on any divergence — same guarantee as the core engine. |
| Scope creep into a real parser | Non-goal stated explicitly; v1 ships heuristic-only; any parser work is a separate opt-in-extra change. |

## Open Questions

1. Should compacted storage be a flag on `add()` (`add(..., compact=True)`) in this change, or a follow-up? Recommendation: follow-up — keep this change to the pure transform + parity, add the storage ergonomics once the transform is proven.
2. Which languages beyond Python/TS/JS in v1? Recommendation: none — match the two languages we already maintain so the fixture stays small and parity stays honest.
