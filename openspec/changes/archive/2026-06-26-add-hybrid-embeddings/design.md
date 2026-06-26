# Design — hybrid embeddings

## Context

BM25 is lexical. Paraphrased queries miss. The fix is to fuse a dense (embedding) similarity signal with the lexical score. The challenge for THIS project is the parity invariant: dense embeddings produce floats that vary by model and runtime, so the byte-identical parity model used for BM25 cannot apply to the dense component. The design must define a weaker-but-honest parity contract.

## Goals / Non-Goals

**Goals:**
- Opt-in hybrid retrieval that retrieves the right doc for paraphrased queries the keyword path misses.
- Keep the zero-dependency keyword default untouched.
- A pluggable embedding backend so users choose the model (or supply their own).

**Non-Goals:**
- Hybrid on by default.
- Raw-float cross-language parity for the dense score.
- Any generation-model involvement.

## Decisions

1. **Fusion via reciprocal-rank fusion (RRF), not raw-score blending.** RRF combines two ranked lists by rank position, which is robust to the two scores being on different scales — and crucially, rank-based fusion is far easier to make behave consistently across languages than float blending.

2. **Parity model changes for the dense path: ranking-parity, not value-parity.** The shared fixture asserts that for a set of paraphrase cases, both languages retrieve the same doc IDs in the same order — NOT that the embedding floats match. This is a documented, deliberate relaxation of the byte-identical rule, justified because raw-float dense parity across models/runtimes is infeasible. The BM25 component keeps full value-parity.

3. **Embedding backend is a pluggable interface, local default, optional extra.** Users install `groundedwork[hybrid]` (Python) / an optional peer (TS) to get the bundled local model; or implement the backend interface with their own embedder. groundedwork core never hard-depends on it.

4. **The embedding model is retrieval-side, explicitly NOT the BYOM generation boundary.** Design must state this loudly: BYOM means "we don't call your GENERATION model." A local embedding model for retrieval ranking is a different thing. Docs must not let this blur the BYOM claim.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Dense path can't be byte-parity tested | Ranking-parity fixture + explicit documented contract change. |
| "It uses a model now" undercuts BYOM messaging | Sharp docs: retrieval-side embedder ≠ generation model; opt-in; pluggable. |
| Optional extra complicates install | Keyword default unchanged; extra is clearly separate; graceful fallback when not installed. |

## Open Questions

1. Which local embedding model as the bundled default? (Deferred to implementation — pick a small, permissively-licensed, widely-available one.)
2. RRF vs weighted-sum fusion — confirm RRF empirically beats weighted-sum on the paraphrase fixture before locking it. (An empirical-comparison task, not a guess.)
