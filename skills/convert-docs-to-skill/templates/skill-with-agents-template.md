---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}. Uses specialized agents for {{AGENT_PURPOSES}}. USE WHEN user says {{TRIGGER_PHRASES}}. Keywords - {{KEYWORDS}}.
---

# {{TOOL_NAME}} - Agent-Powered Workflow

{{TOOL_OVERVIEW}}

**Agent-Enhanced Features:**
- {{AGENT_FEATURE_1}}
- {{AGENT_FEATURE_2}}
- {{AGENT_FEATURE_3}}

## Available Agents

This skill uses specialized agents for different phases of work:

### {{AGENT_1_NAME}} Agent
**Model:** {{AGENT_1_MODEL}} (e.g., sonnet, haiku, opus)
**Purpose:** {{AGENT_1_PURPOSE}}
**Tools:** {{AGENT_1_TOOLS}}
**Use for:** {{AGENT_1_USE_CASES}}

**When to use:**
- {{AGENT_1_TRIGGER_1}}
- {{AGENT_1_TRIGGER_2}}

**Example:**
```typescript
// Agent orchestration handled by skill
// User just requests: "{{AGENT_1_EXAMPLE_REQUEST}}"
```

### {{AGENT_2_NAME}} Agent
**Model:** {{AGENT_2_MODEL}}
**Purpose:** {{AGENT_2_PURPOSE}}
**Tools:** {{AGENT_2_TOOLS}}
**Use for:** {{AGENT_2_USE_CASES}}

**When to use:**
- {{AGENT_2_TRIGGER_1}}
- {{AGENT_2_TRIGGER_2}}

### {{AGENT_3_NAME}} Agent (Optional)
**Model:** {{AGENT_3_MODEL}}
**Purpose:** {{AGENT_3_PURPOSE}}
**Tools:** {{AGENT_3_TOOLS}}
**Use for:** {{AGENT_3_USE_CASES}}

## Agent Orchestration Patterns

### Pattern 1: Sequential Workflow

For tasks requiring ordered phases:

```
User Request
    ↓
{{AGENT_1_NAME}} Agent (Phase 1)
    ↓
{{AGENT_2_NAME}} Agent (Phase 2)
    ↓
{{AGENT_3_NAME}} Agent (Phase 3)
    ↓
Result
```

**Example workflow:**
1. **{{AGENT_1_NAME}}**: {{PHASE_1_DESCRIPTION}}
2. **{{AGENT_2_NAME}}**: {{PHASE_2_DESCRIPTION}}
3. **{{AGENT_3_NAME}}**: {{PHASE_3_DESCRIPTION}}

**When to use:**
- {{SEQUENTIAL_USE_CASE_1}}
- {{SEQUENTIAL_USE_CASE_2}}

### Pattern 2: Parallel Execution

For independent analysis tasks (up to 10 agents):

```
User Request
    ↓
┌───────────┬───────────┬───────────┐
│ Agent 1   │ Agent 2   │ Agent 3   │
│ {{TASK_1}}│ {{TASK_2}}│ {{TASK_3}}│
└───────────┴───────────┴───────────┘
    ↓           ↓           ↓
        Aggregate Results
              ↓
           Combined Result
```

**When to use:**
- {{PARALLEL_USE_CASE_1}}
- {{PARALLEL_USE_CASE_2}}

**Parallelizable tasks:**
- {{PARALLEL_TASK_1}}
- {{PARALLEL_TASK_2}}
- {{PARALLEL_TASK_3}}

**NOT parallelizable:**
- {{SEQUENTIAL_TASK_1}} (requires shared state)
- {{SEQUENTIAL_TASK_2}} (depends on previous results)

### Pattern 3: Conditional Routing

Route to different agents based on task type:

```
User Request
    ↓
Task Analysis
    ↓
┌─────────┴─────────┬─────────┐
│                   │         │
If {{CONDITION_1}}  If {{CONDITION_2}}  Otherwise
↓                   ↓         ↓
{{AGENT_1_NAME}}    {{AGENT_2_NAME}}    {{AGENT_3_NAME}}
```

**Example routing:**
- If user requests {{CONDITION_1}} → Use {{AGENT_1_NAME}}
- If user requests {{CONDITION_2}} → Use {{AGENT_2_NAME}}
- Otherwise → Use {{AGENT_3_NAME}}

## Agent Configuration

### Agent Tool Permissions

Each agent has specific tool access for safety:

#### {{AGENT_1_NAME}} Agent
```typescript
allowedTools: [{{AGENT_1_ALLOWED_TOOLS}}]
disallowedTools: [{{AGENT_1_DISALLOWED_TOOLS}}]
```

**Why:**
- {{AGENT_1_PERMISSION_REASON_1}}
- {{AGENT_1_PERMISSION_REASON_2}}

#### {{AGENT_2_NAME}} Agent
```typescript
allowedTools: [{{AGENT_2_ALLOWED_TOOLS}}]
disallowedTools: [{{AGENT_2_DISALLOWED_TOOLS}}]
```

**Why:**
- {{AGENT_2_PERMISSION_REASON_1}}
- {{AGENT_2_PERMISSION_REASON_2}}

### Agent System Prompts

Each agent has specialized instructions:

#### {{AGENT_1_NAME}} System Prompt
```
{{AGENT_1_SYSTEM_PROMPT}}
```

#### {{AGENT_2_NAME}} System Prompt
```
{{AGENT_2_SYSTEM_PROMPT}}
```

## Quick Start

{{#IF_HAS_PREREQUISITES}}
### Prerequisites

{{PREREQUISITES_TEXT}}

**First-time setup:**
```bash
{{SETUP_COMMANDS}}
```
{{/IF_HAS_PREREQUISITES}}

### Basic Usage (Single Agent)

```bash
# Agent automatically selected based on request
{{BASIC_EXAMPLE_COMMAND}}
```

**What happens:**
1. Request analyzed
2. {{AGENT_NAME}} agent activated
3. {{AGENT_ACTION_1}}
4. {{AGENT_ACTION_2}}
5. Result returned

### Advanced Usage (Multi-Agent)

```bash
# Parallel analysis
{{PARALLEL_EXAMPLE_COMMAND}}
```

**What happens:**
1. Request split into {{N}} parallel tasks
2. {{N}} agents launched simultaneously
3. Results aggregated
4. Combined analysis returned

## Core Tasks

### Task 1: {{TASK_1_NAME}}

**Agent used:** {{TASK_1_AGENT}}

```bash
{{TASK_1_COMMAND}}
```

**Agent workflow:**
1. {{TASK_1_STEP_1}}
2. {{TASK_1_STEP_2}}
3. {{TASK_1_STEP_3}}

### Task 2: {{TASK_2_NAME}}

**Agents used:** {{TASK_2_AGENTS}} (parallel)

```bash
{{TASK_2_COMMAND}}
```

**Agent workflow:**
1. Launch {{N}} {{AGENT_NAME}} agents in parallel
2. Each analyzes {{ANALYSIS_SCOPE}}
3. Aggregate findings
4. Return combined result

### Task 3: {{TASK_3_NAME}}

**Agents used:** {{TASK_3_AGENTS}} (sequential)

```bash
{{TASK_3_COMMAND}}
```

**Agent workflow:**
1. {{AGENT_1_NAME}}: {{AGENT_1_ACTION}}
2. {{AGENT_2_NAME}}: {{AGENT_2_ACTION}}
3. {{AGENT_3_NAME}}: {{AGENT_3_ACTION}}

## Agent Collaboration Protocol

### Shared State Management

**Between agents:**
- {{STATE_ITEM_1}}: {{STATE_DESCRIPTION_1}}
- {{STATE_ITEM_2}}: {{STATE_DESCRIPTION_2}}

**State persistence:**
```
{{STATE_STORAGE_LOCATION}}
```

### Agent Communication

Agents communicate through:
1. **Handoff messages**: {{HANDOFF_DESCRIPTION}}
2. **Shared artifacts**: {{ARTIFACT_DESCRIPTION}}
3. **Status updates**: {{STATUS_DESCRIPTION}}

### Error Handling

**Agent failures:**
- {{ERROR_SCENARIO_1}} → {{ERROR_RESPONSE_1}}
- {{ERROR_SCENARIO_2}} → {{ERROR_RESPONSE_2}}

**Retry logic:**
```
If agent fails:
  1. {{RETRY_STEP_1}}
  2. {{RETRY_STEP_2}}
  3. {{RETRY_STEP_3}}
```

## Agent Performance Optimization

### When to Use Parallel Agents

✅ **Good for parallel:**
- {{PARALLEL_GOOD_1}}
- {{PARALLEL_GOOD_2}}
- {{PARALLEL_GOOD_3}}

❌ **Bad for parallel:**
- {{PARALLEL_BAD_1}} (requires sequential order)
- {{PARALLEL_BAD_2}} (shared mutable state)

### Model Selection Per Agent

| Agent | Model | Why |
|-------|-------|-----|
| {{AGENT_1_NAME}} | {{AGENT_1_MODEL}} | {{AGENT_1_MODEL_REASON}} |
| {{AGENT_2_NAME}} | {{AGENT_2_MODEL}} | {{AGENT_2_MODEL_REASON}} |
| {{AGENT_3_NAME}} | {{AGENT_3_MODEL}} | {{AGENT_3_MODEL_REASON}} |

**Cost optimization:**
- Use Haiku for {{HAIKU_USE_CASES}}
- Use Sonnet for {{SONNET_USE_CASES}}
- Use Opus for {{OPUS_USE_CASES}}

## Proven Patterns

{{#IF_HAS_MANDATORY_WORKFLOW}}
**⚠️ MANDATORY:** {{MANDATORY_WORKFLOW_TEXT}}
{{/IF_HAS_MANDATORY_WORKFLOW}}

### Pattern: {{PATTERN_1_NAME}}

**Agents:** {{PATTERN_1_AGENTS}}

```bash
#!/bin/bash
# {{PATTERN_1_DESCRIPTION}}

{{PATTERN_1_COMMANDS}}
```

**Agent execution:**
1. {{PATTERN_1_AGENT_STEP_1}}
2. {{PATTERN_1_AGENT_STEP_2}}
3. {{PATTERN_1_AGENT_STEP_3}}

**When to use:**
- {{PATTERN_1_USE_CASE_1}}
- {{PATTERN_1_USE_CASE_2}}

### Pattern: {{PATTERN_2_NAME}}

**Agents:** {{PATTERN_2_AGENTS}} (parallel)

```bash
{{PATTERN_2_COMMANDS}}
```

**Agent execution:**
```
{{PATTERN_2_PARALLEL_DIAGRAM}}
```

## Troubleshooting

### Agent Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Agent not activating | {{ISSUE_1_CAUSE}} | {{ISSUE_1_SOLUTION}} |
| Slow execution | {{ISSUE_2_CAUSE}} | {{ISSUE_2_SOLUTION}} |
| Incomplete results | {{ISSUE_3_CAUSE}} | {{ISSUE_3_SOLUTION}} |

### Agent Selection

**Wrong agent activated?**
1. Check request phrasing: {{AGENT_SELECTION_TIP_1}}
2. Verify triggers: {{AGENT_SELECTION_TIP_2}}
3. Use explicit routing: {{AGENT_SELECTION_TIP_3}}

## Helper Scripts

{{#IF_HAS_AGENT_SCRIPTS}}
### Agent Management Scripts

**Launch agent manually:**
```bash
{{AGENT_LAUNCH_SCRIPT}}
```

**Monitor agent progress:**
```bash
{{AGENT_MONITOR_SCRIPT}}
```

**Debug agent execution:**
```bash
{{AGENT_DEBUG_SCRIPT}}
```
{{/IF_HAS_AGENT_SCRIPTS}}

## Configuration Files

### Agent Definitions

Located in: `{{AGENT_CONFIG_PATH}}`

```typescript
// {{AGENT_1_NAME}} configuration
const {{AGENT_1_VAR}}: AgentDefinition = {
  name: "{{AGENT_1_NAME}}",
  model: "{{AGENT_1_MODEL}}",
  systemPrompt: "{{AGENT_1_SYSTEM_PROMPT}}",
  allowedTools: [{{AGENT_1_ALLOWED_TOOLS}}],
  workingDirectory: "{{WORKING_DIR}}"
};
```

### Orchestration Config

```yaml
# {{ORCHESTRATION_CONFIG_FILE}}
agents:
  {{AGENT_1_NAME}}:
    enabled: true
    max_parallel: {{AGENT_1_MAX_PARALLEL}}
    timeout: {{AGENT_1_TIMEOUT}}

  {{AGENT_2_NAME}}:
    enabled: true
    max_parallel: {{AGENT_2_MAX_PARALLEL}}
    timeout: {{AGENT_2_TIMEOUT}}

routing:
  default_agent: {{DEFAULT_AGENT}}
  conditional_routing:
    - condition: {{ROUTING_CONDITION_1}}
      agent: {{ROUTING_AGENT_1}}
    - condition: {{ROUTING_CONDITION_2}}
      agent: {{ROUTING_AGENT_2}}
```

## Common Workflows

### Workflow 1: Single Agent Task

```
1. User request: "{{WORKFLOW_1_REQUEST}}"
2. {{AGENT_NAME}} agent activates
3. Executes: {{WORKFLOW_1_ACTION}}
4. Returns: {{WORKFLOW_1_RESULT}}
```

### Workflow 2: Multi-Agent Parallel

```
1. User request: "{{WORKFLOW_2_REQUEST}}"
2. Launch {{N}} agents in parallel
3. Each processes: {{WORKFLOW_2_SCOPE}}
4. Aggregate results
5. Return: {{WORKFLOW_2_RESULT}}
```

### Workflow 3: Sequential Pipeline

```
1. User request: "{{WORKFLOW_3_REQUEST}}"
2. {{AGENT_1_NAME}}: {{WORKFLOW_3_PHASE_1}}
3. {{AGENT_2_NAME}}: {{WORKFLOW_3_PHASE_2}}
4. {{AGENT_3_NAME}}: {{WORKFLOW_3_PHASE_3}}
5. Return: {{WORKFLOW_3_RESULT}}
```

## Tips

**Agent Selection:**
- Request phrasing determines agent routing
- Be specific: {{AGENT_SELECTION_TIP}}
- Use keywords: {{AGENT_KEYWORDS}}

**Performance:**
- Parallel for {{PARALLEL_PERFORMANCE_TIP}}
- Sequential for {{SEQUENTIAL_PERFORMANCE_TIP}}
- Monitor with: {{MONITORING_TIP}}

**Cost Optimization:**
- Use Haiku when possible: {{HAIKU_TIP}}
- Reserve Opus for: {{OPUS_TIP}}
- Batch requests: {{BATCH_TIP}}

**Debugging:**
- Check agent logs: {{LOG_LOCATION}}
- Verify tool permissions: {{PERMISSION_CHECK}}
- Test with single agent first: {{TEST_TIP}}

## Advanced: Custom Agent Orchestration

For advanced users who want to customize agent behavior:

```typescript
// Example: Custom agent orchestration
import { query } from "@anthropic-ai/claude-agent-sdk";

async function customOrchestration(request: string) {
  // Phase 1: {{CUSTOM_PHASE_1}}
  const analysis = await runAgent({
    name: "{{AGENT_1_NAME}}",
    prompt: request,
    model: "{{AGENT_1_MODEL}}",
    allowedTools: [{{AGENT_1_TOOLS}}]
  });

  // Phase 2: {{CUSTOM_PHASE_2}} (parallel)
  const tasks = analysis.taskList;
  const results = await Promise.all(
    tasks.map(task => runAgent({
      name: "{{AGENT_2_NAME}}",
      prompt: task,
      model: "{{AGENT_2_MODEL}}",
      allowedTools: [{{AGENT_2_TOOLS}}]
    }))
  );

  // Phase 3: {{CUSTOM_PHASE_3}}
  return aggregateResults(results);
}
```

## See Also

**Related skills:**
- {{RELATED_SKILL_1}} - {{RELATED_DESCRIPTION_1}}
- {{RELATED_SKILL_2}} - {{RELATED_DESCRIPTION_2}}

**References:**
- [Agent SDK Documentation]({{AGENT_SDK_DOCS}})
- [Tool Permissions Guide]({{TOOL_PERMISSIONS_GUIDE}})
- {{ADDITIONAL_REFERENCE}}

---

**Agent Architecture Summary:**
```
{{ARCHITECTURE_DIAGRAM}}
```

**Key Principles:**
1. {{PRINCIPLE_1}}
2. {{PRINCIPLE_2}}
3. {{PRINCIPLE_3}}
