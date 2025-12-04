#!/bin/bash
# Enable a Raycast script command by moving it to _enabled/
# Usage: enable-script.sh <script-file>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Default to env var or standard location
ENABLED_DIR="${RAYCAST_SCRIPTS_DIR:-$HOME/.dotfiles/raycast/script-commands}/_enabled"

SCRIPT_FILE="${1:-}"

if [[ -z "$SCRIPT_FILE" ]]; then
  echo "Usage: enable-script.sh <script-file>"
  exit 1
fi

if [[ ! -f "$SCRIPT_FILE" ]]; then
  echo "Error: File not found: $SCRIPT_FILE"
  exit 1
fi

# Validate before enabling
if ! "$SCRIPT_DIR/validate-metadata.sh" "$SCRIPT_FILE"; then
  echo ""
  echo "Fix validation errors before enabling."
  exit 1
fi

# Ensure _enabled directory exists
mkdir -p "$ENABLED_DIR"

# Get filename
FILENAME=$(basename "$SCRIPT_FILE")

# Check for existing file
if [[ -f "$ENABLED_DIR/$FILENAME" ]]; then
  echo "Warning: $FILENAME already exists in _enabled/"
  read -p "Overwrite? [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

# Make executable if shell script
if [[ "$SCRIPT_FILE" == *.sh ]]; then
  chmod +x "$SCRIPT_FILE"
fi

# Move to enabled
mv "$SCRIPT_FILE" "$ENABLED_DIR/"

echo "✓ Enabled: $ENABLED_DIR/$FILENAME"
echo ""
echo "Script is now available in Raycast."
