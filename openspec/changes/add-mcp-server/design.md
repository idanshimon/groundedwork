# Design — MCP server

## Context

MCP is the supported way to give an agent host an external tool. groundedwork's `retrieve()`/`messages()` map directly to MCP tools. This is a thin transport wrapper over the existing engine.

## Goals / Non-Goals

**Goals:**
- Expose `retrieve` and `messages` as MCP tools over a configured corpus.
- Keep the core library transport-free (server is a separate extra/entrypoint).

**Non-Goals:**
- Changing any retrieval behavior.
- Transparent prompt interception (platform-unsupported).
- Dual-language parity (transport-only, no retrieval semantics).

## Decisions

1. **Wrap, don't reimplement.** The server imports the existing engine and exposes its methods as MCP tools. Zero new retrieval logic.
2. **One reference implementation is enough.** Because it adds no retrieval semantics, the MCP server is exempt from the cross-language parity rule. Likely TypeScript (Node/MCP ecosystem fit). Documented exception.
3. **Separate entrypoint/extra.** Core library gains no MCP/transport dependency.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Users expect it to intercept Copilot prompts | Docs state plainly: it's a tool the agent calls, not an interceptor. |
| Corpus configuration complexity | v1 takes a simple configured corpus path; richer config deferred. |

## Open Questions

1. Stdio vs HTTP MCP transport for v1? Recommendation: stdio (simplest, matches local IDE use).
