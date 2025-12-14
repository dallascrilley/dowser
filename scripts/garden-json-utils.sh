#!/bin/bash
# garden-json-utils.sh - JSON output utilities for garden scripts
#
# Usage: Source this file, then call functions to build JSON output.
#   source garden-json-utils.sh
#   init_json_output
#   add_skill_json "category/skill" "/path/to/SKILL.md" "name" "short_desc" "desc" "when_to_use" "version"
#   add_issue_json "category/skill" "warning" "long_when_to_use" "when_to_use exceeds 300 chars"
#   export_skills_json

# Requires: jq

# Initialize JSON accumulator (call at start)
init_json_output() {
    GARDEN_JSON_SKILLS="{}"
}

# Escape string for JSON (handles quotes, newlines, special chars)
json_escape() {
    local str="$1"
    # Use jq for reliable JSON escaping
    printf '%s' "$str" | jq -Rs '.'
}

# Add a skill entry with frontmatter
# Args: skill_key path name short_desc description when_to_use version
add_skill_json() {
    local skill_key="$1"
    local path="$2"
    local name="$3"
    local short_desc="$4"
    local description="$5"
    local when_to_use="$6"
    local version="$7"

    local short_desc_len=${#short_desc}
    local when_to_use_len=${#when_to_use}

    # Build skill JSON using jq for safe escaping
    GARDEN_JSON_SKILLS=$(echo "$GARDEN_JSON_SKILLS" | jq \
        --arg key "$skill_key" \
        --arg path "$path" \
        --arg name "$name" \
        --arg short_desc "$short_desc" \
        --arg desc "$description" \
        --arg when "$when_to_use" \
        --arg ver "$version" \
        --argjson sd_len "$short_desc_len" \
        --argjson wtu_len "$when_to_use_len" \
        '.[$key] = {
            path: $path,
            frontmatter: {
                name: $name,
                short_description: $short_desc,
                description: $desc,
                when_to_use: $when,
                version: $ver
            },
            metrics: {
                short_description_length: $sd_len,
                when_to_use_length: $wtu_len
            },
            issues: []
        }')
}

# Add an issue to a skill
# Args: skill_key type code message
# type: "error" or "warning"
# code: e.g., "missing_when_to_use", "long_short_description"
add_issue_json() {
    local skill_key="$1"
    local type="$2"
    local code="$3"
    local message="$4"

    # Add issue to skill's issues array
    GARDEN_JSON_SKILLS=$(echo "$GARDEN_JSON_SKILLS" | jq \
        --arg key "$skill_key" \
        --arg type "$type" \
        --arg code "$code" \
        --arg msg "$message" \
        'if .[$key] then .[$key].issues += [{type: $type, code: $code, message: $msg}] else . end')
}

# Export skills JSON (call at end)
export_skills_json() {
    echo "$GARDEN_JSON_SKILLS"
}

# Extract only frontmatter from a SKILL.md file (between --- markers)
# Usage: extract_frontmatter "/path/to/SKILL.md"
extract_frontmatter() {
    local skill_file="$1"
    if [[ ! -f "$skill_file" ]]; then
        echo "Error: File not found: $skill_file" >&2
        return 1
    fi
    # Extract content between first two --- markers (inclusive)
    sed -n '/^---$/,/^---$/p' "$skill_file"
}

# Initialize on source
init_json_output
