#!/bin/bash

# Load environment
if [ ! -f .env ]; then
  echo "Error: .env file not found. Create it from .env.example"
  exit 1
fi

source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Basecamp 4 API Connection Test"
echo "=============================="
echo

# Validate configuration
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ ACCESS_TOKEN not configured${NC}"
  exit 1
fi

if [ -z "$ACCOUNT_ID" ]; then
  echo -e "${RED}✗ ACCOUNT_ID not configured${NC}"
  exit 1
fi

USER_AGENT=${USER_AGENT:-"Basecamp API Test (api@example.com)"}

# Test 1: Connect to /my/profile endpoint
echo "Test 1: Fetching user profile..."
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  https://3.basecampapi.com/$ACCOUNT_ID/my/profile.json)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Successfully connected to API${NC}"
  NAME=$(echo "$BODY" | jq -r '.name')
  echo "  User: $NAME"
else
  echo -e "${RED}✗ API connection failed (HTTP $HTTP_CODE)${NC}"
  echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
  exit 1
fi

echo

# Test 2: List projects
echo "Test 2: Fetching projects list..."
RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  https://3.basecampapi.com/$ACCOUNT_ID/projects.json)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  COUNT=$(echo "$BODY" | jq 'length')
  echo -e "${GREEN}✓ Successfully fetched projects${NC}"
  echo "  Total projects: $COUNT"
else
  echo -e "${RED}✗ Failed to fetch projects (HTTP $HTTP_CODE)${NC}"
  exit 1
fi

echo

# Test 3: Check rate limits
echo "Test 3: Checking rate limit headers..."
RESPONSE=$(curl -s -i \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "User-Agent: $USER_AGENT" \
  https://3.basecampapi.com/$ACCOUNT_ID/my/profile.json 2>&1)

X_RATE=$(echo "$RESPONSE" | grep -i "X-Ratelimit-Remaining" | cut -d' ' -f2)
if [ -z "$X_RATE" ]; then
  echo -e "${YELLOW}⚠ Rate limit header not found${NC}"
else
  echo -e "${GREEN}✓ Rate limit header present${NC}"
  echo "  Remaining requests: $X_RATE"
fi

echo
echo -e "${GREEN}All connection tests passed!${NC}"
