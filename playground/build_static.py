#!/usr/bin/env python3
"""Bundle the compiled real TS engine and replace only the explicit adapter slot."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
UI = (ROOT / "playground/index.html").read_text(encoding="utf-8")
START = "<!-- playground:adapter:start -->"
END = "<!-- playground:adapter:end -->"


def script_json(value):
    """JSON embedded in HTML must not terminate its script element."""
    return json.dumps(value, ensure_ascii=True, separators=(",", ":")).replace(
        "<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def replace_adapter(html, adapter):
    if html.count(START) != 1 or html.count(END) != 1:
        raise ValueError("Expected exactly one playground adapter slot.")
    before, rest = html.split(START)
    if END not in rest:
        raise ValueError("Playground adapter slot markers are out of order.")
    _, after = rest.split(END)
    return before + START + "\n" + adapter + "\n" + END + after


def build():
    engine_path = ROOT / "ts/dist/index.js"
    if not engine_path.is_file():
        raise FileNotFoundError("Compile the real engine first: npm --prefix ts run build")
    engine = engine_path.read_text(encoding="utf-8").strip()
    if "</script" in engine.lower() or "<!--" in engine:
        raise ValueError("Compiled engine contains an unsafe HTML script delimiter.")
    fixture = json.loads((ROOT / "fixtures/nimbus.json").read_text(encoding="utf-8"))
    adapter = """<script type="module">
%s

try {
  const CORPUS = %s;
  const CFG = %s;
  const engine = new GroundedWork({
    minScore: CFG.min_score, topK: CFG.top_k, k1: CFG.k1, b: CFG.b,
    prefs: "The user is on the Pro plan.",
  }).addMany(CORPUS);
  function analyze(query) {
    const retrieval = engine.retrieve(query);
    const full = engine.retrieve(query, CORPUS.length);
    const messages = engine.messages(query);
    const score = hit => ({id: hit.doc.id, title: hit.doc.title,
      score: Math.round(hit.score * 1e4) / 1e4});
    return {
      query, terms: retrieval.terms, floor: CFG.min_score,
      scored: full.hits.map(score), grounded: retrieval.grounded,
      hits: retrieval.hits.map(hit => ({...score(hit), body: hit.doc.body})),
      messages: messages.messages, stable_prefix: messages.stablePrefix,
      answer: engine.ask(query), corpus_size: CORPUS.length,
    };
  }
  window.__GW = {
    analyze, version: VERSION, config: CFG, corpus_size: CORPUS.length,
    corpus: CORPUS.map(doc => ({id: doc.id, title: doc.title})),
  };
  window.playground.connect({
    info: () => ({...window.__GW, runtime: 'TypeScript / in browser'}),
    analyze,
  });
} catch (error) {
  window.playground.fail(error);
}
</script>""" % (engine, script_json(fixture["corpus"]), script_json(fixture["config"]))
    html = replace_adapter(UI, adapter)
    if "/api/" in html or "fetch(" in html:
        raise ValueError("Static bundle must not contain a backend request.")
    out_dir = ROOT / "playground/dist"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / "index.html"
    with out.open("w", encoding="utf-8", newline="\n") as output:
        output.write(html)
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Wrote playground/dist/index.html ({len(html.encode('utf-8'))} bytes); "
          f"real TypeScript engine, {len(fixture['corpus'])} documents, offline.")
    return out


if __name__ == "__main__":
    build()
