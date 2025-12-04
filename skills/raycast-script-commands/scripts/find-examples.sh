#!/bin/bash
# Find Raycast script examples by keyword
# Usage: find-examples.sh <query> [--list] [--remote]
#
# Options:
#   --list    Show only matching script titles (not full content)
#   --remote  Also search GitHub community repo

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXAMPLES_FILE="$SCRIPT_DIR/../references/examples.md"

QUERY="${1:-}"
LIST_MODE=false
REMOTE_MODE=false
FUZZY_MODE=false

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --list) LIST_MODE=true ;;
    --remote) REMOTE_MODE=true ;;
    --fuzzy) FUZZY_MODE=true ;;
  esac
done

# ============================================
# SEMANTIC KEYWORD EXPANSION
# ============================================
# Map common concepts to actual keywords in examples

expand_query() {
  local query_lower
  query_lower=$(echo "$1" | tr '[:upper:]' '[:lower:]')

  case "$query_lower" in
    # Clipboard concepts
    copy)      echo "clipboard|pbcopy|copy" ;;
    paste)     echo "clipboard|pbpaste|paste" ;;
    clipboard) echo "clipboard|pbcopy|pbpaste|copy" ;;

    # Music concepts
    music)     echo "spotify|apple|music|audio" ;;
    song)      echo "spotify|music|track|song" ;;
    play)      echo "spotify|music|toggle|play" ;;
    pause)     echo "spotify|music|toggle|pause" ;;

    # Development concepts
    code)      echo "vscode|visual|studio|code" ;;
    editor)    echo "vscode|sublime|editor" ;;
    terminal)  echo "iterm|warp|hyper|terminal" ;;
    dev)       echo "developer|git|npm|node|python|dev" ;;

    # System concepts
    notification) echo "notify|alert|notification" ;;
    alert)     echo "notification|notify|alert" ;;
    dark)      echo "dark|mode|theme|appearance" ;;
    light)     echo "light|mode|theme|appearance" ;;
    theme)     echo "dark|light|mode|appearance|theme" ;;

    # Files
    file)      echo "finder|file|path" ;;
    folder)    echo "directory|finder|folder" ;;
    directory) echo "folder|finder|directory" ;;

    # Web concepts
    search)    echo "google|search|browser|web" ;;
    browse)    echo "browser|safari|chrome|firefox|browse" ;;
    url)       echo "link|uri|browser|url" ;;
    link)      echo "url|uri|link" ;;

    # Utilities
    random)    echo "uuid|generate|random" ;;
    uuid)      echo "uuid|generate|random|unique" ;;
    date)      echo "date|time|timestamp" ;;
    time)      echo "date|time|timestamp|clock" ;;
    calc)      echo "calculator|math|calc" ;;
    math)      echo "calculator|calc|math" ;;

    # No expansion - return original
    *)         echo "$1" ;;
  esac
}

if [[ -z "$QUERY" ]] || [[ "$QUERY" == "--"* ]]; then
  echo "Usage: find-examples.sh <query> [--list] [--remote] [--fuzzy]"
  echo ""
  echo "Options:"
  echo "  --list    Show only matching script titles"
  echo "  --remote  Also search GitHub community repo"
  echo "  --fuzzy   Use fzf for interactive fuzzy search"
  echo ""
  echo "Semantic search enabled - try concepts like:"
  echo "  'copy' → finds clipboard, pbcopy examples"
  echo "  'music' → finds spotify, apple music examples"
  echo "  'code' → finds vscode, editor examples"
  echo ""
  echo "Examples:"
  echo "  find-examples.sh clipboard"
  echo "  find-examples.sh copy --list"
  echo "  find-examples.sh git --remote"
  exit 1
fi

# Expand query with semantic synonyms
EXPANDED_QUERY=$(expand_query "$QUERY")
if [[ "$EXPANDED_QUERY" != "$QUERY" ]]; then
  echo "(Expanded '$QUERY' → searching: $EXPANDED_QUERY)"
  echo ""
fi

if [[ ! -f "$EXAMPLES_FILE" ]]; then
  echo "Error: Examples file not found: $EXAMPLES_FILE"
  exit 1
fi

# Interactive fuzzy mode using fzf
if $FUZZY_MODE; then
  if command -v fzf &> /dev/null; then
    echo "=== Interactive Fuzzy Search ==="
    echo "(Type to filter, Enter to select, Esc to cancel)"
    echo ""

    # Extract all script titles and let user fuzzy search
    SELECTED=$(grep "^### " "$EXAMPLES_FILE" | sed 's/^### //' | fzf --height=40% --reverse --prompt="Script: ")

    if [[ -n "$SELECTED" ]]; then
      echo "Selected: $SELECTED"
      echo ""
      # Show the full script block (escape special chars for awk)
      ESCAPED_SELECTED=$(printf '%s\n' "$SELECTED" | sed 's/[[\.*^$()+?{|]/\\&/g')
      awk "/^### ${ESCAPED_SELECTED}\$/,/^### [^$]|^## [^#]/" "$EXAMPLES_FILE" | head -40
    fi
    exit 0
  else
    echo "fzf not installed. Install with: brew install fzf"
    echo "Falling back to regular search..."
    echo ""
  fi
fi

echo "=== Searching for '$QUERY' ==="
echo ""

# Use expanded query for grep (supports regex OR pattern)
SEARCH_PATTERN="$EXPANDED_QUERY"

if $LIST_MODE; then
  # Extract script titles (### headings) from matching sections
  # Find lines with query, get nearby ### headings
  MATCHES=$(grep -iE -B10 "$SEARCH_PATTERN" "$EXAMPLES_FILE" 2>/dev/null | grep "^### " | sort -u || true)

  if [[ -n "$MATCHES" ]]; then
    COUNT=$(echo "$MATCHES" | wc -l | tr -d ' ')
    echo "Found $COUNT matching scripts:"
    echo ""
    echo "${MATCHES//### /  • }"
  else
    echo "No matches for '$QUERY'"
  fi
else
  # Full content mode - extract complete script blocks
  # Find ### headings that have the query nearby, then show the block

  TEMP_FILE=$(mktemp)
  trap 'rm -f "$TEMP_FILE"' EXIT

  # Get all matching sections with context (using expanded pattern)
  grep -iE -B5 -A25 "$SEARCH_PATTERN" "$EXAMPLES_FILE" 2>/dev/null > "$TEMP_FILE" || true

  if [[ -s "$TEMP_FILE" ]]; then
    # Count unique script headings
    COUNT=$(grep "^### " "$TEMP_FILE" 2>/dev/null | sort -u | wc -l | tr -d ' ')
    echo "Found $COUNT matching scripts:"
    echo ""

    # Show content, limit to first 100 lines
    head -100 "$TEMP_FILE"

    TOTAL_LINES=$(wc -l < "$TEMP_FILE" | tr -d ' ')
    if [[ $TOTAL_LINES -gt 100 ]]; then
      echo ""
      echo "... (showing first 100 of $TOTAL_LINES lines, use --list for titles only)"
    fi
  else
    echo "No matches for '$QUERY'"
    echo ""
    echo "Try:"
    echo "  • Different keywords (e.g., 'pbcopy' instead of 'clipboard')"
    echo "  • Browse categories: scripts/browse-categories.sh"
    echo "  • Search GitHub: find-examples.sh $QUERY --remote"
  fi
fi

# Remote search if requested
if $REMOTE_MODE; then
  echo ""
  echo "=== GitHub Community Repo ==="
  echo ""

  # URL encode the query
  ENCODED_QUERY="${QUERY// /%20}"
  SEARCH_URL="https://api.github.com/search/code?q=${ENCODED_QUERY}+in:file+repo:raycast/script-commands+extension:sh"

  RESULTS=$(curl -s "$SEARCH_URL" 2>/dev/null)

  if echo "$RESULTS" | grep -q '"total_count"'; then
    COUNT=$(echo "$RESULTS" | grep -o '"total_count":[0-9]*' | cut -d: -f2)
    echo "Found $COUNT matches in raycast/script-commands"
    echo ""

    # Extract file paths
    PATHS=$(echo "$RESULTS" | grep -o '"path":"[^"]*"' | cut -d'"' -f4 | head -10)

    if [[ -n "$PATHS" ]]; then
      echo "$PATHS" | while read -r path; do
        NAME=$(basename "$path" .sh)
        echo "  • $NAME"
        echo "    https://github.com/raycast/script-commands/blob/master/$path"
      done
    fi

    if [[ $COUNT -gt 10 ]]; then
      echo ""
      echo "... showing first 10 of $COUNT. Browse more:"
      echo "    https://github.com/raycast/script-commands/search?q=$ENCODED_QUERY"
    fi
  else
    echo "GitHub API rate limited or error. Browse directly:"
    echo "  https://github.com/raycast/script-commands/search?q=$ENCODED_QUERY"
  fi
fi
