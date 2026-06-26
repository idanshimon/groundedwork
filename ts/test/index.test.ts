/**
 * groundedwork TS suite — runs against the SHARED cross-language fixture.
 *
 * fixtures/nimbus.json is the SAME file the Python suite consumes. If both
 * pass, the implementations are behaviorally identical. Uses Node's built-in
 * test runner (node --test), zero external deps.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { GroundedWork, GROUNDING_PROMPT, tokenize } from "../src/index.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
// fixtures/ lives at the repo root: ts/test/ -> ts/ -> repo root -> fixtures/
const FIXTURE = JSON.parse(
  readFileSync(join(__dirname, "..", "..", "fixtures", "nimbus.json"), "utf-8"),
);

function build(opts = {}) {
  const cfg = FIXTURE.config;
  const gw = new GroundedWork({
    minScore: cfg.min_score,
    topK: cfg.top_k,
    k1: cfg.k1,
    b: cfg.b,
    ...opts,
  });
  gw.addMany(FIXTURE.corpus);
  return gw;
}

// -- parity: the shared cases ----------------------------------------------
for (const c of FIXTURE.cases) {
  test(`shared fixture: ${c.query}`, () => {
    const r = build().retrieve(c.query);
    assert.equal(r.grounded, c.grounded, `grounded mismatch for "${c.query}"`);
    if (c.expect_top !== null) {
      assert.ok(r.hits.length > 0, `expected a hit for "${c.query}"`);
      assert.equal(r.hits[0].doc.id, c.expect_top, `top doc mismatch for "${c.query}"`);
    } else {
      assert.equal(r.hits.length, 0, `expected abstain for "${c.query}"`);
    }
  });
}

// -- the differentiators ----------------------------------------------------
test("grounded by default: prompt carries the grounding instruction", () => {
  const p = build().prompt("How do I get a refund?");
  const low = p.system.toLowerCase();
  assert.ok(low.includes("only") && (low.includes("guess") || low.includes("do not have")));
  assert.equal(p.system, GROUNDING_PROMPT);
});

test("absent query injects no knowledge", () => {
  const p = build().prompt("xyzzy quantum platypus protocol");
  assert.equal(p.grounded, false);
  assert.equal(p.knowledge, "");
  assert.deepEqual(p.sources, []);
});

test("ask abstains when ungrounded", () => {
  const a = build().ask("xyzzy quantum platypus");
  assert.equal(a.grounded, false);
  assert.equal(a.source, null);
  assert.ok(a.answer.toLowerCase().includes("don't have") || a.answer.toLowerCase().includes("won't guess"));
});

test("ask answers when grounded", () => {
  const a = build().ask("How do I get a refund?");
  assert.equal(a.grounded, true);
  assert.equal(a.source, "returns");
});

test("relevance floor drops weak matches", () => {
  const low = build({ minScore: 0.0, topK: 5 }).retrieve("coffee");
  const high = build({ minScore: 5.0, topK: 5 }).retrieve("coffee");
  assert.ok(high.hits.length <= low.hits.length);
});

test("add is chainable", () => {
  const gw = new GroundedWork().add({ id: "a", title: "A", body: "alpha" }).add({ id: "b", title: "B", body: "beta" });
  assert.equal(gw.size, 2);
});

test("tokenize drops stopwords", () => {
  assert.ok(!tokenize("the quick brown fox").includes("the"));
  assert.ok(tokenize("the quick brown fox").includes("quick"));
});
