# PandaDoc API Endpoints Reference

**Document Version:** 1.0
**Last Updated:** 2024-11-11
**API Version:** v1
**Base URL:** https://api.pandadoc.com/public/v1

---

## Table of Contents

1. [Authentication](#authentication)
2. [Documents API](#documents-api)
3. [Templates API](#templates-api)
4. [Contacts API](#contacts-api)
5. [Webhooks API](#webhooks-api)
6. [Error Reference](#error-reference)

---

## Authentication

All PandaDoc API requests require authentication using one of two methods:

### API Key Authentication

**Method:** Include API key in Authorization header

```http
GET /documents HTTP/1.1
Host: api.pandadoc.com
Authorization: API-Key YOUR_API_KEY
Content-Type: application/json
```

**Example:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/documents \
  -H "Authorization: API-Key sk_live_1234567890abcdef" \
  -H "Content-Type: application/json"
```

### OAuth 2.0 Authentication

**Method:** Use Bearer token in Authorization header

```http
GET /documents HTTP/1.1
Host: api.pandadoc.com
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

---

## Documents API

### Create Document

Create a new document from a template with pre-filled data.

**Endpoint:** `POST /documents`

**Request Headers:**
```http
Authorization: API-Key YOUR_API_KEY
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Sales Proposal - Acme Corp",
  "template_uuid": "abc123-def456-ghi789",
  "recipients": [
    {
      "email": "john@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "Client"
    },
    {
      "email": "sales@mycompany.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "Manager",
      "signing_order": 1
    }
  ],
  "fields": {
    "Company Name": "Acme Corporation",
    "Proposal Amount": "$50,000",
    "Effective Date": "2024-01-15",
    "Discount Percentage": "10%"
  },
  "tokens": [
    {
      "name": "Company.Address",
      "value": "123 Main St, Austin, TX 78701"
    }
  ],
  "metadata": {
    "opportunity_id": "opp_12345",
    "sales_rep": "Jane Smith"
  },
  "tags": ["proposal", "sales", "2024-q1"]
}
```

**Response (201 Created):**
```json
{
  "id": "doc_8e6f8e6f8e6f8e6f8e6f8e6f",
  "name": "Sales Proposal - Acme Corp",
  "status": "document.uploaded",
  "template_uuid": "abc123-def456-ghi789",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z",
  "recipients": [
    {
      "id": "r_1234567890",
      "email": "john@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "Client",
      "signing_order": 2,
      "status": "waiting"
    },
    {
      "id": "r_0987654321",
      "email": "sales@mycompany.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "role": "Manager",
      "signing_order": 1,
      "status": "waiting"
    }
  ],
  "fields": {
    "Company Name": "Acme Corporation",
    "Proposal Amount": "$50,000",
    "Effective Date": "2024-01-15",
    "Discount Percentage": "10%"
  }
}
```

**Status Codes:**
- `201 Created` - Document created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Template not found
- `429 Too Many Requests` - Rate limit exceeded

**Key Points:**
- Document creation is asynchronous - initial status is `document.uploaded`
- You MUST poll for `document.draft` status before sending
- See [Status Polling Pattern](#status-polling-pattern) for polling example

---

### List Documents

List all documents with optional filtering and pagination.

**Endpoint:** `GET /documents`

**Query Parameters:**
```
count=100              # Number of results per page (max 100, default 50)
page=1                 # Page number (default 1)
status=0               # Filter by status code (optional)
order_by=date_created  # Sort field (date_created, date_modified, name)
order=desc             # Sort order (asc, desc)
tag=proposal           # Filter by tag (optional, can use multiple)
```

**Example Request:**
```bash
curl -X GET "https://api.pandadoc.com/public/v1/documents?count=50&page=1&status=0&order_by=date_created" \
  -H "Authorization: API-Key YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "doc_8e6f8e6f8e6f8e6f8e6f8e6f",
      "name": "Sales Proposal - Acme Corp",
      "status": "document.draft",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:05:00Z",
      "template_uuid": "abc123-def456-ghi789",
      "tag": ["proposal", "sales"]
    }
  ],
  "count": 1,
  "next": "https://api.pandadoc.com/public/v1/documents?page=2",
  "previous": null
}
```

**Status Codes:**
- `200 OK` - List retrieved successfully
- `401 Unauthorized` - Invalid API key

---

### Get Document

Get details for a specific document.

**Endpoint:** `GET /documents/{id}`

**Path Parameters:**
```
id - Document ID (required)
```

**Example Request:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/documents/doc_8e6f8e6f8e6f8e6f8e6f8e6f \
  -H "Authorization: API-Key YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "id": "doc_8e6f8e6f8e6f8e6f8e6f8e6f",
  "name": "Sales Proposal - Acme Corp",
  "status": "document.draft",
  "template_uuid": "abc123-def456-ghi789",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:05:00Z",
  "recipients": [
    {
      "id": "r_1234567890",
      "email": "john@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "Client",
      "status": "waiting"
    }
  ],
  "fields": {
    "Company Name": "Acme Corporation",
    "Proposal Amount": "$50,000",
    "Effective Date": "2024-01-15"
  }
}
```

**Status Codes:**
- `200 OK` - Document retrieved
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Document not found

---

### Send Document

Send a document to recipients.

**Endpoint:** `POST /documents/{id}/send`

**Path Parameters:**
```
id - Document ID (required)
```

**Request Body:**
```json
{
  "subject": "Sales Proposal for Your Review",
  "message": "Please review the attached proposal and sign if you agree to the terms.",
  "silent": false,
  "forwarding_settings": {
    "forwarding_allowed": true
  }
}
```

**Response (200 OK):**
```json
{
  "id": "doc_8e6f8e6f8e6f8e6f8e6f8e6f",
  "status": "document.sent",
  "sent_at": "2024-01-15T14:30:00Z",
  "recipients": [
    {
      "email": "john@acme.com",
      "status": "sent",
      "sent_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK` - Document sent successfully
- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Document not found or not in draft status
- `409 Conflict` - Document not in correct state for sending

**Prerequisites:**
- Document must be in `document.draft` status
- At least one recipient with valid email required
- All required fields must be populated

---

### Download Document

Download a completed document as PDF.

**Endpoint:** `GET /documents/{id}/download`

**Path Parameters:**
```
id - Document ID (required)
```

**Query Parameters:**
```
watermark=false  # Add watermark (optional)
```

**Example Request:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/documents/doc_8e6f8e6f/download \
  -H "Authorization: API-Key YOUR_API_KEY" \
  -o downloaded_document.pdf
```

**Response (200 OK):**
- Binary PDF file

**Status Codes:**
- `200 OK` - Document downloaded
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Document not found
- `409 Conflict` - Document not completed yet

**Prerequisites:**
- Document must be in `document.completed` or `document.approved` status

---

### Delete Document

Delete a document.

**Endpoint:** `DELETE /documents/{id}`

**Example Request:**
```bash
curl -X DELETE https://api.pandadoc.com/public/v1/documents/doc_8e6f8e6f \
  -H "Authorization: API-Key YOUR_API_KEY"
```

**Response (204 No Content):**
- No response body

**Status Codes:**
- `204 No Content` - Document deleted
- `401 Unauthorized` - Invalid API key
- `404 Not Found` - Document not found

---

## Templates API

### List Templates

Get all available templates in your account.

**Endpoint:** `GET /templates`

**Query Parameters:**
```
count=50   # Results per page
page=1     # Page number
```

**Example Request:**
```bash
curl -X GET https://api.pandadoc.com/public/v1/templates \
  -H "Authorization: API-Key YOUR_API_KEY"
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "abc123-def456-ghi789",
      "name": "Standard Sales Proposal",
      "created_at": "2023-06-01T10:00:00Z",
      "fields": [
        {
          "name": "Company Name",
          "type": "text"
        },
        {
          "name": "Proposal Amount",
          "type": "text"
        }
      ]
    }
  ],
  "count": 1,
  "next": null,
  "previous": null
}
```

---

### Get Template Details

Get detailed information about a specific template.

**Endpoint:** `GET /templates/{uuid}`

**Response (200 OK):**
```json
{
  "id": "abc123-def456-ghi789",
  "name": "Standard Sales Proposal",
  "created_at": "2023-06-01T10:00:00Z",
  "fields": [
    {
      "name": "Company Name",
      "type": "text",
      "placeholder": "e.g., Acme Corp"
    },
    {
      "name": "Proposal Amount",
      "type": "text"
    }
  ],
  "roles": ["Client", "Manager"],
  "tokens": [
    {
      "name": "Company.Address",
      "description": "Company mailing address"
    }
  ]
}
```

---

## Contacts API

### List Contacts

Get all contacts in your account.

**Endpoint:** `GET /contacts`

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "c_1234567890",
      "email": "john@acme.com",
      "first_name": "John",
      "last_name": "Doe",
      "company_name": "Acme Corp",
      "phone": "+1-555-0123"
    }
  ],
  "count": 1
}
```

---

### Create Contact

Create a new contact.

**Endpoint:** `POST /contacts`

**Request Body:**
```json
{
  "email": "john@acme.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp",
  "phone": "+1-555-0123"
}
```

**Response (201 Created):**
```json
{
  "id": "c_1234567890",
  "email": "john@acme.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp"
}
```

---

## Webhooks API

### Create Webhook Subscription

Register a webhook to receive real-time notifications.

**Endpoint:** `POST /webhook-subscriptions`

**Request Body:**
```json
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

**Response (201 Created):**
```json
{
  "id": "ws_1234567890",
  "name": "Document Status Tracker",
  "url": "https://your-server.com/webhooks/pandadoc",
  "triggers": ["document_state_changed"],
  "active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

---

### List Webhook Subscriptions

Get all active webhooks.

**Endpoint:** `GET /webhook-subscriptions`

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "ws_1234567890",
      "name": "Document Status Tracker",
      "url": "https://your-server.com/webhooks/pandadoc",
      "active": true
    }
  ]
}
```

---

## Status Codes Reference

| Code | Meaning | Cause | Solution |
|------|---------|-------|----------|
| 200 | OK | Request successful | Process response |
| 201 | Created | Resource created | Save resource ID |
| 204 | No Content | Success (no body) | Operation complete |
| 400 | Bad Request | Invalid parameters | Check request format |
| 401 | Unauthorized | Invalid API key | Verify credentials |
| 404 | Not Found | Resource doesn't exist | Verify IDs/UUIDs |
| 409 | Conflict | Invalid state operation | Check document status |
| 429 | Rate Limit | Too many requests | Implement backoff |
| 500+ | Server Error | PandaDoc server issue | Retry with backoff |

---

## Status Polling Pattern

Document creation is asynchronous. You must poll for `document.draft` status before sending.

```python
import time
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.pandadoc.com/public/v1"

def create_and_send_document(template_uuid, recipients, fields):
    # Step 1: Create document
    response = requests.post(
        f"{BASE_URL}/documents",
        headers={"Authorization": f"API-Key {API_KEY}", "Content-Type": "application/json"},
        json={
            "name": "Proposal",
            "template_uuid": template_uuid,
            "recipients": recipients,
            "fields": fields
        }
    )
    document = response.json()
    document_id = document['id']
    print(f"Document created: {document_id} (status: {document['status']})")

    # Step 2: Poll for draft status (MANDATORY)
    for attempt in range(30):  # Max 30 attempts = 60 seconds
        time.sleep(2)

        status_response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers={"Authorization": f"API-Key {API_KEY}"}
        )
        status_data = status_response.json()
        print(f"Attempt {attempt + 1}: Status = {status_data['status']}")

        if status_data['status'] == 'document.draft':
            print("Document ready!")
            break

        if status_data['status'].startswith('document.error'):
            raise Exception(f"Document creation error: {status_data['status']}")
    else:
        raise TimeoutError("Document not ready after 60 seconds")

    # Step 3: Send document
    send_response = requests.post(
        f"{BASE_URL}/documents/{document_id}/send",
        headers={"Authorization": f"API-Key {API_KEY}", "Content-Type": "application/json"},
        json={
            "subject": "Proposal for Review",
            "message": "Please review and sign",
            "silent": False
        }
    )
    print("Document sent successfully!")
    return document_id

# Usage
create_and_send_document(
    template_uuid="your_template_id",
    recipients=[
        {"email": "client@acme.com", "role": "Client"}
    ],
    fields={"Company Name": "Acme Corp"}
)
```

---

## Error Response Examples

### 400 Bad Request
```json
{
  "type": "validation_error",
  "detail": "Invalid field value",
  "errors": [
    {
      "field": "recipients",
      "message": "At least one recipient is required"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "type": "authentication_error",
  "detail": "Invalid API key provided"
}
```

### 404 Not Found
```json
{
  "type": "not_found_error",
  "detail": "Document not found"
}
```

### 429 Rate Limit
```json
{
  "type": "rate_limit_error",
  "detail": "Too many requests",
  "retry_after": 60
}
```

---

## Rate Limiting

**Limits:**
- Sandbox: 10 requests per minute
- Production: Higher limits (contact PandaDoc)

**Headers (if provided):**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640000000
```

**Backoff Strategy:**
```python
import time

def handle_rate_limit(func, max_retries=3):
    base_delay = 60

    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            print(f"Rate limited. Waiting {delay}s...")
            time.sleep(delay)
```

---

## Common API Patterns

### Async Pattern
1. Create document (returns `document.uploaded` status)
2. Poll for `document.draft` status
3. Perform operations (send, download, etc.)

### Paginated List Pattern
```python
page = 1
all_results = []

while True:
    response = requests.get(
        f"{BASE_URL}/documents?page={page}&count=100"
    )
    results = response.json()

    all_results.extend(results['results'])

    if results['next'] is None:
        break

    page += 1
```

### Error Handling Pattern
```python
try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Handle rate limit
        wait_time = int(e.response.headers.get('Retry-After', 60))
        time.sleep(wait_time)
    elif e.response.status_code == 401:
        # Handle authentication error
        raise ValueError("Invalid API key")
    else:
        raise
```

---

## Reference Links

- [PandaDoc API Documentation](https://developers.pandadoc.com/reference)
- [Template Management](./field-mapping-guide.md)
- [Webhook Integration](./webhook-integration-guide.md)
- [Troubleshooting Guide](./troubleshooting.md)
