# Garden Skills

Run health checks on the PAI skills wiki.

## Instructions

1. Execute the garden.sh script from the plugin scripts directory
2. **Read the JSON report file** printed at the end of output (path: `/tmp/garden-report-*.json`)
3. Report issues from the JSON data - DO NOT re-read individual SKILL.md files
4. Offer to fix errors, applying edits directly using frontmatter data from JSON
5. Summarize the health status

## CRITICAL: Use JSON Report

The garden.sh script outputs a JSON report containing **all frontmatter data** for every skill.

**DO NOT re-read SKILL.md files to gather information.** The JSON report contains:
- Full frontmatter (name, short_description, description, when_to_use, version)
- Character counts for length validation
- All issues with type, code, and message

**Only read a SKILL.md file when you need to EDIT it.**

## Usage

```bash
# Run health check
~/PAI/.claude/plugins/pai-skills/scripts/garden.sh

# Then read the JSON report path printed at the end
```

## JSON Report Schema

```json
{
  "timestamp": "ISO8601",
  "skills_dir": "/path/to/skills",
  "total_skills": 120,
  "summary": {
    "errors": 2,
    "warnings": 28,
    "passing": 90
  },
  "skills": {
    "category/skill-name": {
      "path": "/full/path/SKILL.md",
      "frontmatter": {
        "name": "Skill Name",
        "short_description": "...",
        "description": "...",
        "when_to_use": "...",
        "version": "1.0.0"
      },
      "metrics": {
        "short_description_length": 142,
        "when_to_use_length": 287
      },
      "issues": [
        {"type": "warning", "code": "long_when_to_use", "message": "..."}
      ]
    }
  }
}
```

## Issue Codes Reference

| Code | Type | Meaning | Fix |
|------|------|---------|-----|
| `missing_when_to_use` | error | No when_to_use field | Add when_to_use frontmatter |
| `missing_short_description` | error | No short_description or description | Add short_description |
| `missing_version` | warning | No version field | Add version: "1.0.0" |
| `long_when_to_use` | warning | when_to_use > 300 chars | Shorten to < 300 chars |
| `long_short_description` | warning | short_description > 300 chars | Shorten or split into description |
| `needs_short_description` | warning | description > 300 chars, no short_description | Add concise short_description |

## Available Checks

- **Link validation** - Verifies all skill cross-references
- **Naming consistency** - Checks kebab-case directories and frontmatter
- **INDEX coverage** - Ensures all skills are properly indexed
- **Frontmatter quality** - Validates required fields and lengths

## After Running

1. Parse JSON report for skills with issues
2. Group issues by type (errors first, then warnings)
3. For each fix:
   - Use frontmatter data from JSON to understand current state
   - Read SKILL.md only when editing
   - Apply minimal targeted edit
4. Re-run to verify fixes

## Quick Reference

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✅ | Pass | None needed |
| ❌ | Error | Must fix |
| ⚠️ | Warning | Should fix |
| ℹ️ | Info | No action |