# Bulk Import Implementation Guide

This guide provides detailed information about the Copper CRM bulk import helper architecture and implementation.

## Architecture Overview

```
bulk_import.py
├── Dataclasses (ImportRecord, ImportResult)
├── CopperCRMClient (API interactions)
├── BulkImporter (orchestration)
└── CLI (argparse + main)
```

## Core Components

### 1. Data Models

#### ImportRecord
```python
@dataclass
class ImportRecord:
    row_num: int              # CSV row number for error reporting
    data: Dict[str, Any]      # Normalized record data
    entity_type: str          # Type: leads, people, companies, opportunities
    errors: List[str]         # Validation errors (if any)
```

#### ImportResult
```python
@dataclass
class ImportResult:
    row_num: int              # CSV row number
    success: bool             # Whether import succeeded
    record_id: Optional[str]  # ID of created/updated record
    is_duplicate: bool        # True if updated existing record
    error_message: Optional[str]
    retry_count: int          # Number of retry attempts made
```

### 2. CopperCRMClient

Handles all API interactions with Copper CRM.

#### Key Methods

- `find_duplicate(entity_type, record)` - Search for existing record
  - Leads: By email
  - People: By email
  - Companies: By name
  - Opportunities: By name

- `upsert_record(entity_type, record, duplicate_id)` - Create or update
  - PUT if duplicate_id provided
  - POST if new record

- `_rate_limit()` - Enforce 3 req/sec rate limiting

#### Rate Limiting

```python
def _rate_limit(self):
    elapsed = time.time() - self.last_request_time
    min_interval = 1.0 / RATE_LIMIT  # 0.333 seconds
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
```

### 3. BulkImporter

Main orchestration class for the import process.

#### Workflow

1. **Load Records** - Read CSV file
2. **Validate Headers** - Check required columns exist
3. **Validate Data** - Per-record validation
4. **Batch Processing** - Import in batches of 10
5. **Error Recovery** - Retry failed records up to 3x
6. **Reporting** - Generate summary report

#### Validation Logic

- **Required Fields**: Check all required fields present and non-empty
- **Format Validation**:
  - Emails: Must contain "@"
  - Monetary Values: Must be numeric
- **Entity-Specific**: Extensible per entity type

#### Batch Processing

```
Records: [1, 2, 3, ..., 100]
         ↓
Batch 1: [1-10]  → Import with rate limiting
         ↓
Batch 2: [11-20] → Import with rate limiting
         ↓
...
Batch 10: [91-100] → Import with rate limiting
          ↓
         Report
```

### 4. Error Recovery Strategy

Three-tier retry approach:

1. **First Attempt**: Full process (find duplicate + upsert)
2. **Second Attempt**: Wait 2 seconds, retry
3. **Third Attempt**: Wait 2 seconds, final attempt
4. **Failure**: Record error message and continue

Result tracking:
- Success count
- Failed records list with error messages
- Duplicate update count
- Success rate calculation

## CSV Format Details

### Header Auto-detection

- Case-insensitive (normalized to lowercase)
- Whitespace trimmed
- Order doesn't matter
- Extra columns ignored

### Data Normalization

Each row is normalized:
```python
normalized_row = {
    k.lower(): v.strip() if v else ""
    for k, v in row.items()
}
```

### Entity-Type Specific Fields

#### Leads CSV
```
name       | Required | String
email      | Required | Email format
company_name | Required | String
title      | Required | String
phone      | Required | String
```

#### People CSV
```
name       | Required | String
email      | Required | Email format
company_name | Required | String
title      | Required | String
```

#### Companies CSV
```
name       | Required | String
email_domain | Required | String (domain format)
address    | Required | String
```

#### Opportunities CSV
```
name       | Required | String
primary_contact_email | Required | Email format
monetary_value | Required | Numeric (float/int)
```

## API Integration

### Endpoints Used

```
POST   /leads/search              - Find lead by email
POST   /people/search             - Find person by email
POST   /companies/search          - Find company by name
POST   /opportunities/search      - Find opportunity by name

POST   /leads                     - Create lead
POST   /people                    - Create person
POST   /companies                 - Create company
POST   /opportunities             - Create opportunity

PUT    /leads/{id}                - Update lead
PUT    /people/{id}               - Update person
PUT    /companies/{id}            - Update company
PUT    /opportunities/{id}        - Update opportunity
```

### Authentication

Header-based API key authentication:
```
X-PB-API-KEY: <api_key>
Content-Type: application/json
```

### Response Handling

Success (200/201):
```json
{
  "id": "12345",
  "name": "John Smith",
  ...
}
```

Error:
```json
{
  "error": {
    "message": "Invalid email format"
  }
}
```

## Performance Characteristics

### Speed

- Batch Size: 10 records
- Rate Limit: 3 requests/second = ~300 ms per request
- Per Record: ~400-500ms (including duplicate check + import)
- Throughput: ~100-150 records/minute

### Memory

- Stream processing (no full file load in memory)
- Memory usage: O(batch_size) = ~10 records
- CSV row count: ~1000 = ~10 batches = 3-4 minutes

### API Limits

- 3 req/second hardcoded
- Easily adjustable in constants
- Account for duplicate search (1 req) + import (1 req) per record

## Extensibility

### Adding New Entity Types

1. Add headers to `ENTITY_HEADERS` dict:
```python
ENTITY_HEADERS = {
    "new_type": ["field1", "field2", "field3"],
}
```

2. Add validation method:
```python
def _validate_new_type(self, record: ImportRecord):
    # Custom validation logic
    pass
```

3. Add duplicate search method in `CopperCRMClient`:
```python
def _find_new_type(self, key: str) -> Optional[str]:
    status, response = self._make_request("POST", "/new_type/search", {...})
    # Extract ID
    return id
```

4. Update `find_duplicate()` method to handle new type

### Customizing Validation

Extend `_validate_record()` to add stricter rules:
```python
def _validate_record(self, record: ImportRecord):
    # Call parent validation
    super()._validate_record(record)

    # Add custom rules
    if record.data.get("field") == "invalid":
        record.errors.append("Custom validation error")
```

### Adjusting Rate Limiting

Change `RATE_LIMIT` constant:
```python
RATE_LIMIT = 5  # 5 requests per second
```

Change `BATCH_SIZE`:
```python
BATCH_SIZE = 20  # 20 records per batch
```

Change retry behavior:
```python
MAX_RETRIES = 5  # 5 attempts
RETRY_DELAY = 1  # 1 second between retries
```

## Error Messages

### CSV Errors

- "File not found: <path>" - CSV file doesn't exist
- "Missing required columns: <columns>" - Required headers missing
- "Error reading CSV: <error>" - CSV parsing error

### Validation Errors

- "Missing required field: <field>" - Required field empty
- "Invalid email format: <email>" - Email missing @
- "Invalid monetary_value: <value>" - Non-numeric value

### API Errors

- Returned from Copper API
- Includes specific reason from API
- Recorded in ImportResult.error_message

## Testing

### Manual Testing

1. Create test CSV with valid data
2. Set up test Copper CRM account
3. Export API key
4. Run import with small batch
5. Verify in Copper CRM interface

### Test Cases

- Valid CSV with all required fields
- CSV with missing headers
- CSV with empty values
- CSV with invalid email formats
- CSV with duplicate records (test UPSERT)
- Large CSV (1000+ records)
- Network errors during import
- Invalid API key

### Example Test Run

```bash
# Create test CSV
cat > test.csv << 'EOF'
name,email,company_name,title,phone
Test Lead,test@example.com,Test Co,Sales,555-0001
EOF

# Set API key
export COPPER_API_KEY="test-key-123"

# Run import
python bulk_import.py leads test.csv --mode upsert

# Expected output:
# Loading CSV file: test.csv
# Loaded 1 records
# Importing 1 records... 100%
# ============================================================
# Import Summary Report
# ...
```

## Debugging

### Enable Verbose Logging

Add to CopperCRMClient:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In _make_request:
logger.debug(f"Request: {method} {url}")
logger.debug(f"Response: {status} {response}")
```

### Common Issues

1. **"Invalid API key"**
   - Verify key format
   - Check Copper API documentation
   - Test with curl first

2. **"Rate limit exceeded"**
   - Reduce RATE_LIMIT constant
   - Check if other processes using same key

3. **"Duplicate detection not working"**
   - Verify search endpoints available
   - Check data format matches expectations

4. **"CSV headers not recognized"**
   - Check for extra spaces in headers
   - Verify column names match exactly
   - Check CSV encoding (UTF-8)

## Production Deployment

### Pre-deployment Checklist

- [ ] Test with production API key (on test data)
- [ ] Verify all required fields handled
- [ ] Check batch size appropriate for data volume
- [ ] Review error recovery strategy
- [ ] Plan rollback procedure
- [ ] Monitor API rate limits
- [ ] Set up logging/monitoring

### Recommended Practices

1. **Backup**: Always backup Copper data before large imports
2. **Test Run**: Import small sample first (10-20 records)
3. **Validation**: Review generated report carefully
4. **Monitoring**: Watch for failed records during import
5. **Rate Limit**: Start conservative, increase as needed
6. **Logging**: Keep detailed logs of all imports

### High-Volume Imports

For 10,000+ records:
1. Split into multiple CSV files
2. Run imports sequentially
3. Increase retry delay to reduce API load
4. Consider scheduling off-peak times
5. Monitor API response times

## Performance Optimization

### For Large Datasets

1. **Reduce Duplicate Searches**
   - Use `--mode create` if no existing records
   - Saves 1 API call per record

2. **Increase Batch Size** (if API allows)
   ```python
   BATCH_SIZE = 25
   ```

3. **Adjust Rate Limit** (test carefully)
   ```python
   RATE_LIMIT = 5  # 5 req/sec
   ```

4. **Parallel Processing** (future enhancement)
   - Use ThreadPoolExecutor for rate-limited batches
   - Maintain thread-safe result list

### For Network Constraints

1. **Increase Retry Delay**
   ```python
   RETRY_DELAY = 5
   ```

2. **Reduce Batch Size**
   ```python
   BATCH_SIZE = 5
   ```

3. **Reduce Rate Limit**
   ```python
   RATE_LIMIT = 1  # 1 req/sec
   ```

## Future Enhancements

Potential improvements:
1. Async API calls for parallel processing
2. Custom field mapping (CSV column → API field)
3. Data transformation pipeline (normalize phone, addresses)
4. Webhook integration for notifications
5. Scheduled imports via cron
6. REST API wrapper for import functionality
7. Web UI for drag-and-drop CSV import
8. Database backend for import history
9. Advanced duplicate detection (fuzzy matching)
10. Rollback functionality for failed imports
