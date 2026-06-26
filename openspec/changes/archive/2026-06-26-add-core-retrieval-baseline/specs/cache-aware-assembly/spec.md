# Cache-aware assembly

## ADDED Requirements

### Requirement: stable prefix precedes volatile knowledge
The `messages` assembly MUST place the stable `[system + prefs]` content first and the volatile retrieved knowledge last, so a prompt-caching endpoint can reuse the prefix across queries.

#### Scenario: prefix is identical across different queries
- **WHEN** `messages` is assembled for two different queries with the same configuration
- **THEN** the leading `[system + prefs]` prefix is byte-identical between them
- **AND** the retrieved knowledge appears after that prefix

### Requirement: knowledge is never placed in the system block
The assembly MUST keep retrieved knowledge out of the system message so that injecting per-query knowledge does not invalidate the cached system prefix.

#### Scenario: system block excludes retrieved knowledge
- **WHEN** a grounded prompt is assembled
- **THEN** the retrieved documents appear in a later message, not in the system block

### Requirement: per-user preferences pin into the stable prefix
The assembly MUST allow caller-supplied `prefs` to be pinned into the stable prefix so a persona or per-user preamble is cached alongside the system prompt.

#### Scenario: prefs are part of the cached prefix
- **WHEN** `prefs` are supplied at construction
- **THEN** the stable prefix includes those prefs and remains identical across queries
