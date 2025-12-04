# Linear ↔ GitHub Entity Mapping

This reference explains how Linear and GitHub entities map to each other for synchronization.

## The Central Entity: Linear Issues

**Linear Issues are the hub that connects everything.** All GitHub entities (branches, commits, PRs) link back to Linear issues.

## Entity Mappings

### Linear Projects ↔ GitHub Repositories

**Relationship:** One Linear project per GitHub repository

**Convention:** Use repository name (owner/repo format) as Linear project name
- Example: `dallascrilley/my-project`

**Setup:**
- Check if project exists before starting work
- Create project if missing using `setup_linear_project.sh`
- Project name should match GitHub repository path

### Linear Issues ↔ GitHub Branches

**Relationship:** One branch per Linear issue

**Convention:** Branch name includes Linear issue ID
- Format: `<type>/<issue-id>-<slug>`
- Example: `feature/dal-128-fix-health-status`

**Linking:**
- Branch name contains issue ID (e.g., `DAL-128`)
- Linear automatically detects and links branch
- Use `create_branch_from_issue.sh` to create properly named branches

### Linear Issues ↔ GitHub Commits

**Relationship:** Multiple commits can reference one Linear issue

**Convention:** Include Linear issue ID in commit message

**Examples:**
```
fix(api): propagate health status correctly (DAL-128)
feat(cli): add new command for project setup (DAL-129)
docs: update README with Linear integration (DAL-130)
```

**Commit Message Format:**
```
type(scope): brief description (ISSUE-ID)

Optional longer description
```

### Linear Issues ↔ GitHub Pull Requests

**Relationship:** One PR per Linear issue (typically)

**Convention:** Reference Linear issue in PR title or description

**Linking Methods:**
1. **Branch name** - If branch name contains issue ID, PR auto-links
2. **PR title** - Include issue ID: `[DAL-128] Fix health status bug`
3. **PR description** - Use magic words:
   - `Fixes DAL-128` - Auto-closes issue when PR merges
   - `Closes DAL-128` - Auto-closes issue when PR merges
   - `Related to DAL-128` - Links but doesn't auto-close

**Auto-close behavior:**
When PR with `Fixes DAL-XXX` or `Closes DAL-XXX` merges:
- Linear issue status automatically updates to "Done"
- No manual update needed

### Linear Reviews ↔ GitHub PR Reviews

**Relationship:** PR review state syncs to Linear

**Automatic synchronization:**
- GitHub PR review status appears in Linear issue
- Review notifications show up in Linear
- Reviewer list visible on linked Linear issues

## Workflow Summary

1. **Start:** Linear issue exists or is created
2. **Branch:** Create branch with issue ID in name → Auto-links to Linear
3. **Commit:** Include issue ID in commit messages → Shows in Linear
4. **PR:** Reference issue in PR description → Links PR to Linear
5. **Merge:** PR with "Fixes" merges → Auto-closes Linear issue

## Key Principle

**Always start from the Linear issue.** The issue is your source of truth that connects all GitHub activities.
