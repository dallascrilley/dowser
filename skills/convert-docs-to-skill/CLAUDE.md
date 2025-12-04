# Skill Creator from Documentation - Core Methodology

## Purpose

Transform documentation for tools, CLIs, APIs, or libraries into production-ready PAI skills with helper scripts, templates, and guardrails.

**For detailed methodology:** See `docs/methodology/` directory  
**For agent orchestration:** See `docs/agent-orchestration.md`  
**For examples:** See `docs/examples.md`  
**For best practices:** See `docs/best-practices.md`

## What is a Documentation-Based Skill?

A skill created by:
1. Analyzing tool/CLI/API documentation
2. Extracting workflows and patterns
3. Identifying pitfalls and best practices
4. Creating helper scripts for automation
5. Designing configuration templates
6. Building guardrails to prevent mistakes
7. Packaging into a comprehensive skill

**Goal:** Make documentation-based skills as good as (or better than) manual skills through systematic analysis and automation.

## The Six-Phase Methodology

```
Phase 1: Documentation Gathering
    ↓
Phase 2: Documentation Analysis
    ↓
Phase 3: Skill Design Brainstorming
    ↓
Phase 4: Artifact Creation
    ↓
Phase 5: SKILL.md Creation
    ↓
Phase 6: Integration & Testing
```

Each phase has specific deliverables and validation checkpoints.

## Phase Overview

### Phase 1: Documentation Gathering
**Goal:** Collect complete, clean documentation in markdown format.

**Methods:**
- Direct markdown input
- URL extraction (using-crawl4ai-cli)
- Mixed approach (docs + user context)

**Deliverable:** Complete documentation in markdown

**See:** `docs/methodology/phase-1-gathering.md` for detailed methods

### Phase 2: Documentation Analysis & Component Design (Merged)
**Goal:** Extract structure, patterns, workflows, and gotchas, then design components.

**Analysis Framework:**
1. Tool Overview (purpose, capabilities, use cases)
2. Command/API Patterns (syntax, flags, combinations)
3. Workflows (multi-step processes)
4. Pitfalls & Gotchas (warnings, common mistakes)
5. Best Practices (recommendations, optimizations)

**Design Framework:**
1. Helper Scripts (setup, validation, generators, inspection)
2. Config Templates (basic, advanced, scenario-specific)
3. Guardrails (mandatory workflows, validation gates)
4. Checklists (setup, pre-execution, troubleshooting)
5. Reference Structure (SKILL.md vs references/)

**Deliverable:** Complete analysis + component design document

**See:** `docs/methodology/phase-2-analysis.md` and `docs/methodology/phase-3-design.md` for detailed frameworks

**Note:** Phase 2 and 3 are merged for efficiency - design is informed by fresh analysis context in a single pass.

### Phase 4: Artifact Creation
**Goal:** Generate all skill components.

**Artifacts:**
- Helper scripts (from templates)
- Config templates (presets)
- Reference docs (CLI, config, patterns, troubleshooting)

**Deliverable:** Complete skill directory structure

**See:** `docs/methodology/phase-4-generation.md` for generation details

### Phase 5: SKILL.md Creation
**Goal:** Write comprehensive quick-reference SKILL.md.

**Structure:**
- YAML frontmatter (name, description, triggers)
- Tool overview
- Prerequisites & setup
- Quick start
- Core tasks
- Command reference
- Configuration files
- Proven patterns
- Troubleshooting
- Helper scripts
- Workflow requirements

**Deliverable:** Complete SKILL.md file

**See:** `docs/methodology/phase-5-6.md` for SKILL.md structure

### Phase 6: Integration & Testing
**Goal:** Integrate skill and validate it works.

**Steps:**
1. Add to global context (KAI.md)
2. Test skill activation
3. Test helper scripts
4. Test config templates
5. Validate file references
6. Execute workflows

**Deliverable:** Production-ready skill

**See:** `docs/methodology/phase-5-6.md` for testing workflow

## Agent Architecture (Summary)

**Current:** 5 optimized agents (down from 16-19 original, 7 previous consolidation)

- **Phase 1:** 1 Documentation Crawler
- **Phase 2:** 2 agents (Comprehensive Analyzer-Designer + Pitfall Hunter) in parallel
- **Phase 4:** 2 agents (Script Generator + Config/Doc Generator) in parallel
- **Phase 6:** 1 Integration Tester

**Performance:**
- Total time: ~17 minutes (vs ~29 min manual, ~19 min with 7 agents)
- Improvement: 2 minutes faster + 29% fewer agents than previous consolidation

**See:** `docs/agent-orchestration.md` for detailed agent specs and orchestration code

## Quick Decision Trees

### When to Use Agents
- ✅ Large documentation (multiple pages)
- ✅ Complex tools (many commands/flags)
- ✅ Multiple scripts/templates needed
- ✅ Time-sensitive creation

### When to Skip Agents
- ❌ Simple single-page docs
- ❌ Quick skills (1-2 scripts)
- ❌ User provides markdown directly
- ❌ Thoroughness > speed priority

### Which Phase Am I In?

**Phase 1:** Do I have complete documentation? → No: Gather docs
**Phase 2:** Do I have analysis + component design? → No: Analyze docs and design components
**Phase 4:** Do I have all artifacts? → No: Generate artifacts
**Phase 5:** Do I have SKILL.md? → No: Write SKILL.md
**Phase 6:** Is skill tested? → No: Test and integrate

## Key Principles

1. **Template-Driven:** Use templates for consistency
2. **Helper Scripts Over Manual Steps:** Automate error-prone tasks
3. **Guardrails Prevent Mistakes:** Add ⚠️ MANDATORY workflows
4. **Progressive Disclosure:** SKILL.md = quick ref, references/ = details
5. **Validation Built-In:** Create validation scripts for common errors
6. **Examples Everywhere:** Every section needs working examples
7. **Prerequisites Automated:** Setup scripts handle first-time setup
8. **Troubleshooting Proactive:** Anticipate and document common issues

## Extended Documentation

For comprehensive details, see:

- **`docs/methodology/`** - Detailed phase-by-phase methodology
  - `phase-1-gathering.md` - Documentation extraction methods
  - `phase-2-analysis.md` - Analysis frameworks and patterns
  - `phase-3-design.md` - Component design patterns (now merged into Phase 2)
  - `phase-4-generation.md` - Artifact creation workflows
  - `phase-5-6.md` - SKILL.md writing and testing

- **`docs/agent-orchestration.md`** - Agent architecture, configuration, orchestration code

- **`docs/examples.md`** - Complete real-world examples (jq, ripgrep, etc.)

- **`docs/templates-guide.md`** - Template usage patterns and customization

- **`docs/best-practices.md`** - Quality checklists, common pitfalls, success criteria

## Integration with PAI Ecosystem

- **Extends:** `create-skill` (general framework)
- **Uses:** `using-crawl4ai-cli` (Phase 1 documentation extraction)
- **Generates:** Skills following same pattern as `using-crawl4ai-cli`

---

**For complete methodology:** See extended documentation in `docs/` directory.
