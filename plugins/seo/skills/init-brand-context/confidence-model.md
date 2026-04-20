# Confidence Model — init-brand-context

Scoring rubrics for the four output files. Adapted from the
`initialize-client-repo` confidence model with identical dimension weights
and the same ceiling rule for source diversity. The per-file rubrics
diverge because this skill produces a different file set and relies on
scrape-first data collection.

---

## Dimension Weights

| Dimension          | Weight | What it measures |
|--------------------|--------|------------------|
| Essential coverage | 35%    | Structural essentials filled |
| Source diversity   | 25%    | Right-weighted sources contributed |
| Data grounding     | 20%    | Data-dependent sections backed by actual data |
| Consistency        | 10%    | Sources agree; tensions flagged |
| Recency            | 10%    | Sources are fresh |

---

## Source Type Weights

| Source Type                                      | Weight | Tag          |
|--------------------------------------------------|--------|--------------|
| User interview response during this session      | 1.0    | CLIENT_VOICE |
| Pasted hand-off intel from Phase 2               | 1.0    | CLIENT_VOICE |
| Customer review or press mention (web_search)    | 0.60   | REVIEW       |
| Industry comparison page (web_search)            | 0.50   | COMPARISON   |
| Client site scrape (marketing copy)              | 0.45   | STRUCTURAL   |
| Competitor site scrape                           | 0.45   | STRUCTURAL   |
| Sitemap XML                                      | 0.25   | STRUCTURAL   |
| Blank / no inputs                                | 0.0    | —            |

**Scoring approach for Source diversity dimension:**
- 0 sources → 0
- 1 STRUCTURAL source only → max 40
- 1 STRUCTURAL + 1 REVIEW or COMPARISON → max 55
- 2+ STRUCTURAL sources only → max 60
- Any CLIENT_VOICE source + ≥1 STRUCTURAL → 75–90
- CLIENT_VOICE + REVIEW + STRUCTURAL (3 types) → 90–100

**Ceiling rule:** No CLIENT_VOICE source → source diversity **caps at 60%**
regardless of how many other sources are present. Interview responses and
pasted hand-off intel lift the cap. State the ceiling explicitly when it
applies in the Phase 10 summary.

---

## Per-File Rubrics

---

### `company.md`

**Essential coverage (35%):**

| Field                            | Points |
|----------------------------------|--------|
| `name` populated and non-empty   | 20     |
| `domain` populated and normalized | 20    |
| `market` valid ISO 3166-1 alpha-2 | 20    |
| `language` valid ISO 639-1        | 15    |
| `description` 15–60 words         | 25    |

Max 100. Convert to 0–100%.

**Data grounding (20%):**
- `name` sourced from Impressum (legal entity): +10
- `market` sourced from Impressum jurisdiction: +5
- `language` sourced from `<html lang>`: +3
- `description` sourced from homepage meta or h1+paragraph: +2

If any field is user-provided rather than scraped, that field contributes
full credit for grounding (interview is ground truth).

**Consistency (10%):**
- No contradictions between Impressum and homepage copy: 100
- `<html lang>` conflicts with product page language: 60
- Multiple legal names across pages: 40

**Recency (10%):**
- Always 100 on fresh scrape.

---

### `competitors.json`

**Essential coverage (35%):**

| Field                                                       | Points |
|-------------------------------------------------------------|--------|
| At least 2 competitors present in the array                 | 10     |
| Each competitor has `name` + `domain` + `positioning`       | 20     |
| Each competitor has `observable_strengths` (≥ 2 bullets)    | 15     |
| Each competitor has `observable_weaknesses` (≥ 2 bullets)   | 15     |
| Each competitor has `products` non-empty                    | 15     |
| Each competitor has `source_urls` (≥ 1)                     | 25     |

Per-competitor score averaged across the array to yield the file essential score.

**Data grounding (20%):**
This is the dimension explicitly designed to score LOW at init time. That
is intentional — `domain_rating`, `backlinks`, `page_count` are all null
until enrichment.

- `pricing_visible` boolean set (not assumed): +5
- `case_studies_count` integer set (not zero-by-default): +5
- `domain_rating` populated (will be null at init): +8 (available to enrichment)
- `backlinks` populated (null at init): +2 (available to enrichment)

Expect 10/20 at init, rising to 20/20 post-enrichment. State this in summary.

**Consistency (10%):**
- Each competitor's positioning stable across their scraped pages: 100
- Pricing visible on one page but contradicted on another: 60
- Product list contradicts positioning statement: 40

**Recency (10%):**
- Always 100 on fresh scrape.

---

### `icp.md`

**Essential coverage (35%):**

| Field                                | Points |
|--------------------------------------|--------|
| Firmographics (≥ 3 of 5 sub-fields)  | 20     |
| Situational triggers (≥ 2)           | 15     |
| Must-haves (≥ 2)                     | 15     |
| Disqualifiers (≥ 1 or marked UNKNOWN)| 15     |
| Current solutions (≥ 2)              | 15     |
| Decision process (≥ 2 of 4 sub-fields)| 20    |

**Data grounding (20%):**
- Named customer examples in scrape: +10
- Explicit decision-maker role stated in copy: +5
- Explicit sales motion signal (demo vs self-serve vs enterprise): +5

**Consistency (10%):**
- ICP description consistent across product pages: 100
- Different industries named across pages without hierarchy: 60
- Contradictory target-market claims: 30 + flag

**Recency (10%):**
- Scrape-based fields: 100
- Interview-based fields: 100

---

### `personas.md`

**Essential coverage (35%):**

| Field                                         | Points |
|-----------------------------------------------|--------|
| ≥ 2 personas populated (or 1 + placeholder)   | 10     |
| Each persona: Identity complete (4/4 fields)  | 15     |
| Each persona: JTBD (primary + 1 more)         | 15     |
| Each persona: Pains (≥ 2)                     | 15     |
| Each persona: Language & vocabulary (≥ 2 quotes) | 15  |
| Each persona: Objections (≥ 1)                | 10     |
| Each persona: Voice/tone notes (≥ 3 of 5 sub-fields) | 20 |

Averaged across the persona count.

**Data grounding (20%):**
- Actual quotes in Language & vocabulary (`[V]` tagged): +10
- Named roles/titles from case studies: +5
- Search behavior explicitly stated (not guessed): +5

**Consistency (10%):**
- Persona description consistent across product pages: 100
- Different implied personas across pages without hierarchy: 60

**Recency (10%):**
- Scrape: 100
- Interview: 100

**Expected confidence cap:** Without call transcripts or win/loss interviews,
the source diversity dimension caps at 60% per the ceiling rule above. Even
with a full interview in Phase 8 (which lifts the cap), personas inferred
primarily from marketing copy typically land in the 60–75% range at init.
State this honestly in the Phase 10 summary.

---

## Confidence Thresholds

| Score    | Status     | Header label   |
|----------|------------|----------------|
| ≥ 90%    | COMPLETE   | ✓ Ready        |
| 70–89%   | PARTIAL    | ⚠ Partial      |
| < 70%    | INCOMPLETE | ✗ Incomplete   |

Files are generated at any score. Threshold affects the header label and
whether the interview loop continues. Hard interview cap is 10 questions
regardless of thresholds.

---

## Computation

Weighted total per file:

```
total = (essential × 0.35) + (sources × 0.25) + (data × 0.20)
      + (consistency × 0.10) + (recency × 0.10)
```

Round to nearest integer. Recompute after every interview answer that
affects the file.
