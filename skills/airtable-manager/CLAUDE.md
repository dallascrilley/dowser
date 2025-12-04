# Airtable Manager - Comprehensive Documentation

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Documentation Sources:**
- Official Airtable Web API Reference
- airtable-api-comprehensive-analysis.md (2,397 lines)
- airtable-api-cheat-sheet.md
- Local API reference documentation

---

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Authentication](#authentication)
3. [Core REST API Endpoints](#core-rest-api-endpoints)
4. [Field Types Reference (30+ Types)](#field-types-reference-30-types)
5. [Filtering with filterByFormula](#filtering-with-filterbyformula)
6. [Workflows & Patterns](#workflows--patterns)
7. [JavaScript SDK Guide](#javascript-sdk-guide)
8. [Python SDK Guide](#python-sdk-guide)
9. [Rate Limiting & Performance](#rate-limiting--performance)
10. [Webhooks & Real-time Updates](#webhooks--real-time-updates)
11. [Error Handling & Troubleshooting](#error-handling--troubleshooting)
12. [Enterprise Features](#enterprise-features)
13. [Best Practices](#best-practices)
14. [Complete Code Examples](#complete-code-examples)

---

## Overview & Architecture

### Data Hierarchy

```
Workspace (Organization)
├── Base (Database) - app...
│   ├── Table (Spreadsheet) - tbl...
│   │   ├── Record (Row) - rec...
│   │   │   └── Field (Column/Cell)
│   │   └── View (Filtered/Sorted subset)
│   └── Webhook
└── Collaborators/Permissions
```

### Key Identifiers

- **Base ID**: `app...` - Unique identifier for your database (16 characters)
- **Table ID**: `tbl...` - Unique identifier for a table (can also use table name)
- **Record ID**: `rec...` - Unique identifier for each row (17 characters)
- **Field ID**: `fld...` - Unique identifier for each column
- **View ID**: `viw...` - Unique identifier for each view
- **Webhook ID**: `ach...` - Unique identifier for each webhook

### Base URL

```
https://api.airtable.com/v0
```

### API Version

Current: **v0**
- Stable and production-ready
- Breaking changes announced 12+ months in advance
- Changelog: https://airtable.com/developers/web/api/changelog

---

## Authentication

### Personal Access Token (PAT) - Recommended

**Why PAT:**
- ✅ API keys deprecated February 2024
- ✅ Granular scopes control
- ✅ Higher rate limits (50 req/sec per user)
- ✅ No expiration unless revoked
- ✅ Works with server-to-server integrations

**Creating a PAT:**
1. Go to https://airtable.com/create/tokens
2. Click "Create new token"
3. Name your token
4. Add required scopes (e.g., `data.records:read`, `data.records:write`)
5. Add access to specific bases
6. Generate and securely store token

**Required Scopes:**
```
data.records:read     - List and get records
data.records:write    - Create, update, delete records
schema.bases:read     - Get base metadata
schema.bases:write    - Modify base structure
webhook:manage        - Create and manage webhooks
user.email:read       - Get user email (OAuth)
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_PAT_TOKEN" \
  "https://api.airtable.com/v0/appXXX/TableName"
```

```javascript
const Airtable = require('airtable');
Airtable.configure({ apiKey: process.env.AIRTABLE_TOKEN });
```

```python
from pyairtable import Api
api = Api(os.environ['AIRTABLE_TOKEN'])
```

### OAuth 2.0 - User-delegated Access

**When to use OAuth:**
- Third-party applications
- User needs to authorize access to their bases
- Building marketplace integrations
- Need user-specific permissions

**OAuth Flow:**
```
1. User clicks "Connect to Airtable"
2. Redirect to Airtable authorization URL
3. User grants permissions
4. Airtable redirects back with authorization code
5. Exchange code for access token + refresh token
6. Use access token for API requests
7. Refresh token when access token expires
```

**OAuth Endpoints:**
```
Authorization: https://airtable.com/oauth2/v1/authorize
Token: https://airtable.com/oauth2/v1/token
```

**Example Authorization URL:**
```
https://airtable.com/oauth2/v1/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=https://your-app.com/oauth/callback&
  response_type=code&
  scope=data.records:read data.records:write&
  state=random_state_string
```

---

## Core REST API Endpoints

### Records Endpoints

#### List Records

```
GET /v0/{baseId}/{tableIdOrName}
```

**Query Parameters:**
- `fields[]` - Array of field names to include
- `filterByFormula` - Airtable formula for filtering
- `maxRecords` - Maximum number of records to return
- `pageSize` - Number of records per page (1-100, default 100)
- `sort[0][field]` & `sort[0][direction]` - Sorting configuration
- `view` - View name or ID
- `offset` - Pagination token
- `cellFormat` - `json` (default) or `string`
- `timeZone` - Timezone for string formatting (e.g., `America/New_York`)
- `userLocale` - Locale for string formatting (e.g., `en-us`)
- `returnFieldsByFieldId` - Return fields by ID instead of name (boolean)
- `recordMetadata` - Include `commentCount` in response

**Response:**
```json
{
  "records": [
    {
      "id": "rec...",
      "createdTime": "2024-01-15T10:30:00.000Z",
      "fields": {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Status": "Active"
      }
    }
  ],
  "offset": "itrXXX..."  // If more records exist
}
```

**Example:**
```bash
curl "https://api.airtable.com/v0/appXXX/Contacts?\
filterByFormula=AND(%7BStatus%7D%3D'Active'%2C%7BPriority%7D%3E7)&\
sort[0][field]=Priority&\
sort[0][direction]=desc&\
fields[]=Name&\
fields[]=Email&\
maxRecords=100" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Single Record

```
GET /v0/{baseId}/{tableIdOrName}/{recordId}
```

**Response:**
```json
{
  "id": "rec...",
  "createdTime": "2024-01-15T10:30:00.000Z",
  "fields": {
    "Name": "John Doe",
    "Email": "john@example.com"
  }
}
```

#### Create Records

```
POST /v0/{baseId}/{tableIdOrName}
```

**Request Body:**
```json
{
  "records": [
    {
      "fields": {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Status": "Active"
      }
    }
  ],
  "typecast": false  // Auto-convert types if true
}
```

**Limits:**
- Maximum 10 records per request
- Use batch operations for efficiency

**Response:**
```json
{
  "records": [
    {
      "id": "rec...",
      "createdTime": "2024-01-15T10:30:00.000Z",
      "fields": {...}
    }
  ]
}
```

#### Update Records (PATCH)

```
PATCH /v0/{baseId}/{tableIdOrName}
```

**Request Body (standard update):**
```json
{
  "records": [
    {
      "id": "rec...",
      "fields": {
        "Status": "Completed",
        "Notes": "Task finished"
      }
    }
  ]
}
```

**Request Body (upsert - create or update):**
```json
{
  "performUpsert": {
    "fieldsToMergeOn": ["Email"]
  },
  "records": [
    {
      "fields": {
        "Email": "john@example.com",
        "Name": "John Doe Updated",
        "Status": "Active"
      }
    }
  ]
}
```

**Response (upsert):**
```json
{
  "records": [{"id": "rec...", "createdTime": "...", "fields": {...}}],
  "createdRecords": ["rec..."],  // IDs of newly created records
  "updatedRecords": ["rec..."]   // IDs of updated records
}
```

**Key Upsert Features:**
- Automatically creates record if no match found
- Updates existing record if match found
- Can merge on multiple fields: `["Email", "Name"]`
- Max 10 records per request
- Returns separate arrays for created vs updated

#### Delete Records

```
DELETE /v0/{baseId}/{tableIdOrName}?records[]=rec1&records[]=rec2
```

**Or use request body:**
```json
{
  "records": ["rec...", "rec..."]
}
```

**Response:**
```json
{
  "records": [
    {"id": "rec...", "deleted": true},
    {"id": "rec...", "deleted": true}
  ]
}
```

### Metadata Endpoints

#### Get Base Schema

```
GET /v0/meta/bases/{baseId}/tables
```

**Response:**
```json
{
  "tables": [
    {
      "id": "tbl...",
      "name": "Contacts",
      "primaryFieldId": "fld...",
      "fields": [
        {
          "id": "fld...",
          "name": "Name",
          "type": "singleLineText"
        },
        {
          "id": "fld...",
          "name": "Email",
          "type": "email"
        }
      ],
      "views": [
        {
          "id": "viw...",
          "name": "Main View",
          "type": "grid"
        }
      ]
    }
  ]
}
```

#### List Bases

```
GET /v0/meta/bases
```

**Response:**
```json
{
  "bases": [
    {
      "id": "app...",
      "name": "My Database",
      "permissionLevel": "create"
    }
  ]
}
```

### CSV Sync Endpoint

```
POST /v0/{baseId}/{tableIdOrName}/sync
```

**Upload CSV data directly:**
```bash
curl -X POST "https://api.airtable.com/v0/appXXX/TableName/sync" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/csv" \
  --data-binary @data.csv
```

**Limits:**
- 10,000 rows maximum
- 500 columns maximum
- 2MB request size maximum
- Rate limit: 20 requests per 5 minutes

**Use cases:**
- Bulk import from spreadsheets
- One-time data migration
- Periodic batch updates

---

## Field Types Reference (30+ Types)

### Text-Based Fields

#### Single Line Text
```json
// Read & Write
"Name": "John Doe"
```

#### Long Text
```json
// Read & Write (supports multiline)
"Description": "This is a long\nmultiline\ntext field"
```

#### Email
```json
// Read & Write (validated email format)
"Email": "john@example.com"
```

#### Phone Number
```json
// Read & Write
"Phone": "+1-555-0100"
```

#### URL
```json
// Read & Write (validated URL format)
"Website": "https://example.com"
```

### Numeric Fields

#### Number
```json
// Read & Write (integer or float)
"Price": 99.99,
"Quantity": 5
```

#### Currency
```json
// Read & Write (stored as number)
"Budget": 50000.00
```

#### Percent
```json
// Read & Write (0.0 to 1.0)
"Progress": 0.75  // 75%
```

#### Duration
```json
// Read & Write (seconds)
"Duration": 3600  // 1 hour
```

#### Rating
```json
// Read & Write (1-10)
"Rating": 8
```

### Boolean & Selection Fields

#### Checkbox
```json
// Read & Write
"IsActive": true,
"IsDeleted": false
```

#### Single Select
```json
// Read & Write (must match option)
"Status": "Active"  // Options: Active, Pending, Completed
```

#### Multiple Select
```json
// Read & Write (array of options)
"Tags": ["urgent", "customer", "priority"]
```

### Date & Time Fields

#### Date
```json
// Read & Write (YYYY-MM-DD)
"DueDate": "2024-12-31"
```

#### Date/Time
```json
// Read & Write (ISO 8601)
"CreatedAt": "2024-01-15T10:30:00.000Z"
```

### Advanced Fields

#### Attachments
```json
// Read format
"Attachments": [
  {
    "id": "att...",
    "url": "https://v5.airtableusercontent.com/...",
    "filename": "document.pdf",
    "size": 102400,
    "type": "application/pdf",
    "width": null,  // For images
    "height": null,  // For images
    "thumbnails": {  // For images
      "small": {"url": "...", "width": 36, "height": 36},
      "large": {"url": "...", "width": 200, "height": 200},
      "full": {"url": "...", "width": 3000, "height": 3000}
    }
  }
]

// Write format
"Attachments": [
  {"url": "https://example.com/file.pdf"}
]
```

**Notes:**
- URLs expire after 2 hours
- Max file size: 1GB
- Supported: images, PDFs, videos, audio, documents
- Use upload endpoint first, then update record

#### Linked Records
```json
// Read & Write (array of record IDs)
"RelatedContacts": ["rec...", "rec...", "rec..."]

// To get actual data, fetch linked records separately
```

#### Formula (Read-Only)
```json
// Read format (various types depending on formula)
"FullName": "John Doe",  // Text formula
"TotalPrice": 99.99,     // Number formula
"IsExpired": false       // Boolean formula
```

**Note:** Cannot write to formula fields

#### Rollup (Read-Only)
```json
// Read format (aggregated value from linked records)
"TotalSales": 50000.00,
"AverageRating": 4.5,
"CountProjects": 12
```

**Note:** Cannot write to rollup fields

#### Lookup (Read-Only)
```json
// Read format (array of values from linked records)
"CustomerEmails": ["john@example.com", "jane@example.com"]
```

**Note:** Cannot write to lookup fields

#### Rich Text (Read-Only)
```json
// Read format (Markdown string)
"RichDescription": "**Bold** and *italic* text\n\n- List item 1\n- List item 2"
```

**Note:** Cannot write to rich text fields

#### AI Text (Read-Only)
```json
// Read format
"AIGenerated": {
  "state": "generated",  // or "loading", "error"
  "value": "AI-generated content...",
  "isStale": false
}
```

**Note:** Cannot write to AI text fields

#### Barcode
```json
// Read & Write
"Barcode": {
  "text": "1234567890",
  "type": "ean13"
}
```

#### Button
```json
// Read format
"ActionButton": {
  "label": "Click me",
  "url": "https://example.com/action"
}
```

**Note:** Triggers external URL when clicked

### Field Type Summary

| Field Type | Read/Write | Value Type | Notes |
|------------|------------|------------|-------|
| Single line text | R/W | `string` | Plain text |
| Long text | R/W | `string` | Multiline |
| Email | R/W | `string` | Validated format |
| Phone | R/W | `string` | Any format |
| URL | R/W | `string` | Validated URL |
| Number | R/W | `number` | Int or float |
| Currency | R/W | `number` | Stored as number |
| Percent | R/W | `number` | 0.0 to 1.0 |
| Duration | R/W | `number` | Seconds |
| Rating | R/W | `number` | 1-10 |
| Checkbox | R/W | `boolean` | true/false |
| Single select | R/W | `string` | Must match option |
| Multiple select | R/W | `string[]` | Array of options |
| Date | R/W | `string` | YYYY-MM-DD |
| Date/Time | R/W | `string` | ISO 8601 |
| Attachments | R/W | `object[]` | URL array for write |
| Linked records | R/W | `string[]` | Record ID array |
| Formula | R | varies | Cannot write |
| Rollup | R | varies | Cannot write |
| Lookup | R | `any[]` | Cannot write |
| Rich text | R | `string` | Markdown, cannot write |
| AI Text | R | `object` | Cannot write |
| Barcode | R/W | `object` | Text + type |
| Button | R | `object` | Label + URL |

---

## Filtering with filterByFormula

### Formula Syntax Basics

**URL Encoding Required:**
```javascript
// Original formula
const formula = "AND({Status}='Active', {Priority}>7)";

// URL encoded
const encoded = encodeURIComponent(formula);
// "AND(%7BStatus%7D%3D'Active'%2C%7BPriority%7D%3E7)"
```

**Field References:**
```javascript
{FieldName}      // Use curly braces
{Status}         // Field name
{Due Date}       // Spaces OK in curly braces
```

### Comparison Operators

```javascript
// Equality
{Status}='Active'
{Count}=5

// Inequality
{Status}!='Archived'
{Priority}!=0

// Greater than
{Priority}>7
{Budget}>10000

// Greater than or equal
{Progress}>=0.5
{Count}>=1

// Less than
{DueDate}<TODAY()
{Score}<50

// Less than or equal
{Expiration}<=TODAY()
```

### Logical Operators

#### AND - All conditions must be true
```javascript
AND({Status}='Active', {Priority}>7)
AND({Status}='Active', {Priority}>7, {Budget}>5000)
```

#### OR - At least one condition must be true
```javascript
OR({Status}='Active', {Status}='Pending')
OR({Priority}>7, {Urgent}=TRUE())
```

#### NOT - Negates condition
```javascript
NOT({Status}='Archived')
NOT({Deleted}=TRUE())
```

#### Complex combinations
```javascript
AND(
  OR({Status}='Active', {Status}='Pending'),
  {Priority}>5,
  NOT({Archived})
)
```

### Text Functions

#### SEARCH - Case-insensitive text search
```javascript
// Find "keyword" anywhere in Description
SEARCH('keyword', {Description})>0

// Check if found (returns position or 0)
SEARCH('word', {Field})
```

#### FIND - Case-sensitive text search
```javascript
FIND('Word', {Description})>0
```

#### CONCATENATE - Combine text
```javascript
CONCATENATE({FirstName}, ' ', {LastName})
```

#### LEFT, RIGHT, MID - Extract text
```javascript
LEFT({Phone}, 3)          // First 3 characters
RIGHT({Phone}, 4)         // Last 4 characters
MID({Phone}, 5, 3)        // 3 chars starting at position 5
```

#### LEN - Text length
```javascript
LEN({Description})>100    // Longer than 100 chars
```

#### LOWER, UPPER - Change case
```javascript
LOWER({Email})='john@example.com'
UPPER({Status})='ACTIVE'
```

#### TRIM - Remove whitespace
```javascript
TRIM({Name})!=''
```

### Date Functions

#### TODAY - Current date
```javascript
{DueDate}=TODAY()
{StartDate}<TODAY()
```

#### NOW - Current date and time
```javascript
{Expiration}<NOW()
```

#### DATEADD - Add/subtract time
```javascript
// 30 days ago
DATEADD(TODAY(), -30, 'days')

// Future dates
DATEADD(TODAY(), 7, 'days')      // +7 days
DATEADD(TODAY(), 2, 'weeks')     // +2 weeks
DATEADD(TODAY(), 1, 'months')    // +1 month
DATEADD(TODAY(), 1, 'years')     // +1 year
```

#### IS_BEFORE, IS_AFTER - Date comparisons
```javascript
// Before today
IS_BEFORE({DueDate}, TODAY())

// After 30 days ago
IS_AFTER({Created}, DATEADD(TODAY(), -30, 'days'))

// Between dates
AND(
  IS_AFTER({Date}, DATEADD(TODAY(), -30, 'days')),
  IS_BEFORE({Date}, TODAY())
)
```

#### YEAR, MONTH, DAY - Extract components
```javascript
YEAR({DueDate})=2024
MONTH({DueDate})=12
DAY({DueDate})=25
```

#### WEEKDAY - Day of week
```javascript
WEEKDAY({Date})=0    // Sunday
WEEKDAY({Date})=1    // Monday
```

### Numeric Functions

#### ABS - Absolute value
```javascript
ABS({Balance})>1000
```

#### ROUND, CEIL, FLOOR - Rounding
```javascript
ROUND({Price}, 2)    // 2 decimal places
CEIL({Value})        // Round up
FLOOR({Value})       // Round down
```

#### MAX, MIN - Comparisons
```javascript
MAX({Score1}, {Score2}, {Score3})>80
MIN({Price1}, {Price2})
```

#### MOD - Modulo
```javascript
MOD({Number}, 2)=0   // Even numbers
```

#### SUM, AVERAGE - Aggregations (for arrays)
```javascript
SUM(values)
AVERAGE(values)
```

### Record & Array Functions

#### BLANK - Check if empty
```javascript
{Email}=BLANK()          // Empty field
NOT({Email}=BLANK())     // Not empty
{Notes}!=BLANK()         // Has value
```

#### IF - Conditional logic
```javascript
IF({Priority}>7, 'High', 'Low')
IF({Status}='Active', 1, 0)
IF(
  {Score}>90,
  'A',
  IF({Score}>80, 'B', 'C')
)
```

#### SWITCH - Multiple conditions
```javascript
SWITCH(
  {Status},
  'Active', 1,
  'Pending', 2,
  'Completed', 3,
  0  // default
)
```

#### RECORD_ID - Get record ID
```javascript
RECORD_ID()='rec...'
SEARCH('rec123', RECORD_ID())>0
```

#### COUNTALL - Count array items
```javascript
COUNTALL({LinkedRecords})>5
```

### Common Filtering Patterns

#### 1. Filter by Status
```javascript
// Single status
{Status}='Active'

// Multiple statuses
OR({Status}='Active', {Status}='Pending', {Status}='In Progress')
```

#### 2. Date Range Filters
```javascript
// Last 30 days
IS_AFTER({Created}, DATEADD(TODAY(), -30, 'days'))

// This month
MONTH({Date})=MONTH(TODAY())

// This year
YEAR({Date})=YEAR(TODAY())

// Between specific dates
AND(
  IS_AFTER({Date}, DATETIME_PARSE('2024-01-01', 'YYYY-MM-DD')),
  IS_BEFORE({Date}, DATETIME_PARSE('2024-12-31', 'YYYY-MM-DD'))
)

// Overdue items
AND(
  IS_BEFORE({DueDate}, TODAY()),
  NOT({Status}='Completed')
)
```

#### 3. Text Search
```javascript
// Case-insensitive search
SEARCH('keyword', {Description})>0

// Multiple keywords (OR)
OR(
  SEARCH('urgent', {Notes})>0,
  SEARCH('priority', {Notes})>0
)

// Multiple keywords (AND)
AND(
  SEARCH('urgent', {Notes})>0,
  SEARCH('customer', {Notes})>0
)
```

#### 4. Numeric Ranges
```javascript
// Greater than threshold
{Priority}>7

// Between values
AND({Price}>=10, {Price}<=100)

// Outside range
OR({Score}<60, {Score}>90)
```

#### 5. Boolean Combinations
```javascript
// Active and high priority
AND({IsActive}=TRUE(), {Priority}>7)

// Not archived and not deleted
AND(NOT({Archived}), NOT({Deleted}))
```

#### 6. Empty/Null Checks
```javascript
// Has email
NOT({Email}=BLANK())

// Missing required fields
OR(
  {Name}=BLANK(),
  {Email}=BLANK(),
  {Phone}=BLANK()
)

// Has any linked records
COUNTALL({LinkedRecords})>0

// No linked records
COUNTALL({LinkedRecords})=0
```

### Complete URL Examples

#### Example 1: Active High-Priority Tasks
```bash
curl "https://api.airtable.com/v0/appXXX/Tasks?\
filterByFormula=AND(%7BStatus%7D%3D'Active'%2C%7BPriority%7D%3E7)&\
sort[0][field]=Priority&\
sort[0][direction]=desc&\
fields[]=Name&\
fields[]=Priority&\
fields[]=DueDate&\
maxRecords=100" \
  -H "Authorization: Bearer $TOKEN"
```

**Decoded formula:**
```javascript
AND({Status}='Active', {Priority}>7)
```

#### Example 2: Recent Updates (Last 7 Days)
```bash
curl "https://api.airtable.com/v0/appXXX/Contacts?\
filterByFormula=IS_AFTER(%7BLastModified%7D%2CDATEADD(TODAY()%2C-7%2C'days'))&\
sort[0][field]=LastModified&\
sort[0][direction]=desc" \
  -H "Authorization: Bearer $TOKEN"
```

**Decoded formula:**
```javascript
IS_AFTER({LastModified}, DATEADD(TODAY(), -7, 'days'))
```

#### Example 3: Search with Multiple Conditions
```bash
curl "https://api.airtable.com/v0/appXXX/Projects?\
filterByFormula=AND(SEARCH('customer'%2C%7BNotes%7D)%3E0%2COR(%7BStatus%7D%3D'Active'%2C%7BStatus%7D%3D'Pending')%2C%7BBudget%7D%3E5000)" \
  -H "Authorization: Bearer $TOKEN"
```

**Decoded formula:**
```javascript
AND(
  SEARCH('customer', {Notes})>0,
  OR({Status}='Active', {Status}='Pending'),
  {Budget}>5000
)
```

#### Example 4: Overdue Incomplete Tasks
```bash
curl "https://api.airtable.com/v0/appXXX/Tasks?\
filterByFormula=AND(IS_BEFORE(%7BDueDate%7D%2CTODAY())%2CNOT(%7BStatus%7D%3D'Completed'))" \
  -H "Authorization: Bearer $TOKEN"
```

**Decoded formula:**
```javascript
AND(
  IS_BEFORE({DueDate}, TODAY()),
  NOT({Status}='Completed')
)
```

### POST Request for Long Formulas

**When URL exceeds 16,000 characters:**
```bash
curl -X POST "https://api.airtable.com/v0/appXXX/TableName/listRecords" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filterByFormula": "AND({Status}='Active', {Priority}>7)",
    "sort": [{"field": "Priority", "direction": "desc"}],
    "fields": ["Name", "Priority", "DueDate"],
    "maxRecords": 100
  }'
```

---

## Workflows & Patterns

### 1. Complete CRUD Workflow

```javascript
// Step 1: List bases
const basesResponse = await fetch('https://api.airtable.com/v0/meta/bases', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const bases = await basesResponse.json();

// Step 2: Get base schema
const schemaResponse = await fetch(
  `https://api.airtable.com/v0/meta/bases/${baseId}/tables`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const schema = await schemaResponse.json();

// Step 3: List records with filtering
const recordsResponse = await fetch(
  `https://api.airtable.com/v0/${baseId}/TableName?` +
  `filterByFormula=${encodeURIComponent("AND({Status}='Active', {Priority}>7)")}&` +
  `sort[0][field]=Priority&sort[0][direction]=desc&maxRecords=100`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const records = await recordsResponse.json();

// Step 4: Create record
const createResponse = await fetch(
  `https://api.airtable.com/v0/${baseId}/TableName`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      records: [{ fields: { Name: 'John', Status: 'Active' } }]
    })
  }
);

// Step 5: Update record
const updateResponse = await fetch(
  `https://api.airtable.com/v0/${baseId}/TableName`,
  {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      records: [{ id: recordId, fields: { Status: 'Completed' } }]
    })
  }
);

// Step 6: Delete record
const deleteResponse = await fetch(
  `https://api.airtable.com/v0/${baseId}/TableName?records[]=${recordId}`,
  {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
```

### 2. Pagination Workflow

```javascript
async function fetchAllRecords(baseId, tableName, token) {
  const allRecords = [];
  let offset = null;

  do {
    const url = offset
      ? `https://api.airtable.com/v0/${baseId}/${tableName}?offset=${offset}`
      : `https://api.airtable.com/v0/${baseId}/${tableName}`;

    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    const data = await response.json();
    allRecords.push(...data.records);
    offset = data.offset;

  } while (offset);

  return allRecords;
}
```

### 3. Upsert Workflow (Create or Update)

```javascript
async function upsertRecords(baseId, tableName, token, records, mergeFields) {
  const response = await fetch(
    `https://api.airtable.com/v0/${baseId}/${tableName}`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        performUpsert: { fieldsToMergeOn: mergeFields },
        records: records.map(r => ({ fields: r }))
      })
    }
  );

  const result = await response.json();
  console.log(`Created: ${result.createdRecords.length}`);
  console.log(`Updated: ${result.updatedRecords.length}`);
  return result;
}

// Usage
await upsertRecords(baseId, 'Contacts', token, [
  { Email: 'john@example.com', Name: 'John Doe', Status: 'Active' },
  { Email: 'jane@example.com', Name: 'Jane Smith', Status: 'Pending' }
], ['Email']);
```

### 4. Incremental Sync with LAST_MODIFIED_TIME

```javascript
async function incrementalSync(baseId, tableName, token, lastSyncTime) {
  // Build formula for records modified since last sync
  const formula = `IS_AFTER(LAST_MODIFIED_TIME(), ` +
    `DATETIME_PARSE('${lastSyncTime.toISOString()}', 'YYYY-MM-DDTHH:mm:ss.SSSZ'))`;

  const response = await fetch(
    `https://api.airtable.com/v0/${baseId}/${tableName}?` +
    `filterByFormula=${encodeURIComponent(formula)}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  const data = await response.json();
  return data.records;
}

// Usage
const lastSync = new Date('2024-01-01T00:00:00Z');
const updatedRecords = await incrementalSync(baseId, 'Contacts', token, lastSync);
```

### 5. Batch Operations with Rate Limiting

```javascript
async function batchCreateWithRateLimit(baseId, tableName, token, records) {
  const BATCH_SIZE = 10;
  const DELAY_MS = 200;  // 5 req/sec = 200ms between requests

  const batches = [];
  for (let i = 0; i < records.length; i += BATCH_SIZE) {
    batches.push(records.slice(i, i + BATCH_SIZE));
  }

  const results = [];
  for (const batch of batches) {
    const response = await fetch(
      `https://api.airtable.com/v0/${baseId}/${tableName}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          records: batch.map(r => ({ fields: r }))
        })
      }
    );

    const data = await response.json();
    results.push(...data.records);

    // Rate limiting delay
    if (batches.indexOf(batch) < batches.length - 1) {
      await new Promise(resolve => setTimeout(resolve, DELAY_MS));
    }
  }

  return results;
}
```

### 6. Webhook Lifecycle Management

```javascript
class WebhookManager {
  constructor(baseId, token) {
    this.baseId = baseId;
    this.token = token;
    this.webhookId = null;
    this.refreshInterval = null;
  }

  async create(notificationUrl, filters = {}) {
    const response = await fetch(
      `https://api.airtable.com/v0/bases/${this.baseId}/webhooks`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          notificationUrl,
          specification: {
            options: { filters: filters.dataTypes ? { dataTypes: filters.dataTypes } : {} }
          }
        })
      }
    );

    const webhook = await response.json();
    this.webhookId = webhook.id;
    this.startAutoRefresh();
    return webhook;
  }

  async refresh() {
    if (!this.webhookId) throw new Error('No webhook ID');

    const response = await fetch(
      `https://api.airtable.com/v0/bases/${this.baseId}/webhooks/${this.webhookId}/refresh`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );

    return await response.json();
  }

  startAutoRefresh() {
    // Refresh every 6 days (7-day expiration)
    this.refreshInterval = setInterval(() => {
      this.refresh().catch(console.error);
    }, 6 * 24 * 60 * 60 * 1000);
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  async delete() {
    if (!this.webhookId) throw new Error('No webhook ID');

    await fetch(
      `https://api.airtable.com/v0/bases/${this.baseId}/webhooks/${this.webhookId}`,
      {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${this.token}` }
      }
    );

    this.stopAutoRefresh();
    this.webhookId = null;
  }
}

// Usage
const manager = new WebhookManager(baseId, token);
await manager.create('https://your-server.com/webhook', {
  dataTypes: ['tableData']
});
```

### 7. Attachment Upload Workflow

```javascript
async function uploadAttachment(baseId, tableName, recordId, token, fileBuffer, filename) {
  // Step 1: Upload to Airtable CDN
  const uploadResponse = await fetch(
    `https://api.airtable.com/v0/${baseId}/${tableName}/uploadAttachment`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/octet-stream'
      },
      body: fileBuffer
    }
  );

  const { url } = await uploadResponse.json();

  // Step 2: Update record with attachment URL
  const updateResponse = await fetch(
    `https://api.airtable.com/v0/${baseId}/${tableName}`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        records: [
          {
            id: recordId,
            fields: {
              Attachments: [{ url, filename }]
            }
          }
        ]
      })
    }
  );

  return await updateResponse.json();
}
```

### 8. CSV Sync Workflow

```javascript
async function syncCSV(baseId, tableName, token, csvData) {
  const response = await fetch(
    `https://api.airtable.com/v0/${baseId}/${tableName}/sync`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'text/csv'
      },
      body: csvData
    }
  );

  if (response.status === 429) {
    // Rate limit: 20 requests per 5 minutes
    throw new Error('CSV sync rate limit exceeded. Wait 5 minutes.');
  }

  return await response.json();
}

// Usage
const csv = `Name,Email,Status
John Doe,john@example.com,Active
Jane Smith,jane@example.com,Pending`;

await syncCSV(baseId, 'Contacts', token, csv);
```

---

## JavaScript SDK Guide

### Installation

```bash
npm install airtable
```

### Basic Setup

```javascript
const Airtable = require('airtable');

// Global configuration
Airtable.configure({
  apiKey: process.env.AIRTABLE_TOKEN
});

// Get base reference
const base = Airtable.base('appXXXXXXXXXXXXXX');
```

### Reading Records

```javascript
// Get all records
const records = await base('TableName').select().all();

// With filtering
const filtered = await base('TableName')
  .select({
    filterByFormula: "AND({Status}='Active', {Priority}>7)",
    sort: [{ field: 'Priority', direction: 'desc' }],
    maxRecords: 100,
    fields: ['Name', 'Email', 'Status']
  })
  .all();

// Pagination with eachPage
base('TableName').select({ pageSize: 100 })
  .eachPage(
    (records, fetchNextPage) => {
      records.forEach(record => {
        console.log(record.id, record.fields.Name);
      });
      fetchNextPage();
    },
    (err) => {
      if (err) console.error(err);
    }
  );

// Get first page only
const firstPage = await base('TableName')
  .select({ maxRecords: 100 })
  .firstPage();

// Get single record
const record = await base('TableName').find('recXXXXXXXXXXXXXXX');
console.log(record.fields.Name);
```

### Creating Records

```javascript
// Create single record
const newRecord = await base('TableName').create({
  'Name': 'John Doe',
  'Email': 'john@example.com',
  'Status': 'Active'
});
console.log(newRecord.id);

// Create multiple records (max 10)
const newRecords = await base('TableName').create([
  { 'Name': 'John Doe', 'Email': 'john@example.com' },
  { 'Name': 'Jane Smith', 'Email': 'jane@example.com' }
]);

// With typecast (auto-convert types)
const record = await base('TableName').create(
  { 'Name': 'Test', 'Price': '99.99' },  // String will convert to number
  { typecast: true }
);
```

### Updating Records

```javascript
// Update single record
const updated = await base('TableName').update('recXXX', {
  'Status': 'Completed',
  'Notes': 'Task finished'
});

// Update multiple records (max 10)
const updatedRecords = await base('TableName').update([
  { id: 'recXXX', fields: { 'Status': 'Completed' } },
  { id: 'recYYY', fields: { 'Status': 'Active' } }
]);

// Upsert (create or update)
const upserted = await base('TableName').update(
  [
    { fields: { 'Email': 'john@example.com', 'Name': 'John Doe Updated' } }
  ],
  { performUpsert: { fieldsToMergeOn: ['Email'] } }
);

console.log('Created:', upserted.createdRecords.length);
console.log('Updated:', upserted.updatedRecords.length);
```

### Deleting Records

```javascript
// Delete single record
await base('TableName').destroy('recXXXXXXXXXXXXXXX');

// Delete multiple records (max 10)
await base('TableName').destroy([
  'recXXXXXXXXXXXXXXX',
  'recYYYYYYYYYYYYYYY'
]);
```

### Error Handling

```javascript
try {
  const records = await base('TableName').select().all();
} catch (err) {
  if (err.statusCode === 401) {
    console.error('Unauthorized: Check API key');
  } else if (err.statusCode === 429) {
    console.error('Rate limit exceeded: Wait 30 seconds');
  } else if (err.statusCode === 404) {
    console.error('Not found: Check base/table name');
  } else {
    console.error('Error:', err.message);
  }
}
```

---

## Python SDK Guide

### Installation

```bash
pip install pyairtable
```

### Basic Setup

```python
import os
from pyairtable import Api, Base, Table

# Initialize API
api = Api(os.environ['AIRTABLE_TOKEN'])

# Get base
base = api.base('appXXXXXXXXXXXXXX')

# Get table
table = base.table('TableName')
# Or
table = Table(os.environ['AIRTABLE_TOKEN'], 'appXXX', 'TableName')
```

### Reading Records

```python
# Get all records
all_records = table.all()

# With filtering
filtered = table.all(
    formula="AND({Status}='Active', {Priority}>7)",
    sort=['Priority'],
    max_records=100,
    fields=['Name', 'Email', 'Status']
)

# Iterate records (automatic pagination)
for record in table.iterate():
    print(record['id'], record['fields']['Name'])

# Get single record
record = table.get('recXXXXXXXXXXXXXXX')
print(record['fields']['Name'])

# Get first record matching formula
first = table.first(formula="{Status}='Active'")
```

### Creating Records

```python
# Create single record
new_record = table.create({
    'Name': 'John Doe',
    'Email': 'john@example.com',
    'Status': 'Active'
})
print(new_record['id'])

# Create multiple records (batch)
new_records = table.batch_create([
    {'Name': 'John Doe', 'Email': 'john@example.com'},
    {'Name': 'Jane Smith', 'Email': 'jane@example.com'}
])

# With typecast
record = table.create(
    {'Name': 'Test', 'Price': '99.99'},
    typecast=True
)
```

### Updating Records

```python
# Update single record
updated = table.update('recXXX', {
    'Status': 'Completed',
    'Notes': 'Task finished'
})

# Update multiple records (batch)
table.batch_update([
    {'id': 'recXXX', 'fields': {'Status': 'Completed'}},
    {'id': 'recYYY', 'fields': {'Status': 'Active'}}
])

# Upsert (create or update)
upserted = table.batch_upsert(
    [
        {'Email': 'john@example.com', 'Name': 'John Doe Updated'},
        {'Email': 'jane@example.com', 'Name': 'Jane Smith Updated'}
    ],
    key_fields=['Email']
)

print(f"Created: {len(upserted['createdRecords'])}")
print(f"Updated: {len(upserted['updatedRecords'])}")
```

### Deleting Records

```python
# Delete single record
table.delete('recXXXXXXXXXXXXXXX')

# Delete multiple records (batch)
table.batch_delete(['recXXX', 'recYYY', 'recZZZ'])
```

### Rate Limiting

```python
from pyairtable.api import RateLimiter

# Built-in rate limiter (5 req/sec)
rate_limiter = RateLimiter(rate=5, per_seconds=1)
rate_limiter.acquire_sync()

# Use with custom client
from pyairtable import Table

class RateLimitedTable(Table):
    def __init__(self, *args, rate_limiter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rate_limiter = rate_limiter

    def all(self, *args, **kwargs):
        if self.rate_limiter:
            self.rate_limiter.acquire_sync()
        return super().all(*args, **kwargs)
```

### Error Handling

```python
from pyairtable.api.exceptions import (
    RateLimitError,
    UnauthorizedError,
    NotFoundError,
    InvalidRequestError
)

try:
    records = table.all()
except UnauthorizedError:
    print("Unauthorized: Check API token")
except NotFoundError:
    print("Not found: Check base/table name")
except RateLimitError:
    print("Rate limit exceeded: Wait 30 seconds")
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Rate Limiting & Performance

### Rate Limits

**Per-Base Limits:**
- **5 requests per second** (all pricing tiers)
- Applies to all operations on a single base
- Shared across all API keys accessing that base

**User-Level Limits (Personal Access Tokens):**
- **50 requests per second** across all bases
- Applies to all traffic using the same PAT
- Higher limit for power users

**Special Limits:**
- CSV Sync: **20 requests per 5 minutes**
- Attachment uploads: Share base rate limits

**429 Error Handling:**
- Required wait time: **30 seconds** before retrying
- Implement exponential backoff
- JavaScript SDK has built-in retry logic

### Performance Optimization Strategies

#### 1. Batch Operations
```javascript
// ❌ Bad: Multiple individual requests
for (const record of records) {
  await base('Table').create(record);  // 100 records = 100 requests
}

// ✅ Good: Batch create (10 per request)
const batches = chunk(records, 10);
for (const batch of batches) {
  await base('Table').create(batch);  // 100 records = 10 requests
}
```

#### 2. Field Selection
```javascript
// ❌ Bad: Fetch all fields
const records = await base('Table').select().all();

// ✅ Good: Only fetch needed fields
const records = await base('Table')
  .select({ fields: ['Name', 'Email', 'Status'] })
  .all();
```

#### 3. Server-Side Filtering
```javascript
// ❌ Bad: Client-side filtering
const allRecords = await base('Table').select().all();
const filtered = allRecords.filter(r => r.fields.Status === 'Active');

// ✅ Good: Server-side filtering
const filtered = await base('Table')
  .select({ filterByFormula: "{Status}='Active'" })
  .all();
```

#### 4. Pagination Control
```javascript
// ❌ Bad: Fetch all records at once
const records = await base('Table').select().all();  // Could be 10,000+ records

// ✅ Good: Controlled pagination
const firstPage = await base('Table')
  .select({ maxRecords: 100 })
  .firstPage();
```

#### 5. Incremental Sync
```javascript
// ❌ Bad: Full sync every time
const allRecords = await base('Table').select().all();

// ✅ Good: Incremental sync with LAST_MODIFIED_TIME
const formula = `IS_AFTER(LAST_MODIFIED_TIME(), ` +
  `DATETIME_PARSE('${lastSyncTime}', 'YYYY-MM-DDTHH:mm:ss.SSSZ'))`;
const updated = await base('Table')
  .select({ filterByFormula: formula })
  .all();
```

#### 6. Upsert vs Create/Update
```javascript
// ❌ Bad: Check existence, then create or update
const existing = await base('Table')
  .select({ filterByFormula: `{Email}='${email}'` })
  .firstPage();

if (existing.length > 0) {
  await base('Table').update(existing[0].id, fields);
} else {
  await base('Table').create(fields);
}

// ✅ Good: Single upsert operation
await base('Table').update(
  [{ fields }],
  { performUpsert: { fieldsToMergeOn: ['Email'] } }
);
```

#### 7. Parallel Requests (Within Limits)
```javascript
// ❌ Bad: Sequential requests
for (const table of tables) {
  await fetchTableData(table);
}

// ✅ Good: Parallel requests (respecting rate limits)
const promises = tables.map(table => fetchTableData(table));
const results = await Promise.all(promises);
```

#### 8. Caching
```javascript
class AirtableCache {
  constructor(ttl = 60000) {  // 1 minute TTL
    this.cache = new Map();
    this.ttl = ttl;
  }

  async get(key, fetchFn) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      return cached.data;
    }

    const data = await fetchFn();
    this.cache.set(key, { data, timestamp: Date.now() });
    return data;
  }
}

// Usage
const cache = new AirtableCache();
const records = await cache.get('active-contacts', () =>
  base('Contacts').select({ filterByFormula: "{Status}='Active'" }).all()
);
```

---

## Webhooks & Real-time Updates

### Webhook Overview

**Purpose:**
- Receive notifications when data changes in Airtable
- Build real-time integrations without polling
- Trigger automations based on Airtable events

**Lifecycle:**
- Webhooks expire after **7 days** if not refreshed
- Refresh extends expiration by another 7 days
- Must refresh every 6 days to prevent expiration
- Requires **base creator** permissions

### Creating Webhooks

```javascript
const response = await fetch(
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
            dataTypes: ['tableData'],  // or ['tableData', 'tableFields', 'tableMetadata']
            recordChangeScope: 'tblXXX',  // Optional: specific table ID
            watchDataInFieldIds: ['fldXXX', 'fldYYY']  // Optional: specific fields
          }
        }
      }
    })
  }
);

const webhook = await response.json();
console.log('Webhook ID:', webhook.id);
console.log('Expiration:', webhook.expirationTime);  // 7 days from now
```

### Webhook Specification Options

```typescript
{
  options: {
    filters: {
      // Data type filters
      dataTypes?: ['tableData' | 'tableFields' | 'tableMetadata'],

      // Scope to specific table
      recordChangeScope?: 'tblXXX',

      // Watch specific fields only
      watchDataInFieldIds?: ['fldXXX', 'fldYYY'],

      // Watch specific record IDs
      watchRecords?: {
        recordIds: ['recXXX', 'recYYY']
      },

      // Watch all tables or specific tables
      watchSchemas?: {
        tableIds: ['tblXXX', 'tblYYY']
      }
    }
  }
}
```

### Webhook Payload Structure

```json
{
  "base": {
    "id": "appXXX"
  },
  "webhook": {
    "id": "achXXX"
  },
  "timestamp": "2024-01-15T10:30:00.000Z",
  "actionMetadata": {
    "source": "publicApi",
    "sourceMetadata": {
      "user": {
        "id": "usrXXX",
        "email": "user@example.com"
      }
    }
  },
  "changedTablesById": {
    "tblXXX": {
      "createdRecordsById": {
        "recXXX": {
          "createdTime": "2024-01-15T10:30:00.000Z",
          "cellValuesByFieldId": {
            "fldXXX": "John Doe",
            "fldYYY": "john@example.com"
          }
        }
      },
      "changedRecordsById": {
        "recYYY": {
          "current": {
            "cellValuesByFieldId": {
              "fldXXX": "Updated Value"
            }
          },
          "previous": {
            "cellValuesByFieldId": {
              "fldXXX": "Old Value"
            }
          },
          "unchanged": {
            "cellValuesByFieldId": {
              "fldYYY": "Unchanged Value"
            }
          }
        }
      },
      "destroyedRecordIds": ["recZZZ"]
    }
  }
}
```

**Note:** Webhook payloads contain **abbreviated data**. For complete record data, fetch from API.

### Refreshing Webhooks

```javascript
async function refreshWebhook(baseId, webhookId, token) {
  const response = await fetch(
    `https://api.airtable.com/v0/bases/${baseId}/webhooks/${webhookId}/refresh`,
    {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );

  const data = await response.json();
  console.log('New expiration:', data.expirationTime);
  return data;
}

// Auto-refresh every 6 days
setInterval(() => {
  refreshWebhook(baseId, webhookId, token).catch(console.error);
}, 6 * 24 * 60 * 60 * 1000);
```

### Handling Webhook Notifications

```javascript
// Express.js webhook receiver
app.post('/webhook', express.json(), async (req, res) => {
  const payload = req.body;

  // Acknowledge receipt immediately (must respond within 30 seconds)
  res.status(200).json({ success: true });

  // Process webhook asynchronously
  processWebhookAsync(payload).catch(console.error);
});

async function processWebhookAsync(payload) {
  const { changedTablesById } = payload;

  for (const [tableId, changes] of Object.entries(changedTablesById)) {
    // Handle created records
    if (changes.createdRecordsById) {
      for (const [recordId, record] of Object.entries(changes.createdRecordsById)) {
        console.log('Created:', recordId, record.cellValuesByFieldId);

        // Fetch full record data from API
        const fullRecord = await fetchRecord(baseId, tableId, recordId, token);
        await processCreatedRecord(fullRecord);
      }
    }

    // Handle changed records
    if (changes.changedRecordsById) {
      for (const [recordId, change] of Object.entries(changes.changedRecordsById)) {
        console.log('Changed:', recordId);
        console.log('Current:', change.current.cellValuesByFieldId);
        console.log('Previous:', change.previous.cellValuesByFieldId);

        await processChangedRecord(recordId, change);
      }
    }

    // Handle deleted records
    if (changes.destroyedRecordIds) {
      for (const recordId of changes.destroyedRecordIds) {
        console.log('Deleted:', recordId);
        await processDeletedRecord(recordId);
      }
    }
  }
}
```

### Best Practices

1. **Respond quickly** - Return 200 OK within 30 seconds
2. **Process asynchronously** - Don't block webhook response
3. **Fetch full data** - Webhook payloads are abbreviated
4. **Auto-refresh** - Schedule refresh every 6 days
5. **Handle duplicates** - Webhooks may send duplicate events
6. **Validate source** - Verify webhook comes from Airtable
7. **Error handling** - Implement retry logic for processing failures
8. **Monitor expiration** - Alert before webhook expires

---

## Error Handling & Troubleshooting

### Common HTTP Status Codes

| Code | Meaning | Common Causes | Solution |
|------|---------|---------------|----------|
| 200 | OK | Success | - |
| 401 | Unauthorized | Invalid/missing token, expired token | Regenerate PAT, check Authorization header |
| 403 | Forbidden | Insufficient permissions, wrong scope | Add required scopes, verify base access |
| 404 | Not Found | Base/table/record doesn't exist | Verify IDs, check permissions |
| 422 | Unprocessable Entity | Invalid field names/types, formula error | Check field names, verify data types |
| 429 | Too Many Requests | Rate limit exceeded | Wait 30 seconds, implement backoff |
| 413 | Request Too Large | Batch >10 records, request >16MB | Reduce batch size |
| 503 | Service Unavailable | Airtable server issues | Retry with exponential backoff |

### Error Response Format

```json
{
  "error": {
    "type": "INVALID_REQUEST_BODY",
    "message": "Invalid field name: 'InvalidField'"
  }
}
```

### Retry Logic with Exponential Backoff

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);

      if (response.status === 429) {
        // Rate limit: wait 30 seconds
        await new Promise(resolve => setTimeout(resolve, 30000));
        continue;
      }

      if (response.status === 503) {
        // Server error: exponential backoff
        const delay = Math.pow(2, i) * 1000;  // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(`${response.status}: ${error.error.message}`);
      }

      return await response.json();

    } catch (error) {
      if (i === maxRetries - 1) throw error;
      console.error(`Retry ${i + 1}/${maxRetries}:`, error.message);
    }
  }
}
```

### Common Issues & Solutions

#### 1. Empty Fields Not Returned

**Issue:**
```javascript
const record = await base('Table').find('recXXX');
console.log(record.fields.OptionalField);  // undefined
```

**Cause:** Airtable doesn't return empty fields (`""`, `[]`, `false`, `null`)

**Solution:**
```javascript
const value = record.fields.OptionalField || 'default value';
const tags = record.fields.Tags || [];
const isActive = record.fields.IsActive ?? false;
```

#### 2. URL Character Limit (16,000 chars)

**Issue:**
```javascript
const formula = "OR({Field1}='Value1', {Field2}='Value2', ...)";  // Very long
const url = `https://api.airtable.com/v0/appXXX/Table?filterByFormula=${encodeURIComponent(formula)}`;
// URL too long!
```

**Solution:** Use POST to `/listRecords`:
```javascript
const response = await fetch(
  `https://api.airtable.com/v0/appXXX/Table/listRecords`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      filterByFormula: formula,
      sort: [{field: 'Name', direction: 'asc'}]
    })
  }
);
```

#### 3. Linked Record Data Not Included

**Issue:**
```javascript
const record = await base('Table').find('recXXX');
console.log(record.fields.LinkedRecords);  // ['recYYY', 'recZZZ'] (just IDs)
```

**Solution:** Fetch linked records separately:
```javascript
const linkedIds = record.fields.LinkedRecords || [];
const linkedRecords = await Promise.all(
  linkedIds.map(id => base('RelatedTable').find(id))
);
```

#### 4. Attachment URL Expiration

**Issue:** Attachment URLs expire after 2 hours

**Solution:**
```javascript
async function getValidAttachmentUrl(baseId, tableName, recordId, fieldName, token) {
  // Always fetch fresh from API
  const record = await base(tableName).find(recordId);
  const attachments = record.fields[fieldName] || [];
  return attachments[0]?.url;  // Fresh URL
}
```

#### 5. Formula Field Calculation Delays

**Issue:** Formula fields may not update immediately

**Solution:**
```javascript
async function waitForFormulaUpdate(baseId, tableName, recordId, fieldName, token) {
  let retries = 5;
  while (retries > 0) {
    const record = await base(tableName).find(recordId);
    const value = record.fields[fieldName];

    if (value !== null && value !== undefined) {
      return value;
    }

    await new Promise(resolve => setTimeout(resolve, 1000));
    retries--;
  }
  throw new Error('Formula field did not update');
}
```

---

## Enterprise Features

### Base Management

#### Delete Base (Enterprise Admin Only)
```javascript
await fetch(`https://api.airtable.com/v0/meta/bases/${baseId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

**Notes:**
- Requires enterprise admin permissions
- Bases moved to Trash (restorable)
- Cannot delete last base in workspace

### Workspace Management

#### List Workspaces
```
GET /v0/meta/workspaces
```

#### Create Workspace
```
POST /v0/meta/workspaces
```

#### Get Workspace Restrictions
```
GET /v0/meta/workspaces/{workspaceId}/restrictions
```

### User Management

#### List Users (Enterprise)
```
GET /v0/meta/users
```

#### Provision User on Workspace
```
POST /v0/meta/workspaces/{workspaceId}/users
```

#### Remove User from Workspace
```
DELETE /v0/meta/workspaces/{workspaceId}/users/{userId}
```

### Audit Logs (Enterprise)

#### List Audit Log Events
```
GET /v0/meta/auditLogs/events
```

**Query Parameters:**
- `startDate` - Filter events after date
- `endDate` - Filter events before date
- `actionType` - Filter by action type
- `userId` - Filter by user

### SCIM Support (Enterprise)

**SCIM 2.0 endpoints for user provisioning:**
```
GET  /v1/scim/Users
POST /v1/scim/Users
GET  /v1/scim/Users/{id}
PATCH /v1/scim/Users/{id}
DELETE /v1/scim/Users/{id}

GET  /v1/scim/Groups
POST /v1/scim/Groups
GET  /v1/scim/Groups/{id}
PATCH /v1/scim/Groups/{id}
DELETE /v1/scim/Groups/{id}
```

---

## Best Practices

### Security

1. **Use Personal Access Tokens (PATs)** - API keys deprecated Feb 2024
2. **Store tokens in environment variables** - Never hardcode in source
3. **Implement minimal scopes** - Only grant required permissions
4. **Rotate tokens regularly** - Generate new tokens periodically
5. **Use OAuth for user apps** - Let users authorize their own bases
6. **Validate webhook sources** - Verify notifications come from Airtable
7. **Secure webhook endpoints** - Use HTTPS, implement authentication

### Performance

1. **Batch operations** - Create/update up to 10 records per request
2. **Use filterByFormula** - Filter server-side, not client-side
3. **Select specific fields** - Reduce response size with `fields` parameter
4. **Implement pagination** - Don't fetch all records at once
5. **Use incremental sync** - Query only changed records with `LAST_MODIFIED_TIME()`
6. **Respect rate limits** - 5 req/sec per base, 50 req/sec per user
7. **Cache responses** - Reduce API calls for static data
8. **Use upsert** - Single operation instead of check-then-create/update

### Data Integrity

1. **Validate before create/update** - Check required fields and types
2. **Handle empty fields** - Account for missing/null values
3. **Use record IDs** - Don't rely on field values as unique identifiers
4. **Implement error handling** - Retry failed operations with backoff
5. **Test with sandbox base** - Don't test in production
6. **Monitor webhook expiration** - Auto-refresh every 6 days
7. **Fetch full record data** - Webhook payloads are abbreviated

### Code Organization

1. **Create reusable clients** - Encapsulate API logic in classes
2. **Use environment config** - Store base IDs, table names in env
3. **Implement logging** - Track API calls and errors
4. **Write integration tests** - Test against sandbox base
5. **Document field mappings** - Maintain field name/type reference
6. **Version control schemas** - Track table structure changes
7. **Handle breaking changes** - Monitor API changelog

### Monitoring

1. **Track rate limit usage** - Monitor 429 errors
2. **Alert on webhook expiration** - Notify before 7-day deadline
3. **Log failed operations** - Track and retry failures
4. **Monitor API latency** - Detect performance degradation
5. **Set up error notifications** - Alert on repeated errors
6. **Track sync lag** - Monitor incremental sync delays
7. **Dashboard API health** - Visualize success/error rates

---

## Complete Code Examples

### Full CRUD Client (JavaScript)

```javascript
const Airtable = require('airtable');

class AirtableClient {
  constructor(apiKey, baseId) {
    this.base = new Airtable({ apiKey }).base(baseId);
  }

  // List records with filtering
  async list(tableName, options = {}) {
    try {
      const records = await this.base(tableName)
        .select({
          filterByFormula: options.filterByFormula,
          sort: options.sort,
          fields: options.fields,
          maxRecords: options.maxRecords || 100
        })
        .all();

      return records.map(r => ({
        id: r.id,
        createdTime: r.fields.createdTime,
        ...r.fields
      }));
    } catch (error) {
      this.handleError(error);
    }
  }

  // Get single record
  async get(tableName, recordId) {
    try {
      const record = await this.base(tableName).find(recordId);
      return { id: record.id, ...record.fields };
    } catch (error) {
      this.handleError(error);
    }
  }

  // Create records (batch up to 10)
  async create(tableName, records) {
    try {
      const created = await this.base(tableName).create(
        records.map(r => ({ fields: r }))
      );
      return created.map(r => ({ id: r.id, ...r.fields }));
    } catch (error) {
      this.handleError(error);
    }
  }

  // Update records (batch up to 10)
  async update(tableName, records) {
    try {
      const updated = await this.base(tableName).update(
        records.map(r => ({ id: r.id, fields: r.fields }))
      );
      return updated.map(r => ({ id: r.id, ...r.fields }));
    } catch (error) {
      this.handleError(error);
    }
  }

  // Upsert records
  async upsert(tableName, records, mergeFields) {
    try {
      const result = await this.base(tableName).update(
        records.map(r => ({ fields: r })),
        { performUpsert: { fieldsToMergeOn: mergeFields } }
      );

      console.log(`Created: ${result.createdRecords.length}`);
      console.log(`Updated: ${result.updatedRecords.length}`);

      return result.records.map(r => ({ id: r.id, ...r.fields }));
    } catch (error) {
      this.handleError(error);
    }
  }

  // Delete records (batch up to 10)
  async delete(tableName, recordIds) {
    try {
      await this.base(tableName).destroy(recordIds);
      return { deleted: recordIds.length };
    } catch (error) {
      this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.statusCode === 401) {
      throw new Error('Unauthorized: Invalid API key');
    } else if (error.statusCode === 403) {
      throw new Error('Forbidden: Insufficient permissions');
    } else if (error.statusCode === 404) {
      throw new Error('Not found: Check base/table/record ID');
    } else if (error.statusCode === 422) {
      throw new Error(`Invalid request: ${error.message}`);
    } else if (error.statusCode === 429) {
      throw new Error('Rate limit exceeded: Wait 30 seconds');
    } else {
      throw error;
    }
  }
}

// Usage
const client = new AirtableClient(
  process.env.AIRTABLE_TOKEN,
  'appXXXXXXXXXXXXXX'
);

// List active contacts
const contacts = await client.list('Contacts', {
  filterByFormula: "{Status}='Active'",
  sort: [{ field: 'Name', direction: 'asc' }],
  fields: ['Name', 'Email', 'Phone']
});

// Create contacts
const newContacts = await client.create('Contacts', [
  { Name: 'John Doe', Email: 'john@example.com' },
  { Name: 'Jane Smith', Email: 'jane@example.com' }
]);

// Upsert contacts (merge on email)
const upserted = await client.upsert('Contacts', [
  { Email: 'john@example.com', Name: 'John Doe Updated', Status: 'Active' }
], ['Email']);
```

### Full CRUD Client (Python)

```python
import os
from typing import List, Dict, Optional
from pyairtable import Api, Table
from pyairtable.api.exceptions import (
    RateLimitError,
    UnauthorizedError,
    NotFoundError,
    InvalidRequestError
)

class AirtableClient:
    def __init__(self, api_key: str, base_id: str):
        self.api = Api(api_key)
        self.base_id = base_id

    def _get_table(self, table_name: str) -> Table:
        return self.api.base(self.base_id).table(table_name)

    # List records with filtering
    def list(
        self,
        table_name: str,
        formula: Optional[str] = None,
        sort: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        max_records: int = 100
    ) -> List[Dict]:
        try:
            table = self._get_table(table_name)
            records = table.all(
                formula=formula,
                sort=sort,
                fields=fields,
                max_records=max_records
            )
            return [{**r['fields'], 'id': r['id']} for r in records]
        except Exception as e:
            self._handle_error(e)

    # Get single record
    def get(self, table_name: str, record_id: str) -> Dict:
        try:
            table = self._get_table(table_name)
            record = table.get(record_id)
            return {**record['fields'], 'id': record['id']}
        except Exception as e:
            self._handle_error(e)

    # Create records (batch)
    def create(self, table_name: str, records: List[Dict]) -> List[Dict]:
        try:
            table = self._get_table(table_name)
            created = table.batch_create(records)
            return [{**r['fields'], 'id': r['id']} for r in created]
        except Exception as e:
            self._handle_error(e)

    # Update records (batch)
    def update(self, table_name: str, records: List[Dict]) -> List[Dict]:
        try:
            table = self._get_table(table_name)
            updates = [
                {'id': r['id'], 'fields': {k: v for k, v in r.items() if k != 'id'}}
                for r in records
            ]
            updated = table.batch_update(updates)
            return [{**r['fields'], 'id': r['id']} for r in updated]
        except Exception as e:
            self._handle_error(e)

    # Upsert records
    def upsert(
        self,
        table_name: str,
        records: List[Dict],
        merge_fields: List[str]
    ) -> Dict:
        try:
            table = self._get_table(table_name)
            result = table.batch_upsert(records, key_fields=merge_fields)

            print(f"Created: {len(result.get('createdRecords', []))}")
            print(f"Updated: {len(result.get('updatedRecords', []))}")

            return {
                'records': [{**r['fields'], 'id': r['id']} for r in result['records']],
                'created': result.get('createdRecords', []),
                'updated': result.get('updatedRecords', [])
            }
        except Exception as e:
            self._handle_error(e)

    # Delete records (batch)
    def delete(self, table_name: str, record_ids: List[str]) -> Dict:
        try:
            table = self._get_table(table_name)
            table.batch_delete(record_ids)
            return {'deleted': len(record_ids)}
        except Exception as e:
            self._handle_error(e)

    # Error handling
    def _handle_error(self, error: Exception):
        if isinstance(error, UnauthorizedError):
            raise Exception("Unauthorized: Invalid API key")
        elif isinstance(error, NotFoundError):
            raise Exception("Not found: Check base/table/record ID")
        elif isinstance(error, RateLimitError):
            raise Exception("Rate limit exceeded: Wait 30 seconds")
        elif isinstance(error, InvalidRequestError):
            raise Exception(f"Invalid request: {str(error)}")
        else:
            raise error

# Usage
client = AirtableClient(
    os.environ['AIRTABLE_TOKEN'],
    'appXXXXXXXXXXXXXX'
)

# List active contacts
contacts = client.list(
    'Contacts',
    formula="{Status}='Active'",
    sort=['Name'],
    fields=['Name', 'Email', 'Phone'],
    max_records=100
)

# Create contacts
new_contacts = client.create('Contacts', [
    {'Name': 'John Doe', 'Email': 'john@example.com'},
    {'Name': 'Jane Smith', 'Email': 'jane@example.com'}
])

# Upsert contacts (merge on email)
upserted = client.upsert('Contacts', [
    {'Email': 'john@example.com', 'Name': 'John Doe Updated', 'Status': 'Active'}
], ['Email'])
```

---

## Additional Resources

### Official Documentation
- Web API Reference: https://airtable.com/developers/web/api/introduction
- API Changelog: https://airtable.com/developers/web/api/changelog
- OAuth Reference: https://airtable.com/developers/web/api/oauth-reference
- Scopes Reference: https://airtable.com/developers/web/api/scopes

### SDKs
- JavaScript: https://github.com/Airtable/airtable.js
- Python: https://github.com/gtalarico/pyairtable

### Local Documentation
- Comprehensive Analysis: `~/Code/docs/airtable/airtable-api-comprehensive-analysis.md`
- Cheat Sheet: `~/Code/docs/airtable/airtable-api-cheat-sheet.md`
- Additional Reference: `~/Code/docs/All_APIs/API_Docs/Airtable API/Airtable-API.md`

---

**End of comprehensive documentation**
