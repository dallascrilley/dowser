# Copper CRM API - Rate Limiting Guide

Comprehensive guide to understanding and managing rate limits when working with the Copper CRM API.

---

## 1. Rate Limit Specifications

Copper CRM enforces different rate limits depending on the type of operation:

### Standard API Endpoints
- **Limit:** 180 requests per minute
- **Window:** Rolling 60-second window
- **Applies to:** All standard CRUD operations (GET, POST, PUT, DELETE) and search endpoints

### Bulk API Endpoints
- **Limit:** 3 requests per second
- **Window:** Rolling per-second window
- **Applies to:** All bulk create/update operations
- **Batch size:** Maximum 10 records per request

### Webhook Notifications
- **Limit:** 600 notifications per minute
- **Extended limit:** 1,800 notifications per 10 minutes
- **Multi-event:** Each notification can contain up to 30 record IDs

### Important Notes
- Rate limits are applied **per account**, not per API key
- Multiple integrations using the same account share the same rate limit bucket
- Webhook notifications count towards separate limits and don't affect API request limits

---

## 2. How Rate Limits Work

### Rolling Window Algorithm

Copper uses a **rolling window** approach for rate limiting:

```
Standard APIs (180/minute):
├─ Time Window: 60 seconds
├─ Counter: Tracks requests in the last 60 seconds
└─ Behavior: Any 60-second period cannot exceed 180 requests

Bulk APIs (3/second):
├─ Time Window: 1 second
├─ Counter: Tracks requests in the last 1 second
└─ Behavior: Any 1-second period cannot exceed 3 requests
```

### How It Works

1. **Request initiated** → Counter increments
2. **Window slides continuously** → Old requests fall out of the window
3. **Counter checked** → If limit exceeded, request rejected with 429
4. **Time passes** → Capacity becomes available as window slides forward

**Example Timeline (Standard API - 180/min):**

```
00:00 - 00:59  →  180 requests made  [LIMIT REACHED]
00:01 - 01:00  →  Can make 0 new requests (window still full)
00:15 - 01:14  →  Some capacity available as old requests expire
01:00 - 01:59  →  Full 180 requests available again
```

### Why Rolling Windows Matter

Unlike fixed-window rate limiting (which resets at specific times), rolling windows:
- Prevent burst abuse at window boundaries
- Provide more consistent throughput
- Make capacity availability predictable based on request history

---

## 3. Detecting Rate Limit Errors

### HTTP 429 Response

When you exceed the rate limit, Copper returns a `429 Too Many Requests` status code:

**Response Structure:**
```json
{
  "message": "Rate limit exceeded",
  "status": 429
}
```

**Response Headers:**
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
```

### Error Detection in Code

**Python:**
```python
import requests

response = requests.post(url, headers=headers, json=data)

if response.status_code == 429:
    print("Rate limit exceeded")
    # Handle retry logic
elif response.status_code == 200:
    print("Request successful")
else:
    print(f"Error: {response.status_code}")
```

**JavaScript/Node.js:**
```javascript
const response = await fetch(url, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify(data)
});

if (response.status === 429) {
  console.log('Rate limit exceeded');
  // Handle retry logic
} else if (response.ok) {
  const data = await response.json();
  console.log('Request successful');
} else {
  console.error(`Error: ${response.status}`);
}
```

### Best Practice: Always Handle 429

Every API call should include error handling for rate limits:

```python
# Anti-pattern (Don't do this)
response = requests.get(url, headers=headers)
data = response.json()  # Will fail if 429 returned

# Correct pattern
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
elif response.status_code == 429:
    # Handle rate limit with retry logic
    pass
else:
    # Handle other errors
    pass
```

---

## 4. Exponential Backoff Implementation

Exponential backoff is the recommended strategy for handling rate limit errors. It progressively increases wait time between retries.

### How Exponential Backoff Works

```
Attempt 1: Wait 1 second   (2^0 = 1)
Attempt 2: Wait 2 seconds  (2^1 = 2)
Attempt 3: Wait 4 seconds  (2^2 = 4)
Attempt 4: Wait 8 seconds  (2^3 = 8)
Attempt 5: Wait 16 seconds (2^4 = 16)
```

### Python Implementation

```python
import time
import requests
from typing import Optional, Dict, Any

def make_request_with_backoff(
    method: str,
    url: str,
    headers: Dict[str, str],
    data: Optional[Dict[str, Any]] = None,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> requests.Response:
    """
    Make API request with exponential backoff retry logic.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: API endpoint URL
        headers: Request headers
        data: Request body (for POST/PUT)
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries

    Returns:
        Response object if successful

    Raises:
        Exception if all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() in ['POST', 'PUT']:
                response = requests.request(method, url, headers=headers, json=data)
            else:
                response = requests.delete(url, headers=headers)

            # Success
            if response.status_code == 200:
                return response

            # Rate limit exceeded
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    # Calculate exponential backoff delay
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"Rate limit hit. Waiting {delay}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Rate limit exceeded. Max retries ({max_retries}) exhausted")

            # Other errors
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                print(f"Request failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise

    raise Exception("Request failed after all retries")


# Usage example
headers = {
    'X-PW-AccessToken': 'YOUR_API_KEY',
    'X-PW-Application': 'developer_api',
    'X-PW-UserEmail': 'your.email@company.com',
    'Content-Type': 'application/json'
}

url = "https://api.copper.com/developer_api/v1/leads/search"
search_data = {"page_size": 200}

response = make_request_with_backoff('POST', url, headers, search_data)
leads = response.json()
```

### JavaScript/Node.js Implementation

```javascript
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function makeRequestWithBackoff(
  method,
  url,
  headers,
  data = null,
  maxRetries = 5,
  baseDelay = 1000,
  maxDelay = 60000
) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const options = {
        method,
        headers,
        ...(data && { body: JSON.stringify(data) })
      };

      const response = await fetch(url, options);

      // Success
      if (response.ok) {
        return response;
      }

      // Rate limit exceeded
      if (response.status === 429) {
        if (attempt < maxRetries - 1) {
          // Calculate exponential backoff delay
          const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
          console.log(`Rate limit hit. Waiting ${delay}ms before retry ${attempt + 1}/${maxRetries}`);
          await wait(delay);
          continue;
        } else {
          throw new Error(`Rate limit exceeded. Max retries (${maxRetries}) exhausted`);
        }
      }

      // Other errors
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);

    } catch (error) {
      if (attempt < maxRetries - 1) {
        const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
        console.log(`Request failed: ${error.message}. Retrying in ${delay}ms...`);
        await wait(delay);
      } else {
        throw error;
      }
    }
  }

  throw new Error('Request failed after all retries');
}

// Usage example
const headers = {
  'X-PW-AccessToken': 'YOUR_API_KEY',
  'X-PW-Application': 'developer_api',
  'X-PW-UserEmail': 'your.email@company.com',
  'Content-Type': 'application/json'
};

const url = "https://api.copper.com/developer_api/v1/leads/search";
const searchData = { page_size: 200 };

const response = await makeRequestWithBackoff('POST', url, headers, searchData);
const leads = await response.json();
```

### Jitter for Better Distribution

Add randomization to prevent thundering herd problem:

```python
import random

def exponential_backoff_with_jitter(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate delay with exponential backoff and jitter."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    # Add random jitter (±25%)
    jitter = delay * 0.25 * (2 * random.random() - 1)
    return delay + jitter
```

---

## 5. Request Throttling Patterns

### Fixed-Rate Throttling

Limit requests to a specific rate regardless of API limits. Useful for controlling costs and preventing bursts.

**Python - Token Bucket Algorithm:**
```python
import time
import threading
from collections import deque

class TokenBucket:
    """Thread-safe token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int = None):
        """
        Initialize token bucket.

        Args:
            rate: Tokens per second (e.g., 3.0 for 180/min)
            capacity: Maximum tokens (defaults to rate)
        """
        self.rate = rate
        self.capacity = capacity or int(rate)
        self.tokens = self.capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens.

        Returns:
            True if tokens available, False otherwise
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update

            # Add new tokens based on elapsed time
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # Try to consume
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for_token(self, tokens: int = 1):
        """Block until tokens available."""
        while not self.consume(tokens):
            time.sleep(0.1)


# Usage for standard API (180/min = 3/sec)
standard_limiter = TokenBucket(rate=3.0, capacity=180)

def make_standard_api_call():
    standard_limiter.wait_for_token()
    # Make API request
    response = requests.get(url, headers=headers)
    return response


# Usage for bulk API (3/sec)
bulk_limiter = TokenBucket(rate=3.0, capacity=3)

def make_bulk_api_call():
    bulk_limiter.wait_for_token()
    # Make bulk API request
    response = requests.post(bulk_url, headers=headers, json=bulk_data)
    return response
```

**JavaScript - Simple Rate Limiter:**
```javascript
class RateLimiter {
  constructor(requestsPerSecond) {
    this.requestsPerSecond = requestsPerSecond;
    this.queue = [];
    this.requestTimes = [];
  }

  async throttle(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.processQueue();
    });
  }

  async processQueue() {
    if (this.queue.length === 0) return;

    const now = Date.now();
    const oneSecondAgo = now - 1000;

    // Remove old timestamps
    this.requestTimes = this.requestTimes.filter(time => time > oneSecondAgo);

    // Check if we can make a request
    if (this.requestTimes.length < this.requestsPerSecond) {
      const { fn, resolve, reject } = this.queue.shift();
      this.requestTimes.push(now);

      try {
        const result = await fn();
        resolve(result);
      } catch (error) {
        reject(error);
      }

      // Process next item
      setTimeout(() => this.processQueue(), 0);
    } else {
      // Wait until we can make the next request
      const oldestRequest = Math.min(...this.requestTimes);
      const waitTime = oldestRequest + 1000 - now;
      setTimeout(() => this.processQueue(), waitTime);
    }
  }
}

// Usage for standard API (3 requests/sec)
const standardLimiter = new RateLimiter(3);

async function makeStandardApiCall() {
  return standardLimiter.throttle(async () => {
    const response = await fetch(url, { headers });
    return response.json();
  });
}

// Usage for bulk API (3 requests/sec with stricter enforcement)
const bulkLimiter = new RateLimiter(3);

async function makeBulkApiCall(data) {
  return bulkLimiter.throttle(async () => {
    const response = await fetch(bulkUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });
    return response.json();
  });
}
```

### Adaptive Throttling

Adjust rate based on API responses:

```python
class AdaptiveRateLimiter:
    """Rate limiter that adapts based on 429 responses."""

    def __init__(self, initial_rate: float = 3.0, min_rate: float = 1.0, max_rate: float = 3.0):
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.bucket = TokenBucket(rate=initial_rate)
        self.consecutive_429s = 0
        self.consecutive_successes = 0

    def on_success(self):
        """Call after successful request."""
        self.consecutive_429s = 0
        self.consecutive_successes += 1

        # Gradually increase rate after 10 consecutive successes
        if self.consecutive_successes >= 10:
            self.current_rate = min(self.current_rate * 1.1, self.max_rate)
            self.bucket = TokenBucket(rate=self.current_rate)
            self.consecutive_successes = 0

    def on_rate_limit(self):
        """Call after 429 response."""
        self.consecutive_successes = 0
        self.consecutive_429s += 1

        # Decrease rate by 50%
        self.current_rate = max(self.current_rate * 0.5, self.min_rate)
        self.bucket = TokenBucket(rate=self.current_rate)

    def wait_for_token(self):
        """Block until token available."""
        self.bucket.wait_for_token()


# Usage
limiter = AdaptiveRateLimiter(initial_rate=3.0)

def make_api_call_adaptive():
    limiter.wait_for_token()
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        limiter.on_rate_limit()
        raise Exception("Rate limited")
    elif response.status_code == 200:
        limiter.on_success()
        return response.json()
```

---

## 6. Request Queue Implementation

### Producer-Consumer Pattern

Use queues to manage high-volume operations while respecting rate limits:

**Python - Threading Queue:**
```python
import queue
import threading
import time
from typing import Callable, Any, List

class RateLimitedQueue:
    """Thread-safe queue processor with rate limiting."""

    def __init__(
        self,
        rate_limiter: TokenBucket,
        num_workers: int = 3,
        retry_on_429: bool = True
    ):
        self.queue = queue.Queue()
        self.rate_limiter = rate_limiter
        self.num_workers = num_workers
        self.retry_on_429 = retry_on_429
        self.results = []
        self.errors = []
        self.lock = threading.Lock()
        self.workers = []

    def add_task(self, task: Callable, *args, **kwargs):
        """Add task to queue."""
        self.queue.put((task, args, kwargs))

    def worker(self):
        """Worker thread that processes queue."""
        while True:
            try:
                task, args, kwargs = self.queue.get(timeout=1)
            except queue.Empty:
                break

            # Wait for rate limit token
            self.rate_limiter.wait_for_token()

            try:
                result = task(*args, **kwargs)
                with self.lock:
                    self.results.append(result)
            except Exception as e:
                if '429' in str(e) and self.retry_on_429:
                    # Re-queue the task
                    self.queue.put((task, args, kwargs))
                else:
                    with self.lock:
                        self.errors.append({
                            'task': task.__name__,
                            'error': str(e)
                        })
            finally:
                self.queue.task_done()

    def process(self):
        """Start processing queue."""
        # Start worker threads
        for _ in range(self.num_workers):
            worker = threading.Thread(target=self.worker)
            worker.start()
            self.workers.append(worker)

        # Wait for all tasks to complete
        self.queue.join()

        # Wait for all workers to finish
        for worker in self.workers:
            worker.join()

        return {
            'results': self.results,
            'errors': self.errors,
            'success_count': len(self.results),
            'error_count': len(self.errors)
        }


# Usage example: Process 500 leads
def create_lead(lead_data):
    """Create single lead."""
    response = requests.post(
        'https://api.copper.com/developer_api/v1/leads',
        headers=headers,
        json=lead_data
    )
    if response.status_code == 429:
        raise Exception('429 Rate Limited')
    response.raise_for_status()
    return response.json()

# Create rate limiter (3 req/sec)
limiter = TokenBucket(rate=3.0)

# Create queue processor
queue_processor = RateLimitedQueue(
    rate_limiter=limiter,
    num_workers=3,
    retry_on_429=True
)

# Add 500 leads to queue
leads_to_create = [
    {'name': f'Lead {i}', 'email': {'email': f'lead{i}@example.com'}}
    for i in range(500)
]

for lead_data in leads_to_create:
    queue_processor.add_task(create_lead, lead_data)

# Process queue
results = queue_processor.process()
print(f"Created {results['success_count']} leads")
print(f"Failed {results['error_count']} leads")
```

**JavaScript - Async Queue with Concurrency Control:**
```javascript
class AsyncQueue {
  constructor(rateLimiter, concurrency = 3) {
    this.queue = [];
    this.rateLimiter = rateLimiter;
    this.concurrency = concurrency;
    this.running = 0;
    this.results = [];
    this.errors = [];
  }

  addTask(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.process();
    });
  }

  async process() {
    if (this.running >= this.concurrency || this.queue.length === 0) {
      return;
    }

    this.running++;
    const { fn, resolve, reject } = this.queue.shift();

    try {
      // Wait for rate limit
      const result = await this.rateLimiter.throttle(fn);
      this.results.push(result);
      resolve(result);
    } catch (error) {
      this.errors.push(error);
      reject(error);
    } finally {
      this.running--;
      this.process();
    }
  }

  async processAll() {
    const promises = [];
    while (this.queue.length > 0 || this.running > 0) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return {
      results: this.results,
      errors: this.errors,
      successCount: this.results.length,
      errorCount: this.errors.length
    };
  }
}

// Usage example
const limiter = new RateLimiter(3);
const asyncQueue = new AsyncQueue(limiter, 3);

// Create 500 leads
const leadsToCreate = Array.from({ length: 500 }, (_, i) => ({
  name: `Lead ${i}`,
  email: { email: `lead${i}@example.com` }
}));

// Add all tasks to queue
const promises = leadsToCreate.map(leadData =>
  asyncQueue.addTask(async () => {
    const response = await fetch('https://api.copper.com/developer_api/v1/leads', {
      method: 'POST',
      headers,
      body: JSON.stringify(leadData)
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
);

// Wait for all to complete
const results = await Promise.allSettled(promises);
console.log(`Created ${results.filter(r => r.status === 'fulfilled').length} leads`);
```

---

## 7. Monitoring and Tracking Usage

### Request Counter and Logger

Track API usage to stay within limits:

**Python - Usage Tracker:**
```python
import time
from collections import deque
from datetime import datetime, timedelta
import json

class APIUsageTracker:
    """Track API usage and provide metrics."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self.requests = deque()
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'rate_limited_requests': 0,
            'error_requests': 0
        }

    def record_request(self, status_code: int, endpoint: str = None):
        """Record API request."""
        now = time.time()

        # Clean old requests outside window
        cutoff = now - self.window_seconds
        while self.requests and self.requests[0]['timestamp'] < cutoff:
            self.requests.popleft()

        # Record new request
        self.requests.append({
            'timestamp': now,
            'status_code': status_code,
            'endpoint': endpoint
        })

        # Update stats
        self.stats['total_requests'] += 1
        if status_code == 200:
            self.stats['successful_requests'] += 1
        elif status_code == 429:
            self.stats['rate_limited_requests'] += 1
        else:
            self.stats['error_requests'] += 1

    def get_current_rate(self) -> float:
        """Get requests per second in current window."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old requests
        while self.requests and self.requests[0]['timestamp'] < cutoff:
            self.requests.popleft()

        if not self.requests:
            return 0.0

        time_span = now - self.requests[0]['timestamp']
        if time_span == 0:
            return 0.0

        return len(self.requests) / time_span

    def get_requests_in_window(self) -> int:
        """Get number of requests in current window."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Clean old requests
        while self.requests and self.requests[0]['timestamp'] < cutoff:
            self.requests.popleft()

        return len(self.requests)

    def get_capacity_remaining(self, limit: int) -> int:
        """Get remaining capacity in current window."""
        return max(0, limit - self.get_requests_in_window())

    def get_stats(self) -> dict:
        """Get usage statistics."""
        return {
            **self.stats,
            'current_rate_per_second': self.get_current_rate(),
            'requests_in_window': self.get_requests_in_window(),
            'window_seconds': self.window_seconds
        }

    def print_report(self):
        """Print usage report."""
        stats = self.get_stats()
        print("\n=== API Usage Report ===")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Successful: {stats['successful_requests']}")
        print(f"Rate Limited (429): {stats['rate_limited_requests']}")
        print(f"Errors: {stats['error_requests']}")
        print(f"Current Rate: {stats['current_rate_per_second']:.2f} req/sec")
        print(f"Requests in Last {self.window_seconds}s: {stats['requests_in_window']}")
        print("========================\n")


# Usage with requests
tracker = APIUsageTracker(window_seconds=60)

def make_tracked_request(url, **kwargs):
    """Make request and track usage."""
    response = requests.request(url=url, **kwargs)
    tracker.record_request(response.status_code, endpoint=url)

    # Check if approaching limit
    capacity = tracker.get_capacity_remaining(limit=180)
    if capacity < 20:
        print(f"Warning: Only {capacity} requests remaining in window")

    return response

# Use throughout your application
response = make_tracked_request(
    'https://api.copper.com/developer_api/v1/leads/search',
    method='POST',
    headers=headers,
    json={'page_size': 200}
)

# Print usage report periodically
tracker.print_report()
```

**JavaScript - Usage Tracker:**
```javascript
class APIUsageTracker {
  constructor(windowSeconds = 60) {
    this.windowSeconds = windowSeconds;
    this.requests = [];
    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      rateLimitedRequests: 0,
      errorRequests: 0
    };
  }

  recordRequest(statusCode, endpoint = null) {
    const now = Date.now();
    const cutoff = now - (this.windowSeconds * 1000);

    // Clean old requests
    this.requests = this.requests.filter(r => r.timestamp > cutoff);

    // Record new request
    this.requests.push({ timestamp: now, statusCode, endpoint });

    // Update stats
    this.stats.totalRequests++;
    if (statusCode === 200) {
      this.stats.successfulRequests++;
    } else if (statusCode === 429) {
      this.stats.rateLimitedRequests++;
    } else {
      this.stats.errorRequests++;
    }
  }

  getCurrentRate() {
    const now = Date.now();
    const cutoff = now - (this.windowSeconds * 1000);

    // Clean old requests
    this.requests = this.requests.filter(r => r.timestamp > cutoff);

    if (this.requests.length === 0) return 0;

    const timeSpan = (now - this.requests[0].timestamp) / 1000;
    if (timeSpan === 0) return 0;

    return this.requests.length / timeSpan;
  }

  getRequestsInWindow() {
    const now = Date.now();
    const cutoff = now - (this.windowSeconds * 1000);
    this.requests = this.requests.filter(r => r.timestamp > cutoff);
    return this.requests.length;
  }

  getCapacityRemaining(limit) {
    return Math.max(0, limit - this.getRequestsInWindow());
  }

  getStats() {
    return {
      ...this.stats,
      currentRatePerSecond: this.getCurrentRate(),
      requestsInWindow: this.getRequestsInWindow(),
      windowSeconds: this.windowSeconds
    };
  }

  printReport() {
    const stats = this.getStats();
    console.log('\n=== API Usage Report ===');
    console.log(`Total Requests: ${stats.totalRequests}`);
    console.log(`Successful: ${stats.successfulRequests}`);
    console.log(`Rate Limited (429): ${stats.rateLimitedRequests}`);
    console.log(`Errors: ${stats.errorRequests}`);
    console.log(`Current Rate: ${stats.currentRatePerSecond.toFixed(2)} req/sec`);
    console.log(`Requests in Last ${stats.windowSeconds}s: ${stats.requestsInWindow}`);
    console.log('========================\n');
  }
}

// Usage
const tracker = new APIUsageTracker(60);

async function makeTrackedRequest(url, options = {}) {
  const response = await fetch(url, options);
  tracker.recordRequest(response.status, url);

  // Check if approaching limit
  const capacity = tracker.getCapacityRemaining(180);
  if (capacity < 20) {
    console.warn(`Warning: Only ${capacity} requests remaining in window`);
  }

  return response;
}

// Use throughout application
const response = await makeTrackedRequest(
  'https://api.copper.com/developer_api/v1/leads/search',
  {
    method: 'POST',
    headers,
    body: JSON.stringify({ page_size: 200 })
  }
);

// Print usage report periodically
setInterval(() => tracker.printReport(), 60000); // Every minute
```

---

## 8. Bulk Operation Pacing

Bulk operations have stricter limits and require careful pacing.

### Constraints
- **Rate:** 3 requests per second
- **Batch size:** Maximum 10 records per request
- **Total capacity:** ~180 records per minute (if using full batches)

### Bulk Create/Update Pattern

**Python - Bulk Processor:**
```python
import time
from typing import List, Dict, Any

class BulkOperationProcessor:
    """Process bulk operations with automatic batching and pacing."""

    def __init__(
        self,
        batch_size: int = 10,
        requests_per_second: float = 2.5,  # Leave buffer
        endpoint: str = None,
        headers: Dict[str, str] = None
    ):
        self.batch_size = batch_size
        self.delay_between_requests = 1.0 / requests_per_second
        self.endpoint = endpoint
        self.headers = headers
        self.limiter = TokenBucket(rate=requests_per_second)

    def chunk_records(self, records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Split records into batches."""
        return [
            records[i:i + self.batch_size]
            for i in range(0, len(records), self.batch_size)
        ]

    def process_bulk_create(
        self,
        resource_type: str,
        records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process bulk create operation.

        Args:
            resource_type: 'leads', 'people', 'companies', etc.
            records: List of records to create

        Returns:
            Dictionary with results and statistics
        """
        url = f"https://api.copper.com/developer_api/v1/{resource_type}/bulk_create"
        batches = self.chunk_records(records)

        results = {
            'created': [],
            'failed': [],
            'total_batches': len(batches),
            'processed_batches': 0
        }

        print(f"Processing {len(records)} records in {len(batches)} batches...")

        for i, batch in enumerate(batches, 1):
            # Wait for rate limit
            self.limiter.wait_for_token()

            # Prepare request
            payload = {resource_type: batch}

            try:
                response = requests.post(url, headers=self.headers, json=payload)

                if response.status_code == 429:
                    print(f"Rate limited on batch {i}. Waiting 60s...")
                    time.sleep(60)
                    # Retry this batch
                    response = requests.post(url, headers=self.headers, json=payload)

                response.raise_for_status()

                # Parse response
                batch_results = response.json()
                for item in batch_results:
                    if item.get('id'):
                        results['created'].append(item)
                    else:
                        results['failed'].append(item)

                results['processed_batches'] += 1
                print(f"Batch {i}/{len(batches)} complete")

            except Exception as e:
                print(f"Error processing batch {i}: {e}")
                results['failed'].extend(batch)

        results['success_count'] = len(results['created'])
        results['failure_count'] = len(results['failed'])
        results['success_rate'] = (
            results['success_count'] / len(records) * 100
            if records else 0
        )

        return results


# Usage example: Bulk create 100 leads
processor = BulkOperationProcessor(
    batch_size=10,
    requests_per_second=2.5,
    headers=headers
)

leads = [
    {
        'name': f'Lead {i}',
        'email': {'email': f'lead{i}@example.com', 'category': 'work'},
        'company_name': f'Company {i}'
    }
    for i in range(100)
]

results = processor.process_bulk_create('leads', leads)

print("\n=== Bulk Create Results ===")
print(f"Total Records: {len(leads)}")
print(f"Successfully Created: {results['success_count']}")
print(f"Failed: {results['failure_count']}")
print(f"Success Rate: {results['success_rate']:.1f}%")
print(f"Batches Processed: {results['processed_batches']}/{results['total_batches']}")
```

**JavaScript - Bulk Processor:**
```javascript
class BulkOperationProcessor {
  constructor(batchSize = 10, requestsPerSecond = 2.5, headers = {}) {
    this.batchSize = batchSize;
    this.delayBetweenRequests = 1000 / requestsPerSecond;
    this.headers = headers;
    this.lastRequestTime = 0;
  }

  chunkRecords(records) {
    const chunks = [];
    for (let i = 0; i < records.length; i += this.batchSize) {
      chunks.push(records.slice(i, i + this.batchSize));
    }
    return chunks;
  }

  async waitForRateLimit() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequestTime;
    const timeToWait = Math.max(0, this.delayBetweenRequests - timeSinceLastRequest);

    if (timeToWait > 0) {
      await new Promise(resolve => setTimeout(resolve, timeToWait));
    }

    this.lastRequestTime = Date.now();
  }

  async processBulkCreate(resourceType, records) {
    const url = `https://api.copper.com/developer_api/v1/${resourceType}/bulk_create`;
    const batches = this.chunkRecords(records);

    const results = {
      created: [],
      failed: [],
      totalBatches: batches.length,
      processedBatches: 0
    };

    console.log(`Processing ${records.length} records in ${batches.length} batches...`);

    for (let i = 0; i < batches.length; i++) {
      await this.waitForRateLimit();

      const batch = batches[i];
      const payload = { [resourceType]: batch };

      try {
        let response = await fetch(url, {
          method: 'POST',
          headers: this.headers,
          body: JSON.stringify(payload)
        });

        if (response.status === 429) {
          console.log(`Rate limited on batch ${i + 1}. Waiting 60s...`);
          await new Promise(resolve => setTimeout(resolve, 60000));

          // Retry
          response = await fetch(url, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify(payload)
          });
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const batchResults = await response.json();
        for (const item of batchResults) {
          if (item.id) {
            results.created.push(item);
          } else {
            results.failed.push(item);
          }
        }

        results.processedBatches++;
        console.log(`Batch ${i + 1}/${batches.length} complete`);

      } catch (error) {
        console.error(`Error processing batch ${i + 1}:`, error);
        results.failed.push(...batch);
      }
    }

    results.successCount = results.created.length;
    results.failureCount = results.failed.length;
    results.successRate = records.length > 0
      ? (results.successCount / records.length) * 100
      : 0;

    return results;
  }
}

// Usage
const processor = new BulkOperationProcessor(10, 2.5, headers);

const leads = Array.from({ length: 100 }, (_, i) => ({
  name: `Lead ${i}`,
  email: { email: `lead${i}@example.com`, category: 'work' },
  company_name: `Company ${i}`
}));

const results = await processor.processBulkCreate('leads', leads);

console.log('\n=== Bulk Create Results ===');
console.log(`Total Records: ${leads.length}`);
console.log(`Successfully Created: ${results.successCount}`);
console.log(`Failed: ${results.failureCount}`);
console.log(`Success Rate: ${results.successRate.toFixed(1)}%`);
console.log(`Batches Processed: ${results.processedBatches}/${results.totalBatches}`);
```

### Progressive Batch Size

Automatically adjust batch size based on response times:

```python
class AdaptiveBulkProcessor:
    """Bulk processor with adaptive batch sizing."""

    def __init__(self, initial_batch_size: int = 10, min_batch_size: int = 5):
        self.batch_size = initial_batch_size
        self.min_batch_size = min_batch_size
        self.limiter = TokenBucket(rate=2.5)
        self.avg_response_time = 0.0
        self.request_count = 0

    def adjust_batch_size(self, response_time: float):
        """Adjust batch size based on response time."""
        # Update average
        self.request_count += 1
        self.avg_response_time = (
            (self.avg_response_time * (self.request_count - 1) + response_time)
            / self.request_count
        )

        # If responses are slow, reduce batch size
        if response_time > 5.0 and self.batch_size > self.min_batch_size:
            self.batch_size -= 1
            print(f"Reduced batch size to {self.batch_size}")

        # If responses are fast, increase batch size
        elif response_time < 2.0 and self.batch_size < 10:
            self.batch_size += 1
            print(f"Increased batch size to {self.batch_size}")
```

---

## 9. Best Practices

### 1. Always Implement Exponential Backoff
Never ignore 429 errors. Always retry with exponential backoff.

```python
# Good
response = make_request_with_backoff(url, headers, data)

# Bad
response = requests.post(url, headers=headers, json=data)
# Ignores 429 errors
```

### 2. Use Conservative Rate Limits
Leave buffer room to handle spikes and prevent hitting limits.

```python
# Standard API: 180/min = 3/sec
# Use 2.5/sec to leave buffer
limiter = TokenBucket(rate=2.5)

# Bulk API: 3/sec
# Use 2.5/sec for safety
bulk_limiter = TokenBucket(rate=2.5)
```

### 3. Batch When Possible
Use bulk endpoints for creating/updating multiple records.

```python
# Good - Single request for 10 leads
bulk_create_leads([lead1, lead2, ..., lead10])

# Bad - 10 separate requests
for lead in leads:
    create_lead(lead)  # 10 API calls
```

### 4. Monitor Usage Continuously
Track your API usage to identify patterns and prevent overuse.

```python
tracker = APIUsageTracker()

# Regular monitoring
if tracker.get_capacity_remaining(180) < 20:
    alert("Approaching rate limit")
```

### 5. Handle Partial Failures
Bulk operations may partially succeed. Handle each record individually.

```python
results = bulk_create_leads(leads)

for i, result in enumerate(results):
    if result.get('id'):
        print(f"Lead {i} created: {result['id']}")
    else:
        print(f"Lead {i} failed: {result.get('message')}")
        # Retry or log failure
```

### 6. Implement Circuit Breaker
Stop making requests after consecutive failures to prevent cascade issues.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = 'closed'  # closed, open, half-open

    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = 'closed'

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self.state = 'open'
            print(f"Circuit breaker opened after {self.failures} failures")
```

### 7. Use Connection Pooling
Reuse HTTP connections to reduce overhead.

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Create session with connection pooling
session = requests.Session()

# Configure retries (but handle 429 separately)
retry_strategy = Retry(
    total=3,
    status_forcelist=[500, 502, 503, 504],
    backoff_factor=1
)

adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
session.mount("https://", adapter)

# Use session for all requests
response = session.post(url, headers=headers, json=data)
```

### 8. Log and Alert on Rate Limits
Track when rate limits are hit for capacity planning.

```python
import logging

logger = logging.getLogger(__name__)

def make_api_call(url, **kwargs):
    response = requests.request(url=url, **kwargs)

    if response.status_code == 429:
        logger.warning(f"Rate limit hit for {url}")
        # Send alert to monitoring system
        send_alert("Rate limit exceeded", {"endpoint": url})

    return response
```

### 9. Respect Webhook Limits
For webhook-heavy integrations, monitor notification rates.

```
Webhook limits:
- 600 notifications/minute
- 1,800 notifications/10 minutes

Each notification can contain up to 30 record IDs.
```

### 10. Test Rate Limiting Locally
Simulate rate limiting in development to verify retry logic.

```python
class MockRateLimiter:
    """Mock API that enforces rate limits for testing."""

    def __init__(self, limit: int = 180, window: int = 60):
        self.limit = limit
        self.window = window
        self.requests = deque()

    def make_request(self):
        now = time.time()
        cutoff = now - self.window

        # Clean old requests
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

        # Check limit
        if len(self.requests) >= self.limit:
            return {'status': 429, 'message': 'Rate limit exceeded'}

        # Record request
        self.requests.append(now)
        return {'status': 200, 'message': 'Success'}

# Test your retry logic
mock_api = MockRateLimiter(limit=5, window=1)

for i in range(10):
    result = mock_api.make_request()
    if result['status'] == 429:
        print("Rate limited - retry logic should kick in")
```

---

## Summary

### Key Takeaways

1. **Rate Limits:**
   - Standard APIs: 180/min (3/sec)
   - Bulk APIs: 3/sec with max 10 records/batch
   - Webhooks: 600/min, 1800/10min

2. **Always Handle 429:**
   - Implement exponential backoff
   - Never ignore rate limit errors
   - Track and monitor usage

3. **Use Bulk Operations:**
   - 10x efficiency for bulk creates/updates
   - Requires stricter rate limiting (3/sec)
   - Handle partial failures gracefully

4. **Monitor and Track:**
   - Implement usage tracking
   - Alert on approaching limits
   - Log all rate limit incidents

5. **Leave Buffer Room:**
   - Use conservative limits (2.5/sec instead of 3/sec)
   - Account for spikes and retries
   - Plan capacity for peak usage

### Quick Reference

```python
# Rate limiter setup
standard_limiter = TokenBucket(rate=2.5)  # 150/min buffer
bulk_limiter = TokenBucket(rate=2.5)      # 150/min buffer

# Usage tracker
tracker = APIUsageTracker(window_seconds=60)

# Make request with backoff
response = make_request_with_backoff(
    method='POST',
    url=url,
    headers=headers,
    data=data,
    max_retries=5
)

# Bulk operations
processor = BulkOperationProcessor(
    batch_size=10,
    requests_per_second=2.5,
    headers=headers
)
results = processor.process_bulk_create('leads', leads)

# Monitor usage
capacity = tracker.get_capacity_remaining(limit=180)
if capacity < 20:
    alert("Approaching rate limit")
```

---

**Official Documentation:**
- Copper API Docs: https://developer.copper.com
- Best Practices: https://developer.copper.com/introduction/best_practices.html
- Webhooks: https://developer.copper.com/webhooks/overview.html
