/**
 * Basic Lootbox Tool Usage Examples
 *
 * Copy and modify these examples to get started with tools
 * All examples use REAL installed tools (kv, sqlite, github, linear)
 */

// ===== Example 1: Simple Key-Value Store =====

// Get a value
const value = await tools.kv.get({key: "user:123"});
console.log(`Key exists: ${value.exists}`);
console.log(`Value: ${value.value}`);

// Set a value
const setResult = await tools.kv.set({
  key: "user:123",
  value: {name: "Alice", email: "alice@example.com"}
});
console.log(`Stored: ${setResult.success}`);

// ===== Example 2: Creating and Retrieving Data (KV) =====

// Create user data in KV
const userData = {name: "Bob", email: "bob@example.com"};
const createResult = await tools.kv.set({
  key: "user:bob",
  value: userData
});

if (createResult.success) {
  console.log(`User data stored at: ${createResult.key}`);

  // Retrieve the user
  const getResult = await tools.kv.get({key: "user:bob"});

  if (getResult.exists) {
    console.log(`User: ${getResult.value.name}`);
  }
}

// ===== Example 3: Pagination with KV List =====

// List items with pagination
const list1 = await tools.kv.list({limit: 10, offset: 0});
console.log(`First page: ${list1.entries.length} items`);

const list2 = await tools.kv.list({limit: 10, offset: 10});
console.log(`Second page: ${list2.entries.length} items`);

// ===== Example 4: Error Handling - Native Tools Use Status Fields =====

// KV tools return status, don't throw errors
const result = await tools.kv.get({key: "nonexistent"});
if (result.exists === false) {  // ✓ Shell-safe comparison
  console.log("User not found");
}

const deleteResult = await tools.kv.deleteKey({key: "test"});
if (deleteResult.success === false) {  // ✓ Shell-safe comparison
  console.log("Delete failed");
}

// ===== Example 5: Error Handling - External API Tools Throw Errors =====

// GitHub/Linear tools THROW errors on API failures
try {
  const repo = await tools.github.getRepo({repo: "anthropics/claude-code"});
  console.log(`Repo: ${repo.repo.name}, Stars: ${repo.repo.stars}`);
} catch (error) {
  console.log(`Error: ${error instanceof Error ? error.message : String(error)}`);
}

// ===== Example 6: Parallel Tool Calls =====

// Fetch multiple independent pieces of data in parallel
const [kvResult, infoResult] = await Promise.all([
  tools.kv.get({key: "config"}),
  tools.kv.info({})
]);

console.log(`Config exists: ${kvResult.exists}`);
console.log(`KV has ${infoResult.keyCount} keys`);

// ===== Example 7: Chaining Tool Calls with GitHub =====

// First fetch repo info
try {
  const repo = await tools.github.getRepo({repo: "anthropics/claude-code"});

  if (repo.repo) {
    // Now fetch issues for that repo
    const issues = await tools.github.listIssues({
      repo: "anthropics/claude-code",
      state: "open",
      limit: 5
    });
    console.log(`${repo.repo.name} has ${issues.issues.length} open issues (showing first 5)`);
  }
} catch (error) {
  console.log(`Error fetching GitHub data: ${error instanceof Error ? error.message : String(error)}`);
}

// ===== Example 8: Pagination - Correct Pattern =====

let allItems: any[] = [];
let offset = 0;
let hasMore = true;

while (hasMore) {
  const page = await tools.kv.list({
    limit: 50,
    offset
  });

  allItems.push(...page.entries);
  offset += page.returnedCount;  // ✓ Use returnedCount
  hasMore = offset < page.totalCount;  // ✓ Compare to totalCount, not page.hasMore
}

console.log(`Total items: ${allItems.length}`);

// ===== Example 9: Batch Processing with Proper Types =====

const keys = ["user:1", "user:2", "user:3", "user:4", "user:5"];

// ✓ Explicit type annotations prevent TypeScript errors
const results: {
  successful: Array<{key: string, value: any}>,
  failed: Array<{key: string, reason: string}>
} = {successful: [], failed: []};

for (const key of keys) {
  const result = await tools.kv.get({key});
  if (result.exists) {
    results.successful.push({key, value: result.value});
  } else {
    results.failed.push({key, reason: "not found"});
  }
}

console.log(`Success: ${results.successful.length}, Failed: ${results.failed.length}`);

// ===== Example 10: Batch Processing with API Tools (Error Handling) =====

const repoNames = ["anthropics/claude-code", "anthropics/anthropic-sdk-python"];

const repoResults: {
  successful: Array<{repo: string, stars: number}>,
  failed: Array<{repo: string, error: string}>
} = {successful: [], failed: []};

for (const repoName of repoNames) {
  try {
    const result = await tools.github.getRepo({repo: repoName});
    repoResults.successful.push({repo: repoName, stars: result.repo.stars});
  } catch (error) {
    repoResults.failed.push({
      repo: repoName,
      error: error instanceof Error ? error.message : String(error)
    });
  }
}

console.log(`Success: ${repoResults.successful.length}, Failed: ${repoResults.failed.length}`);

// ===== Example 11: Combining Native and External Tools (Caching) =====

// Use native KV cache, fall back to GitHub API
const cacheKey = "github:anthropics:repos";
const cached = await tools.kv.get({key: cacheKey});

let searchData;
if (cached.exists) {
  console.log("Using cached results (fast)");
  searchData = cached.value;
} else {
  console.log("Fetching fresh results from GitHub (slower)");
  try {
    const fresh = await tools.github.searchRepos({
      query: "anthropic",
      limit: 5
    });

    // Cache for next time
    await tools.kv.set({
      key: cacheKey,
      value: fresh.repos
    });

    searchData = fresh.repos;
  } catch (error) {
    console.error("GitHub search failed:", error instanceof Error ? error.message : String(error));
    searchData = [];
  }
}

console.log(`Found ${searchData.length} repos`);

// ===== Example 12: Conditional Logic with KV Get-or-Create =====

const userKey = "user:charlie";
const userResult = await tools.kv.get({key: userKey});

if (userResult.exists === false) {  // ✓ Shell-safe comparison
  console.log("User not found - creating...");
  const created = await tools.kv.set({
    key: userKey,
    value: {name: "Charlie", email: "charlie@example.com", status: "active"}
  });
  console.log(`Created at: ${created.key}`);
} else if (userResult.value.status === "inactive") {
  console.log("User is inactive - reactivating...");
  userResult.value.status = "active";
  await tools.kv.set({key: userKey, value: userResult.value});
} else {
  console.log(`User is active: ${userResult.value.name}`);
}

// ===== Example 13: Data Transformation with Linear =====

// Fetch and transform Linear issues
try {
  const issues = await tools.linear.listIssues({limit: 100});

  const highPriorityIssues = issues.issues
    .filter(issue => issue.priority === 1)
    .map(issue => ({
      id: issue.id,
      title: issue.title,
      state: issue.state
    }));

  console.log(`High priority issues: ${highPriorityIssues.length}`);
} catch (error) {
  console.error("Linear API error:", error instanceof Error ? error.message : String(error));
}

// ===== Example 14: Counting and Aggregation with SQLite =====

// ✓ Use execute() for CREATE/INSERT/UPDATE/DELETE (modifies data)
await tools.sqlite.execute({
  sql: `CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    name TEXT,
    status TEXT,
    processed BOOLEAN
  )`
});

let totalProcessed = 0;
let totalFailed = 0;

// Insert sample data
const items = [
  {id: 1, name: "Item 1", status: "pending", processed: false},
  {id: 2, name: "Item 2", status: "complete", processed: true},
  {id: 3, name: "Item 3", status: "pending", processed: false}
];

for (const item of items) {
  // ✓ Use execute() for INSERT/UPDATE/DELETE
  const insertResult = await tools.sqlite.execute({
    sql: "INSERT OR REPLACE INTO items (id, name, status, processed) VALUES (?, ?, ?, ?)",
    params: [item.id, item.name, item.status, item.processed ? 1 : 0]
  });

  if (insertResult.success) {
    totalProcessed++;
  } else {
    totalFailed++;
  }
}

// ✓ Use query() for SELECT (reads data, returns rows)
const countResult = await tools.sqlite.query({
  sql: "SELECT COUNT(*) as total, SUM(processed) as processed FROM items",
  params: []
});

console.log(`Total: ${countResult.rows[0].total}, Processed: ${countResult.rows[0].processed}`);

// ===== Example 15: Cleanup and Validation =====

// Ensure all required fields are present before calling tools
const newUserData = {
  name: "Diana",
  email: "diana@example.com"
};

// Validate before calling
if (newUserData.name === undefined || newUserData.name === "" ||
    newUserData.email === undefined || newUserData.email === "") {
  throw new Error("Name and email are required");
}

const finalResult = await tools.kv.set({
  key: `user:${newUserData.name.toLowerCase()}`,
  value: newUserData
});
console.log(`Created: ${finalResult.key}`);
