# PAI-Skills Productivity Improvement Plan

> Generated: 2025-12-14

## Focus Summary

**Purpose:** Personal skills library with 100+ domain-specific skills, automatic skill suggestion via hybrid search (Fuse.js + TF-IDF + rules), metrics tracking, and maintenance tooling

### Key Flows

- UserPromptSubmit hook analyzes prompts and suggests relevant skills
- SessionStart hook injects PAI context automatically
- Garden scripts validate skill frontmatter, links, and coverage
- Metrics track suggestions, activations, searches, and gaps

### Constraints

- Bun runtime required
- Skills must have SKILL.md with valid YAML frontmatter
- Metrics stored in lib/skill-metrics.json (gitignored)

### Risks & Unknowns

- ⚠️ Massive suggestion-to-activation gap (1193 suggestions, 3 activations) indicates skill relevance issues
- ⚠️ 1679-line analyzer file is complex and hard to maintain
- ⚠️ No automated skill quality scoring beyond frontmatter validation
- ⚠️ Gap detection is passive - requires manual review

## Improvements Overview

| # | ID | Title | Category | Priority | Impact | Effort |
|---|-----|-------|----------|----------|--------|--------|
| 1 | [IMP-001](./IMP-001.md) | Add skill effectiveness scoring to close suggestion-activation gap | 📋 Conventional | 2.50 | 5/5 | 2/5 |
| 2 | [IMP-002](./IMP-002.md) | Create auto-fix command for common frontmatter issues | 📋 Conventional | 2.00 | 4/5 | 2/5 |
| 3 | [IMP-003](./IMP-003.md) | Implement lazy skill indexing with persistent cache | 📋 Conventional | 2.00 | 4/5 | 2/5 |
| 4 | [IMP-004](./IMP-004.md) | Add skill scaffolding CLI with templates | 📋 Conventional | 1.33 | 4/5 | 3/5 |
| 5 | [IMP-007](./IMP-007.md) | Add OpenTelemetry tracing for skill search pipeline | 💡 Creative | 1.33 | 4/5 | 3/5 |
| 6 | [IMP-006](./IMP-006.md) | Build session-aware skill recommendation engine | 💡 Creative | 1.25 | 5/5 | 4/5 |
| 7 | [IMP-005](./IMP-005.md) | Extract skill analyzer into modular library | 📋 Conventional | 1.00 | 3/5 | 3/5 |
| 8 | [IMP-008](./IMP-008.md) | Implement AI-powered skill gap auto-generation | 🚀 Moonshot | 1.00 | 5/5 | 5/5 |

## Epics

### EPIC-01: Skill Analytics & Effectiveness

- [IMP-001](./IMP-001.md): Add skill effectiveness scoring to close suggestion-activation gap
- [IMP-007](./IMP-007.md): Add OpenTelemetry tracing for skill search pipeline

### EPIC-02: Developer Experience & Tooling

- [IMP-002](./IMP-002.md): Create auto-fix command for common frontmatter issues
- [IMP-004](./IMP-004.md): Add skill scaffolding CLI with templates

### EPIC-03: Performance & Architecture

- [IMP-003](./IMP-003.md): Implement lazy skill indexing with persistent cache
- [IMP-005](./IMP-005.md): Extract skill analyzer into modular library

### EPIC-04: Intelligent Recommendations

- [IMP-006](./IMP-006.md): Build session-aware skill recommendation engine
- [IMP-008](./IMP-008.md): Implement AI-powered skill gap auto-generation

## Recommended Sequence

1. [IMP-001](./IMP-001.md): Add skill effectiveness scoring to close suggestion-activation gap
2. [IMP-002](./IMP-002.md): Create auto-fix command for common frontmatter issues
3. [IMP-003](./IMP-003.md): Implement lazy skill indexing with persistent cache
4. [IMP-004](./IMP-004.md): Add skill scaffolding CLI with templates
5. [IMP-007](./IMP-007.md): Add OpenTelemetry tracing for skill search pipeline
6. [IMP-005](./IMP-005.md): Extract skill analyzer into modular library
7. [IMP-006](./IMP-006.md): Build session-aware skill recommendation engine
8. [IMP-008](./IMP-008.md): Implement AI-powered skill gap auto-generation

## Category Distribution

- 📋 **Conventional:** 5
- 💡 **Creative:** 2
- 🚀 **Moonshot:** 1
