# Competitor discovery

Rules for suggesting up to 5 candidate competitors via `web_search` in
Phase 5 of `init-brand-context`. Output is a candidate list the user
confirms, edits, or rejects before Phase 6 scraping runs.

The skill does not decide competitors. It proposes. User confirms.

---

## Section 1 — Signal detection

Pick the query pattern based on signals observed during Phase 3 scrape
of the client site. Check signals in this order; first match wins.

### Pattern A — SaaS / subscription

Signals (need ≥ 2):
- `/pricing` page present with monthly/yearly numeric tiers
- Homepage contains words like "free trial", "sign up", "get started"
- Copy language is English-dominant
- Product is digital (no physical shipping copy, no manufacturing language)

### Pattern B — DACH industrial B2B (David's most common case)

Signals (need ≥ 2):
- `/impressum` with German legal entity (GmbH, UG, AG)
- Product copy references physical manufacturing terms ("Fertigung",
  "Hersteller", "Maschinenbau", specific ISO norms, sizes, materials)
- `<html lang>` is `de`
- No public pricing page, or pricing on request only

### Pattern C — Services / consulting / agency

Signals (need ≥ 2):
- Team page present with headshots and bios
- Copy describes "we help", "we work with", "our clients" in service-delivery framing
- No product pages, or products are consulting packages
- Case studies center on outcomes delivered to named clients

### Pattern D — Fallback

Used when signals are ambiguous or the scrape failed to load enough pages
to detect a pattern. Runs the generic queries only.

---

## Section 2 — Query templates

Each pattern has 2–3 template queries. Run all templates in the pattern
concurrently (separate `web_search` calls), then merge and deduplicate
candidates.

### Pattern A — SaaS / subscription

```
1. "[brand] alternatives"
2. "best [category] software [year]"
3. "[brand] vs"
```

Replace `[brand]` with the company name from Phase 4 extraction.
Replace `[category]` with the primary product category extracted from
`/products` or hero copy.
Replace `[year]` with the current year (e.g. `2026`).

### Pattern B — DACH industrial B2B

```
1. "[category] Hersteller Deutschland"
2. "[brand] Konkurrenz"
3. "[category] Anbieter Vergleich"
```

If the client operates in Austria or Switzerland specifically (from
`market` extraction), swap `Deutschland` for the correct country name
(`Österreich`, `Schweiz`).

### Pattern C — Services / consulting / agency

```
1. "[category] agency [city or country]"
2. "best [category] services [year]"
3. "[brand] competitors"
```

`[city]` comes from Impressum address. If no city, use market.

### Pattern D — Fallback

```
1. "[brand] alternatives"
2. "[brand] vs"
```

Generic. Works but noisy.

---

## Section 3 — Filtering rules

Apply to all search results before presenting candidates to the user.

1. **Exclude the client domain itself.** Even if it ranks for its own
   brand alternatives query.

2. **Exclude aggregator / review-farm domains** unless they ARE the
   subject of the query. Exclusion list:
   - `g2.com`, `capterra.com`, `gartner.com`, `trustpilot.com`
   - `getapp.com`, `softwareadvice.com`, `crozdesk.com`
   - `quora.com`, `reddit.com`, `medium.com`
   - Wikipedia, YouTube, LinkedIn unless the LinkedIn result is a
     competitor's company page

3. **Exclude the client's own parent or subsidiary domains.** If
   `acme.example` returns `acme-group.example` or `acme.de`, and both
   are clearly the same organization, skip the sibling.

4. **Exclude domains where the snippet is clearly unrelated.** If the
   search for "cleanroom Hersteller" returns a cleaning services
   company, skip it. Use common sense; err toward exclusion when
   unsure — it is better to surface 3 tight candidates than 5 with
   two wrong.

5. **Deduplicate by domain.** Multiple search results on the same
   domain count as one candidate.

6. **Rank by relevance.** Prefer candidates that appear in multiple
   query results, candidates with clear positioning in their snippet,
   candidates on TLDs that match the client's market.

---

## Section 4 — Candidate presentation

Present up to 5 candidates to the user as a multi-select, plus a
free-form add slot. Each candidate shows:

```
[domain]
[one-line positioning from search snippet]
[signal count: "appeared in 2 of 3 queries"]
```

Ask: "Which of these are actual competitors? Add any I missed."

Accept the user's edits without re-ranking. If the user adds a domain,
validate with a single `web_fetch` to the root before adding to the
scrape queue (make sure the domain resolves and is not a parking page).

If the user selects zero candidates and adds none, skip Phase 6 entirely.
`competitors.json` is written with an empty `competitors` array and a
note in `_meta.unknown_fields_note`.

---

## Section 5 — Budget

Total `web_search` calls for Phase 5 capped at:
- 3 template queries × 1 call each = 3 calls for the chosen pattern
- +1 optional validation fetch per user-added domain

If results from the 3 template queries yield fewer than 3 unique
candidates after filtering, run one additional fallback query from
Pattern D. Maximum 4 total `web_search` calls in Phase 5.
