# GitHub Search: Developer's Cheat Sheet

## Table of Contents
1. [Overview & Core Purpose](#overview--core-purpose)
2. [Quick Start](#quick-start)
3. [Core Concepts & Architecture](#core-concepts--architecture)
4. [Search Syntax Fundamentals](#search-syntax-fundamentals)
5. [Essential Qualifiers by Search Type](#essential-qualifiers-by-search-type)
6. [Common Query Patterns](#common-query-patterns)
7. [Practical Query Examples](#practical-query-examples)
8. [Common Workflows](#common-workflows)
9. [Sorting Results](#sorting-results)
10. [Search Type Specific Details](#search-type-specific-details)
11. [Troubleshooting & Common Pitfalls](#troubleshooting--common-pitfalls)
12. [Quick Reference](#quick-reference)

---

## Overview & Core Purpose

GitHub Search is a powerful query language that allows you to find repositories, code, issues, pull requests, commits, discussions, and other resources across GitHub using specialized keywords called **qualifiers**.

**Key Value Proposition**: Construct precise queries to locate exactly what you need across millions of repositories using boolean logic, date ranges, numeric comparisons, and context-specific filters.

---

## Quick Start

GitHub Search is built-in to GitHub.com—no installation required. Simply use the search bar at the top of any GitHub page.

**Minimal Example:**
```
react hooks language:javascript stars:>100
```
This finds JavaScript repositories mentioning "react hooks" with over 100 stars.

**Basic Structure:**
```
<search-terms> <qualifier>:<value> <qualifier>:<value> ...
```

---

## Core Concepts & Architecture

### Mental Model

Think of GitHub Search as constructing a filter pipeline:

1. **Start with search terms** (words to match)
2. **Add qualifiers** to narrow scope and context
3. **Apply operators** for logic and ranges
4. **Sort results** for ordering

```
Broad Terms → Add Qualifiers → Apply Logic → Sort → Results
```

### Key Terminology

| Term | Definition | Example |
|------|------------|---------|
| **Qualifier** | Special keyword that filters results | `language:`, `is:`, `author:` |
| **Search Term** | Plain text words to match | `bug fix`, `react` |
| **Operator** | Logic or comparison symbol | `AND`, `OR`, `NOT`, `>`, `<`, `..` |
| **Scope** | Where the search applies | Repository, organization, user |
| **Sort Qualifier** | Orders results by a criterion | `sort:stars-desc` |

### Query Processing Order

1. Terms and qualifiers are evaluated (implicit AND between space-separated terms)
2. Boolean operators (`OR`, `NOT`) are applied
3. Parentheses group complex logic
4. Results are filtered
5. Sort order is applied

---

## Search Syntax Fundamentals

### Basic Operators

| Syntax | Purpose | Example |
|--------|---------|---------|
| `term1 term2` | Implicit AND—both terms required | `api documentation` |
| `term1 OR term2` | Either term matches | `python OR ruby` |
| `NOT term` | Excludes term | `api NOT graphql` |
| `-qualifier:value` | Excludes qualifier | `-language:javascript` |
| `"exact phrase"` | Multi-word exact match | `"memory leak"` |
| `()` | Groups expressions | `(ruby OR python) stars:>100` |

### Comparison Operators (Numeric & Dates)

| Operator | Meaning | Example |
|----------|---------|---------|
| `>n` | Greater than | `stars:>1000` |
| `>=n` | Greater than or equal | `forks:>=50` |
| `<n` | Less than | `size:<1000` |
| `<=n` | Less than or equal | `stars:<=100` |
| `n..n` | Inclusive range | `stars:100..500` |
| `n..*` | Greater than or equal (alternative) | `stars:100..*` |
| `*..n` | Less than or equal (alternative) | `stars:*..100` |

### Date Syntax

Dates must follow **ISO8601** format: `YYYY-MM-DD`

Optional time precision: `YYYY-MM-DDTHH:MM:SS+00:00`

| Usage | Example |
|-------|---------|
| After date | `created:>2023-01-01` |
| Before date | `pushed:<2023-12-31` |
| On exact date | `closed:2023-06-15` |
| Date range | `created:2023-01-01..2023-12-31` |
| With timezone | `created:2023-01-01T00:00:00+00:00` |

### Special Keywords

| Keyword | Usage | Example |
|---------|-------|---------|
| `@me` | References current user | `author:@me` |
| `@copilot` | References GitHub Copilot | `reviewed-by:@copilot` |

---

## Essential Qualifiers by Search Type

### Universal Qualifiers (All Search Types)

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `in:title` | Search in title only | `bug in:title` |
| `in:body` | Search in body/description | `error in:body` |
| `in:comments` | Search in comments | `thanks in:comments` |
| `in:readme` | Search in README files | `installation in:readme` |
| `in:name` | Search in repository name | `react in:name` |
| `in:description` | Search in repo description | `api in:description` |
| `in:topics` | Search in repository topics | `machine-learning in:topics` |

### Scoping Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `repo:OWNER/NAME` | Specific repository | `repo:facebook/react` |
| `org:ORGNAME` | Organization scope | `org:microsoft` |
| `user:USERNAME` | User's repositories | `user:torvalds` |

### Repository Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `language:LANG` | Programming language | `language:python` |
| `stars:n` | Star count (use operators) | `stars:>1000` |
| `forks:n` | Fork count | `forks:100..500` |
| `size:n` | Repo size in KB | `size:<1000` |
| `followers:n` | User/org followers | `followers:>=100` |
| `topics:n` | Number of topics | `topics:>3` |
| `created:DATE` | Repository creation date | `created:>2023-01-01` |
| `pushed:DATE` | Last push date | `pushed:>2023-06-01` |
| `fork:true\|false\|only` | Include/exclude/only forks | `fork:true` |
| `archived:true\|false` | Archived status | `archived:false` |
| `is:public\|private` | Visibility | `is:public` |
| `mirror:true\|false` | Mirror repositories | `mirror:false` |
| `template:true\|false` | Template repositories | `template:false` |
| `license:LICENSE` | License type | `license:mit` |
| `good-first-issues:>n` | Count of good first issues | `good-first-issues:>5` |
| `help-wanted-issues:>n` | Count of help wanted issues | `help-wanted-issues:>10` |
| `is:sponsorable` | Has GitHub Sponsors | `is:sponsorable` |
| `has:funding-file` | Has FUNDING file | `has:funding-file` |

### Issues & Pull Requests Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `is:issue\|pr` | Type filter | `is:issue` |
| `type:issue\|pr` | Alternative type filter | `type:pr` |
| `is:open\|closed` | State filter | `is:open` |
| `state:open\|closed` | Alternative state filter | `state:closed` |
| `is:merged\|unmerged` | Merge status (PRs only) | `is:merged` |
| `is:locked\|unlocked` | Lock status | `is:unlocked` |
| `is:public\|private` | Visibility | `is:public` |
| `author:USERNAME` | Created by user | `author:octocat` |
| `assignee:USERNAME` | Assigned to user | `assignee:defunkt` |
| `mentions:USERNAME` | User is mentioned | `mentions:torvalds` |
| `commenter:USERNAME` | User commented | `commenter:gaearon` |
| `involves:USERNAME` | User involved (author/assignee/mentions/commenter) | `involves:octocat` |
| `team:ORG/TEAM` | Team mentioned | `team:github/docs` |
| `label:"LABEL"` | Has specific label | `label:"bug"` |
| `no:label\|milestone\|assignee\|project` | Missing metadata | `no:assignee` |
| `milestone:NAME` | In milestone | `milestone:"v1.0"` |
| `project:NUMBER` | In project | `project:github/1` |
| `linked:pr\|issue` | Linked to PR or issue | `linked:pr` |
| `reason:completed\|"not planned"` | Close reason | `reason:completed` |
| `is:draft` | Draft pull request | `is:draft` |
| `review:none\|required\|approved\|changes_requested` | Review status | `review:approved` |
| `reviewed-by:USERNAME` | Reviewed by user | `reviewed-by:octocat` |
| `review-requested:USERNAME` | Review requested from user | `review-requested:@me` |
| `user-review-requested:@me` | Your review requested | `user-review-requested:@me` |
| `team-review-requested:TEAM` | Team review requested | `team-review-requested:github/docs` |
| `status:pending\|success\|failure` | CI/CD status | `status:success` |
| `head:BRANCH` | PR head branch | `head:feature-branch` |
| `base:BRANCH` | PR base branch | `base:main` |
| `comments:n` | Number of comments | `comments:>10` |
| `interactions:n` | Reactions + comments | `interactions:>50` |
| `reactions:n` | Number of reactions | `reactions:>100` |
| `created:DATE` | Creation date | `created:>2023-01-01` |
| `updated:DATE` | Last update date | `updated:>=2023-06-01` |
| `closed:DATE` | Close date | `closed:<2023-12-31` |
| `merged:DATE` | Merge date (PRs) | `merged:2023-01-01..2023-12-31` |
| `SHA` | Commit SHA (exact or partial) | `e1109ab` |
| `is:queued` | Queued to merge | `is:queued` |

### Commits Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `author:USERNAME` | Commit author | `author:torvalds` |
| `committer:USERNAME` | Committer | `committer:octocat` |
| `author-name:NAME` | Author name | `author-name:Linus` |
| `committer-name:NAME` | Committer name | `committer-name:GitHub` |
| `author-email:EMAIL` | Author email | `author-email:user@example.com` |
| `committer-email:EMAIL` | Committer email | `committer-email:bot@github.com` |
| `author-date:DATE` | Author date | `author-date:>2023-01-01` |
| `committer-date:DATE` | Commit date | `committer-date:<2023-12-31` |
| `merge:true\|false` | Include/exclude merge commits | `merge:false` |
| `hash:HASH` | Commit hash | `hash:abc123` |
| `parent:HASH` | Parent commit hash | `parent:def456` |
| `tree:HASH` | Tree hash | `tree:789ghi` |
| `is:public\|private` | Repository visibility | `is:public` |

### Code Search Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `repo:OWNER/NAME` | Repository scope | `repo:rails/rails` |
| `org:ORGNAME` | Organization scope | `org:github` |
| `user:USERNAME` | User scope | `user:octocat` |
| `language:LANG` | Programming language | `language:go` |
| `path:PATH` | File path (supports globs) | `path:src/*.js` |
| `path:/(regex)/` | Path regex | `path:/^src\/components\//` |
| `symbol:NAME` | Symbol definition | `symbol:handleClick` |
| `content:TERM` | File content only | `content:TODO` |
| `is:archived\|fork\|vendored\|generated` | Repository type | `NOT is:fork` |

### Discussions Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `is:open\|closed` | Discussion state | `is:open` |
| `is:answered\|unanswered` | Answer status | `is:answered` |
| `is:locked\|unlocked` | Lock status | `is:locked` |
| `is:public\|private` | Visibility | `is:public` |
| `author:USERNAME` | Discussion author | `author:octocat` |
| `commenter:USERNAME` | User commented | `commenter:defunkt` |
| `answered-by:USERNAME` | Answer author | `answered-by:torvalds` |
| `involves:USERNAME` | User involved | `involves:gaearon` |
| `comments:n` | Comment count | `comments:>10` |
| `created:DATE` | Creation date | `created:>2023-01-01` |
| `updated:DATE` | Update date | `updated:>=2023-06-01` |
| `category:NAME` | Discussion category | `category:Ideas` |
| `label:"LABEL"` | Discussion label | `label:"question"` |

### Topics Qualifiers

| Qualifier | Description | Example |
|-----------|-------------|---------|
| `is:featured` | Featured topics | `is:featured` |
| `is:curated` | Curated topics | `is:curated` |
| `is:not-featured` | Exclude featured | `is:not-featured` |
| `is:not-curated` | Exclude curated | `is:not-curated` |
| `repositories:n` | Repository count | `repositories:>1000` |
| `created:DATE` | Topic creation date | `created:>2020-01-01` |
| `topic:TOPIC` | Find repos by topic | `topic:machine-learning` |

---

## Common Query Patterns

### Pattern 1: Scope → Filter → Refine

Start broad, progressively narrow:

```
# Start with topic
machine learning

# Add language
machine learning language:python

# Add quality metrics
machine learning language:python stars:>500

# Add recency
machine learning language:python stars:>500 pushed:>2023-01-01

# Exclude archived
machine learning language:python stars:>500 pushed:>2023-01-01 archived:false
```

### Pattern 2: User-Centric Search

Find items related to specific users:

```
# User's repositories
user:octocat language:javascript

# Issues authored by user
is:issue author:torvalds

# PRs involving user (any role)
is:pr involves:gaearon

# Your assigned issues
is:issue assignee:@me is:open

# PRs awaiting your review
is:pr review-requested:@me
```

### Pattern 3: State + Metadata Filtering

Combine state with organizational metadata:

```
# Open bugs assigned to someone
is:issue is:open label:bug assignee:*

# Unassigned good first issues
is:issue is:open label:"good first issue" no:assignee

# Recently closed feature requests
is:issue is:closed label:enhancement closed:>2023-06-01

# Approved PRs awaiting merge
is:pr review:approved is:open -is:draft
```

### Pattern 4: Date Range Queries

Temporal filtering:

```
# Created in specific month
created:2023-06-01..2023-06-30

# Active in last 30 days
pushed:>2023-11-21

# Merged last quarter
is:pr is:merged merged:2023-10-01..2023-12-31
```

### Pattern 5: Metric-Based Discovery

Find repositories by popularity metrics:

```
# Popular but not overly mature
stars:100..1000 created:>2022-01-01

# Actively maintained popular repos
stars:>1000 pushed:>2023-06-01

# Well-forked libraries
forks:>500 language:java
```

### Pattern 6: Exclusion Pattern

Use NOT or `-` to refine:

```
# JavaScript but not Node.js
language:javascript NOT node

# Issues excluding bots
is:issue -author:app/dependabot

# Active repos excluding archived
pushed:>2023-01-01 archived:false

# PRs without CI failures
is:pr -status:failure
```

### Pattern 7: Boolean Combinations

Complex logic with OR and parentheses:

```
# Multiple languages
(language:python OR language:ruby) machine-learning

# Multiple states
is:issue (label:bug OR label:security)

# Multiple orgs
(org:facebook OR org:google) language:go stars:>500
```

---

## Practical Query Examples

### Example 1: Finding Active OSS Projects to Contribute To

**Goal**: Find beginner-friendly, actively maintained Python projects.

```
language:python 
is:issue 
is:open 
label:"good first issue" 
no:assignee 
stars:>100 
pushed:>2023-06-01 
archived:false
sort:updated-desc
```

**Why Each Qualifier**:
- `language:python` - Focus on Python projects
- `is:issue is:open` - Open issues only
- `label:"good first issue"` - Beginner-friendly
- `no:assignee` - Available to claim
- `stars:>100` - Quality indicator
- `pushed:>2023-06-01` - Recently active
- `archived:false` - Not abandoned
- `sort:updated-desc` - Most recently updated first

### Example 2: Auditing Security Issues in Dependencies

**Goal**: Find unresolved security issues in a dependency ecosystem.

```
org:nodejs 
is:issue 
is:open 
label:security 
-label:duplicate 
created:>2023-01-01
sort:reactions-desc
```

**Why Each Qualifier**:
- `org:nodejs` - Scope to Node.js organization
- `is:issue is:open` - Active security issues
- `label:security` - Security-related
- `-label:duplicate` - Exclude duplicates
- `created:>2023-01-01` - Recent vulnerabilities
- `sort:reactions-desc` - Community priority

### Example 3: Code Archaeology - Finding Implementation Patterns

**Goal**: Find how a specific function is implemented across codebases.

```
language:go 
symbol:WithContext 
NOT is:fork
```

**For path-specific code search**:
```
path:src/components/*.tsx 
language:typescript 
useState
```

**Why Each Qualifier**:
- `language:go` - Target language
- `symbol:WithContext` - Function/symbol definition
- `NOT is:fork` - Original implementations only
- `path:src/components/*.tsx` - Specific directory
- `useState` - Search term in code

### Example 4: Tracking Team Activity

**Goal**: Monitor team's recent pull request activity.

```
is:pr 
team-review-requested:github/security 
is:open 
created:>2023-11-01
sort:updated-desc
```

**Or for individual**:
```
involves:@me 
is:pr 
updated:>2023-11-01
sort:updated-desc
```

**Why Each Qualifier**:
- `is:pr` - Pull requests only
- `team-review-requested:github/security` - Team-specific
- `involves:@me` - Personal involvement
- `is:open` - Active PRs
- `created/updated:>DATE` - Recent activity
- `sort:updated-desc` - Latest first

### Example 5: Project Health Assessment

**Goal**: Evaluate repository maintenance quality.

```
repo:facebook/react 
is:issue 
is:open 
-label:duplicate 
comments:>5 
created:<2022-01-01
sort:comments-desc
```

**Why Each Qualifier**:
- `repo:facebook/react` - Specific repository
- `is:issue is:open` - Unresolved issues
- `-label:duplicate` - Real issues only
- `comments:>5` - Active discussion
- `created:<2022-01-01` - Old issues (maintenance debt)
- `sort:comments-desc` - Most discussed

---

## Common Workflows

### Workflow 1: Discovering New Projects

**Objective**: Find recently created, trending projects in your domain.

**Step 1**: Broad topic search
```
machine learning
```

**Step 2**: Add language and recency
```
machine learning language:python created:>2023-10-01
```

**Step 3**: Filter for quality and activity
```
machine learning language:python created:>2023-10-01 stars:>50 pushed:>2023-11-01
```

**Step 4**: Sort by popularity
```
machine learning language:python created:>2023-10-01 stars:>50 pushed:>2023-11-01 sort:stars-desc
```

### Workflow 2: Issue Triage for Maintainers

**Objective**: Prioritize issues requiring attention.

**Step 1**: Find unassigned open issues
```
is:issue is:open no:assignee
```

**Step 2**: Filter by labels and age
```
is:issue is:open no:assignee label:bug created:>2023-11-01
```

**Step 3**: Exclude known patterns
```
is:issue is:open no:assignee label:bug created:>2023-11-01 -label:duplicate -label:"needs more info"
```

**Step 4**: Sort by community engagement
```
is:issue is:open no:assignee label:bug created:>2023-11-01 -label:duplicate sort:reactions-desc
```

### Workflow 3: Code Review Queue Management

**Objective**: Manage incoming review requests efficiently.

**Step 1**: Check personal review requests
```
is:pr review-requested:@me is:open
```

**Step 2**: Filter by priority labels
```
is:pr review-requested:@me is:open (label:priority OR label:urgent)
```

**Step 3**: Exclude drafts
```
is:pr review-requested:@me is:open (label:priority OR label:urgent) -is:draft
```

**Step 4**: Sort by update time
```
is:pr review-requested:@me is:open (label:priority OR label:urgent) -is:draft sort:updated-asc
```

### Workflow 4: Monitoring Dependencies

**Objective**: Track updates and issues in dependencies.

**Step 1**: List recent commits in dependency
```
repo:lodash/lodash committer-date:>2023-11-01 merge:false
```

**Step 2**: Check for open security issues
```
repo:lodash/lodash is:issue is:open label:security
```

**Step 3**: Review recent pull requests
```
repo:lodash/lodash is:pr is:merged merged:>2023-11-01 sort:merged-desc
```

### Workflow 5: Competitive Analysis

**Objective**: Analyze similar projects in your space.

**Step 1**: Find similar projects
```
topic:static-site-generator language:javascript stars:>100
```

**Step 2**: Filter by activity
```
topic:static-site-generator language:javascript stars:>100 pushed:>2023-06-01
```

**Step 3**: Compare metrics
```
topic:static-site-generator language:javascript stars:>100 pushed:>2023-06-01 sort:forks-desc
```

**Step 4**: Analyze issue activity
```
# Switch to Issues search
topic:static-site-generator is:issue created:>2023-11-01
```

---

## Sorting Results

Sort qualifiers control result ordering. Always use with direction suffix (`-asc` or `-desc`).

### General Sort Options

| Sort Qualifier | Description | Example |
|----------------|-------------|---------|
| `sort:relevance` | Default: relevance score | `sort:relevance` |
| `sort:created` | Creation date | `sort:created-desc` |
| `sort:updated` | Last update date | `sort:updated-desc` |

### Repository-Specific Sorts

| Sort Qualifier | Description | Example |
|----------------|-------------|---------|
| `sort:stars` | Star count | `sort:stars-desc` |
| `sort:forks` | Fork count | `sort:forks-desc` |

### Issues & PRs Sorts

| Sort Qualifier | Description | Example |
|----------------|-------------|---------|
| `sort:comments` | Comment count | `sort:comments-desc` |
| `sort:interactions` | Reactions + comments | `sort:interactions-desc` |
| `sort:reactions` | Total reactions | `sort:reactions-desc` |
| `sort:reactions-+1` | Thumbs up reactions | `sort:reactions-+1-desc` |
| `sort:reactions--1` | Thumbs down reactions | `sort:reactions--1-desc` |
| `sort:reactions-smile` | Smile reactions | `sort:reactions-smile-desc` |
| `sort:reactions-tada` | Celebration reactions | `sort:reactions-tada-desc` |
| `sort:reactions-heart` | Heart reactions | `sort:reactions-heart-desc` |
| `sort:reactions-thinking_face` | Thinking reactions | `sort:reactions-thinking_face-desc` |
| `sort:reactions-rocket` | Rocket reactions | `sort:reactions-rocket-desc` |
| `sort:reactions-eyes` | Eyes reactions | `sort:reactions-eyes-desc` |

### Commit-Specific Sorts

| Sort Qualifier | Description | Example |
|----------------|-------------|---------|
| `sort:author-date` | Author date | `sort:author-date-desc` |
| `sort:committer-date` | Committer date | `sort:committer-date-desc` |

**Sort Direction**:
- `-desc` (or omitted): Descending (high to low)
- `-asc`: Ascending (low to high)

**Example**:
```
# Most starred repos first
language:rust sort:stars-desc

# Oldest issues first
is:issue is:open sort:created-asc

# Most discussed PRs
is:pr sort:comments-desc
```

---

## Search Type Specific Details

### Repository Search

**Default Behavior**: 
- Searches repository name, description, README, and topics
- Excludes forks by default
- Returns repositories

**Key Patterns**:
```
# By metadata
language:go stars:>1000

# By content
"API documentation" in:readme

# By property
license:mit archived:false

# By custom properties (if configured)
org:github props.environment:production
```

**Remember**: Use `fork:true` to include forks.

### Code Search

**Default Behavior**:
- Searches file content and paths
- Excludes forks unless fork has more stars than parent
- Case-insensitive by default

**Special Syntax**:
```
# Regular expressions
/sparse.*index/

# Exact matches
"exact code snippet"

# Path globs
path:src/**/*.js

# Symbol definitions
symbol:ComponentName language:typescript
```

**Remember**: 
- Wrap regex in `/`
- Use `\\` to escape backslash
- Use `\"` to escape quotes
- Case-sensitive regex: `/(?-i)CamelCase/`

### Issues & Pull Requests Search

**Default Behavior**:
- Searches titles, bodies, and comments
- Returns both issues and PRs unless filtered
- Includes open and closed

**Key Patterns**:
```
# By user role
author:@me assignee:@me involves:@me

# By review status
is:pr review:approved review-requested:@me

# By linked items
is:issue linked:pr

# By CI status
is:pr status:failure
```

**Remember**: Use `type:pr` or `is:pr` to separate PRs from issues.

### Commits Search

**Default Behavior**:
- Searches commit messages
- Must scope to repo, org, or user
- Returns commits

**Key Patterns**:
```
# By author
repo:torvalds/linux author:torvalds

# By date
author-date:>2023-01-01 merge:false

# By content
refactor committer-date:>2023-06-01
```

**Remember**: Differentiate `author-date` (when authored) from `committer-date` (when committed).

### Discussions Search

**Default Behavior**:
- Searches discussion titles, bodies, and comments
- Includes all discussions

**Key Patterns**:
```
# By category
category:Ideas is:open

# By answer status
is:unanswered created:>2023-11-01

# By involvement
involves:@me updated:>2023-11-01
```

### Topics Search

**Default Behavior**:
- Searches topic names
- Returns topic pages

**Key Patterns**:
```
# Curated topics
is:curated machine-learning

# By repository count
repositories:>1000 created:>2020-01-01
```

---

## Troubleshooting & Common Pitfalls

### Problem: No Results for Code in Forks

**Symptom**: Known code exists in a fork, but search returns nothing.

**Cause**: Code search excludes forks unless the fork has more stars than the parent.

**Solution**: 
```
# Specify the fork directly
repo:username/forked-repo your-search-term

# Or use fork:true (limited effectiveness for code search)
your-search-term fork:true
```

**Prevention**: Use direct repository scoping when searching forks.

---

### Problem: Multi-Word Label Not Matching

**Symptom**: `label:good first issue` returns no results.

**Cause**: Spaces in label names require quotes.

**Solution**:
```
# Correct
label:"good first issue"

# Incorrect
label:good first issue  # This searches for label:good AND first AND issue
```

**Prevention**: Always quote multi-word qualifiers.

---

### Problem: Date Filter Not Working

**Symptom**: `created:01/15/2023` returns error or unexpected results.

**Cause**: Incorrect date format.

**Solution**:
```
# Correct
created:2023-01-15

# Incorrect
created:01/15/2023
created:15-01-2023
```

**Prevention**: Use ISO8601 format: `YYYY-MM-DD`.

---

### Problem: Finding Your Own Content Returns Nothing

**Symptom**: `author:myusername` finds nothing.

**Cause**: Wrong qualifier for search type, or not scoped correctly.

**Solution**:
```
# For your issues/PRs (correct)
is:issue author:@me

# For commits in a repo (correct)
repo:owner/repo author:@me

# For your repositories (correct)
user:@me
```

**Prevention**: Use `@me` shorthand and ensure correct scope.

---

### Problem: Too Many Results

**Symptom**: Search returns thousands of results, hard to navigate.

**Cause**: Query too broad, needs refinement.

**Solution**: Add progressive qualifiers:
```
# Start
api

# Add language
api language:python

# Add quality filter
api language:python stars:>100

# Add recency
api language:python stars:>100 pushed:>2023-01-01

# Add sort
api language:python stars:>100 pushed:>2023-01-01 sort:stars-desc
```

**Prevention**: Start specific, broaden if needed.

---

### Problem: Boolean Logic Not Working as Expected

**Symptom**: `api NOT documentation OR tutorial` returns unexpected results.

**Cause**: Operator precedence or missing parentheses.

**Solution**:
```
# Correct - clear precedence
api NOT (documentation OR tutorial)

# Or be explicit
api -documentation -tutorial
```

**Prevention**: Use parentheses for complex boolean expressions.

---

### Problem: Symbol Search Returns Nothing

**Symptom**: `symbol:MyFunction` returns no results despite function existing.

**Cause**: Symbol not extracted, or language not supported.

**Solution**:
- Verify language is in supported list (Go, Rust, Python, JavaScript, TypeScript, etc.)
- Use fallback to content search: `MyFunction language:go`
- Scope to repository: `repo:owner/name symbol:MyFunction`

**Prevention**: Check language support; use content search as fallback.

---

### Problem: Cannot Exclude Bots from Search

**Symptom**: Results include automated bot accounts.

**Cause**: Bots are app accounts with `app/` prefix.

**Solution**:
```
# Exclude specific bot
is:issue -author:app/dependabot

# Exclude multiple bots
is:pr -author:app/dependabot -author:app/renovate
```

**Prevention**: Use `-author:app/botname` pattern.

---

### Problem: Regex Not Matching in Code Search

**Symptom**: Regular expression returns no results.

**Cause**: Regex must be wrapped in `/` for code search.

**Solution**:
```
# Correct
/function\s+\w+\(/

# Incorrect (treated as literal string)
function\s+\w+\(
```

**Prevention**: Always wrap regex in forward slashes in code search.

---

## Quick Reference

### Most Common Queries (Copy-Paste Ready)

```bash
# Recently active Python projects with good first issues
language:python is:issue is:open label:"good first issue" no:assignee stars:>100 pushed:>2023-06-01 archived:false

# My open issues and PRs
involves:@me is:open

# PRs awaiting my review
is:pr review-requested:@me is:open -is:draft

# Popular repos by topic
topic:machine-learning stars:>1000 pushed:>2023-01-01 archived:false sort:stars-desc

# Recent commits by user in repo
repo:owner/name author:username committer-date:>2023-11-01 merge:false

# Code with specific symbol
language:go symbol:WithContext NOT is:fork

# Open security issues in org
org:orgname is:issue is:open label:security sort:reactions-desc

# Unmerged PRs in date range
is:pr is:unmerged created:2023-11-01..2023-11-30
```

### Essential Qualifier Cheat Sheet

| Category | Qualifiers |
|----------|------------|
| **Scope** | `repo:`, `org:`, `user:` |
| **Type** | `is:issue`, `is:pr`, `type:pr` |
| **State** | `is:open`, `is:closed`, `is:merged` |
| **User** | `author:`, `assignee:`, `mentions:`, `involves:`, `commenter:` |
| **Label/Milestone** | `label:`, `milestone:`, `no:label` |
| **Date** | `created:`, `updated:`, `pushed:`, `closed:`, `merged:` |
| **Metrics** | `stars:`, `forks:`, `comments:`, `reactions:` |
| **Language** | `language:` |
| **Review** | `review:`, `reviewed-by:`, `review-requested:` |
| **Sort** | `sort:stars-desc`, `sort:updated-desc`, `sort:created-asc` |

### Operator Quick Reference

| Operator | Example |
|----------|---------|
| `AND` (implicit) | `bug fix` |
| `OR` | `python OR ruby` |
| `NOT` | `api NOT graphql` |
| `-` | `-label:duplicate` |
| `>` | `stars:>1000` |
| `<` | `forks:<50` |
| `..` | `stars:100..500` |
| `"..."` | `"memory leak"` |
| `()` | `(ruby OR python) stars:>100` |
| `/regex/` | `/function.*name/` (code search) |

### Syntax Rules Summary

1. **Spaces = AND**: `bug fix` means both "bug" AND "fix"
2. **Quote multi-word values**: `label:"good first issue"`
3. **Dates are ISO8601**: `YYYY-MM-DD`
4. **Ranges are inclusive**: `stars:10..50` includes 10 and 50
5. **Negation prefix**: `-language:javascript` or `NOT javascript`
6. **Fork inclusion**: Add `fork:true` for repositories/code
7. **Case sensitivity**: Generally case-insensitive; use `/(?-i)Term/` for sensitive regex
8. **Special users**: `@me` = current user, `@copilot` = GitHub Copilot

---

<chatName="GitHub Search Cheat Sheet - Comprehensive LLM Reference"/>