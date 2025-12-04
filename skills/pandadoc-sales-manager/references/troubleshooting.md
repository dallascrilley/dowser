# PandaDoc Troubleshooting Guide

**Document Version:** 1.0
**Last Updated:** 2024-11-11

Comprehensive troubleshooting guide for common PandaDoc API issues.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Authentication Issues](#authentication-issues)
3. [Document Creation Issues](#document-creation-issues)
4. [Document Sending Issues](#document-sending-issues)
5. [Status and Polling Issues](#status-and-polling-issues)
6. [Rate Limiting Issues](#rate-limiting-issues)
7. [Data and Field Issues](#data-and-field-issues)
8. [Performance Issues](#performance-issues)
9. [Webhook Issues](#webhook-issues)
10. [Diagnostic Commands](#diagnostic-commands)

---

## Quick Reference

| Error Code | Issue | Solution |
|-----------|-------|----------|
| 401 | Invalid API key | Check `PANDADOC_API_KEY` environment variable |
| 404 | Document/template not found | Verify ID exists, wait for document to be ready |
| 400 | Invalid parameters | Check field names match template exactly (case-sensitive) |
| 409 | Invalid document state | Verify document is in correct status (e.g., draft before send) |
| 429 | Rate limit exceeded | Implement backoff, wait 60-240 seconds before retrying |
| 500+ | Server error | Retry with exponential backoff (1s, 2s, 4s) |

---

## Authentication Issues

### Issue: 401 Unauthorized

**Symptoms:**
- All API requests return 401 error
- Error message: "Invalid API key"
- Cannot list documents or templates

**Causes:**
1. API key not set in environment
2. API key is expired or revoked
3. API key is for wrong environment (sandbox vs production)
4. API key is malformed

**Solutions:**

**1. Check environment variable:**
```bash
# Verify API key is set
echo $PANDADOC_API_KEY

# If empty, set it
export PANDADOC_API_KEY="your_api_key"

# On Windows
set PANDADOC_API_KEY=your_api_key
```

**2. Test API key validity:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/members/current \
  -H "Authorization: API-Key YOUR_API_KEY"
```

Expected response (200 OK):
```json
{
  "id": "user_123",
  "email": "you@company.com",
  "created_at": "2023-01-01T00:00:00Z"
}
```

**3. Generate new API key:**
- Log into PandaDoc
- Go to Settings → API
- Generate new API key
- Update environment variable

**4. Verify environment:**
```python
import os

# Check which environment
api_key = os.environ.get('PANDADOC_API_KEY')
if not api_key:
    print("ERROR: PANDADOC_API_KEY not set")
else:
    print(f"Using API key: {api_key[:10]}...")  # Show first 10 chars

# Check environment setting
env = os.environ.get('PANDADOC_ENV', 'sandbox')
print(f"Environment: {env}")
```

**Prevention:**
- Store API keys in `.env` file (add to .gitignore)
- Never commit credentials to version control
- Rotate API keys every 90 days
- Use separate keys for dev/staging/production

---

### Issue: 403 Forbidden

**Symptoms:**
- API key is valid but permission denied
- Error: "Insufficient permissions"

**Causes:**
1. API key has limited permissions
2. Trying to access resource user doesn't own
3. API key restricted to specific templates

**Solutions:**
1. Contact PandaDoc support to increase permissions
2. Verify you're accessing your own resources
3. Check API key restrictions in PandaDoc settings

---

## Document Creation Issues

### Issue: 404 Document Not Found After Creation

**Symptoms:**
- Document created successfully (received ID)
- Immediately trying to use it returns 404
- Error: "Document not found"

**Cause:**
Document creation is asynchronous. Trying to use document before it's ready.

**Solution:**
Always poll for `document.draft` status before using document.

```python
import time
import requests

def create_and_wait(template_uuid, recipients, fields):
    # Create document
    response = requests.post(
        'https://api.pandadoc.com/public/v1/documents',
        headers={'Authorization': f'API-Key {API_KEY}'},
        json={
            'template_uuid': template_uuid,
            'recipients': recipients,
            'fields': fields
        }
    )
    doc = response.json()
    doc_id = doc['id']

    # CRITICAL: Wait for draft status
    for attempt in range(30):
        time.sleep(2)  # Wait 2 seconds between checks

        response = requests.get(
            f'https://api.pandadoc.com/public/v1/documents/{doc_id}',
            headers={'Authorization': f'API-Key {API_KEY}'}
        )
        status_doc = response.json()

        print(f"Attempt {attempt + 1}: {status_doc['status']}")

        if status_doc['status'] == 'document.draft':
            print("Document ready!")
            return doc_id

        if status_doc['status'].startswith('document.error'):
            raise Exception(f"Document failed: {status_doc['status']}")

    raise TimeoutError("Document not ready after 60 seconds")
```

---

### Issue: 400 Bad Request - Invalid Field

**Symptoms:**
- Error during document creation
- Message: "Invalid field value"
- Field validation errors

**Causes:**
1. Field name doesn't match template exactly (case-sensitive)
2. Field value is wrong type (e.g., text instead of number)
3. Required field missing
4. Field value format incorrect

**Solutions:**

**1. Verify field names match template:**
```python
import requests

API_KEY = "your_key"

# Get template details
response = requests.get(
    'https://api.pandadoc.com/public/v1/templates/YOUR_TEMPLATE_ID',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
template = response.json()

print("Expected fields:")
for field in template.get('fields', []):
    print(f"  - {field['name']}")

# Your field mapping must match exactly
fields = {
    field['name']: value  # Use exact field name from template
    for field, value in your_data.items()
}
```

**2. Check field values:**
```python
# Validate field values before creating
from datetime import datetime

def validate_fields(fields):
    for field_name, value in fields.items():
        # Check not empty
        if not value:
            print(f"ERROR: {field_name} is empty")

        # Check type
        if 'Date' in field_name:
            try:
                datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                print(f"ERROR: {field_name} must be YYYY-MM-DD format")

        # Check amount fields
        if 'Amount' in field_name or 'Price' in field_name:
            try:
                float(value.replace('$', '').replace(',', ''))
            except ValueError:
                print(f"ERROR: {field_name} must be numeric")

validate_fields(my_fields)
```

**3. Use template_mappings.yml:**
Define field mappings in configuration:
```yaml
templates:
  sales_proposal:
    field_mappings:
      customer_name: "Company Name"      # Exact match from template
      proposal_amount: "Proposal Amount"
      effective_date: "Effective Date"
```

---

### Issue: 404 Template Not Found

**Symptoms:**
- Error: "Template not found"
- Error: "Invalid template UUID"

**Causes:**
1. Template UUID is incorrect
2. Template doesn't exist in your account
3. Template was deleted
4. Wrong environment (sandbox vs production)

**Solutions:**

**1. List available templates:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/templates \
  -H "Authorization: API-Key YOUR_API_KEY" | jq .
```

**2. Verify template UUID in code:**
```python
# Get list of templates
response = requests.get(
    'https://api.pandadoc.com/public/v1/templates',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
templates = response.json()['results']

# Print all template IDs
for template in templates:
    print(f"{template['name']}: {template['id']}")

# Use correct ID
template_uuid = "abc123-def456-ghi789"  # From list above
```

**3. Check template still exists:**
```bash
# Try to fetch template directly
curl -X GET https://api.pandadoc.com/public/v1/templates/abc123-def456-ghi789 \
  -H "Authorization: API-Key YOUR_API_KEY"
```

---

## Document Sending Issues

### Issue: 409 Conflict - Document Not Ready

**Symptoms:**
- Error when trying to send: "Document not in correct state"
- HTTP 409 Conflict
- Document is in wrong status for operation

**Causes:**
1. Sending before document status is `document.draft`
2. Sending document that's already sent
3. Sending document in error state

**Solutions:**

**1. Check document status before sending:**
```python
def safe_send_document(document_id):
    # Get document status
    response = requests.get(
        f'https://api.pandadoc.com/public/v1/documents/{document_id}',
        headers={'Authorization': f'API-Key {API_KEY}'}
    )
    doc = response.json()

    print(f"Current status: {doc['status']}")

    # Check if ready to send
    if doc['status'] != 'document.draft':
        print(f"ERROR: Cannot send document in {doc['status']} state")
        print("Document must be in 'document.draft' status to send")
        return False

    # Safe to send
    send_response = requests.post(
        f'https://api.pandadoc.com/public/v1/documents/{document_id}/send',
        headers={'Authorization': f'API-Key {API_KEY}'},
        json={'subject': 'Review', 'message': 'Please sign'}
    )

    return send_response.status_code == 200
```

**2. State transition diagram:**
```
document.uploaded (creation in progress)
    ↓
document.draft (ready to send or modify)
    ↓
document.sent (sent to recipients)
    ↓
document.viewed (recipient opened)
    ↓
document.completed (all signed)
```

---

### Issue: Invalid Recipients

**Symptoms:**
- Error: "Invalid recipient email"
- Error: "At least one recipient required"
- Recipients not receiving emails

**Causes:**
1. Email address is invalid format
2. No recipients provided
3. Recipient email is duplicate
4. Recipient role doesn't match template

**Solutions:**

**1. Validate recipient emails:**
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Validate before creating document
recipients = [
    {'email': 'john@acme.com', 'role': 'Client'},
    {'email': 'invalid_email', 'role': 'Manager'}
]

for recipient in recipients:
    if not validate_email(recipient['email']):
        print(f"ERROR: Invalid email {recipient['email']}")

# Remove duplicates
emails = set()
unique_recipients = []
for recipient in recipients:
    if recipient['email'] not in emails:
        unique_recipients.append(recipient)
        emails.add(recipient['email'])
```

**2. Verify recipient roles match template:**
```python
# Get template to see allowed roles
response = requests.get(
    'https://api.pandadoc.com/public/v1/templates/TEMPLATE_ID',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
template = response.json()

allowed_roles = template.get('roles', [])
print(f"Allowed roles: {allowed_roles}")

# Validate recipient roles
for recipient in recipients:
    if recipient['role'] not in allowed_roles:
        print(f"ERROR: Role {recipient['role']} not in template")
```

---

## Status and Polling Issues

### Issue: Document Stuck in "uploaded" Status

**Symptoms:**
- Document status never changes from `document.uploaded`
- Polling returns same status for 60+ seconds

**Causes:**
1. Document processing error on PandaDoc server
2. Too many concurrent requests (rate limit)
3. Network connectivity issue
4. PandaDoc server issue

**Solutions:**

**1. Check for error status:**
```python
response = requests.get(
    f'https://api.pandadoc.com/public/v1/documents/{document_id}',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
doc = response.json()

if 'error' in doc['status']:
    print(f"Document creation error: {doc['status']}")
    # Check error details
    if 'error_details' in doc:
        print(f"Details: {doc['error_details']}")
```

**2. Check server status:**
Visit https://status.pandadoc.com to see if there are API issues

**3. Recreate document:**
```python
# If stuck for 60+ seconds, try creating again
doc_id = create_document(...)
time.sleep(2)

# Check status
response = requests.get(
    f'https://api.pandadoc.com/public/v1/documents/{doc_id}',
    headers={'Authorization': f'API-Key {API_KEY}'}
)

if response.json()['status'] == 'document.error':
    print("Retrying document creation...")
    doc_id = create_document(...)
```

---

### Issue: Status Not Updating

**Symptoms:**
- Document stuck in same status for hours
- Recipients haven't received notifications
- Can't download completed document

**Causes:**
1. Recipient email invalid (bounced)
2. Recipients not opening email
3. Network issue preventing status updates
4. Polling timeout too short

**Solutions:**

**1. Check recipient email delivery:**
```python
# Get recipient status
response = requests.get(
    f'https://api.pandadoc.com/public/v1/documents/{document_id}',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
doc = response.json()

for recipient in doc.get('recipients', []):
    print(f"Recipient: {recipient['email']}")
    print(f"  Status: {recipient.get('status')}")
    print(f"  Role: {recipient.get('role')}")
    print(f"  Sent at: {recipient.get('sent_at')}")
```

**2. Increase polling timeout:**
```python
# Poll for up to 24 hours instead of 60 seconds
max_attempts = 8640  # 24 hours at 10-second intervals

for attempt in range(max_attempts):
    time.sleep(10)

    response = requests.get(...)
    doc = response.json()

    if doc['status'] == 'document.completed':
        break

    if attempt % 100 == 0:  # Log every 100 attempts
        print(f"Still waiting... {doc['status']}")
```

**3. Use webhooks instead:**
Webhooks notify you immediately when status changes, no polling needed.

---

## Rate Limiting Issues

### Issue: 429 Too Many Requests

**Symptoms:**
- HTTP 429 error
- Error: "Rate limit exceeded"
- Message: "Too many requests"

**Causes:**
1. Sending requests faster than rate limit (10 req/min for sandbox)
2. Multiple processes making requests simultaneously
3. Retry loop making requests too quickly

**Solutions:**

**1. Implement rate limiting:**
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, requests_per_minute=10):
        self.requests_per_minute = requests_per_minute
        self.request_times = deque()

    def wait_if_needed(self):
        now = time.time()
        one_minute_ago = now - 60

        # Remove requests older than 1 minute
        while self.request_times and self.request_times[0] < one_minute_ago:
            self.request_times.popleft()

        # Check if at limit
        if len(self.request_times) >= self.requests_per_minute:
            # Wait until oldest request is out of window
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest) + 0.1

            print(f"Rate limit reached. Waiting {wait_time:.1f}s...")
            time.sleep(wait_time)

        # Record this request
        self.request_times.append(time.time())

# Usage
limiter = RateLimiter(requests_per_minute=10)

def api_call():
    limiter.wait_if_needed()
    return requests.get(url, headers=headers)
```

**2. Implement exponential backoff:**
```python
import random

def call_with_backoff(func, max_retries=3):
    base_delay = 60  # Start with 60 seconds

    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff: 60s, 120s, 240s
            delay = base_delay * (2 ** attempt)
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.1)

            print(f"Rate limited. Retrying in {delay + jitter:.1f}s...")
            time.sleep(delay + jitter)
```

**3. Sequential processing:**
Instead of parallel requests, process sequentially with delays:

```python
# Bad: Parallel processing hits rate limit
# from concurrent.futures import ThreadPoolExecutor
# executor.map(create_document, customers)  # Too fast!

# Good: Sequential with delays
for customer in customers:
    create_document(customer)
    time.sleep(6)  # 6 seconds = 10 requests/minute
```

**4. Check rate limit headers:**
```python
response = requests.get(url, headers=headers)

if 'X-RateLimit-Remaining' in response.headers:
    remaining = response.headers['X-RateLimit-Remaining']
    limit = response.headers['X-RateLimit-Limit']
    reset = response.headers['X-RateLimit-Reset']

    print(f"Requests remaining: {remaining}/{limit}")
    print(f"Resets at: {reset}")
```

---

## Data and Field Issues

### Issue: Field Values Not Appearing in Document

**Symptoms:**
- Document created but custom fields are blank
- Field values not populated in PDF
- Template fields not filled

**Causes:**
1. Field names don't match template (case-sensitive)
2. Field value is null or empty
3. Field is a system field, not custom field
4. Field requires special formatting

**Solutions:**

**1. Use exact field names:**
```python
# WRONG: Case doesn't match
fields = {
    "company name": "Acme",      # Template has "Company Name"
    "proposal amount": "$50,000" # Template has "Proposal Amount"
}

# RIGHT: Exact match
fields = {
    "Company Name": "Acme",
    "Proposal Amount": "$50,000"
}
```

**2. Handle special field types:**
```python
# Date fields must be YYYY-MM-DD
fields["Effective Date"] = "2024-01-15"  # Correct
# fields["Effective Date"] = "01/15/2024" # Wrong!

# Currency fields
fields["Proposal Amount"] = "$50,000.00"  # With symbol
# or
fields["Proposal Amount"] = "50000.00"    # Just number

# Percentages
fields["Discount"] = "10%"
# or
fields["Discount"] = "10"
```

**3. Debug with field output:**
```python
# Create document and check what fields it has
response = requests.get(
    f'https://api.pandadoc.com/public/v1/documents/{doc_id}',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
doc = response.json()

print("Document fields:")
for field_name, field_value in doc.get('fields', {}).items():
    print(f"  {field_name}: {field_value}")
```

---

## Performance Issues

### Issue: Slow Document Creation

**Symptoms:**
- Document takes 30+ seconds to reach draft status
- Network seems slow
- API calls taking a long time

**Solutions:**

**1. Check network latency:**
```bash
# Ping PandaDoc API
ping api.pandadoc.com

# Check DNS resolution
nslookup api.pandadoc.com

# Measure HTTP latency
curl -w "Total time: %{time_total}s\n" \
  https://api.pandadoc.com/public/v1/documents \
  -H "Authorization: API-Key YOUR_KEY"
```

**2. Optimize request size:**
```python
# Remove unnecessary data
payload = {
    "name": "Proposal",
    "template_uuid": "uuid",
    "recipients": [...],
    "fields": {...},
    # Don't include metadata if not needed
    # Don't include unnecessary fields
}
```

**3. Use connection pooling:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()

    # Retry strategy
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    # Connection pooling
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)

    return session

session = create_session()
response = session.get(url, headers=headers)
```

---

## Webhook Issues

### Issue: Webhook Not Receiving Events

**Symptoms:**
- Webhook subscribed but no events received
- Document status changes but no webhook call

**Causes:**
1. Webhook endpoint is down or unreachable
2. Endpoint returns non-2xx status
3. Firewall blocking PandaDoc IPs
4. Signature verification failing

**Solutions:**

**1. Test webhook endpoint:**
```bash
# Test that endpoint is accessible
curl -X POST https://your-server.com/webhooks/pandadoc \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Should return 200 OK
```

**2. Check endpoint in code:**
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/pandadoc', methods=['POST'])
def webhook():
    print(f"Received webhook: {request.json}")

    # MUST return 200 within 30 seconds
    return {'success': True}, 200

if __name__ == '__main__':
    # Run on port accessible from internet
    app.run(host='0.0.0.0', port=8080)
```

**3. Verify HTTPS/SSL certificate:**
```bash
# Check certificate validity
openssl s_client -connect your-server.com:443

# Should show valid certificate
```

**4. Check webhook subscription:**
```bash
# List webhooks
curl https://api.pandadoc.com/public/v1/webhook-subscriptions \
  -H "Authorization: API-Key YOUR_KEY"

# Check if active
```

**5. Enable webhook logging:**
```python
import json
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route('/webhooks/pandadoc', methods=['POST'])
def webhook():
    # Log everything
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.get_data(as_text=True)}")
    print(f"JSON: {request.json}")

    return {'success': True}, 200
```

---

## Diagnostic Commands

### Check API Key Validity

```bash
curl -X GET https://api.pandadoc.com/public/v1/members/current \
  -H "Authorization: API-Key YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

Expected: `{"id": "...", "email": "...", ...}`

### List All Templates

```bash
curl -X GET https://api.pandadoc.com/public/v1/templates \
  -H "Authorization: API-Key YOUR_API_KEY"
```

### Check Specific Document

```bash
curl -X GET https://api.pandadoc.com/public/v1/documents/DOC_ID \
  -H "Authorization: API-Key YOUR_API_KEY"
```

### Enable Debug Logging (Python)

```python
import logging
import requests

# Enable debug logging
logging.basicConfig()
logging.getLogger('urllib3').setLevel(logging.DEBUG)

# Now all HTTP requests will be logged
response = requests.get(url, headers=headers)
```

### Test Rate Limiter

```python
import time
import requests

# Make 15 requests rapidly (should hit rate limit)
for i in range(15):
    response = requests.get(
        'https://api.pandadoc.com/public/v1/documents',
        headers={'Authorization': f'API-Key {API_KEY}'}
    )

    print(f"Request {i + 1}: {response.status_code}")

    if response.status_code == 429:
        print("Rate limited!")
        break

    time.sleep(0.1)  # Very fast requests
```

---

## Getting Help

If issues persist:

1. **Check PandaDoc Status:** https://status.pandadoc.com
2. **Review API Documentation:** https://developers.pandadoc.com
3. **Contact Support:** support@pandadoc.com
4. **Check Logs:** Enable debug logging to see exact requests/responses
5. **Verify Configuration:** Double-check all configuration files

---

## See Also

- [Endpoints Reference](./endpoints-reference.md)
- [Workflows Guide](./workflows.md)
- [Webhook Integration](./webhook-integration-guide.md)
