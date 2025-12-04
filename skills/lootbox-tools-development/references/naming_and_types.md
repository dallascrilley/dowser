# Naming Conventions and Type Specifications

This reference provides complete guidance on naming conventions and type interfaces for lootbox tools.

## Naming Conventions

Before creating tools, understand the naming conventions used throughout lootbox:

**Tool Names (File Names)**
- **Format**: `lowercase-with-hyphens` or `lowercase_with_underscores`
- **File location**: `.lootbox/tools/<toolname>.ts`
- **Examples**: `kv.ts`, `github.ts`, `testcalculator.ts`, `test_timeout.ts`
- **TypeScript namespace**: File name converted to camelCase/lowercase (hyphens removed or converted to underscores)

**Function Names**
- **Format**: `camelCase`
- **Pattern**: Exactly matches `<FunctionName>Args` and `<FunctionName>Result` interface names
- **Examples**: `get()`, `set()`, `search()`, `processItems()`

**Interface Names**
- **Format**: `<FunctionName>Args` and `<FunctionName>Result` (PascalCase + suffix)
- **Pattern**: Function name with capitalized first letter + "Args" or "Result"
- **Examples**: `GetArgs`, `GetResult`, `SearchArgs`, `SearchResult`

**MCP Server Names**
- **Format**: Use hyphens in config (e.g., `chrome-devtools`)
- **TypeScript namespace**: Hyphens sanitized to underscores for RPC (e.g., `mcp_chrome_devtools`)
- **Special Prefix**: All MCP servers in TypeScript use `mcp_` prefix

**Summary Table**

| Item | Format | Example | Namespace |
|------|--------|---------|-----------|
| Tool file | lowercase or lowercase_with_underscores | `kv.ts`, `test_calculator.ts` | `tools.kv`, `tools.test_calculator` |
| Function | camelCase | `get()`, `processItems()` | `tools.kv.get()` |
| Args interface | FunctionNameArgs | `GetArgs`, `ProcessItemsArgs` | Generated as `Kv_GetArgs` |
| Result interface | FunctionNameResult | `GetResult`, `ProcessItemsResult` | Generated as `Kv_GetResult` |
| MCP server | hyphen-separated | `chrome-devtools` | `mcp_chrome_devtools` |

## Type Interface Specifications

### Defining Type Interfaces

For every function, define two interfaces:

```typescript
// Input interface - always <FunctionName>Args
export interface GetArgs {
  key: string;
  defaultValue?: unknown;  // Optional with ?
}

// Output interface - always <FunctionName>Result
export interface GetResult {
  value: unknown;
  exists: boolean;
}
```

**Rules:**
- Both interfaces must be exported (recommended)
- Arguments: Single object with named properties
- Results: Always structured object (not primitives)
- Optional fields use `?` syntax
- Document non-obvious fields with comments

### Note on Inline Types

Inline types (e.g., `function get(args: { id: string })`) work correctly and appear in the RpcClient interface. However, **named interfaces are strongly recommended** because:
- ✅ Better documentation and discoverability
- ✅ Consistent naming convention across the codebase
- ✅ Easier to reference and import in other files
- ✅ Follows the established pattern of `<FunctionName>Args` / `<FunctionName>Result`

Inline types are not broken—they're just not the recommended convention.

### Important Note on Type Naming

When you extract types later with `lootbox tools types`, interface names are automatically converted to PascalCase with the namespace prefix. For example:
- Tool file: `kv.ts` with function `get()` and `GetArgs` interface
- Generated types: `Kv_GetArgs`, `Kv_GetResult` (both namespace and function name become PascalCase)
- In your tool file, keep the names simple (e.g., `GetArgs`, `GetResult`). The namespace prefix is added automatically during type extraction.

## Understanding Name Sanitization

Server names are sanitized to be valid TypeScript identifiers. **All non-alphanumeric characters** (not just hyphens) are replaced with underscores:

| Original | Sanitized | In lootbox scripts | Via Claude MCP |
|----------|-----------|-------------------|----------------|
| `my-server` | `my_server` | `tools.mcp_my_server` | `mcp__lootbox__lootbox_mcp_my_server` |
| `chrome-devtools` | `chrome_devtools` | `tools.mcp_chrome_devtools` | `mcp__lootbox__lootbox_mcp_chrome_devtools` |
| `my@api.v2` | `my_api_v2` | `tools.mcp_my_api_v2` | `mcp__lootbox__lootbox_mcp_my_api_v2` |

**Key Point**: Original MCP tool names are preserved internally. Sanitization applies to server names only, for TypeScript compatibility.

## Implementing Tool Functions

### Basic Function Structure

```typescript
export async function get(args: GetArgs): Promise<GetResult> {
  // Implementation
  const store = await loadData();
  const value = store[args.key];

  return {
    value: value !== undefined ? value : args.defaultValue,
    exists: value !== undefined
  };
}
```

**Function Requirements:**
- Must be `export async function`
- Single parameter: object matching `<FunctionName>Args`
- Return type: `Promise<FunctionNameResult>`
- Input validation (check required fields)
- Error handling (throw or return error fields)

### Sync vs Async Functions

Lootbox supports **both sync and async functions**. Sync functions are automatically wrapped as `Promise<Result>` and work perfectly fine. However:

| Aspect | Async (Recommended) | Sync (Supported) |
|--------|-------------------|------------------|
| Declaration | `export async function` | `export function` |
| Return type | `Promise<Result>` | `Result` |
| Can await within | ✅ Yes | ❌ No |
| Type clarity | ✅ Clear contract | ⚠️ Implicit wrapping |
| RPC discovery | ✅ Fully supported | ✅ Works (auto-wrapped) |

**When to Use Sync Functions:**
- ✅ Pure functions (no I/O, no side effects) - e.g., `add(a, b)`, data transformation
- ✅ Calculations and simple logic
- ✅ Data validation and formatting
- ❌ File operations (use async)
- ❌ Network calls (use async)
- ❌ Database queries (use async)
- ❌ Anything involving external systems (use async)

**Recommendation:** Always use `export async` even if you don't use `await` inside. This makes the async contract explicit and prevents accidental blocking operations in future code changes. If a function later needs I/O, it's ready for async operations without type signature changes.
