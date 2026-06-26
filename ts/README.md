# groundedwork (TypeScript)

**Retrieval that knows when it doesn't know.**

A tiny, zero-dependency retrieval layer for giving an LLM a knowledge base bigger than its context window. It pulls only the documents that answer the question into the prompt — and stays silent when nothing matches instead of feeding the model plausible-looking junk.

The TypeScript mirror of the [Python package](https://github.com/idanshimon/groundedwork) — same API, behavior verified identical against a shared test fixture.

```typescript
import { GroundedWork } from "groundedwork";

const kb = new GroundedWork().addMany([
  { id: "returns", title: "Returns & Refunds", body: "Return any unopened bag within 30 days for a full refund." },
  { id: "shipping", title: "US Shipping", body: "Orders arrive in 3-5 business days. Free over $40." },
]);

kb.ask("How do I get a refund?");
// { grounded: true, answer: "Return any unopened bag...", source: "returns" }

kb.ask("What's the capital of France?");
// { grounded: false, answer: "I don't have that in my knowledge base, so I won't guess.", source: null }
```

## Install

```bash
npm install groundedwork   # Node >= 18, zero runtime dependencies
```

## API

| Method | What it does |
|---|---|
| `add(doc)` / `addMany(docs)` | Index a document (or many). Chainable. |
| `retrieve(query)` | The relevance-floored working set: `{ hits, terms, grounded }`. |
| `prompt(query)` | LLM message payload: `{ system, knowledge, user, grounded, sources }`. On a miss, `knowledge` is `""` and `grounded` is `false`. |
| `ask(query)` | Dependency-free demo answerer. Real apps pass `prompt(query)` to their own model. |

### With a real model

```typescript
const p = kb.prompt(userQuestion);
if (!p.grounded) return "I don't have that in our docs.";   // skip the API call
const reply = await myLlm.chat({ system: p.system, context: p.knowledge, user: p.user });
```

## Why this exists & the honest limitation

Built on the ideas of [ContextForge](https://github.com/Betanu701/ContextForge) by Derek Thomas; the improvements here (grounding + relevance floor + abstention, all on by default) come from empirically testing that SDK. groundedwork uses BM25 keyword matching — fast and transparent, but it matches on **words**, so paraphrased questions can miss. Hybrid embedding retrieval to close that gap is the v0.2 headline. Full story and the data: see the [Python README](https://github.com/idanshimon/groundedwork) and the companion article.

MIT licensed.
