# Basecamp 4 API Scripts - Quick Start Guide

Generated: 2025-11-11

## 30-Second Setup

```bash
# 1. Copy credentials template
cp .env.example .env

# 2. Edit with your credentials
vi .env
# Add:
#   ACCESS_TOKEN=your_oauth_token
#   ACCOUNT_ID=your_account_id
#   USER_AGENT="MyApp (me@example.com)"

# 3. Validate setup
./setup.sh

# 4. Done! You're ready to go
```

## Most Common Tasks

### List Your Projects
```bash
./list_projects.sh
```

### Post a Message to a Project
```bash
./post_message.sh 2085958499
# Then follow the prompts
```

### Create a Document
```bash
./create_document.sh 2085958499
# Then follow the prompts
```

### Get Tool IDs for a Project
```bash
./get_project_tools.sh 2085958499
```

### Test Your Connection
```bash
./test_connection.sh
```

## All Scripts at a Glance

| Script | Purpose | Command |
|--------|---------|---------|
| setup.sh | Initial validation | `./setup.sh` |
| validate_config.sh | Check .env file | `./validate_config.sh` |
| list_projects.sh | List all projects | `./list_projects.sh` |
| get_project_tools.sh | Get tool IDs | `./get_project_tools.sh <ID>` |
| post_message.sh | Post message | `./post_message.sh <ID>` |
| create_document.sh | Create document | `./create_document.sh <ID>` |
| test_connection.sh | Test API | `./test_connection.sh` |

## Getting Help

Every script has built-in help:
```bash
./setup.sh -h
./list_projects.sh --help
./post_message.sh -h
```

## Required Variables (.env)

```bash
# REQUIRED
ACCESS_TOKEN=your_oauth_token
ACCOUNT_ID=999999999

# OPTIONAL but RECOMMENDED
USER_AGENT="MyApp (me@example.com)"
```

## Common Errors & Fixes

| Error | Fix |
|-------|-----|
| "HTTP 400" | Missing USER_AGENT in .env |
| "HTTP 401" | Invalid ACCESS_TOKEN |
| "HTTP 404" | Invalid ACCOUNT_ID or PROJECT_ID |
| "Rate limit" | Scripts auto-retry; rarely an issue |

## Next Steps

1. Read [README.md](README.md) for complete documentation
2. Check the [Analysis and Design Document](../../scratchpad/2025-11-11-015402_basecamp-analysis-design/analysis-and-design.md) for API details
3. Reference the [Basecamp 4 API Cheat Sheet](../../../All_APIs/API_Docs/Basecamp%20API/Basecamp_CHEAT_SHEET.md)

## Key Concepts

- **Buckets**: Projects are called "buckets" in API URLs
- **Dock**: Array of enabled tools (message board, vault, etc.) in each project
- **Vault**: Document folder in a project
- **Tool ID**: ID for each tool (message board, vault, todoset, etc.)

## Important Reminders

1. ✓ Always include User-Agent header (scripts do this automatically)
2. ✓ Rate limit is 50 requests per 10 seconds (scripts handle this)
3. ✓ Never retry 404 errors (scripts implement this correctly)
4. ✓ Follow Link headers for pagination (scripts do this automatically)

---

**For complete documentation, see [README.md](README.md)**
