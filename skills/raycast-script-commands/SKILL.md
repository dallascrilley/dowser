---
name: raycast-script-commands
description: >-
  Create, edit, and manage Raycast script commands. Use when users ask to build
  Raycast scripts, automate macOS tasks via Raycast, create launcher shortcuts,
  or develop script commands with arguments and output modes. Covers all
  supported languages (bash, python, node, swift, ruby, applescript) and
  metadata configuration.
when_to_use: >-
  When building Raycast scripts, automating macOS tasks via Raycast launcher,
  creating shortcuts with arguments, or configuring script command metadata.
version: 1.0.0
category: automation-and-scripting
short_description: 'Create, edit, and manage Raycast script commands.'
---

# Raycast Script Commands

Create script commands that execute from Raycast with a few keystrokes.

## Setup

**Skill scripts location:** `~/.claude/skills/automation-and-scripting/raycast-script-commands/scripts/`

**Target scripts directory:** defaults to `~/.dotfiles/raycast/script-commands`. Override with:

```bash
export RAYCAST_SCRIPTS_DIR="/path/to/your/scripts"
```

For convenience, set an alias:

```bash
SKILL_DIR="$HOME/.claude/skills/automation-and-scripting/raycast-script-commands"
```

## Find Inspiration First

Before writing, search for existing examples:

```bash
# Semantic search - use concepts, not just keywords
$SKILL_DIR/scripts/find-examples.sh copy --list      # finds clipboard, pbcopy examples
$SKILL_DIR/scripts/find-examples.sh music --list     # finds spotify, apple music examples

# Full content search
$SKILL_DIR/scripts/find-examples.sh clipboard        # shows complete code blocks

# Interactive fuzzy search (requires fzf)
$SKILL_DIR/scripts/find-examples.sh --fuzzy

# Search GitHub community repo
$SKILL_DIR/scripts/find-examples.sh git --remote

# Browse categories
$SKILL_DIR/scripts/browse-categories.sh              # List all
$SKILL_DIR/scripts/browse-categories.sh developer-utils  # Open in browser
```

## Quick Start

Use automation scripts for fastest workflow:

```bash
# Create new script from template
$SKILL_DIR/scripts/new-script.sh my-command bash

# Validate metadata
$SKILL_DIR/scripts/validate-metadata.sh my-command.sh

# Enable (moves to _enabled/ after validation)
$SKILL_DIR/scripts/enable-script.sh my-command.sh

# List enabled scripts
$SKILL_DIR/scripts/list-enabled.sh
$SKILL_DIR/scripts/list-enabled.sh --detail

# Disable a script
$SKILL_DIR/scripts/disable-script.sh my-command.sh
```

Or manually:
1. Copy template from `assets/`
2. Add required metadata comments
3. Implement script logic
4. Run `scripts/enable-script.sh` to validate and enable

## Required Metadata

Every script needs these comment-based metadata fields:

```bash
# @raycast.schemaVersion 1
# @raycast.title Command Name
# @raycast.mode fullOutput|compact|silent|inline
```

For JS/Swift, use `//` comments instead of `#`.

## Output Modes

| Mode | Behavior |
|------|----------|
| `fullOutput` | Terminal-like view showing all output |
| `compact` | Toast showing last line of output |
| `silent` | HUD overlay after Raycast closes |
| `inline` | First line shown in command list (requires `refreshTime`) |

## Optional Metadata

```bash
# @raycast.packageName Category Name
# @raycast.icon emoji or path or https://url
# @raycast.iconDark icon for dark theme
# @raycast.description Brief description
# @raycast.author Your Name
# @raycast.authorURL https://your-url
# @raycast.needsConfirmation true  # for destructive actions
# @raycast.refreshTime 10s|1m|1h   # required for inline mode
# @raycast.currentDirectoryPath ~
```

## Arguments (up to 3)

Define inputs shown in Raycast search bar:

```bash
# @raycast.argument1 { "type": "text", "placeholder": "Query" }
# @raycast.argument2 { "type": "text", "placeholder": "Optional", "optional": true }
# @raycast.argument3 { "type": "dropdown", "placeholder": "Select", "data": [{"title": "A", "value": "a"}] }
```

Argument types: `text`, `password`, `dropdown`

Access arguments:
- Bash: `$1`, `$2`, `$3`
- Python: `sys.argv[1:]`
- Node: `process.argv.slice(2)`
- Swift: `CommandLine.arguments[1...]`
- Ruby: `ARGV[0]`, `ARGV[1]`

Optional fields: `optional: true`, `percentEncoded: true`

## Error Handling

Exit with non-zero status and echo error message:

```bash
if ! command_succeeds; then
  echo "Error: something went wrong"
  exit 1
fi
```

## Scripts

Automation scripts in `$SKILL_DIR/scripts/`:

| Script | Purpose |
|--------|---------|
| `find-examples.sh <query> [--list] [--remote]` | Semantic search with concept expansion |
| `browse-categories.sh [category]` | List or open community categories |
| `new-script.sh <name> [lang]` | Create from template |
| `validate-metadata.sh <file>` | Check required fields + auto-detect 10+ issues |
| `enable-script.sh <file>` | Validate and move to `_enabled/` |
| `list-enabled.sh [--detail]` | Show active scripts |
| `disable-script.sh <name>` | Remove from `_enabled/` |

## Templates

Language templates in `assets/`:
- `bash.template.sh`
- `python.template.py`
- `node.template.js`
- `swift.template.swift`
- `ruby.template.rb`
- `applescript.template.applescript`

## References

Detailed documentation (load as needed):
- `references/metadata.md` - Complete metadata reference
- `references/output-modes.md` - Output modes and ANSI colors
- `references/arguments.md` - Argument configuration
- `references/examples.md` - Ready-to-use patterns (clipboard, dashboard, API, etc.)
- `references/icons.md` - Icon reference by category
- `references/community.md` - Finding and using community scripts

## Common Patterns

### Web Search

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Search Site
# @raycast.mode silent
# @raycast.argument1 { "type": "text", "placeholder": "Query", "percentEncoded": true }

open "https://example.com/search?q=$1"
```

### Dashboard Inline

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title CPU Usage
# @raycast.mode inline
# @raycast.refreshTime 10s

echo "CPU: $(ps -A -o %cpu | awk '{s+=$1} END {print s "%"}')"
```

### Clipboard Transform

```bash
#!/bin/bash
# @raycast.schemaVersion 1
# @raycast.title Uppercase
# @raycast.mode compact

pbpaste | tr '[:lower:]' '[:upper:]' | pbcopy
echo "Uppercased"
```

See `references/examples.md` for 35+ ready-to-use patterns.

## Troubleshooting

- **Script not appearing**: Check filename doesn't contain `.template`, verify all required metadata
- **Shell errors**: Run through ShellCheck linter
- **Output issues in compact/silent/inline**: Use quiet flags, avoid streaming output
- **Validation fails**: Run `$SKILL_DIR/scripts/validate-metadata.sh` for specific errors (auto-detects 10+ issues)
