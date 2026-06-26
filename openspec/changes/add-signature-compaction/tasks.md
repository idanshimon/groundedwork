# Tasks — signature compaction

## 1. Shared fixture
- [ ] 1.1 Author `fixtures/compaction.json` with `{lang, source, expected_skeleton}` cases for Python and TS/JS (imports kept, class/def signatures kept, bodies → `...`, decorators kept, docstring first line kept).
- [ ] 1.2 Cover edge cases the heuristic is expected to handle: nested defs, decorators, multi-import blocks, a class with methods.
- [ ] 1.3 Validation: fixture is valid JSON and each case's expected_skeleton is hand-verified correct.

## 2. Python implementation
- [ ] 2.1 Implement `compact(text, lang=None)` in `python/groundedwork/__init__.py` (heuristic line classification per design Decision 1-2).
- [ ] 2.2 Add Python tests asserting `compact(source, lang) == expected_skeleton` for every fixture case.
- [ ] 2.3 Validation: `pytest` green.

## 3. TypeScript implementation
- [ ] 3.1 Implement `compact(text, lang?)` in `ts/src/index.ts` mirroring the Python algorithm exactly.
- [ ] 3.2 Add TS tests asserting parity against the same fixture cases.
- [ ] 3.3 Validation: `npm test` green.

## 4. Cross-language parity
- [ ] 4.1 Extend `bench/emit_results.py` and `bench/emit_results.mts` to emit compaction output for the fixture cases.
- [ ] 4.2 Extend `bench/parity.py` to diff compaction output to byte-equality and regenerate `bench/golden.json`.
- [ ] 4.3 Validation: `make test` green AND parity reports IDENTICAL for compaction.

## 5. Docs
- [ ] 5.1 README "what it's good at" gains a code-corpus note referencing `compact()`.
- [ ] 5.2 `docs/ARCHITECTURE.md` gains a "Signature compaction" section + the ContextForge credit for the idea.
- [ ] 5.3 Validation: every doc claim about compaction is backed by a passing fixture case.
