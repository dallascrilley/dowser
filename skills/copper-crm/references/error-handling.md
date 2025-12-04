# Copper CRM - Comprehensive Error Handling Guide

## Table of Contents
1. [HTTP Status Code Reference](#http-status-code-reference)
2. [Error Response Formats](#error-response-formats)
3. [Common Error Scenarios](#common-error-scenarios)
4. [Validation Errors (422)](#validation-errors-422)
5. [Rate Limiting (429)](#rate-limiting-429)
6. [Recovery Strategies](#recovery-strategies)
7. [Client-Side Validation](#client-side-validation)
8. [Bulk Operation Error Handling](#bulk-operation-error-handling)
9. [Debug Checklist](#debug-checklist)
10. [Code Examples](#code-examples)

---

## HTTP Status Code Reference

### Success Codes

| Code | Status | Meaning | Action Required |
|------|--------|---------|----------------|
| 200 | OK | Request succeeded | Continue normal flow |
| 201 | Created | Resource created successfully | Save returned ID for future reference |

### Client Error Codes (4xx)

| Code | Status | Meaning | Typical Cause | Retry? |
|------|--------|---------|---------------|--------|
| 400 | Bad Request | Invalid request format or parameters | Malformed JSON, invalid parameters | No - Fix request |
| 401 | Unauthorized | Missing or invalid authentication | Invalid API key, missing headers | No - Fix credentials |
| 403 | Forbidden | Valid auth but insufficient permissions | User lacks required permissions | No - Check permissions |
| 404 | Not Found | Resource doesn't exist | Invalid ID, resource deleted | No - Verify ID |
| 422 | Unprocessable Entity | Valid request but business logic error | Duplicate record, validation failure | Maybe - See details |
| 429 | Too Many Requests | Rate limit exceeded | Too many requests in time window | Yes - Exponential backoff |

### Server Error Codes (5xx)

| Code | Status | Meaning | Action Required |
|------|--------|---------|----------------|
| 500 | Internal Server Error | Server-side error | Retry with exponential backoff |
| 502 | Bad Gateway | Upstream service issue | Retry with exponential backoff |
| 503 | Service Unavailable | Temporary service outage | Retry with exponential backoff |
| 504 | Gateway Timeout | Request timeout | Retry with exponential backoff |

---

## Error Response Formats

### Standard Error Response Structure

```json
{
  "message": "Error description",
  "status": 400
}
```

### Detailed Validation Error Response

```json
{
  "message": "Validation failed",
  "status": 422,
  "errors": {
    "email": [
      {
        "error": "invalid",
        "message": "Email address already exists"
      }
    ],
    "name": [
      {
        "error": "required",
        "message": "Name is required"
      }
    ]
  }
}
```

### Bulk Operation Error Response

```json
{
  "errors": [
    {
      "index": 0,
      "id": null,
      "errors": {
        "name": [
          {
            "error": "invalid",
            "message": "Name is required"
          }
        ]
      }
    },
    {
      "index": 2,
      "id": null,
      "errors": {
        "email": [
          {
            "error": "duplicate",
            "message": "Email address already exists"
          }
        ]
      }
    }
  ],
  "successes": [
    {
      "index": 1,
      "id": 12345,
      "name": "Successfully Created Lead"
    }
  ]
}
```

---

## Common Error Scenarios

### 1. Authentication Errors (401)

**Cause:** Missing or invalid API key

**Error Response:**
```json
{
  "message": "Unauthorized",
  "status": 401
}
```

**Solutions:**
- Verify API key is correct and not expired
- Check that all required headers are present:
  - `X-PW-AccessToken`: Your API key
  - `X-PW-Application`: `developer_api`
  - `X-PW-UserEmail`: Email of token owner
  - `Content-Type`: `application/json`
- Ensure email matches the user who generated the API key
- Generate a new API key if current one is compromised

**Code Example:**
```python
def validate_auth_headers(api_key: str, user_email: str) -> dict:
    """Validate and return proper auth headers"""
    if not api_key:
        raise ValueError("API key is required")
    if not user_email or "@" not in user_email:
        raise ValueError("Valid user email is required")

    return {
        "X-PW-AccessToken": api_key,
        "X-PW-Application": "developer_api",
        "X-PW-UserEmail": user_email,
        "Content-Type": "application/json",
    }
```

### 2. Permission Errors (403)

**Cause:** Valid authentication but insufficient permissions

**Error Response:**
```json
{
  "message": "Forbidden - insufficient permissions",
  "status": 403
}
```

**Solutions:**
- Verify user has appropriate role in Copper CRM
- Check if user has access to the specific resource
- Ensure user is not trying to modify system-level settings without admin rights
- Contact Copper CRM administrator to grant necessary permissions

### 3. Resource Not Found (404)

**Cause:** Requested resource doesn't exist

**Error Response:**
```json
{
  "message": "Lead not found",
  "status": 404
}
```

**Solutions:**
- Verify the resource ID is correct
- Check if resource was deleted (use search to verify)
- Ensure you're using the correct endpoint for the resource type
- Confirm you have access to view the resource

**Code Example:**
```python
def safe_get_resource(client, resource_type: str, resource_id: int):
    """Safely get resource with proper error handling"""
    try:
        response = client.get(f"/{resource_type}/{resource_id}")
        if response.status_code == 404:
            return None  # Resource doesn't exist
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise
```

### 4. Bad Request (400)

**Cause:** Malformed request or invalid parameters

**Common Issues:**
- Invalid JSON syntax
- Wrong data types (string instead of number)
- Invalid enum values
- Malformed email addresses or phone numbers

**Error Response:**
```json
{
  "message": "Invalid JSON in request body",
  "status": 400
}
```

**Solutions:**
- Validate JSON syntax before sending
- Ensure data types match API expectations
- Verify all enum values are valid (check API docs)
- Use JSON schema validation on client side

---

## Validation Errors (422)

### Overview

422 errors indicate the request was well-formed but failed business logic validation. These are the most common errors when working with Copper CRM.

### Common Validation Scenarios

#### 1. Duplicate Email Addresses (People)

**Rule:** Email addresses must be unique across all People records

**Error Response:**
```json
{
  "message": "Email address already exists",
  "status": 422,
  "errors": {
    "email": [
      {
        "error": "duplicate",
        "message": "A person with this email already exists"
      }
    ]
  }
}
```

**Solutions:**
```python
def upsert_person(client, person_data):
    """Create or update person based on email uniqueness"""
    email = person_data.get("email", {}).get("email")

    if not email:
        raise ValueError("Email is required for person records")

    # Search for existing person by email
    existing = client.search_people({"email": email})

    if existing and len(existing) > 0:
        # Update existing person
        person_id = existing[0]["id"]
        return client.update_person(person_id, person_data)
    else:
        # Create new person
        return client.create_person(person_data)
```

#### 2. Duplicate Company Email Domains

**Rule:** Email domains must be unique across Companies

**Error Response:**
```json
{
  "message": "Email domain already exists",
  "status": 422
}
```

**Solution:**
- Search for companies by domain before creating
- Use UPSERT pattern (search then create/update)
- Consider using a different identifying field

#### 3. Missing Required Fields

**Common Required Fields:**

| Entity Type | Required Fields |
|-------------|----------------|
| Leads | `name` |
| People | `name`, `email` (unique) |
| Companies | `name` |
| Opportunities | `name`, `primary_contact_id` OR `company_id` |
| Activities | `parent`, `type` |

**Error Response:**
```json
{
  "message": "Validation failed",
  "status": 422,
  "errors": {
    "name": [
      {
        "error": "required",
        "message": "Name is required"
      }
    ]
  }
}
```

**Solution:**
```python
# Validate before sending
REQUIRED_FIELDS = {
    "leads": ["name"],
    "people": ["name", "email"],
    "companies": ["name"],
    "opportunities": ["name"],
}

def validate_required_fields(entity_type: str, data: dict) -> list:
    """Validate required fields are present"""
    errors = []
    required = REQUIRED_FIELDS.get(entity_type, [])

    for field in required:
        if not data.get(field):
            errors.append(f"Missing required field: {field}")

    return errors
```

#### 4. Invalid Data Types

**Error Response:**
```json
{
  "message": "Validation failed",
  "status": 422,
  "errors": {
    "monetary_value": [
      {
        "error": "invalid_type",
        "message": "monetary_value must be a number"
      }
    ]
  }
}
```

**Common Type Validation:**
```python
def validate_opportunity_data(data: dict) -> list:
    """Validate opportunity data types"""
    errors = []

    # Validate monetary_value is numeric
    if "monetary_value" in data:
        try:
            float(data["monetary_value"])
        except (ValueError, TypeError):
            errors.append("monetary_value must be a number")

    # Validate close_date format (mm/dd/yyyy)
    if "close_date" in data:
        close_date = data["close_date"]
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', close_date):
            errors.append("close_date must be in format mm/dd/yyyy")

    return errors
```

#### 5. Invalid References

**Error Response:**
```json
{
  "message": "Invalid company_id",
  "status": 422
}
```

**Solution:**
```python
def validate_references(client, data: dict) -> list:
    """Validate referenced IDs exist"""
    errors = []

    # Validate company_id if present
    if company_id := data.get("company_id"):
        company = client.get_company(company_id)
        if not company:
            errors.append(f"Company {company_id} not found")

    # Validate primary_contact_id if present
    if contact_id := data.get("primary_contact_id"):
        person = client.get_person(contact_id)
        if not person:
            errors.append(f"Person {contact_id} not found")

    return errors
```

---

## Rate Limiting (429)

### Rate Limit Rules

| API Type | Rate Limit | Time Window | Recovery Time |
|----------|-----------|-------------|---------------|
| Standard APIs | 180 requests | 1 minute (rolling) | Wait ~1 minute |
| Bulk APIs | 3 requests | 1 second | Wait ~1 second |
| Search APIs | 180 requests | 1 minute (rolling) | Wait ~1 minute |

### Rate Limit Error Response

```json
{
  "message": "Rate limit exceeded",
  "status": 429
}
```

### Exponential Backoff Implementation

**Strategy:** Retry with progressively longer delays

```python
import time
import random
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

def exponential_backoff(
    func: Callable[[], T],
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> T:
    """
    Execute function with exponential backoff retry logic

    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Multiplier for exponential growth
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Result of successful function call

    Raises:
        Last exception if all retries exhausted
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e

            # Don't retry on non-retryable errors
            if hasattr(e, 'response'):
                status_code = getattr(e.response, 'status_code', None)
                if status_code and status_code not in [429, 500, 502, 503, 504]:
                    raise

            if attempt >= max_retries:
                raise last_exception

            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)

            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())

            print(f"Attempt {attempt + 1} failed. Retrying in {delay:.2f}s...")
            time.sleep(delay)

    raise last_exception
```

### Rate Limiter Class

```python
import time
from collections import deque
from threading import Lock

class RateLimiter:
    """Token bucket rate limiter"""

    def __init__(self, requests_per_second: float = 3.0, burst_size: int = 5):
        """
        Initialize rate limiter

        Args:
            requests_per_second: Max sustained request rate
            burst_size: Max burst of requests allowed
        """
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = Lock()

    def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens, blocking if necessary

        Args:
            tokens: Number of tokens to acquire

        Returns:
            Time spent waiting (in seconds)
        """
        with self.lock:
            # Refill tokens based on time elapsed
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(
                self.burst_size,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # Wait if not enough tokens
            wait_time = 0.0
            if self.tokens < tokens:
                needed = tokens - self.tokens
                wait_time = needed / self.rate
                time.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= tokens

            return wait_time

# Usage
standard_limiter = RateLimiter(requests_per_second=180/60)  # 3 req/sec
bulk_limiter = RateLimiter(requests_per_second=3.0)  # 3 req/sec

def rate_limited_request(limiter: RateLimiter, func: Callable):
    """Execute function with rate limiting"""
    limiter.acquire()
    return func()
```

### Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    """Rate limiter that adapts to 429 responses"""

    def __init__(self, initial_rate: float = 3.0, min_rate: float = 0.5):
        self.current_rate = initial_rate
        self.min_rate = min_rate
        self.max_rate = initial_rate
        self.last_request_time = 0
        self.consecutive_429s = 0

    def wait_if_needed(self):
        """Wait if necessary to respect current rate limit"""
        now = time.time()
        min_interval = 1.0 / self.current_rate
        elapsed = now - self.last_request_time

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_request_time = time.time()

    def record_success(self):
        """Record successful request - gradually increase rate"""
        self.consecutive_429s = 0
        # Gradually increase rate (max 10% per success)
        self.current_rate = min(
            self.max_rate,
            self.current_rate * 1.1
        )

    def record_429(self):
        """Record 429 error - decrease rate"""
        self.consecutive_429s += 1
        # Decrease rate by 50% on first 429, more aggressive after
        reduction_factor = 0.5 ** self.consecutive_429s
        self.current_rate = max(
            self.min_rate,
            self.current_rate * reduction_factor
        )
```

---

## Recovery Strategies

### 1. Retry Strategy Matrix

| Error Code | Retry? | Strategy | Max Retries | Notes |
|-----------|--------|----------|-------------|-------|
| 429 | Yes | Exponential backoff | 5 | Start with 1s delay |
| 500 | Yes | Exponential backoff | 3 | Server error |
| 502 | Yes | Exponential backoff | 3 | Gateway error |
| 503 | Yes | Exponential backoff | 3 | Service unavailable |
| 504 | Yes | Linear backoff | 2 | Timeout |
| 422 | Conditional | Fix data then retry | 1 | Only if fixable |
| 401 | No | Fix credentials | 0 | Auth error |
| 403 | No | Check permissions | 0 | Permission error |
| 404 | No | Verify ID | 0 | Not found |
| 400 | No | Fix request | 0 | Bad request |

### 2. Idempotency Patterns

**Problem:** Retries can cause duplicate records

**Solution:** Implement idempotency

```python
import hashlib
import json

def generate_idempotency_key(data: dict) -> str:
    """Generate idempotency key from request data"""
    # Sort keys for consistent hashing
    normalized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

class IdempotentClient:
    """Client with idempotency tracking"""

    def __init__(self, api_client):
        self.client = api_client
        self.completed_requests = {}  # key -> response

    def create_with_idempotency(self, endpoint: str, data: dict):
        """Create resource with idempotency protection"""
        key = generate_idempotency_key(data)

        # Check if already processed
        if key in self.completed_requests:
            return self.completed_requests[key]

        # Make request
        response = self.client.post(endpoint, data)

        # Store result
        if response.status_code in [200, 201]:
            self.completed_requests[key] = response.json()

        return response.json()
```

### 3. Circuit Breaker Pattern

**Purpose:** Prevent cascading failures

```python
import time
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 2

class CircuitBreaker:
    """Circuit breaker for API calls"""

    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def call(self, func: Callable) -> any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func()
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise

    def _record_success(self):
        """Record successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0

    def _record_failure(self):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not self.last_failure_time:
            return True

        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.recovery_timeout
```

---

## Client-Side Validation

### Pre-Request Validation

**Benefits:**
- Reduce API calls
- Faster error feedback
- Lower rate limit usage
- Better user experience

### Validation Framework

```python
from typing import Dict, List, Any, Callable
from dataclasses import dataclass

@dataclass
class ValidationRule:
    """Single validation rule"""
    field: str
    validator: Callable[[Any], bool]
    error_message: str

class Validator:
    """Client-side validation engine"""

    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {
            "leads": [],
            "people": [],
            "companies": [],
            "opportunities": [],
        }
        self._setup_rules()

    def _setup_rules(self):
        """Define validation rules for each entity type"""

        # Lead rules
        self.rules["leads"] = [
            ValidationRule(
                field="name",
                validator=lambda x: bool(x and len(x.strip()) > 0),
                error_message="Name is required"
            ),
            ValidationRule(
                field="email",
                validator=lambda x: not x or "@" in x,
                error_message="Invalid email format"
            ),
        ]

        # People rules
        self.rules["people"] = [
            ValidationRule(
                field="name",
                validator=lambda x: bool(x and len(x.strip()) > 0),
                error_message="Name is required"
            ),
            ValidationRule(
                field="email",
                validator=lambda x: x and "@" in x.get("email", ""),
                error_message="Valid email is required for people"
            ),
        ]

        # Opportunity rules
        self.rules["opportunities"] = [
            ValidationRule(
                field="name",
                validator=lambda x: bool(x and len(x.strip()) > 0),
                error_message="Name is required"
            ),
            ValidationRule(
                field="monetary_value",
                validator=lambda x: not x or self._is_numeric(x),
                error_message="Monetary value must be numeric"
            ),
            ValidationRule(
                field="close_date",
                validator=lambda x: not x or self._is_valid_date(x),
                error_message="Close date must be in mm/dd/yyyy format"
            ),
        ]

    @staticmethod
    def _is_numeric(value: Any) -> bool:
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def _is_valid_date(date_str: str) -> bool:
        """Validate date format mm/dd/yyyy"""
        import re
        return bool(re.match(r'^\d{2}/\d{2}/\d{4}$', date_str))

    def validate(self, entity_type: str, data: dict) -> List[str]:
        """
        Validate data against rules

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        rules = self.rules.get(entity_type, [])

        for rule in rules:
            value = data.get(rule.field)
            if not rule.validator(value):
                errors.append(rule.error_message)

        return errors

# Usage
validator = Validator()

def create_lead_with_validation(client, lead_data: dict):
    """Create lead with client-side validation"""
    # Validate before sending
    errors = validator.validate("leads", lead_data)
    if errors:
        raise ValueError(f"Validation errors: {'; '.join(errors)}")

    # Send to API
    return client.create_lead(lead_data)
```

### Email Validation

```python
import re

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_email_uniqueness(client, email: str, entity_type: str = "people"):
    """Check if email already exists"""
    search_results = client.search(entity_type, {"email": email})
    return len(search_results) == 0
```

---

## Bulk Operation Error Handling

### Bulk Operation Challenges

1. Partial failures (some records succeed, some fail)
2. Order dependencies (e.g., create company before person)
3. Rate limiting (3 requests/second for bulk APIs)
4. Error recovery (resume from failure point)

### Batch Processing with Error Handling

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import time

@dataclass
class BatchResult:
    """Result of processing a single record"""
    index: int
    success: bool
    record_id: Optional[str] = None
    error: Optional[str] = None
    is_duplicate: bool = False
    retry_count: int = 0

class BulkProcessor:
    """Process bulk operations with error handling"""

    def __init__(self, client, batch_size: int = 10, rate_limit: float = 3.0):
        self.client = client
        self.batch_size = batch_size
        self.rate_limiter = RateLimiter(requests_per_second=rate_limit)
        self.results: List[BatchResult] = []

    def process_records(
        self,
        entity_type: str,
        records: List[Dict],
        upsert: bool = True,
        save_checkpoint: bool = True,
    ) -> Dict[str, Any]:
        """
        Process records in batches with error handling

        Args:
            entity_type: Type of entity (leads, people, etc.)
            records: List of records to process
            upsert: If True, update existing records instead of failing
            save_checkpoint: Save progress after each batch

        Returns:
            Summary of processing results
        """
        total = len(records)
        processed = 0

        # Process in batches
        for batch_start in range(0, total, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total)
            batch = records[batch_start:batch_end]

            # Process each record in batch
            for index, record in enumerate(batch, start=batch_start):
                result = self._process_single_record(
                    entity_type=entity_type,
                    record=record,
                    index=index,
                    upsert=upsert,
                )
                self.results.append(result)
                processed += 1

            # Save checkpoint
            if save_checkpoint:
                self._save_checkpoint(processed, total)

            print(f"Processed {processed}/{total} records")

        return self._generate_summary()

    def _process_single_record(
        self,
        entity_type: str,
        record: Dict,
        index: int,
        upsert: bool,
    ) -> BatchResult:
        """Process single record with retry logic"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                # Rate limiting
                self.rate_limiter.acquire()

                # Check for duplicates if upserting
                duplicate_id = None
                if upsert:
                    duplicate_id = self._find_duplicate(entity_type, record)

                # Create or update
                if duplicate_id:
                    response = self.client.update(
                        entity_type, duplicate_id, record
                    )
                    return BatchResult(
                        index=index,
                        success=True,
                        record_id=str(duplicate_id),
                        is_duplicate=True,
                        retry_count=attempt,
                    )
                else:
                    response = self.client.create(entity_type, record)
                    return BatchResult(
                        index=index,
                        success=True,
                        record_id=str(response.get("id")),
                        retry_count=attempt,
                    )

            except Exception as e:
                # Check if retryable
                if not self._is_retryable_error(e):
                    return BatchResult(
                        index=index,
                        success=False,
                        error=str(e),
                        retry_count=attempt,
                    )

                # Wait before retry
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        # Max retries exhausted
        return BatchResult(
            index=index,
            success=False,
            error="Max retries exhausted",
            retry_count=max_retries,
        )

    @staticmethod
    def _is_retryable_error(error: Exception) -> bool:
        """Check if error is retryable"""
        if hasattr(error, 'response'):
            status = getattr(error.response, 'status_code', None)
            return status in [429, 500, 502, 503, 504]
        return False

    def _find_duplicate(self, entity_type: str, record: Dict) -> Optional[str]:
        """Find duplicate record"""
        # Entity-specific duplicate detection
        if entity_type == "people":
            email = record.get("email", {}).get("email")
            if email:
                results = self.client.search(entity_type, {"email": email})
                if results:
                    return str(results[0]["id"])
        elif entity_type == "companies":
            name = record.get("name")
            if name:
                results = self.client.search(entity_type, {"name": name})
                if results:
                    return str(results[0]["id"])

        return None

    def _save_checkpoint(self, processed: int, total: int):
        """Save progress checkpoint"""
        checkpoint_data = {
            "processed": processed,
            "total": total,
            "results": [
                {
                    "index": r.index,
                    "success": r.success,
                    "record_id": r.record_id,
                    "error": r.error,
                }
                for r in self.results
            ]
        }

        # Save to file or database
        with open(".bulk_import_checkpoint.json", "w") as f:
            json.dump(checkpoint_data, f)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of results"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        duplicates = [r for r in successful if r.is_duplicate]

        return {
            "total": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "duplicates": len(duplicates),
            "success_rate": len(successful) / len(self.results) * 100,
            "failed_records": [
                {"index": r.index, "error": r.error}
                for r in failed
            ],
        }
```

---

## Debug Checklist

### Pre-Request Checklist

- [ ] All required headers present?
  - [ ] `X-PW-AccessToken` set
  - [ ] `X-PW-Application` = `developer_api`
  - [ ] `X-PW-UserEmail` matches token owner
  - [ ] `Content-Type` = `application/json`

- [ ] Authentication valid?
  - [ ] API key not expired
  - [ ] Email matches key owner
  - [ ] User has necessary permissions

- [ ] Request body valid?
  - [ ] Valid JSON syntax
  - [ ] All required fields present
  - [ ] Correct data types
  - [ ] No duplicate fields

- [ ] References valid?
  - [ ] IDs exist (company_id, primary_contact_id, etc.)
  - [ ] User has access to referenced resources

### Post-Error Checklist

- [ ] Check status code category
  - [ ] 4xx = client error (fix request)
  - [ ] 5xx = server error (retry)

- [ ] For 422 errors:
  - [ ] Check for duplicate email (People)
  - [ ] Check for duplicate domain (Companies)
  - [ ] Verify all required fields present
  - [ ] Validate data types
  - [ ] Check referenced IDs exist

- [ ] For 429 errors:
  - [ ] Implement exponential backoff
  - [ ] Check rate (180/min standard, 3/sec bulk)
  - [ ] Add jitter to prevent thundering herd

- [ ] For 401/403 errors:
  - [ ] Regenerate API key
  - [ ] Verify user permissions
  - [ ] Check email matches key owner

### Search Troubleshooting

- [ ] Getting 0 results but records exist?
  - [ ] Filters too restrictive?
  - [ ] Using `allow_empty` for optional fields?
  - [ ] Correct search syntax?

- [ ] Pagination issues?
  - [ ] Sorting by stable field (date_modified)?
  - [ ] Checking `X-PW-TOTAL` header?
  - [ ] Page size within limits (max 200)?

### Rate Limiting Checklist

- [ ] Implementing rate limiting?
  - [ ] Token bucket or leaky bucket algorithm
  - [ ] 3 requests/second for bulk APIs
  - [ ] 180 requests/minute for standard APIs

- [ ] Handling 429 responses?
  - [ ] Exponential backoff implemented
  - [ ] Maximum retry count set
  - [ ] Jitter added to backoff

---

## Code Examples

### Complete Error Handler Class

```python
import time
import logging
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)

@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

class CopperAPIError(Exception):
    """Base exception for Copper API errors"""
    def __init__(self, message: str, status_code: int, response: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(self.message)

class CopperValidationError(CopperAPIError):
    """Validation error (422)"""
    pass

class CopperRateLimitError(CopperAPIError):
    """Rate limit error (429)"""
    pass

class CopperAuthError(CopperAPIError):
    """Authentication error (401)"""
    pass

class CopperErrorHandler:
    """Comprehensive error handler for Copper CRM API"""

    def __init__(self, retry_config: RetryConfig = None):
        self.retry_config = retry_config or RetryConfig()
        self.rate_limiter = RateLimiter(requests_per_second=3.0)

    def handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response with comprehensive error handling

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response

        Raises:
            Appropriate CopperAPIError subclass
        """
        # Success
        if response.status_code in [200, 201]:
            return response.json() if response.text else {}

        # Parse error response
        try:
            error_data = response.json()
        except:
            error_data = {"message": response.text or "Unknown error"}

        message = error_data.get("message", "Unknown error")

        # Raise specific exception based on status code
        if response.status_code == 400:
            raise CopperAPIError(
                f"Bad Request: {message}",
                status_code=400,
                response=error_data
            )
        elif response.status_code == 401:
            raise CopperAuthError(
                f"Authentication failed: {message}",
                status_code=401,
                response=error_data
            )
        elif response.status_code == 403:
            raise CopperAuthError(
                f"Permission denied: {message}",
                status_code=403,
                response=error_data
            )
        elif response.status_code == 404:
            raise CopperAPIError(
                f"Resource not found: {message}",
                status_code=404,
                response=error_data
            )
        elif response.status_code == 422:
            raise CopperValidationError(
                f"Validation error: {message}",
                status_code=422,
                response=error_data
            )
        elif response.status_code == 429:
            raise CopperRateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=429,
                response=error_data
            )
        elif response.status_code >= 500:
            raise CopperAPIError(
                f"Server error: {message}",
                status_code=response.status_code,
                response=error_data
            )
        else:
            raise CopperAPIError(
                f"API error: {message}",
                status_code=response.status_code,
                response=error_data
            )

    def execute_with_retry(
        self,
        func: Callable,
        retry_on: tuple = (CopperRateLimitError, CopperAPIError),
    ) -> Any:
        """
        Execute function with retry logic

        Args:
            func: Function to execute
            retry_on: Exception types to retry on

        Returns:
            Function result
        """
        import random

        last_exception = None
        config = self.retry_config

        for attempt in range(config.max_retries + 1):
            try:
                # Rate limiting
                self.rate_limiter.acquire()

                # Execute function
                return func()

            except retry_on as e:
                last_exception = e

                # Log error
                logger.warning(
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}"
                )

                # Don't retry non-retryable errors
                if isinstance(e, CopperAPIError):
                    if e.status_code not in [429, 500, 502, 503, 504]:
                        raise

                # Last attempt - raise
                if attempt >= config.max_retries:
                    raise last_exception

                # Calculate delay
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )

                # Add jitter
                if config.jitter:
                    delay = delay * (0.5 + random.random())

                # Extra delay for rate limit errors
                if isinstance(e, CopperRateLimitError):
                    delay = max(delay, 60.0)  # Wait at least 1 minute

                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)

        raise last_exception

# Usage Example
error_handler = CopperErrorHandler()

def make_api_call():
    """Example API call"""
    response = requests.get(
        "https://api.copper.com/developer_api/v1/account",
        headers={
            "X-PW-AccessToken": "YOUR_KEY",
            "X-PW-Application": "developer_api",
            "X-PW-UserEmail": "user@example.com",
        }
    )
    return error_handler.handle_response(response)

# Execute with retry
try:
    result = error_handler.execute_with_retry(make_api_call)
    print(f"Success: {result}")
except CopperAuthError as e:
    print(f"Auth error: {e.message}")
except CopperValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.response}")
except CopperRateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except CopperAPIError as e:
    print(f"API error: {e.message}")
```

### Logging and Monitoring

```python
import logging
from datetime import datetime
from typing import Dict, Any

class APILogger:
    """Logger for API calls with structured logging"""

    def __init__(self, log_file: str = "copper_api.log"):
        self.logger = logging.getLogger("copper_api")
        self.logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log_request(
        self,
        method: str,
        endpoint: str,
        payload: Dict = None,
        sanitize: bool = True,
    ):
        """Log API request"""
        if sanitize and payload:
            payload = self._sanitize_payload(payload.copy())

        self.logger.info(
            f"REQUEST: {method} {endpoint}",
            extra={
                "method": method,
                "endpoint": endpoint,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def log_response(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        error: str = None,
    ):
        """Log API response"""
        level = logging.ERROR if error else logging.INFO

        self.logger.log(
            level,
            f"RESPONSE: {method} {endpoint} - {status_code} ({response_time:.2f}s)",
            extra={
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "response_time": response_time,
                "error": error,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    @staticmethod
    def _sanitize_payload(payload: Dict) -> Dict:
        """Remove sensitive data from payload"""
        sensitive_keys = ["api_key", "token", "password", "secret"]

        for key in payload.keys():
            if any(s in key.lower() for s in sensitive_keys):
                payload[key] = "***REDACTED***"

        return payload
```

---

## Summary

### Key Takeaways

1. **Always handle 429 errors** - Use exponential backoff with jitter
2. **Validate client-side** - Reduce API calls and improve UX
3. **Implement idempotency** - Prevent duplicate records on retries
4. **Use circuit breakers** - Prevent cascading failures
5. **Log everything** - But sanitize sensitive data
6. **Test error paths** - Don't just test happy paths
7. **Monitor rate limits** - Stay under limits proactively
8. **Handle partial failures** - In bulk operations, track success/failure per record

### Error Handling Priority

1. **Prevent errors** - Client-side validation
2. **Handle gracefully** - User-friendly error messages
3. **Retry intelligently** - Exponential backoff for retryable errors
4. **Log for debugging** - Structured logging with context
5. **Monitor and alert** - Track error rates and patterns

### Common Pitfalls

- Not implementing rate limiting (leads to 429 errors)
- Retrying non-retryable errors (wastes time)
- Not sanitizing logs (security risk)
- Ignoring partial failures in bulk operations
- Not validating before sending (wastes API calls)
- Hard-coding delays instead of exponential backoff
- Not adding jitter (thundering herd problem)

### Additional Resources

- **Official Docs:** https://developer.copper.com
- **API Status:** https://status.copper.com
- **Support:** https://support.copper.com
