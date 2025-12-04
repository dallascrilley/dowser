# Basecamp 4 API - Complete Endpoint Reference

**Last Updated:** November 11, 2025
**API Version:** Basecamp 4
**Base URL:** `https://3.basecampapi.com/{ACCOUNT_ID}/`

---

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [Projects (Buckets)](#projects-buckets)
4. [Messages](#messages)
5. [Documents](#documents)
6. [People](#people)
7. [Vaults](#vaults)
8. [To-Do Items](#to-do-items)
9. [Rate Limits](#rate-limits)
10. [Error Handling](#error-handling)

---

## Introduction

The Basecamp 4 API is a REST-style HTTP API for accessing and managing Basecamp 4 projects. All data is transmitted as JSON.

### Key Characteristics

- **Authentication:** OAuth 2.0 Bearer tokens only
- **Data Format:** JSON with snake_case keys
- **Content Type:** `application/json; charset=utf-8`
- **Required Headers:** `Authorization`, `User-Agent`, `Content-Type` (POST/PUT)
- **HTTPS Only:** All requests must use HTTPS
- **Base URL Structure:** `https://3.basecampapi.com/{ACCOUNT_ID}/`
- **Resource URLs:** End with `.json` extension

### Mandatory Headers

Every request MUST include:

```http
Authorization: Bearer {ACCESS_TOKEN}
User-Agent: AppName (contact@example.com)
Content-Type: application/json; charset=utf-8  # POST/PUT only
```

Missing any of these headers will result in errors:
- Missing `User-Agent` → 400 Bad Request
- Missing `Content-Type` (POST/PUT) → 415 Unsupported Media Type
- Missing `Authorization` → 401 Unauthorized

---

## Authentication

### Using OAuth 2.0 Tokens

All API requests must include your OAuth 2.0 access token in the `Authorization` header.

**Important:** Extract just the `access_token` value from the OAuth response, not the entire JSON.

```bash
# CORRECT - Extract access_token
token=$(echo "$oauth_response" | jq -r '.access_token')

# WRONG - Don't use entire JSON
token="$oauth_response"  # This will cause "internal checksum failed" error
```

---

## Projects (Buckets)

Projects are called "buckets" in API URLs. They contain tools like message boards, documents, and to-dos.

### List All Projects

**Endpoint:** `GET /projects.json`

**Description:** Retrieve all active projects in the account

**Parameters:**
- `status` (optional): Filter by status - `active`, `archived`, or `trashed`

**Response:** Array of project objects

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
```

**Response (200 OK):**

```json
[
  {
    "id": 2085958499,
    "name": "The Leto Laptop",
    "description": "Project description",
    "status": "active",
    "created_at": "2022-10-28T08:23:58.169Z",
    "updated_at": "2022-11-22T17:56:27.363Z",
    "url": "https://3.basecampapi.com/195539477/projects/2085958499.json",
    "app_url": "https://3.basecamp.com/195539477/projects/2085958499",
    "dock": [
      {
        "id": 1069479338,
        "title": "Message Board",
        "name": "message_board",
        "enabled": true,
        "position": 1,
        "url": "https://3.basecampapi.com/195539477/buckets/2085958499/message_boards/1069479338.json"
      },
      {
        "id": 1069479340,
        "title": "Docs & Files",
        "name": "vault",
        "enabled": true,
        "position": 3,
        "url": "https://3.basecampapi.com/195539477/buckets/2085958499/vaults/1069479340.json"
      }
    ]
  }
]
```

**Pagination:** Uses Link headers (RFC5988)

---

### Get Single Project

**Endpoint:** `GET /projects/{id}.json`

**Description:** Retrieve details for a specific project including its dock

**URL Parameters:**
- `id` (required): Project ID

**Response:** Single project object with full dock array

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499.json"
```

**Related:** See **Workflows** section for extracting tool IDs from dock

---

### Create Project

**Endpoint:** `POST /projects.json`

**Description:** Create a new project

**Request Body:**

```json
{
  "name": "Project Name",
  "description": "Optional description"
}
```

**Response:** 201 Created with new project object including dock

**Example:**

```bash
curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"name":"New Project","description":"Q4 2024 initiative"}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
```

**Errors:**
- `507 Insufficient Storage` - Free account has reached project limit

**See Also:** [Workflow: Create Project with Initial Content](./workflow-patterns.md#project-setup)

---

### Update Project

**Endpoint:** `PUT /projects/{id}.json`

**Description:** Update project name and description

**URL Parameters:**
- `id` (required): Project ID

**Request Body:**

```json
{
  "name": "Updated Name",
  "description": "Updated description"
}
```

**Response:** 200 OK with updated project object

**Example:**

```bash
curl -s -X PUT \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"name":"Updated Name"}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499.json"
```

---

### Delete Project (Archive)

**Endpoint:** `DELETE /projects/{id}.json`

**Description:** Archive/delete a project (moves to trashed status)

**URL Parameters:**
- `id` (required): Project ID

**Response:** 204 No Content (on success)

**Example:**

```bash
curl -s -X DELETE \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499.json"
```

---

## Messages

Messages are posted to a project's message board. Each project has one message board in its dock.

### List Messages

**Endpoint:** `GET /buckets/{project_id}/message_boards/{board_id}/messages.json`

**Description:** List all messages in a message board

**URL Parameters:**
- `project_id` (required): Project ID
- `board_id` (required): Message board ID (from dock)

**Response:** Array of message objects

**Example:**

```bash
# First, get the message_board ID from project's dock
MESSAGE_BOARD_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: MyApp (me@example.com)" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499.json" | \
  jq -r '.dock[] | select(.name=="message_board") | .id')

# Then list messages
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/message_boards/$MESSAGE_BOARD_ID/messages.json"
```

**Response (200 OK):**

```json
[
  {
    "id": 1069479530,
    "subject": "Project Kickoff",
    "content": "<div><strong>Welcome!</strong><br>First meeting Monday 10am.</div>",
    "status": "active",
    "created_at": "2022-10-28T10:30:00.000Z",
    "updated_at": "2022-10-28T10:30:00.000Z",
    "creator": {
      "id": 1049715914,
      "name": "Victor Cooper",
      "email_address": "victor@example.com"
    },
    "bucket": {
      "id": 2085958499,
      "name": "The Leto Laptop",
      "type": "Project"
    },
    "parent": {
      "id": 1069479338,
      "title": "Message Board",
      "type": "Message::Board",
      "url": "https://3.basecampapi.com/195539477/buckets/2085958499/message_boards/1069479338.json"
    },
    "comments_count": 2,
    "comments_url": "https://3.basecampapi.com/195539477/buckets/2085958499/messages/1069479530/comments.json",
    "url": "https://3.basecampapi.com/195539477/buckets/2085958499/messages/1069479530.json",
    "app_url": "https://3.basecamp.com/195539477/buckets/2085958499/messages/1069479530"
  }
]
```

**Pagination:** Uses Link headers - follow Link header for next page

---

### Get Single Message

**Endpoint:** `GET /buckets/{project_id}/messages/{id}.json`

**Description:** Retrieve a specific message with comments

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Message ID

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/messages/1069479530.json"
```

---

### Create Message

**Endpoint:** `POST /buckets/{project_id}/message_boards/{board_id}/messages.json`

**Description:** Post a new message to the message board

**URL Parameters:**
- `project_id` (required): Project ID
- `board_id` (required): Message board ID (from dock)

**Request Body:**

```json
{
  "subject": "Message Subject",
  "content": "<div>Message content in HTML</div>",
  "status": "active"
}
```

**Response:** 201 Created with new message object

**Example:**

```bash
curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{
       "subject": "Project Update",
       "content": "<div><strong>Important:</strong> Deadline moved to Friday</div>",
       "status": "active"
     }' \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/message_boards/$MESSAGE_BOARD_ID/messages.json"
```

**Content Requirements:**
- HTML format with allowed tags: `div`, `h1`, `br`, `strong`, `em`, `strike`, `a`, `pre`, `ol`, `ul`, `li`, `blockquote`, `bc-attachment`
- No script tags or dangerous content
- HTML entities must be properly encoded

**See Also:**
- [Workflow: Post Message](./workflow-patterns.md#content-publishing)
- [Rich Text Guidelines](./rich-text-guidelines.md)

---

### Update Message

**Endpoint:** `PUT /buckets/{project_id}/messages/{id}.json`

**Description:** Update message subject and content

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Message ID

**Request Body:**

```json
{
  "subject": "Updated Subject",
  "content": "<div>Updated content</div>",
  "status": "active"
}
```

**Response:** 200 OK with updated message

---

## Documents

Documents are stored in a project's vault (Docs & Files tool). Documents support rich HTML content and can have comments.

### List Documents in Vault

**Endpoint:** `GET /buckets/{project_id}/vaults/{vault_id}/documents.json`

**Description:** List all documents in a vault

**URL Parameters:**
- `project_id` (required): Project ID
- `vault_id` (required): Vault ID (from dock)

**Example:**

```bash
# Get vault ID
VAULT_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: MyApp (me@example.com)" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499.json" | \
  jq -r '.dock[] | select(.name=="vault") | .id')

# List documents
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/vaults/$VAULT_ID/documents.json"
```

**Response:** Array of document objects

---

### Get Single Document

**Endpoint:** `GET /buckets/{project_id}/documents/{id}.json`

**Description:** Retrieve a specific document

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Document ID

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/documents/1069480000.json"
```

---

### Create Document

**Endpoint:** `POST /buckets/{project_id}/vaults/{vault_id}/documents.json`

**Description:** Create a new document in a vault

**URL Parameters:**
- `project_id` (required): Project ID
- `vault_id` (required): Vault ID (from dock)

**Request Body:**

```json
{
  "title": "Document Title",
  "content": "<h1>Heading</h1><p>Document content</p>",
  "status": "active"
}
```

**Response:** 201 Created with new document object

**Example:**

```bash
curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{
       "title": "Project Requirements",
       "content": "<h1>Overview</h1><p>Key requirements for Q4 launch...</p>",
       "status": "active"
     }' \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/vaults/$VAULT_ID/documents.json"
```

**See Also:**
- [Workflow: Create Document](./workflow-patterns.md#content-publishing)
- [Workflow: Nested Vaults](./workflow-patterns.md#organize-documents)

---

### Update Document

**Endpoint:** `PUT /buckets/{project_id}/documents/{id}.json`

**Description:** Update document content

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Document ID

**Request Body:**

```json
{
  "title": "Updated Title",
  "content": "<h1>Updated content</h1>",
  "status": "active"
}
```

**Response:** 200 OK with updated document

---

### Delete Document

**Endpoint:** `DELETE /buckets/{project_id}/documents/{id}.json`

**Description:** Delete/archive a document

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Document ID

**Response:** 204 No Content

---

## People

Manage project members and team access.

### List All People

**Endpoint:** `GET /people.json`

**Description:** List all people with account access

**Response:** Array of person objects

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/people.json"
```

---

### List Project Members

**Endpoint:** `GET /projects/{id}/people.json`

**Description:** List all members with access to a project

**URL Parameters:**
- `id` (required): Project ID

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499/people.json"
```

---

### Grant Project Access

**Endpoint:** `PUT /projects/{id}/people/users.json`

**Description:** Grant access to existing person or create new person with access

**URL Parameters:**
- `id` (required): Project ID

**Request Body - Grant Access to Existing Person:**

```json
{
  "grant": [1049715914, 1049715915]
}
```

**Request Body - Create New Person and Grant Access:**

```json
{
  "create": [
    {
      "name": "Jane Smith",
      "email_address": "jane@example.com",
      "title": "Project Manager",
      "company_name": "Acme Corp"
    }
  ]
}
```

**Request Body - Combined Operations:**

```json
{
  "grant": [1049715914],
  "revoke": [1049715915],
  "create": [
    {
      "name": "New Person",
      "email_address": "new@example.com"
    }
  ]
}
```

**Response:** 200 OK with updated access list

**Example:**

```bash
curl -s -X PUT \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"grant": [1049715914]}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/projects/2085958499/people/users.json"
```

---

### Revoke Project Access

**Endpoint:** `PUT /projects/{id}/people/users.json`

**Description:** Remove person's access to project

**Request Body:**

```json
{
  "revoke": [1049715914]
}
```

---

## Vaults

Vaults are the Docs & Files tool in projects. They support nested vaults (sub-folders).

### List Nested Vaults

**Endpoint:** `GET /buckets/{project_id}/vaults/{vault_id}/vaults.json`

**Description:** List all sub-vaults (folders) within a vault

**URL Parameters:**
- `project_id` (required): Project ID
- `vault_id` (required): Parent vault ID (from dock)

**Example:**

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/vaults/$VAULT_ID/vaults.json"
```

---

### Create Nested Vault

**Endpoint:** `POST /buckets/{project_id}/vaults/{vault_id}/vaults.json`

**Description:** Create a new sub-vault (folder) inside a vault

**URL Parameters:**
- `project_id` (required): Project ID
- `vault_id` (required): Parent vault ID

**Request Body:**

```json
{
  "title": "Sub-Folder Name"
}
```

**Response:** 201 Created with new vault object

**Example:**

```bash
curl -s -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "User-Agent: MyApp (me@example.com)" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"title":"Design Assets"}' \
     "https://3.basecampapi.com/$ACCOUNT_ID/buckets/2085958499/vaults/$VAULT_ID/vaults.json"
```

**See Also:** [Workflow: Organize Documents in Nested Vaults](./workflow-patterns.md#organize-documents)

---

### Get Vault Details

**Endpoint:** `GET /buckets/{project_id}/vaults/{id}.json`

**Description:** Get vault information

**URL Parameters:**
- `project_id` (required): Project ID
- `id` (required): Vault ID

---

### Update Vault

**Endpoint:** `PUT /buckets/{project_id}/vaults/{id}.json`

**Description:** Update vault name

**Request Body:**

```json
{
  "title": "Updated Vault Name"
}
```

---

## To-Do Items

To-do items are organized in to-do lists within a to-do set.

### List To-Do Lists

**Endpoint:** `GET /buckets/{project_id}/todosets/{set_id}/todolists.json`

**Description:** List all to-do lists in the to-do set

**URL Parameters:**
- `project_id` (required): Project ID
- `set_id` (required): To-do set ID (from dock)

---

### List To-Dos in List

**Endpoint:** `GET /buckets/{project_id}/todolists/{list_id}/todos.json`

**Description:** List all to-dos in a to-do list

**URL Parameters:**
- `project_id` (required): Project ID
- `list_id` (required): To-do list ID

---

### Create To-Do

**Endpoint:** `POST /buckets/{project_id}/todolists/{list_id}/todos.json`

**Description:** Create a new to-do item

**Request Body:**

```json
{
  "content": "Task name",
  "description": "Optional description",
  "assignee_ids": [1049715914],
  "due_on": "2025-01-31",
  "starts_on": "2025-01-15"
}
```

**Response:** 201 Created with new to-do object

---

### Update To-Do

**Endpoint:** `PUT /buckets/{project_id}/todos/{id}.json`

**Description:** Update to-do item

**Important:** Pass ALL existing fields along with updates to prevent data loss

**Request Body:**

```json
{
  "content": "Updated task name",
  "description": "Updated description",
  "assignee_ids": [1049715914, 1049715915],
  "due_on": "2025-02-28",
  "starts_on": "2025-01-20",
  "completion_subscriber_ids": [1049715914],
  "notify": false
}
```

**Pitfall Alert:** Omitting fields clears their values (e.g., omitting `assignee_ids` removes all assignees)

**See Also:** [Error Handling: Todo Update](./error-handling.md#updating-todos)

---

### Complete To-Do

**Endpoint:** `PUT /buckets/{project_id}/todos/{id}/completion.json`

**Description:** Mark to-do as complete

**Request Body:**

```json
{
  "completed": true
}
```

---

## Rate Limits

### Rate Limit Specifications

- **Limit:** 50 requests per 10 seconds per IP address
- **Enforcement:** At IP level, not per token
- **Response Code:** 429 Too Many Requests
- **Response Header:** `Retry-After: {seconds}`

### Handling Rate Limits

```bash
# Check for 429 response
if [ "$HTTP_CODE" = "429" ]; then
  # Get wait time from Retry-After header
  retry_after=$(curl -i "$url" | grep -i "Retry-After:" | awk '{print $2}')

  # Wait the specified time
  sleep $retry_after

  # Retry request
  curl "$url"
fi
```

**See Also:** [Rate Limiting Guide](./rate-limiting.md)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action | Retryable |
|------|---------|--------|-----------|
| 200 | OK | Success | N/A |
| 201 | Created | Resource created | N/A |
| 204 | No Content | Success (delete) | N/A |
| 400 | Bad Request | Check headers/format | No |
| 401 | Unauthorized | Refresh token | Yes |
| 404 | Not Found | Resource deleted or no access | No |
| 415 | Unsupported Media | Missing Content-Type | No |
| 429 | Rate Limited | Wait Retry-After, retry | Yes |
| 500-504 | Server Error | Exponential backoff | Yes |
| 507 | Insufficient Storage | Account limit reached | No |

### Error Response Format

```json
{
  "error": "Human-readable error message"
}
```

### Common Errors

**400 Bad Request - Missing User-Agent:**
```
curl: Missing User-Agent header
HTTP/1.1 400 Bad Request
```
Solution: Add `-H "User-Agent: AppName (contact@example.com)"`

**415 Unsupported Media Type - Missing Content-Type:**
```
curl -d '{"name":"Project"}'  # Missing Content-Type
HTTP/1.1 415 Unsupported Media Type
```
Solution: Add `-H "Content-Type: application/json; charset=utf-8"`

**404 Not Found - Account Inactive:**
```
HTTP/1.1 404 Not Found
Reason: Account Inactive

# This means trial expired or account suspended
```
Solution: Notify user, disable integration

**429 Too Many Requests:**
```
HTTP/1.1 429 Too Many Requests
Retry-After: 8
```
Solution: Wait 8 seconds, then retry

**See Also:** [Error Handling Guide](./error-handling.md)

---

## Quick Reference

### Extract Tool IDs from Project Dock

```bash
# Get project with dock
project=$(curl -s -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: MyApp (me@example.com)" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json")

# Extract specific tool ID
message_board_id=$(echo "$project" | jq -r '.dock[] | select(.name=="message_board") | .id')
vault_id=$(echo "$project" | jq -r '.dock[] | select(.name=="vault") | .id')
todoset_id=$(echo "$project" | jq -r '.dock[] | select(.name=="todoset") | .id')
```

### Pagination Pattern

```bash
url="https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/messages.json"

while [ ! -z "$url" ]; do
  response=$(curl -i -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: MyApp (me@example.com)" \
    "$url")

  # Process response
  body=$(echo "$response" | sed -n '/^\[/,$p')

  # Get next page URL from Link header
  url=$(echo "$response" | grep -i "^Link:" | \
    sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')
done
```

---

## Related Documentation

- [Workflow Patterns](./workflow-patterns.md) - Common multi-step workflows
- [Error Handling](./error-handling.md) - Detailed error recovery
- [Rate Limiting](./rate-limiting.md) - Rate limit management
- [Pagination](./pagination.md) - Advanced pagination techniques

---

**For questions or issues:** Consult the [Basecamp API Documentation](https://github.com/basecamp/bc4-api)
