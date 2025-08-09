#!/usr/bin/env python3
from __future__ import annotations
import os, json, requests

ENDPOINT = os.getenv("WEAVIATE_ENDPOINT", "http://localhost:8080").rstrip("/")
SCHEMA_PATH = os.getenv("WEAVIATE_SCHEMA", "schemas/weaviate_schema.json")

def main() -> int:
    with open(SCHEMA_PATH, "r") as f:
        data = json.load(f)
    # Ensure server is reachable
    try:
        r = requests.get(f"{ENDPOINT}/v1/.well-known/ready", timeout=5)
        r.raise_for_status()
    except Exception as e:
        print(f"Weaviate not ready at {ENDPOINT}: {e}")
        return 1
    # Fetch existing classes
    ex = requests.get(f"{ENDPOINT}/v1/schema").json().get("classes", [])
    existing = {c.get("class") for c in ex}
    created = 0
    for cls in data.get("classes", []):
        name = cls.get("class")
        if name in existing:
            print(f"[skip] {name} exists")
            continue
        # Weaviate 1.32 accepts POST of a single class object to /v1/schema
        resp = requests.post(f"{ENDPOINT}/v1/schema", json=cls)
        if resp.status_code >= 300:
            print(f"[error] {name}: {resp.status_code} {resp.text}")
            return 1
        print(f"[ok] created {name}")
        created += 1
    print(f"Done. Created {created} classes.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
