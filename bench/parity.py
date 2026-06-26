#!/usr/bin/env python3
"""Cross-language parity harness for groundedwork.

Runs the Python and TypeScript retrieval emitters over the shared fixture and
proves their output is byte-identical (scores to 9 dp, rankings, matched terms).
Writes/updates the golden snapshot at bench/golden.json so future changes that
break parity are caught by a diff.

Usage:
    python bench/parity.py            # check parity, print a report, exit 0/1
    python bench/parity.py --update   # regenerate the golden snapshot

This is the spine of the test bench: add a fixture case, add a third-language
port — all of them must reproduce golden.json or the harness fails loudly.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "bench" / "golden.json"


def run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"emitter failed: {' '.join(cmd)}\n{p.stderr}")
    return json.loads(p.stdout)


def results_only(doc: dict) -> list:
    return doc["results"]


def main() -> int:
    update = "--update" in sys.argv

    py = run([sys.executable, "bench/emit_results.py"])
    ts = run(["node", "--experimental-strip-types", "bench/emit_results.mts"])

    py_r, ts_r = results_only(py), results_only(ts)

    # canonical serialization of each language's results, language tag stripped
    py_s = json.dumps(py_r, sort_keys=True, indent=2, ensure_ascii=False)
    ts_s = json.dumps(ts_r, sort_keys=True, indent=2, ensure_ascii=False)

    identical = py_s == ts_s
    n_cases = len(py_r)
    n_hits = sum(len(c["hits"]) for c in py_r)

    print("=" * 60)
    print("  groundedwork — cross-language parity report")
    print("=" * 60)
    print(f"  fixture cases : {n_cases}")
    print(f"  total hits    : {n_hits}")
    print(f"  python engine : {'ok' if py_r else 'EMPTY'}")
    print(f"  typescript    : {'ok' if ts_r else 'EMPTY'}")
    print(f"  numeric parity: scores compared to 9 decimal places")
    print("-" * 60)

    if identical:
        print("  RESULT: ✅ IDENTICAL — both engines agree on every case")
    else:
        print("  RESULT: ❌ DIVERGENCE")
        # show first differing case
        for pc, tc in zip(py_r, ts_r):
            if pc != tc:
                print(f"  first divergent case: {pc['query']!r}")
                print(f"    python: {json.dumps(pc['hits'])}")
                print(f"    ts    : {json.dumps(tc['hits'])}")
                break
    print("=" * 60)

    if update:
        GOLDEN.write_text(py_s + "\n")
        print(f"  golden snapshot written: {GOLDEN.relative_to(ROOT)}")
        return 0

    # verify against golden if it exists
    if GOLDEN.exists():
        golden = GOLDEN.read_text().rstrip("\n")
        if py_s != golden:
            print("  ⚠ python output differs from golden.json — run --update if intended")
            return 1

    return 0 if identical else 1


if __name__ == "__main__":
    sys.exit(main())
