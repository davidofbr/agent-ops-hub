---
name: serp-analyzer
description: Deconstructs a Google SERP for a target keyword into structured intelligence — top 10 organic results, AI Overview, PAA, rich features — then extracts and analyzes the top 10 page contents so downstream AI can build a winning content brief. Use this skill whenever the user wants to analyze a keyword, research a SERP, understand what's ranking, build a content brief, or prepare to write content for SEO/AEO. Also trigger on phrases like "analyze this keyword", "what's ranking for X", "deconstruct the SERP for Y", or when a keyword is dropped in with an implied intent to write for it. Defaults to German locale (location_code=2276, language_code=de) for B2B clients — override only when the user signals otherwise.
---

# SERP Analyzer

Read `${CLAUDE_SKILL_DIR}/references/output-schema.md`, `${CLAUDE_SKILL_DIR}/references/locale-defaults.md`,
and `${CLAUDE_SKILL_DIR}/references/dataforseo.md` before doing anything else. The schema
is the contract every agent writes against. The DataForSEO reference
explains the flat `items[]` taxonomy — if you don't understand it, you
will misread the data.

---

## What this skill does

Given a keyword, produces a structured JSON + Markdown analysis of:
- The top 10 organic results (what they are, what they cover, how)
- The AI Overview (if present) and who Google cites
- People Also Ask, related searches, rich features
- Table-stakes vs differentiator vs gap content coverage across top 10

Output is designed to be consumed by another AI (Claude, GPT, custom
agent) to write the actual content brief or draft. This skill does not
write content. It produces intelligence.

---

## Inputs

The skill runs with two pieces of information and one defaulted one:

1. **Keyword** — the primary term. Required. Take it from the user
   prompt. If the user has not provided a keyword, ask for one. Do
   not guess. Do not run on a keyword you inferred from surrounding
   conversation unless the user confirms it.
2. **Locale** — defaults to `location_code=2276, language_code=de`
   (Germany, German). Only override if the user explicitly signals a
   non-German market or if the keyword is unambiguously in a non-German
   language. When in doubt, confirm before running.
3. **Intent hint** (optional) — if the user already knows the angle
   (e.g. "we're a fund, not a SaaS"), capture it. Passed to downstream
   AI, not used by this skill directly.

---

## Root-directory contract

The skill runs relative to the directory it's invoked from (CWD).
Everything it writes goes under `<cwd>/output/`. If that directory
doesn't exist, create it.

Structure:

```
<cwd>/
├── .env                 # optional — DataForSEO creds if not in shell env
└── output/
    ├── serp/            # Phase 1 SERP snapshots
    ├── pages/           # Phase 2 raw page markdown (per URL)
    ├── dissection/      # Phase 2 dissection JSON
    ├── aeo/             # Phase 3 AEO analysis JSON
    └── final/           # Phase 4 synthesis JSON + MD
```

The scripts read credentials from the shell environment first
(`DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD`, optional `JINA_API_KEY`)
and fall back to `<cwd>/.env`. The skill folder itself holds no
secrets and no outputs.

`${CLAUDE_SKILL_DIR}` is only used to locate scripts and references.

---

## Workflow

The agents chain. Do not reorder. Do not skip phases.

### Phase 1 — SERP snapshot

Spawn **serp-scout** with:
- `keyword`
- `locale` — `{location_code, language_code, device}` (defaults above)
- `skill_dir`: `${CLAUDE_SKILL_DIR}`
- `output_path`: `<cwd>/output/serp/{keyword_slug}_{language_code}_{YYYY-MM-DD}.json`

serp-scout calls `scripts/fetch_serp.py`, which POSTs to DataForSEO's
`serp/google/organic/live/advanced` endpoint. The response is a flat
`items[]` array; the script partitions items by `type` and writes a
normalized snapshot to `output_path`.

Check the cache first. If a snapshot for the same keyword + locale +
date already exists at `output_path`, reuse it — do not re-hit the API.

### Phase 2 — Content dissection

Read the snapshot from Phase 1. Extract the top 10 organic URLs from
the normalized `organic[]` array.

Spawn **content-dissector** with:
- `urls`: list of top 10 organic URLs
- `keyword`: for context (what the page should be answering)
- `skill_dir`: `${CLAUDE_SKILL_DIR}`
- `pages_dir`: `<cwd>/output/pages/`
- `output_path`: `<cwd>/output/dissection/{keyword_slug}_{YYYY-MM-DD}_dissection.json`

content-dissector fetches each URL via `scripts/fetch_page.py` (which
uses r.jina.ai to return clean markdown) and analyzes the content with
language understanding — no regex, no hardcoded parsing. The agent reads
the page like a human strategist would.

### Phase 3 — AEO layer

Spawn **aeo-analyzer** with:
- `snapshot_path`: the Phase 1 output
- `dissection_path`: the Phase 2 output
- `skill_dir`: `${CLAUDE_SKILL_DIR}`
- `output_path`: `<cwd>/output/aeo/{keyword_slug}_{YYYY-MM-DD}_aeo.json`

aeo-analyzer looks at the AI Overview block (if present), maps which
top 10 pages Google actually cites, and extracts the sub-questions the
AI Overview answers. This is where the differentiator lives — every
agency builds SERP scrapers, almost none build citation analysis.

### Phase 4 — Synthesis

Once all three agents have written their outputs, you (the hub) do the
final synthesis. This step is not an agent — it's your job. Read all
three files and produce:

- `<cwd>/output/final/{keyword_slug}_{YYYY-MM-DD}.json` — the full
  structured output per `${CLAUDE_SKILL_DIR}/references/output-schema.md`
- `<cwd>/output/final/{keyword_slug}_{YYYY-MM-DD}.md` — a human-readable
  version for quick scan

The synthesis must include:
- **Table stakes**: topics covered by 7+/10 top results (must-have or you don't rank)
- **Differentiators**: topics covered by 2–4/10 results (opportunities)
- **Gaps**: relevant topics covered by 0–1/10 results (the edge)
- **AEO citation map**: which domains Google's AI Overview trusts
- **SERP feature inventory**: rich snippets, PAA, related searches
- **Domain list**: top 10 domains, no authority scoring (v1 scope)

Do not make recommendations. Do not write the brief. The downstream
AI does that. Your job is to hand it clean, complete data.

---

## Cost awareness

Every run uses:
- 1 DataForSEO live/advanced call per keyword (Phase 1) — $0.002 flat.
  Enabling `load_async_ai_overview` adds a small supplement when an
  AI Overview is actually generated.
- 10 r.jina.ai fetches per keyword (Phase 2) — free tier usually enough.

DataForSEO returns the per-request `cost` in the response. The fetch
script records it in `diagnostics.cost_usd`; include
`dataforseo_cost_usd`, `ai_overview_fetch_mode`, and `pages_fetched`
in the final output. Sum `dataforseo_cost_usd` across runs to get real
monthly spend for client reporting.

If the Phase 1 snapshot already exists for today's date, Phase 1 costs 0.
If the cache has page markdown for URLs that haven't changed, reuse
it — `fetch_page.py` does cache-first keyed on the `--out` path.

---

## What this skill is not

- Not a content writer. Hands data to downstream AI.
- Not a ranking tracker. One-shot analysis, not time series.
- Not an authority scorer. Domain list only, no DR/DA (v1).
- Not a keyword research tool. Takes one keyword, analyzes it deeply.
  For cluster/volume work, use a different tool and feed this one.

---

## Failure modes to watch for

- **Wrong locale**: running a German B2B keyword with
  `location_code=2840` (US) produces a US SERP. The whole analysis is
  garbage. Confirm locale on every run if the user hasn't pinned it.
- **Jina returns empty**: some sites block it. The fetch script logs
  these — flag them in the final output rather than silently dropping.
- **AI Overview not present**: don't force it. Mark as null and move on.
  Real absence is a signal, not a failure.
- **Async AI Overview pending**: if `ai_overview_fetch_mode` is
  `async_pending`, the data is incomplete. Surface it in the AEO output
  rather than treating it as absent.
- **Paywalls / login walls**: content-dissector will see almost nothing.
  Flag and skip rather than hallucinating what's behind the wall.
- **Missing credentials**: `fetch_serp.py` exits with a clear error if
  `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` are not set. The hub should
  surface this to the user rather than swallowing it.
