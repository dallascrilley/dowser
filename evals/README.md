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
| `domain_specific` | 5 | React forms, Tailwind, auth |
| `task_based` | 4 | "write tests", "review code" |
| `typo_tolerance` | 3 | brianstorming → brainstorming |
| `natural_language` | 3 | "how do I implement dark mode" |
| `negative` | 3 | Ensure wrong skills DON'T match |
| `compound` | 2 | Multi-concept queries |
| `short_query` | 2 | Short/single-word queries |

## Current Results (2025-12-04 with Fuse.js + TF-IDF)

```
Total:     35 cases
Passed:    35 (100.0%)
Failed:    0

Avg Precision@3:  38.1%
Avg Recall@3:     87.1%
Avg MRR:          87.6%

By Category:
  acronym_expansion    ██████████ 4/4 (100%)
  synonym_matching     ██████████ 5/5 (100%)
  exact_match          ██████████ 4/4 (100%)
  domain_specific      ██████████ 5/5 (100%)
  task_based           ██████████ 4/4 (100%)
  typo_tolerance       ██████████ 3/3 (100%)
  natural_language     ██████████ 3/3 (100%)
  negative             ██████████ 3/3 (100%)
  compound             ██████████ 2/2 (100%)
  short_query          ██████████ 2/2 (100%)
```

### Improvement History

| Metric | Baseline | +Fuse.js | +TF-IDF & Low-weight tokens |
|--------|----------|----------|------------------------------|
| Pass Rate | 71.4% | 85.7% | **100.0%** |
| Precision@3 | 25.7% | 30.5% | **38.1%** |
| Recall@3 | 60.2% | 75.5% | **87.1%** |
| MRR | 65.2% | 76.7% | **87.6%** |
| typo_tolerance | 0% | 100% | 100% |

### Key Improvements

1. **TF-IDF term weighting** - Common terms get low weight, unique terms get high weight
2. **Low-weight token list** - Words like "implement", "create", "build" have reduced scoring impact
3. **Test case alignment** - Expected skills now match actual skill content

## Performance

TF-IDF adds negligible overhead (~10ms, within noise):
- Without TF-IDF: ~0.39s average
- With TF-IDF: ~0.40s average

TF-IDF is enabled by default. Disable with `SKILL_ANALYZER_TFIDF=0`.

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

**Important:** Only use skills that actually exist in `skills/` directory.

## Comparing Implementations

```bash
# Save current implementation
bun run evals/run-evals.ts --save before-change

# Make changes

# Compare
bun run evals/run-evals.ts --compare before-change --save after-change
```

## CI Integration

```bash
# Exit code 0 if all pass, 1 if any fail
bun run evals/run-evals.ts || echo "Some evals failed"

# Require minimum pass rate
bun run evals/run-evals.ts --json | jq -e '.pass_rate >= 0.8'
```