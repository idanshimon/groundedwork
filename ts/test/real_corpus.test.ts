/**
 * Real-corpus test battery for groundedwork (TypeScript).
 *
 * Mirror of python/tests/test_real_corpus.py against the same 392-doc fixture
 * (fixtures/corpus_large.json). Proves the TypeScript engine holds the same
 * behavior at scale: correct ranking, floor abstention, the paraphrase gap,
 * and performance. The BM25 oracle (vs rank_bm25) lives only in the Python
 * suite — here we prove TS matches the SAME labeled expectations, which is the
 * cross-language guarantee.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { GroundedWork } from "../src/index.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const FIXTURE = JSON.parse(
  readFileSync(join(__dirname, "..", "..", "fixtures", "corpus_large.json"), "utf-8"),
);
const CFG = FIXTURE.config;
const CORPUS = FIXTURE.corpus;

function build(opts = {}) {
  return new GroundedWork({
    minScore: CFG.min_score,
    topK: CFG.top_k,
    k1: CFG.k1,
    b: CFG.b,
    ...opts,
  }).addMany(CORPUS);
}

// ── corpus sanity ──────────────────────────────────────────────────────────
test("real corpus is large", () => {
  assert.ok(CORPUS.length >= 300);
});

test("all doc ids are unique", () => {
  const ids = CORPUS.map((d: { id: string }) => d.id);
  assert.equal(ids.length, new Set(ids).size);
});

// ── answerable ─────────────────────────────────────────────────────────────
test("every answerable query ranks its target first", () => {
  const gw = build();
  const misses: unknown[] = [];
  for (const c of FIXTURE.answerable) {
    const r = gw.retrieve(c.query);
    const got = r.hits.length ? r.hits[0].doc.id : null;
    if (got !== c.expect_top) misses.push([c.query, c.expect_top, got]);
  }
  assert.deepEqual(misses, [], `${misses.length} answerable queries mis-ranked`);
});

test("answerable recall is total (target in returned set)", () => {
  const gw = build();
  let inSet = 0;
  for (const c of FIXTURE.answerable) {
    const ids = gw.retrieve(c.query).hits.map((h) => h.doc.id);
    if (ids.includes(c.expect_top)) inSet++;
  }
  assert.equal(inSet, FIXTURE.answerable.length);
});

// ── floor at scale ─────────────────────────────────────────────────────────
test("real queries still ground at 392-doc scale", () => {
  const gw = build();
  const grounded = FIXTURE.answerable.filter((c: { query: string }) => gw.retrieve(c.query).grounded).length;
  assert.equal(grounded, FIXTURE.answerable.length);
});

test("absent queries all abstain at scale", () => {
  const gw = build();
  const leaked = FIXTURE.absent.filter((q: string) => gw.retrieve(q).grounded);
  assert.deepEqual(leaked, [], `floor failed to abstain on: ${leaked}`);
});

test("floor never makes abstention worse than floor=0", () => {
  const gw = build();
  const noFloor = build({ minScore: 0.0 });
  const flooredGrounded = FIXTURE.absent.filter((q: string) => gw.retrieve(q).grounded).length;
  const noFloorGrounded = FIXTURE.absent.filter((q: string) => noFloor.retrieve(q).grounded).length;
  assert.ok(flooredGrounded <= noFloorGrounded);
  assert.equal(flooredGrounded, 0);
});

// ── abstention ─────────────────────────────────────────────────────────────
test("every absent query abstains with an honest answer", () => {
  const gw = build();
  for (const q of FIXTURE.absent) {
    const a = gw.ask(q);
    assert.equal(a.grounded, false, `should abstain: ${q}`);
    assert.equal(a.source, null);
    assert.ok(a.answer.toLowerCase().includes("don't have") || a.answer.toLowerCase().includes("won't guess"));
  }
});

test("prompt injects no knowledge on absent queries", () => {
  const gw = build();
  for (const q of FIXTURE.absent) {
    const p = gw.prompt(q);
    assert.equal(p.grounded, false);
    assert.equal(p.knowledge, "");
    assert.deepEqual(p.sources, []);
  }
});

// ── paraphrase gap (regression target for v0.2) ───────────────────────────
test("paraphrase recall is measured, and the gap is observable", () => {
  const gw = build();
  let hitsTarget = 0;
  for (const c of FIXTURE.paraphrase) {
    const ids = gw.retrieve(c.query).hits.map((h) => h.doc.id);
    if (ids.includes(c.expect_top)) hitsTarget++;
  }
  const total = FIXTURE.paraphrase.length;
  // keyword-only must NOT solve every paraphrase, or we wouldn't need v0.2 embeddings
  assert.ok(hitsTarget < total, "keyword-only unexpectedly solved every paraphrase — re-tune fixture");
});

// ── scale / performance ────────────────────────────────────────────────────
test("ingest of the full corpus completes quickly", () => {
  const t = performance.now();
  build();
  assert.ok(performance.now() - t < 10000);
});

test("retrieval is fast at scale", () => {
  const gw = build();
  const queries = FIXTURE.answerable.slice(0, 100).map((c: { query: string }) => c.query);
  const t = performance.now();
  for (const q of queries) gw.retrieve(q);
  const perMs = (performance.now() - t) / queries.length;
  assert.ok(perMs < 50, `retrieval averaged ${perMs.toFixed(2)}ms/query`);
});

test("no crash on pathological input", () => {
  const gw = build();
  for (const q of ["", "   ", "?!@#$%", "a", "the and of", "x".repeat(5000)]) {
    const r = gw.retrieve(q);
    assert.equal(typeof r.grounded, "boolean");
  }
});
