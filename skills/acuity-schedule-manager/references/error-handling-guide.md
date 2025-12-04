# Acuity Scheduling API - Comprehensive Error Handling Guide

**Last Updated:** 2025-11-11
**Audience:** Developers
**Complexity:** Intermediate

---

## Table of Contents

1. [HTTP Status Code Reference](#http-status-code-reference)
2. [Common Error Scenarios](#common-error-scenarios)
3. [Error Response Format](#error-response-format)
4. [Retry Strategies](#retry-strategies)
5. [Circuit Breaker Pattern](#circuit-breaker-pattern)
6. [Error Recovery Procedures](#error-recovery-procedures)
7. [Logging Best Practices](#logging-best-practices)
8. [Debugging Tips](#debugging-tips)
9. [Error Handling Checklist](#error-handling-checklist)

---

## HTTP Status Code Reference

### 2xx Success Codes

**200 OK**
- Request succeeded
- Response body contains requested data
- Idempotent requests safe to retry if timeout occurs

**201 Created**
- Resource successfully created
- Response contains created resource object

### 4xx Client Error Codes

**400 Bad Request**
- Invalid parameters or malformed request
- Missing required fields
- Invalid date format or timezone

**When to Expect:**
- Invalid appointment type ID
- Missing required fields (firstName, lastName, email)
- Invalid datetime format
- Invalid timezone string

**What to Do:**
- ❌ Don't retry (same request will fail again)
- ✅ Fix request data and resubmit
- ✅ Log error for debugging
- ✅ Return user-friendly error message

**Example:**
```python
response = session.post(
    f"{BASE_URL}/appointments",
    json={
        'appointmentTypeID': 12345,
        # Missing required fields!
    }
)

if response.status_code == 400:
    error = response.json()
    print(f"Validation error: {error['message']}")
    # Show user what fields are required
```

**401 Unauthorized**
- Invalid or expired API credentials
- Missing Authorization header
- Insufficient permissions

**When to Expect:**
- Invalid User ID or API Key
- API key for different account
- User account lacks admin permissions

**What to Do:**
- ❌ Don't retry (credentials won't become valid)
- ✅ Check credentials in environment
- ✅ Verify API key hasn't been revoked
- ✅ Ensure user has admin role
- ✅ Alert administrator immediately

**Example:**
```python
response = session.get(f"{BASE_URL}/me")

if response.status_code == 401:
    logging.critical("API authentication failed!")
    logging.critical("Check ACUITY_USER_ID and ACUITY_API_KEY")
    send_alert("Authentication failure - API credentials invalid")
    raise AuthenticationError("Cannot authenticate with Acuity API")
```

**403 Forbidden**
- User authenticated but lacks permission
- Usually indicates wrong user account

**When to Expect:**
- API key belongs to different Acuity account
- User doesn't have admin permissions

**What to Do:**
- ❌ Don't retry
- ✅ Verify correct Acuity account
- ✅ Ensure user has admin access
- ✅ Contact Acuity support if needed

**404 Not Found**
- Resource doesn't exist
- Invalid endpoint or resource ID

**When to Expect:**
- Appointment ID doesn't exist
- Invalid endpoint URL
- Deleted resource

**What to Do:**
- ❌ Don't retry
- ✅ Verify resource ID is correct
- ✅ Check endpoint spelling
- ✅ Handle gracefully (show "not found" to user)

**Example:**
```python
response = session.get(f"{BASE_URL}/appointments/999999999")

if response.status_code == 404:
    print("Appointment not found")
    # Don't retry - it won't appear
    return None
```

**429 Too Many Requests**
- Rate limit exceeded
- Making >10 requests/second or >20 concurrent

**When to Expect:**
- Bulk operations without throttling
- Tight loops making rapid API calls
- Multiple integrations using same credentials

**What to Do:**
- ✅ Retry with exponential backoff
- ✅ Implement rate limiting
- ✅ Reduce concurrent requests
- ✅ Add delays between requests

**See:** [Retry Strategies](#retry-strategies) section

### 5xx Server Error Codes

**500 Internal Server Error**
- Acuity server encountered error
- Usually temporary
- Safe to retry

**When to Expect:**
- Acuity experiencing issues
- Rare but occasionally happens
- Often resolves quickly

**What to Do:**
- ✅ Retry with exponential backoff
- ✅ Check Acuity status page
- ✅ Log for monitoring
- ⏳ Wait before retry (don't hammer)

**503 Service Unavailable**
- Server temporarily unavailable
- Maintenance or temporary overload
- Safe to retry

**When to Expect:**
- Scheduled maintenance
- High-traffic periods
- Deployment happening

**What to Do:**
- ✅ Retry with longer backoff delays
- ✅ Check status page: https://status.acuityscheduling.com
- ✅ Implement circuit breaker (stop retrying after many failures)
- ✅ Alert if persists

---

## Common Error Scenarios

### Scenario 1: Invalid Email During Booking

**Error:**
```json
{
  "status_code": 400,
  "error": "bad_request",
  "message": "Invalid email format"
}
```

**Root Cause:**
- User entered invalid email
- Email validation not implemented client-side
- Typo in email address

**Prevention:**
```python
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Use before API call
if not validate_email(email):
    return {'error': 'Invalid email address'}
```

**Recovery:**
- Ask user to correct email
- Re-validate before resubmission
- Show helpful error message

---

### Scenario 2: Appointment Time Already Booked

**Error:**
```json
{
  "status_code": 400,
  "error": "bad_request",
  "message": "This appointment time is no longer available"
}
```

**Root Cause:**
- Race condition (another user booked same time)
- Stale cached availability
- Time slot filled between check and booking

**Prevention:**
```python
def book_with_fallbacks(appointment_data, alternative_times):
    """Try primary time, then alternatives"""
    times_to_try = [appointment_data['datetime']] + alternative_times

    for time_slot in times_to_try:
        appointment_data['datetime'] = time_slot

        response = session.post(
            f"{BASE_URL}/appointments",
            json=appointment_data
        )

        if response.status_code == 200:
            return response.json()

    # All times failed
    return None
```

**Recovery:**
- Show alternative times to user
- Allow user to re-check availability
- Book next available if acceptable

---

### Scenario 3: Rate Limiting During Bulk Export

**Error:**
```json
{
  "status_code": 429,
  "error": "too_many_requests",
  "message": "Rate limit reached. Limit 10req/s and 20 concurrent connections."
}
```

**Root Cause:**
- Fetching large appointment list
- No delays between requests
- Multiple requests in parallel without limit

**Prevention:**
```python
import time

def fetch_all_with_rate_limit(endpoint, params, rate_limit=9):
    """Fetch with rate limiting"""
    all_data = []
    offset = 0
    max_per_page = 100
    requests_this_second = 0
    second_start = time.time()

    while True:
        # Rate limiting
        requests_this_second += 1
        if requests_this_second >= rate_limit:
            elapsed = time.time() - second_start
            if elapsed < 1:
                time.sleep(1 - elapsed)
            second_start = time.time()
            requests_this_second = 0

        # Make request
        params['offset'] = offset
        params['max'] = max_per_page

        response = session.get(endpoint, params=params)

        if response.status_code == 429:
            # Rate limited - wait longer
            time.sleep(5)
            continue

        if response.status_code != 200:
            response.raise_for_status()

        data = response.json()
        if not data:
            break

        all_data.extend(data)
        offset += max_per_page

    return all_data
```

**Recovery:**
- Wait 1-5 seconds before retrying
- Use exponential backoff
- Implement rate limiter before requests

---

### Scenario 4: Timezone Mismatch

**Not a direct API error, but common mistake:**

```python
# WRONG - No timezone specified
response = session.get(
    f"{BASE_URL}/availability/times",
    params={
        'appointmentTypeID': 12345,
        'date': '2025-11-15'
        # Missing timezone!
    }
)

# CORRECT - Always specify timezone
response = session.get(
    f"{BASE_URL}/availability/times",
    params={
        'appointmentTypeID': 12345,
        'date': '2025-11-15',
        'timezone': 'America/New_York'  # Client's timezone
    }
)
```

**Impact:**
- Appointments booked at wrong times
- Customer confusion and no-shows
- Reputational damage

**Prevention:**
- Always pass `timezone` to availability endpoints
- Validate timezone before use
- Display timezone in confirmation

---

## Error Response Format

### Standard Error Structure

```json
{
  "status_code": 400,
  "error": "error_code",
  "message": "Human-readable error message"
}
```

### Parsing Error Responses

```python
def parse_error_response(response):
    """Extract error details from API response"""
    try:
        error_data = response.json()
        return {
            'status_code': error_data.get('status_code', response.status_code),
            'error_code': error_data.get('error', 'unknown'),
            'message': error_data.get('message', 'No error message provided'),
            'http_status': response.status_code
        }
    except ValueError:
        # Response isn't JSON
        return {
            'status_code': response.status_code,
            'error_code': 'parsing_error',
            'message': response.text,
            'http_status': response.status_code
        }
```

---

## Retry Strategies

### Basic Retry with Exponential Backoff

```python
import time
import logging

def make_request_with_retry(
    method,
    url,
    max_retries=3,
    backoff_factor=2
):
    """
    Make API request with automatic retry on transient errors

    Retryable errors: 429, 500, 502, 503, 504, timeouts
    Non-retryable: 400, 401, 404, 403
    """
    for attempt in range(max_retries):
        try:
            response = session.request(
                method,
                url,
                timeout=30
            )

            # Success
            if response.status_code < 300:
                return response

            # Rate limit - always retry
            if response.status_code == 429:
                wait_time = backoff_factor ** attempt
                logging.warning(
                    f"Rate limited. Retry {attempt + 1}/{max_retries} "
                    f"in {wait_time}s"
                )
                time.sleep(wait_time)
                continue

            # Server error - retry
            if response.status_code >= 500:
                if attempt < max_retries - 1:
                    wait_time = backoff_factor ** attempt
                    logging.warning(
                        f"Server error {response.status_code}. "
                        f"Retry {attempt + 1}/{max_retries} in {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue

            # Client error - don't retry
            if response.status_code >= 400:
                return response

        except requests.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logging.warning(f"Request timeout. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise

        except requests.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                logging.warning(f"Connection error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            raise

    raise Exception("Max retries exceeded")
```

### Retry with Jitter

Jitter prevents "thundering herd" when many clients retry simultaneously:

```python
import random
import time

def calculate_backoff_with_jitter(attempt, base=2):
    """
    Exponential backoff with jitter
    Prevents synchronized retries from multiple clients
    """
    exponential = base ** attempt
    jitter = random.uniform(0, exponential)
    return jitter

# Example: 0-1s, 0-2s, 0-4s, 0-8s, 0-16s
for attempt in range(5):
    wait_time = calculate_backoff_with_jitter(attempt)
    time.sleep(wait_time)
    print(f"Attempt {attempt + 1} after {wait_time:.1f}s wait")
```

### Idempotent Retries

For safe retry on operations that aren't naturally idempotent:

```python
import uuid

def create_appointment_idempotent(appointment_data):
    """
    Create appointment with idempotency key
    Same request won't create duplicate if retried
    """
    # Generate unique idempotency key
    idempotency_key = appointment_data.get(
        'idempotency_key',
        str(uuid.uuid4())
    )

    # Store in database to detect duplicates
    if appointment_exists_with_key(idempotency_key):
        return get_appointment_by_key(idempotency_key)

    # Make request
    response = session.post(
        f"{BASE_URL}/appointments",
        json=appointment_data,
        headers={'Idempotency-Key': idempotency_key}
    )

    if response.status_code == 200:
        appointment = response.json()
        # Cache the key-to-appointment mapping
        cache_appointment_by_key(idempotency_key, appointment)
        return appointment

    # If fails, safe to retry with same key
    return None
```

---

## Circuit Breaker Pattern

Prevent cascading failures by temporarily stopping requests:

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Failing, refuse requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception(f"Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Reset on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Track failure and open circuit if threshold reached"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logging.error(
                f"Circuit breaker OPEN after {self.failure_count} failures"
            )

    def _should_attempt_reset(self):
        """Check if enough time passed to try again"""
        if not self.last_failure_time:
            return True

        return time.time() - self.last_failure_time > self.reset_timeout

# Usage
breaker = CircuitBreaker(failure_threshold=5, reset_timeout=60)

def get_appointments():
    return breaker.call(
        lambda: session.get(f"{BASE_URL}/appointments").json()
    )

try:
    appointments = get_appointments()
except Exception as e:
    logging.error(f"Failed to get appointments: {e}")
    # Show cached/stale data or error message to user
```

---

## Error Recovery Procedures

### Webhook Failures Recovery

**If webhook endpoint returns 500 errors persistently:**

1. Fix the endpoint (check application logs)
2. Test locally: `curl -X POST http://localhost/webhooks/acuity`
3. Deploy fix to production
4. Manually backfill missed events:

```python
from datetime import datetime, timedelta

def backfill_missed_webhooks(since_date):
    """Fetch appointments since webhook failure for manual processing"""
    # Determine when webhooks stopped working
    last_good_webhook = get_last_successful_webhook_timestamp()

    # Get all appointments since then
    params = {
        'minDate': last_good_webhook.strftime('%Y-%m-%d'),
        'maxDate': datetime.now().strftime('%Y-%m-%d')
    }

    appointments = session.get(
        f"{BASE_URL}/appointments",
        params=params
    ).json()

    # Process each as if webhook arrived
    for apt in appointments:
        process_webhook_event({
            'action': 'scheduled',
            'id': apt['id'],
            **apt
        })

    logging.info(f"Backfilled {len(appointments)} appointments")
```

### Rate Limiting Recovery

If repeatedly hitting rate limits:

1. Check current API usage
2. Implement rate limiter in code
3. Reduce batch sizes
4. Implement request queuing

```python
from queue import Queue
import threading

class APIRequestQueue:
    def __init__(self, rate_limit=9):
        self.queue = Queue()
        self.rate_limit = rate_limit
        self.running = True

        # Start worker thread
        worker = threading.Thread(target=self._worker, daemon=True)
        worker.start()

    def _worker(self):
        """Background thread processing queued requests"""
        request_times = []

        while self.running:
            # Get next request
            if self.queue.empty():
                time.sleep(0.1)
                continue

            request_func = self.queue.get()

            # Rate limiting
            now = time.time()
            request_times = [t for t in request_times if now - t < 1]

            if len(request_times) >= self.rate_limit:
                wait = 1 - (now - request_times[0])
                time.sleep(wait)
                now = time.time()

            # Execute request
            try:
                request_func()
            except Exception as e:
                logging.error(f"Request failed: {e}")

            request_times.append(now)

    def enqueue(self, func):
        """Queue a request for later execution"""
        self.queue.put(func)

# Usage
queue = APIRequestQueue(rate_limit=9)

for apt_id in appointment_ids:
    queue.enqueue(
        lambda id=apt_id: session.get(f"{BASE_URL}/appointments/{id}")
    )
```

---

## Logging Best Practices

### Structured Logging

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
logger = logging.getLogger('acuity_api')
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Log with context
logger.info("API request", extra={
    'method': 'GET',
    'endpoint': '/appointments',
    'status_code': 200,
    'duration_ms': 125
})
```

### What to Log

```python
# Log request details
logging.info(f"Requesting {method} {endpoint}")

# Log response status
logging.info(f"Response {status_code}")

# Log errors with context
logging.error(f"Request failed: {error}", extra={
    'status_code': response.status_code,
    'error': response.json(),
    'request_data': appointment_data,
    'attempt': attempt_number
})

# DON'T log sensitive data
# WRONG:
logging.info(f"Credentials: {user_id}:{api_key}")

# CORRECT:
logging.info(f"Using API key ****{api_key[-4:]}")
```

---

## Debugging Tips

### Enable Verbose Logging

```python
import logging
import http.client

# Enable HTTP debugging
http.client.HTTPConnection.debuglevel = 1

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('urllib3').setLevel(logging.DEBUG)
```

### Inspect API Response

```python
response = session.get(url)

print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text}")
print(f"JSON: {response.json()}")
```

### Test with curl

```bash
# Simple GET
curl -u "$USER_ID:$API_KEY" \
  https://acuityscheduling.com/api/v1/me

# With headers
curl -v -u "$USER_ID:$API_KEY" \
  https://acuityscheduling.com/api/v1/me

# POST request
curl -X POST -u "$USER_ID:$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"firstName":"John","lastName":"Doe","email":"john@example.com"}' \
  https://acuityscheduling.com/api/v1/appointments
```

---

## Error Handling Checklist

- [ ] Validate input before API calls
- [ ] Check HTTP status codes
- [ ] Parse error responses
- [ ] Implement retry logic for transient errors
- [ ] Don't retry on client errors (400, 401, 404)
- [ ] Use exponential backoff
- [ ] Implement rate limiting
- [ ] Log errors with context
- [ ] Don't log sensitive data
- [ ] Handle timeouts gracefully
- [ ] Implement circuit breaker for cascading failures
- [ ] Test error scenarios
- [ ] Monitor error rates
- [ ] Alert on critical failures
- [ ] Document expected errors

---

## See Also

- [API Endpoints Reference](api-endpoints-reference.md) - Status codes per endpoint
- [Risk Assessment & Pitfalls](../risk-assessment-guide.md) - Common integration mistakes
- [Webhook Integration Guide](webhook-integration-guide.md) - Webhook error handling

---

**Last Updated:** 2025-11-11
**Generated with Claude Code**
