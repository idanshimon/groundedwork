# groundedwork playground

A small, framework-free retrieval inspector. It runs the **real engine**, not a
scoring simulation, and never calls an LLM. The default refund result is computed
on load. The source extract is the retrieved document body, **not an AI answer**.

## Run

From the repository root:

```bash
python3 playground/server.py
# open http://localhost:8000 (real Python engine)
```

The server imports this checkout's `python/` package. No install is required.

For a self-contained, offline page:

```bash
# Restore build tools if missing:
env -u NODE_ENV -u NODE_PATH -u NODE_OPTIONS npm --prefix ts ci --ignore-scripts
env -u NODE_ENV -u NODE_PATH -u NODE_OPTIONS npm --prefix ts run build
python3 playground/build_static.py
# Open playground/dist/index.html, or serve playground/dist/ with any static server.
```

The build embeds the actual compiled `ts/dist/index.js`, fixture corpus and
configuration. It has no external runtime dependencies, network requests, model
calls, API keys, or private paths. Identical inputs produce identical bytes.
`dist/` is a gitignored build artifact; rebuild it before integration.

The header's `./walkthrough/` link is the integration point for the separately
maintained animated walkthrough. The local Python server serves only the
playground/API; it does not host that sibling. Integration must place the
walkthrough beside the static playground.

## Inspect

The query and five compact scenarios precede a two-column decision/source and
ranked-evidence workspace. Prompt and raw metadata stay collapsed initially.

| Scenario | Actual keyword-engine behavior |
| --- | --- |
| Refund policy | `returns`, score `3.8605`, `grounded=true` |
| Out of scope | No hits for the capital of France; `grounded=false` |
| Keyword mismatch | Delivery paraphrase returns the **wrong source**, `pause`, score `2.9429`, `grounded=true` |
| Multiple terms | Pause/subscription/billing query; six returned hits, three in the prompt |
| Product lookup | Decaf ranks first, alongside other coffee-related hits |

The floor is a **lexical score threshold**, not correctness verification. A
wrong-source match can exceed it. Optional hybrid retrieval may help with
paraphrases but is neither enabled here nor a guaranteed fix.

Bars show only retained **returned hits**, from a second real retrieval with
`top_k=corpus_size`. Below-floor documents/scores are not exposed by the engine
and are not fabricated. Every bar shares a scale with an explicitly labelled
floor tick. Scores retain the existing adapter's four-decimal precision.

## Adapter contract

`index.html` owns one controller and an explicitly delimited adapter slot.
Adapters provide `info()` and `analyze(query)`, synchronously or asynchronously.
The Python adapter calls the existing `/api/version`, `/api/scenarios`, and
`/api/ask` routes. Scenario labels and teaching notes belong to the shared UI;
legacy scenario prose from the server is not displayed.

`build_static.py` replaces **only** that slot, failing if markers are missing,
duplicated, or reversed. It does not rewrite fetch statements or controller
code. The browser adapter calls the actual `retrieve`, `messages`, and `ask`
methods and obtains the version from the engine's `VERSION` export.
`window.__GW.analyze(query)` remains available for inspection.

Both adapters preserve `query`, `terms`, `floor`, `scored`, `grounded`, `hits`,
`messages`, `stable_prefix`, `answer`, and `corpus_size`. Python also returns its
existing `prompt` field. `answer` remains the engine's demo-only canned
`ask()` response; it is not used as the primary source extract.

All query/document/metadata output uses text nodes, never raw HTML. JSON in the
static script is escaped against HTML script termination. Startup and query
failures have visible feedback, bounded waits and a retry path; failed queries
hide stale results.

## Design manifest

**Analytical archetype:** evidence inspector, not chatbot or dashboard.
**Primary question:** Which documents reached the model's context, and why?

Warm paper, ink and a restrained mint selection state establish a single light
theme. System fonts keep the page offline and small. The reading order is query,
scenario, decision, verbatim source, returned evidence, then optional raw prompt.
Whitespace separates decisions instead of reserving empty terminal space.
On narrow screens the same content stacks without horizontal page scrolling.
Controls have 44px-or-larger targets, native keyboard/Enter behavior, visible
focus, explicit labels and reduced-motion support. Color is never the only
indicator of selection or outcome.

## Regression tests

With Python Playwright and its Chromium browser available:

```bash
python3 playground/build_static.py
python3 -m unittest discover -s playground/tests -v
```

The suite starts isolated ephemeral HTTP servers, drives both real adapters at
1280px and 390px, and compares every shared result field against the real Python
engine for all five scenarios. It checks fixed baseline scores and the
wrong-source behavior, offline `file://` execution, deterministic output,
fail-closed slots, escaped script JSON, named controls, Enter, focus visibility,
touch sizes, page overflow, hostile queries/documents/metadata, startup failure,
query errors, retry and a missing-engine timeout. No retrieval implementation
or fixtures are modified.
