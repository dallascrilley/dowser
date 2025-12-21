---
name: acuity-schedule-manager
short_description: >-
  Manage Acuity Scheduling API integrations for appointment booking, client
  management, availability checking, and webhook handling.
description: >-
  Manage Acuity Scheduling API integrations with appointment booking, client
  management, availability checking, and webhook handling. USE WHEN user needs
  to integrate Acuity Scheduling, create/manage appointments, sync client data,
  check availability, or set up booking webhooks. Keywords - acuity, scheduling,
  appointments, booking, calendar, availability, webhooks, client management,
  CRM sync.
when_to_use: >-
  Use when integrating Acuity Scheduling API, creating/managing/canceling
  appointments programmatically, checking availability for time slots and dates,
  managing client data via API, syncing Acuity appointments with CRM systems,
  setting up Acuity webhooks for real-time notifications...
version: 1.0.0
category: integrations-and-saas
---

# Acuity Scheduling API Manager

Complete toolkit for integrating with Acuity Scheduling API - automate appointment booking, client management, availability checking, and real-time webhook event processing with production-ready scripts and comprehensive guardrails.

## Tool Overview

**Acuity Scheduling API** is a RESTful web service for programmatic appointment scheduling and business automation.

**Key Capabilities:**
- **Appointment Management** - Create, update, cancel, reschedule appointments
- **Availability Checking** - Query available time slots and dates
- **Client Management** - Create, update, retrieve client information
- **Webhook Support** - Real-time notifications for appointment events
- **Multi-Calendar** - Manage multiple calendars and staff schedules
- **Custom Forms** - Retrieve intake forms and field configurations
- **Gift Certificates** - Handle certificate creation and validation
- **Product Orders** - Manage product sales and orders

**Use Cases:**
- Custom scheduling interfaces and mobile apps
- CRM integration for client management
- Automated appointment booking from external systems
- Healthcare appointment management
- Professional services booking automation
- Analytics and reporting dashboards

## Prerequisites

**IMPORTANT:** Before using this skill, you need Acuity Scheduling credentials.

### Obtaining API Credentials

1. **Log into your Acuity Scheduling account**
2. **Navigate to:** Business Settings → Integrations → API
3. **Copy your User ID** (numeric)
4. **Generate or retrieve your API Key** (alphanumeric string)
5. **Store securely** (treat as password - never commit to version control)

### First-Time Setup

Run the automated setup script:

```bash
cd ~/.claude/skills/acuity-schedule-manager/scripts
./setup.sh
```

This script will:
- Install required Python dependencies (requests, python-dotenv, pydantic, pytz, rich)
- Verify credential format
- Test API connectivity
- Check optional dependencies (Redis for caching)
- Create necessary directory structure

**Manual Setup:**

```bash
# Create credentials file
cp templates/credentials.env.template .env

# Edit with your credentials
nano .env

# Test credentials
python scripts/validate_credentials.py
```

## Quick Start

**Check available appointment types:**
```bash
curl -u {userId}:{apiKey} https://acuityscheduling.com/api/v1/appointment-types
```

**Check availability:**
```bash
python scripts/check_availability.py --interactive
```

**Create appointment:**
```bash
python scripts/create_appointment.py --interactive
```

**Using example files:**
```bash
# Create appointment from sample data
python scripts/create_appointment.py --file examples/sample_appointment.json

# Explore API with cURL
./examples/curl_examples.sh

# Set up CRM sync
cp examples/sample_sync_config.yml config/sync_config.yml
```

**See:** [examples/README.md](examples/README.md) for complete examples collection

## Core Tasks

### Task 1: Check Availability

**Quick check for today:**
```bash
python scripts/check_availability.py --appointment-type 12345 --date today
```

**Interactive mode:**
```bash
python scripts/check_availability.py --interactive
```

**Export to JSON:**
```bash
python scripts/check_availability.py --appointment-type 12345 --date 2025-11-15 --json > availability.json
```

**See:** [references/workflows-reference.md](references/workflows-reference.md#availability-calendar-display)

### Task 2: Create Appointments

**Interactive guided creation:**
```bash
python scripts/create_appointment.py --interactive
```

**Batch creation from JSON:**
```bash
python scripts/create_appointment.py --file appointments.json
```

**Example JSON:**
```json
{
  "appointmentTypeID": 12345,
  "datetime": "2025-11-15T14:00:00-0500",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "555-0123"
}
```

**See:** [references/workflows-reference.md](references/workflows-reference.md#complete-appointment-booking)

### Task 3: Export Appointments

**Export this month to CSV:**
```bash
python scripts/export_appointments.py --this-month --format csv --output november_2025.csv
```

**Custom date range:**
```bash
python scripts/export_appointments.py \
  --start-date 2025-11-01 \
  --end-date 2025-11-30 \
  --format json \
  --output appointments.json
```

**Using config preset:**
```bash
python scripts/export_appointments.py --config templates/export_config.yml --preset monthly_report
```

**See:** [references/workflows-reference.md](references/workflows-reference.md#bulk-appointment-export)

### Task 4: Sync with CRM

**Sync new appointments since yesterday:**
```bash
python scripts/sync_clients.py --since yesterday --config templates/sync_config.yml
```

**Sync specific client:**
```bash
python scripts/sync_clients.py --email john@example.com --config templates/sync_config.yml
```

**Dry run (preview changes):**
```bash
python scripts/sync_clients.py --since yesterday --dry-run
```

**See:** [references/workflows-reference.md](references/workflows-reference.md#crm-synchronization)

### Task 5: Webhook Setup

**Test your webhook endpoint:**
```bash
python scripts/test_webhook.py \
  --url https://your-server.com/webhooks/acuity \
  --event scheduled \
  --secret your_webhook_secret
```

**Test all event types:**
```bash
python scripts/test_webhook.py \
  --url https://your-server.com/webhooks/acuity \
  --all-events \
  --secret your_webhook_secret
```

**See:** [references/webhook-integration-guide.md](references/webhook-integration-guide.md)

## API Reference

### Base URL
```
https://acuityscheduling.com/api/v1
```

### Authentication
HTTP Basic Authentication using User ID and API Key:

```bash
curl -u {userId}:{apiKey} https://acuityscheduling.com/api/v1/appointments
```

**Python:**
```python
from requests.auth import HTTPBasicAuth
import requests

session = requests.Session()
session.auth = HTTPBasicAuth('12345678', 'your-api-key')
response = session.get('https://acuityscheduling.com/api/v1/appointments')
```

**See:** [references/authentication-guide.md](references/authentication-guide.md) for complete auth setup

### Common Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/appointments` | GET | List/search appointments |
| `/appointments` | POST | Create appointment |
| `/appointments/{id}` | GET | Get appointment details |
| `/appointments/{id}` | PUT | Update appointment |
| `/appointments/{id}/cancel` | PUT | Cancel appointment |
| `/appointments/{id}/reschedule` | PUT | Reschedule appointment |
| `/availability/times` | GET | Check available times |
| `/availability/dates` | GET | Check available dates |
| `/clients` | GET/POST | Manage clients |
| `/appointment-types` | GET | List appointment types |
| `/calendars` | GET | List calendars |
| `/forms` | GET | Get intake forms |

**See:** [references/api-endpoints-reference.md](references/api-endpoints-reference.md) for complete endpoint catalog

### Rate Limiting

- **Default:** 10 requests per second
- **Burst:** Up to 50 requests in short burst
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

**See:** [references/error-handling-guide.md](references/error-handling-guide.md#rate-limiting-429)

## Configuration Files

### Credentials Configuration

**Template:** `templates/credentials.env.template`

```bash
# Copy template
cp templates/credentials.env.template .env

# Edit with your credentials
ACUITY_USER_ID=12345678
ACUITY_API_KEY=your_api_key_here
ACUITY_BASE_URL=https://acuityscheduling.com/api/v1

# Environment
ENVIRONMENT=development  # development, staging, production

# Cache Settings
CACHE_ENABLED=true
CACHE_TTL_APPOINTMENT_TYPES=86400  # 24 hours
CACHE_TTL_AVAILABILITY=300  # 5 minutes

# Webhook
WEBHOOK_SECRET=your_webhook_secret_here

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Webhook Configuration

**Template:** `templates/webhook_config.yml.template`

Configure webhook endpoints, event subscriptions, and handler actions:

```yaml
webhook:
  endpoint:
    url: https://your-server.com/webhooks/acuity
    method: POST

  events:
    - appointment_scheduled
    - appointment_rescheduled
    - appointment_canceled

  security:
    signature_verification: true
    secret_env_var: WEBHOOK_SECRET
```

**See:** [references/webhook-integration-guide.md](references/webhook-integration-guide.md) for complete setup

### CRM Sync Configuration

**Template:** `templates/sync_config.yml.template`

Configure bidirectional synchronization with your CRM:

```yaml
sync:
  direction: acuity_to_crm  # acuity_to_crm, crm_to_acuity, bidirectional

  field_mapping:
    client:
      email: email
      firstName: first_name
      lastName: last_name
      phone: phone_number
```

### Export Configuration

**Template:** `templates/export_config.yml.template`

Presets for common export scenarios:

- `monthly_report` - Full appointment details for reporting
- `daily_backup` - JSON backup of all appointments
- `revenue_analysis` - Revenue-focused export with payment info

## Proven Patterns

### ⚠️ MANDATORY: Pre-Appointment Creation Workflow

**Always follow this workflow when creating appointments:**

1. **Check availability FIRST:**
   ```bash
   python scripts/check_availability.py --appointment-type 12345 --date 2025-11-15
   ```

2. **Validate input data:**
   - Email format (RFC 5322)
   - Phone number format
   - Datetime in ISO 8601 format with timezone
   - Required fields present

3. **Create appointment:**
   ```bash
   python scripts/create_appointment.py --file appointment.json
   ```

4. **Verify creation:**
   - Check response for appointment ID
   - Verify confirmation code
   - Log successful creation

**Why this prevents failures:**
- **Prevents race conditions** - Availability can change between check and creation
- **Ensures data validity** - Catches format errors before API call
- **Provides fallback times** - Can offer alternative slots if first choice taken
- **Maintains audit trail** - Logging enables troubleshooting

**See:** [CRITICAL PITFALL #5 in Risk Assessment](All_APIs/API_Docs/Acuity_Scheduling_API/RISK_ASSESSMENT_AND_PITFALLS.md#critical-pitfall-5-availability-race-condition)

### ⚠️ MANDATORY: Webhook Security Validation

**Before deploying webhooks to production:**

1. **Use HTTPS only** (never HTTP)
2. **Implement signature verification:**
   ```python
   import hmac
   import hashlib

   def verify_webhook_signature(payload, signature, secret):
       expected = hmac.new(
           secret.encode(),
           payload,
           hashlib.sha256
       ).hexdigest()
       return hmac.compare_digest(signature, expected)
   ```

3. **Return 200 immediately** (process in background queue)
4. **Set up webhook health monitoring** (check daily)
5. **Handle duplicate events** (use Redis with TTL)

**Why this prevents failures:**
- **Prevents webhook auto-disable** - Acuity disables after 5 days of failures
- **Stops malicious requests** - Signature verification ensures authenticity
- **Avoids timeout disable** - Immediate 200 response prevents timeout failures
- **Enables recovery** - Health monitoring catches issues early

**See:** [CRITICAL PITFALL #2 in Risk Assessment](All_APIs/API_Docs/Acuity_Scheduling_API/RISK_ASSESSMENT_AND_PITFALLS.md#critical-pitfall-2-webhook-auto-disabling)

### Pattern 1: Complete Appointment Booking Flow

```python
# Step 1: Get appointment types
appointment_types = api.get('/appointment-types')

# Step 2: Check availability
availability = api.get('/availability/times', params={
    'appointmentTypeID': selected_type['id'],
    'date': '2025-11-15',
    'timezone': 'America/New_York'
})

# Step 3: Create appointment with validation
if availability:
    appointment = api.post('/appointments', json={
        'appointmentTypeID': selected_type['id'],
        'datetime': availability[0]['time'],
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'phone': '555-0123'
    })
```

**See:** [references/workflows-reference.md](references/workflows-reference.md) for 7 complete workflow patterns

### Pattern 2: Multi-Calendar Availability Aggregation

```python
# Get all calendars
calendars = api.get('/calendars')

# Check availability for each
all_availability = {}
for calendar in calendars:
    availability = api.get('/availability/times', params={
        'appointmentTypeID': 12345,
        'date': '2025-11-15',
        'calendarID': calendar['id']
    })
    all_availability[calendar['id']] = availability

# Find common times across all calendars
common_times = find_overlapping_slots(all_availability)
```

### Pattern 3: Robust Error Handling with Retry

```python
import time

def make_api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = session.get(url)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited - exponential backoff
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            elif response.status_code >= 500:
                # Server error - retry
                time.sleep(2 ** attempt)
                continue
            else:
                # Client error - don't retry
                raise Exception(f"API Error: {response.status_code}")

        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
```

**See:** [references/error-handling-guide.md](references/error-handling-guide.md) for comprehensive error handling patterns

## Troubleshooting

**Quick fixes for common issues:**

| Issue | Solution |
|-------|----------|
| **401 Unauthorized** | Check User ID and API Key in `.env` file. Run `python scripts/validate_credentials.py` |
| **429 Too Many Requests** | Implement rate limiting with exponential backoff. See [error-handling-guide.md](references/error-handling-guide.md#rate-limiting-429) |
| **Timezone mismatch** | Always specify timezone parameter in availability checks. Use `America/New_York` format |
| **Webhook not firing** | Check webhook status in Acuity dashboard. May be auto-disabled after 5 days of failures |
| **Availability race condition** | Use optimistic booking - book immediately, handle 409 conflicts with fallback times |
| **Invalid email format** | Validate with regex: `^[\w\.-]+@[\w\.-]+\.\w+$` before API call |
| **Appointment not created** | Check for availability first. Verify all required fields present and correctly formatted |
| **Signature verification fails** | Ensure webhook secret matches Acuity dashboard. Use `hmac.compare_digest()` for comparison |

**For detailed solutions:** [references/error-handling-guide.md](references/error-handling-guide.md)

**For critical pitfalls:** [RISK_ASSESSMENT_AND_PITFALLS.md](All_APIs/API_Docs/Acuity_Scheduling_API/RISK_ASSESSMENT_AND_PITFALLS.md)

## Helper Scripts

**Location:** `~/.claude/skills/acuity-schedule-manager/scripts/`

### Setup & Validation

**`setup.sh`** - First-time installation and verification
```bash
./scripts/setup.sh
```

**`validate_credentials.py`** - Test API credentials
```bash
python scripts/validate_credentials.py
```

### Core Operations

**`check_availability.py`** - Interactive availability checker
```bash
# Interactive mode
python scripts/check_availability.py --interactive

# Quick check
python scripts/check_availability.py --appointment-type 12345 --date today

# Export to JSON
python scripts/check_availability.py --appointment-type 12345 --date 2025-11-15 --json
```

**`create_appointment.py`** - Guided appointment creation
```bash
# Interactive guided creation
python scripts/create_appointment.py --interactive

# Batch from JSON file
python scripts/create_appointment.py --file appointments.json
```

**`export_appointments.py`** - Bulk appointment export
```bash
# Export this month
python scripts/export_appointments.py --this-month --format csv

# Custom date range
python scripts/export_appointments.py --start-date 2025-11-01 --end-date 2025-11-30

# Use preset
python scripts/export_appointments.py --config templates/export_config.yml --preset monthly_report
```

### Integration & Testing

**`sync_clients.py`** - CRM synchronization
```bash
# Sync since yesterday
python scripts/sync_clients.py --since yesterday --config templates/sync_config.yml

# Sync specific client
python scripts/sync_clients.py --email john@example.com

# Dry run
python scripts/sync_clients.py --since yesterday --dry-run
```

**`test_webhook.py`** - Webhook endpoint tester
```bash
# Test single event
python scripts/test_webhook.py --url https://your-server.com/webhooks --event scheduled

# Test all events
python scripts/test_webhook.py --url https://your-server.com/webhooks --all-events

# With signature verification
python scripts/test_webhook.py --url https://your-server.com/webhooks --secret your_secret
```

**See:** [scripts/README.md](scripts/README.md) for complete script documentation

## Workflow Requirements

### ⚠️ MANDATORY: Always Follow Appointment Creation Workflow

When creating appointments programmatically, you MUST follow this workflow to prevent booking failures and race conditions:

**1. Check Availability First**
```bash
python scripts/check_availability.py --appointment-type 12345 --date 2025-11-15
```

**2. Validate All Input Data**
- Email format (RFC 5322 compliant)
- Phone number (E.164 format recommended)
- Datetime (ISO 8601 with timezone)
- Required fields present (appointmentTypeID, datetime, firstName, lastName, email)

**3. Create Appointment with Validated Data**
```bash
python scripts/create_appointment.py --file validated_appointment.json
```

**4. Handle Creation Response**
- On success (200): Log appointment ID and confirmation code
- On conflict (409): Offer fallback times from availability check
- On validation error (400): Show specific field errors to user
- On rate limit (429): Retry with exponential backoff

**Why this prevents failures:**

1. **Prevents Race Conditions** - Between availability check and creation, slots can be taken. Having fallback times ready prevents user frustration.

2. **Ensures Data Validity** - Validating before API call prevents 400 errors and provides better user feedback.

3. **Maintains Audit Trail** - Logging each step enables troubleshooting and debugging.

4. **Handles Rate Limiting** - Proper retry logic prevents cascading failures.

5. **Provides User Experience** - Fallback times and clear error messages improve UX.

**Validation Script:**
```bash
# Run pre-deployment validation
python scripts/validate_credentials.py
python scripts/test_webhook.py --url https://your-server.com/webhooks --all-events
```

**See Critical Pitfall #5:** [RISK_ASSESSMENT_AND_PITFALLS.md](All_APIs/API_Docs/Acuity_Scheduling_API/RISK_ASSESSMENT_AND_PITFALLS.md#critical-pitfall-5)

---

## Common Workflows

### Workflow 1: Daily Appointment Sync to CRM

**Purpose:** Automatically sync yesterday's appointments to your CRM every morning

**Steps:**
```bash
# 1. Export yesterday's appointments
python scripts/export_appointments.py \
  --start-date yesterday \
  --end-date yesterday \
  --format json \
  --output /tmp/yesterday_appointments.json

# 2. Sync to CRM
python scripts/sync_clients.py \
  --since yesterday \
  --config templates/sync_config.yml

# 3. Verify sync (optional)
python scripts/validate_credentials.py
```

**Automation:** Add to crontab
```bash
# Run daily at 8am
0 8 * * * cd ~/.claude/skills/acuity-schedule-manager && python scripts/sync_clients.py --since yesterday --config templates/sync_config.yml >> /var/log/acuity-sync.log 2>&1
```

### Workflow 2: Weekly Appointment Report

**Purpose:** Generate weekly appointment summary for management

**Steps:**
```bash
# Export this week's appointments to Excel
python scripts/export_appointments.py \
  --this-week \
  --format csv \
  --config templates/export_config.yml \
  --preset weekly_report \
  --output reports/week_$(date +%Y-%m-%d).csv

# Generate statistics
python -c "
import json
with open('reports/week_$(date +%Y-%m-%d).json') as f:
    data = json.load(f)
    print(f'Total appointments: {len(data)}')
    print(f'Canceled: {sum(1 for a in data if a.get(\"canceled\"))}')
"
```

### Workflow 3: Real-time Booking with Fallback

**Purpose:** Book appointment with automatic fallback if first choice is taken

**Steps:**
```python
# 1. Check availability and get multiple options
availability = check_availability(
    appointment_type_id=12345,
    date='2025-11-15',
    timezone='America/New_York'
)

primary_time = availability[0]['time']
fallback_times = [slot['time'] for slot in availability[1:4]]

# 2. Attempt booking with primary time
try:
    appointment = create_appointment({
        'appointmentTypeID': 12345,
        'datetime': primary_time,
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john@example.com',
        'phone': '555-0123'
    })
    print(f"Booked at {primary_time}")

except ConflictError:
    # 3. Try fallback times
    for fallback_time in fallback_times:
        try:
            appointment = create_appointment({
                'appointmentTypeID': 12345,
                'datetime': fallback_time,
                # ... other fields
            })
            print(f"Booked at fallback time {fallback_time}")
            break
        except ConflictError:
            continue
    else:
        print("No available times - please select different date")
```

### Workflow 4: Webhook Event Processing Pipeline

**Purpose:** Handle Acuity webhook events with queue-based processing

**Setup:**
```bash
# 1. Configure webhook
cp templates/webhook_config.yml.template webhook_config.yml
# Edit with your settings

# 2. Start webhook handler (Flask/FastAPI)
python webhook_handler.py

# 3. Start background worker (Celery)
celery -A tasks worker --loglevel=info

# 4. Monitor webhook health
python scripts/test_webhook.py --url https://your-server.com/webhooks --all-events
```

**See:** [references/webhook-integration-guide.md](references/webhook-integration-guide.md) for complete implementation

### Workflow 5: Monthly Revenue Analysis

**Purpose:** Export appointment data for revenue analysis and reporting

**Steps:**
```bash
# Export previous month with revenue details
python scripts/export_appointments.py \
  --last-month \
  --config templates/export_config.yml \
  --preset revenue_analysis \
  --output reports/revenue_$(date +%Y-%m).xlsx

# Generate summary statistics
python -c "
import pandas as pd
df = pd.read_excel('reports/revenue_$(date +%Y-%m).xlsx')
print(f'Total Revenue: ${df[\"price\"].sum():.2f}')
print(f'Total Appointments: {len(df)}')
print(f'Average Price: ${df[\"price\"].mean():.2f}')
print(f'\\nRevenue by Type:')
print(df.groupby('type')[\"price\"].sum())
"
```

## Tips

### Performance Optimization

**Cache Frequently Accessed Data:**
```bash
# Enable caching in .env
CACHE_ENABLED=true
CACHE_TTL_APPOINTMENT_TYPES=86400  # 24 hours
CACHE_TTL_AVAILABILITY=300  # 5 minutes

# Use Redis for distributed caching
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Batch Operations:**
```bash
# Good: Retrieve multiple appointments in one request
python scripts/export_appointments.py --this-month

# Avoid: Individual requests for each appointment
# for id in appointment_ids:
#     curl -u {userId}:{apiKey} https://acuityscheduling.com/api/v1/appointments/{id}
```

**Use Webhooks Instead of Polling:**
- Set up webhooks for real-time notifications
- Avoid constant polling for new appointments
- Reduces API calls by ~95%

### Security Best Practices

**Never Expose API Credentials:**
```bash
# ✅ Good: Use environment variables
export ACUITY_USER_ID=12345678
export ACUITY_API_KEY=your_api_key

# ❌ Bad: Hardcode in code
api_key = "abc123def456"  # NEVER DO THIS
```

**Always Use Server-Side Proxy:**
```javascript
// ❌ NEVER call Acuity API directly from browser
// This exposes your credentials!
fetch('https://acuityscheduling.com/api/v1/appointments', {
  headers: {
    'Authorization': 'Basic ' + btoa(userId + ':' + apiKey)
  }
})

// ✅ Always proxy through your server
fetch('/api/appointments')  // Your server handles Acuity API
```

**Rotate API Keys Regularly:**
```bash
# Generate new API key every 90 days
# Update .env file
# Test with validate_credentials.py
# Deploy new key
# Revoke old key
```

### Error Handling

**Always Implement Retry Logic:**
```python
# Use exponential backoff for rate limiting
for attempt in range(max_retries):
    try:
        response = api.get(url)
        if response.status_code == 429:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
            continue
        break
    except Exception:
        if attempt == max_retries - 1:
            raise
```

**Log Everything:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger.info(f"Creating appointment for {email}")
logger.error(f"Failed to create appointment: {error}")
```

### Timezone Handling

**Always Specify Timezone:**
```python
# ✅ Good: Explicit timezone
availability = api.get('/availability/times', params={
    'appointmentTypeID': 12345,
    'date': '2025-11-15',
    'timezone': 'America/New_York'
})

# ❌ Bad: No timezone (uses calendar default)
availability = api.get('/availability/times', params={
    'appointmentTypeID': 12345,
    'date': '2025-11-15'
})
```

**Use pytz for Timezone Conversion:**
```python
import pytz
from datetime import datetime

utc = pytz.UTC
eastern = pytz.timezone('America/New_York')

# Convert to client timezone
utc_time = datetime.fromisoformat('2025-11-15T19:00:00Z')
local_time = utc_time.astimezone(eastern)
```

## Testing

### Running Tests

**Quick test run:**
```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
./tests/run_tests.sh

# Run specific test types
./tests/run_tests.sh unit          # Unit tests only (fast)
./tests/run_tests.sh integration   # Integration tests
./tests/run_tests.sh coverage      # With coverage report
```

### Test Coverage

**Unit Tests:**
- Email validation (10+ test cases)
- Phone validation (8+ test cases)
- Datetime validation (7+ test cases)
- Appointment data validation (5+ test cases)
- Timezone validation (6+ test cases)
- Rate limiting logic (3+ test cases)

**Integration Tests:**
- Authentication workflow
- Availability checking workflow
- Appointment creation workflow (with validation)
- Rate limiting and retry logic
- Error handling patterns
- Batch operations and pagination
- Real API integration (optional, requires credentials)

### Test Against Real API

```bash
# Set credentials
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key"

# Run integration tests against real API
./tests/run_tests.sh real
```

**See:** [tests/README.md](tests/README.md) for complete testing documentation

---

**See also:**
- [examples/README.md](examples/README.md) - Complete examples collection with cURL, JSON samples, and workflows
- [tests/README.md](tests/README.md) - Comprehensive test suite documentation
- [references/api-endpoints-reference.md](references/api-endpoints-reference.md) - Complete API documentation
- [references/authentication-guide.md](references/authentication-guide.md) - Authentication setup and security
- [references/workflows-reference.md](references/workflows-reference.md) - Proven workflow patterns
- [references/error-handling-guide.md](references/error-handling-guide.md) - Error handling strategies
- [references/webhook-integration-guide.md](references/webhook-integration-guide.md) - Webhook implementation guide
- [RISK_ASSESSMENT_AND_PITFALLS.md](All_APIs/API_Docs/Acuity_Scheduling_API/RISK_ASSESSMENT_AND_PITFALLS.md) - Critical pitfalls and prevention
