# Dowser - Library Files

Configuration and metrics data for the Dowser Claude Code plugin.

## Files

### `skill-rules.json`
Explicit matching rules for skills. Defines:
- `promptTriggers.keywords` - Words that trigger skill matching
- `priority` - Base priority boost for important skills
- `enforcement` - Whether skill is mandatory for certain contexts

### `config.ts`
Shared scoring thresholds and hybrid weights used by the skill analyzer.

### `skill-metrics.json`
Runtime metrics tracking skill usage (gitignored). Categories:

```json
{
  "suggestions": { "skill-name": 123 },
  "activations": { "skill-name": 45 },
  "searches": { "query": 10 },
  "lastUpdated": "2025-12-04T..."
}
```

**View metrics:**
```bash
bun run scripts/view-metrics.ts
bun run scripts/view-metrics.ts --summary
bun run scripts/view-metrics.ts --activations
bun run scripts/view-metrics.ts --searches
```

**Record metrics manually:**
```bash
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-activation "skill-name"
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-search "kubernetes deployment"
```

### `skill-metrics-legacy-2025-12-03.json`
Historical snapshot from before the structured metrics format. Kept for reference only.
