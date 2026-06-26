# Tasks — core retrieval baseline

> All implementation is already shipped in v0.1 (73 tests pass). Tasks are
> marked `[x]` because the code exists; this change documents it.

## 1. core-retrieval capability
- [x] 1.1 BM25 indexing (k1=1.5, b=0.75, title 2×) implemented in both languages.
- [x] 1.2 Relevance floor (min_score default 0.5) implemented in both languages.
- [x] 1.3 Validated against reference rank_bm25 + 392-doc corpus battery.

## 2. grounding-abstention capability
- [x] 2.1 Grounded-by-default system prompt shipped in both languages.
- [x] 2.2 First-class `grounded` return value + no-knowledge-on-miss shipped.
- [x] 2.3 Systematic abstention tests pass (all absent queries abstain).

## 3. cache-aware-assembly capability
- [x] 3.1 `messages()` with stable prefix + volatile-knowledge-last shipped.
- [x] 3.2 `prefs` + `stable_prefix()` shipped; tests assert prefix stability.

## 4. cross-language-parity capability
- [x] 4.1 Shared fixture (nimbus.json) consumed by both suites.
- [x] 4.2 `bench/parity.py` diffs to 9 dp against golden.json; reports IDENTICAL.

## 5. Archive
- [x] 5.1 Validate `--strict` and archive so `openspec/specs/` is populated with the four canonical capabilities.
