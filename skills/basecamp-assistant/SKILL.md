---
name: basecamp-assistant
description: >-
  Comprehensive Basecamp 4 API integration assistant. Manages projects,
  messages, documents, people, todos, and all Basecamp resources via REST API.
when_to_use: >-
  Use when integrating with Basecamp 4, building Basecamp automations, managing
  projects programmatically, posting messages/documents, working with Basecamp
  API, basecamp 4, bc3-api, basecamp integration, project management api, oauth
  basecamp, message boards, or docs and files.
version: 1.0.0
category: integrations-and-saas
---

# Basecamp 4 API Assistant

Expert assistant for integrating with the Basecamp 4 REST API. Helps with authentication, project management, messages, documents, todos, people management, and all Basecamp operations.

## Prerequisites

**IMPORTANT:** You must have a Basecamp 4 account and OAuth 2.0 credentials to use this API.

### First-Time Setup

1. **Get OAuth 2.0 Token:**
   - Register your app at https://launchpad.37signals.com/integrations
   - Follow OAuth 2.0 flow to get ACCESS_TOKEN
   - Find your ACCOUNT_ID (numeric ID from your Basecamp URL)

2. **Set Environment Variables:**
   ```bash
   # Create .env file (or export directly)
   export ACCESS_TOKEN="your_oauth2_access_token_here"
   export ACCOUNT_ID="999999999"
   export USER_AGENT="YourApp (contact@example.com)"
   ```

3. **Validate Setup:**
   ```bash
   ./scripts/setup.sh
   # Or manually test:
   ./scripts/validate_config.sh
   ./scripts/test_connection.sh
   ```

4. **Use Templates:**
   - Copy `templates/basic.env.template` → `.env`
   - Fill in your ACCESS_TOKEN and ACCOUNT_ID
   - Source the file: `source .env`

## Quick Start

```bash
# Set up environment
export ACCESS_TOKEN="your_token"
export ACCOUNT_ID="999999999"

# Test connection
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/projects.json

# List projects using helper script
./scripts/list_projects.sh

# Get project tools (dock IDs)
./scripts/get_project_tools.sh 2085958499

# Post a message
./scripts/post_message.sh 2085958499 1069479338 "Hello Basecamp!"

# Create a document
./scripts/create_document.sh 2085958499 1069479340 "My Document"
```

## Core Tasks

### Working with Projects

**List all projects:**
```bash
# Active projects (default)
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/projects.json

# Archived projects
./scripts/list_projects.sh --status=archived
```

**Get project details and dock:**
```bash
PROJECT_ID=2085958499
PROJECT_JSON=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: MyApp (you@example.com)" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json)

# Extract tool IDs
MESSAGE_BOARD_ID=$(echo $PROJECT_JSON | jq -r '.dock[] | select(.name=="message_board") | .id')
VAULT_ID=$(echo $PROJECT_JSON | jq -r '.dock[] | select(.name=="vault") | .id')
TODOSET_ID=$(echo $PROJECT_JSON | jq -r '.dock[] | select(.name=="todoset") | .id')

# Or use helper script
./scripts/get_project_tools.sh $PROJECT_ID
```

**Create a project:**
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -H "User-Agent: MyApp (you@example.com)" \
     -d '{"name":"Product Launch 2024","description":"Q4 Marketing Campaign"}' \
     https://3.basecampapi.com/$ACCOUNT_ID/projects.json
```

### Working with Messages

**Post a message:**
```bash
PROJECT_ID=2085958499
MESSAGE_BOARD_ID=1069479338

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -H "User-Agent: MyApp (you@example.com)" \
     -d '{
       "subject": "Project Kickoff",
       "content": "<div><strong>Welcome!</strong> First meeting Monday 10am.</div>",
       "status": "active"
     }' \
     https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json
```

**List messages with pagination:**
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json

# Follow Link header for next page (see references/pagination.md)
```

### Working with Documents

**Create a document:**
```bash
PROJECT_ID=2085958499
VAULT_ID=1069479340

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -H "User-Agent: MyApp (you@example.com)" \
     -d '{
       "title": "Project Requirements",
       "content": "<h1>Overview</h1><p>Key requirements...</p>",
       "status": "active"
     }' \
     https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/documents.json
```

**List documents in a vault:**
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/documents.json
```

### Working with People

**List all people:**
```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/people.json
```

**Grant project access:**
```bash
PROJECT_ID=2085958499

curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -H "User-Agent: MyApp (you@example.com)" \
     -d '{
       "grant": [1049715922],
       "create": [
         {"name": "Jane Smith", "email_address": "jane@example.com", "title": "PM"}
       ]
     }' \
     -X PUT \
     https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people/users.json
```

## API Reference

**Base URL:** `https://3.basecampapi.com/{ACCOUNT_ID}/`

**Required Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`
- `User-Agent: AppName (contact@example.com)` ⚠️ **MANDATORY**
- `Content-Type: application/json` (for POST/PUT only)

**Key Concepts:**
- **Projects** are called "buckets" in API URLs
- **Dock** is an array of tools (message_board, vault, todoset, etc.) in each project
- **Vaults** are the "Docs & Files" section (can be nested)
- **Rich Text** uses HTML with special `<bc-attachment>` tags

**See:** [references/api-reference.md](references/api-reference.md) for complete endpoint documentation.

## Configuration Files

### Environment Variables (.env)

**Required:**
- `ACCESS_TOKEN` - OAuth 2.0 Bearer token
- `ACCOUNT_ID` - Your Basecamp account ID (numeric)
- `USER_AGENT` - Format: "AppName (contact@email.com)"

**Optional:**
- `DEBUG` - Set to "true" for verbose output
- `BASE_URL` - Override default (for testing)

**Templates available:**
- `templates/basic.env.template` - Minimal config
- `templates/development.env.template` - Dev environment with debugging
- `templates/production.env.template` - Production with monitoring

### Configuration Validation

```bash
# Validate without making API calls
./scripts/validate_config.sh

# Validate with API test
./scripts/setup.sh
```

## Proven Patterns

**⚠️ MANDATORY: Always include User-Agent header**

Every API request MUST include a User-Agent header with your app name and contact email. Missing this header results in `400 Bad Request`.

```bash
# ✅ CORRECT
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     https://3.basecampapi.com/$ACCOUNT_ID/projects.json

# ❌ WRONG - will return 400 Bad Request
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     https://3.basecampapi.com/$ACCOUNT_ID/projects.json
```

**⚠️ MANDATORY: Follow Link headers for pagination**

NEVER construct pagination URLs manually. Always follow the `Link` header with `rel="next"`.

```bash
# ✅ CORRECT - follow Link header
NEXT_URL=$(echo "$RESPONSE" | grep -i "^Link:" | sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "User-Agent: MyApp (you@example.com)" \
     "$NEXT_URL"

# ❌ WRONG - don't construct URLs
curl "https://3.basecampapi.com/$ACCOUNT_ID/projects.json?page=2"
```

See [references/pagination.md](references/pagination.md) for complete pagination guide.

**⚠️ MANDATORY: Handle rate limits with exponential backoff**

Rate limit: 50 requests per 10 seconds per IP. Always implement backoff for 429 responses.

```bash
# Check for 429 status
if [ "$HTTP_CODE" = "429" ]; then
  RETRY_AFTER=$(echo "$RESPONSE" | grep -i "Retry-After:" | awk '{print $2}')
  sleep $RETRY_AFTER
  # Retry request
fi
```

See [references/rate-limiting.md](references/rate-limiting.md) for complete guide.

**⚠️ MANDATORY: Never retry 404 errors**

404 errors are permanent. Don't retry them.

```bash
if [ "$HTTP_CODE" = "404" ]; then
  echo "Resource not found or no access - will not retry"
  exit 1
fi
```

**⚠️ MANDATORY: Always validate ACCESS_TOKEN before operations**

```bash
# Test token before running batch operations
./scripts/test_connection.sh
if [ $? -ne 0 ]; then
  echo "Invalid token, aborting"
  exit 1
fi
```

## Troubleshooting

**Quick fixes for common issues:**

| Issue | Solution |
|-------|----------|
| `400 Bad Request` | Add User-Agent header: `User-Agent: MyApp (you@example.com)` |
| `404 Not Found` | Resource deleted or no access - check permissions, don't retry |
| `415 Unsupported Media Type` | Add Content-Type header: `Content-Type: application/json` |
| `429 Too Many Requests` | Rate limit exceeded - read `Retry-After` header and wait |
| `500-504 Server Errors` | Transient issue - retry with exponential backoff |
| `507 Insufficient Storage` | Free account project limit - upgrade or archive projects |
| Pagination not working | Follow `Link` header, don't construct URLs manually |
| `checksum failed` in OAuth | Token expired or invalid - get new token |

**For detailed solutions:** [references/error-handling.md](references/error-handling.md)

## Helper Scripts

**Setup & Validation:**
- `scripts/setup.sh` - First-time setup and validation
- `scripts/validate_config.sh` - Quick config check (no API calls)
- `scripts/test_connection.sh` - Test API connectivity and auth

**Project Operations:**
- `scripts/list_projects.sh` - List all projects with pagination
- `scripts/get_project_tools.sh PROJECT_ID` - Extract dock tool IDs

**Content Creation:**
- `scripts/post_message.sh PROJECT_ID BOARD_ID "Subject"` - Post message
- `scripts/create_document.sh PROJECT_ID VAULT_ID "Title"` - Create document

**See:** [scripts/README.md](scripts/README.md) for complete scripts documentation.

## Workflow Requirements

**⚠️ MANDATORY: Always follow this workflow when working with Basecamp API:**

1. **Validate Configuration**
   ```bash
   ./scripts/validate_config.sh
   ```

2. **Test Connection**
   ```bash
   ./scripts/test_connection.sh
   ```

3. **Get Resource IDs**
   ```bash
   # For messages/documents, you need project + tool IDs
   ./scripts/get_project_tools.sh PROJECT_ID
   ```

4. **Make API Request**
   ```bash
   # Always include required headers
   curl -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "User-Agent: MyApp (you@example.com)" \
        -H "Content-Type: application/json" \
        ...
   ```

5. **Handle Errors**
   ```bash
   # Check HTTP status code
   # 429 → wait and retry
   # 500-504 → retry with backoff
   # 404 → don't retry
   ```

**Why this prevents failures:**
- Validates credentials before making requests
- Ensures required headers are present
- Gets correct resource IDs (prevents 404s)
- Handles rate limits and transient errors
- Follows pagination correctly

---

## Common Workflows

### Workflow 1: Create Project → Post Welcome Message

```bash
# Step 1: Create project
PROJECT_JSON=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: MyApp (you@example.com)" \
  -d '{"name":"New Project","description":"Team collaboration"}' \
  https://3.basecampapi.com/$ACCOUNT_ID/projects.json)

# Step 2: Extract IDs
PROJECT_ID=$(echo $PROJECT_JSON | jq -r '.id')
MESSAGE_BOARD_ID=$(echo $PROJECT_JSON | jq -r '.dock[] | select(.name=="message_board") | .id')

# Step 3: Post welcome message
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: MyApp (you@example.com)" \
  -d '{"subject":"Welcome","content":"<div>Project created!</div>","status":"active"}' \
  https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json
```

### Workflow 2: Create Document in Vault

```bash
PROJECT_ID=2085958499

# Step 1: Get vault ID from project dock
VAULT_ID=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: MyApp (you@example.com)" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json | \
  jq -r '.dock[] | select(.name=="vault") | .id')

# Step 2: Create document
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "User-Agent: MyApp (you@example.com)" \
  -d '{"title":"Meeting Notes","content":"<h1>Notes</h1>","status":"active"}' \
  https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/documents.json
```

### Workflow 3: Fetch All Messages with Pagination

```bash
PROJECT_ID=2085958499
MESSAGE_BOARD_ID=1069479338
ALL_MESSAGES="[]"
NEXT_URL="https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json"

while [ ! -z "$NEXT_URL" ]; do
  RESPONSE=$(curl -s -i -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "User-Agent: MyApp (you@example.com)" \
    "$NEXT_URL")

  # Extract JSON body
  BODY=$(echo "$RESPONSE" | sed -n '/^\[/,$p')
  ALL_MESSAGES=$(echo "$ALL_MESSAGES $BODY" | jq -s 'add')

  # Extract next URL from Link header
  NEXT_URL=$(echo "$RESPONSE" | grep -i "^Link:" | sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')
done

echo $ALL_MESSAGES | jq '.'
```

### Workflow 4: Add Person → Grant Project Access

```bash
PROJECT_ID=2085958499

# Step 1: Check if person exists
PEOPLE=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: MyApp (you@example.com)" \
  https://3.basecampapi.com/$ACCOUNT_ID/people.json)

PERSON_ID=$(echo $PEOPLE | jq -r '.[] | select(.email_address=="jane@example.com") | .id')

# Step 2: Grant access (create if doesn't exist)
if [ -z "$PERSON_ID" ]; then
  curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -H "User-Agent: MyApp (you@example.com)" \
    -d '{"create":[{"name":"Jane Smith","email_address":"jane@example.com"}]}' \
    -X PUT \
    https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people/users.json
else
  curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -H "User-Agent: MyApp (you@example.com)" \
    -d "{\"grant\":[$PERSON_ID]}" \
    -X PUT \
    https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people/users.json
fi
```

See [references/workflow-patterns.md](references/workflow-patterns.md) for more workflows.

## Tips

**Authentication:**
- OAuth 2.0 tokens don't expire but can be revoked
- Store tokens securely (use .env files, never commit)
- Test token regularly with `/my/profile.json`

**Performance:**
- Use HTTP caching with ETags to reduce API calls
- Batch operations when possible
- Follow rate limits (50 req/10s)
- Use pagination efficiently (Link headers)

**Error Handling:**
- Always check HTTP status codes
- Implement exponential backoff for retries
- Log all API errors with request context
- Never retry 404s (permanent)

**Projects (Buckets):**
- Projects are "buckets" in API URLs
- Get dock IDs after creating projects
- Each tool (message_board, vault, etc.) has unique ID
- Use helper script to extract IDs

**Rich Text:**
- Use HTML tags for formatting
- `<bc-attachment>` for mentions and files
- Test content rendering in Basecamp UI
- Escape special characters properly

**Pagination:**
- ALWAYS follow Link headers
- Never construct pagination URLs
- Check X-Total-Count header for totals
- Page sizes vary (geared: 15→30→50→100+)

**See also:**
- [references/api-reference.md](references/api-reference.md) - Complete API documentation
- [references/workflow-patterns.md](references/workflow-patterns.md) - Multi-step workflows
- [references/error-handling.md](references/error-handling.md) - Error codes and recovery
- [references/rate-limiting.md](references/rate-limiting.md) - Rate limit management
- [references/pagination.md](references/pagination.md) - Pagination best practices
- [scripts/README.md](scripts/README.md) - Helper scripts guide
