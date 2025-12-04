# Advanced Patterns for Lootbox Tools

This reference provides battle-tested implementation patterns for common tool scenarios, with complete code examples and usage guidance.

---

## Pattern 1: Simple CRUD Tool

**Use when:** Building basic data storage, key-value stores, simple databases

**Complete implementation:**

```typescript
// Type interfaces for all operations
export interface GetArgs { id: string; }
export interface GetResult { data: unknown; exists: boolean; }

export interface SetArgs { id: string; data: unknown; }
export interface SetResult { success: boolean; id: string; }

export interface DeleteArgs { id: string; }
export interface DeleteResult { success: boolean; }

// Implementation functions
export async function get(args: GetArgs): Promise<GetResult> {
  const store = await loadStore();
  const data = store[args.id];
  return { data, exists: !!data };
}

export async function set(args: SetArgs): Promise<SetResult> {
  const store = await loadStore();
  store[args.id] = args.data;
  await saveStore(store);
  return { success: true, id: args.id };
}

export async function remove(args: DeleteArgs): Promise<DeleteResult> {
  const store = await loadStore();
  delete store[args.id];
  await saveStore(store);
  return { success: true };
}
```

**Key characteristics:**
- ✅ Complete type safety with Args/Result interfaces
- ✅ Consistent naming conventions
- ✅ Clear success/failure indicators
- ✅ Exists flag for get() prevents null confusion

**Usage:**
```typescript
// Get data
const result = await tools.storage.get({ id: 'user-123' });
if (result.exists) {
  console.log('Found:', result.data);
}

// Set data
await tools.storage.set({ id: 'user-123', data: { name: 'Alice' } });

// Delete data
await tools.storage.remove({ id: 'user-123' });
```

---

## Pattern 2: Caching with TTL (Time-To-Live)

**Use when:** Reducing expensive API calls, caching external data, rate-limiting protection

**Complete implementation:**

```typescript
// Module-level cache state
let cache: Record<string, unknown> | null = null;
let cacheTime: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes in milliseconds

// Private helper function
async function getCached(): Promise<Record<string, unknown>> {
  const now = Date.now();
  
  // Check if cache exists and is fresh
  if (cache && (now - cacheTime) < CACHE_TTL) {
    return cache;
  }
  
  // Cache miss or expired - fetch fresh data
  cache = await fetchFresh();
  cacheTime = now;
  return cache;
}

// Public tool function
export interface GetDataArgs { 
  useCache?: boolean;  // Optional, defaults to true
}

export interface GetDataResult { 
  data: unknown; 
  cached: boolean;  // Indicates if result came from cache
}

export async function getData(args: GetDataArgs): Promise<GetDataResult> {
  const useCache = args.useCache !== false;  // Default to true
  const data = useCache ? await getCached() : await fetchFresh();
  return { data, cached: useCache && !!cache };
}
```

**Key characteristics:**
- ✅ Reduces expensive external calls
- ✅ Configurable cache bypass
- ✅ Returns cache status for debugging
- ✅ Simple timestamp-based expiration

**Advanced variations:**

**Per-key caching:**
```typescript
interface CacheEntry { data: unknown; timestamp: number; }
const cache = new Map<string, CacheEntry>();

async function getCachedByKey(key: string): Promise<unknown> {
  const entry = cache.get(key);
  const now = Date.now();
  
  if (entry && (now - entry.timestamp) < CACHE_TTL) {
    return entry.data;
  }
  
  const data = await fetchByKey(key);
  cache.set(key, { data, timestamp: now });
  return data;
}
```

**Cache invalidation:**
```typescript
export interface InvalidateCacheArgs { key?: string; }
export interface InvalidateCacheResult { cleared: boolean; }

export async function invalidateCache(args: InvalidateCacheArgs): Promise<InvalidateCacheResult> {
  if (args.key) {
    cache.delete(args.key);
  } else {
    cache.clear();
  }
  return { cleared: true };
}
```

**Usage:**
```typescript
// First call - fetches fresh data
const result1 = await tools.api.getData({ useCache: true });
console.log(result1.cached); // false

// Second call within TTL - uses cache
const result2 = await tools.api.getData({ useCache: true });
console.log(result2.cached); // true

// Force fresh data
const result3 = await tools.api.getData({ useCache: false });
console.log(result3.cached); // false
```

---

## Pattern 3: Batch Processing with Error Handling

**Use when:** Processing multiple items, bulk operations, parallel execution with partial failure tolerance

**Complete implementation:**

```typescript
export interface ProcessItemsArgs {
  items: Array<{ id: string; data: unknown }>;
  parallel?: boolean;  // Optional, defaults to sequential
}

export interface ProcessItemsResult {
  successful: Array<{ id: string; result: unknown }>;
  failed: Array<{ id: string; error: string }>;
}

export async function processItems(args: ProcessItemsArgs): Promise<ProcessItemsResult> {
  const successful: Array<{ id: string; result: unknown }> = [];
  const failed: Array<{ id: string; error: string }> = [];

  if (args.parallel) {
    // Parallel execution with Promise.allSettled
    const results = await Promise.allSettled(
      args.items.map(async (item) => {
        try {
          const result = await processItem(item);
          return { status: 'success' as const, id: item.id, result };
        } catch (error) {
          return { 
            status: 'error' as const, 
            id: item.id, 
            error: error instanceof Error ? error.message : String(error)
          };
        }
      })
    );

    // Separate successes from failures
    results.forEach((r) => {
      if (r.status === 'fulfilled' && r.value.status === 'success') {
        successful.push({ id: r.value.id, result: r.value.result });
      } else {
        const err = r.status === 'rejected' ? r.reason : r.value.error;
        failed.push({ 
          id: r.status === 'fulfilled' ? r.value.id : 'unknown',
          error: String(err) 
        });
      }
    });
  } else {
    // Sequential execution
    for (const item of args.items) {
      try {
        const result = await processItem(item);
        successful.push({ id: item.id, result });
      } catch (error) {
        failed.push({ 
          id: item.id, 
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
  }

  return { successful, failed };
}
```

**Key characteristics:**
- ✅ Handles partial failures gracefully
- ✅ Reports both successes and failures
- ✅ Supports parallel or sequential execution
- ✅ Doesn't throw on individual item failures

**When to use parallel vs sequential:**

| Use Parallel | Use Sequential |
|--------------|----------------|
| Independent operations | Order matters |
| I/O-bound (API calls) | Rate-limited APIs |
| No shared state | Shared state updates |
| Fast completion priority | Predictable memory usage |

**Usage:**
```typescript
const items = [
  { id: '1', data: { value: 100 } },
  { id: '2', data: { value: 200 } },
  { id: '3', data: { value: -1 } },  // Invalid, will fail
];

// Sequential processing
const result = await tools.batch.processItems({ 
  items, 
  parallel: false 
});

console.log(`Succeeded: ${result.successful.length}`);
console.log(`Failed: ${result.failed.length}`);

result.failed.forEach(f => {
  console.error(`Item ${f.id} failed: ${f.error}`);
});
```

---

## Pattern 4: Retry Logic with Exponential Backoff

**Use when:** Handling transient failures, rate-limited APIs, network instability

**Implementation:**

```typescript
export interface RetryableArgs {
  operation: string;
  maxRetries?: number;
  initialDelayMs?: number;
}

export interface RetryableResult {
  success: boolean;
  attempts: number;
  result?: unknown;
  error?: string;
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export async function retryableOperation(args: RetryableArgs): Promise<RetryableResult> {
  const maxRetries = args.maxRetries ?? 3;
  const initialDelay = args.initialDelayMs ?? 1000;
  
  let lastError: Error | null = null;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const result = await performOperation(args.operation);
      return { success: true, attempts: attempt, result };
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Don't retry on last attempt
      if (attempt < maxRetries) {
        const delay = initialDelay * Math.pow(2, attempt - 1);  // Exponential backoff
        console.error(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
        await sleep(delay);
      }
    }
  }
  
  return { 
    success: false, 
    attempts: maxRetries,
    error: lastError?.message ?? 'Unknown error'
  };
}
```

**Key characteristics:**
- ✅ Exponential backoff prevents hammering failures
- ✅ Configurable retry count and initial delay
- ✅ Returns attempt count for diagnostics
- ✅ Doesn't retry on last attempt

**Usage:**
```typescript
const result = await tools.resilient.retryableOperation({
  operation: 'fetch-user-data',
  maxRetries: 5,
  initialDelayMs: 500
});

if (result.success) {
  console.log(`Succeeded after ${result.attempts} attempts`);
} else {
  console.error(`Failed after ${result.attempts} attempts: ${result.error}`);
}
```

---

## Pattern 5: Pagination Support

**Use when:** Working with large datasets, API pagination, memory-constrained environments

**Implementation:**

```typescript
export interface ListArgs {
  page?: number;      // 1-based page number
  pageSize?: number;  // Items per page
  cursor?: string;    // Optional cursor-based pagination
}

export interface ListResult {
  items: Array<unknown>;
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
  nextCursor?: string;
}

export async function list(args: ListArgs): Promise<ListResult> {
  const page = args.page ?? 1;
  const pageSize = args.pageSize ?? 100;
  
  const allItems = await loadAllItems();
  const total = allItems.length;
  
  // Calculate offset
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  
  // Slice page
  const items = allItems.slice(startIndex, endIndex);
  const hasMore = endIndex < total;
  
  return {
    items,
    total,
    page,
    pageSize,
    hasMore,
    nextCursor: hasMore ? String(page + 1) : undefined
  };
}
```

**Usage:**
```typescript
// Get first page
let result = await tools.data.list({ page: 1, pageSize: 50 });
console.log(`Page 1: ${result.items.length} items`);

// Get next page
while (result.hasMore) {
  result = await tools.data.list({ 
    page: result.page + 1, 
    pageSize: result.pageSize 
  });
  console.log(`Page ${result.page}: ${result.items.length} items`);
}
```

---

## Optimization Strategies

### Strategy 1: Lazy Loading

**Problem:** Loading entire dataset upfront is slow

**Solution:**
```typescript
let dataCache: Map<string, unknown> | null = null;

async function getItem(id: string): Promise<unknown> {
  if (!dataCache) {
    dataCache = new Map();
  }
  
  if (!dataCache.has(id)) {
    const item = await fetchItem(id);
    dataCache.set(id, item);
  }
  
  return dataCache.get(id);
}
```

---

### Strategy 2: Debouncing

**Problem:** Too many rapid calls to expensive operations

**Solution:**
```typescript
let debounceTimer: number | null = null;
let pendingArgs: Args | null = null;

export async function debouncedOperation(args: Args): Promise<Result> {
  pendingArgs = args;
  
  if (debounceTimer !== null) {
    clearTimeout(debounceTimer);
  }
  
  return new Promise((resolve) => {
    debounceTimer = setTimeout(async () => {
      const result = await performOperation(pendingArgs!);
      resolve(result);
      debounceTimer = null;
      pendingArgs = null;
    }, 300);  // 300ms debounce
  });
}
```

---

### Strategy 3: Connection Pooling

**Problem:** Creating new connections for each operation is expensive

**Solution:**
```typescript
let connectionPool: Connection[] = [];
const MAX_CONNECTIONS = 5;

async function getConnection(): Promise<Connection> {
  // Try to reuse idle connection
  const idle = connectionPool.find(c => !c.inUse);
  if (idle) {
    idle.inUse = true;
    return idle;
  }
  
  // Create new if under limit
  if (connectionPool.length < MAX_CONNECTIONS) {
    const conn = await createConnection();
    connectionPool.push(conn);
    return conn;
  }
  
  // Wait for available connection
  return new Promise((resolve) => {
    const interval = setInterval(() => {
      const available = connectionPool.find(c => !c.inUse);
      if (available) {
        clearInterval(interval);
        available.inUse = true;
        resolve(available);
      }
    }, 50);
  });
}
```

---

## Function Execution Limits & Workarounds

### 10-Second Timeout Limit

**Reality:** All tool functions have a **10-second execution timeout**.

**Workarounds:**

**1. Chunking Strategy:**
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
  const items = await loadAllItems();
  const totalChunks = Math.ceil(items.length / args.chunkSize);
  
  const start = args.chunkIndex * args.chunkSize;
  const end = start + args.chunkSize;
  const chunk = items.slice(start, end);
  
  // Process this chunk (should finish in < 10 seconds)
  await processItems(chunk);
  
  return {
    processed: chunk.length,
    totalChunks,
    complete: args.chunkIndex >= totalChunks - 1
  };
}
```

**2. Async Kickoff:**
```typescript
export interface StartJobArgs { jobId: string; params: unknown; }
export interface StartJobResult { jobId: string; status: 'started'; }

export async function startLongJob(args: StartJobArgs): Promise<StartJobResult> {
  // Kick off job asynchronously (doesn't wait)
  longRunningTask(args.jobId, args.params).catch(err => {
    console.error(`Job ${args.jobId} failed:`, err);
  });
  
  return { jobId: args.jobId, status: 'started' };
}

export interface CheckJobArgs { jobId: string; }
export interface CheckJobResult { jobId: string; status: string; result?: unknown; }

export async function checkJob(args: CheckJobArgs): Promise<CheckJobResult> {
  const status = await getJobStatus(args.jobId);
  return status;
}
```

**3. Caching for Expensive Operations:**
```typescript
// Cache expensive computation results
const computationCache = new Map<string, unknown>();

export async function expensiveComputation(args: ComputeArgs): Promise<ComputeResult> {
  const cacheKey = JSON.stringify(args);
  
  if (computationCache.has(cacheKey)) {
    return { result: computationCache.get(cacheKey), cached: true };
  }
  
  // Perform expensive computation (< 10 seconds)
  const result = await compute(args);
  computationCache.set(cacheKey, result);
  
  return { result, cached: false };
}
```

---

## When to Use Which Pattern

| Scenario | Pattern | Reason |
|----------|---------|--------|
| Simple data storage | CRUD Tool | Clear, predictable operations |
| External API calls | Caching with TTL | Reduces API costs and latency |
| Processing lists | Batch Processing | Handles partial failures gracefully |
| Unreliable external service | Retry with Backoff | Handles transient failures |
| Large datasets | Pagination | Prevents memory issues |
| Slow initial load | Lazy Loading | Defers expensive work |
| Rapid repeated calls | Debouncing | Reduces unnecessary operations |
| Database connections | Connection Pooling | Reuses expensive resources |
| Long-running tasks | Chunking or Async Kickoff | Works within 10-second limit |

---

## Testing Your Pattern

For each pattern, verify:

1. ☐ **Type safety:** Args and Result interfaces defined
2. ☐ **Discovery:** `lootbox tools types <namespace>` shows function
3. ☐ **Execution:** `lootbox exec 'await tools...'` works
4. ☐ **Error handling:** Invalid inputs produce clear errors
5. ☐ **Performance:** Completes within 10-second timeout
6. ☐ **Edge cases:** Empty inputs, null values, boundary conditions handled

