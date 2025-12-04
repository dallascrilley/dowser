#!/bin/bash
# Create a Git branch from a Linear issue
# Usage: create_branch_from_issue.sh <issue-id> [branch-type]
# Example: create_branch_from_issue.sh DAL-128 feature

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
ISSUE_ID="$1"
BRANCH_TYPE="${2:-feature}"  # Default to 'feature' if not specified

# Validate arguments
if [ -z "$ISSUE_ID" ]; then
    echo -e "${RED}Error: Issue ID is required${NC}"
    echo "Usage: $0 <issue-id> [branch-type]"
    echo "Example: $0 DAL-128 feature"
    exit 1
fi

# Validate branch type
case "$BRANCH_TYPE" in
    feature|fix|hotfix|chore|docs|refactor)
        ;;
    *)
        echo -e "${YELLOW}Warning: Unusual branch type '$BRANCH_TYPE'${NC}"
        echo "Common types: feature, fix, hotfix, chore, docs, refactor"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        ;;
esac

# Main execution
main() {
    echo -e "${GREEN}=== Creating Branch from Linear Issue ===${NC}\n"
    
    # Check if linctl is available
    if ! command -v linctl &> /dev/null; then
        echo -e "${RED}Error: linctl is not installed${NC}"
        echo "Install it with: brew install dorkitude/linctl/linctl"
        exit 1
    fi
    
    # Fetch issue details
    echo -e "Fetching issue ${GREEN}$ISSUE_ID${NC}..."
    ISSUE_JSON=$(linctl issue get "$ISSUE_ID" --json 2>/dev/null)
    
    if [ -z "$ISSUE_JSON" ] || [ "$ISSUE_JSON" == "null" ]; then
        echo -e "${RED}Error: Issue $ISSUE_ID not found${NC}"
        exit 1
    fi
    
    # Extract issue title and create slug
    ISSUE_TITLE=$(echo "$ISSUE_JSON" | jq -r '.title')
    
    # Create slug from title (lowercase, replace spaces/special chars with hyphens)
    SLUG=$(echo "$ISSUE_TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g' | cut -c1-50)
    
    # Create branch name
    BRANCH_NAME="${BRANCH_TYPE}/${ISSUE_ID,,}-${SLUG}"
    
    echo -e "Issue: ${GREEN}$ISSUE_TITLE${NC}"
    echo -e "Branch: ${GREEN}$BRANCH_NAME${NC}\n"
    
    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
        echo -e "${YELLOW}Warning: Branch $BRANCH_NAME already exists${NC}"
        read -p "Switch to it anyway? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout "$BRANCH_NAME"
            echo -e "${GREEN}✓ Switched to existing branch${NC}"
        fi
        exit 0
    fi
    
    # Ensure we're on main/master
    DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
    
    echo -e "Creating branch from ${GREEN}$DEFAULT_BRANCH${NC}..."
    
    # Update main branch
    if ! git checkout "$DEFAULT_BRANCH" 2>/dev/null; then
        echo -e "${YELLOW}Warning: Could not checkout $DEFAULT_BRANCH, using current branch${NC}"
    else
        git pull origin "$DEFAULT_BRANCH" 2>/dev/null || echo -e "${YELLOW}Warning: Could not pull latest changes${NC}"
    fi
    
    # Create and checkout new branch
    git checkout -b "$BRANCH_NAME"
    
    # Update Linear issue status to "In Progress"
    echo -e "\n${YELLOW}Updating issue status to 'In Progress'...${NC}"
    UPDATE_RESULT=$(linctl issue update "$ISSUE_ID" --state "In Progress" --json 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Issue status updated${NC}"
    else
        echo -e "${YELLOW}Warning: Could not update issue status (may need to do manually)${NC}"
    fi
    
    echo -e "\n${GREEN}=== Branch Created ===${NC}"
    echo -e "Branch: ${GREEN}$BRANCH_NAME${NC}"
    echo -e "Issue: ${GREEN}$ISSUE_ID - $ISSUE_TITLE${NC}"
    echo -e "\n${YELLOW}Remember:${NC}"
    echo -e "  • Include $ISSUE_ID in commit messages"
    echo -e "  • Include '$ISSUE_ID' or 'Fixes $ISSUE_ID' in PR description"
}

main
