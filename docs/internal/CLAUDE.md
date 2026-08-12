# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin (`dowser`) that provides intelligent skill discovery and matching. It automatically suggests relevant skills based on user prompts using a hybrid search system (Fuse.js fuzzy matching + TF-IDF term weighting + declarative rules).

## Tech Stack

| Setting | Value |
|---------|-------|
| Language | TypeScript (Bun runtime) |
| Package Manager | pnpm |
| Runtime | Bun |
| Test Runner | Custom eval framework (`evals/run-evals.ts`) |

## Commands

```bash
# Install dependencies
pnpm install

# Run skill search evals
bun run evals/run-evals.ts

# Save/compare eval baselines
bun run evals/run-evals.ts --save baseline
bun run evals/run-evals.ts --compare baseline

# Run evals for specific category
bun run evals/run-evals.ts --category typo

# View skill usage metrics
bun run scripts/view-metrics.ts
bun run scripts/view-metrics.ts --gaps        # Show skill gaps
bun run scripts/view-metrics.ts --activations # Show skill activations

# Run health checks on skills
./scripts/garden.sh

# Record skill activation/search manually
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-activation "skill-name"
bun run hooks/prompt-submit/analyze-prompt-skills.ts --record-search "query"
```

## Architecture

### Hook System

The plugin uses Claude Code's hook system to inject skill suggestions:

1. **SessionStart** (`hooks/session-start/load-core-context.ts`): Loads PAI skill context at session start
2. **UserPromptSubmit** (`hooks/prompt-submit/analyze-prompt-skills.ts`): Analyzes each user prompt and suggests relevant skills

### Skill Analyzer (`hooks/prompt-submit/analyze-prompt-skills.ts`)

The core hybrid search engine that combines:

- **Fuse.js fuzzy matching**: Handles typos (threshold: 0.4)
- **TF-IDF term weighting**: Weights unique terms higher than common ones
- **Token-based matching**: Exact/partial name, folder, description matching
- **Declarative rules** (`lib/skill-rules.json`): Keyword triggers, intent patterns, priority boosts
- **Acronym/synonym expansion**: "tdd" → "test-driven-development", "debug" → "troubleshoot"

Key scoring weights:
- Exact folder match: +12
- Name match: +10
- Rule keyword match: +8
- Fuse.js score: normalized to 0-20
- TF-IDF score: normalized to 0-25
- Project-level skills: +10 boost

### Skills Directory Structure

Each skill lives in `skills/<skill-name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: Skill Display Name
description: Brief description (for search matching)
when_to_use: Trigger conditions for auto-suggestion
version: 1.0.0
category: optional-category
---

# Skill content follows...
```

### Metrics System (`lib/skill-metrics.json`)

Tracks three types of usage:
- **suggestions**: Skills suggested by the hook
- **activations**: Skills actually loaded via Skill tool
- **gaps**: Queries with low match scores (potential missing skills)

### Eval System (`evals/`)

Test cases in `test-cases.json` covering:
- Acronym expansion (tdd → test-driven-development)
- Synonym matching (debug ↔ troubleshoot)
- Typo tolerance (brianstorming → brainstorming)
- Domain-specific, task-based, natural language queries
- Negative cases (skills that should NOT match)

Metrics: Precision@K, Recall@K, MRR (Mean Reciprocal Rank), Pass Rate

## Configuration

Environment variables for debugging:
- `SKILL_ANALYZER_DEBUG=1`: Show all scores and matching details
- `SKILL_ANALYZER_DEBUG_FUZZY=1`: Show fuzzy match details
- `SKILL_ANALYZER_DEBUG_RULES=1`: Show rules.json matching
- `SKILL_ANALYZER_DEBUG_TFIDF=1`: Show TF-IDF scoring
- `SKILL_ANALYZER_SHOW_SCORES=1`: Include scores in output
- `SKILL_ANALYZER_TFIDF=0`: Disable TF-IDF (enabled by default)

## Key Files

- `hooks/prompt-submit/analyze-prompt-skills.ts`: Main skill analyzer (1600+ lines)
- `lib/skill-rules.json`: Declarative matching rules per skill
- `lib/skill-metrics.json`: Runtime usage metrics (gitignored)
- `evals/test-cases.json`: Eval test cases
- `evals/run-evals.ts`: Eval runner
- `commands/garden-skills.md`: Health check command documentation
- `scripts/garden.sh`: Skills health check script
