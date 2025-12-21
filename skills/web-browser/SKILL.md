---
name: web-browser
description: >
  This skill provides tools for browser automation and web page interaction
  through Chrome DevTools Protocol (CDP).

  It should be used when automating web browsers, testing web applications,
  scraping data, taking screenshots,

  or interacting with web pages programmatically.


  Use when: automating browser tasks, web scraping, testing websites, capturing
  screenshots, evaluating JavaScript,

  selecting page elements, navigating pages, filling forms, or debugging web
  applications.


  Keywords: browser automation, CDP, Chrome DevTools Protocol, web scraping,
  puppeteer, screenshot, JavaScript evaluation,

  DOM inspection, element picker, browser testing, headless Chrome, page
  navigation, web automation
when_to_use: >
  Use when automating browsers via CDP, testing web apps, scraping data, taking
  screenshots, evaluating JavaScript, selecting elements, navigating pages,
  filling forms, or debugging web apps.
version: 1.0.0
license: MIT
category: research-and-learning
short_description: >-
  This skill provides tools for browser automation and web page interaction
  through Chrome DevTools Protocol (CDP).
---

# Web Browser Skill

Remote control Chrome/Chromium through CDP for automated web interaction and testing.

## Prerequisites

**Required:**
- Node.js (for running tools)
- Google Chrome or Chromium browser
- macOS (current implementation)

**Install Dependencies:**
```bash
cd tools/
bun install
# or: npm install
```

----

## Quick Start

**1. Start Chrome with remote debugging:**
```bash
./web start
```

**2. Navigate to a page:**
```bash
./web nav https://example.com
```

**3. Evaluate JavaScript:**
```bash
./web eval 'document.title'
```

**4. Capture screenshot:**
```bash
./web screenshot
```

**5. Stop Chrome when done:**
```bash
./web stop
```

**Note:** You can also use `./tools/web.js` directly if preferred.

----

## Commands Reference

### start - Start Chrome

```bash
./web start              # Fresh profile
./web start --profile    # Copy default Chrome profile
```

Starts Chrome on port `:9222` with remote debugging enabled. Creates isolated profile in `~/.cache/scraping`.

**Profile option:** Copies cookies and login sessions from default Chrome profile (first run may take 10-30 seconds).

### nav - Navigate Pages

```bash
./web nav <url>          # Navigate current/create new tab
./web nav <url> --new    # Force new tab
```

Navigate to URL in current tab or open new tab. Creates tab if none exist.

**Examples:**
```bash
./web nav https://github.com
./web nav https://example.com --new
```

### eval - Evaluate JavaScript

```bash
./web eval '<code>'
```

Execute JavaScript in active tab (async context). Returns result to stdout.

**Examples:**
```bash
# Get page title
./web eval 'document.title'

# Count links
./web eval 'document.querySelectorAll("a").length'

# Extract data
./web eval 'Array.from(document.querySelectorAll("h1")).map(h => h.textContent)'

# Complex queries (use single quotes for outer string)
./web eval 'JSON.stringify(Array.from(document.querySelectorAll("a")).map(a => ({text: a.textContent.trim(), href: a.href})))'
```

**String escaping:** Use single quotes for shell command, double quotes inside JavaScript.

### screenshot - Capture Screenshots

```bash
./web screenshot
```

Screenshot current viewport, saves to temp directory, returns file path.

**Output:** `/var/folders/.../screenshot-<timestamp>.png`

### pick - Pick Elements

```bash
./web pick "<message>"
```

Interactive element picker with visual overlay.

**Controls:**
- Hover: Highlight elements
- Click: Select element (finishes)
- Cmd/Ctrl+Click: Multi-select
- Enter: Finish with selections
- Esc: Cancel

**Example:**
```bash
./web pick "Select the submit button"
```

Returns element info: tag, id, class, text, HTML, parent hierarchy.

### stop - Stop Chrome

```bash
./web stop
```

Kill Chrome instance and clean up. Run when finished to free resources.

### help - Show Help

```bash
./web help
```

Display usage information and command reference.

----

## Critical Rules

### Always Do
- Run `./web start` before other commands (Chrome must be running on `:9222`)
- Use single quotes for `eval` commands to avoid shell escaping issues
- Check CDP connection: `curl http://localhost:9222/json/version`
- Stop Chrome when done: `./web stop`

### Never Do
- Run multiple Chrome instances on same port (causes connection errors)
- Use double quotes for outer string in `eval` (shell parsing issues)
- Assume tab exists (`nav` creates one if needed)
- Leave Chrome running indefinitely (uses system resources)

----

## Common Patterns

### Scraping Workflow
```bash
# 1. Start browser
./web start

# 2. Navigate to target
./web nav https://example.com

# 3. Extract data
./web eval 'document.querySelectorAll("h2").length'

# 4. Screenshot for reference
./web screenshot

# 5. Clean up
./web stop
```

### Testing Workflow
```bash
# Start with profile (logged-in state)
./web start --profile

# Navigate to app
./web nav https://app.example.com

# Interact and verify
./web eval 'document.querySelector("#status").textContent'

# Stop when done
./web stop
```

### Multi-Page Analysis
```bash
./web start
./web nav https://site1.com --new
./web nav https://site2.com --new
./web nav https://site3.com --new
# Each opens in new tab
./web stop
```

----

## Troubleshooting

### Chrome won't start
- Use stop command first: `./web stop`
- Wait 2 seconds, try again: `./web start`
- Check Chrome is installed: `test -d "/Applications/Google Chrome.app"`

### "Cannot connect to browser"
- Verify Chrome is running: `curl http://localhost:9222/json/version`
- Check no other process using port 9222: `lsof -i :9222`
- Restart: `./web stop` then `./web start`

### "Cannot read properties of undefined"
- Error indicates no active tab
- Solution: `nav` command creates tab automatically
- Or manually: Use `--new` flag

### eval fails with syntax error
- Check string quoting: Use `'` outside, `"` inside
- Escape special chars if needed
- Test JavaScript in browser console first
- Better error messages: New CLI shows helpful hints

### Screenshot returns empty path
- Ensure page loaded: Wait after `nav` command
- Check temp directory writable: `ls -la /tmp` or `$TMPDIR`

----

## Technical Details

**Architecture:**
- CDP connection via `puppeteer-core` (no bundled Chromium)
- Chrome runs detached (survives script exit)
- Profile stored in `~/.cache/scraping/`
- Port 9222 for remote debugging

**Compatibility:**
- macOS: ✅ Tested
- Linux: ⚠️ Update Chrome path in `start.js`
- Windows: ❌ Not supported (path and process management differ)

**Dependencies:**
- `puppeteer-core` ^24.27.0 (lightweight, no bundled browser)

----

## Examples

### Data Extraction
```bash
./web start
./web nav https://news.ycombinator.com

# Extract top stories
./web eval 'Array.from(document.querySelectorAll(".titleline > a")).slice(0, 5).map(a => ({title: a.textContent, url: a.href}))'

# Clean up
./web stop
```

### Visual Testing
```bash
./web start
./web nav https://example.com

# Capture before
BEFORE=$(./web screenshot)

# Make changes
./web eval 'document.body.style.backgroundColor = "red"'

# Capture after
AFTER=$(./web screenshot)

echo "Before: $BEFORE"
echo "After: $AFTER"

# Clean up
./web stop
```

### Form Interaction
```bash
./web start
./web nav https://example.com/form

# Fill fields
./web eval 'document.querySelector("#email").value = "test@example.com"'
./web eval 'document.querySelector("#password").value = "password123"'

# Submit
./web eval 'document.querySelector("form").submit()'

# Clean up
./web stop
```
