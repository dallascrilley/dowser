# Basecamp 4 API - Workflow Patterns

**Last Updated:** November 11, 2025
**Purpose:** Complete examples of common multi-step workflows
**Skill Level:** Intermediate to Advanced

---

## Table of Contents

1. [Project Setup Workflow](#project-setup-workflow)
2. [Content Publishing Workflow](#content-publishing-workflow)
3. [Data Collection Workflow](#data-collection-workflow)
4. [Member Management Workflow](#member-management-workflow)
5. [Bulk Operations Workflow](#bulk-operations-workflow)
6. [Organize Documents in Nested Vaults](#organize-documents-workflow)
7. [Error Recovery Patterns](#error-recovery-patterns)

---

## Project Setup Workflow

**Objective:** Create a complete project with initial structure, welcome message, and team members

**Steps:**
1. Create project and capture dock IDs
2. Post welcome message
3. Create initial document structure
4. Add team members

### Complete Script

```bash
#!/bin/bash
set -e

# Load configuration
source .env

# Validate setup
if [ -z "$ACCESS_TOKEN" ] || [ -z "$ACCOUNT_ID" ] || [ -z "$USER_AGENT" ]; then
  echo "Error: Missing required environment variables"
  exit 1
fi

# Color output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Basecamp Project Setup ===${NC}\n"

# Step 1: Create Project
echo -e "${BLUE}Step 1: Creating project...${NC}"

project_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "name": "Q4 2024 Launch",
    "description": "Product launch and marketing campaign for Q4"
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects.json")

# Extract IDs
PROJECT_ID=$(echo "$project_json" | jq -r '.id')
MESSAGE_BOARD_ID=$(echo "$project_json" | jq -r '.dock[] | select(.name=="message_board") | .id')
VAULT_ID=$(echo "$project_json" | jq -r '.dock[] | select(.name=="vault") | .id')
TODOSET_ID=$(echo "$project_json" | jq -r '.dock[] | select(.name=="todoset") | .id')

echo -e "${GREEN}✓ Project created: $PROJECT_ID${NC}"
echo "  - Message Board ID: $MESSAGE_BOARD_ID"
echo "  - Vault ID: $VAULT_ID"
echo "  - To-Do Set ID: $TODOSET_ID"
echo ""

# Step 2: Post Welcome Message
echo -e "${BLUE}Step 2: Posting welcome message...${NC}"

message_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "subject": "Welcome to Q4 2024 Launch Project!",
    "content": "<div><h2>Project Kickoff</h2><p>Welcome to the Q4 2024 launch project. This is where we will coordinate all marketing and product efforts for the Q4 release.</p><p><strong>First Team Meeting:</strong> Monday 10am in conference room</p></div>",
    "status": "active"
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json")

MESSAGE_ID=$(echo "$message_json" | jq -r '.id')
echo -e "${GREEN}✓ Welcome message posted: $MESSAGE_ID${NC}\n"

# Step 3: Create Document Structure
echo -e "${BLUE}Step 3: Creating document structure...${NC}"

# Create Design folder
design_vault_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Design Assets"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/vaults.json")

DESIGN_VAULT_ID=$(echo "$design_vault_json" | jq -r '.id')
echo -e "${GREEN}✓ Created Design Assets folder: $DESIGN_VAULT_ID${NC}"

# Create Marketing folder
marketing_vault_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Marketing Materials"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/vaults.json")

MARKETING_VAULT_ID=$(echo "$marketing_vault_json" | jq -r '.id')
echo -e "${GREEN}✓ Created Marketing Materials folder: $MARKETING_VAULT_ID${NC}"

# Create Project Brief document
brief_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "title": "Project Brief",
    "content": "<h1>Q4 2024 Launch - Project Brief</h1><h2>Overview</h2><p>Product launch for Q4 2024 with focus on marketing and customer acquisition.</p><h2>Timeline</h2><ul><li>Design phase: September-October</li><li>Development: October-November</li><li>Launch: December 1st</li></ul><h2>Success Metrics</h2><ul><li>1000 new signups</li><li>50% increase in website traffic</li><li>PR coverage in 5+ publications</li></ul>",
    "status": "active"
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/documents.json")

BRIEF_ID=$(echo "$brief_json" | jq -r '.id')
echo -e "${GREEN}✓ Created Project Brief: $BRIEF_ID${NC}\n"

# Step 4: Add Team Members
echo -e "${BLUE}Step 4: Adding team members...${NC}"

members_json=$(curl -s -X PUT \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "grant": [1049715914, 1049715915, 1049715916],
    "create": [
      {
        "name": "Jane Marketing Manager",
        "email_address": "jane.marketing@company.com",
        "title": "Marketing Manager"
      },
      {
        "name": "Bob Design Lead",
        "email_address": "bob.design@company.com",
        "title": "Design Lead"
      }
    ]
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people/users.json")

echo -e "${GREEN}✓ Team members added${NC}\n"

# Final Summary
echo -e "${BLUE}=== Project Setup Complete ===${NC}"
echo -e "${GREEN}Project ID:${NC} $PROJECT_ID"
echo -e "${GREEN}Project URL:${NC} https://3.basecamp.com/$ACCOUNT_ID/projects/$PROJECT_ID"
echo ""
echo "Documents created:"
echo "  - Design Assets folder ($DESIGN_VAULT_ID)"
echo "  - Marketing Materials folder ($MARKETING_VAULT_ID)"
echo "  - Project Brief ($BRIEF_ID)"
echo ""
echo "Ready for team collaboration!"
```

### Key Points

- **Error Handling:** Uses `set -e` to exit on first error
- **ID Extraction:** All IDs captured from API responses for subsequent calls
- **Validation:** Configuration checked at start
- **User Feedback:** Clear progress indicators
- **Idempotency:** Can be modified to check if project exists first

### Gotchas

- **Tool IDs:** Must extract from dock array, don't hardcode
- **HTML Content:** Ensure proper formatting and allowed tags
- **Email Validation:** API will accept invalid emails; validate before sending

---

## Content Publishing Workflow

**Objective:** Upload files and create documents with embedded attachments, then publish announcement

**Steps:**
1. Upload attachment file
2. Create document with embedded attachment
3. Post announcement message with link

### Complete Script

```bash
#!/bin/bash
set -e

source .env

PROJECT_ID="2085958499"
VAULT_ID="1069479340"
MESSAGE_BOARD_ID="1069479338"

echo "Publishing content with attachments..."

# Step 1: Upload Attachment
echo "Step 1: Uploading image file..."

# Create temporary test image (1x1 pixel PNG)
echo -n -e '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82' > /tmp/logo.png

attachment_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: image/png" \
  -H "Content-Length: $(wc -c < /tmp/logo.png)" \
  --data-binary "@/tmp/logo.png" \
  "https://3.basecampapi.com/$ACCOUNT_ID/attachments.json?name=logo.png")

SGID=$(echo "$attachment_json" | jq -r '.attachable_sgid')
echo "✓ Attachment uploaded: $SGID"

# Step 2: Create Document with Attachment
echo "Step 2: Creating document with attachment..."

# Properly escape JSON for embedded document
doc_content="<div><h1>New Logo Design</h1><p>Here's the new logo design for the Q4 campaign:</p><bc-attachment sgid=\"$SGID\"></bc-attachment><p><strong>Design notes:</strong> Modern, clean aesthetic suitable for all marketing materials.</p></div>"

# Create document with embedded attachment
doc_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d "{\"title\":\"New Logo Design\",\"content\":\"$doc_content\",\"status\":\"active\"}" \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/documents.json")

DOC_ID=$(echo "$doc_json" | jq -r '.id')
DOC_URL=$(echo "$doc_json" | jq -r '.app_url')
echo "✓ Document created: $DOC_ID"
echo "  URL: $DOC_URL"

# Step 3: Post Announcement
echo "Step 3: Posting announcement message..."

announcement_content="<div><h2>New Logo Design Available</h2><p>Check out the new logo design for our Q4 campaign in the <a href=\"$DOC_URL\">Design Assets</a> folder.</p><p>The design team has created a modern, clean aesthetic that will work across all marketing materials. Please review and provide feedback by Friday.</p></div>"

message_json=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d "{\"subject\":\"New Logo Design Available\",\"content\":\"$announcement_content\",\"status\":\"active\"}" \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/message_boards/$MESSAGE_BOARD_ID/messages.json")

MESSAGE_ID=$(echo "$message_json" | jq -r '.id')
echo "✓ Announcement posted: $MESSAGE_ID"

echo ""
echo "=== Content Publishing Complete ==="
echo "Document: $DOC_URL"
echo "Message ID: $MESSAGE_ID"

# Cleanup
rm /tmp/logo.png
```

### Key Points

- **Attachment Upload:** Use `--data-binary` for file uploads, proper Content-Type
- **SGID Extraction:** Get from attachment response, use in bc-attachment tag
- **HTML Escaping:** Properly escape quotes in JSON content
- **Links:** Use relative or absolute URLs in HTML

### Pitfall Alert

- **Reusing Attachments:** Never reuse SGID from other elements - always upload new
- **Content-Type:** Must specify correct MIME type or images won't display inline

---

## Data Collection Workflow

**Objective:** Fetch all projects and messages with proper pagination

**Steps:**
1. List all projects with pagination
2. For each project, collect all messages
3. Aggregate results

### Complete Script

```bash
#!/bin/bash
set -e

source .env

echo "Collecting all project and message data..."

# Initialize results
all_projects="[]"
all_messages="[]"

# Step 1: Fetch All Projects (with pagination)
echo "Step 1: Fetching all projects..."

next_url="https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
page=1

while [ ! -z "$next_url" ]; do
  echo "  - Fetching projects page $page..."

  response=$(curl -s -i \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "User-Agent: $USER_AGENT" \
    "$next_url")

  # Extract body (starts with [)
  body=$(echo "$response" | sed -n '/^\[/,$p')

  # Merge into all_projects
  all_projects=$(echo "$all_projects" "$body" | jq -s 'add')

  # Extract next URL from Link header
  next_url=$(echo "$response" | grep -i "^Link:" | \
    sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')

  page=$((page + 1))
done

project_count=$(echo "$all_projects" | jq 'length')
echo "✓ Fetched $project_count projects"

# Step 2: For Each Project, Fetch Messages
echo "Step 2: Fetching messages for each project..."

echo "$all_projects" | jq -r '.[] | .id' | while read project_id; do
  project_name=$(echo "$all_projects" | jq -r ".[] | select(.id==$project_id) | .name")
  echo "  - Processing project: $project_name ($project_id)"

  # Get message board ID from dock
  message_board_id=$(echo "$all_projects" | jq -r ".[] | select(.id==$project_id) | .dock[] | select(.name==\"message_board\") | .id")

  if [ -z "$message_board_id" ] || [ "$message_board_id" = "null" ]; then
    echo "    (no message board)"
    return
  fi

  # Fetch all messages for this project (with pagination)
  next_url="https://3.basecampapi.com/$ACCOUNT_ID/buckets/$project_id/message_boards/$message_board_id/messages.json"
  message_page=1

  while [ ! -z "$next_url" ]; do
    response=$(curl -s -i \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "User-Agent: $USER_AGENT" \
      "$next_url")

    body=$(echo "$response" | sed -n '/^\[/,$p')

    # Tag messages with project ID for tracking
    body=$(echo "$body" | jq --arg proj_id "$project_id" '.[] += {project_id: ($proj_id | tonumber)}')

    # Merge messages
    all_messages=$(echo "$all_messages" "$body" | jq -s 'add')

    # Get next URL
    next_url=$(echo "$response" | grep -i "^Link:" | \
      sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')

    message_page=$((message_page + 1))
  done

  echo "    ✓ Fetched $(echo "$body" | jq 'length') messages"
done

# Step 3: Generate Report
echo ""
echo "=== Data Collection Complete ==="
echo "Total projects: $project_count"
echo "Total messages: $(echo "$all_messages" | jq 'length')"

# Show sample
echo ""
echo "Sample data (first 5 messages):"
echo "$all_messages" | jq '.[0:5] | .[] | {project_id, subject, created_at}' | head -20

# Save to file for analysis
echo "$all_projects" > projects.json
echo "$all_messages" > messages.json
echo ""
echo "Data saved to:"
echo "  - projects.json"
echo "  - messages.json"
```

### Key Points

- **Pagination:** Always follow Link header, never construct URLs
- **Header Extraction:** Use grep with regex to find Link header
- **Data Aggregation:** Use jq to merge arrays
- **Progress Tracking:** Show page numbers and counts
- **Persistence:** Save results to files

### Error Scenarios

If pagination fails:
- Check for empty Link header (end of list)
- Verify URL is properly formatted
- Add safety limit to prevent infinite loops

---

## Member Management Workflow

**Objective:** Add multiple team members to projects, handling new and existing users

**Steps:**
1. Get all existing people in account
2. Identify who needs access
3. Create new people if needed
4. Grant access to projects

### Complete Script

```bash
#!/bin/bash
set -e

source .env

PROJECT_ID="2085958499"

echo "Managing project members..."

# Step 1: Get existing people
echo "Step 1: Fetching existing account members..."

existing_people=$(curl -s \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  "https://3.basecampapi.com/$ACCOUNT_ID/people.json")

existing_count=$(echo "$existing_people" | jq 'length')
echo "✓ Found $existing_count existing members"

# Step 2: Define team to add
echo "Step 2: Processing new team members..."

declare -a new_members=(
  "Sarah Developer:sarah.dev@company.com:Developer"
  "Mike Manager:mike.manager@company.com:Project Manager"
  "Lisa Designer:lisa.designer@company.com:Designer"
)

grant_ids=()
create_members=()

for member_info in "${new_members[@]}"; do
  IFS=':' read -r name email title <<< "$member_info"

  # Check if person already exists
  person_id=$(echo "$existing_people" | jq -r ".[] | select(.email_address==\"$email\") | .id")

  if [ ! -z "$person_id" ] && [ "$person_id" != "null" ]; then
    echo "  ✓ $name ($email) - Already exists (ID: $person_id)"
    grant_ids+=("$person_id")
  else
    echo "  + $name ($email) - Will be created"
    create_members+=("{\"name\":\"$name\",\"email_address\":\"$email\",\"title\":\"$title\"}")
  fi
done

# Step 3: Apply access changes
echo "Step 3: Applying access changes..."

# Build request JSON
request_body="{"

# Add grant IDs if any
if [ ${#grant_ids[@]} -gt 0 ]; then
  grant_json=$(IFS=,; echo "${grant_ids[*]}")
  request_body="$request_body\"grant\":[$grant_json]"
fi

# Add new members if any
if [ ${#create_members[@]} -gt 0 ]; then
  # Add comma if grant already added
  if [ ${#grant_ids[@]} -gt 0 ]; then
    request_body="$request_body,"
  fi

  # Join create members with comma
  create_json=$(IFS=,; echo "${create_members[*]}")
  request_body="$request_body\"create\":[$create_json]"
fi

request_body="$request_body}"

echo "Request: $request_body"

# Send request
result=$(curl -s -X PUT \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d "$request_body" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people/users.json")

echo "✓ Access granted to $(echo "$result" | jq '.grants | length') members"

# Step 4: Verify
echo "Step 4: Verifying project membership..."

project_members=$(curl -s \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  "https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/people.json")

member_list=$(echo "$project_members" | jq -r '.[] | .name + " (" + .email_address + ")"')

echo ""
echo "=== Project Team ==="
echo "$member_list"
echo ""
echo "Total: $(echo "$project_members" | jq 'length') members"
```

### Key Points

- **Batch Operations:** Combine grant and create in single request
- **Email Lookup:** Check if person exists before creating
- **Error Handling:** Request can partially succeed
- **Verification:** Always verify after granting access

---

## Organize Documents Workflow

**Objective:** Create hierarchical folder structure for document organization

**Steps:**
1. Create main folders
2. Create sub-folders
3. Create documents in appropriate folders

### Complete Script

```bash
#!/bin/bash
set -e

source .env

PROJECT_ID="2085958499"
VAULT_ID="1069479340"

echo "Creating document structure..."

# Define folder structure
declare -A folders

# Step 1: Create main folders
echo "Step 1: Creating main folders..."

folders[design]=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Design"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/vaults.json" | jq -r '.id')

folders[marketing]=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Marketing"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/vaults.json" | jq -r '.id')

folders[development]=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Development"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$VAULT_ID/vaults.json" | jq -r '.id')

echo "✓ Created main folders"

# Step 2: Create subfolders
echo "Step 2: Creating subfolders..."

# Design subfolders
design_branding=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Branding"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/${folders[design]}/vaults.json" | jq -r '.id')

design_mockups=$(curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{"title":"Mockups"}' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/${folders[design]}/vaults.json" | jq -r '.id')

echo "✓ Created subfolders"

# Step 3: Add documents
echo "Step 3: Adding documents..."

# Brand guidelines in Branding subfolder
curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "title":"Brand Guidelines",
    "content":"<h1>Brand Guidelines</h1><h2>Colors</h2><ul><li>Primary: #FF6B35</li><li>Secondary: #004E89</li></ul><h2>Typography</h2><p>Use Open Sans for headers, Roboto for body text</p>",
    "status":"active"
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/$design_branding/documents.json"

echo "✓ Added Brand Guidelines"

# Marketing calendar
curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -H "User-Agent: $USER_AGENT" \
  -d '{
    "title":"Marketing Calendar",
    "content":"<h1>Q4 Marketing Calendar</h1><p>Key dates and campaign launches...</p>",
    "status":"active"
  }' \
  "https://3.basecampapi.com/$ACCOUNT_ID/buckets/$PROJECT_ID/vaults/${folders[marketing]}/documents.json"

echo "✓ Added Marketing Calendar"

echo ""
echo "=== Document Structure Created ==="
echo "Design folder: ${folders[design]}"
echo "  - Branding: $design_branding"
echo "  - Mockups: $design_mockups"
echo "Marketing folder: ${folders[marketing]}"
echo "Development folder: ${folders[development]}"
```

### Key Points

- **Hierarchical Structure:** Create parent first, then children
- **Nesting URLs:** Use parent vault ID in POST URL for subfolders
- **Document Placement:** Target specific folder vault ID
- **Organization:** Makes content discoverable and maintainable

---

## Error Recovery Patterns

### Pattern 1: Handle Rate Limits with Exponential Backoff

```bash
make_request_with_retry() {
  local url=$1
  local method=${2:-GET}
  local data=$3
  local max_retries=5
  local retry_count=0
  local backoff=1

  while [ $retry_count -lt $max_retries ]; do
    # Make request
    if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
      response=$(curl -s -i -w "\n%{http_code}" -X "$method" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json; charset=utf-8" \
        -H "User-Agent: $USER_AGENT" \
        -d "$data" \
        "$url")
    else
      response=$(curl -s -i -w "\n%{http_code}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "User-Agent: $USER_AGENT" \
        "$url")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "204" ]; then
      echo "$body"
      return 0
    elif [ "$http_code" = "429" ]; then
      # Rate limited - check Retry-After header
      retry_after=$(echo "$response" | grep -i "^Retry-After:" | awk '{print $2}' | tr -d '\r')

      if [ ! -z "$retry_after" ]; then
        echo "Rate limited. Waiting ${retry_after}s..." >&2
        sleep $retry_after
      else
        echo "Rate limited. Waiting ${backoff}s (exponential backoff)..." >&2
        sleep $backoff
        backoff=$((backoff * 2))
        [ $backoff -gt 30 ] && backoff=30  # Cap at 30 seconds
      fi

      retry_count=$((retry_count + 1))
    elif [ "$http_code" = "404" ]; then
      # Permanent failure - check reason
      reason=$(echo "$response" | grep -i "^Reason:" | cut -d' ' -f2- | tr -d '\r')
      echo "Error: Resource not found (404)" >&2
      [ ! -z "$reason" ] && echo "Reason: $reason" >&2
      return 1
    elif [ $http_code -ge 500 ]; then
      # Server error - retry with backoff
      echo "Server error $http_code. Waiting ${backoff}s..." >&2
      sleep $backoff
      backoff=$((backoff * 2))
      [ $backoff -gt 30 ] && backoff=30
      retry_count=$((retry_count + 1))
    else
      # Other errors - don't retry
      echo "Error: HTTP $http_code" >&2
      echo "$body" >&2
      return 1
    fi
  done

  echo "Max retries exceeded" >&2
  return 1
}
```

### Pattern 2: Validate Setup Before Operations

```bash
validate_setup() {
  # Check environment
  if [ -z "$ACCESS_TOKEN" ] || [ -z "$ACCOUNT_ID" ] || [ -z "$USER_AGENT" ]; then
    echo "Error: Missing required environment variables"
    echo "Please set ACCESS_TOKEN, ACCOUNT_ID, and USER_AGENT"
    return 1
  fi

  # Test API connection
  response=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "User-Agent: $USER_AGENT" \
    "https://3.basecampapi.com/$ACCOUNT_ID/my/profile.json")

  http_code=$(echo "$response" | tail -n1)

  if [ "$http_code" != "200" ]; then
    echo "Error: Authentication failed (HTTP $http_code)"
    echo "Check your ACCESS_TOKEN and ACCOUNT_ID"
    return 1
  fi

  echo "✓ Setup validated"
  return 0
}
```

### Pattern 3: Handle Pagination Safely

```bash
fetch_all_pages() {
  local initial_url=$1
  local url="$initial_url"
  local all_data="[]"
  local page_count=0
  local max_pages=1000  # Safety limit

  while [ ! -z "$url" ] && [ $page_count -lt $max_pages ]; do
    # Fetch page
    response=$(curl -s -i \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "User-Agent: $USER_AGENT" \
      "$url")

    # Extract body
    body=$(echo "$response" | sed -n '/^\[/,$p')
    http_code=$(echo "$response" | head -1 | awk '{print $2}')

    if [ "$http_code" != "200" ]; then
      echo "Error fetching page $page_count: HTTP $http_code" >&2
      return 1
    fi

    # Merge data
    all_data=$(echo "$all_data" "$body" | jq -s 'add')

    # Get next URL from Link header
    url=$(echo "$response" | grep -i "^Link:" | \
      sed -n 's/.*<\(.*\)>; rel="next".*/\1/p')

    page_count=$((page_count + 1))
  done

  if [ $page_count -ge $max_pages ]; then
    echo "Warning: Reached maximum page limit ($max_pages)" >&2
  fi

  echo "$all_data"
}
```

---

## Related Documentation

- [API Reference](./api-reference.md) - Detailed endpoint reference
- [Error Handling](./error-handling.md) - Error recovery strategies
- [Rate Limiting](./rate-limiting.md) - Rate limit management
- [Pagination](./pagination.md) - Advanced pagination techniques

---

**For questions or issues:** Consult the [Basecamp API Documentation](https://github.com/basecamp/bc4-api)
