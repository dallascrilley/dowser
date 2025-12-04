#!/bin/bash
set -e

# Load environment
source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
  echo "Usage: $0 <PROJECT_ID> <VAULT_ID> <DOCUMENT_NAME> <DOCUMENT_CONTENT>"
  echo
  echo "Example:"
  echo "  $0 2085958499 1069479340 'Project Plan' 'This is our project plan...'"
  echo
  echo "To get VAULT_ID, run:"
  echo "  ./scripts/get_project_tools.sh <PROJECT_ID>"
  exit 1
fi

PROJECT_ID=$1
VAULT_ID=$2
DOCUMENT_NAME=$3
DOCUMENT_CONTENT=$4

# Set default USER_AGENT if not set
USER_AGENT=${USER_AGENT:-"Basecamp API Script (api@example.com)"}

echo "Creating document in project $PROJECT_ID..."

# Create JSON payload
PAYLOAD=$(jq -n \
  --arg title "$DOCUMENT_NAME" \
  --arg content "$DOCUMENT_CONTENT" \
  '{title: $title, content: $content}')

# Post document
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "$PAYLOAD" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects/$PROJECT_ID/documents.json)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "201" ]; then
  echo -e "${RED}Error: Failed to create document (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 1
fi

# Display success
DOCUMENT_ID=$(echo "$BODY" | jq -r '.id')
DOCUMENT_URL=$(echo "$BODY" | jq -r '.url')

echo -e "${GREEN}✓ Document created successfully${NC}"
echo
echo "Document ID: $DOCUMENT_ID"
echo "Name: $DOCUMENT_NAME"
echo "URL: $DOCUMENT_URL"
