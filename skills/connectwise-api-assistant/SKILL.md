---
name: connectwise-api-assistant
description: >-
  Lookup ConnectWise records and troubleshoot ConnectWise CLI issues.
  Comprehensive support for ConnectWise Manage API operations, search,
  filtering, and error resolution.
when_to_use: >-
  Use when working with ConnectWise Manage API, cw, connectwise-cli, searching
  for agreements/companies/invoices/catalog items/contacts, debugging connection
  errors (401, 403, 404, 429, timeout), building filter queries, friendly search
  syntax, agreement additions, write operations, or ConnectWise CLI commands.
version: 1.0.0
license: MIT
category: integrations-and-saas
---

# ConnectWise Lookup

**Status**: Beta
**Last Updated**: 2025-11-10
**Dependencies**: connectwise-cli (local installation)
**CLI Commands**: `connectwise-cli` or `cw`

---

## Quick Start

### 1. Verify CLI is Installed

Check if ConnectWise CLI is available:

```bash
cw --version
```

If not found, activate the virtual environment:
```bash
cd /Users/dallascrilley/Code/personal-projects/connectwise-cli
source .venv/bin/activate
```

**Why this matters:**
- CLI must be in PATH to execute queries
- Virtual environment contains all dependencies

### 2. Test Connection

Before any lookup, verify API connection:

```bash
cw config test
```

**CRITICAL:**
- If this fails with 401/403/404, credentials need fixing (see Error Solutions below)
- Check `cw config show` to view current configuration (credentials masked)

### 3. Basic Record Lookup

```bash
# Get specific record by ID
cw agreements get <ID>
cw companies get <ID>
cw invoices get <ID>
cw catalog get <ID>

# List records with filters
cw agreements list --conditions "agreementStatus='Active'"
cw companies list --conditions "name contains 'Tech'"
```

---

## Critical Rules

### Always Do

✅ **Test connection first** - Run `cw config test` before complex queries
✅ **Use filters on server-side** - `--conditions` or `--search` instead of piping to jq
✅ **Try friendly search first** - Use `--search "active and company 250"` for common queries
✅ **Check date format** - Dates MUST use `[YYYY-MM-DD]` with brackets (in `--conditions`)
✅ **Quote conditions** - Always quote filter strings: `--conditions "field=value"`
✅ **Verify IDs exist** - List records first to get valid IDs
✅ **Use --limit for large datasets** - Prevent timeouts with `--limit 100`

### Never Do

❌ **Never forget brackets on dates** - `startDate>[2025-01-01]` not `startDate>2025-01-01`
❌ **Never use grep when --conditions works** - Filter server-side for performance
❌ **Never skip connection test on errors** - `cw config test` reveals most issues
❌ **Never assume IDs without verifying** - List records to confirm IDs exist

---

## Common Query Patterns

### Customer Health Check

Get complete view of a customer:

```bash
# Get company details
cw companies get <COMPANY_ID>

# Active agreements
cw agreements list --conditions "company/id=<COMPANY_ID> AND agreementStatus='Active'"

# Recent invoices
cw invoices list --conditions "company/id=<COMPANY_ID>" --limit 10 --format json

# Agreement products/services
cw agreements additions <AGREEMENT_ID>
```

### Finding Expiring Agreements

```bash
# macOS date calculation
DATE_60=$(date -v+60d +%Y-%m-%d)

# Linux date calculation
DATE_60=$(date -d "+60 days" +%Y-%m-%d)

# Query expiring agreements
cw agreements list --conditions "endDate<=[${DATE_60}] AND agreementStatus='Active'"
```

### Unpaid/Overdue Invoices

```bash
# Unpaid invoices (status/id=1 means "Sent")
cw invoices list --conditions "status/id=1"

# Overdue invoices
TODAY=$(date +%Y-%m-%d)
cw invoices list --conditions "dueDate<[${TODAY}] AND status/id=1"

# Invoices for specific agreement
cw invoices list --conditions "agreement/id=<AGREEMENT_ID>"
```

### Search by Name

```bash
# Company name search (case-insensitive)
cw companies list --conditions "name contains 'Tech'"

# Product search
cw catalog list --conditions "description contains 'Server'"

# Multiple terms with OR
cw companies list --conditions "name contains 'Tech' OR name contains 'Solutions'"
```

### High-Value Records

```bash
# Agreements over $5000/month
cw agreements list --conditions "billAmount>5000 AND agreementStatus='Active'"

# Invoices over $1000
cw invoices list --conditions "total>1000"

# Products in price range
cw catalog list --conditions "price>=10 AND price<=100"
```

### Contact Management

```bash
# List contacts for a company
cw contacts list --conditions "company/id=<COMPANY_ID>"

# Search contacts by name
cw contacts list --conditions "firstName contains 'John'"

# Get contact details (automatically enriched with phones, emails)
cw contacts get <CONTACT_ID>

# Find contacts by email domain
cw contacts list --conditions "defaultEmailAddress like '*@company.com'"
```

---

## Filter Syntax Reference

### Operators

- **Comparison**: `=`, `!=`, `>`, `>=`, `<`, `<=`
- **Text**: `contains` (case-insensitive), `like` (wildcards: `*` multiple chars, `?` single char)
- **Logical**: `AND`, `OR`, `NOT`, `in (val1,val2,val3)`
- **Null**: `=null`, `!=null`

### Field References

```bash
# Direct field
--conditions "name='Acme Corp'"

# Related field (lookup)
--conditions "company/id=250"
--conditions "company/name='Acme Corp'"

# Nested related field
--conditions "company/status/id=1"
```

### Date Filters

**Format:** `[YYYY-MM-DD]` (brackets required!)

```bash
# After date
--conditions "startDate>[2025-01-01]"

# Date range
--conditions "invoiceDate>=[2025-01-01] AND invoiceDate<=[2025-01-31]"

# Null check
--conditions "cancelledDate=null"
```

### Combining Conditions

```bash
# AND (all must be true)
--conditions "company/id=250 AND agreementStatus='Active'"

# OR (at least one true)
--conditions "status='Active' OR status='Pending'"

# Complex (use parentheses)
--conditions "(status='Active' OR status='Pending') AND company/id=250"

# List membership
--conditions "company/id in (250,251,252)"
```

See references/filter-patterns.md for comprehensive syntax guide.

---

## Friendly Search Syntax

**NEW**: Natural language search alternative to complex `--conditions` syntax.

Commands with `@searchable_command` decorator support friendly queries that are automatically translated to ConnectWise filter syntax:

```bash
# Natural language queries (automatically converted)
cw agreements list --search "active and company 250"
cw companies list --search "name tech or name solutions"
cw invoices list --search "unpaid and overdue"
cw contacts list --search "email @acme.com and company 250"

# Equivalent to complex --conditions
# "active and company 250" → "agreementStatus='Active' AND company/id=250"
# "unpaid" → "status/id=1"
# "overdue" → "dueDate<[TODAY]"
```

**Search Keywords by Entity**:

**Agreements**:
- Status: `active`, `inactive`, `cancelled`
- Time: `expiring` (next 60 days), `expired`
- Reference: `company <ID>`, `agreement <ID>`

**Invoices**:
- Status: `paid`, `unpaid`, `overdue`
- Reference: `company <ID>`, `agreement <ID>`

**Companies**:
- Text: `name <term>` (contains search)

**Contacts**:
- Text: `name <term>`, `email <pattern>`
- Reference: `company <ID>`

**Operators**:
- Logical: `and`, `or`, `not`
- Comparison: `>`, `>=`, `<`, `<=`, `=`

**Benefits**:
- Easier to remember than ConnectWise syntax
- Automatic field name resolution
- Built-in date calculation (expiring, overdue)
- Value validation and error messages

**Use Cases**:
```bash
# Find expiring agreements for a company
cw agreements list --search "expiring and company 250"

# Get overdue invoices for high-value agreements
cw invoices list --search "overdue and agreement 161"

# Search contacts by email domain
cw contacts list --search "email @company.com"
```

**Note**: For complex queries not covered by search keywords, fall back to `--conditions` with full ConnectWise syntax.

---

## Troubleshooting Guide

### "Command not found: connectwise-cli"

**Solution:**
```bash
# Activate virtual environment
cd /Users/dallascrilley/Code/personal-projects/connectwise-cli
source .venv/bin/activate
cw --version
```

### "401 Unauthorized"

**Cause:** Invalid API credentials

**Solution:**
```bash
# Test connection
cw config test

# Regenerate API keys in ConnectWise:
# System > Members > [Your User] > API Keys

# Update configuration
cw config init
```

### "403 Forbidden"

**Cause:** Authenticated but not authorized for this resource

**Solution:**
- Check member permissions: System > Members > [User] > Security
- Verify security roles allow API access
- Contact admin for elevated permissions

### "404 Not Found"

**Cause:** Resource doesn't exist or wrong endpoint

**Solution:**
```bash
# Verify resource exists by listing
cw agreements list --limit 5

# Check configuration
cw config show

# Verify API base URL is correct
# North America: https://api-na.myconnectwise.net
# Europe: https://api-eu.myconnectwise.net
# Australia: https://api-aus.myconnectwise.net
```

### "422 Unprocessable Entity"

**Cause:** Invalid filter syntax

**Solution:**
```bash
# Check date format - must have brackets
# WRONG: "startDate>2025-01-01"
# RIGHT: "startDate>[2025-01-01]"

# Use debug mode to see exact error
cw --debug agreements list --conditions "your filter"

# Test with simple filter first
cw agreements list --conditions "id>0" --limit 1
```

### "429 Too Many Requests"

**Cause:** Rate limit exceeded

**Solution:**
```bash
# Wait and retry
sleep 60 && cw agreements list

# Add delays between requests
for id in $(seq 1 10); do
  cw agreements get $id
  sleep 2
done

# Use larger page sizes to reduce request count
cw agreements list --limit 100
```

### "Connection timeout"

**Solution:**
```bash
# Increase timeout in ~/.connectwiserc
# Edit file and add:
timeout: 60.0  # seconds

# Or use smaller page sizes
cw agreements list --limit 10

# Test basic connectivity
ping api-na.myconnectwise.net
```

### "No results found"

**Solution:**
```bash
# Test without filters first
cw agreements list --limit 5

# Check filter syntax with debug
cw --debug agreements list --conditions "your filter"

# View sample data to verify field names
cw agreements list --format json --limit 1 | jq
```

See references/error-solutions.md for complete troubleshooting guide.

---

## Output Formats

```bash
# Table (default, for terminal viewing)
cw agreements list

# JSON (for processing with jq)
cw agreements list --format json

# CSV (for Excel/spreadsheets)
cw agreements list --format csv --output data.csv

# Markdown (for documentation)
cw agreements list --format markdown
```

**JSON Processing:**
```bash
# Count results
cw agreements list --format json | jq 'length'

# Get specific field
cw agreements list --format json | jq '.[].id'

# Filter in jq (use --conditions instead when possible!)
cw agreements list --format json | jq '.[] | select(.company.id == 250)'
```

---

## Configuration Management

```bash
# Show current config (credentials masked)
cw config show

# Show config file location
cw config path

# Test API connection
cw config test

# Initialize/update config interactively
cw config init
```

**Configuration Precedence** (highest to lowest):
1. CLI arguments (`--api-url`, `--company-id`, etc.)
2. Config file (`~/.connectwiserc`)
3. Environment variables (`CONNECTWISE_API_BASE_URL`, etc.)

**Config File Location:** `~/.connectwiserc`

```yaml
api_base_url: https://api-na.myconnectwise.net
api_version: v2025_1
company_id: yourcompany
public_key: your_public_key
private_key: your_private_key
client_id: your_client_id
timeout: 30.0
```

---

## Shell Completion

Generate shell completions for command auto-complete:

```bash
# Bash
cw completion bash > ~/.local/share/bash-completion/completions/cw
source ~/.bashrc

# Zsh
cw completion zsh > ~/.zsh/completions/_cw
# Add to ~/.zshrc: fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit

# Fish
cw completion fish > ~/.config/fish/completions/cw.fish
```

**Benefits**:
- Tab-complete commands: `cw agr<TAB>` → `cw agreements`
- Tab-complete subcommands: `cw agreements li<TAB>` → `cw agreements list`
- Tab-complete options: `cw agreements list --co<TAB>` → `cw agreements list --conditions`

---

## Common Resources

### Agreements
- `cw agreements list [--conditions "filter"]`
- `cw agreements get <ID>`
- `cw agreements additions <ID>` - List products/services in agreement

### Companies
- `cw companies list [--conditions "filter"]`
- `cw companies get <ID>`

### Invoices
- `cw invoices list [--conditions "filter"]`
- `cw invoices get <ID>`

### Catalog
- `cw catalog list [--conditions "filter"]`
- `cw catalog get <ID>`

### Contacts
- `cw contacts list [--conditions "filter"]`
- `cw contacts get <ID>`
- Includes automatic contact enrichment (phone numbers, email addresses, etc.)

---

## Write Operations

### Agreement Additions (Products/Services)

**IMPORTANT**: Write operations are restricted to Agreement ID 161 only (safety measure).

```bash
# Create new product/service in agreement
cw agreements additions-write create 161 \
  --product-id <CATALOG_ID> \
  --quantity 1

# Update existing addition
cw agreements additions-write update 161 <ADDITION_ID> \
  --quantity 2 \
  --price 99.99 \
  --description "Updated description"

# Delete addition (with confirmation)
cw agreements additions-write delete 161 <ADDITION_ID>

# Delete without confirmation prompt
cw agreements additions-write delete 161 <ADDITION_ID> --yes
```

**Available Fields for Create/Update**:
- `--product-id` - Catalog item ID (required for create)
- `--quantity` - Quantity (default: 1)
- `--price` - Override catalog price
- `--description` - Custom description
- `--effective-date` - Start date [YYYY-MM-DD]
- `--cancelled-date` - End date [YYYY-MM-DD]

**Safety Notes**:
- All write operations validate agreement ID = 161
- Delete operations prompt for confirmation (use `--yes` to skip)
- Review changes with `cw agreements additions 161` after operations

---

## Quick Reference by Use Case

| Use Case | Command |
|----------|---------|
| Customer health check | `cw companies get <ID>` + agreements + invoices + contacts |
| Expiring agreements | `--search "expiring"` or `--conditions "endDate<=[DATE] AND agreementStatus='Active'"` |
| Overdue invoices | `--search "overdue"` or `--conditions "dueDate<[TODAY] AND status/id=1"` |
| Active agreements | `--search "active"` or `--conditions "agreementStatus='Active'"` |
| Search by name | `--search "name text"` or `--conditions "name contains 'text'"` |
| High-value agreements | `--conditions "billAmount>5000"` |
| By company | `--search "company <ID>"` or `--conditions "company/id=<ID>"` |
| Contact by email | `--search "email @domain.com"` |
| Date range | `--conditions "date>=[START] AND date<=[END]"` |
| Add product to agreement | `cw agreements additions-write create 161 --product-id <ID>` |

See references/common-queries.md for comprehensive examples.

---

## Performance Tips

✅ **Filter on server with --conditions** - Don't fetch all data and filter client-side
✅ **Use --limit for large datasets** - Prevent timeouts: `--limit 100`
✅ **Filter on indexed fields** - `id`, `status/id`, `company/id`, dates (fast)
✅ **Paginate large exports** - Use `--page` and `--limit` together

❌ **Avoid text search when ID works** - `company/id=250` faster than `company/name contains 'Acme'`
❌ **Avoid fetching all then filtering** - Use `--conditions` instead of piping to jq

---

## Debug Commands

```bash
# Enable debug output
cw --debug agreements list

# Enable verbose logging
cw --verbose agreements list

# Collect diagnostic information
cw --version
cw config show
cw config test
cw --debug [command] 2>&1 | tee debug.log
```

---

## Documentation Location

Full documentation: `/Users/dallascrilley/Code/personal-projects/connectwise-cli/docs/`

- `getting-started.md` - Installation and setup
- `api-examples.md` - Comprehensive usage examples
- `filtering.md` - Complete filter syntax guide
- `troubleshooting.md` - Detailed error solutions
- `configuration.md` - Configuration options

---

## Quick Workflow

1. **Always start with connection test**: `cw config test`
2. **Try friendly search first**: `--search "active and company 250"` is easier than complex `--conditions`
3. **List before getting**: `cw agreements list --limit 5` to see available records
4. **Test filters with --limit 1**: Verify syntax before large queries
5. **Use debug on errors**: `cw --debug [command]` reveals exact issue
6. **Check docs for complex cases**: references/ for detailed patterns

---

## Notes

- All dates MUST use `[YYYY-MM-DD]` format with brackets
- Always quote `--conditions` values: `"field=value"`
- Filter on server with `--conditions`, not client-side with jq
- Test connection with `cw config test` before complex operations
- Virtual environment must be activated: `source .venv/bin/activate`
