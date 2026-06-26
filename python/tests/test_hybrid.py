"""Tests for the optional hybrid (BM25 + dense embeddings) retrieval path.

These use a DETERMINISTIC in-test embedder — no model download, no optional
dependency — so they run anywhere and prove the fusion logic, the opt-in gating,
and that the zero-dependency default is untouched. The real-model improvement is
measured separately by bench/paraphrase_eval.py.
"""
import math

from groundedwork import GroundedWork


def _toy_embedder(dim: int = 24):
    """A cheap, deterministic bag-of-known-tokens embedder. Only tokens seen in
    the corpus vocabulary contribute, so a query of all-unknown tokens yields a
    zero vector — faithfully modelling "this means nothing like our docs". Good
    enough to exercise fusion + the zero-norm grounding guard without a real model."""
    vocab = set()
    for d in DOCS:
        for tok in (d["title"] + " " + d["body"]).lower().replace(".", " ").split():
            vocab.add(tok)

    def encode(texts):
        out = []
        for t in texts:
            v = [0.0] * dim
            for tok in t.lower().replace(".", " ").split():
                if tok not in vocab:
                    continue  # unknown token: no signal (like a real OOV-ish model)
                h = 0
                for c in tok:
                    h = (h * 31 + ord(c)) % 1_000_003
                v[h % dim] += 1.0
            out.append(v)
        return out
    return encode


DOCS = [
    {"id": "refund", "title": "Refund Policy", "body": "Money back within 14 days of purchase. Full reimbursement."},
    {"id": "shipping", "title": "Shipping", "body": "Orders arrive in three to five business days via courier."},
    {"id": "twofa", "title": "Two Factor Authentication", "body": "Protect your account login with a second verification step."},
]


class TestOptInGating:
    def test_default_has_no_embedder(self):
        kb = GroundedWork()
        assert kb.embedder is None

    def test_default_path_is_pure_keyword(self):
        # Without an embedder, behavior is identical to classic BM25 retrieval.
        kb = GroundedWork(min_score=0.0).add_many(DOCS)
        r = kb.retrieve("refund")
        assert r.grounded
        assert r.hits[0].doc.id == "refund"

    def test_zero_dependency_default_still_works(self):
        # The whole point: no embedder, no numpy, no model — still retrieves.
        kb = GroundedWork(min_score=0.0).add_many(DOCS)
        assert kb.retrieve("shipping").hits[0].doc.id == "shipping"


class TestHybridRetrieval:
    def test_hybrid_accepts_callable_embedder(self):
        kb = GroundedWork(min_score=0.0, embedder=_toy_embedder()).add_many(DOCS)
        r = kb.retrieve("refund")
        assert r.grounded

    def test_hybrid_accepts_object_with_encode(self):
        class E:
            def encode(self, texts):
                return _toy_embedder()(texts)
        kb = GroundedWork(min_score=0.0, embedder=E()).add_many(DOCS)
        assert kb.retrieve("refund").grounded

    def test_hybrid_doc_embeddings_are_cached(self):
        calls = {"n": 0}
        base = _toy_embedder()

        def counting(texts):
            calls["n"] += 1
            return base(texts)

        kb = GroundedWork(min_score=0.0, embedder=counting).add_many(DOCS)
        kb.retrieve("a")
        first = calls["n"]
        kb.retrieve("b")
        # Doc embedding happens once (cached); only the per-query encode recurs.
        assert calls["n"] == first + 1

    def test_hybrid_preserves_abstention_on_garbage(self):
        # A query that neither keyword-matches nor embeds near anything must abstain.
        kb = GroundedWork(min_score=0.5, embedder=_toy_embedder()).add_many(DOCS)
        r = kb.retrieve("zzzzz qqqqq xkcd")
        assert not r.grounded

    def test_hybrid_keeps_exact_keyword_match(self):
        # Hybrid must not lose the obvious exact match.
        kb = GroundedWork(min_score=0.0, embedder=_toy_embedder()).add_many(DOCS)
        assert kb.retrieve("shipping").hits[0].doc.id == "shipping"


class TestHybridConfig:
    def test_rrf_k_default(self):
        assert GroundedWork().rrf_k == 60

    def test_dense_floor_default(self):
        assert abs(GroundedWork().dense_floor - 0.30) < 1e-9

    def test_custom_dense_floor(self):
        assert GroundedWork(dense_floor=0.5).dense_floor == 0.5
