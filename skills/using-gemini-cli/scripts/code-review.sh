#!/bin/bash

# code-review.sh - Automated Code Review via Google Gemini CLI
# Performs rigorous pre-commit code review using AI-powered static analysis

set -euo pipefail

PROMPT_FILE="${GEMINI_PROMPTS_DIR:-$HOME/.gemini/commands/}"
DEFAULT_MODEL="gemini-3-pro-preview"

show_help() {
  cat << 'EOF'
code-review.sh - AI-Powered Code Review via Google Gemini CLI

USAGE:
  code-review.sh [OPTIONS] <request> [files...]
  code-review.sh --help

DESCRIPTION:
  Performs comprehensive pre-commit code review by combining:
    - Your staged git changes (via git diff --staged)
    - Your unstaged changes (via git diff)
    - A structured review prompt from ~/.gemini/prompts/code-review.md
    - Original request/context for the changes
    - Optional related source files for additional context

  The script pipes all inputs to Gemini CLI for AI-powered static analysis,
  checking for security issues, bugs, performance problems, code quality,
  and potential technical debt.

  Uses gemini-3-pro-preview model by default (use -m to override) with 5-minute timeout.

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
  --model, -m MODEL    Specify Gemini model (default: gemini-3-pro-preview)
                       Options: gemini-2.5-flash (faster), gemini-3-pro-preview (deeper)
  --output-format FMT  Output format: text (default) or json
                       Use json for structured parsing with jq

REQUIREMENTS:
  - gemini CLI must be installed and authenticated
  - ~/.gemini/prompts/code-review.md must exist (or set GEMINI_PROMPTS_DIR)
  - Git repository with changes (staged or unstaged)
  - Files must be readable (will show error if not found)

EXAMPLES:
  # Basic review of all changes (staged and unstaged)
  code-review.sh "Fix authentication bug"

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

  # Use faster model for quick reviews
  code-review.sh -m gemini-2.5-flash "Quick review"

  # Get structured JSON output
  code-review.sh --output-format json "Review changes" | jq '.response'

WORKFLOW:
  1. Make your changes:          Edit files as needed
  2. Run this script:            code-review.sh "description"
  3. Review AI feedback
  4. Make corrections if needed
  5. Re-run review:              code-review.sh "description"
  6. Stage and commit when approved:
     git add <files> && git commit -m "message"

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

  With --output-format json, output is structured JSON:
    {
      "response": "review text...",
      "stats": { ... }
    }

FILES:
  Input:  ~/.gemini/commands/code-review/best-practices.toml  (review instructions)
  Source: git diff --staged                 (staged changes)
          git diff                           (unstaged changes)
  Output: stdout                            (review results)

EXIT CODES:
  0    Review completed successfully
  1    Missing required arguments or files
  2    Gemini CLI error
  124  Timeout (exceeded 5 minutes)

NOTES:
  - Uses gemini-3-pro-preview model by default (use -m to change)
  - 5-minute timeout to prevent hangs
  - Reviews BOTH staged and unstaged changes
  - Does not modify any files (read-only by default)
  - Use --output-format json for programmatic processing

SEE ALSO:
  git-diff(1), gemini(1)
  Documentation: skills/agents-and-skills/using-gemini-cli/SKILL.md
  Headless mode: https://geminicli.com/docs/cli/headless/

AUTHOR:
  Created for use with Google Gemini CLI automated code review workflows

EOF
}

# Parse command-line options
MODEL="$DEFAULT_MODEL"
OUTPUT_FORMAT="text"
REQUEST=""
FILES=()

while [[ $# -gt 0 ]]; do
  case $1 in
    --help|-h)
      show_help
      exit 0
      ;;
    --model|-m)
      MODEL="$2"
      shift 2
      ;;
    --output-format)
      OUTPUT_FORMAT="$2"
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
  echo "Usage: $0 <request> [files...]" >&2
  echo "       $0 --help" >&2
  echo "" >&2
  echo "Example: $0 'Add auth feature' auth.py login.py" >&2
  exit 1
fi

# Validate prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE" >&2
  echo "Please create the code review prompt at this location." >&2
  echo "You can set GEMINI_PROMPTS_DIR to use a different directory." >&2
  exit 1
fi

# Validate output format
if [[ "$OUTPUT_FORMAT" != "text" && "$OUTPUT_FORMAT" != "json" ]]; then
  echo "Error: Invalid output format: $OUTPUT_FORMAT" >&2
  echo "Valid formats: text, json" >&2
  exit 1
fi

TIMEOUT="5m"

# Build comprehensive prompt with all context and pipe to Gemini CLI
# Using --prompt flag to ensure headless mode is explicitly triggered
{
  cat "$PROMPT_FILE"
  
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
} | timeout "$TIMEOUT" gemini \
    --prompt "Perform a comprehensive code review following the instructions and analyzing the provided code changes" \
    --model "$MODEL" \
    --output-format "$OUTPUT_FORMAT"