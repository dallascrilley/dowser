---
name: claude-action-workflows
short_description: >-
  Create and edit GitHub Actions workflows for Claude Code Action. Validates
  CLAUDE_CODE_OAUTH_TOKEN secret, generates workflows for PR reviews, issue
  triage, CI auto-fix, and interactive @claude assistants.
description: >-
  Create and edit GitHub Actions workflows for Claude Code Action. Validates
  CLAUDE_CODE_OAUTH_TOKEN secret, generates workflows for PR reviews, issue
  triage, CI auto-fix, and interactive @claude assistants. Use when creating
  .github/workflows/*.yml files, configuring claude_args, setting up MCP
  servers, validating secrets, or troubleshooting Claude Code Action workflows.
when_to_use: >-
  Use this skill when setting up or modifying GitHub Actions workflows related
  to Claude Code Action, especially when you need to validate secrets, generate
  workflows for specific tasks like PR reviews or issue triage, or troubleshoot
  existing workflows.
version: 1.0.0
languages: all
category: agents-and-skills
---

# Claude Code Action Workflows

Guide for creating and editing GitHub Actions workflows that integrate Claude Code Action. Ensures proper authentication, permissions, and configuration.

## Prerequisites Check

**CRITICAL: Before creating any workflow, verify authentication is configured.**

### Check for CLAUDE_CODE_OAUTH_TOKEN

```bash
# Check if secret exists in GitHub repo
gh secret list | rg CLAUDE_CODE_OAUTH_TOKEN
```

**If missing, set it:**

```bash
# Get token value from COMMON_ENV.md
OAUTH_TOKEN="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"

# Set in current repository
gh secret set CLAUDE_CODE_OAUTH_TOKEN --body "$OAUTH_TOKEN"

# Verify it was set
gh secret list | rg CLAUDE_CODE_OAUTH_TOKEN
```

**Alternative: API Key (if no Claude Pro/Max subscription)**

```bash
# If using API key instead of OAuth token
API_KEY="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"
gh secret set ANTHROPIC_API_KEY --body "$API_KEY"
```

**Why OAuth Token is preferred:**
- Uses existing Claude Pro/Max subscription ($20-200/mo)
- More secure (short-lived tokens)
- Higher usage limits
- No separate API billing

---

## Workflow Patterns

### Pattern 1: Interactive Assistant (@claude mentions)

Creates a workflow that responds when users mention `@claude` in comments.

**File:** `.github/workflows/claude-assistant.yml`

```yaml
name: Claude Assistant
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  claude:
    # Only trigger on @claude mentions (cost control)
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      issues: write
      id-token: write  # Required for OAuth OIDC
    env:
      # Uses Claude Pro/Max subscription
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    steps:
      - uses: actions/checkout@v5
      - uses: anthropics/claude-code-action@v1
        with:
          claude_args: |
            --max-turns 10
            --system-prompt "Follow TypeScript coding standards"
```

**Key Points:**
- `if: contains()` prevents unnecessary runs
- `id-token: write` required for OAuth
- `CLAUDE_CODE_OAUTH_TOKEN` as environment variable (NOT action input)
- No `prompt` input = interactive mode

---

### Pattern 2: Automated PR Review

Automatically reviews every new PR.

**File:** `.github/workflows/claude-auto-review.yml`

```yaml
name: Claude Auto Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    env:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          track_progress: true  # Show progress checkboxes
          prompt: |
            REPO: ${{ github.repository }}
            PR: #${{ github.event.pull_request.number }}

            Perform code review focusing on:
            1. Code quality and best practices
            2. Security vulnerabilities
            3. Performance issues
            4. Test coverage

            Post general feedback as top-level comment.
            Use inline comments for specific lines.
          claude_args: |
            --allowedTools "mcp__github_inline_comment__create_inline_comment,Bash(gh pr comment:*),Bash(gh pr diff:*)"
            --max-turns 15
```

**Key Points:**
- `prompt` input triggers automation mode
- `track_progress: true` shows checkboxes
- Specific tool permissions for security
- Context variables (${{ github.* }})

---

### Pattern 3: Path-Specific Security Review

Only reviews when critical files change.

**File:** `.github/workflows/security-review.yml`

```yaml
name: Security Review
on:
  pull_request:
    paths:
      - "src/auth/**"
      - "src/security/**"
      - "**/*.security.ts"

jobs:
  security-review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      id-token: write
    env:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    steps:
      - uses: actions/checkout@v5
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Security-focused review of PR #${{ github.event.pull_request.number }}

            Check for:
            - Input validation and sanitization
            - Authentication/authorization issues
            - SQL injection, XSS, CSRF vulnerabilities
            - Secure credential handling
            - OWASP Top 10 compliance
          claude_args: |
            --model claude-opus-4-1-20250805
            --max-turns 20
```

**Key Points:**
- `paths` filter reduces unnecessary runs
- Opus model for complex security analysis
- Higher turn limit for thorough review

---

### Pattern 4: CI Auto-Fix

Automatically fixes CI failures.

**File:** `.github/workflows/ci-auto-fix.yml`

```yaml
name: Auto Fix CI Failures
on:
  workflow_run:
    workflows: ["CI"]  # Name of your main CI workflow
    types: [completed]

jobs:
  auto-fix:
    if: |
      github.event.workflow_run.conclusion == 'failure' &&
      !startsWith(github.event.workflow_run.head_branch, 'claude-auto-fix-ci-')
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
      actions: read  # Essential for reading logs
      id-token: write
    env:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    steps:
      - name: Checkout failing branch
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.workflow_run.head_branch }}

      - name: Fix CI failures
        uses: anthropics/claude-code-action@v1
        with:
          additional_permissions: |
            actions: read
          prompt: |
            CI workflow failed on branch `${{ github.event.workflow_run.head_branch }}`.

            MISSION:
            1. Use mcp__github_ci__download_job_log to get logs from run ${{ github.event.workflow_run.id }}
            2. Analyze the failure
            3. Fix relevant files
            4. Commit changes with message "fix(ci): Attempt to fix CI failure"
          claude_args: |
            --allowedTools "mcp__github_ci__download_job_log,Read,Write,Edit,Bash(git:*),Bash(npm install),Bash(npm test)"
            --max-turns 25
```

**Key Points:**
- Loop prevention: `!startsWith(... 'claude-auto-fix-ci-')`
- `actions: read` permission for CI logs
- `additional_permissions` in action config
- Specific tool allowlist for safety

---

### Pattern 5: Issue Triage

Analyzes new issues, applies labels, closes duplicates.

**File:** `.github/workflows/issue-triage.yml`

```yaml
name: Issue Triage
on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      contents: read
      id-token: write
    env:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: |
            Analyze issue #${{ github.event.issue.number }} in ${{ github.repository }}.

            TASKS:
            1. Search for existing issues to identify duplicates
            2. If duplicate: comment with link, add "duplicate" label, close it
            3. If not duplicate: analyze and apply appropriate labels
               (bug, feature-request, needs-triage)

            Do not comment unless it's a duplicate.
          claude_args: |
            --allowedTools "mcp__github__get_issue,mcp__github__search_issues,mcp__github__create_issue_comment,mcp__github__update_issue"
            --max-turns 10
```

---

## Configuration Reference

### Essential Permissions

| Workflow Type       | Required Permissions                                          |
| ------------------- | ------------------------------------------------------------- |
| **Interactive**     | `contents: write`, `pull-requests: write`, `issues: write`, `id-token: write` |
| **PR Review**       | `contents: read`, `pull-requests: write`, `id-token: write`   |
| **Code Changes**    | `contents: write`, `pull-requests: write`, `id-token: write`  |
| **CI Log Access**   | Add `actions: read` + `additional_permissions: actions: read` |
| **Issue Triage**    | `issues: write`, `contents: read`, `id-token: write`          |

**Always include `id-token: write` for OAuth authentication.**

---

### Tool Permissions Guide

**Security Best Practice:** Always use least-privilege. Grant specific commands only.

```yaml
# ❌ DANGEROUS - Allows any command
--allowedTools "Bash(*)"

# ✅ SECURE - Specific commands only
--allowedTools "Bash(npm install),Bash(npm test),Bash(git status)"
```

**Common Tool Patterns:**

| Task              | Recommended Tools                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| **Code Review**   | `mcp__github_inline_comment__create_inline_comment`, `Bash(gh pr comment:*)`, `Bash(gh pr diff:*)` |
| **Writing Code**  | `Read`, `Write`, `Edit`, `MultiEdit`, `Bash(git:*)`                                                |
| **Running Tests** | `Bash(npm install)`, `Bash(npm test)`, `Bash(bun test)`                                            |
| **Issue Triage**  | `mcp__github__get_issue`, `mcp__github__update_issue`, `mcp__github__search_issues`                |
| **Reading Files** | `Read`, `Glob`, `Grep`, `LS`                                                                       |
| **Debugging CI**  | `mcp__github_ci__get_ci_status`, `mcp__github_ci__download_job_log`                                |

---

### Model Selection

| Task Complexity                    | Model                        | Cost | Speed  |
| ---------------------------------- | ---------------------------- | ---- | ------ |
| Simple triage, labeling            | `claude-3-haiku-20240307`    | $    | ⚡⚡⚡ |
| Standard PR reviews                | `claude-sonnet-4-5-20250929` | $$   | ⚡⚡   |
| Security audits, complex refactors | `claude-opus-4-1-20250805`   | $$$  | ⚡     |

**Specify model:**
```yaml
claude_args: |
  --model claude-opus-4-1-20250805
```

---

### Turn Limits

```yaml
# Quick tasks (triage, labels)
--max-turns 5

# Standard reviews
--max-turns 10-15

# Complex refactors
--max-turns 20-30

# Defensive maximum
--max-turns 50
```

---

## Troubleshooting

**See:** `references/troubleshooting.md` for complete troubleshooting guide including:
- Authentication issues (missing secrets, OIDC errors)
- Tool permission errors
- Triggering issues (@mention not working)
- CI integration problems
- Performance and rate limiting

**Quick fixes:**
- Secret not set: `gh secret set CLAUDE_CODE_OAUTH_TOKEN --body "..."`
- Missing permission: Add `id-token: write` to permissions
- Tool not allowed: Add to `--allowedTools` list
- Claude doesn't respond: Check trigger condition and user access

---

## Quick Checklist

When creating workflows, verify:

- [ ] CLAUDE_CODE_OAUTH_TOKEN secret is set (`gh secret list`)
- [ ] `id-token: write` permission included
- [ ] OAuth token passed as **environment variable** (not action input)
- [ ] Tool permissions follow least-privilege
- [ ] `--max-turns` set to prevent runaway costs
- [ ] Trigger conditions prevent unnecessary runs
- [ ] Proper checkout step included when using `prompt` input

---

## Common Patterns

### API Key Instead of OAuth Token

```yaml
# If using API key instead of OAuth token
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}  # Action input, not env var
    prompt: "Review this PR"
    # No need for id-token: write permission
```

---

### Custom Trigger Phrase

```yaml
name: Claude Assistant
on:
  issue_comment:
    types: [created]

jobs:
  claude:
    if: startsWith(github.event.comment.body, '/claude')  # Use /claude instead
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          trigger_phrase: "/claude"
```

---

### Multi-Stage Automation

```yaml
# Stage 1: Quick Haiku review
- name: Quick Review
  uses: anthropics/claude-code-action@v1
  with:
    prompt: "Quick triage: any obvious issues?"
    claude_args: |
      --model claude-3-haiku-20240307
      --max-turns 5

# Stage 2: Deep Opus review if security-critical
- name: Deep Security Review
  if: contains(github.event.pull_request.labels.*.name, 'security')
  uses: anthropics/claude-code-action@v1
  with:
    prompt: "Deep security analysis with OWASP checklist"
    claude_args: |
      --model claude-opus-4-1-20250805
      --max-turns 20
```

---

## References

**Technical Details:** `docs/reference/TECHNICAL-REFERENCE.md`
**Comprehensive Guide:** `ULTIMATE-CLAUDE-CODE-ACTION-CHEAT-SHEET.md`
**Action Reference:** `docs/reference/claude-code-reference.md`
**Test Scenarios:** `TEST_SCENARIOS.md` - Token efficiency metrics and known issues

**Authentication Secrets:** `~/.config/ai-rules/COMMON_ENV.md`
