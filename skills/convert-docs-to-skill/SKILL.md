---
name: convert-docs-to-skill
short_description: >-
  Transform documentation into comprehensive PAI skills with helper scripts,
  templates, and guardrails. Analyzes docs (markdown or URLs), deduces
  workflows, generates artifacts. Supports agent-powered parallel execution for
  2-5x speedup.
description: >-
  Create comprehensive PAI skills from tool/CLI/API documentation. Analyzes docs
  (markdown or URLs via crawl4ai), deduces workflows, generates helper
  scripts/templates/guardrails, and builds complete skill packages. Supports
  agent-powered parallel execution for 2-5x speedup. USE WHEN user says 'create
  skill from docs', 'build skill for [tool]', 'turn documentation into skill',
  or provides documentation to transform into a skill.
when_to_use: >
  Use when user says 'create skill from docs', 'build skill for [tool]', 'turn
  documentation into skill', or provides

  documentation to transform into a skill. Analyzes docs (markdown or URLs),
  deduces workflows, generates helpers/templates/guardrails.
version: 1.0.0
category: agents-and-skills
---

# Skill Creator from Documentation

Transform documentation for tools, CLIs, APIs, or libraries into comprehensive, production-ready PAI skills with helper scripts, templates, and guardrails.

## Execution Methods

### Method 1: Agent-Powered (Claude Code Active) ⚡ RECOMMENDED
**This skill uses Task tool with optimized agent architecture**

When activated in Claude Code:
- **5 specialized agents** (down from 16-19 in original design, 7 in previous consolidation)
- Phase 2: 2 agents in parallel (Analyzer-Designer + Pitfall Hunter) (~4 min vs ~12 min sequential)
- Phase 4: 2 generator agents in parallel (~2 min vs ~5 min sequential)
- Total time: ~17 minutes (vs ~31 min manual, ~19 min with 7 agents)
- Cost: ~$0.06 (optimized for efficiency)
- **74% complexity reduction** from original, **29% reduction** from previous consolidation

**Improvement:** 2 minutes faster than previous consolidation, 5 agents vs 7

**Use when:** Working in Claude Code and want optimal balance of speed and maintainability

### Method 2: Automated Sequential (Python Standalone)
**For automation without Claude Code active**

```bash
python ~/.claude/skills/skill-creator-from-docs/scripts/create_skill.py docs.md --skill-name tool
```

- Sequential 6-phase pipeline
- No API costs (uses local file processing where possible)
- Reliable, predictable execution
- Resume support if interrupted

**Use when:** Want automation without active Claude session, or prefer deterministic execution

## When to Activate This Skill

- "Create a skill from [tool] documentation"
- "Build a skill for [CLI tool]"
- "Turn this documentation into a skill"
- User provides documentation (markdown or URLs) and wants a skill
- "Generate a skill that helps me use [API/library]"
- "Make [tool] easier to use with a skill"

## Core Workflow

### Phase 1: Documentation Gathering

**Agent-Powered Execution (Parallel):**

When this skill is active in Claude Code, spawn documentation crawler agent:

```
Launch documentation gathering agent:
- Agent: Documentation Crawler
  - Extracts docs from URLs using using-crawl4ai-cli
  - Handles JavaScript-heavy documentation
  - Manages multi-page documentation
  - Combines pages into cohesive document
  - Cleans navigation/UI artifacts

Agent uses subagent_type="general-purpose" with bash, read, write tools
Handles: Single pages, multi-page docs, dynamic sites, API docs
```

**Fallback Execution (Manual):**

If agent unavailable, extract manually:

1. **Markdown Documentation (Direct)**
   ```
   User provides markdown content directly
   ```

2. **Documentation URLs (Extract with using-crawl4ai-cli)**
   ```bash
   # For single page
   crwl https://docs.example.com/tool -o markdown > docs.md

   # For multiple pages
   crwl https://docs.example.com/guide/page1 -o markdown > part1.md
   crwl https://docs.example.com/guide/page2 -o markdown > part2.md
   
   # For JavaScript-heavy docs
   crwl https://docs.example.com \
     --bypass-cache \
     -c "wait_until=networkidle,delay_before_return_html=2" \
     -o markdown > docs.md
   ```

3. **Mixed Approach**
   Combine crawled content with user-provided context

**Deliverable:** Complete documentation in markdown format

### Phase 2: Documentation Analysis & Component Design (Merged)

**Agent-Powered Execution (Optimized - Parallel):**

When this skill is active in Claude Code, spawn TWO agents in parallel using Task tool:

```
Launch in parallel (2 agents):

Agent 1: Comprehensive Analyzer & Designer
  - Analyzes documentation AND designs components in single pass
  - Extracts: Tool overview, command/API patterns, workflows,
    configuration, best practices, key examples
  - Designs: Helper scripts, config templates, guardrails, checklists,
    reference structure
  - Model: Sonnet
  - Tools: read, write, grep
  - Output: Complete analysis + component design document
  - Efficiency: Design informed by fresh analysis context

Agent 2: Comprehensive Pitfall Hunter
  - Unified risk assessment from docs + web search
  - Identifies: Warnings, common mistakes, error-prone operations,
    prerequisites, community issues, recovery procedures
  - Model: Sonnet
  - Tools: read, grep, websearch
  - Output: Risk matrix with severity × frequency prioritization

Each agent uses subagent_type="general-purpose"
Speedup: ~3x faster than sequential (4 min vs 12 min for separate phases)
Agent reduction: 29% fewer agents (5 total vs 7) for easier maintenance
Time saved: 2 minutes (from 19 min → 17 min)
```

**Fallback Execution (Sequential):**

If agents unavailable, analyze and design sequentially:

1. **Tool Overview** - What it does, use cases, capabilities
2. **Command/API Patterns** - Common commands, flags, options
3. **Workflows** - Standard workflows, multi-step processes
4. **Pitfalls & Gotchas** - Warnings, error-prone areas, common mistakes
5. **Best Practices** - Recommended approaches, performance tips
6. **Component Design** - Helper scripts, templates, guardrails, checklists

**Deliverable:** Complete analysis + component design document

### Phase 4: Artifact Creation

**Agent-Powered Execution (Consolidated - Parallel):**

When this skill is active in Claude Code, spawn TWO generator agents in parallel:

```
Create directory structure first, then launch in parallel (2 agents):

Agent 1: Script & Automation Generator
  - Generates ALL helper scripts sequentially
  - Creates: setup.sh, validate_*.py, generate_*.py, inspect_*.sh, test utilities
  - Model: Haiku (fast for well-defined generation)
  - Tools: read, write
  - Output: All helper scripts + scripts/README.md
  - Sequential generation maintains consistency across scripts

Agent 2: Configuration & Documentation Generator
  - Generates ALL config templates and reference docs sequentially
  - Creates: Config templates (basic, advanced, scenario-specific)
  - Creates: Reference docs (CLI/API, config, patterns, troubleshooting, scripts/README)
  - Model: Haiku (fast template/doc generation)
  - Tools: read, write
  - Output: All templates + all reference documentation
  - Sequential generation ensures cross-references are consistent

Each agent uses subagent_type="general-purpose"

Speedup: ~2.5x faster than sequential (2 min vs 5 min)
Agent reduction: 75% fewer agents (2 vs 8+) for easier maintenance
Sequential generation within agents ensures consistency
```

**Fallback Execution (Sequential):**

If agents unavailable, create sequentially:

1. **Directory Structure** - Create full skill directory layout
2. **Helper Scripts** - Generate from templates (setup, validation, generators)
3. **Config Templates** - Create presets (basic, advanced, specialized)
4. **Reference Docs** - Write CLI, config, patterns, troubleshooting guides

**Deliverable:** Complete skill directory with all artifacts

### Phase 5: SKILL.md Creation

**Write the main SKILL.md file:**

1. **YAML Frontmatter**
   ```yaml
   ---
   name: tool-name
   description: Clear description. USE WHEN triggers. Keywords.
   ---
   ```

2. **Structure** (use template: `templates/tool-skill-SKILL.md.template`)
   - Tool overview
   - Prerequisites (if needed)
   - Quick start
   - Core tasks
   - Command reference
   - Configuration files
   - Proven patterns
   - Troubleshooting
   - Helper scripts
   - Workflow requirements
   - Common workflows
   - Tips

3. **Key Elements**
   - ⚠️ MANDATORY sections for critical workflows
   - Quick reference tables
   - Code examples for every section
   - Links to detailed references
   - Helper script usage

**Deliverable:** Complete SKILL.md file

### Phase 6: Integration & Testing

1. **Add to Global Context**
   Update `~/.claude/global/CLAUDE.md`:
   ```xml
   <skill>
   <name>tool-name</name>
   <description>Your skill description</description>
   <location>user</location>
   </skill>
   ```

2. **Test Activation**
   - Try natural language triggers
   - Verify skill loads correctly
   - Check all file references work

3. **Test Workflows**
   - Run setup scripts
   - Try common commands
   - Test validation scripts
   - Verify templates work

4. **Iterate**
   - Refine based on testing
   - Add missing components
   - Improve documentation

**Deliverable:** Production-ready skill integrated into PAI

## 🚀 Agent Implementation Details

### How Agents Are Spawned

This skill uses the **Task tool** to spawn parallel agents. When Claude Code activates this skill:

**Phase 1 Example - Documentation Extraction:**
```
# Launch documentation crawler agent
Task({
  subagent_type: "general-purpose",
  description: "Extract documentation from URLs",
  prompt: "Extract complete documentation from {urls} using crawl4ai. Handle JavaScript rendering, combine multiple pages, clean artifacts."
})
```

**Phase 2 Example - Parallel Analysis & Design (Optimized):**
```
# Launch 2 agents in parallel
Task({
  subagent_type: "general-purpose",
  description: "Analyze docs and design components in single pass",
  prompt: "Analyze {docs} comprehensively AND design skill components. Extract: tool overview, command patterns, workflows, configuration, best practices, key examples. Then design: helper scripts, config templates, guardrails, checklists, reference structure. Output complete analysis + component design."
})

Task({
  subagent_type: "general-purpose",
  description: "Risk assessment and pitfall identification",
  prompt: "Analyze {docs} for warnings, gotchas, common mistakes, prerequisites. Search web for community-reported issues. Output risk matrix with severity × frequency prioritization."
})
```

**Phase 4 Example - Parallel Generation (Consolidated):**
```
# Launch 2 generator agents in parallel
Task({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Generate all helper scripts",
  prompt: "Generate ALL helper scripts from designs: setup.sh, validate_*.py, generate_*.py, inspect_*.sh. Use templates, include error handling, create scripts/README.md. Sequential generation ensures consistency."
})

Task({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Generate configs and reference docs",
  prompt: "Generate ALL config templates (basic, advanced, scenario-specific) and reference docs (CLI, config, patterns, troubleshooting). Sequential generation ensures cross-references are consistent."
})
```

### Agent Configuration

**Documentation Gathering Agent (Phase 1):**
- Model: Sonnet (handles complex extraction logic)
- Tools: bash, read, write, grep
- Timeout: 10 minutes (documentation can be large)
- Max parallel: 1 agent (sequential extraction)

**Analysis & Design Agents (Phase 2):**
- Agent 1: Comprehensive Analyzer & Designer
  - Model: Sonnet (complex reasoning + design)
  - Tools: Read, Write, Grep
  - Timeout: 6 minutes (longer for combined task)
  - Max parallel: 1 per execution
- Agent 2: Comprehensive Pitfall Hunter
  - Model: Sonnet (complex reasoning + web research)
  - Tools: Read, Grep, WebSearch
  - Timeout: 7 minutes (web searches take longer)
  - Max parallel: 1 per execution
- Phase 2 Orchestration: Launch both agents in parallel (2 total)

**Generator Agents (Phase 4):**
- Model: Haiku (fast generation for well-defined tasks)
- Tools: Read, Write
- Timeout: 3 minutes per agent (handles sequential generation)
- Max parallel: 2 agents (consolidated approach)

### Performance Comparison

**Traditional (manual sequential):**
```
Phase 1: 5 minutes (manual URL extraction)
Phase 2: 8 minutes (analyze all docs sequentially)
Phase 3: 5 minutes (manual component design)
Phase 4: 8 minutes (generate artifacts sequentially)
Phase 5: 5 minutes (write SKILL.md)
Total: ~31 minutes end-to-end
Cost: ~$0.03
```

**Agent-powered (optimized architecture):**
```
Phase 1: 3 minutes (automated extraction with crawler agent)
Phase 2: 4 minutes (2 agents in parallel: Analyzer-Designer + Pitfall Hunter)
Phase 4: 2 minutes (2 generator agents in parallel)
Phase 5: 5 minutes (write SKILL.md)
Phase 6: 3 minutes (integration testing)
Total: ~17 minutes end-to-end ⚡ 1.8x faster than manual
Cost: ~$0.06 (optimized for efficiency)

**Improvement vs previous consolidation:**
- 2 minutes faster (17 min vs 19 min)
- 29% fewer agents (5 vs 7)
- Design informed by fresh analysis context
- Single-pass efficiency (no re-reading analysis)
```

### When Agents Activate

Agents spawn automatically when:
- ✅ This skill is activated in Claude Code
- ✅ Documentation URLs are provided (Phase 1 crawler)
- ✅ Documentation is complex (multiple sections/pages)
- ✅ User requests "quickly" or "fast"

Agents are skipped when:
- ❌ Python standalone mode (use create_skill.py instead)
- ❌ Simple single-page documentation
- ❌ User provides markdown directly (no extraction needed)
- ❌ User explicitly requests sequential execution

**Agent Directory:** `.claude/agents/`  
**See:** `docs/agent-orchestration.md` for complete agent methodology

## Templates Available

Located in `~/.claude/skills/convert-docs-to-skill/templates/`:

- `tool-skill-SKILL.md.template` - Main skill structure
- `helper-script.py.template` - Python helper script
- `helper-script.sh.template` - Bash helper script
- `config-template.yml.template` - Configuration file
- `README-scripts.md.template` - Scripts directory README
- `skill-with-agents-template.md` - Skill with agent support

## Key Principles

1. **Template-Driven**: Use templates for consistency
2. **Helper Scripts Over Manual Steps**: Automate common tasks
3. **Guardrails Prevent Mistakes**: Add ⚠️ MANDATORY workflows
4. **Progressive Disclosure**: SKILL.md = quick ref, references/ = details
5. **Validation Built-In**: Create validation scripts for common errors
6. **Examples Everywhere**: Every section needs working examples
7. **Prerequisites Automated**: Setup scripts handle first-time setup
8. **Troubleshooting Proactive**: Anticipate and document common issues

## Example Pattern: CLI Tool Skill

For a CLI tool, typically create:

**Helper Scripts:**
- `setup.sh` - First-time installation and verification
- `validate_config.py` - Validate configuration files
- `generate_config.py` - Interactive config generator

**Templates:**
- `basic_config.yml` - Simple use case preset
- `advanced_config.yml` - Full-featured preset
- `[specific]_config.yml` - Task-specific presets

**References:**
- `cli-reference.md` - Complete flag documentation
- `config-reference.md` - All configuration options
- `patterns.md` - Proven multi-step workflows
- `troubleshooting.md` - Common issues and solutions

**SKILL.md Sections:**
- Prerequisites with automated setup
- Quick start with minimal example
- Core tasks (common operations)
- Proven patterns with complete examples
- Troubleshooting quick reference table
- Workflow requirements (mandatory steps)

## Supplementary Resources

**For comprehensive methodology:**
- `CLAUDE.md` - Core methodology overview
- `docs/methodology/` - Detailed phase-by-phase guides
- `docs/agent-orchestration.md` - Agent architecture details
- `docs/examples.md` - Real-world examples
- `docs/templates-guide.md` - Template usage patterns
- `docs/best-practices.md` - Quality checklists

**For templates:**
- `templates/` - All available templates
- See `docs/templates-guide.md` for usage

## Common Workflows

### Workflow 1: Create Skill from URLs

```
1. User provides documentation URLs
2. Use using-crawl4ai-cli to extract docs to markdown
3. Analyze extracted documentation
4. Brainstorm components (scripts, templates, guardrails)
5. Create directory structure
6. Generate artifacts from templates
7. Write SKILL.md
8. Test and iterate
```

### Workflow 2: Create Skill from Markdown

```
1. User provides markdown documentation
2. Analyze documentation directly
3. Brainstorm components
4. Create directory structure
5. Generate artifacts from templates
6. Write SKILL.md
7. Test and iterate
```

### Workflow 3: Enhance Existing Skill

```
1. Analyze current skill structure
2. Identify missing components (scripts, templates, refs)
3. Generate missing pieces from templates
4. Update SKILL.md with new components
5. Test enhancements
```

## Tips

**Documentation Analysis:**
- Look for "common mistakes" or "gotchas" sections
- Extract command patterns and flag combinations
- Identify multi-step workflows
- Note prerequisites and dependencies
- Find configuration patterns

**Script Creation:**
- Start with templates
- Focus on automating error-prone steps
- Add validation and clear error messages
- Include usage examples in script help

**Template Design:**
- Create presets for common scenarios
- Add explanatory comments
- Include usage instructions
- Show example output or results

**Guardrails:**
- Mark critical workflows as ⚠️ MANDATORY
- Create validation scripts for common mistakes
- Add prerequisite checks to scripts
- Include "why this prevents failures" sections

**Testing:**
- Test every helper script
- Verify all templates work
- Check all file references
- Try natural language activation
- Validate examples in SKILL.md
