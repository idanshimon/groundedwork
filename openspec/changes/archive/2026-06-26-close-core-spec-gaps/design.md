# Design — close core-spec gaps

## Context

A spec audit found three shipped behaviors with no canonical requirement. This change documents them. No code changes; the behaviors already exist and are tested.

## Goals / Non-Goals

**Goals:**
- Make BYOM a canonical, enforceable requirement (its own capability).
- Govern `top_k` and custom system-prompt override.

**Non-Goals:**
- Any behavior, API, or dependency change.

## Decisions

1. **BYOM gets its own capability, not a requirement buried in grounding.** BYOM is a package-wide architectural guarantee (it constrains the entire library, not just prompting), so it reads cleaner as a standalone `byom` capability. This also makes it the obvious thing a reviewer checks when a new method is proposed.

2. **The BYOM requirement is testable by absence.** The scenario asserts that retrieval and assembly complete with no network/model call — which is already true because the code imports no model SDK. The requirement codifies the architecture the zero-dependency design already enforces.

3. **`top_k` and custom-prompt are ADDED, not MODIFIED.** Their requirement names do not exist in the canonical specs yet, so per OpenSpec semantics they are ADDED requirements to existing capabilities (the capability spec exists; these specific requirements are new).

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| BYOM requirement becomes false if a future feature adds a model call | That is exactly the point — the requirement makes such a change a visible spec violation, forcing a deliberate MODIFIED delta and review. |
| Over-speccing minor knobs (top_k) | Kept to one terse requirement; documents real public behavior without bloating the surface. |

## Open Questions

None — documents shipped, tested behavior.
