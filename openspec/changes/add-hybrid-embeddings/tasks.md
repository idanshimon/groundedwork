# Tasks — hybrid embeddings

## 1. Paraphrase fixture
- [ ] 1.1 Author `fixtures/paraphrase.json` with cases the keyword path provably misses (query words ≠ doc words) and the doc that SHOULD be retrieved.
- [ ] 1.2 Validation: confirm the current keyword engine misses these cases (establishes the baseline the feature must beat).

## 2. Embedding backend interface
- [ ] 2.1 Define a pluggable embedding-backend interface in both languages.
- [ ] 2.2 Provide a local default backend as an optional extra (Python extra + optional TS peer).
- [ ] 2.3 Validation: core imports and the keyword default still work with the extra NOT installed.

## 3. Hybrid scoring (both languages)
- [ ] 3.1 Implement RRF fusion of BM25 ranks + dense ranks in Python.
- [ ] 3.2 Implement the same in TypeScript.
- [ ] 3.3 Validation: paraphrase fixture cases now retrieve the right doc in both languages.

## 4. Parity (ranking-level)
- [ ] 4.1 Extend the parity harness with a ranking-parity check for the dense path (same IDs, same order; not float-equality).
- [ ] 4.2 Validation: `make test` green; BM25 value-parity unchanged; hybrid ranking-parity IDENTICAL.

## 5. Docs
- [ ] 5.1 Flip the README "honest limitation" section to "v0.2 closes the paraphrase gap (opt-in)".
- [ ] 5.2 Document the retrieval-embedder ≠ generation-model BYOM distinction explicitly.
- [ ] 5.3 Validation: every claim backed by a passing paraphrase fixture case.
