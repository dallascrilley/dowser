# LLM Tool Architecture Guide

> Design patterns for creating composable, LLM-accessible tools in lootbox

## Configuration Files

### Two Key Configuration Files

Before diving into architecture, understand the two key configuration files:

**`.mcp.json`** (Claude Code MCP client config)
- **Purpose**: Used by Claude Code to discover lootbox and other MCP servers
- **Location**: Your project root or `~/.claude/`
- **Usage**: Only needed if you want Claude to access lootbox tools
- **Important**: Do NOT put your tool definitions here

**`lootbox.config.json`** (Lootbox server config)
- **Purpose**: Configures lootbox itself and the MCP servers it manages
- **Location**: Your lootbox project root
- **Usage**: Where you define MCP server integrations and set environment variables for tools
- **Important**: This is the file you edit to add tools and MCP servers

⚠️ **Key Distinction**:
- **`.mcp.json`**: Defines how Claude Code connects to MCP servers, including the lootbox server itself
- **`lootbox.config.json`**: Defines which MCP servers lootbox itself manages and connects to internally

Do not confuse these roles. Both files are needed: `.mcp.json` for Claude Code's discovery, `lootbox.config.json` for lootbox's internal MCP management.

⚠️ **Environment Variables**:
- **`lootbox.config.json`**: Supports `${VAR}` interpolation (e.g., `"GITHUB_TOKEN": "${GITHUB_TOKEN}"`)
- **`.mcp.json`**: Also supports `${VAR}` interpolation for environment variables in the `env` section
- **Always set variables in shell first**: `export GITHUB_TOKEN="..."` before running `lootbox server` or Claude Code
- Both files require environment variables to be set in your shell before the respective servers start

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ Your Shell Environment                                  │
│ (export GITHUB_TOKEN="...", export LINEAR_API_KEY="...") │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  lootbox.config.json │
        │                      │
        │ - mcpServers         │
        │ - port: 3000         │
        │ - env: ${TOKEN}      │
        └──────────┬───────────┘
                   │
        lootbox server command
                   │
                   ▼
        ┌──────────────────────────────────┐
        │ Lootbox Server (port 3000)       │
        │                                  │
        │ - Native tools (.lootbox/tools/) │
        │ - MCP server connections         │
        └──────────┬───────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    Native Tools          MCP Servers
    (kv, fs, etc)     (mcp_perplexity, etc)
        │                     │
        └──────────┬──────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │ .mcp.json                        │
        │ (Claude Code's MCP client config)│
        │                                  │
        │ references lootbox as MCP server │
        └──────────┬───────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │ Claude Code / LLM Scripts        │
        │                                  │
        │ await tools.kv.get(...)         │
        │ await tools.mcp_perplexity...   │
        └──────────────────────────────────┘
```

**Key Points:**
1. Shell environment variables → `lootbox.config.json` → Lootbox Server
2. Lootbox Server discovers native tools and starts MCP servers
3. `.mcp.json` tells Claude Code where to find lootbox (as an MCP server)
4. LLM scripts access all tools through the unified tools interface

## Runtime Environments

⚠️ **Important**: This guide assumes Deno runtime. If your lootbox project uses Node.js, adjust the examples accordingly:

| Aspect | Deno | Node.js |
|--------|------|---------|
| File I/O | `Deno.readTextFile(path)` | `import fs from "fs"` |
| Env vars | `Deno.env.get("VAR")` | `process.env.VAR` |
| URL imports | `import { foo } from "https://deno.land/std/..."` | `npm install` + `import { foo } from "package"` |
| Async file ops | Built-in | Use `fs.promises` |

Check your project's startup command to determine runtime:
- Deno: `deno run ...`
- Node.js: `node ...` or `npx tsx ...`

## Overview

This document describes the architecture for building tools that LLM agents can effectively use. The key principles are:

1. **Consistency** - All tools follow the same patterns
2. **Composability** - Outputs of one function work as inputs to others
3. **Self-documenting** - Clear names and structured returns
4. **Parallel-safe** - Functions can be called concurrently

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│         COMPOUND FUNCTIONS (workflows.ts)       │
│   syncGitHubToLinear(), getPRContext(),        │
│   backupPRToS3()                                │
├─────────────────────────────────────────────────┤
│              BASE FUNCTIONS                      │
│   github.ts    linear.ts    s3.ts               │
│   - listIssues  - listIssues  - listObjects    │
│   - createIssue - createIssue - getObject      │
│   - getPR       - updateIssue - putObject      │
│   - getPRDiff   - search      - deleteObject   │
│   - searchCode                                  │
├─────────────────────────────────────────────────┤
│              SHARED PATTERNS                     │
│   Args/Result interfaces, error handling,       │
│   consistent ID formats, pagination             │
└─────────────────────────────────────────────────┘
```

## Design Principles

### 1. Consistent Return Patterns

Every function returns structured data that's easy to chain:

```typescript
// All results include typed, named fields
interface ListIssuesResult {
  issues: Issue[];      // The actual data
  total: number;        // Metadata for pagination
}

// Complex operations include success indicator
interface CreateIssueResult {
  issue: Issue;         // Created resource
}
```

### 2. Resource Identifiers as First-Class

Use consistent ID patterns so outputs flow into inputs:

| Service | ID Format | Example |
|---------|-----------|---------|
| GitHub Issue | `owner/repo#number` | `anthropics/claude#123` |
| GitHub PR | `owner/repo#number` | `anthropics/claude#456` |
| Linear Issue | `identifier` | `ENG-123` |
| S3 Object | `bucket/key` | `my-bucket/path/to/file.json` |

### 3. Single Args Object

All functions take a single `args` object with named parameters:

```typescript
// CORRECT - Single args object
export async function listIssues(args: ListIssuesArgs): Promise<ListIssuesResult>

// WRONG - Multiple positional parameters
export async function listIssues(repo: string, state: string, limit: number)
```

Benefits:
- No argument ordering confusion
- Easy to add optional parameters
- Self-documenting call sites
- IDE autocomplete works better

### 4. Predictable Interface Naming

```typescript
// Pattern: <FunctionName>Args and <FunctionName>Result
export interface ListIssuesArgs { ... }
export interface ListIssuesResult { ... }
export async function listIssues(args: ListIssuesArgs): Promise<ListIssuesResult>

export interface CreateIssueArgs { ... }
export interface CreateIssueResult { ... }
export async function createIssue(args: CreateIssueArgs): Promise<CreateIssueResult>
```

## Base Tool Specifications

### GitHub (`github.ts`)

Core operations for GitHub repositories, issues, and pull requests.

| Function | Purpose | Key Args |
|----------|---------|----------|
| `listIssues` | Query repository issues | `repo`, `state?`, `labels?`, `limit?` |
| `createIssue` | Create new issue | `repo`, `title`, `body?`, `labels?` |
| `getPR` | Get PR details | `repo`, `prNumber` |
| `getPRDiff` | Get PR diff and changed files | `repo`, `prNumber` |
| `searchCode` | Search code across GitHub | `query`, `repo?`, `language?` |

**Environment Variables:**
- `GITHUB_TOKEN` - GitHub personal access token

### Linear (`linear.ts`)

Core operations for Linear issue tracking.

| Function | Purpose | Key Args |
|----------|---------|----------|
| `listIssues` | Query team issues | `teamKey?`, `state?`, `limit?` |
| `createIssue` | Create new issue | `teamId`, `title`, `description?`, `priority?` |
| `updateIssue` | Update issue state/fields | `issueId`, `stateId?`, `priority?` |
| `searchIssues` | Search issues by term | `term`, `teamKey?`, `limit?` |
| `getIssue` | Get single issue by ID | `issueId` |

**Note:** The `issueSearch` GraphQL query is deprecated. Use `searchIssues` with `term` parameter instead.

**Environment Variables:**
- `LINEAR_API_KEY` - Linear API key

### S3 (`s3.ts`)

Core operations for AWS S3 object storage.

| Function | Purpose | Key Args |
|----------|---------|----------|
| `listObjects` | List bucket contents | `bucket`, `prefix?`, `limit?` |
| `getObject` | Read object content | `bucket`, `key` |
| `putObject` | Write object | `bucket`, `key`, `content`, `contentType?` |
| `deleteObject` | Delete object | `bucket`, `key` |

**Environment Variables:**
- `AWS_REGION` - AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

## Compound Functions (`workflows.ts`)

Compound functions compose base tools to create workflows LLMs naturally want.

### `syncGitHubToLinear`

Syncs GitHub issues to Linear, creating corresponding tickets.

```typescript
await tools.workflows.syncGitHubToLinear({
  githubRepo: "owner/repo",
  linearTeamId: "team-uuid",
  labels: ["needs-tracking"],    // Only sync issues with this label
  addGitHubLabel: "synced",      // Mark synced issues
});
```

### `backupPRToS3`

Archives PR metadata and diff to S3 for compliance/auditing.

```typescript
await tools.workflows.backupPRToS3({
  repo: "owner/repo",
  prNumber: 123,
  bucket: "pr-backups",
  keyPrefix: "2024/Q4",
});
```

### `getPRContext`

Gathers everything needed to review a PR - metadata, diff, linked issues.

```typescript
const context = await tools.workflows.getPRContext({
  repo: "owner/repo",
  prNumber: 123,
});

// Returns: pr details, full diff, linked issues, related code
```

## Usage Examples

### Basic Operations

```typescript
// List open issues with a specific label
const issues = await tools.github.listIssues({
  repo: "anthropics/claude",
  state: "open",
  labels: ["bug"],
});

// Create a Linear issue from GitHub
for (const issue of issues.issues) {
  await tools.linear.createIssue({
    teamId: "engineering-team-id",
    title: `[GH] ${issue.title}`,
    description: `From: ${issue.url}\n\n${issue.body}`,
  });
}
```

### Chaining Operations

```typescript
// Search for code, then create issues for TODO comments
const todos = await tools.github.searchCode({
  query: "TODO FIXME",
  repo: "owner/repo",
  language: "typescript",
});

for (const match of todos.matches) {
  await tools.github.createIssue({
    repo: match.repo,
    title: `Address TODO in ${match.path}`,
    body: `Found in: ${match.url}\n\n${match.textMatches.join("\n")}`,
    labels: ["tech-debt"],
  });
}
```

### Using Compound Functions

```typescript
// Get full context for reviewing a PR
const { context } = await tools.workflows.getPRContext({
  repo: "owner/repo",
  prNumber: 42,
});

console.log(`Reviewing: ${context.pr.title}`);
console.log(`Changes: +${context.pr.stats.additions} -${context.pr.stats.deletions}`);
console.log(`Files: ${context.diff.files.map(f => f.filename).join(", ")}`);
console.log(`Linked issues: ${context.linkedIssues.map(i => `#${i.number}`).join(", ")}`);
```

## Error Handling

All tools throw errors with descriptive messages:

```typescript
try {
  await tools.github.getPR({ repo: "owner/repo", prNumber: 99999 });
} catch (error) {
  // Error: PR #99999 not found in owner/repo
}
```

For operations that might partially succeed, use batch result patterns:

```typescript
interface BatchResult {
  successful: Array<{ id: string; result: unknown }>;
  failed: Array<{ id: string; error: string }>;
}
```

## Adding New Tools

To add a new tool, follow the existing patterns:

1. **Create the tool file** in `.lootbox/tools/<name>.ts`
2. **Define interfaces** for each function's args and result
3. **Export async functions** with typed signatures
4. **Use consistent ID patterns** that work with existing tools
5. **Document environment variables** needed

Example skeleton:

```typescript
// .lootbox/tools/myservice.ts

export interface ListItemsArgs {
  filter?: string;
  limit?: number;
}

export interface Item {
  id: string;
  name: string;
  // ...
}

export interface ListItemsResult {
  items: Item[];
  total: number;
}

export async function listItems(args: ListItemsArgs): Promise<ListItemsResult> {
  // Implementation
}
```

## File Structure

```
.lootbox/tools/
├── github.ts         # GitHub API operations
├── linear.ts         # Linear API operations
├── s3.ts             # AWS S3 operations
├── workflows.ts      # Compound functions
├── deepwiki.ts       # DeepWiki documentation (HTTP MCP wrapper)
├── kv.ts             # Key-value store (built-in)
├── sqlite.ts         # SQLite database (built-in)
├── fs.ts             # Filesystem operations (built-in)
├── memory.ts         # Knowledge graph (built-in)
├── graphql.ts        # GraphQL utilities (built-in)
├── contacts.ts       # Contacts management (optional)
└── scratchpad.ts     # Temporary storage (optional)
```

**Configuration file:**
```
lootbox.config.json   # MCP servers, port, lootboxRoot settings
```

## Best Practices Summary

| Do | Don't |
|----|-------|
| Use single args object | Use multiple positional parameters |
| Return structured objects | Return raw strings |
| Include metadata (total, pagination) | Return only the data |
| Use consistent ID formats | Mix different ID styles |
| Throw errors with context | Return generic error messages |
| Make functions parallel-safe | Rely on shared mutable state |
| Document environment variables | Hardcode credentials |
