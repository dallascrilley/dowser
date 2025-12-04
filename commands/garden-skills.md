# Garden Skills

Run health checks on the PAI skills wiki.

## Instructions

1. Execute the garden.sh script from the plugin scripts directory
2. Report any issues found categorized by severity (❌ errors, ⚠️ warnings)
3. Offer to fix critical errors automatically
4. Summarize the health status

## Usage

```bash
# Full health check
/garden-skills

# Or run directly:
~/PAI/.claude/plugins/pai-skills/scripts/garden.sh
```

## Available Checks

- **Link validation** - Verifies all skill cross-references
- **Naming consistency** - Checks kebab-case directories and frontmatter
- **INDEX coverage** - Ensures all skills are properly indexed
- **Frontmatter quality** - Validates required fields

## After Running

If errors are found:
1. Review each error message
2. Ask user which ones to fix
3. Apply fixes using appropriate tools (Edit, Write)
4. Re-run health check to verify

## Quick Reference

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✅ | Pass | None needed |
| ❌ | Error | Must fix |
| ⚠️ | Warning | Should fix |
| ℹ️ | Info | No action |
