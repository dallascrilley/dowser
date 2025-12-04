# Configuration Reference

Complete reference for browser, crawler, and extraction configurations.

## Browser Configuration

```yaml
# browser.yml
headless: true
viewport_width: 1280
viewport_height: 720
user_agent_mode: "random"  # or "custom"
user_agent: "custom user agent string"  # if user_agent_mode is "custom"
ignore_https_errors: true
verbose: true
```

### Browser Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | boolean | `true` | Run browser in headless mode |
| `viewport_width` | integer | 1280 | Browser viewport width in pixels |
| `viewport_height` | integer | 720 | Browser viewport height in pixels |
| `user_agent_mode` | string | default | User agent mode: `"random"`, `"custom"`, or default |
| `user_agent` | string | - | Custom user agent (when mode is `"custom"`) |
| `ignore_https_errors` | boolean | `false` | Ignore HTTPS certificate errors |
| `verbose` | boolean | `false` | Enable verbose browser logging |

**Common Configurations:**

```yaml
# Mobile device
viewport_width: 375
viewport_height: 812
user_agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0...)"

# Desktop
viewport_width: 1920
viewport_height: 1080

# Anti-detection
user_agent_mode: "random"
ignore_https_errors: true
```

## Crawler Configuration

```yaml
# crawler.yml
cache_mode: "bypass"  # or "normal"
wait_until: "networkidle"  # or "load"
page_timeout: 30000
delay_before_return_html: 0.5
word_count_threshold: 100
scan_full_page: false
scroll_delay: 0.3
css_selector: null
process_iframes: false
remove_overlay_elements: false
magic: false
verbose: true
```

### Crawler Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `cache_mode` | string | `"normal"` | Cache strategy: `"bypass"`, `"normal"` |
| `wait_until` | string | `"load"` | Wait condition: `"load"`, `"networkidle"` |
| `page_timeout` | integer | 30000 | Max wait time in milliseconds |
| `delay_before_return_html` | float | 0 | Additional wait after page load (seconds) |
| `word_count_threshold` | integer | 0 | Minimum words per content block |
| `scan_full_page` | boolean | `false` | Scroll to bottom for infinite scroll |
| `scroll_delay` | float | 0.2 | Delay between scroll steps (seconds) |
| `css_selector` | string | null | Target specific page section |
| `process_iframes` | boolean | `false` | Extract content from iframes |
| `remove_overlay_elements` | boolean | `false` | Remove modals and overlays |
| `magic` | boolean | `false` | Enable advanced extraction features |
| `verbose` | boolean | `false` | Enable verbose logging |

### Configuration Presets

**Basic (Static Sites):**
```yaml
cache_mode: "normal"
wait_until: "load"
page_timeout: 30000
delay_before_return_html: 0.5
scan_full_page: false
verbose: true
```

**Dynamic (JavaScript-Heavy):**
```yaml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 60000
delay_before_return_html: 2.0
scan_full_page: true
scroll_delay: 0.5
remove_overlay_elements: true
magic: true
verbose: true
```

**Monitoring (Fast Updates):**
```yaml
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 30000
delay_before_return_html: 1.0
word_count_threshold: 50
scan_full_page: false
verbose: false
```

## Extraction Configuration

### CSS Extraction

```yaml
# extract_css.yml
type: "json-css"
params:
  verbose: true
```

Requires accompanying `schema.json` with CSS selectors.

### LLM Extraction

```yaml
# extract_llm.yml
type: "llm"
provider: "openai/gpt-4"
instruction: "Extract article titles, authors, and summaries"
api_token: "sk-your-api-key"
params:
  temperature: 0.3
  max_tokens: 1000
```

**Supported LLM Providers:**
- `openai/gpt-4` - OpenAI GPT-4 (requires API key)
- `anthropic/claude-3-sonnet` - Claude 3 Sonnet (requires API key)
- `ollama/llama2` - Local Ollama (no API key needed)
- See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for full list

## Filter Configuration

### BM25 Filter

```yaml
# filter_bm25.yml
type: "bm25"
query: "machine learning optimization algorithms"
threshold: 1.0
```

**Use when:** Keyword-based relevance filtering

### Pruning Filter

```yaml
# filter_pruning.yml
type: "pruning"
query: "focus topic keywords"
threshold: 0.48
```

**Use when:** Semantic similarity filtering

## Parameter Selection Guide

### For Static HTML Sites

```yaml
wait_until: "load"
page_timeout: 30000
scan_full_page: false
delay_before_return_html: 0
```

### For Single Page Apps (React/Vue/Angular)

```yaml
wait_until: "networkidle"
page_timeout: 60000
delay_before_return_html: 2.0
remove_overlay_elements: true
```

### For Infinite Scroll Pages

```yaml
scan_full_page: true
scroll_delay: 0.5
wait_until: "networkidle"
page_timeout: 90000
```

### For Content Behind Modals

```yaml
remove_overlay_elements: true
delay_before_return_html: 1.0
```

### For Slow/Heavy Sites

```yaml
page_timeout: 90000
delay_before_return_html: 3.0
wait_until: "networkidle"
```

## Global LLM Configuration

Located at: `~/.crawl4ai/global.yml`

```yaml
default_provider: "openai/gpt-4"
api_token: "sk-your-api-key-here"
```

**For Ollama (local, no API key):**
```yaml
default_provider: "ollama/llama2"
```

## Troubleshooting Configurations

| Problem | Solution |
|---------|----------|
| Timeout errors | Increase `page_timeout`, reduce `scan_full_page` |
| Missing content | Increase `delay_before_return_html`, enable `scan_full_page` |
| Empty extraction | Lower `word_count_threshold`, check `css_selector` |
| Modal blocking content | Enable `remove_overlay_elements` |
| Iframe content missing | Enable `process_iframes` |
| Too slow | Use `css_selector` for targeted extraction, disable `scan_full_page` |
