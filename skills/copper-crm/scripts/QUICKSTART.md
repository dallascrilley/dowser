# Bulk Import Quick Start Guide

Get started with the Copper CRM bulk importer in 5 minutes.

## 1. Installation

```bash
# Install dependencies
pip install requests rich

# Or with uv
uv add requests rich
```

## 2. Set Up API Key

```bash
# Option A: Set environment variable
export COPPER_API_KEY="your-api-key-here"

# Option B: Use --api-key flag in command
python bulk_import.py leads import.csv --api-key "your-api-key-here"
```

## 3. Prepare CSV File

Create a CSV with required columns:

**Leads:**
```csv
name,email,company_name,title,phone
John Smith,john@acmecorp.com,Acme Corp,Sales Manager,555-0101
Jane Doe,jane@techstartup.io,TechStartup Inc,Product Lead,555-0102
```

**People:**
```csv
name,email,company_name,title
John Smith,john@acmecorp.com,Acme Corp,Sales Manager
Jane Doe,jane@techstartup.io,TechStartup Inc,Product Lead
```

**Companies:**
```csv
name,email_domain,address
Acme Corporation,acmecorp.com,"123 Main St, New York, NY"
TechStartup Inc,techstartup.io,"456 Tech Ave, San Francisco, CA"
```

**Opportunities:**
```csv
name,primary_contact_email,monetary_value
Enterprise Deal,contact@company.com,50000
Startup Lead,startup@new.io,15000
```

## 4. Run Import

```bash
# Basic usage
python bulk_import.py leads leads.csv

# With UPSERT mode (default)
python bulk_import.py leads leads.csv --mode upsert

# With CREATE mode (skip existing)
python bulk_import.py leads leads.csv --mode create

# Using specific API key
python bulk_import.py leads leads.csv --api-key "your-key"
```

## 5. Review Results

The script outputs:
- Real-time progress bar
- Summary of successes/failures/duplicates
- Error details for failed records
- Overall success rate

Example output:
```
Loading CSV file: leads.csv
Loaded 100 records

Importing 100 records... ████████████████████████ 100%

============================================================
Import Summary Report
============================================================
Total Records:              100
Successful:                 98
Duplicates Updated:         12
Failed:                     2
Success Rate:              98.0%

Failed Records:
  Row 45: Invalid email format
  Row 87: Missing required field: company_name
============================================================
```

## Common Commands

```bash
# Import 50 leads with UPSERT
python bulk_import.py leads leads.csv --mode upsert

# Import 100 people as new records only
python bulk_import.py people people.csv --mode create

# Import companies
python bulk_import.py companies companies.csv

# Import opportunities
python bulk_import.py opportunities opportunities.csv

# Test with example file
python bulk_import.py leads example_leads.csv
```

## Troubleshooting

### API Key Error
```bash
# Set environment variable
export COPPER_API_KEY="your-key-here"

# Or use flag
python bulk_import.py leads data.csv --api-key "your-key"
```

### CSV Headers Error
Check that column names exactly match requirements:
- Leads: name, email, company_name, title, phone
- People: name, email, company_name, title
- Companies: name, email_domain, address
- Opportunities: name, primary_contact_email, monetary_value

### Email Format Error
Ensure all emails have "@" symbol:
```csv
name,email,company_name,title,phone
John Smith,john@company.com,Acme,Manager,555-1234
```

### File Not Found Error
Use absolute or relative path to CSV:
```bash
python bulk_import.py leads ./data/leads.csv
python bulk_import.py leads /full/path/to/leads.csv
```

## Performance Notes

- Batch size: 10 records
- Rate limit: 3 requests/second
- Speed: ~100-150 records/minute
- 1000 records: ~6-10 minutes

For faster processing of non-duplicate records, use `--mode create`.

## Next Steps

1. Test with small CSV (10 records) first
2. Review errors and fix data
3. Run final import with full CSV
4. Verify results in Copper CRM interface

For detailed documentation, see:
- `README.md` - Full feature documentation
- `IMPLEMENTATION_GUIDE.md` - Architecture and advanced usage
- `example_leads.csv` - Sample CSV format
