# Webhook Integration Guide

**Document Version:** 1.0
**Last Updated:** 2024-11-11

Complete guide to setting up and using PandaDoc webhooks for real-time document event notifications.

---

## Table of Contents

1. [Webhook Overview](#webhook-overview)
2. [Why Use Webhooks](#why-use-webhooks)
3. [Setup](#setup)
4. [Event Types](#event-types)
5. [Payload Structure](#payload-structure)
6. [Security](#security)
7. [Handling Events](#handling-events)
8. [Testing](#testing)
9. [Production Checklist](#production-checklist)
10. [Troubleshooting](#troubleshooting)

---

## Webhook Overview

### What are Webhooks?

Webhooks are HTTP callbacks that PandaDoc uses to push real-time event notifications to your server.

Instead of polling PandaDoc API repeatedly asking "Is the document signed?", webhooks notify you instantly when status changes.

```
Traditional Polling          With Webhooks
┌─────────────┐              ┌──────────────┐
│   Your App  │              │  PandaDoc    │
└────┬────────┘              └───────┬──────┘
     │                               │
     │ GET /documents/123 ──────────→ "pending"
     │ GET /documents/123 ──────────→ "pending"
     │ GET /documents/123 ──────────→ "pending"
     │ GET /documents/123 ──────────→ "completed"
     │                               │
     │                    POST /webhook ← Document completed
     │                               │
```

---

## Why Use Webhooks

### Benefits

| Aspect | Polling | Webhooks |
|--------|---------|----------|
| **Latency** | 30+ seconds | < 1 second |
| **API Calls** | Constant | Only on events |
| **Rate Limits** | Hit quickly | Rarely hit |
| **Reliability** | Miss events | Guaranteed delivery |
| **Cost** | Higher | Lower |
| **Scalability** | Doesn't scale | Scales well |

### Use Cases

1. **Live Document Tracking** - Notify user when document is signed
2. **CRM Integration** - Auto-update opportunity when deal is signed
3. **Workflow Automation** - Trigger follow-up actions on completion
4. **Email Notifications** - Send email when document status changes
5. **Analytics** - Track document metrics in real-time
6. **Approval Alerts** - Alert managers when approval needed

---

## Setup

### Step 1: Create Webhook Endpoint

Your webhook endpoint is an HTTPS endpoint that receives POST requests from PandaDoc.

**Python (Flask) Example:**

```python
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)

# Shared key for signature verification
WEBHOOK_SHARED_KEY = "your_secure_random_key_here"

@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_pandadoc_webhook():
    """Handle incoming webhook from PandaDoc."""

    # Get webhook signature from header
    signature = request.headers.get('X-Pandadoc-Signature', '')

    # Get raw request body
    payload = request.get_data(as_text=True)

    # Verify signature (CRITICAL for security)
    if not verify_signature(payload, signature):
        print("ERROR: Invalid signature")
        return {'error': 'Invalid signature'}, 401

    # Parse event
    event = json.loads(payload)

    print(f"Event: {event.get('event_type')}")
    print(f"Document: {event.get('document', {}).get('id')}")

    # Handle event
    handle_event(event)

    # MUST return 200 OK within 30 seconds
    return {'success': True}, 200

def verify_signature(payload, signature):
    """Verify webhook signature using HMAC-SHA256."""

    expected = hmac.new(
        WEBHOOK_SHARED_KEY.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected)

def handle_event(event):
    """Process webhook event."""

    event_type = event.get('event_type')

    if event_type == 'document_completed':
        handle_document_completed(event)
    elif event_type == 'document_sent':
        handle_document_sent(event)
    elif event_type == 'document_declined':
        handle_document_declined(event)
    elif event_type == 'document_viewed':
        handle_document_viewed(event)
    else:
        print(f"Unknown event type: {event_type}")

def handle_document_completed(event):
    """Handle document completion event."""

    doc_id = event['document']['id']
    doc_name = event['document']['name']

    print(f"Document completed: {doc_name} ({doc_id})")

    # Update database, send email, trigger workflow, etc.
    update_crm(doc_id, 'completed')
    send_congratulations_email(event)

def handle_document_sent(event):
    """Handle document sent event."""

    doc_id = event['document']['id']
    print(f"Document sent: {doc_id}")

    # Log event, update UI, etc.
    log_event('document_sent', doc_id)

def handle_document_declined(event):
    """Handle document declined event."""

    doc_id = event['document']['id']
    print(f"Document declined: {doc_id}")

    # Alert sales team
    send_alert(f"Document {doc_id} was declined")

def handle_document_viewed(event):
    """Handle document viewed event."""

    doc_id = event['document']['id']
    print(f"Document viewed: {doc_id}")

    # Placeholder for viewed handling
    pass

if __name__ == '__main__':
    # Run on port accessible from internet (HTTPS required)
    app.run(host='0.0.0.0', port=8080)
```

### Step 2: Deploy Endpoint

Your endpoint must be:
1. **HTTPS** (required for production)
2. **Accessible from internet** (not on localhost)
3. **Available 24/7** (or at least when documents are being used)

**Deployment Options:**

```
Cloud Platforms:
- AWS Lambda + API Gateway
- Google Cloud Functions
- Azure Functions
- Heroku
- DigitalOcean

Self-Hosted:
- Express server on your VPS
- Django/Flask on your server
- Any HTTP server behind reverse proxy
```

**Example: AWS Lambda + API Gateway**

```python
import json
import hmac
import hashlib

WEBHOOK_SHARED_KEY = "your_key"

def lambda_handler(event, context):
    """AWS Lambda handler for webhook."""

    # Extract signature and body
    headers = event.get('headers', {})
    signature = headers.get('x-pandadoc-signature', '')
    body = event.get('body', '')

    # Verify signature
    expected = hmac.new(
        WEBHOOK_SHARED_KEY.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        return {
            'statusCode': 401,
            'body': json.dumps({'error': 'Invalid signature'})
        }

    # Parse and handle event
    webhook_event = json.loads(body)
    handle_event(webhook_event)

    return {
        'statusCode': 200,
        'body': json.dumps({'success': True})
    }
```

### Step 3: Register Webhook Subscription

Create the webhook subscription in PandaDoc:

```bash
curl -X POST https://api.pandadoc.com/public/v1/webhook-subscriptions \
  -H "Authorization: API-Key YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Document Status Tracker",
    "url": "https://your-domain.com/webhooks/pandadoc",
    "triggers": [
      "document_state_changed",
      "document_sent",
      "document_viewed",
      "document_completed",
      "document_declined"
    ],
    "payload": ["metadata", "fields", "recipients"]
  }'
```

**Or using Python:**

```python
import requests

response = requests.post(
    'https://api.pandadoc.com/public/v1/webhook-subscriptions',
    headers={
        'Authorization': f'API-Key {API_KEY}',
        'Content-Type': 'application/json'
    },
    json={
        'name': 'Document Status Tracker',
        'url': 'https://your-domain.com/webhooks/pandadoc',
        'triggers': [
            'document_state_changed',
            'document_sent',
            'document_viewed',
            'document_completed',
            'document_declined'
        ],
        'payload': ['metadata', 'fields', 'recipients']
    }
)

webhook = response.json()
print(f"Webhook created: {webhook['id']}")
```

**Response:**
```json
{
  "id": "ws_1234567890",
  "name": "Document Status Tracker",
  "url": "https://your-domain.com/webhooks/pandadoc",
  "triggers": ["document_state_changed", "document_sent"],
  "active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

## Event Types

### document_state_changed

Any document status change.

**When triggered:**
- Sent → Viewed
- Viewed → Completed
- Draft → Sent
- Any state transition

**Payload:**
```json
{
  "event_type": "document_state_changed",
  "timestamp": "2024-01-15T14:30:00Z",
  "document": {
    "id": "doc_8e6f8e6f",
    "name": "Proposal",
    "status": "document.viewed",
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  }
}
```

### document_sent

Document sent to recipients.

**When triggered:**
- User clicks "Send" in PandaDoc
- API sends document
- Recipients receive email

**Payload:**
```json
{
  "event_type": "document_sent",
  "timestamp": "2024-01-15T14:30:00Z",
  "document": {
    "id": "doc_8e6f8e6f",
    "status": "document.sent",
    "sent_at": "2024-01-15T14:30:00Z"
  }
}
```

### document_viewed

Recipient opened document.

**When triggered:**
- Recipient clicks link in email
- Document opened in PandaDoc

**Payload:**
```json
{
  "event_type": "document_viewed",
  "timestamp": "2024-01-15T14:30:00Z",
  "document": {
    "id": "doc_8e6f8e6f",
    "status": "document.viewed"
  },
  "recipient": {
    "email": "john@acme.com",
    "viewed_at": "2024-01-15T14:30:00Z"
  }
}
```

### document_completed

All recipients signed document.

**When triggered:**
- Last recipient signs
- All signatures collected
- Document fully executed

**Payload:**
```json
{
  "event_type": "document_completed",
  "timestamp": "2024-01-15T14:30:00Z",
  "document": {
    "id": "doc_8e6f8e6f",
    "name": "Proposal",
    "status": "document.completed",
    "completed_at": "2024-01-15T14:30:00Z"
  },
  "recipients": [
    {
      "email": "john@acme.com",
      "completed_at": "2024-01-15T14:25:00Z"
    },
    {
      "email": "jane@company.com",
      "completed_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### document_declined

Recipient declined to sign.

**When triggered:**
- Recipient clicks "Decline" in document
- Recipient rejects signature

**Payload:**
```json
{
  "event_type": "document_declined",
  "timestamp": "2024-01-15T14:30:00Z",
  "document": {
    "id": "doc_8e6f8e6f",
    "status": "document.declined"
  },
  "recipient": {
    "email": "john@acme.com",
    "declined_at": "2024-01-15T14:30:00Z"
  }
}
```

### Other Event Types

```
document_waiting_approval   - Awaiting approval
document_approved          - Approved by reviewer
document_rejected          - Rejected by reviewer
document_waiting_pay       - Awaiting payment
document_paid              - Payment received
document_voided            - Document voided
recipient_completed        - Individual recipient completed
recipient_declined         - Individual recipient declined
```

---

## Payload Structure

### Root Level Fields

```json
{
  "event_type": "document_completed",      // Event type
  "timestamp": "2024-01-15T14:30:00Z",     // UTC timestamp
  "document": {...},                       // Document info
  "recipient": {...},                      // Recipient (if applicable)
  "user": {...},                           // User who triggered event
  "metadata": {...}                        // Custom metadata
}
```

### Document Object

```json
{
  "id": "doc_8e6f8e6f8e6f8e6f",
  "name": "Sales Proposal - Acme",
  "status": "document.completed",
  "template_uuid": "abc123-def456",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "completed_at": "2024-01-15T14:30:00Z",
  "recipients": [
    {
      "id": "r_1234567890",
      "email": "john@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "Client",
      "status": "completed",
      "completed_at": "2024-01-15T14:30:00Z"
    }
  ],
  "fields": {
    "Company Name": "Acme Corp",
    "Proposal Amount": "$50,000"
  }
}
```

---

## Security

### Signature Verification

**CRITICAL:** Always verify webhook signatures to ensure requests are from PandaDoc.

**Algorithm:** HMAC-SHA256

**Header:** `X-Pandadoc-Signature`

**Implementation:**

```python
import hmac
import hashlib

def verify_webhook_signature(raw_body, signature, shared_key):
    """Verify webhook signature."""

    expected = hmac.new(
        shared_key.encode(),
        raw_body.encode(),
        hashlib.sha256
    ).hexdigest()

    # Use constant-time comparison (prevents timing attacks)
    return hmac.compare_digest(signature, expected)

# Usage
raw_body = request.get_data(as_text=True)
signature = request.headers.get('X-Pandadoc-Signature')

if not verify_webhook_signature(raw_body, signature, WEBHOOK_SHARED_KEY):
    return {'error': 'Unauthorized'}, 401
```

### HTTPS Requirement

Webhook endpoints **MUST** use HTTPS in production.

```python
# Check request is HTTPS
if request.scheme != 'https':
    return {'error': 'HTTPS required'}, 400
```

### IP Allowlisting (Optional)

Restrict to PandaDoc IP addresses:

```python
# Get PandaDoc webhook server IPs from:
# https://api.pandadoc.com/webhook-ips

PANDADOC_IPS = [
    "192.0.2.1",
    "192.0.2.2"
]

client_ip = request.remote_addr

if client_ip not in PANDADOC_IPS:
    return {'error': 'Forbidden'}, 403
```

### Response Requirements

Your endpoint **MUST**:
1. Respond with HTTP 2xx status (200, 201, 202)
2. Respond within 30 seconds
3. Not require authentication

```python
@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_webhook():
    # Process quickly
    event = request.json
    queue_event_for_processing(event)  # Don't process synchronously

    # Return immediately
    return {'success': True}, 200  # Must be 2xx
```

---

## Handling Events

### Pattern 1: Queue Processing

Process events asynchronously to respond quickly:

```python
from queue import Queue
import threading

event_queue = Queue()

@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_webhook():
    """Webhook handler - respond quickly."""

    event = request.json

    # Queue for processing
    event_queue.put(event)

    # Return immediately
    return {'success': True}, 200

def process_events():
    """Background worker - process events from queue."""

    while True:
        event = event_queue.get()

        try:
            # Long-running processing
            handle_event(event)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            event_queue.task_done()

# Start worker thread
worker = threading.Thread(target=process_events, daemon=True)
worker.start()
```

### Pattern 2: Idempotent Processing

Handle duplicate events gracefully:

```python
import json

# Track processed events
processed_events = set()

def is_duplicate(event):
    """Check if we've already processed this event."""

    # Use document ID + event type + timestamp as unique key
    event_key = f"{event['document']['id']}_{event['event_type']}_{event['timestamp']}"

    if event_key in processed_events:
        return True

    # Remember this event
    processed_events.add(event_key)

    # Clean up old entries (keep last 1 hour)
    # In production, use database instead of set
    return False

@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_webhook():
    event = request.json

    if is_duplicate(event):
        print(f"Duplicate event, ignoring")
        return {'success': True}, 200

    handle_event(event)
    return {'success': True}, 200
```

### Pattern 3: Update CRM

Sync document status to CRM:

```python
def handle_event(event):
    """Handle webhook event."""

    event_type = event.get('event_type')
    doc_id = event['document']['id']

    if event_type == 'document_completed':
        # Get document details
        response = requests.get(
            f'https://api.pandadoc.com/public/v1/documents/{doc_id}',
            headers={'Authorization': f'API-Key {API_KEY}'}
        )
        doc = response.json()

        # Update CRM opportunity
        update_crm_opportunity(
            opportunity_id=doc['metadata'].get('opportunity_id'),
            stage='Closed Won',
            signed_date=doc['completed_at'],
            document_id=doc_id
        )

        # Download and attach document
        download_response = requests.get(
            f'https://api.pandadoc.com/public/v1/documents/{doc_id}/download',
            headers={'Authorization': f'API-Key {API_KEY}'}
        )

        attach_to_crm(
            opportunity_id=doc['metadata'].get('opportunity_id'),
            file_content=download_response.content,
            file_name=f"{doc['name']}.pdf"
        )
```

---

## Testing

### Test 1: Use Webhook Tester Service

Use a free service to test webhook:

```bash
# 1. Get a test URL from https://webhook.site/
# 2. Create webhook subscription with test URL
# 3. Create a document in PandaDoc
# 4. See webhook requests in webhook.site dashboard
```

### Test 2: Send Test Webhook

PandaDoc can send test webhooks:

```bash
# Get webhook subscription ID
curl https://api.pandadoc.com/public/v1/webhook-subscriptions \
  -H "Authorization: API-Key YOUR_KEY"

# Send test event (if supported)
curl -X POST https://api.pandadoc.com/public/v1/webhook-subscriptions/WS_ID/test \
  -H "Authorization: API-Key YOUR_KEY"
```

### Test 3: Simulate Webhook Locally

```python
import json
import hmac
import hashlib
import requests

# Simulate webhook from PandaDoc
WEBHOOK_URL = "http://localhost:8080/webhooks/pandadoc"
WEBHOOK_SHARED_KEY = "your_key"

# Create test event
event = {
    "event_type": "document_completed",
    "timestamp": "2024-01-15T14:30:00Z",
    "document": {
        "id": "doc_test123",
        "name": "Test Proposal",
        "status": "document.completed"
    }
}

# Sign event
body = json.dumps(event)
signature = hmac.new(
    WEBHOOK_SHARED_KEY.encode(),
    body.encode(),
    hashlib.sha256
).hexdigest()

# Send webhook
response = requests.post(
    WEBHOOK_URL,
    data=body,
    headers={
        'Content-Type': 'application/json',
        'X-Pandadoc-Signature': signature
    }
)

print(f"Response: {response.status_code}")
print(f"Body: {response.text}")
```

---

## Production Checklist

Before deploying webhooks to production:

### Infrastructure
- [ ] HTTPS endpoint with valid certificate
- [ ] Endpoint accessible from internet
- [ ] 99.9% uptime SLA
- [ ] Load balancing for scale
- [ ] Monitoring and alerting

### Security
- [ ] Signature verification enabled
- [ ] HTTPS only (no HTTP)
- [ ] IP allowlisting (optional)
- [ ] Rate limiting configured
- [ ] Secrets in environment variables

### Code
- [ ] Responds within 30 seconds
- [ ] Returns HTTP 200-204
- [ ] Idempotent (handles duplicates)
- [ ] Queues long-running tasks
- [ ] Error handling and logging
- [ ] Graceful degradation

### Monitoring
- [ ] Webhook delivery logged
- [ ] Failed webhooks tracked
- [ ] Latency monitored
- [ ] Error rate tracked
- [ ] Alerts configured

### Documentation
- [ ] Event types documented
- [ ] Payload structure documented
- [ ] Troubleshooting guide
- [ ] Runbook for failures
- [ ] Update procedures

### Testing
- [ ] Unit tests for handlers
- [ ] Integration tests
- [ ] Load testing
- [ ] Failover testing
- [ ] Signature verification tested

---

## Troubleshooting

### Webhook Not Received

**Symptoms:**
- Document status changes but no webhook received
- Endpoint seems to be working

**Causes:**
1. Webhook subscription not active
2. Endpoint returning non-2xx status
3. Endpoint timing out
4. Firewall blocking PandaDoc IPs

**Solutions:**

```bash
# Verify webhook subscription exists
curl https://api.pandadoc.com/public/v1/webhook-subscriptions \
  -H "Authorization: API-Key YOUR_KEY"

# Check subscription is active
# Look for "active": true

# Test endpoint accessibility
curl -X POST https://your-domain.com/webhooks/pandadoc \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Should return 200 OK
```

### Signature Verification Failing

**Symptoms:**
- Webhooks received but signature verification fails
- Error: "Invalid signature"

**Causes:**
1. Using wrong shared key
2. Modifying request body before verification
3. Different encoding (UTF-8 vs other)

**Solutions:**

```python
# Check shared key matches
print(f"Shared key: {WEBHOOK_SHARED_KEY}")

# Verify using raw request body
raw_body = request.get_data(as_text=True)  # Get raw bytes
signature = request.headers.get('X-Pandadoc-Signature')

# Use constant-time comparison
import hmac
expected = hmac.new(
    WEBHOOK_SHARED_KEY.encode('utf-8'),
    raw_body.encode('utf-8'),
    hashlib.sha256
).hexdigest()

if hmac.compare_digest(expected, signature):
    print("Signature valid!")
else:
    print(f"Signature mismatch")
    print(f"Expected: {expected}")
    print(f"Got: {signature}")
```

### Webhook Timeout

**Symptoms:**
- Webhook response takes too long
- PandaDoc retries webhook
- Response after 30 seconds

**Solutions:**

```python
# Process asynchronously
@app.route('/webhooks/pandadoc', methods=['POST'])
def handle_webhook():
    event = request.json

    # Queue for background processing (non-blocking)
    background_worker.queue_task(process_event, event)

    # Return immediately (< 1 second)
    return {'success': True}, 200

def process_event(event):
    """Long-running task - process asynchronously."""
    # Download files
    # Update CRM
    # Send emails
    # etc.
```

### Duplicate Webhook Handling

**Symptoms:**
- Same event processed multiple times
- Database constraints failing
- Duplicate data in CRM

**Solutions:**

```python
def process_event(event):
    """Handle event idempotently."""

    # Create unique event ID
    event_id = f"{event['document']['id']}_{event['event_type']}_{event['timestamp']}"

    # Check if already processed
    if is_processed(event_id):
        print(f"Already processed: {event_id}")
        return

    # Process event
    do_processing(event)

    # Mark as processed
    mark_processed(event_id)

def is_processed(event_id):
    """Check if event was already processed."""
    # Use database, cache, or file
    query = db.query(ProcessedEvent).filter_by(id=event_id).first()
    return query is not None

def mark_processed(event_id):
    """Mark event as processed."""
    db.add(ProcessedEvent(id=event_id))
    db.commit()
```

---

## See Also

- [Endpoints Reference](./endpoints-reference.md)
- [Workflows Guide](./workflows.md)
- [Troubleshooting Guide](./troubleshooting.md)
