# Copper CRM Workflows

Comprehensive guide to common workflows and operations in Copper CRM.

## Table of Contents

1. [Lead Lifecycle Workflow](#1-lead-lifecycle-workflow)
2. [Person and Company Management](#2-person-and-company-management)
3. [Opportunity Creation and Tracking](#3-opportunity-creation-and-tracking)
4. [Activity Logging Workflow](#4-activity-logging-workflow)
5. [Lead Conversion Process](#5-lead-conversion-process)
6. [Working with Custom Fields](#6-working-with-custom-fields)
7. [Related Records Workflow](#7-related-records-workflow)
8. [Bulk Import Workflow](#8-bulk-import-workflow)
9. [Data Sync Strategies](#9-data-sync-strategies)
10. [Step-by-Step Examples](#10-step-by-step-examples)

---

## 1. Lead Lifecycle Workflow

### Overview

Leads flow through stages from initial capture to conversion or disqualification.

### Lead Stages

1. **New** - Initial capture, uncontacted
2. **Contacted** - First contact made
3. **Qualified** - Meets qualification criteria
4. **Unqualified** - Does not meet criteria
5. **Converted** - Converted to Person/Opportunity

### Workflow Steps

```
Create Lead → Contact → Qualify → Convert or Disqualify
```

### Step 1: Create Lead

**Via API:**

```bash
POST /leads
{
  "name": "John Smith",
  "email": {
    "email": "john.smith@acmecorp.com",
    "category": "work"
  },
  "company_name": "Acme Corporation",
  "title": "VP of Sales",
  "phone_numbers": [{
    "number": "415-555-1234",
    "category": "mobile"
  }],
  "details": "Interested in enterprise plan",
  "tags": ["inbound", "enterprise"],
  "status": "New"
}
```

**Via CLI:**

```bash
python copper_cli.py create leads
# Interactive prompts follow
```

### Step 2: Contact Lead

Log interaction:

```bash
POST /activities
{
  "parent": {
    "id": <lead_id>,
    "type": "lead"
  },
  "type": {
    "category": "user",
    "name": "Call"
  },
  "details": "Initial discovery call - discussed needs"
}
```

### Step 3: Qualify Lead

Update lead status:

```bash
PUT /leads/{lead_id}
{
  "status": "Qualified",
  "tags": ["qualified", "hot"]
}
```

### Step 4: Convert or Disqualify

**Convert:** See [Lead Conversion Process](#5-lead-conversion-process)

**Disqualify:**

```bash
PUT /leads/{lead_id}
{
  "status": "Unqualified",
  "details": "Budget too small"
}
```

---

## 2. Person and Company Management

### Creating a Company First

Best practice: Create company before person records.

**Step 1: Create Company**

```bash
POST /companies
{
  "name": "Acme Corporation",
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "postal_code": "94105",
    "country": "US"
  },
  "phone_numbers": [{
    "number": "415-555-0000",
    "category": "work"
  }],
  "emails": [{
    "email": "contact@acmecorp.com",
    "category": "work"
  }],
  "websites": [{
    "url": "https://acmecorp.com",
    "category": "work"
  }],
  "details": "Enterprise software company"
}
```

**Step 2: Create Person Associated with Company**

```bash
POST /people
{
  "name": "Jane Doe",
  "email": {
    "email": "jane.doe@acmecorp.com",
    "category": "work"
  },
  "company_id": <company_id_from_step_1>,
  "title": "CTO",
  "phone_numbers": [{
    "number": "415-555-1234",
    "category": "mobile"
  }]
}
```

### Updating Person Information

```bash
PUT /people/{person_id}
{
  "title": "VP of Engineering",
  "phone_numbers": [{
    "number": "415-555-5678",
    "category": "work"
  }]
}
```

### Linking Existing Person to Company

```bash
PUT /people/{person_id}
{
  "company_id": <company_id>
}
```

### Managing Multiple Contacts

1. Create company once
2. Create all persons with same `company_id`
3. Set `primary_contact_id` on company if needed

---

## 3. Opportunity Creation and Tracking

### Prerequisites

- Company must exist
- Primary contact (person) must exist
- Pipeline and stage must be configured

### Step 1: Create Opportunity

```bash
POST /opportunities
{
  "name": "Acme Corp - Enterprise License",
  "primary_company_id": <company_id>,
  "primary_contact_id": <person_id>,
  "assignee_id": <user_id>,
  "close_date": "2025-06-30",
  "monetary_value": 50000,
  "currency": "USD",
  "status": "Open",
  "pipeline_id": 1,
  "stage_id": 2,
  "customer_source_id": 3,
  "details": "25 user licenses for enterprise plan",
  "tags": ["enterprise", "high-value"]
}
```

### Step 2: Track Progress Through Stages

**Move to next stage:**

```bash
PUT /opportunities/{opp_id}
{
  "stage_id": 3
}
```

**Update value:**

```bash
PUT /opportunities/{opp_id}
{
  "monetary_value": 75000,
  "details": "Expanded to 40 licenses"
}
```

### Step 3: Close Opportunity

**Win:**

```bash
PUT /opportunities/{opp_id}
{
  "status": "Won",
  "stage_id": <won_stage_id>
}
```

**Loss:**

```bash
PUT /opportunities/{opp_id}
{
  "status": "Lost",
  "loss_reason_id": <reason_id>,
  "details": "Chose competitor"
}
```

### Monitoring Pipeline

**Get all opportunities in a stage:**

```bash
GET /opportunities?stage_id=2
```

**Get opportunities closing this month:**

```bash
POST /opportunities/search
{
  "close_date": {
    "after": "2025-01-01",
    "before": "2025-01-31"
  }
}
```

---

## 4. Activity Logging Workflow

### Activity Types

- **Call** - Phone conversations
- **Email** - Email communications
- **Meeting** - In-person or virtual meetings
- **Task** - To-do items
- **Note** - General notes

### Logging an Activity

```bash
POST /activities
{
  "parent": {
    "id": <record_id>,
    "type": "opportunity"  # or "person", "company", "lead"
  },
  "type": {
    "category": "user",
    "name": "Call"
  },
  "details": "Discussed implementation timeline and requirements",
  "activity_date": 1640995200
}
```

### Activity Workflow Pattern

1. **Before Contact:** Create task
2. **During Contact:** Update task with notes
3. **After Contact:** Complete task, log outcome
4. **Schedule Follow-up:** Create new task

### Example: Complete Call Workflow

```bash
# Step 1: Create task
POST /tasks
{
  "name": "Call Jane Doe - Discovery",
  "related_resource": {
    "id": <opportunity_id>,
    "type": "opportunity"
  },
  "assignee_id": <user_id>,
  "due_date": "2025-01-15"
}

# Step 2: Complete task with notes
PUT /tasks/{task_id}
{
  "status": "Completed",
  "details": "Discussed pricing, needs demo"
}

# Step 3: Log activity
POST /activities
{
  "parent": {
    "id": <opportunity_id>,
    "type": "opportunity"
  },
  "type": {
    "category": "user",
    "name": "Call"
  },
  "details": "Discovery call completed - scheduling demo"
}

# Step 4: Create follow-up
POST /tasks
{
  "name": "Schedule Product Demo",
  "related_resource": {
    "id": <opportunity_id>,
    "type": "opportunity"
  },
  "due_date": "2025-01-20"
}
```

---

## 5. Lead Conversion Process

### Detailed Lead Conversion Workflow

Converting a lead creates a person record and optionally an opportunity.

### Step 1: Retrieve Lead Data

```bash
GET /leads/{lead_id}
```

### Step 2: Check for Existing Company

Search by company name to avoid duplicates:

```bash
POST /companies/search
{
  "name": "Acme Corporation"
}
```

### Step 3: Create or Link Company

**If company doesn't exist:**

```bash
POST /companies
{
  "name": "<lead.company_name>",
  "emails": [{
    "email": "<lead.email>",
    "category": "work"
  }]
}
```

**If company exists:** Use existing `company_id`

### Step 4: Create Person from Lead

```bash
POST /people
{
  "name": "<lead.name>",
  "email": {
    "email": "<lead.email>",
    "category": "work"
  },
  "company_id": <company_id>,
  "title": "<lead.title>",
  "phone_numbers": "<lead.phone_numbers>",
  "address": "<lead.address>",
  "details": "Converted from lead",
  "tags": "<lead.tags>"
}
```

### Step 5: Create Opportunity (Optional)

```bash
POST /opportunities
{
  "name": "Deal - <lead.company_name>",
  "primary_company_id": <company_id>,
  "primary_contact_id": <person_id>,
  "status": "Open",
  "pipeline_id": 1,
  "stage_id": 1
}
```

### Step 6: Mark Lead as Converted

```bash
PUT /leads/{lead_id}
{
  "status": "Converted",
  "details": "Converted to person #{person_id}"
}
```

Or delete the lead:

```bash
DELETE /leads/{lead_id}
```

### Complete Conversion Script

```python
def convert_lead(lead_id):
    # 1. Get lead
    lead = api.get(f"/leads/{lead_id}")

    # 2. Find or create company
    companies = api.post("/companies/search", {
        "name": lead["company_name"]
    })

    if companies:
        company_id = companies[0]["id"]
    else:
        company = api.post("/companies", {
            "name": lead["company_name"]
        })
        company_id = company["id"]

    # 3. Create person
    person = api.post("/people", {
        "name": lead["name"],
        "email": lead["email"],
        "company_id": company_id,
        "title": lead["title"],
        "phone_numbers": lead["phone_numbers"]
    })

    # 4. Create opportunity
    opportunity = api.post("/opportunities", {
        "name": f"Deal - {lead['company_name']}",
        "primary_company_id": company_id,
        "primary_contact_id": person["id"],
        "pipeline_id": 1,
        "stage_id": 1
    })

    # 5. Mark lead converted
    api.put(f"/leads/{lead_id}", {
        "status": "Converted"
    })

    return {
        "person_id": person["id"],
        "company_id": company_id,
        "opportunity_id": opportunity["id"]
    }
```

---

## 6. Working with Custom Fields

### Step 1: Get Custom Field Definitions

```bash
GET /custom_field_definitions
```

Response includes field IDs and types.

### Step 2: Set Custom Field Values

Custom fields use field definition ID as key:

```bash
PUT /opportunities/{opp_id}
{
  "custom_fields": [
    {
      "custom_field_definition_id": 12345,
      "value": "Enterprise"
    },
    {
      "custom_field_definition_id": 12346,
      "value": "2 Years"
    }
  ]
}
```

### Custom Field Types

- **Text** - String value
- **Number** - Numeric value
- **Date** - Unix timestamp
- **Dropdown** - Option ID from definition
- **Multi-Select** - Array of option IDs
- **Checkbox** - Boolean
- **URL** - String (URL format)

### Example: Setting All Field Types

```bash
PUT /companies/{company_id}
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100,
      "value": "Premium Customer"  # Text
    },
    {
      "custom_field_definition_id": 101,
      "value": 50000  # Number
    },
    {
      "custom_field_definition_id": 102,
      "value": 1640995200  # Date (Unix timestamp)
    },
    {
      "custom_field_definition_id": 103,
      "value": 5  # Dropdown (option ID)
    },
    {
      "custom_field_definition_id": 104,
      "value": [1, 3, 5]  # Multi-select (option IDs)
    },
    {
      "custom_field_definition_id": 105,
      "value": true  # Checkbox
    },
    {
      "custom_field_definition_id": 106,
      "value": "https://example.com"  # URL
    }
  ]
}
```

### Querying by Custom Fields

```bash
POST /opportunities/search
{
  "custom_fields": [
    {
      "custom_field_definition_id": 100,
      "value": "Premium Customer"
    }
  ]
}
```

---

## 7. Related Records Workflow

### Linking People to Companies

**Method 1: At Creation**

```bash
POST /people
{
  "name": "John Smith",
  "company_id": <company_id>
}
```

**Method 2: Update Existing**

```bash
PUT /people/{person_id}
{
  "company_id": <company_id>
}
```

### Linking Opportunities to Records

```bash
POST /opportunities
{
  "name": "Deal Name",
  "primary_company_id": <company_id>,
  "primary_contact_id": <person_id>,
  "secondary_contact_ids": [<person_id_2>, <person_id_3>]
}
```

### Managing Related Opportunities

**Link opportunities together:**

```bash
PUT /opportunities/{opp_id}
{
  "related_opportunities": [<opp_id_2>, <opp_id_3>]
}
```

### Retrieving Related Records

**Get all people at a company:**

```bash
POST /people/search
{
  "company_id": <company_id>
}
```

**Get all opportunities for a company:**

```bash
POST /opportunities/search
{
  "primary_company_id": <company_id>
}
```

**Get all activities for an opportunity:**

```bash
GET /opportunities/{opp_id}/activities
```

---

## 8. Bulk Import Workflow

### Overview

Bulk importing allows you to import hundreds or thousands of records efficiently with validation, duplicate detection, and error recovery.

### Step 1: Prepare CSV File

**For Leads:**

```csv
name,email,company_name,title,phone
John Smith,john@acme.com,Acme Corp,VP Sales,555-0101
Jane Doe,jane@techco.io,TechCo,CTO,555-0102
```

**For People:**

```csv
name,email,company_name,title
John Smith,john@acme.com,Acme Corp,VP Sales
Jane Doe,jane@techco.io,TechCo,CTO
```

**For Companies:**

```csv
name,email_domain,address
Acme Corp,acme.com,"123 Main St, SF, CA"
TechCo,techco.io,"456 Oak Ave, NY, NY"
```

**For Opportunities:**

```csv
name,primary_contact_email,monetary_value
Big Deal,john@acme.com,50000
Quick Win,jane@techco.io,10000
```

### Step 2: Validate CSV Format

```bash
python validate_config.py leads.csv leads
```

### Step 3: Run Import (UPSERT Mode)

```bash
python bulk_import.py leads leads.csv --mode upsert
```

Or via CLI:

```bash
python copper_cli.py bulk-import leads.csv \
  --entity leads \
  --upsert \
  --upsert-field email
```

### Step 4: Review Results

Import summary shows:
- Total records processed
- Successful imports
- Duplicates updated
- Failed records with errors
- Success rate

### Step 5: Handle Failures

Review failed records and fix issues:

```
Failed Records:
  Row 45: Invalid email format
  Row 87: Missing required field: company_name
```

### Bulk Import Best Practices

1. **Start Small:** Test with 10-20 records first
2. **Use Dry Run:** `--dry-run` flag to preview without changes
3. **UPSERT by Default:** Prevents duplicates
4. **Validate First:** Check CSV format before importing
5. **Monitor Progress:** Watch for errors in real-time
6. **Batch Processing:** Automatic (10 records per batch)
7. **Rate Limiting:** Built-in (3 req/sec)
8. **Error Recovery:** Automatic retries (3 attempts)

### Import Modes

**CREATE Mode:**
- Creates new records only
- Skips duplicates
- Faster (no duplicate checking)

```bash
python bulk_import.py leads leads.csv --mode create
```

**UPSERT Mode (Recommended):**
- Updates existing records
- Creates new if not found
- Prevents duplicates

```bash
python bulk_import.py leads leads.csv --mode upsert
```

---

## 9. Data Sync Strategies

### Strategy 1: Incremental Sync

Sync only new/modified records since last sync.

**Implementation:**

```python
def incremental_sync():
    # Get last sync timestamp
    last_sync = get_last_sync_time()

    # Fetch records modified since last sync
    response = api.post("/people/search", {
        "modified_date": {
            "after": last_sync
        }
    })

    # Process new/modified records
    for record in response:
        sync_to_external_system(record)

    # Update last sync timestamp
    save_last_sync_time(current_timestamp)
```

### Strategy 2: UPSERT Sync

Update existing records or create new ones.

**Implementation:**

```python
def upsert_sync(records):
    for record in records:
        # Search for existing record
        existing = api.post("/people/search", {
            "email": record["email"]
        })

        if existing:
            # Update existing
            api.put(f"/people/{existing[0]['id']}", record)
        else:
            # Create new
            api.post("/people", record)
```

### Strategy 3: Bidirectional Sync

Sync changes in both directions between systems.

**Implementation:**

```python
def bidirectional_sync():
    # Copper → External System
    copper_modified = get_copper_modified_since(last_sync)
    for record in copper_modified:
        push_to_external(record)

    # External System → Copper
    external_modified = get_external_modified_since(last_sync)
    for record in external_modified:
        push_to_copper(record)
```

### Strategy 4: Full Refresh

Periodically sync all records (use sparingly).

**Implementation:**

```python
def full_refresh():
    # Fetch all records (paginated)
    page = 1
    while True:
        response = api.get(f"/people?page={page}")

        if not response:
            break

        for record in response:
            sync_to_external_system(record)

        page += 1
```

### Sync Best Practices

1. **Use Incremental:** Most efficient for regular syncs
2. **Track Timestamps:** Store last sync time
3. **Handle Conflicts:** Define conflict resolution rules
4. **Batch Operations:** Process in batches to avoid timeouts
5. **Error Handling:** Retry failed syncs
6. **Rate Limiting:** Respect API limits (3 req/sec)
7. **Idempotency:** Make syncs repeatable safely
8. **Logging:** Track all sync operations
9. **Validation:** Verify data before syncing

### Conflict Resolution

When same record modified in both systems:

**Last Write Wins:**
```python
if record.modified_date > external.modified_date:
    use_copper_version()
else:
    use_external_version()
```

**Manual Resolution:**
```python
if conflict_detected():
    flag_for_manual_review()
```

**Field-Level Merge:**
```python
merged = {
    "name": external.name if external.name else copper.name,
    "email": copper.email,  # Always use Copper email
    "phone": external.phone if external.phone_updated else copper.phone
}
```

---

## 10. Step-by-Step Examples

### Example 1: Complete Sales Cycle

**Scenario:** Convert inbound lead to closed opportunity

```bash
# Step 1: Create lead from website form
POST /leads
{
  "name": "Sarah Johnson",
  "email": {"email": "sarah@bigcorp.com", "category": "work"},
  "company_name": "BigCorp Inc",
  "title": "Director of IT",
  "details": "Interested in enterprise plan"
}
# Returns: lead_id = 1001

# Step 2: Log initial contact
POST /activities
{
  "parent": {"id": 1001, "type": "lead"},
  "type": {"category": "user", "name": "Email"},
  "details": "Sent welcome email with product overview"
}

# Step 3: Qualify lead
PUT /leads/1001
{
  "status": "Qualified",
  "tags": ["qualified", "enterprise"]
}

# Step 4: Create company
POST /companies
{
  "name": "BigCorp Inc",
  "emails": [{"email": "info@bigcorp.com", "category": "work"}]
}
# Returns: company_id = 2001

# Step 5: Convert lead to person
POST /people
{
  "name": "Sarah Johnson",
  "email": {"email": "sarah@bigcorp.com", "category": "work"},
  "company_id": 2001,
  "title": "Director of IT"
}
# Returns: person_id = 3001

# Step 6: Create opportunity
POST /opportunities
{
  "name": "BigCorp - Enterprise Plan",
  "primary_company_id": 2001,
  "primary_contact_id": 3001,
  "monetary_value": 100000,
  "status": "Open",
  "pipeline_id": 1,
  "stage_id": 1
}
# Returns: opportunity_id = 4001

# Step 7: Schedule demo
POST /tasks
{
  "name": "Product Demo",
  "related_resource": {"id": 4001, "type": "opportunity"},
  "due_date": "2025-01-20"
}

# Step 8: Move through stages
PUT /opportunities/4001
{"stage_id": 2}  # Demo completed
PUT /opportunities/4001
{"stage_id": 3}  # Proposal sent
PUT /opportunities/4001
{"stage_id": 4}  # Negotiation

# Step 9: Close won
PUT /opportunities/4001
{
  "status": "Won",
  "stage_id": 5
}
```

### Example 2: Bulk Import with Company Linking

**Scenario:** Import 100 contacts across 20 companies

```bash
# Step 1: Import companies first
python bulk_import.py companies companies.csv --mode upsert

# Step 2: Prepare people CSV with company names
# people.csv:
# name,email,company_name,title
# John Smith,john@acme.com,Acme Corp,VP Sales
# ...

# Step 3: Import people (will link to companies)
python bulk_import.py people people.csv --mode upsert

# Step 4: Review results
# Summary shows:
# - 100 people imported
# - 20 companies linked
# - 5 duplicates updated
# - 2 failures (missing company)
```

### Example 3: Managing Opportunity Pipeline

**Scenario:** Track deals through sales pipeline

```bash
# Get all opportunities in discovery stage
POST /opportunities/search
{
  "stage_id": 1
}

# Move deals forward
for opportunity in opportunities:
    if opportunity.demo_completed:
        PUT /opportunities/{opportunity.id}
        {"stage_id": 2}

# Get opportunities closing this quarter
POST /opportunities/search
{
  "close_date": {
    "after": "2025-01-01",
    "before": "2025-03-31"
  },
  "status": "Open"
}

# Calculate pipeline value
total_value = sum(opp.monetary_value for opp in opportunities)
```

### Example 4: Activity Tracking

**Scenario:** Log all customer interactions

```bash
# Log call
POST /activities
{
  "parent": {"id": 4001, "type": "opportunity"},
  "type": {"category": "user", "name": "Call"},
  "details": "Discussed pricing options",
  "activity_date": 1640995200
}

# Log email
POST /activities
{
  "parent": {"id": 3001, "type": "person"},
  "type": {"category": "user", "name": "Email"},
  "details": "Sent proposal document"
}

# Log meeting
POST /activities
{
  "parent": {"id": 2001, "type": "company"},
  "type": {"category": "user", "name": "Meeting"},
  "details": "On-site visit - met with decision makers"
}

# Get all activities for opportunity
GET /opportunities/4001/activities
```

### Example 5: Custom Field Management

**Scenario:** Track deal-specific information

```bash
# Step 1: Get custom field definitions
GET /custom_field_definitions

# Returns fields like:
# - ID 100: "Contract Length" (Dropdown)
# - ID 101: "Implementation Complexity" (Dropdown)
# - ID 102: "Support Level" (Text)

# Step 2: Set custom fields on opportunity
PUT /opportunities/4001
{
  "custom_fields": [
    {"custom_field_definition_id": 100, "value": 2},  # 2 years
    {"custom_field_definition_id": 101, "value": 1},  # Low complexity
    {"custom_field_definition_id": 102, "value": "Premium"}
  ]
}

# Step 3: Query by custom field
POST /opportunities/search
{
  "custom_fields": [
    {"custom_field_definition_id": 102, "value": "Premium"}
  ]
}
```

### Example 6: Data Sync Implementation

**Scenario:** Sync Copper with external CRM

```python
import requests
from datetime import datetime, timedelta

def sync_copper_to_external():
    """Incremental sync from Copper to external system"""

    # Get last sync timestamp
    last_sync = get_config("last_sync_time")

    # Fetch modified records
    copper_api = CopperAPI(api_key)
    modified_people = copper_api.post("/people/search", {
        "modified_date": {
            "after": last_sync
        }
    })

    # Sync each record
    external_api = ExternalAPI(api_key)

    for person in modified_people:
        try:
            # UPSERT to external system
            external_api.upsert_contact({
                "email": person["email"]["email"],
                "first_name": person["name"].split()[0],
                "last_name": person["name"].split()[-1],
                "company": person.get("company_name", ""),
                "title": person.get("title", "")
            })
        except Exception as e:
            log_error(f"Failed to sync person {person['id']}: {e}")

    # Update last sync time
    save_config("last_sync_time", datetime.now().timestamp())

# Run sync every hour
sync_copper_to_external()
```

---

## Summary

This workflows guide covers the most common Copper CRM operations:

1. **Lead Lifecycle** - Capturing, qualifying, and converting leads
2. **Person/Company Management** - Creating and linking contacts
3. **Opportunity Tracking** - Managing deals through pipeline
4. **Activity Logging** - Recording all customer interactions
5. **Lead Conversion** - Detailed conversion process
6. **Custom Fields** - Working with custom data
7. **Related Records** - Linking entities together
8. **Bulk Import** - Efficiently importing large datasets
9. **Data Sync** - Strategies for system integration
10. **Examples** - Complete workflow implementations

### Key Takeaways

- **Always create companies first** before people
- **Use UPSERT mode** for imports to prevent duplicates
- **Log all activities** to maintain complete history
- **Leverage custom fields** for industry-specific data
- **Implement incremental sync** for efficient data integration
- **Follow the pipeline** from lead → person → opportunity
- **Use batch operations** for large-scale changes
- **Validate data** before bulk operations

### CLI Quick Reference

```bash
# Interactive mode
python copper_cli.py interactive

# Create record
python copper_cli.py create leads

# Search records
python copper_cli.py search people --query "Smith" --limit 10

# Update record
python copper_cli.py update opportunities 12345

# Bulk import
python copper_cli.py bulk-import leads.csv --entity leads --upsert

# Bulk import script
python bulk_import.py leads leads.csv --mode upsert
```

### Next Steps

- Review [API Reference Documentation](../README.md)
- Explore [Templates](../templates/) for data structures
- Try [Example Scripts](../scripts/) for automation
- Configure [Custom Fields](#6-working-with-custom-fields) for your needs
- Set up [Data Sync](#9-data-sync-strategies) workflows
