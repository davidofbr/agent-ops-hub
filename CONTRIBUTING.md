# Contributing

Thanks for your interest.

## Reporting issues

Open a [GitHub issue](https://github.com/davidofbr/agent-ops-hub/issues) with:
- What you ran
- What you expected
- What happened instead
- Claude Code version (`claude --version`)

## Proposing a skill

1. Open an issue first with a short description of the skill and its trigger case
2. Wait for a thumbs-up before building — not every skill belongs in this hub
3. Submit a PR with:
   - `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` (with `name` and `description` frontmatter)
   - Any supporting files co-located in the skill directory
   - A short README section if the skill takes arguments or needs setup

## Commit convention

```
<type>: <description>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.

## What not to include

- Real client data, logs, or proprietary prompts
- API keys, tokens, or credentials
- Large binary assets (>1 MB) without prior discussion
