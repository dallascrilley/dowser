# Basecamp 4 API - Rate Limiting Guide

**Last Updated:** November 11, 2025
**Purpose:** Understand and handle Basecamp rate limits
**Key Limit:** 50 requests per 10 seconds per IP address

---

## Table of Contents

1. [Rate Limit Specifications](#rate-limit-specifications)
2. [Understanding the Limits](#understanding-the-limits)
3. [Rate Limit Response](#rate-limit-response)
4. [Detection Strategies](#detection-strategies)
5. [Backoff Strategies](#backoff-strategies)
6. [Request Rate Tracking](#request-rate-tracking)
7. [Prevention Best Practices](#prevention-best-practices)
8. [Monitoring & Alerts](#monitoring--alerts)

---

## Rate Limit Specifications

### Primary Limit

- **Limit:** 50 requests per 10 seconds per IP address
- **Scoping:** Enforced at the IP level, not per access token
- **Response Code:** 429 Too Many Requests
- **Response Header:** `Retry-After: {seconds}`

### Important Notes

1. **IP-Based Enforcement:** All requests from the same IP share the limit
   - Multiple users behind same NAT/proxy share quota
   - Could affect all clients on corporate network
   - Cloud deployments may share IPs

2. **No Burst Allowance:** Exactly 50 requests in 10 seconds
   - Request #51 will be rejected
   - No allowance for short bursts
   - Very strict enforcement

3. **Dynamic Adjustment:** Basecamp may adjust limits
   - Documentation mentions "multiple rate limits adjusted dynamically"
   - Different limits for GET vs POST vs PUT
   - Per-second, per-hour, per-day limits may apply
   - Always honor Retry-After header

4. **Flooding Flag:** Repeated violations flag your client
   - Retrying before Retry-After expires = flooding
   - Multiple consecutive 429s = potential ban
   - May result in temporary IP blacklist

---

## Understanding the Limits

### The 50 Request Window

```
Time: 0s      5s      10s     15s     20s
      |-------|-------|-------|-------|
      |<----- 10 second window ---->|

Requests in window:
Request 1:  0.0s  ✓
Request 2:  0.1s  ✓
...
Request 50: 9.9s  ✓
Request 51: 10.0s ✗ (429 Too Many Requests, must wait)

Next window starts:
Request 51: 10.1s ✓ (oldest request aged out)
```

### Request Rate Calculation

```
50 requests / 10 seconds = 5 requests per second average

Safe operating point: 3-4 requests per second
(leaves buffer for spikes)
```

### What Counts Toward Limit

- All HTTP methods (GET, POST, PUT, DELETE)
- All endpoints under `https://3.basecampapi.com/`
- Failed requests (400, 404, 5xx all count)
- Authentication attempts (401 counts)
- Pagination requests (Link header follow counts)

### What Doesn't Count

- HTTPS handshake
- DNS lookups
- HEAD requests (if applicable)
- Requests to other domains

---

## Rate Limit Response

### Headers Returned

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 8
Content-Type: application/json
```

### Response Body

```json
{
  "error": "Rate limit exceeded"
}
```

### Retry-After Header

The `Retry-After` header specifies how many seconds to wait:

```bash
# Extract retry-after value
retry_after=$(curl -s -i "$url" | grep -i "Retry-After:" | awk '{print $2}')

# Wait exactly that long
echo "Sleeping for ${retry_after}s..."
sleep "$retry_after"

# Then retry
curl "$url"
```

**Important:**
- Always respect Retry-After value
- Don't retry before waiting
- If header missing, use exponential backoff (1s, 2s, 4s...)

---

## Detection Strategies

### Strategy 1: HTTP Status Code Check

```bash
check_rate_limit() {
  local url=$1

  response=$(curl -s -w "\n%{http_code}" -H "..." "$url")
  http_code=$(echo "$response" | tail -n1)

  if [ "$http_code" = "429" ]; then
    echo "Rate limited!"
    return 0
  else
    echo "Not rate limited (HTTP $http_code)"
    return 1
  fi
}
```

### Strategy 2: Python with Requests Library

```python
import requests

def check_rate_limit(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        print(f"Rate limited. Retry after {retry_after}s")
        return True

    return False
```

### Strategy 3: JavaScript/Node.js

```javascript
async function checkRateLimit(url, headers) {
  const response = await fetch(url, { headers });

  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After') || '1';
    console.log(`Rate limited. Retry after ${retryAfter}s`);
    return true;
  }

  return false;
}
```

---

## Backoff Strategies

### Strategy 1: Simple Backoff (Using Retry-After)

**Best for:** Simple integrations, API consumption from single client

```bash
#!/bin/bash

make_request_with_retry() {
  local url=$1
  local max_attempts=3
  local attempt=0

  while [ $attempt -lt $max_attempts ]; do
    # Make request
    response=$(curl -s -i -w "\n%{http_code}" -H "..." "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
      echo "$body"
      return 0
    fi

    if [ "$http_code" = "429" ]; then
      # Rate limited - use Retry-After header
      retry_after=$(echo "$response" | grep -i "Retry-After:" | \
        awk '{print $2}' | tr -d '\r')

      echo "Rate limited. Waiting ${retry_after}s..." >&2
      sleep "$retry_after"
      attempt=$((attempt + 1))
      continue
    fi

    # Other error - don't retry
    echo "Error: HTTP $http_code" >&2
    echo "$body" >&2
    return 1
  done

  echo "Max retries exceeded" >&2
  return 1
}
```

### Strategy 2: Exponential Backoff

**Best for:** Robust integrations, handling transient server errors

```python
import time

def make_request_with_exponential_backoff(url, headers, max_retries=5):
    """
    Make request with exponential backoff for 429 and 5xx errors

    Backoff sequence: 1s, 2s, 4s, 8s, 16s (capped at 30s)
    """
    retry_count = 0
    backoff = 1

    while retry_count < max_retries:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            # Rate limited - use Retry-After if available
            retry_after = int(response.headers.get('Retry-After', backoff))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            retry_count += 1
            continue

        elif response.status_code >= 500:
            # Server error - exponential backoff
            print(f"Server error {response.status_code}. Waiting {backoff}s...")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)  # Cap at 30 seconds
            retry_count += 1
            continue

        else:
            # Other error - don't retry
            raise Exception(f"HTTP {response.status_code}")

    raise Exception("Max retries exceeded")
```

### Strategy 3: Exponential Backoff with Jitter

**Best for:** Distributed systems, multiple concurrent clients

```python
import time
import random

def exponential_backoff_with_jitter(retry_count, base=1, max_backoff=30):
    """
    Calculate backoff with jitter to prevent thundering herd

    Formula: min(max_backoff, base * 2^retry_count * random(0.5, 1.5))
    """
    exponential = base * (2 ** retry_count)
    jitter = random.uniform(0.5, 1.5)
    backoff = min(max_backoff, exponential * jitter)
    return backoff

def make_request_with_jitter_backoff(url, headers, max_retries=5):
    """Make request with jittered exponential backoff"""
    retry_count = 0

    while retry_count < max_retries:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()

        elif response.status_code in [429] + list(range(500, 505)):
            # Rate limit or server error
            retry_after = response.headers.get('Retry-After')

            if retry_after:
                # Use header value
                wait_time = int(retry_after)
            else:
                # Calculate with jitter
                wait_time = exponential_backoff_with_jitter(retry_count)

            print(f"Waiting {wait_time:.2f}s before retry...")
            time.sleep(wait_time)
            retry_count += 1
        else:
            raise Exception(f"HTTP {response.status_code}")

    raise Exception("Max retries exceeded")
```

---

## Request Rate Tracking

### Strategy 1: Simple Time-Window Tracker

```python
from collections import deque
from datetime import datetime, timedelta

class RequestRateTracker:
    """Track request rate over 10-second windows"""

    def __init__(self, window_seconds=10, max_requests=50):
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.request_times = deque()

    def get_current_rate(self):
        """Get number of requests in current window"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove requests older than window
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        return len(self.request_times)

    def can_make_request(self):
        """Check if we can make another request"""
        return self.get_current_rate() < self.max_requests

    def wait_if_needed(self):
        """Wait if approaching limit"""
        rate = self.get_current_rate()

        if rate >= self.max_requests:
            # At limit - must wait for oldest request to age out
            oldest = self.request_times[0]
            age = (datetime.now() - oldest).total_seconds()
            wait_time = self.window_seconds - age

            if wait_time > 0:
                print(f"At rate limit. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time + 0.01)  # Small buffer

        # Check again after potential wait
        return self.can_make_request()

    def record_request(self):
        """Record that a request was made"""
        self.request_times.append(datetime.now())

    def get_summary(self):
        """Get current tracking summary"""
        rate = self.get_current_rate()
        remaining = self.max_requests - rate
        return {
            'current_rate': rate,
            'remaining_requests': remaining,
            'percentage_used': (rate / self.max_requests) * 100
        }

# Usage
tracker = RequestRateTracker()

def make_request_safely(url, headers):
    tracker.wait_if_needed()

    response = requests.get(url, headers=headers)
    tracker.record_request()

    if response.status_code == 429:
        # Still got rate limited - wait and retry
        retry_after = int(response.headers.get('Retry-After', 2))
        time.sleep(retry_after)
        return make_request_safely(url, headers)

    return response

# Monitor rate
print(tracker.get_summary())
# Output: {'current_rate': 25, 'remaining_requests': 25, 'percentage_used': 50.0}
```

### Strategy 2: Proactive Rate Limit Alerts

```python
class RateLimitMonitor:
    """Monitor and alert on approaching rate limits"""

    def __init__(self, warning_threshold=0.8):
        self.tracker = RequestRateTracker()
        self.warning_threshold = warning_threshold
        self.alerts_sent = 0

    def check_and_alert(self):
        """Check rate and send alerts"""
        summary = self.tracker.get_summary()
        percentage = summary['percentage_used'] / 100

        if percentage >= self.warning_threshold:
            self.send_alert(
                f"High API usage: {percentage:.0%} of rate limit used"
            )
            self.alerts_sent += 1

        if percentage >= 0.99:
            self.send_critical_alert(
                "Critical: Nearly at rate limit!"
            )

    def send_alert(self, message):
        """Send warning alert"""
        print(f"WARNING: {message}")
        # Could send to monitoring system (Sentry, DataDog, etc.)

    def send_critical_alert(self, message):
        """Send critical alert"""
        print(f"CRITICAL: {message}")
        # Could page on-call engineer
```

---

## Prevention Best Practices

### Practice 1: Request Throttling

Limit requests to safe rate (3-4 per second):

```python
from time import sleep, time

class RateLimiter:
    """Throttle requests to stay under rate limit"""

    def __init__(self, requests_per_second=3):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0

    def throttle(self):
        """Enforce minimum interval between requests"""
        elapsed = time() - self.last_request_time

        if elapsed < self.min_interval:
            sleep(self.min_interval - elapsed)

        self.last_request_time = time()

# Usage
limiter = RateLimiter(requests_per_second=3)

for project_id in project_ids:
    limiter.throttle()
    response = api.get_project(project_id)
```

### Practice 2: HTTP Caching (ETags)

Reduce requests by caching unchanged resources:

```python
import requests

class CachedAPIClient:
    """API client with ETag-based caching"""

    def __init__(self):
        self.cache = {}  # {url: (response, etag)}

    def get(self, url, headers=None):
        """Get resource, using cache if available"""
        if not headers:
            headers = {}

        # Check cache
        if url in self.cache:
            response, etag = self.cache[url]
            headers['If-None-Match'] = etag

        # Make request
        resp = requests.get(url, headers=headers)

        if resp.status_code == 304:
            # Not modified - use cached response
            print(f"Cache hit for {url}")
            return self.cache[url][0]

        elif resp.status_code == 200:
            # Update cache
            etag = resp.headers.get('ETag')
            if etag:
                self.cache[url] = (resp, etag)
                print(f"Cached {url}")

            return resp

        else:
            return resp

# Usage
client = CachedAPIClient()

# First request - hits API
project = client.get(f"https://3.basecampapi.com/{ACCOUNT_ID}/projects/123.json")

# Second request - returns cached version (304 Not Modified)
project = client.get(f"https://3.basecampapi.com/{ACCOUNT_ID}/projects/123.json")
```

### Practice 3: Request Queueing

Queue requests and process at controlled rate:

```python
import queue
import threading
import requests

class APIRequestQueue:
    """Process API requests from queue at controlled rate"""

    def __init__(self, requests_per_second=3):
        self.queue = queue.Queue()
        self.requests_per_second = requests_per_second
        self.running = False

    def add_request(self, url, headers):
        """Add request to queue"""
        self.queue.put((url, headers))

    def start(self):
        """Start processing queue in background thread"""
        self.running = True
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()

    def stop(self):
        """Stop processing queue"""
        self.running = False

    def _process_queue(self):
        """Process requests from queue"""
        from time import time, sleep

        min_interval = 1.0 / self.requests_per_second
        last_request = 0

        while self.running:
            try:
                url, headers = self.queue.get(timeout=1)

                # Throttle
                elapsed = time() - last_request
                if elapsed < min_interval:
                    sleep(min_interval - elapsed)

                # Make request
                response = requests.get(url, headers=headers)
                last_request = time()

                # Process response
                self._handle_response(url, response)

            except queue.Empty:
                continue

    def _handle_response(self, url, response):
        """Handle API response"""
        if response.status_code == 200:
            print(f"✓ {url}")
        else:
            print(f"✗ {url} - HTTP {response.status_code}")
```

### Practice 4: Batch Operations

Group related requests together:

```python
def add_team_members_batched(project_id, members_list):
    """Add multiple members in single API call"""

    # Separate into new and existing members
    new_members = [m for m in members_list if not member_exists(m)]
    existing_members = [m for m in members_list if member_exists(m)]

    # Single request combines grant + create
    payload = {
        'grant': [m['id'] for m in existing_members],
        'create': [
            {
                'name': m['name'],
                'email_address': m['email'],
                'title': m['title']
            }
            for m in new_members
        ]
    }

    # One request instead of N requests
    return api.update_project_members(project_id, payload)
```

---

## Monitoring & Alerts

### Metrics to Track

```python
class RateLimitMetrics:
    """Track rate limiting metrics"""

    def __init__(self):
        self.total_requests = 0
        self.rate_limited_requests = 0
        self.request_times = []
        self.max_concurrent_rate = 0

    def record_request(self, status_code):
        """Record a request"""
        self.total_requests += 1

        if status_code == 429:
            self.rate_limited_requests += 1

    def get_statistics(self):
        """Get current statistics"""
        rate_limit_percentage = (
            self.rate_limited_requests / self.total_requests * 100
            if self.total_requests > 0
            else 0
        )

        return {
            'total_requests': self.total_requests,
            'rate_limited': self.rate_limited_requests,
            'rate_limit_percentage': rate_limit_percentage,
            'max_concurrent_rate': self.max_concurrent_rate
        }

# Usage
metrics = RateLimitMetrics()

# After each request
metrics.record_request(response.status_code)

# Monitor periodically
stats = metrics.get_statistics()
print(f"Rate limited: {stats['rate_limit_percentage']:.1f}%")
```

### Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Rate limited requests | >1% of total | Review request patterns |
| Consecutive 429s | >3 in a row | Check if client is flooding |
| Average response rate | 40+ req/10s | May hit limit soon |
| Peak request rate | 50+ req/10s | Already at limit |

---

## Related Documentation

- [Error Handling](./error-handling.md) - Handling 429 errors
- [API Reference](./api-reference.md) - Endpoint details
- [Pagination](./pagination.md) - Pagination efficiency

---

**For questions or issues:** Consult the [Basecamp API Documentation](https://github.com/basecamp/bc4-api)
