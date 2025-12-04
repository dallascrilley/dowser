# Raycast Script Command Metadata Reference

## Required Parameters

| Name | Description | Example |
|------|-------------|---------|
| `schemaVersion` | API schema version. Always `1`. | `@raycast.schemaVersion 1` |
| `title` | Display name in Raycast search | `@raycast.title My Command` |
| `mode` | Output presentation mode | `@raycast.mode compact` |

## Optional Parameters

| Name | Description | Example |
|------|-------------|---------|
| `packageName` | Category shown as subtitle | `@raycast.packageName Utilities` |
| `icon` | Emoji, file path, or https URL (64px recommended) | `@raycast.icon 🚀` |
| `iconDark` | Icon for dark theme | `@raycast.iconDark 🌙` |
| `description` | Brief description of command | `@raycast.description Does X` |
| `author` | Author name | `@raycast.author John Doe` |
| `authorURL` | Author URL/social/email | `@raycast.authorURL https://...` |
| `currentDirectoryPath` | Working directory for script | `@raycast.currentDirectoryPath ~` |
| `needsConfirmation` | Show confirmation before running | `@raycast.needsConfirmation true` |
| `refreshTime` | Auto-refresh interval (inline mode) | `@raycast.refreshTime 10s` |
| `argument1..3` | Input arguments (see arguments.md) | `@raycast.argument1 {...}` |

## Mode Values

- `fullOutput` - Terminal-like scrollable view
- `compact` - Toast with last line
- `silent` - HUD overlay after close
- `inline` - Embedded in command list (requires `refreshTime`)

## Refresh Time Format

For inline mode: `10s`, `1m`, `5m`, `1h`, `12h`, `1d`

Minimum: 10 seconds. Only first 10 inline commands auto-refresh.

## Comment Syntax

Use `#` for bash/python/ruby/php, `//` for js/swift/applescript.
