# Copper CRM Search & Filtering Guide

## Overview

This guide covers advanced search and filtering capabilities in Copper CRM, including pagination strategies, filter options, and common search patterns.

## Search Endpoint Pattern

All search operations in Copper CRM follow a consistent POST pattern:

```
POST /api/v1/{entity}/search
```

### Supported Entities
- `people` - Contact records
- `companies` - Company/Account records
- `opportunities` - Deal/Opportunity records
- `leads` - Lead records
- `tasks` - Task records
- `projects` - Project records

---

## Core Search Structure

### Basic Search Request

```json
{
  "page_number": 1,
  "page_size": 20,
  "sort_by": "field_name",
  "sort_direction": "asc",
  "filters": {
    // Entity-specific filters
  },
  "fields": [
    // Optional: specify fields to return
  ]
}
```

### Parameters

| Parameter | Type | Description | Default | Limits |
|-----------|------|-------------|---------|--------|
| `page_number` | integer | Page to retrieve (1-indexed) | 1 | Max varies by entity |
| `page_size` | integer | Records per page | 20 | Min: 1, Max: 200 |
| `sort_by` | string | Field to sort by | varies | Must be valid field |
| `sort_direction` | string | Sort order: `asc` or `desc` | `asc` | - |
| `filters` | object | Filter criteria | {} | See entity filters |
| `fields` | array | Fields to include in response | all | Optional optimization |

---

## Pagination Strategies

### Standard Pagination

```json
{
  "page_number": 1,
  "page_size": 100
}
```

**Best Practices:**
- Use `page_size: 100` for bulk operations (better than 200 smaller requests)
- Use `page_size: 20-50` for UI/interactive operations
- Always handle empty result sets (indicates last page reached)

### Calculating Total Pages

```javascript
// Response typically includes total count
const response = await searchCompanies({ page_number: 1, page_size: 100 });
const totalRecords = response.total_count;
const pageSize = 100;
const totalPages = Math.ceil(totalRecords / pageSize);

// Iterate through all pages
for (let page = 1; page <= totalPages; page++) {
  const results = await searchCompanies({
    page_number: page,
    page_size: pageSize,
    filters: yourFilters
  });
  // Process results
}
```

### Handling 100k Record Limit

Copper CRM limits total searchable records to approximately 100,000 per query. For large datasets:

**Strategy 1: Date-Based Partitioning**
```json
{
  "filters": {
    "created_after": "2024-01-01",
    "created_before": "2024-03-31"
  }
}
```

**Strategy 2: ID-Based Cursor**
```json
{
  "filters": {
    "minimum_id": 1000000
  },
  "sort_by": "id",
  "sort_direction": "asc"
}
```

**Strategy 3: Assignee-Based Sharding**
```json
// Search per assignee to partition dataset
{
  "filters": {
    "assignee_id": 12345
  }
}
```

### Sorting Options

#### Common Sort Fields by Entity

**People:**
- `first_name`, `last_name`, `email`, `created_at`, `updated_at`, `company_name`

**Companies:**
- `name`, `annual_revenue`, `created_at`, `updated_at`, `employee_count`

**Opportunities:**
- `name`, `close_date`, `monetary_value`, `created_at`, `updated_at`, `win_probability`

**Direction:**
- `asc` - Ascending (A-Z, 0-9, oldest first)
- `desc` - Descending (Z-A, 9-0, newest first)

---

## Filter Options by Entity

### People (Contacts) Filters

```json
{
  "filters": {
    // Name filters
    "first_name": "John",
    "last_name": "Doe",
    "name": "John Doe",                    // Searches both first and last

    // Contact info
    "email": "john@example.com",           // Exact or partial match
    "phone_number": "415-555-1234",        // See phone search section

    // Relationships
    "company_id": 12345,
    "company_name": "Acme Corp",

    // Classification
    "job_title": "VP of Sales",
    "tags": ["decision-maker", "champion"],

    // Assignment
    "assignee_id": 67890,

    // Date ranges
    "created_after": "2024-01-01",
    "created_before": "2024-12-31",
    "updated_after": "2024-06-01",
    "updated_before": "2024-06-30",

    // Custom fields
    "custom_fields": {
      "contact_tier": "A",
      "lead_score": 85
    }
  }
}
```

### Companies Filters

```json
{
  "filters": {
    // Basic info
    "name": "Acme",                        // Partial match supported

    // Classification
    "industry": "Technology",
    "tags": ["enterprise", "tech-stack"],

    // Financial
    "annual_revenue_min": 1000000,
    "annual_revenue_max": 100000000,
    "employee_count_min": 50,
    "employee_count_max": 500,

    // Assignment
    "assignee_id": 12345,

    // Contact info
    "email": "contact@acme.com",
    "phone_number": "415-555-0000",
    "city": "San Francisco",
    "state": "CA",
    "country": "US",
    "postal_code": "94102",

    // Date ranges
    "created_after": "2024-01-01",
    "created_before": "2024-12-31",
    "updated_after": "2024-06-01",

    // Custom fields
    "custom_fields": {
      "company_tier": "Enterprise",
      "market_segment": "Financial Services"
    }
  }
}
```

### Opportunities Filters

```json
{
  "filters": {
    // Basic info
    "name": "Deal Name",

    // Status and pipeline
    "status": "Open",                      // "Open", "Won", "Lost", "Abandoned"
    "pipeline_id": 1,
    "stage_id": 2,
    "win_probability_min": 50,
    "win_probability_max": 100,

    // Financial
    "monetary_value_min": 10000,
    "monetary_value_max": 500000,

    // Dates
    "close_date_after": "2025-01-01",
    "close_date_before": "2025-12-31",
    "created_after": "2024-01-01",
    "updated_after": "2024-11-01",

    // Relationships
    "company_id": 12345,
    "primary_contact_id": 67890,
    "assignee_id": 11111,

    // Classification
    "tags": ["hot-lead", "enterprise"],
    "customer_source_id": 3,
    "loss_reason_id": null,                // Filter by lost reason

    // Activity
    "interaction_count_min": 5,
    "interaction_count_max": 20,

    // Custom fields
    "custom_fields": {
      "deal_size": "Large",
      "contract_length": "2 Years"
    }
  }
}
```

### Leads Filters

```json
{
  "filters": {
    "name": "Lead Name",
    "email": "lead@example.com",
    "phone_number": "415-555-1234",
    "status": "New",
    "assignee_id": 12345,
    "customer_source_id": 1,
    "tags": ["inbound", "webinar"],
    "created_after": "2024-01-01",
    "custom_fields": {
      "lead_score": 75
    }
  }
}
```

---

## Custom Field Search

### Understanding Custom Fields

Custom fields in Copper are defined per entity type and can be:
- Text fields
- Numeric fields
- Dropdown selections
- Date fields
- Multi-select fields
- Checkboxes

### Searching Custom Fields

```json
{
  "filters": {
    "custom_fields": {
      "field_name_1": "exact_value",
      "field_name_2": 12345,
      "field_name_3": ["option1", "option2"]  // Multi-select
    }
  }
}
```

### Examples

**Text Custom Field:**
```json
{
  "custom_fields": {
    "company_tier": "Enterprise"
  }
}
```

**Numeric Custom Field:**
```json
{
  "custom_fields": {
    "lead_score": 85,
    "contract_value": 50000
  }
}
```

**Date Custom Field:**
```json
{
  "custom_fields": {
    "renewal_date": "2025-12-31"
  }
}
```

**Dropdown/Multi-select:**
```json
{
  "custom_fields": {
    "product_interest": ["Product A", "Product B"],
    "account_status": "Active"
  }
}
```

### Custom Field Best Practices

1. **Get field definitions first** - Use `/custom_field_definitions` endpoint
2. **Match exact values** - Custom field searches are typically exact match
3. **Use correct data types** - Numbers as integers, dates as ISO strings
4. **Case sensitivity** - Depends on field type; typically case-insensitive for text

---

## Phone Number Search

Phone number search in Copper supports both fuzzy and partial matching.

### Search Modes

**Partial Match (Default):**
```json
{
  "filters": {
    "phone_number": "555-1234"  // Matches any number containing this
  }
}
```

**Fuzzy Match:**
Copper normalizes phone numbers, so these all match the same record:
```json
// All of these match +1-415-555-1234
"phone_number": "415-555-1234"
"phone_number": "(415) 555-1234"
"phone_number": "4155551234"
"phone_number": "+14155551234"
```

### Phone Number Best Practices

1. **Remove formatting** - Search with digits only for best results
2. **Use partial matches** - Last 4 digits or area code + exchange
3. **Consider country codes** - International numbers may need +country prefix

### Examples

**Find by area code:**
```json
{
  "filters": {
    "phone_number": "415"
  }
}
```

**Find by last 4 digits:**
```json
{
  "filters": {
    "phone_number": "1234"
  }
}
```

**Find exact number (any format):**
```json
{
  "filters": {
    "phone_number": "4155551234"
  }
}
```

---

## Tags Search

Tags enable flexible categorization across all entities.

### Single Tag

```json
{
  "filters": {
    "tags": ["enterprise"]
  }
}
```

### Multiple Tags (OR Logic)

```json
{
  "filters": {
    "tags": ["enterprise", "tech-stack", "high-value"]
  }
}
```

**Behavior:** Returns records that have ANY of the specified tags.

### Tag Best Practices

1. **Case sensitivity** - Tags are case-insensitive
2. **Exact match** - Tag names must match exactly
3. **Normalization** - Spaces and special characters preserved
4. **Bulk tagging** - Use tags for batch operations

### Common Tag Patterns

**Lead Qualification:**
```json
"tags": ["qualified", "sql", "mql"]
```

**Account Segmentation:**
```json
"tags": ["enterprise", "mid-market", "smb"]
```

**Campaign Tracking:**
```json
"tags": ["webinar-2024-q1", "trade-show", "inbound"]
```

**Deal Stage Markers:**
```json
"tags": ["hot-lead", "negotiation", "legal-review"]
```

---

## Date Range Filtering

### Standard Date Filters

All entities support created/updated date filtering:

```json
{
  "filters": {
    "created_after": "2024-01-01",
    "created_before": "2024-12-31",
    "updated_after": "2024-11-01",
    "updated_before": "2024-11-30"
  }
}
```

### Date Format

**ISO 8601 Format:** `YYYY-MM-DD`

**Examples:**
- `2024-01-01` - January 1, 2024
- `2024-12-31` - December 31, 2024

### Timestamp Precision

Dates are typically treated as:
- `created_after`: Start of day (00:00:00)
- `created_before`: End of day (23:59:59)

### Common Date Range Patterns

**Last 7 days:**
```javascript
const today = new Date();
const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);

{
  "filters": {
    "created_after": sevenDaysAgo.toISOString().split('T')[0]
  }
}
```

**Current month:**
```javascript
const now = new Date();
const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);

{
  "filters": {
    "created_after": firstDay.toISOString().split('T')[0],
    "created_before": lastDay.toISOString().split('T')[0]
  }
}
```

**Current quarter:**
```javascript
const now = new Date();
const quarter = Math.floor(now.getMonth() / 3);
const firstDay = new Date(now.getFullYear(), quarter * 3, 1);
const lastDay = new Date(now.getFullYear(), quarter * 3 + 3, 0);

{
  "filters": {
    "created_after": firstDay.toISOString().split('T')[0],
    "created_before": lastDay.toISOString().split('T')[0]
  }
}
```

**Year to date:**
```javascript
const now = new Date();
const startOfYear = new Date(now.getFullYear(), 0, 1);

{
  "filters": {
    "created_after": startOfYear.toISOString().split('T')[0]
  }
}
```

### Entity-Specific Date Filters

**Opportunities:**
```json
{
  "filters": {
    "close_date_after": "2025-01-01",
    "close_date_before": "2025-12-31"
  }
}
```

**Tasks:**
```json
{
  "filters": {
    "due_date_after": "2024-11-01",
    "due_date_before": "2024-11-30",
    "completed_date_after": "2024-10-01"
  }
}
```

---

## Search Examples - Common Scenarios

### 1. Find All Open High-Value Opportunities

```json
{
  "page_size": 100,
  "sort_by": "monetary_value",
  "sort_direction": "desc",
  "filters": {
    "status": "Open",
    "monetary_value_min": 50000,
    "win_probability_min": 50,
    "tags": ["enterprise"]
  }
}
```

**Use Case:** Sales dashboard, pipeline review

---

### 2. Find Recently Updated Enterprise Companies

```json
{
  "page_size": 50,
  "sort_by": "updated_at",
  "sort_direction": "desc",
  "filters": {
    "tags": ["enterprise"],
    "updated_after": "2024-11-01",
    "annual_revenue_min": 5000000
  }
}
```

**Use Case:** Activity monitoring, account review

---

### 3. Find Decision Makers at Target Accounts

```json
{
  "page_size": 100,
  "sort_by": "last_name",
  "sort_direction": "asc",
  "filters": {
    "company_id": 12345,
    "tags": ["decision-maker", "champion"],
    "custom_fields": {
      "contact_tier": "A"
    }
  }
}
```

**Use Case:** Deal strategy, stakeholder mapping

---

### 4. Find Stale Opportunities (No Recent Activity)

```json
{
  "page_size": 100,
  "sort_by": "updated_at",
  "sort_direction": "asc",
  "filters": {
    "status": "Open",
    "updated_before": "2024-09-01",
    "assignee_id": 12345
  }
}
```

**Use Case:** Pipeline cleanup, follow-up reminders

---

### 5. Find Contacts Without Companies

```json
{
  "page_size": 100,
  "filters": {
    "company_id": null
  }
}
```

**Use Case:** Data hygiene, enrichment tasks

---

### 6. Find Tech Companies in San Francisco

```json
{
  "page_size": 100,
  "sort_by": "name",
  "filters": {
    "industry": "Technology",
    "city": "San Francisco",
    "state": "CA",
    "employee_count_min": 10
  }
}
```

**Use Case:** Territory planning, prospecting

---

### 7. Find Closing Opportunities This Quarter

```json
{
  "page_size": 100,
  "sort_by": "close_date",
  "sort_direction": "asc",
  "filters": {
    "status": "Open",
    "close_date_after": "2024-10-01",
    "close_date_before": "2024-12-31",
    "win_probability_min": 60
  }
}
```

**Use Case:** Forecast accuracy, resource planning

---

### 8. Find Unassigned Leads

```json
{
  "page_size": 100,
  "sort_by": "created_at",
  "sort_direction": "desc",
  "filters": {
    "assignee_id": null,
    "status": "New"
  }
}
```

**Use Case:** Lead distribution, queue management

---

### 9. Find VIP Contacts (Multiple Criteria)

```json
{
  "page_size": 50,
  "sort_by": "last_name",
  "filters": {
    "job_title": "VP",
    "tags": ["decision-maker"],
    "custom_fields": {
      "contact_tier": "A",
      "executive_level": "C-Suite"
    }
  }
}
```

**Use Case:** Executive engagement, relationship mapping

---

### 10. Bulk Export All Companies (Pagination Pattern)

```javascript
async function exportAllCompanies() {
  const allCompanies = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await searchCompanies({
      page_number: page,
      page_size: 200,
      sort_by: "id",
      sort_direction: "asc"
    });

    allCompanies.push(...response.data);
    hasMore = response.data.length === 200;
    page++;

    // Respect rate limits
    await sleep(100);
  }

  return allCompanies;
}
```

**Use Case:** Data export, backup, migration

---

## Performance Optimization

### Field Selection

Only request fields you need:

```json
{
  "fields": [
    "id",
    "name",
    "email",
    "company_id"
  ]
}
```

**Benefits:**
- Faster response times
- Reduced bandwidth
- Lower API rate limit consumption

### Batch Operations

**Good:**
```json
{
  "page_size": 200,  // Fetch maximum per request
  "filters": {
    "created_after": "2024-01-01"
  }
}
```

**Bad:**
```json
{
  "page_size": 10  // Too many requests needed
}
```

### Incremental Sync Pattern

```javascript
// Track last sync time
const lastSync = getLastSyncTime(); // e.g., "2024-11-07T10:00:00Z"

const updates = await searchEntities({
  page_size: 200,
  filters: {
    updated_after: lastSync.split('T')[0]
  },
  sort_by: "updated_at",
  sort_direction: "asc"
});

// Update local cache
saveToCache(updates);
setLastSyncTime(new Date().toISOString());
```

### Rate Limit Handling

Copper CRM enforces rate limits. Best practices:

1. **Batch requests** - Use maximum page_size
2. **Add delays** - Wait 100-200ms between requests
3. **Handle 429 responses** - Implement exponential backoff
4. **Cache results** - Avoid redundant searches

```javascript
async function searchWithRetry(params, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await search(params);
    } catch (error) {
      if (error.status === 429) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await sleep(delay);
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Troubleshooting

### Empty Results

**Check:**
1. Filter values are exact match where required
2. Date formats are correct (YYYY-MM-DD)
3. Entity has the filtered field
4. Field values are not null

### Slow Searches

**Solutions:**
1. Reduce `page_size` for first page
2. Add more specific filters
3. Use indexed fields (id, created_at, updated_at)
4. Request fewer fields

### Inconsistent Results

**Causes:**
1. Data being modified during pagination
2. Sort order not deterministic (use `id` as secondary sort)
3. Concurrent updates affecting results

**Fix:**
```json
{
  "sort_by": "created_at",
  "sort_direction": "asc",
  "filters": {
    "created_before": "2024-11-08"  // Fix snapshot point
  }
}
```

### Missing Custom Fields

**Check:**
1. Custom field is defined for entity type
2. Field name matches exactly (case-sensitive)
3. User has permission to view field
4. Field has been populated on records

---

## Advanced Patterns

### Compound Search (Multiple Entities)

```javascript
async function findRelatedRecords(companyId) {
  const [company, contacts, opportunities] = await Promise.all([
    searchCompanies({ filters: { id: companyId } }),
    searchPeople({ filters: { company_id: companyId } }),
    searchOpportunities({ filters: { company_id: companyId } })
  ]);

  return {
    company: company.data[0],
    contacts: contacts.data,
    opportunities: opportunities.data
  };
}
```

### Deduplication Search

```javascript
async function findDuplicateCompanies() {
  // Search by phone number
  const byPhone = await searchCompanies({
    filters: { phone_number: "415-555-1234" }
  });

  // Search by domain
  const byDomain = await searchCompanies({
    filters: { email: "@acme.com" }
  });

  // Compare results
  return findOverlap(byPhone.data, byDomain.data);
}
```

### Progressive Filtering

```javascript
async function progressiveSearch(baseCriteria) {
  // Start broad
  let results = await search({ filters: baseCriteria });

  // If too many results, add filters
  if (results.total_count > 1000) {
    results = await search({
      filters: {
        ...baseCriteria,
        updated_after: "2024-01-01"
      }
    });
  }

  // If still too many, narrow further
  if (results.total_count > 1000) {
    results = await search({
      filters: {
        ...baseCriteria,
        updated_after: "2024-06-01",
        tags: ["active"]
      }
    });
  }

  return results;
}
```

---

## API Response Structure

### Standard Search Response

```json
{
  "data": [
    {
      "id": 12345,
      "name": "Example Company",
      // ... entity fields
    }
  ],
  "total_count": 1523,
  "page_number": 1,
  "page_size": 100,
  "total_pages": 16
}
```

### Empty Results

```json
{
  "data": [],
  "total_count": 0,
  "page_number": 1,
  "page_size": 100,
  "total_pages": 0
}
```

### Error Response

```json
{
  "error": {
    "message": "Invalid filter parameter",
    "code": "INVALID_FILTER",
    "details": {
      "field": "monetary_value_min",
      "issue": "must be a number"
    }
  }
}
```

---

## Quick Reference

### Most Common Filters

```json
{
  "filters": {
    // Universal
    "tags": ["tag1", "tag2"],
    "assignee_id": 12345,
    "created_after": "2024-01-01",
    "updated_after": "2024-11-01",

    // People
    "email": "user@example.com",
    "company_id": 12345,

    // Companies
    "name": "Acme",
    "industry": "Technology",

    // Opportunities
    "status": "Open",
    "pipeline_id": 1,
    "monetary_value_min": 10000
  }
}
```

### Optimal Pagination

```json
{
  "page_size": 100,              // Balance speed vs requests
  "sort_by": "id",               // Deterministic ordering
  "sort_direction": "asc"
}
```

### Safe Date Ranges

```json
{
  "filters": {
    "created_after": "2024-01-01",
    "created_before": "2024-12-31"
  }
}
```

---

## Summary

**Key Takeaways:**

1. **Use consistent patterns** - All search endpoints follow POST /{entity}/search
2. **Optimize pagination** - Use page_size: 100-200 for bulk operations
3. **Handle limits** - Partition large datasets by date, assignee, or ID ranges
4. **Be specific** - More filters = faster, more accurate results
5. **Request only needed fields** - Reduces response time and bandwidth
6. **Implement retry logic** - Handle rate limits with exponential backoff
7. **Cache smartly** - Use incremental sync for large datasets

For additional details on specific entities or advanced use cases, refer to the Copper CRM API documentation or entity-specific templates.
