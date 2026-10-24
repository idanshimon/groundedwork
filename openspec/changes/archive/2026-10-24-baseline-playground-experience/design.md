## Context
Source main contains the shipped evidence inspector, explicit static-adapter slot and visible-run-feedback fixes. The public demo is a separate deployment repository; its latest site-return navigation must not be overwritten by rebuilding this source.

## Goals / Non-Goals
**Goals:** Record observable behavior and executable evidence for the shipped UI. Preserve algorithm and input/output contracts.
**Non-Goals:** New implementation, additional library APIs, model calls, or ownership of the companion's runtime internals.

## Decisions
1. The source repository owns the working playground and real-engine adapter contract. The demo repository owns its playback composition and deployment-specific navigation; link rather than duplicate those normative requirements.
2. The static builder replaces exactly one explicit adapter slot. It embeds the actual compiled TS module and safely encoded synthetic corpus/config, and rejects missing/duplicate/reversed markers and backend requests.
3. The UI presents retrieved document bodies and actual returned-hit scores, never generated text or fabricated discarded candidates. The retained working set can still be the wrong source.
4. Each successful run increments a visible receipt. Explicit user runs focus/reveal offscreen results; startup default population does not take over focus/scroll. Busy controls and visible errors distinguish actual work from inactivity.
5. No public API or dependency is added. Python/server and TS/browser existing payload fields remain equal for the shared scenarios; the golden parity fixture is unchanged.

## UX Microcopy
| Surface | Copy / meaning |
|---|---|
| Initial populated state | Example ready; edit the question or try a case |
| Submit | Run query / Running… |
| Completed run | Run N complete with selected-document count and no-model disclosure |
| Empty working set | No working set / No documents selected |
| Source | Verbatim document, not AI output |
| Wrong match | Keyword mismatch; wrong source despite grounded=true |
| Companion | Watch walkthrough with play icon and 30s duration |

## Risks / Trade-offs
- A threshold can pass irrelevant evidence: keep the wrong-match example and explicit boundary.
- Default prepopulation can mask a repeated run: completion is persistent and numbered, not only an accessibility-only live region.
- Static and server adapters can drift: compare full shared fields and exact ranked scores through both real paths.
- Deployment shell can evolve separately: preserve newer demo navigation instead of blindly replacing its entire index during spec maintenance.

## Open Questions
No open implementation questions in this retrospective scope. Existing unrelated CI failures are recorded separately, not treated as passing validation.
