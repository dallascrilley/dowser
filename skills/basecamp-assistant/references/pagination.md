# Basecamp 4 API - Pagination Guide

**Last Updated:** November 11, 2025
**Purpose:** Master RFC5988 Link headers for safe pagination
**Critical Rule:** NEVER construct pagination URLs manually

---

## Table of Contents

1. [RFC5988 Link Headers](#rfc5988-link-headers)
2. [Geared Pagination](#geared-pagination)
3. [Extraction Patterns](#extraction-patterns)
4. [Complete Loop Examples](#complete-loop-examples)
5. [Common Mistakes](#common-mistakes)
6. [Advanced Patterns](#advanced-patterns)
7. [Troubleshooting](#troubleshooting)

---

## RFC5988 Link Headers

### What Are Link Headers?

Link headers are HTTP headers that tell clients how to navigate between pages of results. They follow RFC 5988 specification.

**Example:**
```http
HTTP/1.1 200 OK
Link: <https://3.basecampapi.com/195539477/projects.json?page=2>; rel="next"
X-Total-Count: 150
Content-Type: application/json

[
  { "id": 1, "name": "Project 1" },
  { "id": 2, "name": "Project 2" }
]
```

### Link Header Components

```
Link: <{url}>; rel="{relation}"

Components:
- <{url}>    = The URL to fetch next (enclosed in angle brackets)
- rel="{x}"  = Relationship type (next, prev, first, last)
```

### Relationship Types

| Relation | Meaning | Usage |
|----------|---------|-------|
| `next` | URL for the next page | Always present except on last page |
| `prev` | URL for previous page | Present on pages 2+ |
| `first` | URL for first page | Always same |
| `last` | URL for last page | Points to final page |

### Other Headers

**X-Total-Count:** Total number of items across all pages
```
X-Total-Count: 150  # 150 total items
```

**X-Per-Page:** Number of items in this page
```
X-Per-Page: 30  # This page has 30 items
```

---

## Geared Pagination

### What is Geared Pagination?

Geared pagination means page sizes vary based on the collection size. Basecamp uses this strategy:

- Small collections: 15 items per page
- Medium collections: 30 items per page
- Large collections: 50 items per page
- Very large collections: 100+ items per page

### Why Geared Pagination?

This approach:
- Reduces total number of requests for small collections
- Provides finer granularity for large collections
- Optimizes API performance
- Can change between requests

### Why You Can't Predict Page Size

```
❌ WRONG - Assuming fixed page size
GET /projects.json?page=1 → 30 items returned
GET /projects.json?page=2 → 50 items returned (different!)
GET /projects.json?page=3 → 15 items returned (different!)

Your assumption that each page has 30 items is wrong!

✅ CORRECT - Follow Link header
Response 1: Link: <...?page=2>; rel="next"  → 30 items
Response 2: Link: <...?page=3>; rel="next"  → 50 items
Response 3: No Link header → last page
```

### The Critical Rule

> **NEVER construct pagination URLs manually. Always extract from Link header.**

Why this matters:
- URL parameters may change
- Page numbering may not be sequential
- Basecamp may add new parameters
- Constructed URLs may skip or duplicate results
- API may reject manually constructed URLs

---

## Extraction Patterns

### Pattern 1: Bash with Grep and Sed

```bash
extract_next_url() {
  local response=$1

  # Extract URL from Link header's rel="next"
  echo "$response" | grep -i "^Link:" | \
    sed -n 's/.*<\(.*\)>; rel="next".*/\1/p'
}

# Usage
response=$(curl -i -H "..." "$url")
next_url=$(extract_next_url "$response")

if [ ! -z "$next_url" ]; then
  echo "Next page URL: $next_url"
else
  echo "No next page (last page reached)"
fi
```

### Pattern 2: Bash with Regex

```bash
extract_next_url_regex() {
  local response=$1

  # Using extended regex
  if [[ "$response" =~ \<([^>]+)\>;[[:space:]]*rel=\"next\" ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
}
```

### Pattern 3: Python

```python
import re

def extract_next_url(response_headers):
    """Extract next page URL from Link header"""

    link_header = response_headers.get('Link', '')

    # Parse Link header for rel="next"
    match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)

    if match:
        return match.group(1)

    return None

# Usage with requests library
import requests

response = requests.get(url, headers=headers)
next_url = extract_next_url(response.headers)

if next_url:
    print(f"Next page: {next_url}")
else:
    print("No next page")
```

### Pattern 4: JavaScript/Node.js

```javascript
function extractNextUrl(linkHeader) {
  // Parse Link header for rel="next"
  const match = linkHeader.match(/<([^>]+)>;\s*rel="next"/);

  if (match) {
    return match[1];
  }

  return null;
}

// Usage with fetch
const response = await fetch(url, { headers });
const linkHeader = response.headers.get('Link') || '';
const nextUrl = extractNextUrl(linkHeader);

if (nextUrl) {
  console.log(`Next page: ${nextUrl}`);
} else {
  console.log('No next page');
}
```

### Pattern 5: Ruby

```ruby
def extract_next_url(link_header)
  # Parse Link header for rel="next"
  link_header.match(/<([^>]+)>;\s*rel="next"/)&.captures&.first
end

# Usage
response = RestClient.get(url, headers)
next_url = extract_next_url(response.headers[:link])

if next_url
  puts "Next page: #{next_url}"
else
  puts "No next page"
end
```

---

## Complete Loop Examples

### Example 1: Basic Pagination Loop (Bash)

```bash
#!/bin/bash

# Load configuration
source .env

# Initialize
url="https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
all_data="[]"
page=1

echo "Fetching all projects..."

while [ ! -z "$url" ]; do
  echo "  Page $page..."

  # Make request with headers
  response=$(curl -s -i \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "User-Agent: $USER_AGENT" \
    "$url")

  # Extract body (starts with [)
  body=$(echo "$response" | sed -n '/^\[/,$p')

  # Merge into all_data
  all_data=$(echo "$all_data" "$body" | jq -s 'add')

  # Extract next URL from Link header
  url=$(echo "$response" | grep -i "^Link:" | \
    sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')

  page=$((page + 1))

  # Safety check (prevent infinite loops)
  if [ $page -gt 100 ]; then
    echo "Warning: Stopping at page 100 for safety"
    break
  fi
done

# Display results
total=$(echo "$all_data" | jq 'length')
echo "✓ Fetched $total projects"

echo "$all_data" | jq '.[] | {id, name}'
```

### Example 2: Python with Requests

```python
import requests
import re

def fetch_all_pages(initial_url, headers):
    """Fetch all pages following Link headers"""

    all_data = []
    url = initial_url
    page_count = 0

    while url:
        print(f"Fetching page {page_count + 1}: {url}")

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            break

        # Collect data
        page_data = response.json()
        all_data.extend(page_data)

        # Extract next URL from Link header
        link_header = response.headers.get('Link', '')
        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)

        url = match.group(1) if match else None

        page_count += 1

        # Safety limit
        if page_count > 100:
            print("Warning: Stopping at 100 pages for safety")
            break

    print(f"✓ Fetched {len(all_data)} total items")
    return all_data

# Usage
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'User-Agent': USER_AGENT
}

projects = fetch_all_pages(
    f'https://3.basecampapi.com/{ACCOUNT_ID}/projects.json',
    headers
)

for project in projects:
    print(f"  - {project['name']} (ID: {project['id']})")
```

### Example 3: Stream Processing (Large Collections)

```python
def stream_pages(initial_url, headers):
    """Generator that yields items from each page"""

    url = initial_url
    page_count = 0

    while url:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            break

        # Yield each item from this page
        for item in response.json():
            yield item

        # Get next page URL
        link_header = response.headers.get('Link', '')
        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
        url = match.group(1) if match else None

        page_count += 1

# Usage - Process large collection without loading everything into memory
for project in stream_pages(projects_url, headers):
    print(f"Processing: {project['name']}")
    # Process immediately, don't accumulate
```

### Example 4: Handle Rate Limits in Pagination

```python
def fetch_all_pages_with_rate_limiting(initial_url, headers):
    """Fetch all pages with rate limit handling"""

    import time

    all_data = []
    url = initial_url

    while url:
        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 2))
                print(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue  # Retry same URL

            elif response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                break

            # Process successful response
            all_data.extend(response.json())

            # Get next URL
            link_header = response.headers.get('Link', '')
            match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
            url = match.group(1) if match else None

        except requests.RequestException as e:
            print(f"Request error: {e}")
            break

    return all_data
```

---

## Common Mistakes

### Mistake 1: Manually Constructing URLs

```python
# ❌ WRONG - Never do this
for page_num in range(1, 11):
    url = f"https://3.basecampapi.com/{account_id}/projects.json?page={page_num}"
    response = requests.get(url, headers=headers)
    # This may skip or duplicate items!
    # Page numbers may not be sequential!
```

**Why it's wrong:**
- Basecamp doesn't guarantee sequential page numbers
- Page sizes vary (geared pagination)
- Constructed URLs may not match API's expectations
- Could skip or duplicate results

**Correct approach:**
```python
# ✅ CORRECT - Always follow Link header
url = f"https://3.basecampapi.com/{account_id}/projects.json"

while url:
    response = requests.get(url, headers=headers)

    # Process data
    for item in response.json():
        yield item

    # Get NEXT URL from Link header, not constructed
    link = response.headers.get('Link', '')
    match = re.search(r'<([^>]+)>;\s*rel="next"', link)
    url = match.group(1) if match else None
```

### Mistake 2: Not Checking for Empty Link Header

```python
# ❌ WRONG - Assumes Link header always present
while True:
    response = requests.get(url, headers=headers)
    link = response.headers.get('Link', '')
    match = re.search(r'<([^>]+)>;\s*rel="next"', link)
    url = match.group(1) if match else None
    # This may loop forever if not careful!
```

**Correct approach:**
```python
# ✅ CORRECT - Break when no next link
while True:
    response = requests.get(url, headers=headers)

    # Process response
    for item in response.json():
        yield item

    # Check for next page
    link = response.headers.get('Link', '')
    match = re.search(r'<([^>]+)>;\s*rel="next"', link)

    if match:
        url = match.group(1)
    else:
        # No next link = last page reached
        break
```

### Mistake 3: Not Handling Rate Limits

```python
# ❌ WRONG - Ignores rate limits
while url:
    response = requests.get(url, headers=headers)
    # May get 429 and then crash or loop infinitely
```

**Correct approach:**
```python
# ✅ CORRECT - Handle 429 with retry
while url:
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        time.sleep(retry_after)
        continue  # Retry same URL

    # Process response...
```

### Mistake 4: Accumulating All Data Without Limit

```python
# ❌ WRONG - Loads everything into memory
all_data = []
while url:
    response = requests.get(url, headers=headers)
    all_data.extend(response.json())  # May use too much memory!
    # Get next URL...
```

**Correct approach for large collections:**
```python
# ✅ CORRECT - Use generator for large collections
def get_all_items(initial_url, headers):
    url = initial_url
    while url:
        response = requests.get(url, headers=headers)

        # Yield items one by one
        for item in response.json():
            yield item

        # Get next URL...

# Process without loading everything
for item in get_all_items(url, headers):
    process_item(item)  # Handle one at a time
```

### Mistake 5: Not Implementing Safety Limits

```python
# ❌ WRONG - Could loop forever on bugs
page = 0
while url:
    response = requests.get(url, headers=headers)
    # ... extract next_url...
    page += 1
    # No safety check!
```

**Correct approach:**
```python
# ✅ CORRECT - Add safety limit
page = 0
max_pages = 1000  # Safety limit

while url and page < max_pages:
    response = requests.get(url, headers=headers)

    # ... extract next_url...

    page += 1

if page >= max_pages:
    print("Warning: Stopped at page limit for safety")
```

---

## Advanced Patterns

### Pattern 1: Parallel Pagination

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_page_parallel(url, headers):
    """Fetch a single page"""
    response = requests.get(url, headers=headers)
    return response.json(), response.headers.get('Link', '')

def parallel_fetch_all(initial_url, headers, max_workers=3):
    """Fetch pages in parallel"""

    all_data = []
    to_fetch = [initial_url]
    fetched = set()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        while to_fetch or futures:
            # Submit new requests
            while to_fetch and len(futures) < max_workers:
                url = to_fetch.pop(0)

                if url in fetched:
                    continue  # Already fetching or fetched

                fetched.add(url)
                future = executor.submit(fetch_page_parallel, url, headers)
                futures[future] = url

            # Process completed requests
            for future in as_completed(futures):
                data, link_header = future.result()
                all_data.extend(data)

                # Extract next URL
                match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                if match:
                    next_url = match.group(1)
                    if next_url not in fetched:
                        to_fetch.append(next_url)

                del futures[future]

    return all_data
```

### Pattern 2: Pagination with Caching

```python
import json
from datetime import datetime, timedelta

class CachedPagination:
    """Fetch pages with caching"""

    def __init__(self, cache_dir='/tmp/basecamp_cache'):
        self.cache_dir = cache_dir

    def get_cache_key(self, url):
        """Generate cache key for URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()

    def get_cached(self, url, max_age_seconds=3600):
        """Get cached page if not expired"""
        cache_key = self.get_cache_key(url)
        cache_file = f"{self.cache_dir}/{cache_key}.json"

        try:
            stat = os.stat(cache_file)
            age = (datetime.now().timestamp() - stat.st_mtime)

            if age < max_age_seconds:
                with open(cache_file) as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        return None

    def set_cache(self, url, data):
        """Cache page data"""
        cache_key = self.get_cache_key(url)
        cache_file = f"{self.cache_dir}/{cache_key}.json"

        os.makedirs(self.cache_dir, exist_ok=True)

        with open(cache_file, 'w') as f:
            json.dump(data, f)

    def fetch_all(self, initial_url, headers, max_age=3600):
        """Fetch all pages with caching"""

        all_data = []
        url = initial_url

        while url:
            # Check cache first
            cached = self.get_cached(url, max_age)

            if cached:
                print(f"Cache hit: {url}")
                page_data, link_header = cached
            else:
                print(f"Fetching: {url}")
                response = requests.get(url, headers=headers)
                page_data = response.json()
                link_header = response.headers.get('Link', '')
                self.set_cache(url, (page_data, link_header))

            all_data.extend(page_data)

            # Get next URL
            match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
            url = match.group(1) if match else None

        return all_data
```

---

## Troubleshooting

### Issue: No Link Header in Response

**Symptom:** Link header is missing

**Causes:**
- Last page has no next link (this is normal)
- API error prevented full response
- Response header not captured

**Debug:**
```bash
# Check all headers
curl -i -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "$url" | head -20
```

**Fix:**
```python
link = response.headers.get('Link', '')
if not link:
    print("No Link header (last page)")
    # This is normal - stop pagination
else:
    # Parse Link header
```

### Issue: Infinite Loop in Pagination

**Symptom:** Pagination never stops

**Causes:**
- Same URL returned in Link header
- Bug in pagination logic
- No safety limit

**Debug:**
```python
# Print each URL being fetched
print(f"Fetching: {url}")

# Compare with previous URL
if url == previous_url:
    print("ERROR: Same URL twice!")
    break
```

**Fix:**
```python
fetched_urls = set()

while url:
    if url in fetched_urls:
        print("ERROR: Circular pagination")
        break

    fetched_urls.add(url)

    response = requests.get(url, headers=headers)
    # ... process ...

    # Get next URL
```

### Issue: Missing Items in Results

**Symptom:** Total item count doesn't match

**Causes:**
- Manually constructed URL skipped pages
- Pagination loop exited early
- Not accumulating all pages

**Debug:**
```python
# Use X-Total-Count header
x_total_count = response.headers.get('X-Total-Count')
print(f"Expected {x_total_count} items total")
print(f"Got {len(all_data)} items")

if int(x_total_count) != len(all_data):
    print("ERROR: Missing items!")
```

**Fix:**
```python
# Ensure all pages are fetched
link = response.headers.get('Link', '')
if '<' in link and 'rel="next"' in link:
    # Next page exists
    continue

elif 'rel="next"' not in link:
    # No next link = last page
    break
```

---

## Related Documentation

- [API Reference](./api-reference.md) - Paginated endpoints
- [Error Handling](./error-handling.md) - Handle errors during pagination
- [Rate Limiting](./rate-limiting.md) - Rate limits during pagination

---

**For questions or issues:** Consult the [Basecamp API Documentation](https://github.com/basecamp/bc4-api)
