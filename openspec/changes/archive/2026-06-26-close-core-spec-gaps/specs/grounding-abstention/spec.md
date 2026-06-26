# Grounding and abstention

## ADDED Requirements

### Requirement: a custom system prompt overrides the grounded default
The engine MUST accept a caller-supplied system prompt that replaces the default grounding prompt in the assembled output, so callers can tailor instructions while keeping retrieval and abstention behavior unchanged.

#### Scenario: a custom system prompt is used when provided
- **WHEN** an engine is constructed with a custom `system_prompt`
- **THEN** the assembled prompt's system content is the custom prompt
- **AND** the relevance floor and `grounded` decision are unchanged

#### Scenario: the grounded default is used when none is provided
- **WHEN** an engine is constructed without a custom system prompt
- **THEN** the assembled prompt uses the default grounding instructions
