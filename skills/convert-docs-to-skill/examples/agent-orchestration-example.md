# Agent-Powered Skill Creation - Example Workflow

This example demonstrates using specialized agents to accelerate the 6-phase skill creation process.

## Overview

**Traditional workflow:** Single Claude instance processes each phase sequentially

**Agent-powered workflow:** Multiple specialized agents work in parallel where possible

**Speedup:** 3-5x faster for complex documentation

## Agent Architecture

### Agent 1: Documentation Analyzer Agent
**Model:** Sonnet
**Purpose:** Extract patterns, commands, and workflows from documentation
**Tools:** Read, Grep, Glob
**Parallel:** Yes (can analyze multiple doc pages simultaneously)

### Agent 2: Pitfall Hunter Agent
**Model:** Sonnet
**Purpose:** Identify gotchas, warnings, and error scenarios
**Tools:** Read, WebSearch (for known issues)
**Parallel:** Yes (can scan different doc sections independently)

### Agent 3: Script Generator Agent
**Model:** Haiku
**Purpose:** Create helper scripts from templates
**Tools:** Read, Write
**Parallel:** Yes (can generate multiple scripts simultaneously)

### Agent 4: Template Populator Agent
**Model:** Haiku
**Purpose:** Fill config templates with doc-specific values
**Tools:** Read, Write
**Parallel:** Yes (can create multiple templates simultaneously)

### Agent 5: Integration Tester Agent
**Model:** Sonnet
**Purpose:** Test generated skill components
**Tools:** Read, Bash
**Parallel:** No (sequential testing required)

## Phase-by-Phase Agent Usage

### Phase 1: Documentation Gathering

**Agent:** None (user provides docs or using-crawl4ai-cli extracts)

**Traditional:**
```bash
crwl https://docs.tool.com/guide -o markdown > docs.md
```

**Agent-powered (parallel multi-page):**
```bash
# Launch 5 parallel agents to extract 5 pages simultaneously
docs=(
  "https://docs.tool.com/intro"
  "https://docs.tool.com/usage"
  "https://docs.tool.com/config"
  "https://docs.tool.com/advanced"
  "https://docs.tool.com/api"
)

for doc in "${docs[@]}"; do
  crwl "$doc" -o markdown > "$(basename $doc).md" &
done
wait

# Combine
cat *.md > complete_docs.md
```

**Speedup:** 5x (5 pages in parallel vs sequential)

### Phase 2: Documentation Analysis

**Agents Used:** Documentation Analyzer (multiple instances) + Pitfall Hunter (multiple instances)

**Parallelization:**
```
complete_docs.md
    ↓
Split into sections
    ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Analyzer 1  │ Analyzer 2  │ Analyzer 3  │ Analyzer 4  │
│ Intro +     │ Usage +     │ Config +    │ Advanced +  │
│ Tool        │ Command     │ Config      │ Best        │
│ Overview    │ Patterns    │ Patterns    │ Practices   │
└─────────────┴─────────────┴─────────────┴─────────────┘
    ↓           ↓             ↓             ↓
        Aggregate Analysis Results
                  ↓
        ┌─────────────────┬─────────────────┐
        │ Pitfall Hunter 1│ Pitfall Hunter 2│
        │ Common Errors   │ Known Issues    │
        │ from Docs       │ from Web        │
        └─────────────────┴─────────────────┘
                  ↓
          Complete Analysis
```

**Traditional approach:**
```
Time: ~10-15 minutes for complex docs
Process: Read all docs → Identify patterns → Extract workflows → Find pitfalls
```

**Agent-powered approach:**
```typescript
// Pseudo-code showing agent orchestration

// Step 1: Split documentation into analyzable chunks
const sections = splitDocumentation(docs, {
  maxSections: 4,
  criteriaBy: "topic"
});

// Step 2: Launch parallel documentation analyzer agents
const analysisPromises = sections.map(section =>
  query({
    prompt: `Analyze this documentation section and extract:
      1. Tool/command patterns
      2. Common workflows
      3. Configuration options
      4. Key examples

      Section: ${section}`,
    options: {
      model: "sonnet",
      allowedTools: ["Read"],
      systemPrompt: "You are a documentation analysis expert. Extract structured patterns and workflows from technical documentation."
    }
  })
);

// Step 3: Simultaneously launch pitfall hunter agents
const pitfallPromises = [
  query({
    prompt: `Analyze ${tool} documentation for warnings, gotchas, and common mistakes.`,
    options: {
      model: "sonnet",
      allowedTools: ["Read", "WebSearch"]
    }
  }),
  query({
    prompt: `Search web for common ${tool} issues and error patterns.`,
    options: {
      model: "sonnet",
      allowedTools: ["WebSearch"]
    }
  })
];

// Step 4: Await all agents
const [analyses, pitfalls] = await Promise.all([
  Promise.all(analysisPromises),
  Promise.all(pitfallPromises)
]);

// Step 5: Aggregate results
const completeAnalysis = aggregateAnalyses(analyses, pitfalls);
```

**Speedup:** 3-4x (4 analyzer agents + 2 pitfall agents in parallel)

**Output:**
```markdown
# Tool Analysis

## Tool Overview (from Analyzer 1)
...

## Command Patterns (from Analyzer 2)
...

## Configuration (from Analyzer 3)
...

## Best Practices (from Analyzer 4)
...

## Pitfalls & Gotchas
### From Documentation (Pitfall Hunter 1)
...

### From Community (Pitfall Hunter 2 - web search)
...
```

### Phase 3: Skill Design Brainstorming

**Agents Used:** None (human/Claude decides component structure based on analysis)

**Traditional:** Review analysis → Design components → Decide on scripts/templates

**Agent-powered:** Same (this phase benefits from thoroughness, not parallelization)

### Phase 4: Artifact Creation

**Agents Used:** Script Generator (multiple) + Template Populator (multiple)

**Parallelization:**
```
Design Document
    ↓
Component List
    ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Generator 1  │ Generator 2  │ Generator 3  │ Generator 4  │
│ setup.sh     │ validate.py  │ generate.py  │ inspect.sh   │
└──────────────┴──────────────┴──────────────┴──────────────┘
    ↓              ↓              ↓              ↓
        Generated Helper Scripts
                  ↓
        ┌──────────────┬──────────────┬──────────────┐
        │ Populator 1  │ Populator 2  │ Populator 3  │
        │ basic.yml    │ advanced.yml │ dynamic.yml  │
        └──────────────┴──────────────┴──────────────┘
                  ↓
        Generated Templates + Scripts
```

**Agent orchestration:**
```typescript
// Design specifies needed components
const componentsNeeded = {
  scripts: ["setup.sh", "validate.py", "generate.py", "inspect.sh"],
  templates: ["basic.yml", "advanced.yml", "dynamic.yml"]
};

// Generate scripts in parallel
const scriptPromises = componentsNeeded.scripts.map(scriptName =>
  query({
    prompt: `Generate ${scriptName} for ${tool} based on this design:
      ${design[scriptName]}

      Use template: ${getTemplate(scriptName)}
      Fill with tool-specific logic.`,
    options: {
      model: "haiku", // Fast generation for well-defined tasks
      allowedTools: ["Read", "Write"],
      systemPrompt: "You are a script generation expert. Create production-ready helper scripts from templates."
    }
  })
);

// Generate templates in parallel
const templatePromises = componentsNeeded.templates.map(templateName =>
  query({
    prompt: `Create ${templateName} config template for ${tool}:
      Settings: ${design.configOptions[templateName]}
      Scenario: ${design.scenarios[templateName]}`,
    options: {
      model: "haiku",
      allowedTools: ["Read", "Write"]
    }
  })
);

// All artifacts generated simultaneously
await Promise.all([...scriptPromises, ...templatePromises]);
```

**Speedup:** 5-7x (7 parallel generators vs sequential)

**Example output:**
```bash
# All generated simultaneously
scripts/
├── setup.sh ✅ (Generator 1 - 30 seconds)
├── validate.py ✅ (Generator 2 - 30 seconds)
├── generate.py ✅ (Generator 3 - 30 seconds)
└── inspect.sh ✅ (Generator 4 - 30 seconds)

templates/
├── basic.yml ✅ (Populator 1 - 20 seconds)
├── advanced.yml ✅ (Populator 2 - 20 seconds)
└── dynamic.yml ✅ (Populator 3 - 20 seconds)

Total time: ~30 seconds (vs ~3.5 minutes sequential)
```

### Phase 5: SKILL.md Creation

**Agents Used:** None (requires holistic view of all components)

**Traditional:** Write complete SKILL.md with all sections

**Agent-powered:** Same (main SKILL.md benefits from single coherent narrative)

**Potential parallelization (optional):**
Could use agents to generate individual reference docs simultaneously:
```typescript
// Generate reference docs in parallel
const refPromises = [
  query({ prompt: "Generate cli-reference.md from analysis" }),
  query({ prompt: "Generate config-reference.md from templates" }),
  query({ prompt: "Generate patterns.md from workflows" }),
  query({ prompt: "Generate troubleshooting.md from pitfalls" })
];

await Promise.all(refPromises);
```

### Phase 6: Integration & Testing

**Agents Used:** Integration Tester (sequential - must test in order)

**Traditional:** Test each component manually

**Agent-powered:**
```typescript
// Sequential testing with single agent (can't parallelize)
const tester = createAgent({
  name: "Integration Tester",
  model: "sonnet",
  allowedTools: ["Read", "Bash"]
});

// Test sequence
const tests = [
  "Test skill activation with natural language",
  "Run all helper scripts",
  "Validate all templates",
  "Execute proven patterns",
  "Check all file references"
];

for (const test of tests) {
  const result = await tester.query({ prompt: test });
  if (result.failed) {
    await tester.query({ prompt: "Debug and fix the issue" });
  }
}
```

**Speedup:** Minimal (testing must be sequential)

## Complete Example: Creating `ripgrep` Skill with Agents

### Input
```
User: "Create a skill for ripgrep from https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md"
```

### Execution Timeline

**Phase 1: Docs (30 seconds)**
```
Extract GUIDE.md using crawl4ai
```

**Phase 2: Analysis (2 minutes with agents vs 8 minutes traditional)**
```
Launch 4 analyzer agents + 2 pitfall agents in parallel
Agent 1: Tool overview
Agent 2: Command patterns (-i, -l, -n, etc.)
Agent 3: Workflows (search, filter, context)
Agent 4: Best practices
Agent 5: Explicit warnings from docs
Agent 6: Web search for common ripgrep issues
```

**Phase 3: Design (3 minutes)**
```
Human/Claude reviews analysis
Designs: 3 scripts + 3 templates + 2 guardrails
```

**Phase 4: Generation (1 minute with agents vs 5 minutes traditional)**
```
Launch 6 generator agents in parallel
Agents 1-3: Generate helper scripts
Agents 4-6: Generate config templates
```

**Phase 5: SKILL.md (5 minutes)**
```
Write main SKILL.md
Optionally: 4 agents generate reference docs in parallel (1 min vs 4 min)
```

**Phase 6: Testing (3 minutes)**
```
Sequential testing with agent
```

**Total Time:**
- **With Agents:** ~14 minutes (30s + 2m + 3m + 1m + 5m + 3m)
- **Traditional:** ~29 minutes (30s + 8m + 3m + 5m + 5m + 3m + 5m)
- **Speedup:** ~2x overall

**Most time saved in:** Phases 2 (analysis) and 4 (generation)

## Agent Configuration Files

### analyzer-agent.ts
```typescript
export const documentationAnalyzer: AgentDefinition = {
  name: "Documentation Analyzer",
  model: "sonnet",
  systemPrompt: `You are an expert at analyzing technical documentation.

  Extract:
  - Tool capabilities and purpose
  - Command patterns and syntax
  - Common workflows
  - Configuration options
  - Key examples

  Be systematic and thorough.`,
  allowedTools: ["Read"],
  workingDirectory: process.cwd()
};
```

### pitfall-hunter-agent.ts
```typescript
export const pitfallHunter: AgentDefinition = {
  name: "Pitfall Hunter",
  model: "sonnet",
  systemPrompt: `You are an expert at identifying potential issues and gotchas.

  Look for:
  - Explicit warnings in docs
  - Common mistakes mentioned
  - Error-prone operations
  - Prerequisites often missed
  - Known issues and workarounds

  Search web for real-world problems users encounter.`,
  allowedTools: ["Read", "WebSearch"],
  workingDirectory: process.cwd()
};
```

### script-generator-agent.ts
```typescript
export const scriptGenerator: AgentDefinition = {
  name: "Script Generator",
  model: "haiku", // Fast for well-defined tasks
  systemPrompt: `You are an expert at generating helper scripts from templates.

  Create production-ready scripts that:
  - Follow template structure
  - Include error handling
  - Have clear usage messages
  - Use color-coded output
  - Validate inputs

  Make scripts user-friendly and robust.`,
  allowedTools: ["Read", "Write"],
  workingDirectory: process.cwd()
};
```

## Benefits of Agent-Powered Workflow

### Speed
- **2-5x faster** for complex documentation
- **Most gain** in analysis and generation phases
- **Parallel execution** where tasks are independent

### Quality
- **Multiple perspectives** from different agents
- **Specialized focus** (analysis vs generation vs testing)
- **Thorough coverage** (parallel agents can examine different aspects)

### Cost Efficiency
- **Use Haiku** for well-defined generation tasks
- **Use Sonnet** for complex analysis
- **Parallel execution** doesn't increase token usage much

## When to Use Agents

### ✅ Use Agents For:
- Large documentation sets (multiple pages)
- Complex tools (many flags, options, workflows)
- Multiple script/template generation
- Parallel analysis needs

### ❌ Don't Use Agents For:
- Simple tools (single page docs)
- Quick skills (minimal scripts/templates)
- Tasks requiring holistic view (SKILL.md main content)
- Sequential workflows (testing)

## Orchestration Best Practices

1. **Parallelize independent tasks**: Analysis of different doc sections
2. **Keep sequential tasks sequential**: Testing must be ordered
3. **Use appropriate models**: Haiku for generation, Sonnet for analysis
4. **Aggregate results carefully**: Ensure consistency across parallel outputs
5. **Handle failures**: One agent failure shouldn't block others

---

**Summary: Agents accelerate skill creation by 2-5x through parallel analysis and generation, while maintaining quality through specialized focus.**
