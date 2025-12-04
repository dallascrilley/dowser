#!/bin/bash
set -e

# Load environment
source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Usage: $0 <PROJECT_ID> <MESSAGE_BOARD_ID> <MESSAGE_TEXT>"
  echo
  echo "Example:"
  echo "  $0 2085958499 1069479338 'Hello team!'"
  echo
  echo "To get MESSAGE_BOARD_ID, run:"
  echo "  ./scripts/get_project_tools.sh <PROJECT_ID>"
  exit 1
fi

PROJECT_ID=$1
MESSAGE_BOARD_ID=$2
MESSAGE_TEXT=$3

# Set default USER_AGENT if not set
USER_AGENT=${USER_AGENT:-"Basecamp API Script (api@example.com)"}

echo "Posting message to project $PROJECT_ID..."

# Create JSON payload
PAYLOAD=$(jq -n \
  --arg content "$MESSAGE_TEXT" \
  '{subject: "Message", content: $content}')

# Post message
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$PAYLOAD" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/messages.json)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "201" ]; then
  echo -e "${RED}Error: Failed to post message (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 1
fi

# Display success
MESSAGE_ID=$(echo "$BODY" | jq -r '.id')
MESSAGE_URL=$(echo "$BODY" | jq -r '.url')

echo -e "${GREEN}✓ Message posted successfully${NC}"
echo
echo "Message ID: $MESSAGE_ID"
echo "URL: $MESSAGE_URL"
