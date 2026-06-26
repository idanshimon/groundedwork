#!/usr/bin/env python3
"""Emit canonical retrieval results for every fixture case — Python side.

Part of the cross-language parity harness. Both this and bench/emit_results.mjs
load the SAME fixture, run retrieve() over every case, and print a canonical
JSON document (sorted keys, scores rounded to 9 dp). bench/parity.py diffs the
two outputs: if they are byte-identical, the Python and TypeScript engines are
behaviorally indistinguishable.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from groundedwork import GroundedWork  # noqa: E402


def emit() -> dict:
    fx = json.loads((ROOT / "fixtures" / "nimbus.json").read_text())
    cfg = fx["config"]
    gw = GroundedWork(
        min_score=cfg["min_score"], top_k=cfg["top_k"], k1=cfg["k1"], b=cfg["b"]
    )
    gw.add_many(fx["corpus"])

    out = []
    for case in fx["cases"]:
        r = gw.retrieve(case["query"])
        out.append(
            {
                "query": case["query"],
                "grounded": r.grounded,
                "terms": r.terms,
                "hits": [
                    {
                        "id": h.doc.id,
                        "score": round(h.score, 9),
                        "matched": sorted(h.matched),
                    }
                    for h in r.hits
                ],
            }
        )
    return {"lang": "python", "results": out}


if __name__ == "__main__":
    print(json.dumps(emit(), indent=2, sort_keys=True, ensure_ascii=False))
