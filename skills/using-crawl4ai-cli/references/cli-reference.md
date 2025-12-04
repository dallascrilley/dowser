# Crawl4AI CLI Reference

Complete command-line flag reference for `crwl` command.

## Basic Usage

```bash
crwl URL [OPTIONS]
```

## Output Flags

| Flag | Values | Description |
|------|--------|-------------|
| `-o`, `--output` | `markdown`, `md`, `markdown-fit`, `md-fit`, `json`, `all` | Output format (default: `all`) |
| `-v`, `--verbose` | - | Enable verbose output with debug info |

**Output Format Details:**
- `markdown` / `md` - Clean markdown content only
- `markdown-fit` / `md-fit` - Filtered markdown for better readability
- `json` - Extracted structured data (requires extraction config)
- `all` - Complete crawl result including HTML, markdown, and metadata

## Extraction Flags

| Flag | Argument | Description |
|------|----------|-------------|
| `-e`, `--extract` | `file.yml` | Extraction config file (CSS or LLM) |
| `-s`, `--schema` | `schema.json` | Schema file for extraction |
| `-q`, `--question` | `"text"` | Ask LLM question about page content |
| `-f`, `--filter` | `filter.yml` | Content filter config (BM25 or pruning) |

## Crawler Configuration Flags

| Flag | Argument | Description |
|------|----------|-------------|
| `-C`, `--crawler-config` | `crawler.yml` | Crawler config file (YAML) |
| `-c`, `--crawler-params` | `"key=val,key2=val2"` | Inline crawler parameters |

**Inline Parameter Format:**
```bash
crwl URL -c "scan_full_page=true,delay_before_return_html=2,page_timeout=60000"
```

## Browser Configuration Flags

| Flag | Argument | Description |
|------|----------|-------------|
| `-B`, `--browser-config` | `browser.yml` | Browser config file (YAML) |
| `-b`, `--browser-params` | `"key=val"` | Inline browser parameters |

## Cache Flags

| Flag | Description |
|------|-------------|
| `--bypass-cache` | Force fresh crawl, ignore cached content |

## Help and Examples

| Flag | Description |
|------|-------------|
| `--help` | Show help message |
| `--example` | Show usage examples |

## Common Command Patterns

**Quick content preview:**
```bash
crwl https://example.com -o markdown
```

**Structured data extraction:**
```bash
crwl https://example.com -e extract_css.yml -s schema.json -o json
```

**LLM Q&A:**
```bash
crwl https://example.com -q "Summarize key points"
```

**Dynamic content with fresh data:**
```bash
crwl https://example.com --bypass-cache -c "scan_full_page=true,delay_before_return_html=2"
```

**Full configuration:**
```bash
crwl https://example.com \
    -B browser.yml \
    -C crawler.yml \
    -e extract_css.yml \
    -s schema.json \
    -f filter.yml \
    -o json
```

## Parameter Precedence

When using both config files and inline parameters:
1. Inline parameters (`-c`, `-b`) override config file values
2. Config files (`-C`, `-B`) provide base configuration
3. Default values apply when neither is specified

**Example:**
```bash
# crawler.yml has page_timeout: 30000
# This command overrides it to 60000
crwl URL -C crawler.yml -c "page_timeout=60000"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Crawl failed or error occurred |
| 2 | Invalid arguments or configuration |
