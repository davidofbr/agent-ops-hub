# Output Schema — The Contract

This is what the skill produces. Downstream AI (Claude, GPT, agency
writing pipeline) consumes this file. The schema is the contract.
Breaking it breaks everything downstream — bump `schema_version` if
you change it.

## File locations

All outputs are written under `<cwd>/output/`. The tree:

```
<cwd>/output/
├── serp/                              # Phase 1 snapshots
│   └── {keyword_slug}_{lang}_{date}.json
├── pages/                             # Phase 2 per-URL markdown
│   └── {hash}.md  (plus {hash}.failure.json on fetch failures)
├── dissection/                        # Phase 2 combined dissection
│   └── {keyword_slug}_{date}_dissection.json
├── aeo/                               # Phase 3 AEO analysis
│   └── {keyword_slug}_{date}_aeo.json
└── final/                             # Phase 4 synthesis
    ├── {keyword_slug}_{date}.json
    └── {keyword_slug}_{date}.md
```

## Phase 1 snapshot (normalized)

Path: `<cwd>/output/serp/{keyword_slug}_{lang}_{date}.json`

```json
{
  "keyword": "reinraumkabine",
  "locale": { "location_code": 2276, "language_code": "de", "device": "desktop" },
  "fetched_at": "2026-04-19T07:57:02+00:00",
  "provider": "dataforseo",
  "dataforseo_cost_usd": 0.002,
  "organic": [ /* DataForSEO organic items verbatim */ ],
  "ai_overview": null,
  "ai_overview_fetch_mode": "absent",
  "people_also_ask": [],
  "related_searches": ["Reinraumzelt gebraucht", "Reinraumzelt Preis", "..."],
  "featured_snippet": null,
  "answer_box": null,
  "knowledge_graph": null,
  "rich_features": {
    "has_ai_overview": false,
    "has_featured_snippet": false,
    "has_answer_box": false,
    "has_knowledge_graph": false,
    "paa_count": 0,
    "organic_count": 10,
    "related_searches_count": 7,
    "images_blocks": 1,
    "videos_blocks": 0,
    "other_block_types": []
  },
  "diagnostics": {
    "api_status_code": 20000,
    "api_status_message": "Ok.",
    "cost_usd": 0.002,
    "task_status_code": 20000,
    "task_status_message": "Ok."
  },
  "_raw_response": { /* full DataForSEO JSON, unaltered */ }
}
```

## Final output file

Path: `<cwd>/output/final/{keyword_slug}_{date}.json`

```json
{
  "schema_version": "2.0",
  "keyword": "reinraumkabine",
  "keyword_slug": "reinraumkabine",
  "locale": { "location_code": 2276, "language_code": "de", "device": "desktop" },
  "analyzed_at": "2026-04-19T14:32:00Z",

  "cost": {
    "provider": "dataforseo",
    "dataforseo_cost_usd": 0.002,
    "pages_fetched": 10,
    "pages_failed": 0
  },

  "serp_features": {
    "ai_overview_present": false,
    "ai_overview_fetch_mode": "absent",
    "featured_snippet_present": false,
    "knowledge_panel_present": false,
    "paa_count": 0,
    "related_searches_count": 7,
    "rich_features": ["images"]
  },

  "organic_top_10": [
    {
      "position": 1,
      "url": "...",
      "domain": "...",
      "title": "...",
      "description": "..."
    }
  ],

  "content_analysis": {
    "pages": [
      {
        "url": "...",
        "position": 1,
        "page_title": "...",
        "meta_description": "...",
        "domain": "...",
        "content_length_words": 2847,
        "h_outline": [
          { "level": 2, "text": "..." }
        ],
        "main_points": ["...", "..."],
        "entities": ["...", "..."],
        "questions_answered": ["...", "..."],
        "images_count": 12,
        "has_original_data": true,
        "has_author_byline": true,
        "publish_date": "2024-06-...",
        "last_updated": null,
        "ctas": {
          "primary": "...",
          "primary_placement": "...",
          "primary_count": 4,
          "secondary": "...",
          "secondary_count": 1
        },
        "schema_types_detected": ["Article", "FAQPage"],
        "fetch_status": "ok",
        "notes": "..."
      }
    ],
    "fetch_failures": []
  },

  "coverage_map": {
    "table_stakes": [
      { "topic": "...", "covered_by_n_pages": 9, "pages": [1,2,3,4,5,6,7,8,9] }
    ],
    "differentiators": [
      { "topic": "...", "covered_by_n_pages": 3, "pages": [2,5,7] }
    ],
    "gaps": [
      { "topic": "...", "covered_by_n_pages": 0, "rationale": "Relevant to intent but nobody covers it" }
    ]
  },

  "aeo": {
    "ai_overview_present": false,
    "ai_overview_fetch_mode": "absent",
    "ai_overview": null,
    "paa": [
      { "question": "...", "answered_by_top_10": true, "answered_by_urls": ["..."] }
    ],
    "paa_gaps": ["..."]
  },

  "related_searches": ["..."],

  "domain_list": [
    { "domain": "...", "positions": [1], "cited_in_ai_overview": false }
  ]
}
```

When `ai_overview_present` is true, the `aeo.ai_overview` object follows
the shape produced by the AEO analyzer (see `agents/aeo-analyzer.md`):

```json
{
  "claims": [
    { "claim": "…", "element_type": "ai_overview_element", "cited_references": [0, 2] }
  ],
  "sub_questions_answered": ["…"],
  "comparisons_made": [ /* from ai_overview_table_element */ ],
  "citations": [
    { "url": "…", "domain": "…", "reference_index": 0, "also_in_organic_top_10": true, "organic_position": 3 }
  ],
  "aeo_only_winners": [ /* references cited in AI Overview but not in organic top 10 */ ]
}
```

## Markdown sidecar

Path: `<cwd>/output/final/{keyword_slug}_{date}.md`

Human-readable scan of the same data. Structure:

1. Header: keyword, locale, date, cost
2. SERP features summary (one line)
3. Top 10 list (position, domain, title)
4. AI Overview summary (if present) + citation list
5. PAA questions (with "covered / gap" tag)
6. Related searches (flat list)
7. Coverage map: table stakes / differentiators / gaps as three lists
8. Fetch failures (if any)

No recommendations. No brief. Just a structured scan of the data.

## Schema rules

- Every field is always present. Use null or empty array when absent.
- Dates are ISO 8601 UTC.
- Domains never include scheme or trailing slash (`example.com`, not `https://example.com/`).
- URLs preserve the full original form from DataForSEO.
- `ai_overview_fetch_mode` MUST be one of: `inline`, `async`, `async_pending`, `absent`. Do not conflate `absent` with `async_pending` — they mean different things.
- `content_length_words` is the word count of the main content body,
  not the whole HTML document. Navigation and footer don't count.
- Bump `schema_version` on any breaking change.
