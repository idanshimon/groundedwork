"""groundedwork MCP server — expose the retrieval engine as agent tools.

This is a thin wrapper. ALL retrieval logic lives in the groundedwork package;
the server only loads a corpus and forwards calls. Abstention is preserved: when
nothing clears the relevance floor, tools report grounded=false and never invent
content.

Corpus source (v1): point GROUNDEDWORK_CORPUS at either
  - a JSON file: [{"id","title","body","answer"?}, ...]  (or {"corpus":[...]})
  - a directory: every *.md / *.txt becomes a doc (filename=title, contents=body)

Run:  GROUNDEDWORK_CORPUS=/path uvx groundedwork-mcp     (stdio transport)
"""
from __future__ import annotations

import glob
import json
import os
import sys

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "groundedwork-mcp needs the 'mcp' package. Install: pip install 'groundedwork[mcp]'\n"
    )
    raise

from groundedwork import GroundedWork

mcp = FastMCP("groundedwork")
_kb = GroundedWork()


def _load_corpus(source: str) -> int:
    """Index a JSON file or a directory of .md/.txt. Returns doc count."""
    docs: list[dict] = []
    if os.path.isdir(source):
        for path in sorted(glob.glob(os.path.join(source, "**/*"), recursive=True)):
            if not path.lower().endswith((".md", ".txt")):
                continue
            with open(path, encoding="utf-8") as f:
                body = f.read()
            title = os.path.splitext(os.path.basename(path))[0]
            docs.append({"id": path, "title": title, "body": body})
    elif os.path.isfile(source):
        with open(source, encoding="utf-8") as f:
            data = json.load(f)
        docs = data.get("corpus", data) if isinstance(data, dict) else data
    else:
        raise FileNotFoundError(f"corpus source not found: {source}")
    _kb.add_many(docs)
    return len(_kb)


@mcp.tool()
def retrieve(query: str, top_k: int = 0) -> dict:
    """Retrieve the grounded working set for a query. When nothing clears the
    relevance floor, grounded is false and hits is empty (abstain, do not guess)."""
    r = _kb.retrieve(query, top_k or None)
    return {
        "grounded": r.grounded,
        "query": r.query,
        "hits": [
            {"id": h.doc.id, "title": h.doc.title, "body": h.doc.body, "score": round(h.score, 4)}
            for h in r.hits
        ],
    }


@mcp.tool()
def messages(query: str) -> dict:
    """Build the cache-aware chat payload for a query. grounded=false means the
    corpus has no answer; assemble nothing and tell the user you don't have it."""
    return _kb.messages(query)


@mcp.tool()
def corpus_info() -> dict:
    """Report indexed document count and whether a corpus is loaded."""
    return {"documents": len(_kb), "ready": len(_kb) > 0}


def main() -> None:
    source = os.environ.get("GROUNDEDWORK_CORPUS")
    if source:
        n = _load_corpus(source)
        sys.stderr.write(f"[groundedwork-mcp] indexed {n} docs from {source}; ready.\n")
    else:
        sys.stderr.write("[groundedwork-mcp] no GROUNDEDWORK_CORPUS set; corpus empty.\n")
    mcp.run()


if __name__ == "__main__":
    main()
