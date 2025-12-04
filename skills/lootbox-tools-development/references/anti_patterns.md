# Anti-Patterns to Avoid

This reference documents common mistakes in lootbox tools development, explains why they're problematic, and provides correct alternatives.

---

## Anti-Pattern 1: No Type Definitions

### ❌ WRONG - Missing Type Definitions

```typescript
// No types - loses all IDE support and type safety
export async function get(args) { 
  return data[args.key]; 
}
```

**Why this is bad:**
- ❌ No compile-time type checking
- ❌ No IDE autocomplete for function arguments
- ❌ Caller has no idea what fields are required
- ❌ Runtime errors instead of compile-time catches
- ❌ Function won't appear in generated RpcClient interface correctly

### ✅ RIGHT - Always Type Everything

```typescript
export interface GetArgs { 
  key: string; 
}

export interface GetResult { 
  value: unknown; 
  exists: boolean; 
}

export async function get(args: GetArgs): Promise<GetResult> {
  const value = data[args.key];
  return { value, exists: value !== undefined };
}
```

**Why this is good:**
- ✅ Compile-time type checking catches errors early
- ✅ IDE provides autocomplete for args.key
- ✅ Clear contract: caller knows exactly what to provide
- ✅ Self-documenting code
- ✅ Appears correctly in RpcClient interface

---

## Anti-Pattern 2: Weak Typing - Promise<unknown>

### ❌ WEAK - No Type Safety for Return Value

```typescript
export interface DivideArgs { a: number; b: number; }

// Using Promise<unknown> - caller has no idea what to expect
export async function divide(args: DivideArgs): Promise<unknown> {
  return { result: args.a / args.b };
}
```

**Why this is bad:**
- ❌ Caller loses type safety for return value
- ❌ No IDE autocomplete for result properties
- ❌ Runtime errors when accessing result.result (typo won't be caught)
- ❌ Function appears in RpcClient as `Promise<unknown>`
- ❌ No documentation of what the function actually returns

**What happens:**
```typescript
// Caller has no type safety
const result = await tools.math.divide({ a: 10, b: 2 });
console.log(result.result);  // ❌ No autocomplete, no type checking
console.log(result.reuslt);  // ❌ Typo not caught at compile time
```

### ✅ STRONG - Always Define Result Interface

```typescript
export interface DivideArgs { a: number; b: number; }

export interface DivideResult { 
  result: number; 
}

export async function divide(args: DivideArgs): Promise<DivideResult> {
  if (args.b === 0) {
    throw new Error('Cannot divide by zero');
  }
  return { result: args.a / args.b };
}
```

**Why this is good:**
- ✅ Full type safety for return value
- ✅ IDE autocomplete shows result.result
- ✅ Compile-time catches typos like result.reuslt
- ✅ Function appears in RpcClient with proper types
- ✅ Self-documenting: caller knows exactly what they'll get

**Impact on RpcClient:**
```typescript
// Generated RpcClient interface
export interface RpcClient {
  math: {
    divide(args: DivideArgs): Promise<DivideResult>;  // ✅ Fully typed
  };
}
```

---

## Anti-Pattern 3: Untyped or Sync Functions

### ❌ WRONG - Sync Function (No async/Promise)

```typescript
// Sync function - no async keyword
export function get(args: GetArgs): GetResult {
  return data[args.id];
}
```

**Why this might cause issues:**
- ⚠️ Cannot use await inside function
- ⚠️ Future changes requiring I/O break the contract
- ⚠️ Implicit wrapping by RPC layer (less clear)

**Note:** Sync functions ARE supported and auto-wrapped as Promise<Result>, but they're not recommended.

### ✅ RIGHT - Always Use Async

```typescript
// Async function - explicit Promise return
export async function get(args: GetArgs): Promise<GetResult> {
  const value = await loadData(args.id);
  return { value, exists: true };
}
```

**Why this is good:**
- ✅ Can use await for I/O operations
- ✅ Explicit async contract
- ✅ Future-proof for async operations
- ✅ Consistent with async-first design

---

## Sync vs Async Functions - The Reality

### What Actually Works

| Aspect | Async (Recommended) | Sync (Supported) |
|--------|-------------------|------------------|
| Declaration | `export async function` | `export function` |
| Return type | `Promise<Result>` | `Result` |
| Can await within | ✅ Yes | ❌ No |
| Type clarity | ✅ Clear contract | ⚠️ Implicit wrapping |
| RPC discovery | ✅ Fully supported | ✅ Works (auto-wrapped) |

### When Sync Functions Are Acceptable

**✅ Use sync functions for:**
- Pure functions with no I/O (e.g., `add(a, b)`, `formatDate()`)
- Data transformations
- Calculations
- Simple validation

**❌ Never use sync functions for:**
- File operations
- Network calls
- Database queries
- Any external system interaction

### Example: Pure Function (Sync OK)

```typescript
export interface AddArgs { a: number; b: number; }
export interface AddResult { sum: number; }

// Sync is fine here - pure calculation
export function add(args: AddArgs): AddResult {
  return { sum: args.a + args.b };
}
```

This gets auto-wrapped as `Promise<AddResult>` by the RPC layer.

### Recommendation

**Always use `export async`** even if you don't use `await` inside:
- Makes the async contract explicit
- Ready for async operations if requirements change
- Prevents accidental blocking operations in future
- No performance penalty

---

## Anti-Pattern 4: Multiple Arguments

### ❌ WRONG - Violates RPC Protocol

```typescript
// Multiple parameters - will be silently excluded
export async function search(query: string, limit: number): Promise<SearchResult> {
  // implementation
}
```

**Why this is bad:**
- ❌ Function silently excluded from RpcClient interface
- ❌ Violates RPC protocol requirement
- ❌ Caller gets confusing "Property does not exist" error
- ❌ No clear indication why it doesn't work

**What happens:**

```bash
$ lootbox tools types search
# Types extracted successfully:
export interface SearchArgs { query: string; limit: number; }

export interface RpcClient {
  search: {
    // ❌ search() is NOT listed here because it has 2 parameters
    // Other functions appear here, but not search()
  };
}
```

**Caller experience:**
```typescript
await tools.search.search('keyword', 10);
// ❌ Error: Property 'search' does not exist on type '{ /* other functions */ }'
```

### ✅ RIGHT - Single Args Object

```typescript
export interface SearchArgs { 
  query: string; 
  limit?: number;  // Optional with default
}

export interface SearchResult {
  results: Array<unknown>;
  total: number;
}

export async function search(args: SearchArgs): Promise<SearchResult> {
  const limit = args.limit ?? 100;  // Default value
  // implementation
}
```

**Why this is good:**
- ✅ Follows RPC protocol
- ✅ Function appears in RpcClient interface
- ✅ Supports optional parameters with defaults
- ✅ Easy to add new parameters without breaking changes

**Caller experience:**
```typescript
// With all arguments
await tools.search.search({ query: 'keyword', limit: 10 });

// With defaults
await tools.search.search({ query: 'keyword' });
```

---

## Anti-Pattern 5: Blocking Operations

### ❌ WRONG - Exceeds Timeout

```typescript
// Blocks entire worker for 60+ seconds
export async function slowOp(args: Args): Promise<Result> {
  const result = await veryExpensiveOperation();  // 60 seconds
  return { result };
}
```

**Why this is bad:**
- ❌ Exceeds 10-second timeout
- ❌ Fails with timeout error
- ❌ Wastes resources
- ❌ Poor user experience

### ✅ RIGHT - Use Caching or Chunking

**Option 1: Caching**
```typescript
let cache: Result | null = null;
let cacheTime = 0;
const TTL = 5 * 60 * 1000;  // 5 minutes

export async function quickOp(args: Args): Promise<Result> {
  const now = Date.now();
  
  // Return cached if fresh
  if (cache && (now - cacheTime) < TTL) {
    return cache;
  }
  
  // Fetch fresh (optimized to < 10 seconds)
  const result = await reasonablyFastOperation(args);
  cache = result;
  cacheTime = now;
  
  return result;
}
```

**Option 2: Chunking**
```typescript
export interface ProcessChunkArgs {
  chunkIndex: number;
  chunkSize: number;
}

export interface ProcessChunkResult {
  processed: number;
  totalChunks: number;
  complete: boolean;
}

export async function processChunk(args: ProcessChunkArgs): Promise<ProcessChunkResult> {
  const items = await loadItems();
  const totalChunks = Math.ceil(items.length / args.chunkSize);
  
  const start = args.chunkIndex * args.chunkSize;
  const chunk = items.slice(start, start + args.chunkSize);
  
  // Process chunk (< 10 seconds)
  await processItems(chunk);
  
  return {
    processed: chunk.length,
    totalChunks,
    complete: args.chunkIndex >= totalChunks - 1
  };
}
```

---

## Anti-Pattern 6: Ignoring Error Handling

### ❌ WRONG - No Validation or Error Handling

```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  // No validation
  const result = await database.insert(args.name);
  return { id: result.id };
}
```

**Why this is bad:**
- ❌ Crashes on null/empty name
- ❌ No clear error messages
- ❌ Database errors propagate raw
- ❌ Caller can't distinguish error types

### ✅ RIGHT - Validate Inputs and Handle Errors

```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  // Validate input
  if (!args.name || args.name.trim() === '') {
    throw new Error('Name is required and cannot be empty');
  }
  
  if (args.name.length > 100) {
    throw new Error('Name cannot exceed 100 characters');
  }
  
  // Handle external failures
  try {
    const result = await database.insert(args.name);
    return { id: result.id, success: true };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Failed to create record: ${message}`);
  }
}
```

**Why this is good:**
- ✅ Clear, actionable error messages
- ✅ Validates at entry point (fail fast)
- ✅ Handles external failures gracefully
- ✅ Provides context in error messages

---

## Anti-Pattern 7: Inconsistent Naming

### ❌ WRONG - Mismatched Names

```typescript
// Args interface doesn't match function name
export interface UserArgs { id: string; }
export interface UserResult { data: unknown; }

// Function name is 'get' but interfaces say 'User'
export async function get(args: UserArgs): Promise<UserResult> {
  // implementation
}
```

**Why this is bad:**
- ❌ Confusing for developers
- ❌ Breaks naming convention
- ❌ Harder to maintain

### ✅ RIGHT - Follow Naming Convention

```typescript
// Interfaces match function name
export interface GetArgs { id: string; }
export interface GetResult { data: unknown; }

export async function get(args: GetArgs): Promise<GetResult> {
  // implementation
}
```

**Convention:**
- Function: `functionName`
- Args: `FunctionNameArgs` (PascalCase)
- Result: `FunctionNameResult` (PascalCase)

---

## Anti-Pattern 8: Not Using Inline Types When Appropriate

### ⚠️ CLARIFICATION - Inline Types Are Not Broken

**Common misconception:** "Inline types don't work"

**Reality:** Inline types work perfectly and appear in RpcClient interface.

**Inline type example:**
```typescript
// This works fine
export async function get(args: { id: string }): Promise<{ value: unknown }> {
  return { value: data[args.id] };
}
```

**Generated RpcClient:**
```typescript
export interface RpcClient {
  mytools: {
    get(args: { id: string }): Promise<{ value: unknown }>;  // ✅ Works
  };
}
```

### Why Named Interfaces Are Still Recommended

**Use named interfaces for:**
- ✅ Better documentation and discoverability
- ✅ Consistent naming convention across codebase
- ✅ Easier to reference in other files
- ✅ Follows established `<FunctionName>Args` pattern
- ✅ More professional/maintainable code

**Use inline types when:**
- ✅ Prototyping or quick tests
- ✅ Single-use, simple shapes
- ✅ You explicitly prefer brevity

**Inline types are NOT broken—they're just not the recommended convention.**

---

## Anti-Pattern 9: Returning Raw External Data

### ❌ WRONG - No Transformation

```typescript
export async function getUser(args: GetUserArgs): Promise<unknown> {
  // Returns raw API response
  const response = await fetch(`/api/users/${args.id}`);
  return await response.json();
}
```

**Why this is bad:**
- ❌ No type safety
- ❌ Exposes internal API structure
- ❌ Difficult to change API provider
- ❌ May include sensitive fields

### ✅ RIGHT - Transform to Defined Interface

```typescript
export interface GetUserResult {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export async function getUser(args: GetUserArgs): Promise<GetUserResult> {
  const response = await fetch(`/api/users/${args.id}`);
  const raw = await response.json();
  
  // Transform to defined interface
  return {
    id: raw.userId,
    name: raw.fullName,
    email: raw.emailAddress,
    createdAt: raw.created
  };
}
```

**Why this is good:**
- ✅ Type-safe return value
- ✅ Hides internal API details
- ✅ Easy to swap API providers
- ✅ Controls what's exposed

---

## Anti-Pattern 10: Mutating Arguments

### ❌ WRONG - Modifying Input

```typescript
export async function process(args: ProcessArgs): Promise<ProcessResult> {
  // Mutates caller's data
  args.items.sort();
  args.processed = true;
  
  return { success: true };
}
```

**Why this is bad:**
- ❌ Unexpected side effects
- ❌ Breaks caller's assumptions
- ❌ Hard to debug
- ❌ Not idempotent

### ✅ RIGHT - Pure Function (No Mutation)

```typescript
export async function process(args: ProcessArgs): Promise<ProcessResult> {
  // Create new sorted array, don't mutate original
  const sorted = [...args.items].sort();
  
  const processed = await processItems(sorted);
  
  return { 
    success: true, 
    processedCount: processed.length 
  };
}
```

**Why this is good:**
- ✅ No side effects
- ✅ Predictable behavior
- ✅ Easier to test
- ✅ Idempotent

---

## Summary: Golden Rules

1. **Always define Args and Result interfaces** - Never use `unknown` or untyped parameters
2. **Use async functions** - Even for pure functions, for consistency
3. **Single object parameter** - Never multiple arguments
4. **Handle errors gracefully** - Validate inputs, catch external failures
5. **Follow naming conventions** - `FunctionNameArgs`, `FunctionNameResult`
6. **Stay under 10-second timeout** - Use caching, chunking, or async kickoff
7. **Transform external data** - Don't return raw API responses
8. **Don't mutate arguments** - Keep functions pure
9. **Prefer named interfaces** - Inline types work but aren't the convention
10. **Test thoroughly** - Verify discovery, types, and execution

---

## Verification Checklist

Before committing your tool:

- ☐ All functions have `*Args` and `*Result` interfaces
- ☐ Functions use `async` keyword
- ☐ Single object parameter (not multiple args)
- ☐ Input validation with clear error messages
- ☐ Naming convention followed
- ☐ Executes in < 10 seconds
- ☐ No mutation of arguments
- ☐ External data transformed to typed interfaces
- ☐ `lootbox tools` shows namespace
- ☐ `lootbox tools types <namespace>` succeeds
- ☐ `lootbox exec 'await tools...'` works
- ☐ Error cases tested

