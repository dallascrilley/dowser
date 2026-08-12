# Contributing to Dowser

Thanks for helping improve skill discovery for Claude Code.

## Setup

Requirements:

- [Bun](https://bun.sh) 1.0+ (hooks and tests run on Bun)

```bash
git clone https://github.com/dallascrilley/dowser.git
cd dowser
bun install
bun run test
```

Bun is the supported runtime for hooks and tests. A `pnpm-lock.yaml` may be present for Node tooling compatibility; prefer `bun install` for local development.

## What to change

| Area | Path | Notes |
|------|------|--------|
| Search engine | `hooks/prompt-submit/skill-analyzer/` | Hybrid Fuse + TF-IDF + rules scoring |
| Hooks | `hooks/` | SessionStart and UserPromptSubmit |
| Skill library | `skills/<name>/SKILL.md` | YAML frontmatter + body |
| Activation rules | `lib/skill-rules.json` | Keywords, intents, priorities |
| Maintenance scripts | `scripts/` | Garden checks, metrics, migrations |

## Skill conventions

- Folder names are `kebab-case`.
- Every skill needs `SKILL.md` with frontmatter: at least `name`, `description` or `short_description`, and `when_to_use`.
- Prefer relative paths or `$HOME/...` placeholders. Do not commit machine-specific absolute paths.
- If you vendor third-party skill content, include license or attribution in the skill dir and update `NOTICE`.

## Tests

```bash
bun test                 # unit tests under hooks/__tests__
bun run test:garden      # frontmatter smoke check (optional, slower)
```

Add or update tests next to the behavior you change. Keep tests deterministic: use temp dirs, not your real `~/.claude`.

## Pull requests

1. Branch from `main`.
2. Keep the change focused.
3. Run `bun test` and note the result in the PR.
4. Use conventional commits when practical: `feat:`, `fix:`, `docs:`, `chore:`, `test:`.

## Code style

TypeScript ESM, 2-space indent, single quotes, semicolons. No required formatter at repo root; match neighboring files.

## Security

Do not commit secrets, API keys, or personal context files. Report vulnerabilities as described in [SECURITY.md](./SECURITY.md).
