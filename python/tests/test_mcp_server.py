"""MCP server round-trip: spawn over stdio, list tools, ground, abstain.

Skipped automatically when the optional 'mcp' package is not installed, so the
zero-dependency core suite is unaffected.
"""
import asyncio
import json
import os
import sys

import pytest

pytest.importorskip("mcp")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

CORPUS = os.path.join(os.path.dirname(__file__), "mcp_corpus.json")


async def _roundtrip():
    env = dict(os.environ)
    env["GROUNDEDWORK_CORPUS"] = CORPUS
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "groundedwork.mcp_server"], env=env
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = {t.name for t in (await s.list_tools()).tools}
            info = json.loads((await s.call_tool("corpus_info", {})).content[0].text)
            grounded = json.loads(
                (await s.call_tool("retrieve", {"query": "refund policy"})).content[0].text
            )
            abstain = json.loads(
                (await s.call_tool("retrieve", {"query": "capital of France"})).content[0].text
            )
            return tools, info, grounded, abstain


def test_mcp_server_roundtrip():
    tools, info, grounded, abstain = asyncio.run(_roundtrip())
    assert {"retrieve", "messages", "corpus_info"} <= tools
    assert info["documents"] == 3 and info["ready"]
    assert grounded["grounded"] and grounded["hits"]
    assert not abstain["grounded"] and abstain["hits"] == []  # abstention preserved
