# Error Handling & Debugging

This reference provides comprehensive error handling patterns, common errors, and debugging strategies for lootbox tools development.

---

## Common Errors & Solutions

### Type-Checking Errors (caught before execution)

| Error | TypeScript Code | Cause | Fix |
|-------|-----------------|-------|-----|
| `Property 'X' does not exist` | TS2339 | Function not exported or wrong name | Add `export` before function, verify function name matches call |
| `Argument of type '{}' is not assignable to parameter of type 'X_YArgs'` | TS2345 | Missing required fields in arguments | Check `*Args` interface for required fields, provide all required arguments |
| `Type '...' is missing the following properties` | TS2739 | Wrong argument structure | Verify argument object has all required properties defined in `*Args` |

### Tool Discovery Errors (when running `lootbox tools` or `lootbox tools types`)

| Error | Cause | Fix |
|-------|-------|-----|
| Missing named `*Args` interface | Function uses inline type | Function works but doesn't follow naming convention. Add `export interface MyFunctionArgs {}` for consistency |
| Missing `*Result` interface | Function returns `Promise<unknown>` | Add `export interface MyFunctionResult {}` for type safety |
| `Failed to extract function X: Error: RPC function must have at most one parameter. Found N parameters` | Function has multiple parameters instead of single object | Change function signature from `func(a: T, b: U)` to `func(args: {a: T, b: U})` |
| `Namespace unavailable after fixing file` | Type extraction failed due to syntax error | Run `lootbox tools types <namespace>` to see detailed error, check TypeScript syntax |
| `Tool not in namespace` | File not in `.lootbox/tools/` | Move file to correct directory |

### Runtime Errors (caught during function execution)

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot divide by zero` or custom errors | Function validation failed | Check function input validation, provide valid arguments |
| `Timeout: function too long` | Exceeds 10 seconds | Optimize, cache, or break into smaller calls |
| Type mismatch at runtime | Return type doesn't match `*Result` interface | Verify return object has all fields in `*Result` interface |

---

## Error Handling Best Practices

### Validate inputs at entry point

**Pattern:**
```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  if (!args.name || args.name.trim() === '') {
    throw new Error('Name is required');
  }
  // ... implementation
}
```

**Why:**
- ✅ Fail fast - catch invalid input before expensive operations
- ✅ Clear error messages - tells caller exactly what's wrong
- ✅ Type safety - validates beyond TypeScript's compile-time checks

---

### Handle external failures gracefully

**Pattern:**
```typescript
try {
  const response = await fetch(args.url);
  const data = await response.json();
  return { success: true, data };
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  throw new Error(`API call failed: ${message}`);
}
```

**Why:**
- ✅ Provides context - "API call failed" tells more than raw fetch error
- ✅ Handles unknown error types - safely converts to string
- ✅ Maintains error stack - preserves debugging information

---

## Error Handling Patterns

### Option A: Throw Errors (Recommended for most cases)

**Pattern:**
```typescript
export async function create(args: CreateArgs): Promise<CreateResult> {
  if (!args.name) throw new Error('Name is required');
  // ... rest of implementation
}
```

**Characteristics:**
- ✅ Simple and idiomatic
- ✅ Stops execution immediately
- ✅ Works with try/catch in calling code
- ✅ TypeScript enforces handling

**Use cases:**
- Validation failures (missing required fields, invalid types)
- Unexpected conditions (database connection failed, file not found)
- Authorization issues (permission denied, unauthorized)
- Most single-operation functions

---

### Option B: Return Errors in Result Object (For partial success scenarios)

**Pattern:**
```typescript
export interface ProcessResult {
  data?: unknown;
  error?: string;
  success: boolean;
}

export async function process(args: ProcessArgs): Promise<ProcessResult> {
  if (!args.value) {
    return { success: false, error: 'Value is required' };
  }
  return { success: true, data: processedValue };
}
```

**Characteristics:**
- ✅ Allows partial success reporting
- ✅ Caller decides how to handle errors
- ✅ No need for try/catch
- ⚠️ Caller must check `success` field

**Use cases:**
- Batch operations (process 100 items, some fail)
- Retry scenarios (operation is retryable, let caller decide)
- Partial success (deletion of multiple items where some might fail)
- Complex operations with multiple phases

---

## Decision Tree: Which Pattern to Use?

```
Is this a batch operation or multi-phase process?
├─ Yes → Use Error-in-Result pattern
│         (Report both successes and failures)
│
└─ No → Use Throw Errors pattern
          (Simple, idiomatic, fail-fast)
```

**Guideline:** Choose one approach per tool and stick with it. Throwing errors is simpler and more idiomatic for most cases. Use error-in-result only when partial success is meaningful and you need to report both successes and failures together.

---

## Debugging Methodology

### Step 1: Identify the Phase

**Where did it fail?**
- **Type-checking phase** → Error before execution starts (TS errors)
- **Discovery phase** → `lootbox tools` or `lootbox tools types` errors
- **Execution phase** → Runtime errors during function execution

**How to tell:**
```bash
# Type-checking errors show TS error codes
lootbox exec 'await tools.foo.bar({})'
# TS2339 [ERROR]: Property 'bar' does not exist

# Discovery errors show during tools listing
lootbox tools types foo
# Failed to extract function bar: Error: ...

# Runtime errors show during execution
lootbox exec 'await tools.foo.bar({id: 1})'
# Error: Cannot connect to database
```

---

### Step 2: Verify Tool Structure

**Checklist:**
```bash
# 1. Tool file is in correct location
ls .lootbox/tools/foo.ts  # Should exist

# 2. Functions are exported
grep "export async function" .lootbox/tools/foo.ts

# 3. Type interfaces exist
grep "export interface.*Args" .lootbox/tools/foo.ts
grep "export interface.*Result" .lootbox/tools/foo.ts

# 4. Tool is discovered
lootbox tools | grep foo

# 5. Types are extracted
lootbox tools types foo
```

---

### Step 3: Test in Isolation

**Minimal test:**
```bash
# Test single function with minimal args
lootbox exec 'await tools.foo.bar({id: 1})'

# Test with console logging
lootbox exec 'console.log(await tools.foo.bar({id: 1}))'

# Test type extraction
lootbox tools types foo
```

---

### Step 4: Add Debugging Output

**Add logging to your tool:**
```typescript
export async function bar(args: BarArgs): Promise<BarResult> {
  console.error('[DEBUG] bar called with:', JSON.stringify(args));
  
  try {
    const result = await someOperation(args);
    console.error('[DEBUG] bar result:', JSON.stringify(result));
    return result;
  } catch (error) {
    console.error('[DEBUG] bar error:', error);
    throw error;
  }
}
```

**Why console.error:**
- ✅ Appears in terminal immediately (not buffered like console.log)
- ✅ Distinguishable from normal output
- ✅ Preserved in error logs

---

## Common Pitfalls & Solutions

### Pitfall 1: Silent Exclusion

**Problem:** Function is not showing up in `tools.namespace.*`

**Causes:**
- Multiple parameters instead of single object
- Not exported
- Wrong file location

**Solution:**
```bash
# Check what was discovered
lootbox tools types namespace

# Look for exclusion reasons
lootbox tools types namespace 2>&1 | grep -i "failed\|error"
```

---

### Pitfall 2: Timeout Confusion

**Problem:** "Timeout" error but unclear which phase

**Understanding:**
- 10-second timeout applies to **execution phase only**
- Type-checking failures happen **before** execution starts
- If you see TS errors, execution never started

**Solution:**
```typescript
// Break long operations into chunks
export async function processAll(args: ProcessAllArgs): Promise<ProcessAllResult> {
  // Instead of processing all items in one call
  // Return batch info and let caller request each batch
  return {
    totalBatches: Math.ceil(args.items.length / 100),
    batchSize: 100,
    message: 'Call processBatch() for each batch'
  };
}
```

---

### Pitfall 3: Inline Types vs Named Interfaces

**Problem:** Confusion about inline type support

**Reality:**
- ✅ Inline types **work correctly** (e.g., `args: { id: string }`)
- ✅ Function appears in RpcClient interface
- ⚠️ Not the recommended convention

**Recommendation:**
Use named interfaces for:
- Better documentation
- Consistent naming convention
- Easier to reference in other files
- Follows `<FunctionName>Args` / `<FunctionName>Result` pattern

**Not broken, just not preferred.**

---

## Validation Checklist

Before marking your tool as complete:

- ☐ **Type safety:** All functions have `*Args` and `*Result` interfaces
- ☐ **Discovery:** `lootbox tools` shows your namespace
- ☐ **Type extraction:** `lootbox tools types <namespace>` succeeds
- ☐ **Execution:** `lootbox exec 'await tools...'` works
- ☐ **Input validation:** Invalid inputs throw clear errors
- ☐ **Error handling:** External failures are caught and reported
- ☐ **Timeout awareness:** Long operations are chunked or cached
- ☐ **Debugging:** Console.error statements for critical paths
- ☐ **Documentation:** Functions have JSDoc comments explaining purpose

