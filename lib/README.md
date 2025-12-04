# PAI Skills - Library Files

This directory contains configuration and metrics data for the pai-skills plugin.

## Files

### `skill-rules.json`
Explicit matching rules for skills. Defines:
- `promptTriggers.keywords` - Words that trigger skill matching
- `priority` - Base priority boost for important skills
- `enforcement` - Whether skill is mandatory for certain contexts

### `skill-metrics.json`
Runtime metrics tracking skill usage in three categories:

```json
{
  "suggestions": { "skill-name": 123 },  // Hook suggested this skill
  "activations": { "skill-name": 45 },   // Skill was loaded via Skill tool
  "searches": { "query": 10 },           // User searched for this (gap analysis)
  "lastUpdated": "2025-12-04T..."
}
```

**View metrics:**
```bash
bun run scripts/view-metrics.ts              # Top 20 suggestions
bun run scripts/view-metrics.ts --summary    # Summary of all types
bun run scripts/view-metrics.ts --activations # Skills actually loaded
bun run scripts/view-metrics.ts --searches   # Gap analysis (missing skills)
bun run scripts/view-metrics.ts --all        # All items
```

**Record metrics manually:**
```bash
# Record skill activation (when Skill tool loads a skill)
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-activation "skill-name"

# Record search (for gap analysis - what users are looking for)
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-search "kubernetes deployment"
```

**Note:** This file is gitignored since it changes frequently at runtime.

### `skill-metrics-legacy-2025-12-03.json`
Historical snapshot of skill usage metrics from the legacy system before migration to this plugin. Contains 7,917 total hits across 124 skills (all counted as suggestions since we didn't distinguish types before).

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

## Metrics Categories Explained

### Suggestions
When the prompt-submit hook analyzes a user message and suggests relevant skills. High suggestion count means the skill is frequently relevant to user prompts.

### Activations
When a skill is actually loaded via the Skill tool. Compare to suggestions to see:
- **High suggestion, low activation** → Skill is suggested but not used (maybe too generic?)
- **High activation, low suggestion** → Skill is explicitly requested by users
- **High both** → Very useful, frequently used skill

### Searches (Gap Analysis)
Queries users searched for but didn't find a matching skill. Use this to identify:
- Skills that should be created
- Missing documentation or keywords in existing skills
- Areas where users need more support

## Data Location History

Previously metrics were stored at:
- `~/PAI/.claude/metrics/skill-hit-counts.json` (flat format, suggestions only)

Now integrated into the plugin at:
- `~/PAI/.claude/plugins/pai-skills/lib/skill-metrics.json` (structured format)
