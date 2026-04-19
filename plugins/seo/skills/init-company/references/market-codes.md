# Market codes

ISO 3166-1 alpha-2 country codes for the `market` field of `company.md`. Use this
table to convert free-form user input (country names, common misspellings,
well-known abbreviations) to the two-letter code.

This table is intentionally scoped to the countries the hub is likely to serve
in practice. If the user names a country not listed here, look it up on the
canonical ISO 3166-1 registry and use the alpha-2 code — do not reject a valid
country just because it is not in this table.

---

## DACH + Europe

| Free-form input (accepted) | Code |
|---|---|
| Germany, Deutschland, DE | `DE` |
| Austria, Österreich, AT | `AT` |
| Switzerland, Schweiz, Suisse, Svizzera, CH | `CH` |
| France, Frankreich, FR | `FR` |
| Italy, Italia, Italien, IT | `IT` |
| Spain, España, Spanien, ES | `ES` |
| Netherlands, Nederland, Niederlande, Holland, NL | `NL` |
| Belgium, België, Belgique, Belgien, BE | `BE` |
| Luxembourg, Luxemburg, LU | `LU` |
| Denmark, Danmark, Dänemark, DK | `DK` |
| Sweden, Sverige, Schweden, SE | `SE` |
| Norway, Norge, Norwegen, NO | `NO` |
| Finland, Suomi, Finnland, FI | `FI` |
| Poland, Polska, Polen, PL | `PL` |
| Czech Republic, Czechia, Tschechien, CZ | `CZ` |
| Portugal, PT | `PT` |
| Ireland, Irland, IE | `IE` |
| United Kingdom, UK, Great Britain, Britain, England, GB | `GB` |

## Americas

| Free-form input (accepted) | Code |
|---|---|
| United States, USA, US, America | `US` |
| Canada, CA | `CA` |
| Mexico, México, MX | `MX` |
| Brazil, Brasil, BR | `BR` |

## Asia-Pacific

| Free-form input (accepted) | Code |
|---|---|
| Singapore, SG | `SG` |
| Australia, AU | `AU` |
| New Zealand, NZ | `NZ` |
| Japan, 日本, Nihon, JP | `JP` |
| South Korea, Korea, 한국, KR | `KR` |
| India, IN | `IN` |

---

## Region-to-country prompts

When the user names a multi-country region, do not guess — ask them to pick the
single primary country, then map that.

| Region | Prompt with |
|---|---|
| DACH | Germany, Austria, Switzerland |
| Benelux | Netherlands, Belgium, Luxembourg |
| Nordics | Sweden, Norway, Denmark, Finland |
| UK & Ireland | United Kingdom, Ireland |
| Iberia | Spain, Portugal |
| LATAM | Mexico, Brazil (plus named country if user specifies) |
| EU | Ask for a specific country — EU is not a market in SEO terms |

---

## Normalization rules

1. **Case-insensitive match.** Compare lowercased input against the accepted names.
2. **Trim whitespace and punctuation.** `"Germany."` → `Germany`.
3. **Exact match only.** Do not fuzzy-match across countries (`Austr` is ambiguous
   between Austria and Australia — ask the user).
4. **Return uppercase alpha-2.** `DE`, not `de` or `Deu`.
