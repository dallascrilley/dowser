# Error Handling Guide for Lootbox Tools

This reference provides comprehensive error handling patterns and strategies for lootbox tools.

## Lootbox Error Patterns

Most lootbox native tools use **result-based error handling** (they return status in the result object rather than throwing):

```typescript
// Most lootbox tools return status fields instead of throwing
const result = await tools.kv.get({key: "test"});
if (result.exists === false) {
  console.log("Key not found");
}

const deleteResult = await tools.kv.deleteKey({key: "test"});
if (deleteResult.success) {
  console.log(`Deleted (existed: ${deleteResult.existed})`);
}
```

**Some external tools or MCP tools may throw errors:**

```typescript
// Wrap in try/catch if the tool might throw
try {
  const result = await tools.mcp_external.riskyOperation({...});
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.log(`Error: ${message}`);
}
```

## Error Patterns by Tool Type

**Native Local Tools** (kv, sqlite, fs, memory):
```typescript
// Return status in result - DON'T throw
const result = await tools.kv.get({key: "test"});
if (result.exists === false) {
  console.log("Not found");
}
```

**External API Tools** (github, linear):
```typescript
// THROW errors on API failures - MUST use try/catch
try {
  const repo = await tools.github.getRepo({repo: "owner/name"});
  console.log(`Found: ${repo.repo.name}`);
} catch (error) {
  console.log(`Error: ${error instanceof Error ? error.message : String(error)}`);
  // Handles: 404 Not Found, 403 Forbidden, Network errors, etc.
}
```

**Why this matters:**
- GitHub/Linear make network requests that can fail
- 404s, auth errors, rate limits all throw exceptions
- Not wrapping in try/catch will crash your script

**Quick test:**
```bash
# This will throw an error:
lootbox exec 'await tools.github.getRepo({repo: "fake/nonexistent"})'

# This handles it gracefully:
lootbox exec 'try { await tools.github.getRepo({repo: "fake/nonexistent"}) } catch(e) { console.log("Caught:", e.message) }'
```

## Check Tool Documentation

To understand error handling for a specific tool:

```bash
lootbox tools types <namespace>
# Check the Result interface for fields like:
# - 'success' → returns boolean status, doesn't throw
# - 'exists' → returns boolean status, doesn't throw
# - 'error' → may include error message in result
```

## Common Error Causes

### 1. Missing Required Arguments

(caught at execution time with `lootbox exec`)

```typescript
await tools.kv.get({});  // ✗ Error - 'key' required
// Error: Property 'key' is missing in type '{}' but required in type 'Kv_GetArgs'
```

Note: When using `lootbox exec`, TypeScript errors occur at runtime. If you use an IDE or TypeScript compiler, errors are caught before execution. With `lootbox exec`, the script will fail when it reaches this line.

### 2. Wrong Argument Type

```typescript
await tools.kv.set({key: "test", value: 123});           // ✓ Works
await tools.sqlite.query({sql: "SELECT...", params: []}); // ✓ Works - array
await tools.sqlite.query({sql: "SELECT...", params: 123}); // ✗ Error - should be array
```

### 3. Operation Failed

(data not found, API error, etc.)

```typescript
// Check the result status
const result = await tools.kv.get({key: "nonexistent"});
if (result.exists === false) {
  console.log("Key not found");
}
```

## Defensive Programming

Always handle potential errors:

```typescript
// ✓ Good: Check for success/exists
const result = await tools.kv.get({key: "test"});
if (result.exists === false) {
  console.log("Not found");
  return;  // Don't continue
}
console.log(result.value); // Safe - we know it exists

// ✓ Good: Wrap in try/catch for external tools that might throw
try {
  const result = await tools.mcp_external.fetchData({...});
} catch (error) {
  console.log(`Error: ${error instanceof Error ? error.message : String(error)}`);
  // Handle gracefully
}

// ✗ Bad: Ignore potential errors
const result = await tools.kv.get({key: "test"});
console.log(result.value);  // Might be null if key doesn't exist
```
