/**
 * Tests for the optional hybrid (BM25 + dense embeddings) retrieval path.
 *
 * Uses a DETERMINISTIC in-test embedder — no model, no network — so it proves
 * fusion, opt-in gating, the zero-norm grounding guard, and that the
 * zero-dependency keyword default is untouched. Mirrors python/tests/test_hybrid.py.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { GroundedWork, type Doc } from "../src/index.ts";

const DOCS: Doc[] = [
  { id: "refund", title: "Refund Policy", body: "Money back within 14 days of purchase. Full reimbursement." },
  { id: "shipping", title: "Shipping", body: "Orders arrive in three to five business days via courier." },
  { id: "twofa", title: "Two Factor Authentication", body: "Protect your account login with a second verification step." },
];

// Deterministic bag-of-known-tokens embedder: only corpus-vocabulary tokens
// contribute, so all-unknown queries yield a zero vector (faithful OOV model).
function toyEmbedder(dim = 24) {
  const vocab = new Set<string>();
  for (const d of DOCS) {
    for (const tok of (d.title + " " + d.body).toLowerCase().replace(/\./g, " ").split(/\s+/)) {
      if (tok) vocab.add(tok);
    }
  }
  return {
    encode(texts: string[]): number[][] {
      return texts.map((t) => {
        const v = new Array(dim).fill(0);
        for (const tok of t.toLowerCase().replace(/\./g, " ").split(/\s+/)) {
          if (!vocab.has(tok)) continue;
          let h = 0;
          for (const c of tok) h = (h * 31 + c.charCodeAt(0)) % 1_000_003;
          v[h % dim] += 1;
        }
        return v;
      });
    },
  };
}

// --- opt-in gating: zero-dependency default is pure keyword ---
test("default has no embedder", () => {
  assert.equal(new GroundedWork().embedder, undefined);
});

test("default path is pure keyword retrieval", () => {
  const kb = new GroundedWork({ minScore: 0 }).addMany(DOCS);
  const r = kb.retrieve("refund");
  assert.ok(r.grounded);
  assert.equal(r.hits[0].doc.id, "refund");
});

test("zero-dependency default still works without any embedder", () => {
  const kb = new GroundedWork({ minScore: 0 }).addMany(DOCS);
  assert.equal(kb.retrieve("shipping").hits[0].doc.id, "shipping");
});

// --- hybrid behavior ---
test("hybrid accepts an object embedder with encode()", () => {
  const kb = new GroundedWork({ minScore: 0, embedder: toyEmbedder() }).addMany(DOCS);
  assert.ok(kb.retrieve("refund").grounded);
});

test("hybrid accepts a bare function embedder", () => {
  const fn = (texts: string[]) => toyEmbedder().encode(texts);
  const kb = new GroundedWork({ minScore: 0, embedder: fn }).addMany(DOCS);
  assert.ok(kb.retrieve("refund").grounded);
});

test("hybrid keeps the exact keyword match", () => {
  const kb = new GroundedWork({ minScore: 0, embedder: toyEmbedder() }).addMany(DOCS);
  assert.equal(kb.retrieve("shipping").hits[0].doc.id, "shipping");
});

test("hybrid preserves abstention on garbage (zero-norm guard)", () => {
  const kb = new GroundedWork({ minScore: 0.5, embedder: toyEmbedder() }).addMany(DOCS);
  assert.equal(kb.retrieve("zzzzz qqqqq xkcd").grounded, false);
});

test("async embedder throws a clear error in sync retrieve()", () => {
  const asyncEmbedder = { encode: async (texts: string[]) => texts.map(() => [0]) };
  // deno-lint-ignore no-explicit-any
  const kb = new GroundedWork({ embedder: asyncEmbedder as any }).addMany(DOCS);
  assert.throws(() => kb.retrieve("refund"), /synchronous embedder/);
});

// --- config defaults ---
test("rrfK and denseFloor have sane defaults", () => {
  const kb = new GroundedWork();
  assert.equal(kb.rrfK, 60);
  assert.ok(Math.abs(kb.denseFloor - 0.3) < 1e-9);
});
