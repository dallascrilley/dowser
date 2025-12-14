#!/bin/bash
# Extract only frontmatter from a SKILL.md file
# Usage: extract-frontmatter.sh /path/to/SKILL.md

if [[ $# -eq 0 ]]; then
    echo "Usage: extract-frontmatter.sh /path/to/SKILL.md" >&2
    exit 1
fi

SKILL_FILE="$1"

if [[ ! -f "$SKILL_FILE" ]]; then
    echo "Error: File not found: $SKILL_FILE" >&2
    exit 1
fi

# Extract content between first two --- markers (inclusive)
sed -n '/^---$/,/^---$/p' "$SKILL_FILE"
