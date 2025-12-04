# Linear CLI Quick Reference

Essential `linctl` commands for agent workflows. Always use `--json` flag for scripting.

## Authentication

```bash
# Check authentication status
linctl whoami

# Authenticate (if needed)
linctl auth
```

## Projects

```bash
# List all projects
linctl project list --json

# Search for project by name
linctl project list --json | jq '.[] | select(.name | contains("repo-name"))'

# Get project details
linctl project get <project-id> --json

# Create project (prefer using setup_linear_project.sh)
linctl project create --name "owner/repo" --team TEAM --description "Description" --json
```

## Issues

### Searching Issues

```bash
# Search by assignee
linctl issue list --assignee me --json

# Search by state
linctl issue list --state "In Progress" --json

# Search by team
linctl issue list --team TEAM --json

# Include completed issues (excluded by default)
linctl issue list --include-completed --json

# Search recent issues (default is 6 months)
linctl issue list --newer-than 1_week_ago --json
linctl issue list --newer-than all_time --json
```

### Getting Issue Details

```bash
# Get full issue details (includes branches, cycle, project, attachments, comments)
linctl issue get DAL-123 --json

# Extract specific fields
linctl issue get DAL-123 --json | jq '.title'
linctl issue get DAL-123 --json | jq '.state.name'
linctl issue get DAL-123 --json | jq '.assignee.email'
```

### Creating Issues

```bash
# Create issue
linctl issue create \
  --title "Issue title" \
  --team TEAM \
  --description "Description" \
  --assign-me \
  --json

# Create issue with priority
linctl issue create \
  --title "Urgent bug" \
  --team TEAM \
  --priority 1 \
  --json
```

### Updating Issues

```bash
# Update status
linctl issue update DAL-123 --state "In Progress" --json

# Update assignee
linctl issue update DAL-123 --assignee me --json
linctl issue update DAL-123 --assignee john@example.com --json
linctl issue update DAL-123 --assignee unassigned --json

# Update priority (0=None, 1=Urgent, 2=High, 3=Normal, 4=Low)
linctl issue update DAL-123 --priority 1 --json

# Update multiple fields
linctl issue update DAL-123 \
  --title "New title" \
  --state "In Progress" \
  --assignee me \
  --json
```

## Comments

```bash
# List comments on issue
linctl comment list DAL-123 --json

# Add comment
linctl comment create DAL-123 --body "Progress update" --json

# Add blocker comment
linctl comment create DAL-123 --body "Blocked by DAL-456" --json
```

## Teams

```bash
# List teams
linctl team list --json

# Get team details
linctl team get TEAM --json

# List team members
linctl team members TEAM --json
```

## Common Patterns

### Check if issue exists

```bash
ISSUE_ID="DAL-123"
if linctl issue get "$ISSUE_ID" --json &>/dev/null; then
  echo "Issue exists"
fi
```

### Find issues assigned to me

```bash
MY_ISSUES=$(linctl issue list --assignee me --json)
echo "$MY_ISSUES" | jq -r '.[] | "\(.identifier): \(.title)"'
```

### Create issue and get ID

```bash
RESULT=$(linctl issue create \
  --title "New feature" \
  --team TEAM \
  --assign-me \
  --json)

ISSUE_ID=$(echo "$RESULT" | jq -r '.identifier')
echo "Created issue: $ISSUE_ID"
```

### Update issue status and add comment

```bash
linctl issue update DAL-123 --state "In Progress" --json
linctl comment create DAL-123 --body "Starting work on this issue" --json
```

## Priority Levels

- `0` = None
- `1` = Urgent (red)
- `2` = High (orange)
- `3` = Normal (yellow, default)
- `4` = Low (gray)

## Common States

Standard workflow states:
- `Todo` / `Backlog`
- `In Progress`
- `In Review`
- `Done`
- `Canceled`

(Actual state names depend on team configuration)

## Time Filters

Use `--newer-than` to filter by creation date:
- `1_day_ago` - Last 24 hours
- `1_week_ago` - Last 7 days
- `2_weeks_ago` - Last 14 days
- `1_month_ago` - Last month
- `6_months_ago` - Last 6 months (default)
- `all_time` - No filter (all issues)

## Important Defaults

- `issue list` defaults to last 6 months only
- `issue list` excludes completed/canceled by default
- Use `--include-completed` to see all issues
- Use `--newer-than all_time` to see all historical issues
