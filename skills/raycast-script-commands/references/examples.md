# Ready-to-Use Patterns

Copy and customize these patterns for common use cases.

## Web & Search

### Open URL with Query

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Search Google
# @raycast.mode silent
# @raycast.icon 🔍
# @raycast.argument1 { "type": "text", "placeholder": "Query", "percentEncoded": true }

open "https://www.google.com/search?q=$1"
```

### Open GitHub Repo

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Open Repo
# @raycast.mode silent
# @raycast.icon 🐙
# @raycast.argument1 { "type": "text", "placeholder": "owner/repo" }

open "https://github.com/$1"
```

## Clipboard Operations

### Copy Current Date

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Copy Date
# @raycast.mode compact
# @raycast.icon 📅

DATE=$(date +"%Y-%m-%d")
echo -n "$DATE" | pbcopy
echo "Copied: $DATE"
```

### Copy UUID

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Copy UUID
# @raycast.mode compact
# @raycast.icon 🔑

UUID=$(uuidgen | tr '[:upper:]' '[:lower:]')
echo -n "$UUID" | pbcopy
echo "Copied: $UUID"
```

### Transform Clipboard

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Uppercase Clipboard
# @raycast.mode compact
# @raycast.icon 🔠

CONTENT=$(pbpaste | tr '[:lower:]' '[:upper:]')
echo -n "$CONTENT" | pbcopy
echo "Uppercased clipboard"
```

## System Info (Inline Dashboard)

### CPU Usage

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title CPU
# @raycast.mode inline
# @raycast.refreshTime 10s
# @raycast.icon 💻

ps -A -o %cpu | awk '{s+=$1} END {printf "%.1f%%", s}'
```

### Memory Usage

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Memory
# @raycast.mode inline
# @raycast.refreshTime 30s
# @raycast.icon 🧠

memory_pressure | grep "System-wide memory free percentage:" | awk '{print 100-$5"%"}'
```

### Disk Space

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Disk
# @raycast.mode inline
# @raycast.refreshTime 1h
# @raycast.icon 💾

df -h / | awk 'NR==2 {print $5 " used (" $4 " free)"}'
```

### IP Address

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title IP
# @raycast.mode inline
# @raycast.refreshTime 5m
# @raycast.icon 🌐

curl -s ifconfig.me
```

## App Control

### Toggle App

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Toggle Spotify
# @raycast.mode silent
# @raycast.icon 🎵

if pgrep -x "Spotify" > /dev/null; then
  osascript -e 'tell application "Spotify" to quit'
else
  open -a "Spotify"
fi
```

### Kill App

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Kill App
# @raycast.mode compact
# @raycast.needsConfirmation true
# @raycast.icon ☠️
# @raycast.argument1 { "type": "text", "placeholder": "App name" }

pkill -x "$1" && echo "Killed $1" || echo "App not running: $1"
```

## Notifications

### Show Notification

```applescript
#!/usr/bin/osascript
# @raycast.schemaVersion 1
# @raycast.title Notify
# @raycast.mode silent
# @raycast.icon 🔔
# @raycast.argument1 { "type": "text", "placeholder": "Message" }

on run argv
  display notification (item 1 of argv) with title "Raycast"
end run
```

### Speak Text

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Speak
# @raycast.mode silent
# @raycast.icon 🗣️
# @raycast.argument1 { "type": "text", "placeholder": "Text to speak" }

say "$1"
```

## Developer Tools

### JSON Pretty Print Clipboard

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Pretty JSON
# @raycast.mode compact
# @raycast.icon 📋

if pbpaste | jq . > /tmp/pretty.json 2>/dev/null; then
  cat /tmp/pretty.json | pbcopy
  echo "JSON formatted"
else
  echo "Invalid JSON in clipboard"
  exit 1
fi
```

### Base64 Encode/Decode

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Base64 Toggle
# @raycast.mode compact
# @raycast.icon 🔄

CONTENT=$(pbpaste)
DECODED=$(echo "$CONTENT" | base64 -d 2>/dev/null)

if [[ $? -eq 0 && -n "$DECODED" ]]; then
  echo -n "$DECODED" | pbcopy
  echo "Decoded"
else
  echo -n "$CONTENT" | base64 | pbcopy
  echo "Encoded"
fi
```

### Git Status

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Git Status
# @raycast.mode fullOutput
# @raycast.icon 📦
# @raycast.currentDirectoryPath ~/projects/myrepo

git status
```

## File Operations

### Quick Note

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Quick Note
# @raycast.mode compact
# @raycast.icon 📝
# @raycast.argument1 { "type": "text", "placeholder": "Note content" }

NOTES_DIR="$HOME/Notes"
mkdir -p "$NOTES_DIR"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
echo "$1" >> "$NOTES_DIR/quick-notes.md"
echo "Saved note"
```

### Open Recent Downloads

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Recent Download
# @raycast.mode silent
# @raycast.icon 📥

RECENT=$(ls -t ~/Downloads | head -1)
open "$HOME/Downloads/$RECENT"
```

## API Calls

### Check Website Status

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Site Status
# @raycast.mode compact
# @raycast.icon 🌐
# @raycast.argument1 { "type": "text", "placeholder": "URL" }

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$1")
if [[ "$STATUS" == "200" ]]; then
  echo "✓ $1 is up ($STATUS)"
else
  echo "✗ $1 returned $STATUS"
fi
```

### Weather (using wttr.in)

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Weather
# @raycast.mode inline
# @raycast.refreshTime 1h
# @raycast.icon 🌤️

curl -s "wttr.in/?format=%c+%t"
```

---

## From Raycast Community Repository

These patterns are adapted from https://github.com/raycast/script-commands

### System Activity Dashboard (Color-Coded)

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title System Activity
# @raycast.mode inline
# @raycast.refreshTime 5s
# @raycast.packageName Dashboard
# @raycast.icon 📈

ps -A -o %cpu,%mem | awk '{ cpu += $1; mem += $2} END {print "CPU: "cpu"% MEM: "mem"%"}'
```

### Git Status Dashboard (Color-Coded)

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Git Status
# @raycast.mode inline
# @raycast.refreshTime 5m
# @raycast.packageName Git
# @raycast.icon 📦
# @raycast.currentDirectoryPath ~/your-repo

MESSAGE=""

ADDED=$(git status --short | grep -c " A")
[ $ADDED -gt 0 ] && MESSAGE="$MESSAGE \033[32m$ADDED Added\033[0m"

MODIFIED=$(git status --short | grep -c " M")
[ $MODIFIED -gt 0 ] && MESSAGE="$MESSAGE \033[33m$MODIFIED Modified\033[0m"

DELETED=$(git status --short | grep -c " D")
[ $DELETED -gt 0 ] && MESSAGE="$MESSAGE \033[31m$DELETED Deleted\033[0m"

UNTRACKED=$(git status --short | grep -c "??")
[ $UNTRACKED -gt 0 ] && MESSAGE="$MESSAGE \033[34m$UNTRACKED Untracked\033[0m"

[ -z "$MESSAGE" ] && MESSAGE="No pending changes"

echo -e $MESSAGE
```

### Prettify JSON (Full Output)

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Prettify JSON
# @raycast.mode fullOutput
# @raycast.packageName Developer Utilities
# @raycast.icon 💻
# @raycast.description Pretty prints the JSON currently in the clipboard.

pbpaste | python3 -m json.tool
```

### Generate UUID (Silent)

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Generate UUID
# @raycast.mode silent
# @raycast.packageName Developer Utilities
# @raycast.icon 💻
# @raycast.description Generates a UUID and copies it to the clipboard.

uuidgen | pbcopy
echo "UUID Generated"
```

### Spotify Play/Pause (AppleScript)

```applescript
#!/usr/bin/osascript
# @raycast.schemaVersion 1
# @raycast.title Toggle Play/Pause
# @raycast.mode silent
# @raycast.packageName Spotify
# @raycast.icon 🎵
# @raycast.description Toggles play or pause of current track in Spotify.

tell application "Spotify" to playpause
```

### Apple Music Play/Pause

```applescript
#!/usr/bin/osascript
# @raycast.schemaVersion 1
# @raycast.title Toggle Play/Pause
# @raycast.mode silent
# @raycast.packageName Music
# @raycast.icon 🎵

tell application "Music" to playpause
```

### Empty Trash

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Empty Trash
# @raycast.mode compact
# @raycast.packageName System
# @raycast.icon 🗑️
# @raycast.needsConfirmation true

rm -rf ~/.Trash/*
echo "Trash emptied"
```

### Toggle Hidden Files

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Toggle Hidden Files
# @raycast.mode compact
# @raycast.packageName Finder
# @raycast.icon 👁️

CURRENT=$(defaults read com.apple.finder AppleShowAllFiles)
if [ "$CURRENT" = "TRUE" ]; then
  defaults write com.apple.finder AppleShowAllFiles FALSE
  echo "Hidden files: OFF"
else
  defaults write com.apple.finder AppleShowAllFiles TRUE
  echo "Hidden files: ON"
fi
killall Finder
```

### Flush DNS

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Flush DNS
# @raycast.mode compact
# @raycast.packageName Network
# @raycast.icon 🌐

sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
echo "DNS cache flushed"
```

### Lock Screen

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Lock Screen
# @raycast.mode silent
# @raycast.packageName System
# @raycast.icon 🔒

pmset displaysleepnow
```

### Bitcoin Price

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Bitcoin Price
# @raycast.mode inline
# @raycast.refreshTime 5m
# @raycast.packageName Dashboard
# @raycast.icon ₿

curl -s "https://api.coindesk.com/v1/bpi/currentprice/USD.json" | jq -r '.bpi.USD.rate'
```

### Year Progress

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Year Progress
# @raycast.mode inline
# @raycast.refreshTime 1d
# @raycast.packageName Dashboard
# @raycast.icon 📅

DAY=$(date +%j)
PROGRESS=$(echo "scale=1; $DAY * 100 / 365" | bc)
echo "${PROGRESS}% of year complete"
```

### World Clock

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title World Time
# @raycast.mode inline
# @raycast.refreshTime 1m
# @raycast.packageName Dashboard
# @raycast.icon 🌍

NY=$(TZ="America/New_York" date +%H:%M)
LON=$(TZ="Europe/London" date +%H:%M)
TOK=$(TZ="Asia/Tokyo" date +%H:%M)
echo "NY:$NY LON:$LON TOK:$TOK"
```

### Password Generator

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Generate Password
# @raycast.mode compact
# @raycast.packageName Developer Utilities
# @raycast.icon 🔐
# @raycast.argument1 { "type": "text", "placeholder": "Length (default: 16)", "optional": true }

LENGTH=${1:-16}
PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c "$LENGTH")
echo -n "$PASSWORD" | pbcopy
echo "Password copied ($LENGTH chars)"
```

### URL Encode Clipboard

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title URL Encode
# @raycast.mode compact
# @raycast.packageName Developer Utilities
# @raycast.icon 🔗

pbpaste | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read().strip()))" | pbcopy
echo "URL encoded"
```

### URL Decode Clipboard

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title URL Decode
# @raycast.mode compact
# @raycast.packageName Developer Utilities
# @raycast.icon 🔗

pbpaste | python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.stdin.read().strip()))" | pbcopy
echo "URL decoded"
```
