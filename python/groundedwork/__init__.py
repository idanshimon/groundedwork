"""groundedwork — retrieval that knows when it doesn't know.

A tiny, dependency-free retrieval layer for giving an LLM a knowledge base
bigger than its context window. Keyword (BM25) retrieval into a relevance-floored
"working set", with grounding and abstention built in as defaults — not as
prompt-engineering you have to remember.

Lineage: groundedwork is a from-scratch reimplementation inspired by ContextForge
(github.com/Betanu701/ContextForge) by Derek Thomas. Every design decision here
comes from empirically testing that SDK and fixing what we measured: permissive
default prompts that let small models hallucinate, and top-k retrieval with no
relevance floor that injects distractors on a miss. See README for the evidence.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

__version__ = "0.1.0"

# Words too common to carry retrieval signal. Mirrors the validated browser demo.
_STOP = set(
    "a an the is are was were be been do does did of to in on at for and or but with "
    "from by as this that these those your you we our it its i my me can how what when "
    "where which will would should could about get got".split()
)


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, drop stopwords and 1-char tokens."""
    return [
        w
        for w in re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
        if len(w) > 1 and w not in _STOP
    ]


@dataclass
class Doc:
    id: str
    title: str
    body: str
    answer: str = ""          # optional canonical answer text for grounded replies
    meta: dict = field(default_factory=dict)


@dataclass
class Hit:
    doc: Doc
    score: float
    matched: list[str]


@dataclass
class Retrieval:
    """The result of a retrieve() call.

    grounded == True  -> at least one doc cleared the relevance floor.
    grounded == False -> nothing matched well enough; the honest answer is
                         "I don't have that" and `hits` is empty. This is a
                         first-class signal, not a hallucinated answer.
    """
    query: str
    hits: list[Hit]
    terms: list[str]

    @property
    def grounded(self) -> bool:
        return len(self.hits) > 0


# The grounding instruction that shipped 0/72 hallucinations in our testing,
# vs 5/72 for a permissive prompt. This is the DEFAULT, not opt-in.
GROUNDING_PROMPT = (
    "You are a helpful assistant. Answer using ONLY the information in the "
    "knowledge provided below. If the answer is not contained in it, say you "
    "do not have that information — do not guess or use outside knowledge."
)


class GroundedWork:
    """An in-memory, relevance-floored BM25 knowledge base.

    Args:
        min_score: relevance floor. A query whose best match scores below this
            returns an EMPTY, ungrounded result instead of near-irrelevant
            distractors. Default 2.0 (measured to drop distractors while keeping
            real answers). Set 0.0 for classic always-return-top-k behavior.
        top_k:     max docs in a working set.
        k1, b:     BM25 tuning. Defaults match Robertson/Zaragoza standard.
        system_prompt: the grounding instruction. Defaults to GROUNDING_PROMPT.
    """

    def __init__(
        self,
        min_score: float = 2.0,
        top_k: int = 3,
        k1: float = 1.5,
        b: float = 0.75,
        system_prompt: str = GROUNDING_PROMPT,
    ) -> None:
        self.min_score = min_score
        self.top_k = top_k
        self.k1 = k1
        self.b = b
        self.system_prompt = system_prompt
        self._docs: list[Doc] = []
        self._tf: list[dict[str, int]] = []
        self._len: list[int] = []
        self._df: dict[str, int] = {}
        self._avgdl: float = 0.0

    # -- ingestion --------------------------------------------------------
    def add(self, id: str, title: str, body: str, answer: str = "", **meta) -> "GroundedWork":
        """Add one document. Title is weighted 2x (matches the reference demo)."""
        doc = Doc(id=id, title=title, body=body, answer=answer, meta=meta)
        toks = tokenize(title + " " + title + " " + body)
        tf: dict[str, int] = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        self._docs.append(doc)
        self._tf.append(tf)
        self._len.append(len(toks))
        for term in tf:
            self._df[term] = self._df.get(term, 0) + 1
        self._avgdl = sum(self._len) / len(self._len)
        return self  # chainable

    def add_many(self, docs: list[dict]) -> "GroundedWork":
        for d in docs:
            self.add(**d)
        return self

    def __len__(self) -> int:
        return len(self._docs)

    # -- retrieval --------------------------------------------------------
    def retrieve(self, query: str, top_k: Optional[int] = None) -> Retrieval:
        """Return the relevance-floored working set for a query."""
        k = top_k if top_k is not None else self.top_k
        terms = tokenize(query)
        n = len(self._docs)
        if not terms or n == 0:
            return Retrieval(query=query, hits=[], terms=terms)

        scores: list[tuple[int, float, list[str]]] = []
        for i, tf in enumerate(self._tf):
            s = 0.0
            matched: list[str] = []
            dl = self._len[i]
            for t in terms:
                f = tf.get(t)
                if not f:
                    continue
                df = self._df.get(t, 0)
                idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
                s += idf * (f * (self.k1 + 1)) / (
                    f + self.k1 * (1 - self.b + self.b * dl / (self._avgdl or 1))
                )
                matched.append(t)
            if s > 0:
                scores.append((i, s, matched))

        scores.sort(key=lambda x: -x[1])
        hits = [
            Hit(doc=self._docs[i], score=s, matched=m)
            for i, s, m in scores[:k]
            if s >= self.min_score  # the floor: below it, inject nothing
        ]
        return Retrieval(query=query, hits=hits, terms=terms)

    # -- prompt assembly --------------------------------------------------
    def prompt(self, query: str) -> dict:
        """Build the message payload an LLM would receive for this query.

        Returns {"system", "knowledge", "user", "grounded", "sources"}.
        On an ungrounded query the knowledge block is empty and grounded=False,
        so a caller can short-circuit to an honest "I don't have that".
        """
        r = self.retrieve(query)
        knowledge = "\n\n".join(f"### {h.doc.title}\n{h.doc.body}" for h in r.hits)
        return {
            "system": self.system_prompt,
            "knowledge": knowledge,
            "user": query,
            "grounded": r.grounded,
            "sources": [h.doc.id for h in r.hits],
        }

    def ask(self, query: str) -> dict:
        """Demo-grade answerer with NO LLM call: returns the canonical answer of
        the top grounded hit, or an honest abstention. Real apps pass
        prompt(query) to their own model; this exists so the package is runnable
        and testable with zero external dependencies or API keys.
        """
        r = self.retrieve(query)
        if not r.grounded:
            return {
                "grounded": False,
                "answer": "I don't have that in my knowledge base, so I won't guess.",
                "source": None,
            }
        top = r.hits[0].doc
        return {
            "grounded": True,
            "answer": top.answer or top.body,
            "source": top.id,
        }
