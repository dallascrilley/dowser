#!/bin/bash
# List enabled Raycast script commands
# Usage: list-enabled.sh [--detail]

# Default to env var or standard location
ENABLED_DIR="${RAYCAST_SCRIPTS_DIR:-$HOME/.dotfiles/raycast/script-commands}/_enabled"
DETAIL_MODE=false

[[ "$1" == "--detail" ]] && DETAIL_MODE=true

if [[ ! -d "$ENABLED_DIR" ]]; then
  echo "No _enabled/ directory found"
  exit 0
fi

SCRIPTS=$(find "$ENABLED_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.swift" -o -name "*.rb" -o -name "*.applescript" \) 2>/dev/null | sort)

if [[ -z "$SCRIPTS" ]]; then
  echo "No enabled scripts found"
  exit 0
fi

COUNT=$(echo "$SCRIPTS" | wc -l | tr -d ' ')
echo "=== $COUNT Enabled Scripts ==="
echo

while IFS= read -r script; do
  FILENAME=$(basename "$script")

  if $DETAIL_MODE; then
    # Extract metadata
    TITLE=$(grep -m1 "@raycast.title" "$script" 2>/dev/null | sed 's/.*@raycast.title //' | tr -d '\r')
    MODE=$(grep -m1 "@raycast.mode" "$script" 2>/dev/null | sed 's/.*@raycast.mode //' | tr -d '\r')
    ICON=$(grep -m1 "@raycast.icon" "$script" 2>/dev/null | sed 's/.*@raycast.icon //' | tr -d '\r')

    echo "${ICON:-📄} $FILENAME"
    echo "   Title: ${TITLE:-<none>}"
    echo "   Mode:  ${MODE:-<none>}"
    echo
  else
    # Simple list with title
    TITLE=$(grep -m1 "@raycast.title" "$script" 2>/dev/null | sed 's/.*@raycast.title //' | tr -d '\r')
    ICON=$(grep -m1 "@raycast.icon" "$script" 2>/dev/null | sed 's/.*@raycast.icon //' | tr -d '\r')
    echo "  ${ICON:-📄} ${TITLE:-$FILENAME} ($FILENAME)"
  fi
done <<< "$SCRIPTS"
