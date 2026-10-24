# grounding-abstention Specification

## Purpose
Grounded-by-default prompting and first-class abstention. The default system prompt instructs answer-only-from-knowledge; `grounded` is a real return value that is false when nothing clears the relevance floor, and no knowledge is injected in that case. On a miss, `ask` returns an abstention with a null source, and the caller can skip the model entirely. A returned working set can still be irrelevant; `grounded=true` is not semantic verification, and prompt instructions cannot guarantee a downstream model's answer correctness.
## Requirements
### Requirement: grounded-by-default system prompt
The default assembled prompt MUST instruct the model to answer only from the provided knowledge and to refuse when the knowledge does not contain the answer.

#### Scenario: the default prompt carries grounding instructions
- **WHEN** a prompt is assembled without a custom system prompt
- **THEN** the system text instructs answer-only-from-knowledge and no-guessing

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

### Requirement: abstention answers honestly
The `ask` convenience MUST return an honest "I don't have that" style answer with a null source when the query is ungrounded, rather than fabricating an answer.

#### Scenario: ask abstains without fabricating
- **WHEN** `ask` is called with an out-of-corpus question
- **THEN** the returned answer states the information is not available
- **AND** the source is null

### Requirement: a custom system prompt overrides the grounded default
The engine MUST accept a caller-supplied system prompt that replaces the default grounding prompt in the assembled output, so callers can tailor instructions while keeping retrieval and abstention behavior unchanged.

#### Scenario: a custom system prompt is used when provided
- **WHEN** an engine is constructed with a custom `system_prompt`
- **THEN** the assembled prompt's system content is the custom prompt
- **AND** the relevance floor and `grounded` decision are unchanged

#### Scenario: the grounded default is used when none is provided
- **WHEN** an engine is constructed without a custom system prompt
- **THEN** the assembled prompt uses the default grounding instructions

