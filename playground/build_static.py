#!/usr/bin/env python3
"""Build the static, browser-only playground for GitHub Pages.

GitHub Pages can't run the Python server, so this bundles the REAL TypeScript
engine (ts/dist/index.js — the same implementation that passes 33 tests and is
proven byte-identical to the Python reference by the parity harness) and runs it
IN THE BROWSER. No backend, no API calls, numbers still real.

Output: playground/dist/index.html  — a single self-contained file.

The page reuses the redesigned UI verbatim; the only change is that the
`ask()` data source is swapped from `fetch('/api/ask')` to the in-browser
engine producing the identical data shape the server's analyze() returned.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
UI = (ROOT / "playground" / "index.html").read_text()
ENGINE_JS = (ROOT / "ts" / "dist" / "index.js").read_text()
FIXTURE = json.loads((ROOT / "fixtures" / "nimbus.json").read_text())

CFG = FIXTURE["config"]
CORPUS = FIXTURE["corpus"]
SCENARIOS = [
    {"label": "✅ Grounded answer", "query": "How do I get a refund?",
     "teaches": "A clear match. Watch the score clear the floor and the answer come from one document."},
    {"label": "🚫 Honest abstention", "query": "What is the capital of France?",
     "teaches": "Not in the knowledge base. The floor blocks everything and the engine refuses to guess — grounded=false."},
    {"label": "🌀 Paraphrase miss", "query": "when does it show up at my door?",
     "teaches": "BM25 is keyword-based. 'show up at my door' shares no words with the shipping doc, so it misses — the limitation v0.2 embeddings will fix."},
    {"label": "📦 Multi-term query", "query": "how do I pause my subscription billing?",
     "teaches": "Several terms combine. See how each scored document contributes."},
    {"label": "☕ Product question", "query": "do you have decaf coffee?",
     "teaches": "A specific product lookup grounded in the catalog doc."},
]

# The in-browser replacement for the server. Imports the REAL engine, builds the
# same engine instance the server builds, and exposes window.__analyze(query)
# returning the EXACT dict shape the server's analyze() returned.
BROWSER_ENGINE = """
<script type="module">
// ── the REAL groundedwork TypeScript engine, compiled to browser JS ──
%(engine)s

// ── the same corpus + config the Python server and the test suite use ──
const CORPUS = %(corpus)s;
const CFG = %(cfg)s;
const SCENARIOS = %(scenarios)s;

// one real engine instance, configured exactly like the server/tests
const ENGINE = new GroundedWork({
  minScore: CFG.min_score, topK: CFG.top_k, k1: CFG.k1, b: CFG.b,
  prefs: "The user is on the Pro plan.",
}).addMany(CORPUS);

// reproduce the server's analyze() → identical data shape the UI expects
function analyze(query){
  const retrieval = ENGINE.retrieve(query);
  const full = ENGINE.retrieve(query, CORPUS.length);
  const scored = full.hits.map(h => ({id:h.doc.id, title:h.doc.title, score:Math.round(h.score*1e4)/1e4}));
  const messages = ENGINE.messages(query);
  const answer = ENGINE.ask(query);
  return {
    query,
    terms: retrieval.terms,
    floor: CFG.min_score,
    scored,
    grounded: retrieval.grounded,
    hits: retrieval.hits.map(h => ({id:h.doc.id, title:h.doc.title, score:Math.round(h.score*1e4)/1e4, body:h.doc.body})),
    messages: messages.messages,
    stable_prefix: messages.stablePrefix,
    answer,
    corpus_size: CORPUS.length,
  };
}

// expose to the UI script (which runs as a classic script below)
window.__GW = { analyze, scenarios: SCENARIOS,
  corpus: CORPUS.map(d => ({id:d.id, title:d.title})),
  config: CFG, version: VERSION, corpus_size: CORPUS.length };
window.dispatchEvent(new Event('gw-ready'));
</script>
""" % {
    "engine": ENGINE_JS,
    "corpus": json.dumps(CORPUS, ensure_ascii=False),
    "cfg": json.dumps(CFG),
    "scenarios": json.dumps(SCENARIOS, ensure_ascii=False),
}


def build():
    html = UI

    # Swap the three fetch-based data sources for the in-browser engine.
    # These are literal-string replacements against the redesigned UI's exact
    # syntax (more robust than regex). window.__GW is provided by BROWSER_ENGINE.

    # 1. version fetch -> read from __GW
    html = html.replace(
        "fetch('/api/version').then(r => r.json()).then(v => {",
        "Promise.resolve(window.__GW).then(v => {",
    )
    # 2. scenarios fetch -> read from __GW
    html = html.replace(
        "fetch('/api/scenarios').then(r => r.json()).then(d => {",
        "Promise.resolve(window.__GW).then(d => {",
    )
    # 3. the ask() POST -> in-browser analyze (synchronous, wrapped in resolved promise
    #    so the surrounding `await` still works unchanged)
    html = html.replace(
        """    const r = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q })
    });
    
    const data = await r.json();""",
        "    const data = window.__GW.analyze(q);",
    )

    # The UI script runs immediately on parse, but __GW is set by the module
    # script. Modules are deferred, so they execute AFTER classic scripts — we
    # must make the UI wait. Gate the two immediate calls + guarantee order by
    # moving engine init to run first: inject BROWSER_ENGINE in <head> as a
    # classic (non-module) bundle is not possible (it uses export). Instead we
    # wrap the UI's immediate __GW reads in a 'gw-ready' listener.
    html = html.replace(
        "Promise.resolve(window.__GW).then(v => {",
        "window.addEventListener('gw-ready', () => Promise.resolve(window.__GW).then(v => {",
    ).replace(
        "  document.getElementById('meta').textContent = `disconnected`;\n});",
        "  document.getElementById('meta').textContent = `disconnected`;\n}));",
    )
    html = html.replace(
        "window.addEventListener('gw-ready', () => Promise.resolve(window.__GW).then(d => {",
        "window.addEventListener('gw-ready', () => Promise.resolve(window.__GW).then(d => {",
    )
    # scenarios block also needs the gw-ready gate
    html = html.replace(
        "Promise.resolve(window.__GW).then(d => {",
        "window.addEventListener('gw-ready', () => Promise.resolve(window.__GW).then(d => {",
    ).replace(
        "}).catch(e => console.error(e));",
        "}));",
    )

    # Inject the engine module at end of body (modules are deferred → run after
    # the classic UI script has defined ask(), esc(), etc., then fire gw-ready).
    html = html.replace("</body>", BROWSER_ENGINE + "\n</body>")

    # Provenance banner.
    banner = ('<div style="max-width:1100px;margin:0 auto;padding:8px 20px 0;'
              'color:#8b949e;font-size:12px;text-align:center">Runs the actual groundedwork '
              '<b style="color:#e6edf3">TypeScript engine</b> in your browser — '
              'the same implementation the test suite verifies byte-identical to '
              'the Python reference. Every score is computed live.</div>')
    html = html.replace('<div class="wrap">', banner + '\n<div class="wrap">', 1)

    out_dir = ROOT / "playground" / "dist"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "index.html"
    out.write_text(html)
    (out_dir / ".nojekyll").write_text("")
    print(f"wrote {out.relative_to(ROOT)}  ({len(html)//1024} KB)")
    print(f"  engine: real ts/dist/index.js ({len(ENGINE_JS)//1024} KB)")
    print(f"  corpus: {len(CORPUS)} docs inlined")
    # sanity: no fetch calls should remain
    remaining = html.count("fetch('/api")
    print(f"  fetch('/api calls remaining: {remaining}  {'✓' if remaining == 0 else '✗ STILL PRESENT'}")


if __name__ == "__main__":
    build()
