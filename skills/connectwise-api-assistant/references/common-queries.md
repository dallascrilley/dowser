# Common ConnectWise CLI Queries

Quick reference for frequently-used ConnectWise queries.

## Finding Records by ID

```bash
# Agreement details
cw agreements get <ID>

# Company details
cw companies get <ID>

# Invoice details
cw invoices get <ID>

# Catalog item details
cw catalog get <ID>
```

## Customer Health Check

```bash
# All active agreements for a company
cw agreements list --conditions "company/id=<COMPANY_ID> AND agreementStatus='Active'"

# Recent invoices for a company
cw invoices list --conditions "company/id=<COMPANY_ID>" --limit 10

# Get company details
cw companies get <COMPANY_ID>
```

## Agreement Queries

```bash
# Active agreements only
cw agreements list --conditions "agreementStatus='Active'"

# Agreements expiring in next 60 days
cw agreements list --conditions "endDate<=[DATE_60_DAYS] AND agreementStatus='Active'"

# High-value agreements (>$5000/month)
cw agreements list --conditions "billAmount>5000 AND agreementStatus='Active'"

# Agreement additions (products/services)
cw agreements additions <AGREEMENT_ID>

# Filter by company
cw agreements list --conditions "company/id=<COMPANY_ID>"
```

## Invoice Queries

```bash
# Unpaid invoices
cw invoices list --conditions "status/id=1"

# Overdue invoices
cw invoices list --conditions "dueDate<[TODAY] AND status/id=1"

# Invoices for specific agreement
cw invoices list --conditions "agreement/id=<AGREEMENT_ID>"

# Invoices over certain amount
cw invoices list --conditions "total>1000"

# Date range (e.g., last month)
cw invoices list --conditions "invoiceDate>=[2025-01-01] AND invoiceDate<=[2025-01-31]"
```

## Company Queries

```bash
# Search by name (partial match)
cw companies list --conditions "name contains 'Tech'"

# Active companies
cw companies list --conditions "status/id=1"

# By territory
cw companies list --conditions "territory/id=<TERRITORY_ID>"
```

## Catalog Queries

```bash
# Active products
cw catalog list --conditions "inactiveFlag=false"

# Search by description
cw catalog list --conditions "description contains 'Server'"

# Price range
cw catalog list --conditions "price>=10 AND price<=100"

# By category
cw catalog list --conditions "category/id=<CATEGORY_ID>"
```

## Output Formats

```bash
# JSON (for processing)
cw agreements list --format json

# CSV (for Excel)
cw agreements list --format csv --output data.csv

# Markdown (for documentation)
cw agreements list --format markdown

# Table (default, for terminal)
cw agreements list --format table
```

## Dynamic Date Calculations

```bash
# macOS date calculations
TODAY=$(date +%Y-%m-%d)
LAST_MONTH=$(date -v-1m +%Y-%m-%d)
NEXT_MONTH=$(date -v+1m +%Y-%m-%d)
DATE_60_DAYS=$(date -v+60d +%Y-%m-%d)

# Linux date calculations
TODAY=$(date +%Y-%m-%d)
LAST_MONTH=$(date -d "1 month ago" +%Y-%m-%d)
NEXT_MONTH=$(date -d "1 month" +%Y-%m-%d)
DATE_60_DAYS=$(date -d "+60 days" +%Y-%m-%d)

# Use in queries
cw invoices list --conditions "invoiceDate>=[${LAST_MONTH}]"
```
