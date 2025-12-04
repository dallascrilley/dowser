#!/bin/bash
set -e

# Load environment
source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check PROJECT_ID
PROJECT_ID=$1
if [ -z "$PROJECT_ID" ]; then
  echo "Usage: $0 <PROJECT_ID>"
  exit 1
fi

# Set default USER_AGENT if not set
USER_AGENT=${USER_AGENT:-"Basecamp API Script (api@example.com)"}

# Fetch project
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID.json)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo -e "${RED}Error: Failed to fetch project (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 2
fi

# Display project info
PROJECT_NAME=$(echo "$BODY" | jq -r '.name')
echo "Project: $PROJECT_NAME ($PROJECT_ID)"
echo

# Extract enabled tools
echo "Enabled Tools:"
echo "=============="
echo "$BODY" | jq -r '.dock[] | select(.enabled == true) | "\(.name): \(.id)"' | while read line; do
  echo -e "${GREEN}$line${NC}"
done

echo
echo "Disabled Tools:"
echo "==============="
echo "$BODY" | jq -r '.dock[] | select(.enabled == false) | "\(.name): \(.id)"'

echo
echo "Export commands:"
echo "$BODY" | jq -r '.dock[] | select(.enabled == true) | "export \(.name | ascii_upcase)_ID=\(.id)"'
