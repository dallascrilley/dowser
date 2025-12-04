# Web-Browser LLM-Friendly Enhancements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform web-browser skill into a more LLM-friendly tool by implementing auto-start detection, JSON output mode, and smart wait/retry logic.

**Architecture:** Enhance existing bash wrapper (`web`) with intelligent state detection, structured output formatting, and robust timing controls. All changes maintain backward compatibility while adding opt-in flags for new behavior.

**Tech Stack:** Bash scripting, Chrome DevTools Protocol (CDP), JSON formatting with `jq`, superpowers-chrome MCP server

---

## Phase 1: Foundation & Auto-Start Detection

### Task 1: Add Chrome State Detection Helper

**Files:**
- Modify: `tools/web:1-50` (add helper functions at top)
- Test: Manual testing with Chrome running/stopped

**Step 1: Write state detection function**

Add after shebang and before existing functions:

```bash
# Check if Chrome is running on CDP port
is_chrome_running() {
    if nc -z localhost 9222 2>/dev/null; then
        return 0  # Chrome is running
    else
        return 1  # Chrome is not running
    fi
}

# Auto-start Chrome if not running
ensure_chrome_started() {
    if ! is_chrome_running; then
        echo "🚀 Auto-starting Chrome..." >&2
        start_chrome
        sleep 2  # Give Chrome time to start

        # Verify it started
        if ! is_chrome_running; then
            echo "❌ Failed to auto-start Chrome" >&2
            exit 1
        fi
    fi
}
```

**Step 2: Test detection manually**

```bash
# With Chrome stopped
./web status
# Expected: No output (Chrome not running)

# Start Chrome manually
./web start

# Check detection
nc -z localhost 9222 && echo "Detected" || echo "Not detected"
# Expected: "Detected"
```

**Step 3: Commit**

```bash
git add tools/web
git commit -m "feat(web): add Chrome state detection helpers"
```

---

### Task 2: Integrate Auto-Start into Navigation Command

**Files:**
- Modify: `tools/web` (nav function)

**Step 1: Add auto-start to nav command**

Find the `nav` command handler and add `ensure_chrome_started` at the beginning:

```bash
nav)
    ensure_chrome_started

    url="$2"
    if [ -z "$url" ]; then
        echo "Usage: $0 nav <url> [--new]"
        exit 1
    fi

    # Rest of existing nav logic...
```

**Step 2: Test auto-start navigation**

```bash
# Stop Chrome if running
./web stop

# Navigate without manually starting
./web nav https://example.com
# Expected:
# 🚀 Auto-starting Chrome...
# [navigation output]
```

**Step 3: Test with Chrome already running**

```bash
# Chrome is already running from previous test
./web nav https://example.com
# Expected: No auto-start message, direct navigation
```

**Step 4: Commit**

```bash
git add tools/web
git commit -m "feat(web): auto-start Chrome on navigation"
```

---

### Task 3: Integrate Auto-Start into Other Commands

**Files:**
- Modify: `tools/web` (eval, screenshot, extract commands)

**Step 1: Add auto-start to eval command**

```bash
eval)
    ensure_chrome_started

    # Rest of existing eval logic...
```

**Step 2: Add auto-start to screenshot command**

```bash
screenshot)
    ensure_chrome_started

    # Rest of existing screenshot logic...
```

**Step 3: Add auto-start to extract command**

```bash
extract)
    ensure_chrome_started

    # Rest of existing extract logic...
```

**Step 4: Test each command without Chrome running**

```bash
./web stop

./web eval 'document.title'
# Expected: Auto-starts, then evaluates

./web screenshot
# Expected: Uses already-running Chrome, takes screenshot

./web stop
./web extract --selector 'h1'
# Expected: Auto-starts, then extracts
```

**Step 5: Commit**

```bash
git add tools/web
git commit -m "feat(web): add auto-start to eval, screenshot, extract"
```

---

## Phase 2: JSON Output Mode

### Task 4: Add JSON Output Helper Functions

**Files:**
- Modify: `tools/web` (add JSON helpers)

**Step 1: Write JSON formatting helpers**

Add after the `ensure_chrome_started` function:

```bash
# Check if JSON output is requested
use_json_output() {
    [[ "$*" == *"--json"* ]]
}

# Format success response as JSON
json_success() {
    local data="$1"
    local url="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat <<EOF
{
  "success": true,
  "timestamp": "$timestamp",
  "url": "$url",
  "data": $data
}
EOF
}

# Format error response as JSON
json_error() {
    local error="$1"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat <<EOF
{
  "success": false,
  "timestamp": "$timestamp",
  "error": "$error"
}
EOF
}
```

**Step 2: Test JSON helpers manually**

```bash
# Source the functions
source tools/web

# Test success
json_success '{"title": "Example"}' "https://example.com"
# Expected: Valid JSON output

# Test error
json_error "Page not found"
# Expected: Valid JSON error output

# Validate JSON
json_success '{"test": true}' "https://test.com" | jq .
# Expected: Parsed and pretty-printed JSON
```

**Step 3: Commit**

```bash
git add tools/web
git commit -m "feat(web): add JSON output formatting helpers"
```

---

### Task 5: Add JSON Support to Nav Command

**Files:**
- Modify: `tools/web` (nav command)

**Step 1: Update nav to support --json flag**

Modify the nav command to check for --json and format output:

```bash
nav)
    ensure_chrome_started

    url=""
    new_tab=false
    json_mode=false

    # Parse arguments
    shift  # Remove 'nav'
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --new)
                new_tab=true
                shift
                ;;
            --json)
                json_mode=true
                shift
                ;;
            *)
                url="$1"
                shift
                ;;
        esac
    done

    if [ -z "$url" ]; then
        echo "Usage: $0 nav <url> [--new] [--json]"
        exit 1
    fi

    # Navigate
    if [ "$new_tab" = true ]; then
        result=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=new_tab payload="$url" 2>&1)
    else
        result=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=navigate payload="$url" 2>&1)
    fi

    # Format output
    if [ "$json_mode" = true ]; then
        # Get page title for enriched response
        title=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload='document.title' 2>&1 || echo "Unknown")

        json_success "{\"url\": \"$url\", \"title\": \"$title\", \"new_tab\": $new_tab}" "$url"
    else
        echo "$result"
    fi
    ;;
```

**Step 2: Test nav with JSON output**

```bash
./web nav https://example.com --json
# Expected:
# {
#   "success": true,
#   "timestamp": "2025-11-07T...",
#   "url": "https://example.com",
#   "data": {
#     "url": "https://example.com",
#     "title": "Example Domain",
#     "new_tab": false
#   }
# }

# Validate JSON
./web nav https://example.com --json | jq .success
# Expected: true
```

**Step 3: Test backward compatibility**

```bash
./web nav https://example.com
# Expected: Original text output (no JSON)
```

**Step 4: Commit**

```bash
git add tools/web
git commit -m "feat(web): add JSON output mode to nav command"
```

---

### Task 6: Add JSON Support to Eval Command

**Files:**
- Modify: `tools/web` (eval command)

**Step 1: Update eval to support --json flag**

```bash
eval)
    ensure_chrome_started

    code=""
    json_mode=false

    # Parse arguments
    shift  # Remove 'eval'
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                json_mode=true
                shift
                ;;
            *)
                code="$1"
                shift
                ;;
        esac
    done

    if [ -z "$code" ]; then
        echo "Usage: $0 eval <javascript> [--json]"
        exit 1
    fi

    # Execute JavaScript
    result=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload="$code" 2>&1)
    exit_code=$?

    # Format output
    if [ "$json_mode" = true ]; then
        current_url=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload='window.location.href' 2>&1 || echo "unknown")

        if [ $exit_code -eq 0 ]; then
            # Try to parse result as JSON, otherwise wrap as string
            if echo "$result" | jq . >/dev/null 2>&1; then
                json_success "$result" "$current_url"
            else
                json_success "\"$result\"" "$current_url"
            fi
        else
            json_error "$result"
        fi
    else
        echo "$result"
    fi
    ;;
```

**Step 2: Test eval with JSON output**

```bash
./web nav https://example.com

./web eval 'document.title' --json
# Expected: JSON with title

./web eval 'document.querySelectorAll("a").length' --json
# Expected: JSON with number

./web eval 'Array.from(document.querySelectorAll("a")).map(a => ({text: a.textContent, href: a.href}))' --json
# Expected: JSON with array of links
```

**Step 3: Test error handling**

```bash
./web eval 'nonexistent.property' --json
# Expected: JSON error response
```

**Step 4: Commit**

```bash
git add tools/web
git commit -m "feat(web): add JSON output mode to eval command"
```

---

## Phase 3: Wait & Retry Logic

### Task 7: Add Wait Helper Functions

**Files:**
- Modify: `tools/web` (add wait helpers)

**Step 1: Write wait helper functions**

Add after JSON helpers:

```bash
# Wait for page load
wait_for_load() {
    local timeout=${1:-10}
    local elapsed=0

    while [ $elapsed -lt $timeout ]; do
        ready=$(mcp__plugin_superpowers-chrome_chrome__use_browser \
            action=eval \
            payload='document.readyState === "complete"' 2>&1)

        if [[ "$ready" == "true" ]]; then
            return 0
        fi

        sleep 0.5
        elapsed=$((elapsed + 1))
    done

    return 1  # Timeout
}

# Wait for network idle
wait_for_idle() {
    local timeout=${1:-10}
    echo "⏳ Waiting for network idle (${timeout}s max)..." >&2
    sleep 2  # Simple implementation: wait 2 seconds
    return 0
}

# Wait for selector to appear
wait_for_selector() {
    local selector="$1"
    local timeout=${2:-10}
    local elapsed=0

    echo "⏳ Waiting for selector: $selector (${timeout}s max)..." >&2

    while [ $elapsed -lt $timeout ]; do
        exists=$(mcp__plugin_superpowers-chrome_chrome__use_browser \
            action=eval \
            payload="document.querySelector('$selector') !== null" 2>&1)

        if [[ "$exists" == "true" ]]; then
            echo "✅ Selector found!" >&2
            return 0
        fi

        sleep 0.5
        elapsed=$((elapsed + 1))
    done

    echo "❌ Timeout waiting for selector" >&2
    return 1  # Timeout
}

# Wait for custom JavaScript condition
wait_for_condition() {
    local condition="$1"
    local timeout=${2:-10}
    local elapsed=0

    echo "⏳ Waiting for condition: $condition (${timeout}s max)..." >&2

    while [ $elapsed -lt $timeout ]; do
        result=$(mcp__plugin_superpowers-chrome_chrome__use_browser \
            action=eval \
            payload="$condition" 2>&1)

        if [[ "$result" == "true" ]]; then
            echo "✅ Condition met!" >&2
            return 0
        fi

        sleep 0.5
        elapsed=$((elapsed + 1))
    done

    echo "❌ Timeout waiting for condition" >&2
    return 1  # Timeout
}
```

**Step 2: Test wait helpers**

```bash
# Source the script
source tools/web

# Start Chrome and navigate
./web start
./web nav https://example.com

# Test wait for load
wait_for_load 5
echo "Exit code: $?"
# Expected: 0 (success)

# Test wait for selector (exists)
wait_for_selector "h1" 5
# Expected: 0 with "✅ Selector found!"

# Test wait for selector (missing)
wait_for_selector "#nonexistent" 2
# Expected: 1 with "❌ Timeout waiting for selector"

# Test wait for condition
wait_for_condition "document.querySelectorAll('a').length > 0" 5
# Expected: 0 with "✅ Condition met!"
```

**Step 3: Commit**

```bash
git add tools/web
git commit -m "feat(web): add wait helper functions for load, selectors, conditions"
```

---

### Task 8: Integrate Wait Flags into Nav Command

**Files:**
- Modify: `tools/web` (nav command)

**Step 1: Add wait flags to nav**

Update nav argument parsing to support wait flags:

```bash
nav)
    ensure_chrome_started

    url=""
    new_tab=false
    json_mode=false
    wait_load=false
    wait_idle=false
    wait_selector=""
    wait_timeout=10

    # Parse arguments
    shift  # Remove 'nav'
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --new)
                new_tab=true
                shift
                ;;
            --json)
                json_mode=true
                shift
                ;;
            --wait-load)
                wait_load=true
                shift
                ;;
            --wait-idle)
                wait_idle=true
                shift
                ;;
            --wait-selector)
                wait_selector="$2"
                shift 2
                ;;
            --timeout)
                wait_timeout="$2"
                shift 2
                ;;
            *)
                url="$1"
                shift
                ;;
        esac
    done

    if [ -z "$url" ]; then
        echo "Usage: $0 nav <url> [--new] [--json] [--wait-load] [--wait-idle] [--wait-selector <sel>] [--timeout <sec>]"
        exit 1
    fi

    # Navigate
    if [ "$new_tab" = true ]; then
        mcp__plugin_superpowers-chrome_chrome__use_browser action=new_tab payload="$url" >/dev/null 2>&1
    else
        mcp__plugin_superpowers-chrome_chrome__use_browser action=navigate payload="$url" >/dev/null 2>&1
    fi

    # Apply wait conditions
    if [ "$wait_load" = true ]; then
        wait_for_load "$wait_timeout" || exit 1
    fi

    if [ "$wait_idle" = true ]; then
        wait_for_idle "$wait_timeout" || exit 1
    fi

    if [ -n "$wait_selector" ]; then
        wait_for_selector "$wait_selector" "$wait_timeout" || exit 1
    fi

    # Get final state
    title=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload='document.title' 2>&1 || echo "Unknown")

    # Format output
    if [ "$json_mode" = true ]; then
        json_success "{\"url\": \"$url\", \"title\": \"$title\", \"new_tab\": $new_tab, \"ready\": true}" "$url"
    else
        echo "✅ Navigated to: $url"
        echo "📄 Title: $title"
    fi
    ;;
```

**Step 2: Test wait-load flag**

```bash
./web nav https://example.com --wait-load
# Expected: Waits for page to fully load before returning

./web nav https://example.com --wait-load --json
# Expected: JSON response after page loads
```

**Step 3: Test wait-selector flag**

```bash
./web nav https://example.com --wait-selector 'h1'
# Expected:
# ⏳ Waiting for selector: h1 (10s max)...
# ✅ Selector found!
# ✅ Navigated to: https://example.com

./web nav https://example.com --wait-selector '#missing' --timeout 2
# Expected: Timeout after 2 seconds with error
```

**Step 4: Test combined flags**

```bash
./web nav https://example.com --wait-load --wait-idle --json
# Expected: Waits for both conditions, then returns JSON
```

**Step 5: Commit**

```bash
git add tools/web
git commit -m "feat(web): add wait flags to nav command (--wait-load, --wait-selector, --timeout)"
```

---

### Task 9: Add Retry Logic to Eval Command

**Files:**
- Modify: `tools/web` (eval command)

**Step 1: Add retry helper function**

Add after wait helpers:

```bash
# Retry a command with exponential backoff
retry_command() {
    local max_retries="$1"
    local action="$2"
    local payload="$3"
    local retry_count=0

    while [ $retry_count -lt $max_retries ]; do
        result=$(mcp__plugin_superpowers-chrome_chrome__use_browser \
            action="$action" \
            payload="$payload" 2>&1)
        exit_code=$?

        if [ $exit_code -eq 0 ]; then
            echo "$result"
            return 0
        fi

        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            wait_time=$((2 ** retry_count))  # Exponential backoff
            echo "⚠️  Retry $retry_count/$max_retries (waiting ${wait_time}s)..." >&2
            sleep "$wait_time"
        fi
    done

    echo "$result"
    return 1  # All retries failed
}
```

**Step 2: Add retry flag to eval**

Update eval command argument parsing:

```bash
eval)
    ensure_chrome_started

    code=""
    json_mode=false
    retry_count=1  # Default: no retry

    # Parse arguments
    shift  # Remove 'eval'
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --json)
                json_mode=true
                shift
                ;;
            --retry)
                retry_count="$2"
                shift 2
                ;;
            *)
                code="$1"
                shift
                ;;
        esac
    done

    if [ -z "$code" ]; then
        echo "Usage: $0 eval <javascript> [--json] [--retry <n>]"
        exit 1
    fi

    # Execute with retry
    if [ $retry_count -gt 1 ]; then
        result=$(retry_command "$retry_count" "eval" "$code")
        exit_code=$?
    else
        result=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload="$code" 2>&1)
        exit_code=$?
    fi

    # Format output (existing JSON logic)
    if [ "$json_mode" = true ]; then
        current_url=$(mcp__plugin_superpowers-chrome_chrome__use_browser action=eval payload='window.location.href' 2>&1 || echo "unknown")

        if [ $exit_code -eq 0 ]; then
            if echo "$result" | jq . >/dev/null 2>&1; then
                json_success "$result" "$current_url"
            else
                json_success "\"$result\"" "$current_url"
            fi
        else
            json_error "$result"
        fi
    else
        echo "$result"
    fi
    ;;
```

**Step 3: Test retry on transient failure**

Create a test page with delayed content:

```bash
# Navigate to a page
./web nav https://example.com

# Try eval that might fail initially (simulate with timing)
./web eval 'document.querySelector("h1")?.textContent || null' --retry 3
# Expected: May retry if timing issues, eventually succeeds

# Test with JSON
./web eval 'document.title' --retry 3 --json
# Expected: JSON response after successful eval
```

**Step 4: Test retry exhaustion**

```bash
# Force a failure scenario
./web eval 'throw new Error("test failure")' --retry 3
# Expected:
# ⚠️  Retry 1/3 (waiting 2s)...
# ⚠️  Retry 2/3 (waiting 4s)...
# [error output]
```

**Step 5: Commit**

```bash
git add tools/web
git commit -m "feat(web): add retry logic with exponential backoff to eval command"
```

---

## Phase 4: Documentation & Testing

### Task 10: Update README with New Features

**Files:**
- Modify: `README.md` (add new features section)

**Step 1: Add Auto-Start section**

Add after "Quick Start" section:

```markdown
## Auto-Start Detection

Chrome is automatically started when needed - no need to run `./web start` manually:

```bash
# Just navigate - Chrome starts automatically if needed
./web nav https://example.com

# All commands auto-start Chrome
./web eval 'document.title'
./web screenshot
```

Manual start/stop still available:
```bash
./web start  # Explicitly start Chrome
./web stop   # Stop Chrome
```
```

**Step 2: Add JSON Output section**

```markdown
## JSON Output Mode

Get structured, machine-readable output with the `--json` flag:

```bash
# Navigation with JSON
./web nav https://example.com --json
# Returns:
# {
#   "success": true,
#   "timestamp": "2025-11-07T12:00:00Z",
#   "url": "https://example.com",
#   "data": {
#     "url": "https://example.com",
#     "title": "Example Domain",
#     "new_tab": false,
#     "ready": true
#   }
# }

# Evaluate JavaScript with JSON
./web eval 'document.querySelectorAll("a").length' --json

# Pipe to jq for processing
./web eval 'Array.from(document.querySelectorAll("a")).map(a => a.href)' --json | jq '.data'
```

**Benefits:**
- Reliable parsing for LLMs and scripts
- Consistent error handling
- Metadata included (timestamp, URL)
- Easy integration with `jq`
```

**Step 3: Add Wait & Retry section**

```markdown
## Wait & Retry Logic

Handle timing issues with built-in wait conditions and retry logic:

### Wait Flags (Navigation)

```bash
# Wait for page load
./web nav https://example.com --wait-load

# Wait for network idle
./web nav https://example.com --wait-idle

# Wait for specific element
./web nav https://example.com --wait-selector '#content'

# Custom timeout (default: 10s)
./web nav https://example.com --wait-selector 'h1' --timeout 5

# Combine with JSON
./web nav https://example.com --wait-load --json
```

### Retry Logic (Eval)

```bash
# Retry up to 3 times on failure
./web eval 'document.querySelector("#dynamic-content")?.textContent' --retry 3

# Combine retry with JSON
./web eval 'document.title' --retry 3 --json
```

**Exponential Backoff:** Retries use 2^n second delays (2s, 4s, 8s...)
```

**Step 4: Verify documentation is complete**

```bash
# Read the updated README
cat README.md

# Check for completeness:
# - Auto-start explained ✓
# - JSON output examples ✓
# - Wait flags documented ✓
# - Retry logic explained ✓
```

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: add auto-start, JSON output, and wait/retry documentation"
```

---

### Task 11: Create Examples Directory with Test Cases

**Files:**
- Create: `examples/01-auto-start.sh`
- Create: `examples/02-json-output.sh`
- Create: `examples/03-wait-retry.sh`
- Create: `examples/README.md`

**Step 1: Create examples directory**

```bash
mkdir -p examples
```

**Step 2: Write auto-start example**

```bash
cat > examples/01-auto-start.sh << 'EOF'
#!/bin/bash
# Example: Auto-Start Detection

set -e

echo "=== Auto-Start Example ==="
echo ""

# Stop Chrome if running
echo "1. Stopping Chrome (if running)..."
./web stop 2>/dev/null || true
echo ""

# Navigate without manual start - Chrome starts automatically
echo "2. Navigate without manual start..."
./web nav https://example.com
echo ""

# Subsequent commands use already-running Chrome
echo "3. Eval with already-running Chrome..."
./web eval 'document.title'
echo ""

echo "✅ Auto-start working correctly!"
EOF

chmod +x examples/01-auto-start.sh
```

**Step 3: Write JSON output example**

```bash
cat > examples/02-json-output.sh << 'EOF'
#!/bin/bash
# Example: JSON Output Mode

set -e

echo "=== JSON Output Example ==="
echo ""

# Navigate with JSON
echo "1. Navigate with JSON output..."
./web nav https://example.com --json | jq .
echo ""

# Eval with JSON
echo "2. Evaluate JavaScript with JSON output..."
./web eval 'document.title' --json | jq .
echo ""

# Extract data with JSON and jq
echo "3. Extract link count..."
COUNT=$(./web eval 'document.querySelectorAll("a").length' --json | jq -r '.data')
echo "Found $COUNT links"
echo ""

echo "✅ JSON output working correctly!"
EOF

chmod +x examples/02-json-output.sh
```

**Step 4: Write wait/retry example**

```bash
cat > examples/03-wait-retry.sh << 'EOF'
#!/bin/bash
# Example: Wait & Retry Logic

set -e

echo "=== Wait & Retry Example ==="
echo ""

# Navigate and wait for load
echo "1. Navigate with wait for load..."
./web nav https://example.com --wait-load
echo ""

# Navigate and wait for selector
echo "2. Navigate and wait for h1 element..."
./web nav https://example.com --wait-selector 'h1'
echo ""

# Eval with retry
echo "3. Evaluate with retry logic..."
./web eval 'document.title' --retry 3
echo ""

# Combined: wait + JSON
echo "4. Navigate with wait and JSON..."
./web nav https://example.com --wait-load --json | jq '.data.ready'
echo ""

echo "✅ Wait/retry working correctly!"
EOF

chmod +x examples/03-wait-retry.sh
```

**Step 5: Create examples README**

```bash
cat > examples/README.md << 'EOF'
# Web-Browser Examples

Practical examples demonstrating the LLM-friendly enhancements.

## Running Examples

Each example is a standalone script:

```bash
# Auto-start detection
./examples/01-auto-start.sh

# JSON output mode
./examples/02-json-output.sh

# Wait & retry logic
./examples/03-wait-retry.sh
```

## What Each Example Shows

**01-auto-start.sh**
- Chrome automatically starts when needed
- No manual `./web start` required
- Seamless command chaining

**02-json-output.sh**
- Structured JSON output with `--json` flag
- Integration with `jq` for data extraction
- Consistent response format

**03-wait-retry.sh**
- Wait for page load with `--wait-load`
- Wait for selectors with `--wait-selector`
- Retry logic with `--retry N`
- Combined flags for robust automation

## Integration Testing

Run all examples to verify the implementation:

```bash
for script in examples/*.sh; do
    echo "Running $script..."
    bash "$script"
    echo ""
done
```
EOF
```

**Step 6: Test all examples**

```bash
# Run each example
./examples/01-auto-start.sh
./examples/02-json-output.sh
./examples/03-wait-retry.sh

# Expected: All examples complete successfully
```

**Step 7: Commit**

```bash
git add examples/
git commit -m "feat: add examples demonstrating auto-start, JSON output, and wait/retry"
```

---

### Task 12: Update SKILL.md with New Capabilities

**Files:**
- Modify: `SKILL.md` (add new features to tool descriptions)

**Step 1: Update navigation command description**

Find the navigation section and update:

```markdown
### Navigation

Navigate to URLs with automatic Chrome startup and smart waiting:

```bash
# Basic navigation (auto-starts Chrome if needed)
./web nav https://example.com

# Open in new tab
./web nav https://example.com --new

# Get structured output
./web nav https://example.com --json

# Wait for page load
./web nav https://example.com --wait-load

# Wait for specific element
./web nav https://example.com --wait-selector '#content'

# Combined: auto-start + wait + JSON
./web nav https://example.com --wait-load --json
```

**Flags:**
- `--new` - Open URL in new tab
- `--json` - Return structured JSON output
- `--wait-load` - Wait for page load (document.readyState === 'complete')
- `--wait-idle` - Wait for network idle
- `--wait-selector <sel>` - Wait for selector to appear
- `--timeout <sec>` - Custom timeout for wait operations (default: 10s)
```

**Step 2: Update eval command description**

```markdown
### JavaScript Evaluation

Execute JavaScript in page context with retry support:

```bash
# Basic evaluation (auto-starts Chrome if needed)
./web eval 'document.title'

# Get structured output
./web eval 'document.title' --json

# Retry on failure (exponential backoff)
./web eval 'document.querySelector("#dynamic")?.textContent' --retry 3

# Extract data as JSON
./web eval 'Array.from(document.querySelectorAll("a")).map(a => ({text: a.textContent, href: a.href}))' --json

# Combined: retry + JSON
./web eval 'document.title' --retry 3 --json | jq -r '.data'
```

**Flags:**
- `--json` - Return structured JSON output
- `--retry <n>` - Retry up to N times on failure (exponential backoff: 2s, 4s, 8s...)
```

**Step 3: Add "For LLM" guidance section**

Add a new section at the end of SKILL.md:

```markdown
## For LLMs: Best Practices

### No Manual Chrome Management Needed

**Don't do this:**
```bash
./web start
./web nav https://example.com
```

**Do this instead:**
```bash
./web nav https://example.com  # Auto-starts Chrome
```

### Use JSON for Reliable Parsing

**Don't do this:**
```bash
result=$(./web eval 'document.title')
# Hard to parse, no error info
```

**Do this instead:**
```bash
result=$(./web eval 'document.title' --json)
success=$(echo "$result" | jq -r '.success')
data=$(echo "$result" | jq -r '.data')
```

### Handle Timing with Wait Flags

**Don't do this:**
```bash
./web nav https://example.com
sleep 3  # Arbitrary wait
./web eval 'document.querySelector("#content").textContent'
```

**Do this instead:**
```bash
./web nav https://example.com --wait-selector '#content'
./web eval 'document.querySelector("#content").textContent' --retry 3
```

### Recommended Patterns

**Data extraction:**
```bash
./web nav <url> --wait-load --json
./web eval '<selector-query>' --retry 3 --json | jq '.data'
```

**Form interaction:**
```bash
./web nav <url> --wait-selector 'form'
./web eval 'document.querySelector("#email").value = "test@example.com"'
./web eval 'document.querySelector("form").submit()'
```

**Monitoring/scraping:**
```bash
while true; do
    ./web nav <url> --wait-load --json | jq '.data.title'
    sleep 60
done
```
```

**Step 4: Verify SKILL.md updates**

```bash
# Read the updated SKILL.md
cat SKILL.md | grep -A 10 "For LLMs"

# Check that all new flags are documented
grep -E "(--json|--retry|--wait-load|--wait-selector)" SKILL.md
```

**Step 5: Commit**

```bash
git add SKILL.md
git commit -m "docs: update SKILL.md with LLM-friendly features and best practices"
```

---

## Phase 5: Final Validation & Cleanup

### Task 13: Integration Testing

**Files:**
- Create: `tests/integration-test.sh`

**Step 1: Write comprehensive integration test**

```bash
cat > tests/integration-test.sh << 'EOF'
#!/bin/bash
# Integration test for LLM-friendly enhancements

set -e

PASSED=0
FAILED=0

test_case() {
    local name="$1"
    local command="$2"
    local expected="$3"

    echo -n "Testing: $name... "

    if output=$(eval "$command" 2>&1); then
        if [[ "$output" == *"$expected"* ]]; then
            echo "✅ PASS"
            PASSED=$((PASSED + 1))
        else
            echo "❌ FAIL (unexpected output)"
            echo "  Expected: $expected"
            echo "  Got: $output"
            FAILED=$((FAILED + 1))
        fi
    else
        echo "❌ FAIL (command failed)"
        FAILED=$((FAILED + 1))
    fi
}

echo "=== Web-Browser Integration Tests ==="
echo ""

# Stop Chrome to test auto-start
./web stop 2>/dev/null || true

# Test 1: Auto-start on nav
test_case "Auto-start on nav" \
    "./web nav https://example.com" \
    "example.com"

# Test 2: JSON output on nav
test_case "JSON output on nav" \
    "./web nav https://example.com --json | jq -r '.success'" \
    "true"

# Test 3: Wait for load
test_case "Wait for load" \
    "./web nav https://example.com --wait-load" \
    "example.com"

# Test 4: Wait for selector
test_case "Wait for selector" \
    "./web nav https://example.com --wait-selector 'h1'" \
    "Selector found"

# Test 5: Eval with JSON
test_case "Eval with JSON" \
    "./web eval 'document.title' --json | jq -r '.success'" \
    "true"

# Test 6: Eval with retry
test_case "Eval with retry (success)" \
    "./web eval 'document.title' --retry 3" \
    "Example"

# Test 7: Combined flags
test_case "Combined: wait + JSON" \
    "./web nav https://example.com --wait-load --json | jq -r '.data.ready'" \
    "true"

# Test 8: Screenshot still works
test_case "Screenshot compatibility" \
    "./web screenshot && [ -f page.png ]" \
    ""

# Summary
echo ""
echo "=== Test Summary ==="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
EOF

chmod +x tests/integration-test.sh
```

**Step 2: Run integration tests**

```bash
./tests/integration-test.sh
# Expected: All tests pass
```

**Step 3: Fix any failures**

If any tests fail:
1. Review the failure output
2. Fix the underlying issue
3. Re-run tests
4. Repeat until all pass

**Step 4: Commit**

```bash
git add tests/integration-test.sh
git commit -m "test: add integration tests for LLM-friendly enhancements"
```

---

### Task 14: Update Changelog

**Files:**
- Create or Modify: `CHANGELOG.md`

**Step 1: Create/update CHANGELOG**

```bash
cat > CHANGELOG.md << 'EOF'
# Changelog

All notable changes to the web-browser skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2025-11-07

### Added - LLM-Friendly Enhancements

**Auto-Start Detection**
- Chrome automatically starts when needed
- No manual `./web start` required for most operations
- State detection via port 9222 check
- Auto-start integrated into: nav, eval, screenshot, extract commands

**JSON Output Mode**
- `--json` flag for structured, machine-readable output
- Consistent response format with success/error states
- Timestamp and URL metadata included
- Easy integration with `jq` for data extraction
- Available on: nav, eval commands

**Wait & Retry Logic**
- `--wait-load` - Wait for page load completion
- `--wait-idle` - Wait for network idle
- `--wait-selector <sel>` - Wait for element to appear
- `--timeout <sec>` - Custom timeout for wait operations
- `--retry <n>` - Retry with exponential backoff (eval command)

**Documentation**
- Updated README with new features
- Added examples directory with test scripts
- Enhanced SKILL.md with LLM best practices
- Created integration test suite

### Changed
- Nav command now supports multiple flags (backward compatible)
- Eval command now supports retry logic (backward compatible)
- Improved error messages and user feedback

### Backward Compatibility
All changes are backward compatible. Existing scripts continue to work without modification.

## [1.0.0] - Previous

Initial release with basic Chrome DevTools Protocol wrapper functionality.

EOF
```

**Step 2: Review changelog**

```bash
cat CHANGELOG.md
# Verify all features are documented
```

**Step 3: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add changelog for v2.0.0 LLM-friendly enhancements"
```

---

### Task 15: Final Review & Documentation Check

**Step 1: Review all changed files**

```bash
git --no-pager diff main --name-status
# Expected list:
# M tools/web
# M README.md
# M SKILL.md
# A CHANGELOG.md
# A examples/01-auto-start.sh
# A examples/02-json-output.sh
# A examples/03-wait-retry.sh
# A examples/README.md
# A tests/integration-test.sh
```

**Step 2: Run final integration tests**

```bash
./tests/integration-test.sh
# Expected: All tests pass
```

**Step 3: Test all examples**

```bash
for script in examples/*.sh; do
    echo "Running $script..."
    bash "$script" || exit 1
done
# Expected: All examples succeed
```

**Step 4: Verify documentation completeness**

Check that documentation covers:
- [ ] Auto-start feature explained
- [ ] JSON output documented with examples
- [ ] All wait flags documented
- [ ] Retry logic explained
- [ ] LLM best practices included
- [ ] Examples provided
- [ ] Changelog updated

**Step 5: Create summary commit (optional)**

```bash
git log --oneline HEAD~15..HEAD
# Review all commits

# Create annotated tag
git tag -a v2.0.0 -m "Release v2.0.0: LLM-Friendly Enhancements

Features:
- Auto-start detection
- JSON output mode
- Wait & retry logic
- Comprehensive documentation
"
```

---

## Success Criteria

✅ **Auto-Start Detection**
- Chrome starts automatically on first command
- No manual start required for common workflows
- State detection works reliably

✅ **JSON Output Mode**
- `--json` flag returns valid JSON
- Consistent structure across commands
- Error handling included
- Easy to parse with `jq`

✅ **Wait & Retry Logic**
- Page load waits work correctly
- Selector waits timeout appropriately
- Retry uses exponential backoff
- Combined flags work together

✅ **Documentation**
- README updated with examples
- SKILL.md has LLM guidance
- Examples directory demonstrates features
- Integration tests pass
- Changelog documents changes

✅ **Backward Compatibility**
- All existing scripts work unchanged
- No breaking changes
- New features are opt-in

---

## Future Enhancements (Not in This Plan)

The following features from the roadmap are **not** included in this implementation:

- Workflow Commands (#2) - Pre-built command bundles
- Chain/Pipeline Support (#5) - Unix-style piping
- Session Management (#6) - Save/restore state
- High-Level Actions (#7) - Declarative interface
- Context-Aware Help (#8) - Smart suggestions
- Error Recovery (#9) - Advanced fault tolerance
- Batch Operations (#10) - Parallel execution

These remain in the roadmap for future iterations.

---

## Notes for Engineer

**Tech Decisions:**
- Using `nc -z` for port checking (portable, no deps)
- `jq` required for JSON validation (assumed installed)
- Exponential backoff: 2^n seconds (2, 4, 8...)
- Default timeout: 10 seconds (customizable)

**Testing Strategy:**
- Integration tests cover happy path
- Examples serve as functional tests
- Manual testing for error cases

**Error Handling:**
- JSON errors always include timestamp
- Wait timeouts provide clear feedback
- Retry shows progress to stderr

**Backward Compatibility:**
- All new flags are optional
- Existing commands work unchanged
- Old output format preserved when --json not used
