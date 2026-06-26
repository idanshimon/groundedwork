# Add signature compaction (`compact()`)

## Why

groundedwork is weak on code knowledge bases. BM25 retrieves whole documents, but a code file's body is mostly noise for retrieval and burns context when injected. ContextForge has a code-specific path — it compacts a file to its signatures (class/def/import skeleton, bodies stripped) and carries only that forward — which is exactly the missing piece for making a code corpus fit the window.

This change ports that one idea — signature compaction — reimplemented from scratch in both languages, BYOM-preserving and zero-dependency, credited to ContextForge. It directly addresses the "is groundedwork any good for code?" gap without absorbing CF's framework or breaking the cross-language parity story (CF is Python-only; we ship both).

This is a deliberately scoped, deferred item — authored now to capture the design, implemented after `add-hybrid-embeddings` ships.

## What Changes

- Add a `compact(text, lang=None)` transform that reduces a source file to its structural skeleton: imports, class/def signatures, decorators, and docstring first lines — method/function bodies replaced with a `...` placeholder.
- Compaction is a pure text transform — no model call, no new dependency (regex/heuristic line classification, not a full parser, in v1).
- Optionally allow a document to be stored in compacted form, or compacted at retrieval time, so a code corpus fits more files per working set.
- Language detection is best-effort by extension/heuristic; `lang` can be passed explicitly. v1 targets Python and TypeScript/JavaScript (the two languages we already maintain).

## Capabilities

### New Capabilities
- `signature-compaction`: reduce a source file to its class/def/import signature skeleton, bodies stripped, as a pure dependency-free transform available in both Python and TypeScript.

## Cross-language impact

Touches retrieval-adjacent behavior — MUST land in BOTH Python and TypeScript with identical output, verified by a new parity fixture (compaction input → expected skeleton). This is not docs/tooling-only.

## Invariant check

- Parity: `compact()` ships in both languages; a shared fixture asserts byte-identical skeletons. ✔
- Safe by default: no change to grounding/floor/abstention. ✔
- BYOM: pure text transform, no model call. ✔
- Zero runtime dependency: regex/heuristic line classification in v1, no parser dependency. ✔ (A real AST-based mode, if ever added, ships as an opt-in extra.)
- Small surface: adds one method (`compact`) + an optional storage flag. Justified by the code use case. ✔

## Impact

- `python/groundedwork/__init__.py`, `ts/src/index.ts` — add `compact()`.
- `fixtures/` — new compaction parity fixture.
- `bench/` — extend the parity emitter/harness to cover compaction.
- Docs — README "what it's good at" gains a code note; ARCHITECTURE gains a compaction section.

## Non-goals

- NOT a full language parser or AST. v1 is heuristic/regex line classification. Good enough to strip bodies; not a semantic analyzer.
- NOT code generation. Compaction feeds retrieval/context; it does not write code.
- NOT a replacement for embeddings. Compaction shrinks each doc; embeddings fix paraphrase matching. They compose; this change does not depend on or block embeddings.
- NOT importing any ContextForge code. This is a clean reimplementation of the idea, credited.
