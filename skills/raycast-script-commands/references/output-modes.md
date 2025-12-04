# Output Modes Reference

## Mode Comparison

| Mode | Shows | Best For |
|------|-------|----------|
| `fullOutput` | All output in terminal view | Multi-line output, logs, verbose commands |
| `compact` | Last line in toast | Quick confirmations, short results |
| `silent` | Last line in HUD after close | Background actions, notifications |
| `inline` | First line in command list | Dashboards, live status, metrics |

## ANSI Color Support

Works in `fullOutput` and `inline` modes. Colors adapt to light/dark theme.

### Foreground Colors

| Color | Code | Example |
|-------|------|---------|
| Black | 30 | `\033[30mtext\033[0m` |
| Red | 31 | `\033[31mtext\033[0m` |
| Green | 32 | `\033[32mtext\033[0m` |
| Yellow | 33 | `\033[33mtext\033[0m` |
| Blue | 34 | `\033[34mtext\033[0m` |
| Magenta | 35 | `\033[35mtext\033[0m` |
| Cyan | 36 | `\033[36mtext\033[0m` |
| White | 97 | `\033[97mtext\033[0m` |

### Background Colors

Add 10 to foreground code: 40-47, 107

### Text Styles

| Style | Code |
|-------|------|
| Reset | 0 |
| Underline | 4 |
| Crossed out | 9 |

### Language Examples

```bash
# Bash
echo -e '\033[31mRed text\033[0m'

# Node.js
console.log('\x1b[31mRed text\x1b[0m')

# Python
print('\033[31mRed text\033[0m')
```

## Inline Mode Requirements

- Must specify `@raycast.refreshTime` (e.g., `10s`, `1m`, `1h`)
- Only first line of output displayed
- Maximum 10 commands auto-refresh
- Minimum refresh interval: 10 seconds

## Long-Running Tasks

`compact`, `silent`, `inline` don't support streaming output.

For commands like `zip`, use quiet flags (`zip -q`) or switch to `fullOutput`.
