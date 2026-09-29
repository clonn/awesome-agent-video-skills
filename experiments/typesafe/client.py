"""Minimal stdlib client for TypeSafe System One (POST /v1/systemone). Key is read from env TYPESAFE_API_KEY and never printed.
Docs: https://docs.typesafe.ai/api.md, https://docs.typesafe.ai/models.md"""
import json
import os
import time
import urllib.error
import urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
PRICE_PER_INPUT_TOKEN = 0.042 / 1_000_000  # USD, input only per models.md; output is free


def call(state, questions, retries=4):
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise RuntimeError("TYPESAFE_API_KEY is not set")
    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            data["_latency_s"] = round(time.time() - t0, 3)
            return data
        except urllib.error.HTTPError as e:
            if e.code in (429, 529) and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"TypeSafe HTTP {e.code}: {e.read()[:300].decode('utf-8', 'replace')}") from None
    raise RuntimeError("unreachable")


def cost(usage):
    return usage.get("input_tokens", 0) * PRICE_PER_INPUT_TOKEN
