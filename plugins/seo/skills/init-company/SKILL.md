---
name: init-company
description: Scaffolds the `company.md` context file at the root of a repo where this hub is installed. Every other skill in this marketplace reads `company.md` for brand-level facts (name, domain, market, language, description) — run this skill first, once per repo. Ask the user plain-language questions, normalize free-form answers into API-safe values (ISO 3166-1 alpha-2 for market, ISO 639-1 for language, bare-hostname for domain), preview the assembled file, then write. Trigger on "initialize this repo", "set up company context", "scaffold company.md", or when any other skill fails because `company.md` is missing at CWD.
---

# init-company

Read `${CLAUDE_SKILL_DIR}/references/schema.md`, `${CLAUDE_SKILL_DIR}/references/market-codes.md`,
and `${CLAUDE_SKILL_DIR}/references/language-codes.md` before running. The schema is the
contract every downstream skill validates against. The code tables are the free-form → API-safe
maps used in normalization.

---

## What this skill does

Produces a single file at `<cwd>/company.md` containing stable, brand-level facts that every
other skill in the hub reads at startup. Keep this file lean and correct — it is not a
campaign brief, a persona sheet, or a brand voice reference. Those belong in separate files.

Written values are API-safe: downstream skills feed `market` straight into DataForSEO
`location_code` lookups, `language` into `language_code`, `domain` into crawler/audit inputs.
No downstream skill should re-parse or re-normalize fields from this file.

---

## Root-directory contract

Runs relative to the directory it is invoked from (CWD). The CWD is the **client repo**, not
the hub. Writes exactly one file:

```
<cwd>/company.md
```

No other files created, no directories created, no edits to anything else.

`${CLAUDE_SKILL_DIR}` is used only to locate the reference files in this skill.

---

## Workflow

Execute in order. Do not reorder. Do not skip.

### Phase 1 — Pre-check

1. Check whether `<cwd>/company.md` exists.
2. If it exists: read it, show the user the current frontmatter, and ask one question:
   "Overwrite with new values, or cancel?" — two options, no third.
   - `cancel` → stop. Do not proceed to Phase 2.
   - `overwrite` → proceed.
3. If it does not exist: proceed.

### Phase 2 — Interactive intake

Ask the following five questions **one at a time**, using the AskUserQuestion tool or plain
conversational turns. Wait for each answer before asking the next. Accept free-form text —
do not pre-filter, do not show code menus.

1. "What is the company name?"
2. "What is the primary domain?"
3. "Which market does the company primarily target? For example: Germany, Austria, Switzerland, United States."
4. "What language is the content in? For example: German, English, French."
5. "In one or two sentences, what does the company do and for whom?"

If an answer is empty, re-ask the same question. Do not invent defaults.

### Phase 3 — Normalization

Convert free-form answers to API-safe values. Do this silently, then show the result in
Phase 4.

| Input | Transformation |
|---|---|
| `name` | Keep verbatim. Preserve case, punctuation, and spacing as typed. |
| `domain` | Strip `https?://`, leading `www.`, trailing `/`. Lowercase the hostname. Example: `https://www.Acme.example/` → `acme.example`. |
| `market` | Look up the free-form answer in `references/market-codes.md`. Return the ISO 3166-1 alpha-2 code (`Germany` → `DE`). If the user named a region that spans multiple countries (e.g. `DACH`, `Benelux`, `Nordics`), ask them to pick the single primary country and map that. If the answer is not in the table, ask the user to restate with a country name. |
| `language` | Look up in `references/language-codes.md`. Return the ISO 639-1 code (`German` → `de`). If ambiguous (e.g. `Swiss`) or not in the table, ask the user to restate with a language name. |
| `description` | Whitespace-trim. Collapse internal runs of whitespace to single spaces. Do not rewrite, shorten, or "improve" the text. |

### Phase 4 — Preview and confirm

Show the user the assembled frontmatter exactly as it will be written:

```yaml
---
name: <name>
domain: <domain>
market: <market>
language: <language>
description: <description>
---
```

Ask one question: "Write this to `company.md`, or cancel?" — two options.
- `cancel` → stop. Do not write.
- `write` → proceed.

### Phase 5 — Write

Write the full content of `<cwd>/company.md`:

```
---
name: <name>
domain: <domain>
market: <market>
language: <language>
description: <description>
---
```

Single trailing newline after the closing `---`. No additional body content, no comments in
the file, no blank lines inside the frontmatter block.

Report the absolute path of the written file to the user. Stop.

---

## Rules

- Write exactly one file: `<cwd>/company.md`. Never write anywhere else.
- Never silently overwrite an existing `company.md`. Always ask in Phase 1.
- Never invent values. If the user does not know the domain, stop and tell them this skill
  cannot continue without it.
- Never rewrite the `description` for clarity or brand voice. This file is the user's words.
- Do not add schema-version fields, comments, or extra frontmatter keys. The contract is
  exactly five fields.
- Do not write agency-specific defaults (e.g. German B2B) unless the user's answer maps to them.
