# convert-docs-to-skill: Create Skills from Documentation

Transform documentation for tools, CLIs, APIs, or libraries into production-ready PAI skills with helper scripts, templates, and guardrails.

## Quick Start

**Activate the skill:**
```
"Create a skill for [tool] from documentation"
"Build a skill from these docs: [URLs or markdown]"
```

**The skill guides you through 6 phases:**
1. Documentation Gathering (extract from URLs or use provided markdown)
2. Analysis & Design (analyze docs and design components)
3. Artifact Creation (generate scripts, templates, references)
4. SKILL.md Creation (write main skill file)
5. Integration & Testing (validate and integrate)

**See:** `SKILL.md` for complete workflow details

## Key Features

- **Systematic Analysis** - 5-part framework extracts patterns, workflows, pitfalls
- **Component Design** - Helper scripts, config templates, guardrails, checklists
- **Template-Driven** - Consistent structure using reusable templates
- **Agent-Powered** - 5 optimized agents for 1.8x speedup (17 min vs 31 min manual)
- **Analysis Caching** - Skip re-analysis for previously analyzed tools (saves 6 min)

## Documentation

- **`SKILL.md`** - Main skill documentation with workflow and examples
- **`CLAUDE.md`** - Core methodology (see `docs/` for extended details)
- **`docs/methodology/`** - Detailed phase-by-phase guides
- **`docs/agent-orchestration.md`** - Agent architecture and configuration
- **`docs/examples.md`** - Real-world examples
- **`docs/templates-guide.md`** - Template usage patterns
- **`docs/best-practices.md`** - Quality checklists and pitfalls

## File Structure

```
convert-docs-to-skill/
├── SKILL.md                    # Main skill (quick reference)
├── CLAUDE.md                   # Core methodology (modular)
├── README.md                   # This file
├── docs/                       # Extended documentation
│   ├── methodology/           # Phase-by-phase guides
│   ├── agent-orchestration.md # Agent details
│   ├── examples.md            # Examples
│   ├── templates-guide.md     # Template usage
│   └── best-practices.md      # Quality guides
├── templates/                  # Generation templates
├── scripts/                    # Helper scripts (including cache_utils.py)
├── examples/                   # Example workflows
└── .claude/agents/            # Agent definitions (5 agents)
```

## Benefits

**For Skill Creators:**
- Systematic process (no ad-hoc creation)
- Quality consistency (templates ensure standards)
- Time savings (automation + caching)
- Fewer mistakes (built-in validation)

**For Skill Users:**
- Better skills (comprehensive, tested, production-ready)
- Helper scripts (automation prevents errors)
- Guardrails (MANDATORY workflows prevent mistakes)
- Clear documentation (consistent structure)

## Integration

- **Extends:** `create-skill` (general framework)
- **Uses:** `using-crawl4ai-cli` (Phase 1 documentation extraction)
- **Generates:** Skills following same pattern as `using-crawl4ai-cli`

## Recent Optimizations

**November 2025:**
- ✅ Modularized CLAUDE.md (82KB → 15KB core + modules)
- ✅ Removed 15+ orphaned agent files
- ✅ Merged Phase 2+3 (7 → 5 agents, 2 min faster)
- ✅ Implemented analysis caching (saves 6 min per cache hit)
- ✅ 70% token reduction per activation
- ✅ 15% speed improvement (17 min vs 19 min)

**See:** `optimize.plan.md` for complete optimization details

---

**Created:** 2025-11-08  
**Purpose:** Enable rapid creation of high-quality skills from tool documentation
