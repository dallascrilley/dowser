# ConnectWise CLI Error Solutions

Quick reference for troubleshooting common errors.

## Configuration Errors

### "Command not found: connectwise-cli"

**Solution:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Verify installation
pip show connectwise-cli
```

### "Configuration Error: Missing required environment variables"

**Solution:**
```bash
# Option 1: Run config wizard
cw config init

# Option 2: Check existing config
cw config show
cw config path

# Option 3: Set environment variables
export CONNECTWISE_API_BASE_URL=https://api-na.myconnectwise.net
export CONNECTWISE_COMPANY_ID=yourcompany
export CONNECTWISE_PUBLIC_KEY=your_key
export CONNECTWISE_PRIVATE_KEY=your_secret
export CONNECTWISE_CLIENT_ID=your_client_id
```

## Authentication Errors

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

**Cause:** Authenticated but not authorized

**Solution:**
- Check member permissions in ConnectWise (System > Members > Security)
- Verify API member has proper security roles
- Contact administrator for elevated permissions

## API Errors

### "404 Not Found"

**Cause:** Resource doesn't exist or wrong endpoint

**Solution:**
```bash
# Verify resource exists
cw agreements list --limit 10

# Check API configuration
cw config show

# Test with known resource
cw agreements list --limit 1
```

### "422 Unprocessable Entity"

**Cause:** Invalid filter syntax

**Solution:**
```bash
# Check date format (must have brackets)
# Correct: "startDate>[2025-01-01]"
# Wrong:   "startDate>2025-01-01"

# Use debug mode to see full error
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

# Use larger page sizes to reduce requests
cw agreements list --limit 100
```

## Connection Errors

### "Connection timeout"

**Solution:**
```bash
# Increase timeout in ~/.connectwiserc
timeout: 60.0  # seconds

# Test network
ping api-na.myconnectwise.net

# Use smaller page sizes
cw agreements list --limit 10
```

### "SSL Certificate Verification Failed"

**Solution:**
```bash
# macOS
brew install ca-certificates

# Ubuntu
sudo apt-get update && sudo apt-get install ca-certificates

# Check system time
date
```

## Data Errors

### "No results found"

**Solution:**
```bash
# Test without filters
cw agreements list --limit 5

# Check filter syntax with debug
cw --debug agreements list --conditions "your filter"

# View sample data to verify field names
cw agreements list --format json --limit 1
```

## Filter Syntax Errors

### Date format errors

```bash
# WRONG: Missing brackets
--conditions "startDate>2025-01-01"

# CORRECT: Dates in [YYYY-MM-DD] format
--conditions "startDate>[2025-01-01]"
```

### Quote escaping

```bash
# Use double quotes for conditions
cw agreements list --conditions "agreementStatus='Active'"

# Complex conditions
cw agreements list --conditions "company/id=250 AND (status='Active' OR status='Pending')"
```

## Quick Diagnostics

```bash
# Check version
cw --version

# Test connection
cw config test

# Show configuration (credentials masked)
cw config show

# Debug mode
cw --debug agreements list --limit 1

# Collect logs
cw --debug [your command] 2>&1 | tee debug.log
```

## Base URL by Region

- **North America**: `https://api-na.myconnectwise.net`
- **Europe**: `https://api-eu.myconnectwise.net`
- **Australia**: `https://api-aus.myconnectwise.net`

## Configuration File Location

Default: `~/.connectwiserc`

```yaml
api_base_url: https://api-na.myconnectwise.net
api_version: v2025_1
company_id: yourcompany
public_key: your_public_key
private_key: your_private_key
client_id: your_client_id
timeout: 30.0
```
