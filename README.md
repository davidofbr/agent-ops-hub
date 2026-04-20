# agent-ops-hub

Open-source Claude Code plugins that power the SEO, AEO, and content operations we run for founder-led B2B companies.

> Status: v0.1.0. Two skills shipping today. More roll out over the coming weeks.

## What this is

A hub of plugins abstracted from the agentic systems we use internally across 30 active paying retainers. This repository contains the stripped-down, reusable versions, cleaned of brand context and rebuilt for anyone to install.

## Philosophy

Most AI tooling today routes every capability through MCP servers and general-purpose agents. We go the other way.

- **Lean context windows.** The more capabilities a model carries at once, the less sharp its answers. Every skill in this hub does one job only.
- **Deterministic where it can be.** The mechanical parts (fetching data, parsing responses, writing files) run as plain scripts. The model is only asked to do the things only a model can do: language and judgment.
- **Composable, not coupled.** Skills talk to each other through files on disk, not through shared memory. You can run one today, come back next week, and pick up where you left off.

Two things fall out of this: predictable cost and predictable quality.

## Who it's for

Operators and founders running their own SEO and AEO work on an existing website, who want to codify the pieces of that work that have stopped benefiting from a human doing them by hand.

You will need Claude Code installed and a few API keys. The full list of expectations lives in [CONTRACT.md](./CONTRACT.md).

## Skills in v0.1.0

- **init-brand-context**: scaffolds the four brand-context files (`company.md`, `competitors.json`, `icp.md`, `personas.md`) from your primary URL. Run this once per client repo.
- **serp-analyzer**: deconstructs a Google SERP for one keyword into structured intelligence a downstream AI can turn into a content brief.

Each skill lives under `plugins/seo/skills/<skill-name>/` with its own `SKILL.md`.

## Install

Clone the hub somewhere stable, then point Claude Code at it from your client repo:

```bash
git clone git@github.com:davidofbr/agent-ops-hub.git ~/agent-ops-hub
cd /path/to/your/client-repo
claude --plugin-dir ~/agent-ops-hub
```

Or reference it from the client repo's `.claude/settings.json`:

```json
{
  "plugins": [
    { "path": "/absolute/path/to/agent-ops-hub" }
  ]
}
```

## The contract

Every skill assumes a specific set of files and environment variables in the project you invoke it from. See [CONTRACT.md](./CONTRACT.md) for the full spec.

## Roadmap

More skills land in the coming weeks as they clear the abstraction pass.

## Contributing

Not accepting external contributions while the hub is still stabilizing. Open an issue if you hit a bug or see something worth publishing.

## Security

For security issues, see [SECURITY.md](./SECURITY.md).

## License

[MIT](./LICENSE). © 2026 David Faber.
