# DataForSEO Reference

DataForSEO is the SERP provider this skill uses. Reliable AI Overview
return, commercial intent signals, and a flat per-call cost model.

## Endpoint

`POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced`

Live = synchronous, no task queue. One keyword per request.

## Authentication

HTTP Basic Auth. `Authorization: Basic base64(login:password)`. The
Python `requests` library handles this directly via `auth=(login, password)`.

The API password is auto-generated in the DataForSEO dashboard
(`https://app.dataforseo.com/api-access`) and is different from the
account password. Never hardcode, never log, never commit.

Credentials come from the shell environment first
(`DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`) and fall back to `<cwd>/.env`
via python-dotenv. The skill folder is never consulted.

## Request body

```json
[
  {
    "keyword": "reinraumkabine",
    "location_code": 2276,
    "language_code": "de",
    "device": "desktop",
    "depth": 10,
    "load_async_ai_overview": true
  }
]
```

Notes:
- The body is an array — DataForSEO accepts batched requests, but this
  skill always sends exactly one task per call.
- `location_code` is numeric. `2276` = Germany. See
  `references/locale-defaults.md` for DACH codes or query
  `/v3/serp/google/locations` for the full list.
- `depth=10` returns the first 10 organic results. Higher depth costs
  more and this skill doesn't need it.
- `load_async_ai_overview=true` instructs DataForSEO to trigger the
  async AI Overview fetch on their side. When the overview is ready,
  it appears as an `ai_overview` item in the response. If it isn't
  ready when the call returns, the placeholder carries an
  `asynchronous_ai_overview` marker — our script records this as
  `ai_overview_fetch_mode: "async_pending"`.

## Response shape

```json
{
  "status_code": 20000,
  "status_message": "Ok.",
  "cost": 0.002,
  "tasks": [
    {
      "status_code": 20000,
      "status_message": "Ok.",
      "result": [
        {
          "keyword": "...",
          "location_code": 2276,
          "language_code": "de",
          "items": [ /* typed blocks — see below */ ]
        }
      ]
    }
  ]
}
```

Top-level `cost` is the per-request dollar amount. The per-task result
sits at `tasks[0].result[0].items[]`. The script normalizes this into
a flat, per-type schema — see `references/output-schema.md`.

## items[] taxonomy

Every block in `items[]` has a `type` field. The types this skill
captures explicitly:

| type               | what it is                                                       |
|--------------------|------------------------------------------------------------------|
| `organic`          | Standard organic result (title, url, domain, description, …)     |
| `ai_overview`      | Google's AI Overview block (see below)                           |
| `people_also_ask`  | PAA container; `items[]` holds the individual Q/A entries        |
| `featured_snippet` | Featured snippet block (when present)                            |
| `answer_box`       | Answer box block (when present)                                  |
| `knowledge_graph`  | Knowledge panel block                                            |
| `related_searches` | Block whose `items[]` is a list of query strings                 |
| `images`           | Inline image carousel                                            |
| `videos`           | Inline video carousel                                            |
| `local_pack`       | Map-pack block                                                   |
| `shopping`         | Shopping carousel                                                |
| `top_stories`      | Top stories block                                                |

Anything else is kept under the normalized snapshot's `rich_features.other_block_types`
and preserved under `_raw_response` for downstream consumers.

## The organic block

Fields we rely on (from DataForSEO's schema):
- `rank_group` — the 1-based organic position. Use this, not `rank_absolute`,
  which also counts non-organic blocks.
- `rank_absolute` — position among ALL items in the SERP.
- `url` — the destination URL.
- `domain` — the host without scheme or path.
- `title` — the SERP title.
- `description` — the SERP snippet.
- `breadcrumb` — the displayed breadcrumb path.
- `website_name` — branded display name, when Google renders one.
- `highlighted` — array of emphasised terms from the snippet.
- `is_featured_snippet`, `is_image`, `is_video` — booleans.

## The AI Overview block

`type: "ai_overview"`. Unlike SerpAPI's `text_blocks` shape, DataForSEO
nests typed sub-elements:

```json
{
  "type": "ai_overview",
  "rank_absolute": 1,
  "markdown": "...",
  "items": [
    {
      "type": "ai_overview_element",
      "title": "…",
      "text": "…",
      "markdown": "…",
      "links": [...],
      "images": [...],
      "references": [ { "ref_id": 0 }, ... ]
    },
    {
      "type": "ai_overview_expanded_element",
      "title": "Was kostet X?",
      "components": [ /* nested ai_overview_element-shaped entries */ ]
    },
    {
      "type": "ai_overview_table_element",
      "markdown": "…",
      "table": { "table_header": [...], "table_content": [[...], [...]] }
    },
    {
      "type": "ai_overview_video_element",
      "title": "…",
      "snippet": "…",
      "url": "…",
      "image_url": "…"
    }
  ],
  "references": [
    { "type": "ai_overview_reference", "title": "…", "url": "…", "domain": "…", "source": "…", "text": "…" }
  ]
}
```

The top-level `ai_overview.references[]` is the source list. Sub-elements
reference sources via their own `references[]` carrying a `ref_id` that
points back into that list.

The AEO analyzer walks the `items[]` tree by sub-element type and
extracts claims + citations together. It does not parse sub-elements
with regex — it reads them with language understanding.

### Fetch modes we track

The script records `ai_overview_fetch_mode` in every snapshot:

- `inline` — AI Overview came back in the response without async deferral
- `async` — `load_async_ai_overview` was requested and the block came back populated
- `async_pending` — the block is a placeholder with `asynchronous_ai_overview` set; data is incomplete
- `absent` — no AI Overview for this query

**Do not conflate `absent` with `async_pending`.** Absent is a real
signal about the SERP. Async_pending is incomplete data.

## Cost

- $0.002 per live/advanced call (flat, regardless of SERP size up to 10 results)
- `load_async_ai_overview` may add a small supplement when an AI Overview is actually generated
- `calculate_rectangles` adds $0.002 per call (we don't use it)

The per-request cost appears at the top level of the response as `cost`.
The script records it in `diagnostics.cost_usd` on every snapshot so
client reporting can sum exact spend.

## Rate limits

Up to 2000 API calls per minute. For this skill's usage pattern (one
keyword at a time from a desktop app) rate limits are not a real concern.

## What we don't use

- `/v3/serp/google/organic/task_post` — asynchronous task queue. Not
  needed for one-keyword-at-a-time runs.
- `/v3/serp/google/ai_mode/...` — the dedicated AI mode endpoint. Our
  `load_async_ai_overview=true` path on the organic endpoint covers it.
- Paid/SEMrush-style history endpoints. One-shot analysis only.
- On-page content parsing. Page fetching goes through r.jina.ai for
  clean markdown.
