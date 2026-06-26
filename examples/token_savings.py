#!/usr/bin/env python3
"""Token-savings benchmark — the measured backing for "retrieval saves tokens".

This is NOT a feature of the library. It is an honest measurement you can run
on a real corpus with a REAL tokenizer (tiktoken), so the token claim is a
number you can defend instead of a marketing line.

Run:  python examples/token_savings.py
Needs:  pip install tiktoken   (the example's dependency, NOT the library's)

What it does:
  - Loads a real 392-doc corpus.
  - Counts the EXACT input tokens of the whole KB (tiktoken, o200k_base = GPT-4o).
  - Counts the EXACT input tokens of the retrieved working set, per query.
  - Reports the real reduction, averaged over many queries.

What it deliberately does NOT do:
  - It does not pretend retrieval is always the right call. When your KB FITS
    in the context window, putting the whole KB in a CACHED system prompt can be
    cheaper and faster than retrieving a fresh slice every query (a cache miss
    each time). This script prints that caveat with the numbers, because the
    honest story is "retrieval is necessary when the KB exceeds the window, and
    an optimization — with caveats — when it doesn't."
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from groundedwork import GroundedWork  # noqa: E402

try:
    import tiktoken
except ImportError:
    print("This benchmark needs a real tokenizer:  pip install tiktoken")
    sys.exit(2)

ENC = tiktoken.get_encoding("o200k_base")  # GPT-4o / GPT-4.1 family


def ntok(text: str) -> int:
    return len(ENC.encode(text))


def doc_text(d) -> str:
    # what you'd actually paste into a prompt for this doc.
    # accepts a corpus dict OR a retrieved Doc dataclass.
    title = d["title"] if isinstance(d, dict) else d.title
    body = d["body"] if isinstance(d, dict) else d.body
    return f"### {title}\n{body}"


def main():
    fx = json.loads((ROOT / "fixtures" / "corpus_large.json").read_text())
    docs = fx["corpus"]
    cfg = fx["config"]

    kb = GroundedWork(min_score=cfg["min_score"], top_k=cfg["top_k"]).add_many(docs)

    # 1. exact token cost of stuffing the ENTIRE KB into one prompt
    full_kb_tokens = sum(ntok(doc_text(d)) for d in docs)

    # 2. exact token cost of the RETRIEVED working set, per query, over a real
    #    query set (the answerable cases — realistic, in-domain questions)
    queries = [c["query"] for c in fx["answerable"]]
    per_query_tokens = []
    grounded_count = 0
    for q in queries:
        r = kb.retrieve(q)
        if r.hits:
            grounded_count += 1
        ws = "\n\n".join(doc_text(h.doc) for h in r.hits)
        per_query_tokens.append(ntok(ws))

    avg_ws = sum(per_query_tokens) / len(per_query_tokens)
    reduction = 100 * (1 - avg_ws / full_kb_tokens)

    # common context windows for the "does it even fit" question
    windows = {"GPT-4o (128k)": 128_000, "Claude (200k)": 200_000, "small (8k)": 8_192}

    print("=" * 70)
    print("TOKEN-SAVINGS BENCHMARK  (exact, tiktoken o200k_base)")
    print("=" * 70)
    print(f"corpus: {len(docs)} docs")
    print(f"whole-KB input tokens (stuff everything): {full_kb_tokens:,}")
    print(f"avg retrieved working-set tokens ({len(queries)} real queries): {avg_ws:,.0f}")
    print(f"  (top_k={cfg['top_k']}, {grounded_count}/{len(queries)} grounded)")
    print()
    print(f"REDUCTION per query: {reduction:.1f}%  "
          f"({full_kb_tokens:,} -> {avg_ws:,.0f} tokens)")
    print()
    print("Does the whole KB even fit in one prompt?")
    for name, w in windows.items():
        verdict = "FITS" if full_kb_tokens <= w else f"DOES NOT FIT ({full_kb_tokens / w:.1f}x over)"
        print(f"  {name:16} {verdict}")
    print()
    print("HONEST CAVEAT")
    print("-" * 70)
    if full_kb_tokens > min(windows.values()):
        print("When the KB exceeds the window, retrieval is REQUIRED — you")
        print("physically cannot paste it. The reduction above is the real saving.")
    print("When the KB FITS, retrieval is an OPTIMIZATION, not a free win:")
    print("a whole-KB prompt placed in a CACHED system prefix can be cheaper and")
    print("faster than retrieving a fresh slice that misses the cache every query.")
    print("Measure your own workload (cache hit-rate, latency) before assuming")
    print("retrieval is cheaper at small KB sizes. groundedwork's cache-aware")
    print("`messages()` ordering exists precisely so you can keep the cache.")


if __name__ == "__main__":
    main()
