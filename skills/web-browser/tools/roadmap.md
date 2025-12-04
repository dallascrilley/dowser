# Brainstorming: Making Web-Browser Skill More LLM-Friendly

## Top 10 Ideas for Enhanced LLM Usability

### 1. **Smart Auto-Start with State Checking**
**Problem:** LLM must remember to start Chrome first
**Solution:** Auto-detect if Chrome is running and start if needed

```bash
# Current:
./web start
./web nav https://example.com

# Proposed:
./web nav https://example.com  # Auto-starts Chrome if needed
```

**Benefits:**
- Reduces cognitive load for LLM
- Fewer steps to remember
- More fault-tolerant
- Better UX in conversations

---

### 2. **Workflow Commands (Pre-built Patterns)**
**Problem:** Common tasks require multiple commands
**Solution:** Bundle common workflows into single commands

```bash
# Current:
./web start
./web nav https://example.com
./web eval 'document.querySelectorAll("h1")'
./web screenshot
./web stop

# Proposed:
./web scrape https://example.com --selector 'h1' --screenshot
# Or:
./web workflow scrape-and-capture <url>
```

**Pre-built workflows:**
- `scrape-page` - Navigate + extract + screenshot
- `test-login` - Navigate + fill form + submit + verify
- `monitor` - Navigate + eval + screenshot + repeat
- `quick-look` - Navigate + screenshot + close

---

### 3. **JSON Output Mode for Structured Data**
**Problem:** Text output is hard for LLM to parse reliably
**Solution:** Add `--json` flag for machine-readable output

```bash
# Current:
./web eval 'Array.from(document.querySelectorAll("a")).map(...)'
# Output: text/objects mixed

# Proposed:
./web eval 'document.querySelectorAll("a")' --json
# Output:
{
  "success": true,
  "count": 42,
  "data": [{"text": "...", "href": "..."}],
  "meta": {
    "url": "https://example.com",
    "timestamp": "2025-11-08T04:00:00Z"
  }
}
```

**Benefits:**
- Reliable parsing
- Type information included
- Error handling standardized
- Metadata for context

---

### 4. **Wait/Retry Logic Built-In**
**Problem:** Page loads take time, timing issues
**Solution:** Smart waiting with customizable timeouts

```bash
# Current:
./web nav https://example.com
sleep 3  # LLM must guess timing
./web eval 'document.title'

# Proposed:
./web nav https://example.com --wait-for 'document.readyState === "complete"'
./web nav https://example.com --wait-for-selector '#content'
./web eval 'document.title' --retry 3 --timeout 10s
```

**Auto-wait options:**
- `--wait-load` - Wait for page load event
- `--wait-idle` - Wait for network idle
- `--wait-selector <sel>` - Wait for element
- `--wait-js <code>` - Wait for condition

---

### 5. **Chain/Pipeline Support**
**Problem:** Multiple steps can't be combined
**Solution:** Unix-style piping between commands

```bash
# Current:
./web nav https://example.com
./web eval 'document.querySelectorAll("a").length'

# Proposed:
./web nav https://example.com | ./web eval 'document.querySelectorAll("a").length' | jq
# Or:
./web chain \
  'nav https://example.com' \
  'eval document.title' \
  'screenshot'
```

---

### 6. **Session Management & Persistence**
**Problem:** Can't save/restore browser state easily
**Solution:** Session save/load commands

```bash
# Save state
./web session save my-session
  # Saves: cookies, localStorage, current tabs, scroll positions

# Restore later
./web session load my-session
  # Restores everything

# List sessions
./web session list

# Use cases:
# - Save logged-in state
# - Resume interrupted workflows
# - Share state between runs
```

---

### 7. **High-Level Actions (Declarative Interface)**
**Problem:** Low-level eval commands require deep DOM knowledge
**Solution:** Pre-built actions for common tasks

```bash
# Current:
./web eval 'document.querySelector("#email").value = "test@example.com"'
./web eval 'document.querySelector("button[type=submit]").click()'

# Proposed:
./web action fill-form --selector 'form' --data '{"email": "test@example.com"}'
./web action click --text "Submit"
./web action wait-for --text "Success"
./web action extract-table --selector 'table.data'
./web action scroll-to-bottom
./web action hover --selector '.menu-item'
```

**Pre-built actions:**
- `fill-form` - Fill form fields
- `click` - Click by selector/text
- `wait-for` - Wait for element/text
- `extract-table` - Parse HTML tables
- `scroll` - Scroll operations
- `hover` - Hover interactions

---

### 8. **Context-Aware Help & Suggestions**
**Problem:** LLM doesn't know what's available in current state
**Solution:** Status command showing available actions

```bash
./web status
# Output:
{
  "chrome_running": true,
  "current_url": "https://example.com",
  "page_title": "Example Domain",
  "available_actions": [
    "eval - execute JavaScript",
    "screenshot - capture current view",
    "nav - go to different page",
    "extract - get page data"
  ],
  "elements_found": {
    "links": 3,
    "forms": 0,
    "buttons": 2
  },
  "suggested_next": [
    "./web extract --selector 'a'",
    "./web screenshot",
    "./web eval 'document.title'"
  ]
}
```

---

### 9. **Error Recovery & Self-Healing**
**Problem:** Errors halt workflow, require manual intervention
**Solution:** Auto-retry with fallbacks

```bash
# Current:
./web eval 'document.querySelector("#missing").textContent'
# Error: Cannot read properties of null

# Proposed (with --safe flag):
./web eval 'document.querySelector("#missing")?.textContent' --safe
# Or:
./web eval 'document.title' --fallback "No title found"

# Auto-recovery features:
./web nav <url> --retry-on-timeout 3
./web eval '<code>' --ignore-errors
./web screenshot --retry-on-blank
```

---

### 10. **Batch Operations & Parallel Execution**
**Problem:** Sequential operations are slow
**Solution:** Batch and parallel command execution

```bash
# Current (sequential):
./web nav https://site1.com --new
./web nav https://site2.com --new
./web nav https://site3.com --new

# Proposed (batch file):
cat urls.txt | ./web batch nav --parallel 3

# Or batch commands:
./web batch << EOF
nav https://site1.com --new
nav https://site2.com --new
nav https://site3.com --new
wait-all
screenshot-all
close-all
EOF

# Multi-tab operations:
./web tabs list
./web tabs foreach 'eval document.title'
./web tabs close-pattern '*example*'
```

---

## Implementation Priority Ranking

### High Priority (Biggest Impact)
1. **Smart Auto-Start (#1)** - 95% of friction removal
2. **JSON Output (#3)** - Makes data usable for LLM
3. **Wait/Retry Logic (#4)** - Handles timing issues

### Medium Priority (Nice to Have)
4. **High-Level Actions (#7)** - Reduces complexity
5. **Context-Aware Help (#8)** - Better discoverability
6. **Workflow Commands (#2)** - Common patterns

### Lower Priority (Advanced)
7. **Error Recovery (#9)** - Better fault tolerance
8. **Session Management (#6)** - State persistence
9. **Chain/Pipeline (#5)** - Power user feature
10. **Batch Operations (#10)** - Scaling feature

---

## Quick Wins (Easiest to Implement)

1. **Auto-start detection** - Check port 9222, start if needed
2. **JSON flag** - Wrap output in JSON structure
3. **Basic wait flags** - Add `--wait-load`, `--wait-idle`
4. **Status command** - Show current state
5. **Retry flags** - Add `--retry N` to commands

---

## Example: Enhanced Quick Start (After Implementation)

```bash
# Before (current):
./web start
./web nav https://example.com
sleep 2
./web eval 'document.title'
./web stop

# After (with enhancements):
./web nav https://example.com --json
# Auto-starts Chrome, waits for load, returns JSON:
{
  "success": true,
  "url": "https://example.com",
  "title": "Example Domain",
  "ready": true
}

# Extract data with retry:
./web eval 'document.querySelectorAll("a")' --json --retry 3

# Workflow command:
./web workflow scrape https://example.com --selector 'h1,h2,h3'
# Returns structured data, takes screenshot, auto-closes
```

---

## For LLM Context: Why These Help

**Current challenges for LLMs using this skill:**
1. Must track Chrome state manually
2. Timing issues require guessing sleep duration
3. Text output is hard to parse reliably
4. Multiple steps for common tasks
5. Errors require manual recovery

**How improvements help:**
1. Auto-start removes state tracking burden
2. Built-in waits eliminate timing guesses
3. JSON output enables reliable parsing
4. Workflows reduce step count
5. Error recovery reduces failure modes

**Result:** LLM can focus on the task, not the tool mechanics.