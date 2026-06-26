# groundedwork

**Retrieval that knows when it doesn't know.**

A tiny, dependency-free retrieval layer that gives an LLM a knowledge base bigger than its context window — pulling in only the documents that answer the question, and staying honestly silent when nothing matches.

Same intuitive API in **Python** and **TypeScript**, with behavior verified identical against a shared test fixture.

| | Package | Tests | Install |
|---|---|---|---|
| 🐍 **Python** | [`python/`](python/) · `groundedwork` | 19 passing | `pip install groundedwork` |
| 🟦 **TypeScript** | [`ts/`](ts/) · `groundedwork` | 16 passing | `npm install groundedwork` |

```python
from groundedwork import GroundedWork

kb = GroundedWork().add_many(docs)
kb.ask("How do I get a refund?")     # {'grounded': True,  'answer': '...', 'source': 'returns'}
kb.ask("capital of France?")          # {'grounded': False, 'answer': "I don't have that...", 'source': None}
```

## What makes it different

Built on the ideas of **[ContextForge](https://github.com/Betanu701/ContextForge)** by Derek Thomas. After a week of empirically testing that SDK (8 models, 216 trials), we shipped the lessons as **defaults**:

- **Grounded by default** — a strict "answer only from the knowledge, don't guess" prompt. Measured 0/72 hallucinations vs 5/72 for a permissive prompt.
- **Relevance floor by default** — when nothing matches well, inject *nothing*, not the least-bad distractors.
- **Abstention is first-class** — `grounded == False` is a real return value, so you can skip the LLM call entirely on a miss.
- **Cache-aware assembly** — `messages()` pins a stable `[system + prefs]` prefix dead-first and puts the volatile retrieved knowledge *last*, so a prompt-caching endpoint (Anthropic / OpenAI / Azure) reuses the whole prefix across calls. ContextForge does the opposite — it buries retrieved content in the system block, busting the cache every query.
- **One obvious, flat API** — the intuitive path is the safe path.
- **Cross-language parity** — Python and TypeScript run the same `fixtures/nimbus.json`, so they can't silently drift.

## The honest limitation

It's BM25 keyword retrieval — fast, transparent, no model required, but it matches on words, so **paraphrased questions can miss** (and occasionally match the wrong doc with false confidence). Grounding + the floor limit the blast radius; **hybrid embedding retrieval to actually close the gap is the v0.2 headline**, opt-in so the zero-dependency default stays zero-dependency. We shipped the honest version first.

## Repository layout

```
groundedwork/
├── python/         pip package — reference implementation
├── ts/             npm package — TypeScript mirror
├── fixtures/       shared cross-language test fixtures (the parity contract)
└── LICENSE         MIT
```

## Credit

The core mechanism — a flat, retrieved "working set" so context cost stops scaling with knowledge size — is Derek Thomas's, from [ContextForge](https://github.com/Betanu701/ContextForge). groundedwork is an independent reimplementation that ships our empirical lessons as defaults and adds a second language. If you build code-heavy or multi-turn agents, look at ContextForge too.

MIT licensed. Built for the empirical version.
