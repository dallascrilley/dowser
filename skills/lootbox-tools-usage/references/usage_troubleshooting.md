# Lootbox Tool Usage Troubleshooting

Solutions for common issues when calling lootbox tools using REAL tools (kv, sqlite, github, linear).

## Tool Not Available

**Symptom:** `Cannot read property 'xyz' of undefined` or `tools.xyz is undefined`

**Causes & Solutions:**

1. **Tool doesn't exist**
   - Check: `lootbox tools`
   - Verify namespace name is correct
   - Solution: Use a tool that exists

2. **Tool not loaded**
   - Check: `lootbox server` is running
   - Tool needs server to be initialized
   - Solution: Start `lootbox server`

3. **Typo in tool name**
   - Called: `tools.kvv.get()` (typo)
   - Actual: `tools.kv.get()`
   - Solution: Check spelling and case sensitivity

4. **Tool from different project**
   - Tool exists in another project but not this one
   - Solution: Copy tool file or run in correct project

---

## Function Not Found

**Symptom:** `tools.kv.wrongname is not a function`

**Causes & Solutions:**

1. **Wrong function name**
   ```typescript
   await tools.kv.get({...});    // ✓ Correct
   await tools.kv.fetch({...});  // ✗ Wrong - doesn't exist
   ```
   - Solution: Run `lootbox tools types kv` to see available functions

2. **Case sensitivity**
   ```typescript
   await tools.kv.get({...});    // ✓ Correct
   await tools.kv.Get({...});    // ✗ Wrong - case matters
   ```
   - Solution: Use exact case from tool definition

3. **Function doesn't exist in this tool**
   ```typescript
   await tools.github.listRepos({...});  // ✗ Wrong - doesn't exist
   await tools.github.searchRepos({...}); // ✓ Correct function name
   ```
   - Check: `lootbox tools types <namespace> | rg "RpcClient" -A 20`
   - Solution: Use the correct function name

---

## Missing Required Argument

**Symptom:**
```
Error: Missing required argument 'key'
or
Argument interface mismatch
```

**Causes & Solutions:**

1. **Didn't provide required field**
   ```typescript
   await tools.kv.get({});                    // ✗ Missing 'key'
   await tools.kv.get({key: "mykey"});        // ✓ Correct
   ```
   - Solution: Check tool types for required fields
   - Run: `lootbox tools types kv`

2. **Typo in argument name**
   ```typescript
   await tools.kv.get({k: "value"});          // ✗ Should be 'key'
   await tools.kv.get({key: "value"});        // ✓ Correct
   ```
   - Solution: Match exact argument names

3. **Using old API**
   - Tool was updated, argument names changed
   - Solution: Run `lootbox tools types <namespace>` to see current API

---

## Wrong Argument Type

**Symptom:**
```
Error: Argument type mismatch
or
Cannot assign string to number
```

**Causes & Solutions:**

1. **String instead of number**
   ```typescript
   await tools.kv.set({key: "count", value: "30"});  // ✓ Works - value is any
   await tools.sqlite.query({sql: "...", params: "test"});  // ✗ params should be array
   await tools.sqlite.query({sql: "...", params: ["test"]});  // ✓ Correct
   ```
   - Solution: Use correct type - check `lootbox tools types`

2. **Missing array brackets**
   ```typescript
   await tools.sqlite.query({sql: "SELECT * FROM users WHERE id = ?", params: "123"});  // ✗ Should be array
   await tools.sqlite.query({sql: "SELECT * FROM users WHERE id = ?", params: ["123"]});  // ✓ Correct
   ```
   - Solution: Check if argument should be array

3. **Object instead of primitive**
   ```typescript
   await tools.kv.get({key: {name: "test"}});           // ✗ Should be string
   await tools.kv.get({key: "test"});                   // ✓ Correct
   ```
   - Solution: Use simple value matching type

---

## Unknown Argument Name

**Symptom:**
```
Error: Unknown property 'badfield'
or
Unexpected property in arguments
```

**Causes & Solutions:**

1. **Argument doesn't exist**
   ```typescript
   await tools.kv.get({key: "x", cache: true});    // ✗ 'cache' doesn't exist
   await tools.kv.get({key: "x"});                 // ✓ Correct
   ```
   - Solution: Remove unknown fields
   - Check: `lootbox tools types kv`

2. **Typo in argument name**
   ```typescript
   await tools.github.getRepo({repository: "owner/name"});  // ✗ Should be 'repo'
   await tools.github.getRepo({repo: "owner/name"});        // ✓ Correct
   ```
   - Solution: Match exact argument names

3. **Using arguments for different function**
   ```typescript
   // Wrong arguments for this function
   await tools.kv.get({key: "test", value: "data"});  // ✗ get() doesn't take 'value'
   // Correct usage
   await tools.kv.get({key: "test"});  // ✓ Correct args for get()
   await tools.kv.set({key: "test", value: "data"});  // ✓ set() takes value
   ```
   - Solution: Verify you're using the right function

---

## Tool Throws Unexpected Error

**Symptom:**
```
Error: [message from tool]
```

**Causes & Solutions:**

1. **External API tool failed (GitHub/Linear)**
   - Wrap in try/catch (external tools throw errors)
   ```typescript
   try {
     const result = await tools.github.getRepo({repo: "owner/name"});
   } catch (error) {
     console.log(`GitHub API error: ${error instanceof Error ? error.message : String(error)}`);
     // Common errors: 404 Not Found, 401 Unauthorized, 403 Forbidden, 429 Rate Limit
   }
   ```

2. **Invalid operation on native tool**
   - Example: Query with bad SQL syntax
   - Solution: Check if parameters are valid
   ```typescript
   try {
     const result = await tools.sqlite.query({
       sql: "SELECT * FROM users WHERE id = ?",
       params: ["123"]  // ✓ Correct parameterized query
     });
   } catch (error) {
     console.error("SQLite error:", error.message);
   }
   ```

3. **Network error (GitHub/Linear)**
   - External API tools depend on network
   - Solution: Implement retry logic or use cached data
   ```typescript
   // Try cache first
   const cached = await tools.kv.get({key: "github:repo:owner/name"});
   if (cached.exists === false) {
     try {
       const fresh = await tools.github.getRepo({repo: "owner/name"});
       await tools.kv.set({key: "github:repo:owner/name", value: fresh.repo});
     } catch (error) {
       console.error("GitHub unavailable, no cached data");
     }
   }
   ```

---

## Cannot Read Result Field

**Symptom:**
```
Cannot read property 'userId' of undefined
or
result.userId is undefined
```

**Causes & Solutions:**

1. **Checking wrong field (native tools use status, not success)**
   ```typescript
   const result = await tools.kv.get({key: "user:123"});
   console.log(result.value);  // ✗ Might be null if doesn't exist

   // Check exists field first
   if (result.exists) {
     console.log(result.value);  // ✓ Safe now
   }
   ```

2. **Optional field not present**
   ```typescript
   const result = await tools.kv.get({key: "user:123"});
   if (result.exists) {
     console.log(result.value.phone);  // ✗ phone might not exist

     // Check optional fields with optional chaining
     console.log(result.value?.phone);  // ✓ Safe
   }
   ```

3. **Accessing field that doesn't exist**
   ```typescript
   const result = await tools.kv.get({key: "test"});
   console.log(result.nonexistent);  // ✗ Field doesn't exist

   // Check types first
   // lootbox tools types kv
   // Then only access valid fields
   ```

4. **Result has different structure than expected**
   ```typescript
   const result = await tools.kv.list({limit: 10, offset: 0});
   console.log(result.items);  // ✗ Result has 'entries', not 'items'

   // Use correct field names
   console.log(result.entries.length);  // ✓ Correct
   console.log(`Total: ${result.totalCount}`);  // ✓ Correct
   ```

---

## Timeout or Hanging

**Symptom:** Tool call never returns, hangs indefinitely

**Causes & Solutions:**

1. **GitHub API is slow or unavailable**
   - GitHub API calls can take 200-500ms or timeout
   - Solution: Add timeout, use cache, implement retry
   ```typescript
   const timeoutPromise = new Promise((_, reject) =>
     setTimeout(() => reject(new Error('Timeout')), 5000)
   );

   try {
     const result = await Promise.race([
       tools.github.getRepo({repo: "owner/name"}),
       timeoutPromise
     ]);
   } catch (error) {
     console.log("Request timed out, using cached data");
   }
   ```

2. **Large SQLite query**
   - Query scanning too many rows
   - Solution: Add LIMIT, create indexes, optimize query
   ```typescript
   // ✗ Slow: scan entire table
   const all = await tools.sqlite.query({sql: "SELECT * FROM logs", params: []});

   // ✓ Fast: limit results
   const recent = await tools.sqlite.query({
     sql: "SELECT * FROM logs ORDER BY created DESC LIMIT 100",
     params: []
   });
   ```

3. **Infinite pagination loop**
   - Pagination logic never completes
   ```typescript
   let offset = 0;
   let hasMore = true;
   let safety = 0;  // Safety counter

   while (hasMore && safety < 1000) {  // ✓ Add safety limit
     const page = await tools.kv.list({limit: 50, offset});
     offset += page.returnedCount;
     hasMore = offset < page.totalCount;
     safety++;
   }
   ```

---

## Tool Returns Unexpected Data

**Symptom:** Tool returns correct structure but wrong values

**Causes & Solutions:**

1. **Stale cached data**
   ```typescript
   // Clear cache if data seems stale
   await tools.kv.deleteKey({key: "github:repo:owner/name"});

   // Fetch fresh
   const fresh = await tools.github.getRepo({repo: "owner/name"});
   await tools.kv.set({key: "github:repo:owner/name", value: fresh.repo});
   ```

2. **Wrong parameters**
   ```typescript
   // Calling with wrong repo name
   const repo = await tools.github.getRepo({repo: "wrong/name"});

   // Verify parameters
   console.log(`Looking for: ${repoName}`);
   ```

3. **Data changed between calls**
   ```typescript
   // Data was modified between calls
   const first = await tools.kv.get({key: "counter"});
   // ... someone else updates counter ...
   const second = await tools.kv.get({key: "counter"});  // Different result

   // Use atomic operations or accept eventual consistency
   ```

---

## MCP Tool Not Working

**Symptom:** MCP tool call fails but native tools work

**Causes & Solutions:**

1. **MCP server not connected**
   - Check: `lootbox tools` shows `mcp_*` namespace
   - Run: `lootbox server` to initialize
   - Solution: Verify `.mcp.json` configuration

2. **Wrong MCP tool name**
   ```typescript
   await tools.mcp_perplexity.search({...});    // ✓ Correct
   await tools.perplexity.search({...});        // ✗ Missing mcp_ prefix
   ```
   - Solution: All MCP tools use `mcp_` prefix

3. **MCP server crashed**
   - MCP server may have exited
   - Solution: Check server logs, restart lootbox

4. **MCP API key missing**
   - MCP server needs credentials in `.mcp.json`
   - Solution: Add environment variables to config
   ```json
   {
     "mcpServers": {
       "perplexity": {
         "env": {"PERPLEXITY_API_KEY": "your-key"}
       }
     }
   }
   ```

5. **API key invalid/expired**
   - Credentials no longer work
   - Solution: Update API key in `.mcp.json`

---

## Performance Issues

**Symptom:** Tool calls are slow

**Causes & Solutions:**

1. **Too many individual GitHub API calls**
   ```typescript
   // ✗ Slow: many sequential GitHub API calls (200-500ms each)
   for (const repo of repos) {
     const result = await tools.github.getRepo({repo});
   }

   // ✓ Fast: parallel with concurrency limit
   const results = await Promise.all(
     repos.slice(0, 5).map(repo => tools.github.getRepo({repo}))
   );
   ```

2. **Not caching repeated GitHub calls**
   ```typescript
   // ✗ Slow: repeated identical GitHub calls
   const repo1 = await tools.github.getRepo({repo: "anthropics/claude-code"});
   const repo2 = await tools.github.getRepo({repo: "anthropics/claude-code"});  // Same call!

   // ✓ Fast: cache result in KV
   const cacheKey = "github:repo:anthropics/claude-code";
   const cached = await tools.kv.get({key: cacheKey});
   if (cached.exists === false) {
     const fresh = await tools.github.getRepo({repo: "anthropics/claude-code"});
     await tools.kv.set({key: cacheKey, value: fresh.repo});
   }
   ```

3. **Sequential when parallel possible**
   ```typescript
   // ✗ Slow: sequential (500ms + 5ms = 505ms total)
   const repo = await tools.github.getRepo({repo: "owner/name"});
   const config = await tools.kv.get({key: "settings"});

   // ✓ Fast: parallel (max(500ms, 5ms) = 500ms total)
   const [repo, config] = await Promise.all([
     tools.github.getRepo({repo: "owner/name"}),
     tools.kv.get({key: "settings"})
   ]);
   ```

4. **Large KV list without pagination**
   ```typescript
   // ✗ Slow: load all at once
   const all = await tools.kv.list({limit: 999999, offset: 0});

   // ✓ Fast: paginate
   let offset = 0;
   while (offset < total) {
     const page = await tools.kv.list({limit: 50, offset});
     // process page
     offset += page.returnedCount;
   }
   ```

---

## No Results

**Symptom:** Tool returns empty results when expecting data

**Causes & Solutions:**

1. **KV key doesn't exist**
   ```typescript
   const result = await tools.kv.get({key: "user:999"});
   if (result.exists === false) {
     console.log("Key not found");
   }
   ```

2. **GitHub repo/issue not found**
   ```typescript
   try {
     const repo = await tools.github.getRepo({repo: "owner/nonexistent"});
   } catch (error) {
     if (error.message.includes("404")) {
       console.log("Repository not found");
     }
   }
   ```

3. **SQLite query returns no rows**
   ```typescript
   const result = await tools.sqlite.query({
     sql: "SELECT * FROM users WHERE name = ?",
     params: ["NonexistentUser"]
   });
   if (result.rows.length === 0) {
     console.log("No users found with that name");
   }
   ```

4. **Linear team/issue not found**
   ```typescript
   try {
     const issue = await tools.linear.getIssue({issueId: "fake-id"});
   } catch (error) {
     console.log("Issue not found:", error.message);
   }
   ```

---

## Getting Help

1. **List available tools:**
   ```bash
   lootbox tools
   ```

2. **Check tool signature:**
   ```bash
   lootbox tools types <namespace>
   ```

3. **Discover available functions:**
   ```bash
   lootbox tools types github | rg "RpcClient" -A 20
   ```

4. **Test a call:**
   ```bash
   lootbox exec 'console.log(await tools.kv.get({key: "test"}))'
   ```

5. **Check tool file:**
   ```bash
   cat .lootbox/tools/<name>.ts
   ```

6. **Check MCP config:**
   ```bash
   cat .mcp.json | jq
   ```

---

## Debugging Checklist

Before asking for help:

- [ ] Run `lootbox tools` - tool exists?
- [ ] Run `lootbox tools types <namespace>` - function exists?
- [ ] Use `rg "RpcClient"` to discover correct function names
- [ ] Check argument names match exactly
- [ ] Check argument types are correct (number vs string, array vs single)
- [ ] For external tools (github, linear): wrap in try/catch
- [ ] For native tools (kv, sqlite): check status fields (exists, success)
- [ ] Try in `lootbox exec` to isolate issue
- [ ] Check if tool/server is running
- [ ] Look for typos in names (case sensitive)
- [ ] Check `.mcp.json` syntax if using MCP tools
- [ ] For GitHub/Linear: verify API keys in environment variables

---

## Common Error Patterns by Tool Type

### Native Tools (kv, sqlite, fs, memory)
- ✅ Return status in result object
- ✅ Check `result.exists` or `result.success`
- ✅ Don't throw errors for "not found" cases
- ✅ Fast (~1-10ms)

### External API Tools (github, linear)
- ⚠️ Throw errors on API failures
- ⚠️ **Must wrap in try/catch**
- ⚠️ Can timeout or be rate-limited
- ⚠️ Slower (~200-500ms)
- ⚠️ Common errors: 404, 401, 403, 429, network

**See main SKILL.md for detailed error handling patterns and examples.**
