# Advanced Lootbox Tool Usage Patterns

Professional patterns for building robust tool-based workflows using REAL installed tools (kv, sqlite, github, linear).

## SQLite Function Reference

**Quick Reference:**
- `query()` - For SELECT statements → Returns `{rows, columns, rowCount}`
- `execute()` - For INSERT/UPDATE/DELETE → Returns `{success, changes, lastInsertRowId}`
- `queryOne()` - For SELECT returning single row → Returns `{row}` (row is null if not found)
- `transaction()` - For multiple statements atomically → Returns `{success, executedCount, totalChanges}`

Use `query()` when you need to read data, `execute()` when you need to modify data.

---

## Pattern 1: Resilient Retry with Exponential Backoff

```typescript
async function callWithRetry<T = any>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelayMs: number = 100
): Promise<T> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (attempt < maxRetries - 1) {
        const delayMs = initialDelayMs * Math.pow(2, attempt);
        console.log(`Retry attempt ${attempt + 1}/${maxRetries} after ${delayMs}ms`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
  }

  throw lastError || new Error("Operation failed after all retries");
}

// Usage with GitHub (external API that can fail)
try {
  const result = await callWithRetry(
    () => tools.github.getRepo({repo: "anthropics/claude-code"}),
    3,
    100
  );
  console.log(`Repo: ${result.repo.name}`);
} catch (error) {
  console.error("Failed after retries:", error);
}
```

## Pattern 2: Parallel Batch Processing with Concurrency Limit

```typescript
async function processBatchWithLimit<T = any, R = any>(
  items: T[],
  processor: (item: T) => Promise<R>,
  concurrency: number = 5
): Promise<Array<{success: boolean; result?: R; error?: string}>> {
  const results: Array<{success: boolean; result?: R; error?: string}> = [];
  const queue = [...items];
  let running = 0;

  return new Promise((resolve, reject) => {
    const processNext = async () => {
      if (queue.length === 0 && running === 0) {
        resolve(results);
        return;
      }

      while (running < concurrency && queue.length > 0) {
        running++;
        const item = queue.shift();

        processor(item!).then(
          (result) => {
            results.push({success: true, result});
            running--;
            processNext();
          },
          (error) => {
            results.push({success: false, error: error.message});
            running--;
            processNext();
          }
        );
      }
    };

    processNext();
  });
}

// Usage: Fetch multiple GitHub repos in parallel with concurrency limit
const repoNames = ["anthropics/claude-code", "anthropics/anthropic-sdk-python", "anthropics/courses"];

const results = await processBatchWithLimit(
  repoNames,
  async (repo) => {
    const result = await tools.github.getRepo({repo});
    return {repo, stars: result.repo.stars};
  },
  5  // 5 concurrent requests (respects GitHub rate limits)
);

console.log(`Fetched ${results.filter(r => r.success).length}/${results.length} repos`);
```

## Pattern 3: Tool Result Caching with TTL

```typescript
interface CacheEntry<T = any> {
  value: T;
  timestamp: number;
  ttl: number;
}

class ToolCache<T = any> {
  private cache = new Map<string, CacheEntry<T>>();

  async get(
    key: string,
    fetcher: () => Promise<T>,
    ttlMs: number = 5 * 60 * 1000
  ): Promise<T> {
    const entry = this.cache.get(key);

    // Return cached if valid
    if (entry && Date.now() - entry.timestamp < entry.ttl) {
      return entry.value;
    }

    // Fetch fresh
    const value = await fetcher();

    // Cache it
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl: ttlMs,
    });

    return value;
  }

  clear(key?: string) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }
}

// Usage: Cache GitHub API calls with 1 minute TTL
const cache = new ToolCache<any>();

const repo = await cache.get(
  `github:anthropics/claude-code`,
  async () => {
    const result = await tools.github.getRepo({repo: "anthropics/claude-code"});
    return result.repo;
  },
  60000  // 1 minute TTL
);

console.log(`Repo: ${repo.name}, Stars: ${repo.stars}`);
```

## Pattern 4: Conditional Tool Composition

```typescript
// Chain tools based on intermediate results
async function fetchRepoWithDetails(repoName: string): Promise<any> {
  // Step 1: Get repo info
  let repoInfo: any;
  try {
    const result = await tools.github.getRepo({repo: repoName});
    repoInfo = result.repo;
  } catch (error) {
    throw new Error(`Repository not found: ${repoName}`);
  }

  // Step 2: Fetch related data based on repo characteristics
  let details: any = {};

  if (repoInfo.stars > 1000) {
    // High-profile repo - fetch issues
    try {
      const issues = await tools.github.listIssues({
        repo: repoName,
        state: "open",
        limit: 10
      });
      details.topIssues = issues.issues;
    } catch (error) {
      details.topIssues = [];
    }
  }

  // Cache the combined result
  const cacheKey = `repo:${repoName}:full`;
  await tools.kv.set({
    key: cacheKey,
    value: {...repoInfo, ...details}
  });

  // Step 3: Combine results
  return {
    ...repoInfo,
    ...details,
  };
}
```

## Pattern 5: Aggregating Results from Multiple Tools

```typescript
// Fetch from multiple tools and aggregate
async function buildRepoAnalysis(repoName: string): Promise<any> {
  // Fetch all data in parallel
  const [repoResult, issuesResult, cachedData] = await Promise.all([
    tools.github.getRepo({repo: repoName}).catch((e: any) => ({error: e.message})),
    tools.github.listIssues({repo: repoName, state: "open", limit: 5}).catch((e: any) => ({error: e.message})),
    tools.kv.get({key: `analysis:${repoName}`})
  ]) as any[];

  // Check for errors
  if ('error' in repoResult) {
    throw new Error(`Repository not found: ${repoName}`);
  }

  return {
    repo: repoResult.repo,
    openIssues: 'error' in issuesResult ? [] : issuesResult.issues,
    cached: cachedData.exists ? cachedData.value : null,
    analysisDate: new Date().toISOString()
  };
}
```

## Pattern 6: Error Aggregation in Batch Processing

```typescript
// Track successes and failures separately
async function batchStoreRepoData(repos: string[]): Promise<any> {
  const results: {
    successful: Array<{repo: string; stars: number}>;
    failed: Array<{repo: string; error: string}>;
  } = {
    successful: [],
    failed: [],
  };

  for (const repoName of repos) {
    try {
      // Fetch repo data
      const repoData = await tools.github.getRepo({repo: repoName});

      // Store in KV
      const storeResult = await tools.kv.set({
        key: `github:repo:${repoName}`,
        value: repoData.repo
      });

      if (storeResult.success) {
        results.successful.push({
          repo: repoName,
          stars: repoData.repo.stars
        });
      } else {
        results.failed.push({
          repo: repoName,
          error: "Failed to store in KV"
        });
      }
    } catch (error) {
      results.failed.push({
        repo: repoName,
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  }

  console.log(`Success: ${results.successful.length}, Failed: ${results.failed.length}`);
  return results;
}
```

## Pattern 7: Fallback Tool Selection

```typescript
// Try primary tool, fall back to secondary
async function fetchRepoData(repoName: string): Promise<any> {
  try {
    // Try KV cache first (fast)
    const cached = await tools.kv.get({key: `github:repo:${repoName}`});
    if (cached.exists) {
      console.log("From cache (fast)");
      return cached.value as any;
    }
  } catch (error) {
    console.log("Cache unavailable");
  }

  try {
    // Try GitHub API (slower, counts against rate limit)
    const result = await tools.github.getRepo({repo: repoName});

    // Store in cache for next time
    await tools.kv.set({
      key: `github:repo:${repoName}`,
      value: result.repo
    });

    console.log("From GitHub API (cached for next time)");
    return result.repo;
  } catch (error) {
    console.log("GitHub API failed, checking SQLite backup");
  }

  // Fall back to SQLite local backup
  const backup = await tools.sqlite.query({
    sql: "SELECT data FROM repo_backups WHERE name = ?",
    params: [repoName]
  });

  if (backup.rows.length > 0) {
    console.log("From SQLite backup");
    return JSON.parse((backup.rows[0] as any).data);
  }

  throw new Error(`No data available for repo: ${repoName}`);
}
```

## Pattern 8: Streaming Results with Tool Pagination

```typescript
// Process large result sets without loading everything
async function* streamAllKVEntries(pageSize: number = 50) {
  let offset = 0;
  let hasMore = true;

  while (hasMore) {
    const page = await tools.kv.list({limit: pageSize, offset});

    for (const entry of page.entries) {
      yield entry;
    }

    offset += page.returnedCount;
    hasMore = offset < page.totalCount;
  }
}

// Usage: Process all KV entries one at a time
for await (const entry of streamAllKVEntries(50)) {
  const e = entry as any;
  console.log(`Processing key: ${e.key}`);

  // Store metadata in SQLite
  await tools.sqlite.execute({
    sql: "INSERT OR REPLACE INTO kv_metadata (key, size, updated) VALUES (?, ?, ?)",
    params: [e.key, JSON.stringify(e.value).length, Date.now()]
  });
}
```

## Pattern 9: Tool-Based State Machine

```typescript
// Use tools to manage state transitions for Linear issue workflow
async function processLinearIssue(issueId: string): Promise<any> {
  // Get current issue
  let issue = await tools.linear.getIssue({issueId});

  while (issue.issue.state !== "Done" && issue.issue.state !== "Canceled") {
    console.log(`Issue ${issueId} state: ${issue.issue.state}`);

    // Store state transition in SQLite
    await tools.sqlite.execute({
      sql: "INSERT INTO issue_states (issue_id, state, timestamp) VALUES (?, ?, ?)",
      params: [issueId, issue.issue.state, Date.now()]
    });

    switch (issue.issue.state) {
      case "Backlog":
        // Move to Todo
        issue = await tools.linear.updateIssue({
          issueId,
          state: "Todo"
        });
        break;

      case "Todo":
        // Move to In Progress
        issue = await tools.linear.updateIssue({
          issueId,
          state: "In Progress"
        });
        break;

      case "In Progress":
        // Check if ready to review
        // (In real scenario, you'd check some condition)
        issue = await tools.linear.updateIssue({
          issueId,
          state: "In Review"
        });
        break;

      case "In Review":
        // Mark as done
        issue = await tools.linear.updateIssue({
          issueId,
          state: "Done"
        });
        break;
    }

    // Small delay between updates
    await new Promise(r => setTimeout(r, 100));
  }

  // Cache final state
  await tools.kv.set({
    key: `linear:issue:${issueId}:final`,
    value: issue.issue
  });

  return issue;
}
```

## Pattern 10: Tool Performance Profiling

```typescript
// Measure and log tool call performance
interface ToolCall {
  tool: string;
  function: string;
  durationMs: number;
  timestamp: number;
}

class ToolProfiler {
  private calls: ToolCall[] = [];

  async call<T = any>(
    tool: string,
    fn: string,
    call: () => Promise<T>
  ): Promise<T> {
    const start = Date.now();
    const result = await call();
    const duration = Date.now() - start;

    this.calls.push({
      tool,
      function: fn,
      durationMs: duration,
      timestamp: start,
    });

    return result;
  }

  report() {
    const byTool = new Map<string, {count: number; totalMs: number}>();

    for (const call of this.calls) {
      const key = `${call.tool}.${call.function}`;
      const existing = byTool.get(key) || {count: 0, totalMs: 0};
      byTool.set(key, {
        count: existing.count + 1,
        totalMs: existing.totalMs + call.durationMs,
      });
    }

    console.log("\nTool Performance Report:");
    console.log("------------------------");
    for (const [key, stats] of byTool) {
      const avg = Math.round(stats.totalMs / stats.count);
      console.log(`${key}: ${stats.count} calls, ${avg}ms avg`);
    }
  }
}

// Usage: Profile KV vs GitHub performance
const profiler = new ToolProfiler();

// Measure KV cache access
const cachedRepo = await profiler.call("kv", "get", () =>
  tools.kv.get({key: "github:repo:anthropics/claude-code"})
);

// Measure GitHub API access
const freshRepo = await profiler.call("github", "getRepo", () =>
  tools.github.getRepo({repo: "anthropics/claude-code"})
);

profiler.report();
// Output shows: kv.get: ~1-5ms, github.getRepo: ~200-500ms
```

---

## Choosing the Right Pattern

| Requirement | Pattern | Key Feature |
|---|---|---|
| Handle API failures gracefully | Pattern 1 | Retry with backoff |
| Process many repos/issues fast | Pattern 2 | Concurrency limit |
| Reduce GitHub API calls | Pattern 3 | Caching with TTL |
| Complex conditional flows | Pattern 4 | Conditional composition |
| Combine KV + GitHub + Linear | Pattern 5 | Result aggregation |
| Track success/failure split | Pattern 6 | Error aggregation |
| Handle GitHub API outages | Pattern 7 | Fallback selection |
| Process large KV datasets | Pattern 8 | Streaming/pagination |
| Manage Linear workflows | Pattern 9 | State machine |
| Debug performance (KV vs API) | Pattern 10 | Performance profiling |

---

## Performance Tips

### 1. Use Parallel Calls When Safe
```typescript
// Parallel - independent calls
const [kvData, repoData] = await Promise.all([
  tools.kv.get({key: "config"}),
  tools.github.getRepo({repo: "anthropics/claude-code"})
]);

// Sequential - dependent calls
const repo = await tools.github.getRepo({repo: "anthropics/claude-code"});
const cacheResult = await tools.kv.set({key: "cached:repo", value: repo.repo});
```

### 2. Implement Caching Strategically
```typescript
// Cache expensive GitHub API calls (slow, rate-limited)
const cacheKey = "github:repo:anthropics/claude-code";
const cached = await tools.kv.get({key: cacheKey});
if (cached.exists === false) {
  const fresh = await tools.github.getRepo({repo: "anthropics/claude-code"});
  await tools.kv.set({key: cacheKey, value: fresh.repo});
}

// Don't cache KV reads (already fast)
const config = await tools.kv.get({key: "config"});
```

### 3. Batch When Possible
```typescript
// Better: Use Promise.all for parallel fetches
const repos = ["anthropics/claude-code", "anthropics/anthropic-sdk-python"];
const results = await Promise.all(
  repos.map(repo => tools.github.getRepo({repo}).catch(e => ({error: e.message})))
);

// Worse: Sequential fetches (5x slower)
for (const repo of repos) {
  await tools.github.getRepo({repo});  // Slow!
}
```

### 4. Use Pagination for Large Datasets
```typescript
// Good: Paginate KV list
let offset = 0;
let hasMore = true;
while (hasMore) {
  const page = await tools.kv.list({limit: 50, offset});
  // process page
  offset += page.returnedCount;
  hasMore = offset < page.totalCount;
}

// Bad: Try to load all at once
const all = await tools.kv.list({limit: 999999, offset: 0});  // May timeout!
```

### 5. Profile Before Optimizing
```typescript
// Measure first
const profiler = new ToolProfiler();

await profiler.call("kv", "get", () => tools.kv.get({key: "test"}));
await profiler.call("github", "getRepo", () => tools.github.getRepo({repo: "..."}));

profiler.report();
// Example output:
// kv.get: 10 calls, 2ms avg
// github.getRepo: 3 calls, 350ms avg
// ^ Shows GitHub is bottleneck - cache it!
```

---

## Real-World Workflow Example

Combining multiple patterns for a production workflow:

```typescript
// Fetch GitHub repo data with caching, retries, and error handling
async function syncGitHubRepos(repoNames: string[]): Promise<any> {
  const profiler = new ToolProfiler();
  const cache = new ToolCache<any>();

  const results = await processBatchWithLimit(
    repoNames,
    async (repoName: string) => {
      // Pattern 3: Cache with TTL
      const repo = await cache.get(
        `github:${repoName}`,
        async () => {
          // Pattern 1: Retry with backoff
          return await callWithRetry(
            async () => {
              // Pattern 10: Profile performance
              return await profiler.call("github", "getRepo", () =>
                tools.github.getRepo({repo: repoName})
              );
            },
            3,
            100
          );
        },
        60000  // 1 minute TTL
      );

      // Store in SQLite for backup (Pattern 7: Fallback)
      await tools.sqlite.execute({
        sql: "INSERT OR REPLACE INTO repos (name, data, synced_at) VALUES (?, ?, ?)",
        params: [repoName, JSON.stringify(repo.repo), Date.now()]
      });

      return repo;
    },
    5  // Pattern 2: Concurrency limit
  );

  profiler.report();
  return results;
}
```

This workflow demonstrates:
- ✅ Caching to reduce API calls
- ✅ Retries for reliability
- ✅ Concurrency limits to respect rate limits
- ✅ SQLite backup for fallback
- ✅ Performance profiling to identify bottlenecks
