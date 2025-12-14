#!/bin/bash
# Master gardening script for skills wiki maintenance
# Outputs human-readable summary AND JSON report for programmatic access

SKILLS_DIR="${1:-$HOME/.claude/skills}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
REPORT_FILE="/tmp/garden-report-$(date +%s).json"

echo "=== Skills Wiki Health Check ==="
echo ""

# Make scripts executable if not already
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

# Run all checks (human output)
bash "$SCRIPT_DIR/check-naming.sh" "$SKILLS_DIR"
echo ""

bash "$SCRIPT_DIR/check-frontmatter.sh" "$SKILLS_DIR"
echo ""

bash "$SCRIPT_DIR/check-links.sh" "$SKILLS_DIR"
echo ""

bash "$SCRIPT_DIR/check-index-coverage.sh" "$SKILLS_DIR"

echo ""
echo "=== Health Check Complete ==="
echo ""
echo "Fix: ❌ errors (broken/missing) | Consider: ⚠️  warnings | ✅ = correct"

# --- JSON Report Generation ---
# Run check-frontmatter in JSON mode to get structured data
SKILLS_JSON=$(bash "$SCRIPT_DIR/check-frontmatter.sh" "$SKILLS_DIR" json)

# Count skills and issues
TOTAL_SKILLS=$(echo "$SKILLS_JSON" | jq 'length')
ERROR_COUNT=$(echo "$SKILLS_JSON" | jq '[.[] | .issues[] | select(.type == "error")] | length')
WARNING_COUNT=$(echo "$SKILLS_JSON" | jq '[.[] | .issues[] | select(.type == "warning")] | length')
PASSING_COUNT=$((TOTAL_SKILLS - $(echo "$SKILLS_JSON" | jq '[.[] | select(.issues | length > 0)] | length')))

# Build final report
jq -n \
    --arg timestamp "$TIMESTAMP" \
    --arg skills_dir "$SKILLS_DIR" \
    --argjson total "$TOTAL_SKILLS" \
    --argjson errors "$ERROR_COUNT" \
    --argjson warnings "$WARNING_COUNT" \
    --argjson passing "$PASSING_COUNT" \
    --argjson skills "$SKILLS_JSON" \
    '{
        timestamp: $timestamp,
        skills_dir: $skills_dir,
        total_skills: $total,
        summary: {
            errors: $errors,
            warnings: $warnings,
            passing: $passing
        },
        skills: $skills
    }' > "$REPORT_FILE"

echo ""
echo "📋 JSON report: $REPORT_FILE"
echo "   Use this report to fix issues without re-reading SKILL.md files."