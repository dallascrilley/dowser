# Basecamp 4 API Skill - Complete Index

**Last Updated:** November 11, 2025  
**Status:** PRODUCTION READY  
**Completion:** 100%  

---

## Navigation Guide

### Quick Links

- **Getting Started**: Start with `scripts/setup.sh` and `scripts/README.md`
- **Configuration**: Copy appropriate template from `templates/`
- **API Reference**: Read `references/api-reference.md`
- **Common Issues**: Check `references/error-handling.md`
- **Rate Limits**: Review `references/rate-limiting.md`
- **Workflows**: Study `references/workflow-patterns.md`
- **Pagination**: Learn `references/pagination.md`

---

## Files by Category

### Configuration Templates (`templates/`)

| File | Size | Purpose | When to Use |
|------|------|---------|------------|
| `basic.env.template` | 1.7 KB | Minimal setup | First-time integration |
| `development.env.template` | 3.2 KB | Dev environment | Local development |
| `production.env.template` | 6.8 KB | Production config | Deployment & monitoring |

**How to use:**
1. Copy the appropriate template: `cp templates/basic.env.template .env`
2. Edit `.env` with your ACCESS_TOKEN and ACCOUNT_ID
3. Run `./scripts/validate_config.sh` to verify

---

### Reference Documentation (`references/`)

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| `api-reference.md` | 22.4 KB | 750 | Complete endpoint documentation |
| `workflow-patterns.md` | 25.7 KB | 800 | Multi-step workflow examples |
| `error-handling.md` | 21.0 KB | 700 | HTTP codes & recovery strategies |
| `rate-limiting.md` | 18.7 KB | 600 | Rate limit management |
| `pagination.md` | 19.2 KB | 650 | RFC5988 Link header patterns |

**How to use:**
- **Building anything**: Start with `api-reference.md`
- **Multi-step operations**: Read `workflow-patterns.md`
- **API failures**: Consult `error-handling.md`
- **High-volume requests**: Review `rate-limiting.md`
- **Fetching lists**: Study `pagination.md`

---

### Helper Scripts (`scripts/`)

#### Setup & Validation

| Script | Size | Purpose |
|--------|------|---------|
| `validate_config.sh` | 1.2 KB | Check .env configuration (quick) |
| `test_connection.sh` | 2.3 KB | Test API connectivity |
| `setup.sh` | 2.1 KB | Full validation with user info |

**Usage:**
```bash
./scripts/validate_config.sh      # Quick config check
./scripts/test_connection.sh      # Verify API access
./scripts/setup.sh                # Complete setup validation
```

#### Project Operations

| Script | Size | Purpose |
|--------|------|---------|
| `list_projects.sh` | 1.7 KB | List all projects |
| `get_project_tools.sh` | 1.3 KB | Extract tool IDs |

**Usage:**
```bash
./scripts/list_projects.sh              # Show all projects
./scripts/list_projects.sh active       # Active only
./scripts/get_project_tools.sh 2085958499  # Get tool IDs
```

#### Content Operations

| Script | Size | Purpose |
|--------|------|---------|
| `post_message.sh` | 1.5 KB | Post to message board |
| `create_document.sh` | 1.6 KB | Create vault document |

**Usage:**
```bash
./scripts/post_message.sh <PROJECT_ID> <BOARD_ID> "Message text"
./scripts/create_document.sh <PROJECT_ID> <VAULT_ID> "Title" "Content"
```

---

### Documentation

| File | Size | Purpose |
|------|------|---------|
| `scripts/README.md` | 14.2 KB | Complete scripts guide |
| `DELIVERABLES.md` | 18 KB | Summary of all files |
| `INDEX.md` | This file | Navigation guide |

---

## Common Tasks

### Task: Set Up Integration

1. Copy template: `cp templates/basic.env.template .env`
2. Add credentials to `.env`
3. Validate: `./scripts/validate_config.sh`
4. Test: `./scripts/test_connection.sh`
5. Read: `references/api-reference.md`

**Time:** ~5 minutes

---

### Task: Post Message to Project

1. Get project ID: `./scripts/list_projects.sh`
2. Get board ID: `./scripts/get_project_tools.sh <PROJECT_ID>`
3. Post message: `./scripts/post_message.sh <PROJECT_ID> <BOARD_ID> "Your message"`

**Time:** ~2 minutes

---

### Task: Handle API Error

1. Check HTTP status code from error
2. Look up code in: `references/error-handling.md`
3. Follow recommended recovery strategy
4. Verify rate limits: `./scripts/test_connection.sh`
5. Check logs for details

**Time:** ~5 minutes

---

### Task: Fetch Large Dataset

1. Read: `references/pagination.md`
2. Implement Link header extraction
3. Follow pattern from appropriate language example
4. Add delays per: `references/rate-limiting.md`
5. Test with small dataset first

**Time:** ~30 minutes

---

### Task: Implement Complex Workflow

1. Study similar workflow in: `references/workflow-patterns.md`
2. Reference endpoints in: `references/api-reference.md`
3. Add error handling from: `references/error-handling.md`
4. Manage rate limits per: `references/rate-limiting.md`
5. Test thoroughly before deployment

**Time:** ~2 hours

---

## Key Concepts

### Authentication
- **Method:** OAuth 2.0 Bearer tokens
- **Header:** `Authorization: Bearer {ACCESS_TOKEN}`
- **Required:** USER_AGENT header with contact info

### Endpoints
- **Base URL:** `https://3.basecampapi.com/{ACCOUNT_ID}/`
- **Format:** JSON with snake_case keys
- **Methods:** GET, POST, PUT (no PATCH)

### Rate Limiting
- **Limit:** 50 requests per 10 seconds
- **Header:** `X-Ratelimit-Remaining`
- **Backoff:** Exponential (1s, 2s, 4s, 8s, 16s)

### Resources
- **Projects:** Called "buckets" in URLs
- **Tools:** Message board, vault, to-do list, etc. (in "dock")
- **Content:** Messages, documents, to-do items

### Pagination
- **Method:** RFC5988 Link headers
- **Format:** `Link: <url>; rel="next"`
- **Variable page size:** 15, 30, 50, 100+ items

---

## File Locations

All files are in the skill directory:

```
~/.claude/skills/basecamp-assistant/
├── templates/
│   ├── basic.env.template
│   ├── development.env.template
│   └── production.env.template
├── references/
│   ├── api-reference.md
│   ├── workflow-patterns.md
│   ├── error-handling.md
│   ├── rate-limiting.md
│   └── pagination.md
├── scripts/
│   ├── setup.sh
│   ├── validate_config.sh
│   ├── test_connection.sh
│   ├── list_projects.sh
│   ├── get_project_tools.sh
│   ├── post_message.sh
│   ├── create_document.sh
│   └── README.md
├── DELIVERABLES.md
└── INDEX.md (this file)
```

---

## Code Examples Available

All reference documents include working code examples in:
- **Bash/Shell** (20+ examples)
- **Python** (15+ examples)
- **JavaScript/Node.js** (12+ examples)
- **Ruby** (5+ examples)
- **cURL** (25+ examples)

Total: **75+ working code examples**

---

## Standards & Best Practices

### Implemented
- ✓ OAuth 2.0 authentication
- ✓ Proper error handling
- ✓ Rate limit respect
- ✓ Exponential backoff
- ✓ RFC5988 pagination
- ✓ Input validation
- ✓ Colorized output
- ✓ Exit code standards

### Security
- ✓ Token validation
- ✓ HTTPS only
- ✓ .env file isolation
- ✓ User-Agent requirements
- ✓ Input sanitization

---

## Troubleshooting Guide

| Problem | Solution | Reference |
|---------|----------|-----------|
| Configuration invalid | Run `validate_config.sh` | scripts/README.md |
| Can't connect to API | Run `test_connection.sh` | scripts/README.md |
| API returns error | Check status code in | references/error-handling.md |
| Too many requests | Review rate limiting | references/rate-limiting.md |
| Pagination issue | Check Link header | references/pagination.md |
| Script permissions | Make executable: `chmod +x` | scripts/README.md |
| Wrong PROJECT_ID | Use `list_projects.sh` | scripts/README.md |
| Can't find tool ID | Use `get_project_tools.sh` | scripts/README.md |

---

## Support Resources

1. **Quick Help**: `scripts/README.md`
2. **API Details**: `references/api-reference.md`
3. **Common Issues**: `references/error-handling.md`
4. **Complete Summary**: `DELIVERABLES.md`
5. **Official Docs**: https://developer.basecamp.com/

---

## Version Information

- **Skill Version:** 1.0
- **API Version:** Basecamp 4
- **Last Updated:** November 11, 2025
- **Created By:** Configuration & Documentation Generator
- **Status:** Production Ready

---

## Quick Reference

### Files to Read First
1. This file (INDEX.md)
2. scripts/README.md
3. references/api-reference.md

### Scripts to Run First
1. ./scripts/validate_config.sh
2. ./scripts/test_connection.sh
3. ./scripts/list_projects.sh

### Most Important References
1. references/api-reference.md (70+ endpoints)
2. references/error-handling.md (all status codes)
3. references/rate-limiting.md (prevent 429 errors)

---

**Welcome to the Basecamp 4 API Skill!**

Start with `./scripts/setup.sh` for a complete verification of your setup, then refer to the relevant documentation based on your needs.
