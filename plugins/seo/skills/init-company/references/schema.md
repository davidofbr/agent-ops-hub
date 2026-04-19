# `company.md` schema

The canonical contract for the brand-level context file at the root of every repo
where this hub is installed. Every skill in this marketplace reads `company.md`
and treats these five fields as a hard contract.

---

## Location

`<repo-root>/company.md`

Always at the root. Not inside `.claude/`, not inside a skill folder, not in a
subdirectory. Consuming skills look at `./company.md` relative to the CWD where
they are invoked.

---

## Format

YAML frontmatter only. No body, no comments inside the frontmatter block.

```yaml
---
name: <string>
domain: <string>
market: <string>
language: <string>
description: <string>
---
```

Exactly five keys. No extras. No optional fields. If a sixth field is ever needed,
bump the schema — don't silently grow it.

---

## Fields

### `name`

- **Type:** string
- **Format:** verbatim, as the company writes itself
- **Rule:** preserve case, punctuation, and internal spacing. `Acme GmbH`, `acme`,
  `ACME International` are all valid — whichever the company uses.

### `domain`

- **Type:** string
- **Format:** bare hostname, lowercased
- **Rule:** no protocol, no `www.`, no trailing slash, no path. One domain only —
  the canonical/primary one. If the brand operates multiple TLDs (`.de`, `.com`),
  pick the one that is canonical for search/SEO purposes.
- **Examples:**
  - Valid: `acme.example`, `sub.acme.example`
  - Invalid: `https://acme.example`, `www.acme.example`, `acme.example/`, `acme.example/en`

### `market`

- **Type:** string
- **Format:** ISO 3166-1 alpha-2 country code, uppercase
- **Rule:** two-letter code. Scalar, not a list. If the company operates across
  multiple markets, pick the single primary one for search/SEO purposes.
- **Examples:** `DE`, `AT`, `CH`, `US`, `GB`, `FR`, `IT`, `NL`, `SG`
- **Downstream use:** maps to DataForSEO `location_code` / `location_name`,
  Serper `gl`, Google Ads geo targets.

### `language`

- **Type:** string
- **Format:** ISO 639-1 language code, lowercase
- **Rule:** two-letter code. The language the company publishes content in. For
  bilingual brands, pick the primary content language.
- **Examples:** `de`, `en`, `fr`, `it`, `nl`
- **Downstream use:** maps to DataForSEO `language_code`, Serper `hl`,
  content-generation locale.

### `description`

- **Type:** string
- **Format:** one or two sentences, plain prose
- **Rule:** what the company does, for whom. Kept tight so LLMs can ground
  themselves quickly. No marketing fluff. No multi-paragraph brand story — that
  belongs in a separate file.
- **Length guidance:** ~15–60 words. Longer is not better.

---

## Stability

Values are meant to be stable. Editing `company.md` describes a rebrand, a market
pivot, or a domain migration — not a campaign, a new product launch, or a
quarterly priority shift.

If a skill needs context that changes more than once a year, it does not belong
in `company.md`.

---

## Validation (for future consumer skills)

A skill reading `company.md` should:

1. Resolve `./company.md` relative to CWD.
2. Fail fast with a clear message if the file does not exist — point the user
   at the `init-company` skill.
3. Parse YAML frontmatter.
4. Check all five keys are present and non-empty. Fail fast on any violation.
5. Validate `market` against ISO 3166-1 alpha-2 and `language` against ISO 639-1.
   Reject values that don't match the format (e.g. `Germany`, `de-DE`, `DEU`).
6. Trust the values. No re-normalization of `domain`, no rewrite of `description`.
