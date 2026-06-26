# cross-language-parity Specification

## Purpose
The invariant that makes groundedwork's two implementations one library: Python and TypeScript produce identical retrieval output (same ids, same order, same scores to 9 decimal places) for the same corpus and query. Enforced mechanically by `bench/parity.py` diffing both engines against `bench/golden.json` over the shared `fixtures/nimbus.json`. The load-bearing rule: any retrieval-behavior change must land in both languages and keep the harness green — a one-language change is a bug, not a feature.
## Requirements
### Requirement: Python and TypeScript produce identical retrieval output
The Python and TypeScript implementations MUST produce identical retrieval results — same documents, same order, same scores to 9 decimal places — for the same corpus and query.

#### Scenario: both engines agree on the shared fixture
- **WHEN** both implementations retrieve over the shared `fixtures/nimbus.json`
- **THEN** their ranked document ids are identical
- **AND** their scores match to 9 decimal places

### Requirement: parity is enforced by a golden snapshot
The build MUST include a parity harness that diffs the two implementations' output against a committed golden snapshot and fails when they diverge.

#### Scenario: the parity harness reports identical
- **WHEN** `bench/parity.py` runs the shared fixture through both engines
- **THEN** it compares both against the golden snapshot
- **AND** it reports the result as identical when they agree

### Requirement: behavior changes must preserve parity
Any change to retrieval behavior MUST be made in both languages and MUST keep the parity harness passing, so the two implementations cannot silently drift.

#### Scenario: a one-language change is caught
- **WHEN** retrieval behavior is changed in only one language
- **THEN** the parity harness reports a divergence and fails

