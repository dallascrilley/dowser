# Troubleshooting Claude Code Action Workflows

## Authentication Issues

### Secret Not Set

**Symptom:** Authentication errors, "Missing Clerk Secret Key"

**Solution:**
```bash
# Verify secret exists
gh secret list | rg CLAUDE_CODE_OAUTH_TOKEN

# If missing, set it
gh secret set CLAUDE_CODE_OAUTH_TOKEN --body "sk-ant-oat01-..."
```

---

### Missing id-token Permission

**Symptom:** OIDC authentication errors

**Solution:**
```yaml
# ❌ WRONG
permissions:
  contents: read
  pull-requests: write

# ✅ CORRECT
permissions:
  contents: read
  pull-requests: write
  id-token: write  # Required for OAuth
```

---

### OAuth Token vs API Key

**OAuth Token (Recommended):**
- Pro/Max subscription users only
- Passed as environment variable
- Requires `id-token: write` permission
- Uses subscription quota

```yaml
env:
  CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

**API Key (Alternative):**
- All users
- Passed as action input
- No special permissions needed
- Separate API billing

```yaml
with:
  anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Tool Permission Errors

### "Bash tool is disabled"

**Solution:**
```yaml
# Explicitly enable specific commands
claude_args: |
  --allowedTools "Bash(npm install),Bash(npm test),Bash(git:*)"
```

---

### Tool Not Allowed

Check tool naming:
- Built-in: `Read`, `Write`, `Edit`, `Bash(...)`
- MCP: `mcp__server-name__tool-name`
- Patterns: `Bash(git:*)`, `Bash(npm run:*)`

---

## Triggering Issues

### Claude Doesn't Respond to @mentions

**Check:**
1. Trigger condition exists: `if: contains(github.event.comment.body, '@claude')`
2. User has write access to repository
3. Workflow includes all events:
   ```yaml
   on:
     issue_comment:
       types: [created]
     pull_request_review_comment:
       types: [created]
   ```

---

### @mentions from Bots Don't Work

**Cause:** `github-actions` bot can't trigger other workflows (prevents loops)

**Solution:** Use Personal Access Token (PAT)
```yaml
- name: Comment with PAT
  run: gh pr comment ${{ github.event.pull_request.number }} --body "@claude review"
  env:
    GH_TOKEN: ${{ secrets.PERSONAL_ACCESS_TOKEN }}
```

---

## CI Integration Issues

### "Cannot access workflow logs"

**Solution:** Add `actions: read` permission
```yaml
permissions:
  actions: read  # Required

# AND in action config:
- uses: anthropics/claude-code-action@v1
  with:
    additional_permissions: |
      actions: read
```

---

### Infinite CI Fix Loops

**Solution:** Add loop prevention
```yaml
if: |
  github.event.workflow_run.conclusion == 'failure' &&
  !startsWith(github.event.workflow_run.head_branch, 'claude-auto-fix-ci-')
```

---

## Performance Issues

### Action Times Out

**Solution:** Set `--max-turns` limit
```yaml
claude_args: |
  --max-turns 15  # Reasonable for most tasks
```

---

### Hitting Rate Limits

**Solutions:**
1. Use path filters to reduce runs
2. Use cheaper models (Haiku) for simple tasks
3. Set `--max-turns` limits
4. Add trigger conditions: `if: contains(...)`

---

## Common Error Messages

| Error                                  | Quick Fix                              |
| -------------------------------------- | -------------------------------------- |
| `Permission denied`                    | Add write access for user              |
| `OIDC token missing`                   | Add `id-token: write` permission       |
| `Tool not allowed`                     | Add to `--allowedTools` list           |
| `Cannot push to branch`                | Check if PR is closed                  |
| `API rate limit`                       | Use `--max-turns`                      |
| `Model not found`                      | Check model name format                |
| `github-actions bot can't trigger`     | Use PAT instead of GITHUB_TOKEN        |
| `Missing Clerk Secret Key`             | Set CLAUDE_CODE_OAUTH_TOKEN            |
| `Resource not accessible by integration` | Set `bot_id` and `bot_name`          |
