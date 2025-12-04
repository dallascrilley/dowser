# Detailed Workflow Guide

This reference provides extended explanations and examples for the workflows outlined in SKILL.md.

## Native Tool Development - Detailed Steps

### Step-by-Step Breakdown

Each step from the main workflow includes detailed explanations, edge cases, and troubleshooting guidance.

#### Step 1: Define Your Tool's Interface

Before writing implementation, define what your tool does:

1. **Tool name**: Lowercase, no hyphens (file name) - see naming_and_types.md
2. **Functions**: What operations does it support?
3. **Arguments**: What inputs does each function need?
4. **Results**: What data does each function return?

**Example: Key-Value Store Tool**
```
Name: kv
Functions:
  - get(key: string) → {value, exists}
  - set(key: string, value: unknown) → {success, key}
  - delete(key: string) → {success}
```

#### Step 6: Verify Tool Discovery - Extended

**Quick Check:**
```bash
lootbox tools
# Output should include your namespace: kv, fs, sqlite, mycalculator, etc.
```

**⚠️ IMPORTANT: `lootbox tools` Only Does Partial Validation**

`lootbox tools` checks if your tool file exists and has functions, BUT it doesn't validate function signatures. To fully validate your tool (including function parameter rules), use:

```bash
lootbox tools types mycalculator
# If this succeeds, your tool is properly formatted
# If this fails, you'll see detailed errors about syntax or parsing issues
```

**⚠️ CRITICAL: Silent Exclusion Behavior**

`lootbox tools types` will **succeed** even if functions have incorrect signatures, but those functions will be **silently excluded** from the RpcClient interface. If a function you defined is missing from the RpcClient output:

- ✅ Check function has exactly one parameter (object matching `<FunctionName>Args`)
- ✅ Check function is exported with `export async function`
- ✅ Verify the function appears in the RpcClient interface at the bottom of the output

**What Gets Validated:**
- ✅ Tool file exists and can be parsed (errors shown)
- ✅ TypeScript syntax is valid (errors shown)
- ⚠️ Functions accept exactly one parameter (silently excluded if wrong)
- ⚠️ All functions have proper interfaces (may work with inline types)

**If a function is missing from RpcClient**, check these common issues:
- Function has multiple parameters (e.g., `function(a, b)` instead of `function({a, b})`)
- Function isn't exported with `export async function`
- Missing `export interface <FunctionName>Args {}` (inline types may work but are not guaranteed)
- Missing `export interface <FunctionName>Result {}` (will show as `Promise<unknown>`)

### Step 8-9: Testing (Server Required)

⚠️ **NOTE: Starting with Step 8, you must have `lootbox server` running in a separate terminal.** Steps 1-7 work without the server, but `lootbox exec` requires a running WebSocket server.

**Terminal 1 (Server - keep running):**
```bash
lootbox server
# Output: Listening on port 3000...
```

**Terminal 2 (Client - run your tests):**
```bash
lootbox exec 'console.log(await tools.mycalculator.add({a: 5, b: 3}))'
# Output: { result: 8, operation: 'addition' }
```

**Type checking note**: By default, `lootbox exec` performs TypeScript type checking. Type errors will be reported before execution. Verify that all function signatures match the `*Args` interface and return `Promise<*Result>`. If type checking blocks you, verify:
- Function has `export interface <Name>Args { }`
- Function has `export interface <Name>Result { }`
- Function signature is `export async function name(args: <Name>Args): Promise<<Name>Result>`

## MCP Integration - Extended Details

### Two-Terminal Workflow

```
┌─────────────────────────────────┐    ┌────────────────────────────────┐
│  Terminal 1: Server              │    │  Terminal 2: Client            │
│  (Must stay running)             │    │  (For commands & testing)       │
├─────────────────────────────────┤    ├────────────────────────────────┤
│ $ lootbox server                │    │ $ lootbox tools                │
│ Initializing MCP servers...     │    │ (Discovers all tools)          │
│ Connected to: chrome_devtools   │    │                                │
│ Connected to: perplexity        │    │ $ lootbox exec '...'           │
│ Listening on port 3000          │    │ (Executes tools)               │
│ [Server is now ready]           │    │                                │
│ [Leave this terminal open!]     │    │ [Can open multiple terminals]  │
└─────────────────────────────────┘    └────────────────────────────────┘
          ↑ Don't close!                       ↑ Tools only work when server is running
```

### Configuration Changes Take Effect on Restart

⚠️ **IMPORTANT: Configuration Changes Only Take Effect When Server Starts/Restarts**

After editing `lootbox.config.json`, changes are NOT active until you (re)start the lootbox server. If you've already started the server with an old config:
1. Stop the running `lootbox server` (Ctrl+C in the server terminal)
2. Make your edits to `lootbox.config.json`
3. Start a fresh `lootbox server` in Step 4

If you're starting for the first time, just proceed to Step 4.

### Diagnostic Commands for MCP Issues

If MCP tools still don't appear, use these commands to diagnose the issue:

```bash
# 1. Verify lootbox server is actually running
ps aux | grep "lootbox server" | grep -v grep
# Should show: ... lootbox server ...

# 2. Check if port 3000 is in use
lsof -i :3000
# Should show lootbox process listening

# 3. Validate lootbox.config.json syntax
cat lootbox.config.json | jq . > /dev/null && echo "Valid JSON" || echo "Invalid JSON"

# 4. Check if environment variables are set
echo "PERPLEXITY_API_KEY: $PERPLEXITY_API_KEY"
echo "LINEAR_API_KEY: $LINEAR_API_KEY"
# Should show your actual keys, not empty

# 5. Test MCP server command manually
export PERPLEXITY_API_KEY="your-key"
npx @modelcontextprotocol/server-perplexity --help
# Should show help output, not "command not found"

# 6. Run lootbox server with verbose logging
lootbox server --debug
# Watch for errors during server initialization
```

## HTTP-Based MCP Server Integration

Some MCP servers use **HTTP transport** instead of stdio (command/args). These require a **native tool wrapper** instead of config in `lootbox.config.json`.

### When to Use This Approach

- MCP server has HTTP endpoint (e.g., `https://mcp.example.com/mcp`)
- Server doesn't provide a CLI command
- You want direct HTTP integration without subprocess management

### Example: DeepWiki Integration

DeepWiki provides documentation for GitHub repos via `https://mcp.deepwiki.com/mcp`.

⚠️ **CRITICAL: HTTP Headers for MCP Servers**

Some MCP servers like DeepWiki require the `Accept` header to handle streaming responses. The header must include BOTH `application/json` and `text/event-stream`, separated by a comma:

```typescript
headers: {
  "Content-Type": "application/json",
  "Accept": "application/json, text/event-stream",  // BOTH required
}
```

**Why both?** MCP servers can return either JSON responses or text-event-stream responses. If you omit either format from the Accept header, the server returns a **406 Not Acceptable error**.

**Step 1: Create native tool wrapper**

Create `.lootbox/tools/deepwiki.ts`:

```typescript
const DEEPWIKI_API = "https://mcp.deepwiki.com/mcp";

interface McpRequest {
  jsonrpc: "2.0";
  id: number;
  method: string;
  params: Record<string, unknown>;
}

interface McpResponse {
  jsonrpc: "2.0";
  id: number;
  result?: unknown;
  error?: { code: number; message: string };
}

async function mcpCall(toolName: string, args: Record<string, unknown>): Promise<unknown> {
  const request: McpRequest = {
    jsonrpc: "2.0",
    id: Date.now(),
    method: "tools/call",
    params: { name: toolName, arguments: args },
  };

  const response = await fetch(DEEPWIKI_API, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream",  // CRITICAL: Required for streaming support
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`API error (${response.status}): ${await response.text()}`);
  }

  const json: McpResponse = await response.json();
  if (json.error) {
    throw new Error(`MCP error: ${json.error.message}`);
  }
  return json.result;
}

// Expose MCP tools as typed functions
export interface ReadWikiStructureArgs { repoName: string; }
export interface ReadWikiStructureResult { topics: Array<{ id: string; title: string }>; }

export async function readWikiStructure(args: ReadWikiStructureArgs): Promise<ReadWikiStructureResult> {
  return await mcpCall("read_wiki_structure", args) as ReadWikiStructureResult;
}

export interface AskQuestionArgs { repoName: string; question: string; }
export interface AskQuestionResult { answer: string; sources?: string[]; }

export async function askQuestion(args: AskQuestionArgs): Promise<AskQuestionResult> {
  return await mcpCall("ask_question", args) as AskQuestionResult;
}
```

**Step 2: Use like any native tool**

```typescript
const answer = await tools.deepwiki.askQuestion({
  repoName: "facebook/react",
  question: "How does reconciliation work?"
});
console.log(answer.answer);
```

### Key Differences from Stdio MCP

| Aspect | Stdio MCP (config) | HTTP MCP (native wrapper) |
|--------|-------------------|---------------------------|
| Config location | `lootbox.config.json` | `.lootbox/tools/<name>.ts` |
| Transport | Subprocess stdio | HTTP fetch |
| Namespace | `tools.mcp_<name>` | `tools.<name>` (no prefix) |
| Lifecycle | Managed by lootbox | Stateless HTTP calls |

### Common HTTP Headers for MCP Servers

| Header | Purpose | Example | When Required |
|--------|---------|---------|----------------|
| `Content-Type` | Request body format | `application/json` | Always for JSON bodies |
| `Accept` | Response format | `application/json, text/event-stream` | **Critical for streaming servers** - Missing this header causes 406 errors |
| `Authorization` | Authentication | `Bearer token` or `Authorization: sk-xxx` | If server requires auth |
| `User-Agent` | Client identification | `lootbox/1.0` | Some servers may require this |

**Critical Note on Accept Header:**
Some MCP servers like DeepWiki require the `Accept` header to handle streaming responses. The header must include both `application/json` and `text/event-stream`:
```typescript
const response = await fetch(API_URL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",  // CRITICAL
  },
  body: JSON.stringify(request),
});
```

Omitting this header will result in a `406 Not Acceptable` error.

**Best Practice:** Always check the MCP server's documentation for required headers. Test with curl or Postman first if you encounter unexpected errors:
```bash
curl -X POST https://mcp.example.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{}}'
```

## Testing Patterns

### Integration Testing

**Important**: lootbox performs **TypeScript type-checking by default**. Invalid argument types are caught during type-checking, not at runtime.

**Type Checking vs. Runtime Testing:**
- **Type-checking errors** (caught before execution): Missing required fields, wrong types, unknown properties. These fail with TypeScript TS errors (e.g., TS2339).
- **Runtime errors** (caught during execution): Logic errors, validation failures, API failures. These throw Error objects you can catch.

**Recommended approach**: Use inline code directly for testing valid inputs and catching runtime errors:

```bash
# Test basic functionality
lootbox exec 'const result = await tools.mynewtool.get({id: "123"}); console.log("Test 1:", result);'

# Test with options
lootbox exec 'const result = await tools.mynewtool.list({limit: 10, sort: "desc"}); console.log("Test 2:", result);'

# Test edge cases and error handling (use valid types that trigger runtime errors)
# Example: Test divide-by-zero error
lootbox exec 'try { await tools.calculator.divide({a: 10, b: 0}); console.log("ERROR: Should have failed"); } catch (e) { const msg = e instanceof Error ? e.message : String(e); console.log("Test 3 (expected error):", msg); }'
```

**Testing with Invalid Types:**

If you need to test how functions handle invalid argument types (for documentation purposes), use the `--no-check` flag to skip TypeScript validation:

```bash
# Skip type checking to test runtime behavior with invalid types
lootbox exec --no-check 'const result = await tools.mynewtool.get({id: 123}); console.log(result);'

# This allows testing type coercion or error handling for type mismatches
# Note: --no-check is useful for testing, but functions should always validate inputs in production
```

**Best Practice**: Design your functions to validate inputs and throw clear errors. Most testing should use properly-typed valid arguments and test error paths through legitimate runtime conditions.

**For longer test suites**, create a file and use shell substitution:

```bash
cat > test_tool.ts << 'EOF'
// Test basic functionality
const result1 = await tools.mynewtool.get({id: "123"});
console.log("Test 1:", result1);

// Test with options
const result2 = await tools.mynewtool.list({limit: 10, sort: "desc"});
console.log("Test 2:", result2);

// Test edge cases
try {
  await tools.mynewtool.create({});  // Missing required field
  console.log("ERROR: Should have failed");
} catch (e) {
  console.log("Test 3 (expected error):", e.message);
}
EOF

# Execute with proper quoting
lootbox exec "$(cat test_tool.ts)"
```

## Function Execution Limits

### Timeout Constraint

**Timeout Constraint:** Functions must complete within **10 seconds** of execution. Operations exceeding this will be **terminated with a timeout error**.

**Origin:** This 10-second timeout is enforced by the Deno runtime and WebSocket RPC layer in lootbox. It applies to the entire function execution, including:
- Async I/O operations (API calls, database queries, file reads)
- CPU-bound computation
- Waiting on promises or timers

The timeout is a hard limit and cannot be configured per-tool or per-call. Functions that need longer operations should be broken into smaller pieces or use background job patterns.

When a timeout occurs:
- The function execution is stopped
- The process may produce TypeScript compilation/download errors or connection failures rather than a clean timeout message
- Any partial work is discarded (database transactions, file writes, etc. may be incomplete)
- The function cannot recover from the timeout (cannot continue executing after 10s)

**Note**: This timeout applies to the function **execution phase**. If `lootbox exec` fails with type-checking errors before reaching execution, the function wasn't executed at all. Timeout error messages may vary depending on when the timeout occurs (during fetch, during function execution, etc.). You may see connection errors, type-checking errors, or other indicators that execution was terminated.

### Testing for Timeout Issues

```typescript
// Create a test function to verify timeout behavior
export interface TestTimeoutArgs { delayMs: number; }
export interface TestTimeoutResult { completed: boolean; timeElapsed: number; }

export async function testTimeout(args: TestTimeoutArgs): Promise<TestTimeoutResult> {
  const start = Date.now();
  await new Promise(resolve => setTimeout(resolve, args.delayMs));
  return { completed: true, timeElapsed: Date.now() - start };
}

// Then test:
// ✅ Should succeed: lootbox exec 'await tools.testtool.testTimeout({delayMs: 3000})'
// ❌ Will timeout: lootbox exec 'await tools.testtool.testTimeout({delayMs: 15000})'
```

### Optimization Strategies

1. **Caching** - Avoid repeated expensive operations
```typescript
let cache: unknown = null;
let cacheTime = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export async function getData(args: GetDataArgs): Promise<GetDataResult> {
  const now = Date.now();
  if (cache && (now - cacheTime) < CACHE_TTL) {
    return { data: cache, cached: true };  // Return cached result (instant)
  }
  cache = await fetchExpensiveData();  // Only fetch once per 5 minutes
  cacheTime = now;
  return { data: cache, cached: false };
}
```

2. **Breaking into Smaller Operations** - Multiple quick calls instead of one slow call
```typescript
// Instead of: process 10,000 items in one call (15+ seconds)
export async function processAll(args: ProcessAllArgs): Promise<void> {
  for (const item of args.items) {  // ❌ This might timeout
    await expensiveProcessing(item);
  }
}

// Better: Process in batches, call function multiple times
export async function processBatch(args: ProcessBatchArgs): Promise<ProcessBatchResult> {
  const results = [];
  for (const item of args.items) {  // Process subset (< 10 seconds)
    results.push(await expensiveProcessing(item));
  }
  return { results, nextOffset: args.offset + results.length };
}
// Client calls this multiple times with different offsets
```

3. **Persistent Storage** - Pre-compute and cache results
```typescript
// Pre-compute expensive results and store them
export async function refreshCache(_args: RefreshCacheArgs): Promise<RefreshCacheResult> {
  const results = await expensiveComputation();
  await tools.kv.set({ key: "cached_results", value: results });
  return { success: true, itemsComputed: results.length };
}

// Later, retrieve from cache instantly
export async function getResults(args: GetResultsArgs): Promise<GetResultsResult> {
  const { value } = await tools.kv.get({ key: "cached_results" });
  return { results: value, fromCache: true };  // Instant response
}
```

4. **Background Jobs** - Offload long operations outside tool execution
```typescript
// Start a long job asynchronously
export async function startBackgroundJob(args: StartJobArgs): Promise<StartJobResult> {
  const jobId = generateId();
  // Store job metadata (instant)
  await tools.kv.set({
    key: `job:${jobId}`,
    value: { status: "running", args, startTime: Date.now() }
  });
  // Return immediately (< 10s)
  return { jobId, status: "started" };
}

// Check job progress later
export async function getJobStatus(args: GetJobStatusArgs): Promise<GetJobStatusResult> {
  const { value: job } = await tools.kv.get({ key: `job:${args.jobId}` });
  return { status: job.status, result: job.result };  // Instant lookup
}
```
