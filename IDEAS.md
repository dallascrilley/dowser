# PAI-Skills Ideas & Roadmap

> Backlog of improvements for the skill discovery system. Updated: 2025-12-21

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
| `backlog` | **Skill scaffolding CLI** | `/skill create` wizard: auto-extracts keywords from content, validates frontmatter, generates SKILL.md + directories, auto-adds to skill-rules.json. Impact: 3, Complexity: 2 |
| `backlog` | **"Explain why" rationale** | Show short rationale for each suggestion + 1-step usage example. Increases adoption by demystifying matches. Impact: 4, Complexity: 2 |
| `backlog` | **Searchable skill catalog** | `/skills` browser command: interactive search, filter by category, show usage stats. Helps users discover skills. Impact: 4, Complexity: 2 |

## Performance & Architecture

| Status | Idea | Notes |
|--------|------|-------|
| `partial` | **Skill caching** | In-memory cache exists (`skillCache`). Missing: persistent `skill-index.json` for cross-session caching |
| `backlog` | **Similarity-to-recent cache** | Reuse matching decisions for similar prompts within session. Hash prompt → result for O(1) lookup on near-duplicates. Impact: 3, Complexity: 2 |
| `backlog` | **Dynamic context budgeter** | Only load minimal skill content needed. Reduces token usage and improves latency. Impact: 4, Complexity: 4 |
| `backlog` | **Embedding-based semantic search** | Replace/augment TF-IDF with embeddings (local or API) for better concept matching. Impact: 4, Complexity: 4 |
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
