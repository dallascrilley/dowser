# Troubleshooting Guide

Solutions to common crawl4ai CLI issues.

## Empty Extraction Results

**Symptom:** Schema returns `[]` or empty JSON

**Diagnosis:**
```bash
# Step 1: Check if baseSelector matches
crwl URL -c "css_selector=.your-base-selector" -o markdown

# Step 2: View raw HTML
crwl URL -o all | jq -r '.html' > debug.html
# Open debug.html in browser and inspect elements

# Step 3: Test with verbose mode
crwl URL -e extract_css.yml -s schema.json -v -o json
```

**Solutions:**

1. **Wrong CSS selector**
   ```bash
   # Test selector in browser DevTools console:
   document.querySelectorAll('.your-selector')
   ```

2. **Content loads via JavaScript**
   ```bash
   crwl URL \
       -c "delay_before_return_html=3,wait_until=networkidle" \
       -e extract_css.yml -s schema.json -o json
   ```

3. **Content in iframe**
   ```bash
   crwl URL -c "process_iframes=true" -e extract_css.yml -s schema.json -o json
   ```

4. **Selector too specific**
   ```json
   // ❌ Too specific
   {"selector": "body > div > div > h2"}

   // ✓ Better
   {"selector": "h2.title"}
   ```

## Page Timeout Exceeded

**Symptom:** `Error: Page timeout exceeded`

**Solutions:**

1. **Increase timeout**
   ```bash
   crwl URL -c "page_timeout=90000"  # 90 seconds
   ```

2. **Disable full page scan**
   ```bash
   crwl URL -c "scan_full_page=false,page_timeout=30000"
   ```

3. **Target specific section**
   ```bash
   crwl URL -c "css_selector=#main-content,page_timeout=30000"
   ```

4. **Change wait condition**
   ```bash
   crwl URL -c "wait_until=load,page_timeout=30000"  # Don't wait for all network activity
   ```

**If site is truly slow:**
```yaml
# crawler_slow_site.yml
page_timeout: 120000
wait_until: "load"
scan_full_page: false
delay_before_return_html: 5.0
```

## LLM Provider Not Configured

**Symptom:** `Error: LLM provider not configured`

**Solution:**

```bash
# Option 1: Run any Q&A command (triggers setup wizard)
crwl https://example.com -q "test"

# Option 2: Manually create config
mkdir -p ~/.crawl4ai
cat > ~/.crawl4ai/global.yml << 'EOF'
default_provider: "openai/gpt-4"
api_token: "sk-your-api-key-here"
EOF

# Option 3: Use Ollama (no API key needed)
cat > ~/.crawl4ai/global.yml << 'EOF'
default_provider: "ollama/llama2"
EOF
```

**Verify configuration:**
```bash
cat ~/.crawl4ai/global.yml
```

## No Content or Filtered Out

**Symptom:** `Warning: No content extracted or filtered out`

**Solutions:**

1. **Lower word count threshold**
   ```bash
   crwl URL -c "word_count_threshold=10" -o markdown
   ```

2. **Disable filtering temporarily**
   ```bash
   crwl URL -o markdown  # No filter
   ```

3. **Adjust filter threshold**
   ```yaml
   # filter.yml
   type: "bm25"
   query: "your keywords"
   threshold: 0.5  # Lower threshold = more permissive
   ```

4. **Check if content is JavaScript-rendered**
   ```bash
   crwl URL -c "delay_before_return_html=2" -o markdown
   ```

## Invalid JSON Schema Format

**Symptom:** `Error: Invalid JSON schema format`

**Diagnosis:**
```bash
# Validate JSON syntax
jq '.' schema.json

# Check for errors
python scripts/validate_config.py schema.json
```

**Common mistakes:**

1. **Trailing commas**
   ```json
   // ❌ Wrong
   {
     "name": "test",
     "fields": [],  // ← Remove this comma
   }

   // ✓ Correct
   {
     "name": "test",
     "fields": []
   }
   ```

2. **Missing attribute field**
   ```json
   // ❌ Wrong
   {
     "type": "attribute",
     "selector": "a"
     // Missing: "attribute": "href"
   }

   // ✓ Correct
   {
     "type": "attribute",
     "selector": "a",
     "attribute": "href"
   }
   ```

3. **Wrong field type**
   ```json
   // ❌ Wrong
   {"type": "link"}  // Not a valid type

   // ✓ Correct
   {"type": "attribute", "attribute": "href"}
   ```

## Content Behind Modal/Overlay

**Symptom:** Main content not extracted, only modal text

**Solution:**
```bash
crwl URL -c "remove_overlay_elements=true,delay_before_return_html=1" -o markdown
```

**Or in config:**
```yaml
# crawler.yml
remove_overlay_elements: true
delay_before_return_html: 1.0
```

## Incomplete Infinite Scroll

**Symptom:** Not all items extracted from infinite scroll page

**Solutions:**

1. **Increase scroll delay**
   ```bash
   crwl URL -c "scan_full_page=true,scroll_delay=1.0,page_timeout=90000"
   ```

2. **Add extra wait time**
   ```yaml
   # crawler_infinite.yml
   scan_full_page: true
   scroll_delay: 1.0
   delay_before_return_html: 3.0
   page_timeout: 120000
   wait_until: "networkidle"
   ```

## Rate Limiting / Blocked by Site

**Symptom:** `403 Forbidden` or empty responses after multiple requests

**Solutions:**

1. **Add delays between requests**
   ```bash
   #!/bin/bash
   for url in "${urls[@]}"; do
       crwl "$url" -o json > "output.json"
       sleep 5  # Wait 5 seconds
   done
   ```

2. **Use random user agent**
   ```bash
   crwl URL -b "user_agent_mode=random" -o markdown
   ```

3. **Slow down crawling**
   ```yaml
   # browser.yml
   user_agent_mode: "random"

   # crawler.yml
   delay_before_return_html: 2.0
   ```

## JSON Output Not Valid

**Symptom:** Output contains error messages or mixed content

**Diagnosis:**
```bash
# Validate JSON
crwl URL -e extract_css.yml -s schema.json -o json | jq '.'
```

**Solutions:**

1. **Redirect stderr**
   ```bash
   crwl URL -e extract_css.yml -s schema.json -o json 2>/dev/null | jq '.'
   ```

2. **Use non-verbose mode**
   ```yaml
   # extract_css.yml
   type: "json-css"
   params:
     verbose: false  # Disable debug output
   ```

## Debugging Checklist

When extraction fails:

- [ ] Test baseSelector matches elements: `crwl URL -c "css_selector=.base" -o markdown`
- [ ] View raw HTML: `crwl URL -o all | jq -r '.html' > debug.html`
- [ ] Test selectors in browser DevTools
- [ ] Enable verbose mode: `-v`
- [ ] Check for JavaScript content: increase `delay_before_return_html`
- [ ] Validate schema: `python scripts/validate_config.py schema.json`
- [ ] Start with minimal schema (one field)
- [ ] Check if content needs authentication
- [ ] Verify site allows scraping (robots.txt, terms of service)

## Getting Help

1. **Check configuration**
   ```bash
   python scripts/validate_config.py schema.json extract_css.yml crawler.yml
   ```

2. **View verbose output**
   ```bash
   crwl URL -e extract_css.yml -s schema.json -v -o json
   ```

3. **Test incrementally**
   - Start with basic `crwl URL -o markdown`
   - Add configs one at a time
   - Test each change

4. **Review documentation**
   - [CLI Reference](cli-reference.md)
   - [Config Reference](config-reference.md)
   - [CSS Schema Guide](css-schema-guide.md)
   - [Patterns](patterns.md)

## Chrome MCP Inspection Issues

### Cannot navigate to page or page.md empty

**Cause:** Chrome MCP not configured or page requires authentication

**Solutions:**

1. **Verify Chrome MCP is available**
   ```bash
   # Check that mcp__plugin_superpowers-chrome_chrome__use_browser tool is accessible
   ```

2. **For authenticated pages**
   - Navigate with Chrome MCP
   - Use action: "type" to fill login forms
   - Use action: "click" to submit
   - Then inspect the authenticated page

3. **For JavaScript-heavy pages**
   - Use action: "await_element" to wait for content to load
   - Increase timeout if needed: `timeout: 10000` (10 seconds)

**Example: Inspect dynamic page**
```bash
# 1. Navigate: action="navigate", payload="https://example.com"
# 2. Wait: action="await_element", selector=".article-container", timeout=5000
# 3. Screenshot: action="screenshot", payload="page_layout.png"
# 4. Extract: action="extract", selector="body", payload="markdown"
```

## Output Validation Failures

### Extracted navigation links instead of content

**Symptom:** Titles like "Home", "Menu", "Contact Us" in output

**Solution:** Refine baseSelector to target content area only

```json
// ❌ Bad
{
  "baseSelector": "body"
}

// ✓ Good
{
  "baseSelector": ".article-content"  // or #main, or article
}
```

**Automated check:**
```bash
python scripts/validate_extraction.py data.json
# Will flag navigation contamination automatically
```

### Empty fields in extraction

**Symptom:** `jq` shows `""` or `null` for content fields

**Solutions:**

1. **Verify selector in Chrome MCP**
   ```bash
   # Use action="extract", selector="YOUR_SELECTOR", payload="text"
   # to test if selector returns content
   ```

2. **Check selector specificity**
   ```bash
   # Selector might be too specific or misspelled
   # Test variations: ".class", "#id", "tag.class", "tag#id"
   ```

3. **Wait for dynamic content**
   ```bash
   crwl URL -c "delay_before_return_html=2.0" -e extract_css.yml -s schema.json -o json
   ```

### Wrong number of records extracted

**Symptom:** Expected 20 articles, got 2 or 200

**Solutions:**

1. **Verify baseSelector targets correct level**
   ```text
   Too broad:    body (gets everything)
   Too specific: .article-content .inner .text (misses articles)
   Just right:   .article-card (gets each article)
   ```

2. **Check for pagination**
   ```bash
   # If only getting first page, handle pagination:
   crwl URL -c "scan_full_page=true,scroll_delay=0.5" -e extract_css.yml -s schema.json -o json
   ```

3. **Use Chrome MCP to count expected elements**
   ```bash
   # action="extract", selector="YOUR_BASE_SELECTOR", payload="html"
   # Count how many matches you see in the output
   ```

**Automated validation:**
```bash
python scripts/validate_extraction.py data.json --min-records=10 --required-fields=title,content
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `File not found` | Config file path wrong | Use absolute paths or check working directory |
| `Invalid YAML` | Syntax error in YAML | Check indentation, colons, quotes |
| `Invalid JSON` | Syntax error in JSON | Run `jq '.' file.json` to find error |
| `Selector returned no results` | CSS selector doesn't match | Test in browser DevTools |
| `Timeout exceeded` | Page too slow | Increase `page_timeout`, reduce `scan_full_page` |
| `Cannot read property` | Schema missing required field | Validate with `validate_config.py` |
| `LLM API error` | Invalid API key or quota | Check `~/.crawl4ai/global.yml` |
| `Navigation contamination` | baseSelector too broad | Use `validate_extraction.py`, refine baseSelector |
| `Empty required fields` | Wrong field selectors | Use Chrome MCP to test selectors |
