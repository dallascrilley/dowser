#!/usr/bin/env bash
# Check and optionally set CLAUDE_CODE_OAUTH_TOKEN in GitHub repo secrets

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Credentials must be supplied by the user through the environment or a secret manager.
# No credential defaults are stored in this script.

echo -e "${BLUE}🔐 Claude Code Action Secret Checker${NC}"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ GitHub CLI (gh) not found. Install it first:${NC}"
    echo "   brew install gh"
    echo "   or visit: https://cli.github.com"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with GitHub CLI${NC}"
    echo "   Run: gh auth login"
    exit 1
fi

# Get current repo
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo -e "${RED}❌ Not in a GitHub repository${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Repository: ${NC}$REPO"
echo ""

# Check for CLAUDE_CODE_OAUTH_TOKEN
echo -e "${YELLOW}Checking for CLAUDE_CODE_OAUTH_TOKEN...${NC}"
if gh secret list | grep -q "CLAUDE_CODE_OAUTH_TOKEN"; then
    echo -e "${GREEN}✅ CLAUDE_CODE_OAUTH_TOKEN is set${NC}"
    OAUTH_SET=true
else
    echo -e "${RED}❌ CLAUDE_CODE_OAUTH_TOKEN is NOT set${NC}"
    OAUTH_SET=false
fi

# Check for ANTHROPIC_API_KEY
echo -e "${YELLOW}Checking for ANTHROPIC_API_KEY...${NC}"
if gh secret list | grep -q "ANTHROPIC_API_KEY"; then
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY is set${NC}"
    API_KEY_SET=true
else
    echo -e "${RED}❌ ANTHROPIC_API_KEY is NOT set${NC}"
    API_KEY_SET=false
fi

echo ""

# If neither is set, offer to set OAuth token (recommended)
if [ "$OAUTH_SET" = false ] && [ "$API_KEY_SET" = false ]; then
    echo -e "${RED}⚠️  No authentication configured!${NC}"
    echo ""
    echo "Claude Code Action requires either:"
    echo "  1. CLAUDE_CODE_OAUTH_TOKEN (recommended for Claude Pro/Max users)"
    echo "  2. ANTHROPIC_API_KEY (for users without subscription)"
    echo ""

    read -p "Would you like to set CLAUDE_CODE_OAUTH_TOKEN now? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Setting CLAUDE_CODE_OAUTH_TOKEN...${NC}"

        if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
            echo -e "${RED}❌ Supply CLAUDE_CODE_OAUTH_TOKEN through your environment or secret manager first${NC}"
            exit 1
        fi

        if printf '%s' "$CLAUDE_CODE_OAUTH_TOKEN" | gh secret set CLAUDE_CODE_OAUTH_TOKEN; then
            echo -e "${GREEN}✅ Successfully set CLAUDE_CODE_OAUTH_TOKEN${NC}"
            echo ""
            echo -e "${BLUE}📝 Note: This uses your Claude Pro/Max subscription${NC}"
            echo "   • More secure (short-lived tokens)"
            echo "   • No separate API billing"
            echo "   • Higher usage limits"
        else
            echo -e "${RED}❌ Failed to set secret${NC}"
            exit 1
        fi
    else
        echo ""
        echo "To set it manually:"
        echo ""
        echo -e "${YELLOW}For OAuth token (recommended):${NC}"
        echo '  : "${CLAUDE_CODE_OAUTH_TOKEN:?Supply CLAUDE_CODE_OAUTH_TOKEN securely}" &&'
        echo "  printf '%s' \"\$CLAUDE_CODE_OAUTH_TOKEN\" | gh secret set CLAUDE_CODE_OAUTH_TOKEN"
        echo ""
        echo -e "${YELLOW}For API key (alternative):${NC}"
        echo '  : "${ANTHROPIC_API_KEY:?Supply ANTHROPIC_API_KEY securely}" &&'
        echo "  printf '%s' \"\$ANTHROPIC_API_KEY\" | gh secret set ANTHROPIC_API_KEY"
    fi
elif [ "$OAUTH_SET" = true ]; then
    echo -e "${GREEN}✅ Authentication configured (OAuth token)${NC}"
    echo "   Using Claude Pro/Max subscription"
elif [ "$API_KEY_SET" = true ]; then
    echo -e "${GREEN}✅ Authentication configured (API key)${NC}"
    echo "   Using separate API billing"
fi

echo ""
echo -e "${BLUE}📚 Next steps:${NC}"
echo "   1. Create workflow file in .github/workflows/"
echo "   2. Include 'id-token: write' permission (for OAuth)"
echo "   3. Set CLAUDE_CODE_OAUTH_TOKEN as environment variable"
echo ""
echo "Example:"
echo "  env:"
echo "    CLAUDE_CODE_OAUTH_TOKEN: \${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}"
