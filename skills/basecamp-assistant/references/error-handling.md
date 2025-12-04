# Basecamp 4 API - Error Handling Guide

**Last Updated:** November 11, 2025
**Purpose:** Comprehensive error handling and recovery strategies
**Audience:** Developers building Basecamp integrations

---

## Table of Contents

1. [HTTP Status Codes](#http-status-codes)
2. [Error Response Format](#error-response-format)
3. [Critical Errors (Stop Immediately)](#critical-errors-stop-immediately)
4. [Retryable Errors (Exponential Backoff)](#retryable-errors-exponential-backoff)
5. [Transient Errors (Rate Limits)](#transient-errors-rate-limits)
6. [Special Cases](#special-cases)
7. [Error Handling Implementation](#error-handling-implementation)
8. [Monitoring & Alerting](#monitoring--alerting)

---

## HTTP Status Codes

### Success Responses (2xx)

| Code | Meaning | Context |
|------|---------|---------|
| 200 | OK | Successful GET or PUT request |
| 201 | Created | Successful POST request (resource created) |
| 204 | No Content | Successful DELETE request |

**Action:** Process the response normally

### Client Errors (4xx)

| Code | Meaning | Cause | Action | Retryable |
|------|---------|-------|--------|-----------|
| 400 | Bad Request | Missing User-Agent header, invalid JSON, malformed request | Fix the request, check headers | No |
| 401 | Unauthorized | Invalid or expired OAuth token | Refresh OAuth token | Yes (after refresh) |
| 403 | Forbidden | User lacks permission for operation | Verify user has access | No |
| 404 | Not Found | Resource deleted, doesn't exist, or no access | Check resource ID, verify access, don't retry | **No - Critical** |
| 415 | Unsupported Media Type | Missing Content-Type header on POST/PUT | Add Content-Type header | No |
| 429 | Too Many Requests | Rate limit exceeded | Wait Retry-After seconds, then retry | Yes |

### Server Errors (5xx)

| Code | Meaning | Cause | Action | Retryable |
|------|---------|-------|--------|-----------|
| 500 | Internal Server Error | Basecamp server error | Retry with exponential backoff | Yes |
| 502 | Bad Gateway | Temporarily unavailable | Retry with exponential backoff | Yes |
| 503 | Service Unavailable | Maintenance or overload | Retry with exponential backoff | Yes |
| 504 | Gateway Timeout | Request timeout at Basecamp | Retry with exponential backoff | Yes |

### Account Limits

| Code | Meaning | Cause | Action | Retryable |
|------|---------|-------|--------|-----------|
| 507 | Insufficient Storage | Free account project limit reached | Show upgrade prompt | No |

---

## Error Response Format

### Standard Error Response

All error responses follow this JSON format:

```json
{
  "error": "Human-readable error message"
}
```

### Example Error Responses

**400 Bad Request (Missing User-Agent):**
```json
{
  "error": "User-Agent header is required"
}
```

**415 Unsupported Media Type:**
```json
{
  "error": "Content-Type header must be application/json"
}
```

**404 Not Found with Reason Header:**
```http
HTTP/1.1 404 Not Found
Reason: Account Inactive
Content-Type: application/json

{
  "error": "The account could not be found."
}
```

**429 Too Many Requests:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 8
Content-Type: application/json

{
  "error": "Rate limit exceeded"
}
```

**507 Insufficient Storage:**
```json
{
  "error": "The project limit for this account has been reached."
}
```

---

## Critical Errors (Stop Immediately)

These errors indicate permanent failures that cannot be resolved by retrying.

### Error 400: Bad Request - Missing User-Agent

**Symptoms:**
```http
HTTP/1.1 400 Bad Request
```

**Cause:** The `User-Agent` header is missing from the request

**Why This Happens:**
- Basecamp requires User-Agent to identify all API clients
- This is a hard requirement with no exceptions
- Used for abuse tracking and client identification

**Fix:**

```bash
# WRONG - Missing User-Agent
curl -H "Authorization: Bearer $TOKEN" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"

# CORRECT - Include User-Agent
curl -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
```

**User-Agent Requirements:**
- Must include application name
- Must include contact email or URL
- Format: `AppName (contact@example.com)`

**Prevention:**
- Set User-Agent in environment variable
- Add to all request helper functions
- Validate in setup script

---

### Error 415: Unsupported Media Type - Missing Content-Type

**Symptoms:**
```http
HTTP/1.1 415 Unsupported Media Type
```

**Cause:** Missing `Content-Type` header on POST or PUT request

**Why This Happens:**
- Basecamp only accepts JSON
- Content-Type tells server how to parse request body
- Required on all write operations

**Fix:**

```bash
# WRONG - Missing Content-Type
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"name":"Project"}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"

# CORRECT - Include Content-Type
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"name":"Project"}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
```

**Content-Type Specification:**
- Must use: `application/json; charset=utf-8`
- Must include charset for international characters
- Only for POST/PUT requests

**Prevention:**
- Add Content-Type automatically for write operations
- Validate in request helpers
- Test all POST/PUT endpoints

---

### Error 404: Not Found - Permanent Failure

**Symptoms:**
```http
HTTP/1.1 404 Not Found
```

**Cause:** Resource doesn't exist, was deleted, or no access

**CRITICAL: Never retry 404 errors - they indicate permanent failures**

**Why 404 is Permanent:**
1. Resource is genuinely deleted (will never come back)
2. User lacks permission (won't gain access by retrying)
3. Account is inactive (requires external action to fix)
4. Retrying wastes API calls and delays error detection

**Check Reason Header:**

```bash
# Check for account inactive status
reason=$(curl -s -I -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: MyApp (me@example.com)" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json" | \
  grep -i "^Reason:" | cut -d' ' -f2-)

if [ "$reason" = "Account Inactive" ]; then
  # Account trial expired or suspended
  echo "Error: Basecamp account is inactive"
  echo "User needs to reactivate account at https://basecamp.com"
  exit 1
fi
```

**Handling 404:**

```python
if response.status_code == 404:
    # Check for account inactive
    reason = response.headers.get('Reason', '')
    if 'Inactive' in reason:
        # Account inactive - disable integration
        notify_user("Your Basecamp account is inactive")
        disable_integration()
    else:
        # Resource not found or no access
        notify_user("Resource not found or you don't have access")

    # DO NOT RETRY
    return False
```

**Prevention:**
- Verify resource exists before deleting
- Check user permissions before operations
- Monitor for 404 error spikes
- Set up alerts for repeated 404s

---

### Error 507: Insufficient Storage

**Symptoms:**
```json
{
  "error": "The project limit for this account has been reached."
}
```

**Cause:** Free Basecamp account has reached project limit

**Why This Happens:**
- Free accounts have limited projects (typically 3)
- Upgrading to paid account removes limit
- Each plan has different limits

**Fix:**
1. Delete unused projects to free up slots
2. Archive instead of delete (still uses slot)
3. Upgrade to paid Basecamp account

**User Communication:**

```python
if response.status_code == 507:
    show_upgrade_prompt(
        "Your Basecamp account has reached its project limit. "
        "Please upgrade to create more projects: https://basecamp.com/upgrade"
    )
```

**Prevention:**
- Check account before project creation
- Implement quota tracking
- Show upgrade prompts proactively

---

## Retryable Errors (Exponential Backoff)

These errors are transient and should be retried with exponential backoff.

### Error 401: Unauthorized - Expired Token

**Symptoms:**
```http
HTTP/1.1 401 Unauthorized
```

**Cause:** OAuth token is invalid or expired

**Why Tokens Expire:**
- OAuth tokens have expiration times (~2 weeks)
- Tokens must be refreshed using refresh_token
- Invalid token format or corrupted data

**Fix - Token Refresh:**

```python
def get_valid_token():
    """Get valid access token, refreshing if expired"""

    # Check if token expires soon (within 1 day)
    if token_expires_soon():
        refresh_token()

    return ACCESS_TOKEN

def refresh_token():
    """Refresh access token using refresh_token"""
    response = requests.post(
        'https://launchpad.37signals.com/authorization/token',
        data={
            'type': 'refresh',
            'refresh_token': REFRESH_TOKEN,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
    )

    if response.status_code == 200:
        data = response.json()
        ACCESS_TOKEN = data['access_token']
        REFRESH_TOKEN = data['refresh_token']
        save_tokens(ACCESS_TOKEN, REFRESH_TOKEN)
    else:
        # Token refresh failed - re-authenticate
        notify_user("Please re-authenticate")
        trigger_oauth_flow()
```

**Prevention:**
- Store both access_token and refresh_token
- Implement automatic refresh before expiration
- Set up cron job for token refresh
- Monitor for 401 errors

---

### Error 5xx: Server Errors

**Symptoms:**
```http
HTTP/1.1 500 Internal Server Error
HTTP/1.1 502 Bad Gateway
HTTP/1.1 503 Service Unavailable
HTTP/1.1 504 Gateway Timeout
```

**Cause:** Basecamp server issues, maintenance, or overload

**Why Retry Helps:**
- Basecamp infrastructure may temporarily fail
- Automatic retries allow recovery
- Exponential backoff prevents flooding

**Implementation - Exponential Backoff:**

```python
def retry_with_exponential_backoff(func, max_retries=5):
    """Retry with exponential backoff: 1s, 2s, 4s, 8s, 16s"""
    retry_count = 0
    backoff = 1

    while retry_count < max_retries:
        try:
            return func()
        except Exception as e:
            if should_retry(e):
                print(f"Retrying in {backoff}s... ({e})")
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)  # Cap at 30s
                retry_count += 1
            else:
                raise

def should_retry(error):
    """Determine if error is retryable"""
    if hasattr(error, 'status_code'):
        # Retry 5xx and 429, not 4xx (except 401)
        return error.status_code >= 500 or error.status_code == 429
    return False
```

**Backoff Strategy:**
- Start with 1 second
- Double each time (exponential growth)
- Cap at 30 seconds to prevent excessive waits
- Add jitter for distributed systems (optional)

**Prevention:**
- Implement backoff from day one
- Monitor error rates by endpoint
- Set up alerts for elevated error rates
- Have fallback/graceful degradation strategy

---

## Transient Errors (Rate Limits)

### Error 429: Too Many Requests

**Symptoms:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 8
```

**Cause:** Exceeded rate limit (50 requests per 10 seconds per IP)

**Rate Limit Details:**
- Limit: 50 requests per 10 seconds
- Scoped by: IP address (not per token)
- Response header: `Retry-After: {seconds}`
- Implications: Could affect all clients on same IP

**Why Rate Limits Matter:**
- Basecamp protects infrastructure
- Prevents denial-of-service
- Retrying immediately flags client for flooding
- Continued violations may result in IP ban

**Fix - Respect Retry-After Header:**

```bash
# Get retry-after value from response
retry_after=$(curl -s -i "$url" | grep -i "Retry-After:" | awk '{print $2}')

if [ ! -z "$retry_after" ]; then
  echo "Rate limited. Waiting ${retry_after}s as instructed..."
  sleep $retry_after
else
  # Fallback to exponential backoff if header missing
  sleep 2
fi

# Then retry the request
curl -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "$url"
```

**Python Implementation:**

```python
import time

def request_with_rate_limit_handling(url):
    """Make request, handling rate limits properly"""
    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 429:
            # Rate limited - use Retry-After header
            retry_after = int(response.headers.get('Retry-After', 2))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            continue

        return response
```

**Prevention - Request Rate Tracking:**

```python
from collections import deque
from datetime import datetime, timedelta
import time

class RateLimiter:
    def __init__(self, max_requests=50, window_seconds=10):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times = deque()

    def is_available(self):
        """Check if request can be made"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # Remove old requests
        while self.request_times and self.request_times[0] < cutoff:
            self.request_times.popleft()

        # Check if under limit
        return len(self.request_times) < self.max_requests

    def wait_if_needed(self):
        """Wait if necessary to stay under rate limit"""
        while not self.is_available():
            # Calculate wait time
            oldest = self.request_times[0]
            age = (datetime.now() - oldest).total_seconds()
            wait = self.window_seconds - age

            if wait > 0:
                print(f"Rate limit approaching. Waiting {wait:.1f}s...")
                time.sleep(wait + 0.1)  # Small buffer

    def record_request(self):
        """Record that a request was made"""
        self.request_times.append(datetime.now())

# Usage
limiter = RateLimiter()

def make_request(url):
    limiter.wait_if_needed()
    response = requests.get(url, headers=headers)
    limiter.record_request()
    return response
```

**Prevention Best Practices:**
- Use request rate tracker
- Set limit buffer at 45 requests (not 50)
- Add delays between high-frequency requests
- Use HTTP caching (ETags) to reduce requests
- Batch operations where possible
- Monitor real-time request rate

---

## Special Cases

### Account Inactive (404 with Reason Header)

**Detection:**
```http
HTTP/1.1 404 Not Found
Reason: Account Inactive
```

**Meaning:**
- Basecamp trial period expired
- Account suspended or deleted
- User needs to reactivate

**Handling:**

```python
def handle_account_inactive():
    """Gracefully handle inactive account"""

    # Disable integration
    disable_feature('basecamp')

    # Notify user
    send_email(
        to=user.email,
        subject="Your Basecamp account needs attention",
        body="""
        Your Basecamp account appears to be inactive.

        Please reactivate your account to continue using our integration:
        https://basecamp.com/account/reactivate

        Once reactivated, you may need to re-authorize the integration.
        """
    )

    # Show in-app message
    show_message(
        "Your Basecamp integration is temporarily disabled. "
        "Please reactivate your Basecamp account."
    )
```

### Invalid OAuth Token Checksum

**Error Message:**
```
OAuth token could not be verified. The internal checksum failed,
so the token data was somehow mangled or tampered with.
```

**Cause:** Using entire OAuth JSON response instead of extracting access_token

**Fix:**

```python
# WRONG - Using entire response
token = oauth_response.text  # This is JSON with quotes, line breaks, etc.

# CORRECT - Parse and extract
token_data = oauth_response.json()
token = token_data['access_token']  # Just the token string
```

---

## Error Handling Implementation

### Complete Error Handler

```python
import time
import requests
from functools import wraps

class BasecampAPIError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")

class RateLimitError(BasecampAPIError):
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__(429, f"Rate limited. Retry after {retry_after}s")

def handle_response(response):
    """Parse response and handle errors"""

    if 200 <= response.status_code < 300:
        # Success
        return response

    elif response.status_code == 400:
        raise BasecampAPIError(400, "Bad request - check headers and format")

    elif response.status_code == 401:
        raise BasecampAPIError(401, "Unauthorized - refresh OAuth token")

    elif response.status_code == 404:
        reason = response.headers.get('Reason', '')
        if 'Inactive' in reason:
            raise BasecampAPIError(404, f"Account inactive: {reason}")
        else:
            raise BasecampAPIError(404, "Resource not found")

    elif response.status_code == 415:
        raise BasecampAPIError(415, "Missing Content-Type header")

    elif response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        raise RateLimitError(retry_after)

    elif response.status_code >= 500:
        raise BasecampAPIError(
            response.status_code,
            f"Server error - {response.status_code}"
        )

    elif response.status_code == 507:
        raise BasecampAPIError(507, "Account project limit reached")

    else:
        raise BasecampAPIError(response.status_code, "Unknown error")

def retry_on_transient_error(max_retries=3):
    """Decorator to handle transient errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            backoff = 1

            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    print(f"Rate limited. Waiting {e.retry_after}s...")
                    time.sleep(e.retry_after)
                    retry_count += 1

                except BasecampAPIError as e:
                    if e.status_code >= 500:
                        print(f"Server error {e.status_code}. Retrying in {backoff}s...")
                        time.sleep(backoff)
                        backoff = min(backoff * 2, 30)
                        retry_count += 1
                    else:
                        # Non-retryable error
                        raise

                except Exception as e:
                    print(f"Unexpected error: {e}")
                    raise

            raise Exception(f"Max retries ({max_retries}) exceeded")

        return wrapper
    return decorator

# Usage
@retry_on_transient_error(max_retries=5)
def get_projects():
    response = requests.get(
        f"https://3.basecampapi.com/{ACCOUNT_ID}/projects.json",
        headers={
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'User-Agent': USER_AGENT
        }
    )
    handle_response(response)
    return response.json()
```

---

## Monitoring & Alerting

### Key Metrics to Monitor

```python
# Track error rates
error_counts = {
    '400': 0,  # Bad request
    '401': 0,  # Unauthorized
    '404': 0,  # Not found
    '429': 0,  # Rate limited
    '5xx': 0   # Server errors
}

def log_error(status_code, endpoint):
    """Log errors for monitoring"""
    if status_code >= 500:
        error_counts['5xx'] += 1
    else:
        error_counts[str(status_code)] = error_counts.get(str(status_code), 0) + 1

    # Alert if too many errors
    total_errors = sum(error_counts.values())
    if total_errors > 100:
        alert("High error rate detected")

def get_error_metrics():
    """Get error rate statistics"""
    return {
        'unauthorized_rate': error_counts['401'] / total_requests,
        'rate_limit_rate': error_counts['429'] / total_requests,
        'not_found_rate': error_counts['404'] / total_requests,
        'server_error_rate': error_counts['5xx'] / total_requests
    }
```

### Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| 401 errors | >1% of requests | Check token refresh |
| 404 errors | >0.5% of requests | Check IDs and permissions |
| 429 errors | Any | Review rate limiting |
| 5xx errors | >2% of requests | Page on-call engineer |
| Response time | >5s average | Check Basecamp status |

---

## Related Documentation

- [API Reference](./api-reference.md) - Endpoint details
- [Rate Limiting](./rate-limiting.md) - Rate limit management
- [Pagination](./pagination.md) - Safe pagination
- [Workflow Patterns](./workflow-patterns.md) - Common workflows with error handling

---

**For questions or issues:** Consult the [Basecamp API Documentation](https://github.com/basecamp/bc4-api)
