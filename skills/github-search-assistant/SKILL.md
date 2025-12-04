---
name: github-search-assistant
short_description: >-
  Transform natural language into precise GitHub search queries for
  repositories, code, issues, PRs, or commits. Generates properly formatted URLs
  and optionally executes searches via API with formatted results.
description: >-
  This skill should be used when searching GitHub for repositories, code,
  issues, pull requests, or commits. Use when user wants to find projects,
  discover code examples, track issues, or analyze GitHub activity. Trigger
  phrases include "search GitHub", "find repos", "GitHub query", "search for
  code", "find issues", "discover projects".
when_to_use: >-
  locating specific repositories, code examples, issues, or pull requests on
  GitHub, particularly when faced with vague search queries or needing to
  analyze GitHub activity.
version: 1.0.0
languages: all
category: agents-and-skills
---

# GitHub Search Assistant

Transform natural language requests into precise GitHub search queries, then optionally execute them via API and present formatted results.

## When to Use This Skill

Use this skill when:
- User wants to search GitHub for repositories, code, issues, PRs, or commits
- User asks to "find" or "discover" projects on GitHub
- User needs help constructing GitHub search queries
- User wants to analyze GitHub activity or trends
- User mentions searching for code examples or implementations

## How This Skill Works

### Step 1: Understand User Intent

Parse the user's request to identify:
- **Search type**: repositories, code, issues, pull requests, commits, discussions, topics
- **Key criteria**: language, stars, date ranges, labels, authors, organizations
- **Sort preference**: stars, forks, recently updated, relevance
- **Quality filters**: active maintenance, beginner-friendly, etc.

### Step 2: Generate Search Queries

Construct 2-4 targeted GitHub search queries using advanced qualifiers. For each query:

1. **Build the query string** using GitHub search syntax
2. **Generate the clickable URL** in this format:
   - Repositories: `https://github.com/search?q={encoded_query}&type=repositories`
   - Code: `https://github.com/search?q={encoded_query}&type=code`
   - Issues: `https://github.com/search?q={encoded_query}&type=issues`
   - PRs: `https://github.com/search?q={encoded_query}&type=pullrequests`
   - Commits: `https://github.com/search?q={encoded_query}&type=commits`

3. **Explain the query** - briefly describe what each query targets

**Present queries in this format:**

```markdown
### Query 1: [Brief description]
**Query**: `language:python machine-learning stars:>100 pushed:>2024-01-01`
**URL**: https://github.com/search?q=language%3Apython+machine-learning+stars%3A>100+pushed%3A>2024-01-01&type=repositories
**Targets**: Active Python ML projects with good community traction

### Query 2: [Brief description]
**Query**: `language:python topic:machine-learning is:issue is:open label:"good first issue" no:assignee`
**URL**: https://github.com/search?q=language%3Apython+topic%3Amachine-learning+is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22+no%3Aassignee&type=issues
**Targets**: Beginner-friendly open issues in ML projects
```

### Step 3: Offer API Execution

After presenting queries, ask:

> "Would you like me to execute any of these searches via the GitHub API and show you the results?"

If user agrees:
- Use `scripts/github_search.py` to execute the query
- Present results in clean, formatted output

### Step 4: Present Results

Format API results as:

```markdown
## Search Results: [Query description]

### Top Results (showing X of Y total):

#### 1. [Repository/Issue/Code Name]
- **URL**: [direct link]
- **Stars/Reactions**: [count]
- **Last Updated**: [date]
- **Description**: [brief description]
- [Additional relevant metadata]

#### 2. [Next result]
...
```

## Common Query Patterns

Reference `references/github-search-syntax.md` for comprehensive syntax. Key patterns:

### Repository Discovery
```
language:LANG stars:>N pushed:>DATE archived:false
topic:TOPIC stars:N..N created:>DATE
```

### Issue Hunting
```
is:issue is:open label:"LABEL" no:assignee stars:>N
is:issue author:USER created:>DATE sort:reactions-desc
```

### Code Examples
```
language:LANG symbol:FUNCTION NOT is:fork
path:PATH/*.EXT SEARCH_TERM language:LANG
```

### PR Tracking
```
is:pr review-requested:@me is:open -is:draft
is:pr is:merged merged:DATE..DATE org:ORG
```

## Quick Start

### With API Execution

**Requires**: `GITHUB_TOKEN` environment variable (optional but recommended for higher rate limits)

```bash
# Set GitHub token (optional)
export GITHUB_TOKEN="your-token-here"

# Execute search
python scripts/github_search.py \
  --query "language:python machine-learning stars:>100" \
  --type repositories \
  --limit 10
```

### URL-Only Mode

**No authentication needed** - just generate query URLs for the user to click.

## Search Type Reference

| Type | URL Parameter | Common Use Cases |
|------|---------------|------------------|
| Repositories | `type=repositories` | Finding projects, libraries, frameworks |
| Code | `type=code` | Finding implementation examples, patterns |
| Issues | `type=issues` | Finding bugs, feature requests, discussions |
| Pull Requests | `type=pullrequests` | Tracking contributions, reviews |
| Commits | `type=commits` | Code archaeology, author tracking |
| Discussions | `type=discussions` | Community Q&A, announcements |
| Topics | `type=topics` | Discovering categories, trends |

## Essential Qualifiers

**Scope**:
- `repo:owner/name` - Specific repository
- `org:orgname` - Organization scope
- `user:username` - User's repositories
- `language:lang` - Programming language

**Quality**:
- `stars:>N` or `stars:N..N` - Star count ranges
- `forks:>N` - Fork count
- `pushed:>DATE` - Last push date (activity indicator)
- `created:>DATE` - Creation date

**State** (Issues/PRs):
- `is:open` or `is:closed` - State
- `is:merged` - Merged PRs
- `is:draft` - Draft PRs
- `no:assignee` - Unassigned issues

**User Roles**:
- `author:user` - Created by
- `assignee:user` - Assigned to
- `involves:user` - Any involvement
- `review-requested:user` - Review requested

**Labels/Metadata**:
- `label:"label name"` - Has label
- `no:label` - No labels
- `milestone:name` - In milestone

**Sorting**:
- `sort:stars-desc` - Most starred first
- `sort:updated-desc` - Recently updated
- `sort:created-asc` - Oldest first

## Restrictions & Limitations

### Code Search Restrictions

**Critical limitations when searching code** (`type=code`):

#### ❌ DON'T: Use sorting qualifiers in code search

**What fails:**
```
language:python sort:stars
filename:config.json sort:pushed
```

**Why:** Sorting qualifiers aren't supported for code search; results are always in "best match" order.

**✅ DO THIS INSTEAD:**
```
type:repository language:python sort:stars
```

#### ❌ DON'T: Search by repository properties in code search

**What fails:**
```
topic:react language:javascript
team:myteam filename:index.js
pushed:>2024-01-01 language:python
```

**Why:** `topic:`, `team:`, and `pushed:` only work for repository searches, not code searches.

**✅ DO THIS INSTEAD:**
```
# For topics: search the name as text
react language:javascript

# For time-based searches: segment by keyword
"import requests" language:python
"import asyncio" language:python

# For team-owned code: search specific repos
org:myteam repo:project-name language:python
```

#### ❌ DON'T: Try to get results beyond the 100-result limit

**What happens:** Code search caps at 100 results per query (5 pages × 20 results).

**✅ DO THIS INSTEAD:**

**Segment by time:**
```
created:>=2024-01-01 created:<2024-06-01 language:python
created:>=2023-06-01 created:<2024-01-01 language:python
```

**Segment by keyword:**
```
"async def" language:python
"asyncio.run" language:python
```

**Use repository drill-down:**
```
repo:kubernetes/kubernetes "concurrency"
repo:golang/go "concurrency"
```

#### ❌ DON'T: Make anonymous searches

**What happens:** Code search severely rate-limits or blocks unauthenticated users.

**✅ DO THIS INSTEAD:**
Always sign into GitHub before searching. If rate-limited despite login, wait 6 seconds between requests (10 req/min limit).

#### ❌ DON'T: Rely on exact string matching

**What fails:**
```
"const x = 42"
# You get fuzzy matches: "const x=42", "let x = 42", etc.
```

**Why:** Code search uses fuzzy matching, not exact literal matching.

**✅ DO THIS INSTEAD:**
Use specific surrounding context:
```
"function getUserData() {" language:javascript
```

### Supported vs Unsupported Qualifiers

#### ✅ What WORKS in Code Search

| Qualifier | Example | Use Case |
|-----------|---------|----------|
| `language:` | `language:python` | Filter by programming language |
| `path:` | `path:config` | Search specific file paths |
| `filename:` | `filename:.env` | Search specific filenames |
| `org:` | `org:kubernetes` | Limit to organization repos |
| `repo:` | `repo:torvalds/linux` | Search specific repository |
| `fork:` | `fork:true`, `fork:false` | Include/exclude forks |
| `user:` | `user:torvalds` | Search user's repositories |
| `is:public` | `is:public language:python` | Public repos only |
| `symbol:` | `symbol:MyClass` | Search code symbols |
| Text/regex | `"function getName"` | Direct text matching |

#### ❌ What DOESN'T Work in Code Search

| Qualifier | Why Not | Alternative |
|-----------|---------|-------------|
| `sort:*` | Not supported for code | Use `type:repository sort:*` |
| `pushed:` | Not supported for code | Segment by date range |
| `topic:` | Only for repos | Search as plain text |
| `team:` | Only for repos | Use `org:` |
| `stars:>100` | Not supported for code | Use `type:repository stars:>100` |

### Rate Limits

| Limit | Value | Fix |
|-------|-------|-----|
| Requests/minute | 10 (authenticated) | Wait 6 seconds between requests |
| Results per query | 100 max | Segment into multiple queries |
| Results per page | 20 | Pagination stops at 5 pages |
| Anonymous access | Severely limited | Sign into GitHub |

**When rate limited:**
- Wait 60 seconds, then space requests at least 6 seconds apart
- Verify you're logged in (check top-right avatar)
- Consider using GitHub Archive API for large-scale analysis (no limits)

### Workarounds & Proven Patterns

#### Pattern 1: Time-Based Segmentation

Divide searches into date ranges to bypass the 100-result limit:
```
created:>=2024-01-01 created:<2024-04-01 language:python "search term"
created:>=2024-04-01 created:<2024-07-01 language:python "search term"
```

#### Pattern 2: Keyword Segmentation

Search keyword variations separately for multiplicative coverage:
```
"async function" language:javascript
"async () =>" language:javascript
```

#### Pattern 3: Repository Drill-Down

Search within specific high-value repos (often returns <100 results):
```
repo:kubernetes/kubernetes "concurrency"
repo:golang/go "concurrency"
```

#### Pattern 4: Repository Search as Gateway

Use repository search (which supports sorting) to find quality repos, then drill down with code search:
```
# First: type:repository language:go sort:stars
# Then: repo:kubernetes/kubernetes "context.Context"
```

### Quick Decision Tree

```
Do you know which specific repos matter?
├─ YES → Use repo:name "search" (often <100 results)
└─ NO → Need to find repos first?
   ├─ YES → type:repository sort:stars, then drill down
   └─ NO → Need all results across many repos?
      ├─ YES → Use segmentation (time or keyword)
      └─ NO → Single search for top 100 matches
```

## Error Handling

**Rate Limiting** (API mode):
- GitHub API: 60 requests/hour (unauthenticated), 5000/hour (authenticated)
- Code search: 10 requests/minute (authenticated) - wait 6 seconds between requests
- If rate limited, suggest using URL mode or setting `GITHUB_TOKEN`
- See [Rate Limits](#rate-limits) section for detailed limits

**Invalid Queries**:
- Check for quoted multi-word labels: `label:"good first issue"` not `label:good first issue`
- Validate date format: `YYYY-MM-DD` (ISO 8601)
- Ensure operators have correct syntax: `stars:>100` not `stars > 100`
- **Code search**: Don't use `sort:`, `topic:`, `pushed:`, `team:`, or `stars:` qualifiers (see [Restrictions & Limitations](#restrictions--limitations))

**"Qualifier not supported for code search"**:
- You used a qualifier that only works for repository search
- Replace unsupported qualifiers:
  - ❌ `language:python sort:stars` → ✅ `type:repository language:python sort:stars`
  - ❌ `topic:machine-learning neural network` → ✅ `machine-learning neural network language:python`

**"Too many requests" or "API rate limit exceeded"**:
- Wait 60 seconds, then space requests at least 6 seconds apart
- Verify you're logged in (check top-right avatar)
- For code search: Ensure authentication is active

**"Only getting 100 results, need more"**:
- Code search is capped at 100 results per query
- Use segmentation strategies (time-based, keyword-based, or repo-based)
- See [Workarounds & Proven Patterns](#workarounds--proven-patterns) section

**Search results aren't exact matches**:
- Code search uses fuzzy matching, not exact literal matching
- Add more context to reduce false positives:
  - ❌ Too generic: `"const x = 42"`
  - ✅ More specific: `"function initDatabase() { const x = 42"`

**Can't search without logging in**:
- Code search requires authentication since mid-2023
- Sign in via browser or CLI (`gh auth login`)
- For large-scale analysis, use GitHub Archive (https://www.gharchive.org/), which has no limits

**No Results**:
- Suggest broadening criteria (remove filters incrementally)
- Check for typos in language names, labels
- Try alternative qualifiers (e.g., search topic name as text instead of `topic:`)
- Verify qualifiers are supported for the search type (see [Restrictions & Limitations](#restrictions--limitations))

## Examples

### Example 1: Finding Contribution Opportunities

**User request**: "Find Python projects I can contribute to"

**Generated queries**:

**Query 1: Beginner-friendly open issues**
```
Query: language:python is:issue is:open label:"good first issue" no:assignee stars:>50 pushed:>2024-01-01
URL: https://github.com/search?q=language%3Apython+is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22+no%3Aassignee+stars%3A>50+pushed%3A>2024-01-01&type=issues
```

**Query 2: Active projects seeking help**
```
Query: language:python label:"help wanted" is:issue is:open archived:false sort:updated-desc
URL: https://github.com/search?q=language%3Apython+label%3A%22help+wanted%22+is%3Aissue+is%3Aopen+archived%3Afalse+sort%3Aupdated-desc&type=issues
```

### Example 2: Finding Code Implementations

**User request**: "Show me how people implement authentication in FastAPI"

**Generated queries**:

**Query 1: Symbol search for auth functions**
```
Query: language:python symbol:authenticate path:**/auth*.py
URL: https://github.com/search?q=language%3Apython+symbol%3Aauthenticate+path%3A**%2Fauth*.py&type=code
```

**Query 2: FastAPI authentication examples**
```
Query: "FastAPI" "authentication" language:python path:*.py NOT is:fork
URL: https://github.com/search?q=%22FastAPI%22+%22authentication%22+language%3Apython+path%3A*.py+NOT+is%3Afork&type=code
```

### Example 3: Repository Discovery

**User request**: "Find popular Rust CLI tools created recently"

**Generated queries**:

**Query 1: Recent high-quality Rust CLIs**
```
Query: topic:cli language:rust stars:>100 created:>2023-01-01 archived:false sort:stars-desc
URL: https://github.com/search?q=topic%3Acli+language%3Arust+stars%3A>100+created%3A>2023-01-01+archived%3Afalse+sort%3Astars-desc&type=repositories
```

**Query 2: Actively maintained Rust tools**
```
Query: rust cli stars:50..500 pushed:>2024-06-01 sort:updated-desc
URL: https://github.com/search?q=rust+cli+stars%3A50..500+pushed%3A>2024-06-01+sort%3Aupdated-desc&type=repositories
```

## Progressive Disclosure

- **SKILL.md**: Quick start, common patterns, examples
- **references/github-search-syntax.md**: Complete GitHub search cheat sheet with all qualifiers, operators, and advanced patterns

Load the reference file when:
- User needs comprehensive qualifier documentation
- Constructing complex multi-criteria queries
- Troubleshooting query syntax issues
- Exploring advanced search features

## Workflow Checklist

When user requests a GitHub search:

```
- [ ] Parse intent: What are they looking for? (repos, code, issues, etc.)
- [ ] Identify criteria: Language, stars, date, labels, authors?
- [ ] Determine sort preference: Stars, recency, relevance?
- [ ] Check for code search restrictions: Avoid sort:, topic:, pushed:, team:, stars: in code searches
- [ ] Construct 2-4 targeted queries with proper qualifiers
- [ ] Verify qualifiers are supported for the search type (see Restrictions & Limitations)
- [ ] Generate properly URL-encoded search URLs
- [ ] Explain what each query targets
- [ ] Offer API execution option
- [ ] If API: Execute and format results (respect rate limits: 6s between code searches)
- [ ] If needed: Reference github-search-syntax.md for advanced qualifiers
- [ ] If hitting limits: Suggest segmentation strategies (time/keyword/repo-based)
```

## Notes

- **URL encoding**: Space becomes `+`, special chars use `%XX` format
- **Quote multi-word values**: Labels, milestones, exact phrases
- **Date format**: Always `YYYY-MM-DD` (ISO 8601)
- **API limits**: 60/hour unauthenticated, 5000/hour with token; Code search: 10/minute authenticated
- **Code search restrictions**: No `sort:`, `topic:`, `pushed:`, `team:`, or `stars:` qualifiers; 100 result limit; requires authentication
- **Progressive refinement**: Start broad, narrow with filters if too many results
- **For comprehensive syntax**: See `references/github-search-syntax.md`
- **For restrictions & workarounds**: See [Restrictions & Limitations](#restrictions--limitations) section
