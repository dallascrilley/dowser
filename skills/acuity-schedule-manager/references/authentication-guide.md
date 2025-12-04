# Acuity Scheduling API - Authentication Setup Guide

**Last Updated:** 2025-11-11
**Difficulty Level:** Beginner
**Time to Complete:** 10-15 minutes

---

## Table of Contents

1. [Getting Credentials](#getting-credentials)
2. [Environment Setup](#environment-setup)
3. [Testing Authentication](#testing-authentication)
4. [Code Examples](#code-examples)
5. [Security Best Practices](#security-best-practices)
6. [Credential Rotation](#credential-rotation)
7. [Troubleshooting](#troubleshooting)

---

## Getting Credentials

### Step 1: Log into Acuity Dashboard

1. Go to [acuityscheduling.com](https://acuityscheduling.com)
2. Click "Log In" and enter your credentials
3. You should see your appointment calendar

### Step 2: Navigate to API Settings

1. Click **"Settings"** in the top left corner
2. Select **"Integrations"** from the menu
3. Click **"API"** (or "Developer API")

### Step 3: Get Your Credentials

You'll see:

- **User ID** - A numeric identifier (e.g., `12345678`)
- **API Key** - An alphanumeric string (e.g., `abc123def456xyz789`)

**Important:** You may see multiple API keys if you've created them before. Use the one you're currently using.

### Step 4: Generate New Key (if needed)

If you need a new API key:

1. Click **"Generate New Key"** or **"Create API Key"**
2. Accept the confirmation
3. The new key will appear in the interface
4. Copy it immediately (you won't see it again)

---

## Environment Setup

### For Development

Create a `.env` file in your project root:

```bash
# Create .env file
echo "ACUITY_USER_ID=12345678" > .env
echo "ACUITY_API_KEY=abc123def456xyz789" >> .env
```

**Never commit `.env` to version control!**

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
credentials/
secrets/
```

### For Production

**Use a secure secrets management system:**

#### AWS Secrets Manager
```python
import boto3

client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='acuity/production')
credentials = json.loads(secret['SecretString'])
user_id = credentials['user_id']
api_key = credentials['api_key']
```

#### Environment Variables (Heroku, etc.)
```bash
heroku config:set ACUITY_USER_ID=12345678
heroku config:set ACUITY_API_KEY=abc123def456xyz789
```

#### Docker Secrets
```yaml
version: '3.9'
services:
  app:
    environment:
      ACUITY_USER_ID_FILE: /run/secrets/acuity_user_id
      ACUITY_API_KEY_FILE: /run/secrets/acuity_api_key
secrets:
  acuity_user_id:
    external: true
  acuity_api_key:
    external: true
```

### Environment-Specific Configuration

Create separate `.env` files:

```
.env                          # Default (development)
.env.development              # Development overrides
.env.staging                  # Staging environment
.env.production               # Production environment
```

Load in order:
```bash
set -a
source .env
source .env.$ENVIRONMENT
set +a
```

---

## Testing Authentication

### Quick Test: Get Account Info

The `/me` endpoint returns account information and requires valid auth.

**Bash:**
```bash
curl -u "12345678:abc123def456xyz789" \
  https://acuityscheduling.com/api/v1/me
```

**Expected Response (200 OK):**
```json
{
  "id": "12345678",
  "name": "John Smith",
  "email": "john@yourdomain.com",
  "timezone": "America/New_York",
  "businessName": "Smith Consulting"
}
```

**On Failure (401 Unauthorized):**
```json
{
  "status_code": 401,
  "error": "Unauthorized",
  "message": "Invalid credentials"
}
```

### Python Test Script

```python
#!/usr/bin/env python3
"""Test Acuity API authentication"""

import os
import requests
from requests.auth import HTTPBasicAuth

def test_authentication():
    """Test API credentials"""
    user_id = os.getenv('ACUITY_USER_ID')
    api_key = os.getenv('ACUITY_API_KEY')

    if not user_id or not api_key:
        print("❌ Missing credentials")
        print("   Set ACUITY_USER_ID and ACUITY_API_KEY")
        return False

    try:
        response = requests.get(
            'https://acuityscheduling.com/api/v1/me',
            auth=HTTPBasicAuth(user_id, api_key),
            timeout=10
        )

        if response.status_code == 200:
            account = response.json()
            print("✅ Authentication successful!")
            print(f"   User ID: {account['id']}")
            print(f"   Name: {account['name']}")
            print(f"   Email: {account['email']}")
            print(f"   Timezone: {account['timezone']}")
            return True

        elif response.status_code == 401:
            print("❌ Authentication failed")
            print("   Check User ID and API Key")
            return False

        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"   {response.json()}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == '__main__':
    import sys
    sys.exit(0 if test_authentication() else 1)
```

Run the test:
```bash
python test_auth.py
```

---

## Code Examples

### Python with Requests

```python
import os
import requests
from requests.auth import HTTPBasicAuth

# Load credentials from environment
USER_ID = os.getenv('ACUITY_USER_ID')
API_KEY = os.getenv('ACUITY_API_KEY')
BASE_URL = "https://acuityscheduling.com/api/v1"

# Create session with auth
session = requests.Session()
session.auth = HTTPBasicAuth(USER_ID, API_KEY)
session.headers.update({
    'Content-Type': 'application/json',
    'User-Agent': 'MyApp/1.0'
})

# Make authenticated request
response = session.get(f"{BASE_URL}/appointment-types")
appointment_types = response.json()

for apt_type in appointment_types:
    print(f"{apt_type['name']}: ${apt_type['price']}")
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');
const Buffer = require('buffer').Buffer;

const USER_ID = process.env.ACUITY_USER_ID;
const API_KEY = process.env.ACUITY_API_KEY;
const BASE_URL = "https://acuityscheduling.com/api/v1";

// Create Basic Auth header
const credentials = Buffer.from(`${USER_ID}:${API_KEY}`).toString('base64');
const authHeader = `Basic ${credentials}`;

// Make authenticated request
async function getAppointmentTypes() {
  const response = await fetch(`${BASE_URL}/appointment-types`, {
    method: 'GET',
    headers: {
      'Authorization': authHeader,
      'Content-Type': 'application/json'
    }
  });

  const types = await response.json();
  return types;
}

getAppointmentTypes().then(types => {
  types.forEach(type => {
    console.log(`${type.name}: $${type.price}`);
  });
});
```

### PHP

```php
<?php
$userId = getenv('ACUITY_USER_ID');
$apiKey = getenv('ACUITY_API_KEY');
$baseUrl = "https://acuityscheduling.com/api/v1";

// Create Basic Auth header
$credentials = base64_encode("$userId:$apiKey");
$authHeader = "Authorization: Basic $credentials";

// Get appointment types
$context = stream_context_create([
    'http' => [
        'method' => 'GET',
        'header' => "$authHeader\r\nContent-Type: application/json\r\n"
    ]
]);

$response = file_get_contents(
    "$baseUrl/appointment-types",
    false,
    $context
);

$types = json_decode($response, true);
foreach ($types as $type) {
    echo "{$type['name']}: \${$type['price']}\n";
}
?>
```

### Ruby

```ruby
require 'net/http'
require 'json'
require 'base64'

user_id = ENV['ACUITY_USER_ID']
api_key = ENV['ACUITY_API_KEY']
base_url = "https://acuityscheduling.com/api/v1"

# Create Basic Auth
credentials = Base64.encode64("#{user_id}:#{api_key}").chomp
uri = URI("#{base_url}/appointment-types")

# Make request
http = Net::HTTP.new(uri.host, uri.port)
http.use_ssl = true

request = Net::HTTP::Get.new(uri.path)
request['Authorization'] = "Basic #{credentials}"
request['Content-Type'] = 'application/json'

response = http.request(request)
types = JSON.parse(response.body)

types.each do |type|
  puts "#{type['name']}: $#{type['price']}"
end
```

---

## Security Best Practices

### DO

✅ **Store credentials securely**
- Use environment variables in development
- Use AWS Secrets Manager, Vault, or similar in production
- Never hardcode in source files

✅ **Use separate credentials per environment**
- Development: test credentials
- Staging: staging credentials
- Production: production credentials with restricted API key

✅ **Rotate API keys regularly**
- Every 90 days minimum
- Immediately if compromised
- Before offboarding team members

✅ **Restrict API key permissions**
- Use read-only keys where possible
- Create separate keys for different integrations

✅ **Use HTTPS for all requests**
- Acuity enforces HTTPS (automatic)
- Ensure your server uses HTTPS too

✅ **Monitor API usage**
- Track authentication failures
- Alert on unusual access patterns
- Review API logs regularly

✅ **Implement server-side API proxy**
- Never expose credentials to frontend
- Use secure server-side proxy to Acuity API

✅ **Implement API rate limiting**
- Stay well under Acuity's 10 req/sec limit
- Use exponential backoff for retries

### DON'T

❌ **Hardcode credentials**
```python
# WRONG - NEVER DO THIS
USER_ID = "12345678"
API_KEY = "abc123def456xyz789"
```

❌ **Commit credentials to version control**
```bash
# WRONG - Never commit .env
git add .env
git commit -m "Add credentials"
```

❌ **Expose credentials in logs**
```python
# WRONG - Logs API key in plaintext
logging.info(f"Using key: {api_key}")

# CORRECT - Mask sensitive data
logging.info(f"Using key: ****{api_key[-4:]}")
```

❌ **Use same credentials across environments**
```python
# WRONG - Same key for dev/prod
API_KEY = "shared_key_everywhere"

# CORRECT - Environment-specific keys
API_KEY = os.getenv('ACUITY_API_KEY')  # Different per env
```

❌ **Make API calls from frontend/browser**
```javascript
// WRONG - Exposes API key in browser
const response = await fetch(apiUrl, {
  headers: { 'Authorization': `Basic ${btoa(userId + ':' + apiKey)}` }
});

// CORRECT - Call your backend, which calls Acuity
const response = await fetch('/api/appointments');
```

❌ **Ignore authentication errors**
```python
# WRONG - Silently fails
response = session.get(url)
data = response.json()  # May be empty if 401

# CORRECT - Check status and handle errors
response = session.get(url)
if response.status_code == 401:
    raise AuthenticationError("Invalid credentials")
data = response.json()
```

---

## Credential Rotation

### Step 1: Generate New Credentials

1. Go to Acuity Settings → Integrations → API
2. Click "Generate New Key"
3. Copy the new API Key (shown only once)
4. **Don't delete old key yet**

### Step 2: Update Application

1. Update environment variables with new credentials
2. Deploy to staging first
3. Test authentication with new credentials
4. Deploy to production

### Step 3: Verify New Credentials Work

```bash
# Test with new credentials
curl -u "12345678:new_api_key_here" \
  https://acuityscheduling.com/api/v1/me
```

### Step 4: Delete Old Credentials

Once verified in production:

1. Go back to Acuity Settings → Integrations → API
2. Find the old API Key
3. Click "Delete" or "Revoke"
4. Confirm deletion

### Step 5: Document Rotation

Update rotation log:
```
Date Rotated: 2025-11-11
Old Key: ****xyz789 (deleted)
New Key: ****abc123
Reason: Routine 90-day rotation
Verified By: John Smith
```

---

## Troubleshooting

### "Invalid Credentials" (401)

**Possible Causes:**
1. Wrong User ID or API Key
2. Credentials not set in environment
3. Leading/trailing whitespace in credentials

**Solutions:**
```bash
# Check credentials are set
echo $ACUITY_USER_ID
echo $ACUITY_API_KEY

# Verify no extra spaces
# Remove any quotes or extra characters

# Try test script
python test_auth.py
```

### "Forbidden" (403)

**Possible Causes:**
1. Your user account lacks admin permissions
2. API key doesn't have required scope

**Solution:**
- Contact Acuity support to ensure your account has admin role
- User must have: Settings → Integrations → API access

### "Connection Refused"

**Possible Causes:**
1. Network/firewall blocking outbound connections
2. Acuity service down

**Solutions:**
```bash
# Test connectivity
ping acuityscheduling.com

# Try curl
curl https://acuityscheduling.com/api/v1/me \
  -u "12345678:api_key"

# Check status page
# https://status.acuityscheduling.com
```

### "Timeout"

**Possible Causes:**
1. Slow network connection
2. Acuity API slow
3. Firewall blocking

**Solution:**
```python
# Increase timeout
response = session.get(
    url,
    timeout=30  # Seconds
)
```

### Rate Limiting Issues

If getting 429 errors frequently:

1. Reduce API calls (use caching)
2. Lower request rate
3. Implement exponential backoff

```python
import time

def make_request_with_backoff(url, max_retries=3):
    for attempt in range(max_retries):
        response = session.get(url)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 429:
            wait = 2 ** attempt  # 1, 2, 4, 8...
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue

        else:
            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

---

## See Also

- [API Endpoints Reference](api-endpoints-reference.md) - Complete endpoint documentation
- [Error Handling Guide](error-handling-guide.md) - Error codes and solutions
- [Risk Assessment & Pitfalls](../risk-assessment-guide.md) - Security considerations
- [Official Acuity API Documentation](https://developer.acuityscheduling.com)

---

**Last Updated:** 2025-11-11
**Generated with Claude Code**
