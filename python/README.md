# groundedwork

**Retrieval that knows when it doesn't know.**

A tiny, dependency-free retrieval layer for giving an LLM a knowledge base bigger than its context window. It pulls only the handful of documents that answer the question into the prompt — and, crucially, **stays silent when nothing matches** instead of feeding the model plausible-looking junk.

Same API in **Python** and **TypeScript**. Zero runtime dependencies. No vector database, no embeddings server, no API key required to run the tests.

```python
from groundedwork import GroundedWork

kb = GroundedWork().add_many([
    {"id": "returns", "title": "Returns & Refunds",
     "body": "Return any unopened bag within 30 days for a full refund."},
    {"id": "shipping", "title": "US Shipping",
     "body": "Orders arrive in 3-5 business days. Free over $40."},
])

kb.ask("How do I get a refund?")
# {'grounded': True, 'answer': 'Return any unopened bag...', 'source': 'returns'}

kb.ask("What's the capital of France?")
# {'grounded': False, 'answer': "I don't have that in my knowledge base, so I won't guess.", 'source': None}
```

```typescript
import { GroundedWork } from "groundedwork";

const kb = new GroundedWork().addMany([
  { id: "returns", title: "Returns & Refunds", body: "Return any unopened bag within 30 days for a full refund." },
  { id: "shipping", title: "US Shipping", body: "Orders arrive in 3-5 business days. Free over $40." },
]);

kb.ask("How do I get a refund?");
// { grounded: true, answer: "Return any unopened bag...", source: "returns" }
```

---

## Why this exists

This is a from-scratch reimplementation inspired by [ContextForge](https://github.com/Betanu701/ContextForge) by Derek Thomas — a genuinely clever SDK that pioneered the "flat working-set" idea this package builds on. Full credit to that project for the core mechanism (see [Lineage & credit](#lineage--credit) at the bottom).

We spent a week empirically testing ContextForge across 8 models and 216 trials. groundedwork ships the lessons from that testing **as defaults**, so you can't accidentally hold it wrong:

| Lesson we measured | ContextForge default | groundedwork default |
|---|---|---|
| **Grounding** — does the model guess when retrieval misses? | A permissive prompt → **5/72 hallucinations** in our test | A strict grounding prompt → **0/72**. On by default. |
| **Relevance floor** — what happens when nothing matches? | Always returns top-k, injecting distractors | A score floor → returns **nothing** when nothing is relevant. On by default. |
| **One obvious path** | `chat()` grows the transcript; `infinite.query()` stays flat — the quickstart is the *wrong* one | A single flat API. The intuitive path is the safe path. |
| **Abstention** | Implicit; you prompt-engineer it per call | `result.grounded == False` is a first-class return signal |
| **Languages** | Python only | Python **and** TypeScript, behavior verified identical |

The full write-up with the data is in the [companion article](#).

---

## The honest part: where keyword retrieval breaks

groundedwork uses BM25 keyword matching. It is fast, transparent, and needs no model — but it matches on **words**, so it has one real blind spot: **paraphrase**.

Ask *"when does it show up at my door?"* against a doc that says *"orders arrive in 3-5 days"* and they share zero content words. Worse, a stray word can match the **wrong** doc with false confidence. This is a property of keyword search, not a bug — and it's exactly why grounding + the relevance floor matter (they limit the damage when a miss happens).

**The fix for paraphrase is hybrid retrieval** (keyword + a small local embedding model). That's the headline feature of **v0.2**, shipped as an opt-in flag so the zero-dependency default stays zero-dependency. We're shipping the honest keyword version first, with the limitation documented, rather than hiding it.

---

## Install

```bash
# Python (>=3.9, stdlib only)
pip install groundedwork

# TypeScript / JavaScript (Node >=18)
npm install groundedwork
```

## API

Both languages expose the same four methods:

| Method | What it does |
|---|---|
| `add(...)` / `add_many([...])` | Index a document (or many). Chainable. |
| `retrieve(query)` | Return the relevance-floored working set: `{ hits, terms, grounded }`. |
| `prompt(query)` | Build the LLM message payload: `{ system, knowledge, user, grounded, sources }`. On a miss, `knowledge` is empty and `grounded` is `False` — short-circuit to an honest abstention without spending a token. |
| `ask(query)` | Dependency-free demo answerer (no LLM call). Returns the top grounded doc's answer, or an honest abstention. Real apps pass `prompt(query)` to their own model. |

### Using it with a real model

`ask()` is for demos and tests. In production you own the model call — groundedwork just builds the grounded payload:

```python
p = kb.prompt(user_question)
if not p["grounded"]:
    return "I don't have that in our docs."        # save the API call entirely
reply = my_llm.chat(system=p["system"], context=p["knowledge"], user=p["user"])
```

### Tuning

```python
GroundedWork(
    min_score=2.0,   # relevance floor. 0.0 = classic always-return-top-k. Higher = stricter.
    top_k=3,         # max docs per working set
)
```

---

## Tests & cross-language parity

The two implementations are kept honest by a **shared fixture** (`fixtures/nimbus.json`): one corpus, one set of expected-retrieval cases, consumed by *both* test suites. If Python and TypeScript both pass, they are behaving identically — including on the tricky paraphrase-failure case.

```bash
# Python
cd python && pip install -e ".[dev]" && pytest        # 19 passed

# TypeScript
cd ts && npm install && npm test                       # 16 passed
```

---

## Roadmap

- **v0.1** (now) — Python + TypeScript, BM25 + relevance floor + grounding, shared-fixture parity.
- **v0.2** — opt-in hybrid retrieval (local embeddings) to close the paraphrase gap. Persistent on-disk store. Streaming-friendly `prompt()`.
- **later** — more language mirrors (Go, Rust) against the same fixture; pluggable rankers.

---

## Lineage & credit

groundedwork stands on the shoulders of **[ContextForge](https://github.com/Betanu701/ContextForge) by Derek Thomas.** The core idea — keep a flat, retrieved "working set" so an LLM's context cost stops scaling with how much you know — is his. We reimplemented it from scratch in two languages and shipped our empirical lessons (grounding-by-default, the relevance floor, the single intuitive API, the abstention signal) as defaults. If you're building code-heavy or multi-turn agent systems, go look at ContextForge too — it goes deeper on those.

MIT licensed. Built for the empirical version — see the [companion article](#) for the data behind every claim above.
