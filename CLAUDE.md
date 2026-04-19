# agent-ops-hub

A Claude Code plugin hub for SEO, AEO, and content-ops skills.

## What this repo is

A collection of Claude Code plugins, each containing one or more skills. Plugins live under `plugins/<plugin-name>/` and are loaded via `claude --plugin-dir` or a project's `.claude/settings.json`.

## Repository layout

```
.claude-plugin/marketplace.json   ← marketplace metadata for this hub
plugins/<plugin-name>/
  .claude-plugin/plugin.json      ← per-plugin metadata (when present)
  skills/<skill-name>/SKILL.md    ← one directory per skill
```

## Adding a skill

1. Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
2. Frontmatter must include `name` and `description`
3. Reference any supporting files (agents, schemas, prompts) with relative paths from the skill directory

## Conventions

- Skills are self-contained — no implicit dependencies on files outside the skill directory
- No real client data, credentials, or proprietary prompts in this repo
- Working folders like `/exports/`, `/outputs/`, `/data/` are gitignored by convention
