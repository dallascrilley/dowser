---
name: using-crawl4ai-cli
description: >-
  Extract structured data from websites using crawl4ai CLI. Generate CSS
  extraction schemas, create crawler configs for dynamic content, and build
  complete scraping workflows with Chrome MCP inspection and automated
  validation. Use when scraping websites, extracting product data, monitoring
  content changes, or handling JavaScript-heavy sites. Keywords - crwl, web
  scraping, CSS selectors, Chrome MCP, output validation, XPath, LLM extraction,
  crawl4ai.
when_to_use: >
  Use when extracting structured data from websites (crwl), generating CSS
  schemas, scraping dynamic content, extracting product data, monitoring
  changes, handling JavaScript-heavy sites, or LLM Q&A on pages.
version: 1.0.0
category: research-and-learning
short_description: Extract structured data from websites using crawl4ai CLI.
---

# Crawl4AI CLI Guide

Use crawl4ai CLI (`crwl`) to scrape websites, extract structured data, and handle dynamic JavaScript content. For detailed configuration options, see [references/config-reference.md](references/config-reference.md). For CSS selector guidance, see [references/css-schema-guide.md](references/css-schema-guide.md).

## Prerequisites

**IMPORTANT:** Before using crawl4ai CLI for the first time, verify installation and setup Playwright browsers.

### First-Time Setup

**Option 1: Automated Setup (Recommended)**

Run the included setup script to verify installation and configure everything automatically:

```bash
# Navigate to the scripts directory
cd ~/.claude/skills/using-crawl4ai-cli/scripts

# Run the setup script
./setup.sh

# The script will:
# 1. Verify crwl is installed
# 2. Check crwl --help works
# 3. Detect the Python version crwl uses
# 4. Install Playwright browsers
# 5. Test with a live request
```

**Option 2: Manual Setup**

If you prefer to set up manually:

```bash
# Step 1: Verify crwl is installed and working
crwl --help

# Step 2: Find which Python version crwl uses
which crwl
cat $(which crwl)  # Check the shebang line (first line)

# Step 3: Install Playwright browsers using that Python version
# Automatic detection:
PYTHON_PATH=$(head -1 $(which crwl) | sed 's/#!//')
$PYTHON_PATH -m playwright install chromium

# Or manually (example for Homebrew Python 3.11):
/opt/homebrew/opt/python@3.11/bin/python3.11 -m playwright install chromium

# Step 4: Verify installation
crwl https://example.com -o markdown | head -20
```

**If crwl is not installed:**

```bash
# Using pip
pip install crawl4ai

# Using uv (recommended)
uv pip install crawl4ai

# Then run setup again
```

## Quick Start

```bash
# View page content as markdown
crwl https://example.com -o markdown

# Extract structured data with CSS selectors
crwl https://example.com -e extract_css.yml -s schema.json -o json

# Ask questions about page content (requires LLM setup)
crwl https://example.com -q "What is the main topic?"

# Handle dynamic JavaScript content
crwl https://example.com -c "scan_full_page=true,delay_before_return_html=2"

# Bypass cache for fresh content
crwl https://example.com --bypass-cache -o markdown
```

## Core Tasks

### Get Page Content

```bash
# Basic markdown output
crwl https://example.com -o markdown

# Save to file
crwl https://example.com -o markdown > content.md

# Full metadata (HTML + markdown + metadata)
crwl https://example.com -o all

# Filtered for readability
crwl https://example.com -o markdown-fit
```

**Output Formats:**
- `markdown` / `md` - Clean markdown
- `markdown-fit` / `md-fit` - Filtered for readability
- `json` - Extracted data (when using extraction)
- `all` - Complete crawl result with metadata

### Extract Structured Data

**Setup CSS extraction:**

```bash
# Create extraction config
cat > extract_css.yml << 'EOF'
type: "json-css"
params:
  verbose: true
EOF

# Create schema (or use scripts/generate_schema.py)
cat > schema.json << 'EOF'
{
  "name": "ArticleExtractor",
  "baseSelector": ".article-card",
  "fields": [
    {
      "name": "title",
      "selector": "h2.title",
      "type": "text"
    },
    {
      "name": "link",
      "selector": "a",
      "type": "attribute",
      "attribute": "href"
    }
  ]
}
EOF

# Extract data
crwl https://example.com -e extract_css.yml -s schema.json -o json
```

**Field types:**
- `text` - Extract text content
- `html` - Extract HTML
- `attribute` - Extract attribute value (specify `attribute` key)

**Generate schema interactively:**
```bash
python scripts/generate_schema.py
```

### LLM-Powered Q&A

```bash
# First-time setup (prompted for LLM provider and API key)
crwl https://example.com -q "Summarize this page"

# Ask multiple questions
crwl https://example.com -q "What is the main topic?"
crwl https://example.com -q "List key points in bullet format"

# Use with specific LLM config
cat > extract_llm.yml << 'EOF'
type: "llm"
provider: "openai/gpt-4"
instruction: "Extract article titles and authors"
api_token: "sk-your-key"
EOF

crwl https://example.com -e extract_llm.yml -o json
```

**LLM configuration stored in:** `~/.crawl4ai/global.yml`

**Supported providers:** `openai/gpt-4`, `anthropic/claude-3-sonnet`, `ollama/llama2` (no API key needed)

### Handle Dynamic Content

For JavaScript-heavy sites, infinite scroll, or lazy-loaded content:

```bash
# Basic dynamic handling
crwl https://example.com -c "scan_full_page=true,delay_before_return_html=2"

# Full dynamic config
cat > crawler_dynamic.yml << 'EOF'
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 60000
delay_before_return_html: 2.0
scan_full_page: true
scroll_delay: 0.5
remove_overlay_elements: true
magic: true
verbose: true
EOF

crwl https://example.com -C crawler_dynamic.yml -o markdown
```

**Key parameters:**
- `scan_full_page: true` - Scrolls to bottom for infinite scroll
- `delay_before_return_html: 2.0` - Wait 2s after load for JS
- `wait_until: "networkidle"` - Wait for network activity to stop
- `page_timeout: 60000` - Max wait time (60s)

### Cache Control

```bash
# Force fresh crawl (bypass cache)
crwl https://example.com --bypass-cache -o markdown

# Use cache if available (default)
crwl https://example.com -o markdown
```

### Content Filtering

```bash
# Create filter config
cat > filter_bm25.yml << 'EOF'
type: "bm25"
query: "target keywords here"
threshold: 1.0
EOF

# Apply filter
crwl https://example.com -f filter_bm25.yml -o markdown-fit
```

## Command Reference

**Common flags:**
- `-o <format>` - Output format (markdown, json, all, markdown-fit)
- `-e <file>` - Extraction config (CSS or LLM)
- `-s <file>` - Schema file (CSS or LLM JSON schema)
- `-q <question>` - Ask question about content
- `-c <params>` - Crawler parameters (inline: `key=val,key2=val2`)
- `-C <file>` - Crawler config file (YAML)
- `-b <params>` - Browser parameters (inline)
- `-B <file>` - Browser config file (YAML)
- `-f <file>` - Content filter config
- `-v` - Verbose output
- `--bypass-cache` - Force fresh crawl

**See also:** [references/cli-reference.md](references/cli-reference.md) for complete flag documentation.

## Configuration Files

### Browser Config

```yaml
# browser.yml
headless: true
viewport_width: 1280
user_agent_mode: "random"
ignore_https_errors: true
verbose: true
```

Usage: `crwl URL -B browser.yml`

**See also:** [references/config-reference.md](references/config-reference.md) for all browser options.

### Crawler Config

```yaml
# crawler.yml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 30000
delay_before_return_html: 0.5
word_count_threshold: 100
scan_full_page: false
scroll_delay: 0.3
verbose: true
```

Usage: `crwl URL -C crawler.yml`

**Inline usage:** `crwl URL -c "scan_full_page=true,delay_before_return_html=2"`

## Proven Patterns

**⚠️ MANDATORY:** For ALL patterns below, follow the [Inspect → Extract → Validate workflow](#workflow-requirements).

### Pattern: News Monitoring

```bash
#!/bin/bash
# Monitor news site for updates
# First time: Run ./scripts/inspect_page.sh https://news.example.com

site="https://news.example.com"
timestamp=$(date +"%Y-%m-%d_%H-%M")

# Extract articles
crwl "$site" \
    --bypass-cache \
    -c "wait_until=networkidle,delay_before_return_html=1" \
    -e extract_css.yml \
    -s article_schema.json \
    -o json > "articles_${timestamp}.json"

# Validate extraction
python scripts/validate_extraction.py "articles_${timestamp}.json" --required-fields=title,content

# Generate summary
crwl "$site" --bypass-cache -q "List top 5 trending topics" > "summary_${timestamp}.txt"
```

### Pattern: Product Price Tracking

```bash
#!/bin/bash
# Track product prices
# First time: Run ./scripts/inspect_page.sh https://store.com/product/12345

product_url="https://store.com/product/12345"

# Extract and validate
crwl "$product_url" --bypass-cache -e extract_css.yml -s product_schema.json -o json > current.json
python scripts/validate_extraction.py current.json --required-fields=price,product_name

# Save with timestamp
jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '. + {timestamp: $ts}' current.json >> price_history.jsonl
```

### Pattern: Research Data Collection

```bash
#!/bin/bash
# Collect and analyze research papers
# First time: Run ./scripts/inspect_page.sh https://arxiv.org/list/cs.AI/recent

# Extract papers
crwl "https://arxiv.org/list/cs.AI/recent" -e extract_css.yml -s paper_schema.json -o json > papers.json

# Validate extraction
python scripts/validate_extraction.py papers.json --required-fields=paper_id,title --min-records=5

# Analyze each paper
jq -r '.[].paper_id' papers.json | while read id; do
    crwl "https://arxiv.org/abs/${id}" -q "Summarize methodology, findings, and limitations" > "analysis_${id}.txt"
    sleep 2
done
```

**See also:** [references/patterns.md](references/patterns.md) for more proven workflows.

## Troubleshooting

**Quick fixes for common issues:**

| Issue | Solution |
|-------|----------|
| Navigation contamination | Run `python scripts/validate_extraction.py data.json` to detect, refine `baseSelector` |
| Empty extraction | Use Chrome MCP to verify selectors, add `delay_before_return_html=2` |
| Playwright not found | Run `./scripts/setup.sh` to install browsers |
| Page timeout | Increase timeout: `-c "page_timeout=60000"` |
| LLM not configured | Run `crwl URL -q "test"` to trigger setup wizard |
| Wrong record count | Use Chrome MCP to count expected elements, adjust `baseSelector` |

**For detailed solutions:** [references/troubleshooting.md](references/troubleshooting.md)

## Helper Scripts

**Setup and verify installation:**
```bash
./scripts/setup.sh
```

**Generate extraction schema:**
```bash
python scripts/generate_schema.py
```

**Create crawler config from preset:**
```bash
python scripts/init_crawler.py --preset dynamic
```

**Create extraction config:**
```bash
python scripts/init_extraction.py --type css
```

**Validate configs before running:**
```bash
python scripts/validate_config.py schema.json extract_css.yml
```

## Workflow Requirements

**⚠️ MANDATORY: Always follow this workflow for new sites:**

1. **Inspect first** (before scraping): `./scripts/inspect_page.sh URL` or use Chrome MCP
   - See [references/inspection-guide.md](references/inspection-guide.md) for complete workflow
   
2. **Extract** with validated selectors: `crwl URL -e extract_css.yml -s schema.json -o json > data.json`

3. **Validate** output: `python scripts/validate_extraction.py data.json --required-fields=title,content`

**Why this prevents failures:**
- Step 1 identifies correct selectors (prevents scraping navigation instead of content)
- Step 3 catches schema errors early (saves time before processing large datasets)

---

## Common Workflows

**0. First Time Setup:**
```bash
# Run setup script to verify installation
cd ~/.claude/skills/using-crawl4ai-cli/scripts
./setup.sh

# Verify with crwl --help
crwl --help

# Test basic functionality
crwl https://example.com -o markdown | head -20
```

**1. Preview → Extract → Validate:**
```bash
# Preview structure
crwl URL -o markdown | head -50

# Extract with schema
crwl URL -e extract_css.yml -s schema.json -o json > data.json

# Validate extraction
python scripts/validate_extraction.py data.json --required-fields=title,content

# Analyze if validation passes
crwl URL -q "What insights can you extract from this data?"
```

**2. Dynamic Content Extraction:**
```bash
# Handle JavaScript-rendered content
crwl URL -C crawler_dynamic.yml -e extract_css.yml -s schema.json -o json > results.json

# Validate output
python scripts/validate_extraction.py results.json
```

**3. Content Monitoring:**
```bash
# Crawl and save
crwl URL --bypass-cache -o markdown > "content_$(date +%Y-%m-%d).md"

# Compare changes
diff previous.md current.md

# Get LLM summary
crwl URL -q "What changed since yesterday?"
```

## Tips

**Getting Started:**
- Run `./scripts/setup.sh` on first use to verify installation
- Test with `crwl --help` before starting any scraping work
- Use `crwl https://example.com -o markdown | head -20` to verify Playwright is working

**Speed optimization:**
- Use `css_selector` to target specific sections
- Set `scan_full_page=false` when not needed
- Reduce `page_timeout` for fast sites

**Accuracy:**
- Test selectors in browser DevTools first
- Use verbose mode (`-v`) to debug
- Start with simple schemas, add fields incrementally

**Cost reduction (LLM):**
- Use filtering (`-f`) before LLM extraction
- Try CSS extraction first, LLM for complex cases
- Consider local `ollama` for free LLM processing

**See also:**
- [scripts/README.md](scripts/README.md) - Helper scripts documentation
- [references/cli-reference.md](references/cli-reference.md) - Complete CLI documentation
- [references/config-reference.md](references/config-reference.md) - All configuration options
- [references/css-schema-guide.md](references/css-schema-guide.md) - CSS selector reference
- [references/patterns.md](references/patterns.md) - Proven workflows
- [references/troubleshooting.md](references/troubleshooting.md) - Solutions to common issues
