# How to Use the Git Expert Skill

Hey Claude—I just added the "git-expert" skill. Can you help me with Git version control?

## Example Invocations

### Basic Operations

**Example 1: Feature Branch Workflow**
```
Hey Claude—I just added the "git-expert" skill. Can you walk me through creating a feature branch, making commits, and opening a PR?
```

**Example 2: Undoing Changes**
```
Hey Claude—I just added the "git-expert" skill. I accidentally committed something to the wrong branch. How do I undo this while keeping my changes?
```

**Example 3: Commit Message Help**
```
Hey Claude—I just added the "git-expert" skill. I made changes to the authentication module. What's a good commit message following Conventional Commits?
```

### Intermediate Operations

**Example 4: Conflict Resolution**
```
Hey Claude—I just added the "git-expert" skill. I'm getting merge conflicts when pulling from main. Can you guide me through resolving them?
```

**Example 5: Branch Management**
```
Hey Claude—I just added the "git-expert" skill. I have multiple old feature branches. What's the safe way to clean them up?
```

**Example 6: Syncing Fork**
```
Hey Claude—I just added the "git-expert" skill. My fork is behind the upstream repository. How do I sync it?
```

### Advanced Operations

**Example 7: Interactive Rebase**
```
Hey Claude—I just added the "git-expert" skill. I have 5 messy commits on my feature branch. Help me squash them into logical commits.
```

**Example 8: Cherry-Picking**
```
Hey Claude—I just added the "git-expert" skill. I need to cherry-pick commits from the develop branch to a hotfix branch. How do I do this safely?
```

**Example 9: Git Bisect**
```
Hey Claude—I just added the "git-expert" skill. A bug was introduced sometime in the last 20 commits. How can I find which commit caused it?
```

**Example 10: Emergency Recovery**
```
Hey Claude—I just added the "git-expert" skill. I accidentally did a hard reset and lost my work. Can I recover it?
```

**Example 11: Sparse Checkout (Clone Specific Folders)**
```
Hey Claude—I just added the "git-expert" skill. I only need the docs folder from a large repository. How do I clone just that specific folder?
```

### Workflow & Strategy

**Example 12: Workflow Setup**
```
Hey Claude—I just added the "git-expert" skill. Our team is starting a new project. What Git workflow would you recommend and how do we set it up?
```

**Example 13: Sensitive Data Removal**
```
Hey Claude—I just added the "git-expert" skill. I accidentally committed an API key. How do I remove it from history?
```

## What to Provide

For best results, include:

- **Current situation**: What you're trying to accomplish
- **Repository state**: Current branch, uncommitted changes
- **Team context**: Workflow conventions, collaboration requirements
- **Specific details**: Branch names, commit messages, error messages
- **Constraints**: What you can't do (e.g., can't rewrite shared history)

## What You'll Get

The git-expert skill provides:

- **Exact commands**: Copy-paste ready Git commands with explanations
- **Step-by-step guidance**: Detailed workflows for complex operations
- **Best practices**: Recommendations for commits, branches, and collaboration
- **Safety warnings**: Alerts about destructive operations
- **Alternative approaches**: Multiple solutions when applicable
- **Troubleshooting**: Solutions for common errors and edge cases
- **Examples**: Real-world scenarios and code patterns
- **Workflow strategies**: GitHub Flow, Gitflow, trunk-based development

## Tips for Success

1. **Be specific**: "How do I rebase?" vs "How do I rebase my feature branch on main while preserving my commits?"
2. **Share context**: Mention your workflow (GitHub Flow, Gitflow, etc.)
3. **Include errors**: Copy full error messages if you're stuck
4. **Ask about safety**: Request validation before destructive operations
5. **Follow up**: Ask for clarification on any step you're unsure about

## Common Scenarios

### Starting a New Feature
```
Help me start a new feature branch for user authentication
```

### Cleaning Up History
```
I have 10 WIP commits. Help me combine them into 3 logical commits
```

### Fixing Mistakes
```
I committed to main instead of a feature branch. How do I fix this?
```

### Collaboration
```
What's the best way to handle code review feedback in my PR?
```

### Advanced Debugging
```
Help me use git bisect to find which commit broke the login feature
```

### Partial Repository Cloning
```
I need to clone only the src/api and docs folders from a 10GB repository
```

## Related Skills

The git-expert skill works well with:
- Code review skills
- CI/CD automation skills
- Project management skills
- Documentation skills

---

**Note**: This is a prompt-based skill that provides expert guidance. Always review commands before executing them, especially destructive operations like `reset --hard` or `push --force`.
