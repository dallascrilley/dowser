# Repository Guidelines

## Project Settings
| Setting | Value |
|---------|-------|
| Language | TypeScript 5.x |
| Package Manager | bun |
| Backend Framework | None (plugin/scripts only) |
| Frontend Framework | None |
| Database/ORM | None |
| Test Runner | bun:test |
| Linter/Formatter | None (use garden scripts) |

Quality gates (run in order):
```bash
typecheck: (not configured at repo root)
lint:      ./scripts/garden.sh
test:      bun test
build:     (not applicable; no build step)
```

## Project Structure & Module Organization
- `skills/` — individual skill folders, each with `SKILL.md` and supporting assets.
- `hooks/` — Claude plugin hooks (e.g., `prompt-submit/`, `session-start/`) and `hooks/__tests__/`.
- `lib/` — shared data files like `skill-rules.json` and metrics (see note below).
- `scripts/` — maintenance and validation utilities (“garden” checks).
- `evals/` — evaluation cases and results for search quality.
- `docs/plans/` — planning docs for ongoing improvements.

## Build, Test, and Development Commands
- `bun test` — runs `bun:test` suites (notably in `hooks/__tests__/`).
- `./scripts/garden.sh [SKILLS_DIR]` — full skill health check (naming, frontmatter, links, coverage).
- `./scripts/check-frontmatter.sh [SKILLS_DIR]` — frontmatter-only validation.
- `bun run hooks/prompt-submit/analyze-prompt-skills.ts` — run the prompt-submit hook locally.
- `bun run scripts/view-metrics.ts --summary` — view skill metrics summary.

## Coding Style & Naming Conventions
- TypeScript ESM, 2‑space indentation, single quotes, semicolons.
- Skill folders use `kebab-case`; each skill must include `SKILL.md` with YAML frontmatter.
- Tests use `*.test.ts`; scripts use `kebab-case` (`.ts` or `.sh`).

## Testing Guidelines
- Prefer focused unit tests for hook behavior and regressions.
- Keep tests close to the code they cover (e.g., `hooks/__tests__/`).
- Run `bun test` before opening a PR that touches hooks or scripts.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `chore:`, `test:`.
- PRs should include a short summary and the commands run (if any).
- Link related issues/plan items when applicable.

## Security & Configuration Tips
- `lib/skill-metrics.json` is gitignored; do not commit local metrics.
- Avoid committing secrets; use `.env.example` if configuration is needed.
