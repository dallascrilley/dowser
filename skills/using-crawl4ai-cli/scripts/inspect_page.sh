#!/bin/bash
# Visual page inspection workflow using Chrome MCP
# Usage: ./scripts/inspect_page.sh https://example.com

set -e

URL="$1"

if [ -z "$URL" ]; then
    echo "Usage: $0 <URL>"
    echo "Example: $0 https://news.example.com"
    exit 1
fi

echo "🔍 Chrome MCP Inspection Workflow"
echo "=================================="
echo "URL: $URL"
echo ""
echo "INSTRUCTIONS:"
echo "1. Use Chrome MCP to navigate to URL"
echo "2. Take screenshot to see visual layout"
echo "3. Review page.md (auto-captured) for structure"
echo "4. Identify these elements:"
echo "   - Navigation sections (header, sidebar, footer)"
echo "   - Main content/article body sections"
echo "   - Repeated patterns (article cards, list items)"
echo "   - Dynamic content areas"
echo ""
echo "CHECKLIST:"
echo "- [ ] Navigated to URL"
echo "- [ ] Screenshot captured"
echo "- [ ] Reviewed page.md structure"
echo "- [ ] Identified navigation vs. content"
echo "- [ ] Documented selectors for:"
echo "    - [ ] Base container (article, .post, etc.)"
echo "    - [ ] Title element"
echo "    - [ ] Content element"
echo "    - [ ] Metadata (date, author, etc.)"
echo ""
echo "NEXT STEPS:"
echo "1. Create schema.json with identified selectors"
echo "2. Test extraction: crwl $URL -e extract_css.yml -s schema.json -o json > test.json"
echo "3. Validate: python scripts/validate_extraction.py test.json"
echo ""
echo "COMMON SELECTOR PATTERNS:"
echo "  Articles:    article, .article, .post, [class*='article']"
echo "  Title:       h1, .title, .headline, [class*='title']"
echo "  Content:     .content, .body, .entry-content, [class*='content']"
echo "  Exclude:     header, nav, footer, aside, .sidebar"

