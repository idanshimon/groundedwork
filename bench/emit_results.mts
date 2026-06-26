/**
 * Emit canonical retrieval results for every fixture case — TypeScript side.
 *
 * Mirror of bench/emit_results.py. Same fixture, same canonical shape (sorted
 * keys, scores to 9 dp). bench/parity.py diffs the two outputs byte-for-byte.
 *
 * Run: node --experimental-strip-types bench/emit_results.mts
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import { GroundedWork } from "../ts/src/index.ts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const fx = JSON.parse(readFileSync(join(ROOT, "fixtures", "nimbus.json"), "utf-8"));

const cfg = fx.config;
const gw = new GroundedWork({
  minScore: cfg.min_score,
  topK: cfg.top_k,
  k1: cfg.k1,
  b: cfg.b,
});
gw.addMany(fx.corpus);

const round9 = (n: number) => Math.round(n * 1e9) / 1e9;

const results = fx.cases.map((c: { query: string }) => {
  const r = gw.retrieve(c.query);
  return {
    query: c.query,
    grounded: r.grounded,
    terms: r.terms,
    hits: r.hits.map((h) => ({
      id: h.doc.id,
      score: round9(h.score),
      matched: [...h.matched].sort(),
    })),
  };
});

// Canonical JSON: sorted keys, 2-space indent — must match Python's json.dumps(sort_keys=True, indent=2)
function canonical(value: unknown, indent = 0): string {
  const pad = "  ".repeat(indent);
  const padIn = "  ".repeat(indent + 1);
  if (value === null) return "null";
  if (typeof value === "number") {
    // match Python repr of rounded floats / ints
    return Number.isInteger(value) ? String(value) : String(value);
  }
  if (typeof value === "boolean") return value ? "true" : "false";
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) {
    if (value.length === 0) return "[]";
    const items = value.map((v) => padIn + canonical(v, indent + 1));
    return "[\n" + items.join(",\n") + "\n" + pad + "]";
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  if (keys.length === 0) return "{}";
  const items = keys.map((k) => `${padIn}${JSON.stringify(k)}: ${canonical(obj[k], indent + 1)}`);
  return "{\n" + items.join(",\n") + "\n" + pad + "}";
}

process.stdout.write(canonical({ lang: "typescript", results }) + "\n");
