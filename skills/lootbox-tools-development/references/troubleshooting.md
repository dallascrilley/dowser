# Lootbox Tools Troubleshooting Guide

## Configuration File Confusion

**Symptom:** Not sure whether to edit `.mcp.json` or `lootbox.config.json`

**Answer:**

- **`.mcp.json`** → Claude Code's MCP client config (tells Claude how to find lootbox)
  - Located in project root or `~/.claude/`
  - Used to expose lootbox and other MCPs to Claude Code
  - Do NOT define tools here
  - Example: `"lootbox": {"command": "deno", "args": [...], "cwd": "..."}`

- **`lootbox.config.json`** → Lootbox server config (how lootbox manages itself)
  - Located in lootbox project root
  - Where you add MCP server integrations
  - Where you set environment variables for tools
  - Example: `"mcpServers": {"perplexity": {"command": "npx", ...}}`

**Rule**: If you're adding a tool or MCP server to lootbox, edit `lootbox.config.json`. If you want Claude to see lootbox, set up `.mcp.json`.

---

## Tool Not Discovered

**Symptom:** `lootbox tools` doesn't show your namespace

**Causes & Solutions:**

1. **File in wrong location**
   - Tool must be in `.lootbox/tools/` (project) or `~/.lootbox/tools/` (global)
   - Check: `ls -la .lootbox/tools/`
   - Fix: Move file to correct directory

2. **File doesn't have `.ts` extension**
   - Tool must be named `<toolname>.ts`
   - Check: `ls .lootbox/tools/`
   - Fix: Rename to include `.ts` extension

3. **TypeScript syntax errors**
   - Tool file has invalid TypeScript
   - Check: `lootbox tools types <namespace>` (will show errors)
   - Fix: Fix syntax errors in your tool file

4. **Namespace conflicts**
   - Built-in tool has same name
   - Check: `lootbox tools` to see all namespaces
   - Fix: Rename your tool to unique name

---

## Function Not Found

**Symptom:** `Function not found: myfunction` when calling tool

**Causes & Solutions:**

1. **Function not exported**
   ```typescript
   // ❌ WRONG
   async function myfunction(args: Args): Promise<Result> { }

   // ✅ CORRECT
   export async function myfunction(args: Args): Promise<Result> { }
   ```
   - Fix: Add `export` keyword

2. **Wrong function name**
   - Called: `tools.namespace.wrongname()`
   - Actual: `export async function rightname() { }`
   - Fix: Check spelling and case sensitivity

3. **Function is not async**
   ```typescript
   // ❌ WRONG
   export function myfunction(args: Args): Result { }

   // ✅ CORRECT
   export async function myfunction(args: Args): Promise<Result> { }
   ```
   - Fix: Add `async` keyword and `Promise<>`

---

## Arguments Interface Not Found

**Symptom:** `Arguments interface not found` when checking types

**Causes & Solutions:**

1. **Missing Args interface**
   ```typescript
   // ❌ WRONG - no interface
   export async function myfunction(args: any): Promise<Result> { }

   // ✅ CORRECT
   export interface MyfunctionArgs { }
   export async function myfunction(args: MyfunctionArgs): Promise<Result> { }
   ```
   - Fix: Create `export interface <FunctionName>Args {}`

2. **Args interface not exported**
   ```typescript
   // ❌ WRONG
   interface MyfunctionArgs { }
   export async function myfunction(args: MyfunctionArgs) { }

   // ✅ CORRECT
   export interface MyfunctionArgs { }
   export async function myfunction(args: MyfunctionArgs) { }
   ```
   - Fix: Add `export` before interface

3. **Args interface has wrong name**
   - Function: `myfunction`
   - Interface: `ArgInterface` or `MyArgs`
   - Pattern: `<FunctionName>Args` (case-sensitive)
   - Fix: Rename interface to match pattern

4. **Args interface is empty (but that's OK)**
   ```typescript
   // This is VALID if function takes no arguments
   export interface MyfunctionArgs { }
   export async function myfunction(args: MyfunctionArgs): Promise<Result> { }
   ```
   - Usage: `await tools.namespace.myfunction({})`

---

## Result Interface Not Found

**Symptom:** `Result interface not found` when checking types

**Causes & Solutions:**

Same as "Arguments Interface Not Found" but for Result:

1. **Missing Result interface** → Create it
2. **Result interface not exported** → Add `export`
3. **Result interface has wrong name** → Follow `<FunctionName>Result` pattern
4. **Result must return object, not primitive**
   ```typescript
   // ❌ WRONG - returns primitive
   export async function add(args: AddArgs): Promise<number> { }

   // ✅ CORRECT - returns object
   export interface AddResult { result: number; }
   export async function add(args: AddArgs): Promise<AddResult> { }
   ```

---

## Type Mismatch in Function Call

**Symptom:** TypeScript error when calling function with arguments

**Causes & Solutions:**

1. **Missing required field**
   ```typescript
   // Interface
   export interface GetArgs { key: string; }  // key is REQUIRED

   // Usage - WRONG
   await tools.kv.get({});  // Missing 'key' - ERROR

   // Usage - CORRECT
   await tools.kv.get({key: "mykey"});
   ```
   - Fix: Provide all required fields

2. **Wrong field type**
   ```typescript
   // Interface
   export interface AddArgs { a: number; b: number; }

   // Usage - WRONG
   await tools.calc.add({a: "5", b: 3});  // a should be number - ERROR

   // Usage - CORRECT
   await tools.calc.add({a: 5, b: 3});
   ```
   - Fix: Use correct data type

3. **Field doesn't exist**
   ```typescript
   // Interface
   export interface GetArgs { key: string; }

   // Usage - WRONG
   await tools.kv.get({key: "x", cache: true});  // 'cache' doesn't exist - ERROR

   // Usage - CORRECT
   await tools.kv.get({key: "x"});
   ```
   - Fix: Remove unknown fields or add to interface

---

## Timeout: Function Too Long

**Symptom:** Tool function takes > 30 seconds or times out

**Causes & Solutions:**

1. **Function does expensive operation**
   - Fetching large dataset
   - Waiting for external API
   - Processing massive file

   **Solutions:**
   - Add caching to avoid repeated work
   - Use pagination instead of loading all data
   - Add timeout to external calls
   - Break into smaller operations

   **Example - Add caching:**
   ```typescript
   let cache: unknown = null;
   const CACHE_TTL = 5 * 60 * 1000;
   let cacheTime = 0;

   export async function getExpensiveData(): Promise<DataResult> {
     const now = Date.now();
     if (cache && (now - cacheTime) < CACHE_TTL) {
       return { data: cache, cached: true };
     }
     cache = await fetchExpensiveData();
     cacheTime = now;
     return { data: cache, cached: false };
   }
   ```

2. **Infinite loop or deadlock**
   - Check for `while(true)` loops without exit
   - Check for recursive calls without base case
   - Check for waiting on unresolved promises

   **Fix:** Add timeout handling
   ```typescript
   async function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
     return Promise.race([
       promise,
       new Promise<T>((_, reject) =>
         setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
       ),
     ]);
   }

   // Usage
   const result = await withTimeout(expensiveOperation(), 25000);  // 25 second timeout
   ```

---

## Cannot Find Module

**Symptom:** `Cannot find module 'X'` when importing

**Causes & Solutions:**

1. **Import from npm package**
   ```typescript
   // ❌ WRONG - trying to import npm package
   import { something } from "some-package";  // Not available

   // ✅ CORRECT - Use URL import
   import { something } from "https://esm.sh/some-package@1.0.0";
   ```

2. **Relative import path wrong**
   ```typescript
   // ❌ WRONG
   import { helper } from "./helper";  // File doesn't exist

   // ✅ CORRECT
   import { helper } from "./helpers.ts";  // Correct filename and .ts extension
   ```

3. **Using Node.js modules**
   - Lootbox runs on Deno, not Node.js
   - Can't use CommonJS require()
   - Can't use Node.js built-ins directly

   **Use Deno equivalents:**
   - File system: Use Deno APIs or deno.land/std
   - HTTP: Use native fetch()
   - JSON: Use JSON.stringify/parse
   - Path: `import { join } from "https://deno.land/std/path/mod.ts"`

4. **Missing import statement**
   ```typescript
   // ❌ WRONG - using Date without import
   const now = Date.now();  // Date is global in Deno, but be explicit

   // ✅ CORRECT - Date is built-in global
   const now = Date.now();  // Works, no import needed
   ```

---

## Function Returns Wrong Type

**Symptom:** Function returns data but structure doesn't match Result interface

**Causes & Solutions:**

1. **Returning primitive instead of object**
   ```typescript
   // ❌ WRONG
   export async function get(args: GetArgs): Promise<GetResult> {
     return "value";  // Primitive, not object
   }

   // ✅ CORRECT
   export async function get(args: GetArgs): Promise<GetResult> {
     return { value: "value", exists: true };  // Object
   }
   ```

2. **Missing required fields in result**
   ```typescript
   // Interface
   export interface GetResult { value: unknown; exists: boolean; }

   // ❌ WRONG - missing 'exists'
   export async function get(args: GetArgs): Promise<GetResult> {
     return { value: "data" };  // Missing 'exists' field
   }

   // ✅ CORRECT
   export async function get(args: GetArgs): Promise<GetResult> {
     return { value: "data", exists: true };
   }
   ```

3. **Wrong field types in result**
   ```typescript
   // Interface
   export interface CountResult { count: number; }

   // ❌ WRONG - count is string
   export async function getCount(): Promise<CountResult> {
     return { count: "5" };  // Should be number
   }

   // ✅ CORRECT
   export async function getCount(): Promise<CountResult> {
     return { count: 5 };  // Correct type
   }
   ```

---

## Error Handling Not Working

**Symptom:** Error thrown but not handled properly

**Causes & Solutions:**

1. **Function doesn't throw on error**
   ```typescript
   // ❌ WRONG - silently fails
   export async function get(args: GetArgs): Promise<GetResult> {
     if (!args.key) {
       // Just returns undefined, no error
       return { value: undefined, exists: false };
     }
   }

   // ✅ CORRECT - validates input
   export async function get(args: GetArgs): Promise<GetResult> {
     if (!args.key || args.key.trim() === "") {
       throw new Error("Key is required");
     }
   }
   ```

2. **Inconsistent error approach**
   - Some functions throw, some return error in result
   - Choose ONE approach and use consistently

   **Approach 1: Throw errors**
   ```typescript
   export async function create(args: CreateArgs): Promise<CreateResult> {
     if (!args.name) throw new Error("Name required");
     // ...
     return { success: true };
   }
   ```

   **Approach 2: Return error in result**
   ```typescript
   export async function create(args: CreateArgs): Promise<CreateResult> {
     if (!args.name) return { success: false, error: "Name required" };
     // ...
     return { success: true };
   }
   ```

3. **Not catching external errors**
   ```typescript
   // ❌ WRONG - unhandled rejection if fetch fails
   export async function getUser(args: GetUserArgs): Promise<GetUserResult> {
     const response = await fetch(`/users/${args.id}`);
     return { user: await response.json() };
   }

   // ✅ CORRECT - catches and handles errors
   export async function getUser(args: GetUserArgs): Promise<GetUserResult> {
     try {
       const response = await fetch(`/users/${args.id}`);
       if (!response.ok) {
         return { success: false, error: `HTTP ${response.status}` };
       }
       return { success: true, user: await response.json() };
     } catch (error) {
       return { success: false, error: error.message };
     }
   }
   ```

---

## MCP Server Not Connecting

**Symptom:** MCP server configured but not appearing in `lootbox tools`

**Causes & Solutions:**

1. **Wrong configuration file location**
   - Must be at project root: `lootbox.config.json`
   - Not in `.lootbox/` directory
   - Check: `ls lootbox.config.json`

2. **Invalid JSON in configuration**
   - Missing comma, bracket, quote
   - Validate with: `cat lootbox.config.json | jq`
   - Fix syntax errors

3. **Command not executable**
   ```json
   // ❌ WRONG - npx not in PATH
   {"command": "npx-missing", ...}

   // ✅ CORRECT - use full path or verified command
   {"command": "npx", "args": ["@modelcontextprotocol/server-perplexity"]}
   ```
   - Check: `which npx` or `which python3`
   - Use full path if needed: `/usr/bin/python3`

4. **Missing environment variables**
   ```json
   {
     "mcpServers": {
       "perplexity": {
         "command": "npx",
         "args": ["@modelcontextprotocol/server-perplexity"],
         "env": {"PERPLEXITY_API_KEY": ""}  // ❌ Missing value
       }
     }
   }
   ```
   - Fix: Add actual API key or use shell passthrough: `"${PERPLEXITY_API_KEY}"`
   - Check shell has value: `echo $PERPLEXITY_API_KEY`
   - Export before running: `export PERPLEXITY_API_KEY="pplx-xxx" && lootbox server`

5. **Server command takes too long**
   - Server startup taking > 30 seconds
   - Fix: Check server logs for errors
   - Run server manually to debug: `npx @modelcontextprotocol/server-perplexity`

6. **Server crashes on startup**
   - Check `lootbox.config.json` syntax again
   - Test server directly: `npx @modelcontextprotocol/server-perplexity`
   - Look for error messages in console

7. **HTTP-based MCP server (not stdio)**
   - Some MCP servers use HTTP transport, not stdio
   - These CANNOT go in `lootbox.config.json`
   - Create a native tool wrapper in `.lootbox/tools/<name>.ts`
   - See "HTTP-Based MCP Server Integration" in SKILL.md

---

## MCP Tool Not Working

**Symptom:** MCP server connected but tool function fails

**Causes & Solutions:**

1. **Wrong tool name**
   - MCP server name: `perplexity`
   - Namespace: `mcp_perplexity` (with underscore, not hyphen)
   - Function: Check available tools with `lootbox tools types mcp_perplexity`

2. **Wrong argument name or type**
   - Check types: `lootbox tools types mcp_perplexity`
   - Match exact parameter names and types
   - Try with required fields only first

3. **API key not working**
   - Verify key is valid and not expired
   - Check environment variable is set: `echo $API_KEY`
   - Test in `.mcp.json` env field or shell

4. **Service unavailable**
   - Check service status (API might be down)
   - Try request manually outside lootbox
   - Check network connectivity

---

## Performance Issues

**Symptom:** Tool functions are slow or using too much memory

**Causes & Solutions:**

1. **Unbounded caching**
   ```typescript
   // ❌ WRONG - cache grows forever
   const cache = new Map();
   cache.set(key, data);  // No cleanup

   // ✅ CORRECT - bounded cache with TTL
   const cache = new Map();
   const MAX_CACHE_SIZE = 1000;
   if (cache.size >= MAX_CACHE_SIZE) {
     cache.delete(cache.keys().next().value);
   }
   ```

2. **Loading all data at once**
   ```typescript
   // ❌ WRONG - loads all users into memory
   export async function listUsers(): Promise<UsersResult> {
     const allUsers = await db.getAllUsers();  // Might be millions
     return { users: allUsers };
   }

   // ✅ CORRECT - paginate
   export async function listUsers(args: ListUsersArgs): Promise<UsersResult> {
     const users = await db.getUsers(args.limit, args.offset);
     return { users, hasMore: true };
   }
   ```

3. **Synchronous operations blocking**
   - File I/O: Use `Deno.readTextFile` (async)
   - Network: Use `fetch` (async)
   - Always use async/await

---

## Getting Help

1. **Check types:** `lootbox tools types <namespace>`
2. **Check syntax:** Look for TypeScript compilation errors
3. **Check naming:** Interfaces follow `<FunctionName>Args` and `<FunctionName>Result`
4. **Check exports:** All interfaces and functions use `export`
5. **Check location:** Tool file in `.lootbox/tools/<name>.ts`
6. **Check discovery:** `lootbox tools` shows your namespace
7. **Test manually:** `lootbox exec 'await tools.<ns>.<fn>(...)'`

---

## Common Typos

| You wrote | You meant | Result |
|-----------|-----------|--------|
| `GetArgs` | `GetArgs` (matches function) | ✓ Correct |
| `GetArg` | `GetArgs` | ✗ Interface not found |
| `get_args` | `GetArgs` (camelCase) | ✗ Interface not found |
| `Result` | `GetResult` | ✗ Wrong naming convention |
| `function get()` | `export async function get()` | ✗ Not found |

Check case sensitivity - JavaScript/TypeScript is case-sensitive!
