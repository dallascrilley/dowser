# Dowser

Dowser surfaces the right skill from a curated Claude Code skill library.

## What it is

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin that watches each prompt and suggests relevant skills from a local library. Matching combines:

- **Fuse.js** fuzzy search (typo-tolerant names and descriptions)
- **TF-IDF** term weighting
- **Declarative rules** in `lib/skill-rules.json` (keywords, intent patterns, priorities)
- Optional **semantic embeddings** via `@xenova/transformers` (on by default; set `SKILL_ANALYZER_SEMANTIC=0` to disable)

When a skill fits, the UserPromptSubmit hook injects a short suggestion into context so you can load it with the Skill tool.

This repository also ships the skill library under `skills/` (100+ domain and workflow skills).

## Requirements

- [Bun](https://bun.sh) 1.0+ (hooks and tests run on Bun)
- Claude Code with plugin support
- macOS or Linux paths that match Claude Code’s usual `~/.claude` layout

## Install (Claude Code plugin)

From a cold clone:

```bash
git clone https://github.com/dallascrilley/dowser.git
cd dowser
bun install
```

Point Claude Code at this plugin directory (local path install). Exact UI labels vary by Claude Code version; the contract is:

1. Plugin root is this repository (contains `.claude-plugin/plugin.json` and `hooks/hooks.json`).
2. `CLAUDE_PLUGIN_ROOT` resolves to that directory when hooks run.
3. Dependencies are installed so `hooks/run-hook.sh` can `bun run` the TypeScript hooks.

If you already manage plugins under `~/.claude/plugins/`, you can clone or symlink this repo as `~/.claude/plugins/dowser` (or keep a legacy `dowser` directory name; the search code still recognizes it).

```bash
mkdir -p ~/.claude/plugins
ln -sfn "$(pwd)" ~/.claude/plugins/dowser
```

Restart Claude Code or start a new session. On SessionStart, Dowser tries to load optional personal PAI context if you keep a `PAI/SKILL.md` (or `~/.claude/skills/PAI/SKILL.md`). Missing PAI context is a warning, not a failure: skill search still works.

**Note:** The GitHub repository may still be named `dowser` until rename to Dowser completes. Clone URLs in this README track the current remote.

## Quickstart (local smoke)

```bash
bun install
bun run test
# full suite (slower cold start): bun run test:all
```

Exercise the analyzer without Claude Code:

```bash
echo '{"userMessage":"help me write a failing test first","session_id":"local"}' \
  | bun run hooks/prompt-submit/analyze-prompt-skills.ts
```

You should get JSON with an optional skill suggestion block for TDD or related skills.

Garden checks (skill frontmatter health):

```bash
bun run test:garden
# or full garden suite
./scripts/garden.sh skills
```

## Architecture

```
.claude-plugin/plugin.json   # Claude Code plugin metadata
hooks/
  hooks.json                 # UserPromptSubmit + SessionStart wiring
  run-hook.sh                # Ensures deps, runs Bun hook scripts
  prompt-submit/             # Hybrid skill search
    skill-analyzer/          # Fuse, TF-IDF, rules, discovery, hybrid score
  session-start/             # Optional PAI core-context inject
skills/<name>/SKILL.md       # Curated skill library
lib/skill-rules.json         # Explicit activation rules
lib/config.ts                # Score thresholds and weights
scripts/                     # Garden, migrate, metrics utilities
evals/                       # Offline search quality cases
```

**Prompt path:** UserPromptSubmit → `analyze-prompt-skills.ts` → discover skills from user, plugin, and project roots → score with rules + Fuse + TF-IDF (+ optional embeddings) → format top matches as additional context.

**Skill roots (simplified order):** `~/.claude/skills` → this plugin’s `skills/` (via `CLAUDE_PLUGIN_ROOT` or `.../plugins/dowser`) → other plugin skill trees under `~/.claude/plugins` → project `.claude/skills` (wins on name clash).

## Non-goals

- Not a general web search product or hosted skill marketplace.
- Not a replacement for Claude Code’s built-in Skill tool; it recommends what to load.
- Not guaranteed offline embedding quality on first run (model download may occur when semantic search is enabled).
- Not a full Personal AI Infrastructure (PAI) distribution; PAI context loading is optional integration.

## Configuration

| Variable | Purpose |
|----------|---------|
| `CLAUDE_PLUGIN_ROOT` | Set by Claude Code to the plugin install path |
| `PAI_DIR` | Optional personal context root (default `~/PAI` or `~/.claude`) |
| `SKILL_ANALYZER_DEBUG=1` | Verbose scoring to stderr |
| `SKILL_ANALYZER_SEMANTIC=0` | Disable embeddings |
| `SKILL_ANALYZER_PREFER_PLUGIN_SKILLS=0` | Disable priority boost for this plugin’s skills |
| `SKILL_ANALYZER_PLUGIN_BOOST` | Numeric boost (default 25) |

Legacy env names `SKILL_ANALYZER_PREFER_PAI_SKILLS` and `SKILL_ANALYZER_PAI_BOOST` still work.

## License audit (skills/)

Plugin code is MIT (see [LICENSE](./LICENSE)). Skill content is a mix of original writeups, MIT-declared skills, Superpowers-aligned workflows (MIT upstream), and one Apache-2.0 skill (`skills/skill-creator/`). Full attribution lives in [NOTICE](./NOTICE).

| Category | Count (approx.) | Handling |
|----------|-----------------|----------|
| Explicit `license: MIT` in frontmatter | 16 | Kept |
| Apache-2.0 (`skill-creator`) | 1 | Kept with LICENSE.txt |
| Superpowers-aligned workflows | ~35 | Kept; attributed in NOTICE |
| Dallas-curated / no separate LICENSE | remainder | Published under root MIT; open an issue if provenance is wrong |

Prefer remove or attribute over guessing rights. If upstream terms are unclear for a skill you care about, file an issue and we can stub or drop it.

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md). Security reports: [SECURITY.md](./SECURITY.md).

```bash
bun test                 # unit tests
bun run evals            # search quality eval harness
bun run scripts/view-metrics.ts --summary
```

Internal planning notes live under `docs/internal/` and are not part of the user install path.

## License

MIT © 2025-2026 Dallas Crilley. Third-party skill attributions: [NOTICE](./NOTICE).
