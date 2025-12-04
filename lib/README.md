# PAI Skills - Library Files

This directory contains configuration and metrics data for the pai-skills plugin.

## Files

### `skill-rules.json`
Explicit matching rules for skills. Defines:
- `promptTriggers.keywords` - Words that trigger skill matching
- `priority` - Base priority boost for important skills
- `enforcement` - Whether skill is mandatory for certain contexts

### `skill-metrics.json`
Runtime metrics tracking how often each skill is suggested by the prompt analyzer hook.

**View metrics:**
```bash
bun run scripts/view-metrics.ts          # Top 20
bun run scripts/view-metrics.ts --top 50 # Top 50
bun run scripts/view-metrics.ts --all    # All skills
```

**Note:** This file is gitignored since it changes frequently at runtime.

### `skill-metrics-legacy-2025-12-03.json`
Historical snapshot of skill usage metrics from the legacy system before migration to this plugin. Contains 7,917 total hits across 124 skills.

**Top 10 historically:**
| Rank | Skill | Hits |
|------|-------|------|
| 1 | PAI | 1,182 |
| 2 | Google Gemini API | 1,080 |
| 3 | react-hook-form-zod | 973 |
| 4 | cleaning-up-post-task | 532 |
| 5 | Tailwind v4 + shadcn/ui Stack | 444 |
| 6 | frontend-dev-guidelines-tailwind | 316 |
| 7 | openai-responses | 269 |
| 8 | using-gemini-cli | 242 |
| 9 | OpenAI API | 227 |
| 10 | git-expert | 192 |

## Data Location History

Previously metrics were stored at:
- `~/PAI/.claude/metrics/skill-hit-counts.json`

Now integrated into the plugin at:
- `~/PAI/.claude/plugins/pai-skills/lib/skill-metrics.json`
