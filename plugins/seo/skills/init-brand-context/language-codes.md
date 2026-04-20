# Language codes

ISO 639-1 two-letter language codes for the `language` field of `company.md`.
Use this table to convert free-form user input (language names, common
translations, abbreviations) to the two-letter code.

If the user names a language not listed here, look it up on the canonical
ISO 639-1 registry and use the code — do not reject a valid language just
because it is not in this table.

---

## Common content languages

| Free-form input (accepted) | Code |
|---|---|
| German, Deutsch, DE | `de` |
| English, Englisch, EN | `en` |
| French, Français, Französisch, FR | `fr` |
| Italian, Italiano, Italienisch, IT | `it` |
| Spanish, Español, Spanisch, ES | `es` |
| Dutch, Nederlands, Niederländisch, NL | `nl` |
| Portuguese, Português, Portugiesisch, PT | `pt` |
| Polish, Polski, Polnisch, PL | `pl` |
| Czech, Čeština, Tschechisch, CS | `cs` |
| Danish, Dansk, Dänisch, DA | `da` |
| Swedish, Svenska, Schwedisch, SV | `sv` |
| Norwegian, Norsk, Norwegisch, NO | `no` |
| Finnish, Suomi, Finnisch, FI | `fi` |
| Japanese, 日本語, JA | `ja` |
| Korean, 한국어, KO | `ko` |
| Chinese (simplified), 中文, ZH | `zh` |

---

## Ambiguity

Some inputs are ambiguous. Ask the user to clarify instead of guessing.

| Ambiguous input | Why | Ask |
|---|---|---|
| Swiss | Switzerland has four official languages (`de`, `fr`, `it`, `rm`) | Which language specifically — German, French, Italian, Romansh? |
| Belgian | Belgium has three (`nl`, `fr`, `de`) | Which language — Dutch, French, or German? |
| Chinese | Simplified vs Traditional encoded differently | Simplified (`zh`) or Traditional (use `zh-TW` if needed — but then the user should be using a non-ISO-639-1 extension, flag this) |

ISO 639-1 does not distinguish Simplified vs Traditional Chinese at the
two-letter level. If the distinction matters for a downstream skill, it will
need its own locale handling — for `company.md`, `zh` is acceptable and
callers decide.

---

## Normalization rules

1. **Case-insensitive match.** Compare lowercased input against the accepted names.
2. **Trim whitespace and punctuation.** `"German."` → `German`.
3. **Exact match only.** Do not fuzzy-match.
4. **Return lowercase alpha-2.** `de`, not `DE` or `deu`.
5. **Do not accept locale codes.** If the user types `de-DE`, `en-US`, ask them
   for just the language (`de`, `en`). Locale is split across `market` and
   `language` in `company.md` by design — do not let it re-combine here.
