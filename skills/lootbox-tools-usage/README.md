# Lootbox Tools Usage Skill

A practical guide to using and calling lootbox tools in LLM scripts.

## About This Skill

This skill teaches how to **use** lootbox tools in your scripts. It complements the `lootbox-tools-development` skill (which teaches how to **create** tools).

**Perfect for:**
- LLM developers writing scripts with tools
- Understanding how to call native and MCP tools
- Building workflows that combine multiple tools
- Troubleshooting tool usage issues

## Quick Start

### The Basic Pattern

```typescript
const result = await tools.<namespace>.<function>({param: value});
```

**Three parts:**
1. **`tools`** - Always available in lootbox scripts
2. **`<namespace>`** - Group of related functions (matches filename)
3. **`<function>`** - Individual function name

### Examples

```typescript
// Get a key-value
await tools.kv.get({key: "mykey"});

// Set a key-value
await tools.kv.set({key: "user:alice", value: {name: "Alice", email: "alice@example.com"}});

// Search the web (MCP tool)
await tools.mcp_perplexity.search({query: "AI news"});
```

## What's Inside

### Main Guidance (SKILL.md)

- Tool calling syntax
- Native vs MCP tools
- Argument passing (required vs optional)
- Handling results and errors
- Common usage patterns
- Best practices

### Reference Guides (references/)

**usage_patterns.md** - 10 advanced patterns:
- Retry with exponential backoff
- Parallel batch processing with concurrency limits
- Tool result caching with TTL
- Conditional tool composition
- Result aggregation
- Error handling in batches
- Fallback tool selection
- Streaming with pagination
- State machines
- Performance profiling

**usage_troubleshooting.md** - Solutions for:
- Tool not found
- Function not found
- Missing/wrong arguments
- Type mismatches
- Result field errors
- MCP tool issues
- Performance problems
- And more...

### Examples (assets/examples/)

**basic_tool_usage.ts** - 15 complete working examples:
1. Simple key-value operations
2. Creating and retrieving data
3. Optional arguments
4. Error handling (try/catch)
5. Error handling (result fields)
6. Parallel calls
7. Chaining dependent calls
8. Pagination
9. Batch processing
10. MCP tools
11. Combining native + MCP tools
12. Conditional logic
13. Data transformation
14. Counting and aggregation
15. Validation

## Learning Paths

### Beginner: Just Getting Started

1. Read SKILL.md sections:
   - "Quick Start"
   - "Calling Tools: The Syntax"
   - "Handling Results"
2. Copy `assets/examples/basic_tool_usage.ts`
3. Run examples in `lootbox exec`
4. Modify for your use case

### Intermediate: Building Real Workflows

1. Study "Common Usage Patterns" in SKILL.md
2. See `references/usage_patterns.md` Pattern 4-6 (composition, aggregation, error handling)
3. Combine multiple tools in your scripts

### Advanced: Optimization and Reliability

1. Study all patterns in `references/usage_patterns.md`
2. Implement Pattern 1 (retries) for reliability
3. Implement Pattern 2 (concurrency) for speed
4. Implement Pattern 3 (caching) for efficiency

### Debugging: Something's Not Working

1. Check `references/usage_troubleshooting.md`
2. Use `lootbox tools` to verify tool exists
3. Use `lootbox tools types <namespace>` to see correct syntax
4. Test with `lootbox exec` to isolate issue

## Key Concepts

### Tool Namespace

A group of related functions. One file = one namespace:

```typescript
// File: .lootbox/tools/kv.ts
// Namespace: tools.kv
// Functions: tools.kv.get(), tools.kv.set(), tools.kv.list(), etc.
```

### Native Tools vs MCP Tools

| Type | Prefix | Speed | Use Case |
|------|--------|-------|----------|
| Native | `tools.<name>` | Fast | Local operations |
| MCP | `tools.mcp_<name>` | Slower | External APIs |

### Required vs Optional Arguments

```typescript
// Required (no ?)
export interface GetArgs { key: string; }

// Optional (with ?)
export interface GetArgs { key: string; defaultValue?: unknown; }
```

### Result Structure

All functions return typed objects:

```typescript
const result = await tools.kv.get({key: "test"});
// Always an object: {value: unknown, exists: boolean}
// IDE autocomplete available for fields
```

## Common Tasks

### Task: List Available Tools
```bash
lootbox tools
```

### Task: See Tool Function Signatures
```bash
lootbox tools types <namespace>
```

### Task: Test a Tool Call
```bash
lootbox exec 'await tools.<ns>.<fn>({param: "value"})'
```

### Task: Get an Example
→ See `assets/examples/basic_tool_usage.ts`

### Task: Understand a Pattern
→ See `references/usage_patterns.md` (10 patterns)

### Task: Fix an Error
→ See `references/usage_troubleshooting.md`

## Quick Reference

### Calling Tools

```typescript
// Simple call
const result = await tools.kv.get({key: "test"});

// With optional arguments
const result = await tools.kv.list({limit: 10, offset: 0});

// With error handling (external API tools)
try {
  const result = await tools.github.getRepo({repo: "owner/name"});
} catch (error) {
  console.log(`Error: ${error.message}`);
}
```

### Working with Results

```typescript
// Access fields
console.log(result.value);
console.log(result.entries.length);

// Check optional fields
if (result.value?.email) {
  console.log(result.value.email);
}

// Check result status (native tools)
const kvResult = await tools.kv.get({key: "test"});
if (kvResult.exists) {
  console.log(kvResult.value);
} else {
  console.log("Key not found");
}
```

### Parallel Execution

```typescript
// Run independent operations in parallel
const [a, b] = await Promise.all([
  tools.a.get({...}),
  tools.b.get({...})
]);
```

### Error Handling

```typescript
// Native tools (kv, sqlite) - Check status in result
const kvResult = await tools.kv.get({key: "test"});
if (kvResult.exists === false) {
  console.log("Not found");
}

const sqliteResult = await tools.sqlite.query({sql: "SELECT * FROM users", params: []});
if (sqliteResult.success) {
  console.log(`Rows: ${sqliteResult.rows.length}`);
}

// External API tools (github, linear) - Use try/catch
try {
  const repo = await tools.github.getRepo({repo: "owner/name"});
  console.log(`Stars: ${repo.repo.stars}`);
} catch (error) {
  console.log(`GitHub error: ${error.message}`);
}
```

## File Structure

```
lootbox-tools-usage/
├── SKILL.md                        # Main skill content
├── README.md                       # This file
├── references/
│   ├── usage_patterns.md          # 10 advanced patterns
│   └── usage_troubleshooting.md   # Problem solutions
└── assets/
    └── examples/
        └── basic_tool_usage.ts    # 15 working examples
```

## Related Skills

- **lootbox-tools-development** - How to **create** tools
- **This skill** - How to **use** tools

## Success Criteria

You're ready when you can:

- [ ] List available tools with `lootbox tools`
- [ ] Understand tool namespaces and function names
- [ ] Call a native tool with correct arguments
- [ ] Call an MCP tool with correct arguments
- [ ] Handle results correctly
- [ ] Handle errors appropriately
- [ ] Chain multiple tool calls
- [ ] Combine native and MCP tools
- [ ] Implement a pattern from `usage_patterns.md`

## Quick Debugging Checklist

If a tool call fails:

1. **Does tool exist?** → `lootbox tools`
2. **Is function correct?** → `lootbox tools types <ns>`
3. **Are arguments right?** → Check type info
4. **Are required fields provided?** → All non-optional fields
5. **Are types correct?** → Number vs string vs array
6. **Is server running?** → `lootbox server`
7. **Is syntax correct?** → Try in `lootbox exec`
8. **Is it MCP?** → Use `mcp_` prefix

## Examples in This Skill

### Quick Examples (5 lines each)
- Get/set key-value
- Store and retrieve data
- List with pagination
- Error handling (native and external tools)
- MCP tool search

### Full Examples (15-20 lines each)
- Parallel execution
- Chaining calls
- Batch processing
- Combining native + MCP
- Conditional workflows

### Advanced Examples (50+ lines each)
- All 10 patterns in `usage_patterns.md`
- Real-world workflows
- Production patterns

## Learn by Doing

**Don't just read:**

1. Copy example from `basic_tool_usage.ts`
2. Run in: `lootbox exec --file example.ts`
3. Modify and re-run
4. Build from there

## Getting Help

**Quick lookup:** Run `lootbox tools types <namespace>`

**For patterns:** `references/usage_patterns.md`

**For errors:** `references/usage_troubleshooting.md`

**For examples:** `assets/examples/basic_tool_usage.ts`

**For creating tools:** See `lootbox-tools-development` skill

---

**Version:** 1.0
**Complements:** lootbox-tools-development skill
**Last Updated:** 2025-11-27
