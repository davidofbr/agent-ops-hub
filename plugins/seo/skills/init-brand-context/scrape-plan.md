# Scrape plan

Rules for fetching the client site in Phase 3 of `init-brand-context`. Covers
URL discovery, the candidate list for common pages, and field extraction
mappings for every output file.

`web_fetch` is the only allowed fetcher. Cap Phase 3 at **8 total calls**.
Cap Phase 6 at 4 pages per competitor and 5 competitors total (20 calls).

---

## Section 1 — URL discovery order

1. **Root URL.** Always fetch first. This is the `web_fetch` input the user
   gave. From the root, harvest:
   - `<html lang>` attribute → language candidate
   - `<meta name="description">` → description candidate
   - `<meta property="og:site_name">` → name candidate
   - All same-domain anchor hrefs → URL candidate set
   - Links to `sitemap.xml`, `robots.txt`

2. **Sitemap.** If the root HTML, a `<link rel="sitemap">`, or `robots.txt`
   points to a sitemap, fetch `sitemap.xml` next. Prioritize URLs from the
   sitemap that match the candidate patterns below. If the sitemap is large
   (>500 URLs) only pick the top match per candidate category.

3. **Candidate patterns.** Walk this list in order, stop at first match per
   category. Try both German and English variants on DACH sites.

   | Category   | Candidate slugs                                                          |
   |------------|--------------------------------------------------------------------------|
   | about      | `/about`, `/about-us`, `/company`, `/ueber-uns`, `/ueber`, `/about/company` |
   | pricing    | `/pricing`, `/preise`, `/kosten`, `/tarife`, `/plans`                    |
   | products   | `/products`, `/product`, `/produkte`, `/solutions`, `/loesungen`         |
   | customers  | `/customers`, `/cases`, `/case-studies`, `/kunden`, `/referenzen`, `/projekte` |
   | team       | `/team`, `/leadership`, `/people`, `/ueber-uns/team`                     |
   | imprint    | `/impressum`, `/imprint`, `/legal`, `/rechtliches`                       |
   | contact    | `/contact`, `/kontakt`                                                   |

4. **Budget enforcement.** Cap is 8 calls. Priority order when cap is tight:
   root → imprint (legal validation) → about → pricing → products → customers →
   team → contact. Skip lower-priority categories if cap is hit.

5. **Failure handling.** A 404 or non-200 response burns one of the 8 calls.
   Do not retry with a different slug in the same category — move to the next
   category. Domain not resolving: stop the skill, report to user.

---

## Section 2 — Field extraction map

Per field, where it comes from, confidence tag applied.

### For `company.md`

| Field         | Primary source                                      | Fallback                                  | Tag |
|---------------|-----------------------------------------------------|-------------------------------------------|-----|
| `name`        | Impressum legal name                                | `og:site_name` → homepage `<title>` → user | `[V]` if impressum, else `[I]` |
| `domain`      | User-provided URL, normalized                       | —                                         | `[V]` |
| `market`      | Impressum jurisdiction (country of registration)    | `<html lang>` region → geo mentions → user | `[V]` if impressum, else `[I]` |
| `language`    | `<html lang>` attribute                             | Dominant content language detection → user | `[V]` |
| `description` | Homepage hero copy (first h1/h2 + nearest paragraph) | `<meta name="description">` → user        | `[I]` always |

### For `competitors.json`

Filled in Phase 6, one object per confirmed competitor.

| Field                    | Source                                                                 |
|--------------------------|------------------------------------------------------------------------|
| `name`                   | Competitor homepage `<title>` or brand element                         |
| `domain`                 | User-confirmed domain, normalized (strip protocol, `www.`, trailing `/`) |
| `positioning`            | Competitor hero copy, first sentence                                   |
| `products`               | List from competitor `/products` or main nav                           |
| `pricing_visible`        | `true` if `/pricing` exists and shows numeric prices; else `false`     |
| `case_studies_count`     | Count on `/cases` or `/customers` page; 0 if page absent               |
| `observable_strengths`   | Inferred list (2–4 bullets) from their copy                            |
| `observable_weaknesses`  | Inferred list (2–4 bullets) from gaps or tradeoffs in their offering   |
| `domain_rating`          | `null` always. Enrichment skill fills this later.                      |
| `backlinks`              | `null` always. Enrichment later.                                       |
| `page_count`             | `null` always. Enrichment later.                                       |
| `source_urls`            | All URLs fetched for this competitor                                   |
| `confidence`             | 0–1.0 score based on how many fields populated                         |
| `provenance`             | String: "[I] inferred from scrape of [URL list]"                       |

### For `icp.md`

| Field                   | Source                                                                         |
|-------------------------|--------------------------------------------------------------------------------|
| Firmographics           | Who-is-it-for copy, industries page, case study customer names                 |
| Situational triggers    | Pain-point language in copy ("if you're struggling with X, we help…")          |
| Must-haves              | Table-stakes claims on product pages ("our platform requires…")                |
| Disqualifiers           | Interview only. Marketing copy rarely states this. Flag `[UNKNOWN]` if no interview answer. |
| Current solutions       | "Switching from X" or "replace Y" language + competitor comparison tables     |
| Decision process        | Sales funnel signals: demo request vs. self-serve vs. contact-sales-only       |

### For `personas.md`

| Field                | Source                                                                     |
|----------------------|----------------------------------------------------------------------------|
| Identity (role)      | Direct mentions in copy ("for CMOs", "for DevOps leads", "built for engineers") |
| Background           | Interview only. Flag `[UNKNOWN]` if no answer.                             |
| Jobs-to-be-done      | Hero benefit copy mapped to outcomes                                       |
| Pain points          | Explicit "do you struggle with" language + competitor comparison framing   |
| Search behavior      | Interview only. Do not guess.                                              |
| Language/vocabulary  | Direct phrases extracted from testimonials and case study quotes           |
| Decision criteria    | Feature comparison tables, "why us" pages                                  |
| Objections           | FAQ page + "myth vs. fact" sections                                        |
| Voice/tone notes     | Inferred from testimonial tone (formal/informal, technical/executive)      |

---

## Section 3 — Extraction rules

1. **Prefer structured data.** JSON-LD, microdata, Open Graph tags are
   higher-signal than free-flowing copy. Parse them first.

2. **Legal name wins on conflict.** If Impressum says "Acme GmbH" and
   homepage says "Acme", use `Acme GmbH` for `name`. If the user overrides
   during Phase 8 interview, use the user's answer.

3. **Country from Impressum is authoritative for `market`.** A German
   Impressum with "Sitz in München" is a hard `DE` signal. Override only
   on explicit user input ("we target US primarily, EU registration is
   incidental").

4. **Do not rewrite copy.** `description` is the user's words (or the
   site's hero copy), not a marketing-optimized summary. Trim whitespace,
   that's it.

5. **Testimonials are `[I]`.** They may be real or cherry-picked. Never
   elevate a testimonial to `[V]`.

6. **Case study customer names are `[V]`** only if they are named companies
   with logos or links. "A leading Fortune 500 company" is `[H]`.

7. **Never infer across languages.** If the site is in German and a
   product page is in English, flag that inconsistency in the consistency
   dimension score.

8. **Strip tracking params and hash fragments** from all `source_urls`
   recorded. Canonical URL only.

---

## Section 4 — Output summary after Phase 3

After scraping, report a single line to the user:

> Scraped acme.example: root ✓ | imprint ✓ | about ✓ | pricing ✗ | products ✓
> | customers ✓ | team ✗ | contact ✓. 7 URLs, 1 404.

Do not dump extracted content yet. That surfaces in Phase 9 file generation
or in Phase 8 interview clarifications when needed.
