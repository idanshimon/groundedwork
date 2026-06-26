# groundedwork playground

A zero-dependency, in-browser walkthrough that runs the **real** groundedwork
engine — not a mockup, not hardcoded numbers.

```bash
# from the repo root
make play          # then open http://localhost:8000
# or:
python playground/server.py
```

## What it shows

You type a question about a fictional coffee company's help docs, and the page
shows the actual pipeline, stage by stage:

1. **Tokenized query terms** — the real tokenizer output.
2. **BM25 scores vs the relevance floor** — real scores, with the floor drawn in.
3. **The decision** — grounded or abstained, and how many docs were injected.
4. **The assembled prompt** — the exact cache-aware message array your model
   would receive (stable `[system + prefs]` prefix first, retrieved knowledge last).

Five guided scenarios cover a grounded answer, an honest abstention, the keyword
paraphrase gap, a multi-term query, and a product lookup.

## How it's wired

`server.py` is a stdlib `http.server` (zero dependencies, matching the package
itself). It imports the installed `groundedwork` package and calls the same
`retrieve` / `prompt` / `messages` / `ask` methods the test suite uses — so every
score, floor decision, and prompt you see is the live engine. There are no
hardcoded scores anywhere; the UI only displays values the server returns.

groundedwork is **BYOM** — it never calls an LLM. The "answer" shown is the
source document's text; everything *before* it (retrieval, scoring, floor,
grounding, prompt assembly) is the real engine running.
