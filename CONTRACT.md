> Every skill in this hub operates against a shared contract: a specific set of files and environment variables that live in the project you invoke Claude from (the "client repo"). Meet the contract and the skills run cleanly.

# Contract

## Client repo layout

Run skills from the root of a dedicated directory for each company or client you work with. This is where brand context, credentials, and skill outputs live.

```
<client-repo>/
├── .env                 # API credentials (gitignored)
├── company.md           # company name, primary URL, positioning, one-liner
├── competitors.json     # structured competitor set
├── icp.md               # ideal customer profile, segment targeting
├── personas.md          # buyer archetypes
└── output/              # everything skills write (gitignored by convention)
    ├── serp/
    ├── pages/
    ├── dissection/
    ├── aeo/
    └── final/
```

## Brand context files

Four markdown/JSON files at the root of the client repo describe the company whose work is being done. They are the single source of truth for name, URL, positioning, audience, and competitive set. Every content-oriented skill in this hub reads from them.

| File | Purpose |
|---|---|
| `company.md` | Company name, primary URL, positioning, one-line description |
| `competitors.json` | Up to five competitors with structured metadata |
| `icp.md` | Segment-level targeting: who the company sells to |
| `personas.md` | Buyer archetypes for later agent embodiment |

### Bootstrapping these files

Run `init-brand-context` once per client repo, pointed at the primary URL. It scrapes the site, runs corroboration searches, scores confidence per file, and interviews you to close the highest-impact gaps. Output lands at the repo root.

## Environment variables

Stored in `<client-repo>/.env` (gitignored) or exported in your shell. Scripts read the shell environment first and fall back to `.env`.

| Variable | Required by | Notes |
|---|---|---|
| `DATAFORSEO_LOGIN` | `serp-analyzer` | Basic-auth login from [app.dataforseo.com/api-access](https://app.dataforseo.com/api-access) |
| `DATAFORSEO_PASSWORD` | `serp-analyzer` | API password (not your account password) |
| `JINA_API_KEY` | `serp-analyzer` (optional) | Loosens `r.jina.ai` rate limits on the free tier |

Missing credentials fail fast with a clear error. Secrets never live inside the hub itself; only the client repo holds them.

## Output directory

Skills write under `<client-repo>/output/<skill-topic>/` and never touch the hub's skill folders. The `output/` tree is gitignored in the client repo by convention.

## Skill matrix

| Skill | Reads | Writes |
|---|---|---|
| `init-brand-context` | primary URL from user | `company.md`, `competitors.json`, `icp.md`, `personas.md` |
| `serp-analyzer` | keyword from user | `output/serp/`, `output/pages/`, `output/dissection/`, `output/aeo/`, `output/final/` |

Skills shipped later will read from `company.md`, `icp.md`, and `personas.md` as their source of brand context. Run `init-brand-context` first on any new client repo.
