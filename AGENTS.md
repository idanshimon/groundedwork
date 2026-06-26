# AGENTS.md

Machine-oriented guide for AI coding agents working **on** groundedwork or integrating it **into** another project. Human docs: `README.md`, `docs/ARCHITECTURE.md`. This file is the contract — if you change behavior, the parity harness must still pass.

---

## What this package is (one paragraph)

groundedwork is a dependency-free retrieval + prompt-assembly layer. It indexes documents, retrieves a relevance-floored "working set" via BM25 keyword scoring, and assembles a grounded, cache-optimal prompt for an LLM. It does **not** call any model. Python reference + TypeScript mirror, behavior verified identical to 9 decimal places.

## Roadmap & spec-driven changes

The roadmap lives in OpenSpec, not in scattered TODOs. Run `openspec list` to see active changes (the planning queue), and read `openspec/changes/<name>/` for the full proposal/design/tasks/spec of each. Current queue: `add-hybrid-embeddings` (v0.2, closes the paraphrase gap), `add-signature-compaction` (code-corpus support, a clean reimplementation of a ContextForge idea), `add-mcp-server` (groundedwork as an MCP tool for agent hosts), `add-disk-persistence`.

Any change touching retrieval behavior, a public API, or an invariant goes through OpenSpec first: `openspec new change <name>`, author the four files, `openspec validate <name> --strict`. The config at `openspec/config.yaml` encodes the project invariants the proposal/design must respect. Pure bug fixes / docs / test additions do not require a change proposal.

---

## Integrating groundedwork into your project

### Python

```python
from groundedwork import GroundedWork

kb = GroundedWork(prefs="optional stable per-user/persona text")
kb.add_many([{"id": "doc1", "title": "...", "body": "..."}, ...])

m = kb.messages(user_question)
if not m["grounded"]:
    answer = "I don't have that in the knowledge base."   # no model call needed
else:
    answer = your_llm_client.chat(m["messages"])           # YOU own the model call
```

### TypeScript

```typescript
import { GroundedWork } from "groundedwork";

const kb = new GroundedWork({ prefs: "optional stable text" });
kb.addMany([{ id: "doc1", title: "...", body: "..." }]);

const m = kb.messages(userQuestion);
const answer = m.grounded ? await yourLlmClient.chat(m.messages) : "I don't have that.";
```

### Integration invariants (do not violate)

1. **groundedwork never calls a model.** Do not add a provider SDK, API key, or `base_url` to it. The model call belongs in YOUR code. This is the design, not an omission.
2. **Always check `grounded` before calling the model.** On `false`, short-circuit to an honest "I don't have that" — it saves a token spend and prevents a hallucination on an absent answer.
3. **Use `messages()` (not `prompt()`) when your endpoint does prompt caching.** It orders the request so the stable `[system + prefs]` prefix is cacheable and the volatile knowledge is last. `prompt()` returns the loose pieces if you need to assemble differently.
4. **`ask()` is demo-only.** It returns canned document text with NO model call, for examples/tests. Never ship it as your production answerer.

---

## Working ON the package (modifying it)

### Repository map

```
python/groundedwork/__init__.py   reference implementation (single file)
python/tests/                     pytest suite (consumes the shared fixture)
ts/src/index.ts                   TypeScript mirror (single file)
ts/test/                          node:test suite (consumes the shared fixture)
fixtures/nimbus.json              SHARED corpus + cases — the parity contract
bench/emit_results.py|.mts        canonical-output emitters (one per language)
bench/parity.py                   cross-language diff + golden check
bench/golden.json                 committed golden snapshot (regenerate via make golden)
docs/ARCHITECTURE.md              algorithm, design, interface contract
Makefile                          `make test` = everything
```

### The golden rule of changes

**Any change to retrieval behavior must keep both languages identical.** The two implementations are independent code but one specification. If you touch scoring, tokenization, the floor, or assembly:

1. Make the change in **both** `python/groundedwork/__init__.py` AND `ts/src/index.ts`.
2. Run `make test`. The parity harness (`bench/parity.py`) diffs the two engines' output to 9 dp.
3. If the change is intentional and parity-preserving but alters output, run `make golden` to update the snapshot, and review the diff.
4. If you add a fixture case, both suites pick it up automatically — re-run `make golden`.

A change that passes one language's unit tests but breaks parity is a **bug**, even if that language "works."

### Behavioral contract (the invariants a change must not silently break)

- `tokenize`: lowercase → strip non-alphanumerics → drop len≤1 and stopwords. **The stopword list is identical in both languages.** Changing it changes scores.
- Title is weighted 2× (concatenated twice before tokenizing).
- BM25 with `k1=1.5`, `b=0.75`, `IDF = ln(1 + (N - df + 0.5)/(df + 0.5))`.
- The relevance floor drops hits with `score < min_score` AFTER top-k selection.
- `grounded == (len(hits) > 0)`.
- Default `system_prompt` is the grounding instruction (`GROUNDING_PROMPT`); it must instruct the model to answer only from context and not guess.
- `messages()` order is exactly: `system(stable_prefix)`, then `user(knowledge)` IF grounded, then `user(query)`.
- `stable_prefix()` is query-independent (same output regardless of the question).

### Adding a third language (e.g. Go, Rust)

1. Implement the same contract (§ above) in `<lang>/`.
2. Add a `bench/emit_results.<lang>` emitter that prints the canonical JSON shape (sorted keys, scores to 9 dp, `matched` sorted).
3. Extend `bench/parity.py` to run it and diff against `golden.json`.
4. It must reproduce `golden.json` exactly, or it isn't done.

---

## Verification commands

```bash
make test       # python suite + typescript suite + cross-language parity
make test-py    # python only
make test-ts    # typescript only
make parity     # parity check vs golden.json (exit 1 on divergence)
make golden     # regenerate golden.json after an intentional change
```

`make test` exiting 0 is the definition of "green." CI runs the same on Python 3.9/3.11/3.13 and Node 18/20/22.

---

## Non-negotiables (project values, learned empirically)

- **Honesty over polish.** The README and ARCHITECTURE state the paraphrase limitation plainly. Do not remove or soften it. A claim must be backed by a test or a measurement.
- **Safe by default.** Grounding and the floor are ON by default. A PR that makes the unsafe behavior the default is wrong.
- **Zero runtime dependencies.** The core stays stdlib-only in both languages. New capabilities (e.g. embeddings) ship as opt-in extras, never as a base dependency.
- **Credit the lineage.** groundedwork is built on the ideas of ContextForge (github.com/Betanu701/ContextForge) by Derek Thomas. Keep that attribution in the README.
