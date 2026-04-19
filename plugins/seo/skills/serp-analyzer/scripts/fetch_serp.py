#!/usr/bin/env python3
"""
fetch_serp.py — DataForSEO wrapper for serp-analyzer skill.

HTTP fetch only. No parsing logic, no content analysis. Writes the raw
DataForSEO response plus a thin normalized snapshot. The LLM reads the
file and does the interpretation.

DataForSEO returns a single flat items[] array where each item has a
type field (organic, ai_overview, people_also_ask, related_searches,
featured_snippet, answer_box, knowledge_graph, images, etc.). We
normalize this into a stable per-type schema so downstream agents have
predictable field names.

Credentials (DATAFORSEO_LOGIN + DATAFORSEO_PASSWORD) are read from the
shell environment first, then from <cwd>/.env if missing.

Usage:
    python scripts/fetch_serp.py --keyword "..." --location-code 2276 \\
        --language-code de --out path.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


DATAFORSEO_ENDPOINT = (
    "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
)


def load_credentials() -> tuple[str, str]:
    """
    Priority: shell env first, then <cwd>/.env. Fail hard if still missing.
    The skill folder is never consulted — credentials belong to the
    invocation root, not the skill.
    """
    login = os.environ.get("DATAFORSEO_LOGIN")
    password = os.environ.get("DATAFORSEO_PASSWORD")

    if not login or not password:
        load_dotenv(Path.cwd() / ".env")
        login = login or os.environ.get("DATAFORSEO_LOGIN")
        password = password or os.environ.get("DATAFORSEO_PASSWORD")

    if not login or not password:
        print(
            "ERROR: DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD must be set.\n"
            "Either export them in your shell or add them to <cwd>/.env.\n"
            "Get credentials at https://app.dataforseo.com/api-access",
            file=sys.stderr,
        )
        sys.exit(2)

    return login, password


def fetch_serp(
    keyword: str,
    location_code: int,
    language_code: str,
    device: str,
    depth: int,
    load_async_ai_overview: bool,
    login: str,
    password: str,
) -> dict:
    body = [
        {
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "depth": depth,
            "load_async_ai_overview": load_async_ai_overview,
        }
    ]
    resp = requests.post(
        DATAFORSEO_ENDPOINT,
        auth=(login, password),
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def extract_task_result(raw: dict) -> tuple[dict | None, dict]:
    """
    DataForSEO wraps results as: {tasks: [{result: [{items: [...]}]}]}.
    Return (result_object, diagnostics) where diagnostics includes task
    status_code and cost so the caller can record them.
    """
    diagnostics: dict = {
        "api_status_code": raw.get("status_code"),
        "api_status_message": raw.get("status_message"),
        "cost_usd": raw.get("cost", 0.0),
    }

    tasks = raw.get("tasks") or []
    if not tasks:
        diagnostics["task_error"] = "no tasks in response"
        return None, diagnostics

    task = tasks[0]
    diagnostics["task_status_code"] = task.get("status_code")
    diagnostics["task_status_message"] = task.get("status_message")

    results = task.get("result") or []
    if not results:
        diagnostics["task_error"] = "task returned no result"
        return None, diagnostics

    return results[0], diagnostics


def partition_items(items: list[dict]) -> dict:
    """
    Split DataForSEO's flat items[] by type. Known types we capture
    explicitly; everything else is preserved in `other`.
    """
    buckets: dict[str, list[dict]] = {
        "organic": [],
        "ai_overview": [],
        "people_also_ask": [],
        "featured_snippet": [],
        "answer_box": [],
        "knowledge_graph": [],
        "related_searches": [],
        "images": [],
        "videos": [],
        "local_pack": [],
        "shopping": [],
        "top_stories": [],
        "other": [],
    }
    for item in items:
        t = item.get("type")
        if t in buckets:
            buckets[t].append(item)
        else:
            buckets["other"].append(item)
    return buckets


def resolve_ai_overview(
    ai_items: list[dict],
    load_async_requested: bool,
) -> tuple[dict | None, str]:
    """
    Return (payload, fetch_mode). Modes:
      - inline: AI Overview block is present and populated
      - async: load_async_ai_overview was requested and block present
      - async_pending: block returned with async_ai_overview flag still pending
      - absent: no ai_overview item in the response
    """
    if not ai_items:
        return None, "absent"

    block = ai_items[0]

    # DataForSEO marks async results with asynchronous-related fields.
    # If the block has nested items or markdown content, it's populated.
    has_content = bool(block.get("items")) or bool(block.get("markdown"))
    if not has_content and block.get("asynchronous_ai_overview"):
        return block, "async_pending"

    return block, "async" if load_async_requested else "inline"


def flatten_related_searches(blocks: list[dict]) -> list[str]:
    """
    Each related_searches block has an items[] of strings. Flatten across
    all blocks (there's usually only one).
    """
    out: list[str] = []
    for block in blocks:
        for q in block.get("items") or []:
            if isinstance(q, str):
                out.append(q)
    return out


def normalize(
    raw: dict,
    result: dict | None,
    diagnostics: dict,
    keyword: str,
    location_code: int,
    language_code: str,
    device: str,
    load_async_requested: bool,
) -> dict:
    items = (result or {}).get("items") or []
    buckets = partition_items(items)

    ai_overview, ai_mode = resolve_ai_overview(
        buckets["ai_overview"], load_async_requested
    )

    paa = buckets["people_also_ask"]
    organic = buckets["organic"]
    related = flatten_related_searches(buckets["related_searches"])

    featured = buckets["featured_snippet"][0] if buckets["featured_snippet"] else None
    answer = buckets["answer_box"][0] if buckets["answer_box"] else None
    kg = buckets["knowledge_graph"][0] if buckets["knowledge_graph"] else None

    return {
        "keyword": keyword,
        "locale": {
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
        },
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "provider": "dataforseo",
        "dataforseo_cost_usd": diagnostics.get("cost_usd", 0.0),
        "organic": organic,
        "ai_overview": ai_overview,
        "ai_overview_fetch_mode": ai_mode,
        "people_also_ask": paa,
        "related_searches": related,
        "featured_snippet": featured,
        "answer_box": answer,
        "knowledge_graph": kg,
        "rich_features": {
            "has_ai_overview": ai_overview is not None,
            "has_featured_snippet": featured is not None,
            "has_answer_box": answer is not None,
            "has_knowledge_graph": kg is not None,
            "paa_count": len(paa),
            "organic_count": len(organic),
            "related_searches_count": len(related),
            "images_blocks": len(buckets["images"]),
            "videos_blocks": len(buckets["videos"]),
            "other_block_types": sorted(
                {b.get("type") for b in buckets["other"] if b.get("type")}
            ),
        },
        "diagnostics": diagnostics,
        "_raw_response": raw,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--location-code", type=int, default=2276)
    parser.add_argument("--language-code", default="de")
    parser.add_argument("--device", default="desktop")
    parser.add_argument("--depth", type=int, default=10)
    parser.add_argument(
        "--no-ai-overview",
        action="store_true",
        help="Skip the load_async_ai_overview flag (slightly cheaper).",
    )
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    login, password = load_credentials()
    load_async = not args.no_ai_overview

    try:
        raw = fetch_serp(
            args.keyword,
            args.location_code,
            args.language_code,
            args.device,
            args.depth,
            load_async,
            login,
            password,
        )
    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        body = e.response.text[:300] if e.response is not None else ""
        print(
            f"ERROR: DataForSEO returned {status}: {body}",
            file=sys.stderr,
        )
        sys.exit(1)
    except requests.RequestException as e:
        print(f"ERROR: network failure calling DataForSEO: {e}", file=sys.stderr)
        sys.exit(1)

    result, diagnostics = extract_task_result(raw)

    if result is None:
        print(
            "ERROR: DataForSEO returned no result. Diagnostics: "
            + json.dumps(diagnostics),
            file=sys.stderr,
        )
        sys.exit(1)

    snapshot = normalize(
        raw,
        result,
        diagnostics,
        args.keyword,
        args.location_code,
        args.language_code,
        args.device,
        load_async,
    )

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print(
        json.dumps(
            {
                "status": "ok",
                "path": str(out_path),
                "organic_count": snapshot["rich_features"]["organic_count"],
                "ai_overview_present": snapshot["rich_features"]["has_ai_overview"],
                "ai_overview_fetch_mode": snapshot["ai_overview_fetch_mode"],
                "paa_count": snapshot["rich_features"]["paa_count"],
                "cost_usd": snapshot["dataforseo_cost_usd"],
            }
        )
    )


if __name__ == "__main__":
    main()
