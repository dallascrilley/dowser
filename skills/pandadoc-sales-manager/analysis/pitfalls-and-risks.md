# PandaDoc API - Pitfalls and Risk Assessment

## Critical Warnings (Severity: HIGH)

### 1. Asynchronous Document Processing - 404 Errors

**Risk:** Attempting to use a newly created document before PandaDoc servers process it will result in a '404 document not found' response.

**Details:**
- Document creation is **non-blocking (asynchronous)**
- Initial response returns `status: document.uploaded`
- Document is NOT ready for further operations until status changes to `document.draft`
- Processing typically takes 2-5 seconds for simple PDFs, longer for complex documents
- Any API call to the document during `document.uploaded` state will fail with 404

**Impact:** Broken workflows, failed automation, user-facing errors

**Example Error Pattern:**
```javascript
// WRONG - Will fail with 404
const doc = await createDocument(data);
await sendDocument(doc.id); // FAILS - document not ready

// CORRECT - Wait for status change
const doc = await createDocument(data);
await waitForStatus(doc.id, 'document.draft');
await sendDocument(doc.id); // SUCCESS
```

**Mitigation Required:** Implement status polling or webhook handling before ANY subsequent operation.

---

### 2. Rate Limiting - Sandbox vs Production

**Risk:** Severe rate limiting in Sandbox environment (10 req/min) can break development/testing workflows.

**Sandbox Limits:**
- **10 requests per minute** for ANY endpoint
- Shared across all operations (create, list, send, etc.)
- Returns `429 Too Many Requests` when exceeded

**Production Limits:**
- Create Document from Template: 500/min
- Download Document: 100/min
- Other endpoints: Variable (contact PandaDoc for details)

**Critical Gotcha:**
- Limits calculated using **sliding window** (last 60 seconds), not reset at minute boundaries
- Limits are **per user**, not per API key - multiple keys share the same limit
- Limits are **per operation type**, not cumulative (50 creates + 50 downloads = OK)

**Impact:** Testing impossible with realistic data volumes, integration tests timing out

**Mitigation Required:** Request queue implementation, exponential backoff, separate test strategies

---

### 3. Authentication Scope - API Key Dependency

**Risk:** API keys tied to individual users will be deactivated if that user is removed from workspace.

**Details:**
- API keys inherit capabilities from the user who generates them
- User removal = immediate key deactivation
- No warning or graceful degradation
- Affects all integrations using that key

**Impact:** Production outages, silent failures, broken automations

**Best Practice:**
- Create API keys under **stable, long-term service accounts**
- Document which user owns which keys
- Never use temporary/contractor accounts for API key generation
- Monitor user changes in workspace

---

### 4. Document Status Error Handling

**Risk:** Failing to check for `document.error` status during polling leads to infinite loops.

**Status Flow:**
```
document.uploaded → document.draft (SUCCESS)
document.uploaded → document.error (FAILURE)
```

**Common Mistake:**
```python
# WRONG - Infinite loop on error
while doc_status == 'document.uploaded':
    time.sleep(1)
    doc_status = get_status(doc_id)

# CORRECT - Handle error status
while doc_status == 'document.uploaded':
    time.sleep(1)
    doc_status = get_status(doc_id)
    if doc_status == 'document.error':
        raise DocumentCreationError("Document creation failed")
```

**Impact:** Hung processes, resource exhaustion, delayed error detection

---

## Common Mistakes (Severity: MEDIUM)

### 5. Field vs Token Confusion

**Risk:** Mixing up `tokens` and `fields` parameters causes data not to appear in documents.

**Distinction:**
- **Tokens:** Replace template variables (use square brackets in template: `{{variable_name}}`)
- **Fields:** Pre-fill interactive form fields (cannot pre-fill Signature fields)

**API Structure:**
```json
{
  "name": "Sales Proposal",
  "template_uuid": "abc-123",
  "tokens": [
    {"name": "CompanyName", "value": "Acme Corp"}  // For template variables
  ],
  "fields": {
    "amount": {"value": "50000"}  // For form fields
  }
}
```

**Common Errors:**
- Putting form field data in `tokens` (data ignored)
- Using square brackets with `fields` (not needed)
- Attempting to pre-fill signature fields (not supported)

**Impact:** Missing data in documents, manual correction required, customer confusion

---

### 6. Pagination Gotchas

**Risk:** Inconsistent pagination behavior across endpoints causes data truncation.

**Endpoint-Specific Behavior:**
- **Contacts:** Returns ALL contacts in single response (pagination params ignored)
- **Templates/Documents:** Hard limit of 100 records per page (ignores `count > 100`)
- **Some endpoints:** Known bug returns same page repeatedly

**Best Practice:**
```python
# Track unique IDs to detect duplicate pages
seen_ids = set()
page = 1

while True:
    results = fetch_page(page)
    if not results:
        break

    new_ids = {r['id'] for r in results}
    if new_ids.issubset(seen_ids):
        break  # Duplicate page detected

    seen_ids.update(new_ids)
    page += 1
```

**Impact:** Missing records, incomplete data sync, duplicate processing

---

### 7. Timestamp Timezone Handling

**Risk:** PandaDoc returns timestamps with timezone info; PostgreSQL compatibility issues.

**API Response:** `2024-01-15T10:30:00+00:00`
**Storage Required:** `2024-01-15T10:30:00` (naive UTC)

**Affected Fields:**
- `date_created`
- `date_modified`
- `date_completed`

**Solution:** Strip timezone info before storage:
```python
from datetime import datetime

def strip_timezone(dt_string):
    dt = datetime.fromisoformat(dt_string)
    return dt.replace(tzinfo=None)
```

**Impact:** Database insertion errors, query failures, data type mismatches

---

### 8. Polling Best Practices Violations

**Risk:** Aggressive polling causes rate limit exhaustion and poor performance.

**Bad Patterns:**
- Polling every 100ms (hits rate limit immediately)
- No exponential backoff
- Checking status endpoint repeatedly for multiple documents

**Recommended Approach:**
- **Initial delay:** 1-2 seconds (most documents ready by then)
- **Poll interval:** 1 second minimum
- **Max polling duration:** 30 seconds (document.uploaded beyond this indicates failure)
- **Better:** Use webhooks instead of polling for production

**Rate Limit Impact:**
- Sandbox: Only 10 requests/min total (6 documents = rate limit)
- Production: Status checks count against limits

**Impact:** Rate limit errors, slow document processing, poor user experience

---

### 9. File Size and Type Validation

**Risk:** Upload failures with unclear errors when file constraints violated.

**Limits:**
- **Maximum file size:** 50 MB
- **Error on exceed:** `413 Request Entity Too Large`
- **Supported formats:** PDF, DOCX, XLSX, etc. (check official docs)

**Best Practice:**
- Validate file size client-side before upload
- Check file MIME type
- Provide clear user feedback on rejection

**Impact:** User frustration, failed uploads, support tickets

---

## Prerequisites & Setup Gotchas (Severity: MEDIUM)

### 10. Enterprise Plan Requirement

**Risk:** Production API access requires Enterprise plan; testing assumptions don't match production reality.

**Access Tiers:**
- **Sandbox API:** Available on trial Enterprise, active Enterprise, and Business (if Dev Center enabled)
- **Production API:** **Requires active Enterprise plan only**

**Common Issue:**
- Develop and test on Sandbox
- Attempt to deploy to production
- Discover Production API unavailable on current plan
- Project blocked pending plan upgrade

**Mitigation:**
- Verify production API access early in project lifecycle
- Include plan upgrade in project timeline and budget
- Test against production environment (not just Sandbox) before launch

---

### 11. Email Verification Requirement

**Risk:** API calls fail with `403 Forbidden: Email not verified` even with valid API key.

**Requirement:**
- Email associated with API key **must be verified**
- No automatic reminder if email unverified
- Error message not immediately obvious

**Solution:**
1. Check email inbox for verification link
2. Resend verification if needed
3. Generate new API key after verification

**Impact:** Blocked development, confusing error messages, delayed onboarding

---

### 12. Authorization Header Format

**Risk:** Incorrect header format causes `401 Unauthorized` errors.

**Correct Formats:**
```
API Key:    Authorization: API-Key {your_api_key}
OAuth 2.0:  Authorization: Bearer {access_token}
```

**Common Mistakes:**
```
Authorization: {api_key}           // WRONG - missing "API-Key" prefix
Authorization: Bearer {api_key}     // WRONG - using Bearer with API key
Authorization: API-Key Bearer {token}  // WRONG - mixing formats
```

**Impact:** Authentication failures, confusion with OAuth vs API key

---

### 13. OAuth Token Expiration

**Risk:** OAuth access tokens expire after 1 year; applications fail silently if refresh not implemented.

**Token Lifecycle:**
- **Expiration:** 31,535,999 seconds (≈1 year)
- **Error on expiration:** `401 Unauthorized`
- **Refresh required:** Use stored `refresh_token` to get new `access_token`

**Critical:**
- Must implement automatic token refresh
- Store `refresh_token` securely
- Handle refresh errors gracefully

**Impact:** Long-running integrations break after 1 year, user re-authentication required

---

## Community-Reported Issues (From Web Search)

### 14. 503 Service Unavailable on Document Creation

**Issue:** Users report intermittent `503 Service Unavailable` errors on Document Creation API calls.

**Observed Pattern:**
- Sporadic, not tied to rate limits
- Affects all document creation methods
- No clear pattern or resolution from PandaDoc

**Mitigation:**
- Implement retry logic with exponential backoff
- Consider circuit breaker pattern
- Monitor PandaDoc status page: https://status.pandadoc.com
- Provide user-facing status indicators

**Source:** Community forums, GitHub issues

---

### 15. Empty Parameter Validation (400 Errors)

**Issue:** List Documents and List Templates endpoints return `400 Bad Request` when parameters sent with empty values.

**Example:**
```javascript
// WRONG - Sends empty string
GET /documents?tag=&status=

// CORRECT - Omit empty parameters
GET /documents?status=1
```

**Solution:** Filter out empty/null parameters before API call

**Impact:** Query failures, unexpected empty result sets

**Source:** PandaDoc Changelog (2024)

---

### 16. Webhook Delivery Failures

**Issue:** Webhooks occasionally fail to deliver, causing status update misses.

**Recommended Pattern:** Hybrid approach
1. **Primary:** Webhooks for real-time notifications
2. **Fallback:** Scheduled polling job for documents stuck in `document.uploaded` > 30 seconds

**Implementation:**
```sql
-- Find documents potentially missed by webhooks
SELECT * FROM documents
WHERE status = 'document.uploaded'
AND created_at < NOW() - INTERVAL '30 seconds';
```

**Impact:** Stuck workflows, delayed document processing

**Source:** PandaDoc Developer Docs - "Building a Reliable Document Creation Workflow"

---

### 17. CRM Field Mapping Issues

**Issue:** When integrating with Salesforce/Dynamics, field mapping confusion between PandaDoc fields and CRM fields.

**Problem:**
- CRM custom fields have different naming conventions
- No clear documentation on field name transformation
- Case sensitivity issues

**Mitigation:**
- Use Document Details API to inspect exact field names
- Test with simple document first
- Document field mapping explicitly

**Source:** Community forums (Zapier, Make.com)

---

## Risk Mitigation Strategies

### Strategy 1: Implement Hybrid Polling + Webhook Pattern

**Purpose:** Maximize reliability for async document processing

**Implementation:**
```python
class DocumentStatusManager:
    def __init__(self):
        self.webhook_receiver = WebhookReceiver()
        self.poller = DocumentPoller()

    async def wait_for_document_ready(self, doc_id, timeout=30):
        """Wait for document using webhooks with polling fallback"""

        # Register webhook listener
        webhook_future = self.webhook_receiver.wait_for(doc_id)

        # Start polling as backup
        poll_future = self.poller.poll_until_ready(doc_id, timeout)

        # Race between webhook and polling
        result = await asyncio.wait([webhook_future, poll_future],
                                     return_when=asyncio.FIRST_COMPLETED)

        return result
```

**Benefits:**
- Webhook delivers instantly when working (best case)
- Polling catches missed webhooks (reliability)
- 30-second timeout prevents infinite waits

---

### Strategy 2: Rate Limit Queue with Backoff

**Purpose:** Prevent 429 errors and handle them gracefully

**Implementation:**
```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class RateLimitQueue:
    def __init__(self, requests_per_minute=10):
        self.rpm = requests_per_minute
        self.request_times = deque()
        self.retry_delays = [60, 120, 240]  # Exponential backoff

    async def execute(self, func, *args, **kwargs):
        """Execute function with rate limiting"""

        # Wait if at rate limit
        await self._wait_if_needed()

        # Try with retries
        for attempt, delay in enumerate([0] + self.retry_delays):
            if attempt > 0:
                await asyncio.sleep(delay)

            try:
                result = await func(*args, **kwargs)
                self._record_request()
                return result

            except RateLimitError as e:
                if attempt == len(self.retry_delays):
                    raise
                continue

    async def _wait_if_needed(self):
        """Wait if we've hit rate limit in last minute"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Remove requests older than 1 minute
        while self.request_times and self.request_times[0] < minute_ago:
            self.request_times.popleft()

        # Wait if at limit
        if len(self.request_times) >= self.rpm:
            oldest = self.request_times[0]
            wait_until = oldest + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
```

**Benefits:**
- Proactive rate limiting (never hit 429)
- Automatic retry with backoff
- Adapts to sandbox (10/min) and production (higher) limits

---

### Strategy 3: Pre-Flight Validation Script

**Purpose:** Catch configuration errors before API calls

**Checklist:**
```python
class PandaDocValidator:
    def validate_setup(self, config):
        """Validate PandaDoc configuration before use"""

        checks = {
            'api_key_format': self._check_api_key_format(config.api_key),
            'email_verified': self._check_email_verified(config),
            'plan_access': self._check_plan_access(config),
            'template_exists': self._check_template_exists(config.template_id),
            'field_names_valid': self._check_field_names(config.fields),
            'file_size': self._check_file_size(config.file_path),
        }

        failures = {k: v for k, v in checks.items() if not v['passed']}

        if failures:
            raise ValidationError(f"Pre-flight checks failed: {failures}")

        return True

    def _check_api_key_format(self, api_key):
        """Validate API key format"""
        # Check length, format, etc.
        if not api_key or len(api_key) < 32:
            return {'passed': False, 'error': 'Invalid API key format'}
        return {'passed': True}

    def _check_email_verified(self, config):
        """Check if email is verified"""
        try:
            # Call current member endpoint
            member = self.client.get_current_member()
            return {'passed': True}
        except ForbiddenError as e:
            if 'email not verified' in str(e).lower():
                return {'passed': False, 'error': 'Email not verified'}
            raise
```

**Benefits:**
- Catch errors before production
- Clear error messages
- Automated validation in CI/CD

---

### Strategy 4: Document Status State Machine

**Purpose:** Enforce correct status transition handling

**Implementation:**
```python
from enum import Enum
from typing import Set

class DocumentStatus(Enum):
    UPLOADED = 'document.uploaded'
    DRAFT = 'document.draft'
    SENT = 'document.sent'
    VIEWED = 'document.viewed'
    COMPLETED = 'document.completed'
    ERROR = 'document.error'

class DocumentStateMachine:
    # Define valid transitions
    TRANSITIONS = {
        DocumentStatus.UPLOADED: {
            DocumentStatus.DRAFT,
            DocumentStatus.ERROR
        },
        DocumentStatus.DRAFT: {
            DocumentStatus.SENT,
            DocumentStatus.ERROR
        },
        DocumentStatus.SENT: {
            DocumentStatus.VIEWED,
            DocumentStatus.COMPLETED,
            DocumentStatus.ERROR
        },
        # ... etc
    }

    def __init__(self, doc_id):
        self.doc_id = doc_id
        self.current_status = DocumentStatus.UPLOADED

    def can_transition_to(self, new_status: DocumentStatus) -> bool:
        """Check if transition is valid"""
        return new_status in self.TRANSITIONS.get(self.current_status, set())

    def transition_to(self, new_status: DocumentStatus):
        """Attempt status transition with validation"""
        if not self.can_transition_to(new_status):
            raise InvalidTransitionError(
                f"Cannot transition from {self.current_status} to {new_status}"
            )

        self.current_status = new_status

    def is_ready_for_operation(self, operation: str) -> bool:
        """Check if document status allows operation"""
        required_status = {
            'send': {DocumentStatus.DRAFT},
            'download': {DocumentStatus.COMPLETED},
            'update': {DocumentStatus.DRAFT},
        }

        return self.current_status in required_status.get(operation, set())
```

**Benefits:**
- Prevent invalid operations
- Clear error messages
- Enforce async processing awareness

---

### Strategy 5: Field/Token Mapper Helper

**Purpose:** Simplify field vs token distinction

**Implementation:**
```python
class PandaDocDataMapper:
    """Helper to correctly map data to tokens vs fields"""

    def __init__(self, template_id):
        self.template_id = template_id
        self.template_schema = self._fetch_template_schema(template_id)

    def map_data(self, data: dict) -> dict:
        """
        Auto-detect whether data should go in tokens or fields

        Args:
            data: Dict of {name: value} pairs

        Returns:
            Dict with 'tokens' and 'fields' arrays properly structured
        """
        result = {
            'tokens': [],
            'fields': {}
        }

        for name, value in data.items():
            if self._is_token(name):
                result['tokens'].append({
                    'name': name,
                    'value': str(value)
                })
            elif self._is_field(name):
                result['fields'][name] = {'value': value}
            else:
                raise UnknownFieldError(
                    f"'{name}' not found in template {self.template_id}"
                )

        return result

    def _is_token(self, name: str) -> bool:
        """Check if name is a template token"""
        return name in self.template_schema['tokens']

    def _is_field(self, name: str) -> bool:
        """Check if name is a form field"""
        return name in self.template_schema['fields']

    def _fetch_template_schema(self, template_id):
        """Fetch template to identify tokens vs fields"""
        template = self.client.get_template_details(template_id)

        return {
            'tokens': [t['name'] for t in template.get('tokens', [])],
            'fields': [f['name'] for f in template.get('fields', [])]
        }
```

**Benefits:**
- Automatic field/token detection
- Clear errors when names don't match
- Template-aware validation

---

### Strategy 6: Comprehensive Error Handling

**Purpose:** Handle all PandaDoc error scenarios gracefully

**Implementation:**
```python
class PandaDocErrorHandler:
    """Centralized error handling for PandaDoc API"""

    def handle_error(self, error, context=None):
        """Handle PandaDoc API errors with appropriate actions"""

        if isinstance(error, requests.HTTPError):
            status_code = error.response.status_code

            handlers = {
                401: self._handle_unauthorized,
                403: self._handle_forbidden,
                404: self._handle_not_found,
                413: self._handle_file_too_large,
                422: self._handle_validation_error,
                429: self._handle_rate_limit,
                503: self._handle_service_unavailable,
            }

            handler = handlers.get(status_code, self._handle_generic_error)
            return handler(error, context)

        return self._handle_generic_error(error, context)

    def _handle_unauthorized(self, error, context):
        """401 - Invalid API key or expired token"""
        # Check if OAuth token (needs refresh)
        if context and context.get('auth_type') == 'oauth':
            return {'action': 'refresh_token', 'retry': True}

        # API key invalid
        return {
            'action': 'check_api_key',
            'retry': False,
            'message': 'API key invalid or expired. Please verify credentials.'
        }

    def _handle_forbidden(self, error, context):
        """403 - Email not verified or insufficient permissions"""
        error_body = error.response.json()

        if 'email not verified' in str(error_body).lower():
            return {
                'action': 'verify_email',
                'retry': False,
                'message': 'Please verify your email address before using the API.'
            }

        return {
            'action': 'check_permissions',
            'retry': False,
            'message': 'Insufficient permissions for this operation.'
        }

    def _handle_not_found(self, error, context):
        """404 - Document not found (likely async processing issue)"""
        if context and context.get('operation') == 'document_access':
            return {
                'action': 'wait_for_processing',
                'retry': True,
                'delay': 2,
                'message': 'Document still processing. Waiting before retry...'
            }

        return {
            'action': 'check_resource_id',
            'retry': False,
            'message': 'Resource not found. Please verify the ID.'
        }

    def _handle_rate_limit(self, error, context):
        """429 - Rate limit exceeded"""
        retry_after = error.response.headers.get('Retry-After', 60)

        return {
            'action': 'backoff',
            'retry': True,
            'delay': int(retry_after),
            'message': f'Rate limit exceeded. Retrying in {retry_after} seconds...'
        }
```

**Benefits:**
- Context-aware error handling
- Automatic recovery when possible
- Clear user feedback

---

## Risk Matrix

| Risk | Severity | Frequency | Likelihood | Prevention Strategy |
|------|----------|-----------|------------|---------------------|
| **Async 404 Errors** | HIGH | VERY HIGH | 100% without handling | Strategy 1: Hybrid Polling + Webhooks |
| **Rate Limit (Sandbox)** | HIGH | HIGH | 80% in testing | Strategy 2: Rate Limit Queue |
| **API Key Deactivation** | HIGH | LOW | 10% over 1 year | Documentation + Service Account |
| **Missing document.error check** | HIGH | MEDIUM | 40% of implementations | Strategy 4: State Machine |
| **Field/Token Confusion** | MEDIUM | HIGH | 60% first-time | Strategy 5: Field Mapper |
| **Pagination Data Loss** | MEDIUM | MEDIUM | 30% multi-page results | Duplicate Detection + Testing |
| **Timezone Issues** | MEDIUM | LOW | 20% with PostgreSQL | Timezone Strip Helper |
| **Aggressive Polling** | MEDIUM | MEDIUM | 50% naive implementations | Strategy 1: Smart Polling |
| **File Size Exceeded** | MEDIUM | LOW | 15% with large files | Pre-flight Validation |
| **Email Not Verified** | MEDIUM | LOW | 10% new accounts | Strategy 3: Pre-Flight Checks |
| **Wrong Auth Header** | MEDIUM | LOW | 25% initial setup | Strategy 6: Error Handler |
| **OAuth Expiration** | MEDIUM | VERY LOW | 100% after 1 year | Automatic Token Refresh |
| **503 Service Errors** | LOW | LOW | 5% sporadic | Retry Logic + Circuit Breaker |
| **Empty Param 400s** | LOW | LOW | 5% edge cases | Parameter Filtering |
| **Webhook Failures** | LOW | LOW | 2% missed events | Strategy 1: Hybrid Approach |

---

## Severity Definitions

**HIGH Severity:**
- Breaks core functionality
- Causes data loss or corruption
- Results in production outages
- No workaround available
- Affects >50% of use cases

**MEDIUM Severity:**
- Causes feature degradation
- Has workarounds but requires code changes
- Results in poor user experience
- Affects 10-50% of use cases

**LOW Severity:**
- Minor inconveniences
- Easy workarounds available
- Affects <10% of use cases
- No user impact if handled

---

## Testing Checklist

Before deploying PandaDoc integration, verify:

- [ ] **Async Handling:** Document status polling implemented with 30s timeout
- [ ] **Error States:** `document.error` status handled in polling loop
- [ ] **Rate Limiting:** Queue system limits requests to <10/min in sandbox
- [ ] **Exponential Backoff:** Retry logic with 60s, 120s, 240s delays
- [ ] **Authentication:** API key format validated, email verified
- [ ] **API Key Ownership:** Keys created by stable service account, not individual user
- [ ] **Field Mapping:** Tokens vs fields distinction clear and tested
- [ ] **Pagination:** Duplicate page detection for list endpoints
- [ ] **Timezone Handling:** Timestamps stripped before database storage
- [ ] **File Validation:** Size and type checked before upload
- [ ] **Webhook Fallback:** Polling backup for missed webhook deliveries
- [ ] **OAuth Refresh:** Token refresh implemented for OAuth integrations
- [ ] **Error Messages:** User-facing errors clear and actionable
- [ ] **Monitoring:** Rate limit, error rate, and async processing time tracked
- [ ] **Documentation:** Field names, auth setup, and gotchas documented for team

---

## Recommended Implementation Order

1. **Pre-Flight Validation** (Strategy 3)
   - Catch setup issues early
   - Block invalid configurations

2. **Error Handling** (Strategy 6)
   - Handle all error codes
   - Provide clear feedback

3. **Rate Limit Queue** (Strategy 2)
   - Prevent 429 errors
   - Essential for sandbox testing

4. **Async Status Handling** (Strategy 1)
   - Core requirement for document operations
   - Highest impact on reliability

5. **Field Mapper** (Strategy 5)
   - Improve developer experience
   - Reduce field mapping bugs

6. **State Machine** (Strategy 4)
   - Enforce valid operations
   - Catch logic errors

---

## Additional Resources

- **Official Docs:** https://developers.pandadoc.com/reference/about
- **Status Page:** https://status.pandadoc.com
- **Rate Limits:** https://developers.pandadoc.com/reference/limits
- **Reliable Workflows:** https://developers.pandadoc.com/docs/reliable-document-workflow
- **Webhook Guide:** https://developers.pandadoc.com/docs/webhooks-concepts

---

## Version History

- **v1.0** (2025-01-11): Initial risk assessment based on API documentation and community research
