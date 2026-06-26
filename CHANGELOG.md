# Changelog

All notable changes to groundedwork are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- On-disk persistence for the index.
- `compact()` — signature compaction for code corpora (a clean reimplementation of a ContextForge idea).
- MCP server — groundedwork as a tool for agent hosts.

## [0.2.0] — 2026-06-26

### Added
- **Opt-in hybrid retrieval** — pass an `embedder` (any object with `encode(texts) -> vectors`, or a bare callable) and `retrieve()` fuses the BM25 ranking with a dense-similarity ranking via Reciprocal Rank Fusion (RRF), closing the paraphrase gap where a query shares meaning but not words with the relevant document. Python: `pip install "groundedwork[hybrid]"` (model2vec). TypeScript: caller-supplied embedder, no peer dependency.
- **`bench/paraphrase_eval.py`** — the empirical before/after. Measured on a real model: paraphrase recall@1 **1/4 → 2/4**, with **zero regression** on the 390 exact-match cases and abstention intact. The script asserts no-regression and no-broken-abstention.
- New config: `rrf_k` (fusion constant, default 60) and `dense_floor` (min cosine for a keyword-less hit to ground, default 0.30).

### Changed
- The zero-dependency keyword default is **unchanged and still byte-identical** across Python and TypeScript (parity harness green). Hybrid is strictly opt-in.

### Safety
- **Zero-norm guard** — a degenerate or empty embedding is normalized to an all-zero vector (cosine 0), so it can never fabricate a grounded hit. Abstention holds in hybrid mode.
- The embedder is **retrieval-side only**; groundedwork still never calls a generation model (BYOM intact).

## [0.1.0] — 2026-06-25

First release. A tiny, dependency-free BM25 working-set retrieval layer for giving an LLM a knowledge base bigger than its context window — grounded and abstaining by default. Python reference implementation + TypeScript mirror, behavior verified identical.

### Added
- **Core retrieval** — in-memory BM25 keyword index (`k1=1.5`, `b=0.75`, title weighted 2×). No embeddings, no vector store, no network calls.
- **Relevance floor** — `min_score` (default `0.5`): when nothing scores above the floor, retrieval returns empty and the result is marked ungrounded, instead of injecting distractors.
- **Grounding by default** — the default system prompt instructs the model to answer only from the provided knowledge and not guess.
- **First-class abstention** — `grounded` is a real return value; callers can skip the model call entirely when nothing matches.
- **Cache-aware assembly** — `messages()` pins a stable `[system + prefs]` prefix first and places the volatile retrieved knowledge last, maximizing prompt-cache hits on caching endpoints. `prefs` and `stable_prefix()` support per-user/persona pinning.
- **Four-method API** in both languages: `add`/`add_many`, `retrieve`, `prompt`/`messages`, `ask`.
- **Cross-language parity harness** (`bench/`) — Python and TypeScript emitters produce canonical retrieval output diffed to 9 decimal places against a committed golden snapshot. Proves the two implementations are numerically identical, not just independently green.
- **Docs** — `README.md`, `docs/ARCHITECTURE.md` (algorithm + design + interface contract), `AGENTS.md` (machine-oriented integration/extension guide), runnable `examples/`.
- **CI** — GitHub Actions across Python 3.9/3.11/3.13 and Node 18/20/22, with a parity job gated behind both unit suites.

### Credit
Built on the ideas of [ContextForge](https://github.com/Betanu701/ContextForge) by Derek Thomas. The improvements here — grounding, the relevance floor, abstention, cache-aware ordering, and a second language — come from empirically testing that SDK and shipping the lessons as defaults.

[Unreleased]: https://github.com/idanshimon/groundedwork/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/idanshimon/groundedwork/releases/tag/v0.1.0
