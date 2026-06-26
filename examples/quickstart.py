"""Quickstart — the 60-second tour of groundedwork.

Run:  python examples/quickstart.py
Needs nothing but the package (pip install -e python/  or  pip install groundedwork).
"""
from groundedwork import GroundedWork

# 1. Build a knowledge base. Each doc is just id + title + body.
kb = GroundedWork().add_many([
    {"id": "returns", "title": "Returns & Refunds",
     "body": "Return any unopened bag within 30 days for a full refund. Opened bags get store credit."},
    {"id": "shipping", "title": "US Shipping",
     "body": "Orders arrive in 3 to 5 business days. Free shipping on orders over $40."},
    {"id": "decaf", "title": "Decaf Options",
     "body": "Every coffee is available decaffeinated using the Swiss Water process."},
])

print("== a question the docs CAN answer ==")
print(kb.ask("How do I get a refund?"))
# {'grounded': True, 'answer': 'Return any unopened bag...', 'source': 'returns'}

print("\n== a question the docs CANNOT answer ==")
print(kb.ask("What's the capital of France?"))
# {'grounded': False, 'answer': "I don't have that...", 'source': None}
# ^ note: grounded=False. In real code you'd skip the LLM call entirely here.

print("\n== what actually gets sent to your model ==")
payload = kb.prompt("How do I get a refund?")
print("grounded:", payload["grounded"], "| sources:", payload["sources"])
print("system :", payload["system"][:70], "...")
print("knowledge:\n", payload["knowledge"][:120], "...")
