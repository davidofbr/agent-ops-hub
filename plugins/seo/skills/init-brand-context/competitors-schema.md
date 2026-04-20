# `competitors.json` schema

Structured artifact listing up to 5 competitors discovered and scraped
during `init-brand-context` Phases 5–6. Designed as the enrichable
source of truth: this skill fills qualitative fields; later enrichment
skills fill quant fields (DR, backlinks, page_count) when Ahrefs and
Screaming Frog data is available.

---

## Location

`<repo-root>/competitors.json`

One file. Root level. Same directory as `company.md`.

---

## Format

Valid JSON. UTF-8. Indented with 2 spaces for human readability.

```json
{
  "_meta": {
    "generated_at": "<ISO 8601 UTC timestamp>",
    "source_company_domain": "<bare hostname>",
    "confidence": "<0-100 integer>",
    "essential": "<0-100 integer>",
    "sources": "<0-100 integer>",
    "data": "<0-100 integer>",
    "consistency": "<0-100 integer>",
    "recency": "<0-100 integer>",
    "status": "COMPLETE | PARTIAL | INCOMPLETE",
    "skill": "init-brand-context",
    "discovery_method": "web_search_suggested_user_confirmed | user_provided_only | skipped_no_candidates",
    "unknown_fields_note": "<string describing what enrichment adds>"
  },
  "competitors": [
    {
      "name": "<string>",
      "domain": "<bare hostname>",
      "positioning": "<one sentence>",
      "products": ["<string>", "..."],
      "pricing_visible": true,
      "case_studies_count": 8,
      "observable_strengths": ["<string>", "..."],
      "observable_weaknesses": ["<string>", "..."],
      "domain_rating": null,
      "backlinks": null,
      "page_count": null,
      "source_urls": ["<url>", "..."],
      "confidence": 0.7,
      "provenance": "[I] inferred from scrape of homepage + about + pricing"
    }
  ]
}
```

---

## Field contracts

### `_meta` object

| Field                   | Type           | Required | Rule                                                     |
|-------------------------|----------------|----------|----------------------------------------------------------|
| `generated_at`          | ISO 8601 UTC   | yes      | Timestamp of skill run                                   |
| `source_company_domain` | string         | yes      | Matches `domain` in `company.md`                         |
| `confidence`            | integer 0–100  | yes      | Weighted score per `confidence-model.md`                 |
| `essential`             | integer 0–100  | yes      | Per confidence-model rubric for competitors.json         |
| `sources`               | integer 0–100  | yes      | Source diversity, subject to ceiling rule                |
| `data`                  | integer 0–100  | yes      | Data grounding (will be low until enrichment fills nulls)|
| `consistency`           | integer 0–100  | yes      | Positioning consistency across competitor source pages   |
| `recency`               | integer 0–100  | yes      | Always 100 on fresh scrape                               |
| `status`                | enum           | yes      | `COMPLETE` (≥90), `PARTIAL` (70–89), `INCOMPLETE` (<70)  |
| `skill`                 | string         | yes      | Always `init-brand-context` for files this skill writes  |
| `discovery_method`      | enum           | yes      | One of the three values above                            |
| `unknown_fields_note`   | string         | yes      | What the enrichment skill fills in later                 |

### `competitors` array

Zero to five objects. Zero is valid (if user rejected all candidates).

### Per-competitor object

| Field                   | Type                     | Nullable | Rule                                               |
|-------------------------|--------------------------|----------|----------------------------------------------------|
| `name`                  | string                   | no       | From competitor homepage                           |
| `domain`                | string                   | no       | Bare hostname, lowercased, no protocol or www.     |
| `positioning`           | string                   | no       | One sentence from hero                             |
| `products`              | array of strings         | no       | `[]` if none found on site                         |
| `pricing_visible`       | boolean                  | no       | `true` iff `/pricing` page has numeric prices      |
| `case_studies_count`    | integer                  | no       | `0` if no case-study page                          |
| `observable_strengths`  | array of strings         | no       | 2–4 bullets, `[]` if insufficient copy             |
| `observable_weaknesses` | array of strings         | no       | 2–4 bullets, `[]` if insufficient copy             |
| `domain_rating`         | integer 0–100 or null    | **yes**  | `null` at init. Enrichment fills.                  |
| `backlinks`             | integer or null          | **yes**  | `null` at init. Enrichment fills.                  |
| `page_count`            | integer or null          | **yes**  | `null` at init. Enrichment fills.                  |
| `source_urls`           | array of strings         | no       | Every URL fetched for this competitor              |
| `confidence`            | float 0.0–1.0            | no       | Per-competitor confidence, rounded to 2 decimals   |
| `provenance`            | string                   | no       | Provenance tag with source description             |

---

## Null-safety rules

1. **`null` means "not available at init time".** Downstream consumers
   MUST check for `null` before using `domain_rating`, `backlinks`,
   `page_count`. They must not throw on missing data; they must
   skip or defer.

2. **Never omit a nullable field.** The key must be present with value
   `null`. This keeps the schema stable across enrichment cycles.

3. **Arrays are never null.** Empty `[]` means "checked, nothing found".
   Null here would be ambiguous.

4. **Strings are never empty.** Either a non-empty value or the field
   is absent (only allowed for nullable fields above — and those must
   be nullable integer, not string).

---

## Example — real output

```json
{
  "_meta": {
    "generated_at": "2026-04-20T10:15:00Z",
    "source_company_domain": "acme.example",
    "confidence": 58,
    "essential": 72,
    "sources": 45,
    "data": 35,
    "consistency": 80,
    "recency": 100,
    "status": "INCOMPLETE",
    "skill": "init-brand-context",
    "discovery_method": "web_search_suggested_user_confirmed",
    "unknown_fields_note": "DR, backlinks, and page_count require Ahrefs and Screaming Frog enrichment. Run enrichment skill after this init."
  },
  "competitors": [
    {
      "name": "Schilling Engineering",
      "domain": "schillingengineering.de",
      "positioning": "Premium modular cleanroom solutions, brand-led positioning with GMP compliance coverage.",
      "products": ["Reinraumzelte", "Reinraumkabinen", "Sauberräume"],
      "pricing_visible": false,
      "case_studies_count": 40,
      "observable_strengths": [
        "Deep content depth on GMP and certification topics",
        "Large volume of named case studies",
        "Active Google Ads presence on core commercial terms"
      ],
      "observable_weaknesses": [
        "No pricing transparency",
        "No installation service visible in product copy"
      ],
      "domain_rating": null,
      "backlinks": null,
      "page_count": null,
      "source_urls": [
        "https://schillingengineering.de/",
        "https://schillingengineering.de/unternehmen",
        "https://schillingengineering.de/referenzen"
      ],
      "confidence": 0.72,
      "provenance": "[I] inferred from scrape of homepage + company + references"
    }
  ]
}
```

---

## Validation for consumer skills

A skill reading `competitors.json`:

1. Resolves `./competitors.json` relative to CWD.
2. Parses as JSON. Fails fast on invalid JSON.
3. Validates `_meta` contains all required keys above.
4. Treats `competitors[].domain_rating | backlinks | page_count` as
   possibly null. Skips or defers behavior when null.
5. Does not re-normalize domains or re-compute confidences. Trust
   the values at init time.
6. Uses `_meta.discovery_method` to decide whether to prompt the user
   for more competitors before running (e.g. enrichment skills might
   refuse to run on an `INCOMPLETE` file).
