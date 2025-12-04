# PandaDoc Sales Manager Skill - Analysis & Component Design

**Created:** 2025-11-11
**Purpose:** Comprehensive analysis of PandaDoc API documentation and complete component design for the PandaDoc Sales Manager skill
**Status:** Complete

---

## Part 1: Documentation Analysis

### Tool Overview

**What PandaDoc Does:**
PandaDoc is a document automation platform that enables sales teams to create, send, track, and e-sign proposals, quotes, contracts, and agreements. The API provides programmatic access to all document lifecycle operations.

**Core Capabilities:**
- **Document Creation:** Create documents from templates or PDF files with pre-filled data
- **Document Management:** Update, send, track status, download, and delete documents
- **Template Management:** Manage reusable document templates
- **Contact Management:** Maintain customer/recipient information
- **Recipient Management:** Add, edit, remove, and reassign document recipients
- **E-Signature:** Send documents for electronic signature with signing order control
- **Status Tracking:** Monitor document progress through sent → viewed → completed lifecycle
- **Webhook Integration:** Receive real-time notifications of document events
- **Attachment Management:** Add supporting files to documents
- **Pricing Tables & Quotes:** Create and manage product pricing within documents
- **Folder Organization:** Organize documents and templates in folders

**Sales Manager Use Cases:**
1. **Proposal Automation:** Create custom proposals from templates with customer-specific data
2. **Quote Management:** Generate and send pricing quotes with approval workflows
3. **Contract Signing:** Send agreements for e-signature and track completion
4. **Customer Onboarding:** Automate document workflows for new customers
5. **Sales Pipeline Integration:** Link documents to CRM opportunities and track conversion
6. **Team Collaboration:** Share templates and documents across sales teams
7. **Performance Tracking:** Monitor document completion rates and bottlenecks
8. **Follow-up Automation:** Set up reminders for unsigned documents

**API Base URL:** `https://api.pandadoc.com`

---

### API Patterns

#### Authentication Methods

**1. API Key Authentication (Recommended for Server-Side)**
```http
Authorization: API-Key YOUR_API_KEY
Content-Type: application/json
```

**Use Cases:** Backend automation, server-to-server integration, scheduled jobs

**2. OAuth 2.0 Authentication (Recommended for User-Facing Apps)**
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**OAuth Flow:**
```http
POST /oauth2/access_token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET&
code=AUTHORIZATION_CODE&
scope=read+write
```

**Token Refresh:**
```http
POST /oauth2/access_token
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token&
client_id=YOUR_CLIENT_ID&
client_secret=YOUR_CLIENT_SECRET&
refresh_token=YOUR_REFRESH_TOKEN
```

#### Common Request/Response Patterns

**Paginated List Requests:**
```http
GET /public/v1/documents?count=100&page=1&status=0&order_by=date_created

Response:
{
  "results": [...],
  "count": 100,
  "next": "https://api.pandadoc.com/public/v1/documents?page=2",
  "previous": null
}
```

**Document Creation (Async Pattern):**
```http
POST /public/v1/documents
{
  "name": "Sales Proposal",
  "template_uuid": "template_id",
  "recipients": [...],
  "fields": {...}
}

Response (201 Created):
{
  "id": "document_id",
  "status": "document.uploaded",  // Initial async status
  "links": {...}
}
```

**Status Polling Pattern:**
```http
GET /public/v1/documents/{id}

Response:
{
  "id": "document_id",
  "name": "Sales Proposal",
  "status": "document.draft"  // Ready for operations
}
```

**Document Sending:**
```http
POST /public/v1/documents/{id}/send
{
  "message": "Please review and sign",
  "subject": "Proposal for Review",
  "silent": false
}

Response (200 OK):
{
  "id": "document_id",
  "status": "document.sent",
  "recipients": [...]
}
```

**Error Response Pattern:**
```json
{
  "type": "validation_error",
  "detail": "Invalid field value",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

#### HTTP Status Codes

| Code | Meaning | Common Causes | Action Required |
|------|---------|---------------|-----------------|
| 200 | OK | Request successful | Process response data |
| 201 | Created | Resource created | Save resource ID |
| 204 | No Content | Update/delete successful | No further action |
| 400 | Bad Request | Invalid parameters | Fix request parameters |
| 401 | Unauthorized | Invalid/missing API key | Check authentication |
| 404 | Not Found | Resource doesn't exist | Verify resource ID |
| 409 | Conflict | Invalid state operation | Check document status |
| 429 | Rate Limit | Too many requests | Implement backoff |
| 500+ | Server Error | PandaDoc server issue | Retry with backoff |

---

### Core Workflows

#### Workflow 1: Complete Document Lifecycle (Create → Send → Track)

**Steps:**
1. **Create Document from Template**
   - Endpoint: `POST /public/v1/documents`
   - Provide: template_uuid, recipients, fields, tokens
   - Receive: document ID with status "document.uploaded"

2. **Poll for Draft Status**
   - Endpoint: `GET /public/v1/documents/{id}`
   - Poll every 2 seconds until status = "document.draft"
   - Timeout: 60 seconds (usually takes 2-5 seconds)

3. **Send Document**
   - Endpoint: `POST /public/v1/documents/{id}/send`
   - Provide: subject, message, silent flag
   - Status changes to "document.sent"

4. **Track Status Changes**
   - Poll: `GET /public/v1/documents/{id}`
   - States: sent → viewed → completed
   - Or use webhooks for real-time updates

5. **Download Completed Document**
   - Endpoint: `GET /public/v1/documents/{id}/download`
   - Only when status = "document.completed"
   - Returns PDF binary data

**Critical Points:**
- MUST wait for "document.draft" before sending
- Cannot skip status polling (async processing)
- Rate limit: max 10 requests/minute
- Use exponential backoff on 429 errors

#### Workflow 2: Proposal Creation with Approval

**Steps:**
1. **Create Document with Multiple Recipients**
   ```json
   {
     "recipients": [
       {
         "email": "manager@company.com",
         "role": "Manager",
         "signing_order": 1
       },
       {
         "email": "client@customer.com",
         "role": "Client",
         "signing_order": 2
       }
     ]
   }
   ```

2. **Send with Approval Workflow**
   - Manager must sign first (signing_order: 1)
   - Client can only access after manager signs
   - Track completion per recipient

3. **Monitor Progress**
   - Check document status
   - View recipient-specific status
   - Handle declined scenarios

#### Workflow 3: Bulk Document Creation

**Pattern for Creating Multiple Documents:**
```python
documents = []
for customer in customers:
    # Create document
    response = create_document(customer_data)
    documents.append(response)

    # Rate limiting: 10 req/min = 1 req per 6 seconds
    time.sleep(6)

    # Poll for ready status
    wait_for_draft(response['id'])

    # Rate limiting again
    time.sleep(6)
```

**Best Practices:**
- Batch size: 50-100 documents per run
- Add delays between requests (6+ seconds)
- Implement exponential backoff on errors
- Log failures for retry
- Use async status polling efficiently

#### Workflow 4: Document with Attachments

**Steps:**
1. Create document (wait for draft)
2. Add attachments via multipart upload
3. Send document with attachments
4. Recipients receive document + attachments

**Attachment Upload:**
```http
POST /public/v1/documents/{id}/attachments?upload
Content-Type: multipart/form-data

file: <binary>
data: {"name": "Supporting Document"}
```

#### Workflow 5: Webhook Integration for Real-Time Tracking

**Setup Webhook:**
```json
POST /public/v1/webhook-subscriptions
{
  "name": "Document Status Tracker",
  "url": "https://your-server.com/webhooks/pandadoc",
  "triggers": [
    "document_state_changed",
    "document_sent",
    "document_viewed",
    "document_completed"
  ],
  "payload": ["metadata", "fields", "recipients"]
}
```

**Webhook Events:**
- Receive real-time notifications
- No need for status polling
- Handle webhook verification
- Process document state changes

---

### Configuration Requirements

#### API Key Setup

**Obtaining API Key:**
1. Log in to PandaDoc account
2. Navigate to Settings → API
3. Generate API key (Sandbox or Production)
4. Copy and securely store API key

**Environment Variables:**
```bash
# Sandbox (Testing)
export PANDADOC_API_KEY="YOUR_SANDBOX_API_KEY"
export PANDADOC_ENV="sandbox"

# Production
export PANDADOC_API_KEY="YOUR_PRODUCTION_API_KEY"
export PANDADOC_ENV="production"
```

**Security Best Practices:**
- NEVER commit API keys to version control
- Use environment variables or secret managers
- Rotate API keys regularly (quarterly recommended)
- Use separate keys for dev/staging/production
- Limit API key permissions when possible

#### Rate Limiting

**Limits:**
- **Sandbox:** 10 requests per minute
- **Production:** Higher limits (contact PandaDoc for details)

**Rate Limit Headers (if provided):**
```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640000000
```

**Handling Strategy:**
```python
def handle_rate_limit(func):
    max_retries = 3
    base_delay = 60  # Start with 60 seconds

    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # Exponential: 60s, 120s, 240s
            time.sleep(delay)
```

#### Template Configuration

**Template Requirements:**
- Templates must be created in PandaDoc UI first
- Note template UUIDs for use in API
- Document field names and roles
- Understand merge fields vs custom fields

**Template Mapping File Example:**
```yaml
templates:
  sales_proposal:
    uuid: "abc123-def456-ghi789"
    name: "Standard Sales Proposal"
    fields:
      - Company Name
      - Proposal Amount
      - Effective Date
    roles:
      - Client
      - Manager

  service_agreement:
    uuid: "xyz789-uvw456-rst123"
    name: "Service Agreement Template"
    fields:
      - Service Type
      - Start Date
      - End Date
    roles:
      - Client
```

#### Webhook Configuration

**Webhook Endpoint Requirements:**
- HTTPS endpoint (required for production)
- Handle POST requests
- Verify webhook signature
- Return 200 OK within 30 seconds
- Implement idempotency (handle duplicate events)

**Webhook Signature Verification:**
```python
import hmac
import hashlib

def verify_webhook(payload, signature, shared_key):
    expected = hmac.new(
        shared_key.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

### Best Practices

#### 1. Asynchronous Processing

**CRITICAL: Always Poll for Status**

Document creation is asynchronous. Attempting operations before the document is ready results in 404 errors.

**Correct Pattern:**
```python
def create_and_wait(api_client, request):
    # Step 1: Create document (async)
    response = api_client.create_document(request)
    document_id = response['id']

    # Step 2: Poll until ready (REQUIRED)
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(2)  # Wait 2 seconds between checks

        status_response = api_client.get_document_status(document_id)

        if status_response['status'] == 'document.draft':
            return document_id  # Ready for operations

        if status_response['status'].startswith('document.error'):
            raise DocumentCreationError(status_response['status'])

    raise TimeoutError(f"Document not ready after {max_attempts * 2} seconds")
```

**Why This Matters:**
- Server needs 2-5 seconds to process document
- Sending immediately causes 404 "document not found"
- Status polling is NOT optional
- No way to skip this step

#### 2. Error Handling Strategies

**Specific Exception Handling:**
```python
try:
    response = api_client.create_document(request)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        # Authentication failed
        log.error("Invalid API key")
        refresh_credentials()
        retry()

    elif e.response.status_code == 404:
        # Document not found (too early after creation)
        log.warning("Document not ready yet, waiting...")
        time.sleep(2)
        retry()

    elif e.response.status_code == 429:
        # Rate limited
        log.warning("Rate limit exceeded")
        wait_time = extract_retry_after(e.response.headers)
        time.sleep(wait_time)
        retry()

    elif e.response.status_code >= 500:
        # Server error - retry with backoff
        log.error("Server error, retrying...")
        exponential_backoff_retry()

    else:
        # Other error - log and fail
        log.error(f"Unexpected error: {e.response.status_code}")
        raise
```

#### 3. Field Mapping Standards

**Use Merge Fields for Standard Data:**
```python
# Good: Use PandaDoc system merge fields
fields = {
    "[Client.Company]": customer.company_name,
    "[Client.Email]": customer.email,
    "[Client.Phone]": customer.phone,
    "[Client.Address]": customer.address
}
```

**Template-Specific Fields:**
```python
# Custom fields defined in template
fields = {
    "Proposal Amount": "$50,000",
    "Discount Percentage": "10%",
    "Effective Date": "2024-01-15"
}
```

**Field Naming Conventions:**
- Use descriptive names: "Proposal Amount" not "amt"
- Consistent capitalization: "Company Name" across all templates
- Avoid special characters except spaces, periods, underscores
- Match exact template field names (case-sensitive)

#### 4. Document Status Management

**Status Enum Reference:**
```python
DOCUMENT_STATUSES = {
    0: "document.draft",          # Ready for sending
    1: "document.sent",           # Sent to recipients
    2: "document.completed",      # All signatures collected
    3: "document.uploaded",       # Initial async processing
    4: "document.error",          # Error during processing
    5: "document.viewed",         # Recipient viewed
    6: "document.waiting_approval",  # Pending approval
    7: "document.approved",       # Approved
    8: "document.rejected",       # Rejected
    9: "document.waiting_pay",    # Pending payment
    10: "document.paid",          # Payment completed
    11: "document.voided",        # Voided
    12: "document.declined",      # Recipient declined
    13: "document.external_review" # External review
}
```

**Status Transition Logic:**
```python
def can_send_document(status):
    return status == "document.draft"

def can_download_document(status):
    return status in ["document.completed", "document.approved"]

def is_final_status(status):
    return status in [
        "document.completed",
        "document.declined",
        "document.voided"
    ]
```

#### 5. Recipient Management

**Recipient Verification Settings:**
```python
recipient = {
    "email": "client@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "Client",
    "verification_settings": {
        "verification_place": "before_open",  # Verify before opening doc
        "passcode_verification": {
            "passcode": "1234"  # Simple passcode
        },
        "phone_verification": {
            "phone": "+1-555-0123"  # SMS verification
        }
    }
}
```

**Signing Order:**
```python
recipients = [
    {
        "email": "manager@company.com",
        "role": "Manager",
        "signing_order": 1  # Must sign first
    },
    {
        "email": "director@company.com",
        "role": "Director",
        "signing_order": 1  # Can sign in parallel with manager
    },
    {
        "email": "client@customer.com",
        "role": "Client",
        "signing_order": 2  # Signs after internal approvals
    }
]
```

#### 6. Logging and Monitoring

**Comprehensive Logging:**
```python
import logging

logger = logging.getLogger(__name__)

def create_document_with_logging(request):
    logger.info(f"Creating document: {request['name']}")
    logger.debug(f"Template: {request['template_uuid']}")
    logger.debug(f"Recipients: {len(request['recipients'])}")

    try:
        response = api_client.create_document(request)
        logger.info(f"Document created: {response['id']}")

        # Log status transitions
        status = wait_for_draft(response['id'])
        logger.info(f"Document ready: {response['id']} (status: {status})")

        return response

    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        logger.exception("Full traceback:")
        raise
```

**Metrics to Track:**
- Document creation rate
- Average time to draft status
- Send success rate
- Completion rate
- Average completion time
- Error rate by type
- Rate limit incidents

---

### Key Examples

#### Example 1: Create Document from Template

```python
import os
import time
import requests

API_KEY = os.environ["PANDADOC_API_KEY"]
BASE_URL = "https://api.pandadoc.com/public/v1"

def create_document():
    """Create a document from template with pre-filled data."""

    # Step 1: Create document
    url = f"{BASE_URL}/documents"
    headers = {
        "Authorization": f"API-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": "Sales Proposal - Acme Corp",
        "template_uuid": "YOUR_TEMPLATE_UUID",
        "recipients": [
            {
                "email": "client@acme.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "Client"
            }
        ],
        "fields": {
            "Company Name": "Acme Corporation",
            "Proposal Amount": "$50,000",
            "Effective Date": "2024-01-15"
        },
        "tokens": [
            {
                "name": "Company.Address",
                "value": "123 Main St, Austin, TX 78701"
            }
        ],
        "metadata": {
            "opportunity_id": "12345",
            "sales_rep": "Jane Smith"
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    document = response.json()

    print(f"Document created: {document['id']}")
    print(f"Status: {document['status']}")

    # Step 2: Wait for document to be ready
    document_id = document['id']
    max_attempts = 30

    for attempt in range(max_attempts):
        time.sleep(2)

        status_url = f"{BASE_URL}/documents/{document_id}"
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        status_data = status_response.json()

        print(f"Attempt {attempt + 1}: {status_data['status']}")

        if status_data['status'] == 'document.draft':
            print("Document ready!")
            return document_id

    raise TimeoutError("Document not ready after 60 seconds")

if __name__ == "__main__":
    doc_id = create_document()
    print(f"Ready to send: {doc_id}")
```

#### Example 2: Send Document

```python
def send_document(document_id):
    """Send document to recipients."""

    url = f"{BASE_URL}/documents/{document_id}/send"
    headers = {
        "Authorization": f"API-Key {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "Proposal for Review",
        "message": "Please review the attached proposal and sign if you agree to the terms.",
        "silent": False,  # Send email notifications
        "forwarding_settings": {
            "forwarding_allowed": True
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    print("Document sent successfully!")
    return response.json()
```

#### Example 3: Check Document Status

```python
def check_status(document_id):
    """Check current document status."""

    url = f"{BASE_URL}/documents/{document_id}"
    headers = {
        "Authorization": f"API-Key {API_KEY}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    doc = response.json()

    print(f"Document: {doc['name']}")
    print(f"Status: {doc['status']}")
    print(f"Recipients: {len(doc.get('recipients', []))}")

    return doc
```

#### Example 4: Download Completed Document

```python
def download_document(document_id, output_path):
    """Download completed document as PDF."""

    url = f"{BASE_URL}/documents/{document_id}/download"
    headers = {
        "Authorization": f"API-Key {API_KEY}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        f.write(response.content)

    print(f"Document downloaded: {output_path}")
```

#### Example 5: Complete Workflow

```python
def complete_workflow():
    """Complete document workflow from creation to download."""

    # 1. Create document
    print("1. Creating document...")
    doc_id = create_document()

    # 2. Send document
    print("\n2. Sending document...")
    send_document(doc_id)

    # 3. Monitor status
    print("\n3. Monitoring status...")
    while True:
        doc = check_status(doc_id)

        if doc['status'] == 'document.completed':
            print("\nDocument completed!")
            break

        print(f"Status: {doc['status']} - waiting...")
        time.sleep(30)  # Check every 30 seconds

    # 4. Download completed document
    print("\n4. Downloading document...")
    download_document(doc_id, f"completed_{doc_id}.pdf")

    print("\nWorkflow complete!")

if __name__ == "__main__":
    complete_workflow()
```

---

## Part 2: Component Design

### Helper Scripts Design

#### Script 1: create_proposal.py

**Purpose:** Create a sales proposal from template with customer data

**Inputs:**
- Template UUID or name
- Customer information (JSON or command-line args)
- Optional: pricing data, fields, metadata

**Outputs:**
- Document ID
- Status updates during creation
- Success/failure message

**Workflow:**
1. Load customer data from input
2. Validate required fields
3. Create document via API
4. Poll for draft status
5. Return document ID

**Error Handling:**
- Validate template exists
- Check for missing required fields
- Handle rate limiting
- Log all operations

**Example Usage:**
```bash
python create_proposal.py \
  --template "Sales Proposal" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com" \
  --amount "50000" \
  --effective-date "2024-01-15"
```

**Code Structure:**
```python
def main():
    args = parse_arguments()
    customer_data = load_customer_data(args)

    # Validate inputs
    validate_customer_data(customer_data)
    template = get_template(args.template)

    # Create document
    doc_id = create_document(template, customer_data)

    print(f"Proposal created: {doc_id}")
```

#### Script 2: send_document.py

**Purpose:** Send a document to recipients with customizable message

**Inputs:**
- Document ID
- Optional: custom subject and message
- Optional: silent mode flag

**Outputs:**
- Send confirmation
- Recipient list
- Tracking URL

**Workflow:**
1. Verify document exists and is in draft status
2. Send document via API
3. Confirm recipients received notification

**Error Handling:**
- Check document status before sending
- Handle invalid document ID
- Validate document is not already sent

**Example Usage:**
```bash
python send_document.py \
  --document-id "abc123" \
  --subject "Proposal for Review" \
  --message "Please review and sign"
```

#### Script 3: check_document_status.py

**Purpose:** Check status of one or more documents

**Inputs:**
- Document ID(s)
- Optional: watch mode (continuous monitoring)
- Optional: export format (JSON, CSV, table)

**Outputs:**
- Current status
- Last modified timestamp
- Recipient status (if available)
- Next action recommendations

**Workflow:**
1. Fetch document status via API
2. Parse and format status information
3. Display in requested format
4. If watch mode: poll every N seconds

**Error Handling:**
- Handle document not found
- Rate limit monitoring
- Graceful exit on Ctrl+C

**Example Usage:**
```bash
# Single document
python check_document_status.py --document-id "abc123"

# Multiple documents
python check_document_status.py --document-ids "abc123,def456,ghi789"

# Watch mode
python check_document_status.py --document-id "abc123" --watch --interval 30

# Export to CSV
python check_document_status.py --document-ids "abc123,def456" --format csv --output status.csv
```

#### Script 4: bulk_create_documents.py

**Purpose:** Create multiple documents from template with batch customer data

**Inputs:**
- Template UUID or name
- Customer data file (CSV, JSON, Excel)
- Field mapping configuration
- Batch size and delay settings

**Outputs:**
- Created document IDs
- Success/failure report
- Error log for failed documents

**Workflow:**
1. Load customer data from file
2. Validate all records
3. Process in batches with rate limiting
4. Track progress and errors
5. Generate completion report

**Error Handling:**
- Continue on individual failures
- Log failed records for retry
- Implement exponential backoff
- Save progress for resume capability

**Example Usage:**
```bash
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.csv \
  --batch-size 50 \
  --delay 6
```

#### Script 5: download_completed.py

**Purpose:** Download all completed documents in a date range

**Inputs:**
- Date range (from/to)
- Optional: status filter
- Optional: output directory
- Optional: naming pattern

**Outputs:**
- Downloaded PDF files
- Download summary report
- Failed downloads log

**Workflow:**
1. List documents in date range with status filter
2. Filter for completed documents
3. Download each document
4. Save with configured naming pattern
5. Generate summary report

**Error Handling:**
- Handle download failures
- Retry failed downloads
- Skip already downloaded files
- Rate limit handling

**Example Usage:**
```bash
python download_completed.py \
  --from "2024-01-01" \
  --to "2024-01-31" \
  --output ./downloads \
  --pattern "{date}_{customer}_{id}.pdf"
```

#### Script 6: template_manager.py

**Purpose:** List, inspect, and manage templates

**Inputs:**
- Command: list, show, fields, export
- Optional: template name/UUID

**Outputs:**
- Template list or details
- Field definitions
- Template JSON export

**Workflow:**
1. Execute requested command
2. Format and display results
3. Export if requested

**Error Handling:**
- Handle template not found
- Validate permissions

**Example Usage:**
```bash
# List all templates
python template_manager.py list

# Show template details
python template_manager.py show --template "Sales Proposal"

# List template fields
python template_manager.py fields --template "Sales Proposal"

# Export template configuration
python template_manager.py export --template "Sales Proposal" --output template.json
```

#### Script 7: webhook_tester.py

**Purpose:** Test webhook endpoint and simulate events

**Inputs:**
- Webhook URL
- Event type to simulate
- Optional: custom payload

**Outputs:**
- Test results
- Response verification
- Signature validation results

**Workflow:**
1. Send test webhook event
2. Verify response
3. Check signature validation
4. Report results

**Example Usage:**
```bash
python webhook_tester.py \
  --url "https://your-server.com/webhooks/pandadoc" \
  --event "document_completed" \
  --verify-signature
```

---

### Config Templates Design

#### Template 1: api_config.yml

**Purpose:** Central configuration for API settings and credentials

**Structure:**
```yaml
# PandaDoc API Configuration

# Environment settings
environment: sandbox  # sandbox | production

# Authentication
authentication:
  type: api_key  # api_key | oauth2
  api_key: ${PANDADOC_API_KEY}  # Use environment variable

  # OAuth2 settings (if using OAuth)
  oauth2:
    client_id: ${PANDADOC_CLIENT_ID}
    client_secret: ${PANDADOC_CLIENT_SECRET}
    redirect_uri: http://localhost:8080/callback
    scopes:
      - read
      - write

# API settings
api:
  base_url: https://api.pandadoc.com
  version: v1
  timeout: 30  # seconds

  # Rate limiting
  rate_limit:
    requests_per_minute: 10
    backoff_strategy: exponential  # exponential | linear
    max_retries: 3
    retry_delays: [60, 120, 240]  # seconds

# Async processing
async:
  status_poll_interval: 2  # seconds
  status_poll_timeout: 60  # seconds
  max_poll_attempts: 30

# Logging
logging:
  level: INFO  # DEBUG | INFO | WARNING | ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/pandadoc.log
  console: true

# Defaults
defaults:
  document:
    silent: false  # Send email notifications by default
    forwarding_allowed: true

  download:
    format: pdf
    watermark: false
```

**Usage Scenario:** Load at application startup, override with environment-specific settings

#### Template 2: template_mappings.yml

**Purpose:** Map business data fields to PandaDoc template fields

**Structure:**
```yaml
# Template Field Mappings

templates:
  sales_proposal:
    uuid: "abc123-def456-ghi789"
    name: "Standard Sales Proposal"

    # Field mappings: business_field -> template_field
    field_mappings:
      customer_name: "Company Name"
      customer_email: "[Client.Email]"
      customer_phone: "[Client.Phone]"
      customer_address: "[Client.Address]"
      proposal_amount: "Proposal Amount"
      discount_percent: "Discount Percentage"
      effective_date: "Effective Date"
      expiration_date: "Expiration Date"

    # Token mappings
    token_mappings:
      sales_rep_name: "SalesRep.Name"
      sales_rep_email: "SalesRep.Email"
      company_address: "Company.Address"

    # Default values
    defaults:
      discount_percent: "0%"
      payment_terms: "Net 30"

    # Required fields
    required_fields:
      - customer_name
      - customer_email
      - proposal_amount
      - effective_date

    # Recipient roles
    roles:
      - name: Client
        signing_order: 2
      - name: Manager
        signing_order: 1

  service_agreement:
    uuid: "xyz789-uvw456-rst123"
    name: "Service Agreement Template"

    field_mappings:
      customer_name: "Client Company"
      service_type: "Service Type"
      start_date: "Start Date"
      end_date: "End Date"
      monthly_fee: "Monthly Fee"

    required_fields:
      - customer_name
      - service_type
      - start_date
      - end_date

    roles:
      - name: Client
        signing_order: 1
```

**Usage Scenario:** Load mappings at runtime, validate data before document creation

#### Template 3: webhook_config.yml

**Purpose:** Configuration for webhook subscriptions

**Structure:**
```yaml
# Webhook Configuration

webhooks:
  document_tracker:
    name: "Document Status Tracker"
    url: "https://your-server.com/webhooks/pandadoc/status"
    active: true

    triggers:
      - document_state_changed
      - document_sent
      - document_viewed
      - document_completed
      - document_declined

    payload:
      - metadata
      - fields
      - recipients

    # Webhook endpoint settings
    endpoint:
      verify_signature: true
      timeout: 30  # seconds
      retry_failed: true
      max_retries: 3

  approval_notifications:
    name: "Approval Notifications"
    url: "https://your-server.com/webhooks/pandadoc/approvals"
    active: true

    triggers:
      - document_waiting_approval
      - document_approved
      - document_rejected

    payload:
      - metadata
      - recipients
```

**Usage Scenario:** Create/update webhook subscriptions, configure webhook endpoints

#### Template 4: batch_config.yml

**Purpose:** Configuration for batch processing operations

**Structure:**
```yaml
# Batch Processing Configuration

batch:
  # Batch size limits
  default_batch_size: 50
  max_batch_size: 100

  # Processing delays
  inter_request_delay: 6  # seconds (for rate limiting)
  inter_batch_delay: 60  # seconds between batches

  # Error handling
  error_handling:
    continue_on_error: true
    log_errors: true
    error_log_path: logs/batch_errors.log

    # Retry configuration
    retry_failed: true
    max_retries_per_item: 3
    retry_delay: 60  # seconds

  # Progress tracking
  progress:
    save_progress: true
    progress_file: .batch_progress.json
    resume_on_restart: true

  # Output
  output:
    format: csv  # csv | json | excel
    path: output/batch_results.csv
    include_timestamp: true
```

**Usage Scenario:** Configure batch document creation, downloads, or updates

#### Template 5: field_validation.yml

**Purpose:** Define validation rules for document fields

**Structure:**
```yaml
# Field Validation Rules

validation_rules:
  email:
    type: email
    required: true
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

  phone:
    type: phone
    required: false
    pattern: "^\\+?1?\\d{10,15}$"
    example: "+1-555-0123"

  date:
    type: date
    required: true
    format: "YYYY-MM-DD"
    min: "2024-01-01"
    max: "2030-12-31"

  currency:
    type: currency
    required: true
    pattern: "^\\$?\\d{1,3}(,\\d{3})*(\\.\\d{2})?$"
    example: "$50,000.00"

  percentage:
    type: percentage
    required: false
    pattern: "^\\d{1,3}%?$"
    min: 0
    max: 100

  company_name:
    type: string
    required: true
    min_length: 2
    max_length: 200

  postal_code:
    type: string
    required: false
    pattern: "^\\d{5}(-\\d{4})?$"
    example: "78701"
```

**Usage Scenario:** Validate fields before document creation, provide helpful error messages

---

### Guardrails & Mandatory Workflows

#### Guardrail 1: Status Polling Before Send

**Rule:** MUST poll for "document.draft" status before sending

**Reason:** Document creation is asynchronous. Sending before ready causes 404 errors.

**Implementation:**
```python
def create_and_send_document(request):
    # Step 1: Create
    doc_id = create_document(request)

    # Step 2: MANDATORY - Poll for draft status
    wait_for_draft_status(doc_id)  # Raises error if timeout

    # Step 3: Now safe to send
    send_document(doc_id)
```

**Validation:**
- Function enforces polling before send
- No direct send without status check
- Timeout after 60 seconds with clear error

#### Guardrail 2: Rate Limit Enforcement

**Rule:** MUST respect 10 requests/minute limit in sandbox

**Reason:** Exceeding rate limit results in 429 errors and temporary blocking

**Implementation:**
```python
class RateLimiter:
    def __init__(self, requests_per_minute=10):
        self.requests_per_minute = requests_per_minute
        self.request_times = []

    def wait_if_needed(self):
        now = time.time()
        minute_ago = now - 60

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if t > minute_ago]

        # Check if limit reached
        if len(self.request_times) >= self.requests_per_minute:
            # Calculate wait time
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest) + 1

            print(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)

        # Record this request
        self.request_times.append(now)

# Usage
rate_limiter = RateLimiter()

def api_call():
    rate_limiter.wait_if_needed()
    return make_request()
```

#### Guardrail 3: Credential Validation

**Rule:** MUST validate API key before operations

**Reason:** Invalid credentials cause all operations to fail

**Implementation:**
```python
def validate_credentials():
    """Validate API key by making test request."""
    try:
        url = f"{BASE_URL}/members/current"
        headers = {"Authorization": f"API-Key {API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key")
        raise

# Run at startup
validate_credentials()
```

#### Guardrail 4: Template Existence Check

**Rule:** MUST verify template exists before creating documents

**Reason:** Invalid template UUID causes creation to fail

**Implementation:**
```python
def verify_template(template_uuid):
    """Verify template exists and is accessible."""
    try:
        url = f"{BASE_URL}/templates/{template_uuid}"
        headers = {"Authorization": f"API-Key {API_KEY}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Template not found: {template_uuid}")
        raise

# Check before document creation
template = verify_template(template_uuid)
```

#### Guardrail 5: Field Validation

**Rule:** MUST validate required fields before document creation

**Reason:** Missing required fields cause creation to fail or produce incomplete documents

**Implementation:**
```python
def validate_fields(fields, required_fields):
    """Validate all required fields are present and valid."""
    missing = []
    invalid = []

    for field_name in required_fields:
        if field_name not in fields:
            missing.append(field_name)
        elif not fields[field_name]:
            invalid.append(field_name)

    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    if invalid:
        raise ValueError(f"Empty required fields: {', '.join(invalid)}")

# Usage
required_fields = ["Company Name", "Proposal Amount", "Effective Date"]
validate_fields(request['fields'], required_fields)
```

#### Guardrail 6: Exponential Backoff on Errors

**Rule:** MUST implement exponential backoff for 429 and 500+ errors

**Reason:** Immediate retries amplify problems, exponential backoff allows recovery

**Implementation:**
```python
def exponential_backoff_retry(func, max_retries=3):
    """Retry function with exponential backoff."""
    base_delay = 2

    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code not in [429, 500, 502, 503, 504]:
                raise  # Don't retry other errors

            if attempt == max_retries - 1:
                raise  # Last attempt, give up

            # Exponential backoff: 2s, 4s, 8s
            delay = base_delay * (2 ** attempt)
            print(f"Retry {attempt + 1}/{max_retries} after {delay}s...")
            time.sleep(delay)
```

---

### Checklists Design

#### Checklist 1: Initial Setup

**Purpose:** Ensure proper environment setup before using the skill

```markdown
## PandaDoc Sales Manager - Initial Setup Checklist

### Prerequisites
- [ ] Python 3.8+ installed
- [ ] pip package manager available
- [ ] Git installed (if cloning from repository)
- [ ] Text editor or IDE configured

### Account Setup
- [ ] PandaDoc account created
- [ ] Sandbox API key generated
- [ ] Production API key generated (for production use)
- [ ] API keys stored securely (password manager, secret vault)

### Environment Configuration
- [ ] Create `.env` file from `.env.example`
- [ ] Set `PANDADOC_API_KEY` environment variable
- [ ] Set `PANDADOC_ENV` to "sandbox" or "production"
- [ ] Verify `.env` is in `.gitignore`

### Dependency Installation
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify installation: `python -c "import requests; print('OK')"`

### Template Setup
- [ ] Create templates in PandaDoc UI
- [ ] Document template UUIDs
- [ ] Update `template_mappings.yml` with UUIDs
- [ ] Document required fields per template
- [ ] Document recipient roles per template

### Configuration Files
- [ ] Copy `config/api_config.example.yml` to `config/api_config.yml`
- [ ] Update API configuration values
- [ ] Review rate limiting settings
- [ ] Configure logging preferences
- [ ] Set appropriate timeouts

### Validation
- [ ] Run `python scripts/validate_setup.py`
- [ ] Test API connectivity: `python scripts/test_connection.py`
- [ ] Verify template access: `python template_manager.py list`
- [ ] Create test document: `python create_proposal.py --test`

### Security Review
- [ ] API keys stored in environment variables only
- [ ] No credentials in code files
- [ ] `.env` file excluded from version control
- [ ] Appropriate file permissions set
- [ ] API key rotation schedule defined

### Documentation
- [ ] Review README.md
- [ ] Review API documentation
- [ ] Bookmark PandaDoc API reference
- [ ] Save template field reference
- [ ] Document custom workflows

### Next Steps
- [ ] Complete training/tutorial
- [ ] Create first real document
- [ ] Set up monitoring/logging
- [ ] Configure webhooks (if needed)
- [ ] Plan document workflows
```

#### Checklist 2: Document Creation Validation

**Purpose:** Validate document creation requests before submitting

```markdown
## Document Creation Validation Checklist

### Template Validation
- [ ] Template UUID is valid
- [ ] Template exists in PandaDoc account
- [ ] Template is not deleted
- [ ] Have permissions to use template

### Recipient Validation
- [ ] At least one recipient specified
- [ ] All recipient emails are valid format
- [ ] Recipient roles match template roles
- [ ] Signing order is logical (if multiple recipients)
- [ ] No duplicate recipient emails

### Field Validation
- [ ] All required fields provided
- [ ] Field names match template exactly (case-sensitive)
- [ ] Field values are appropriate types
- [ ] Date fields in correct format (YYYY-MM-DD)
- [ ] Currency fields formatted correctly
- [ ] Email/phone fields validated

### Token Validation
- [ ] Token names match template tokens
- [ ] All token values provided
- [ ] Token values are strings
- [ ] Special characters escaped if needed

### Metadata Validation
- [ ] Metadata is valid JSON object
- [ ] Metadata keys are meaningful
- [ ] Metadata values for tracking/reporting
- [ ] No sensitive data in metadata (if logged)

### Tags Validation
- [ ] Tags are meaningful for organization
- [ ] Tag naming convention followed
- [ ] Tags useful for future filtering

### Request Validation
- [ ] Request payload size reasonable
- [ ] No unnecessary data included
- [ ] Proper JSON formatting
- [ ] Content-Type header set

### Pre-Submission
- [ ] Rate limit check passed
- [ ] API key valid
- [ ] Network connectivity confirmed
- [ ] Error handling in place

### Post-Creation
- [ ] Document ID received
- [ ] Initial status is "document.uploaded"
- [ ] Status polling implemented
- [ ] Timeout handling configured
```

#### Checklist 3: Deployment Checklist

**Purpose:** Ensure production readiness before deployment

```markdown
## Production Deployment Checklist

### Environment Preparation
- [ ] Production environment configured
- [ ] Production API key obtained
- [ ] Environment variables set correctly
- [ ] Configuration files updated for production
- [ ] Logging configured appropriately

### Code Review
- [ ] All code reviewed by peer
- [ ] No hardcoded credentials
- [ ] No debug print statements
- [ ] Error handling comprehensive
- [ ] Rate limiting implemented

### Testing
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] End-to-end workflow tested
- [ ] Error scenarios tested
- [ ] Rate limiting tested
- [ ] Timeout handling tested

### Security Review
- [ ] API keys secure
- [ ] Secrets not in version control
- [ ] HTTPS used for all communications
- [ ] Webhook signature verification enabled
- [ ] Input validation implemented
- [ ] SQL injection prevention (if applicable)
- [ ] XSS prevention (if applicable)

### Monitoring Setup
- [ ] Logging configured
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Performance monitoring enabled
- [ ] Alerting configured
- [ ] Dashboard created

### Rate Limiting
- [ ] Rate limiter implemented
- [ ] Exponential backoff configured
- [ ] 429 error handling tested
- [ ] Rate limit monitoring in place

### Webhook Configuration
- [ ] Webhook endpoint deployed
- [ ] HTTPS certificate valid
- [ ] Signature verification working
- [ ] Event handlers implemented
- [ ] Idempotency handling added
- [ ] Webhook subscriptions created

### Documentation
- [ ] Deployment guide updated
- [ ] API documentation current
- [ ] Runbook created
- [ ] Troubleshooting guide available
- [ ] Architecture diagram updated

### Backup & Recovery
- [ ] Backup strategy defined
- [ ] Recovery procedures documented
- [ ] Rollback plan prepared
- [ ] Data retention policy defined

### Performance
- [ ] Load testing completed
- [ ] Response time acceptable
- [ ] Resource usage monitored
- [ ] Scalability plan defined

### Compliance
- [ ] Data handling compliant with regulations
- [ ] Privacy policy reviewed
- [ ] Terms of service reviewed
- [ ] Audit trail configured

### Launch
- [ ] Deployment window scheduled
- [ ] Team notified
- [ ] Support team briefed
- [ ] Rollback plan ready
- [ ] Post-deployment monitoring plan

### Post-Deployment
- [ ] Smoke tests passed
- [ ] Production monitoring active
- [ ] Error rates normal
- [ ] Performance metrics captured
- [ ] User feedback collected
```

---

### Reference Documentation Structure

The skill should include the following detailed reference documentation:

#### Document 1: endpoints-reference.md

**Purpose:** Complete API endpoint reference

**Structure:**
```markdown
# PandaDoc API Endpoints Reference

## Overview
- API Version
- Base URL
- Authentication

## Documents API

### Create Document
- Endpoint
- Method
- Headers
- Request Body
- Response
- Status Codes
- Examples
- Notes

### List Documents
[Same structure]

### Send Document
[Same structure]

[Continue for all endpoints...]

## Templates API
[Same structure per endpoint]

## Contacts API
[Same structure per endpoint]

## Error Reference
- Error codes
- Error messages
- Resolution steps
```

#### Document 2: workflows.md

**Purpose:** Common workflow patterns and best practices

**Structure:**
```markdown
# PandaDoc Workflows

## Document Lifecycle Workflows

### Standard Proposal Workflow
- Steps
- Code examples
- Error handling
- Best practices

### Approval Workflow
[Same structure]

### Bulk Document Creation
[Same structure]

## Advanced Workflows

### Webhook Integration
[Same structure]

### CRM Integration
[Same structure]
```

#### Document 3: troubleshooting.md

**Purpose:** Common issues and solutions

**Structure:**
```markdown
# Troubleshooting Guide

## Authentication Issues

### Issue: 401 Unauthorized
- Symptoms
- Causes
- Solutions
- Prevention

## Document Creation Issues

### Issue: 404 Document Not Found
[Same structure]

### Issue: 429 Rate Limit Exceeded
[Same structure]

## Performance Issues
[Same structure]
```

#### Document 4: field-mapping-guide.md

**Purpose:** Guide to field mapping and data transformation

**Structure:**
```markdown
# Field Mapping Guide

## Understanding Field Types
- Text fields
- Signature fields
- Date fields
- Currency fields

## Merge Fields
- System merge fields
- Custom merge fields
- Best practices

## Field Mapping Patterns
- CRM to PandaDoc
- Database to PandaDoc
- Form to PandaDoc

## Validation Rules
- Required fields
- Format validation
- Business rules
```

#### Document 5: webhook-integration-guide.md

**Purpose:** Complete webhook setup and handling guide

**Structure:**
```markdown
# Webhook Integration Guide

## Overview
- What are webhooks
- Benefits
- Use cases

## Setup
- Creating subscriptions
- Configuring endpoints
- Security

## Event Handling
- Event types
- Payload structure
- Processing events

## Security
- Signature verification
- HTTPS requirements
- Replay protection

## Testing
- Testing tools
- Simulating events
- Debugging

## Production Checklist
```

---

## Summary

This analysis and design document provides:

1. **Comprehensive API Analysis:**
   - Authentication patterns
   - Request/response structures
   - Core workflows
   - Best practices
   - Real code examples

2. **Complete Component Design:**
   - 7 helper scripts with detailed specifications
   - 5 configuration templates
   - 6 critical guardrails
   - 3 comprehensive checklists
   - 5 reference documentation outlines

3. **Production-Ready Patterns:**
   - Error handling strategies
   - Rate limiting implementation
   - Async processing patterns
   - Security best practices
   - Monitoring and logging

**Next Steps:**
1. Generate helper scripts from specifications
2. Create configuration templates
3. Implement guardrail functions
4. Write reference documentation
5. Create example workflows
6. Set up testing framework

**Key Success Factors:**
- Always poll for document.draft status before operations
- Implement rate limiting (10 req/min in sandbox)
- Use exponential backoff for error recovery
- Validate inputs before API calls
- Comprehensive logging and monitoring
- Security-first approach to credentials
