# grounding-abstention Specification

## Purpose
Grounded-by-default prompting and first-class abstention. The default system prompt instructs answer-only-from-knowledge; `grounded` is a real return value that is false when nothing clears the relevance floor, and no knowledge is injected in that case. The load-bearing guarantee: groundedwork never fabricates — on a miss `ask` returns an honest "I don't have that" with a null source, and the caller can skip the model entirely.
## Requirements
### Requirement: grounded-by-default system prompt
The default assembled prompt MUST instruct the model to answer only from the provided knowledge and to refuse when the knowledge does not contain the answer.

#### Scenario: the default prompt carries grounding instructions
- **WHEN** a prompt is assembled without a custom system prompt
- **THEN** the system text instructs answer-only-from-knowledge and no-guessing

### Requirement: abstention is a first-class return value
Retrieval and prompt assembly MUST expose a `grounded` boolean that is false when nothing clears the relevance floor, and MUST inject no knowledge in that case.

#### Scenario: an absent query abstains
- **WHEN** a query matches nothing above the floor
- **THEN** `grounded` is false
- **AND** the assembled prompt contains no knowledge block
- **AND** the caller can skip the model call

### Requirement: abstention answers honestly
The `ask` convenience MUST return an honest "I don't have that" style answer with a null source when the query is ungrounded, rather than fabricating an answer.

#### Scenario: ask abstains without fabricating
- **WHEN** `ask` is called with an out-of-corpus question
- **THEN** the returned answer states the information is not available
- **AND** the source is null

