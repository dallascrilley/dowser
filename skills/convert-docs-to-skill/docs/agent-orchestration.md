# Agent Orchestration

## Overview

The convert-docs-to-skill skill uses a **consolidated agent architecture** with 7 agents (down from 16-19) that balances simplicity with performance.

**Current Architecture:**
- **Phase 1:** 1 Documentation Crawler
- **Phase 2:** 2 agents (Comprehensive Analyzer + Pitfall Hunter) in parallel
- **Phase 3:** 1 Skill Component Architect
- **Phase 4:** 2 agents (Script Generator + Config/Doc Generator) in parallel
- **Phase 6:** 1 Integration Tester

**Performance:**
- Total time: ~19 minutes (vs ~29 min manual, ~17 min max-parallelized)
- Trade-off: +2 min for 63% complexity reduction

## Phase-by-Phase Agent Integration

### Phase 1: Documentation Gathering

**Agent:** Documentation Crawler  
**Model:** Sonnet  
**Tools:** bash, read, write, grep  
**Purpose:** Extract documentation from URLs using using-crawl4ai-cli

**Capabilities:**
- Single and multi-page extraction
- JavaScript-heavy sites with dynamic content
- Quality verification and cleaning
- Multi-page parallel extraction

**See:** `.claude/agents/phase-1-documentation-gathering/documentation-crawler.md`

### Phase 2: Documentation Analysis

**Agents Used:** 2 Consolidated Agents in parallel

**Agent 1: Comprehensive Documentation Analyzer**
- **Model:** Sonnet
- **Tools:** read, grep
- **Purpose:** Complete documentation analysis in single pass
- **Scope:** Tool overview, command patterns, workflows, configuration, best practices, key examples

**Agent 2: Comprehensive Pitfall Hunter**
- **Model:** Sonnet
- **Tools:** read, grep, websearch
- **Purpose:** Unified risk assessment from docs + community
- **Scope:** Warnings, mistakes, error-prone operations, prerequisites, community issues, platform issues

**Orchestration:**
```typescript
// Launch 2 comprehensive agents in parallel
const [docAnalysis, riskAssessment] = await Promise.all([
  query({
    prompt: `Analyze ${tool} documentation comprehensively...`,
    agent: "comprehensive-documentation-analyzer"
  }),
  query({
    prompt: `Identify all pitfalls, gotchas, and known issues for ${tool}...`,
    agent: "comprehensive-pitfall-hunter"
  })
]);
```

**Speedup:** ~3x faster (3 min vs 8 min sequential)

### Phase 3: Skill Design Brainstorming

**Agent:** Skill Component Architect  
**Model:** Sonnet  
**Tools:** read, write, grep  
**Purpose:** Designs all skill components based on Phase 2 analysis

**Capabilities:**
- Helper script design (setup, validation, generation, inspection)
- Configuration template design (basic, advanced, scenario-specific)
- Guardrail design (mandatory workflows, prerequisite checks, validation gates)
- Checklist design (setup, pre-execution, troubleshooting)
- Reference documentation structure planning

### Phase 4: Artifact Creation

**Agents Used:** 2 Consolidated Agents in parallel

**Agent 1: Script & Automation Generator**
- **Model:** Haiku (fast for well-defined generation)
- **Tools:** read, write
- **Purpose:** Generate all helper scripts sequentially
- **Scope:** Setup scripts, validation scripts, generator scripts, inspection scripts, testing utilities

**Agent 2: Configuration & Documentation Generator**
- **Model:** Haiku
- **Tools:** read, write
- **Purpose:** Generate all configs and reference docs sequentially
- **Scope:** Config templates (basic, advanced, scenario), reference docs (CLI, config, patterns, troubleshooting), scripts/README.md

**Speedup:** ~2.5x faster (2 min vs 5 min sequential)

### Phase 6: Integration & Testing

**Agent:** Integration Tester  
**Model:** Sonnet (for problem-solving)  
**Tools:** read, bash  
**Purpose:** Test generated skill components

**Capabilities:**
- Sequential validation of skill components
- Testing helper scripts
- Verifying config templates
- Executing workflows
- Debugging issues

**Always sequential** (tests depend on previous results)

## Agent Configuration

### Model Selection

**Use Sonnet for:**
- Analysis requiring reasoning (Phases 1-3, 6)
- Identifying patterns and pitfalls
- Problem-solving and debugging
- Complex extraction logic

**Use Haiku for:**
- Well-defined generation tasks (Phase 4)
- Following templates with clear structure
- Fast turnaround needed
- Cost optimization

### Best Practices

1. **Parallelize Independent Tasks**
   - Analyzing different documentation sections
   - Generating multiple helper scripts
   - Creating multiple config templates

2. **Keep Sequential Tasks Sequential**
   - Testing (requires sequential execution)
   - Integration (depends on previous steps)
   - Workflow validation (steps have dependencies)

3. **Handle Failures Gracefully**
   - Use Promise.allSettled instead of Promise.all
   - Retry failed agents sequentially
   - Continue with partial results when possible

4. **Monitor Execution**
   - Track progress, measure speedup, report metrics
   - Log agent execution for debugging

## When Agents Are Skipped

Agents are NOT used when:
- ❌ User provides markdown directly (Phase 1 crawler not needed)
- ❌ Simple single-page documentation
- ❌ Python standalone mode (use create_skill.py)
- ❌ User explicitly requests sequential execution
- ❌ Documentation is very small (< 1000 lines)

**See:** `.claude/agents/README.md` for complete agent documentation

