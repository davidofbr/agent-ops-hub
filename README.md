# agent-ops-hub

A Claude Code plugin hub for SEO, AEO, and content-ops work — starting with skills built for B2B operators, but designed to be installed into any Claude Code project.

> Status: **v0.1.0 — early**. Skills are actively being restructured for public release. Expect changes.

## Install

### Option 1 — local clone

```bash
git clone git@github.com:davidofbr/agent-ops-hub.git
claude --plugin-dir ./agent-ops-hub
```

### Option 2 — reference from any project

Add to your project's `.claude/settings.json`:

```json
{
  "plugins": [
    { "path": "/path/to/agent-ops-hub" }
  ]
}
```

### Option 3 — ad-hoc per session

```bash
claude --plugin-dir /path/to/agent-ops-hub
```

## Skills

No skills are shipped in `v0.1.0`. The first skill (`persona-swarm` — parallel persona research) is being restructured for public release and will land in a follow-up version. Watch the [releases page](https://github.com/davidofbr/agent-ops-hub/releases) for updates.

## Adding your own skills

```
plugins/<plugin-name>/skills/<your-skill-name>/
└── SKILL.md   ← frontmatter: name, description
```

Skills are namespaced under `<plugin-name>:<skill-name>` when loaded.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to propose a skill or report a bug.

## Security

For security issues, see [SECURITY.md](./SECURITY.md). Please don't file public issues for security disclosures.

## License

[MIT](./LICENSE) — © 2026 David Faber
