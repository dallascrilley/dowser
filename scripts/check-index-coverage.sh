#!/bin/bash
# Check that all skills are properly listed in INDEX files

SKILLS_DIR="${1:-$HOME/.claude/skills}"

echo "## INDEX Coverage"
# For each category with an INDEX
for category_dir in "$SKILLS_DIR"/*/; do
    category=$(basename "$category_dir")

    # Skip if not a directory
    [[ ! -d "$category_dir" ]] && continue

    index_file="$category_dir/INDEX.md"

    # Skip if no INDEX (meta directories might not have one)
    [[ ! -f "$index_file" ]] && continue

    # Find all SKILL.md files in this category
    skill_count=0
    indexed_count=0
    missing_count=0

    while IFS= read -r skill_file; do
        skill_count=$((skill_count + 1))
        skill_name=$(basename $(dirname "$skill_file"))

        # Check if skill is referenced in INDEX (format: skills/category/skill-name)
        if grep -q "skills/$category/$skill_name" "$index_file"; then
            indexed_count=$((indexed_count + 1))
        else
            echo "  ❌ NOT INDEXED: $skill_name/SKILL.md"
            missing_count=$((missing_count + 1))
        fi
    done < <(find "$category_dir" -mindepth 2 -maxdepth 2 -type f -name "SKILL.md")

    if [ $skill_count -gt 0 ] && [ $missing_count -eq 0 ]; then
        echo "  ✅ $category: all $skill_count skills indexed"
    elif [ $missing_count -gt 0 ]; then
        echo "  ⚠️  $category: $missing_count/$skill_count skills missing"
    fi
done

echo ""
# Verify INDEX entries have descriptions (format: skills/category/skill-name - Description)
find "$SKILLS_DIR" -type f -name "INDEX.md" | while read -r index_file; do
    category=$(basename "$(dirname "$index_file")")

    # Extract skill references (format: skills/category/skill-name)
    grep -oE 'skills/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+' "$index_file" | while read -r ref; do
        skill_name=$(basename "$ref")

        # Get the line with the reference
        line_num=$(grep -n "$ref" "$index_file" | cut -d: -f1 | head -1)

        # Check if there's a description on the same line
        description=$(sed -n "${line_num}p" "$index_file" | sed "s|.*$ref *- *||")

        if [[ -z "$description" || "$description" == *"$ref"* || "$description" == *"skills/"* ]]; then
            echo "  ⚠️  NO DESCRIPTION: $category/INDEX.md reference to $skill_name"
        fi
    done
done

echo ""
echo "## Rules / skill-rules.json"

RULES_FILE="$SKILLS_DIR/skill-rules.json"

if [[ ! -f "$RULES_FILE" ]]; then
    echo "  ℹ️  No skills/skill-rules.json found at $RULES_FILE (skip rules sync check)"
    exit 0
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "  ⚠️  jq not found - cannot validate skills/skill-rules.json against SKILL inventory"
    exit 0
fi

# Collect current SKILL inventory (directory basenames for SKILL.md files)
# Check both depth 1 (skill/SKILL.md) and depth 2 (category/skill/SKILL.md)
existing_skill_names="$(
  for skill_file in "$SKILLS_DIR"/*/SKILL.md "$SKILLS_DIR"/*/*/SKILL.md; do
    [[ -f "$skill_file" ]] && basename "$(dirname "$skill_file")"
  done | sort -u
)"

# Collect all ruled skill names from skills/skill-rules.json
ruled_skill_names="$(jq -r '.skills | keys[]' "$RULES_FILE" 2>/dev/null || echo "")"

if [[ -z "$ruled_skill_names" ]]; then
    echo "  ℹ️  skills/skill-rules.json has no .skills entries"
    exit 0
fi

# Check for rules that reference non-existent skills
while read -r rule_name; do
    [[ -z "$rule_name" ]] && continue

    if ! grep -qx "$rule_name" <<<"$existing_skill_names"; then
        echo "  ❌ RULE WITHOUT SKILL: $rule_name in skills/skill-rules.json"
        continue
    fi

    # Warn if ruled skill is not present in any INDEX.md reference
    if ! grep -Rqs "skills/.*/$rule_name" "$SKILLS_DIR"/*/INDEX.md 2>/dev/null; then
        echo "  ⚠️  RULED SKILL NOT IN INDEX: $rule_name (present in rules, but not referenced in any INDEX.md)"
    fi
done <<<"$ruled_skill_names"
