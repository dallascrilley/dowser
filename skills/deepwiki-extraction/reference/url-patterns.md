# GitHub URL Parsing Patterns

Reference guide for supported GitHub repository URL formats and parsing edge cases.

---

## Supported Formats

### 1. Shorthand Format
**Pattern:** `owner/repo`

**Examples:**
```
anthropics/claude-code
fastapi/fastapi
pydantic/pydantic
microsoft/vscode
```

**Characteristics:**
- Already in target format
- No transformation needed
- Most efficient input method
- Regex: `^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$`

**Edge Cases:**
- Repo names can contain dots: `owner/repo.js` ✓
- Repo names can contain hyphens: `owner/my-repo` ✓
- Underscores allowed: `my_org/my_repo` ✓
- Cannot contain spaces or special chars: `owner/repo@v1` ✗

---

### 2. HTTPS URLs
**Pattern:** `https://github.com/owner/repo[.git]`

**Examples:**
```
https://github.com/anthropics/anthropic-sdk-python
https://github.com/anthropics/anthropic-sdk-python.git
http://github.com/fastapi/fastapi (auto-upgraded to https)
```

**Transformation:**
1. Parse URL components
2. Verify netloc is `github.com`
3. Extract path components
4. Strip `.git` suffix if present
5. Return `owner/repo`

**Edge Cases:**
- With `.git` suffix: Strip it
- Subpaths (e.g., `/tree/main`): Extract only owner/repo
- HTTP URLs: Accepted (will use HTTPS for DeepWiki)
- Non-GitHub domains: Rejected with error

**Error Cases:**
```
https://gitlab.com/owner/repo  → Error: Not a GitHub URL
https://github.com/owner       → Error: Invalid format (missing repo)
https://github.com             → Error: Invalid format (no path)
```

---

### 3. SSH URLs
**Pattern:** `git@github.com:owner/repo[.git]`

**Examples:**
```
git@github.com:anthropics/claude-code.git
git@github.com:fastapi/fastapi
```

**Transformation:**
1. Match SSH pattern with regex
2. Extract owner and repo groups
3. Strip `.git` suffix if present
4. Return `owner/repo`

**Regex Pattern:**
```python
^git@github\.com:([^/]+)/(.+?)(\.git)?$
```

**Edge Cases:**
- With `.git` suffix: Strip it
- Without `.git` suffix: Accept as-is
- Different hosts: Not supported (GitHub only)

---

### 4. Local Repository
**Pattern:** `[--check-local] /path/to/repo`

**Behavior:**
1. Read `.git/config` from specified path
2. Find `[remote "origin"]` section
3. Extract `url = ...` value
4. Parse URL using HTTPS or SSH patterns above
5. Return `owner/repo`

**Examples:**
```bash
# .git/config contains:
[remote "origin"]
    url = https://github.com/anthropics/claude-code.git

# Command:
python parse_github_url.py --check-local /path/to/repo

# Output:
anthropics/claude-code
```

**Edge Cases:**
- Multiple remotes: Uses first GitHub remote found
- No GitHub remote: Error
- Not a git repo (no `.git/config`): Error
- Malformed config: Error

**Remote URL Patterns Searched:**
- `url = https://github.com/owner/repo.git`
- `url = git@github.com:owner/repo.git`

---

## Validation Rules

### Valid Owner Names
- Alphanumeric: `a-z`, `A-Z`, `0-9`
- Hyphens: `-`
- Underscores: `_`
- Cannot start with hyphen
- Max length: 39 characters (GitHub limit)

### Valid Repository Names
- Alphanumeric: `a-z`, `A-Z`, `0-9`
- Hyphens: `-`
- Underscores: `_`
- Dots: `.`
- Cannot be `.` or `..`
- Max length: 100 characters (GitHub limit)

---

## Error Handling

### Common Errors

**Invalid URL Format:**
```
Input: "not-a-url"
Error: Unrecognized URL format: not-a-url
```

**Non-GitHub URL:**
```
Input: "https://gitlab.com/owner/repo"
Error: Not a GitHub URL: https://gitlab.com/owner/repo
```

**Missing Components:**
```
Input: "https://github.com/owner"
Error: Invalid GitHub URL format: https://github.com/owner
```

**Local Repo Not Found:**
```
Input: --check-local /path/without/git
Error: Not a git repository: /path/without/git
```

**No GitHub Remote:**
```
Input: --check-local /path/to/local-only-repo
Error: No GitHub remote found in /path/to/local-only-repo/.git/config
```

---

## Usage in Workflow

The `parse_github_url.py` script handles all parsing automatically:

```bash
# All these produce: anthropics/claude-code

python scripts/parse_github_url.py "anthropics/claude-code"

python scripts/parse_github_url.py "https://github.com/anthropics/claude-code"

python scripts/parse_github_url.py "git@github.com:anthropics/claude-code.git"

python scripts/parse_github_url.py --check-local ~/repos/claude-code
```

**Integration with DeepWiki:**
```bash
# Parse repository identifier
OWNER_REPO=$(python scripts/parse_github_url.py "$USER_INPUT")

# Construct DeepWiki URL
DEEPWIKI_URL="https://deepwiki.com/$OWNER_REPO"

# Navigate using Chrome DevTools MCP
# mcp__chrome-devtools__navigate_page with DEEPWIKI_URL
```

---

## Testing Edge Cases

When implementing or debugging, test these scenarios:

1. ✓ Standard shorthand: `owner/repo`
2. ✓ HTTPS with .git: `https://github.com/owner/repo.git`
3. ✓ HTTPS without .git: `https://github.com/owner/repo`
4. ✓ SSH with .git: `git@github.com:owner/repo.git`
5. ✓ SSH without .git: `git@github.com:owner/repo`
6. ✓ Local repo with HTTPS remote
7. ✓ Local repo with SSH remote
8. ✗ Invalid shorthand: `owner` (no slash)
9. ✗ Non-GitHub URL: `https://gitlab.com/owner/repo`
10. ✗ Malformed URL: `ht!tp://github/bad`
11. ✗ Local path without .git: `/some/random/path`
12. ✗ Local repo with no GitHub remote

---

## Future Considerations

**Out of Scope (Won't Support):**
- GitLab, Bitbucket, or other Git hosts
- GitHub Enterprise custom domains
- Gist URLs
- GitHub URLs with subpaths (e.g., `/tree/branch`)
- Private repository authentication
- Repository aliases or redirects

**Rationale:** DeepWiki only supports public GitHub repositories at `deepwiki.com/owner/repo` format. Additional patterns would provide no value.
