#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Basecamp 4 API Setup Validation"
echo "================================"
echo

# Step 1: Check .env file
if [ ! -f .env ]; then
  echo -e "${RED}✗ .env file not found${NC}"
  echo "  Create .env file from .env.example"
  exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Step 2: Load environment variables
source .env

# Step 3: Validate ACCESS_TOKEN
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ ACCESS_TOKEN not set${NC}"
  echo "  Set ACCESS_TOKEN in .env file"
  exit 2
fi
echo -e "${GREEN}✓ ACCESS_TOKEN configured${NC}"

# Step 4: Validate ACCOUNT_ID
if [ -z "$ACCOUNT_ID" ]; then
  echo -e "${RED}✗ ACCOUNT_ID not set${NC}"
  echo "  Set ACCOUNT_ID in .env file"
  exit 3
fi

if ! [[ "$ACCOUNT_ID" =~ ^[0-9]+$ ]]; then
  echo -e "${RED}✗ ACCOUNT_ID must be numeric${NC}"
  exit 3
fi
echo -e "${GREEN}✓ ACCOUNT_ID configured ($ACCOUNT_ID)${NC}"

# Step 5: Set default USER_AGENT if not set
if [ -z "$USER_AGENT" ]; then
  USER_AGENT="Basecamp API Script (api@example.com)"
  echo -e "${YELLOW}⚠ USER_AGENT not set, using default${NC}"
fi

# Step 6: Test API connection
echo -e "\nTesting API connection..."

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  https://3.basecampapi.com/$ACCOUNT_ID/my/profile.json 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo -e "${RED}✗ API connection failed (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 4
fi
echo -e "${GREEN}✓ API connection successful${NC}"

# Step 7: Display account info
echo
echo "Account Information:"
echo "===================="
NAME=$(echo "$BODY" | jq -r '.name')
EMAIL=$(echo "$BODY" | jq -r '.email_address')
ADMIN=$(echo "$BODY" | jq -r '.admin')

echo "Account ID: $ACCOUNT_ID"
echo "User: $NAME ($EMAIL)"
echo "Admin: $ADMIN"
echo
echo -e "${GREEN}Setup complete! You can now use other scripts.${NC}"
