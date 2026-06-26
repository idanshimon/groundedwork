# Tasks — on-disk persistence

## 1. Format definition
- [ ] 1.1 Define the on-disk JSON schema: documents, term frequencies, document frequencies, lengths, avgdl, config, and a `format_version` field.
- [ ] 1.2 Author a shared format fixture: a known corpus → its expected serialized form.
- [ ] 1.3 Validation: the fixture is valid JSON and round-trips (load(save(x)) == x semantics).

## 2. Python implementation
- [ ] 2.1 Implement `save(path)` / `load(path)` in Python persisting the computed index (not just raw docs).
- [ ] 2.2 Add tests: a loaded index produces identical retrieval to a freshly-built one.
- [ ] 2.3 Validation: pytest green.

## 3. TypeScript implementation
- [ ] 3.1 Implement `save`/`load` in TypeScript using the same format.
- [ ] 3.2 Add tests mirroring the Python ones.
- [ ] 3.3 Validation: npm test green.

## 4. Cross-language interop
- [ ] 4.1 Add an interop test: an index saved by Python loads in TypeScript (and vice versa) and produces identical retrieval over the shared fixture.
- [ ] 4.2 Validation: make test green; interop IDENTICAL.

## 5. Docs
- [ ] 5.1 Add a persistence section to docs/ARCHITECTURE.md and the READMEs.
- [ ] 5.2 Document the format_version field and the no-migration-tooling-in-v1 stance.
- [ ] 5.3 Validation: documented format matches the fixture exactly.
