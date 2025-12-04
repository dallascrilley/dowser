# Permissions Guide for Claude Code Action

## Required Permissions by Workflow Type

### Interactive Assistant (@claude mentions)

```yaml
permissions:
  contents: write      # Push commits
  pull-requests: write # Comment on PRs
  issues: write        # Comment on issues
  id-token: write      # OAuth authentication
```

---

### Automated PR Review (Read-Only)

```yaml
permissions:
  contents: read       # Read code
  pull-requests: write # Post reviews
  id-token: write      # OAuth authentication
```

---

### Code Changes (Write Access)

```yaml
permissions:
  contents: write      # Push commits
  pull-requests: write # Update PRs
  id-token: write      # OAuth authentication
```

---

### CI Log Access

```yaml
permissions:
  contents: write
  pull-requests: write
  actions: read        # Read workflow logs
  id-token: write

# ALSO required in action config:
- uses: anthropics/claude-code-action@v1
  with:
    additional_permissions: |
      actions: read
```

---

### Issue Triage

```yaml
permissions:
  issues: write        # Label, close issues
  contents: read       # Read code
  id-token: write      # OAuth authentication
```

---

## Permission Levels Explained

| Permission          | Level  | Capabilities                                          |
| ------------------- | ------ | ----------------------------------------------------- |
| `contents`          | read   | Read repository files                                 |
|                     | write  | Push commits, create branches                         |
| `pull-requests`     | read   | View PR details                                       |
|                     | write  | Comment, create PRs, add reviews                      |
| `issues`            | read   | View issues                                           |
|                     | write  | Comment, label, close issues                          |
| `actions`           | read   | Read workflow logs                                    |
|                     | write  | Manage workflows (not granted to Claude by GitHub)   |
| `id-token`          | write  | Required for OAuth OIDC authentication                |

---

## Common Mistakes

### Missing id-token Permission

```yaml
# ❌ WRONG - OAuth authentication will fail
permissions:
  contents: read
  pull-requests: write

# ✅ CORRECT
permissions:
  contents: read
  pull-requests: write
  id-token: write  # Required!
```

---

### Insufficient Permissions for CI Logs

```yaml
# ❌ WRONG - Can't access workflow logs
permissions:
  contents: write
  pull-requests: write
  id-token: write

# ✅ CORRECT
permissions:
  contents: write
  pull-requests: write
  actions: read    # Add this
  id-token: write

# AND in action:
- uses: anthropics/claude-code-action@v1
  with:
    additional_permissions: |
      actions: read
```

---

## Security Best Practices

1. **Least Privilege**: Only grant permissions needed for the specific workflow
2. **Read-Only When Possible**: Use `contents: read` for review-only workflows
3. **No Workflow Write**: GitHub intentionally prevents workflow file modifications
4. **Token Scope**: Permissions only apply to the specific job, not entire workflow
