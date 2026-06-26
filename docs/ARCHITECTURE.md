# Architecture & Design

How groundedwork works, why it's built this way, and the exact interface contract both language implementations honor.

---

## 1. The problem

An LLM has a fixed context window. A knowledge base does not. Pasting every document into every request is slow, expensive, and eventually overflows the window. The job of groundedwork is to put **only the few documents that answer the current question** into the prompt — and to be **honest when none of them do**.

It is a *retrieval and prompt-assembly* layer. It deliberately does **not** call any model (see §6, Non-goals).

---

## 2. The algorithm: BM25 over a working set

### 2.1 Tokenization

```
tokenize(text):
    lowercase
    replace every non-alphanumeric run with a space
    split on whitespace
    drop tokens of length <= 1
    drop stopwords (a fixed ~60-word English list)
```

The stopword list and the length filter are part of the behavioral contract — both languages ship the **identical** list, because a divergence there changes scores. Title text is indexed with **2× weight** (concatenated twice before tokenizing), so a query word that appears in a document's title outranks the same word buried in its body.

### 2.2 BM25 scoring

For a query with tokens `Q` against document `d` in a corpus of `N` documents:

```
score(d, Q) = Σ_{t ∈ Q ∩ d}  IDF(t) · (f(t,d) · (k1 + 1)) / (f(t,d) + k1 · (1 - b + b · |d| / avgdl))

IDF(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))
```

- `f(t,d)` — raw term frequency of `t` in `d`
- `df(t)` — number of documents containing `t`
- `|d|` — token length of `d`; `avgdl` — mean document length
- `k1 = 1.5`, `b = 0.75` — standard Robertson/Zaragoza defaults, configurable

This is the classic Okapi BM25. There is **no embedding model, no vector store, no network call** — scoring is pure arithmetic over an in-memory inverted index, which is why it runs in microseconds and produces **identical results across languages** (verified to 9 decimal places by the parity harness, §5).

### 2.3 The relevance floor (a deliberate departure from naive top-k)

Naive keyword retrieval returns the top-`k` documents *always*, even when the best match is barely relevant. That injects distractors into the prompt on a miss — the leading cause of model hallucination we measured in the predecessor SDK.

groundedwork applies a **relevance floor** (`min_score`, default `2.0`): after ranking, any hit scoring below the floor is dropped. If nothing clears the floor, retrieval returns **empty**, and the result is marked **ungrounded**. This is the mechanism behind honest abstention.

```
retrieve(query):
    terms = tokenize(query)
    score every document; keep score > 0
    sort by score desc, take top_k
    drop any hit with score < min_score      # the floor
    grounded = (at least one hit survives)
```

---

## 3. Grounding & abstention

Two design defaults, both shipped *on*:

1. **The default system prompt is a grounding instruction** — "answer using ONLY the provided knowledge; if it's not there, say you don't have it; don't guess." In testing, a permissive prompt produced 5/72 hallucinations on trap questions; this prompt produced 0/72.

2. **`grounded` is a first-class return value.** When retrieval clears the floor, `grounded = true`. When nothing does, `grounded = false` and the caller can short-circuit to "I don't have that" **without spending a model call**.

The combination means the safe behavior is the default behavior. You have to opt *out* (set `min_score = 0`, replace the system prompt) to get the unsafe classic behavior.

---

## 4. Cache-aware prompt assembly

Prompt-caching endpoints (Anthropic `cache_control`, OpenAI / Azure automatic prefix caching) reuse a request prefix only if it is **byte-identical** to a previous one. So *where* you place volatile content matters.

`messages(query)` assembles the request in cache-optimal order:

```
[ system ]  stable_prefix() = grounding_prompt + prefs   ← never changes → CACHED
[ user   ]  "Knowledge:\n" + retrieved docs              ← volatile, placed LAST
[ user   ]  the question
```

`stable_prefix()` is query-independent, so it is identical on every call and the endpoint's prefix cache covers the entire system block. The retrieved knowledge — which changes per query — is placed *after* the cached region, so it never invalidates the cache. (The predecessor SDK places retrieved content *in* the system block, which busts the cache on every query.)

> **Boundary:** groundedwork *structures* the request for cache hits. It cannot *measure* your cache-hit-rate — that is endpoint response metadata (e.g. `cache_read_input_tokens`). Measure before/after at your call site.

---

## 5. Cross-language parity (the test bench)

Two implementations (Python reference, TypeScript mirror) are kept honest by a layered harness:

| Layer | What it proves | How |
|---|---|---|
| **Shared fixture** | both languages test against the *same* corpus + cases | `fixtures/nimbus.json`, loaded by both suites |
| **Unit suites** | each language's API behaves correctly | `pytest` (23 tests) · `node --test` (20 tests) |
| **Golden parity** | the two engines produce *numerically identical* output | `bench/parity.py` diffs canonical emitter output to 9 dp against `bench/golden.json` |

The parity harness is the spine. Each language has an emitter (`bench/emit_results.{py,mts}`) that runs `retrieve()` over every fixture case and prints a canonical JSON document (sorted keys, scores rounded to 9 dp). `bench/parity.py` runs both and asserts byte-equality, then checks against the committed golden snapshot. Adding a fixture case, or a third-language port, must reproduce the golden file or the harness fails.

```
make test     # python suite + typescript suite + parity, one command
make golden   # regenerate the snapshot after an intentional change
```

CI (`.github/workflows/tests.yml`) runs the Python suite on 3.9/3.11/3.13, the TS suite on Node 18/20/22, then the parity job gated behind both.

---

## 6. Non-goals (what groundedwork deliberately does NOT do)

- **It does not call any LLM.** No provider SDK, no API keys, no `base_url` config. You bring your own model client (local Ollama/llama.cpp/vLLM, Azure OpenAI, OpenAI, Anthropic — anything). `messages()`/`prompt()` hand you a payload; you make the call. This is why "what about local / Azure / X?" is answered by "all of them, zero config."
- **It does not embed.** BM25 keyword retrieval only, by choice (transparent, fast, model-free, deterministic). The cost is the paraphrase gap (§7).
- **It is not a persistence layer (yet).** v0.1 is in-memory. On-disk indexes are roadmap.

---

## 7. Known limitation: the paraphrase gap

BM25 matches on shared *words*. A question phrased with different words than the source document can miss — and worse, a coincidental word overlap can surface the **wrong** document with false confidence (e.g. "show up at my door" matching a "Pausing" doc on the stray word "up"). This is inherent to keyword retrieval, not a bug.

The grounding prompt and the relevance floor *limit the blast radius* of a miss (the model is told not to guess; weak matches are dropped). The actual *fix* is hybrid retrieval (BM25 + a small local embedding model), which is the **v0.2** headline — shipped opt-in so the zero-dependency default stays zero-dependency. The fixture encodes this honestly: the "show up at my door" case asserts the wrong-doc behavior, so any future embedding work must visibly change it.

---

## 8. Interface contract

Both languages expose the same surface (names adjusted to each language's convention).

| Concept | Python | TypeScript |
|---|---|---|
| Construct | `GroundedWork(min_score=2.0, top_k=3, k1=1.5, b=0.75, system_prompt=…, prefs="")` | `new GroundedWork({ minScore, topK, k1, b, systemPrompt, prefs })` |
| Index one | `add(id, title, body, answer="", **meta) -> self` | `add(doc) -> this` |
| Index many | `add_many(list[dict]) -> self` | `addMany(Doc[]) -> this` |
| Retrieve | `retrieve(query, top_k=None) -> Retrieval` | `retrieve(query, topK?) -> Retrieval` |
| Payload | `prompt(query) -> {system, knowledge, user, grounded, sources}` | `prompt(query) -> {…}` |
| Cache-optimal | `messages(query) -> {messages, grounded, sources, stable_prefix}` | `messages(query) -> {…, stablePrefix}` |
| Stable prefix | `stable_prefix() -> str` | `stablePrefix() -> string` |
| Demo answer | `ask(query) -> {grounded, answer, source}` | `ask(query) -> {…}` |
| Size | `len(kb)` | `kb.size` |

**`Retrieval`** = `{ query, hits: [{ doc, score, matched }], terms, grounded }`.
`grounded` is `true` iff `hits` is non-empty (i.e. something cleared the floor).

The contract is enforced, not just documented: the shared fixture + golden parity harness fail if either implementation drifts from this behavior.
