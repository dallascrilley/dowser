# Skill Search Evaluations

Automated evaluation framework for measuring skill search quality.

## Quick Start

```bash
# Run all evals
bun run evals/run-evals.ts

# Save baseline before making changes
bun run evals/run-evals.ts --save baseline

# After changes, compare against baseline
bun run evals/run-evals.ts --compare baseline

# Run specific category
bun run evals/run-evals.ts --category typo

# Verbose output (show all results)
bun run evals/run-evals.ts --verbose
```

## Metrics

| Metric | Description |
|--------|-------------|
| **Precision@K** | What % of top-K results are relevant? |
| **Recall@K** | What % of expected skills appear in top-K? |
| **MRR** | Mean Reciprocal Rank - 1/rank of first relevant result |
| **Pass Rate** | % of test cases where at least one expected skill appears in top 3 |

## Test Case Categories

| Category | Tests | Description |
|----------|-------|-------------|
| `acronym_expansion` | 4 | TDD → test-driven-development |
| `synonym_matching` | 5 | debug ↔ troubleshoot ↔ fix |
| `exact_match` | 4 | Exact folder/name matches |
| `domain_specific` | 5 | React forms, Cloudflare, etc. |
| `task_based` | 4 | "write tests", "review code" |
| `typo_tolerance` | 3 | brianstorming → brainstorming |
| `natural_language` | 3 | "how do I implement dark mode" |
| `negative` | 3 | Ensure wrong skills DON'T match |
| `compound` | 2 | Multi-concept queries |
| `short_query` | 2 | 2-char queries (ai, db) |

## Baseline Results (2025-12-04)

```
Total:     35 cases
Passed:    25 (71.4%)
Failed:    10

Avg Precision@3:  25.7%
Avg Recall@3:     60.2%
Avg MRR:          65.2%

By Category:
  acronym_expansion    ████████░░ 3/4 (75%)
  synonym_matching     ████████░░ 4/5 (80%)
  exact_match          ██████████ 4/4 (100%)
  domain_specific      ████████░░ 4/5 (80%)
  task_based           ██████████ 4/4 (100%)
  typo_tolerance       ░░░░░░░░░░ 0/3 (0%)
  natural_language     ███████░░░ 2/3 (67%)
  negative             ██████████ 3/3 (100%)
  compound             █████░░░░░ 1/2 (50%)
  short_query          ░░░░░░░░░░ 0/2 (0%)
```

## Known Weaknesses

Based on baseline evaluation:

1. **Typo tolerance (0%)** - Levenshtein distance only checks against full skill names, not description tokens
2. **Short queries (0%)** - 2-char tokens like "ai", "db" don't match well despite being allowed
3. **Compound queries (50%)** - Multi-concept queries sometimes match tangentially related skills

## Adding Test Cases

Edit `test-cases.json`:

```json
{
  "id": "unique-test-id",
  "category": "category_name",
  "query": "user query to test",
  "expected": ["skill-name-1", "skill-name-2"],
  "not_expected": ["skill-that-should-not-match"],
  "notes": "Why this test matters"
}
```

## Comparing Implementations

```bash
# Save current implementation
bun run evals/run-evals.ts --save before-fuse

# Make changes (e.g., integrate Fuse.js)

# Compare
bun run evals/run-evals.ts --compare before-fuse --save after-fuse
```

## CI Integration

```bash
# Exit code 0 if all pass, 1 if any fail
bun run evals/run-evals.ts || echo "Some evals failed"

# Require minimum pass rate
bun run evals/run-evals.ts --json | jq -e '.pass_rate >= 0.8'
```
