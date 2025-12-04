#!/bin/bash
# Setup Linear project for current repository
# This script checks if a Linear project exists for the current repo and creates one if needed

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get repository path (owner/repo format)
get_repo_path() {
    # Try gh CLI first
    if command -v gh &> /dev/null; then
        REPO_PATH=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
        if [ -n "$REPO_PATH" ]; then
            echo "$REPO_PATH"
            return 0
        fi
    fi
    
    # Fallback to git remote parsing
    REPO_PATH=$(git remote get-url origin 2>/dev/null | sed -E 's/.*[:/]([^/]+\/[^/]+)(\.git)?$/\1/' | sed 's/\.git$//')
    if [ -n "$REPO_PATH" ]; then
        echo "$REPO_PATH"
        return 0
    fi
    
    return 1
}

# Get Linear API key
get_api_key() {
    # Try environment variable first
    if [ -n "$LINEAR_API_KEY" ]; then
        echo "$LINEAR_API_KEY"
        return 0
    fi
    
    # Try linctl config file
    if [ -f ~/.linctl.yaml ]; then
        API_KEY=$(grep "api_key:" ~/.linctl.yaml | awk '{print $2}')
        if [ -n "$API_KEY" ]; then
            echo "$API_KEY"
            return 0
        fi
    fi
    
    return 1
}

# Main execution
main() {
    echo -e "${GREEN}=== Linear Project Setup ===${NC}\n"
    
    # Get repository path
    REPO_PATH=$(get_repo_path)
    if [ -z "$REPO_PATH" ]; then
        echo -e "${RED}Error: Could not determine repository path${NC}"
        echo "Make sure you're in a git repository with a remote configured"
        exit 1
    fi
    
    echo -e "Repository: ${GREEN}$REPO_PATH${NC}"
    PROJECT_NAME="$REPO_PATH"
    
    # Check if linctl is available
    if ! command -v linctl &> /dev/null; then
        echo -e "${RED}Error: linctl is not installed${NC}"
        echo "Install it with: brew install dorkitude/linctl/linctl"
        exit 1
    fi
    
    # Check authentication
    if ! linctl whoami &> /dev/null; then
        echo -e "${YELLOW}Warning: linctl not authenticated${NC}"
        echo "Run 'linctl auth' to authenticate"
        exit 1
    fi
    
    # Check if project already exists
    echo -e "\nChecking for existing project..."
    EXISTING_PROJECT=$(linctl project list --json 2>/dev/null | jq -r ".[] | select(.name == \"$PROJECT_NAME\") | .id" | head -n 1)
    
    if [ -n "$EXISTING_PROJECT" ]; then
        PROJECT_URL="https://linear.app/project/$EXISTING_PROJECT"
        echo -e "${GREEN}✓ Project already exists${NC}"
        echo -e "Project ID: $EXISTING_PROJECT"
        echo -e "URL: $PROJECT_URL"
    else
        echo -e "${YELLOW}Project not found, creating...${NC}"
        
        # Get team (use first team if multiple exist)
        TEAM_KEY=$(linctl team list --json 2>/dev/null | jq -r '.[0].key')
        
        if [ -z "$TEAM_KEY" ]; then
            echo -e "${RED}Error: No teams found${NC}"
            exit 1
        fi
        
        echo -e "Using team: ${GREEN}$TEAM_KEY${NC}"
        
        # Create project
        CREATE_RESULT=$(linctl project create \
            --name "$PROJECT_NAME" \
            --team "$TEAM_KEY" \
            --description "Linear project for $PROJECT_NAME" \
            --json 2>/dev/null)
        
        PROJECT_ID=$(echo "$CREATE_RESULT" | jq -r '.id')
        
        if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "null" ]; then
            echo -e "${RED}Error: Failed to create project${NC}"
            echo "$CREATE_RESULT"
            exit 1
        fi
        
        PROJECT_URL="https://linear.app/project/$PROJECT_ID"
        echo -e "${GREEN}✓ Project created successfully${NC}"
        echo -e "Project ID: $PROJECT_ID"
        echo -e "URL: $PROJECT_URL"
        
        # Update documentation files
        echo -e "\n${YELLOW}Updating documentation files...${NC}"
        
        for file in README.md CLAUDE.md AGENTS.md; do
            if [ -f "$file" ]; then
                if ! grep -q "Linear Project" "$file"; then
                    {
                        echo ""
                        echo "## Linear Project"
                        echo ""
                        echo "This project is tracked in Linear: [$PROJECT_NAME]($PROJECT_URL)"
                    } >> "$file"
                    echo -e "${GREEN}✓ Updated $file${NC}"
                fi
            fi
        done
    fi
    
    echo -e "\n${GREEN}=== Setup Complete ===${NC}"
}

main
