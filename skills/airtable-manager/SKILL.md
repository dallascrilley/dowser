---
name: airtable-manager
short_description: >-
  Airtable REST API manager for CRUD operations, filtering, upsert, webhooks,
  and data synchronization with JavaScript/Python SDKs.
description: >
  Airtable REST API manager for CRUD operations, filtering, upsert, webhooks,
  and data synchronization.


  Supports JavaScript SDK, Python SDK (pyairtable), and raw HTTP requests.
  Handles 30+ field types, rate limiting (5 req/sec per base, 50 req/sec per
  user), pagination, filterByFormula queries, webhook lifecycle management, CSV
  sync (10k rows), and enterprise features.


  USE WHEN: User requests Airtable integration, needs to read/write/sync
  Airtable data, create automations with Airtable webhooks, build
  Airtable-backed applications, implement upsert operations, filter records with
  formulas, handle attachments, manage organization/bases, or debug Airtable API
  issues.


  Keywords: airtable api, airtable integration, airtable crud, airtable webhook,
  filterByFormula, airtable upsert, airtable sync, pyairtable, airtable.js,
  personal access token, airtable rate limit, airtable pagination, linked
  records, airtable attachments, airtable enterprise
when_to_use: >
  Use when integrating Airtable API with JavaScript/Python, performing CRUD
  operations on Airtable bases/tables/records, filtering Airtable records with
  filterByFormula queries, implementing upsert (create-or-update) operations,
  creating/managing Airtable webhooks for real-time updates, handling pagination
  for large datasets, syncing data between Airtable and other systems, managing
  30+ Airtable field types (attachments, linked records, formulas, rollups),
  handling Airtable rate limits (5 req/sec per base), uploading attachments to
  Airtable, or implementing enterprise Airtable features (base management, user
  provisioning).
version: 1.0.0
category: integrations-and-saas
---

# Airtable Manager Skill

## When to Activate This Skill

- User mentions "Airtable API", "Airtable integration", or "Airtable data"
- Building applications that use Airtable as a database backend
- Automating data synchronization between Airtable and other systems
- Setting up Airtable webhooks for real-time updates
- Filtering Airtable records with complex formulas
- Implementing create-or-update (upsert) operations
- Handling pagination for large Airtable datasets
- Managing Airtable attachments and file uploads
- Enterprise Airtable management (bases, workspaces, users)
- Debugging Airtable API errors or rate limit issues
- "read/write/sync Airtable records"
- "create Airtable webhook"
- "filter Airtable with formula"
- "upload files to Airtable"

## Quick Reference

### Core Endpoints

| Operation | Method | Endpoint | Key Parameters |
|-----------|--------|----------|----------------|
| List records | GET | `/v0/{baseId}/{tableId}` | `filterByFormula`, `sort`, `fields`, `maxRecords`, `pageSize`, `offset` |
| Get record | GET | `/v0/{baseId}/{tableId}/{recordId}` | `returnFieldsByFieldId` |
| Create records | POST | `/v0/{baseId}/{tableId}` | `records` (max 10), `typecast` |
| Update records | PATCH | `/v0/{baseId}/{tableId}` | `records` (max 10), `performUpsert`, `fieldsToMergeOn`, `typecast` |
| Delete records | DELETE | `/v0/{baseId}/{tableId}` | `records` (max 10 IDs) |
| Get base schema | GET | `/v0/meta/bases/{baseId}/tables` | - |
| Create webhook | POST | `/v0/bases/{baseId}/webhooks` | `notificationUrl`, `specification` |
| Refresh webhook | POST | `/v0/bases/{baseId}/webhooks/{webhookId}/refresh` | - |

### Authentication

**Personal Access Token (Recommended):**
```bash
export AIRTABLE_TOKEN="pat..."
curl -H "Authorization: Bearer $AIRTABLE_TOKEN" \
  "https://api.airtable.com/v0/{baseId}/{tableId}"
```

**OAuth 2.0 (User-delegated):**
```bash
# For third-party integrations
Authorization: Bearer {oauth_access_token}
```

### JavaScript SDK Quick Start

```javascript
const Airtable = require('airtable');
const base = new Airtable({ apiKey: process.env.AIRTABLE_TOKEN })
  .base('appXXXXXXXXXXXXXX');

// List records with filtering
const records = await base('TableName')
  .select({
    filterByFormula: "AND({Status}='Active', {Priority}>7)",
    sort: [{ field: 'Priority', direction: 'desc' }],
    maxRecords: 100
  })
  .all();

// Create record
const newRecord = await base('TableName').create({
  'Name': 'John Doe',
  'Email': 'john@example.com',
  'Status': 'Active'
});

// Upsert records (create or update)
const upserted = await base('TableName').update(
  [{ fields: { 'Name': 'John Doe', 'Email': 'updated@example.com' } }],
  { performUpsert: { fieldsToMergeOn: ['Name'] } }
);
```

### Python SDK Quick Start

```python
from pyairtable import Api, Base, Table

# Initialize
api = Api(api_key=os.environ['AIRTABLE_TOKEN'])
base = api.base('appXXXXXXXXXXXXXX')
table = base.table('TableName')

# List records with formula filter
records = table.all(
    formula="AND({Status}='Active', {Priority}>7)",
    sort=['Priority'],
    max_records=100
)

# Create record
new_record = table.create({'Name': 'John Doe', 'Email': 'john@example.com'})

# Update record
table.update(record_id, {'Status': 'Completed'})

# Batch create
table.batch_create([
    {'Name': 'Person 1', 'Email': 'person1@example.com'},
    {'Name': 'Person 2', 'Email': 'person2@example.com'}
])
```

### Raw HTTP Examples

**List records with filtering:**
```bash
curl "https://api.airtable.com/v0/appXXX/TableName?\
filterByFormula=AND(%7BStatus%7D%3D'Active'%2C%7BPriority%7D%3E7)&\
sort[0][field]=Priority&\
sort[0][direction]=desc&\
maxRecords=100" \
  -H "Authorization: Bearer $AIRTABLE_TOKEN"
```

**Create records:**
```bash
curl -X POST "https://api.airtable.com/v0/appXXX/TableName" \
  -H "Authorization: Bearer $AIRTABLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"fields": {"Name": "John Doe", "Email": "john@example.com"}}
    ]
  }'
```

**Upsert records:**
```bash
curl -X PATCH "https://api.airtable.com/v0/appXXX/TableName" \
  -H "Authorization: Bearer $AIRTABLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "performUpsert": {
      "fieldsToMergeOn": ["Email"]
    },
    "records": [
      {"fields": {"Name": "John Doe", "Email": "john@example.com", "Status": "Active"}}
    ]
  }'
```

## Essential Workflows

### 1. Pagination Pattern

```javascript
// JavaScript SDK - automatic pagination
const allRecords = await base('TableName').select().all();

// Manual pagination with eachPage
base('TableName').select({ pageSize: 100 })
  .eachPage((records, fetchNextPage) => {
    records.forEach(record => console.log(record.id));
    fetchNextPage();
  }, (err) => {
    if (err) console.error(err);
  });
```

```python
# Python SDK - automatic pagination
all_records = table.all()

# Manual iteration
for record in table.iterate():
    print(record['id'])
```

### 2. Rate Limiting Handling

**Limits:**
- **5 requests/second per base** (all pricing tiers)
- **50 requests/second per user** (Personal Access Token)
- **30-second wait** after 429 error

**Strategies:**
```javascript
// Implement exponential backoff
async function fetchWithRetry(fn, retries = 3) {
  try {
    return await fn();
  } catch (error) {
    if (error.statusCode === 429 && retries > 0) {
      await new Promise(resolve => setTimeout(resolve, 30000));
      return fetchWithRetry(fn, retries - 1);
    }
    throw error;
  }
}

// Use JavaScript SDK (has built-in retry)
const records = await base('TableName').select().all();
```

### 3. filterByFormula Patterns

**Common formula operators:**
```javascript
// Equality
filterByFormula: "{Status}='Active'"

// Comparison
filterByFormula: "{Priority}>7"

// Logical AND
filterByFormula: "AND({Status}='Active', {Priority}>7)"

// Logical OR
filterByFormula: "OR({Status}='Active', {Status}='Pending')"

// Text search (case-insensitive)
filterByFormula: "SEARCH('keyword', {Description})>0"

// Date comparisons
filterByFormula: "IS_AFTER({DueDate}, TODAY())"
filterByFormula: "IS_AFTER({Created}, DATEADD(TODAY(), -30, 'days'))"

// NOT operator
filterByFormula: "NOT({Status}='Archived')"

// Check for empty/blank
filterByFormula: "{Email}=BLANK()"
filterByFormula: "NOT({Email}=BLANK())"

// Multiple conditions
filterByFormula: "AND(OR({Status}='Active',{Status}='Pending'),{Priority}>5,NOT({Archived}))"
```

**URL encoding (use helper):**
```javascript
class FormulaBuilder {
  static equals(field, value) {
    return `{${field}}='${value}'`;
  }

  static and(...conditions) {
    return `AND(${conditions.join(',')})`;
  }

  static encode(formula) {
    return encodeURIComponent(formula);
  }
}

const formula = FormulaBuilder.and(
  FormulaBuilder.equals('Status', 'Active'),
  '{Priority}>7'
);
const encoded = FormulaBuilder.encode(formula);
```

### 4. Upsert Operations

**Create-or-update based on unique fields:**
```javascript
// JavaScript SDK
const records = await base('Contacts').update(
  [
    {
      fields: {
        'Email': 'john@example.com',
        'Name': 'John Doe',
        'Phone': '+1-555-0100'
      }
    }
  ],
  {
    performUpsert: {
      fieldsToMergeOn: ['Email']  // Match on email
    }
  }
);

// Returns: { createdRecords: [...], updatedRecords: [...] }
```

```python
# Python SDK
response = table.batch_upsert(
    [
        {'Email': 'john@example.com', 'Name': 'John Doe', 'Phone': '+1-555-0100'}
    ],
    key_fields=['Email']
)
```

### 5. Webhook Lifecycle Management

**Create webhook:**
```javascript
const webhook = await fetch(
  `https://api.airtable.com/v0/bases/${baseId}/webhooks`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      notificationUrl: 'https://your-server.com/webhook',
      specification: {
        options: {
          filters: {
            dataTypes: ['tableData']
          }
        }
      }
    })
  }
);
```

**Refresh webhook (extends life by 7 days):**
```javascript
// Refresh every 6 days to prevent expiration
setInterval(async () => {
  await fetch(
    `https://api.airtable.com/v0/bases/${baseId}/webhooks/${webhookId}/refresh`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
}, 6 * 24 * 60 * 60 * 1000);
```

### 6. Attachment Handling

**Upload attachment:**
```bash
# Step 1: Upload to Airtable CDN
curl -X POST "https://api.airtable.com/v0/appXXX/TableName/uploadAttachment" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: image/jpeg" \
  --data-binary @image.jpg

# Response: {"url": "https://v5.airtableusercontent.com/..."}

# Step 2: Update record with attachment URL
curl -X PATCH "https://api.airtable.com/v0/appXXX/TableName/recYYY" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "Attachments": [
        {"url": "https://v5.airtableusercontent.com/..."}
      ]
    }
  }'
```

**Attachment field structure:**
```json
{
  "Attachments": [
    {
      "id": "attXXX",
      "url": "https://v5.airtableusercontent.com/...",
      "filename": "document.pdf",
      "size": 102400,
      "type": "application/pdf",
      "thumbnails": {
        "small": {"url": "...", "width": 36, "height": 36},
        "large": {"url": "...", "width": 200, "height": 200}
      }
    }
  ]
}
```

## Field Types Quick Reference

| Field Type | Read Format | Write Format | Notes |
|------------|-------------|--------------|-------|
| Single line text | `string` | `string` | Plain text |
| Long text | `string` | `string` | Multiline |
| Number | `number` | `number` | Integer or float |
| Checkbox | `boolean` | `boolean` | true/false |
| Date | `"2024-01-15"` | `"2024-01-15"` | YYYY-MM-DD |
| Date/Time | `"2024-01-15T10:30:00.000Z"` | `"2024-01-15T10:30:00.000Z"` | ISO 8601 |
| Single select | `string` | `string` | Must match option |
| Multiple select | `string[]` | `string[]` | Array of options |
| Attachments | `object[]` | `{url: string}[]` | See attachment structure |
| Linked records | `string[]` | `string[]` | Array of record IDs |
| Formula | `any` | - | Read-only |
| Rollup | `any` | - | Read-only |
| Lookup | `any[]` | - | Read-only |
| Rich text | `string` | - | Read-only (Markdown) |
| AI Text | `{state, value, isStale}` | - | Read-only |

## Rate Limits & Best Practices

**Rate Limits:**
- ✅ 5 requests/second per base (all tiers)
- ✅ 50 requests/second per user (PAT)
- ✅ 30-second wait after 429 error
- ✅ JavaScript SDK has built-in retry

**Best Practices:**
1. **Batch operations** - Create/update up to 10 records per request
2. **Use filterByFormula** - Filter server-side, not client-side
3. **Pagination** - Use `pageSize` and `offset` for large datasets
4. **Upsert** - Use `performUpsert` for create-or-update logic
5. **Webhook refresh** - Refresh every 6 days to prevent expiration
6. **Field selection** - Use `fields` parameter to reduce response size
7. **PAT over API keys** - API keys deprecated Feb 2024
8. **Error handling** - Implement retry logic for 429 and 503 errors
9. **Incremental sync** - Use `LAST_MODIFIED_TIME()` formula for incremental updates
10. **Environment variables** - Store tokens in env vars, never in code

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/missing token | Check token, regenerate if expired |
| 403 Forbidden | Insufficient permissions | Verify token has required scopes and base access |
| 404 Not Found | Base/table/record doesn't exist | Verify IDs, check permissions |
| 422 Unprocessable Entity | Invalid field name/type | Check field names match exactly, verify data types |
| 429 Too Many Requests | Rate limit exceeded | Wait 30 seconds, implement exponential backoff |
| 413 Request Too Large | Batch >10 records | Limit to 10 records per batch request |
| 16000 char URL limit | Formula too long | Use POST to `/listRecords` instead of GET |

## Environment Setup

**Node.js:**
```bash
npm install airtable
export AIRTABLE_TOKEN="pat..."
export AIRTABLE_BASE_ID="appXXX"
```

**Python:**
```bash
pip install pyairtable
export AIRTABLE_TOKEN="pat..."
export AIRTABLE_BASE_ID="appXXX"
```

## Supplementary Resources

For comprehensive documentation including:
- All 30+ field types with schemas
- Complete webhook specification
- CSV sync endpoint details (10k rows, 500 columns)
- Enterprise features (SCIM, audit logs, base deletion)
- Advanced filtering patterns and formulas
- OAuth 2.0 implementation
- Complete API changelog
- Troubleshooting guides

Read the comprehensive context:
```bash
read ~/.claude/skills/airtable-manager/CLAUDE.md
```

For condensed cheat sheets:
```bash
read ~/Code/docs/airtable/airtable-api-cheat-sheet.md
read ~/Code/docs/airtable/airtable-api-comprehensive-analysis.md
```
