#!/bin/bash
# Validate Raycast script command metadata
# Usage: validate-metadata.sh <script-file>

set -euo pipefail

SCRIPT_FILE="${1:-}"

if [[ -z "$SCRIPT_FILE" ]]; then
  echo "Usage: validate-metadata.sh <script-file>"
  exit 1
fi

if [[ ! -f "$SCRIPT_FILE" ]]; then
  echo "Error: File not found: $SCRIPT_FILE"
  exit 1
fi

ERRORS=()

# Check required metadata
if ! grep -q "@raycast.schemaVersion" "$SCRIPT_FILE"; then
  ERRORS+=("Missing required: @raycast.schemaVersion")
fi

if ! grep -q "@raycast.title" "$SCRIPT_FILE"; then
  ERRORS+=("Missing required: @raycast.title")
fi

if ! grep -q "@raycast.mode" "$SCRIPT_FILE"; then
  ERRORS+=("Missing required: @raycast.mode")
fi

# Validate mode value
MODE=$(grep -o "@raycast.mode [a-zA-Z]*" "$SCRIPT_FILE" 2>/dev/null | awk '{print $2}' || echo "")
if [[ -n "$MODE" ]]; then
  case "$MODE" in
    fullOutput|compact|silent|inline) ;;
    *) ERRORS+=("Invalid mode '$MODE'. Must be: fullOutput, compact, silent, or inline") ;;
  esac
fi

# Check inline mode has refreshTime
if [[ "$MODE" == "inline" ]] && ! grep -q "@raycast.refreshTime" "$SCRIPT_FILE"; then
  ERRORS+=("Mode 'inline' requires @raycast.refreshTime")
fi

# Check for .template in filename
if [[ "$SCRIPT_FILE" == *".template."* ]]; then
  ERRORS+=("Filename contains '.template.' - Raycast will ignore this file")
fi

# Check file is executable (for shell scripts)
if [[ "$SCRIPT_FILE" == *.sh ]] && [[ ! -x "$SCRIPT_FILE" ]]; then
  ERRORS+=("Script is not executable (run: chmod +x $SCRIPT_FILE)")
fi

# ============================================
# AUTO-DETECT COMMON ISSUES
# ============================================

WARNINGS=()

# Get file extension first (needed for shebang checks)
EXT="${SCRIPT_FILE##*.}"
FIRST_LINE=$(head -1 "$SCRIPT_FILE")

# Issue: Missing shebang (only for script types that need it)
# Note: Swift files use // comments, AppleScript doesn't need shebang
case "$EXT" in
  sh|py|js|rb)
    if [[ ! "$FIRST_LINE" =~ ^#! ]]; then
      ERRORS+=("Missing shebang (first line should be #!/bin/bash or similar)")
    fi
    ;;
esac

# Issue: Wrong shebang for file type
case "$EXT" in
  sh)
    if [[ ! "$FIRST_LINE" =~ ^#!/.*(bash|sh|zsh) ]]; then
      WARNINGS+=("Shell script should have #!/bin/bash shebang")
    fi
    ;;
  py)
    if [[ ! "$FIRST_LINE" =~ ^#!/.*(python|env\ python) ]]; then
      WARNINGS+=("Python script should have #!/usr/bin/env python3 shebang")
    fi
    ;;
  js)
    if [[ ! "$FIRST_LINE" =~ ^#!/.*(node|env\ node) ]]; then
      WARNINGS+=("Node script should have #!/usr/bin/env node shebang")
    fi
    ;;
esac

# Issue: Title too long (Raycast truncates at ~50 chars in UI)
TITLE=$(grep -m1 "@raycast.title" "$SCRIPT_FILE" 2>/dev/null | sed 's/.*@raycast.title //' | tr -d '\r')
if [[ ${#TITLE} -gt 50 ]]; then
  WARNINGS+=("Title is ${#TITLE} chars (may be truncated in Raycast UI)")
fi

# Issue: Missing icon (not required but recommended)
if ! grep -q "@raycast.icon" "$SCRIPT_FILE"; then
  WARNINGS+=("No @raycast.icon specified (consider adding one)")
fi

# Issue: Arguments declared but not used
for i in 1 2 3; do
  if grep -q "@raycast.argument$i" "$SCRIPT_FILE"; then
    # Check if $1, $2, $3 or sys.argv or process.argv is used
    case "$EXT" in
      sh)
        if ! grep -q "\$$i" "$SCRIPT_FILE"; then
          WARNINGS+=("argument$i declared but \$$i not found in script")
        fi
        ;;
      py)
        if ! grep -q "sys.argv\[$i\]" "$SCRIPT_FILE" && ! grep -qE "argv\[.+\]|argparse" "$SCRIPT_FILE"; then
          WARNINGS+=("argument$i declared but may not be used (check sys.argv)")
        fi
        ;;
      js)
        if ! grep -q "process.argv\[$((i+1))\]" "$SCRIPT_FILE" && ! grep -qE "argv\[.+\]" "$SCRIPT_FILE"; then
          WARNINGS+=("argument$i declared but may not be used (check process.argv)")
        fi
        ;;
    esac
  fi
done

# Issue: Using echo in silent mode (won't be seen)
if [[ "$MODE" == "silent" ]]; then
  case "$EXT" in
    sh)
      if grep -qE "^[^#]*echo " "$SCRIPT_FILE"; then
        WARNINGS+=("Using 'echo' in silent mode (output won't be shown)")
      fi
      ;;
    py)
      if grep -qE "^[^#]*print\(" "$SCRIPT_FILE"; then
        WARNINGS+=("Using 'print()' in silent mode (output won't be shown)")
      fi
      ;;
    js)
      if grep -qE "^[^/]*console\.log\(" "$SCRIPT_FILE"; then
        WARNINGS+=("Using 'console.log()' in silent mode (output won't be shown)")
      fi
      ;;
  esac
fi

# Issue: refreshTime on non-inline mode
if [[ "$MODE" != "inline" ]] && grep -q "@raycast.refreshTime" "$SCRIPT_FILE"; then
  WARNINGS+=("@raycast.refreshTime only works with inline mode")
fi

# Issue: needsConfirmation on silent mode (confirmation shown but no feedback)
if [[ "$MODE" == "silent" ]] && grep -q "@raycast.needsConfirmation" "$SCRIPT_FILE"; then
  WARNINGS+=("needsConfirmation with silent mode: user gets no feedback after confirming")
fi

# Issue: Package dependency without checking
if [[ "$EXT" == "py" ]] && grep -qE "^import |^from " "$SCRIPT_FILE"; then
  IMPORTS=$(grep -E "^import |^from " "$SCRIPT_FILE" | grep -v "import os\|import sys\|import json\|import re\|import subprocess" | head -3)
  if [[ -n "$IMPORTS" ]]; then
    WARNINGS+=("External imports detected - ensure @raycast.packageManager is set if needed")
  fi
fi

# Issue: Description missing (recommended for searchability)
if ! grep -q "@raycast.description" "$SCRIPT_FILE"; then
  WARNINGS+=("No @raycast.description (helps with Raycast search)")
fi

# Report results
if [[ ${#ERRORS[@]} -eq 0 ]]; then
  echo "✓ Valid: $SCRIPT_FILE"

  # Show warnings even if valid
  if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo
    echo "⚠ Suggestions:"
    for warning in "${WARNINGS[@]}"; do
      echo "  - $warning"
    done
  fi
  exit 0
else
  echo "✗ Invalid: $SCRIPT_FILE"
  echo
  echo "Errors:"
  for error in "${ERRORS[@]}"; do
    echo "  ✗ $error"
  done

  if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    echo
    echo "Warnings:"
    for warning in "${WARNINGS[@]}"; do
      echo "  ⚠ $warning"
    done
  fi
  exit 1
fi
