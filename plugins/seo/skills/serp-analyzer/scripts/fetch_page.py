#!/usr/bin/env python3
"""
fetch_page.py — r.jina.ai wrapper for serp-analyzer skill.

HTTP fetch only. Returns the page as clean markdown. No regex, no
parsing, no field extraction. The LLM reads the markdown and extracts
fields using language understanding.

Usage:
    python scripts/fetch_page.py --url "https://..." --out path.md
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


JINA_BASE = "https://r.jina.ai/"


def load_jina_key() -> str | None:
    """Jina works without a key but rate-limits harder. Optional.

    Priority: shell env first, then <cwd>/.env. The skill folder is never
    consulted — credentials belong to the invocation root.
    """
    key = os.environ.get("JINA_API_KEY")
    if key:
        return key
    load_dotenv(Path.cwd() / ".env")
    return os.environ.get("JINA_API_KEY")  # may be None


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def fetch(url: str) -> tuple[str, str]:
    """
    Returns (status, content). Status is one of:
      ok | empty | http_error | timeout | network_error
    """
    headers = {"Accept": "text/plain"}
    key = load_jina_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"

    try:
        resp = requests.get(JINA_BASE + url, headers=headers, timeout=45)
    except requests.Timeout:
        return "timeout", ""
    except requests.RequestException as e:
        return "network_error", str(e)

    if resp.status_code >= 400:
        return "http_error", f"{resp.status_code}: {resp.text[:200]}"

    content = resp.text.strip()
    if not content or len(content) < 100:
        return "empty", content

    return "ok", content


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # cache-first: if this URL was already fetched, reuse
    if out_path.exists() and out_path.stat().st_size > 100:
        print(json.dumps({
            "status": "cached",
            "url": args.url,
            "path": str(out_path),
            "bytes": out_path.stat().st_size,
        }))
        return

    status, content = fetch(args.url)

    if status != "ok":
        # write a failure marker file so the agent can see what happened
        failure = {"status": status, "url": args.url, "detail": content}
        out_path.with_suffix(".failure.json").write_text(
            json.dumps(failure, indent=2), encoding="utf-8"
        )
        print(json.dumps({
            "status": status,
            "url": args.url,
            "path": None,
            "detail": content[:300],
        }))
        sys.exit(0 if status in ("empty", "http_error") else 1)

    out_path.write_text(content, encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "url": args.url,
        "path": str(out_path),
        "bytes": len(content),
    }))


if __name__ == "__main__":
    main()
