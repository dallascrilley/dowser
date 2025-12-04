---
name: Gardening Skills Wiki
description: >-
  Maintain skills wiki health - check links, naming, cross-references, and
  coverage
when_to_use: >-
  When adding/removing skills. When reorganizing categories. When links feel
  broken. Periodically (weekly/monthly) to maintain wiki health. When INDEX
  files don't match directory structure. When cross-references might be stale.
version: 1.0.0
languages: bash
category: meta
---

# Gardening Skills Wiki

## Overview

The skills wiki needs regular maintenance to stay healthy: links break, skills get orphaned, naming drifts, INDEX files fall out of sync.

**Core principle:** Automate health checks to maintain wiki quality without burning tokens on manual inspection.

## When to Use

**Run gardening after:**
- Adding new skills
- Removing or renaming skills
- Reorganizing categories
- Updating cross-references
- Suspicious that links are broken

**Periodic maintenance:**
- Weekly during active development
- Monthly during stable periods

## Quick Health Check

```bash
# Run all checks
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh

# Or run specific checks
~/PAI/.claude/skills/meta/gardening-skills-wiki/check-links.sh
~/PAI/.claude/skills/meta/gardening-skills-wiki/check-naming.sh
~/PAI/.claude/skills/meta/gardening-skills-wiki/check-index-coverage.sh

# Analyze search gaps (what skills are missing)
~/PAI/.claude/skills/meta/gardening-skills-wiki/analyze-search-gaps.sh
```

The master script runs all checks and provides a health report.

## What Gets Checked

### 1. Link Validation (`check-links.sh`)

**Checks:**
- Backtick-wrapped `@` links - backticks disable resolution
- Relative paths like skills/ or skills/gardening-skills-wiki/~/ - should use skills/ absolute paths
- All `skills/` references resolve to existing files
- Skills referenced in INDEX files exist
- Orphaned skills (not in any INDEX)

**Fixes:**
- Remove backticks from @ references
- Convert skills/ and skills/gardening-skills-wiki/~/ relative paths to skills/ absolute paths
- Update broken skills/ references to correct paths
- Add orphaned skills to their category INDEX
- Remove references to deleted skills

### 2. Naming Consistency (`check-naming.sh`)

**Checks:**
- Directory names are kebab-case
- No uppercase or underscores in directory names
- Frontmatter fields present (name, description, when_to_use, version, type)
- Skill names use active voice (not "How to...")
- Empty directories

**Fixes:**
- Rename directories to kebab-case
- Add missing frontmatter fields
- Remove empty directories
- Rephrase names to active voice

### 3. INDEX Coverage (`check-index-coverage.sh`)

**Checks:**
- All skills listed in their category INDEX
- All category INDEX files linked from main INDEX
- Skills have descriptions in INDEX entries
- `skills/skill-rules.json` entries only reference existing skills
- `skills/skill-rules.json` metadata (name/description) stays aligned with SKILL frontmatter and INDEX entries

**Fixes:**
- Add missing skills to INDEX files
- Add category links to main INDEX
- Add descriptions for INDEX entries
- Update or remove `skills/skill-rules.json` entries to match the current SKILL inventory and INDEX metadata

## Common Issues and Fixes

### Broken Links

```
❌ BROKEN: skills/debugging/root-cause-tracing
   Target: /path/to/skills/debugging/root-cause-tracing/SKILL.md
```

**Fix:** Update the reference path - skill might have moved or been renamed.

### Orphaned Skills

```
⚠️  ORPHANED: test-invariants/SKILL.md not in testing/INDEX.md
```

**Fix:** Add to the category INDEX:

```markdown
- skills/gardening-skills-wiki/test-invariants - Description of skill
```

### Backtick-Wrapped Links

```
❌ BACKTICKED: skills/testing/condition-based-waiting on line 31
   File: getting-started/SKILL.md
   Fix: Remove backticks - use bare @ reference
```

**Fix:** Remove backticks:

```markdown
# ❌ Bad - backticks disable link resolution
`skills/testing/condition-based-waiting`

# ✅ Good - bare @ reference
skills/testing/condition-based-waiting
```

### Relative Path Links

```
❌ RELATIVE: skills/testing in coding/SKILL.md
   Fix: Use skills/ absolute path instead
```

**Fix:** Convert to absolute path:

```markdown
# ❌ Bad - relative paths are brittle
skills/testing/condition-based-waiting

# ✅ Good - absolute skills/ path
skills/testing/condition-based-waiting
```

### Naming Issues

```
⚠️  Mixed case: TestingPatterns (should be kebab-case)
```

**Fix:** Rename directory:

```bash
cd ~/PAI/.claude/skills/testing
mv TestingPatterns testing-patterns
# Update all references to old name
```

### Missing from INDEX

```
❌ NOT INDEXED: condition-based-waiting/SKILL.md
```

**Fix:** Add to `testing/INDEX.md`:

```markdown
## Available Skills

- skills/gardening-skills-wiki/condition-based-waiting - Replace timeouts with condition polling
```

### Empty Directories

```
⚠️  EMPTY: event-based-testing
```

**Fix:** Remove if no longer needed:

```bash
rm -rf ~/PAI/.claude/skills/event-based-testing
```

## Naming Conventions

### Directory Names

- **Format:** kebab-case (lowercase with hyphens)
- **Process skills:** Use gerunds when appropriate (`creating-skills`, `testing-skills`)
- **Pattern skills:** Use core concept (`flatten-with-flags`, `test-invariants`)
- **Avoid:** Mixed case, underscores, passive voice starters ("how-to-")

### Frontmatter Requirements

**Required fields:**
- `name`: Human-readable name
- `short_description`: Concise summary (<300 chars) - **used for automated context injection**
- `when_to_use`: Symptoms and situations (<300 chars) - CSO-critical for skill discovery
- `version`: Semantic version

**Optional fields:**
- `description`: Full detailed description (any length) - queried manually when needed
- `languages`: Applicable languages
- `dependencies`: Required tools
- `context`: Special context (e.g., "AI-assisted development")

**Why short_description?**
- Keeps automated context lean (skill analyzer, INDEX summaries)
- Full `description` remains available for manual deep-dives
- If only `description` exists and is ≤300 chars, it serves as `short_description`
- If `description` >300 chars without `short_description`, script warns to add one

## Automation Workflow

### After Adding New Skill

```bash
# 1. Create skill
mkdir -p ~/PAI/.claude/skills/category/new-skill
vim ~/PAI/.claude/skills/category/new-skill/SKILL.md

# 2. Add to category INDEX
vim ~/PAI/.claude/skills/category/INDEX.md

# 3. Run health check
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh

# 4. Fix any issues reported
```

### After Reorganizing

```bash
# 1. Move/rename skills
mv ~/PAI/.claude/skills/old-category/skill ~/PAI/.claude/skills/new-category/

# 2. Update all references (grep for old paths)
grep -r "skills/gardening-skills-wiki/old-category/skill" ~/PAI/.claude/skills/

# 3. Run health check
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh

# 4. Fix broken links
```

### Periodic Maintenance

```bash
# Monthly: Run full health check
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh

# Review and fix:
# - ❌ errors (broken links, missing skills)
# - ⚠️  warnings (naming, empty dirs)
# - 🧠 prompt-skill-analyzer: keep documentation/prompt-skill-analyzer.md,
#   hooks/prompt-submit/analyze-prompt-skills.ts, and skills/skill-rules.json in sync
```

## The Scripts

### `garden.sh` (Master)

Runs all health checks and provides comprehensive report.

**Usage:**
```bash
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh [skills_dir]
```

### `check-links.sh`

Validates all `@` references and cross-links.

**Checks:**
- Backtick-wrapped `@` links (disables resolution)
- Relative paths (`skills/` or `skills/gardening-skills-wiki/~/`) - should be `skills/`
- `@` reference resolution to existing files
- Skills in INDEX files exist
- Orphaned skills detection

### `check-naming.sh`

Validates naming conventions and frontmatter.

**Checks:**
- Directory name format
- Frontmatter completeness
- Empty directories

### `check-index-coverage.sh`

Validates INDEX completeness.

**Checks:**
- Skills listed in category INDEX
- Categories linked in main INDEX
- Descriptions present
- `skills/skill-rules.json` kept in sync with SKILL frontmatter and INDEX inventory

## Quick Reference

| Issue | Script | Fix |
|-------|--------|-----|
| Backtick-wrapped links | `check-links.sh` | Remove backticks from `@` refs (including any in `skills/skill-rules.json` comments/docs) |
| Relative paths | `check-links.sh` | Convert to `skills/` absolute |
| Broken links | `check-links.sh` | Update `@` references and any stale targets in `skills/skill-rules.json` |
| Orphaned skills | `check-links.sh` | Add to INDEX and/or remove/update rules in `skills/skill-rules.json` |
| Naming issues | `check-naming.sh` | Rename directories |
| Empty dirs | `check-naming.sh` | Remove with `rm -rf` |
| Missing from INDEX | `check-index-coverage.sh` | Add to INDEX.md (and add/remove matching rule entries in `skills/skill-rules.json` as needed) |
| No description | `check-index-coverage.sh` | Add to INDEX entry and ensure rule description in `skills/skill-rules.json` matches |
| Rules/metadata drift | `check-index-coverage.sh` | Align `skills/skill-rules.json` with SKILL frontmatter and INDEX inventory |

## Output Symbols

- ✅ **Pass** - Item is correct
- ❌ **Error** - Must fix (broken link, missing skill)
- ⚠️  **Warning** - Should fix (naming, empty dir)
- ℹ️  **Info** - Informational (no action needed)

## Integration with Workflow

**Before committing skill changes:**

```bash
~/PAI/.claude/skills/meta/gardening-skills-wiki/garden.sh
# Fix all ❌ errors
# Consider fixing ⚠️  warnings
git add .
git commit -m "Add/update skills"
```

**When links feel suspicious:**

```bash
~/PAI/.claude/skills/meta/gardening-skills-wiki/check-links.sh
```

**When INDEX seems incomplete:**

```bash
~/PAI/.claude/skills/meta/gardening-skills-wiki/check-index-coverage.sh
```

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Will check links manually" | Automated check is faster and more thorough |
| "INDEX probably fine" | Orphaned skills happen - always verify |
| "Naming doesn't matter" | Consistency aids discovery and maintenance |
| "Empty dir harmless" | Clutter confuses future maintainers |
| "Can skip periodic checks" | Issues compound - regular maintenance prevents big cleanups |

## Real-World Impact

**Without gardening:**
- Broken links discovered during urgent tasks
- Orphaned skills never found
- Naming drifts over time
- INDEX files fall out of sync

**With gardening:**
- 30-second health check catches issues early
- Automated validation prevents manual inspection
- Consistent structure aids discovery
- Wiki stays maintainable

## The Bottom Line

**Don't manually inspect - automate the checks.**

Run `garden.sh` after changes and periodically. Fix ❌ errors immediately, address ⚠️  warnings when convenient.

Maintained wiki = findable skills = reusable knowledge.
