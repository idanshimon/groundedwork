#!/usr/bin/env python3
"""Generate a larger, realistic corpus fixture for groundedwork's real-test battery.

Produces fixtures/corpus_large.json: a few hundred docs modeling a software
company's knowledge base (API reference, how-to guides, troubleshooting,
policies, release notes), plus labeled query sets:
  - answerable:  query -> the doc id that should rank #1
  - absent:      queries whose answer is NOT in the corpus (must abstain)
  - paraphrase:  query phrased with different words than its target doc
                 (characterizes the BM25 paraphrase gap; regression target for v0.2)

Deterministic (fixed seed) so the fixture is stable and reviewable.
"""
import json
import pathlib
import random

random.seed(42)
ROOT = pathlib.Path(__file__).resolve().parents[1]

# Building blocks for believable, lexically-distinct docs.
PRODUCTS = ["Nimbus", "Atlas", "Beacon", "Cobalt", "Delta", "Echo"]
API_RESOURCES = ["users", "orders", "invoices", "webhooks", "sessions", "teams",
                 "projects", "files", "payments", "subscriptions", "reports", "tokens"]
HTTP_VERBS = ["create", "retrieve", "update", "delete", "list"]
TOPICS = ["authentication", "rate limiting", "pagination", "error handling",
          "webhooks signatures", "idempotency keys", "data retention",
          "two-factor login", "single sign-on", "audit logging", "data export",
          "role permissions", "billing cycles", "refund processing",
          "password reset", "email verification", "API versioning",
          "timezone handling", "currency conversion", "file uploads"]

docs = []
answerable = []   # {query, expect_top}
paraphrase = []   # {query, expect_top, note}

# 1. API reference docs — each is lexically unique (product + resource + verb).
for product in PRODUCTS:
    for res in API_RESOURCES:
        for verb in HTTP_VERBS:
            did = f"api-{product.lower()}-{verb}-{res}"
            title = f"{product} {verb.capitalize()} {res} endpoint"
            body = (f"The {product} {verb} {res} endpoint lets you {verb} {res} via the "
                    f"{product} REST API. Send a request to the {product} {res} resource path. "
                    f"The response returns the {res} object with its identifier, timestamps, "
                    f"and status fields. Authentication via bearer token is required for the "
                    f"{product} {res} endpoint.")
            docs.append({"id": did, "title": title, "body": body})
            answerable.append({"query": f"how do I {verb} {res} in {product}", "expect_top": did})

# 2. How-to / topic guides — lexically distinct per topic.
for i, topic in enumerate(TOPICS):
    did = f"guide-{topic.replace(' ', '-')}"
    title = f"Guide: {topic}"
    body = (f"This guide explains {topic} in detail. Configure {topic} from your "
            f"dashboard settings. Best practices for {topic} include monitoring, "
            f"testing in staging, and reviewing logs. Common pitfalls with {topic} "
            f"are misconfiguration and missing validation. See the {topic} reference "
            f"for the full option list.")
    docs.append({"id": did, "title": title, "body": body})
    answerable.append({"query": f"guide to configuring {topic}", "expect_top": did})

# 3. Troubleshooting docs — distinct error signatures.
ERRORS = [("401", "unauthorized", "invalid or expired bearer token"),
          ("403", "forbidden", "insufficient role permissions"),
          ("404", "not found", "the resource identifier does not exist"),
          ("409", "conflict", "a duplicate idempotency key was reused"),
          ("422", "validation failed", "a required field was missing or malformed"),
          ("429", "too many requests", "the rate limit was exceeded"),
          ("500", "server error", "an unexpected internal error occurred"),
          ("503", "service unavailable", "the service is temporarily down for maintenance")]
for code, name, cause in ERRORS:
    did = f"error-{code}"
    title = f"Troubleshooting HTTP {code} {name}"
    body = (f"An HTTP {code} {name} response means {cause}. To resolve a {code} error, "
            f"check the request and retry. The {code} status is returned when {cause}.")
    docs.append({"id": did, "title": title, "body": body})
    answerable.append({"query": f"what does HTTP {code} mean", "expect_top": did})

# 4. Policy docs.
POLICIES = [("refund-policy", "Refund Policy",
             "Refunds are issued within 14 days of purchase for unused subscriptions. "
             "Partial refunds apply to annual plans cancelled mid-term. Contact billing support to request a refund."),
            ("privacy-policy", "Privacy Policy",
             "We collect account data, usage telemetry, and billing information. "
             "Personal data is retained for 24 months after account closure, then deleted."),
            ("sla", "Service Level Agreement",
             "We guarantee 99.9 percent monthly uptime. Service credits apply when uptime "
             "falls below the threshold. Scheduled maintenance is excluded from the calculation."),
            ("acceptable-use", "Acceptable Use Policy",
             "Accounts may not be used for spam, abuse, or illegal content. "
             "Violations result in suspension after a warning.")]
for did, title, body in POLICIES:
    docs.append({"id": did, "title": title, "body": body})
answerable.append({"query": "how long until I get a refund issued", "expect_top": "refund-policy"})
answerable.append({"query": "what uptime do you guarantee", "expect_top": "sla"})

# 5. Paraphrase cases — query words deliberately differ from the target doc's words.
#    These characterize the BM25 paraphrase gap. Each names the doc that SHOULD win
#    but probably won't under pure keyword matching.
paraphrase.append({"query": "my login isn't working and says I'm not allowed",
                   "expect_top": "error-403", "note": "'not allowed' vs 'forbidden/permissions'"})
paraphrase.append({"query": "the system says I sent too much traffic",
                   "expect_top": "error-429", "note": "'too much traffic' vs 'rate limit/too many requests'"})
paraphrase.append({"query": "how do I get my money back",
                   "expect_top": "refund-policy", "note": "'money back' vs 'refund'"})
paraphrase.append({"query": "stop people from signing in as someone else",
                   "expect_top": "guide-two-factor-login", "note": "paraphrase of 2FA"})

# 6. Absent queries — answers genuinely not in this corpus. Must abstain.
absent = [
    "what is the boiling point of water",
    "how do I fly to the moon",
    "recommend a good italian restaurant",
    "what year did the roman empire fall",
    "how do I train a neural network from scratch",
    "what is the capital of australia",
    "how do I replace a bicycle tire",
    "explain quantum entanglement",
    "what are the rules of cricket",
    "how do I bake sourdough bread",
]

fixture = {
    "_comment": "Large realistic corpus + labeled query sets for groundedwork's real-test battery. Deterministic (seed 42). Models a software company's knowledge base.",
    "config": {"min_score": 0.5, "top_k": 3, "k1": 1.5, "b": 0.75},
    "corpus": docs,
    "answerable": answerable,
    "paraphrase": paraphrase,
    "absent": absent,
}
out = ROOT / "fixtures" / "corpus_large.json"
out.write_text(json.dumps(fixture, indent=2, ensure_ascii=False))
print(f"wrote {out.relative_to(ROOT)}")
print(f"  docs:       {len(docs)}")
print(f"  answerable: {len(answerable)}")
print(f"  paraphrase: {len(paraphrase)}")
print(f"  absent:     {len(absent)}")
