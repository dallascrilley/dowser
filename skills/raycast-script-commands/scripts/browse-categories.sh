#!/bin/bash
# Browse Raycast script command categories
# Usage: browse-categories.sh [category]

set -euo pipefail

CATEGORIES=(
  "ai:AI tools (Gemini, ChatGPT, Claude)"
  "apps:Application integrations"
  "browsing:Web browsing utilities"
  "communication:Email, Slack, messaging"
  "conversions:Base64, URL encode, units"
  "dashboard:System stats, crypto, weather"
  "developer-utils:Git, UUID, JSON, hashing"
  "home:Smart home (Elgato, Hue)"
  "images:Screenshots, image processing"
  "math:Calculators, converters"
  "media:Spotify, Apple Music"
  "navigation:Folder shortcuts"
  "productivity:Bitwarden, writing tools"
  "remote-control:Device control"
  "system:Power, Finder, Dock, clipboard"
  "web-searches:Google, GitHub, Stack Overflow"
)

CATEGORY="${1:-}"

if [[ -z "$CATEGORY" ]]; then
  echo "Raycast Script Command Categories"
  echo "=================================="
  echo ""
  for cat in "${CATEGORIES[@]}"; do
    NAME="${cat%%:*}"
    DESC="${cat#*:}"
    printf "  %-20s %s\n" "$NAME" "$DESC"
  done
  echo ""
  echo "Usage: browse-categories.sh <category>"
  echo ""
  echo "Opens the GitHub folder for that category."
  exit 0
fi

# Open the category in browser
URL="https://github.com/raycast/script-commands/tree/master/commands/$CATEGORY"
echo "Opening: $URL"
open "$URL" 2>/dev/null || echo "Visit: $URL"
