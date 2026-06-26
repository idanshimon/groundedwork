# Changelog

All notable changes to groundedwork are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/); this project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned (v0.2)
- Opt-in hybrid retrieval (BM25 + a small local embedding model) to close the paraphrase gap — the one limitation of keyword-only retrieval. Ships as an extra so the zero-dependency default is unchanged.
- On-disk persistence for the index.
- Streaming-friendly prompt assembly.

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
