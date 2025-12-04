# Lootbox Tool Implementation Patterns

Common, battle-tested patterns for building lootbox tools.

## Pattern 1: Simple Sync Operation

**Best for:** Stateless operations, calculations, transformations

```typescript
export interface AddArgs {
  a: number;
  b: number;
}

export interface AddResult {
  result: number;
  operation: string;
}

export async function add(args: AddArgs): Promise<AddResult> {
  return {
    result: args.a + args.b,
    operation: "addition",
  };
}
```

**Usage:**
```typescript
const result = await tools.calculator.add({a: 5, b: 3});
// {result: 8, operation: "addition"}
```

---

## Pattern 2: CRUD with Data Storage

**Best for:** Persistent data (files, database, key-value store)

```typescript
let store: Record<string, unknown> = {};

export interface StoreSetArgs {
  key: string;
  value: unknown;
}

export interface StoreSetResult {
  success: boolean;
  key: string;
}

export async function set(args: StoreSetArgs): Promise<StoreSetResult> {
  store[args.key] = args.value;
  // TODO: persist to file/database
  return { success: true, key: args.key };
}

export interface StoreGetArgs {
  key: string;
}

export interface StoreGetResult {
  value: unknown;
  exists: boolean;
}

export async function get(args: StoreGetArgs): Promise<StoreGetResult> {
  const value = store[args.key];
  return { value, exists: value !== undefined };
}
```

---

## Pattern 3: Caching with TTL

**Best for:** Expensive operations (API calls, computations)

```typescript
interface CacheEntry {
  data: unknown;
  timestamp: number;
}

let cache: Record<string, CacheEntry> = {};
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

function getCached(key: string): unknown | null {
  const entry = cache[key];
  if (!entry) return null;

  if (Date.now() - entry.timestamp > CACHE_TTL) {
    delete cache[key];
    return null;
  }

  return entry.data;
}

function setCached(key: string, data: unknown): void {
  cache[key] = { data, timestamp: Date.now() };
}

export interface SearchArgs {
  query: string;
}

export interface SearchResult {
  results: unknown[];
  cached: boolean;
}

export async function search(args: SearchArgs): Promise<SearchResult> {
  // Check cache first
  const cached = getCached(`search:${args.query}`);
  if (cached !== null) {
    return { results: cached as unknown[], cached: true };
  }

  // Fetch fresh data
  const results = await expensiveSearch(args.query);
  setCached(`search:${args.query}`, results);

  return { results, cached: false };
}
```

---

## Pattern 4: API Integration with Error Handling

**Best for:** External API calls

```typescript
async function apiCall<T>(
  method: string,
  endpoint: string,
  body?: unknown
): Promise<T> {
  const url = `https://api.example.com${endpoint}`;
  const response = await fetch(url, {
    method,
    headers: {
      "Authorization": `Bearer ${Deno.env.get("API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${await response.text()}`);
  }

  return await response.json() as T;
}

export interface FetchUserArgs {
  userId: string;
}

export interface FetchUserResult {
  success: boolean;
  user?: { id: string; name: string; email: string };
  error?: string;
}

export async function fetchUser(args: FetchUserArgs): Promise<FetchUserResult> {
  if (!args.userId) {
    return { success: false, error: "User ID is required" };
  }

  try {
    const user = await apiCall<{ id: string; name: string; email: string }>(
      "GET",
      `/users/${args.userId}`
    );
    return { success: true, user };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

---

## Pattern 5: Batch Processing

**Best for:** Processing multiple items, parallel vs sequential

```typescript
export interface ProcessItemsArgs {
  items: Array<{ id: string; data: unknown }>;
  parallel?: boolean;
}

export interface ProcessItemsResult {
  successful: Array<{ id: string; result: unknown }>;
  failed: Array<{ id: string; error: string }>;
  totalMs: number;
}

async function processOne(item: { id: string; data: unknown }): Promise<unknown> {
  // Process a single item
  // This might be an API call, computation, etc.
  return { processed: true, item: item.id };
}

export async function processItems(args: ProcessItemsArgs): Promise<ProcessItemsResult> {
  const startTime = Date.now();
  const successful: Array<{ id: string; result: unknown }> = [];
  const failed: Array<{ id: string; error: string }> = [];

  if (args.parallel) {
    // Process in parallel with Promise.allSettled
    const results = await Promise.allSettled(
      args.items.map((item) => processOne(item).then((result) => ({ id: item.id, result })))
    );

    results.forEach((r) => {
      if (r.status === "fulfilled") {
        successful.push(r.value);
      } else {
        failed.push({
          id: args.items.find((i) => i.id === (r.reason as any).id)?.id || "unknown",
          error: r.reason.message,
        });
      }
    });
  } else {
    // Process sequentially
    for (const item of args.items) {
      try {
        const result = await processOne(item);
        successful.push({ id: item.id, result });
      } catch (error) {
        failed.push({
          id: item.id,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }
  }

  return {
    successful,
    failed,
    totalMs: Date.now() - startTime,
  };
}
```

**Usage:**
```typescript
// Sequential processing (slower, predictable)
const result1 = await tools.batch.processItems({
  items: [{id: "1", data: ...}, {id: "2", data: ...}]
});

// Parallel processing (faster, concurrent)
const result2 = await tools.batch.processItems({
  items: [{id: "1", data: ...}, {id: "2", data: ...}],
  parallel: true
});
```

---

## Pattern 6: Pagination

**Best for:** Large datasets, listing operations

```typescript
export interface ListArgs {
  limit?: number;
  offset?: number;
  sort?: "asc" | "desc";
}

export interface ListResult<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}

export async function listUsers(args: ListArgs): Promise<ListResult<{ id: string; name: string }>> {
  const limit = Math.min(args.limit || 10, 100); // Max 100 per request
  const offset = args.offset || 0;

  const allUsers = await loadAllUsers();

  // Apply sorting
  const sorted = args.sort === "desc" ? allUsers.reverse() : allUsers;

  // Apply pagination
  const paginated = sorted.slice(offset, offset + limit);

  return {
    items: paginated.map((u) => ({ id: u.id, name: u.name })),
    total: allUsers.length,
    limit,
    offset,
    hasMore: offset + limit < allUsers.length,
  };
}
```

**Usage:**
```typescript
// Get first page
const page1 = await tools.users.listUsers({limit: 10, offset: 0});
console.log(page1.hasMore); // true if more results exist

// Get next page
const page2 = await tools.users.listUsers({limit: 10, offset: 10});
```

---

## Pattern 7: Validation & Error Consistency

**Best for:** Input validation, consistent error handling

```typescript
export interface CreateUserArgs {
  name: string;
  email: string;
  age?: number;
}

export interface CreateUserResult {
  success: boolean;
  userId?: string;
  errors?: string[]; // List of validation errors
}

export async function createUser(args: CreateUserArgs): Promise<CreateUserResult> {
  const errors: string[] = [];

  // Validate required fields
  if (!args.name || args.name.trim() === "") {
    errors.push("Name is required");
  }
  if (!args.email || !args.email.includes("@")) {
    errors.push("Valid email is required");
  }

  // Validate optional fields
  if (args.age !== undefined) {
    if (args.age < 0 || args.age > 150) {
      errors.push("Age must be between 0 and 150");
    }
  }

  // Return errors if validation failed
  if (errors.length > 0) {
    return { success: false, errors };
  }

  // Create user
  const userId = await saveUser({
    name: args.name,
    email: args.email,
    age: args.age,
  });

  return { success: true, userId };
}
```

---

## Pattern 8: State Management with Persistence

**Best for:** Stateful operations, counters, history

```typescript
interface State {
  counter: number;
  lastUpdated: number;
  history: Array<{ value: number; timestamp: number }>;
}

let state: State = {
  counter: 0,
  lastUpdated: Date.now(),
  history: [],
};

async function loadState(): Promise<void> {
  // TODO: Load from file/database
  // state = JSON.parse(await Deno.readTextFile("./state.json"));
}

async function saveState(): Promise<void> {
  // TODO: Save to file/database
  // await Deno.writeTextFile("./state.json", JSON.stringify(state, null, 2));
}

export interface IncrementArgs {
  amount?: number;
}

export interface IncrementResult {
  counter: number;
  previousValue: number;
}

export async function increment(args: IncrementArgs): Promise<IncrementResult> {
  await loadState();

  const previousValue = state.counter;
  const amount = args.amount || 1;

  state.counter += amount;
  state.lastUpdated = Date.now();
  state.history.push({
    value: state.counter,
    timestamp: state.lastUpdated,
  });

  // Keep only last 100 items
  if (state.history.length > 100) {
    state.history = state.history.slice(-100);
  }

  await saveState();

  return { counter: state.counter, previousValue };
}

export interface GetStateResult {
  counter: number;
  lastUpdated: number;
  historyLength: number;
}

export async function getState(): Promise<GetStateResult> {
  await loadState();

  return {
    counter: state.counter,
    lastUpdated: state.lastUpdated,
    historyLength: state.history.length,
  };
}
```

---

## Pattern 9: Data Transformation Pipeline

**Best for:** Multi-step transformations

```typescript
export interface TransformArgs {
  input: unknown;
  steps: ("uppercase" | "reverse" | "trim" | "lowercase")[];
}

export interface TransformResult {
  input: unknown;
  output: unknown;
  stepsApplied: string[];
}

function applyTransform(data: unknown, step: string): unknown {
  if (typeof data !== "string") {
    throw new Error("Input must be string for transformations");
  }

  switch (step) {
    case "uppercase":
      return data.toUpperCase();
    case "lowercase":
      return data.toLowerCase();
    case "reverse":
      return data.split("").reverse().join("");
    case "trim":
      return data.trim();
    default:
      throw new Error(`Unknown step: ${step}`);
  }
}

export async function transform(args: TransformArgs): Promise<TransformResult> {
  let result = args.input;
  const stepsApplied: string[] = [];

  for (const step of args.steps) {
    result = applyTransform(result, step);
    stepsApplied.push(step);
  }

  return {
    input: args.input,
    output: result,
    stepsApplied,
  };
}
```

**Usage:**
```typescript
const result = await tools.transform.transform({
  input: "  Hello World  ",
  steps: ["trim", "lowercase", "reverse"]
});
// output: "dlrow olleh"
```

---

## Choosing the Right Pattern

| Use Case | Pattern | Key Features |
|----------|---------|--------------|
| Simple calculations | Pattern 1 | Stateless, fast |
| Persistent storage | Pattern 2 | Files/database backed |
| Expensive operations | Pattern 3 | Caching with TTL |
| External APIs | Pattern 4 | Error handling |
| Multiple items | Pattern 5 | Batch processing |
| Large datasets | Pattern 6 | Pagination |
| Validated input | Pattern 7 | Error lists |
| State over time | Pattern 8 | Persistence |
| Multi-step processing | Pattern 9 | Pipelines |

---

## Performance Considerations

### Keep Functions Fast

- Target: < 1 second per call
- Warn: 1-10 seconds per call
- Timeout: 30 seconds (hard limit)

**Optimization strategies:**
1. Cache expensive results
2. Use pagination for large datasets
3. Offer parallel processing option
4. Batch operations when possible
5. Return early on validation failure

### Memory Management

- Don't store unlimited cache (use TTL)
- Stream large files instead of loading all at once
- Clear state after batch operations
- Use appropriate data structures (Map vs Object)

### Error Recovery

- Throw specific errors with context
- Return partial results when possible
- Log failures for debugging
- Don't retry automatically (let caller decide)

---

## Testing Patterns

### Test Individual Functions

```bash
lootbox exec 'await tools.users.createUser({name: "Alice", email: "alice@example.com"})'
```

### Test Edge Cases

```bash
# Test with invalid input
lootbox exec 'await tools.users.createUser({name: "", email: "invalid"})'

# Test with missing fields
lootbox exec 'await tools.users.createUser({name: "Bob"})'

# Test with optional fields
lootbox exec 'await tools.users.createUser({name: "Charlie", email: "charlie@example.com", age: 30})'
```

### Write Test Scripts

Save common test scenarios for reuse:

```typescript
// test_users.ts
const tests = [
  { name: "Valid user", args: {name: "Alice", email: "alice@example.com"}, expectSuccess: true },
  { name: "Invalid email", args: {name: "Bob", email: "invalid"}, expectSuccess: false },
  { name: "Missing name", args: {name: "", email: "test@example.com"}, expectSuccess: false },
];

for (const test of tests) {
  try {
    const result = await tools.users.createUser(test.args);
    const success = result.success;
    console.log(`${test.name}: ${success === test.expectSuccess ? "✓" : "✗"}`);
  } catch (error) {
    console.log(`${test.name}: ERROR - ${error.message}`);
  }
}
```

Run with: `lootbox exec --file test_users.ts`
