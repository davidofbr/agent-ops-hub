# Locale Defaults

The agency serves German B2B clients. Default locale is German.
Override only when the user explicitly says so.

## Default

```json
{
  "location_code": 2276,
  "language_code": "de",
  "device": "desktop"
}
```

## Why this matters

Google returns wildly different SERPs depending on `location_code` and
`language_code`. If you run a German B2B keyword with `location_code=2840`
(United States), you get:
- US competitors that don't matter to the client
- English-language AI Overview
- English PAA questions
- Entirely different ranking pages

The analysis is not "mostly right" — it's wrong. Discard and re-run.

## Common DACH + Europe codes

| Market              | location_code | language_code |
|---------------------|---------------|---------------|
| Germany (default)   | 2276          | de            |
| Austria             | 2040          | de            |
| Switzerland (DE)    | 2756          | de            |
| Switzerland (FR)    | 2756          | fr            |
| Switzerland (IT)    | 2756          | it            |
| Netherlands         | 2528          | nl            |
| United Kingdom      | 2826          | en            |
| United States       | 2840          | en            |
| Singapore           | 2702          | en            |

For city-level targeting, DataForSEO exposes city-scoped location codes
(e.g. 1004074 for Hamburg). Query `/v3/serp/google/locations` for the
full list, or `/v3/serp/google/locations/{country_iso_code}` to scope
the lookup.

## Device

Defaults to `desktop`. Pass `mobile` only when the client explicitly
needs mobile-first data. For most B2B buyer research, desktop is right.

## When to ask the user

Always confirm locale when:
- The keyword is in a language that doesn't match the default (e.g. the
  user drops an English keyword but the default is German)
- The keyword explicitly contains a geography ("SEO München" is obvious,
  "marketing automation" is not)
- The client is known to be multi-market

Do not ask when:
- The user already specified locale in the request
- The keyword is unambiguously in German and no other signal suggests
  otherwise
