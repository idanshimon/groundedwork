## MODIFIED Requirements

### Requirement: abstention is a first-class return value
Retrieval and prompt assembly MUST expose a `grounded` boolean that is false when nothing clears the relevance floor, and MUST inject no knowledge in that case; a true value MUST report a returned working set rather than assert semantic correctness.

#### Scenario: an absent query abstains
- **WHEN** a query matches nothing above the floor
- **THEN** `grounded` is false
- **AND** the assembled prompt contains no knowledge block
- **AND** the caller can skip the model call

#### Scenario: a lexical false positive can still be grounded
- **WHEN** incidental keyword overlap returns an irrelevant document above the floor
- **THEN** `grounded` is true because a working set was returned
- **AND** that value does not guarantee that the source answers the question
