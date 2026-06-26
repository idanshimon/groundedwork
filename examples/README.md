# Examples

Runnable examples for groundedwork. The library itself has zero dependencies;
a couple of examples pull in an optional package (noted below) to demonstrate a
real integration — those deps are the *example's*, not the library's.

| File | What it shows | Extra dep |
|------|---------------|-----------|
| `quickstart.py` | The 60-second tour — add docs, retrieve, ground, abstain | none |
| `quickstart.ts` | The same tour in TypeScript | none |
| `byo_model.py` | Wire the grounded prompt to a real LLM (local / Azure / OpenAI) | an OpenAI-compatible client |
| `token_savings.py` | **Measured** input-token reduction with a real tokenizer | `tiktoken` |

## token_savings.py — the honest token claim

"Retrieval saves tokens" is easy to say and easy to oversell. This script
*measures* it instead, on a real 392-doc corpus with the actual GPT-4o tokenizer
(`tiktoken`, `o200k_base`):

```
pip install tiktoken
python examples/token_savings.py
```

It reports the exact whole-KB token cost vs. the average retrieved working-set
cost (a ~99% per-query reduction on this corpus), **and** it prints the honest
caveat: when your KB *fits* the context window, retrieval is an optimization —
not a free win — because a whole-KB prompt in a *cached* system prefix can be
cheaper and faster than retrieving a fresh slice that misses the cache every
query. The script tells you which regime you're in rather than assuming
retrieval is always cheaper.
