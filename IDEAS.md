# PAI-Skills Ideas & Roadmap

> Backlog of improvements for the skill discovery system. Updated: 2025-12-21

---

## Priority Rankings

| # | ID | Title | Cat. | Impact | Effort | Exp. | Risk | Novelty | Priority | Targets / Search |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | IMP-A01 | Auto-generate rules from SKILL.md | Recs | 5 | 2 | 2 | 1 | 3 | 2.50 | `loadSkillRules`, `skill-rules.json` |
| 2 | IMP-A02 | Explicit feedback loop | Analytics | 5 | 2 | 2 | 1 | 2 | 2.50 | `formatSkillSuggestions`, `recordSkillActivation` |
| 3 | IMP-D01 | "Explain why" rationale | DX | 4 | 2 | 2 | 1 | 2 | 2.00 | `formatSkillSuggestions`, output formatting |
| 4 | IMP-D02 | Searchable skill catalog | DX | 4 | 2 | 2 | 1 | 2 | 2.00 | `commands/`, `discoverSkillsCached` |
| 5 | IMP-A03 | Effectiveness scoring | Analytics | 4 | 2 | 2 | 1 | 2 | 2.00 | `view-metrics.ts`, `SkillMetrics` |
| 6 | IMP-R06 | Predictive skill chaining | Recs | 4 | 2 | 2 | 1 | 3 | 2.00 | `related_skills` frontmatter, `formatSkillSuggestions` |
| 7 | IMP-R07 | Dynamic gap drafting | Recs | 4 | 2 | 2 | 2 | 3 | 2.00 | `recordGap`, `skills/_drafts/` |
| 8 | IMP-R01 | Gap→Rule automation | Recs | 5 | 3 | 3 | 2 | 3 | 1.67 | `skill-gaps.jsonl`, `skill-rules.json` |
| 9 | IMP-D03 | Skill scaffolding CLI | DX | 3 | 2 | 2 | 1 | 2 | 1.50 | `scripts/create-skill.ts` |
| 10 | IMP-P01 | Persist skill cache | Perf | 3 | 2 | 2 | 2 | 1 | 1.50 | `skillCache`, `skill-index.json` |
| 11 | IMP-P02 | Similarity-to-recent cache | Perf | 3 | 2 | 2 | 1 | 2 | 1.50 | `scoreSkillRelevanceHybrid` |
| 12 | IMP-R02 | Negative trigger rules | Recs | 3 | 2 | 2 | 1 | 2 | 1.50 | `skill-rules.json`, `scoreSkillFromRules` |
| 13 | IMP-R03 | Context-aware boosting | Recs | 4 | 3 | 3 | 2 | 3 | 1.33 | `analyze-prompt-skills.ts`, session state |
| 14 | IMP-A06 | User preference memory | Analytics | 4 | 3 | 2 | 2 | 3 | 1.33 | `learn-preferences.ts`, `user-prefs.md` |
| 15 | IMP-A04 | Learned scoring weights | Analytics | 5 | 4 | 4 | 2 | 4 | 1.25 | `scoreSkillsWithFuse`, `scoreSkillsWithTfIdf` |
| 16 | IMP-P03 | Modular extraction | Perf | 3 | 3 | 2 | 2 | 1 | 1.00 | `analyze-prompt-skills.ts` → `lib/skill-analyzer/` |
| 17 | IMP-A05 | OpenTelemetry tracing | Analytics | 3 | 3 | 3 | 1 | 2 | 1.00 | `lib/tracing.ts`, span wrappers |
| 18 | IMP-P04 | Dynamic context budgeter | Perf | 4 | 4 | 3 | 2 | 3 | 1.00 | skill content loading, token budgets |
| 19 | IMP-P05 | Embedding-based search | Perf | 4 | 4 | 4 | 2 | 4 | 1.00 | `@xenova/transformers`, `all-MiniLM-L6-v2` |
| 20 | IMP-R04 | AI gap auto-generation | Recs | 5 | 5 | 4 | 3 | 5 | 1.00 | `skill-gaps.jsonl`, Claude API |
| 21 | IMP-R05 | A/B testing for rules | Recs | 3 | 4 | 3 | 2 | 3 | 0.75 | `evals/run-evals.ts`, baseline comparison |

### Scoring Key

- **Impact**: Value delivered (1=minor, 5=transformative)
- **Effort**: Dev time (1=hours, 2=half-day, 3=day, 4=days, 5=week+)
- **Expertise**: Skill required (1=basic, 5=specialist)
- **Risk**: Failure/regression potential (1=safe, 5=risky)
- **Novelty**: Innovation level (1=standard, 5=novel)
- **Priority**: `round(impact/effort, 2)`

### Top Pick Rationale

**#1 Auto-generate rules from SKILL.md** — Eliminates core maintenance burden. Every new skill currently requires manual `skill-rules.json` entries. By extracting keywords/patterns from SKILL.md content (name, description, when_to_use), new skills "just work" without human intervention. Low effort (parse YAML + basic NLP) with maximum impact on onboarding velocity.

**#2 Explicit feedback loop** — Ties for priority but ranked #2 because it requires UX integration beyond the hook. Ground-truth data unlocks all downstream ML improvements.

---

## Status Legend

- `done` - Implemented and working
- `partial` - Started but incomplete
- `next` - High priority, ready to start
- `backlog` - Good idea, not prioritized
- `moonshot` - Ambitious, needs more thought

---

## Analytics & Effectiveness

| Status | Idea | Notes |
|--------|------|-------|
| `backlog` | **Explicit feedback loop** | 👍/👎 buttons after skill suggestion + optional "why" text. Ground-truth relevance for tuning. Impact: 5, Complexity: 2 |
| `backlog` | **Effectiveness scoring** | Calculate activation_rate = activations/suggestions per skill. Deprioritize skills with <5% rate after 50+ suggestions. Add `--effectiveness` to view-metrics.ts |
| `backlog` | **Learned scoring weights** | Train lightweight weights on feedback data. When skill activated after suggestion, boost keywords from triggering query (reinforcement loop). Impact: 5, Complexity: 4 |
| `backlog` | **OpenTelemetry tracing** | Wrap scoring functions in spans for performance analysis. Only active when OTEL_EXPORTER_OTLP_ENDPOINT set |

## Developer Experience

| Status | Idea | Notes |
|--------|------|-------|
| `done` | **Auto-fix frontmatter** | `scripts/fix-frontmatter.ts` - adds missing versions, truncates long when_to_use |
| `backlog` | **Skill scaffolding CLI** | `/skill create` wizard: prompts for name (auto-slugify), description, use cases. Lists existing skills for "Related Skills" selection. Auto-creates directory structure + SKILL.md with correct frontmatter. Impact: 3, Complexity: 2 |
| `backlog` | **"Explain why" rationale** | Show short rationale for each suggestion + 1-step usage example. Increases adoption by demystifying matches. Impact: 4, Complexity: 2 |
| `backlog` | **Searchable skill catalog** | `/skills` browser command: interactive search, filter by category, show usage stats. Helps users discover skills. Impact: 4, Complexity: 2 |

## Performance & Architecture

| Status | Idea | Notes |
|--------|------|-------|
| `partial` | **Skill caching** | In-memory cache exists (`skillCache`). Missing: persistent `skill-index.json` for cross-session caching |
| `backlog` | **Similarity-to-recent cache** | Reuse matching decisions for similar prompts within session. Hash prompt → result for O(1) lookup on near-duplicates. Impact: 3, Complexity: 2 |
| `backlog` | **Dynamic context budgeter** | Only load minimal skill content needed. Reduces token usage and improves latency. Impact: 4, Complexity: 4 |
| `backlog` | **Embedding-based semantic search** | Use `@xenova/transformers` with `all-MiniLM-L6-v2` for local 384d embeddings. Generate on first run for all skill descriptions + when_to_use. Cosine similarity catches intent misses (e.g., "make things fast" → "Optimizing Performance"). Impact: 4, Complexity: 4 |
| `backlog` | **Modular extraction** | Split 1600-line analyzer into lib/skill-analyzer/{scoring,cache,metrics,discovery}.ts |

## Intelligent Recommendations

| Status | Idea | Notes |
|--------|------|-------|
| `backlog` | **Auto-generate rules from SKILL.md** | Extract keywords/patterns from skill content automatically. New skills work without manual rules.json entries. Impact: 5, Complexity: 2 ★★★★★ |
| `backlog` | **Gap→Rule automation** | Analyze skill-gaps.jsonl, detect patterns, auto-suggest or auto-add rule entries for low-score queries. Impact: 5, Complexity: 3 |
| `backlog` | **Negative trigger rules** | Explicit "do not match if..." signals in skill-rules.json. Reduces false positives quickly. Impact: 3, Complexity: 2 |
| `backlog` | **Context-aware boosting** | Use current directory, file types, project tech stack + session history to boost relevant skills. Impact: 4, Complexity: 3 |
| `backlog` | **A/B testing for rules** | Test rule changes against baseline eval metrics before committing. Prevents regressions. Impact: 3, Complexity: 4 |
| `moonshot` | **AI gap auto-generation** | Use Claude API to generate SKILL.md from clustered gap queries. Requires human review before merge |

---

## Quick Wins (< 2 hours)

- [ ] **Auto-generate rules from SKILL.md** ← Highest ROI
- [ ] Add `--effectiveness` flag showing activation rates sorted by gap
- [ ] Persist skill index to disk for faster cold starts
- [ ] Add console.time/timeEnd for key functions (lightweight tracing)
- [ ] Add negative trigger rules to skill-rules.json schema
- [ ] Show "matched because: keyword X" in debug output

## Completed

- [x] Hybrid search (Fuse.js + TF-IDF + rules) - core functionality
- [x] Gap tracking with `skill-gaps.jsonl`
- [x] Auto-fix frontmatter script
- [x] In-memory skill caching
- [x] Eval framework with baseline comparisons

---

## Ideas Parking Lot

Rough ideas not yet fleshed out:

- Skill dependency graph (skill A suggests skill B as follow-up)
- Skill versioning with changelog detection
- Auto-deprecation of unused skills after N months
- Skill bundles/collections for common workflows
- Integration with episodic memory for cross-session learning
