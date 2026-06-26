# Close core-spec gaps found in the spec-vs-implementation audit

## Why

A spec-vs-implementation audit found three shipped behaviors that the canonical
specs do not govern:

1. **BYOM is not a canonical requirement.** "groundedwork never calls a model"
   is the package's most load-bearing guarantee — it is why the library works
   with any local/cloud model and never touches credentials — yet it lives only
   in `config.yaml` invariants, proposals, and a Purpose paragraph. No
   requirement enforces it, so a future convenience method that called an LLM
   would pass the spec. This is the single most important gap.
2. **`top_k` (result-set size) is unspecced.** A public, configurable knob
   (default 3) that shapes every retrieval has no requirement.
3. **Custom `system_prompt` override is implied but never required.** The code
   supports overriding the grounding prompt, and a scenario even references
   "without a custom system prompt", but no requirement states the override is a
   supported capability.

This change closes all three. No code changes — it documents shipped, tested
behavior, so it is archived to update the canonical catalog.

## What Changes

- Add a new `byom` capability codifying that groundedwork never calls a
  generation model and holds no credentials.
- Add a `top_k` requirement to `core-retrieval`.
- Add a custom-system-prompt requirement to `grounding-abstention`.

## Capabilities

### New Capabilities
- `byom`: groundedwork performs retrieval and prompt assembly only and never calls a generation model or holds model credentials.

### Modified Capabilities
- `core-retrieval`: add a requirement governing the configurable result-set size (`top_k`).
- `grounding-abstention`: add a requirement governing custom system-prompt override.

## Cross-language impact

Documentation only — no behavior changes. All three behaviors already ship
identically in both languages and are covered by existing tests (BYOM is
implicit in the zero-model architecture; `top_k` and custom prompt are exercised
by the unit suites). No parity impact.

## Invariant check

- Parity: unaffected — documents existing identical behavior. ✔
- Safe by default: the BYOM capability strengthens the safety contract. ✔
- BYOM: this change MAKES BYOM a canonical requirement (the whole point). ✔
- Zero runtime dependency: unaffected. ✔
- Small surface: adds no API; documents existing surface. ✔

## Impact

- `openspec/specs/byom/spec.md` created on archive.
- `openspec/specs/core-retrieval/spec.md` gains the `top_k` requirement.
- `openspec/specs/grounding-abstention/spec.md` gains the custom-prompt requirement.
- No source, test, or dependency changes.

## Non-goals

- NOT changing any behavior. Documentation baseline correction only.
- NOT adding new API. These requirements describe the existing surface.
