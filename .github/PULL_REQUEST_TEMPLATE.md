## What this changes

<!-- One or two sentences. Link any related issue. -->

## Checklist

<!-- The parity rule is the one that matters most — see CONTRIBUTING.md -->

- [ ] If this changes retrieval behavior, I changed **both** `python/groundedwork/__init__.py` and `ts/src/index.ts`
- [ ] `make test` passes (Python suite + TypeScript suite + cross-language parity)
- [ ] If output intentionally changed, I ran `make golden` and reviewed the diff
- [ ] Added/updated tests in both languages (and `fixtures/nimbus.json` if it's a new case)
- [ ] No new runtime dependencies (dev/test deps are fine)
- [ ] Docs updated if behavior or API changed (`README.md` / `docs/ARCHITECTURE.md` / `AGENTS.md`)

## Notes for reviewers

<!-- Anything non-obvious: design tradeoffs, why parity output changed, etc. -->
