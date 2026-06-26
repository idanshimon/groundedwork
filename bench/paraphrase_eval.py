#!/usr/bin/env python3
"""Paraphrase evaluation — the empirical before/after for hybrid retrieval.

Measures recall@1 on the paraphrase cases (queries that share MEANING but not
WORDS with the relevant doc) for:
  - keyword-only (pure BM25, the zero-dependency default)
  - hybrid (BM25 + dense embeddings fused via RRF, opt-in)

and confirms hybrid does NOT regress the normal exact-match cases or the
abstention guarantee.

Requires the optional embedder:  pip install "groundedwork[hybrid]"  (model2vec)
Run:  python bench/paraphrase_eval.py

This is the honest measurement behind the README's hybrid claims. The result is
NOT "embeddings fix everything" — it's a real, bounded improvement on the hard
cases with zero cost to the easy ones.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import groundedwork as g  # noqa: E402

FIXTURE = json.loads((ROOT / "fixtures" / "corpus_large.json").read_text())
DOCS = FIXTURE["corpus"]
CFG = FIXTURE["config"]


def load_embedder():
    try:
        from model2vec import StaticModel
    except ImportError:
        print("model2vec not installed. Run:  pip install 'groundedwork[hybrid]'")
        sys.exit(2)
    return StaticModel.from_pretrained("minishlab/potion-base-8M")


def top1(engine, q):
    hits = engine.retrieve(q).hits
    return hits[0].doc.id if hits else "(abstain)"


def main():
    embedder = load_embedder()
    kw = g.GroundedWork(min_score=CFG["min_score"]).add_many(DOCS)
    hy = g.GroundedWork(min_score=CFG["min_score"], embedder=embedder).add_many(DOCS)

    para = FIXTURE["paraphrase"]
    kw_hits = hy_hits = 0
    print("=" * 78)
    print("PARAPHRASE RECALL@1  (query shares meaning, not words, with the doc)")
    print("=" * 78)
    print(f"{'query':42} {'keyword':14} {'hybrid':14}")
    print("-" * 78)
    for c in para:
        q, exp = c["query"], c["expect_top"]
        k, h = top1(kw, q), top1(hy, q)
        kw_hits += k == exp
        hy_hits += h == exp
        km = "✓" if k == exp else "✗"
        hm = "✓" if h == exp else "✗"
        print(f"{q[:40]:42} {km} {k[:12]:12} {hm} {h[:12]:12}")
    n = len(para)
    print("-" * 78)
    print(f"{'RECALL@1':42} {kw_hits}/{n}{'':11} {hy_hits}/{n}")

    # regression guard: normal exact-match answerable cases
    ans = FIXTURE["answerable"]
    ak = ah = 0
    for c in ans:
        q, exp = c["query"], c["expect_top"]
        ak += top1(kw, q) == exp
        ah += top1(hy, q) == exp
    print()
    print(f"NORMAL RECALL@1 ({len(ans)} exact-match cases):  "
          f"keyword {ak}/{len(ans)}  →  hybrid {ah}/{len(ans)}")
    assert ah >= ak, "REGRESSION: hybrid lost normal cases keyword had"

    # abstention guard
    absent = FIXTURE["absent"]
    bad = [q for q in absent if hy.retrieve(q).grounded]
    print(f"ABSTENTION ({len(absent)} out-of-corpus): hybrid wrongly grounded {len(bad)}")
    assert not bad, f"hybrid broke abstention on: {bad}"

    print()
    print(f"SUMMARY: paraphrase {kw_hits}/{n} → {hy_hits}/{n}"
          f"  (+{hy_hits - kw_hits}), normal {ah}/{len(ans)} preserved, "
          f"abstention intact.")
    if hy_hits <= kw_hits:
        print("WARNING: hybrid did not improve paraphrase recall on this fixture.")
        sys.exit(1)


if __name__ == "__main__":
    main()
