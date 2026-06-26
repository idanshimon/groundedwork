# MCP server

## ADDED Requirements

### Requirement: the server exposes retrieval as MCP tools
The MCP server MUST expose `retrieve` and `messages` as MCP tools that wrap the existing groundedwork engine without changing retrieval behavior.

#### Scenario: an agent host calls the retrieve tool
- **WHEN** an MCP-capable host calls the `retrieve` tool with a query
- **THEN** the server returns the relevance-floored working set and the grounded flag from the wrapped engine

### Requirement: the server never calls a generation model
The MCP server MUST return retrieval results or assembled prompts only, and MUST NOT call a generation model, preserving the BYOM boundary.

#### Scenario: abstention round-trips without generation
- **WHEN** the `messages` tool is called with a query that matches nothing in the corpus
- **THEN** the server returns grounded=false with no knowledge block
- **AND** no generation model is invoked by the server

### Requirement: the server is a separate entrypoint that adds no core dependency
The MCP server MUST ship as a separate entrypoint or extra so that the core groundedwork library gains no transport dependency.

#### Scenario: core install stays transport-free
- **WHEN** groundedwork core is installed without the MCP extra
- **THEN** the core library imports and runs with no MCP/transport dependency present
