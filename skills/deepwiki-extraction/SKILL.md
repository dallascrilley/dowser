---
name: deepwiki-extraction
description: >-
  Extracts comprehensive repository documentation from DeepWiki by navigating
  with Chrome DevTools MCP, capturing all sections as markdown, and enabling Q&A
  about the codebase. Use when the user provides a GitHub repository URL, asks
  about repository documentation, mentions DeepWiki, or wants to understand a
  codebase's structure and features.
when_to_use: >
  Use when extracting repository documentation from DeepWiki, user provides
  GitHub URL, asks about repo docs, mentions DeepWiki, wants to understand
  codebase structure, or needs to extract once and answer multiple questions
  from cached content.
version: 1.0.0
category: research-and-learning
---

# DeepWiki Documentation Extraction

Automate extraction and analysis of GitHub repository documentation from DeepWiki using Chrome DevTools MCP.

## When to Use

Activate when user:
- Provides GitHub repository URL
- Asks to "extract documentation from [repo]"
- Mentions "DeepWiki"
- Requests "summarize [repo]" or "analyze [repo] documentation"
- Wants to understand codebase structure/features

## What This Does

1. Parses GitHub repository identifiers
2. Navigates to DeepWiki using Chrome DevTools MCP
3. Extracts all documentation sections
4. Formats as clean markdown
5. Enables follow-up Q&A from cached extraction

**Key Benefit:** Extract once, answer multiple questions without re-navigating.

---

## Quick Start

**User:** `Extract docs for https://github.com/anthropics/anthropic-sdk-python`

**You:**
```
I'll extract the repository documentation from DeepWiki.
[Execute workflow]

# anthropic-sdk-python Documentation
*Extracted from DeepWiki on 2025-10-26*

[Formatted content...]

What would you like to know about this repository?
```

**Follow-up:** Answer from cached content, no re-navigation needed.

---

## Workflow

### Checklist

- [ ] Parse repository identifier
- [ ] Navigate to DeepWiki page
- [ ] Wait for page load
- [ ] Extract documentation sections
- [ ] Format as markdown
- [ ] Verify completeness
- [ ] Present results

---

### Step 1: Parse Repository

Extract `owner/repo` using `scripts/parse_github_url.py`:

```bash
python scripts/parse_github_url.py "https://github.com/owner/repo"
# Output: owner/repo
```

**Formats:** Full URLs, SSH, shorthand (`owner/repo`), local repos (`--check-local`)
**Errors:** Invalid → Report to user, stop workflow
**Details:** [reference/url-patterns.md](reference/url-patterns.md)

---

### Step 2: Navigate to DeepWiki

```python
mcp__chrome-devtools__navigate_page(
    url="https://deepwiki.com/{owner}/{repo}"
)
```

**Error:** 404 → Repository not found, stop

---

### Step 3: Wait for Load

```python
mcp__chrome-devtools__wait_for(
    text="Documentation",
    timeout=10000
)
```

**Fail:** Check for "not found", report to user

---

### Step 4: Extract Content

**Take snapshot:**
```python
snapshot = mcp__chrome-devtools__take_snapshot()
```

**Extract with JavaScript:**
```python
extraction_script = """
function extractDocumentation() {
    const main = document.querySelector('main') ||
                  document.querySelector('article') ||
                  document.querySelector('[role="main"]');
    if (!main) return { error: 'No content found' };

    const sections = [];
    let currentSection = null;

    main.querySelectorAll('h1, h2, h3, p, pre, ul, ol').forEach(el => {
        const tag = el.tagName.toLowerCase();
        if (['h1','h2','h3'].includes(tag)) {
            if (currentSection) sections.push(currentSection);
            currentSection = { title: el.textContent.trim(), content: '' };
        } else if (currentSection) {
            if (tag === 'pre') {
                const code = el.querySelector('code');
                const lang = code?.className.match(/language-(\\w+)/)?.[1] || '';
                currentSection.content += '\\n```' + lang + '\\n' +
                    (code ? code.textContent : el.textContent) + '\\n```\\n';
            } else {
                currentSection.content += el.textContent.trim() + '\\n\\n';
            }
        }
    });
    if (currentSection) sections.push(currentSection);
    return { repository: document.title.split('|')[0]?.trim(), sections };
}
return extractDocumentation();
"""

result = mcp__chrome-devtools__evaluate_script(function=extraction_script)
```

**Expected:**
```json
{
  "repository": "repo-name",
  "sections": [
    {"title": "Overview", "content": "..."},
    {"title": "Installation", "content": "```bash...```"}
  ]
}
```

**Details:** [reference/extraction-selectors.md](reference/extraction-selectors.md)

---

### Step 5: Format Markdown

```bash
cat > /tmp/extracted.json << 'EOF'
{"repository": "...", "owner_repo": "owner/repo", "sections": [...]}
EOF

python scripts/format_markdown.py --add-toc /tmp/extracted.json
```

**Output:** Markdown with TOC, clean headings, code blocks

---

### Step 6: Verify

**Checks:**
- Content length > 1000 chars
- At least 2 sections
- Has overview/install/usage keywords
- Code blocks closed (even ``` count)

**Fail:** Report warnings, present partial results

---

### Step 7: Present

```markdown
I've extracted documentation for {owner/repo}.

{formatted_content}

**Summary:** {count} sections, {words} words
Source: https://deepwiki.com/{owner}/{repo}

What would you like to know?
```

**Follow-ups:** Answer from cache, don't re-navigate

---

## Error Handling

### Repository Not Found
- **Symptom:** 404 or "not found" message
- **Action:** Report to user, suggest checking URL, stop

### Page Load Timeout
- **Symptom:** `wait_for` times out
- **Action:** Try extended wait (15s), report if fails, stop

### Empty Extraction
- **Symptom:** No sections or <100 chars
- **Action:** Check snapshot, try alternative selectors, report failure

### Invalid URL
- **Symptom:** Parse error
- **Action:** Report supported formats, stop

### Malformed Output
- **Symptom:** Broken markdown
- **Action:** `format_markdown.py` auto-fixes, report warnings

---

## Examples

**Example 1: Standard Extraction**
```
User: Extract docs for pydantic/pydantic
✓ Parse: pydantic/pydantic
✓ Navigate: https://deepwiki.com/pydantic/pydantic
✓ Extract: 8 sections
✓ Present formatted docs
```

**Example 2: Follow-up**
```
User: [After extraction] How do I add middleware?
✓ Search cached docs for "middleware"
✓ Answer from extracted content
✗ Don't re-navigate
```

**Example 3: Not Found**
```
User: Extract docs for fake/repo-123
✓ Parse: fake/repo-123
✓ Navigate
✗ 404: Repository not found
✓ Report error with alternatives
```

---

## Best Practices

**Efficiency:**
- Extract once, answer many questions
- Single comprehensive JavaScript extraction
- Cache aggressively for follow-ups

**Validation:**
- Check page load before extracting
- Verify content length early
- Report issues immediately

**Communication:**
```
During: "Extracting documentation from DeepWiki..."
Success: "Extracted {count} sections. What would you like to know?"
Partial: "Extracted content with warnings: {warnings}..."
Failure: "Error: {specific issue}. Alternatives: {suggestions}"
```

---

## Reference

### Scripts

**parse_github_url.py**
```bash
python scripts/parse_github_url.py "url_or_shorthand"
# --check-local for local repos
# Exit 0: success, 1: error
```

**format_markdown.py**
```bash
python scripts/format_markdown.py input.json
# --add-toc: Generate table of contents
# --stdin: Read from stdin
# Exit 0: success, 1: error
```

### Reference Files

- **[url-patterns.md](reference/url-patterns.md)** - All GitHub URL formats, parsing patterns, edge cases
- **[extraction-selectors.md](reference/extraction-selectors.md)** - CSS/XPath selectors, extraction strategies, validation

### MCP Tools

- `mcp__chrome-devtools__navigate_page` - Navigate to URL
- `mcp__chrome-devtools__wait_for` - Wait for content
- `mcp__chrome-devtools__take_snapshot` - Get page structure
- `mcp__chrome-devtools__evaluate_script` - Extract with JavaScript

---

## Troubleshooting

**No Content Extracted**
1. Check snapshot for page structure
2. Adjust selectors (see extraction-selectors.md)
3. Try alternative extraction (full text)
4. Report failure with alternatives

**Formatting Issues**
1. `format_markdown.py` auto-fixes most issues
2. Check code block closure
3. Verify heading hierarchy
4. Review cleaning functions

**Performance Problems**
1. Use single comprehensive extraction
2. Cache for follow-ups
3. Avoid incremental extraction

---

## Limitations

**NOT Supported:**
- Private repositories (DeepWiki public only)
- Other Git hosts (GitLab, Bitbucket)
- Source code extraction (docs only)
- Real-time updates (snapshot-based)
- Interactive documentation elements

**Alternatives:**
- Private: GitHub API or local clone
- Other hosts: Visit directly
- Source: GitHub clone/API
- Updates: Re-extract when needed
- Interactive: Manual browser visit

---

## Success Criteria

**Successful When:**
- ✓ Repository parsed correctly
- ✓ DeepWiki loads without errors
- ✓ 2+ sections extracted
- ✓ Content > 1000 chars
- ✓ Valid markdown syntax
- ✓ Code blocks closed, headings hierarchical
- ✓ Follow-ups answerable from cache

**Failed When:**
- ✗ Repository not found (404)
- ✗ Page load timeout
- ✗ No content (<100 chars)

---

## Summary

**Purpose:** Automated DeepWiki documentation extraction with browser automation

**Workflow:** Parse → Navigate → Extract → Format → Verify → Present

**Key Features:**
- Multiple GitHub URL format support
- Comprehensive content extraction
- Clean markdown formatting
- Validation and error handling
- Follow-up Q&A from cache

**Files:**
- `SKILL.md` - This guide
- `scripts/parse_github_url.py` - URL parsing
- `scripts/format_markdown.py` - Markdown formatting
- `reference/url-patterns.md` - URL reference
- `reference/extraction-selectors.md` - Extraction guide

**Next Steps:**
- Answer questions from cached docs
- Reference specific sections
- Re-extract only for new repositories
