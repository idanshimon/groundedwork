"""groundedwork test suite — runs against the SHARED cross-language fixture.

The same fixtures/nimbus.json is consumed by the TypeScript suite, so a passing
run in both languages proves the implementations are behaviorally identical.
"""
import json
import pathlib

import pytest

from groundedwork import GroundedWork, GROUNDING_PROMPT, tokenize

FIXTURE = json.loads(
    (pathlib.Path(__file__).parents[2] / "fixtures" / "nimbus.json").read_text()
)


def build():
    cfg = FIXTURE["config"]
    gw = GroundedWork(min_score=cfg["min_score"], top_k=cfg["top_k"], k1=cfg["k1"], b=cfg["b"])
    gw.add_many(FIXTURE["corpus"])
    return gw


@pytest.fixture
def gw():
    return build()


# -- parity: the shared cases ------------------------------------------------
@pytest.mark.parametrize("case", FIXTURE["cases"], ids=[c["query"] for c in FIXTURE["cases"]])
def test_shared_fixture_cases(gw, case):
    r = gw.retrieve(case["query"])
    assert r.grounded == case["grounded"], f"grounded mismatch for {case['query']!r}"
    if case["expect_top"] is not None:
        assert r.hits, f"expected a hit for {case['query']!r}"
        assert r.hits[0].doc.id == case["expect_top"], (
            f"{case['query']!r}: expected top {case['expect_top']!r}, got {r.hits[0].doc.id!r}"
        )
    else:
        assert not r.hits, f"expected NO hits (abstain) for {case['query']!r}"


# -- the differentiators -----------------------------------------------------
class TestGroundedByDefault:
    def test_default_prompt_is_grounded(self, gw):
        p = gw.prompt("How do I get a refund?")
        low = p["system"].lower()
        assert "only" in low and ("guess" in low or "do not have" in low)
        assert p["system"] == GROUNDING_PROMPT

    def test_absent_query_injects_no_knowledge(self, gw):
        # genuinely-absent query with zero corpus overlap -> abstain, nothing to bluff from
        p = gw.prompt("xyzzy quantum platypus protocol")
        assert p["grounded"] is False
        assert p["knowledge"] == ""          # nothing to bluff from
        assert p["sources"] == []

    def test_ask_abstains_when_ungrounded(self, gw):
        a = gw.ask("xyzzy quantum platypus")
        assert a["grounded"] is False
        assert a["source"] is None
        assert "don't have" in a["answer"].lower() or "won't guess" in a["answer"].lower()

    def test_ask_answers_when_grounded(self, gw):
        a = gw.ask("How do I get a refund?")
        assert a["grounded"] is True
        assert a["source"] == "returns"


class TestRelevanceFloor:
    def test_floor_zero_returns_top_k_classic(self):
        gw = GroundedWork(min_score=0.0, top_k=3).add_many(FIXTURE["corpus"])
        r = gw.retrieve("xyzzy quantum platypus")
        # nonsense still has zero term overlap, so even floor=0 yields nothing here
        assert r.hits == []
        # but a weak real query returns distractors at floor 0...
        weak = gw.retrieve("coffee")
        assert len(weak.hits) >= 1

    def test_floor_drops_weak_matches(self):
        low = GroundedWork(min_score=0.0, top_k=5).add_many(FIXTURE["corpus"])
        high = GroundedWork(min_score=5.0, top_k=5).add_many(FIXTURE["corpus"])
        q = "coffee"
        assert len(high.retrieve(q).hits) <= len(low.retrieve(q).hits)

    def test_floor_keeps_strong_match(self, gw):
        r = gw.retrieve("How do I make a pour over?")
        assert r.grounded and r.hits[0].doc.id == "pourover"


class TestApi:
    def test_add_is_chainable(self):
        gw = GroundedWork().add("a", "A", "alpha body").add("b", "B", "beta body")
        assert len(gw) == 2

    def test_tokenize_drops_stopwords(self):
        assert "the" not in tokenize("the quick brown fox")
        assert "quick" in tokenize("the quick brown fox")

    def test_prompt_shape(self, gw):
        p = gw.prompt("refund")
        assert set(p) == {"system", "knowledge", "user", "grounded", "sources"}


class TestCacheAwareAssembly:
    """The fix for the cache-hit advice given to ContextForge's author: pin a
    stable [system + prefs] prefix and put the volatile retrieved knowledge LAST,
    so a prompt-caching endpoint reuses the whole prefix across calls.
    """

    def test_stable_prefix_is_query_independent(self, gw):
        # the cache target must be byte-identical regardless of the question
        a = gw.messages("How do I get a refund?")["stable_prefix"]
        b = gw.messages("Do you have decaf?")["stable_prefix"]
        assert a == b
        assert a == gw.stable_prefix()

    def test_prefs_are_pinned_into_prefix(self):
        gw = GroundedWork(prefs="The user is on the Pro plan and prefers terse answers.")
        gw.add_many(FIXTURE["corpus"])
        assert "Pro plan" in gw.stable_prefix()
        # prefs live in the STABLE prefix, never in the volatile knowledge block
        m = gw.messages("How do I get a refund?")
        assert "Pro plan" in m["messages"][0]["content"]
        assert m["messages"][0]["role"] == "system"

    def test_knowledge_comes_last_before_user(self, gw):
        m = gw.messages("How do I get a refund?")["messages"]
        # order: system(prefix) -> knowledge -> user question
        assert m[0]["role"] == "system"
        assert "Knowledge:" in m[1]["content"]
        assert m[-1]["content"] == "How do I get a refund?"
        # the volatile knowledge must NOT be in the cached system prefix
        assert "Knowledge:" not in m[0]["content"]

    def test_ungrounded_query_has_no_knowledge_message(self, gw):
        m = gw.messages("xyzzy quantum platypus")["messages"]
        # just system prefix + the user turn; nothing injected
        assert len(m) == 2
        assert m[0]["role"] == "system"
        assert m[1]["content"] == "xyzzy quantum platypus"
