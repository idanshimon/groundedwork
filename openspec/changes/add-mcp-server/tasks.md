# Tasks — MCP server

## 1. Server scaffold
- [ ] 1.1 Create a separate MCP server entrypoint/package that imports the existing groundedwork engine (no new retrieval logic).
- [ ] 1.2 Configure a corpus source (v1: a path/glob the server indexes on startup).
- [ ] 1.3 Validation: server starts and reports the indexed document count.

## 2. Tools
- [ ] 2.1 Expose a `retrieve` MCP tool wrapping `retrieve(query)` → hits + grounded flag.
- [ ] 2.2 Expose a `messages` MCP tool wrapping `messages(query)` → cache-optimal payload.
- [ ] 2.3 Validation: both tools callable over stdio MCP from a test client; abstention (grounded=false) is returned faithfully.

## 3. Host integration check
- [ ] 3.1 Verify the server registers and is callable from at least one MCP host (Claude Desktop or Copilot agent mode).
- [ ] 3.2 Validation: a grounded answer and an honest abstention both round-trip through the host.

## 4. Docs
- [ ] 4.1 Write a "use groundedwork from Copilot / Claude / Cursor" guide.
- [ ] 4.2 State plainly: it is a tool the agent calls, NOT a prompt interceptor.
- [ ] 4.3 Validation: the guide's setup steps reproduce on a clean machine.
