"""Bring-your-own-model — wire groundedwork to a REAL LLM.

groundedwork builds the grounded, cache-aware payload. YOU own the model call.
This example works with ANY OpenAI-compatible endpoint:

  - Local:  Ollama (http://localhost:11434/v1), llama.cpp, vLLM, LM Studio
  - Cloud:  OpenAI, Azure OpenAI, OpenRouter, Together, Groq, ...

Set env vars to point at your endpoint, then:  python examples/byo_model.py
If OPENAI_BASE_URL is unset, it prints the payload instead of calling a model,
so the example always runs.

  export OPENAI_BASE_URL=http://localhost:11434/v1   # Ollama
  export OPENAI_API_KEY=ollama                        # any non-empty string for local
  export OPENAI_MODEL=llama3.2
"""
import os
from groundedwork import GroundedWork

kb = GroundedWork(prefs="The user is on the Pro plan. Keep answers terse.").add_many([
    {"id": "returns", "title": "Returns & Refunds",
     "body": "Return any unopened bag within 30 days for a full refund."},
    {"id": "shipping", "title": "US Shipping",
     "body": "Orders arrive in 3 to 5 business days. Free over $40."},
])


def answer(question: str) -> str:
    m = kb.messages(question)

    # 1. Abstain WITHOUT calling the model when nothing matches — saves the spend.
    if not m["grounded"]:
        return "I don't have that in our docs."

    base_url = os.getenv("OPENAI_BASE_URL")
    if not base_url:
        # No endpoint configured — show what WOULD be sent (so this file always runs).
        return f"[would call your LLM with {len(m['messages'])} messages; sources={m['sources']}]"

    # 2. You own the model call. groundedwork stays out of it (no provider dep).
    from openai import OpenAI  # pip install openai — YOUR dependency, not groundedwork's
    client = OpenAI(base_url=base_url, api_key=os.getenv("OPENAI_API_KEY", "x"))
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=m["messages"],   # already cache-optimally ordered
    )
    return resp.choices[0].message.content or "(empty response)"


if __name__ == "__main__":
    for q in ["How do I get a refund?", "When will it arrive?", "Do you sell laptops?"]:
        print(f"Q: {q}\nA: {answer(q)}\n")
