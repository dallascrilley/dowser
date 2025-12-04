# Acuity Scheduling API - Complete Endpoints Reference

**Last Updated:** 2025-11-11
**API Version:** v1
**Base URL:** `https://acuityscheduling.com/api/v1`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Appointments](#appointments)
3. [Availability](#availability)
4. [Clients](#clients)
5. [Appointment Types](#appointment-types)
6. [Calendars](#calendars)
7. [Forms & Fields](#forms--fields)
8. [Labels](#labels)
9. [Webhooks](#webhooks)
10. [Blocks & Certificates](#blocks--certificates)
11. [Orders & Products](#orders--products)
12. [Rate Limiting](#rate-limiting)
13. [Error Codes](#error-codes)

---

## Authentication

All requests require HTTP Basic Authentication using User ID and API Key.

**Format:**
```
Authorization: Basic {base64(userId:apiKey)}
```

**Example:**
```bash
curl -u "12345678:abc123def456xyz789" \
  https://acuityscheduling.com/api/v1/me
```

**Python:**
```python
from requests.auth import HTTPBasicAuth
import requests

session = requests.Session()
session.auth = HTTPBasicAuth("12345678", "abc123def456xyz789")
response = session.get("https://acuityscheduling.com/api/v1/me")
```

---

## Appointments

### GET /appointments - List Appointments

Retrieve appointments with optional filtering and pagination.

**Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| minDate | string | no | Start date (YYYY-MM-DD) | 2025-11-01 |
| maxDate | string | no | End date (YYYY-MM-DD) | 2025-11-30 |
| appointmentTypeID | number | no | Filter by appointment type ID | 12345 |
| calendarID | number | no | Filter by calendar/provider ID | 67890 |
| canceled | boolean | no | Include canceled appointments | false |
| max | number | no | Results per page (max 100) | 100 |
| offset | number | no | Pagination offset | 0 |

**Response:**
```json
[
  {
    "id": 123456789,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "555-0123",
    "datetime": "2025-11-15T14:00:00-0500",
    "endTime": "2025-11-15T15:00:00-0500",
    "appointmentTypeID": 12345,
    "appointmentTypeName": "Consultation",
    "calendarID": 67890,
    "calendarName": "John's Calendar",
    "duration": 60,
    "price": "100.00",
    "priceSold": "100.00",
    "paid": "yes",
    "confirmed": true,
    "canceled": false,
    "timezone": "America/New_York",
    "notes": "Customer notes here",
    "confirmationPageUrl": "https://yourdomain.com/confirm"
  }
]
```

**Examples:**

```bash
# Get all appointments for November
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/appointments?minDate=2025-11-01&maxDate=2025-11-30"

# Get appointments for specific appointment type
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/appointments?appointmentTypeID=12345"

# Paginate through large result sets
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/appointments?max=100&offset=0"
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/appointments?max=100&offset=100"
```

**Python:**
```python
import requests
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

session = requests.Session()
session.auth = HTTPBasicAuth(USER_ID, API_KEY)

# Get appointments for current month
start = datetime.now().replace(day=1)
end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

params = {
    'minDate': start.strftime('%Y-%m-%d'),
    'maxDate': end.strftime('%Y-%m-%d'),
    'max': 100,
    'offset': 0
}

response = session.get(
    'https://acuityscheduling.com/api/v1/appointments',
    params=params
)
appointments = response.json()
```

---

### GET /appointments/{id} - Get Specific Appointment

Retrieve details for a single appointment.

**Parameters:**
- `id` (path, required): Appointment ID

**Response:** Single appointment object (see /appointments response format)

**Example:**
```bash
curl -u $USER_ID:$API_KEY \
  https://acuityscheduling.com/api/v1/appointments/123456789
```

---

### POST /appointments - Create Appointment

Create a new appointment.

**Required Fields:**
- `appointmentTypeID` - ID of appointment type
- `datetime` - ISO 8601 format with timezone
- `firstName` - Client first name
- `lastName` - Client last name
- `email` - Client email address

**Optional Fields:**
- `phone` - Client phone number
- `notes` - Appointment notes
- `fields` - Custom form field data
- `certificate` - Gift certificate code

**Request:**
```json
{
  "appointmentTypeID": 12345,
  "datetime": "2025-11-15T14:00:00-0500",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "555-0123",
  "notes": "Customer notes",
  "fields": [
    {
      "id": 67890,
      "value": "Custom field data"
    }
  ]
}
```

**Response:** Created appointment object with ID

**Example:**
```bash
curl -u $USER_ID:$API_KEY \
  -X POST https://acuityscheduling.com/api/v1/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "appointmentTypeID": 12345,
    "datetime": "2025-11-15T14:00:00-0500",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "555-0123"
  }'
```

**Python:**
```python
appointment_data = {
    "appointmentTypeID": 12345,
    "datetime": "2025-11-15T14:00:00-0500",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "555-0123"
}

response = session.post(
    'https://acuityscheduling.com/api/v1/appointments',
    json=appointment_data
)
appointment = response.json()
print(f"Created appointment: {appointment['id']}")
```

**⚠️ Important:** Always check availability before creating appointments to avoid race conditions.

---

### PUT /appointments/{id} - Update Appointment

Update appointment details (not including datetime).

**Updateable Fields:**
- `firstName`
- `lastName`
- `email`
- `phone`
- `notes`
- Custom fields

**Example:**
```bash
curl -u $USER_ID:$API_KEY \
  -X PUT https://acuityscheduling.com/api/v1/appointments/123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "555-9999",
    "notes": "Updated notes"
  }'
```

---

### PUT /appointments/{id}/reschedule - Reschedule Appointment

Change appointment time.

**Required Fields:**
- `datetime` - New appointment time

**Example:**
```bash
curl -u $USER_ID:$API_KEY \
  -X PUT https://acuityscheduling.com/api/v1/appointments/123456789/reschedule \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "2025-11-20T15:00:00-0500"
  }'
```

**⚠️ Important:** Always verify new time is available before rescheduling.

---

### PUT /appointments/{id}/cancel - Cancel Appointment

Cancel an appointment.

**Optional Fields:**
- `notes` - Cancellation reason

**Example:**
```bash
curl -u $USER_ID:$API_KEY \
  -X PUT https://acuityscheduling.com/api/v1/appointments/123456789/cancel
```

---

### GET /appointments/{id}/payments - Get Appointment Payments

Retrieve payment history for an appointment.

**Response:**
```json
[
  {
    "id": 987654321,
    "amount": "100.00",
    "date": "2025-11-15T14:05:00-0500",
    "method": "credit_card",
    "last4": "4242",
    "status": "success"
  }
]
```

---

## Availability

### GET /availability/dates - Get Available Dates

Get dates with availability for an appointment type.

**Parameters:**

| Parameter | Type | Required |
|-----------|------|----------|
| appointmentTypeID | number | yes |
| month | string | no (YYYY-MM format) |
| calendarID | number | no |

**Response:**
```json
[
  {
    "date": "2025-11-15",
    "status": "available"
  },
  {
    "date": "2025-11-16",
    "status": "available"
  }
]
```

---

### GET /availability/times - Get Available Time Slots

Get specific time slots for a date.

**Parameters:**

| Parameter | Type | Required |
|-----------|------|----------|
| appointmentTypeID | number | yes |
| date | string | yes (YYYY-MM-DD) |
| timezone | string | no (IANA timezone) |
| calendarID | number | no |

**⚠️ Critical:** Always include `timezone` parameter to avoid booking at wrong times.

**Response:**
```json
[
  {
    "time": "2025-11-15T09:00:00-0500"
  },
  {
    "time": "2025-11-15T10:00:00-0500"
  },
  {
    "time": "2025-11-15T14:00:00-0500"
  }
]
```

**Example:**
```bash
# Get availability with timezone (CORRECT)
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/availability/times?appointmentTypeID=12345&date=2025-11-15&timezone=America/New_York"

# Without timezone (WRONG - uses server default)
curl -u $USER_ID:$API_KEY \
  "https://acuityscheduling.com/api/v1/availability/times?appointmentTypeID=12345&date=2025-11-15"
```

---

### GET /availability/classes - Get Class Availability

Get availability for group classes.

**Parameters:**
- `appointmentTypeID` - Class ID
- `month` - Month to check (YYYY-MM)

---

## Clients

### GET /clients - List Clients

Retrieve clients with optional filtering.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| email | string | Filter by email (exact match) |
| firstName | string | Filter by first name |
| lastName | string | Filter by last name |
| phone | string | Filter by phone |
| max | number | Results per page |
| offset | number | Pagination offset |

**Response:**
```json
[
  {
    "id": 987654321,
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "555-0123",
    "address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "notes": "Client notes",
    "timezone": "America/New_York"
  }
]
```

---

### GET /clients/{id} - Get Specific Client

Retrieve single client details.

---

### POST /clients - Create Client

Create a new client.

**Required Fields:**
- `firstName`
- `lastName`
- `email`

**Optional Fields:**
- `phone`
- `address`
- `city`
- `state`
- `zip`
- `notes`

---

### PUT /clients/{id} - Update Client

Update client information.

---

### DELETE /clients/{id} - Delete Client

Delete a client record.

---

## Appointment Types

### GET /appointment-types - List Appointment Types

Get all available appointment types/services.

**Response:**
```json
[
  {
    "id": 12345,
    "name": "Consultation",
    "description": "Initial 30-minute consultation",
    "duration": 30,
    "price": "75.00",
    "displayOptions": {
      "color": "#4472C4"
    }
  }
]
```

**Use Case:** Populate dropdown menus, validate appointment types before booking

**Caching:** Safe to cache for 24 hours (rarely changes)

---

### GET /appointment-types/{id} - Get Specific Type

Get details for single appointment type.

---

## Calendars

### GET /calendars - List Calendars

Get all calendars/staff members.

**Response:**
```json
[
  {
    "id": 67890,
    "name": "John Smith",
    "description": "Senior Consultant",
    "email": "john.smith@yourdomain.com",
    "timezone": "America/New_York",
    "active": true
  }
]
```

**Caching:** Safe to cache for 6 hours

---

## Forms & Fields

### GET /forms - List Forms

Get intake forms configured in Acuity.

**Response:**
```json
[
  {
    "id": 11111,
    "name": "Client Intake",
    "fields": [
      {
        "id": 67890,
        "label": "How did you hear about us?",
        "type": "select",
        "required": true
      }
    ]
  }
]
```

**Use Case:** Get custom field IDs for appointment creation

---

## Labels

### GET /labels - List Labels

Get appointment labels/tags configured in Acuity.

**Response:**
```json
[
  {
    "id": 123,
    "name": "VIP Client"
  },
  {
    "id": 456,
    "name": "Priority"
  }
]
```

---

## Webhooks

### GET /webhooks - List Webhooks

Get all configured webhooks.

**Response:**
```json
[
  {
    "id": 999,
    "url": "https://yourdomain.com/webhooks/acuity",
    "events": ["scheduled", "canceled"],
    "enabled": true,
    "created_at": "2025-11-01T10:00:00Z"
  }
]
```

---

### POST /webhooks - Create Webhook

Register a new webhook.

**Request:**
```json
{
  "url": "https://yourdomain.com/webhooks/acuity",
  "events": ["scheduled", "rescheduled", "canceled", "changed"]
}
```

---

### DELETE /webhooks/{id} - Delete Webhook

Remove a webhook.

---

## Blocks & Certificates

### GET /blocks - List Time Blocks

Get scheduled time blocks/availability blocks.

---

### POST /blocks - Create Block

Block off time in calendar.

---

### GET /certificates - List Gift Certificates

Get gift certificates.

---

### POST /certificates - Create Certificate

Create a new gift certificate.

---

## Orders & Products

### GET /orders - List Orders

Get product orders.

---

### GET /products - List Products

Get products/services available for purchase.

---

## Account

### GET /me - Get Account Info

Get current account information.

**Response:**
```json
{
  "id": "12345678",
  "name": "John Smith",
  "email": "john@yourdomain.com",
  "timezone": "America/New_York",
  "businessName": "Smith Consulting",
  "businessPhone": "555-0000",
  "website": "https://yourdomain.com"
}
```

**Use Case:** Verify API authentication, get account details

---

## Rate Limiting

**Limits:**
- 10 requests per second (sustained)
- 20 concurrent connections
- No documented daily limit

**Rate Limit Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1699123456 (Unix timestamp)
```

**Response on Rate Limit (429):**
```json
{
  "status_code": 429,
  "error": "too_many_requests",
  "message": "Rate limit reached. Limit 10req/s and 20 concurrent connections."
}
```

**Handling Rate Limits:**
```python
import time

def make_request_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        response = session.get(url)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
            wait_time = 2 ** attempt
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        else:
            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

---

## Error Codes

**Common HTTP Status Codes:**

| Code | Meaning | Cause | Retry? |
|------|---------|-------|--------|
| **200** | OK | Request successful | N/A |
| **201** | Created | Resource created | N/A |
| **400** | Bad Request | Invalid parameters, missing required fields | ❌ No |
| **401** | Unauthorized | Invalid credentials, expired key | ❌ No |
| **403** | Forbidden | Insufficient permissions | ❌ No |
| **404** | Not Found | Resource doesn't exist | ❌ No |
| **429** | Too Many Requests | Rate limit exceeded | ✅ Yes (exponential backoff) |
| **500** | Internal Server Error | Server error | ✅ Yes (with backoff) |
| **503** | Service Unavailable | Maintenance/overload | ✅ Yes (with backoff) |

**Error Response Format:**
```json
{
  "status_code": 400,
  "error": "bad_request",
  "message": "Invalid appointment type ID"
}
```

---

## See Also

- [Authentication Guide](authentication-guide.md) - Detailed credential setup and security
- [Webhook Integration Guide](webhook-integration-guide.md) - Real-time event handling
- [Error Handling Guide](error-handling-guide.md) - Comprehensive error strategies
- [Workflows Reference](workflows-reference.md) - Complete usage examples
- [Official Acuity API Docs](https://developer.acuityscheduling.com)

---

**Last Updated:** 2025-11-11
**Generated with Claude Code**
