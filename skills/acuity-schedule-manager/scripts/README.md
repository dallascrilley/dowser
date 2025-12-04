# Acuity Scheduling Manager - Helper Scripts

Comprehensive suite of production-ready Python and Bash scripts for managing the Acuity Scheduling API integration. All scripts include error handling, logging, input validation, and beautiful terminal output using the Rich library.

## Quick Start

### 1. Setup Environment

```bash
# Navigate to scripts directory
cd ~/.claude/skills/acuity-schedule-manager/scripts

# Run setup script
bash setup.sh

# Or verify only
bash setup.sh --verify-only
```

### 2. Validate Credentials

```bash
python3 validate_credentials.py
python3 validate_credentials.py --verbose
python3 validate_credentials.py --json
```

## Scripts Overview

### setup.sh - Environment Setup

**Purpose:** Initialize Acuity Scheduling Manager with all dependencies, credential validation, and API connectivity test.

**Features:**
- Python 3.8+ version checking
- Automatic dependency installation (requests, python-dotenv, pydantic, pytz, rich)
- Credential validation with masked output
- API connectivity test (GET /me endpoint)
- Redis availability check (optional)
- Directory structure verification

**Usage:**
```bash
# Full setup with all checks
bash setup.sh

# Verify credentials only
bash setup.sh --verify-only

# Skip Redis check
bash setup.sh --skip-redis

# Verbose output
bash setup.sh --verbose
```

**Exit Codes:**
- 0: Setup successful
- 1: Setup failed
- 2: Invalid arguments

---

### validate_credentials.py - Credential Validator

**Purpose:** Validate Acuity API credentials and test multiple endpoints to ensure proper configuration.

**Features:**
- Load credentials from .env file
- Mask sensitive API keys in output (shows first 4 and last 4 characters)
- Test multiple endpoints (/me, /calendars, /appointment-types)
- Display account info in color-coded output
- Generate detailed validation report
- JSON output for CI/CD integration

**Usage:**
```bash
# Standard validation with color output
python3 validate_credentials.py

# Verbose output with debug details
python3 validate_credentials.py --verbose

# JSON output for automation
python3 validate_credentials.py --json

# Custom .env file location
python3 validate_credentials.py --env /path/to/.env
```

**Output:**
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Acuity Scheduling API Credential Validator      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

✓ API Access: Connected as John's Business
✓ Calendars: 3 configured
✓ Appointment Types: 5 available

✓ Validation Summary
All 3 tests passed! API credentials are valid and working
```

**Exit Codes:**
- 0: All validations passed
- 1: One or more validations failed

---

### check_availability.py - Availability Checker

**Purpose:** Check and display appointment availability in calendar format with time slots.

**Features:**
- Interactive mode: Step-by-step selection of type, date, and time
- Quick mode: CLI arguments for direct query
- Display month calendar with available dates highlighted
- Show time slots with timezone formatting
- JSON export option for API consumption
- Cache support with --no-cache flag
- Timezone handling for global businesses

**Usage:**
```bash
# Interactive mode (guided prompts)
python3 check_availability.py

# Check specific date
python3 check_availability.py --type-id 12345 --date 2025-11-15

# Check month and output JSON
python3 check_availability.py --type-id 12345 --month 2025-11 --json

# Custom timezone
python3 check_availability.py --type-id 12345 --date 2025-11-15 \
  --tz America/Los_Angeles

# Skip caching
python3 check_availability.py --type-id 12345 --date 2025-11-15 --no-cache
```

**Interactive Flow:**
```
1. Select Appointment Type (numbered list)
2. Enter Month (YYYY-MM or 'today')
3. View Calendar (green = available)
4. Enter Date (YYYY-MM-DD)
5. Select Time Slot
```

**Output:**
```
Available Times
┏━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ # ┃ Time      ┃ Timezone    ┃
┡━━╇━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 1 │ 09:00 AM  │ EST         │
│ 2 │ 10:30 AM  │ EST         │
│ 3 │ 02:00 PM  │ EST         │
└━━┴━━━━━━━━━━┴━━━━━━━━━━━━━┘
```

---

### create_appointment.py - Appointment Creator

**Purpose:** Create new appointments with full validation, availability checking, and confirmation.

**Features:**
- Interactive guided mode with step-by-step prompts
- Batch mode for creating multiple appointments from JSON file
- Quick mode for direct CLI creation
- Real-time availability verification before creation
- Pydantic validation for all inputs (email, phone, datetime, timezone)
- Confirmation prompt before API call
- Generate appointment receipt/confirmation
- Handle custom fields and notes
- Disposable email rejection

**Usage:**
```bash
# Interactive mode (guided)
python3 create_appointment.py

# Batch create from JSON
python3 create_appointment.py --batch appointments.json

# Quick mode (all args provided)
python3 create_appointment.py --type-id 12345 \
  --date 2025-11-15T14:00:00-0500 \
  --first John --last Doe \
  --email john@example.com --phone 555-0123

# Custom timezone
python3 create_appointment.py --type-id 12345 \
  --date 2025-11-15T14:00:00-0500 \
  --first John --last Doe \
  --email john@example.com --phone 555-0123 \
  --tz America/Los_Angeles
```

**JSON Batch Format:**
```json
[
  {
    "appointmentTypeID": 12345,
    "datetime": "2025-11-15T14:00:00-0500",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "timezone": "America/New_York",
    "notes": "VIP client"
  },
  {
    "appointmentTypeID": 12345,
    "datetime": "2025-11-16T10:00:00-0500",
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0124"
  }
]
```

**Validation:**
- Email: Valid format, no disposable addresses
- Phone: 10-15 digits with formatting allowed
- Name: 1-100 characters
- Datetime: ISO format, must be in future
- Timezone: Valid IANA timezone

**Output:**
```
✓ Appointment Created Successfully!

Appointment ID: 123456789
Name: John Doe
Email: john@example.com
Date & Time: 2025-11-15T14:00:00-0500
Price: $75.00
Status: Confirmed
```

---

### export_appointments.py - Appointment Exporter

**Purpose:** Export appointments for reporting, analytics, or backup in CSV or JSON format.

**Features:**
- Date range selection with shortcuts (--today, --this-week, --this-month, --last-month)
- Export formats: CSV, JSON with configurable headers
- Pagination handling (automatic, 100 per page)
- Rate limiting compliance (0.1s delay between requests)
- Progress indicator using Rich
- Statistics summary (count, revenue, canceled)
- Date range support
- Appointment type and calendar filtering

**Usage:**
```bash
# Export this month to CSV
python3 export_appointments.py --this-month

# Export this week to JSON
python3 export_appointments.py --this-week --format json

# Export date range
python3 export_appointments.py --start 2025-01-01 --end 2025-12-31

# Custom output file
python3 export_appointments.py --this-month --output my_appointments.csv

# Filter by appointment type
python3 export_appointments.py --this-month --type-id 12345

# Include canceled appointments
python3 export_appointments.py --this-month --include-canceled
```

**Date Range Shortcuts:**
- `--today`: Current date only
- `--this-week`: Monday-today of current week
- `--this-month`: 1st-today of current month
- `--last-month`: First-last day of previous month

**Output Examples:**

CSV: `appointments_2025-11-01_to_2025-11-30.csv`
```csv
id,firstName,lastName,email,datetime,appointmentTypeID,price,canceled
123456789,John,Doe,john@example.com,2025-11-15T14:00:00-0500,12345,75.00,false
```

JSON: `appointments_2025-11-01_to_2025-11-30.json`
```json
{
  "exported_at": "2025-11-11T10:30:00",
  "total_appointments": 150,
  "appointments": [
    {
      "id": 123456789,
      "firstName": "John",
      ...
    }
  ]
}
```

**Summary Output:**
```
Export Complete

Date Range: 2025-11-01 to 2025-11-30
Total Appointments: 150
Canceled: 5
Active: 145
Total Revenue: $11,250.00
API Requests: 2
```

---

### test_webhook.py - Webhook Tester

**Purpose:** Generate webhook payloads, create HMAC signatures, and test webhook delivery.

**Features:**
- Generate sample webhook payloads for all event types
- HMAC-SHA256 signature generation for testing
- Send test payload to local or remote endpoint
- Verify endpoint response and timing
- Test signature validation
- Support multiple event types (scheduled, rescheduled, canceled, order.completed)
- Generate-only mode for payload inspection

**Event Types:**
- `scheduled` / `appointment.scheduled`: New appointment
- `rescheduled` / `appointment.rescheduled`: Rescheduled appointment
- `canceled` / `appointment.canceled`: Canceled appointment
- `changed` / `appointment.changed`: Any appointment change
- `order_completed` / `order.completed`: Product order completed

**Usage:**
```bash
# Test local webhook endpoint
python3 test_webhook.py --endpoint http://localhost:5000/webhooks/acuity

# Test with specific event type
python3 test_webhook.py --endpoint https://api.example.com/webhooks/acuity \
  --event appointment.scheduled

# Custom webhook secret
python3 test_webhook.py --endpoint https://api.example.com/webhooks \
  --secret "my_webhook_secret"

# Generate payload without sending
python3 test_webhook.py --generate-only --event appointment.canceled

# Generate signature only
python3 test_webhook.py --signature-only --event scheduled
```

**Output:**
```
Webhook Payload
{
  "id": 123456789,
  "action": "scheduled",
  "firstName": "Test",
  "lastName": "User",
  "email": "test@example.com",
  "datetime": "2025-11-18T14:00:00.123456"
}

Signature Information
Secret: my_api_key
Signature: a1b2c3d4e5f6...
Header: X-Acuity-Signature: a1b2c3d4e5f6...

Delivery Result
✓ SUCCESS

Endpoint: https://api.example.com/webhooks
Status Code: 200
Response Time: 125.3ms
```

---

### sync_clients.py - Client Synchronizer

**Purpose:** Synchronize appointments and client data from Acuity to external systems (CRM, database, webhooks).

**Features:**
- Date range or specific client email filtering
- YAML config file for destination mapping
- Dry-run mode to preview changes without syncing
- Progress indication
- Error logging and retry logic
- Field transformation and mapping
- Multiple destination support
- Webhook and HTTP POST support

**Configuration (YAML):**
```yaml
destinations:
  - name: "Default CRM"
    type: "webhook"
    url: "https://api.example.com/contacts"
    method: "POST"
    headers:
      Authorization: "Bearer token123"

  - name: "Backup CRM"
    type: "webhook"
    url: "https://api.backup.com/sync"
    method: "POST"

field_mapping:
  email: "customer_email"
  firstName: "first_name"
  lastName: "last_name"
  phone: "phone_number"
  datetime: "appointment_datetime"
```

**Usage:**
```bash
# Sync this month's appointments
python3 sync_clients.py --config sync_config.yaml --this-month

# Sync specific client
python3 sync_clients.py --config sync_config.yaml --email john@example.com

# Dry run to preview changes
python3 sync_clients.py --config sync_config.yaml --this-month --dry-run

# Sync date range
python3 sync_clients.py --config sync_config.yaml \
  --start 2025-01-01 --end 2025-12-31

# Verbose output
python3 sync_clients.py --config sync_config.yaml --this-month --verbose
```

**Output:**
```
Syncing Acuity Clients

Found 45 appointments

✓ Appointment 1 sent to Default CRM
✓ Appointment 2 sent to Default CRM
✓ Appointment 3 sent to Default CRM

Sync Summary
Status: SUCCESS

Total: 45
Successful: 45
Failed: 0
Success Rate: 100.0%
```

---

## Common Workflows

### Workflow 1: Complete Setup and Validation

```bash
# 1. Run setup
bash setup.sh

# 2. Validate credentials
python3 validate_credentials.py

# 3. Check available appointment types and dates
python3 check_availability.py --this-month

# Done! System is ready to use
```

### Workflow 2: Create and Monitor Appointments

```bash
# 1. Create appointment interactively
python3 create_appointment.py

# 2. Verify it was created (export recent)
python3 export_appointments.py --today

# 3. Set up webhook for real-time notifications
python3 test_webhook.py --endpoint https://your-api.com/webhooks/acuity
```

### Workflow 3: Batch Import from CSV

```bash
# 1. Prepare appointments.json with appointment data

# 2. Create appointments in batch
python3 create_appointment.py --batch appointments.json

# 3. Export to confirm
python3 export_appointments.py --today --format json
```

### Workflow 4: Sync to External CRM

```bash
# 1. Create sync_config.yaml with destination mapping

# 2. Test dry-run first
python3 sync_clients.py --config sync_config.yaml --this-month --dry-run

# 3. Execute sync
python3 sync_clients.py --config sync_config.yaml --this-month

# 4. Verify in external system
```

### Workflow 5: Monthly Reporting

```bash
# 1. Export month's data
python3 export_appointments.py --this-month --format csv

# 2. Analyze in Excel or Python:
#    - Total appointments
#    - Revenue
#    - Cancel rate
#    - Busiest days/times

# 3. Archive CSV for records
cp appointments_*.csv ~/archive/
```

---

## Troubleshooting

### "Credentials not found"
```bash
# 1. Check .env file exists and has correct variables
cat ~/.claude/skills/acuity-schedule-manager/.env

# 2. Verify environment variables are set
echo $ACUITY_USER_ID
echo $ACUITY_API_KEY

# 3. Run setup again
bash setup.sh
```

### "API Unauthorized (401)"
```bash
# 1. Verify credentials are correct
python3 validate_credentials.py

# 2. Check API key hasn't been regenerated
# 3. Get new credentials from Acuity dashboard
```

### "Rate limit exceeded (429)"
```bash
# Most scripts handle this automatically, but:
# 1. Check your request frequency (max 10/sec)
# 2. Reduce concurrent requests (max 20 connections)
# 3. Use --no-cache flag to avoid cache misses
```

### "Timezone mismatch in appointments"
```bash
# Always specify timezone explicitly:
python3 create_appointment.py --tz America/Los_Angeles

# Check availability with timezone:
python3 check_availability.py --type-id 12345 --date 2025-11-15 \
  --tz America/Los_Angeles
```

### "Webhook not receiving events"
```bash
# 1. Test webhook delivery
python3 test_webhook.py --endpoint https://your-endpoint.com/webhook

# 2. Verify endpoint is HTTPS (required)
# 3. Check webhook is enabled in Acuity dashboard
# 4. Review firewall/security groups allowing Acuity IP ranges
# 5. Ensure endpoint responds quickly (< 30 seconds)
```

---

## Environment Variables

Required:
- `ACUITY_USER_ID` - Your Acuity User ID
- `ACUITY_API_KEY` - Your Acuity API Key

Optional:
- `ACUITY_WEBHOOK_URL` - Webhook endpoint URL
- `ACUITY_WEBHOOK_SECRET` - Webhook signing secret
- `REDIS_URL` - Redis connection for caching (optional)
- `LOG_LEVEL` - Logging level (INFO, DEBUG, etc.)

---

## Requirements

**Python Packages:**
- requests >= 2.28.0 (HTTP client)
- python-dotenv >= 0.21.0 (Environment loading)
- pydantic >= 1.10.0 (Data validation)
- pytz >= 2023.3 (Timezone handling)
- rich >= 13.0.0 (Terminal formatting)

**Optional:**
- redis (for caching)
- pyyaml (for YAML config files)
- email-validator (for email validation)

**System:**
- Python 3.8+
- Bash (for setup.sh)

---

## Best Practices

### Security
- Never commit .env file to version control
- Rotate API keys every 90 days
- Use separate credentials for dev/staging/prod
- Validate webhook signatures in production
- Run webhooks on HTTPS only

### Performance
- Use --no-cache only when necessary
- Batch operations when creating multiple appointments
- Export in chunks (monthly, not yearly)
- Run sync jobs during off-hours
- Monitor rate limit usage

### Data Quality
- Always validate email addresses
- Include phone validation
- Verify availability before creation
- Test timezone handling
- Monitor canceled rate

### Reliability
- Set up monitoring for webhook delivery
- Use dry-run mode before syncing large datasets
- Keep logs for audit trail
- Test webhooks regularly
- Review error logs daily

---

## Getting Help

- Check script docstrings: `python3 script.py --help`
- Review Acuity API docs: https://acuityscheduling.com/api
- Check logs: `grep ERROR acuity_*.log`
- Test credentials: `python3 validate_credentials.py --verbose`

---

**Version:** 1.0
**Last Updated:** 2025-11-11
**Status:** Production Ready
