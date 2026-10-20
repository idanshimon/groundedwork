# Use groundedwork from Copilot, Claude, Cursor, or Hermes

groundedwork ships an MCP server: a tool an AI agent calls to retrieve grounded
context, or to get an honest "not in the knowledge base" when nothing matches.
It is a **tool the agent calls**, not a prompt interceptor. The agent decides to
call `retrieve`; groundedwork returns the working set or abstains. Nothing sits
between the model and its prompt.

## Install

```bash
pip install "groundedwork[mcp]"      # core stays zero-dependency; mcp is an extra
```

## Run

Point it at a corpus and start it (stdio transport):

```bash
GROUNDEDWORK_CORPUS=/path/to/docs groundedwork-mcp
```

`GROUNDEDWORK_CORPUS` is either:
- a JSON file: `[{"id","title","body","answer"?}, ...]` (or `{"corpus":[...]}`)
- a directory: every `*.md` / `*.txt` is indexed (filename = title, contents = body)

## Tools

| Tool | Returns |
|------|---------|
| `retrieve(query, top_k?)` | `{grounded, query, hits[]}` — empty hits when nothing clears the floor |
| `messages(query)` | cache-aware chat payload `{messages, grounded, sources, stable_prefix}` |
| `corpus_info()` | `{documents, ready}` |

The contract that matters: when the corpus has no answer, `grounded` is false and
`hits` is empty. The agent abstains instead of being fed distractors.

## Hermes Agent

```yaml
mcp_servers:
  groundedwork:
    command: groundedwork-mcp
    env:
      GROUNDEDWORK_CORPUS: /path/to/docs
```

## Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "groundedwork": {
      "command": "groundedwork-mcp",
      "env": { "GROUNDEDWORK_CORPUS": "/path/to/docs" }
    }
  }
}
```

## Copilot agent mode

Add the same `command` + `env` to your MCP config. Note: Copilot already retrieves
your code; groundedwork adds value over *documents* (support KBs, policies, runbooks),
not source files.

## Verify

```bash
GROUNDEDWORK_CORPUS=./examples/corpus.json groundedwork-mcp
# stderr: [groundedwork-mcp] indexed N docs from ./examples/corpus.json; ready.
```
