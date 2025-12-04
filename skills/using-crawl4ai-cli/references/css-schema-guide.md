# CSS Schema Guide

Complete guide to creating CSS extraction schemas for crawl4ai CLI.

## Schema Structure

```json
{
  "name": "ExtractorName",
  "baseSelector": ".container-class",
  "fields": [
    {
      "name": "field_name",
      "selector": ".element-selector",
      "type": "text"
    }
  ]
}
```

### Required Fields

- `name` (string) - Schema identifier
- `baseSelector` (string) - CSS selector for repeating container elements
- `fields` (array) - Array of field definitions

### Field Definition

Each field must have:
- `name` (string) - Field identifier (used in JSON output)
- `selector` (string) - CSS selector relative to baseSelector
- `type` (string) - Extraction type: `"text"`, `"html"`, or `"attribute"`
- `attribute` (string) - Required when type is `"attribute"`

## Field Types

### text

Extract text content only (no HTML tags).

```json
{
  "name": "title",
  "selector": "h2.article-title",
  "type": "text"
}
```

**Result:** `"Breaking News: Tech Advances"`

### html

Extract HTML markup.

```json
{
  "name": "content",
  "selector": ".article-body",
  "type": "html"
}
```

**Result:** `"<p>First paragraph...</p><p>Second...</p>"`

### attribute

Extract attribute value from element.

```json
{
  "name": "link",
  "selector": "a.read-more",
  "type": "attribute",
  "attribute": "href"
}
```

**Result:** `"https://example.com/article"`

**Common attributes:**
- `href` - Links
- `src` - Images, scripts
- `data-id` - Custom data attributes
- `title` - Tooltips
- `alt` - Image descriptions
- `class` - CSS classes
- `id` - Element IDs

## CSS Selector Syntax

### Basic Selectors

| Selector | Matches | Example |
|----------|---------|---------|
| `.class` | Elements with class | `.article-card` |
| `#id` | Element with ID | `#main-content` |
| `tag` | HTML tag | `h1`, `p`, `div` |
| `*` | All elements | `*` |

### Combinators

| Combinator | Matches | Example |
|------------|---------|---------|
| `A B` | B inside A | `div p` (p inside div) |
| `A > B` | B direct child of A | `ul > li` |
| `A + B` | B immediately after A | `h2 + p` |
| `A ~ B` | B sibling after A | `h2 ~ p` |

### Attribute Selectors

| Selector | Matches | Example |
|----------|---------|---------|
| `[attr]` | Has attribute | `[data-id]` |
| `[attr=val]` | Exact value | `[type="submit"]` |
| `[attr*=val]` | Contains value | `[class*="card"]` |
| `[attr^=val]` | Starts with | `[href^="https"]` |
| `[attr$=val]` | Ends with | `[src$=".jpg"]` |

### Pseudo-classes

| Selector | Matches | Example |
|----------|---------|---------|
| `:first-child` | First child | `li:first-child` |
| `:last-child` | Last child | `li:last-child` |
| `:nth-child(n)` | Nth child | `li:nth-child(2)` |
| `:not(selector)` | Not matching | `p:not(.exclude)` |

## Complete Examples

### News Articles

```json
{
  "name": "NewsArticles",
  "baseSelector": "article.post",
  "fields": [
    {
      "name": "title",
      "selector": "h2.post-title a",
      "type": "text"
    },
    {
      "name": "url",
      "selector": "h2.post-title a",
      "type": "attribute",
      "attribute": "href"
    },
    {
      "name": "author",
      "selector": ".author-name",
      "type": "text"
    },
    {
      "name": "date",
      "selector": "time",
      "type": "attribute",
      "attribute": "datetime"
    },
    {
      "name": "excerpt",
      "selector": ".post-excerpt",
      "type": "text"
    },
    {
      "name": "image",
      "selector": "img.post-thumbnail",
      "type": "attribute",
      "attribute": "src"
    }
  ]
}
```

### Product Listings

```json
{
  "name": "Products",
  "baseSelector": ".product-card",
  "fields": [
    {
      "name": "name",
      "selector": "h3.product-name",
      "type": "text"
    },
    {
      "name": "price",
      "selector": ".price-current",
      "type": "text"
    },
    {
      "name": "original_price",
      "selector": ".price-original",
      "type": "text"
    },
    {
      "name": "rating",
      "selector": "[data-rating]",
      "type": "attribute",
      "attribute": "data-rating"
    },
    {
      "name": "image_url",
      "selector": "img.product-image",
      "type": "attribute",
      "attribute": "src"
    },
    {
      "name": "link",
      "selector": "a.product-link",
      "type": "attribute",
      "attribute": "href"
    },
    {
      "name": "in_stock",
      "selector": ".stock-status",
      "type": "text"
    }
  ]
}
```

### Research Papers

```json
{
  "name": "Papers",
  "baseSelector": "dd",
  "fields": [
    {
      "name": "title",
      "selector": ".list-title",
      "type": "text"
    },
    {
      "name": "authors",
      "selector": ".list-authors",
      "type": "text"
    },
    {
      "name": "abstract",
      "selector": ".abstract-full",
      "type": "text"
    },
    {
      "name": "subjects",
      "selector": ".list-subjects",
      "type": "text"
    },
    {
      "name": "paper_url",
      "selector": "a[href*='/abs/']",
      "type": "attribute",
      "attribute": "href"
    }
  ]
}
```

## Best Practices

### Selector Specificity

**Too general (avoid):**
```json
{"selector": "div"}  // Matches too many elements
```

**Too specific (avoid):**
```json
{"selector": "body > div.container > div.row > div.col > article > h2"}  // Brittle
```

**Just right:**
```json
{"selector": "article h2"}  // Specific enough, flexible
{"selector": ".article-title"}  // Best if class exists
```

### Testing Selectors

Use browser DevTools Console:

```javascript
// Test if selector matches elements
document.querySelectorAll('.article-card')

// Test what a selector returns
document.querySelector('.article-card h2').textContent

// Test attribute extraction
document.querySelector('a').getAttribute('href')
```

### Common Mistakes

**❌ Wrong:**
```json
{
  "name": "link",
  "selector": "a",
  "type": "text"  // Gets link text, not URL
}
```

**✓ Correct:**
```json
{
  "name": "link",
  "selector": "a",
  "type": "attribute",
  "attribute": "href"  // Gets actual URL
}
```

**❌ Wrong:**
```json
{
  "baseSelector": ".article-card h2"  // Too specific
}
```

**✓ Correct:**
```json
{
  "baseSelector": ".article-card"  // Container only
}
```

### Handling Missing Elements

If selector doesn't match, crawl4ai returns:
- `null` for single elements
- Empty string for text fields
- Empty array for multiple matches

**Design schemas to handle this:**
- Use optional fields for elements that may not exist
- Test schemas on multiple pages
- Check extraction results for null values

## XPath Alternative

While crawl4ai CLI focuses on CSS selectors, XPath can also be used in schema selectors:

```json
{
  "name": "title",
  "selector": "//h2[@class='title']",
  "type": "text"
}
```

**When to use XPath:**
- Complex parent/sibling navigation
- Text content matching
- Position-based selection

**When to use CSS:**
- Simple class/ID selection (faster)
- Standard HTML structure
- Better readability

## Debugging Failed Extractions

1. **Verify baseSelector matches containers:**
   ```bash
   crwl URL -c "css_selector=.article-card" -o markdown
   ```

2. **Check HTML structure:**
   ```bash
   crwl URL -o all | jq -r '.html' > debug.html
   # Open debug.html and inspect elements
   ```

3. **Test individual field selectors:**
   - Remove all fields except one
   - Test if that field extracts correctly
   - Add fields back one at a time

4. **Enable verbose mode:**
   ```bash
   crwl URL -e extract_css.yml -s schema.json -v -o json
   ```

## Schema Generation

**Generate interactively:**
```bash
python scripts/generate_schema.py
```

**Minimal template:**
```json
{
  "name": "Minimal",
  "baseSelector": ".item",
  "fields": [
    {
      "name": "text",
      "selector": ".content",
      "type": "text"
    }
  ]
}
```
