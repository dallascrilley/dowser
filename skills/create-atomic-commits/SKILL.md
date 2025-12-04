---
name: create-atomic-commits
short_description: >-
  Analyze git changes and create atomic, meaningful commits following
  Conventional Commits format with logical organization.
description: >
  This skill provides systematic analysis of git changes and creates atomic,
  meaningful commits following Conventional Commits format. Use when organizing
  multiple changes into logical commits, splitting mixed work into separate
  commits, or creating commit series from complex changesets.


  Use when: user says 'organize commits', 'split changes', 'create atomic
  commits', 'analyze git changes', 'smart commits', or has multiple unrelated
  changes to commit.


  Keywords: git, commits, atomic commits, conventional commits, git analysis,
  commit organization, git staging, change classification, commit series
when_to_use: >
  Use when organizing multiple changes into logical commits, splitting mixed
  work, creating commit series, analyzing git changes chronologically, or user
  says 'organize commits', 'split changes', 'create atomic commits'.
version: 1.0.0
category: productivity
---

# Create Atomic Commits

## When to Activate This Skill
- User requests commit organization or analysis
- Multiple unrelated changes need to be split into logical commits
- User says "organize my commits", "split these changes", "create atomic commits"
- Mixed feature/bug fix/documentation changes need separation
- Chronological commit organization is needed
- User wants to exclude certain files from commit analysis

## Core Workflow

Follow this systematic approach to analyze git changes and create atomic commits:

### Step 1: Analyze Current Git State

1a) **Extract file timestamps to understand chronological order:**

```bash
# Use helper script to get creation and modification dates
git-file-timestamps --all

# Or for specific subsets:
# git-file-timestamps --staged    # Only staged files
# git-file-timestamps --unstaged  # Only unstaged files
```

1b) **Run these commands in parallel to gather complete git state:**

```bash
git status
git diff --staged
git diff
git status -s
```

1c) **CRITICAL: Read and analyze the diff output carefully**

**Before proceeding to classification or commit messages, you MUST:**
- **Read the actual diff content** - Don't just see file names, examine what changed
- **Understand the code changes** - Look at added/removed/modified lines
- **Identify the purpose** - What problem does this change solve?
- **Note dependencies** - Do changes in one file relate to changes in another?
- **Spot patterns** - Are multiple files making the same type of change?

**Why this matters**: Commit messages based on file names alone are generic and unhelpful. Commit messages based on understanding actual code changes are precise and valuable.

**Example of poor analysis (file-name based):**
- "Updated user service" ❌

**Example of good analysis (diff-based):**
- "Added email validation to user registration flow to prevent duplicate accounts" ✅

**Filter ignored files**: If user specifies files to ignore (e.g., "ignore log files", "skip test files"), interpret casually and exclude matching files from all analysis and recommendations.

**For each changed file** (excluding ignored), identify:
- File path and type
- **Specific lines added/removed/modified** (from diff output)
- **Functional purpose of changes** (inferred from actual code changes, not file name)
- Creation date (first git add)
- Last modification date (filesystem and git)
- Chronological order based on timestamps

### Step 2: Generate File-Level Summaries Based on Diff Analysis

For each changed file (excluding ignored files), write 2-3 sentence summary **based on the actual diff content you analyzed in Step 1c**:

- **What** was changed (specific code changes, not generic "updated file")
- **Why** it was changed (inferred from the actual code modifications in the diff)
- **Impact** on functionality (based on understanding what the code does)

**Requirements:**
- ✅ Reference actual code elements (functions, variables, logic) from the diff
- ✅ Explain the purpose of the change based on code analysis
- ✅ Connect changes across files when they're related
- ❌ Don't write vague summaries like "modified user service"
- ❌ Don't guess - base summaries on what you see in the diff

**Example:**
```
src/auth/jwt.ts:
Added validateTokenExpiry() function and integrated it into the
verifyToken() middleware. This prevents expired tokens from being
accepted, fixing a security vulnerability where old tokens remained valid.
```

### Step 3: Classify Changes

Group all changes (excluding ignored files) by logical category:
- **feat**: Feature additions
- **fix**: Bug fixes
- **refactor**: Code restructuring without functionality change
- **docs**: Documentation updates
- **style**: Formatting, whitespace, missing semicolons
- **test**: Test additions or modifications
- **perf**: Performance improvements
- **chore**: Build process, dependencies, configuration

### Step 4: Organize into Commit Series with Meaningful Messages

Based on your diff analysis from Steps 1-3, organize changes into atomic commits. For each commit:

- **Identify files** to include (exclude ignored files completely)
- **Write commit message based on actual code changes** (from diff analysis, not file names)
- **Use Conventional Commits format**: `<type>(<scope>): <subject>`
- **Keep commits focused** - single logical change per commit
- **Ensure independence** - each commit should be functional on its own
- **Maintain chronology** when requested

**Commit Message Quality Standards:**

✅ **Good commit subjects** (based on understanding code changes):
- `feat(auth): add JWT token expiry validation to prevent security bypass`
- `fix(api): handle null user IDs by returning 404 instead of 500 error`
- `refactor(db): extract user query logic into reusable repository pattern`

❌ **Poor commit subjects** (generic, file-name based):
- `feat(auth): update auth files`
- `fix(api): fix bug`
- `refactor(db): refactor database code`

**The subject line should answer: "What specific problem does this change solve?"**

**Conventional Commits Format:**
```
<type>(<scope>): <subject>

[optional body explaining what and why, referencing specific code changes]

```

### Step 5: Present Analysis

Present findings in this format:

#### File Summaries
- **filename**: [2-3 sentence summary]
- **another-file**: [2-3 sentence summary]

#### Recommended Commit Series

1. `feat(auth): add JWT token validation`
   - Files: src/auth/jwt.ts, src/auth/middleware.ts
   - Rationale: Groups related authentication changes

2. `fix(api): handle null user IDs in profile endpoint`
   - Files: src/api/profile.ts, tests/api/profile.test.ts
   - Rationale: Bug fix with corresponding test update

3. `docs(readme): update installation instructions`
   - Files: README.md
   - Rationale: Documentation change, separate from code

#### Overall Change Summary
[3-5 sentence summary of all changes across the commit series]

### Step 6: Interactive Execution

After presenting analysis:

1. **If no files staged**: Help decide what to stage based on recommended commit series
2. **For each recommended commit**:
   - Show suggested commit message
   - Ask if user wants to:
     - Use message as-is
     - Modify the message
     - Add more details to body
     - Stage different files
     - Skip this commit
3. **Once approved**: Create commit(s) and show result
4. **Repeat** for each commit in series
5. **Finally**: Ask if user wants to push or create PR

## Common Patterns

### Pattern 1: Mixed Feature and Bug Fix

User has changes spanning new feature work and bug fixes.

**Analysis approach**:
- Classify each file by purpose
- Separate feature work (`feat:`) from bug fixes (`fix:`)
- Group related files within each category
- Create 2+ commits (minimum one feat, one fix)

**Example**:
```bash
# Commit 1: Feature
git add src/features/dashboard.ts src/components/DashboardView.tsx
git commit -m "feat(dashboard): add real-time data display"

# Commit 2: Bug fix
git add src/api/users.ts tests/api/users.test.ts
git commit -m "fix(api): correct null handling in user lookup"
```

### Pattern 2: Large Refactoring Across Modules

User has extensive refactoring touching many files across multiple modules.

**Analysis approach**:
- Group by module or logical layer
- Maintain functional independence between commits
- Consider chronological order if refactoring was staged
- Create 4-6 commits representing refactoring phases

**Example**:
```bash
# Commit 1: Core types
git add src/types/*.ts
git commit -m "refactor(types): extract shared interfaces"

# Commit 2: Update module A
git add src/moduleA/*.ts
git commit -m "refactor(moduleA): use new shared types"

# Commit 3: Update module B
git add src/moduleB/*.ts
git commit -m "refactor(moduleB): use new shared types"
```

### Pattern 3: Excluding Temporary Files

User has legitimate changes plus log files, test artifacts, or temporary files.

**Analysis approach**:
- Accept user's casual description ("ignore logs", "skip test files")
- Match files based on description (*.log, tmp/*, test-results/*, etc.)
- Completely exclude matched files from analysis
- Never mention excluded files in commit recommendations

**Example**:
```bash
# User says: "organize commits but ignore log files"
# Script automatically excludes: *.log, logs/*, debug.txt, etc.
# Only analyzes and commits relevant source files
```

## Key Commands

```bash
# Get file timestamps for all changed files
git-file-timestamps --all

# Get timestamps for staged files only
git-file-timestamps --staged

# Get timestamps for unstaged files only
git-file-timestamps --unstaged

# View git status
git status

# View staged changes
git diff --staged

# View unstaged changes
git diff

# Stage specific files
git add file1.ts file2.ts

# Create commit with message
git commit -m "type(scope): subject"

# Create commit with body
git commit -m "$(cat <<'EOF'
type(scope): subject

Body explaining what and why.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## Supplementary Resources

**Script**: `scripts/git-file-timestamps.sh`
- Extracts creation and modification dates for git files
- Supports --all, --staged, --unstaged options
- Handles deleted files and git command failures gracefully
- Outputs formatted, colored display for easy reading
- Available globally as `git-file-timestamps` command (installed in ~/bin)

## Key Principles

1. **Atomic commits** - Each commit should represent one logical change that could be reverted independently
2. **Conventional format** - Always use `<type>(<scope>): <subject>` format for consistency
3. **Functional independence** - Each commit should leave codebase in working state
4. **Clear rationale** - Explain grouping decisions so user understands organization
5. **Respect exclusions** - Never include files user wants ignored
6. **Interactive approval** - Always confirm commit messages before creating them
