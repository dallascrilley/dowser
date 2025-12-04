#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Configuration Validation"
echo "========================"
echo

# Check .env exists
if [ ! -f .env ]; then
  echo -e "${RED}✗ .env file not found${NC}"
  exit 1
fi

# Load .env
source .env

ERRORS=0

# Validate ACCESS_TOKEN
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${RED}✗ ACCESS_TOKEN not set${NC}"
  ERRORS=$((ERRORS + 1))
else
  TOKEN_LENGTH=${#ACCESS_TOKEN}
  echo -e "${GREEN}✓ ACCESS_TOKEN: Set ($TOKEN_LENGTH characters)${NC}"
fi

# Validate ACCOUNT_ID
if [ -z "$ACCOUNT_ID" ]; then
  echo -e "${RED}✗ ACCOUNT_ID not set${NC}"
  ERRORS=$((ERRORS + 1))
elif ! [[ "$ACCOUNT_ID" =~ ^[0-9]+$ ]]; then
  echo -e "${RED}✗ ACCOUNT_ID must be numeric${NC}"
  ERRORS=$((ERRORS + 1))
else
  echo -e "${GREEN}✓ ACCOUNT_ID: $ACCOUNT_ID${NC}"
fi

# Validate USER_AGENT (optional but recommended)
if [ -z "$USER_AGENT" ]; then
  echo -e "${YELLOW}⚠ USER_AGENT not set (optional but recommended)${NC}"
else
  echo -e "${GREEN}✓ USER_AGENT: $USER_AGENT${NC}"
fi

echo

if [ $ERRORS -gt 0 ]; then
  echo -e "${RED}Configuration has $ERRORS error(s)${NC}"
  exit 2
else
  echo -e "${GREEN}All required configuration is valid!${NC}"
fi
