# CLI Reference for ast-grep

Complete command-line reference for ast-grep operations.

## Core Commands

### `sg run` - One-Time Search or Rewrite

The default command for ad-hoc searches and refactoring.

```bash
sg run [OPTIONS] --pattern <PATTERN> [PATHS]...
```

**Common options:**

| Short | Long | Description | Example |
|-------|------|-------------|---------|
| `-p` | `--pattern` | AST pattern to match | `sg run -p 'func($$$)'` |
| `-r` | `--rewrite` | Replacement pattern | `sg run -p 'old' -r 'new'` |
| `-l` | `--lang` | Language (inferred from extension if omitted) | `sg run -p 'x' -l python` |
| `-U` | `--update-all` | Apply all changes without confirmation | `sg run -p 'x' -r 'y' -U` |
| `-i` | `--interactive` | Review each change | `sg run -p 'x' -r 'y' -i` |
| `--dry-run` | | Preview changes only | `sg run ... --dry-run` |
| `--stdin` | | Process code from stdin | `cat f.js \| sg run -p 'x' --stdin` |

**Debug and inspection:**

| Flag | Purpose | Example |
|------|---------|---------|
| `--debug-query[=<format>]` | Show pattern AST | `sg run -p 'x' -l js --debug-query=ast` |
| `--strictness` | Match depth control | `sg run --strictness ast` |
| `-A` / `-B` / `-C` | Show context lines | `sg run -p 'x' -C 2` |

**Output control:**

| Flag | Purpose | Example |
|------|---------|---------|
| `--json[=<STYLE>]` | JSON output | `sg run --json=stream` |
| `--color` | Color control | `sg run --color=always` |
| `--heading` | File name heading | `sg run --heading=always` |

**File filtering:**

| Flag | Purpose | Example |
|------|---------|---------|
| `--globs` | Include/exclude patterns | `sg run --globs '!**/*.test.js'` |
| `--no-ignore` | Ignore .gitignore | `sg run --no-ignore=vcs` |
| `--follow` | Follow symlinks | `sg run --follow` |

### `sg scan` - Project-Wide Linting

Scan with configured rules from `sgconfig.yml`.

```bash
sg scan [OPTIONS] [PATHS]...
```

**Rule selection:**

| Short | Long | Description | Example |
|-------|------|-------------|---------|
| `-c` | `--config` | Config file path | `sg scan -c ./custom-sg.yml` |
| `-r` | `--rule` | Single rule file | `sg scan -r rules/no-console.yml` |
| | `--inline-rules` | Rule from command line | `sg scan --inline-rules 'id: r...'` |
| | `--filter` | Filter rules by regex | `sg scan --filter 'react-'` |

**Severity control:**

| Flag | Purpose | Example |
|------|---------|---------|
| `--error[=<RULE_ID>...]` | Set to error | `sg scan --error no-console` |
| `--warning[=<RULE_ID>...]` | Set to warning | `sg scan --warning` |
| `--info[=<RULE_ID>...]` | Set to info | `sg scan --info` |
| `--off[=<RULE_ID>...]` | Turn off rule | `sg scan --off deprecated-api` |

**Output formats:**

| Flag | Purpose | Example |
|------|---------|---------|
| `--format` | GitHub Actions format | `sg scan --format github` |
| `--json` | JSON output | `sg scan --json=pretty` |
| `--report-style` | Report style | `sg scan --report-style=short` |

**Other options:**

| Flag | Purpose |
|------|---------|
| `-U` / `--update-all` | Auto-fix all issues |
| `-i` / `--interactive` | Review fixes interactively |
| `--include-metadata` | Include rule metadata in JSON |

### `sg test` - Rule Testing

Test your ast-grep rules with test cases.

```bash
sg test [OPTIONS]
```

**Options:**

| Short | Long | Description |
|-------|------|-------------|
| `-c` | `--config` | Path to config YAML |
| `-t` | `--test-dir` | Test directory |
| | `--snapshot-dir` | Snapshot directory name |
| `-U` | `--update-all` | Update all snapshots |
| `-i` | `--interactive` | Selective snapshot updates |
| `-f` | `--filter` | Filter tests by glob pattern |
| | `--skip-snapshot-tests` | Skip output validation |
| | `--include-off` | Include `severity:off` rules |

### `sg new` - Scaffolding

Create new ast-grep projects and items.

```bash
sg new [COMMAND] [OPTIONS] [NAME]
```

**Commands:**

| Command | Purpose | Example |
|---------|---------|---------|
| `project` | Create new project | `sg new project` |
| `rule` | Create new rule | `sg new rule no-console -l javascript` |
| `test` | Create new test | `sg new test no-console-test` |
| `util` | Create utility rule | `sg new util is-react-component` |

**Options:**

| Short | Long | Description |
|-------|------|-------------|
| `-l` | `--lang` | Language for the item |
| `-y` | `--yes` | Accept all defaults |
| `-b` | `--base-dir` | Base directory for creation |

### `sg lsp` - Language Server

Start LSP for editor integration.

```bash
sg lsp [OPTIONS]
```

**Options:**

| Short | Long | Description |
|-------|------|-------------|
| `-c` | `--config` | Config file path |

### `sg completions` - Shell Completions

Generate shell completion scripts.

```bash
sg completions [SHELL]
```

**Supported shells:** bash, elvish, fish, powershell, zsh

## Common Command Patterns

### Search Operations

```bash
# Basic search
sg run -p 'pattern' src/

# Multi-language search
sg run -p 'pattern' -l python scripts/
sg run -p 'pattern' -l javascript src/

# With context
sg run -p 'pattern' -C 3 src/

# JSON output
sg run -p 'pattern' --json=stream src/

# Debug pattern
sg run -p 'pattern' -l javascript --debug-query=ast
```

### Refactoring Operations

```bash
# Preview changes
sg run -p 'old' -r 'new' --dry-run src/

# Apply all changes
sg run -p 'old' -r 'new' -U src/

# Interactive review
sg run -p 'old' -r 'new' -i src/

# With file filtering
sg run -p 'old' -r 'new' --globs '!**/*.test.js' -U src/
```

### Linting Operations

```bash
# Scan with project config
sg scan

# Scan specific paths
sg scan src/ lib/

# Single rule
sg scan -r rules/no-console.yml

# Filter rules
sg scan --filter 'react-'

# GitHub Actions output
sg scan --format github

# Auto-fix all
sg scan -U

# Severity override
sg scan --off --error no-console
```

### Testing Operations

```bash
# Run all tests
sg test

# Update snapshots
sg test -U

# Interactive update
sg test -i

# Filter tests
sg test -f 'no-console*'

# Skip snapshot checks
sg test --skip-snapshot-tests
```

## File Filtering with Globs

**Include patterns:**
```bash
sg run -p 'pattern' --globs '**/*.jsx' src/
```

**Exclude patterns:**
```bash
sg run -p 'pattern' --globs '!**/*.test.js' src/
```

**Multiple patterns:**
```bash
sg run -p 'pattern' --globs '**/*.js' --globs '!**/*.test.js' src/
```

## Debug Flags

### `--debug-query`

Shows how ast-grep parses your pattern.

```bash
sg run -p 'console.log($ARG)' -l javascript --debug-query=ast
```

**Formats:**
- `pattern` - Show the pattern tree
- `ast` - Show AST structure
- `cst` - Show concrete syntax tree
- `sexp` - Show S-expression format

### `--strictness`

Controls matching algorithm precision.

| Level | Behavior | Use Case |
|-------|----------|----------|
| `cst` | Exact concrete syntax | Match specific whitespace/formatting |
| `smart` | Skip unnamed nodes in target | Default, general use |
| `ast` | Skip all unnamed nodes | Ignore punctuation/syntax noise |
| `relaxed` | Ignore comments & trivia | Most flexible |
| `signature` | Match only node kinds | Find similar structures |

```bash
sg run -p 'pattern' --strictness=relaxed src/
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or no matches found) |
| 1 | Matches found (for `sg scan`) or errors occurred |

## Environment Variables

ast-grep respects standard environment variables:

- `NO_COLOR` - Disable colored output
- `PAGER` - Set pager for output (use `cat` to disable)

## Examples by Use Case

### Code Search
```bash
# Find all function calls
sg run -p 'functionName($$$)' src/

# Find specific React hooks
sg run -p 'useState($INITIAL)' -l typescript components/

# Find imports from specific package
sg run -p "import $M from 'lodash'" src/
```

### Code Refactoring
```bash
# Rename function across codebase
sg run -p 'oldFunc($$$ARGS)' -r 'newFunc($$$ARGS)' -U src/

# Migrate API calls
sg run -p 'http.get($URL, $OPTS)' \
       -r 'fetch($URL, { method: "GET", ...$OPTS })' \
       -U src/
```

### Project Linting
```bash
# Full project scan
sg scan

# Specific rule with auto-fix
sg scan -r rules/no-console.yml -U

# CI/CD integration
sg scan --format github --error-only
```

### Pattern Development
```bash
# See how pattern parses
sg run -p 'your pattern' -l javascript --debug-query=ast

# Test on sample file
echo 'const x = 1;' | sg run -p 'const $VAR = $VAL' --stdin -l javascript

# Compare with AST
sg run -p '.' sample.js --debug-query=ast
```
