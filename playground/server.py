#!/usr/bin/env python3
"""groundedwork playground — a real, in-browser walkthrough.

This is NOT a simulation. It imports the actual `groundedwork` package and runs
your query through the real engine: real BM25 scores, the real relevance floor,
the real grounding/abstention decision, and the real assembled prompt. The UI
shows every stage so you can SEE what the library did and why.

Zero dependencies — stdlib http.server only, matching groundedwork itself.

Run:  python playground/server.py
Then open http://localhost:8000

The "answer" shown is the canonical document text (groundedwork is BYOM — it
does not call an LLM). What's real and live is everything BEFORE the answer:
retrieval, scoring, the floor, grounding, and the exact prompt your model would
receive.
"""
import json
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Import the REAL package from python/ (editable or installed).
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import groundedwork as gw_pkg  # noqa: E402

PORT = 8000

# Load the real nimbus corpus the rest of the project tests against.
FIXTURE = json.loads((ROOT / "fixtures" / "nimbus.json").read_text())
CFG = FIXTURE["config"]
CORPUS = FIXTURE["corpus"]

# One real engine instance, configured exactly like the tests.
ENGINE = gw_pkg.GroundedWork(
    min_score=CFG["min_score"], top_k=CFG["top_k"], k1=CFG["k1"], b=CFG["b"],
    prefs="The user is on the Pro plan.",
).add_many(CORPUS)

# Curated walkthrough scenarios — each teaches one behavior.
SCENARIOS = [
    {"label": "✅ Grounded answer", "query": "How do I get a refund?",
     "teaches": "A clear match. Watch the score clear the floor and the answer come from one document."},
    {"label": "🚫 Honest abstention", "query": "What is the capital of France?",
     "teaches": "Not in the knowledge base. The floor blocks everything and the engine refuses to guess — grounded=false."},
    {"label": "🌀 Paraphrase miss", "query": "when does it show up at my door?",
     "teaches": "BM25 is keyword-based. 'show up at my door' shares no words with the shipping doc, so it misses or mis-ranks. v0.2 adds opt-in hybrid (BM25 + embeddings) that closes this gap on real corpora — measured 1/4 to 2/4 paraphrase recall in bench/paraphrase_eval.py. (This 24-doc demo is too small for a tiny embedder to help here; the win shows on the larger corpus.)"},
    {"label": "📦 Multi-term query", "query": "how do I pause my subscription billing?",
     "teaches": "Several terms combine. See how each scored document contributes."},
    {"label": "☕ Product question", "query": "do you have decaf coffee?",
     "teaches": "A specific product lookup grounded in the catalog doc."},
]


def analyze(query: str) -> dict:
    """Run the query through the REAL engine and capture every stage."""
    retrieval = ENGINE.retrieve(query)
    # Score EVERY doc (top_k=all) so the UI can show what cleared/missed the floor.
    full = ENGINE.retrieve(query, top_k=len(CORPUS))
    scored = [{"id": h.doc.id, "title": h.doc.title, "score": round(h.score, 4)} for h in full.hits]
    prompt = ENGINE.prompt(query)
    messages = ENGINE.messages(query)
    answer = ENGINE.ask(query)
    return {
        "query": query,
        "terms": retrieval.terms,                      # real tokenization
        "floor": CFG["min_score"],
        "scored": scored,                               # everything above the floor, real scores
        "grounded": retrieval.grounded,                 # real decision
        "hits": [{"id": h.doc.id, "title": h.doc.title, "score": round(h.score, 4),
                  "body": h.doc.body} for h in retrieval.hits],
        "prompt": prompt,                               # real assembled {system, knowledge, user, ...}
        "messages": messages["messages"],               # real cache-ordered message array
        "stable_prefix": ENGINE.stable_prefix(),        # the cacheable prefix
        "answer": answer,                               # canonical doc text (BYOM: no LLM call)
        "corpus_size": len(CORPUS),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):  # quiet
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, (pathlib.Path(__file__).parent / "index.html").read_text(), "text/html; charset=utf-8")
        elif self.path == "/api/scenarios":
            self._send(200, json.dumps({"scenarios": SCENARIOS,
                                        "corpus": [{"id": d["id"], "title": d["title"]} for d in CORPUS],
                                        "config": CFG}))
        elif self.path == "/api/version":
            self._send(200, json.dumps({"version": getattr(gw_pkg, "__version__", "0.1.0"),
                                        "corpus_size": len(CORPUS)}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/api/ask":
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            query = (payload.get("query") or "").strip()
            if not query:
                self._send(400, json.dumps({"error": "empty query"}))
                return
            self._send(200, json.dumps(analyze(query)))
        except Exception as e:  # never 500 silently
            self._send(500, json.dumps({"error": str(e)}))


def main():
    print(f"groundedwork playground — REAL engine, {len(CORPUS)} docs, floor={CFG['min_score']}")
    print(f"open  http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
