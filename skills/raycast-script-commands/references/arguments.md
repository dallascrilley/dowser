# Arguments Reference

## Syntax

Arguments use JSON in metadata comments:

```bash
# @raycast.argument1 { "type": "text", "placeholder": "Query" }
```

Maximum 3 arguments per script.

## Required Fields

| Field | Description |
|-------|-------------|
| `type` | `"text"`, `"password"`, or `"dropdown"` |
| `placeholder` | Placeholder text in input field |

## Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `optional` | Allow running without this input | `false` |
| `percentEncoded` | URL-encode value before passing | `false` |
| `data` | Dropdown options (required for dropdown type) | - |

## Argument Types

### text
Standard text input.

```bash
# @raycast.argument1 { "type": "text", "placeholder": "Enter name" }
```

### password
Secure entry, displays asterisks.

```bash
# @raycast.argument1 { "type": "password", "placeholder": "API Key" }
```

### dropdown
Select from predefined options.

```bash
# @raycast.argument1 { "type": "dropdown", "placeholder": "Environment", "data": [{"title": "Production", "value": "prod"}, {"title": "Staging", "value": "stage"}] }
```

## Accessing Arguments

| Language | Access Pattern |
|----------|----------------|
| Bash | `$1`, `$2`, `$3` |
| Python | `sys.argv[1]`, `sys.argv[2]`, `sys.argv[3]` |
| Node.js | `process.argv[2]`, `process.argv[3]`, `process.argv[4]` |
| Ruby | `ARGV[0]`, `ARGV[1]`, `ARGV[2]` |
| Swift | `CommandLine.arguments[1...]` |

## Examples

### Required + Optional

```bash
# @raycast.argument1 { "type": "text", "placeholder": "Search query" }
# @raycast.argument2 { "type": "text", "placeholder": "Max results", "optional": true }
```

### URL-Encoded

```bash
# @raycast.argument1 { "type": "text", "placeholder": "Query", "percentEncoded": true }
open "https://google.com/search?q=$1"
```

### Dropdown Selection

```bash
# @raycast.argument1 { "type": "dropdown", "placeholder": "Action", "data": [{"title": "Start", "value": "start"}, {"title": "Stop", "value": "stop"}] }

if [ "$1" = "start" ]; then
  echo "Starting..."
else
  echo "Stopping..."
fi
```

## Pro Tip

Type alias + space to auto-focus the first input field.
