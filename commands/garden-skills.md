# Garden Skills

Run health checks on the Dowser skill library.

## ⚡ EXECUTE IMMEDIATELY

**When this command is invoked, you MUST execute the script immediately using run_terminal_cmd. Do not ask permission or show instructions - just run it.**

```bash
${CLAUDE_PLUGIN_ROOT:-.}/scripts/garden.sh
```

If `CLAUDE_PLUGIN_ROOT` is unset, run from the plugin repository root:

```bash
./scripts/garden.sh skills
```

## Workflow After Execution

1. **Read the JSON report file** from the output (path: `/tmp/garden-report-*.json`)
2. **Report issues** from the JSON data - DO NOT re-read individual SKILL.md files
3. **Offer to fix errors** using frontmatter data from JSON (extract only frontmatter, use claude-haiku-4-5 for simple edits)
4. **Summarize** the health status

## CRITICAL: Use JSON Report

The garden.sh script outputs a JSON report containing **all frontmatter data** for every skill.

**DO NOT re-read SKILL.md files to gather information.** The JSON report contains:
- Full frontmatter (name, short_description, description, when_to_use, version)
- Character counts for length validation
- All issues with type, code, and message

**When editing SKILL.md files, ONLY read the frontmatter section, not the full file.**

### Extracting Frontmatter Only

For simple frontmatter edits (shortening when_to_use, adding version, etc.), extract only the frontmatter:

```bash
# Option 1: Use the helper script
${CLAUDE_PLUGIN_ROOT:-.}/scripts/extract-frontmatter.sh /path/to/SKILL.md

# Option 2: Use sed directly
sed -n '/^---$/,/^---$/p' /path/to/SKILL.md

# Option 3: Use the utility function (if sourced)
source ${CLAUDE_PLUGIN_ROOT:-.}/scripts/garden-json-utils.sh
extract_frontmatter "/path/to/SKILL.md"
```

**NEVER read the full SKILL.md file for frontmatter-only edits.** The full file content is not needed and wastes tokens.

## Usage

```bash
# Run health check from plugin root
./scripts/garden.sh skills

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
   - **For frontmatter-only edits:** Extract only frontmatter (see above), use `claude-haiku-4-5` model
   - **For complex edits:** Read full file only if absolutely necessary, use default model
   - Apply minimal targeted edit
4. Re-run to verify fixes

## Model Selection for Edits

**Use `claude-haiku-4-5` for simple frontmatter edits:**
- Shortening `when_to_use` to < 300 chars
- Adding missing `version: "1.0.0"`
- Truncating `short_description` to < 300 chars
- Adding missing `when_to_use` field (simple text)

**Use default model for complex edits:**
- Edits requiring understanding of full file content
- Structural changes beyond frontmatter
- Multi-field edits with dependencies

**Simple edits = frontmatter-only changes = use haiku model**

## Quick Reference

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✅ | Pass | None needed |
| ❌ | Error | Must fix |
| ⚠️ | Warning | Should fix |
| ℹ️ | Info | No action |
