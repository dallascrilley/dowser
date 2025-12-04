# Proven Patterns

Production-tested workflows for common crawl4ai CLI use cases.

## News Monitoring

Monitor news sites for updates and generate summaries.

```bash
#!/bin/bash
site="https://techcrunch.com"
timestamp=$(date +"%Y-%m-%d_%H-%M")
output_dir="news_archive"
mkdir -p "$output_dir"

# Extract articles
cat > article_schema.json << 'EOF'
{
  "name": "NewsArticles",
  "baseSelector": "article.post-block",
  "fields": [
    {"name": "title", "selector": "h2.post-block__title", "type": "text"},
    {"name": "link", "selector": "a.post-block__title__link", "type": "attribute", "attribute": "href"},
    {"name": "excerpt", "selector": ".post-block__content", "type": "text"}
  ]
}
EOF

cat > extract_css.yml << 'EOF'
type: "json-css"
params:
  verbose: true
EOF

crwl "$site" \
    --bypass-cache \
    -c "wait_until=networkidle,delay_before_return_html=1" \
    -e extract_css.yml \
    -s article_schema.json \
    -o json > "$output_dir/articles_${timestamp}.json"

# Generate summary
crwl "$site" \
    --bypass-cache \
    -q "List the top 5 trending topics from today's articles in bullet points" \
    > "$output_dir/summary_${timestamp}.txt"

# Report
count=$(jq '. | length' "$output_dir/articles_${timestamp}.json")
echo "✓ Extracted $count articles"
```

**Automate with cron:**
```bash
# Run daily at 9 AM
0 9 * * * /path/to/news_monitor.sh
```

## Product Price Tracking

Track product prices and alert on changes.

```bash
#!/bin/bash
product_url="https://store.com/product/12345"
price_file="price_history.jsonl"

# Schema
cat > product_schema.json << 'EOF'
{
  "name": "ProductPrice",
  "baseSelector": ".product-details",
  "fields": [
    {"name": "name", "selector": "h1.product-name", "type": "text"},
    {"name": "price", "selector": ".price-current", "type": "text"},
    {"name": "in_stock", "selector": ".stock-status", "type": "text"}
  ]
}
EOF

cat > extract_css.yml << 'EOF'
type: "json-css"
params:
  verbose: true
EOF

# Extract current price
current=$(crwl "$product_url" \
    --bypass-cache \
    -c "wait_until=networkidle" \
    -e extract_css.yml \
    -s product_schema.json \
    -o json)

# Save with timestamp
timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "$current" | jq --arg ts "$timestamp" '. + {timestamp: $ts}' >> "$price_file"

# Parse and compare
current_price=$(echo "$current" | jq -r '.[0].price // "0"' | tr -d '$,' | sed 's/[^0-9.]//g')
product_name=$(echo "$current" | jq -r '.[0].name // "Unknown"')

echo "Current: $product_name - \$$current_price"

# Compare with previous
if [ -f "$price_file" ] && [ $(wc -l < "$price_file") -gt 1 ]; then
    previous_price=$(tail -2 "$price_file" | head -1 | jq -r '.[0].price // "0"' | tr -d '$,' | sed 's/[^0-9.]//g')

    if command -v bc &> /dev/null && [ "$previous_price" != "0" ]; then
        change=$(echo "scale=2; (($current_price - $previous_price) / $previous_price) * 100" | bc)

        if (( $(echo "$change < -5" | bc -l) )); then
            echo "🎉 Price dropped by ${change#-}%!"
        fi
    fi
fi
```

**Automate:**
```bash
# Check every 6 hours
0 */6 * * * /path/to/price_monitor.sh
```

## Research Data Collection

Collect and analyze research papers with filtering.

```bash
#!/bin/bash
base_url="https://arxiv.org/list/cs.AI/recent"
output_dir="research_papers"
mkdir -p "$output_dir"

# Filter config
cat > filter_research.yml << 'EOF'
type: "bm25"
query: "machine learning optimization algorithms neural networks"
threshold: 1.0
EOF

# Schema
cat > paper_schema.json << 'EOF'
{
  "name": "ResearchPapers",
  "baseSelector": "dd",
  "fields": [
    {"name": "title", "selector": ".list-title", "type": "text"},
    {"name": "authors", "selector": ".list-authors", "type": "text"},
    {"name": "abstract", "selector": ".abstract-full", "type": "text"},
    {"name": "paper_id", "selector": "a[href*='/abs/']", "type": "attribute", "attribute": "href"}
  ]
}
EOF

cat > extract_css.yml << 'EOF'
type: "json-css"
params:
  verbose: true
EOF

# Extract papers
crwl "$base_url" \
    --bypass-cache \
    -e extract_css.yml \
    -s paper_schema.json \
    -f filter_research.yml \
    -o json > "$output_dir/papers_raw.json"

# Analyze each paper
jq -r '.[].paper_id' "$output_dir/papers_raw.json" | while read paper_url; do
    paper_id=$(basename "$paper_url")
    echo "Analyzing: $paper_id"

    crwl "https://arxiv.org${paper_url}" \
        -q "Summarize this research paper's methodology, key findings, and limitations in 3 paragraphs" \
        > "$output_dir/analysis_${paper_id}.txt"

    sleep 2  # Rate limiting
done

paper_count=$(jq '. | length' "$output_dir/papers_raw.json")
echo "✓ Collected $paper_count papers"
```

## Content Change Detection

Monitor webpage changes and send notifications.

```bash
#!/bin/bash
url="https://example.com/terms-of-service"
cache_dir="content_snapshots"
diff_dir="content_changes"
mkdir -p "$cache_dir" "$diff_dir"

date_str=$(date +"%Y-%m-%d")
current_file="$cache_dir/content_${date_str}.md"
previous_file=$(ls -t "$cache_dir"/content_*.md 2>/dev/null | head -1)

# Crawl current version
crwl "$url" \
    --bypass-cache \
    -c "wait_until=networkidle" \
    -o markdown > "$current_file"

# Compare
if [ -n "$previous_file" ] && [ "$previous_file" != "$current_file" ]; then
    if ! diff -q "$previous_file" "$current_file" > /dev/null 2>&1; then
        echo "⚡ Changes detected!"

        # Generate diff
        diff_file="$diff_dir/diff_${date_str}.txt"
        diff -u "$previous_file" "$current_file" > "$diff_file"

        # Get AI summary
        change_summary=$(crwl "$url" -q "What are the main differences between this version and the previous version?")

        echo "$change_summary" > "$diff_dir/summary_${date_str}.txt"
        echo "✓ Change report saved"
    else
        echo "✓ No changes"
    fi
else
    echo "ℹ️ First run - baseline created"
fi

# Cleanup old snapshots (keep 30 days)
find "$cache_dir" -name "content_*.md" -mtime +30 -delete
```

## Infinite Scroll Products

Handle infinite scroll with dynamic content loading.

```bash
#!/bin/bash
# Extract all products from infinite scroll page

cat > product_schema.json << 'EOF'
{
  "name": "Products",
  "baseSelector": ".product-card",
  "fields": [
    {"name": "name", "selector": "h3.product-title", "type": "text"},
    {"name": "price", "selector": ".price-current", "type": "text"},
    {"name": "rating", "selector": "[data-rating]", "type": "attribute", "attribute": "data-rating"},
    {"name": "image", "selector": "img.product-image", "type": "attribute", "attribute": "src"}
  ]
}
EOF

cat > crawler_dynamic.yml << 'EOF'
cache_mode: "bypass"
wait_until: "networkidle"
page_timeout: 90000
delay_before_return_html: 3.0
scan_full_page: true
scroll_delay: 0.8
remove_overlay_elements: true
verbose: true
EOF

cat > extract_css.yml << 'EOF'
type: "json-css"
params:
  verbose: true
EOF

crwl "https://store.com/products" \
    -C crawler_dynamic.yml \
    -e extract_css.yml \
    -s product_schema.json \
    -o json > products.json

count=$(jq '. | length' products.json)
echo "✓ Extracted $count products"
```

## Multi-Page Scraping

Scrape multiple related pages.

```bash
#!/bin/bash
# Scrape product details from multiple pages

base_url="https://store.com/product/"
product_ids=(12345 12346 12347 12348)

for id in "${product_ids[@]}"; do
    echo "Scraping product $id..."

    crwl "${base_url}${id}" \
        -e extract_css.yml \
        -s product_schema.json \
        -o json > "product_${id}.json"

    sleep 2  # Rate limiting
done

# Combine all products
jq -s '.' product_*.json > all_products.json
echo "✓ Combined $(jq '. | length' all_products.json) products"
```

## Authentication Required

Note: crawl4ai CLI doesn't directly support authentication. Use these workarounds:

**Option 1: Extract from logged-in browser**
```bash
# In browser: Log in and copy cookies
# Use browser config to set cookies (if supported by future versions)
```

**Option 2: Public endpoints only**
```bash
# Only scrape publicly accessible pages
# Use API endpoints if available instead
```

## Performance Optimization

**Targeted extraction (fast):**
```bash
crwl URL -c "css_selector=#main-content" -o markdown
```

**Parallel scraping:**
```bash
#!/bin/bash
urls=(url1 url2 url3)

for url in "${urls[@]}"; do
    crwl "$url" -o json > "output_$(echo $url | md5).json" &
done

wait  # Wait for all background jobs
echo "✓ All scrapes complete"
```
