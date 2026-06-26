# byom Specification

## Purpose
The architectural guarantee that defines what groundedwork is: it performs retrieval and prompt assembly only and NEVER calls a generation model. It accepts, stores, and requires no API keys, tokens, or model endpoint — `messages()` returns a provider-neutral message array the caller sends to any model (local, cloud, or self-hosted). This is the load-bearing reason groundedwork works with every model and touches no credentials; a future method that called an LLM would be a visible violation of this capability, not a silent regression.
## Requirements
### Requirement: groundedwork never calls a generation model
The library MUST perform retrieval and prompt assembly only, and MUST NOT call any generation model. The caller owns the model invocation.

#### Scenario: retrieval and assembly invoke no model
- **WHEN** any of `retrieve`, `prompt`, `messages`, or `ask` is called
- **THEN** the result is computed with no call to a generation model
- **AND** no network request to a model endpoint is made

### Requirement: groundedwork holds no model credentials or endpoint configuration
The library MUST NOT accept, store, or require API keys, tokens, or a model endpoint/base URL, so that it stays decoupled from any specific model provider.

#### Scenario: no credential configuration exists
- **WHEN** an engine is constructed
- **THEN** it exposes no parameter for an API key, token, or model base URL
- **AND** it can index and retrieve with no provider configuration of any kind

### Requirement: assembled prompts are portable across any model
The `messages` output MUST be a provider-neutral message array the caller can send to any chat-style model, so a local, cloud, or self-hosted model all consume the same assembled prompt.

#### Scenario: the same payload targets different models
- **WHEN** `messages` assembles a prompt for a query
- **THEN** the returned message array carries roles and content with no provider-specific fields
- **AND** the caller can send it to any chat-completion-compatible model unchanged

