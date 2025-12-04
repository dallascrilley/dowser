#!/bin/bash
# Disable a Raycast script (move from _enabled/ back to parent)
# Usage: disable-script.sh <script-name>

# Default to env var or standard location
BASE_DIR="${RAYCAST_SCRIPTS_DIR:-$HOME/.dotfiles/raycast/script-commands}"
ENABLED_DIR="${BASE_DIR}/_enabled"
PARENT_DIR="${BASE_DIR}"

if [[ -z "$1" ]]; then
  echo "Usage: disable-script.sh <script-name>"
  echo
  echo "Currently enabled scripts:"
  find "$ENABLED_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.swift" -o -name "*.rb" -o -name "*.applescript" \) -exec basename {} \; 2>/dev/null | sort
  exit 1
fi

SCRIPT_NAME="$1"

# Find the script
SCRIPT_PATH=$(find "$ENABLED_DIR" -name "$SCRIPT_NAME" -type f 2>/dev/null | head -1)

# Try with extension if not found
if [[ -z "$SCRIPT_PATH" ]]; then
  for ext in sh py js swift rb applescript; do
    SCRIPT_PATH=$(find "$ENABLED_DIR" -name "${SCRIPT_NAME}.${ext}" -type f 2>/dev/null | head -1)
    [[ -n "$SCRIPT_PATH" ]] && break
  done
fi

if [[ -z "$SCRIPT_PATH" ]]; then
  echo "Error: Script '$SCRIPT_NAME' not found in _enabled/"
  echo
  echo "Available scripts:"
  find "$ENABLED_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.swift" -o -name "*.rb" -o -name "*.applescript" \) -exec basename {} \; 2>/dev/null | sort
  exit 1
fi

FILENAME=$(basename "$SCRIPT_PATH")
DEST="$PARENT_DIR/$FILENAME"

# Check if destination exists
if [[ -f "$DEST" ]]; then
  echo "Warning: $FILENAME already exists in parent directory"
  echo "Overwrite? (y/N)"
  read -r CONFIRM
  [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]] && exit 1
fi

# Move the script
if mv "$SCRIPT_PATH" "$DEST"; then
  echo "✓ Disabled: $FILENAME"
  echo "  Moved to: $DEST"
else
  echo "✗ Failed to disable script"
  exit 1
fi
