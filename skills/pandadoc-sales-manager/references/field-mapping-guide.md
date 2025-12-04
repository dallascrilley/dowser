# Field Mapping Guide

**Document Version:** 1.0
**Last Updated:** 2024-11-11

Complete guide to understanding and implementing field mapping in PandaDoc.

---

## Table of Contents

1. [Field Mapping Concepts](#field-mapping-concepts)
2. [Field Types](#field-types)
3. [Merge Fields](#merge-fields)
4. [Custom Fields](#custom-fields)
5. [Pre-filling Rules](#pre-filling-rules)
6. [Validation Rules](#validation-rules)
7. [Field Naming Conventions](#field-naming-conventions)
8. [Mapping Patterns](#mapping-patterns)
9. [Common Issues](#common-issues)

---

## Field Mapping Concepts

### What is Field Mapping?

Field mapping is the process of connecting your business data (CRM, database) to PandaDoc template fields. It transforms:

```
Your Data                  Template Fields
customer_name       ───→   "Company Name"
customer_email      ───→   "[Client.Email]"
proposal_amount     ───→   "Proposal Amount"
discount_percentage ───→   "Discount Percentage"
```

### Why Field Mapping?

1. **Template Independence** - Template fields don't change when your data structure changes
2. **Reusability** - One template can work with multiple data sources
3. **Validation** - Ensure data is correct before document creation
4. **Transformation** - Convert formats (phone numbers, dates, currency)
5. **Consistency** - Standardize how data appears in documents

### Two-Way Mapping

```
Business → Template (pre-filling)
Template → Business (extracting completed data)
```

---

## Field Types

### 1. Text Fields

Simple text that appears in document.

**Template Definition:**
```
Field Name: "Company Name"
Type: Text
```

**API Usage:**
```python
fields = {
    "Company Name": "Acme Corporation"
}
```

**Validation:**
```python
# Max length validation
if len(company_name) > 200:
    raise ValueError("Company name too long (max 200 characters)")
```

---

### 2. Signature Fields

Fields for electronic signatures. Recipients sign on these fields.

**Template Definition:**
```
Field Name: "Client Signature"
Type: Signature
Role: Client
```

**Special Handling:**
- PandaDoc automatically manages signature fields
- You don't pre-fill signature fields
- Leave empty in API request

```python
# Don't include signature fields in fields dict
fields = {
    "Company Name": "Acme",
    # No signature fields - PandaDoc handles these
}
```

---

### 3. Date Fields

Date values that appear in document.

**Template Definition:**
```
Field Name: "Effective Date"
Type: Date
Format: MM/DD/YYYY
```

**API Usage:**
```python
# Always use YYYY-MM-DD format in API
fields = {
    "Effective Date": "2024-01-15"  # Not 01/15/2024
}
```

**Conversion:**
```python
from datetime import datetime

# Convert any date format to API format
user_input = "01/15/2024"
parsed_date = datetime.strptime(user_input, "%m/%d/%Y")
api_date = parsed_date.strftime("%Y-%m-%d")  # "2024-01-15"

fields = {
    "Effective Date": api_date
}
```

---

### 4. Checkbox Fields

Boolean yes/no fields.

**Template Definition:**
```
Field Name: "Accepts Terms"
Type: Checkbox
```

**API Usage:**
```python
fields = {
    "Accepts Terms": "on"   # or "off", "true", "false", "1", "0"
}
```

---

### 5. Dropdown Fields

Selection from predefined options.

**Template Definition:**
```
Field Name: "Service Type"
Type: Dropdown
Options: ["Consulting", "Development", "Support"]
```

**API Usage:**
```python
# Must be exact match to template options
fields = {
    "Service Type": "Consulting"  # Exact case match required
}

# Validation
allowed_values = ["Consulting", "Development", "Support"]
if fields["Service Type"] not in allowed_values:
    raise ValueError("Invalid service type")
```

---

### 6. Numeric Fields

Numbers like quantities, percentages, etc.

**Template Definition:**
```
Field Name: "Discount Percentage"
Type: Numeric
Format: 0.00
```

**API Usage:**
```python
# Send as string or number
fields = {
    "Discount Percentage": "10",      # String
    # or
    "Discount Percentage": 10         # Number
}
```

---

### 7. Currency Fields

Money amounts.

**Template Definition:**
```
Field Name: "Proposal Amount"
Type: Currency
Format: $#,##0.00
```

**API Usage:**
```python
# Multiple formats accepted
fields = {
    "Proposal Amount": "$50,000.00",      # With symbol and commas
    # or
    "Proposal Amount": "50000.00",        # Just number
    # or
    "Proposal Amount": "$50000",          # Symbol without decimals
}
```

**Normalization:**
```python
def normalize_currency(value):
    """Convert any currency format to standard."""
    # Remove $ and commas
    cleaned = value.replace('$', '').replace(',', '')

    # Convert to float
    amount = float(cleaned)

    # Format as $X,XXX.XX
    return f"${amount:,.2f}"

# Example
print(normalize_currency("50000"))           # $50,000.00
print(normalize_currency("$50k"))            # Error - can't parse
```

---

## Merge Fields

### System Merge Fields

Pre-defined fields that PandaDoc automatically fills from your account.

**Common Merge Fields:**

| Field | Format | Description | Example |
|-------|--------|-------------|---------|
| `[Client.Name]` | Merge | Recipient's full name | John Doe |
| `[Client.Email]` | Merge | Recipient's email | john@acme.com |
| `[Client.Phone]` | Merge | Recipient's phone | 555-0123 |
| `[Client.Company]` | Merge | Recipient's company | Acme Corp |
| `[Client.Address]` | Merge | Recipient's address | 123 Main St |
| `[Company.Name]` | Merge | Your company name | My Company |
| `[Company.Phone]` | Merge | Your company phone | 555-0001 |
| `[Company.Address]` | Merge | Your company address | 456 Oak Ave |

### Using Merge Fields

**In Template:**
```
Customer: [Client.Name]
Email: [Client.Email]
Phone: [Client.Phone]
```

**In API Request:**

Merge fields pull from the recipient data:
```python
recipients = [
    {
        "email": "john@acme.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "555-0123",
        "company": "Acme Corp",
        "role": "Client"
    }
]

# PandaDoc automatically fills:
# [Client.Name] = "John Doe"
# [Client.Email] = "john@acme.com"
# [Client.Phone] = "555-0123"
# [Client.Company] = "Acme Corp"
```

### Custom Merge Fields

Define custom merge fields via tokens:

```python
payload = {
    "recipients": [...],
    "fields": {...},
    "tokens": [
        {
            "name": "SalesRep.Name",
            "value": "Jane Smith"
        },
        {
            "name": "SalesRep.Email",
            "value": "jane@company.com"
        },
        {
            "name": "Company.Address",
            "value": "123 Main St, Austin, TX 78701"
        }
    ]
}

# Template can now use:
# [SalesRep.Name] = "Jane Smith"
# [Company.Address] = "123 Main St, Austin, TX 78701"
```

---

## Custom Fields

### Creating Custom Fields in Templates

Custom fields are defined when creating the template in PandaDoc UI, not via API.

**Steps:**
1. In PandaDoc, create new template or edit existing
2. Add placeholders for custom fields:
   - Click on document
   - Select text to be replaced
   - Define as "Company Name", "Proposal Amount", etc.
3. Save template

**In API:**
```python
# Custom fields become available in your requests
fields = {
    "Company Name": "Acme Corp",
    "Proposal Amount": "$50,000",
    "Effective Date": "2024-01-15"
}
```

### Listing Template Fields

Get all available fields in a template:

```python
import requests

response = requests.get(
    'https://api.pandadoc.com/public/v1/templates/TEMPLATE_ID',
    headers={'Authorization': f'API-Key {API_KEY}'}
)

template = response.json()

print("Available fields:")
for field in template.get('fields', []):
    print(f"  - {field['name']} ({field.get('type', 'text')})")
```

---

## Pre-filling Rules

### Rule 1: Match Field Names Exactly

Field names are **case-sensitive**.

```python
# WRONG
fields = {
    "company name": "Acme",         # Should be "Company Name"
    "PROPOSAL AMOUNT": "$50,000",   # Should be "Proposal Amount"
}

# RIGHT
fields = {
    "Company Name": "Acme",
    "Proposal Amount": "$50,000"
}
```

### Rule 2: Use Correct Data Types

Send data in the format template expects.

```python
# String fields
fields = {
    "Company Name": "Acme Corp"  # String
}

# Date fields - always YYYY-MM-DD
fields = {
    "Effective Date": "2024-01-15"
}

# Currency - any format works, but be consistent
fields = {
    "Proposal Amount": "$50,000.00"
}

# Checkbox - "on" or "off"
fields = {
    "Accepts Terms": "on"
}
```

### Rule 3: Handle Special Characters

Escape special characters in field values:

```python
# Special characters in company names
fields = {
    "Company Name": "Smith & Associates, Inc."  # Ampersand and comma OK
}

# Quotes need escaping in JSON
fields = {
    "Notes": 'Client said "Not interested" today'  # Use single quotes
}

# Or escape in JSON
import json
json_data = json.dumps({
    "fields": {
        "Notes": 'Client said "Not interested"'
    }
})
```

### Rule 4: No Extra Whitespace

Trim leading/trailing whitespace:

```python
# WRONG
fields = {
    "Company Name": "  Acme Corp  "  # Extra spaces
}

# RIGHT
fields = {
    "Company Name": "Acme Corp".strip()
}

# Or define in mapping:
def clean_field_value(value):
    if isinstance(value, str):
        return value.strip()
    return value

cleaned_fields = {
    key: clean_field_value(val)
    for key, val in raw_fields.items()
}
```

### Rule 5: Empty vs. Null Values

Missing optional fields should be empty string or omitted:

```python
# If field is optional and not provided
fields = {
    "Required Field": "Value",
    "Optional Field": "",  # Empty string
    # Or just omit it entirely
}
```

---

## Validation Rules

### Standard Validation Patterns

| Field Type | Validation | Example |
|-----------|-----------|---------|
| Email | RFC 5322 pattern | `user@example.com` |
| Phone | US format or international | `+1-555-0123` |
| Date | YYYY-MM-DD | `2024-01-15` |
| Currency | Numeric with optional symbols | `$50,000.00` |
| Percentage | 0-100 | `10%` or `10` |
| URL | HTTP/HTTPS protocol | `https://example.com` |
| Postal Code | US ZIP or other | `78701` |

### Validation in Code

```python
import re
from datetime import datetime

def validate_field(field_name, field_value, field_type):
    """Validate field value against type rules."""

    if field_type == 'email':
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, field_value):
            raise ValueError(f"{field_name} must be valid email")

    elif field_type == 'date':
        try:
            datetime.strptime(field_value, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f"{field_name} must be YYYY-MM-DD format")

    elif field_type == 'currency':
        # Remove $ and commas, ensure numeric
        cleaned = field_value.replace('$', '').replace(',', '')
        try:
            float(cleaned)
        except ValueError:
            raise ValueError(f"{field_name} must be numeric")

    elif field_type == 'percentage':
        cleaned = field_value.replace('%', '')
        try:
            percent = float(cleaned)
            if percent < 0 or percent > 100:
                raise ValueError(f"{field_name} must be 0-100")
        except ValueError:
            raise ValueError(f"{field_name} must be numeric 0-100")

    return True

# Usage
validate_field("Effective Date", "2024-01-15", "date")
validate_field("Proposal Amount", "$50,000.00", "currency")
validate_field("Discount", "10%", "percentage")
```

---

## Field Naming Conventions

### Best Practices

1. **Use Descriptive Names**
   - Good: "Proposal Amount", "Effective Date"
   - Bad: "amt", "eff_date"

2. **Consistent Capitalization**
   - Use: "Title Case"
   - Example: "Company Name", "Proposal Amount", "Effective Date"

3. **Avoid Special Characters**
   - ✓ Allowed: Letters, numbers, spaces, periods, hyphens
   - ✗ Avoid: Underscores, pipes, brackets, etc.

4. **Keep Meaningful**
   - Use full words: "Company Name" not "Co Name"
   - Include units if necessary: "Monthly Fee (USD)" not "Monthly Fee"

### Example Naming Convention

```
Personal Information:
  - First Name
  - Last Name
  - Email Address
  - Phone Number

Company Information:
  - Company Name
  - Company Address
  - Company Phone

Proposal Details:
  - Proposal Amount
  - Effective Date
  - Expiration Date
  - Discount Percentage

Terms:
  - Payment Terms
  - Service Level
  - Support Hours
```

---

## Mapping Patterns

### Pattern 1: CRM to PandaDoc

Map CRM fields to template fields:

```python
# CRM data
crm_opportunity = {
    'account_name': 'Acme Corp',
    'annual_contract_value': 50000,
    'start_date': '2024-01-15',
    'discount_pct': 10
}

# Mapping configuration
crm_to_pandadoc = {
    'account_name': 'Company Name',
    'annual_contract_value': 'Proposal Amount',
    'start_date': 'Effective Date',
    'discount_pct': 'Discount Percentage'
}

# Transform data
fields = {}
for crm_field, template_field in crm_to_pandadoc.items():
    crm_value = crm_opportunity[crm_field]

    # Apply transformations
    if template_field == 'Proposal Amount':
        value = f"${crm_value:,.2f}"
    elif template_field == 'Effective Date':
        value = crm_value  # Already correct format
    elif template_field == 'Discount Percentage':
        value = f"{crm_value}%"
    else:
        value = str(crm_value)

    fields[template_field] = value

# Result
# {
#   'Company Name': 'Acme Corp',
#   'Proposal Amount': '$50,000.00',
#   'Effective Date': '2024-01-15',
#   'Discount Percentage': '10%'
# }
```

### Pattern 2: Database to PandaDoc

Map database columns to template fields:

```yaml
# config/field_mappings.yml
templates:
  sales_proposal:
    field_mappings:
      customers.company_name: "Company Name"
      customers.email: "[Client.Email]"
      opportunities.amount: "Proposal Amount"
      opportunities.created_date: "Effective Date"

transformations:
  opportunities.amount:
    type: currency
    decimals: 2
  opportunities.created_date:
    type: date
    format: "%Y-%m-%d"
```

### Pattern 3: Form to PandaDoc

Map web form fields to template fields:

```python
def map_form_to_document(form_data):
    """Convert form submission to document fields."""

    # Form submits with field names
    form_data = {
        'company': 'Acme Corp',
        'email': 'john@acme.com',
        'amount': '50000',
        'start_date': '2024-01-15'
    }

    # Define mapping
    mapping = {
        'company': 'Company Name',
        'email': '[Client.Email]',
        'amount': 'Proposal Amount',
        'start_date': 'Effective Date'
    }

    # Transform
    fields = {}
    for form_field, template_field in mapping.items():
        value = form_data.get(form_field)

        if not value:
            continue

        # Format value
        if 'amount' in form_field.lower():
            value = f"${float(value):,.2f}"

        fields[template_field] = value

    return fields
```

---

## Common Issues

### Issue: Field Name Mismatch

**Problem:**
```
Template has: "Company Name"
Code sends: "company_name" or "Company name"
Result: Field not filled
```

**Solution:**
```python
# Use exact field names from template
response = requests.get(
    'https://api.pandadoc.com/public/v1/templates/TEMPLATE_ID',
    headers={'Authorization': f'API-Key {API_KEY}'}
)
template = response.json()

# Get exact field names
print("Template fields:")
for field in template['fields']:
    print(f"  '{field['name']}'")  # Use with quotes

# Map your fields to these exact names
fields = {
    "Company Name": value,  # Match exactly
}
```

### Issue: Date Format Wrong

**Problem:**
```
Template expects: 2024-01-15
Code sends: 01/15/2024
Result: Unpredictable formatting or error
```

**Solution:**
```python
from datetime import datetime

def ensure_date_format(date_value):
    """Convert any date format to YYYY-MM-DD."""

    # If already correct format
    if isinstance(date_value, str) and len(date_value) == 10:
        return date_value

    # Try parsing various formats
    formats = [
        '%m/%d/%Y',     # 01/15/2024
        '%m-%d-%Y',     # 01-15-2024
        '%d/%m/%Y',     # 15/01/2024
        '%Y-%m-%d',     # 2024-01-15
        '%B %d, %Y',    # January 15, 2024
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(str(date_value), fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue

    raise ValueError(f"Cannot parse date: {date_value}")

# Usage
field_value = ensure_date_format('01/15/2024')  # Returns: '2024-01-15'
```

### Issue: Currency Format Issues

**Problem:**
```
Template shows: $50,000
Code sent: 50000
Result: Shows as "50000" without formatting
```

**Solution:**
```python
def format_currency(value):
    """Ensure consistent currency formatting."""

    # Remove all non-numeric except decimal
    import re
    cleaned = re.sub(r'[^0-9.]', '', str(value))

    # Convert to float
    amount = float(cleaned)

    # Format with $ and thousands separator
    return f"${amount:,.2f}"

# Usage
print(format_currency("50000"))      # $50,000.00
print(format_currency("50,000.00"))  # $50,000.00
print(format_currency("$50k"))       # $50,000.00
```

### Issue: Merge Field Not Working

**Problem:**
```
Template has: [Client.Email]
Recipient provided but field shows empty
Result: Blank field in document
```

**Solution:**
```python
# Verify merge field is spelled correctly (case-sensitive)
# Template: [Client.Email] - capital C and E
recipients = [
    {
        "email": "john@acme.com",      # Email address for merge field
        "first_name": "John",
        "last_name": "Doe",
        "role": "Client"
    }
]

# Check that you provided the recipient
# [Client.Email] will be filled from recipient.email
```

---

## Field Mapping Configuration File

**Example: template_mappings.yml**

```yaml
templates:
  sales_proposal:
    uuid: "abc123-def456-ghi789"
    field_mappings:
      customer_name: "Company Name"
      customer_email: "[Client.Email]"
      proposal_amount: "Proposal Amount"
      effective_date: "Effective Date"
      discount_percent: "Discount Percentage"

    transformations:
      proposal_amount:
        format: currency
        decimals: 2
      effective_date:
        format: date
        input_format: "%m/%d/%Y"
        output_format: "%Y-%m-%d"
      discount_percent:
        format: percentage
        add_percent_sign: true

    validation:
      proposal_amount:
        min: 0.01
        max: 999999999
      discount_percent:
        min: 0
        max: 100
```

---

## See Also

- [Endpoints Reference](./endpoints-reference.md)
- [Field Validation Configuration](../templates/field_validation.yml)
- [Template Mappings Configuration](../templates/template_mappings.yml)
