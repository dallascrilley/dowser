# Best Practices for Using Lootbox Tools

This reference provides comprehensive best practices for effective lootbox tool usage.

## 1. Know Your Tools

```bash
# List available tools
lootbox tools

# Get type information for specific tool
lootbox tools types <namespace>

# Understand return types before using
```

## 2. Discover Available Functions

To find the correct function name in a namespace, run:

```bash
# List all functions and their signatures for a namespace
lootbox tools types <namespace>

# Example: Find github functions
lootbox tools types github
```

**Example:** Running `lootbox tools types github` outputs TypeScript interface definitions showing:
- Function names available in the namespace (e.g., `listIssues`, `getIssue`, `createIssue`, `getRepo`)
- Arguments required for each function (e.g., `GithubListIssuesArgs`, `GithubGetRepoArgs`)
- Result types returned by each function (e.g., `GithubListIssuesResult`, `GithubRepoResult`)

Look for lines like:
```typescript
listIssues: (args: GithubListIssuesArgs) => Promise<GithubListIssuesResult>
getRepo: (args: GithubGetRepoArgs) => Promise<GithubRepoResult>
```

**Common mistake:** Guessing function names that don't exist (`listRepos` vs `getRepo`). Always check available functions first with `lootbox tools types <namespace>`.

## 3. Validate Arguments Before Calling

```typescript
// ✓ Good: Check arguments before call using explicit equality (shell-safe)
if (key === undefined || key === "" || key.trim() === "") {
  throw new Error("Key is required");
}
const result = await tools.kv.get({key});

// ✗ Bad: Using ! operator - FAILS in lootbox exec due to shell escaping
// if (!key) { ... }  // Shell interprets ! as history expansion

// ✗ Bad: Rely on tool to validate
const result = await tools.kv.get({key: userData.id});
```

**Important:** When using `lootbox exec`, ALWAYS use explicit equality checks (`key === ""`, `result.exists === false`) instead of negation operators (`!key`, `!result.exists`). The shell escapes `!` as `\!` causing parse errors.

## 4. Handle Errors Appropriately

```typescript
// ✓ Good: Check result status
const result = await tools.kv.get({key: "test"});
if (result.exists === false) {
  console.error("Key not found");
  return null;
}
return result.value;

// ✓ Good: Wrap external tools in try/catch
try {
  const result = await tools.mcp_external.call({...});
} catch (error) {
  console.error(`Exception: ${error instanceof Error ? error.message : String(error)}`);
  return null;
}

// ✗ Bad: Ignore potential errors
const result = await tools.kv.get({key: "test"});
console.log(result.value);  // Might be null if key doesn't exist
```

## 5. Use Appropriate Tool Types

```typescript
// ✓ Good: Use native tools for speed
const value = await tools.kv.get({key: "data"});

// ✓ Good: Use MCP tools for external services (if configured)
const results = await tools.mcp_perplexity.search({query: "..."});

// ✗ Bad: Use slow MCP tool for local operations
const value = await tools.mcp_external_kv.get({key: "data"});
```

## 6. Implement Caching for Expensive Operations

```typescript
// ✓ Good: Cache expensive database queries
const cached = await tools.kv.get({key: `query:${id}`});
if (cached.exists) return cached.value;

const result = await tools.sqlite.query({
  sql: "SELECT * FROM complex_view WHERE id = ?",
  params: [id]
});
await tools.kv.set({key: `query:${id}`, value: result});
return result;

// ✗ Bad: Query database repeatedly for same data
for (const id of ids) {
  const data = await tools.sqlite.query({sql: "...", params: [id]});
}
```

## 7. Chain Operations Efficiently

```typescript
// ✓ Good: Sequential when needed
const user = await tools.kv.get({key: `user:${userId}`});
const metadata = await tools.kv.get({key: `meta:${userId}`});

// ✓ Good: Parallel when independent
const [user, config] = await Promise.all([
  tools.kv.get({key: `user:${userId}`}),
  tools.kv.get({key: "config:app"})
]);

// ✗ Bad: Always sequential even when parallel is possible
const user = await tools.kv.get({key: `user:${userId}`});
const config = await tools.kv.get({key: "config:app"});  // Could be parallel
```
