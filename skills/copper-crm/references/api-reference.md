# Copper CRM API Reference

Complete API reference for the Copper CRM Developer API v1.

## Table of Contents

- [Base URL & Authentication](#base-url--authentication)
- [Endpoint Reference](#endpoint-reference)
- [Common Parameters](#common-parameters)
- [Entity Schemas](#entity-schemas)
- [Request/Response Examples](#requestresponse-examples)
- [Status Codes](#status-codes)
- [Quick Reference Cards](#quick-reference-cards)

---

## Base URL & Authentication

### Base URL

```
https://api.copper.com/developer_api/v1
```

### Authentication Methods

Copper supports two authentication methods:

#### 1. API Key Authentication (Recommended for server-to-server)

**Required Headers:**
```http
X-PW-AccessToken: YOUR_API_KEY
X-PW-Application: developer_api
X-PW-UserEmail: YOUR_EMAIL@EXAMPLE.COM
Content-Type: application/json
```

**How to Get API Key:**
1. Log into Copper web app
2. Navigate to Settings > Integrations > API Keys
3. Click GENERATE API KEY
4. Label the key and save it securely

**Example Request:**
```bash
curl -X GET "https://api.copper.com/developer_api/v1/account" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

#### 2. OAuth 2.0 (Recommended for user-facing apps)

**Authorization Flow:**
1. Redirect user to authorization endpoint
2. User authenticates and grants permission
3. Exchange authorization code for access token
4. Use access token in Authorization header

**Authorization Endpoint:**
```
GET https://app.copper.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=developer/v1/all&state={state}
```

**Token Endpoint:**
```
POST https://app.copper.com/oauth/token
```

**Token Request:**
```bash
curl -X POST "https://app.copper.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code={authorization_code}" \
  -d "redirect_uri={redirect_uri}" \
  -d "client_id={client_id}" \
  -d "client_secret={client_secret}"
```

**Using Access Token:**
```bash
curl -H "Authorization: Bearer {access_token}" \
  https://api.copper.com/developer_api/v1/account
```

**Note:** OAuth access tokens do not expire and do not need to be refreshed.

---

## Endpoint Reference

### Core Endpoints

All CRUD operations follow a consistent pattern across entity types.

#### Account & Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/account` | Fetch account details | Required |
| GET | `/users` | List all users | Required |
| GET | `/users/{id}` | Fetch user by ID | Required |

#### Leads

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/leads` | Create new lead | Required |
| GET | `/leads/{id}` | Fetch lead by ID | Required |
| PUT | `/leads/{id}` | Update lead | Required |
| DELETE | `/leads/{id}` | Delete lead | Required |
| POST | `/leads/search` | Search/list leads | Required |
| POST | `/leads/{id}/convert` | Convert lead to person/company/opportunity | Required |
| GET | `/leads/{id}/activities` | Get lead's activities | Required |

#### People (Contacts)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/people` | Create new person | Required |
| GET | `/people/{id}` | Fetch person by ID | Required |
| PUT | `/people/{id}` | Update person | Required |
| DELETE | `/people/{id}` | Delete person | Required |
| POST | `/people/search` | Search/list people | Required |
| GET | `/people/{id}/activities` | Get person's activities | Required |
| POST | `/people/fetch_by_email` | Fetch person by email | Required |

#### Companies

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/companies` | Create new company | Required |
| GET | `/companies/{id}` | Fetch company by ID | Required |
| PUT | `/companies/{id}` | Update company | Required |
| DELETE | `/companies/{id}` | Delete company | Required |
| POST | `/companies/search` | Search/list companies | Required |
| GET | `/companies/{id}/activities` | Get company's activities | Required |

#### Opportunities (Deals)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/opportunities` | Create new opportunity | Required |
| GET | `/opportunities/{id}` | Fetch opportunity by ID | Required |
| PUT | `/opportunities/{id}` | Update opportunity | Required |
| DELETE | `/opportunities/{id}` | Delete opportunity | Required |
| POST | `/opportunities/search` | Search/list opportunities | Required |

#### Activities

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/activities` | Create new activity | Required |
| GET | `/activities/{id}` | Fetch activity by ID | Required |
| PUT | `/activities/{id}` | Update activity | Required |
| DELETE | `/activities/{id}` | Delete activity | Required |
| POST | `/activities/search` | Search/list activities | Required |

#### Tasks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/tasks` | Create new task | Required |
| GET | `/tasks/{id}` | Fetch task by ID | Required |
| PUT | `/tasks/{id}` | Update task | Required |
| DELETE | `/tasks/{id}` | Delete task | Required |
| POST | `/tasks/search` | Search/list tasks | Required |

#### Projects

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/projects` | Create new project | Required |
| GET | `/projects/{id}` | Fetch project by ID | Required |
| PUT | `/projects/{id}` | Update project | Required |
| DELETE | `/projects/{id}` | Delete project | Required |
| POST | `/projects/search` | Search/list projects | Required |

#### Custom Fields

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/custom_field_definitions` | List all custom field definitions | Required |

#### Pipelines

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/pipelines` | List all pipelines | Required |
| GET | `/pipeline_stages` | List all pipeline stages | Required |

#### Webhooks

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/webhooks` | Create webhook subscription | Required |
| GET | `/webhooks` | List all webhooks | Required |
| GET | `/webhooks/{id}` | Fetch webhook by ID | Required |
| PUT | `/webhooks/{id}` | Update webhook | Required |
| DELETE | `/webhooks/{id}` | Delete webhook | Required |

---

## Common Parameters

### Pagination Parameters

Used in all search endpoints (`POST /{entity}/search`):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_number` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 20 | Records per page (max: 200) |
| `sort_by` | string | - | Field to sort by (e.g., "date_modified", "name") |
| `sort_direction` | string | "asc" | Sort direction ("asc" or "desc") |

**Pagination Limits:**
- Default page size: 20 records
- Maximum page size: 200 records
- Maximum total records: First 100,000 matching records only
- Total count header: `X-PW-TOTAL` (shows upper bound of total records)

**Example:**
```json
{
  "page_number": 1,
  "page_size": 200,
  "sort_by": "date_modified",
  "sort_direction": "desc"
}
```

### Common Search Filters

Available across most entity search endpoints:

| Filter | Type | Description |
|--------|------|-------------|
| `assignee_ids` | array[integer] | Filter by assigned user IDs |
| `tags` | array[string] | Filter by tags |
| `minimum_created_date` | integer | Unix timestamp (records created after) |
| `maximum_created_date` | integer | Unix timestamp (records created before) |
| `minimum_modified_date` | integer | Unix timestamp (records modified after) |
| `maximum_modified_date` | integer | Unix timestamp (records modified before) |
| `custom_fields` | array[object] | Filter by custom field values |

**Custom Field Filter Example:**
```json
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": "Enterprise"
    }
  ]
}
```

### Entity-Specific Filters

#### Lead Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `status_ids` | array[integer] | Filter by lead status IDs |
| `customer_source_ids` | array[integer] | Filter by lead source IDs |

#### People Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `company_ids` | array[integer] | Filter by company IDs |
| `contact_type_ids` | array[integer] | Filter by contact type IDs |

#### Company Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `contact_type_ids` | array[integer] | Filter by contact type IDs |

#### Opportunity Search Filters

| Filter | Type | Description |
|--------|------|-------------|
| `pipeline_ids` | array[integer] | Filter by pipeline IDs |
| `pipeline_stage_ids` | array[integer] | Filter by pipeline stage IDs |
| `statuses` | array[string] | Filter by status ("Open", "Won", "Lost", "Abandoned") |
| `minimum_monetary_value` | integer | Minimum deal value |
| `maximum_monetary_value` | integer | Maximum deal value |

### Rate Limiting

- **Standard APIs:** 180 requests per minute (rolling window)
- **Bulk APIs:** 3 requests per second
- **Response on exceed:** HTTP 429 (Too Many Requests)

**Best Practice:** Implement exponential backoff for 429 errors.

---

## Entity Schemas

### Lead

**Core Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Unique lead ID |
| `name` | string | Yes | Lead name |
| `email` | object/string | No | Email address |
| `title` | string | No | Job title |
| `company_name` | string | No | Company name |
| `status` | string | No | Lead status |
| `assignee_id` | integer | No | Assigned user ID |
| `customer_source_id` | integer | No | Lead source ID |
| `address` | object | No | Mailing address |
| `phone_numbers` | array[object] | No | Phone numbers |
| `socials` | array[object] | No | Social media profiles |
| `websites` | array[object] | No | Website URLs |
| `tags` | array[string] | No | Tag strings |
| `custom_fields` | array[object] | No | Custom field values |
| `converted_contact_id` | integer | No | Converted person ID |
| `converted_to_company_id` | integer | No | Converted company ID |
| `converted_opportunity_id` | integer | No | Converted opportunity ID |
| `converted_at` | integer | No | Conversion timestamp (Unix) |
| `date_created` | integer | Auto | Creation timestamp (Unix) |
| `date_modified` | integer | Auto | Modification timestamp (Unix) |

**Email Object:**
```json
{
  "email": "contact@example.com",
  "category": "work"
}
```

**Phone Number Object:**
```json
{
  "number": "415-555-1234",
  "category": "mobile"
}
```

**Address Object:**
```json
{
  "street": "123 Main St",
  "city": "San Francisco",
  "state": "CA",
  "postal_code": "94105",
  "country": "US"
}
```

### Person (Contact)

**Core Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Unique person ID |
| `name` | string | Yes | Full name |
| `email` | string | No | Primary email (deprecated, use emails array) |
| `emails` | array[object] | No | Email addresses |
| `title` | string | No | Job title |
| `company_id` | integer | No | Associated company ID |
| `assignee_id` | integer | No | Assigned user ID |
| `contact_type_id` | integer | No | Contact type ID |
| `phone_numbers` | array[object] | No | Phone numbers |
| `address` | object | No | Mailing address |
| `websites` | array[object] | No | Website URLs |
| `socials` | array[object] | No | Social media profiles |
| `tags` | array[string] | No | Tag strings |
| `custom_fields` | array[object] | No | Custom field values |
| `date_created` | integer | Auto | Creation timestamp (Unix) |
| `date_modified` | integer | Auto | Modification timestamp (Unix) |

**Unique Constraints:**
- Email address must be unique across all people

### Company

**Core Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Unique company ID |
| `name` | string | Yes | Company name |
| `email_domain` | string | No | Primary email domain |
| `assignee_id` | integer | No | Assigned user ID |
| `primary_contact_id` | integer | No | Primary contact person ID |
| `contact_type_id` | integer | No | Contact type classification |
| `address` | object | No | Company address |
| `phone_numbers` | array[object] | No | Phone numbers |
| `websites` | array[object] | No | Website URLs |
| `socials` | array[object] | No | Social media profiles |
| `tags` | array[string] | No | Tag strings |
| `custom_fields` | array[object] | No | Custom field values |
| `date_created` | integer | Auto | Creation timestamp (Unix) |
| `date_modified` | integer | Auto | Modification timestamp (Unix) |

**Unique Constraints:**
- Email domain must be unique across all companies

### Opportunity (Deal)

**Core Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Unique opportunity ID |
| `name` | string | Yes | Opportunity name |
| `status` | string | No | Status ("Open", "Won", "Lost", "Abandoned") |
| `company_id` | integer | No | Associated company ID |
| `primary_contact_id` | integer | No | Primary contact person ID |
| `assignee_id` | integer | No | Assigned user ID |
| `pipeline_id` | integer | No | Pipeline ID |
| `pipeline_stage_id` | integer | No | Pipeline stage ID |
| `customer_source_id` | integer | No | Lead source ID |
| `monetary_value` | float | No | Deal value |
| `close_date` | string | No | Expected close date (MM/DD/YYYY) |
| `win_probability` | integer | No | Win probability % (0-100) |
| `priority` | string | No | Priority level |
| `tags` | array[string] | No | Tag strings |
| `custom_fields` | array[object] | No | Custom field values |
| `date_created` | integer | Auto | Creation timestamp (Unix) |
| `date_modified` | integer | Auto | Modification timestamp (Unix) |

### Activity

**Core Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Auto | Unique activity ID |
| `parent` | object | Yes | Parent entity (lead/person/company/opportunity) |
| `type` | object | Yes | Activity type |
| `details` | string | No | Activity details/notes |
| `user_id` | integer | Auto | User who created the activity |
| `activity_date` | integer | Auto | Activity timestamp (Unix) |
| `date_created` | integer | Auto | Creation timestamp (Unix) |

**Parent Object:**
```json
{
  "type": "person",
  "id": 27140359
}
```

**Type Object:**
```json
{
  "category": "user",
  "id": 0
}
```

**Activity Categories:**
- `user`: User-created note
- `system`: System-generated activity
- `email`: Email activity
- `call`: Phone call activity

### Custom Field

**Structure:**
```json
{
  "custom_field_definition_id": 12345,
  "value": "custom value"
}
```

**Supported Custom Field Types:**
- String
- Number
- Date
- Dropdown
- Multi-select
- Checkbox
- URL

---

## Request/Response Examples

### Leads

#### Create Lead

**Request:**
```bash
POST /developer_api/v1/leads
```

```json
{
  "name": "John Doe",
  "email": {
    "email": "john.doe@example.com",
    "category": "work"
  },
  "phone_numbers": [
    {
      "number": "415-555-1234",
      "category": "mobile"
    }
  ],
  "company_name": "Acme Corp",
  "title": "VP of Sales",
  "tags": ["inbound", "high-priority"]
}
```

**Response (200 OK):**
```json
{
  "id": 13244480,
  "name": "John Doe",
  "first_name": "John",
  "last_name": "Doe",
  "email": {
    "email": "john.doe@example.com",
    "category": "work"
  },
  "phone_numbers": [
    {
      "number": "415-555-1234",
      "category": "mobile"
    }
  ],
  "company_name": "Acme Corp",
  "title": "VP of Sales",
  "status": "New",
  "tags": ["inbound", "high-priority"],
  "date_created": 1502158444,
  "date_modified": 1502158444
}
```

#### Search Leads

**Request:**
```bash
POST /developer_api/v1/leads/search
```

```json
{
  "page_size": 50,
  "page_number": 1,
  "sort_by": "date_modified",
  "sort_direction": "desc",
  "status_ids": [208231],
  "assignee_ids": [137658],
  "minimum_created_date": 1609459200
}
```

**Response (200 OK):**
```json
[
  {
    "id": 9150547,
    "name": "John Doe",
    "email": {
      "email": "john.doe@example.com",
      "category": "work"
    },
    "status": "New",
    "assignee_id": 137658,
    "company_name": "Acme Corp",
    "date_created": 1490045162,
    "date_modified": 1490045162
  },
  {
    "id": 9150548,
    "name": "Jane Smith",
    "email": {
      "email": "jane.smith@example.com",
      "category": "work"
    },
    "status": "Qualified",
    "assignee_id": 137658,
    "company_name": "TechCo",
    "date_created": 1490045200,
    "date_modified": 1490045300
  }
]
```

**Response Headers:**
```
X-PW-TOTAL: 125
```

#### Get Lead by ID

**Request:**
```bash
GET /developer_api/v1/leads/13244480
```

**Response (200 OK):**
```json
{
  "id": 13244480,
  "name": "John Doe",
  "email": {
    "email": "john.doe@example.com",
    "category": "work"
  },
  "company_name": "Acme Corp",
  "title": "VP of Sales",
  "status": "New",
  "date_created": 1502158444,
  "date_modified": 1502158444
}
```

#### Update Lead

**Request:**
```bash
PUT /developer_api/v1/leads/13244480
```

```json
{
  "status": "Qualified",
  "details": "Spoke with prospect, very interested in Q1 implementation"
}
```

**Response (200 OK):**
```json
{
  "id": 13244480,
  "name": "John Doe",
  "status": "Qualified",
  "details": "Spoke with prospect, very interested in Q1 implementation",
  "date_modified": 1513976942
}
```

#### Delete Lead

**Request:**
```bash
DELETE /developer_api/v1/leads/13244480
```

**Response (200 OK):**
```json
{
  "id": 13244480,
  "status": "deleted"
}
```

#### Convert Lead

**Request:**
```bash
POST /developer_api/v1/leads/13244480/convert
```

```json
{
  "person": {
    "name": "John Doe",
    "emails": [
      {
        "email": "john.doe@example.com",
        "category": "work"
      }
    ]
  },
  "company": {
    "name": "Acme Corp"
  },
  "opportunity": {
    "name": "Acme Corp - Annual Contract",
    "monetary_value": 100000,
    "pipeline_id": 512676
  }
}
```

**Response (200 OK):**
```json
{
  "person_id": 27140359,
  "company_id": 9607580,
  "opportunity_id": 8765432
}
```

### People (Contacts)

#### Create Person

**Request:**
```bash
POST /developer_api/v1/people
```

```json
{
  "name": "Jane Smith",
  "emails": [
    {
      "email": "jane.smith@techco.com",
      "category": "work"
    }
  ],
  "title": "CTO",
  "company_id": 9607580,
  "phone_numbers": [
    {
      "number": "650-555-9999",
      "category": "work"
    }
  ],
  "tags": ["decision-maker"]
}
```

**Response (200 OK):**
```json
{
  "id": 27140359,
  "name": "Jane Smith",
  "emails": [
    {
      "email": "jane.smith@techco.com",
      "category": "work"
    }
  ],
  "title": "CTO",
  "company_id": 9607580,
  "phone_numbers": [
    {
      "number": "650-555-9999",
      "category": "work"
    }
  ],
  "tags": ["decision-maker"],
  "date_created": 1502158500,
  "date_modified": 1502158500
}
```

#### Search People

**Request:**
```bash
POST /developer_api/v1/people/search
```

```json
{
  "page_size": 200,
  "page_number": 1,
  "sort_by": "name",
  "sort_direction": "asc",
  "company_ids": [9607580]
}
```

**Response (200 OK):**
```json
[
  {
    "id": 27140359,
    "name": "Jane Smith",
    "title": "CTO",
    "company_id": 9607580,
    "emails": [
      {
        "email": "jane.smith@techco.com",
        "category": "work"
      }
    ],
    "date_created": 1502158500,
    "date_modified": 1502158500
  }
]
```

#### Update Person

**Request:**
```bash
PUT /developer_api/v1/people/27140359
```

```json
{
  "title": "Chief Technology Officer",
  "emails": [
    {
      "email": "jane@techco.com",
      "category": "work"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "id": 27140359,
  "name": "Jane Smith",
  "title": "Chief Technology Officer",
  "emails": [
    {
      "email": "jane@techco.com",
      "category": "work"
    }
  ],
  "date_modified": 1513976950
}
```

#### Fetch Person by Email

**Request:**
```bash
POST /developer_api/v1/people/fetch_by_email
```

```json
{
  "email": "jane@techco.com"
}
```

**Response (200 OK):**
```json
{
  "id": 27140359,
  "name": "Jane Smith",
  "title": "Chief Technology Officer",
  "emails": [
    {
      "email": "jane@techco.com",
      "category": "work"
    }
  ]
}
```

### Companies

#### Create Company

**Request:**
```bash
POST /developer_api/v1/companies
```

```json
{
  "name": "Acme Corporation",
  "email_domain": "acme.com",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105",
    "country": "US"
  },
  "phone_numbers": [
    {
      "number": "415-555-1234",
      "category": "work"
    }
  ],
  "websites": [
    {
      "url": "https://acme.com",
      "category": "work"
    }
  ],
  "tags": ["enterprise", "west-coast"]
}
```

**Response (200 OK):**
```json
{
  "id": 9607580,
  "name": "Acme Corporation",
  "email_domain": "acme.com",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105",
    "country": "US"
  },
  "phone_numbers": [
    {
      "number": "415-555-1234",
      "category": "work"
    }
  ],
  "websites": [
    {
      "url": "https://acme.com",
      "category": "work"
    }
  ],
  "tags": ["enterprise", "west-coast"],
  "date_created": 1640995200,
  "date_modified": 1640995200
}
```

#### Search Companies

**Request:**
```bash
POST /developer_api/v1/companies/search
```

```json
{
  "page_size": 200,
  "page_number": 1,
  "sort_by": "date_modified",
  "sort_direction": "desc",
  "tags": ["enterprise"]
}
```

**Response (200 OK):**
```json
[
  {
    "id": 9607580,
    "name": "Acme Corporation",
    "email_domain": "acme.com",
    "tags": ["enterprise", "west-coast"],
    "date_created": 1640995200,
    "date_modified": 1704067200
  }
]
```

### Opportunities (Deals)

#### Create Opportunity

**Request:**
```bash
POST /developer_api/v1/opportunities
```

```json
{
  "name": "Q1 Enterprise Deal",
  "primary_contact_id": 27140359,
  "company_id": 9607580,
  "monetary_value": 50000,
  "close_date": "03/31/2024",
  "pipeline_id": 512676,
  "pipeline_stage_id": 982538,
  "priority": "High",
  "win_probability": 75
}
```

**Response (200 OK):**
```json
{
  "id": 8765432,
  "name": "Q1 Enterprise Deal",
  "primary_contact_id": 27140359,
  "company_id": 9607580,
  "monetary_value": 50000,
  "close_date": "03/31/2024",
  "pipeline_id": 512676,
  "pipeline_stage_id": 982538,
  "priority": "High",
  "win_probability": 75,
  "status": "Open",
  "date_created": 1489018784,
  "date_modified": 1489018784
}
```

#### Search Opportunities

**Request:**
```bash
POST /developer_api/v1/opportunities/search
```

```json
{
  "page_size": 100,
  "page_number": 1,
  "sort_by": "monetary_value",
  "sort_direction": "desc",
  "statuses": ["Open"],
  "pipeline_stage_ids": [982538],
  "minimum_monetary_value": 10000
}
```

**Response (200 OK):**
```json
[
  {
    "id": 8765432,
    "name": "Q1 Enterprise Deal",
    "status": "Open",
    "monetary_value": 50000,
    "pipeline_stage_id": 982538,
    "win_probability": 75,
    "date_created": 1489018784,
    "date_modified": 1489018784
  }
]
```

#### Update Opportunity

**Request:**
```bash
PUT /developer_api/v1/opportunities/8765432
```

```json
{
  "pipeline_stage_id": 982539,
  "win_probability": 90,
  "monetary_value": 60000
}
```

**Response (200 OK):**
```json
{
  "id": 8765432,
  "name": "Q1 Enterprise Deal",
  "pipeline_stage_id": 982539,
  "win_probability": 90,
  "monetary_value": 60000,
  "date_modified": 1513976960
}
```

### Activities

#### Create Activity (Note)

**Request:**
```bash
POST /developer_api/v1/activities
```

```json
{
  "parent": {
    "type": "person",
    "id": 27140359
  },
  "type": {
    "category": "user",
    "id": 0
  },
  "details": "Had a great call about their Q1 goals. Follow up in 2 weeks."
}
```

**Response (200 OK):**
```json
{
  "id": 3064242278,
  "parent": {
    "id": 27140359,
    "type": "person"
  },
  "type": {
    "id": 0,
    "category": "user"
  },
  "user_id": 137658,
  "details": "Had a great call about their Q1 goals. Follow up in 2 weeks.",
  "activity_date": 1496772355,
  "date_created": 1496772355
}
```

#### Get Activities for Entity

**Request:**
```bash
GET /developer_api/v1/people/27140359/activities
```

**Response (200 OK):**
```json
[
  {
    "id": 3064242278,
    "parent": {
      "id": 27140359,
      "type": "person"
    },
    "type": {
      "id": 0,
      "category": "user"
    },
    "user_id": 137658,
    "details": "Had a great call about their Q1 goals. Follow up in 2 weeks.",
    "activity_date": 1496772355
  }
]
```

### Custom Fields

#### Get Custom Field Definitions

**Request:**
```bash
GET /developer_api/v1/custom_field_definitions
```

**Response (200 OK):**
```json
[
  {
    "id": 100764,
    "name": "Company Size",
    "data_type": "Dropdown",
    "available_on": ["company", "person"],
    "options": [
      {"id": 167776, "name": "Enterprise"},
      {"id": 167777, "name": "SMB"},
      {"id": 167778, "name": "Startup"}
    ]
  },
  {
    "id": 126240,
    "name": "Budget",
    "data_type": "Currency",
    "available_on": ["opportunity"]
  }
]
```

#### Create Record with Custom Fields

**Request:**
```bash
POST /developer_api/v1/companies
```

```json
{
  "name": "TechCo Inc",
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": 167776
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "id": 9607581,
  "name": "TechCo Inc",
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": 167776
    }
  ],
  "date_created": 1640995300,
  "date_modified": 1640995300
}
```

### Account

#### Get Account Details

**Request:**
```bash
GET /developer_api/v1/account
```

**Response (200 OK):**
```json
{
  "id": 123456,
  "name": "Your Company Name",
  "primary_timezone": "America/New_York",
  "settings": {
    "setting_team_permissions_enabled": true,
    "setting_enable_leads": true
  }
}
```

---

## Status Codes

### Success Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request succeeded |

### Client Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication credentials |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Valid request but business logic error (e.g., duplicate email) |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 500 | Internal Server Error | Unexpected server-side error |
| 502 | Bad Gateway | Server is down or unreachable |
| 503 | Service Unavailable | Server temporarily unavailable |

### Error Response Format

All error responses follow this format:

```json
{
  "message": "Detailed error description",
  "status": 422
}
```

### Common Error Scenarios

#### 401 Unauthorized

**Cause:** Missing or invalid API key

**Example Response:**
```json
{
  "message": "Unauthorized",
  "status": 401
}
```

**Solutions:**
- Verify API key is correct
- Check that `X-PW-AccessToken` header is present
- Ensure `X-PW-UserEmail` matches the token owner

#### 422 Unprocessable Entity

**Cause 1:** Duplicate email address (People)

**Example Response:**
```json
{
  "message": "Email address already exists",
  "status": 422
}
```

**Cause 2:** Missing required field

**Example Response:**
```json
{
  "message": "name is required",
  "status": 422
}
```

**Cause 3:** Invalid data type

**Example Response:**
```json
{
  "message": "monetary_value must be a number",
  "status": 422
}
```

**Solutions:**
- Check for duplicate email addresses (People)
- Check for duplicate domains (Companies)
- Verify all required fields are present
- Validate data types match expected format

#### 429 Too Many Requests

**Cause:** Rate limit exceeded

**Example Response:**
```json
{
  "message": "Rate limit exceeded",
  "status": 429
}
```

**Solutions:**
- Standard APIs: Wait 60 seconds, retry (180 requests/min limit)
- Bulk APIs: Reduce to max 3 requests/second
- Implement exponential backoff retry logic

#### 404 Not Found

**Cause:** Resource doesn't exist

**Example Response:**
```json
{
  "message": "Lead not found",
  "status": 404
}
```

**Solutions:**
- Verify the ID is correct
- Check if resource was deleted
- Confirm you have access to the resource

---

## Quick Reference Cards

### Lead Quick Reference

**Endpoint Pattern:** `/leads`

**CRUD Operations:**
```
Create:  POST   /leads
Read:    GET    /leads/{id}
Update:  PUT    /leads/{id}
Delete:  DELETE /leads/{id}
Search:  POST   /leads/search
Convert: POST   /leads/{id}/convert
```

**Required Fields:**
- `name` (string)

**Optional Key Fields:**
- `email` (object: {email, category})
- `company_name` (string)
- `title` (string)
- `status` (string)
- `assignee_id` (integer)
- `tags` (array[string])

**Search Filters:**
- `status_ids`
- `assignee_ids`
- `customer_source_ids`
- `tags`
- `minimum_created_date`
- `maximum_created_date`

**Example Create:**
```json
{
  "name": "John Doe",
  "email": {"email": "john@example.com", "category": "work"},
  "company_name": "Acme Corp"
}
```

**Conversion:**
Convert lead to person, company, and/or opportunity:
```bash
POST /leads/{id}/convert
{
  "person": {...},
  "company": {...},
  "opportunity": {...}
}
```

---

### Person Quick Reference

**Endpoint Pattern:** `/people`

**CRUD Operations:**
```
Create:       POST /people
Read:         GET  /people/{id}
Update:       PUT  /people/{id}
Delete:       DELETE /people/{id}
Search:       POST /people/search
Fetch by Email: POST /people/fetch_by_email
```

**Required Fields:**
- `name` (string)

**Optional Key Fields:**
- `emails` (array[object]: [{email, category}])
- `title` (string)
- `company_id` (integer)
- `phone_numbers` (array[object])
- `assignee_id` (integer)
- `tags` (array[string])

**Unique Constraints:**
- Email address must be unique

**Search Filters:**
- `company_ids`
- `contact_type_ids`
- `assignee_ids`
- `tags`

**Example Create:**
```json
{
  "name": "Jane Smith",
  "emails": [{"email": "jane@techco.com", "category": "work"}],
  "title": "CTO",
  "company_id": 9607580
}
```

---

### Company Quick Reference

**Endpoint Pattern:** `/companies`

**CRUD Operations:**
```
Create:  POST   /companies
Read:    GET    /companies/{id}
Update:  PUT    /companies/{id}
Delete:  DELETE /companies/{id}
Search:  POST   /companies/search
```

**Required Fields:**
- `name` (string)

**Optional Key Fields:**
- `email_domain` (string)
- `primary_contact_id` (integer)
- `address` (object)
- `phone_numbers` (array[object])
- `websites` (array[object])
- `assignee_id` (integer)
- `tags` (array[string])

**Unique Constraints:**
- Email domain must be unique

**Search Filters:**
- `contact_type_ids`
- `assignee_ids`
- `tags`

**Example Create:**
```json
{
  "name": "Acme Corporation",
  "email_domain": "acme.com",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105"
  }
}
```

---

### Opportunity Quick Reference

**Endpoint Pattern:** `/opportunities`

**CRUD Operations:**
```
Create:  POST   /opportunities
Read:    GET    /opportunities/{id}
Update:  PUT    /opportunities/{id}
Delete:  DELETE /opportunities/{id}
Search:  POST   /opportunities/search
```

**Required Fields:**
- `name` (string)

**Optional Key Fields:**
- `company_id` (integer)
- `primary_contact_id` (integer)
- `monetary_value` (float)
- `close_date` (string: MM/DD/YYYY)
- `pipeline_id` (integer)
- `pipeline_stage_id` (integer)
- `status` (string: Open/Won/Lost/Abandoned)
- `win_probability` (integer: 0-100)
- `priority` (string)
- `tags` (array[string])

**Search Filters:**
- `pipeline_ids`
- `pipeline_stage_ids`
- `statuses`
- `assignee_ids`
- `minimum_monetary_value`
- `maximum_monetary_value`

**Example Create:**
```json
{
  "name": "Q1 Enterprise Deal",
  "company_id": 9607580,
  "primary_contact_id": 27140359,
  "monetary_value": 50000,
  "close_date": "03/31/2024",
  "pipeline_id": 512676,
  "win_probability": 75
}
```

---

### Activity Quick Reference

**Endpoint Pattern:** `/activities`

**CRUD Operations:**
```
Create:  POST   /activities
Read:    GET    /activities/{id}
Update:  PUT    /activities/{id}
Delete:  DELETE /activities/{id}
Search:  POST   /activities/search
```

**Required Fields:**
- `parent` (object: {type, id})
- `type` (object: {category, id})

**Optional Key Fields:**
- `details` (string)
- `activity_date` (integer: Unix timestamp)

**Parent Types:**
- `lead`
- `person`
- `company`
- `opportunity`

**Activity Categories:**
- `user` (id: 0) - User-created note
- `system` - System-generated
- `email` - Email activity
- `call` - Phone call

**Example Create:**
```json
{
  "parent": {
    "type": "person",
    "id": 27140359
  },
  "type": {
    "category": "user",
    "id": 0
  },
  "details": "Follow-up call scheduled for next week"
}
```

---

### Pagination Quick Reference

**Pattern:** Use in all search endpoints

**Standard Pagination:**
```json
{
  "page_number": 1,
  "page_size": 200,
  "sort_by": "date_modified",
  "sort_direction": "desc"
}
```

**Limits:**
- Default page size: 20
- Max page size: 200
- Max total records: 100,000

**Response Header:**
```
X-PW-TOTAL: 125
```

**Calculate Pages:**
```javascript
const totalRecords = parseInt(response.headers['X-PW-TOTAL']);
const pageSize = 200;
const totalPages = Math.ceil(totalRecords / pageSize);
```

**Iterate All Pages:**
```javascript
let page = 1;
let allRecords = [];

while (true) {
  const records = await search({ page_number: page, page_size: 200 });
  if (records.length === 0) break;

  allRecords.push(...records);
  page++;
}
```

---

### Authentication Quick Reference

**API Key Method:**
```http
X-PW-AccessToken: YOUR_API_KEY
X-PW-Application: developer_api
X-PW-UserEmail: your.email@company.com
Content-Type: application/json
```

**OAuth Method:**
```http
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Test Authentication:**
```bash
curl -X GET "https://api.copper.com/developer_api/v1/account" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": 123456,
  "name": "Your Company Name"
}
```

---

### Rate Limiting Quick Reference

**Limits:**
- Standard APIs: 180 requests/minute
- Bulk APIs: 3 requests/second

**Error Response (429):**
```json
{
  "message": "Rate limit exceeded",
  "status": 429
}
```

**Retry Strategy:**
```javascript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
}
```

---

### Custom Fields Quick Reference

**Get Definitions:**
```bash
GET /custom_field_definitions
```

**Response:**
```json
[
  {
    "id": 100764,
    "name": "Company Size",
    "data_type": "Dropdown",
    "available_on": ["company", "person"],
    "options": [
      {"id": 167776, "name": "Enterprise"}
    ]
  }
]
```

**Set Custom Field:**
```json
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": 167776
    }
  ]
}
```

**Search by Custom Field:**
```json
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": 167776
    }
  ]
}
```

**Supported Types:**
- String
- Number
- Date
- Dropdown (use option ID as value)
- Multi-select
- Checkbox
- URL

---

## Additional Resources

**Official Documentation:** https://developer.copper.com

**Support:** https://support.copper.com

**API Version:** v1 (stable)

**Postman Collection:** https://developer.copper.com/download/copper_postman_collection.json

**Changelog:** https://developer.copper.com/introduction/changelog.html
