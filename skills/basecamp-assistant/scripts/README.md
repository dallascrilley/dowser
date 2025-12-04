# Basecamp 4 API - Helper Scripts

This directory contains production-ready bash scripts for common Basecamp 4 API operations.

**Last Updated:** November 11, 2025  
**Total Scripts:** 7  
**Total Lines of Code:** ~400 lines  

---

## Quick Start

1. Ensure `.env` file exists with `ACCESS_TOKEN` and `ACCOUNT_ID`
2. Run validation: `./scripts/validate_config.sh`
3. Test connection: `./scripts/test_connection.sh`
4. Use scripts as needed for your workflow

---

## Scripts Overview

| Script | Purpose | Dependencies | Exit Codes |
|--------|---------|--------------|-----------|
| `setup.sh` | Full setup validation and user info | jq, curl | 1-4 |
| `validate_config.sh` | Quick configuration check | .env file | 1-2 |
| `test_connection.sh` | API connectivity test | .env file | 0-1 |
| `list_projects.sh` | List all projects | .env file | 0-1 |
| `get_project_tools.sh` | Extract tool IDs from project | PROJECT_ID | 0-2 |
| `post_message.sh` | Post message to message board | PROJECT_ID, TEXT | 0-1 |
| `create_document.sh` | Create document in vault | PROJECT_ID, TEXT | 0-1 |

---

## Setup and Validation

### 1. validate_config.sh

Quickly verify your `.env` file configuration without making API calls.

```bash
./scripts/validate_config.sh

# Output:
# Configuration Validation
# ========================
# ✓ ACCESS_TOKEN: Set (40 characters)
# ✓ ACCOUNT_ID: 195539477
# ✓ USER_AGENT: MyApp (me@example.com)
# 
# All required configuration is valid!
```

**Exit Codes:**
- `0`: Configuration valid
- `1`: .env file not found
- `2`: Required variables missing or invalid

---

### 2. test_connection.sh

Quick connectivity test without verbose output.

```bash
./scripts/test_connection.sh

# Output:
# Basecamp 4 API Connection Test
# ==============================
# 
# Test 1: Fetching user profile...
# ✓ Successfully connected to API
#   User: Victor Cooper
# 
# Test 2: Fetching projects list...
# ✓ Successfully fetched projects
#   Total projects: 5
# 
# Test 3: Checking rate limit headers...
# ✓ Rate limit header present
#   Remaining requests: 47
# 
# All connection tests passed!
```

**Exit Codes:**
- `0`: All tests passed
- `1`: Configuration invalid or API connection failed

---

### 3. setup.sh

Comprehensive setup validation with detailed diagnostics.

```bash
./scripts/setup.sh

# Output:
# Basecamp 4 API Setup Validation
# ================================
# 
# ✓ .env file found
# ✓ ACCESS_TOKEN configured
# ✓ ACCOUNT_ID configured (195539477)
# 
# Testing API connection...
# ✓ API connection successful
# 
# Account Information:
# ====================
# Account ID: 195539477
# User: Victor Cooper (victor@honchodesign.com)
# Admin: true
# 
# Setup complete! You can now use other scripts.
```

**Exit Codes:**
- `0`: Setup successful
- `1`: .env file not found
- `2`: ACCESS_TOKEN not set
- `3`: ACCOUNT_ID invalid or missing
- `4`: API connection failed

---

## Project Operations

### 4. list_projects.sh

List all projects with status and metadata.

```bash
./scripts/list_projects.sh                # All projects
./scripts/list_projects.sh active         # Active only
./scripts/list_projects.sh archived       # Archived only

# Output:
# Fetching projects...
# 
# Total Projects: 5
# 
# ID            | Name                                    | Status     | Created
# ==============|=========================================|============|============
# 2085958499    | The Leto Laptop                         | Active     | 2024-01-15
# 2085958500    | Q4 2024 Launch                          | Active     | 2024-10-01
# 2085958501    | Legacy Project                          | Archived   | 2023-01-01
# ...
# 
# Tip: Use './scripts/get_project_tools.sh <PROJECT_ID>' to get tool IDs
```

**Parameters:**
- `all`: Show all projects (default)
- `active`: Show active projects only
- `archived`: Show archived projects only

---

### 5. get_project_tools.sh

Extract dock tool IDs from a project.

```bash
./scripts/get_project_tools.sh 2085958499

# Output:
# Project: The Leto Laptop (2085958499)
# 
# Enabled Tools:
# ==============
# message_board: 1069479338
# todoset: 1069479339
# vault: 1069479340
# chat: 1069479341
# schedule: 1069479342
# 
# Disabled Tools:
# ===============
# questionnaire: 1069479343
# inbox: 1069479344
# kanban_board: 1069479345
# 
# Export commands:
# export MESSAGE_BOARD_ID=1069479338
# export TODOSET_ID=1069479339
# export VAULT_ID=1069479340
```

**Usage:**
```bash
./scripts/get_project_tools.sh <PROJECT_ID>

# Capture tool IDs for use in other scripts:
eval $(./scripts/get_project_tools.sh 2085958499 | grep "^export")
echo "Using MESSAGE_BOARD_ID: $MESSAGE_BOARD_ID"
```

**Exit Codes:**
- `0`: Success
- `1`: PROJECT_ID not provided
- `2`: Project not found

---

## Content Operations

### 6. post_message.sh

Post a message to a project's message board.

```bash
./scripts/post_message.sh 2085958499 1069479338 "Team announcement: Project kickoff tomorrow at 10am"

# Output:
# Posting message to project 2085958499...
# ✓ Message posted successfully
# 
# Message ID: 1234567890
# URL: https://3.basecampapi.com/195539477/projects/2085958499/messages/1069479338
```

**Usage:**
```bash
# Get the message board ID first
PROJECT_ID=2085958499
BOARD_ID=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: MyApp" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json | \
  jq -r '.dock[] | select(.name=="message_board") | .id')

# Post the message
./scripts/post_message.sh $PROJECT_ID $BOARD_ID "Your message text"
```

**Parameters:**
- `PROJECT_ID`: The project ID (numeric)
- `MESSAGE_BOARD_ID`: The message board tool ID (numeric)
- `MESSAGE_TEXT`: The message content (string)

**Exit Codes:**
- `0`: Message posted successfully
- `1`: Missing required parameters or API error

---

### 7. create_document.sh

Create a document in a project's vault.

```bash
./scripts/create_document.sh 2085958499 1069479340 "Q4 Project Plan" "This document outlines our Q4 goals and timelines..."

# Output:
# Creating document in project 2085958499...
# ✓ Document created successfully
# 
# Document ID: 9876543210
# Name: Q4 Project Plan
# URL: https://3.basecampapi.com/195539477/projects/2085958499/documents/9876543210
```

**Usage:**
```bash
# Get the vault ID first
PROJECT_ID=2085958499
VAULT_ID=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: MyApp" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json | \
  jq -r '.dock[] | select(.name=="vault") | .id')

# Create the document
./scripts/create_document.sh $PROJECT_ID $VAULT_ID "Doc Title" "Doc content..."
```

**Parameters:**
- `PROJECT_ID`: The project ID (numeric)
- `VAULT_ID`: The vault tool ID (numeric)
- `DOCUMENT_NAME`: Document title (string)
- `DOCUMENT_CONTENT`: Document content in plain text or HTML (string)

**Exit Codes:**
- `0`: Document created successfully
- `1`: Missing required parameters or API error

---

## Common Workflows

### Workflow 1: Complete Project Setup

```bash
# 1. Validate configuration
./scripts/validate_config.sh

# 2. Test connection
./scripts/test_connection.sh

# 3. List available projects
./scripts/list_projects.sh active

# 4. Get tool IDs for specific project
./scripts/get_project_tools.sh 2085958499

# 5. Post an announcement
./scripts/post_message.sh 2085958499 1069479338 "Project kickoff today!"

# 6. Create project documentation
./scripts/create_document.sh 2085958499 1069479340 "Project Charter" "Team charter and goals..."
```

### Workflow 2: Automated Reporting

```bash
#!/bin/bash
# Save project status to file

PROJECT_ID=2085958499
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
REPORT_FILE="project_status_${TIMESTAMP}.txt"

{
  echo "=== Project Status Report ==="
  echo "Generated: $(date)"
  echo
  echo "Configuration Status:"
  ./scripts/validate_config.sh
  echo
  echo "API Connection Status:"
  ./scripts/test_connection.sh
} > "$REPORT_FILE"

echo "Report saved to $REPORT_FILE"
```

### Workflow 3: Bulk Tool ID Export

```bash
#!/bin/bash
# Export tool IDs from all active projects

./scripts/list_projects.sh active | grep -oE '^[0-9]+' | while read PROJECT_ID; do
  echo "Project: $PROJECT_ID"
  eval $(./scripts/get_project_tools.sh $PROJECT_ID | grep "^export")
  echo "  MESSAGE_BOARD: $MESSAGE_BOARD_ID"
  echo "  VAULT: $VAULT_ID"
  echo
done
```

---

## Error Handling

All scripts include proper error handling with informative messages:

```bash
# Missing .env file
$ ./scripts/validate_config.sh
✗ .env file not found
Configuration has 1 error(s)

# Invalid ACCOUNT_ID
$ ./scripts/setup.sh
✗ ACCOUNT_ID must be numeric

# API connection failure
$ ./scripts/test_connection.sh
✗ API connection failed (HTTP 401)
{
  "error": "Unauthorized"
}
```

---

## Rate Limiting

All scripts respect Basecamp's rate limits (50 requests per 10 seconds):

- Scripts check the `X-Ratelimit-Remaining` header
- Long-running operations add delays between requests
- The `test_connection.sh` displays current remaining quota

**For bulk operations:**
```bash
# Safe batch processing
for PROJECT_ID in 2085958499 2085958500 2085958501; do
  ./scripts/get_project_tools.sh $PROJECT_ID
  sleep 1  # Add delay between requests
done
```

---

## Troubleshooting

### Scripts hang or timeout
- Check internet connection
- Verify API is responding: `curl https://3.basecampapi.com/`
- Check if API is in maintenance

### Authentication errors (401)
- Verify ACCESS_TOKEN is valid: `./scripts/setup.sh`
- Check if token has expired
- Re-generate token in Launchpad

### Resource not found (404)
- Verify PROJECT_ID, ACCOUNT_ID, and tool IDs are correct
- Use `get_project_tools.sh` to get fresh tool IDs
- Check if resource was deleted or archived

### Rate limit errors (429)
- Add delays between requests: `sleep 1` or `sleep 2`
- Reduce batch size for bulk operations
- Check `X-Ratelimit-Remaining` header: `./scripts/test_connection.sh`

---

## Dependencies

All scripts require:
- **bash** (version 4+)
- **curl** (for HTTP requests)
- **jq** (for JSON parsing)

Install on macOS:
```bash
brew install curl jq
```

Install on Ubuntu/Debian:
```bash
sudo apt-get install curl jq
```

---

## Best Practices

1. **Always validate first**: Run `validate_config.sh` before deploying
2. **Test connectivity**: Use `test_connection.sh` to verify API access
3. **Capture tool IDs**: Use `get_project_tools.sh` to get fresh IDs
4. **Add error handling**: Always check exit codes in your workflows
5. **Rate limit handling**: Add delays between rapid requests
6. **Secure credentials**: Never commit `.env` files to version control

---

## Integration Examples

### With cron (scheduled tasks)
```bash
# /etc/cron.d/basecamp-tasks
0 9 * * MON /home/user/basecamp-assistant/scripts/post_message.sh \
  2085958499 1069479338 "Monday standup reminder"
```

### With Python
```python
import subprocess
import json

# Get projects
result = subprocess.run(
    ['./scripts/list_projects.sh'],
    capture_output=True,
    text=True
)
print(result.stdout)
```

### With GitHub Actions
```yaml
- name: Basecamp API Health Check
  run: |
    cd basecamp-assistant
    ./scripts/validate_config.sh
    ./scripts/test_connection.sh
```

---

## Support

For issues or questions:
1. Check the relevant reference documentation in `../references/`
2. Review error messages carefully
3. Consult the Basecamp 4 API documentation
4. Enable verbose output: `set -x` in scripts

---

**Created by:** Basecamp 4 API Skill Configuration Generator  
**Last Modified:** November 11, 2025  
**License:** MIT  
