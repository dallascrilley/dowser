# Crawl4AI CLI Helper Scripts

Collection of utility scripts to help with crawl4ai setup, configuration, and usage.

## Setup Script

### setup.sh

**Purpose:** Verify crawl4ai installation and configure Playwright browsers.

**When to use:** Run this script after installing crawl4ai for the first time, or if you encounter Playwright browser errors.

**Usage:**
```bash
./setup.sh
```

**What it does:**
1. ✓ Verifies `crwl` command is installed
2. ✓ Checks `crwl --help` works correctly
3. ✓ Detects the Python version used by crwl
4. ✓ Installs Playwright Chromium browser for that Python version
5. ✓ Tests crawl4ai with a live request to example.com
6. ✓ Displays success message with example commands

**Exit codes:**
- `0` - Success, everything is configured correctly
- `1` - Error occurred (check error messages)

---

## Workflow Scripts

### inspect_page.sh

**Purpose:** Display Chrome MCP inspection workflow guide for identifying selectors.

**When to use:** Before scraping any new site to identify correct CSS selectors.

**Usage:**
```bash
./inspect_page.sh https://example.com
```

**Output:** Checklist and instructions for inspecting page structure with Chrome MCP.

---

### validate_extraction.py

**Purpose:** Validate crawl4ai extraction output quality with comprehensive error detection.

**When to use:** After extraction to verify output quality before further processing.

**Usage:**
```bash
# Basic validation
python validate_extraction.py data.json

# With required fields check
python validate_extraction.py data.json --required-fields=title,content

# With minimum record count
python validate_extraction.py data.json --min-records=10 --required-fields=title,content
```

**Checks:**
- JSON format validity
- Minimum record count
- Required fields populated
- Navigation contamination detection
- Empty field detection

**Exit codes:**
- `0` - Validation passed
- `1` - Validation failed (with helpful error messages)

---

## Configuration Scripts

### generate_schema.py

**Purpose:** Interactively create CSS extraction schemas for structured data extraction.

**Usage:**
```bash
python generate_schema.py
```

**Prompts for:**
- Schema name
- Base selector (container element)
- Field definitions (name, selector, type)
- Output filename

**Output:** JSON schema file for use with `crwl -s schema.json`

---

### init_crawler.py

**Purpose:** Create crawler configuration files from presets.

**Usage:**
```bash
python init_crawler.py --preset dynamic
python init_crawler.py --preset fast
python init_crawler.py --preset thorough
```

**Presets:**
- `dynamic` - For JavaScript-heavy sites with infinite scroll
- `fast` - For quick scraping with minimal wait times
- `thorough` - For comprehensive crawling with longer timeouts

**Output:** YAML crawler configuration file

---

### init_extraction.py

**Purpose:** Create extraction configuration files for CSS or LLM-based extraction.

**Usage:**
```bash
python init_extraction.py --type css
python init_extraction.py --type llm
```

**Types:**
- `css` - CSS selector-based extraction (requires schema)
- `llm` - LLM-powered extraction with natural language instructions

**Output:** YAML extraction configuration file

---

### validate_config.py

**Purpose:** Validate schema and configuration files before running crawl4ai.

**Usage:**
```bash
python validate_config.py schema.json extract_css.yml
python validate_config.py schema.json
python validate_config.py extract_css.yml
```

**Checks:**
- JSON schema structure and required fields
- YAML configuration syntax
- Field type validity
- Selector format

**Exit codes:**
- `0` - All validations passed
- `1` - Validation errors found

---

## Common Workflows

### First-Time Setup
```bash
# Run setup script
./setup.sh
```

### Create New Extraction Pipeline
```bash
# 1. Inspect page to identify selectors
./inspect_page.sh https://example.com

# 2. Generate schema interactively
python generate_schema.py

# 3. Create extraction config
python init_extraction.py --type css

# 4. Validate before running
python validate_config.py my_schema.json extract_css.yml

# 5. Test extraction
crwl https://example.com -e extract_css.yml -s my_schema.json -o json > data.json

# 6. Validate extraction output
python validate_extraction.py data.json --required-fields=title,content
```

### Setup Dynamic Content Scraper
```bash
# 1. Create dynamic crawler config
python init_crawler.py --preset dynamic

# 2. Generate extraction schema
python generate_schema.py

# 3. Test with dynamic site
crwl https://dynamic-site.com -C crawler_dynamic.yml -e extract_css.yml -s schema.json -o json
```

---

## Troubleshooting

**Script not executable:**
```bash
chmod +x setup.sh
```

**Python scripts not found:**
```bash
# Ensure you're in the scripts directory
cd ~/.claude/skills/using-crawl4ai-cli/scripts

# Or use full path
python /path/to/scripts/generate_schema.py
```

**Module import errors:**
```bash
# Install required dependencies
pip install crawl4ai
# or
uv pip install crawl4ai
```

---

## Contributing

To add new helper scripts:

1. Create the script with clear documentation
2. Make it executable: `chmod +x script_name.sh`
3. Add usage documentation to this README
4. Update the main SKILL.md file with references
