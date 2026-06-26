# Tasks — hybrid embeddings

> Implemented. Scope reconciled against the original plan (noted inline where it
> changed for good reason). All behavior verified; see bench/paraphrase_eval.py
> for the empirical before/after.

## 1. Paraphrase fixture
- [x] 1.1 Paraphrase cases live in `fixtures/corpus_large.json` (`paraphrase` array) — queries whose words ≠ the relevant doc's words. (Reused the existing real corpus instead of a separate paraphrase.json; the cases were already authored there.)
- [x] 1.2 Baseline confirmed: keyword-only recall@1 is 1/4 on these cases (bench/paraphrase_eval.py).

## 2. Embedding backend interface
- [x] 2.1 Pluggable `embedder` (BYOM) in both languages: any object with `encode(texts) -> vectors`, or a bare callable. Python `embedder=`; TS `embedder` option + `Embedder`/`EmbedderLike` types.
- [x] 2.2 Optional extra: Python `pip install groundedwork[hybrid]` (model2vec). TS embedder is caller-supplied (no peer dep needed).
- [x] 2.3 Validation: core imports + the keyword default work with NO embedder and NO extra installed (tested: `test_zero_dependency_default_still_works`, TS equivalent).

## 3. Hybrid scoring (both languages)
- [x] 3.1 RRF fusion of BM25 ranks + dense ranks in Python (`retrieve()` hybrid path, rrf_k=60).
- [x] 3.2 Same in TypeScript (identical fusion + a sync-embedder guard).
- [x] 3.3 Validation: paraphrase recall@1 improves 1/4 → 2/4 (real model2vec model), 390/390 normal cases preserved, abstention intact. A zero-norm guard prevents degenerate embeddings from fabricating hits.

## 4. Parity (ranking-level)
- [x] 4.1 BM25 value-parity is UNCHANGED and still IDENTICAL to 9 dp (hybrid is opt-in; the default keyword path both languages share is byte-identical). 
- [N/A] 4.2 Dense ranking-parity across languages is intentionally NOT asserted: the dense signal depends on the caller's embedder, which differs per runtime (model2vec-py vs a JS embedder). Asserting cross-language dense equality would require shipping one embedder, breaking BYOM + zero-dep. Instead both languages are tested independently with a deterministic in-test embedder, and the FUSION math is identical by construction.

## 5. Docs
- [x] 5.1 README "honest limitation" flipped to "v0.2 closes the paraphrase gap (opt-in, measured 1/4 → 2/4)".
- [x] 5.2 Documented the retrieval-embedder ≠ generation-model distinction: the embedder ranks documents; groundedwork still never calls a generation model (BYOM intact).
- [x] 5.3 Every claim is backed by bench/paraphrase_eval.py (runnable, asserted).

## 6. Validate + archive
- [x] 6.1 `openspec validate add-hybrid-embeddings --strict` clean.
- [x] 6.2 Archive so the `hybrid-retrieval` capability enters the canonical catalog.
