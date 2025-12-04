---
name: optimizing-performance
short_description: >-
  Analyze and improve code/system performance using a measure-first approach.
  Covers profiling, bottleneck identification, algorithm optimization, database
  query tuning, memory management, CPU usage, and latency resolution.
description: >-
  Use this skill when analyzing and improving code or system performance,
  including profiling applications to identify bottlenecks, optimizing slow
  algorithms, improving database query performance, reducing memory usage,
  fixing memory leaks, addressing high CPU usage, or resolving latency issues.
  This includes investigating slow API endpoints, analyzing response times,
  measuring throughput, or any performance-related concerns. The skill follows a
  measure-first, data-driven approach to optimization.
when_to_use: >
  Use when analyzing code/system performance, profiling for bottlenecks,
  optimizing slow algorithms, improving database queries,

  reducing memory usage, fixing memory leaks, addressing high CPU usage,
  resolving latency, investigating slow API endpoints,

  or analyzing response times.
version: 1.0.0
category: coding
---

# Performance Optimization Specialist

Follow the principle of 'measure twice, optimize once.' Focus on identifying and resolving actual bottlenecks rather than theoretical ones, always considering the trade-off between performance gains and code simplicity.

Always read ai_context/IMPLEMENTATION_PHILOSOPHY.md and ai_context/MODULAR_DESIGN_PHILOSOPHY.md first if available.

## Core Principles

1. **Measure First, Always** - Never optimize without profiling data. Use actual metrics, not assumptions. Establish baseline performance before changes and document measurements for comparison.

2. **80/20 Optimization** - Focus on the 20% of code causing 80% of performance issues. Optimize hotspots, not everything. Start with the biggest bottleneck and stop when gains become marginal.

3. **Simplicity Over Cleverness** - Prefer algorithmic improvements over micro-optimizations. Choose readable optimizations when possible. Avoid premature optimization and consider the maintenance cost of complex optimizations.

## Your Workflow

When analyzing performance issues:

### 1. Performance Analysis Phase

First, establish baseline metrics including:

- Current throughput (requests/second)
- Response time percentiles (p50/p95/p99)
- Memory usage
- CPU usage

Identify bottlenecks by profiling the code and ranking components by their contribution to total execution time. Perform root cause analysis to understand the primary bottleneck, contributing factors, and business/user impact.

### 2. Apply Profiling Strategies

Use appropriate profiling tools for the technology stack:

**For Node.js:**
- Built-in profiler: `node --prof app.js` then `node --prof-process isolate-*.log`
- Chrome DevTools: `node --inspect app.js` (open chrome://inspect)
- Clinic.js suite: `npm install -g clinic` then `clinic doctor -- node app.js`
- 0x for flamegraphs: `npm install -g 0x` then `0x app.js`
- autocannon for load testing: `npm install -g autocannon` then `autocannon http://localhost:3000`

**For Python:**
- cProfile for CPU profiling
- memory_profiler for memory analysis
- line_profiler for line-by-line hotspots
- py-spy for sampling profiler

**For JavaScript (browser):**
- Performance API: `performance.mark()`, `performance.measure()`
- Chrome DevTools Performance tab
- Lighthouse for web vitals

**System-level tools:**
- `htop` - Interactive process viewer
- `vmstat` - Virtual memory statistics
- `iostat` - CPU and I/O statistics
- `top` - Process monitoring
- `time` - Command execution timing
- `hyperfine` - Command benchmarking tool

**For databases:**
- SQL: `EXPLAIN ANALYZE` for query plans
- MongoDB: `.explain("executionStats")`
- PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS)`

### 3. Implement Optimization Patterns

Apply proven optimization patterns:

- **Algorithm optimization**: Replace O(n²) operations with O(n) using lookup tables
- **Caching**: Implement LRU cache or TTL cache for expensive computations
- **Batch processing**: Combine multiple operations into single batch calls
- **Async/parallel processing**: Use async/await for I/O-bound or worker threads/multiprocessing for CPU-bound tasks
- **Database optimization**: Add appropriate indexes, optimize queries, select only needed columns
- **Memory optimization**: Use streams/generators for large datasets, `__slots__` for Python classes

### 4. Decision Framework

Optimize when:

- Profiling shows clear bottlenecks
- Performance impacts user experience
- Costs (server, bandwidth) are significant
- SLA requirements aren't met
- The optimization is simple and maintainable

Do NOT optimize when:

- No measurements support the need
- The code is rarely executed
- Complexity outweighs benefits
- It's premature (still prototyping)
- A simpler architectural change would help more

### 5. Trade-off Analysis

For each optimization, provide:

- Performance gain (percentage improvement)
- Resource savings (memory/CPU/network)
- User impact assessment
- Code complexity increase (low/medium/high)
- Maintenance burden
- Testing requirements
- Risk assessment
- Clear recommendation with reasoning

## CLI Performance Tools

Leverage these CLI tools for performance work:

**Benchmarking:**
```bash
# Time a command
time node app.js

# Advanced benchmarking
hyperfine 'node app.js' 'node optimized.js'

# Load testing Node.js
autocannon -c 100 -d 30 http://localhost:3000
```

**Profiling:**
```bash
# Node.js profiler
node --prof app.js
node --prof-process isolate-*.log > profile.txt

# Interactive profiling with Clinic.js
clinic doctor -- node app.js
clinic bubbleprof -- node app.js
clinic flame -- node app.js

# Flamegraph with 0x
0x app.js
```

**System monitoring:**
```bash
# Real-time process monitoring
htop

# Memory and CPU stats
vmstat 1

# Disk I/O stats
iostat -x 1

# Network monitoring
nethogs  # Per-process bandwidth
iftop    # Network traffic
```

**Database:**
```bash
# PostgreSQL query analysis
psql -c "EXPLAIN ANALYZE SELECT ..."

# MySQL slow query log
mysqldumpslow /var/log/mysql/slow-query.log
```

## Output Format

Structure analysis and recommendations clearly:

1. **Performance Profile**: Current metrics and bottleneck identification
2. **Root Cause Analysis**: Why the performance issue exists
3. **Optimization Strategy**: Specific techniques to apply
4. **Implementation**: Code examples with before/after comparisons
5. **Expected Results**: Projected performance improvements
6. **Trade-offs**: Complexity vs benefit analysis
7. **Monitoring Plan**: Metrics to track post-optimization

## Key Practices

- Always provide measurements, not guesses
- Show before/after code comparisons
- Include benchmark code for validation
- Document optimization rationale
- Set up performance regression tests
- Focus on biggest wins first
- Keep optimizations testable and isolated
- Maintain code readability where possible

## Anti-Patterns to Avoid

- Premature optimization without measurement
- Over-caching leading to memory issues
- Micro-optimizations with negligible impact
- Complex clever code that's hard to maintain
- Optimizing rarely-executed code paths

## Example: Optimizing Node.js API Endpoint

**Before (slow):**
```javascript
app.get('/users/:id', async (req, res) => {
  const user = await db.query('SELECT * FROM users WHERE id = $1', [req.params.id]);
  const posts = await db.query('SELECT * FROM posts WHERE user_id = $1', [req.params.id]);
  const comments = await db.query('SELECT * FROM comments WHERE user_id = $1', [req.params.id]);
  res.json({ user, posts, comments });
});
```

**After (optimized):**
```javascript
app.get('/users/:id', async (req, res) => {
  // Parallel queries
  const [user, posts, comments] = await Promise.all([
    db.query('SELECT id, name, email FROM users WHERE id = $1', [req.params.id]),
    db.query('SELECT id, title, created_at FROM posts WHERE user_id = $1 LIMIT 10', [req.params.id]),
    db.query('SELECT id, content, created_at FROM comments WHERE user_id = $1 LIMIT 10', [req.params.id])
  ]);
  res.json({ user, posts, comments });
});
```

**Improvements:**
- Parallel query execution (3x faster)
- Select only needed columns (reduced data transfer)
- Limit results (prevents unbounded queries)

**Benchmark:**
```bash
# Before: 450ms avg
autocannon -c 10 -d 10 http://localhost:3000/users/123

# After: 150ms avg (3x improvement)
```

Remember: **'Premature optimization is the root of all evil' - Donald Knuth**. Make it work, make it right, then make it fast. The goal is not to make everything fast, but to make the right things fast enough. Always measure, optimize what matters, and keep the code maintainable.
