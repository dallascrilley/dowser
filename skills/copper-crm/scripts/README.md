# Copper CRM API Scripts

A suite of Python utilities for working with Copper CRM API, including connection testing, bulk imports, and configuration validation.

## Scripts

### 1. test_connection.py - Connection Test & Diagnostics

A diagnostic tool that validates your Copper CRM API credentials and connection setup.

#### Features

- **Credentials Validation**: Loads and verifies API credentials from .env
- **Authentication Test**: Validates API key and user email
- **Account Information**: Retrieves and displays account name and ID
- **User Permissions**: Checks user role and permission level
- **Rate Limiting Test**: Verifies API rate limits with 5 quick requests
- **Connection Summary**: Comprehensive report of all checks
- **Error Reporting**: Clear error messages for troubleshooting

#### Quick Start

```bash
python test_connection.py
```

#### Output Example

```
Testing Copper CRM API Connection...
--------------------------------------------------
✓ Credentials loaded
✓ Authentication successful
✓ Account: Acme Corp (ID: 123456)
✓ User: john@example.com (Admin permissions)
✓ Rate limit test: 5/5 requests successful
==================================================
CONNECTION TEST SUMMARY
==================================================
✓ Connection ready!

All tests passed! Your Copper CRM API connection is working.

Test Timestamp: 2025-11-08 04:42:15
==================================================
```

#### Requirements

- `.env` file with `COPPER_API_KEY` and `COPPER_USER_EMAIL`
- `requests` library
- `python-dotenv` library

#### Environment Variables

Required in `.env`:
- `COPPER_API_KEY` - Your API key from Copper CRM settings
- `COPPER_USER_EMAIL` - Email associated with your Copper CRM account

Optional:
- `COPPER_BASE_URL` - API endpoint (default: https://api.copper.com/developer_api/v1)

#### Troubleshooting

**"Missing COPPER_API_KEY or COPPER_USER_EMAIL in .env"**
- Create `.env` file in the copper-crm directory
- Copy template from `templates/.env.example`
- Fill in your actual credentials

**"Authentication failed: Invalid API key or email"**
- Verify API key is correct in Copper CRM settings (Settings → Integrations → API)
- Check email address matches your Copper CRM account
- Ensure credentials are not expired

**"Request timeout"**
- Check internet connection
- Verify Copper CRM API is accessible
- Try again in a few moments

---

### 2. validate_config.py - Configuration Validation & Testing

A comprehensive validation tool that tests your Copper CRM configuration end-to-end before running production operations.

#### Features

- **Environment File Loading**: Loads and validates `.env` file
- **Required Variables Check**: Ensures all required credentials are present
- **Email Format Validation**: Validates email address format
- **API Key Validation**: Checks API key format and structure
- **Base URL Validation**: Ensures URL format is correct
- **Authentication Testing**: Makes real API request to `/account` endpoint
- **User Information Extraction**: Retrieves user email and permission level
- **Rate Limit Status**: Displays current rate limit availability
- **Exit Codes**: Standard exit codes for scripting and CI/CD integration

#### Quick Start

```bash
python validate_config.py
```

#### Output Example (Success)

```
✓ Configuration file found
✓ Environment variables validation
✓ Email format validation
✓ API credentials validation
✓ Base URL validation
✓ Authentication successful
✓ User: john.doe@company.com (Admin)
✓ Rate limit status - 180/min available (default)

Configuration validation successful!
```

#### Exit Codes

- **0** - All validations passed, configuration is valid
- **1** - Configuration or format validation error
- **2** - API communication error (network, timeout, endpoint issue)
- **3** - Missing required environment variables

#### Requirements

- `.env` file with:
  - `COPPER_API_KEY` - API key from Copper CRM
  - `COPPER_USER_EMAIL` - Email associated with Copper account
  - `COPPER_BASE_URL` - Base URL for Copper API
- `requests` library
- `python-dotenv` library

#### Validation Checks

1. **Configuration File Loading** - Checks if `.env` exists and can be parsed
2. **Required Variables** - Validates all three required variables are present
3. **Email Format** - Validates email address syntax using RFC 5322 pattern
4. **API Key Format** - Checks API key is non-empty and reasonable length
5. **Base URL Format** - Ensures URL starts with `https://` or `http://`
6. **Authentication Test** - Makes GET request to `/account` endpoint
   - Validates API key and user email
   - Detects permission levels (Admin, User, Limited User, etc.)
   - Handles authentication errors gracefully
7. **Rate Limit Status** - Displays rate limit info from API response

#### Troubleshooting

**"Configuration file not found: .env"**
```bash
# Create .env file with your credentials
cat > .env << 'EOF'
COPPER_API_KEY=your_api_key_here
COPPER_USER_EMAIL=your.email@example.com
COPPER_BASE_URL=https://api.copper.com
EOF
```

**"Missing required environment variables"**
- Add missing variables to `.env` file
- Ensure no typos in variable names

**"Invalid email format"**
- Check email address is valid: `user@domain.com`
- Ensure no spaces or special characters

**"Authentication failed: Invalid API key or user email"**
- Verify API key in Copper CRM: Settings → Integrations → API
- Verify email matches your Copper account
- Check API key hasn't been revoked

**"Account endpoint not found: Check COPPER_BASE_URL"**
- Verify base URL is correct (typically `https://api.copper.com`)
- Ensure no extra path like `/v1` in the URL

**"Failed to connect to API"**
- Check internet connection
- Verify Copper API is accessible
- Check for firewall or proxy restrictions

#### Advanced Usage

Use in scripts and CI/CD pipelines:

```bash
#!/bin/bash
# Validate config before starting application
if ! python validate_config.py; then
    echo "Configuration validation failed"
    exit 1
fi

# Configuration is valid, proceed with application
python main.py
```

GitHub Actions example:

```yaml
- name: Validate Copper CRM Configuration
  run: python validate_config.py
  env:
    COPPER_API_KEY: ${{ secrets.COPPER_API_KEY }}
    COPPER_USER_EMAIL: ${{ secrets.COPPER_USER_EMAIL }}
    COPPER_BASE_URL: https://api.copper.com
```

---

### 3. bulk_import.py - Bulk Data Import

A comprehensive Python utility for importing leads, people, companies, and opportunities into Copper CRM with validation, duplicate detection, and error recovery.

#### Features

- **Multi-Entity Support**: Import leads, people, companies, and opportunities
- **Data Validation**: Automatic validation of required fields and format
- **Duplicate Detection**: UPSERT mode to update existing records or create new ones
- **Batch Processing**: Processes 10 records per batch with 3 req/sec rate limiting
- **Error Recovery**: Automatic retry logic (3 attempts) for failed records
- **Progress Tracking**: Rich progress bar with real-time updates
- **Summary Report**: Detailed report of successes, failures, and duplicates

## Installation

### Dependencies

```bash
pip install requests rich
```

Or with uv:
```bash
uv add requests rich
```

## Usage

### Basic Command

```bash
python bulk_import.py <entity_type> <csv_file> [options]
```

### Entity Types

- **leads** - Create/update lead records
- **people** - Create/update person records
- **companies** - Create/update company records
- **opportunities** - Create/update opportunity records

### Options

- `--mode {create,upsert}` - Import mode (default: upsert)
  - `create`: Only create new records, skip duplicates
  - `upsert`: Update existing records or create if not found
- `--api-key KEY` - Copper CRM API key (can use COPPER_API_KEY env var)

## Examples

### Import Leads with UPSERT

```bash
export COPPER_API_KEY="your-api-key-here"
python bulk_import.py leads leads.csv --mode upsert
```

### Import People from CSV

```bash
python bulk_import.py people people.csv --api-key "your-api-key"
```

### Import Companies (Create Only)

```bash
python bulk_import.py companies companies.csv --mode create --api-key "your-api-key"
```

### Import Opportunities

```bash
python bulk_import.py opportunities deals.csv --api-key "your-api-key"
```

## CSV Format Requirements

### Leads

Required columns:
- `name` - Lead name
- `email` - Email address
- `company_name` - Company name
- `title` - Job title
- `phone` - Phone number

Example:
```csv
name,email,company_name,title,phone
John Smith,john.smith@acmecorp.com,Acme Corporation,Sales Manager,555-0101
```

### People

Required columns:
- `name` - Person name
- `email` - Email address
- `company_name` - Associated company
- `title` - Job title

Example:
```csv
name,email,company_name,title
Jane Doe,jane.doe@techstartup.io,TechStartup Inc,Product Lead
```

### Companies

Required columns:
- `name` - Company name
- `email_domain` - Email domain
- `address` - Company address

Example:
```csv
name,email_domain,address
Acme Corporation,acmecorp.com,"123 Main St, New York, NY"
```

### Opportunities

Required columns:
- `name` - Opportunity name
- `primary_contact_email` - Contact email
- `monetary_value` - Deal value (numeric)

Example:
```csv
name,primary_contact_email,monetary_value
Big Deal,contact@company.com,50000
```

## How It Works

### 1. Data Loading
- Reads CSV file and auto-detects headers
- Validates column names match entity type requirements
- Reports any missing required columns

### 2. Validation
- Checks all required fields are present and non-empty
- Entity-specific validation (email format, numeric values, etc.)
- Records validation errors without stopping the process

### 3. Duplicate Detection (UPSERT Mode)
- For each record, searches for existing match:
  - **Leads/People**: By email address
  - **Companies**: By name
  - **Opportunities**: By name
- If found, updates existing record
- If not found, creates new record

### 4. Batch Processing
- Processes 10 records per batch
- Enforces 3 requests per second rate limit
- Prevents API throttling and rate limit errors

### 5. Error Recovery
- Retries failed records up to 3 times
- Waits 2 seconds between retry attempts
- Reports failures with specific error messages

### 6. Reporting
- Shows real-time progress bar
- Displays summary statistics
- Lists any failed records with error details
- Reports success rate and duplicate counts

## Output Example

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

## Environment Variables

- `COPPER_API_KEY` - Copper CRM API key (alternative to --api-key flag)

## Error Handling

- **Missing API Key**: Script exits with clear error message
- **CSV File Not Found**: Reports file not found error
- **Invalid Headers**: Lists missing required columns
- **Invalid Data**: Records validation errors per row
- **API Errors**: Retries failed records automatically
- **User Cancellation**: Gracefully handles Ctrl+C

## Performance

- **Batch Size**: 10 records per batch
- **Rate Limit**: 3 requests per second (to respect API limits)
- **Retry Logic**: 3 attempts per failed record with 2-second delays
- **Typical Speed**: ~30 records per minute (accounting for rate limits)

## Sample Files

See `example_leads.csv` for a sample leads import file.

## API Key

Get your Copper CRM API key from:
1. Log into Copper CRM
2. Go to Settings → Integrations → API
3. Copy your API key

## Troubleshooting

### "Copper API key not provided"
- Set environment variable: `export COPPER_API_KEY="your-key"`
- Or use flag: `--api-key "your-key"`

### "Missing required columns"
- Check CSV headers match required fields for entity type
- CSV headers are case-insensitive
- Verify no extra spaces in column names

### "Invalid email format"
- Ensure email addresses contain "@" symbol
- Check for typos in email addresses

### High failure rate
- Check API key is correct and has permissions
- Verify Copper API is accessible
- Check rate limiting isn't causing issues
- Review error messages in failed records report

---

### 4. copper_cli.py - Interactive CLI Tool

A comprehensive command-line interface for managing Copper CRM with interactive menus, advanced search, bulk imports, and robust error handling.

#### Features

- **CRUD Operations**: Create, Read, Update, and Delete records for Leads, People, Companies, and Opportunities
- **Advanced Search**: Filter records by multiple criteria
- **Bulk Import**: Import records from CSV files with progress tracking
- **UPSERT Mode**: Prevent duplicates by automatically updating existing records
- **Error Handling**: Automatic retry logic for rate limiting (429) and server errors (500+)
- **Rich UI**: Beautiful formatted output with progress bars and tables
- **Interactive Mode**: Menu-driven interface for users who prefer point-and-click

#### Installation

```bash
pip install -r requirements.txt
```

#### Quick Start

##### Interactive Mode (Recommended)
```bash
python copper_cli.py interactive
```

Launches an interactive menu with options to:
1. Create Record
2. Search Records
3. Update Record
4. Delete Record
5. Bulk Import
6. Exit

##### Command Mode

###### Create a record
```bash
python copper_cli.py create leads
python copper_cli.py create people
python copper_cli.py create companies
python copper_cli.py create opportunities
```

###### Search records
```bash
# Basic search
python copper_cli.py search leads --query "John Doe"

# With filters
python copper_cli.py search people -q "john" -f "email=john@example.com"

# Limit results
python copper_cli.py search companies -l 20
```

Options:
- `-q, --query`: Search query (typically name, email, etc.)
- `-f, --field`: Filter by field (format: field=value, can be used multiple times)
- `-l, --limit`: Number of results to return (default: 10)

###### Update a record
```bash
python copper_cli.py update leads 12345
python copper_cli.py update people 67890
```

The CLI will fetch the current record, display it, and prompt for field updates.

###### Delete a record
```bash
python copper_cli.py delete leads 12345
```

You'll be prompted to confirm deletion before proceeding.

###### Bulk import from CSV
```bash
# Standard import
python copper_cli.py bulk-import data.csv -e leads

# With UPSERT (prevent duplicates)
python copper_cli.py bulk-import data.csv -e people --upsert -u email

# Dry run to preview
python copper_cli.py bulk-import data.csv -e companies --dry-run
```

Options:
- `-e, --entity`: Entity type (leads, people, companies, opportunities) [required]
- `--upsert`: Enable UPSERT mode (update if exists, create if new)
- `-u, --upsert-field`: Field to match for UPSERT (default: email)
- `--dry-run`: Preview import without making changes

#### Supported Entities

##### Leads
- Fields: name, email, phone, company_name, status
- Required: name

##### People
- Fields: first_name, last_name, email, phone, company_id
- Required: first_name, last_name

##### Companies
- Fields: name, email, phone, website, address
- Required: name

##### Opportunities
- Fields: name, company_id, person_id, stage, status, value
- Required: name

#### Advanced Features

##### UPSERT Mode
Prevent duplicate records by automatically updating existing records if they match the specified field:

```bash
# Update by email if exists, otherwise create
python copper_cli.py bulk-import contacts.csv -e people --upsert -u email

# Update by phone if exists
python copper_cli.py bulk-import leads.csv -e leads --upsert -u phone
```

##### Dry Run Mode
Preview your import without making any changes:

```bash
python copper_cli.py bulk-import large_file.csv -e companies --dry-run
```

Shows:
- Total records to import
- Success/failure counts
- Error details
- Without modifying any data

##### Progress Tracking
Bulk imports show real-time progress with:
- Spinner indicator
- Percentage completion
- Record count
- Success/error summary

#### Error Handling

The tool includes robust error handling:

- **Rate Limiting (HTTP 429)**: Automatic retry with exponential backoff (3 attempts, 2x multiplier)
- **Server Errors (HTTP 500+)**: Automatic retry logic with clear error messages
- **Invalid Data**: Field validation with required field checking
- **User-friendly Messages**: Clear feedback for all error conditions

#### API Configuration

The tool uses:
- **Base URL**: https://api.copper.com/developer_api/v1
- **Auth Method**: X-PW-AccessToken header
- **Timeout**: 30 seconds per request
- **Retries**: 3 attempts with exponential backoff

#### Environment Variables

Required in `.env`:
- `COPPER_API_TOKEN` - Your API token from Copper CRM

#### Examples

##### Creating a lead with search
```bash
# Search for existing leads
python copper_cli.py search leads -q "Acme"

# Create a new lead (interactive)
python copper_cli.py create leads
# Follow prompts to enter data
```

##### Importing and updating contacts
```bash
# First import with UPSERT to prevent duplicates
python copper_cli.py bulk-import new_contacts.csv -e people --upsert -u email

# Later, update specific records
python copper_cli.py update people 12345
```

##### Monthly bulk operations
```bash
# Preview what will happen
python copper_cli.py bulk-import monthly_update.csv -e opportunities --dry-run

# If satisfied, run for real
python copper_cli.py bulk-import monthly_update.csv -e opportunities --upsert -u name
```

#### Troubleshooting

**"COPPER_API_TOKEN not found"**
- Ensure `.env` file exists with `COPPER_API_TOKEN=your_token_here`

**Rate limiting errors**
- Reduce batch size in CSV imports
- Add delays between bulk operations
- Modify `RETRY_ATTEMPTS` in code

**CSV import fails**
- Verify CSV has required fields
- Check field names match entity configuration
- Use `--dry-run` to preview issues

**Connection timeouts**
- Check internet connection
- Verify API endpoint is accessible
- Increase `TIMEOUT` in code (default: 30 seconds)

## License

Use freely within your organization.
