# DeepWiki Content Extraction Guide

Reference for extracting documentation from DeepWiki pages using Chrome DevTools MCP.

## Table of Contents
- [Page Structure Overview](#page-structure-overview)
- [Extraction Strategy](#extraction-strategy)
- [Common Selectors](#common-selectors)
- [Content Types](#content-types)
- [JavaScript Extraction](#javascript-extraction)
- [Validation Checks](#validation-checks)

---

## Page Structure Overview

### Typical DeepWiki Layout

DeepWiki generates documentation pages from GitHub repositories with common patterns:

**Expected Structure:**
```
<body>
  <header> (navigation, repo name)
  <main> or <article> (primary content)
    <section> or <div class="section">
      <h1>, <h2>, <h3> (section headings)
      <p> (paragraphs)
      <pre><code> (code blocks)
      <ul>, <ol> (lists)
      <table> (tables)
    </section>
  </main>
  <footer> (metadata, links)
</body>
```

**Key Identifiers:**
- Main content container: `main`, `article`, `.content`, `.documentation`
- Section containers: `section`, `.section`, `.doc-section`
- Headings: `h1`, `h2`, `h3`, `h4` (hierarchical structure)
- Code blocks: `pre code`, `.highlight`, `.code-block`
- Navigation elements: `nav`, `.sidebar`, `.toc` (to exclude)

---

## Extraction Strategy

### Step-by-Step Approach

**1. Initial Page Snapshot**
```python
# Use Chrome DevTools MCP to get page structure
snapshot = mcp__chrome-devtools__take_snapshot()
```

This provides the accessibility tree with UIDs for each element.

**2. Identify Main Content Container**

Look for primary content area (exclude navigation, sidebar, footer):

**Candidate Selectors (in priority order):**
- `main`
- `article`
- `[role="main"]`
- `.content`
- `.documentation`
- `.markdown-body` (GitHub-style)

**3. Extract Section Structure**

Within main content, identify sections by headings:

**Approach:**
- Find all `h1`, `h2`, `h3` elements
- Extract heading text as section titles
- Capture content between consecutive headings
- Group by heading hierarchy

**4. Capture Content Per Section**

For each section:
- **Heading:** Section title
- **Content:** All elements until next heading of same/higher level
- **Preserve formatting:** Code blocks, lists, tables

---

## Common Selectors

### Content Container Selectors

**Primary content (try in order):**
```
main
article
[role="main"]
.content
.documentation
.doc-content
.markdown-body
#content
```

**Exclude from extraction:**
```
nav
.sidebar
.toc
.navigation
header
footer
.breadcrumb
.page-nav
```

### Section Selectors

**Section headings:**
```
main h1
main h2
main h3
article h1
article h2
article h3
```

**Section containers (if explicitly wrapped):**
```
section
.section
.doc-section
.content-section
```

### Content Element Selectors

**Paragraphs:**
```
p
.paragraph
```

**Code blocks:**
```
pre code
.highlight
.code-block
.hljs
```

**Lists:**
```
ul
ol
.list
```

**Tables:**
```
table
.table
```

**Blockquotes:**
```
blockquote
.note
.warning
.info
```

---

## Content Types

### 1. Headings

**Extraction:**
```javascript
// Get heading text and level
const heading = {
  level: element.tagName.toLowerCase(), // h1, h2, h3
  text: element.textContent.trim(),
  id: element.id || '' // for anchor links
}
```

**Markdown Format:**
```markdown
# H1 Heading
## H2 Heading
### H3 Heading
```

### 2. Code Blocks

**Extraction:**
```javascript
// Find code blocks with language detection
const codeBlock = {
  language: element.className.match(/language-(\w+)/)?.[1] || '',
  code: element.textContent
}
```

**Markdown Format:**
```markdown
```python
def example():
    return "code"
` ``
```

**Language Detection Patterns:**
- Class: `language-python`, `lang-python`
- Data attribute: `data-lang="python"`
- Auto-detect from content (keywords, syntax)

### 3. Lists

**Extraction:**
```javascript
// Ordered or unordered lists
const list = {
  type: element.tagName.toLowerCase(), // ul or ol
  items: Array.from(element.querySelectorAll('li')).map(li => li.textContent.trim())
}
```

**Markdown Format:**
```markdown
- Unordered item 1
- Unordered item 2

1. Ordered item 1
2. Ordered item 2
```

### 4. Tables

**Extraction:**
```javascript
// Extract table structure
const table = {
  headers: Array.from(element.querySelectorAll('th')).map(th => th.textContent.trim()),
  rows: Array.from(element.querySelectorAll('tbody tr')).map(tr =>
    Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim())
  )
}
```

**Markdown Format:**
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### 5. Links

**Preservation:**
```markdown
[Link Text](https://url.com)
```

**Internal Links:**
- Convert to section anchors if possible
- Example: `#installation` → `[Installation](#installation)`

---

## JavaScript Extraction

### Comprehensive Content Extraction

**Use `evaluate_script` for complex extraction:**

```javascript
// Extract all sections with content
function extractDocumentation() {
  // Find main content container
  const main = document.querySelector('main') ||
                document.querySelector('article') ||
                document.querySelector('[role="main"]') ||
                document.querySelector('.content');

  if (!main) return { error: 'No main content found' };

  const sections = [];
  let currentSection = null;

  // Traverse all child nodes
  main.querySelectorAll('h1, h2, h3, h4, p, pre, ul, ol, table, blockquote').forEach(el => {
    const tagName = el.tagName.toLowerCase();

    // New section on heading
    if (['h1', 'h2', 'h3', 'h4'].includes(tagName)) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = {
        title: el.textContent.trim(),
        level: tagName,
        content: []
      };
    } else if (currentSection) {
      // Add content to current section
      if (tagName === 'pre') {
        const code = el.querySelector('code');
        const language = code?.className.match(/language-(\w+)/)?.[1] || '';
        currentSection.content.push({
          type: 'code',
          language: language,
          text: code ? code.textContent : el.textContent
        });
      } else if (tagName === 'ul' || tagName === 'ol') {
        currentSection.content.push({
          type: 'list',
          ordered: tagName === 'ol',
          items: Array.from(el.querySelectorAll('li')).map(li => li.textContent.trim())
        });
      } else {
        currentSection.content.push({
          type: 'text',
          text: el.textContent.trim()
        });
      }
    }
  });

  // Push last section
  if (currentSection) {
    sections.push(currentSection);
  }

  return {
    repository: document.title.split('|')[0]?.trim() || 'Unknown',
    sections: sections
  };
}

return extractDocumentation();
```

**This returns structured JSON suitable for `format_markdown.py`**

---

## Validation Checks

### Post-Extraction Verification

**1. Content Length Check**
```python
total_content = sum(len(section['content']) for section in sections)
if total_content < 1000:
    # Warning: Suspiciously short documentation
    # May indicate extraction failure
```

**2. Required Sections**

Most repositories should have:
- Overview/Introduction/About
- Installation/Setup/Getting Started
- Usage/Examples/Quick Start

**Validation:**
```python
section_titles = [s['title'].lower() for s in sections]
required_keywords = ['overview', 'install', 'usage', 'introduction', 'getting started']

found = any(keyword in title for title in section_titles for keyword in required_keywords)
if not found:
    # Warning: May be missing key sections
```

**3. Code Block Verification**

Check code blocks are properly closed:
```python
content_text = '\n'.join(section['content'] for section in sections)
open_blocks = content_text.count('```')

if open_blocks % 2 != 0:
    # Error: Unclosed code block detected
```

**4. Heading Hierarchy**

Ensure logical heading progression:
```python
prev_level = 0
for section in sections:
    level = int(section['level'][1])  # h1 -> 1, h2 -> 2
    if level > prev_level + 1:
        # Warning: Heading hierarchy skip (h1 to h3)
    prev_level = level
```

---

## Error Handling

### Common Issues and Solutions

**Issue: Page not fully loaded**
- **Symptom:** Empty content or only navigation
- **Solution:** Use `wait_for` with content indicator
  ```python
  mcp__chrome-devtools__wait_for(text="Overview")
  mcp__chrome-devtools__wait_for(text="Documentation")
  ```

**Issue: Dynamic content (JavaScript-rendered)**
- **Symptom:** Snapshot shows loading state
- **Solution:** Wait longer or look for specific content
  ```python
  mcp__chrome-devtools__wait_for(text="Installation")
  # Then take snapshot
  ```

**Issue: Navigation elements included**
- **Symptom:** TOC or sidebar in extracted content
- **Solution:** More specific main content selector
  ```python
  # Be explicit about main content area
  main = document.querySelector('main article')
  # Not just document.body
  ```

**Issue: Missing sections**
- **Symptom:** Known sections not captured
- **Solution:** Check for alternative heading levels or containers
  ```python
  # Try multiple heading levels
  headings = main.querySelectorAll('h1, h2, h3, h4, h5, h6')
  ```

**Issue: Malformed markdown output**
- **Symptom:** Broken code blocks, lists
- **Solution:** Use `format_markdown.py` cleaning functions
  - `fix_code_blocks()` - Close unclosed blocks
  - `clean_text()` - Remove artifacts
  - `normalize_headings()` - Fix hierarchy

---

## Adaptive Extraction

### Handling Page Variations

DeepWiki page structure may vary by repository. Use this fallback sequence:

**1. Primary Strategy: Structured Extraction**
- Identify main content container
- Extract by heading hierarchy
- Preserve formatting

**2. Fallback Strategy: Whole Content**
- If structure unclear, extract all text from main
- Use `innerText` or `textContent`
- Post-process with `format_markdown.py`

**3. Alternative Strategy: Screenshot + OCR**
- Last resort if programmatic extraction fails
- Use `take_screenshot` for visual documentation
- Not ideal but better than nothing

**Implementation:**
```python
# Try structured extraction
try:
    data = evaluate_script(structured_extraction_function)
    if data and len(data['sections']) > 0:
        return data
except:
    pass

# Fallback: whole content
try:
    main = find_main_content()
    text = main.textContent
    return simple_parse(text)
except:
    pass

# Last resort: screenshot
screenshot = take_screenshot(fullPage=True)
return {"note": "Extraction failed, screenshot saved", "screenshot": screenshot}
```

---

## Performance Optimization

### Efficient Extraction

**Single JavaScript Call:**
Instead of multiple tool calls, extract everything in one `evaluate_script`:
- ✓ One JavaScript execution
- ✓ Returns complete JSON structure
- ✓ Minimal MCP tool calls
- ✗ Avoid iterative extraction (slow)

**Batch Processing:**
```python
# Good: Single comprehensive extraction
data = evaluate_script(extract_all_function)

# Bad: Multiple incremental extractions
title = evaluate_script(get_title)
section1 = evaluate_script(get_section1)
section2 = evaluate_script(get_section2)
```

---

## Example Output Format

### Target JSON Structure

```json
{
  "repository": "anthropic-sdk-python",
  "owner_repo": "anthropics/anthropic-sdk-python",
  "extracted_at": "2025-10-26T17:45:00Z",
  "sections": [
    {
      "title": "Overview",
      "level": "h2",
      "content": [
        {
          "type": "text",
          "text": "The Anthropic Python SDK provides convenient access to the Anthropic API..."
        },
        {
          "type": "code",
          "language": "python",
          "text": "from anthropic import Anthropic\n\nclient = Anthropic()"
        }
      ]
    },
    {
      "title": "Installation",
      "level": "h2",
      "content": [
        {
          "type": "text",
          "text": "Install using pip:"
        },
        {
          "type": "code",
          "language": "bash",
          "text": "pip install anthropic"
        }
      ]
    }
  ]
}
```

**This format is compatible with `format_markdown.py` for final output.**

---

## Summary

**Extraction Workflow:**
1. Navigate to DeepWiki page
2. Wait for content load
3. Take snapshot to understand structure
4. Use `evaluate_script` with comprehensive extraction function
5. Validate extracted data (length, sections, formatting)
6. Pass to `format_markdown.py` for final output

**Key Principles:**
- Prefer single comprehensive extraction over incremental
- Validate extraction quality before proceeding
- Handle missing sections gracefully
- Clean and format content for readability
- Provide fallback strategies for edge cases
