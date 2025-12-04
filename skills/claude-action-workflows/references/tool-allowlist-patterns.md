# Tool Allowlist Patterns

Security best practice: Always use least-privilege tool access.

## Basic Patterns

### File Operations

```yaml
# Read-only access
--allowedTools "Read,Glob,Grep,LS"

# Read and write
--allowedTools "Read,Write,Edit"

# Full file operations
--allowedTools "Read,Write,Edit,MultiEdit,Glob,Grep,LS"
```

---

### Git Operations

```yaml
# Basic git commands (safe)
--allowedTools "Bash(git status),Bash(git diff),Bash(git log)"

# Git with commits (use carefully)
--allowedTools "Bash(git:*)"

# Specific git commands only
--allowedTools "Bash(git add),Bash(git commit),Bash(git push)"
```

---

### Package Management

```yaml
# Node/npm
--allowedTools "Bash(npm install),Bash(npm test),Bash(npm run:*)"

# Bun
--allowedTools "Bash(bun install),Bash(bun test:*),Bash(bun run:*)"

# Python/uv
--allowedTools "Bash(uv add:*),Bash(uv run:*)"
```

---

### GitHub CLI

```yaml
# PR operations
--allowedTools "Bash(gh pr view:*),Bash(gh pr diff:*),Bash(gh pr comment:*)"

# Issue operations
--allowedTools "Bash(gh issue view:*),Bash(gh issue comment:*)"

# Label operations
--allowedTools "Bash(gh label list),Bash(gh label create:*)"
```

---

## MCP Server Tools

### GitHub Inline Comments

```yaml
# For PR code review with inline comments
--allowedTools "mcp__github_inline_comment__create_inline_comment"
```

---

### GitHub Operations

```yaml
# Issue triage
--allowedTools "mcp__github__get_issue,mcp__github__search_issues,mcp__github__update_issue,mcp__github__create_issue_comment"

# PR operations
--allowedTools "mcp__github__get_pr,mcp__github__list_pr_files"
```

---

### GitHub CI/Actions

```yaml
# CI log access
--allowedTools "mcp__github_ci__get_ci_status,mcp__github_ci__download_job_log"

# Workflow access
--allowedTools "mcp__github_actions__get_workflow_runs"
```

---

## Complete Examples by Use Case

### Code Review (Read-Only)

```yaml
claude_args: |
  --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*),Read,Glob,Grep"
```

---

### Implementation (Write Access)

```yaml
claude_args: |
  --allowedTools "Read,Write,Edit,MultiEdit,Bash(git:*),Bash(npm install),Bash(npm test)"
```

---

### CI Auto-Fix

```yaml
claude_args: |
  --allowedTools "mcp__github_ci__download_job_log,Read,Write,Edit,Bash(git:*),Bash(npm install),Bash(npm test)"
```

---

### Issue Triage

```yaml
claude_args: |
  --allowedTools "mcp__github__get_issue,mcp__github__search_issues,mcp__github__update_issue,mcp__github__create_issue_comment"
```

---

## Dangerous Patterns to Avoid

### ❌ Wildcard Bash Access

```yaml
# NEVER DO THIS - Allows any command
--allowedTools "Bash(*)"
```

---

### ❌ Destructive Commands

```yaml
# Avoid these unless absolutely necessary
--allowedTools "Bash(rm:*)"          # File deletion
--allowedTools "Bash(git push --force:*)"  # Force push
--allowedTools "Bash(npm publish:*)" # Package publishing
```

---

## Tool Naming Convention

| Pattern                       | Example                                            |
| ----------------------------- | -------------------------------------------------- |
| Built-in tools                | `Read`, `Write`, `Edit`, `Bash(...)`               |
| Bash with specific command    | `Bash(npm install)`                                |
| Bash with command prefix      | `Bash(git:*)`, `Bash(npm run:*)`                   |
| MCP tools                     | `mcp__server-name__tool-name`                      |
| Multiple tools (comma-separated) | `"Read,Write,Edit,Bash(git:*)"`                 |

---

## Testing Tool Permissions

To test if a tool is allowed, Claude will report errors like:

```
Error: Tool 'Bash' is not allowed
Error: Tool 'WebFetch' is not in allowedTools list
```

If you see these errors, add the specific tool to your `--allowedTools` list.
