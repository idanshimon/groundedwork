# Add hybrid embeddings (close the paraphrase gap)

## Why

groundedwork's one real limitation is BM25's paraphrase gap: a question phrased with different words than the source ("deduplicate a list" vs a doc about `unique()`) misses, and a stray word can surface the wrong doc with false confidence. This is the headline v0.2 feature: an opt-in hybrid retriever (BM25 + a small local embedding model) that matches on meaning, not just words.

This is the most-requested capability and the biggest single quality lever. It is authored now as the lead roadmap item; it ships before the other deferred changes.

## What Changes

- Add an opt-in hybrid retrieval mode: BM25 lexical score fused with dense embedding similarity (e.g. reciprocal-rank fusion or weighted sum).
- The embedding backend is pluggable and LOCAL by default (a small sentence-embedding model), shipped as an OPTIONAL extra — the zero-dependency keyword default is unchanged when the extra is not installed.
- Retrieval API is unchanged in shape; hybrid is enabled by a constructor flag (e.g. `GroundedWork(hybrid=True)` / `{ hybrid: true }`).

## Capabilities

### New Capabilities
- `hybrid-retrieval`: opt-in dense+lexical fused retrieval that closes the BM25 paraphrase gap, with a local embedding backend shipped as an optional extra.

## Cross-language impact

Touches retrieval behavior — MUST land in BOTH Python and TypeScript with matching semantics. Note: exact embedding floats will differ across runtimes/models, so parity here is asserted on RANKING behavior over a fixture (same docs retrieved in the same order for paraphrase cases), not on raw score equality. This is a deliberate parity-model change documented in design.

## Invariant check

- Parity: ranking-level parity on a paraphrase fixture (raw-float equality is explicitly not required for the dense component — see design). ✔
- Safe by default: grounding + floor + abstention unchanged; hybrid is opt-in. ✔
- BYOM: the embedding model is a LOCAL retrieval-side model, not a generation model — groundedwork still never calls a generation LLM. The embedding backend is pluggable so users can supply their own. ✔ (worth a design note — this is the one place a "model" enters, and it must stay clearly separate from the BYOM generation boundary.)
- Zero runtime dependency: the embedding backend is an OPTIONAL extra; the keyword default stays stdlib-only. ✔
- Small surface: one constructor flag + a pluggable backend interface. ✔

## Impact

- Both implementations gain a hybrid scoring path + a pluggable embedding-backend interface.
- New optional extras: `pip install groundedwork[hybrid]` / an optional npm peer.
- New paraphrase fixture for ranking-parity.
- Docs: the "honest limitation" section flips from "we don't fix paraphrase" to "v0.2 fixes it, opt-in."

## Non-goals

- NOT on by default — keyword stays the zero-dependency default.
- NOT a generation model — the embedding model is retrieval-side only; BYOM for generation is untouched.
- NOT raw-float cross-language parity for the dense component (infeasible across models/runtimes); ranking-parity only.
