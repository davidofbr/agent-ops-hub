---
name: init-brand-context
description: >
  URL-first scaffolder for the Faber & Friends hub. Bootstraps four context
  artifacts at the root of a client repo: `company.md` (5-field API-safe
  contract), `competitors.json` (structured, nullable quant fields),
  `icp.md` (segment-level targeting), `personas.md` (buyer archetypes
  formatted for later agent embodiment). Scrapes the client domain and
  up to five user-confirmed competitor domains via `web_fetch`, runs
  corroboration searches via `web_search`, scores confidence per file,
  and interviews the user one question at a time to close the highest-
  impact gaps. Trigger on "init brand context", "scaffold brand context",
  "set up context for [domain]", "bootstrap brand research", or when a
  user drops a URL with an implied intent to build out client context.
  Do NOT trigger for generic website scraping, competitor-only research,
  rank/SEO data pulls, or updates to existing context files — those have
  their own skills.
---

# SKILL: INIT-BRAND-CONTEXT

Bootstraps four context files for a client repo starting from a URL. Scrapes
the client site and user-confirmed competitors with `web_fetch`, corroborates
with `web_search`, and fills remaining gaps through targeted interviews.

**Read before starting (in order):**
- `references/schema.md` — `company.md` contract. Hard invariant.
- `references/market-codes.md` — free-form → ISO 3166-1 alpha-2 map.
- `references/language-codes.md` — free-form → ISO 639-1 map.
- `references/scrape-plan.md` — URL patterns and extraction rules.
- `references/competitor-discovery.md` — web_search query patterns per industry signal.
- `references/competitors-schema.md` — JSON schema + null-safety rules for `competitors.json`.
- `references/icp-template.md` — full template for `icp.md`.
- `references/personas-template.md` — full template for `personas.md`.
- `references/confidence-model.md` — scoring rubrics, dimension weights, per-file requirements.
- `references/interview-banks.md` — questions by file × dimension for gap-closing.

Runs relative to CWD. CWD is the client repo. `${CLAUDE_SKILL_DIR}` is used only
to locate the reference files above.

---

## Output Files

```
<cwd>/company.md           YAML frontmatter, 5 fields, API-safe
<cwd>/competitors.json     Structured, nullable quant fields
<cwd>/icp.md               Markdown with confidence header
<cwd>/personas.md          Markdown with confidence header
```

No other files are created. No directories are created. Never writes outside CWD.

---

## Hard Contract

These invariants must hold regardless of confidence level or user overrides.
Downstream skills validate against them.

1. `company.md` has exactly the five fields in `references/schema.md`, normalized.
2. `competitors.json` is valid JSON conforming to `references/competitors-schema.md`.
3. Every file written has a confidence header.
4. No field is ever invented. Missing data is `[UNKNOWN]` or `null`, not plausible-sounding.
5. Provenance tags `[V]` / `[I]` / `[H]` are applied per field in `icp.md` and `personas.md`.

---

## Phase 1 — Pre-check

For each target file in CWD, check existence. Show the user a table:

```
company.md         → exists (size, last modified)
competitors.json   → not present
icp.md             → exists (size, last modified)
personas.md        → not present
```

Ask a single multi-select question: "Which files do you want to overwrite?"
Options: each existing file. Files not selected are skipped entirely in later
phases — scrape work is still done but their drafts are discarded at write time.

If the user selects zero files, stop.

---

## Phase 2 — Intake

Ask exactly one required question: "What is the primary company URL?"

Then offer one optional multi-select: "Any existing intel to hand in?"
Options: `customer interviews`, `positioning doc`, `competitor list`,
`pricing sheet`, `none`. If the user selects any, accept free-form paste
in the next turn and weight it as `CLIENT_VOICE` (1.0) in source diversity.

Do not proceed without a URL. Empty answer → re-ask.

---

## Phase 3 — Primary Scrape

Follow `references/scrape-plan.md`. Summary:

1. `web_fetch` the root URL. If it 404s or the domain doesn't resolve, stop
   and tell the user. Do not guess a different TLD.
2. From the root HTML, attempt to locate `sitemap.xml` or `robots.txt`.
   If found and parseable, use it to prioritize URL discovery.
3. If no sitemap, walk the URL candidate list in `scrape-plan.md` in order,
   stopping at the first match per category (`about`, `pricing`, `products`,
   `customers`, `impressum`, `team`).
4. Cap total `web_fetch` calls at 8 for this phase. Report which URLs hit
   and which 404'd in a single summary line after completion.

Record source URLs verbatim. These go into every file's provenance log.

---

## Phase 4 — Extraction

Parse the fetched content into draft fields for each output file.
Extraction rules per field are in `references/scrape-plan.md` Section 3.

Tag every extracted fact internally:
- `[V]` Validated — explicit factual statement from authoritative page
  (Impressum for legal name, `<html lang>` for language, etc.)
- `[I]` Inferred — derived from signals, not stated directly
- `[H]` Hypothesis — suggested by copy but not explicitly claimed

Marketing copy is `[I]` by default. Impressum fields are `[V]`. Pricing
shown on a `/pricing` page is `[V]`. "Trusted by Fortune 500" with no named
customers is `[H]`.

---

## Phase 5 — Competitor Discovery + Confirmation

Read `references/competitor-discovery.md`. Pick the query pattern matching
the signals observed in Phase 3:

- Pricing page present + subscription language → SaaS pattern
- Impressum + physical product copy + DACH language → DE B2B pattern
- Service pages + team page with headshots → services pattern
- Fallback: `"[brand] vs"` + `"[category] alternatives"`

Run `web_search` with the selected pattern. Deduplicate, exclude the client
domain, exclude review/comparison sites (g2.com, capterra.com, etc. unless
they are the actual subject). Present up to 5 candidates with their domains
and a one-line positioning blurb pulled from search snippets.

Ask one multi-select question: "Which of these are actual competitors to
scrape? Add your own if I missed any."

Wait for confirmation. If the user adds domains, accept them. If the user
removes all suggestions and adds zero, skip Phase 6 and mark
`competitors.json` essential coverage as 0.

---

## Phase 6 — Competitor Scrape

For each confirmed competitor, `web_fetch` homepage + `about` + `pricing`
+ `cases` where they exist. Cap at 4 pages per competitor. Total phase cap:
5 competitors × 4 pages = 20 `web_fetch` calls maximum.

Extract per competitor:
- `name` (from their homepage `<title>` or brand element)
- `domain` (normalized, from the URL they were given)
- `positioning` (hero copy, one sentence)
- `products` (list from nav or products page)
- `pricing_visible` (boolean — `/pricing` page present with numeric prices)
- `case_studies_count` (integer — count on their cases/customers page)
- `observable_strengths` (bullet list inferred from copy)
- `observable_weaknesses` (bullet list inferred from gaps in their offering)
- `domain_rating` (null)
- `backlinks` (null)
- `page_count` (null)

Record `source_urls` per competitor.

---

## Phase 7 — Initial Confidence Scoring

Score each file using `references/confidence-model.md` dimension weights:

| Dimension         | Weight |
|-------------------|--------|
| Essential coverage | 35%   |
| Source diversity  | 25%    |
| Data grounding    | 20%    |
| Consistency       | 10%    |
| Recency           | 10%    |

**Source diversity weights for this skill:**

| Source type                                   | Weight | Tag          |
|-----------------------------------------------|--------|--------------|
| User interview response during this session   | 1.0    | CLIENT_VOICE |
| Pasted hand-off intel from Phase 2            | 1.0    | CLIENT_VOICE |
| Customer review or press mention (web_search) | 0.60   | REVIEW       |
| Industry comparison page (web_search)         | 0.50   | COMPARISON   |
| Client site scrape (marketing copy)           | 0.45   | STRUCTURAL   |
| Competitor site scrape                        | 0.45   | STRUCTURAL   |
| Sitemap XML                                   | 0.25   | STRUCTURAL   |

**Ceiling rule:** No CLIENT_VOICE source → source diversity caps at 60%
regardless of how many structural sources are present. Interview responses
in Phase 8 lift the cap.

Report scores before proceeding:

> "Initial scores — company: 78% | competitors: 52% | icp: 41% | personas: 36%
> Files below 90%: competitors, icp, personas
> Starting targeted interview. One question at a time. Say 'stop' any time."

---

## Phase 8 — Targeted Interview

Use `references/interview-banks.md`. Loop:

1. Pick the file with the largest gap below 90%.
2. Within that file, pick the lowest-scoring dimension.
3. Select the highest-impact question for that dimension from the bank.
4. Ask exactly one question.
5. Record the answer as `CLIENT_VOICE` source.
6. Re-score the affected file.
7. Report briefly: "icp now 68%. Next question:"
8. Loop.

**Rules:**
- Never ask about something already extracted or already answered.
- Never ask the same question twice.
- Cap the interview at **10 questions total** across all files, not per file.
  This is the key divergence from `initialize-client-repo`: scrape-first
  skills should not grind the user down with 30-question interviews.
- If the user says "skip" or "don't know", mark the field `[UNKNOWN]`
  and move on.
- If the user says "stop" or "good enough", freeze scores and proceed.
- Honor the 10-question cap even if files are below 90%. Report final
  state honestly.

---

## Phase 9 — File Generation

Generate files in dependency order:
1. `company.md` — others may reference `name`, `domain`, `market`, `language`.
2. `competitors.json` — referenced by icp/personas for competitive framing.
3. `icp.md`
4. `personas.md`

Only write files the user selected in Phase 1. Skipped files are not touched.

Use exact templates from:
- `references/schema.md` for `company.md` structure.
- `references/competitors-schema.md` for `competitors.json`.
- `references/icp-template.md` for `icp.md`.
- `references/personas-template.md` for `personas.md`.

**Confidence header — required on every markdown file:**

```
<!-- CONFIDENCE: [X]% | Essential: [X]% | Sources: [X]% | Data: [X]% | Consistency: [X]% | Recency: [X]% -->
<!-- STATUS: [COMPLETE | PARTIAL | INCOMPLETE] | Last scored: [DATE] | Skill: init-brand-context -->
```

Thresholds:
- ≥ 90%: COMPLETE ✓ Ready
- 70–89%: PARTIAL ⚠ Partial
- < 70%: INCOMPLETE ✗ Incomplete

For `competitors.json`, the confidence header goes in a top-level `_meta`
object per `references/competitors-schema.md`.

**Section-level epistemic markers** apply to `icp.md` and `personas.md`
sections where the dominant facts are `[H]` or `[I]`:

```
> ⚠ HYPOTHESIS — not yet validated with client
```
or
```
> ⚠ INFERRED — derived from marketing copy, not stated directly
```

Clean sections (dominantly `[V]`) get no marker.

---

## Phase 10 — Summary

After all selected files are written, output:

```
## Brand Context Initialized — [COMPANY NAME]

### Files Written
| File              | Score | Status     |
|-------------------|-------|------------|
| company.md        |  XX%  | COMPLETE   |
| competitors.json  |  XX%  | PARTIAL    |
| icp.md            |  XX%  | PARTIAL    |
| personas.md       |  XX%  | INCOMPLETE |

### Scrape Summary
Client pages fetched: [N]
Competitor pages fetched: [N]
Web searches run: [N]
Interview questions asked: [N] / 10

### To Reach 90%+ on Partial Files
[One line per partial file stating the specific missing input. Be honest — if
the gap is customer interview data that no amount of scraping can fix, say so.]

### Enrichment Next Steps
- competitors.json quant fields (DR, backlinks, page_count) require Ahrefs
  and Screaming Frog. Run enrichment skill when data is available.
- personas.md confidence is capped around 60% from marketing copy alone.
  Upload call transcripts or win/loss notes to raise it.
```

---

## What This Skill Never Does

- Invents facts not present in scrape, search, or interview responses.
- Fills `[UNKNOWN]` fields with plausible-sounding guesses.
- Treats `[H]` (hypothesis) facts as validated in output.
- Writes to files the user did not select in Phase 1.
- Runs more than 10 interview questions in Phase 8.
- Writes outside CWD or creates directories.
- Re-runs on a repo where all 4 files are ≥ 90% — tell the user to use the
  enrichment or update skill instead.
- Fetches rank data, backlink data, or any data that requires DataForSEO,
  Ahrefs, or Screaming Frog. Those are separate skills.
- Infers competitors without user confirmation.
- Rewrites the `description` field in `company.md` for clarity or brand voice.
  User's words are preserved verbatim.
