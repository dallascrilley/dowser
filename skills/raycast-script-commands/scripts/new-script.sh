#!/bin/bash
# Create a new Raycast script command from template
# Usage: new-script.sh <name> [language]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"
OUTPUT_DIR="${RAYCAST_SCRIPTS_DIR:-$(pwd)}"

NAME="${1:-}"
LANG="${2:-bash}"

if [[ -z "$NAME" ]]; then
  echo "Usage: new-script.sh <name> [language]"
  echo ""
  echo "Languages: bash (default), python, node, swift, ruby, applescript"
  echo ""
  echo "Examples:"
  echo "  new-script.sh my-command"
  echo "  new-script.sh search-docs python"
  exit 1
fi

# Determine extension and template
case "$LANG" in
  bash|sh)
    EXT="sh"
    TEMPLATE="bash.template.sh"
    ;;
  python|py)
    EXT="py"
    TEMPLATE="python.template.py"
    ;;
  node|js|javascript)
    EXT="js"
    TEMPLATE="node.template.js"
    ;;
  swift)
    EXT="swift"
    TEMPLATE="swift.template.swift"
    ;;
  ruby|rb)
    EXT="rb"
    TEMPLATE="ruby.template.rb"
    ;;
  applescript|osascript)
    EXT="applescript"
    TEMPLATE="applescript.template.applescript"
    ;;
  *)
    echo "Error: Unknown language '$LANG'"
    echo "Supported: bash, python, node, swift, ruby, applescript"
    exit 1
    ;;
esac

# Check template exists
TEMPLATE_PATH="$ASSETS_DIR/$TEMPLATE"
if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Error: Template not found: $TEMPLATE_PATH"
  exit 1
fi

# Generate output filename
OUTPUT_FILE="$OUTPUT_DIR/$NAME.$EXT"

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "Error: File already exists: $OUTPUT_FILE"
  exit 1
fi

# Copy template
cp "$TEMPLATE_PATH" "$OUTPUT_FILE"

# Make executable
chmod +x "$OUTPUT_FILE"

# Replace placeholder title with name
sed -i '' "s/@raycast.title My Command/@raycast.title ${NAME//-/ }/" "$OUTPUT_FILE"

echo "✓ Created: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Edit the script metadata and implementation"
echo "  2. Test: ./$NAME.$EXT"
echo "  3. Enable: enable-script.sh $OUTPUT_FILE"
