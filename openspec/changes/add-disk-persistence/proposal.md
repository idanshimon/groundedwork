# Add on-disk persistence

## Why

v0.1 is in-memory: every process start re-ingests the whole corpus. For a large or slow-changing knowledge base, re-indexing on every boot is wasteful. On-disk persistence lets an index be built once, saved, and reloaded — turning startup from "re-tokenize everything" into "load a file."

Deferred roadmap item — authored now to capture the design; lower priority than hybrid embeddings and compaction.

## What Changes

- Add `save(path)` and `load(path)` (or equivalent) so a built index — documents, term frequencies, document frequencies, lengths, config — can be written to disk and reloaded without re-ingesting.
- The on-disk format is a simple, dependency-free serialization (JSON or a documented compact format), portable and human-inspectable.
- The persisted format is identical in shape across Python and TypeScript so an index saved by one can be loaded by the other.

## Capabilities

### New Capabilities
- `disk-persistence`: save a built index to disk and reload it without re-ingesting, with a cross-language-portable format.

## Cross-language impact

Touches behavior that must match across languages: the on-disk format MUST be identical so a Python-saved index loads in TypeScript and vice versa. MUST land in BOTH languages with a shared format fixture verifying interop. Not docs-only.

## Invariant check

- Parity: a shared format fixture verifies an index saved by one language loads in the other and produces identical retrieval. ✔
- Safe by default: no change to grounding/floor/abstention; loaded index behaves identically to a freshly-built one. ✔
- BYOM: serialization only, no model call. ✔
- Zero runtime dependency: format is stdlib serialization (JSON) — no new dependency. ✔
- Small surface: adds `save`/`load`. ✔

## Impact

- Both implementations gain `save`/`load` + a documented on-disk format.
- New format fixture for cross-language interop.
- Docs: a persistence section.

## Non-goals

- NOT a database or query server — just save/load of the in-memory index.
- NOT incremental/streaming index updates in v1 (full save/load only).
- NOT a versioned migration system in v1 (a format-version field is included, but migration tooling is deferred).
