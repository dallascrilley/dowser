# Acuity Schedule Manager - Examples

Complete collection of examples to help you get started with the Acuity Scheduling API.

## Example Files

### 1. Sample Appointment Data

**`sample_appointment.json`** - Single appointment creation example
```bash
# Create appointment using sample data
python scripts/create_appointment.py --file examples/sample_appointment.json
```

**Fields included:**
- `appointmentTypeID` - Required: The service type ID
- `datetime` - Required: ISO 8601 format with timezone
- `firstName`, `lastName`, `email` - Required: Client information
- `phone` - Client phone number
- `timezone` - Client's timezone
- `fields` - Custom form fields
- `notes` - Appointment notes

### 2. Batch Appointment Data

**`sample_appointment_batch.json`** - Multiple appointments for batch processing
```bash
# Process batch appointments
for appointment in $(jq -c '.[]' examples/sample_appointment_batch.json); do
  echo "$appointment" | python scripts/create_appointment.py --file -
  sleep 0.2  # Rate limiting
done
```

**Use cases:**
- Bulk import from external system
- Scheduled batch booking
- Testing appointment creation workflow

### 3. CRM Sync Configuration

**`sample_sync_config.yml`** - Complete CRM synchronization configuration

**Quick start:**
```bash
# Copy and customize
cp examples/sample_sync_config.yml sync_config.yml

# Edit with your CRM settings
nano sync_config.yml

# Run sync
python scripts/sync_clients.py --config sync_config.yml --since yesterday
```

**Key sections:**
- **Sync Direction:** One-way or bidirectional sync
- **Field Mapping:** Map Acuity fields to your CRM
- **Transformations:** Phone/email/date formatting
- **Filters:** Which appointments to sync
- **Error Handling:** Retry logic and alerting
- **Performance:** Batch size and rate limiting

**Supported CRMs:**
- Salesforce
- HubSpot
- Pipedrive
- Custom (via webhook)

### 4. cURL Examples

**`curl_examples.sh`** - Complete collection of API calls using cURL

**Run all examples:**
```bash
# Set credentials first
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key_here"

# Run examples
./examples/curl_examples.sh
```

**Includes examples for:**
1. Authentication testing (`GET /me`)
2. List appointment types
3. List calendars
4. Check availability
5. Get available times
6. List appointments
7. Create appointment
8. Get specific appointment
9. Update appointment
10. Cancel appointment
11. Reschedule appointment
12. List clients
13. Search client by email
14. Create client
15. Get intake forms
16. Get time blocks
17. Rate limit headers
18. Error handling (404)
19. Error handling (401)

**Requirements:**
- `curl` (pre-installed on macOS/Linux)
- `jq` for JSON formatting (optional but recommended)
  ```bash
  brew install jq  # macOS
  apt-get install jq  # Linux
  ```

## Common Workflows Using Examples

### Workflow 1: Test Your Integration

```bash
# 1. Set credentials
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key_here"

# 2. Validate credentials
python scripts/validate_credentials.py

# 3. Run cURL examples to explore API
./examples/curl_examples.sh

# 4. Try creating a test appointment
python scripts/create_appointment.py --file examples/sample_appointment.json
```

### Workflow 2: Set Up CRM Sync

```bash
# 1. Copy sample config
cp examples/sample_sync_config.yml config/sync_config.yml

# 2. Edit with your CRM details
nano config/sync_config.yml

# 3. Test with dry-run
python scripts/sync_clients.py --config config/sync_config.yml --since yesterday --dry-run

# 4. Run actual sync
python scripts/sync_clients.py --config config/sync_config.yml --since yesterday
```

### Workflow 3: Batch Import Appointments

```bash
# 1. Prepare your data (use sample as template)
cp examples/sample_appointment_batch.json data/appointments_to_import.json

# 2. Edit with your appointment data
nano data/appointments_to_import.json

# 3. Import with error handling
for appointment in $(jq -c '.[]' data/appointments_to_import.json); do
  echo "$appointment" | python scripts/create_appointment.py --file - || echo "Failed to create appointment"
  sleep 0.2  # Rate limiting
done
```

### Workflow 4: Explore API with cURL

```bash
# Quick API exploration
export ACUITY_USER_ID="12345678"
export ACUITY_API_KEY="your_api_key_here"

# Get your appointment types
curl -s -u ${ACUITY_USER_ID}:${ACUITY_API_KEY} \
  "https://acuityscheduling.com/api/v1/appointment-types" | jq '.'

# Check availability for tomorrow
TOMORROW=$(date -v+1d +%Y-%m-%d)
curl -s -u ${ACUITY_USER_ID}:${ACUITY_API_KEY} \
  "https://acuityscheduling.com/api/v1/availability/times?appointmentTypeID=12345&date=${TOMORROW}" | jq '.'
```

## Customizing Examples

### Modify Sample Appointment

Edit `sample_appointment.json` with your specific values:

```json
{
  "appointmentTypeID": 12345,  // ← Replace with your appointment type ID
  "datetime": "2025-11-15T14:00:00-0500",  // ← Adjust date/time/timezone
  "firstName": "John",  // ← Your client's info
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-123-4567"
}
```

### Customize CRM Sync

Key sections to modify in `sample_sync_config.yml`:

**1. Field Mapping:**
```yaml
field_mapping:
  client:
    email: email  // ← Map to your CRM field names
    firstName: first_name
    lastName: last_name
```

**2. Filters:**
```yaml
filters:
  appointment_types:
    include: [12345, 12346]  // ← Your appointment type IDs
```

**3. CRM Settings:**
```yaml
crm:
  type: salesforce  // ← Your CRM type
  credentials:
    api_key_env_var: CRM_API_KEY
```

### Add Custom cURL Examples

Edit `curl_examples.sh` to add your own examples:

```bash
# Add at the end of the file
echo "20. My Custom Example"
echo "---------------------"
curl -s -u ${USER_ID}:${API_KEY} \
  "${BASE_URL}/your-custom-endpoint" | jq '.'
```

## Troubleshooting Examples

### Issue: "Invalid appointment type"
```bash
# List your actual appointment types
curl -s -u ${USER_ID}:${API_KEY} \
  "https://acuityscheduling.com/api/v1/appointment-types" | jq '.[] | {id, name}'

# Update sample_appointment.json with correct ID
```

### Issue: "Invalid datetime format"
```bash
# Check your timezone format
python -c "import pytz; print(pytz.all_timezones)" | grep New_York

# Ensure datetime includes timezone:
# Correct: "2025-11-15T14:00:00-0500"
# Wrong: "2025-11-15 14:00:00"
```

### Issue: "401 Unauthorized"
```bash
# Verify credentials
python scripts/validate_credentials.py

# Check environment variables
echo "User ID: ${ACUITY_USER_ID}"
echo "API Key: ${ACUITY_API_KEY:0:4}****${ACUITY_API_KEY: -4}"
```

## Best Practices

**1. Start with cURL examples** to understand the API
**2. Use sample_appointment.json** as a template for your data
**3. Test with dry-run** before actual CRM sync
**4. Validate data** before batch imports
**5. Implement rate limiting** (0.1s delay between requests)
**6. Log all operations** for debugging
**7. Use environment variables** for credentials

## See Also

- [scripts/README.md](../scripts/README.md) - Helper scripts documentation
- [references/workflows-reference.md](../references/workflows-reference.md) - Complete workflow patterns
- [references/api-endpoints-reference.md](../references/api-endpoints-reference.md) - Full API reference
- [SKILL.md](../SKILL.md) - Main skill documentation
