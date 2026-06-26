# Contributing to groundedwork

Thanks for your interest. groundedwork is small on purpose, and contributions that keep it small, honest, and fast are very welcome.

## The one rule that matters most

**groundedwork is two implementations of one specification.** Python (`python/`) and TypeScript (`ts/`) must behave *identically*. Any change to retrieval behavior — scoring, tokenization, the relevance floor, prompt assembly — must be made in **both** languages and must keep the cross-language parity harness green.

```bash
make test     # runs the Python suite, the TypeScript suite, AND the parity check
```

If `make test` is green, your change is behaviorally consistent across both languages. If it's red on parity, the two implementations have drifted — that's a bug, even if one language's unit tests pass.

## Development setup

```bash
make install          # pip install -e python/ + npm install in ts/
make test             # everything
make test-py          # python only
make test-ts          # typescript only
make parity           # cross-language parity vs bench/golden.json
make golden           # regenerate the golden snapshot after an INTENTIONAL change
```

Requirements: Python ≥ 3.9, Node ≥ 18. Zero runtime dependencies — please keep it that way (dev/test tooling is fine; runtime deps are not).

## Making a change

1. Read [`AGENTS.md`](AGENTS.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — they define the behavioral contract.
2. Change **both** `python/groundedwork/__init__.py` and `ts/src/index.ts`.
3. Add/adjust tests in **both** `python/tests/` and `ts/test/`. New fixture cases go in `fixtures/nimbus.json` and are picked up by both suites automatically.
4. Run `make test`. If a behavior change intentionally alters output, run `make golden` and review the diff.
5. Open a PR. CI runs Python 3.9/3.11/3.13 and Node 18/20/22, then the parity job.

## Project values (learned empirically — please respect them)

- **Honesty over polish.** Claims in the docs are backed by a test or a measurement. The paraphrase limitation is stated plainly; don't soften it. If you add a capability, document what it *doesn't* do too.
- **Safe by default.** Grounding and the relevance floor are ON by default. A change that makes the unsafe behavior the default will not be merged.
- **Zero runtime dependencies.** New capabilities (e.g. embeddings) ship as opt-in extras, never as a base dependency.
- **Small surface.** Four methods (`add` / `retrieve` / `prompt`/`messages` / `ask`) cover the job. New public API needs a strong justification.
- **BYOM.** groundedwork never calls a model. No provider SDKs, no API keys, no `base_url` config. The model call belongs in the user's code.

## Roadmap-aligned contributions we'd love

- **v0.2 hybrid retrieval** — an opt-in local embedding ranker to close the paraphrase gap (the headline limitation). Must stay zero-*required*-dependency.
- **A third language port** (Go, Rust, ...) — implement the contract, add a `bench/emit_results.<lang>` emitter, and reproduce `bench/golden.json` exactly.
- **On-disk persistence** for the index.

## Reporting bugs

Open an issue with a minimal reproduction. If it's a retrieval-behavior bug, the most useful report is a fixture case (corpus + query + what you expected vs got) — that turns straight into a regression test.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
