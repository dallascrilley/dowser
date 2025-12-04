# Real-World Examples

## Example 1: using-crawl4ai-cli Skill

**Tool:** crawl4ai CLI for web scraping

**Analysis highlights:**
- Common pitfall: Scraping navigation instead of content
- Critical workflow: Inspect → Extract → Validate
- Key feature: Dynamic content handling

**Helper scripts created:**
- `setup.sh` - Verify installation, setup Playwright
- `generate_schema.py` - Interactive schema builder
- `validate_extraction.py` - Validate scraped data
- `inspect_page.sh` - Inspect page before scraping

**Templates created:**
- `crawler_basic.yml` - Simple crawling
- `crawler_dynamic.yml` - JavaScript-heavy sites
- `extract_css.yml` - CSS extraction config
- `schema_simple.json` - Basic schema example

**Guardrails implemented:**
- ⚠️ MANDATORY: Inspect → Extract → Validate workflow
- Validation script catches schema errors early
- Setup script ensures prerequisites

**Result:** Users can scrape complex sites without common mistakes.

## Example 2: jq JSON Processor (Complete Walkthrough)

**Tool:** jq - Command-line JSON processor

**Phase 1: Documentation Gathering**
- Extracted from official jq manual
- Combined multiple sections into cohesive document

**Phase 2: Analysis**
- **Tool Overview:** JSON transformation and querying
- **Command Patterns:** `jq [OPTIONS] FILTER [FILE]`
- **Workflows:** Filtering, transforming, combining JSON
- **Pitfalls:** Complex filter syntax, array vs object handling
- **Best Practices:** Use `-r` for raw output, `-c` for compact

**Phase 3: Design**
- **Helper Scripts:** `validate_json.py`, `jq_examples.sh`
- **Templates:** `basic_filter.jq`, `advanced_transform.jq`
- **Guardrails:** Validate JSON before processing
- **References:** CLI reference, filter patterns guide

**Phase 4: Generation**
- Generated all scripts and templates
- Created comprehensive reference docs

**Phase 5: SKILL.md**
- Quick start with common examples
- Core tasks (filter, transform, combine)
- Proven patterns for common use cases

**Phase 6: Testing**
- Verified all examples work
- Tested helper scripts
- Validated templates

## Example 3: ripgrep Skill (Hypothetical)

**Tool:** ripgrep - Fast text search

**Analysis highlights:**
- Common pitfall: Case sensitivity issues
- Common pitfall: Regex escaping
- Best practice: Use `-i` for case-insensitive
- Critical workflow: Search → Filter → Context

**Helper scripts to create:**
- `setup.sh` - Configure ripgrep, verify installation
- `validate_pattern.py` - Check regex patterns
- `search_context.sh` - Search with context lines

**Templates to create:**
- `ripgrep_basic.sh` - Basic search patterns
- `ripgrep_advanced.sh` - Complex search workflows

**Guardrails to implement:**
- ⚠️ MANDATORY: Test pattern before large search
- Validation script checks regex syntax
- Setup script verifies ripgrep version

## Key Patterns from Examples

### Pattern 1: Setup Scripts
All examples include setup scripts that:
- Verify tool installation
- Check dependencies
- Validate configuration
- Provide clear error messages

### Pattern 2: Validation Scripts
Common validation needs:
- Input format validation (JSON, regex, config)
- Schema validation
- Prerequisite checking

### Pattern 3: Guardrails
Effective guardrails:
- Mandatory workflows for error-prone operations
- Validation gates before critical steps
- Clear "why this prevents failures" explanations

### Pattern 4: Progressive Disclosure
All examples follow:
- SKILL.md = quick reference with examples
- references/ = detailed documentation
- Helper scripts = automation for common tasks

**See:** `examples/example-analysis.md` for complete jq walkthrough

