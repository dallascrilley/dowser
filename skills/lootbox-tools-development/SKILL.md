---
name: lootbox-tools-development
short_description: >-
  Develop native TypeScript tools for lootbox, integrate MCP servers, and build
  LLM-accessible tools with type safety.
description: >-
  This skill should be used when developing native TypeScript tools for lootbox,
  integrating external MCP servers, validating tool implementations, or building
  LLM-accessible tools with type safety. Covers tool creation, MCP integration,
  schema definition, testing, and best practices for lootbox tool development.
when_to_use: >-
  When creating new lootbox tools, integrating MCP servers, defining tool
  schemas, debugging tool implementations, or learning lootbox architecture.
version: 1.0.0
category: automation-and-scripting
---

# Developing and Integrating Lootbox Tools

Lootbox is a TypeScript-based tool integration system that provides LLMs with a unified interface to call various tools: native TypeScript functions, MCP servers, and CLI applications. This skill guides you through creating production-ready lootbox tools.

## Quick Start: Choose Your Path

**Creating a new native TypeScript tool?**
→ See: [Native Tool Development Workflow](#native-tool-development-workflow) (Steps 1-10 below)

**Integrating an external MCP server?**
→ See: [MCP Server Integration Workflow](#mcp-server-integration-workflow) (Steps 1-7 below)

**Validating or debugging a tool?**
→ See: [references/error_handling.md](references/error_handling.md)

**Learning lootbox architecture?**
→ See: [references/architecture.md](references/architecture.md)

**Advanced patterns and examples?**
→ See: [references/advanced_patterns.md](references/advanced_patterns.md)

**What to avoid?**
→ See: [references/anti_patterns.md](references/anti_patterns.md)

---

## Understanding Lootbox Architecture

### Key Configuration Files

**`.mcp.json`** (Claude Code MCP client config)
- Used by Claude Code to discover lootbox and other MCP servers
- Do NOT put your tool definitions here

**`lootbox.config.json`** (Lootbox server config)
- Configures lootbox itself and the MCP servers it manages
- This is where you add MCP server integrations
- Supports `${VAR}` interpolation for environment variables

⚠️ **Key Distinction**: `.mcp.json` connects Claude to lootbox; `lootbox.config.json` configures lootbox's internal MCP servers.

**Detailed architecture, data flow, and configuration guidance**: See [references/architecture.md](references/architecture.md)

### Core Concepts

- **Namespace**: Group of related functions (e.g., `kv.ts` → `tools.kv.*`)
- **Tool Function**: Exported async function with typed Args/Result interfaces
- **RPC**: WebSocket-based communication between LLM scripts and tool implementations
- **MCP Server**: External application implementing Model Context Protocol
- **Script**: Reusable TypeScript file in `.lootbox/scripts/` for complex operations
- **`tools` Object**: Pre-injected global object - no imports needed at runtime

### Built-in Tool Namespaces

Lootbox includes these built-in tools (always available):

| Namespace | Purpose |
|-----------|---------|
| `kv` | Key-value store |
| `sqlite` | SQLite database operations |
| `fs` | Filesystem operations |
| `memory` | Knowledge graph / entity storage |

### Runtime Environment

⚠️ **Default**: Lootbox uses **Deno** runtime. Adjust imports if using Node.js.

See [references/architecture.md](references/architecture.md) for runtime-specific guidance.

### Tool Discovery Priority

1. `--lootbox-root` CLI flag
2. `lootboxRoot` in lootbox.config.json
3. Project tools (`.lootbox/tools/`)
4. Global tools (`~/.lootbox/tools/`)

**Debugging discovery issues**: Run `lootbox tools` to see discovered namespaces. See [references/error_handling.md](references/error_handling.md) for troubleshooting.

### Execution Methods

Multiple ways to execute lootbox code:

```bash
# Inline execution
lootbox exec 'await tools.kv.set({key: "foo", value: "bar"})'

# From file
lootbox myscript.ts

# From stdin
echo 'console.log(await tools.kv.get({key: "foo"}))' | lootbox

# List available scripts
lootbox scripts
```

**Important**: The `tools` object is pre-injected - no imports needed. Always use `console.log()` for output; do not use `return` statements in scripts.

### Reusable Scripts

For complex or repeated tasks, create scripts in `.lootbox/scripts/`:

```bash
# Create a new script
lootbox scripts init process-users

# This creates .lootbox/scripts/process-users.ts
# Run it with: lootbox process-users.ts
```

Scripts support piping data via the `stdin()` helper:

```typescript
// .lootbox/scripts/process-users.ts
const input = stdin().json();  // Parse piped JSON

for (const user of input.users) {
  await tools.kv.set({ key: `user:${user}`, value: { name: user } });
}

console.log(JSON.stringify({ processed: input.users.length }));
```

**stdin() methods:**
- `.json()` - Parse JSON input
- `.text()` - Get trimmed text
- `.lines()` - Get array of lines
- `.raw()` - Get raw input

---

## Native Tool Development Workflow

### Naming Conventions

**Tool Names (File Names)**
- Format: `lowercase-with-hyphens` or `lowercase_with_underscores`
- Location: `.lootbox/tools/<toolname>.ts`
- Examples: `kv.ts`, `github.ts`, `testcalculator.ts`
- **Note**: Hyphens in filenames are converted to underscores in namespace names (e.g., `my-tool.ts` → `my_tool` namespace)

**Function Names**
- Format: `camelCase`
- Examples: `get()`, `set()`, `search()`

**Interface Names**
- Format: `<FunctionName>Args` and `<FunctionName>Result` (PascalCase)
- Examples: `GetArgs`, `GetResult`

**MCP Server Names**
- Lootbox sanitizes to TypeScript-safe identifiers
- `perplexity-search` → `mcp_perplexity_search`

**Complete naming and type specifications**: See [references/naming_and_types.md](references/naming_and_types.md)

### Step-by-Step Workflow

**Step 1: Create Tool File**

```bash
# Create namespace file
touch .lootbox/tools/<toolname>.ts
```

**Step 2: Import Dependencies**

```typescript
// Deno runtime (default)
import { readFile } from "https://deno.land/std/fs/mod.ts";

// Or Node.js runtime
import { readFileSync } from "fs";
```

**Step 3: Define Type Interfaces**

```typescript
export interface GetArgs {
  key: string;
}

export interface GetResult {
  value: unknown;
  exists: boolean;
}
```

**Key requirements:**
- Use `export interface <FunctionName>Args {}`
- Use `export interface <FunctionName>Result {}`
- Match function name capitalization

**Step 4: Implement Tool Functions**

```typescript
export async function get(args: GetArgs): Promise<GetResult> {
  const data = await loadData();
  const value = data[args.key];
  return { value, exists: value !== undefined };
}
```

**Requirements:**
- Use `export async function`
- Single object parameter matching `*Args` interface
- Return type matches `*Result` interface
- Add input validation

**Step 5: Restart Server (if needed)**

If lootbox server is already running, restart it to pick up your new tool:

```bash
# In the terminal running lootbox server:
# Press Ctrl+C to stop, then:
lootbox server
```

⚠️ **Important**: New tool files are only discovered when the server starts. The `lootbox tools` command reads files directly, but `lootbox exec` requires the server to have loaded the tool.

**Step 6: Test Tool Discovery**

```bash
lootbox tools
# Should show your namespace

lootbox tools types <namespace>
# Should show extracted type definitions
```

**Step 7: Test Tool Execution**

```bash
lootbox exec 'await tools.<namespace>.<function>({...})'
```

**Step 8: Add Error Handling**

```typescript
export async function get(args: GetArgs): Promise<GetResult> {
  if (!args.key || args.key.trim() === '') {
    throw new Error('Key is required');
  }
  
  try {
    const data = await loadData();
    return { value: data[args.key], exists: true };
  } catch (error) {
    throw new Error(`Failed to load data: ${error.message}`);
  }
}
```

**Step 9: Optimize for Performance**

- Cache expensive operations (5-min TTL recommended)
- Keep operations fast (avoid long-running blocking calls)
- Use chunking for large datasets

**Performance patterns**: See [references/advanced_patterns.md](references/advanced_patterns.md)

**Step 10: Document with JSDoc**

```typescript
/**
 * Retrieves value by key from storage
 * @param args.key - Storage key to retrieve
 * @returns Value and exists flag
 */
export async function get(args: GetArgs): Promise<GetResult> {
  // implementation
}
```

**Detailed workflow explanations, HTTP-based MCP integration, testing patterns**: See [references/workflow_details.md](references/workflow_details.md)

---

## MCP Server Integration Workflow

**Step 1: Find and Install MCP Server**

Find MCP servers at [modelcontextprotocol.io](https://modelcontextprotocol.io/examples) or npm.

```bash
# Most MCP servers work with npx (no install needed)
# Or install globally if preferred:
npm install -g @modelcontextprotocol/server-perplexity
# Or for Python-based MCP servers:
uvx mcp-server-package
```

**Step 2: Add to lootbox.config.json**

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-perplexity"],
      "env": {
        "PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"
      }
    }
  }
}
```

See `mcp-configs/` directory for more examples.

**Step 3: Set Environment Variables**

```bash
export PERPLEXITY_API_KEY="your-key"
```

**Step 4: Restart Lootbox Server**

If lootbox server is already running, stop it first (Ctrl+C in server terminal), then start fresh:

```bash
lootbox server
```

⚠️ **Important**: MCP server configurations are only loaded when lootbox starts. Changes to `lootbox.config.json` require a server restart to take effect.

**Step 5: Verify Integration**

```bash
lootbox tools
# Should show mcp_perplexity namespace

lootbox tools types mcp_perplexity
# Shows available functions
```

**Step 6: Test Execution**

```bash
lootbox exec 'await tools.mcp_perplexity.search({query: "test"})'
```

**Step 7: Handle MCP-Specific Errors**

Common issues:
- `MCP server not found`: Check command/args in config
- `Connection timeout`: Verify server starts correctly
- `Authentication failed`: Check environment variables

**Troubleshooting guide**: See [references/error_handling.md](references/error_handling.md)

**HTTP-based MCP integration, advanced configuration**: See [references/workflow_details.md](references/workflow_details.md)

---

## Tool Validation & Testing

### Quick Validation Checklist

- ☐ Tool file in `.lootbox/tools/<name>.ts`
- ☐ All functions have `*Args` and `*Result` interfaces
- ☐ Functions use `export async function`
- ☐ Single object parameter (not multiple args)
- ☐ `lootbox tools` shows namespace
- ☐ `lootbox tools types <namespace>` succeeds
- ☐ `lootbox exec 'await tools...'` works
- ☐ Input validation with clear errors
- ☐ Executes quickly (recommended < 10 seconds)

**Detailed validation methodology**: See [references/error_handling.md](references/error_handling.md)

### Common Errors & Solutions

**Type-Checking Errors**
- `Property 'X' does not exist` → Add `export` before function
- `Argument not assignable` → Check `*Args` interface fields

**Discovery Errors**
- Missing `*Args` interface → Function works but doesn't follow convention
- Multiple parameters → Function silently excluded from RpcClient

**Runtime Errors**
- Timeout → Optimize, cache, or chunk operations
- Type mismatch → Verify return matches `*Result` interface

**Complete error reference, debugging methodology**: See [references/error_handling.md](references/error_handling.md)

---

## Essential Patterns

### Pattern 1: Simple CRUD Tool

```typescript
export interface GetArgs { id: string; }
export interface GetResult { data: unknown; exists: boolean; }

export async function get(args: GetArgs): Promise<GetResult> {
  const store = await loadStore();
  return { data: store[args.id], exists: !!store[args.id] };
}
```

### Pattern 2: Caching with TTL

```typescript
let cache: Record<string, unknown> | null = null;
let cacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000;

async function getCached() {
  if (cache && (Date.now() - cacheTime) < CACHE_TTL) return cache;
  cache = await fetchFresh();
  cacheTime = Date.now();
  return cache;
}
```

### Pattern 3: Batch Processing

```typescript
export interface ProcessItemsArgs {
  items: Array<{ id: string; data: unknown }>;
  parallel?: boolean;
}

export interface ProcessItemsResult {
  successful: Array<{ id: string; result: unknown }>;
  failed: Array<{ id: string; error: string }>;
}
```

### Pattern 4: Composable Tool Chaining

Design tools so outputs work as inputs to other tools. Use consistent ID patterns:

| Service | ID Format | Example |
|---------|-----------|---------|
| GitHub Issue/PR | `owner/repo#number` | `anthropics/claude#123` |
| Linear Issue | `identifier` | `ENG-123` |
| S3 Object | `bucket/key` | `my-bucket/path/file.json` |

```typescript
// Chain operations - no token overhead between steps
const issues = await tools.github.listIssues({
  repo: "owner/repo",
  state: "open",
  labels: ["bug"]
});

for (const issue of issues.issues) {
  await tools.linear.createIssue({
    teamId: "eng-team-id",
    title: `[GH] ${issue.title}`,
    description: `From: ${issue.url}\n\n${issue.body}`
  });
}
```

### Pattern 5: Compound Functions (Workflows)

Create higher-level functions that compose base tools:

```typescript
// workflows.ts - combines github, linear, s3 tools
export interface SyncGitHubToLinearArgs {
  githubRepo: string;
  linearTeamId: string;
  labels?: string[];
}

export interface SyncGitHubToLinearResult {
  synced: number;
  issues: Array<{ github: string; linear: string }>;
}

export async function syncGitHubToLinear(
  args: SyncGitHubToLinearArgs
): Promise<SyncGitHubToLinearResult> {
  // Compose base tool operations
  const ghIssues = await tools.github.listIssues({ repo: args.githubRepo });
  // ... create Linear issues, return mapping
}
```

**Complete pattern implementations, retry logic, pagination, optimization strategies**: See [references/advanced_patterns.md](references/advanced_patterns.md)

---

## Anti-Patterns to Avoid

❌ **No type definitions** → Always define `*Args` and `*Result` interfaces
❌ **Weak typing** (`Promise<unknown>`) → Always use typed Result interface
❌ **Multiple arguments** → Use single object parameter
❌ **Blocking operations** → Keep fast, use caching/chunking for long operations
❌ **No error handling** → Validate inputs, handle external failures

**Complete anti-pattern reference with examples and fixes**: See [references/anti_patterns.md](references/anti_patterns.md)

---

## Key Constraints & Best Practices

### Function Execution Limits

- **Timeout behavior**: Tool functions should complete quickly (recommended: under 10 seconds). Long-running operations may timeout silently.
- **Workarounds**: Use caching, chunking, or async kickoff patterns for operations that might take longer.

**Timeout behavior details, workarounds**: See [references/workflow_details.md](references/workflow_details.md)

### Type Safety Requirements

- **Named interfaces recommended**: Better documentation than inline types
- **Inline types work**: `args: { id: string }` is supported but not conventional
- **Always use async**: Even for pure functions, for consistency

**Complete type specifications**: See [references/naming_and_types.md](references/naming_and_types.md)

### Error Handling Strategy

- **Throw errors** for validation failures, unexpected conditions
- **Error-in-result** for batch operations, partial success scenarios
- **Choose one approach** per tool and stick with it

**Error handling patterns, decision tree**: See [references/error_handling.md](references/error_handling.md)

---

## Workflow Summary Table

| Task | Command | Details |
|------|---------|---------|
| Create tool | `touch .lootbox/tools/<name>.ts` | [Step 1](#step-by-step-workflow) |
| Verify discovery | `lootbox tools` | [Step 6](#step-by-step-workflow) |
| Check types | `lootbox tools types <namespace>` | [Step 6](#step-by-step-workflow) |
| Test execution | `lootbox exec 'await tools...'` | [Step 7](#step-by-step-workflow) |
| Run script file | `lootbox myscript.ts` | [Execution Methods](#execution-methods) |
| Create script | `lootbox scripts init <name>` | [Reusable Scripts](#reusable-scripts) |
| List scripts | `lootbox scripts` | [Reusable Scripts](#reusable-scripts) |
| Add MCP server | Edit `lootbox.config.json` | [MCP Step 2](#mcp-server-integration-workflow) |
| Debug errors | See error tables | [references/error_handling.md](references/error_handling.md) |
| Optimize performance | Use caching/chunking patterns | [references/advanced_patterns.md](references/advanced_patterns.md) |
| Review anti-patterns | Check violations | [references/anti_patterns.md](references/anti_patterns.md) |

---

## Bundled Resources

This skill includes detailed reference documentation accessible via progressive disclosure:

### Reference Files (in `references/`)

- `architecture.md` - Runtime environment, data flow, configuration details
- `workflow_details.md` - Extended workflow explanations, HTTP-based MCP integration, testing patterns, timeout behavior
- `naming_and_types.md` - Complete naming conventions, type specifications, sanitization rules
- `error_handling.md` - Common errors, debugging methodology, validation best practices
- `advanced_patterns.md` - CRUD, caching, batch processing, retry logic, pagination, optimization strategies
- `anti_patterns.md` - What to avoid and why, with examples and fixes
- `tool_interface_spec.md` - Complete interface specification
- `common_patterns.md` - Reusable implementation patterns
- `troubleshooting.md` - Common issues and solutions
- `best_practices.md` - Best practices for tool development

### Scripts (in `scripts/`)

- `validate_tool.sh` - Shell script to validate tool file syntax and interfaces

### Templates (in `templates/`)

- `basic_kv_tool.ts` - Simple key-value store template
- `api_wrapper_tool.ts` - API integration template

### MCP Config Examples (in `mcp-configs/`)

- `perplexity.mcp.json` - Perplexity search integration
- `custom.mcp.json` - Custom MCP server template

---

## Next Steps

1. **Choose your path**: Native tool or MCP integration?
2. **Follow the workflow**: Complete all steps in order
3. **Use the checklists**: Verify each requirement
4. **Reference detailed docs**: Load on-demand as needed
5. **Test thoroughly**: Discovery, types, and execution

For detailed explanations, code examples, and troubleshooting, see the bundled reference files.
