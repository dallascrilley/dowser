---
name: linear-github-sync
description: Keep Linear and GitHub synchronized when contributing to projects. Use when working on repositories that track issues in Linear - includes project setup, issue management, branch naming, commit messages, and PR linking. Trigger phrases include "work on Linear issue", "start Linear task", "create branch for issue", "sync with Linear", or when Linear issue IDs (e.g., DAL-123) are mentioned.
when_to_use: when working on repositories that track issues in Linear - includes project setup, issue management, branch naming, commit messages, and PR linking. When user wants to work on a Linear issue, create a branch for it, commit with issue reference, and create a PR with issue reference. When user wants to sync with Linear, update the issue status, add a comment, or close the issue.
version: 1.0.0
languages: all
dependencies: linctl (npm install -g linctl), Linear API key
---

# Linear-GitHub Sync

Keep Linear issues synchronized with GitHub activity through proper branch naming, commit messages, and PR references.

## Core Concept

**Linear issues are the hub.** Every GitHub activity (branch, commit, PR) links back to a Linear issue. The synchronization happens automatically when you follow naming conventions.

## Quick Start Workflow

### Before Any Work

**1. Ensure Linear project exists:**

```bash
# Check and create project if needed
./scripts/setup_linear_project.sh
```

This script:
- Detects repository name from git remote
- Searches for existing Linear project
- Creates project if missing
- Updates README.md, CLAUDE.md, AGENTS.md with project reference

**2. Find or create your Linear issue:**

```bash
# Search for existing issue
linctl issue list --assignee me --json

# Search by title keyword
linctl issue list --json | jq '.[] | select(.title | contains("keyword"))'

# Create new issue if needed
linctl issue create \
  --title "Fix authentication bug" \
  --team TEAM \
  --assign-me \
  --json
```

### Starting Work on an Issue

**3. Create branch from issue:**

```bash
# Automatic branch creation with proper naming
./scripts/create_branch_from_issue.sh DAL-123 feature
```

This script:
- Fetches issue details from Linear
- Creates branch named `feature/dal-123-descriptive-slug`
- Updates issue status to "In Progress"
- Checks out the new branch

**Branch naming format:** `<type>/<issue-id>-<slug>`
- Types: `feature`, `fix`, `hotfix`, `chore`, `docs`, `refactor`
- Example: `feature/dal-123-add-authentication`

### During Development

**4. Commit with issue reference:**

```bash
# Include issue ID in commit message
git commit -m "fix(auth): correct token validation (DAL-123)"
```

**Commit message format:**
```
type(scope): description (ISSUE-ID)

Optional longer explanation
```

**5. Push and create PR:**

```bash
git push origin feature/dal-123-add-authentication

# Create PR with issue reference in description
gh pr create --title "[DAL-123] Add authentication" \
  --body "Fixes DAL-123

Implements JWT-based authentication with token validation."
```

**PR description must include:**
- `Fixes DAL-123` or `Closes DAL-123` - Auto-closes issue when merged
- `Related to DAL-123` - Links but doesn't auto-close

### After Merge

**6. Verify issue closure:**

If PR contained `Fixes DAL-XXX`, the issue should auto-close. If not:

```bash
linctl issue update DAL-123 --state "Done" --json
```

## Common Scenarios

### Starting Work Without Existing Issue

```bash
# 1. Create issue
RESULT=$(linctl issue create \
  --title "Add user profile page" \
  --team TEAM \
  --assign-me \
  --json)

# 2. Extract issue ID
ISSUE_ID=$(echo "$RESULT" | jq -r '.identifier')

# 3. Create branch
./scripts/create_branch_from_issue.sh "$ISSUE_ID" feature
```

### Blocking Issues

If work is blocked by another issue:

```bash
linctl comment create DAL-123 \
  --body "Blocked by DAL-456. Waiting for API changes." \
  --json
```

### Checking Issue Status

```bash
# Get full issue details
linctl issue get DAL-123 --json

# Check just the status
linctl issue get DAL-123 --json | jq '.state.name'

# See linked branches
linctl issue get DAL-123 --json | jq '.branchName'
```

### Manual Status Updates

```bash
# Update to In Progress
linctl issue update DAL-123 --state "In Progress" --json

# Update to In Review
linctl issue update DAL-123 --state "In Review" --json

# Mark as Done
linctl issue update DAL-123 --state "Done" --json
```

## Entity Relationships

For detailed explanation of how Linear and GitHub entities map to each other, see [references/entity_mapping.md](references/entity_mapping.md).

**Summary:**
- Linear Projects ↔ GitHub Repositories (1:1)
- Linear Issues ↔ GitHub Branches (1:1, via branch name)
- Linear Issues ↔ GitHub Commits (1:many, via commit message)
- Linear Issues ↔ GitHub PRs (1:1, via PR description)

## CLI Reference

For complete `linctl` command reference, see [references/cli_reference.md](references/cli_reference.md).

**Most used commands:**

```bash
# Authentication
linctl whoami

# List my issues
linctl issue list --assignee me --json

# Get issue details
linctl issue get DAL-123 --json

# Update issue status
linctl issue update DAL-123 --state "In Progress" --json

# Add comment
linctl comment create DAL-123 --body "Progress update" --json
```

## Automation

The synchronization is mostly automatic:
- ✅ Branch names with issue IDs auto-link to Linear
- ✅ Commit messages with issue IDs show in Linear
- ✅ PRs with "Fixes/Closes" auto-close issues when merged
- ⚠️ Manual updates needed: status changes during work, blocking comments

## Troubleshooting

### "Project not found"

Run `./scripts/setup_linear_project.sh` to create the Linear project.

### "Issue not found"

```bash
# Check if issue exists
linctl issue get DAL-123 --json

# Search for it
linctl issue list --newer-than all_time --json | jq '.[] | select(.identifier == "DAL-123")'
```

### Issue didn't auto-close after PR merge

Ensure PR description contained `Fixes DAL-XXX` or `Closes DAL-XXX`. If missed, manually close:

```bash
linctl issue update DAL-123 --state "Done" --json
```

### linctl not authenticated

```bash
linctl auth
```

## Integration with Conventional Commits

This workflow integrates with Conventional Commits for consistent git history:

```
type(scope): description (ISSUE-ID)
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples:**
```
feat(auth): add JWT token validation (DAL-123)
fix(api): handle null responses correctly (DAL-124)
docs: update authentication guide (DAL-125)
refactor(db): optimize query performance (DAL-126)
```

## Required Tools

- `linctl` - Linear CLI ([install](https://github.com/dorkitude/linctl))
- `git` - Version control
- `gh` (optional) - GitHub CLI for PR creation
- `jq` - JSON parsing for scripts

Verify installation:
```bash
linctl whoami
git --version
jq --version
```
