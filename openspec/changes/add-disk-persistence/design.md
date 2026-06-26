# Design — on-disk persistence

## Context

Re-ingesting a corpus on every process start is wasteful for large/slow-changing knowledge bases. Persisting the built index (docs + term frequencies + doc frequencies + lengths + config) lets startup be a file load. The cross-language constraint: the format must be portable so a Python-saved index loads in TypeScript and vice versa.

## Goals / Non-Goals

**Goals:**
- `save(path)` / `load(path)` for a built index, no re-ingestion on reload.
- A dependency-free, cross-language-portable, human-inspectable format.
- Loaded index behaves identically to a freshly-built one.

**Non-Goals:**
- A database or query server.
- Incremental/streaming updates (full save/load only in v1).
- Migration tooling (a version field is stored; migration is deferred).

## Decisions

1. **JSON serialization in v1.** Stdlib in both languages, human-inspectable, trivially portable. A compact binary format is a possible later optimization, not v1.
2. **Persist the computed index, not just raw docs.** Save term frequencies, document frequencies, lengths, and avgdl so reload skips tokenization entirely — that's the speed win. Raw-doc-only persistence would still require re-indexing.
3. **A `format_version` field is included** so a future format change can be detected (and rejected with a clear error rather than mis-parsed). Migration tooling itself is deferred.
4. **Cross-language interop is verified by a shared format fixture** — an index saved by one language must load in the other and produce identical retrieval output.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Float representation of scores differs across languages | Persist the integer/string inputs (term frequencies, lengths), NOT computed float scores — scores are recomputed identically on load. |
| Format drift between languages | Shared format fixture + interop test fail loudly on divergence. |
| Large indexes → large JSON | Acceptable in v1; compact format is a documented future optimization. |

## Open Questions

1. Single-file JSON vs a small directory layout for very large corpora? Recommendation: single file in v1; revisit if size becomes a real problem.
