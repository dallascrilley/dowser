#!/bin/bash
set -e

# Load environment
source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Set default USER_AGENT if not set
USER_AGENT=${USER_AGENT:-"Basecamp API Script (api@example.com)"}

# Optional: Filter by status (all/active/archived)
FILTER=${1:-"all"}

echo "Fetching projects..."
echo

# Build URL with filter
if [ "$FILTER" == "active" ]; then
  URL="https://3.basecampapi.com/$ACCOUNT_ID/projects.json?status=active"
elif [ "$FILTER" == "archived" ]; then
  URL="https://3.basecampapi.com/$ACCOUNT_ID/projects.json?status=archived"
else
  URL="https://3.basecampapi.com/$ACCOUNT_ID/projects.json"
fi

# Fetch projects
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  "$URL")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo -e "${RED}Error: Failed to fetch projects (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 1
fi

# Count projects
COUNT=$(echo "$BODY" | jq 'length')
echo "Total Projects: $COUNT"
echo

# Display projects in table format
echo "ID            | Name                                    | Status     | Created"
echo "==============|=========================================|============|============"
echo "$BODY" | jq -r '.[] | "\(.id) | \(.name // "N/A")\u001b[0m | \(.archived // false | if . then "Archived" else "Active" end) | \(.created_at // "N/A")"' | while read line; do
  # Color active vs archived
  if [[ $line == *"Archived"* ]]; then
    echo -e "${YELLOW}$line${NC}"
  else
    echo -e "${GREEN}$line${NC}"
  fi
done

echo
echo "Tip: Use './scripts/get_project_tools.sh <PROJECT_ID>' to get tool IDs for a project"
