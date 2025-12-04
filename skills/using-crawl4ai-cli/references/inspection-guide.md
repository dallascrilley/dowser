# Chrome MCP Page Inspection Guide

Complete workflow for visual page inspection before scraping.

## Why Visual Inspection is Mandatory

Prevents these common failures:
- Scraping navigation links instead of articles
- Missing dynamic content (infinite scroll, lazy loading)
- Wrong selectors (too broad or too specific)
- Empty fields from incorrect element targeting

## Inspection Workflow

### Step 1: Navigate and Capture

Use Chrome MCP tools to navigate and capture page structure:

```bash
# Tool: mcp__plugin_superpowers-chrome_chrome__use_browser
# Actions:
1. action: "navigate", payload: "https://target-site.com"
2. action: "screenshot", payload: "page_layout.png"
3. action: "extract", selector: "body", payload: "markdown"
   # This auto-saves to page.md
```

### Step 2: Identify Page Sections

Review screenshot and page.md to identify:

**Navigation sections** (EXCLUDE from scraping):
- Header: `header`, `#header`, `.site-header`
- Sidebar: `aside`, `.sidebar`, `#sidebar`
- Footer: `footer`, `.site-footer`
- Menu: `nav`, `.menu`, `.navigation`

**Content sections** (TARGET for scraping):
- Articles: `article`, `.post`, `.article-card`
- Main content: `main`, `#main`, `.content-area`
- List items: `.item`, `.entry`, `[class*='post']`

**Dynamic content indicators**:
- Infinite scroll: Look for "Load More" buttons or scroll triggers
- Lazy loading: Images with `data-src` instead of `src`
- AJAX content: Spinners, "Loading..." placeholders

### Step 3: Test Selectors

Use Chrome MCP to test selectors before creating schema:

```bash
# Test base selector (should match article containers)
action: "extract"
selector: "article"  # or .post, .article-card, etc.
payload: "html"

# Count matches (should match expected number of articles)
# If you see 20 articles visually, selector should return ~20 elements

# Test field selectors within base
action: "extract"
selector: "article h1"  # Title selector
payload: "text"
```

### Step 4: Document Findings

Create selector map:

```json
{
  "site": "https://example.com",
  "inspected_date": "2025-11-07",
  "selectors": {
    "base": "article.post-card",
    "title": "h2.post-title",
    "content": ".post-excerpt",
    "date": "time[datetime]",
    "author": ".author-name"
  },
  "exclusions": {
    "navigation": "header, nav, footer, aside",
    "ads": ".advertisement, .sponsored"
  },
  "dynamic_content": {
    "infinite_scroll": true,
    "lazy_images": true
  }
}
```

## Common Inspection Issues

### Issue: Page requires authentication

**Solution**: Use Chrome MCP to log in first:

```bash
1. Navigate to login page
2. action: "type", selector: "#username", text: "user"
3. action: "type", selector: "#password", text: "pass"
4. action: "click", selector: "button[type=submit]"
5. action: "wait_for", selector: ".logged-in"
6. Then inspect authenticated pages
```

### Issue: Dynamic content not loaded

**Solution**: Wait for content before inspection:

```bash
action: "wait_for"
selector: ".article-container"
timeout: 10000  # 10 seconds

# Or wait for network idle
action: "wait_for"
type: "networkidle"
```

### Issue: Cannot identify correct selectors

**Solution**: Use browser DevTools:

1. Right-click element → Inspect
2. Note the selector shown in DevTools
3. Test in console: `document.querySelectorAll("YOUR_SELECTOR")`
4. Verify count matches visible elements
5. Use more specific selectors if too many matches

## Selector Best Practices

### Base Selector Priority

1. **Semantic HTML** (best): `article`, `main`, `section`
2. **Specific classes** (good): `.article-card`, `.post-item`
3. **Generic containers** (last resort): `.content`, `#main`

### Field Selector Tips

- **Titles**: Usually `h1`, `h2`, or `.title`
- **Content**: Usually `.content`, `.body`, `.text`
- **Dates**: Look for `time`, `.date`, `[datetime]`
- **Authors**: Usually `.author`, `.byline`, `[rel=author]`

### Avoid These Selectors

- ❌ `body` (too broad - gets everything including nav)
- ❌ `div` (too generic - unreliable)
- ❌ `div > div > div` (fragile - breaks when layout changes)
- ❌ `.hidden`, `[style*='display:none']` (no visible content)

## Next Steps After Inspection

1. **Create schema.json** with documented selectors
2. **Test extraction** on sample page
3. **Validate output** with `scripts/validate_extraction.py`
4. **Iterate** if validation fails

See [CSS Schema Guide](css-schema-guide.md) for schema creation details.

