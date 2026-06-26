# Add MCP server (groundedwork as an agent tool)

## Why

Agent hosts — GitHub Copilot agent mode (GA, MCP-capable), Claude Desktop, Cursor, Hermes — consume MCP tools. Exposing groundedwork's retrieval as an MCP server lets any of them ground their answers in a knowledge base via a supported, standard interface, with no per-host extension. This is the right "intermediate layer between a prompt and the model" answer: work WITH the agent via MCP, not behind it via fragile interception.

Deferred roadmap item — authored now to capture the design; implemented after hybrid embeddings (code/doc retrieval quality gates how useful the tool is in an IDE).

## What Changes

- Add a thin MCP server that exposes groundedwork as tools: `retrieve(query)` and `messages(query)` over a configured corpus.
- The server wraps the existing engine; it adds no retrieval behavior, just an MCP transport.
- Ship as a separate entrypoint/extra so the core library stays transport-free.

## Capabilities

### New Capabilities
- `mcp-server`: expose groundedwork retrieval as MCP tools so any MCP-capable agent host can ground answers in a corpus.

## Cross-language impact

Transport layer, not retrieval behavior. The MCP server wraps the existing engine; it does not change scoring/floor/grounding. One reference implementation is sufficient (likely the TypeScript one, given the MCP/Node ecosystem) — this does NOT need to ship in both languages to preserve parity, because it adds no retrieval semantics. Design records this exception explicitly.

## Invariant check

- Parity: N/A for retrieval semantics (transport only); the wrapped engine keeps its parity. ✔
- Safe by default: grounding/floor/abstention come through unchanged from the wrapped engine. ✔
- BYOM: the server returns retrieval results / assembled prompts; it does NOT call a generation model. The agent host's model does. ✔
- Zero runtime dependency: ships as a separate extra/entrypoint; core library gains no dependency. ✔
- Small surface: two tools mirroring existing methods. ✔

## Impact

- New MCP server entrypoint (separate package/extra).
- Docs: an "use groundedwork from Copilot/Claude/Cursor" guide.

## Non-goals

- NOT transparent interception of a host's prompts (unsupported by the platforms; a known dead end).
- NOT a generation tool — it grounds, the host generates.
- NOT required in both languages — transport-only, no parity obligation.
