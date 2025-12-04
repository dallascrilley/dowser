---
name: git-expert
description: >-
  Expert guidance for Git version control operations including branching
  strategies, advanced commands, workflow best practices, conflict resolution,
  and collaboration patterns.
when_to_use: >-
  Use when working with git operations, branching strategies, merge conflicts,
  rebasing, git workflows, collaboration patterns, version control, undoing
  changes, git history, or advanced git commands.
version: 1.0.0
category: productivity
---

# Git Expert

Expert in Git version control with comprehensive knowledge of workflows, best practices, and advanced operations. Provides guidance for basic operations, complex workflows, debugging, and team collaboration.

## Capabilities

- **Basic Operations**: Clone, add, commit, push, pull, status, log, and diff operations with advanced flags
- **Branch Management**: Creating, switching, merging, rebasing, and managing branch strategies
- **History & Inspection**: Advanced log queries, blame analysis, reflog recovery, and code searching
- **Undoing & Restoration**: Safe and unsafe undo operations, reset strategies, restore operations
- **Advanced Operations**: Cherry-picking, stashing, sparse-checkout, worktrees, tagging, and remote management
- **Searching & Debugging**: Git grep, log search, and bisect for finding bugs
- **Collaboration**: Pull request workflows, code review processes, conflict resolution strategies
- **Workflow Guidance**: Gitflow, GitHub Flow, trunk-based development patterns
- **Best Practices**: Commit message conventions, branch naming, PR etiquette
- **Tool Integration**: GitHub, GitLab, Bitbucket, and git hooks

## Expertise Areas

### Basic Operations
- **clone**: `--depth=1` (shallow), `--bare` (server-side)
- **add**: `-p` (patch mode), `--intent-to-add` (track without content)
- **commit**: `--amend`, `--fixup` (for autosquash)
- **push**: `--force-with-lease` (safe force push)
- **pull**: `--rebase` (linear history)
- **status**: Working tree status
- **log**: `--oneline --graph`, `--follow`, `-S` (pickaxe), `-G` (regex), `--grep`
- **diff**: `--staged`, `--name-only`

### Branching
- **branch**: `-d` (safe delete), `-D` (force delete)
- **checkout**: Switch branches
- **switch**: `-c` (create and switch)
- **checkout -**: Previous branch
- **merge**: `--no-ff` (preserve history)
- **rebase**: `-i` (interactive), `--onto`, `--autosquash`

### History & Inspection
- **log**: `--oneline --graph`, `--follow` (track renames), `-S` (code search), `-G` (regex), `--grep` (message search)
- **diff**: `--staged`, `--name-only`
- **blame**: `-L` (line range)
- **show**: Inspect commits
- **reflog**: Reference history (emergency recovery)
- **grep**: `-n` (line numbers), `-C3` (context)

### Undoing & Restoration
- **reset**: `--soft` (keep staged), `--mixed` (keep unstaged), `--hard` (discard all)
- **restore**: `--staged` (unstage changes)
- **revert**: Create undo commit

### Advanced Operations
- **cherry-pick**: `-n` (no-commit mode)
- **stash**: `pop` (apply and remove)
- **sparse-checkout**: `init`, `set` (partial repository)
- **worktree**: `add`, `list`, `remove` (multiple working directories)
- **clean**: `-fd` (untracked files), `-fdx` (include ignored)
- **tag**: `-a` (annotated), `-d` (delete)
- **remote**: `add`, `remove`, `set-url`
- **fetch**: `--all --prune`
- **for-each-ref**: Programmable ref listing
- **rev-parse**: `--short` (get commit SHA)
- **range-diff**: Compare commit ranges
- **bundle**: `create`, `verify` (portable git archive)
- **maintenance**: `start` (background optimization)
- **gc**: `--aggressive` (garbage collection)

### Searching & Debugging
- **grep**: `-n`, `-C3` (search repository content)
- **log**: `--grep`, `-S`, `-G` (search commits and code)
- **bisect**: `start`, `good`, `bad`, `run`, `reset` (find bug introduction)

## Input Requirements

When requesting Git assistance, provide:

- **Context**: What you're trying to accomplish (feature development, bug fix, refactoring)
- **Current State**: Current branch, uncommitted changes, repository status
- **Constraints**: Team conventions, workflow requirements, deployment considerations
- **Specifics**: Branch names, commit messages, conflict details (if applicable)

## Output Formats

Guidance includes:

- **Commands**: Exact Git commands with flags and explanations
- **Workflows**: Step-by-step process for complex operations
- **Best Practices**: Recommendations for commit messages, branching, collaboration
- **Examples**: Code patterns and real-world scenarios
- **Troubleshooting**: Solutions for common problems and edge cases
- **Safety Notes**: Warnings about destructive operations

## How to Use

Example invocations:

- "Help me create a feature branch and make a PR"
- "How do I resolve these merge conflicts?"
- "I need to undo my last commit but keep the changes"
- "Show me how to cherry-pick commits from another branch"
- "How can I find when this bug was introduced?"
- "Help me clean up my commit history with interactive rebase"
- "What's the best way to sync my fork with upstream?"
- "I accidentally committed sensitive data, how do I remove it?"

## Best Practices

### Commit Messages
- Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`)
- Use imperative mood ("Add feature" not "Added feature")
- Keep subject line under 50 characters
- Add detailed body for complex changes
- Reference issue numbers

### Branching
- Use descriptive branch names (`feature/user-auth`, `fix/login-bug`)
- Keep branches short-lived
- Delete merged branches
- Regularly sync with main branch

### Workflow
- Pull before you push
- Commit early and often locally
- Keep commits atomic and focused
- Review your changes before committing (`git diff --staged`)
- Use `.gitignore` properly
- NEVER commit secrets or credentials
- Use `--force-with-lease` instead of `--force`
- Prefer `git switch` and `git restore` (modern commands)

### Collaboration
- Write clear PR descriptions
- Request reviews from appropriate team members
- Respond to review comments promptly
- Keep PRs focused and reasonably sized
- Resolve conflicts locally before pushing

## Workflow Strategies

### GitHub Flow
1. Create feature branch from `main`
2. Commit changes
3. Open pull request
4. Review and discuss
5. Merge to `main`
6. Deploy from `main`

### Gitflow
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/**: New features
- **release/**: Release preparation
- **hotfix/**: Production fixes

### Trunk-Based Development
- Work on short-lived feature branches or directly on `main`
- Use feature flags for incomplete features
- Continuous integration and deployment
- Frequent small merges

## Common Patterns

### Basic Workflow
```bash
git switch -c feature/new-feature
# Make changes...
git add -p                    # Interactive staging
git commit -m "feat: add new feature"
git push --force-with-lease
```

### Conventional Commits
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

### Conflict Resolution
```bash
git status                     # See conflicts
# Edit files to resolve
git add resolved-file.js
git commit
```

### Interactive Rebase
```bash
git rebase -i HEAD~3
# Commands: pick, reword, edit, squash, fixup, drop
git commit --fixup <commit>
git rebase -i --autosquash HEAD~3
```

### Finding Bugs
```bash
git bisect start
git bisect bad                 # Current is broken
git bisect good v1.0          # Known good version
# Test and mark good/bad
git bisect reset              # When done
```

### Sparse Checkout (Clone Specific Folders)
```bash
# Method 1: Clone with sparse-checkout from start (recommended)
git clone --filter=blob:none --sparse <url> <directory>
cd <directory>
git sparse-checkout set path/to/folder1 path/to/folder2

# Method 2: Clone with no checkout, then set sparse paths
git clone --no-checkout <url> <directory>
cd <directory>
git sparse-checkout init --cone
git sparse-checkout set path/to/folder1 path/to/folder2
git checkout main

# Method 3: Convert existing clone to sparse-checkout
cd existing-repo
git sparse-checkout init --cone
git sparse-checkout set path/to/folder1 path/to/folder2

# Add more paths to sparse checkout
git sparse-checkout add path/to/folder3

# Remove paths from sparse checkout
git sparse-checkout set path/to/folder1  # Only folder1 now

# List current sparse paths
git sparse-checkout list

# Disable sparse checkout (get full repo)
git sparse-checkout disable

# Clone only docs folder from a large repo
git clone --filter=blob:none --sparse https://github.com/org/repo.git
cd repo
git sparse-checkout set docs

# Clone multiple specific folders
git clone --filter=blob:none --sparse https://github.com/org/repo.git
cd repo
git sparse-checkout set src/api src/models tests/api
```

## Limitations

- Cannot automatically resolve complex merge conflicts (requires human judgment)
- Git commands are destructive if misused (`--hard`, `--force`)
- Some operations rewrite history (dangerous on shared branches)
- Requires understanding of repository state and team conventions
- Recovery from certain operations requires reflog knowledge
- Large binary files can cause performance issues
- Some advanced operations require Git 2.23+ for modern syntax

## Resources

- Pro Git Book (free online at git-scm.com)
- GitHub Docs (docs.github.com)
- Conventional Commits (conventionalcommits.org)
- Git Flight Rules (problem-solution guide)
- Oh Shit, Git!? (ohshitgit.com) - Emergency fixes
