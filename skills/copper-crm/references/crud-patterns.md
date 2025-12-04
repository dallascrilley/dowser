# Copper CRM CRUD Patterns

Comprehensive guide to Create, Read, Update, and Delete operations for all Copper CRM entities.

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Leads CRUD](#leads-crud)
4. [People CRUD](#people-crud)
5. [Companies CRUD](#companies-crud)
6. [Opportunities CRUD](#opportunities-crud)
7. [UPSERT Patterns](#upsert-patterns)
8. [Bulk Operations](#bulk-operations)
9. [Common Patterns](#common-patterns)
10. [Python Examples](#python-examples)

---

## Overview

Copper CRM follows standard RESTful patterns for CRUD operations:

- **CREATE**: `POST /{entity_type}`
- **READ**: `GET /{entity_type}/{id}`
- **UPDATE**: `PUT /{entity_type}/{id}`
- **DELETE**: `DELETE /{entity_type}/{id}`
- **SEARCH/LIST**: `POST /{entity_type}/search`

**Base URL**: `https://api.copper.com/developer_api/v1`

**Rate Limits**:
- Standard APIs: 180 requests/minute
- Bulk APIs: 3 requests/second

---

## Authentication

All requests require the following headers:

```bash
X-PW-AccessToken: YOUR_API_KEY
X-PW-Application: developer_api
X-PW-UserEmail: your.email@company.com
Content-Type: application/json
```

---

## Leads CRUD

### CREATE Lead

**Endpoint**: `POST /leads`

**Required Fields**:
- `name` - Lead name (string)

**Optional Fields**:
- `email` - Email object with `email` and `category`
- `phone_numbers` - Array of phone objects
- `company_name` - Company name (string)
- `title` - Job title (string)
- `address` - Address object
- `status` - Lead status (string)
- `assignee_id` - Assigned user ID (integer)
- `customer_source_id` - Lead source ID (integer)
- `tags` - Array of tag strings
- `custom_fields` - Array of custom field objects
- `details` - Notes/description (string)

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/leads" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
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
    "title": "VP of Sales"
  }'
```

**Response (200)**:
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
  "date_created": 1502158444,
  "date_modified": 1502158444
}
```

### READ Lead

**Endpoint**: `GET /leads/{id}`

**cURL Example**:
```bash
curl -X GET "https://api.copper.com/developer_api/v1/leads/13244480" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### UPDATE Lead

**Endpoint**: `PUT /leads/{id}`

**Notes**:
- Only fields specified in request body are updated
- To remove a value, set field to `null`
- All fields are optional

**cURL Example**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/leads/13244480" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Qualified",
    "details": "Spoke with prospect, very interested in Q1 implementation"
  }'
```

### DELETE Lead

**Endpoint**: `DELETE /leads/{id}`

**cURL Example**:
```bash
curl -X DELETE "https://api.copper.com/developer_api/v1/leads/13244480" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

**Response (200)**:
```json
{
  "id": 13244480,
  "is_deleted": true
}
```

### SEARCH Leads

**Endpoint**: `POST /leads/search`

**Search Parameters**:
- `page_number` - Page number (1-indexed)
- `page_size` - Results per page (max 200)
- `sort_by` - Field to sort by (e.g., "name", "date_modified")
- `sort_direction` - "asc" or "desc"
- `status_ids` - Array of status IDs
- `assignee_ids` - Array of assignee IDs
- `minimum_created_date` - Unix timestamp
- `maximum_created_date` - Unix timestamp
- `custom_fields` - Array of custom field filters

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/leads/search" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "page_size": 50,
    "sort_by": "name",
    "sort_direction": "asc",
    "status_ids": [208231]
  }'
```

---

## People CRUD

### CREATE Person

**Endpoint**: `POST /people`

**Required Fields**:
- `name` - Full name (string)

**Optional Fields**:
- `emails` - Array of email objects
- `phone_numbers` - Array of phone objects
- `address` - Address object
- `title` - Job title (string)
- `company_id` - Associated company ID (integer)
- `assignee_id` - Assigned user ID (integer)
- `contact_type_id` - Contact type ID (integer)
- `details` - Notes/description (string)
- `websites` - Array of website objects
- `socials` - Array of social media objects
- `tags` - Array of tag strings
- `custom_fields` - Array of custom field objects

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/people" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Contact",
    "emails": [
      {
        "email": "mycontact@example.com",
        "category": "work"
      }
    ],
    "phone_numbers": [
      {
        "number": "415-123-45678",
        "category": "mobile"
      }
    ],
    "address": {
      "street": "123 Main Street",
      "city": "Savannah",
      "state": "Georgia",
      "postal_code": "31410",
      "country": "United States"
    }
  }'
```

**Response (200)**:
```json
{
  "id": 27140448,
  "name": "My Contact",
  "first_name": "My",
  "last_name": "Contact",
  "emails": [
    {
      "email": "mycontact@example.com",
      "category": "work"
    }
  ],
  "phone_numbers": [
    {
      "number": "415-123-45678",
      "category": "mobile"
    }
  ],
  "date_created": 1490045450,
  "date_modified": 1490045450
}
```

### READ Person

**Endpoint**: `GET /people/{id}`

**cURL Example**:
```bash
curl -X GET "https://api.copper.com/developer_api/v1/people/27140448" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### UPDATE Person

**Endpoint**: `PUT /people/{id}`

**Notes**:
- Only fields specified in request body are updated
- To remove a value, set field to `null`
- To update `company_id`, use the Related Items API

**cURL Example**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/people/27140448" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "details": "This is an update"
  }'
```

### DELETE Person

**Endpoint**: `DELETE /people/{id}`

**cURL Example**:
```bash
curl -X DELETE "https://api.copper.com/developer_api/v1/people/27140448" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

**Response (200)**:
```json
{
  "id": 27140448,
  "is_deleted": true
}
```

### SEARCH People

**Endpoint**: `POST /people/search`

**Search Parameters**: Same as Leads search

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/people/search" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "page_size": 200,
    "sort_by": "date_modified",
    "sort_direction": "desc"
  }'
```

---

## Companies CRUD

### CREATE Company

**Endpoint**: `POST /companies`

**Required Fields**:
- `name` - Company name (string)

**Optional Fields**:
- `email_domain` - Primary email domain (string, must be unique)
- `address` - Address object
- `phone_numbers` - Array of phone objects
- `primary_contact_id` - Primary contact person ID (integer)
- `assignee_id` - Assigned user ID (integer)
- `contact_type_id` - Contact type ID (integer)
- `details` - Notes/description (string)
- `websites` - Array of website objects
- `socials` - Array of social media objects
- `tags` - Array of tag strings
- `custom_fields` - Array of custom field objects

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/companies" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Company",
    "address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94105"
    },
    "email_domain": "democompany.com",
    "details": "This is a demo company",
    "phone_numbers": [
      {
        "number": "415-123-45678",
        "category": "work"
      }
    ],
    "primary_contact_id": 27140359
  }'
```

**Response (200)**:
```json
{
  "id": 13358412,
  "name": "Demo Company",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105"
  },
  "email_domain": "democompany.com",
  "primary_contact_id": 27140359,
  "date_created": 1496707930,
  "date_modified": 1496707930
}
```

### READ Company

**Endpoint**: `GET /companies/{id}`

**cURL Example**:
```bash
curl -X GET "https://api.copper.com/developer_api/v1/companies/13358412" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### UPDATE Company

**Endpoint**: `PUT /companies/{id}`

**Notes**:
- Only fields specified in request body are updated
- To remove a value, set field to `null`
- `email_domain` must remain unique

**cURL Example**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/companies/13358412" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "details": "Updated company description"
  }'
```

### DELETE Company

**Endpoint**: `DELETE /companies/{id}`

**cURL Example**:
```bash
curl -X DELETE "https://api.copper.com/developer_api/v1/companies/13358412" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### SEARCH Companies

**Endpoint**: `POST /companies/search`

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/companies/search" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "page_size": 200,
    "sort_by": "name",
    "sort_direction": "asc"
  }'
```

---

## Opportunities CRUD

### CREATE Opportunity

**Endpoint**: `POST /opportunities`

**Required Fields**:
- `name` - Opportunity name (string)
- `primary_contact_id` - Primary contact person ID (integer)

**Optional Fields**:
- `company_id` - Associated company ID (integer)
- `assignee_id` - Assigned user ID (integer)
- `pipeline_id` - Pipeline ID (integer)
- `pipeline_stage_id` - Pipeline stage ID (integer)
- `customer_source_id` - Lead source ID (integer)
- `monetary_value` - Deal value (float)
- `close_date` - Expected close date (string, format: "MM/DD/YYYY")
- `win_probability` - Win probability percentage (integer, 0-100)
- `priority` - Priority level (string: "None", "Low", "Medium", "High")
- `status` - Status (string: "Open", "Won", "Lost", "Abandoned")
- `tags` - Array of tag strings
- `custom_fields` - Array of custom field objects
- `details` - Notes/description (string)

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/opportunities" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q1 Enterprise Deal",
    "primary_contact_id": 27140359,
    "company_id": 13358412,
    "monetary_value": 50000,
    "close_date": "03/31/2024",
    "priority": "High"
  }'
```

**Response (200)**:
```json
{
  "id": 4956209,
  "name": "Q1 Enterprise Deal",
  "primary_contact_id": 27140359,
  "company_id": 13358412,
  "monetary_value": 50000,
  "close_date": "03/31/2024",
  "priority": "High",
  "status": "Open",
  "date_created": 1502158599,
  "date_modified": 1502158599
}
```

### READ Opportunity

**Endpoint**: `GET /opportunities/{id}`

**cURL Example**:
```bash
curl -X GET "https://api.copper.com/developer_api/v1/opportunities/4956209" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### UPDATE Opportunity

**Endpoint**: `PUT /opportunities/{id}`

**cURL Example**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/opportunities/4956209" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Won",
    "win_probability": 100
  }'
```

### DELETE Opportunity

**Endpoint**: `DELETE /opportunities/{id}`

**cURL Example**:
```bash
curl -X DELETE "https://api.copper.com/developer_api/v1/opportunities/4956209" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json"
```

### SEARCH Opportunities

**Endpoint**: `POST /opportunities/search`

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/opportunities/search" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "page_size": 200,
    "sort_by": "date_modified",
    "sort_direction": "desc",
    "statuses": ["Open"]
  }'
```

---

## UPSERT Patterns

UPSERT (Update + Insert) operations atomically check for existence and either update or create.

### UPSERT Lead

**Endpoint**: `PUT /leads/upsert`

**Match Criteria**:
- Name
- Email
- Custom Fields

**Match Outcomes**:
- No matches → Create new lead
- Exactly one match → Update that lead
- Multiple matches (≤30) → Return 422 with matching IDs
- Multiple matches (>30) → Return 422 without IDs

**Request Structure**:
```json
{
  "properties": {
    // Lead fields to set
  },
  "match": {
    "field_name": "email",
    "field_value": "mylead@example.com"
  }
}
```

**cURL Example - Match by Email**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/leads/upsert" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "name": "My Lead",
      "email": {
        "email": "mylead@example.com",
        "category": "work"
      },
      "company_name": "Example Corp"
    },
    "match": {
      "field_name": "email",
      "field_value": "mylead@example.com"
    }
  }'
```

**cURL Example - Match by Custom Field**:
```bash
curl -X PUT "https://api.copper.com/developer_api/v1/leads/upsert" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "name": "My Lead",
      "custom_fields": [
        {
          "custom_field_definition_id": 100764,
          "value": "EXTERNAL_ID_123"
        }
      ]
    },
    "match": {
      "field_name": "custom_fields",
      "custom_field_definition_id": 100764,
      "field_value": "EXTERNAL_ID_123"
    }
  }'
```

---

## Bulk Operations

Bulk operations allow processing multiple records in a single request.

**Bulk Limits**:
- Maximum batch size: 10 records
- Rate limit: 3 requests/second
- All requests return 200 OK with individual success/failure in response

### Bulk Create Leads

**Endpoint**: `POST /leads/bulk_create`

**Request Structure**:
```json
{
  "leads": [
    { /* lead 1 fields */ },
    { /* lead 2 fields */ },
    { /* lead 3 fields */ }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/leads/bulk_create" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "leads": [
      {
        "name": "Lead One",
        "email": {
          "email": "lead1@example.com",
          "category": "work"
        }
      },
      {
        "name": "Lead Two",
        "email": {
          "email": "lead2@example.com",
          "category": "work"
        }
      }
    ]
  }'
```

**Success Response**:
```json
[
  {
    "id": 13244480,
    "name": "Lead One",
    "email": {
      "email": "lead1@example.com",
      "category": "work"
    },
    "date_created": 1502158444
  },
  {
    "id": 13244481,
    "name": "Lead Two",
    "email": {
      "email": "lead2@example.com",
      "category": "work"
    },
    "date_created": 1502158444
  }
]
```

**Failure Response (partial)**:
```json
[
  {
    "id": 13244480,
    "name": "Lead One",
    "date_created": 1502158444
  },
  {
    "success": false,
    "message": {
      "email": [
        {
          "error": "already exists"
        }
      ]
    }
  }
]
```

### Bulk Update Companies

**Endpoint**: `POST /companies/bulk_update`

**Request Structure**:
```json
{
  "companies": [
    {
      "id": 12345,
      /* fields to update */
    },
    {
      "id": 67890,
      /* fields to update */
    }
  ]
}
```

**cURL Example**:
```bash
curl -X POST "https://api.copper.com/developer_api/v1/companies/bulk_update" \
  -H "X-PW-AccessToken: YOUR_API_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d '{
    "companies": [
      {
        "id": 12345,
        "name": "Company One",
        "email_domain": "company1.com"
      },
      {
        "id": 67890,
        "name": "Company Two",
        "email_domain": "company2.com"
      }
    ]
  }'
```

### Other Bulk Endpoints

- **Bulk Create People**: `POST /people/bulk_create`
- **Bulk Update People**: `POST /people/bulk_update`
- **Bulk Create Opportunities**: `POST /opportunities/bulk_create`
- **Bulk Update Opportunities**: `POST /opportunities/bulk_update`

All follow the same pattern as shown above.

---

## Common Patterns

### Custom Fields

Custom fields are supported on all entity types:

```json
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100764,
      "value": "Custom value"
    }
  ]
}
```

**Custom Field Types**:
- String
- Number
- Date
- Dropdown
- Multi-select
- Checkbox
- URL

### Address Object

```json
{
  "address": {
    "street": "123 Main Street",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105",
    "country": "US"
  }
}
```

### Email Object

```json
{
  "email": {
    "email": "contact@example.com",
    "category": "work"
  }
}
```

**Email Categories**: "work", "personal", "other"

### Phone Number Object

```json
{
  "phone_numbers": [
    {
      "number": "415-555-1234",
      "category": "mobile"
    }
  ]
}
```

**Phone Categories**: "mobile", "work", "home", "other"

### Website Object

```json
{
  "websites": [
    {
      "url": "https://example.com",
      "category": "work"
    }
  ]
}
```

### Social Media Object

```json
{
  "socials": [
    {
      "url": "https://twitter.com/username",
      "category": "twitter"
    }
  ]
}
```

### Pagination Pattern

```bash
# Initial request
curl -X POST "https://api.copper.com/developer_api/v1/leads/search" \
  -H "..." \
  -d '{
    "page_number": 1,
    "page_size": 200,
    "sort_by": "date_modified",
    "sort_direction": "desc"
  }'

# Check X-PW-TOTAL header for total count
# If more pages exist, increment page_number

# Next page
curl -X POST "https://api.copper.com/developer_api/v1/leads/search" \
  -H "..." \
  -d '{
    "page_number": 2,
    "page_size": 200,
    "sort_by": "date_modified",
    "sort_direction": "desc"
  }'
```

### Error Handling

**Common Error Codes**:
- `400` - Bad Request (invalid JSON or parameters)
- `401` - Unauthorized (invalid API key or email)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation error, duplicate)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

**Error Response Format**:
```json
{
  "message": "Error description",
  "status": 422
}
```

---

## Python Examples

### Setup

```python
import requests
import json
from typing import Dict, List, Optional

class CopperClient:
    def __init__(self, access_token: str, user_email: str):
        self.base_url = "https://api.copper.com/developer_api/v1"
        self.headers = {
            "X-PW-AccessToken": access_token,
            "X-PW-Application": "developer_api",
            "X-PW-UserEmail": user_email,
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
```

### Create Lead

```python
def create_lead(self, name: str, email: str, **kwargs) -> Dict:
    """Create a new lead."""
    data = {
        "name": name,
        "email": {
            "email": email,
            "category": "work"
        },
        **kwargs
    }
    return self._request("POST", "leads", data)

# Usage
client = CopperClient("YOUR_API_KEY", "your.email@company.com")

lead = client.create_lead(
    name="John Doe",
    email="john@example.com",
    company_name="Acme Corp",
    title="VP of Sales"
)
print(f"Created lead ID: {lead['id']}")
```

### Read Lead

```python
def get_lead(self, lead_id: int) -> Dict:
    """Get lead by ID."""
    return self._request("GET", f"leads/{lead_id}")

# Usage
lead = client.get_lead(13244480)
print(f"Lead name: {lead['name']}")
```

### Update Lead

```python
def update_lead(self, lead_id: int, **updates) -> Dict:
    """Update lead fields."""
    return self._request("PUT", f"leads/{lead_id}", updates)

# Usage
updated = client.update_lead(
    13244480,
    status="Qualified",
    details="Follow-up scheduled for next week"
)
```

### Delete Lead

```python
def delete_lead(self, lead_id: int) -> Dict:
    """Delete a lead."""
    return self._request("DELETE", f"leads/{lead_id}")

# Usage
result = client.delete_lead(13244480)
print(f"Deleted: {result['is_deleted']}")
```

### Search Leads

```python
def search_leads(self, **filters) -> List[Dict]:
    """Search leads with filters."""
    data = {
        "page_size": 200,
        "sort_by": "date_modified",
        "sort_direction": "desc",
        **filters
    }
    return self._request("POST", "leads/search", data)

# Usage
leads = client.search_leads(
    status_ids=[208231],
    assignee_ids=[137658]
)
print(f"Found {len(leads)} leads")
```

### UPSERT Lead

```python
def upsert_lead(self, properties: Dict, match_field: str, match_value: str) -> Dict:
    """UPSERT a lead by matching field."""
    data = {
        "properties": properties,
        "match": {
            "field_name": match_field,
            "field_value": match_value
        }
    }
    return self._request("PUT", "leads/upsert", data)

# Usage - Match by email
lead = client.upsert_lead(
    properties={
        "name": "John Doe",
        "email": {
            "email": "john@example.com",
            "category": "work"
        },
        "company_name": "Updated Corp"
    },
    match_field="email",
    match_value="john@example.com"
)
```

### Bulk Create Leads

```python
def bulk_create_leads(self, leads: List[Dict]) -> List[Dict]:
    """Bulk create leads (max 10 per request)."""
    if len(leads) > 10:
        raise ValueError("Maximum 10 leads per bulk request")

    data = {"leads": leads}
    return self._request("POST", "leads/bulk_create", data)

# Usage
leads_data = [
    {
        "name": "Lead One",
        "email": {"email": "lead1@example.com", "category": "work"}
    },
    {
        "name": "Lead Two",
        "email": {"email": "lead2@example.com", "category": "work"}
    }
]

results = client.bulk_create_leads(leads_data)

for i, result in enumerate(results):
    if "id" in result:
        print(f"Lead {i+1} created: ID {result['id']}")
    else:
        print(f"Lead {i+1} failed: {result.get('message')}")
```

### Complete CRUD Example for People

```python
# CREATE
person = client._request("POST", "people", {
    "name": "Jane Smith",
    "emails": [
        {"email": "jane@example.com", "category": "work"}
    ],
    "title": "CTO",
    "company_id": 13358412
})
person_id = person["id"]

# READ
person = client._request("GET", f"people/{person_id}")
print(f"Person: {person['name']}, Title: {person['title']}")

# UPDATE
updated = client._request("PUT", f"people/{person_id}", {
    "title": "Chief Technology Officer",
    "details": "Updated title"
})

# SEARCH
people = client._request("POST", "people/search", {
    "page_size": 50,
    "company_id": 13358412
})

# DELETE
result = client._request("DELETE", f"people/{person_id}")
print(f"Deleted: {result['is_deleted']}")
```

### Pagination Helper

```python
def search_all_leads(self, **filters) -> List[Dict]:
    """Search all leads with automatic pagination."""
    all_leads = []
    page = 1

    while True:
        data = {
            "page_number": page,
            "page_size": 200,
            "sort_by": "date_modified",
            "sort_direction": "desc",
            **filters
        }

        results = self._request("POST", "leads/search", data)

        if not results:
            break

        all_leads.extend(results)
        page += 1

    return all_leads

# Usage
all_leads = client.search_all_leads(status_ids=[208231])
print(f"Total leads: {len(all_leads)}")
```

### Error Handling

```python
from requests.exceptions import HTTPError

def safe_create_lead(self, name: str, email: str, **kwargs) -> Optional[Dict]:
    """Create lead with error handling."""
    try:
        return self.create_lead(name, email, **kwargs)
    except HTTPError as e:
        if e.response.status_code == 422:
            error_data = e.response.json()
            print(f"Validation error: {error_data.get('message')}")
        elif e.response.status_code == 429:
            print("Rate limit exceeded. Retry after delay.")
        else:
            print(f"HTTP error: {e}")
        return None

# Usage
lead = client.safe_create_lead("John Doe", "john@example.com")
if lead:
    print(f"Created: {lead['id']}")
else:
    print("Failed to create lead")
```

---

## Summary

### Key Takeaways

1. **Standard REST Pattern**: All entities follow the same CRUD pattern
2. **Required Fields**: Vary by entity (Leads: `name`, People: `name`, Companies: `name`, Opportunities: `name` + `primary_contact_id`)
3. **Partial Updates**: Only specified fields are updated in PUT requests
4. **UPSERT**: Prevents duplicates by matching on name, email, or custom fields
5. **Bulk Operations**: Process up to 10 records per request with 3 req/sec limit
6. **Custom Fields**: Supported on all entities via `custom_fields` array
7. **Pagination**: Use `page_number` and `page_size` with max 200 per page
8. **Rate Limits**: 180 req/min for standard APIs, 3 req/sec for bulk APIs

### Best Practices

1. Always validate data client-side before sending
2. Use UPSERT to prevent duplicate leads
3. Implement exponential backoff for rate limit errors
4. Store API keys securely, never hardcode
5. Use pagination for large datasets
6. Handle errors gracefully with proper HTTP status codes
7. Use bulk operations for batch processing
8. Sort by `date_modified` for incremental syncs
