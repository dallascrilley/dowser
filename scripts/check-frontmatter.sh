#!/bin/bash
# Check frontmatter quality in SKILL.md files
# Validates required fields and length constraints
#
# Usage:
#   check-frontmatter.sh [SKILLS_DIR] [json]
#   - SKILLS_DIR: Path to skills directory (default: $HOME/.claude/skills)
#   - json: Pass "json" as 2nd arg for JSON output mode
#
# Frontmatter Schema:
#   - name: (required) Human-readable skill name
#   - short_description: (required, <300 chars) Concise summary for automated context injection
#   - description: (optional) Full detailed description, queried manually
#   - when_to_use: (required, <300 chars) Symptoms/situations that trigger this skill
#   - version: (recommended) Semantic version

SKILLS_DIR="${1:-$HOME/.claude/skills}"
JSON_MODE="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source JSON utilities if in JSON mode
if [[ "$JSON_MODE" == "json" ]]; then
    source "$SCRIPT_DIR/garden-json-utils.sh"
fi

[[ "$JSON_MODE" != "json" ]] && echo "## Frontmatter Quality"

missing_when_to_use=0
missing_short_description=0
missing_version=0
long_when_to_use=0
long_short_description=0
total_skills=0

# Helper function to extract field value (handles multi-line YAML)
extract_field() {
    local frontmatter="$1"
    local field="$2"

    local field_line=$(echo "$frontmatter" | grep "^${field}:")
    if [[ -z "$field_line" ]]; then
        echo ""
        return
    fi

    # Check if it's a multi-line value (starts with | or >)
    if echo "$field_line" | grep -qE "^${field}:\s*[|>]"; then
        # Multi-line: extract until next field or end of frontmatter
        echo "$frontmatter" | sed -n "/^${field}:/,/^[a-z_]*:/p" | sed '1d;$d' | tr '\n' ' '
    else
        # Single line: extract value after colon
        echo "$field_line" | sed "s/^${field}:\s*//"
    fi
}

# Check all SKILL.md files (both depth 1 and depth 2)
for skill_file in "$SKILLS_DIR"/*/SKILL.md "$SKILLS_DIR"/*/*/SKILL.md; do
    [[ ! -f "$skill_file" ]] && continue

    total_skills=$((total_skills + 1))
    skill_name=$(basename "$(dirname "$skill_file")")
    category_dir=$(dirname "$(dirname "$skill_file")")
    category=$(basename "$category_dir")

    # Determine display path / skill key
    if [[ "$category_dir" == "$SKILLS_DIR" ]]; then
        skill_key="$skill_name"
    else
        skill_key="$category/$skill_name"
    fi

    # Extract frontmatter (between --- markers)
    frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_file" | sed '1d;$d')

    # Extract ALL frontmatter fields for JSON output
    name_value=$(extract_field "$frontmatter" "name")
    short_desc_value=$(extract_field "$frontmatter" "short_description")
    desc_value=$(extract_field "$frontmatter" "description")
    when_to_use_value=$(extract_field "$frontmatter" "when_to_use")
    version_value=$(extract_field "$frontmatter" "version")

    # Add skill to JSON (if in JSON mode)
    if [[ "$JSON_MODE" == "json" ]]; then
        add_skill_json "$skill_key" "$skill_file" \
            "$name_value" "$short_desc_value" "$desc_value" \
            "$when_to_use_value" "$version_value"
    fi

    # Check for required fields
    if ! echo "$frontmatter" | grep -q "^when_to_use:"; then
        [[ "$JSON_MODE" != "json" ]] && echo "  ❌ MISSING when_to_use: $skill_key"
        [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "error" "missing_when_to_use" "Missing required when_to_use field"
        missing_when_to_use=$((missing_when_to_use + 1))
    fi

    # Check for short_description (required for automated context)
    # Falls back to description if short_description doesn't exist
    has_short_desc=$(echo "$frontmatter" | grep -c "^short_description:")
    has_desc=$(echo "$frontmatter" | grep -c "^description:")

    if [[ $has_short_desc -eq 0 && $has_desc -eq 0 ]]; then
        [[ "$JSON_MODE" != "json" ]] && echo "  ❌ MISSING short_description: $skill_key"
        [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "error" "missing_short_description" "Missing required short_description or description field"
        missing_short_description=$((missing_short_description + 1))
    elif [[ $has_short_desc -eq 0 && $has_desc -gt 0 ]]; then
        # Has description but no short_description - check if description is short enough
        desc_len=${#desc_value}
        if [[ $desc_len -gt 300 ]]; then
            [[ "$JSON_MODE" != "json" ]] && echo "  ⚠️  NEEDS short_description ($desc_len char description too long for context): $skill_key"
            [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "warning" "needs_short_description" "description ($desc_len chars) too long for context, needs short_description"
            long_short_description=$((long_short_description + 1))
        fi
        # If description <= 300 chars, it can serve as short_description (no warning)
    else
        # Has short_description - check its length
        short_desc_len=${#short_desc_value}
        if [[ $short_desc_len -gt 300 ]]; then
            [[ "$JSON_MODE" != "json" ]] && echo "  ⚠️  LONG short_description ($short_desc_len chars > 300): $skill_key"
            [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "warning" "long_short_description" "short_description ($short_desc_len chars) exceeds 300 char limit"
            long_short_description=$((long_short_description + 1))
        fi
    fi

    if ! echo "$frontmatter" | grep -q "^version:"; then
        [[ "$JSON_MODE" != "json" ]] && echo "  ⚠️  MISSING version: $skill_key"
        [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "warning" "missing_version" "Missing recommended version field"
        missing_version=$((missing_version + 1))
    fi

    # Check when_to_use length
    if [[ -n "$when_to_use_value" ]]; then
        when_to_use_len=${#when_to_use_value}
        if [[ $when_to_use_len -gt 300 ]]; then
            [[ "$JSON_MODE" != "json" ]] && echo "  ⚠️  LONG when_to_use ($when_to_use_len chars > 300): $skill_key"
            [[ "$JSON_MODE" == "json" ]] && add_issue_json "$skill_key" "warning" "long_when_to_use" "when_to_use ($when_to_use_len chars) exceeds 300 char limit"
            long_when_to_use=$((long_when_to_use + 1))
        fi
    fi
done

# Output JSON or human summary
if [[ "$JSON_MODE" == "json" ]]; then
    export_skills_json
else
    # Summary
    errors=$((missing_when_to_use + missing_short_description))
    warnings=$((missing_version + long_when_to_use + long_short_description))

    if [[ $errors -eq 0 && $warnings -eq 0 ]]; then
        echo "  ✅ All $total_skills skills have valid frontmatter"
    else
        echo ""
        [[ $missing_when_to_use -gt 0 ]] && echo "  ❌ $missing_when_to_use skills missing when_to_use"
        [[ $missing_short_description -gt 0 ]] && echo "  ❌ $missing_short_description skills missing short_description"
        [[ $missing_version -gt 0 ]] && echo "  ⚠️  $missing_version skills missing version"
        [[ $long_when_to_use -gt 0 ]] && echo "  ⚠️  $long_when_to_use skills have when_to_use > 300 chars"
        [[ $long_short_description -gt 0 ]] && echo "  ⚠️  $long_short_description skills need short_description (description too long)"
    fi
fi
