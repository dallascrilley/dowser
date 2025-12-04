# ConnectWise Filter Patterns

Reference for ConnectWise `--conditions` filter syntax.

## Basic Syntax

```bash
cw <resource> list --conditions "field operator value"
```

## Operators

### Comparison
- `=` - Equal to
- `!=` - Not equal to
- `>` - Greater than
- `>=` - Greater than or equal
- `<` - Less than
- `<=` - Less than or equal

### Text
- `contains` - Contains substring (case-insensitive)
- `like` - Wildcard match (`*` for multiple chars, `?` for single char)

### Logical
- `AND` - Both conditions true
- `OR` - At least one condition true
- `NOT` - Negate condition
- `in (val1,val2,val3)` - Value in list

## Field References

### Direct Fields
```bash
--conditions "name='Acme Corporation'"
--conditions "status='Active'"
--conditions "total>1000"
```

### Related Fields (Lookups)
```bash
--conditions "company/id=250"
--conditions "company/name='Acme Corp'"
--conditions "agreement/id=161"
--conditions "category/id=15"
```

### Nested Related Fields
```bash
--conditions "company/status/id=1"
--conditions "company/types/id=5"
```

## Date Filters

**Format:** `[YYYY-MM-DD]` (brackets required!)

```bash
# Exact date
--conditions "startDate=[2025-01-01]"

# After date
--conditions "startDate>[2025-01-01]"

# On or after
--conditions "startDate>=[2025-01-01]"

# Before date
--conditions "endDate<[2025-12-31]"

# Date range
--conditions "invoiceDate>=[2025-01-01] AND invoiceDate<=[2025-01-31]"

# Null checks
--conditions "cancelledDate=null"
--conditions "endDate!=null"
```

## Common Patterns

### Active Records
```bash
# Agreements
--conditions "agreementStatus='Active'"

# Companies
--conditions "status/id=1"

# Products
--conditions "inactiveFlag=false"
```

### By Company
```bash
--conditions "company/id=250"
--conditions "company/name='Acme Corp'"
```

### Text Search
```bash
# Contains (case-insensitive)
--conditions "name contains 'Tech'"

# Starts with
--conditions "name like 'Acme*'"

# Ends with
--conditions "name like '*Corp'"

# Multiple terms
--conditions "description contains 'Server' OR description contains 'Hosting'"
```

### Amount Ranges
```bash
# Greater than
--conditions "total>1000"

# Range
--conditions "price>=10 AND price<=100"

# High value
--conditions "billAmount>5000"
```

### Multiple Conditions
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

## Resource-Specific Patterns

### Agreements
```bash
# Expiring soon (next 60 days)
--conditions "endDate<=[DATE] AND agreementStatus='Active'"

# By type
--conditions "type/id=10"

# By billing terms
--conditions "billingTerms/id=5"

# High-value monthly agreements
--conditions "billAmount>5000 AND billingCycle='Monthly'"
```

### Invoices
```bash
# Unpaid
--conditions "status/id=1"

# Overdue
--conditions "dueDate<[TODAY] AND status/id=1"

# By agreement
--conditions "agreement/id=161"

# This month
--conditions "invoiceDate>=[2025-01-01] AND invoiceDate<=[2025-01-31]"
```

### Companies
```bash
# By name search
--conditions "name contains 'Tech'"

# By territory
--conditions "territory/id=10"

# By type
--conditions "types/id=5"

# Has website
--conditions "website!=null"

# By state
--conditions "state='CA'"
```

### Catalog
```bash
# By category
--conditions "category/id=15"

# Price range
--conditions "price>=10 AND price<=100"

# Taxable items
--conditions "taxableFlag=true"

# By type
--conditions "type='Service'"

# Active products
--conditions "inactiveFlag=false"
```

## Performance Tips

### Use Indexed Fields (Fast)
- `id` (primary key)
- Status fields (`status/id`, `agreementStatus`)
- Foreign keys (`company/id`, `agreement/id`)
- Dates (`invoiceDate`, `startDate`, `endDate`)

### Avoid When Possible (Slower)
- Text search (`name contains`)
- Nested lookups beyond 2 levels
- Complex OR conditions without AND

### Best Practices
```bash
# GOOD: Filter on server, small result set
cw agreements list --conditions "company/id=250 AND agreementStatus='Active'"

# BAD: Get all data, filter client-side
cw agreements list --format json | jq '.[] | select(.company.id == 250)'

# GOOD: Use --limit for large result sets
cw agreements list --limit 100

# GOOD: Paginate for very large exports
cw agreements list --page 1 --limit 100
```

## Escaping Special Characters

```bash
# Use double quotes for conditions
cw agreements list --conditions "name contains 'Tech'"

# Single quote in value
--conditions "name='O'Reilly Media'"

# Complex nested conditions
--conditions "(status='Active' OR status='Pending') AND company/id in (250,251)"
```
