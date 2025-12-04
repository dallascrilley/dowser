# PandaDoc Sales Manager - Helper Scripts

Comprehensive collection of Python scripts for automating PandaDoc document workflows including creation, sending, tracking, and webhook management.

## Quick Start

### Prerequisites

- Python 3.8+
- `requests` library: `pip install requests`
- PandaDoc API key

### Setup

1. Set environment variables:
```bash
export PANDADOC_API_KEY="your_api_key_here"
export PANDADOC_ENV="sandbox"  # or "production"
```

2. Make scripts executable:
```bash
chmod +x *.py
```

3. Verify installation:
```bash
python create_proposal.py --help
```

---

## Scripts Overview

### 1. create_proposal.py

Create sales proposals from templates with customer data.

**Purpose:** Template-based document creation with field mapping and status polling.

**Key Features:**
- Customer data validation
- Field mapping from template configuration
- Automatic status polling until document is ready
- Rate limit handling (6 second delays)
- Progress display

**Usage:**

```bash
# From command-line arguments
python create_proposal.py \
  --template "Sales Proposal" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com" \
  --amount "50000" \
  --effective-date "2024-01-15"

# From JSON file
python create_proposal.py \
  --template "Sales Proposal" \
  --data customer.json

# With template UUID
python create_proposal.py \
  --template-uuid "abc123-def456" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com"

# Verbose output
python create_proposal.py \
  --template "Sales Proposal" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com" \
  -v
```

**Arguments:**
- `--template` (required): Template name or UUID
- `--template-uuid`: Explicit template UUID
- `--customer-name`: Customer/company name
- `--customer-email`: Customer email address
- `--amount`: Proposal amount
- `--effective-date`: Effective date (YYYY-MM-DD)
- `--discount-percent`: Discount percentage
- `--data`: Load customer data from JSON file
- `--opportunity-id`: Opportunity ID for tracking
- `--sales-rep-name`: Sales representative name
- `--config`: Path to template mappings file
- `-v, --verbose`: Enable verbose logging

**Exit Codes:**
- `0`: Success
- `1`: Error

---

### 2. send_document.py

Send documents to recipients with customizable messages.

**Purpose:** Document delivery with status verification and recipient validation.

**Key Features:**
- Document status verification before sending
- Custom subject and message support
- Silent mode (no email notifications)
- Recipient list display
- Email validation

**Usage:**

```bash
# Send with default message
python send_document.py --document-id "abc123"

# Send with custom subject and message
python send_document.py \
  --document-id "abc123" \
  --subject "Proposal for Review" \
  --message "Please review and sign by Friday"

# Send silently (no email)
python send_document.py \
  --document-id "abc123" \
  --silent

# Verbose output
python send_document.py \
  --document-id "abc123" \
  -v
```

**Arguments:**
- `--document-id` (required): Document ID to send
- `--subject`: Email subject line
- `--message`: Email message body
- `--silent`: Don't send email notifications
- `-v, --verbose`: Enable verbose logging

**Exit Codes:**
- `0`: Success
- `1`: Error

---

### 3. check_document_status.py

Monitor document status with watch mode and export options.

**Purpose:** Real-time document status tracking with multiple export formats.

**Key Features:**
- Single and multiple document monitoring
- Watch mode with configurable intervals
- JSON/CSV/Table export formats
- Status filtering
- Recipient status display
- ANSI color support in watch mode

**Usage:**

```bash
# Check single document
python check_document_status.py --document-id "abc123"

# Watch document (continuous monitoring)
python check_document_status.py \
  --document-id "abc123" \
  --watch \
  --interval 30

# Check multiple documents
python check_document_status.py \
  --document-ids "abc123,def456,ghi789"

# Export to JSON
python check_document_status.py \
  --document-id "abc123" \
  --format json \
  --output status.json

# Export to CSV
python check_document_status.py \
  --document-ids "abc123,def456" \
  --format csv \
  --output status.csv

# Filter by status
python check_document_status.py \
  --document-ids "abc123,def456" \
  --filter-status "document.completed"
```

**Arguments:**
- `--document-id`: Single document ID
- `--document-ids`: Multiple document IDs (comma-separated)
- `--watch`: Watch continuously
- `--interval`: Watch interval in seconds (default: 30)
- `--format`: Output format (table/json/csv)
- `--output`: Output file path
- `--filter-status`: Filter by status
- `-v, --verbose`: Enable verbose logging

**Exit Codes:**
- `0`: Success
- `1`: Error

---

### 4. bulk_create_documents.py

Batch create documents from template with rate limiting and error recovery.

**Purpose:** High-volume document creation with progress tracking and retry capability.

**Key Features:**
- CSV/JSON customer data import
- Batch processing with configurable size
- Rate limiting with exponential backoff
- Progress saving and resume capability
- Error tracking and logging
- Completion report generation

**Usage:**

```bash
# Create from CSV file
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.csv \
  --batch-size 50

# Create from JSON with custom delay
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.json \
  --delay 6

# Resume from last position
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.csv \
  --resume

# Generate report to file
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.csv \
  --output report.txt \
  -v
```

**Arguments:**
- `--template` (required): Template name or UUID
- `--template-uuid`: Explicit template UUID
- `--customers` (required): Customer data file (CSV or JSON)
- `--batch-size`: Batch size (default: 50)
- `--delay`: Delay between requests in seconds (default: 6)
- `--resume`: Resume from saved progress
- `--output`: Output report file path
- `-v, --verbose`: Enable verbose logging

**Input File Formats:**

CSV:
```csv
customer_name,customer_email,amount,effective_date
Acme Corp,client@acme.com,50000,2024-01-15
TechCorp,contact@techcorp.com,75000,2024-01-20
```

JSON:
```json
{
  "customers": [
    {
      "customer_name": "Acme Corp",
      "customer_email": "client@acme.com",
      "amount": "50000",
      "effective_date": "2024-01-15"
    }
  ]
}
```

**Exit Codes:**
- `0`: All documents created successfully
- `1`: Some documents failed

---

### 5. download_completed.py

Download completed documents within a date range.

**Purpose:** Batch download of completed/approved documents with flexible naming.

**Key Features:**
- Date range filtering
- Status filtering
- Customizable filename patterns
- Automatic retry on failure
- Skip existing files option
- Download summary report

**Usage:**

```bash
# Download from date range
python download_completed.py \
  --from "2024-01-01" \
  --to "2024-01-31" \
  --output ./downloads

# With custom naming pattern
python download_completed.py \
  --from "2024-01-01" \
  --to "2024-12-31" \
  --output ./downloads \
  --pattern "{date}_{customer}_{id}.pdf"

# Download only completed (not approved)
python download_completed.py \
  --from "2024-01-01" \
  --to "2024-01-31" \
  --status "document.completed" \
  --output ./downloads

# Skip already downloaded files
python download_completed.py \
  --from "2024-01-01" \
  --to "2024-01-31" \
  --output ./downloads \
  --skip-existing
```

**Arguments:**
- `--from` (required): From date (YYYY-MM-DD)
- `--to` (required): To date (YYYY-MM-DD)
- `--output` (required): Output directory
- `--status`: Status filter (default: document.completed)
- `--pattern`: Filename pattern
- `--skip-existing`: Skip already downloaded files
- `-v, --verbose`: Enable verbose logging

**Filename Pattern Variables:**
- `{date}` - Document creation date
- `{customer}` - Customer/company name
- `{id}` - Document ID (first 8 chars)
- `{name}` - Document name
- `{index}` - Sequential index (0001, 0002, ...)
- `{status}` - Document status

**Exit Codes:**
- `0`: All documents downloaded successfully
- `1`: Some downloads failed

---

### 6. template_manager.py

List, inspect, and manage templates.

**Purpose:** Template discovery and field mapping reference.

**Key Features:**
- List all available templates
- Search templates by name
- Display template details
- Export field definitions
- Show recipient roles

**Usage:**

```bash
# List all templates
python template_manager.py list

# Search templates
python template_manager.py list --search "proposal"

# Show template details
python template_manager.py show --template "Sales Proposal"

# Show template fields
python template_manager.py fields --template "Sales Proposal"

# Search for template
python template_manager.py search --query "proposal"

# Export template configuration
python template_manager.py export \
  --template "Sales Proposal" \
  --output template.json
```

**Commands:**

```bash
# list - List all templates
python template_manager.py list [--search QUERY]

# show - Show template details
python template_manager.py show --template TEMPLATE

# fields - Show template fields
python template_manager.py fields --template TEMPLATE

# search - Search templates
python template_manager.py search --query QUERY

# export - Export template JSON
python template_manager.py export \
  --template TEMPLATE \
  --output FILE
```

**Arguments:**
- `--search`: Filter templates by name (with list command)
- `--template`: Template name or UUID
- `--query`: Search query
- `--output`: Output file path
- `-v, --verbose`: Enable verbose logging

**Exit Codes:**
- `0`: Success
- `1`: Error

---

### 7. webhook_tester.py

Test webhook endpoints and verify signatures.

**Purpose:** Webhook endpoint testing and local development server.

**Key Features:**
- Send test events to webhook endpoints
- Generate webhook signatures
- Verify signature validity
- Local test server for receiving webhooks
- Sample payload generation
- Signature validation

**Usage:**

```bash
# Send test event
python webhook_tester.py test \
  --url "https://your-server.com/webhooks/pandadoc" \
  --event "document_completed"

# Test with signature
python webhook_tester.py test \
  --url "https://your-server.com/webhooks/pandadoc" \
  --event "document_completed" \
  --verify-signature \
  --shared-key "your_shared_key"

# Send custom payload
python webhook_tester.py test \
  --url "https://your-server.com/webhooks/pandadoc" \
  --payload custom_payload.json

# Run local test server
python webhook_tester.py serve --port 8000

# Generate signature
python webhook_tester.py sign \
  --payload payload.json \
  --shared-key "your_shared_key"

# Verify signature
python webhook_tester.py verify \
  --payload payload.json \
  --signature "abc123..." \
  --shared-key "your_shared_key"
```

**Commands:**

```bash
# test - Send test webhook
python webhook_tester.py test \
  --url URL \
  --event EVENT \
  [--payload FILE] \
  [--verify-signature] \
  [--shared-key KEY]

# serve - Run test server
python webhook_tester.py serve [--port PORT]

# sign - Generate signature
python webhook_tester.py sign \
  --payload FILE \
  --shared-key KEY

# verify - Verify signature
python webhook_tester.py verify \
  --payload FILE \
  --signature SIGNATURE \
  --shared-key KEY
```

**Available Events:**
- `document_completed` - Document signature complete
- `document_sent` - Document sent to recipients
- `document_viewed` - Recipient viewed document
- `document_state_changed` - Document status changed

**Arguments:**
- `--url`: Webhook URL (test command)
- `--event`: Event type (default: document_completed)
- `--payload`: Custom payload JSON file
- `--verify-signature`: Include signature in request
- `--shared-key`: Shared key for signature
- `--port`: Server port (default: 8000)
- `--signature`: Signature to verify
- `-v, --verbose`: Enable verbose logging

**Exit Codes:**
- `0`: Success
- `1`: Error

---

## Common Workflows

### Complete Proposal Workflow

```bash
# 1. Create proposal
python create_proposal.py \
  --template "Sales Proposal" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com" \
  --amount "50000" \
  --effective-date "2024-01-15"
# Output: Document ID: doc_abc123def456

# 2. Send document
python send_document.py \
  --document-id "doc_abc123def456" \
  --subject "Proposal for Review"

# 3. Monitor status
python check_document_status.py \
  --document-id "doc_abc123def456" \
  --watch \
  --interval 30

# 4. Download when complete
python download_completed.py \
  --from "2024-01-15" \
  --to "2024-01-31" \
  --output ./downloads
```

### Bulk Proposal Creation

```bash
# 1. Prepare customer data (CSV)
# customers.csv:
# customer_name,customer_email,amount,effective_date
# Acme Corp,client@acme.com,50000,2024-01-15
# TechCorp,contact@techcorp.com,75000,2024-01-20

# 2. Create all documents
python bulk_create_documents.py \
  --template "Sales Proposal" \
  --customers customers.csv \
  --batch-size 50

# 3. Check status
python check_document_status.py \
  --document-ids "doc1,doc2,doc3" \
  --format csv \
  --output status.csv

# 4. Download completed
python download_completed.py \
  --from "2024-01-15" \
  --to "2024-01-31" \
  --output ./completed_proposals
```

### Template Discovery

```bash
# 1. List all templates
python template_manager.py list

# 2. Find template details
python template_manager.py show --template "Sales Proposal"

# 3. View field requirements
python template_manager.py fields --template "Sales Proposal"

# 4. Export for reference
python template_manager.py export \
  --template "Sales Proposal" \
  --output proposal_template.json
```

### Webhook Testing

```bash
# 1. Start local test server
python webhook_tester.py serve --port 8000
# In another terminal:

# 2. Test webhook endpoint
python webhook_tester.py test \
  --url "http://localhost:8000/webhooks/test" \
  --event "document_completed"

# 3. Generate signatures for production
python webhook_tester.py sign \
  --payload event_payload.json \
  --shared-key "production_key"
```

---

## Error Handling

All scripts implement comprehensive error handling:

- **Authentication errors (401)**: Invalid or missing API key
- **Rate limiting (429)**: Automatic backoff with exponential delays
- **Document not found (404)**: Document ID doesn't exist or not ready
- **Invalid status (409)**: Document in wrong state for operation
- **Server errors (500+)**: Automatic retry with exponential backoff

Most scripts will display helpful error messages and exit with code `1`.

---

## Rate Limiting

PandaDoc API limits requests to 10 per minute in sandbox environment.

All scripts automatically:
- Implement 6-second delays between requests
- Detect 429 responses
- Apply exponential backoff
- Warn when rate limit is reached

No manual rate limit handling needed.

---

## Environment Variables

Required:
- `PANDADOC_API_KEY`: Your PandaDoc API key

Optional:
- `PANDADOC_ENV`: "sandbox" or "production"
- `PANDADOC_BASE_URL`: API base URL (default: https://api.pandadoc.com/public/v1)

---

## Configuration Files

Scripts support optional YAML/JSON configuration files:

```bash
# template_mappings.yml or template_mappings.json
python create_proposal.py \
  --template "Sales Proposal" \
  --customer-name "Acme Corp" \
  --customer-email "client@acme.com" \
  --config ~/.claude/skills/pandadoc-sales-manager/config/template_mappings.json
```

---

## Troubleshooting

### API Key Error
```
PANDADOC_API_KEY environment variable not set
```
Solution:
```bash
export PANDADOC_API_KEY="your_api_key_here"
```

### Document Not Ready
```
Document not found: doc_abc123
```
This usually means the document hasn't finished processing yet. The scripts automatically wait, but you can retry manually.

### Rate Limit Error
```
Rate limit reached. Waiting 60.5 seconds...
```
This is expected. The script automatically handles this. Longer delays when processing many documents.

### Connection Error
```
Failed to connect to webhook URL
```
Verify:
- URL is accessible
- HTTPS is correctly configured
- Firewall allows outbound connections

### Signature Verification Failed
```
Signature mismatch
```
Check:
- Shared key matches webhook configuration
- Payload hasn't been modified
- Timestamp is recent

---

## License

Part of PandaDoc Sales Manager skill for Claude Code.
