---
name: pandadoc-sales-manager
description: >-
  Automate PandaDoc document workflows for sales teams - create proposals from
  templates, send documents, track status, manage contacts.
when_to_use: >-
  Use when creating sales documents, automating proposal workflows, tracking
  document status, bulk document operations, integrating with CRM, working with
  pandadoc api, sales proposals, document automation, esignature, contract
  management, template management, or document tracking.
version: 1.0.0
category: integrations-and-saas
---

# PandaDoc Sales Manager

Streamline sales document workflows with PandaDoc API automation. Create proposals from templates, send documents to customers, track signing status, and manage bulk operations - all from the command line or automated scripts.

## Prerequisites

**IMPORTANT:** You need a PandaDoc account with API access (Enterprise plan for production).

### First-Time Setup

1. **Set your API key:**
  export PANDADOC_API_KEY="a1f67376274f328788df8bd7da0560b62191a358"
   ```

2. **Verify authentication:**
   ```bash
   python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py list
   ```

3. **Configure API settings:**
   ```bash
   # Copy the template config
   cp ~/.claude/skills/pandadoc-sales-manager/templates/api_config.yml ~/pandadoc_config.yml

   # Edit with your settings (optional - defaults work for most cases)
   # The config handles rate limits, timeouts, and retry logic
   ```

**Environment:**
- **Sandbox:** 10 requests/minute (for testing)
- **Production:** 500 requests/minute for creates, 100/min for downloads

## Quick Start

```bash
# Create a sales proposal from a template
python ~/.claude/skills/pandadoc-sales-manager/scripts/create_proposal.py \
  --template-id "abc123-template-id" \
  --customer-name "Acme Corp" \
  --customer-email "john@acme.com" \
  --fields '{"company_name": "Acme Corp", "proposal_amount": "50000"}'

# Check document status
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py doc_xyz789

# Send document to customer
python ~/.claude/skills/pandadoc-sales-manager/scripts/send_document.py doc_xyz789 \
  --subject "Your Sales Proposal" \
  --message "Please review and sign this proposal"

# Watch status in real-time
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py doc_xyz789 --watch
```

## Core Tasks

### Create Documents from Templates

```bash
# Basic proposal creation
python ~/.claude/skills/pandadoc-sales-manager/scripts/create_proposal.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customer-name "John Doe" \
  --customer-email "john@example.com"

# With custom field mapping
python ~/.claude/skills/pandadoc-sales-manager/scripts/create_proposal.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customer-name "Acme Corp" \
  --customer-email "jane@acme.com" \
  --fields '{"company_name": "Acme Corporation", "deal_value": "100000", "start_date": "2024-02-01"}' \
  --tokens '{"Sales.Rep": "Alice Smith", "Sales.Territory": "West Coast"}' \
  --config ~/pandadoc_config.yml

# From JSON customer data file
python ~/.claude/skills/pandadoc-sales-manager/scripts/create_proposal.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customer-data customer.json

# customer.json format:
# {
#   "name": "John Doe",
#   "email": "john@example.com",
#   "company": "Acme Corp",
#   "fields": {"proposal_amount": "50000"},
#   "tokens": {"Sales.Rep": "Alice"}
# }
```

**The script automatically:**
- Validates template exists
- Polls status until `document.draft` (CRITICAL - prevents 404 errors)
- Respects rate limits (6 second delays)
- Returns document ID for next steps

### Send Documents

```bash
# Send with custom message
python ~/.claude/skills/pandadoc-sales-manager/scripts/send_document.py doc_xyz789 \
  --subject "Q1 Sales Proposal for Review" \
  --message "Hi John, please review this proposal and let me know if you have questions."

# Send silently (no email notification - for testing)
python ~/.claude/skills/pandadoc-sales-manager/scripts/send_document.py doc_xyz789 --silent

# Send multiple documents
for doc_id in doc_1 doc_2 doc_3; do
  python ~/.claude/skills/pandadoc-sales-manager/scripts/send_document.py $doc_id
  sleep 6  # Rate limit compliance
done
```

### Track Document Status

```bash
# Check single document
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py doc_xyz789

# Check multiple documents
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py \
  doc_1 doc_2 doc_3

# Watch mode (real-time updates every 10 seconds)
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py doc_xyz789 \
  --watch --interval 10

# Export to JSON for processing
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py doc_xyz789 \
  --format json > status.json

# Export to CSV for reporting
python ~/.claude/skills/pandadoc-sales-manager/scripts/check_document_status.py \
  doc_1 doc_2 doc_3 --format csv > report.csv
```

**Status values:**
- `document.uploaded` - Just created, processing (wait for draft)
- `document.draft` - Ready to send
- `document.sent` - Sent to recipients
- `document.viewed` - Recipient viewed
- `document.completed` - All signatures collected
- `document.declined` - Recipient declined

### Manage Templates

```bash
# List all templates
python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py list

# Search by name
python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py search "Sales Proposal"

# Show detailed template info
python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py show YOUR_TEMPLATE_ID

# Show template fields and types
python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py fields YOUR_TEMPLATE_ID

# Export template schema to JSON
python ~/.claude/skills/pandadoc-sales-manager/scripts/template_manager.py export YOUR_TEMPLATE_ID \
  > template_schema.json
```

### Manage Product Catalog

The product catalog API allows you to retrieve and search catalog items for use in quotes and documents.

**Get Catalog Item Details:**
```bash
# Get a specific catalog item by UUID
curl -X GET "https://api.pandadoc.com/public/v2/product-catalog/items/{item_uuid}" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json"
```

**Search Catalog Items:**
```bash
# Search by query (searches title, SKU, description, category name, custom fields)
curl -X GET "https://api.pandadoc.com/public/v2/product-catalog/items/search?query=product_name" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json"

# Search with filters
curl -X GET "https://api.pandadoc.com/public/v2/product-catalog/items/search?type=product&category_id=123" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json"

# Search with ordering (by SKU, name, price, or modification date)
curl -X GET "https://api.pandadoc.com/public/v2/product-catalog/items/search?order_by=price&order=desc" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json"

# Exclude specific items from search
curl -X GET "https://api.pandadoc.com/public/v2/product-catalog/items/search?exclude_uuids=uuid1,uuid2" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json"
```

**Search Parameters:**
- `query` - Search in title, SKU, description, category name, custom fields name and value
- `type` - Filter by item type
- `billing_type` - Filter by billing type
- `category_id` - Filter by category ID
- `order_by` - Sort by: `sku`, `name`, `price`, or `modified_date`
- `order` - Sort direction: `asc` or `desc`
- `exclude_uuids` - Comma-separated list of UUIDs to exclude

**Use Cases:**
- Retrieve product details for quote generation
- Search products by name or SKU for document creation
- Filter products by category for organized proposals
- Get pricing information for sales calculations

**API Reference:**
- [Get Catalog Item](https://developers.pandadoc.com/reference/get-catalog-item)
- [Search Catalog Items](https://developers.pandadoc.com/reference/search-catalog-items)

### Bulk Operations

```bash
# Create 100 proposals from CSV
python ~/.claude/skills/pandadoc-sales-manager/scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.csv \
  --batch-size 50

# CSV format: name,email,company,proposal_amount
# John Doe,john@example.com,Acme Corp,50000
# Jane Smith,jane@company.com,Beta Inc,75000

# Resume interrupted batch
python ~/.claude/skills/pandadoc-sales-manager/scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.csv \
  --resume

# From JSON file
python ~/.claude/skills/pandadoc-sales-manager/scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.json
```

**The script automatically:**
- Respects rate limits with delays
- Saves progress to `.batch_progress.json`
- Tracks errors and successes
- Can resume from interruptions
- Generates completion report

### Download Completed Documents

```bash
# Download all completed documents from date range
python ~/.claude/skills/pandadoc-sales-manager/scripts/download_completed.py \
  --start-date 2024-01-01 \
  --end-date 2024-01-31 \
  --output-dir ~/documents/completed/

# Download with custom filename pattern
python ~/.claude/skills/pandadoc-sales-manager/scripts/download_completed.py \
  --start-date 2024-01-01 \
  --filename-pattern "{date}_{name}.pdf" \
  --output-dir ~/documents/

# Skip existing files
python ~/.claude/skills/pandadoc-sales-manager/scripts/download_completed.py \
  --start-date 2024-01-01 \
  --skip-existing \
  --output-dir ~/documents/
```

**Filename pattern variables:**
- `{name}` - Document name
- `{id}` - Document ID
- `{date}` - Completion date (YYYY-MM-DD)
- `{status}` - Document status

## API Patterns Reference

**Authentication:**
```python
headers = {
    "Authorization": f"API-Key {os.environ['PANDADOC_API_KEY']}",
    "Content-Type": "application/json"
}
```

**Rate Limiting:**
```python
# CRITICAL: Enforce 6+ second delays between requests
# Sandbox: 10 requests/minute
# Production: 500/min creates, 100/min downloads

import time
time.sleep(6)  # Wait between requests
```

**Status Polling Pattern:**
```python
# CRITICAL: Always poll for draft status before operations
max_retries = 30  # 60 seconds total
for attempt in range(max_retries):
    status = get_document_status(doc_id)
    if status == "document.draft":
        break
    elif status == "document.error":
        raise Exception("Document creation failed")
    time.sleep(2)
else:
    raise TimeoutError("Document not ready after 60 seconds")
```

**Catalog API Patterns:**
```python
import requests
import os

# Get catalog item by UUID
def get_catalog_item(item_uuid):
    url = f"https://api.pandadoc.com/public/v2/product-catalog/items/{item_uuid}"
    headers = {
        "Authorization": f"API-Key {os.environ['PANDADOC_API_KEY']}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Search catalog items
def search_catalog_items(query=None, item_type=None, category_id=None, 
                        order_by="name", order="asc", exclude_uuids=None):
    url = "https://api.pandadoc.com/public/v2/product-catalog/items/search"
    headers = {
        "Authorization": f"API-Key {os.environ['PANDADOC_API_KEY']}",
        "Content-Type": "application/json"
    }
    params = {
        "order_by": order_by,
        "order": order
    }
    if query:
        params["query"] = query
    if item_type:
        params["type"] = item_type
    if category_id:
        params["category_id"] = category_id
    if exclude_uuids:
        params["exclude_uuids"] = ",".join(exclude_uuids) if isinstance(exclude_uuids, list) else exclude_uuids
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Example usage
items = search_catalog_items(query="laptop", order_by="price", order="desc")
item_details = get_catalog_item(items["results"][0]["uuid"])
```

**See also:** [references/endpoints-reference.md](references/endpoints-reference.md) for complete API documentation.

## Configuration Files

### API Configuration

**Location in the skill:** `templates/api_config.yml`

```yaml
api:
  base_url: https://api.pandadoc.com/public/v1
  timeout: 30
  rate_limit:
    requests_per_minute: 10  # Sandbox limit
    delay_seconds: 6

async_processing:
  max_wait_seconds: 60
  poll_interval_seconds: 2
```

**Copy and customize:**
```bash
cp ~/.claude/skills/pandadoc-sales-manager/templates/api_config.yml ~/pandadoc_config.yml
```

### Template Mappings

**Location:** `templates/template_mappings.yml`

Maps your business fields to PandaDoc template fields:

```yaml
templates:
  sales_proposal:
    template_id: "your-template-id"
    fields:
      company_name: "Company Name"
      proposal_amount: "Proposal Amount"
      start_date: "Start Date"
    tokens:
      sales_rep: "Sales.Rep"
      territory: "Sales.Territory"
```

**Usage:**
```bash
python scripts/create_proposal.py \
  --config ~/pandadoc_config.yml \
  --template-mapping sales_proposal \
  --customer-data customer.json
```

### Field Validation

**Location:** `templates/field_validation.yml`

Defines validation rules for fields:

```yaml
global_rules:
  required:
    - customer_email
    - customer_name

  validations:
    customer_email:
      type: email
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"

    proposal_amount:
      type: number
      min: 0
      max: 10000000
```

**See also:**
- [templates/webhook_config.yml](templates/webhook_config.yml) - Webhook subscriptions
- [templates/batch_config.yml](templates/batch_config.yml) - Batch processing settings

## Proven Patterns

### Pattern: Complete Proposal Workflow

**⚠️ MANDATORY:** Always follow this workflow for document creation:

1. **Create document from template** (script polls until ready)
2. **Wait for `document.draft` status** (automatic in scripts)
3. **Send document** (only after draft status confirmed)
4. **Track status** (monitor for completion)

```bash
# Step 1: Create (script handles status polling automatically)
DOC_ID=$(python scripts/create_proposal.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customer-name "Acme Corp" \
  --customer-email "john@acme.com" \
  --fields '{"proposal_amount": "50000"}' | grep -o 'doc_[a-zA-Z0-9]*')

# Step 2: Status is already draft (script waited for it)

# Step 3: Send document
python scripts/send_document.py $DOC_ID \
  --subject "Sales Proposal for Review" \
  --message "Please review and sign"

# Step 4: Track status
python scripts/check_document_status.py $DOC_ID --watch
```

**Why this prevents failures:**
- Documents are NOT ready immediately after creation (async processing)
- Attempting to send before `document.draft` = 404 error
- Status polling is built into all scripts to prevent this
- Rate limiting prevents 429 errors

### Pattern: Bulk Document Creation with Error Recovery

```bash
# Create batch with progress tracking
python scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.csv \
  --batch-size 50 \
  --verbose

# If interrupted, resume from saved progress
python scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.csv \
  --resume

# Check progress file
cat .batch_progress.json
```

**Features:**
- Automatic progress saving after each document
- Resume from interruption point
- Error tracking with details
- Rate limit compliance
- Final completion report

### Pattern: CRM Integration

```bash
# 1. Export opportunities from CRM
# 2. Transform to PandaDoc format
# 3. Bulk create proposals

# Example: Salesforce export → PandaDoc
cat salesforce_opportunities.json | \
  jq '[.[] | {
    name: .ContactName,
    email: .Email,
    company: .AccountName,
    proposal_amount: .Amount
  }]' > pandadoc_customers.json

# Create proposals
python scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers pandadoc_customers.json

# Monitor completion
python scripts/check_document_status.py $(cat .batch_progress.json | jq -r '.successes[].document_id') \
  --format csv > status_report.csv
```

**See also:** [references/workflows.md](references/workflows.md) for complete workflow patterns.

## Troubleshooting

**Quick fixes for common issues:**

| Issue | Solution |
|-------|----------|
| **401 Unauthorized** | Check `PANDADOC_API_KEY` environment variable. Verify key is active in PandaDoc settings. |
| **404 Document Not Found** | Wait for `document.draft` status before operations. Use scripts that auto-poll. |
| **429 Rate Limit** | Sandbox: 10 req/min. Add 6+ second delays. Production: 500/min creates. |
| **Document Stuck in "uploaded"** | Normal - wait 2-5 seconds. Scripts poll automatically. Max wait: 60 seconds. |
| **Fields Not Pre-filled** | Check field names match template exactly. Signature fields cannot be pre-filled. |
| **Invalid Email Format** | Must contain @. Scripts validate automatically. |
| **Template Not Found** | Verify template ID. Use `template_manager.py list` to see available templates. |
| **Empty Recipients** | At least one recipient required. Check email format. |
| **Webhook Not Firing** | Verify URL is HTTPS. Check shared key signature. Test with `webhook_tester.py`. |
| **CSV Import Fails** | Check headers: name,email,company. No spaces in column names. |

**For detailed solutions:** [references/troubleshooting.md](references/troubleshooting.md)

**Diagnostic commands:**
```bash
# Test authentication
python scripts/template_manager.py list

# Verify template exists
python scripts/template_manager.py show YOUR_TEMPLATE_ID

# Check field names
python scripts/template_manager.py fields YOUR_TEMPLATE_ID

# Test webhook
python scripts/webhook_tester.py test https://your-webhook-url.com/webhook
```

## Helper Scripts

**All scripts located in:** `~/.claude/skills/pandadoc-sales-manager/scripts/`

| Script | Purpose | Key Features |
|--------|---------|--------------|
| **create_proposal.py** | Create documents from templates | Status polling, field validation, rate limiting, JSON/YAML support |
| **send_document.py** | Send documents to recipients | Status verification, custom messages, silent mode, batch support |
| **check_document_status.py** | Monitor document status | Watch mode, export (JSON/CSV), multi-document, recipient status |
| **bulk_create_documents.py** | Batch create documents | CSV/JSON import, progress tracking, resume capability, error recovery |
| **download_completed.py** | Download completed documents | Date range filtering, custom filenames, skip existing, batch download |
| **template_manager.py** | Manage templates | List, search, inspect, field mapping, schema export |
| **webhook_tester.py** | Test webhook endpoints | Local server, signature validation, event simulation, payload testing |

**Usage examples:**
```bash
# See detailed help for any script
python scripts/create_proposal.py --help
python scripts/send_document.py --help

# Enable verbose logging
python scripts/create_proposal.py --verbose ...

# All scripts support:
# - Environment variable: PANDADOC_API_KEY
# - Config file: --config path/to/config.yml
# - Verbose output: --verbose or -v
```

**See also:** [scripts/README.md](scripts/README.md) for comprehensive script documentation.

## Workflow Requirements

**⚠️ MANDATORY: Always follow this workflow when creating and sending documents:**

1. **Create document** using `create_proposal.py`
   - Script automatically polls for `document.draft` status
   - Waits up to 60 seconds (2-second intervals)
   - Fails if timeout or error status

2. **Verify status is "document.draft"** before sending
   - Built into all helper scripts
   - Manual check: `check_document_status.py DOC_ID`

3. **Send document** using `send_document.py`
   - Script verifies draft status first
   - Only sends if ready

4. **Track completion** using `check_document_status.py`
   - Watch mode for real-time updates
   - Export for reporting

**Why this prevents failures:**
- **Async Processing:** Documents are NOT ready immediately after creation
- **Race Condition:** Attempting operations before `document.draft` = 404 error
- **Rate Limits:** Proper delays prevent 429 errors
- **State Validation:** Scripts enforce correct status transitions

**Manual verification (if not using scripts):**
```bash
# After creating document, ALWAYS poll status
DOC_ID="doc_xyz789"
while true; do
  STATUS=$(curl -s "https://api.pandadoc.com/public/v1/documents/$DOC_ID" \
    -H "Authorization: API-Key $PANDADOC_API_KEY" | jq -r '.status')

  echo "Status: $STATUS"

  if [ "$STATUS" = "document.draft" ]; then
    echo "Ready to send!"
    break
  elif [ "$STATUS" = "document.error" ]; then
    echo "Error creating document"
    exit 1
  fi

  sleep 2
done
```

---

## Common Workflows

### Workflow 1: Send Proposal to Single Customer

```bash
# 1. Find your template
python scripts/template_manager.py list | grep "Sales Proposal"
# Output: abc123... | Sales Proposal | ...

# 2. Create document with customer data
python scripts/create_proposal.py \
  --template-id "abc123..." \
  --customer-name "John Doe" \
  --customer-email "john@acme.com" \
  --fields '{"company_name": "Acme Corp", "proposal_amount": "50000"}'
# Output: Created document: doc_xyz789 (Status: document.draft)

# 3. Send to customer
python scripts/send_document.py doc_xyz789 \
  --subject "Sales Proposal for Acme Corp" \
  --message "Hi John, please review and sign this proposal."
# Output: Document sent successfully!

# 4. Track status
python scripts/check_document_status.py doc_xyz789 --watch
# Real-time updates until completed
```

### Workflow 2: Bulk Proposal Campaign

```bash
# 1. Export leads from CRM to CSV
# Format: name,email,company,proposal_amount
cat > customers.csv <<EOF
name,email,company,proposal_amount
John Doe,john@acme.com,Acme Corp,50000
Jane Smith,jane@beta.com,Beta Inc,75000
Bob Johnson,bob@gamma.com,Gamma LLC,100000
EOF

# 2. Bulk create proposals
python scripts/bulk_create_documents.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customers customers.csv \
  --batch-size 50 \
  --verbose

# Progress is automatically saved to .batch_progress.json
# Can interrupt and resume at any time

# 3. Check progress
cat .batch_progress.json | jq '{
  total: .total_documents,
  completed: (.successes | length),
  failed: (.errors | length)
}'

# 4. Send all created documents
cat .batch_progress.json | jq -r '.successes[].document_id' | while read doc_id; do
  python scripts/send_document.py $doc_id --silent
  sleep 6  # Rate limit compliance
done

# 5. Monitor completion
python scripts/check_document_status.py \
  $(cat .batch_progress.json | jq -r '.successes[].document_id') \
  --format csv > completion_report.csv
```

### Workflow 3: Download All Completed Q1 Documents

```bash
# Download all documents completed in Q1 2024
python scripts/download_completed.py \
  --start-date 2024-01-01 \
  --end-date 2024-03-31 \
  --output-dir ~/Documents/PandaDoc/Q1_2024/ \
  --filename-pattern "{date}_{name}.pdf" \
  --skip-existing

# Output:
# Downloaded: 2024-01-15_Proposal_Acme_Corp.pdf
# Downloaded: 2024-01-20_Agreement_Beta_Inc.pdf
# Skipped (exists): 2024-02-01_Contract_Gamma_LLC.pdf
# ...
# Total: 45 downloaded, 3 skipped, 0 errors
```

### Workflow 4: Webhook Integration for Real-Time Updates

```bash
# 1. Test your webhook endpoint
python scripts/webhook_tester.py test https://your-app.com/webhook

# 2. Create webhook subscription using config
# Edit templates/webhook_config.yml with your URL

# 3. Subscribe to events
curl -X POST "https://api.pandadoc.com/public/v1/webhook-subscriptions" \
  -H "Authorization: API-Key $PANDADOC_API_KEY" \
  -H "Content-Type: application/json" \
  -d @templates/webhook_config.yml

# 4. Verify webhook receives events
python scripts/webhook_tester.py server --port 8000
# Keep running to receive webhook events locally for testing
```

### Workflow 5: Template Field Mapping and Testing

```bash
# 1. Inspect template fields
python scripts/template_manager.py fields YOUR_TEMPLATE_ID

# Output shows all fields:
# company_name (Text) - REQUIRED
# proposal_amount (Text) - REQUIRED
# start_date (Date) - OPTIONAL
# signature (Signature) - REQUIRED (cannot pre-fill)

# 2. Export full template schema
python scripts/template_manager.py export YOUR_TEMPLATE_ID > schema.json

# 3. Test with sample data
python scripts/create_proposal.py \
  --template-id "YOUR_TEMPLATE_ID" \
  --customer-name "Test Customer" \
  --customer-email "test@example.com" \
  --fields '{"company_name": "Test Corp", "proposal_amount": "1000", "start_date": "2024-02-01"}'

# 4. Verify in watch mode
python scripts/check_document_status.py DOC_ID --watch

# 5. If successful, save mapping to config
# Edit templates/template_mappings.yml
```

## Tips

**API Efficiency:**
- Use `bulk_create_documents.py` for creating multiple documents - handles rate limiting automatically
- Enable verbose mode (`--verbose`) for debugging to see API requests/responses
- Use watch mode for status tracking instead of manual polling
- Cache template IDs and field mappings in `template_mappings.yml`

**Error Prevention:**
- Always use helper scripts - they implement required guardrails (status polling, rate limits)
- Never send documents immediately after creation - scripts handle the mandatory wait
- Validate customer data before bulk operations - saves API calls on errors
- Test with small batches first (10-20 documents) before large campaigns

**Rate Limiting:**
- Sandbox: 10 requests/minute = 6 second minimum delays between requests
- Production: 500/min creates = 0.12 second delays (scripts default to 1 second)
- Scripts automatically handle rate limiting with `RateLimiter` class
- If hitting limits, increase batch delays in `batch_config.yml`

**Field Mapping:**
- Use `template_manager.py fields` to discover exact field names
- Field names are case-sensitive and must match template exactly
- Use `fields` parameter for form fields (no square brackets)
- Use `tokens` parameter for template variables (have square brackets like `[Sales.Rep]`)
- Signature fields cannot be pre-filled - recipients must sign

**Status Tracking:**
- Use watch mode for real-time updates: `--watch --interval 10`
- Export to CSV for spreadsheet analysis: `--format csv`
- Export to JSON for programmatic processing: `--format json`
- Status transitions: uploaded → draft → sent → viewed → completed

**Webhook Integration:**
- Use webhooks for real-time status updates instead of polling
- Test locally first with `webhook_tester.py server`
- Always verify HMAC signatures for security
- Have polling fallback for missed webhook events

**See also:**
- [references/workflows.md](references/workflows.md) - Complete workflow patterns with code
- [references/field-mapping-guide.md](references/field-mapping-guide.md) - Field vs token mapping
- [references/troubleshooting.md](references/troubleshooting.md) - Diagnostic commands and solutions
- [references/webhook-integration-guide.md](references/webhook-integration-guide.md) - Webhook setup and testing
- [scripts/README.md](scripts/README.md) - Complete script documentation
