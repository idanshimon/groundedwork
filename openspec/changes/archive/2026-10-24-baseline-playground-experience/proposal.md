## Why
The shipped playground redesign and query-feedback fixes were merged before their presentation contract was recorded in OpenSpec. This is a retrospective baseline of executed behavior, not a claim that these artifacts guided the original implementation. A preloaded result and a clipped completion region made a working Run query action appear inert; the new visible receipt must remain governed.

## What Changes
- Baseline real-engine adapters, source/evidence rendering, fail-closed static assembly and no-LLM semantics.
- Govern visible completion, user-triggered result focus/reveal, accessible scenario controls and a prominent walkthrough invitation.
- Clarify that grounded=true reports a floor-clearing working set, not semantic correctness.

## Capabilities
### New Capabilities
- `playground-experience`: Functional, honest, responsive evidence inspector and static/server adapter contract.
### Modified Capabilities
- `grounding-abstention`: Clarify the positive boolean's bounded meaning without altering retrieval.

## Impact
Documentation only. Implementation owners: playground/index.html, playground/build_static.py and playground/tests/test_playground.py. The deployed companion's composition/player is owned by idanshimon/groundedwork-demo and its own OpenSpec. Existing unrelated roadmap changes are untouched.

## Cross-language impact
No engine, fixture, scoring, API or dependency changes. The UI uses the real Python/server or compiled TypeScript/browser adapter. Existing equality and parity checks remain authoritative.

## Invariant check
Parity, default floor/abstention, BYOM and core zero-runtime-dependency guarantees are preserved. A lexical wrong match must not be hidden behind a success claim.

## Non-goals
Fixing unrelated MCP/Node CI, changing algorithms, guaranteeing answer correctness, adding a generation model, or rendering a video.
