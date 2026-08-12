---
name: copper-crm
description: >-
  Comprehensive Copper CRM management skill for CRUD and search operations on
  Leads, People, Companies, and Opportunities. Includes helper scripts,
  templates, error handling, and rate limiting strategies.
when_to_use: >-
  Use when managing Copper CRM data, creating/updating leads, syncing contacts,
  tracking opportunities, bulk imports, integrating with Copper API, working
  with sales pipeline, crm management, bulk import, upsert, or rate limiting.
version: 1.0.0
category: integrations-and-saas
---

# Copper CRM Management

Complete skill for managing Copper CRM data through API operations with support for CRUD operations, search, bulk imports, and automation.

## Overview

This skill provides comprehensive tooling for Copper CRM API interactions:

- **Entities Supported:** Leads, People, Companies, Opportunities, Activities, Tasks, Projects
- **Operations:** Create, Read, Update, Delete, Search, Bulk Import, Convert Leads
- **Authentication:** API Key-based with environment configuration
- **Rate Limiting:** Automatic handling (180 req/min standard, 3 req/sec bulk)
- **Error Recovery:** Exponential backoff, UPSERT deduplication, retry logic

**API Documentation:** https://developer.copper.com
**Base URL:** `https://api.copper.com/developer_api/v1`

---

## Prerequisites

### Required

1. **Copper CRM Account** with API access
2. **API Key** - Generate at: Settings > Integrations > API Keys
3. **User Email** - Email address that generated the API key
4. **Python 3.11+** (for helper scripts)

### Recommended

- Admin user credentials for full data access
- Dedicated integration user (not personal account)
- Understanding of team permissions

---

## Quick Start

### 1. First-Time Setup

```bash
# Run setup script
$HOME/.claude/skills/copper-crm/scripts/setup.sh

# This will:
# - Check Python 3.11+
# - Install dependencies (requests, python-dotenv, rich)
# - Create .env from template
# - Test API connection
# - Cache metadata (users, custom fields, pipelines)
```

### 2. Configure Credentials

Edit `.env` file:

```bash
COPPER_API_KEY=your_api_key_here
COPPER_USER_EMAIL=your.email@company.com
COPPER_BASE_URL=https://api.copper.com/developer_api/v1
```

### 3. Test Connection

```bash
python scripts/test_connection.py

# Output:
# ✓ Credentials loaded
# ✓ Authentication successful
# ✓ Account: Your Company (ID: 123456)
# ✓ User: your.email@company.com (Admin)
# ✓ Rate limit test: 5/5 requests successful
```

### 4. First API Call

```bash
# Using CLI tool
python scripts/copper_cli.py create lead

# Or using templates
curl -X POST "https://api.copper.com/developer_api/v1/leads" \
  -H "X-PW-AccessToken: YOUR_KEY" \
  -H "X-PW-Application: developer_api" \
  -H "X-PW-UserEmail: your.email@company.com" \
  -H "Content-Type: application/json" \
  -d @templates/lead_template.json
```

---

## Core Tasks

### Task 1: Create a Lead

**CLI Method:**
```bash
python scripts/copper_cli.py create lead
# Interactive prompts for all fields
```

**API Call:**
```bash
POST /leads
{
  "name": "John Doe",
  "email": {
    "email": "john@example.com",
    "category": "work"
  },
  "company_name": "Acme Corp",
  "title": "VP of Sales",
  "phone_numbers": [{
    "number": "415-555-1234",
    "category": "mobile"
  }]
}
```

**Required Fields:** `name`
**Unique Constraints:** None (duplicates allowed)

### Task 2: Create a Person (Contact)

**⚠️ CRITICAL: Email addresses must be unique across all People records.**

```bash
POST /people
{
  "name": "Jane Smith",
  "emails": [{
    "email": "jane@example.com",
    "category": "work"
  }],
  "company_id": 9607580,
  "title": "CTO"
}
```

**Required Fields:** `name`
**Unique Constraints:** Email address (returns 422 if duplicate)

**Best Practice:** Use UPSERT to prevent duplicates:
```bash
PUT /leads/upsert
{
  "properties": { ...person data... },
  "match": {
    "field_name": "email",
    "field_value": "jane@example.com"
  }
}
```

### Task 3: Create a Company

**⚠️ CRITICAL: Email domains must be unique across all Company records.**

```bash
POST /companies
{
  "name": "TechCo",
  "email_domain": "techco.com",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105"
  }
}
```

**Required Fields:** `name`
**Unique Constraints:** Email domain (returns 422 if duplicate)

### Task 4: Create an Opportunity

```bash
POST /opportunities
{
  "name": "Q1 Enterprise Deal",
  "primary_contact_id": 27140359,
  "company_id": 9607580,
  "monetary_value": 50000,
  "close_date": "03/31/2024",
  "pipeline_id": 512676,
  "pipeline_stage_id": 982538,
  "priority": "High"
}
```

**Required Fields:** `name`, `primary_contact_id`
**Date Format:** `mm/dd/yyyy` (NOT Unix timestamp)

### Task 5: Search & Filter

```bash
POST /leads/search
{
  "page_size": 200,
  "page_number": 1,
  "sort_by": "date_modified",
  "sort_direction": "desc",
  "status_ids": [208231],
  "assignee_ids": [137658],
  "minimum_created_date": 1609459200,
  "tags": ["enterprise", "hot-lead"]
}
```

**Pagination Limits:**
- Max page size: 200 records
- Max total records: 100,000 (first matching only)
- Default: 20 records per page

**Response Header:** `X-PW-TOTAL` shows total matching records

### Task 6: Update a Record

```bash
PUT /leads/12345
{
  "status": "Qualified",
  "details": "Spoke with prospect, very interested",
  "custom_fields": [{
    "custom_field_definition_id": 100764,
    "value": "Enterprise"
  }]
}
```

**Behavior:**
- Only provided fields are updated
- Set field to `null` to clear value
- Set `tags: []` to remove all tags

### Task 7: Convert Lead to Opportunity

```bash
POST /leads/12345/convert
{
  "details": {
    "person": { "name": "Jane Smith" },
    "company": { "name": "TechCo" },
    "opportunity": {
      "name": "TechCo - Annual Contract",
      "monetary_value": 100000,
      "pipeline_id": 213214
    }
  }
}
```

**Returns:** `{person: {...}, company: {...}, opportunity: {...}}`
**Note:** Lead is deleted after successful conversion

### Task 8: Bulk Import from CSV

```bash
python scripts/bulk_import.py leads import.csv --mode upsert

# CSV Format (auto-detected headers):
# name,email,company_name,title,phone
# John Doe,john@example.com,Acme Corp,VP Sales,415-555-1234
```

**Features:**
- Batch processing (10 records per batch)
- Rate limiting (3 req/sec)
- UPSERT mode (prevents duplicates)
- Error recovery with retries
- Progress bar with rich library
- Summary report

---

## Command Reference

### Helper Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup.sh` | First-time setup | `./scripts/setup.sh` |
| `test_connection.py` | Test API connectivity | `python scripts/test_connection.py` |
| `validate_config.py` | Validate configuration | `python scripts/validate_config.py` |
| `copper_cli.py` | Interactive CLI tool | `python scripts/copper_cli.py interactive` |
| `bulk_import.py` | Bulk CSV import | `python scripts/bulk_import.py leads file.csv` |

### CLI Commands

```bash
# Interactive mode
python copper_cli.py interactive

# Create records
python copper_cli.py create lead
python copper_cli.py create person
python copper_cli.py create company
python copper_cli.py create opportunity

# Search records
python copper_cli.py search leads -q "john" -f "status=Qualified" -l 50

# Update record
python copper_cli.py update lead 12345

# Delete record
python copper_cli.py delete lead 12345

# Bulk import
python copper_cli.py bulk-import data.csv -e leads --upsert -u email
```

---

## Configuration Files

### Environment Variables (.env)

```bash
COPPER_API_KEY=your_api_key_here
COPPER_USER_EMAIL=your.email@company.com
COPPER_BASE_URL=https://api.copper.com/developer_api/v1
COPPER_RATE_LIMIT_STANDARD=180  # requests per minute
COPPER_RATE_LIMIT_BULK=3        # requests per second
COPPER_MAX_RETRIES=5
COPPER_RETRY_DELAY=1
```

### Templates Available

| Template | Path | Purpose |
|----------|------|---------|
| Lead | `templates/lead_template.json` | Lead creation reference |
| Person | `templates/person_template.json` | Person creation reference |
| Company | `templates/company_template.json` | Company creation reference |
| Opportunity | `templates/opportunity_template.json` | Opportunity creation reference |
| Search | `templates/search_template.json` | Search query examples |
| CSV Import | `templates/bulk_import_template.csv` | Bulk import format |

---

## Proven Patterns

### Pattern 1: UPSERT to Prevent Duplicates

**Problem:** Creating duplicate People/Companies returns 422 error

**Solution:** Use UPSERT pattern

```bash
PUT /leads/upsert
{
  "properties": {
    "name": "John Doe",
    "email": {
      "email": "john@example.com",
      "category": "work"
    }
  },
  "match": {
    "field_name": "email",
    "field_value": "john@example.com"
  }
}
```

**Outcomes:**
- 0 matches: Creates new record
- 1 match: Updates existing record
- 2-30 matches: Returns 422 with matching IDs
- 30+ matches: Returns 422 without IDs

### Pattern 2: Rate Limit Handling with Exponential Backoff

```python
import time
import requests

def api_call_with_retry(url, headers, data, max_retries=5):
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response

        if response.status_code == 429:
            wait_time = 2 ** attempt  # 1s, 2s, 4s, 8s, 16s
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue

        return response

    raise Exception("Max retries exceeded")
```

### Pattern 3: Pagination for Large Datasets

```python
def fetch_all_leads(filters):
    page_number = 1
    all_leads = []

    while True:
        response = search_leads({
            "page_size": 200,
            "page_number": page_number,
            "sort_by": "date_modified",
            "sort_direction": "desc",
            **filters
        })

        leads = response.json()
        all_leads.extend(leads)

        # Last page if fewer than page_size
        if len(leads) < 200:
            break

        page_number += 1

    return all_leads
```

### Pattern 4: Lead Lifecycle Workflow

```bash
# Step 1: Create lead
POST /leads
{"name": "Jane Smith", "email": {"email": "jane@techco.com"}}
# Returns: {"id": 12345}

# Step 2: Add activity (qualification)
POST /activities
{
  "parent": {"type": "lead", "id": 12345},
  "type": {"category": "user", "id": 0},
  "details": "Qualified - budget confirmed"
}

# Step 3: Update status
PUT /leads/12345
{"status": "Qualified"}

# Step 4: Convert to opportunity
POST /leads/12345/convert
{
  "details": {
    "opportunity": {
      "name": "TechCo Deal",
      "monetary_value": 100000
    }
  }
}
```

### Pattern 5: Bulk Import with Error Recovery

```python
def bulk_import_with_recovery(records):
    results = {"success": [], "failed": []}

    # Process in batches of 10
    for i in range(0, len(records), 10):
        batch = records[i:i+10]

        response = bulk_create_leads(batch)

        for idx, result in enumerate(response):
            if "id" in result:
                results["success"].append(result)
            else:
                # Retry individual failed record
                retry = create_lead(batch[idx])
                if retry.status_code == 200:
                    results["success"].append(retry.json())
                else:
                    results["failed"].append({
                        "record": batch[idx],
                        "error": retry.json()
                    })

        time.sleep(0.334)  # Rate limit: 3/sec

    return results
```

---

## Troubleshooting

### Issue 1: 401 Unauthorized

**Symptoms:**
```json
{"message": "Unauthorized", "status": 401}
```

**Causes:**
- Missing/invalid API key
- Wrong email address
- Missing required headers

**Solutions:**
1. Run `python scripts/validate_config.py` to check credentials
2. Verify all headers are present:
   ```
   X-PW-AccessToken: YOUR_KEY
   X-PW-Application: developer_api
   X-PW-UserEmail: YOUR_EMAIL
   Content-Type: application/json
   ```
3. Regenerate API key in Copper if necessary

### Issue 2: 422 Duplicate Email/Domain

**Symptoms:**
```json
{"message": "Email address already exists", "status": 422}
```

**Causes:**
- People: Email already exists in database
- Companies: Email domain already exists

**Solutions:**
1. Use UPSERT pattern (see Pattern 1)
2. Search before creating:
   ```bash
   POST /people/fetch_by_email
   {"email": "john@example.com"}
   ```
3. For bulk imports, use `--mode upsert`

### Issue 3: 429 Rate Limit Exceeded

**Symptoms:**
```json
{"message": "Rate limit exceeded", "status": 429}
```

**Causes:**
- More than 180 requests/minute (standard)
- More than 3 requests/second (bulk)

**Solutions:**
1. Implement exponential backoff (see Pattern 2)
2. Wait 60 seconds before retrying
3. For bulk operations:
   ```python
   time.sleep(0.334)  # 3 req/sec = 333ms between
   ```
4. Use bulk endpoints instead of individual calls

### Issue 4: Search Returns 0 Results

**Causes:**
- Filters too restrictive (AND logic)
- Not using `allow_empty` for optional fields

**Solutions:**
1. Use `allow_empty` for optional fields:
   ```json
   {
     "city": {
       "allow_empty": true,
       "value": "San Francisco"
     }
   }
   ```
2. Remove some filter criteria
3. Check filter values are correct (IDs, dates, etc.)

### Issue 5: Pagination Missing Records

**Causes:**
- Not sorting results (records shift between pages)
- Records added/modified during pagination

**Solutions:**
1. **Always sort results:**
   ```json
   {
     "sort_by": "date_modified",
     "sort_direction": "desc"
   }
   ```
2. Use stable sort field (`id`, `date_created`)
3. For incremental sync, use date filters:
   ```json
   {"minimum_modified_date": last_sync_timestamp}
   ```

---

## Helper Scripts Reference

### setup.sh

**Purpose:** First-time skill setup

**Actions:**
- Checks Python 3.11+
- Installs dependencies (requests, python-dotenv, rich)
- Creates `.env` from template
- Prompts for API credentials
- Tests API connection
- Caches metadata (users, custom fields, pipelines)

**Usage:**
```bash
./scripts/setup.sh
```

### validate_config.py

**Purpose:** Validate API configuration

**Checks:**
- `.env` file exists with required variables
- API key is valid
- Email format is correct
- Authentication successful
- Rate limit status
- User permissions

**Usage:**
```bash
python scripts/validate_config.py
```

**Exit Codes:**
- 0: All validations passed
- 1: Configuration error
- 2: API communication error
- 3: Missing required variables

### test_connection.py

**Purpose:** Quick API connectivity test

**Tests:**
- Credentials loading
- GET /account endpoint
- Account info display
- Rate limit test (5 requests)
- User permissions check

**Usage:**
```bash
python scripts/test_connection.py
```

### copper_cli.py

**Purpose:** Interactive CLI for CRUD operations

**Features:**
- Interactive menus for all entities
- Field validation and prompts
- Search with filters
- Bulk import from CSV
- Error handling with retry
- Progress indicators

**Usage:**
```bash
# Interactive mode
python scripts/copper_cli.py interactive

# Direct commands
python scripts/copper_cli.py create lead
python scripts/copper_cli.py search people -q "john"
python scripts/copper_cli.py update company 12345
python scripts/copper_cli.py bulk-import data.csv -e leads
```

### bulk_import.py

**Purpose:** Bulk CSV data import

**Features:**
- CSV parsing with auto-header detection
- Validation before import
- UPSERT mode (duplicate prevention)
- Batch processing (10 per batch)
- Rate limiting (3 req/sec)
- Error recovery with retries
- Progress bar
- Summary report

**Usage:**
```bash
python scripts/bulk_import.py leads import.csv --mode upsert
python scripts/bulk_import.py people contacts.csv --mode create
```

**CSV Headers (auto-detected):**
- Leads: `name, email, company_name, title, phone`
- People: `name, email, company_name, title`
- Companies: `name, email_domain, address`
- Opportunities: `name, primary_contact_email, monetary_value`

---

## ⚠️ Workflow Requirements (MANDATORY)

### Before ANY API Call

⚠️ **MANDATORY: Check credentials are configured**
```bash
python scripts/validate_config.py
```

⚠️ **MANDATORY: Implement retry logic for 429 errors**
```python
# Always use exponential backoff (see Pattern 2)
```

⚠️ **MANDATORY: Validate data before sending**
```python
# Check required fields, data types, uniqueness constraints
```

### Creating People or Companies

⚠️ **MANDATORY: Check for duplicates**
- People: Email address must be unique
- Companies: Email domain must be unique

⚠️ **MANDATORY: Use UPSERT pattern when possible**
```bash
PUT /leads/upsert  # Instead of POST /leads
```

### Bulk Operations

⚠️ **MANDATORY: Never exceed 10 records per batch**
```python
for i in range(0, len(records), 10):
    batch = records[i:i+10]
    # Process batch
```

⚠️ **MANDATORY: Respect 3 requests/second rate limit**
```python
time.sleep(0.334)  # Between bulk requests
```

⚠️ **MANDATORY: Handle partial failures**
```python
# Check each result in response for success/failure
# Retry failed records individually
```

### Pagination

⚠️ **MANDATORY: Always sort results by stable field**
```json
{
  "sort_by": "date_modified",
  "sort_direction": "desc"
}
```

⚠️ **MANDATORY: Handle 100k record limit**
```python
# Use date-based sharding for large datasets
# Example: monthly chunks for datasets > 100k
```

---

## Common Workflows

### Workflow 1: Lead to Opportunity Conversion

```bash
# 1. Create lead
POST /leads
{"name": "Jane Smith", "email": {"email": "jane@techco.com"}}

# 2. Qualify with activity
POST /activities
{
  "parent": {"type": "lead", "id": 12345},
  "details": "Budget confirmed, decision timeline 30 days"
}

# 3. Update status
PUT /leads/12345
{"status": "Qualified"}

# 4. Convert to opportunity
POST /leads/12345/convert
{
  "details": {
    "person": {"name": "Jane Smith"},
    "company": {"name": "TechCo"},
    "opportunity": {
      "name": "TechCo - Annual Contract",
      "monetary_value": 100000
    }
  }
}
```

### Workflow 2: Bulk Import with Deduplication

```bash
# Step 1: Prepare CSV file
# name,email,company_name,title
# John Doe,john@acme.com,Acme Corp,VP Sales
# Jane Smith,jane@techco.com,TechCo,CTO

# Step 2: Run bulk import with UPSERT
python scripts/bulk_import.py leads contacts.csv --mode upsert

# Output:
# Processing 100 records...
# [========================================] 100/100
#
# Summary:
# ✓ Successful: 85
# ✓ Updated (duplicates): 10
# ✗ Failed: 5
```

### Workflow 3: Incremental Data Sync

```python
# Store last sync timestamp
last_sync = load_last_sync_timestamp()  # e.g., 1640995200

# Fetch modified records
response = search_leads({
    "page_size": 200,
    "minimum_modified_date": last_sync,
    "sort_by": "date_modified",
    "sort_direction": "asc"
})

# Process records
for lead in response:
    update_local_database(lead)

# Update sync timestamp
save_last_sync_timestamp(current_timestamp())
```

### Workflow 4: Opportunity Pipeline Tracking

```bash
# 1. Create opportunity
POST /opportunities
{
  "name": "Q1 Deal",
  "primary_contact_id": 27140359,
  "monetary_value": 50000,
  "pipeline_stage_id": 982538  # "Proposal Sent"
}

# 2. Add activity
POST /activities
{
  "parent": {"type": "opportunity", "id": 8765432},
  "details": "Demo completed, moving to contract"
}

# 3. Update stage
PUT /opportunities/8765432
{"pipeline_stage_id": 982539}  # "Contract Negotiation"

# 4. Close won
PUT /opportunities/8765432
{
  "status": "Won",
  "close_date": "03/15/2024"
}
```

---

## Tips

**Authentication:**
- Use admin user for API integrations (unrestricted access)
- Create dedicated integration user (not personal account)
- Store API keys in environment variables, never hardcode
- Rotate keys periodically

**Data Quality:**
- Validate emails before creating People records
- Check domains before creating Companies
- Use UPSERT for external data sources
- Clean phone numbers (remove non-numeric except + and spaces)

**Performance:**
- Use bulk endpoints for >10 records
- Maximize page_size (200) for searches
- Cache metadata (users, custom fields, pipelines)
- Implement connection pooling for high-volume use

**Error Handling:**
- Always implement retry with exponential backoff
- Log all errors with request context
- Monitor rate limit usage
- Validate data client-side before API calls

**Custom Fields:**
- Get definitions first: `GET /custom_field_definitions`
- Store field IDs for reuse
- Validate option IDs for dropdowns
- Use correct data types (number vs string)

**Rate Limiting:**
- Standard: 180 requests/minute
- Bulk: 3 requests/second
- Use token bucket or queue patterns
- Monitor X-RateLimit-* headers

**Search Optimization:**
- Always sort by stable field
- Use `allow_empty` for optional filters
- Break large datasets into time chunks
- For >100k records, use date-based sharding

**Security:**
- Never commit `.env` file to git
- Use `.gitignore` for credentials
- Implement audit logging
- Monitor for unusual API usage patterns

---

## Reference Documentation

For detailed information, see:

- **API Reference:** `references/api-reference.md` - Complete endpoint documentation
- **CRUD Patterns:** `references/crud-patterns.md` - Entity-specific CRUD examples
- **Search Guide:** `references/search-guide.md` - Advanced search and filtering
- **Error Handling:** `references/error-handling.md` - Error codes and recovery strategies
- **Workflows:** `references/workflows.md` - Step-by-step common workflows
- **Rate Limiting:** `references/rate-limiting.md` - Rate limit management strategies

---

## Quick Reference Card

### Authentication Headers
```
X-PW-AccessToken: YOUR_API_KEY
X-PW-Application: developer_api
X-PW-UserEmail: your.email@company.com
Content-Type: application/json
```

### Rate Limits
- Standard: 180 requests/minute
- Bulk: 3 requests/second
- Max page size: 200
- Max total records: 100,000

### Required Fields
- Leads: `name`
- People: `name`
- Companies: `name`
- Opportunities: `name`, `primary_contact_id`

### Unique Constraints
- People: Email address
- Companies: Email domain

### Date Formats
- Most fields: Unix timestamp (10-digit integer)
- close_date, due_date: `mm/dd/yyyy`

### HTTP Status Codes
- 200: Success
- 401: Invalid credentials
- 422: Validation error (duplicates, missing fields)
- 429: Rate limit exceeded
- 500: Server error (retry)

### Helper Scripts
```bash
./scripts/setup.sh                    # First-time setup
python scripts/test_connection.py     # Test API
python scripts/validate_config.py     # Validate config
python scripts/copper_cli.py interactive  # CLI tool
python scripts/bulk_import.py leads file.csv  # Bulk import
```
