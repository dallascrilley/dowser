#!/bin/bash
# set-blocking-relationships.sh
# Usage: ./set-blocking-relationships.sh
#
# Creates blocking relationships in Linear using the GraphQL API.
# linctl doesn't support blocking relationships, so we use the API directly.

set -e

# Configuration
LINEAR_API_KEY="${LINEAR_API_KEY:-}"  # Set via environment or edit here
ENDPOINT="https://api.linear.app/graphql"

# Define blocking relationships: "BLOCKER_ID BLOCKED_ID"
# Format: Each line represents one relationship where the first issue blocks the second
# Example: "DAL-105 DAL-104" means DAL-105 blocks DAL-104
RELATIONSHIPS=(
  # Add your blocking relationships here:
  # "BLOCKER-ID BLOCKED-ID"
  # Example:
  # "DAL-105 DAL-104"
  # "DAL-111 DAL-112"
)

# Check if API key is set
if [ -z "$LINEAR_API_KEY" ]; then
  # Try to extract from linctl config
  if [ -f ~/.linctl.yaml ]; then
    LINEAR_API_KEY=$(grep "api_key:" ~/.linctl.yaml | awk '{print $2}')
  fi

  if [ -z "$LINEAR_API_KEY" ]; then
    echo "Error: LINEAR_API_KEY not set"
    echo "Options:"
    echo "  1. Set environment variable: export LINEAR_API_KEY='lin_api_...'"
    echo "  2. Edit this script and set LINEAR_API_KEY at the top"
    echo "  3. Ensure ~/.linctl.yaml exists with api_key"
    exit 1
  fi
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed"
  echo "Install: brew install jq"
  exit 1
fi

# Create blocking relationship mutation
create_blocker() {
  local blocker_id="$1"
  local blocked_id="$2"

  local mutation=$(cat <<EOF
{
  "query": "mutation CreateIssueRelation(\$input: IssueRelationCreateInput!) { issueRelationCreate(input: \$input) { success issueRelation { id } } }",
  "variables": {
    "input": {
      "issueId": "$blocked_id",
      "relatedIssueId": "$blocker_id",
      "type": "blocks"
    }
  }
}
EOF
)

  local response=$(curl -s -X POST "$ENDPOINT" \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$mutation")

  echo "$response" | jq -r '.data.issueRelationCreate.success // "error"'
}

# Process all relationships
echo "Creating blocking relationships in Linear..."
echo ""

success_count=0
error_count=0

for relationship in "${RELATIONSHIPS[@]}"; do
  read -r blocker blocked <<< "$relationship"

  if [ -z "$blocker" ] || [ -z "$blocked" ]; then
    continue
  fi

  echo -n "Setting $blocker blocks $blocked... "

  result=$(create_blocker "$blocker" "$blocked")

  if [ "$result" = "true" ]; then
    echo "✓"
    ((success_count++))
  else
    echo "✗ Failed"
    ((error_count++))
  fi
done

echo ""
echo "Summary:"
echo "  ✓ Success: $success_count"
if [ $error_count -gt 0 ]; then
  echo "  ✗ Failed: $error_count"
fi
echo ""
echo "Verify in Linear UI by opening any blocked issue and checking the 'Blocked by' section."
