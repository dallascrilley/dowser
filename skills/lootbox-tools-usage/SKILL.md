---
name: lootbox-tools-usage
short_description: >-
  Call lootbox tools in LLM scripts, compose tool calls, handle errors, and
  chain multiple tools together.
description: >-
  This skill should be used when calling lootbox tools in LLM scripts, composing
  tool calls, handling errors, chaining multiple tools, or troubleshooting tool
  usage. Covers syntax, argument passing, result handling, native vs MCP tools,
  and practical patterns for tool integration.
when_to_use: >-
  When calling lootbox tools, composing tool chains, handling tool errors,
  troubleshooting tool usage, or learning tool calling patterns.
version: 1.0.0
category: automation-and-scripting
---

# Using and Interfacing with Lootbox Tools

This skill provides practical guidance for calling and using lootbox tools in LLM scripts. Learn how to access tools, pass arguments correctly, handle results, and build workflows that combine multiple tools.

## Quick Start

### Prerequisites

Before using lootbox tools, understand what's available:

- ✅ **Commonly available:** Native tools like `kv`, `sqlite`, `fs`, `memory`, `github`, `linear`, `s3`, `workflows`, `graphql`
- 🔌 **Requires .mcp.json:** External MCP servers like `mcp_perplexity`, `mcp_*` tools
- 💡 **Check YOUR tools:** Run `lootbox tools` to see what's actually available in your environment (available tools vary by installation)

⚠️ **Important:** Examples using `tools.mcp_*` (like `tools.mcp_perplexity`) require external MCP servers configured in `.mcp.json`. If you only see native tools when running `lootbox tools`, skip MCP examples and focus on native tools.

### The Basic Pattern

All lootbox tools follow this simple calling pattern:

```typescript
const result = await tools.<namespace>.<function>({
  param1: "value",
  param2: 42,
  optional: "field"
});

console.log(result);
```

**Three components:**
1. **`tools`** - The tools object (always available in lootbox scripts)
2. **`<namespace>`** - Group of related functions (file name without `.ts`)
3. **`<function>`** - Individual function name

### Examples with Native Tools

```typescript
// Get a value from key-value store
const data = await tools.kv.get({key: "user:123"});

// Query the database
const result = await tools.sqlite.query({
  sql: "SELECT * FROM users WHERE id = ?",
  params: [123]
});
// Result: { rows: [...], columns: ["id", "name", ...], rowCount: number }

// Fetch GitHub repository info (if github tool is available)
const repo = await tools.github.getRepo({repo: "anthropics/claude-code"});
// Result: { repo: { name, stars, ... } }

// List Linear issues (if linear tool is available)
const issues = await tools.linear.listIssues({limit: 10});
// Result: { issues: [...], total, hasMore }
```

**Note:** Run `lootbox tools` to see which namespaces are actually available in your environment. The examples above use commonly available tools.

---

## Understanding Tool Namespaces

### Native Tools (from `.lootbox/tools/`)

Tools you create or that come built-in:

```typescript
await tools.kv.get({key: "mykey"});           // kv namespace
await tools.sqlite.query({sql: "SELECT..."}); // sqlite namespace - for SELECT (returns rows)
await tools.sqlite.execute({sql: "INSERT..."}); // sqlite namespace - for INSERT/UPDATE/DELETE
await tools.myapp.doSomething({...});         // myapp namespace
```

**SQLite Tool Note:**
- `query()` - For SELECT statements (returns `rows`, `columns`, `rowCount`)
- `execute()` - For INSERT/UPDATE/DELETE (returns `success`, `changes`, `lastInsertRowId`)
- `queryOne()` - For SELECT returning single row (returns `row` or `null`)

**Discovery:**
```bash
lootbox tools
# Output: Namespaces: kv, fs, sqlite, memory, myapp, ...
```

### MCP Tools (from external servers)

> 📘 **Advanced Topic:** This section covers integrating external MCP (Model Context Protocol) servers. Most users can skip this and focus on native tools above.

Tools from external MCP servers can be integrated into lootbox through `.mcp.json` configuration. These tools extend lootbox with additional capabilities like web search, LLM access, or specialized APIs.

**How MCP Tools Appear:**

MCP tools can appear in two ways depending on configuration:

1. **As regular namespaces** (when served through lootbox itself):
   ```typescript
   await tools.github.getRepo({repo: "owner/name"});
   await tools.linear.listIssues({teamId: "..."});
   ```

2. **With `mcp_` prefix** (when using external servers directly):
   ```typescript
   // Example - requires mcp_perplexity configured in .mcp.json
   await tools.mcp_perplexity.search({query: "..."});
   ```

**Important:** Run `lootbox tools` to see which MCP tools are actually configured in your environment. Many MCP examples you see online require additional setup in `.mcp.json`.

**To add MCP servers:**
See the [MCP Server documentation](https://github.com/modelcontextprotocol/servers) for setup instructions.

---

## Calling Tools: The Syntax

### Basic Call

```typescript
const result = await tools.<namespace>.<function>({
  arg1: value1,
  arg2: value2
});
```

### Required Arguments

All required fields must be provided:

```typescript
// This function requires 'key'
await tools.kv.get({key: "mykey"});     // ✓ Works
await tools.kv.get({});                 // ✗ Error - missing 'key'
await tools.kv.get({key: "", other: 1}); // ✓ Works (key is provided, even if empty)
```

### Optional Arguments

Fields marked with `?` can be omitted:

```typescript
// kv.list has optional 'prefix' and 'limit' parameters
await tools.kv.list({});                                           // ✓ Works - uses defaults
await tools.kv.list({prefix: "user:", limit: 50});                // ✓ Works - with optional params
```

### Type Correctness

Arguments must match their declared types:

```typescript
// limit should be number, not string
await tools.kv.list({
  limit: 50            // ✓ Number
});

await tools.kv.list({
  limit: "50"          // ✗ Error - should be number
});
```

### Zero-Argument Functions

Functions with no required parameters have different calling conventions based on their type signature. **You MUST use the correct pattern or TypeScript will fail:**

```typescript
// Tools with empty Args interface (e.g., `Kv_InfoArgs {}`) - MUST call with {}
const info = await tools.kv.info({});      // ✓ Works
const cleared = await tools.kv.clear({});  // ✓ Works
// await tools.kv.info();                  // ✗ TypeScript error: Expected 1 argument

// Tools with no Args interface - MUST call without {}
const tables = await tools.sqlite.listTables();  // ✓ Works
const dbInfo = await tools.sqlite.info();        // ✓ Works
// await tools.sqlite.listTables({});            // ✗ TypeScript error: Expected 0 arguments
```

**How to know which to use:**
1. Run `lootbox tools types <namespace>` to see the function signature
2. If you see an Args interface (even empty like `Kv_InfoArgs {}`), you MUST use `{}`
3. If no Args interface is shown (just `listTables(): Promise<...>`), you MUST omit `{}`
4. **These patterns are NOT interchangeable** - using the wrong one causes TypeScript errors

### ⚠️ CRITICAL: Shell Escaping with `lootbox exec`

**This is a common source of errors - read carefully!**

When using `lootbox exec` from the command line, the `!` operator gets escaped by the shell and causes parse errors:

```typescript
// ✗ Fails in shell (! gets escaped to \!):
if (!result.exists) { ... }
if (result.exists !== true) { ... }

// ✓ Use instead:
if (result.exists === false) { ... }
```

**Why:** When passing code as a command-line string argument, the shell interprets `!` as a history expansion operator before passing the code to TypeScript. Use explicit equality comparisons (`=== false`, `=== true`) instead.

**Alternative:** If you need to use the `!` operator:
- Write your code to a `.ts` file and execute the file directly instead of using `lootbox exec`
- Use `set +H` to disable history expansion in bash (may not work in all shells)

### Execution Methods

There are multiple ways to execute lootbox code:

```bash
# Inline execution (quick tests, simple operations)
lootbox exec 'await tools.kv.set({key: "foo", value: "bar"})'

# From a TypeScript file (complex scripts, uses ! operator freely)
lootbox myscript.ts

# From stdin (piping data)
echo 'console.log(await tools.kv.get({key: "foo"}))' | lootbox
```

**When to use each:**
- **`lootbox exec`** - Quick one-liners, testing, simple operations
- **File execution** - Complex logic, scripts with `!` operators, reusable code
- **Stdin piping** - Automation, chaining with other commands

---

## Handling Results

### ⚠️ IMPORTANT: Output with console.log, Not return

In lootbox scripts, **do not use `return` at the top level** - it will throw an error. Always use `console.log()` to output results:

```typescript
// ✗ WRONG - will throw error
const result = await tools.kv.get({key: "answer"});
return result;  // Error: return only allowed in functions

// ✓ CORRECT - use console.log
const result = await tools.kv.get({key: "answer"});
console.log(JSON.stringify(result, null, 2));  // You see this output
```

**Why:** Lootbox scripts execute as top-level async code, not inside a function. Use `console.log()` for all output you want to see.

### Result Structure

All tool functions return structured objects:

```typescript
// Result is always an object with documented fields
const result = await tools.kv.get({key: "test"});

// Always check the result structure
console.log(result);
// { value: "data", exists: true }
```

### Accessing Result Fields

```typescript
const result = await tools.kv.get({key: "user:123"});

// Access fields from result
if (result.exists) {
  console.log(`Found value: ${result.value}`);
} else {
  console.log("Key not found");
}

// Result fields are typed - IDE autocomplete available
result.nonExistent  // ✗ Error - field doesn't exist
```

### Result Documentation

Get type information for tools:

```bash
lootbox tools types <namespace>
# Shows all available functions and their result structures
```

### Status Field Reference

Different lootbox tools use different status fields in their results. Here's a quick reference:

| Status Field | Used By | Meaning | Check Pattern |
|-------------|---------|---------|---------------|
| `exists` | `kv.get()`, `fs.fileInfo()` | Data exists (true/false) | `if (result.exists === false)` |
| `success` | `kv.set()`, `kv.deleteKey()`, `fs.write()`, `sqlite.execute()` | Operation succeeded (true/false) | `if (result.success)` |
| `existed` | `kv.deleteKey()` | Key existed before deletion (returned alongside `success`) | `if (result.existed)` |
| `found` | Some custom tools | Resource found (true/false) | `if (result.found)` |
| `rowCount` | `sqlite.query()` | Number of rows returned | `if (result.rowCount > 0)` |
| `changes` | `sqlite.execute()` | Number of rows modified | `if (result.changes > 0)` |
| `error` | Some tools | Error message if present | `if (result.error)` |

**Note:** Some operations return multiple status fields. For example, `kv.deleteKey()` returns both `success` (operation completed) and `existed` (key was present before deletion).

**Note:** This table shows commonly used status fields. Use `lootbox tools types <namespace>` to see the complete result structure for any tool.

**Key principle:** Always check result status fields before accessing data fields.

**Naming convention:** Status field names follow semantic patterns:
- Present tense (`exists`, `success`) for current state
- Past tense (`existed`, `deleted`) for completed operations
- Count fields (`rowCount`, `changes`) for quantifiable results

Always verify field names with `lootbox tools types <namespace>` for your specific tool version.

---

## Error Handling

### Quick Overview

**Native Local Tools** (kv, sqlite, fs, memory):
- Return status in result object
- Don't throw exceptions
- Check `exists`, `success`, or `error` fields

**External API Tools** (github, linear):
- THROW exceptions on failures
- MUST wrap in try/catch
- Handles 404s, auth errors, rate limits

### Basic Patterns

```typescript
// Native tools - check status fields
const result = await tools.kv.get({key: "test"});
if (result.exists === false) {
  console.log("Key not found");
}

// External tools - use try/catch
try {
  const repo = await tools.github.getRepo({repo: "owner/name"});
  console.log(`Found: ${repo.repo.name}`);
} catch (error) {
  console.log(`Error: ${error instanceof Error ? error.message : String(error)}`);
}
```

**For detailed error handling patterns, see:** `references/error_handling.md`

---

## Native Tools vs MCP Tools

### Native Tools (Fastest)

Tools in `.lootbox/tools/` execute in the local TypeScript environment:

```typescript
// Runs locally, fastest execution
const value = await tools.kv.get({key: "test"});
```

**Use when:**
- You control the tool code
- Speed is important
- Tool doesn't need external services

### MCP Tools (External - Advanced)

Tools from external Model Context Protocol servers (requires `.mcp.json` configuration):

```typescript
// Example: Using an external MCP search service
// ⚠️ This only works if you have the MCP server configured
const results = await tools.mcp_search.query({
  query: "example search"
});
```

**Use when:**
- You need external APIs (search, LLMs, specialized data services)
- Functionality exists in a published MCP server
- You're willing to configure external dependencies

**Setup required:** See MCP documentation for configuration steps

---

## Common Usage Patterns

### Essential Patterns

**Get or Create:**
```typescript
const userId = "user123";
const get = await tools.kv.get({key: userId});
if (get.exists === false) {
  const userData = {name: "Alice", created: Date.now()};
  await tools.kv.set({key: userId, value: userData});
  return userData;
}
return get.value as any;
```

**Pagination:**
```typescript
const allItems: any[] = [];
let offset = 0;
let hasMore = true;

while (hasMore) {
  const page = await tools.kv.list({limit: 50, offset});
  allItems.push(...page.entries);
  offset += page.returnedCount;
  hasMore = offset < page.totalCount;
}
```

**Parallel Operations:**
```typescript
// ✓ Good: Parallel when independent
const [user, config] = await Promise.all([
  tools.kv.get({key: `user:${userId}`}),
  tools.kv.get({key: "config:app"})
]);
```

**For comprehensive patterns and examples, see:** `references/usage_patterns.md`

---

## Best Practices

### Core Principles

1. **Know Your Tools** - Run `lootbox tools` to see available namespaces
2. **Discover Functions** - Use `lootbox tools types <namespace>` before calling
3. **Validate Arguments** - Check arguments before calling tools
4. **Handle Errors** - Check result status or use try/catch appropriately
5. **Cache Expensive Operations** - Use KV store for expensive queries
6. **Chain Efficiently** - Use parallel operations when possible

**For detailed best practices, see:** `references/best_practices.md`

---

## Troubleshooting

### Quick Diagnostics

**Tool Not Found:**
```bash
# Check available tools
lootbox tools
```

**Function Not Found:**
```bash
# List functions in namespace
lootbox tools types <namespace>
```

**Argument Errors:**
- Missing required field: Check tool types for required arguments
- Wrong type: Verify argument types match (number vs string)
- Extra unknown fields: Remove unrecognized parameters

**API Errors (GitHub/Linear):**
- 404 Not Found: Invalid resource name
- 401/403 Unauthorized: Check `GITHUB_TOKEN`, `LINEAR_API_KEY` environment variables
- 429 Rate Limiting: Implement caching to reduce API calls

**For comprehensive troubleshooting, see:** `references/usage_troubleshooting.md`

---

## Scripts: Reusable Code

### Discovering Existing Scripts

Before writing new code, check if a script already exists:

```bash
lootbox scripts              # List all available scripts with examples
```

This shows scripts in `.lootbox/scripts/` that you can run directly.

### Creating Reusable Scripts

For complex or repeated tasks, create a script file:

```bash
# Create a new script from template
lootbox scripts init process-users

# This creates .lootbox/scripts/process-users.ts
# Run it with:
lootbox process-users.ts
```

### The `stdin()` Helper

Scripts can accept piped input using the `stdin()` helper function:

```typescript
/**
 * Process user data from JSON input
 * @example echo '{"users": ["alice", "bob"]}' | lootbox process-users.ts
 */

const input = stdin().json();  // Parse piped JSON data

for (const user of input.users) {
  await tools.kv.set({ key: `user:${user}`, value: { name: user } });
}

console.log(JSON.stringify({ processed: input.users.length }));
```

**`stdin()` methods:**

| Method | Description | Example |
|--------|-------------|---------|
| `.json()` | Parse JSON input | `stdin().json()` → `{users: [...]}` |
| `.text()` | Get trimmed text | `stdin().text()` → `"hello world"` |
| `.lines()` | Get array of lines | `stdin().lines()` → `["line1", "line2"]` |
| `.raw()` | Get raw input string | `stdin().raw()` → `"hello\nworld\n"` |

**Example usage:**

```bash
# Pipe JSON data
echo '{"name": "Alice"}' | lootbox process-user.ts

# Pipe a file
cat users.json | lootbox process-users.ts

# Pipe command output
gh issue list --json number,title | lootbox sync-issues.ts
```

**When to create scripts:**
- Task is repeated frequently
- Logic is complex (multiple steps, conditionals)
- Need to use `!` operator (avoid shell escaping)
- Want to accept piped input
- Code should be version controlled

---

## Getting Help

**To list available tools:**
```bash
lootbox tools
```

**To list available scripts:**
```bash
lootbox scripts
```

**To understand a tool's interface:**
```bash
lootbox tools types <namespace>
```

**To test a tool call:**
```bash
lootbox exec 'console.log(await tools.<ns>.<fn>({...}))'
```

**To create a reusable script:**
```bash
lootbox scripts init <script-name>
```

**For more examples:**
See `assets/examples/basic_tool_usage.ts` for working code samples

**For detailed guides:**
- `references/usage_patterns.md` - Comprehensive usage patterns
- `references/best_practices.md` - Best practices guide
- `references/error_handling.md` - Error handling strategies
- `references/usage_troubleshooting.md` - Troubleshooting guide

---

## Next Steps

- **Want patterns?** → See `references/usage_patterns.md`
- **Want best practices?** → See `references/best_practices.md`
- **Having errors?** → See `references/error_handling.md`
- **Stuck?** → See `references/usage_troubleshooting.md`
