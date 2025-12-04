#!/bin/bash

# code-review.sh - Automated Code Review via OpenAI Codex CLI
# Performs rigorous pre-commit code review using AI-powered static analysis

set -euo pipefail

PROMPT_FILE="$HOME/.codex/prompts/code-review.md"

show_help() {
  cat << 'EOF'
code-review.sh - AI-Powered Code Review via OpenAI Codex CLI

USAGE:
  code-review.sh [OPTIONS] <request> [files...]
  code-review.sh --help

DESCRIPTION:
  Performs comprehensive pre-commit code review by combining:
    - Your staged git changes (via git diff --staged)
    - Your unstaged changes (via git diff)
    - OR committed changes (via --diff option)
    - A structured review prompt from ~/.codex/prompts/code-review.md
    - Original request/context for the changes
    - Optional related source files for additional context

  The script pipes all inputs to Codex CLI for AI-powered static analysis,
  checking for security issues, bugs, performance problems, code quality,
  and potential technical debt.

  Uses gpt-5-codex model with medium reasoning effort and 5-minute timeout.

REQUIRED ARGUMENTS:
  <request>            Original request or acceptance criteria
                       Describes what changed and why
                       Use quotes for multi-word descriptions
                       Example: "Add user authentication feature"

OPTIONAL ARGUMENTS:
  [files...]           Related source files to include as context
                       Files are displayed in full for reference
                       Useful for reviewing changes in context
                       Example: auth.py login.py middleware/auth.py

OPTIONS:
  --help, -h           Show this help message and exit
  --diff <RANGE>       Review committed changes instead of staged/unstaged
                       Use git diff range syntax (e.g., "main...HEAD", "HEAD~3..HEAD")
                       When specified, ignores staged/unstaged changes
                       Example: code-review.sh --diff "main...HEAD" "Review PR changes"

REQUIREMENTS:
  - codex CLI must be installed and authenticated
  - ~/.codex/prompts/code-review.md must exist
  - Git repository with changes (staged, unstaged, or --diff range)
  - Files must be readable (will show error if not found)

SANDBOX MODE:
  Uses --sandbox read-only (code reviews should not modify files)
  Suppresses thinking tokens (2>/dev/null) for clean output

EXAMPLES:
  # Basic review of all changes (staged and unstaged)
  code-review.sh "Fix authentication bug"

  # Review committed changes between branches
  code-review.sh --diff "main...HEAD" "Review PR changes"

  # Review last 3 commits
  code-review.sh --diff "HEAD~3..HEAD" "Review recent commits"

  # Review with related files for context
  code-review.sh "Refactor user service" \
    src/services/user.py src/models/user.py

  # Review with detailed acceptance criteria
  code-review.sh "Add rate limiting to API endpoints. \
Should handle 1000 req/min per user with Redis backend" \
    api/middleware/rate_limit.py

  # Review with multiple context files
  code-review.sh "Fix typo in docstring" utils.py

  # Review only staged changes (stage first, then run)
  git add auth.py && code-review.sh "Staged only review"

WORKFLOW:
  1. Make your changes:          Edit files as needed
  2. Run this script:            code-review.sh "description"
  3. Review AI feedback
  4. Make corrections if needed
  5. Re-run review:              code-review.sh "description"
  6. Stage and commit when approved:
     git add <files> && git commit -m "message"

RESUMING SESSIONS:
  After review completes, you can resume the session for follow-up questions:
    echo "Explain the security concern in detail" | \
      codex exec --skip-git-repo-check resume --last 2>/dev/null

OUTPUT FORMAT:
  The review includes severity-ranked issues:
    [CRITICAL] - Must fix before commit
    [HIGH]     - Should fix before commit
    [MEDIUM]   - Consider fixing
    [LOW]      - Optional improvements

  Each issue includes:
    - File path and line number
    - Description of the problem
    - Specific fix recommendation

FILES:
  Input:  ~/.codex/prompts/code-review.md  (review instructions)
  Source: git diff --staged                 (staged changes)
          git diff                           (unstaged changes)
          git diff <RANGE>                   (committed changes with --diff)
  Output: stdout                            (review results)

EXIT CODES:
  0    Review completed successfully
  1    Missing required arguments or files
  2    Codex CLI error
  124  Timeout (exceeded 5 minutes)

NOTES:
  - Uses gpt-5-codex model with medium reasoning effort (hardcoded)
  - 5-minute timeout to prevent hangs
  - Reviews BOTH staged and unstaged changes (or committed with --diff)
  - Does not modify any files (read-only mode)
  - Thinking tokens suppressed for clean output
  - Always uses --skip-git-repo-check flag
  - Session can be resumed for follow-up analysis
  - Runs in foreground to capture output properly (do not run in background)

SEE ALSO:
  git-diff(1), codex-exec(1)
  Documentation: skills/using-openai-codex-cli/SKILL.md

AUTHOR:
  Created for use with OpenAI Codex CLI automated code review workflows

EOF
}

# Check for help flag
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  show_help
  exit 0
fi

# Parse options
DIFF_RANGE=""
MODEL="gpt-5-codex"
REASONING="medium"
TIMEOUT="5m"
REQUEST=""
FILES=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --diff)
      DIFF_RANGE="$2"
      shift 2
      ;;
    *)
      if [ -z "$REQUEST" ]; then
        REQUEST="$1"
      else
        FILES+=("$1")
      fi
      shift
      ;;
  esac
done

# Validate required arguments
if [ -z "$REQUEST" ]; then
  echo "Error: Missing required argument: <request>" >&2
  echo "" >&2
  echo "Usage: $0 [OPTIONS] <request> [files...]" >&2
  echo "       $0 --help" >&2
  echo "" >&2
  echo "Example: $0 'Add auth feature' auth.py login.py" >&2
  echo "Example: $0 --diff 'main...HEAD' 'Review PR changes'" >&2
  exit 1
fi

# Validate prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE" >&2
  echo "Please create the code review prompt at this location." >&2
  exit 1
fi

# Build the input
{
  cat "$PROMPT_FILE"
  
  if [ -n "$DIFF_RANGE" ]; then
    # Review committed changes from diff range
    echo -e "\n\n=== GIT DIFF (COMMITTED CHANGES: $DIFF_RANGE) ==="
    if git diff --quiet "$DIFF_RANGE" 2>/dev/null; then
      echo "Error: No changes found in range: $DIFF_RANGE" >&2
      exit 1
    else
      git diff "$DIFF_RANGE"
    fi
  else
    # Review staged and unstaged changes
    echo -e "\n\n=== GIT DIFF (STAGED CHANGES) ==="
    if git diff --staged --quiet 2>/dev/null; then
      echo "(No staged changes)"
    else
      git diff --staged
    fi
    
    echo -e "\n\n=== GIT DIFF (UNSTAGED CHANGES) ==="
    if git diff --quiet 2>/dev/null; then
      echo "(No unstaged changes)"
    else
      git diff
    fi
    
    # Warn if no changes found
    if git diff --staged --quiet 2>/dev/null && git diff --quiet 2>/dev/null; then
      echo "" >&2
      echo "Warning: No staged or unstaged changes found." >&2
      echo "To review committed changes, use: $0 --diff 'main...HEAD' \"$REQUEST\"" >&2
      echo "" >&2
    fi
  fi
  
  echo -e "\n\n=== ORIGINAL REQUEST ==="
  echo "$REQUEST"
  
  if [ ${#FILES[@]} -gt 0 ]; then
    echo -e "\n\n=== RELATED FILES ==="
    for file in "${FILES[@]}"; do
      echo -e "\n--- $file ---"
      if [ -f "$file" ]; then
        cat "$file"
      else
        echo "Error: File not found: $file" >&2
      fi
    done
  fi
} | timeout "$TIMEOUT" codex exec --skip-git-repo-check \
    --model "$MODEL" \
    --config model_reasoning_effort="$REASONING" \
    --sandbox read-only \
    2>/dev/null