---
name: searching-code-structures
short_description: >-
  Use ast-grep CLI for syntax-aware code searching, pattern matching,
  refactoring, and custom linting rules. Handles complex structural searches
  beyond text matching (e.g., find async functions without error handling,
  replace callback patterns).
description: >-
  Use ast-grep CLI tool for syntax-aware code searching, pattern matching,
  refactoring, and creating custom linting rules. Invoke when users request to
  "find code patterns", "search for functions that...", "refactor all X to Y",
  "replace code structures", ask about AST structure, or explicitly mention
  ast-grep. Handles complex structural searches beyond simple text matching
  (e.g., "find all async functions without error handling", "replace callback
  patterns with promises").
when_to_use: >
  Use when requesting syntax-aware code searching, finding code patterns,
  searching for functions/structures, refactoring (replace all X to Y),

  understanding AST structure, or creating custom linting rules. Handles complex
  structural searches beyond text matching using ast-grep CLI.
version: 1.0.0
category: coding
---

# Searching Code Structures with ast-grep

Execute syntax-aware code searches, refactoring, and linting using ast-grep's AST-based pattern matching.

## When to Use This Skill

Invoke this skill when the user wants to:

1. **Search for code patterns**: "Find all functions that...", "Show me where X is used", "Search for async calls"
2. **Refactor/rewrite code**: "Replace all X with Y", "Migrate from API A to API B", "Update deprecated patterns"
3. **Understand code structure**: "What's the AST for this?", "How would I match...?", "Debug this pattern"
4. **Create linting rules**: "Set up a rule to prevent...", "Create custom linter for..."

**Key indicators**: Requests involving code structure, patterns, AST matching, syntax-aware operations, or explicit ast-grep mentions.

## Core Workflow

### 1. Understand the Request

**Ask yourself:**
- What code structure are they looking for? (function calls, class methods, patterns)
- What language? (JavaScript, Python, TypeScript, etc.)
- Search only, or search + replace?
- Single-shot CLI command or project-wide linting rule?

**Common request types:**

| User Says | They Want | Approach |
|-----------|-----------|----------|
| "Find all console.log" | Quick search | Use `sg run -p` |
| "Replace console with logger" | Refactor | Use `sg run -p -r -U` |
| "Set up rule for no-console" | Linting rule | Create YAML rule + `sg scan` |
| "Why doesn't this pattern match?" | Debug | Use `--debug-query` |

### 2. Choose the Right ast-grep Command

**Decision tree:**

```
Is this a one-time operation?
├─ YES → Use `sg run` (formerly `sg` alone)
│   ├─ Search only? → sg run -p 'pattern' [paths]
│   ├─ Replace code? → sg run -p 'old' -r 'new' -U [paths]
│   └─ Preview first? → Add --dry-run before -U
│
└─ NO → Set up project scanning
    ├─ Single rule file? → sg scan -r rule.yml
    ├─ Project with multiple rules? → sg scan (needs sgconfig.yml)
    └─ Test rules? → sg test
```

**Quick command reference:**

```bash
# Search for a pattern
sg run -p 'console.log($$$)' src/

# Search with language specified
sg run -p 'func($$$)' -l python src/

# Replace (preview first)
sg run -p 'console.log($$$ARGS)' -r 'logger.info($$$ARGS)' --dry-run src/

# Replace (apply changes)
sg run -p 'console.log($$$ARGS)' -r 'logger.info($$$ARGS)' -U src/

# Scan with project rules
sg scan

# Scan with single rule file
sg scan -r rules/no-console.yml

# Debug a pattern
sg run -p 'pattern' -l javascript --debug-query=ast
```

### 3. Write Effective Patterns

**Pattern syntax quick reference:**

| Pattern | Matches | Example |
|---------|---------|---------|
| `$VAR` | Single node | `func($ARG)` matches `func(x)` |
| `$$$VARS` | Zero or more nodes | `func($$$)` matches `func()` or `func(a, b)` |
| `$$OP` | Unnamed node (operators) | `a $$OP b` matches `a + b` |

**Common patterns:**

```yaml
# Function calls with any arguments
pattern: functionName($$$ARGS)

# Async functions
pattern: async function $NAME($$$) { $$$ }

# React hooks
pattern: useState($INITIAL)

# Method calls on object
pattern: $OBJ.$METHOD($$$)

# Import statements
pattern: import $MODULE from '$PATH'
```

**Pattern development process:**

1. **Start simple**: Begin with the most basic pattern
2. **Test early**: Use `--debug-query` to see AST structure
3. **Iterate**: Add constraints or relational rules if needed
4. **Verify**: Test against example code

### 4. Apply Rules (Atomic, Relational, Composite)

When simple patterns aren't enough, use rule objects in YAML.

**Rule categories:**

```yaml
# ATOMIC: Match node properties
rule:
  pattern: console.log($ARG)      # Code structure
  # OR
  kind: call_expression           # AST node type
  # OR
  regex: '^test.*'                # Text content

# RELATIONAL: Match by position/context
rule:
  pattern: $CALL()
  inside:                         # Must be inside...
    kind: function_declaration
    stopBy: end                   # Search all the way up

# COMPOSITE: Combine rules with logic
rule:
  all:                            # Must match ALL
    - pattern: var $X = $Y
    - inside: { kind: function }
  # OR
  any: [...]                      # Match ANY
  # OR
  not: { pattern: ... }           # Must NOT match
```

**Pro tip**: Always add `stopBy: end` to relational rules (`inside`, `has`) to search thoroughly.

See [./rule-patterns.md](./rule-patterns.md) for detailed examples and common patterns.

### 5. Handle Common Scenarios

#### Scenario A: Quick Search

```bash
# User: "Find all places where we call fetchData"
sg run -p 'fetchData($$$)' src/

# User: "Find all async functions"
sg run -p 'async function $NAME($$$) { $$$ }' -l javascript src/
```

#### Scenario B: Refactoring

```bash
# User: "Replace all var with const"
sg run -p 'var $X = $Y' -r 'const $X = $Y' -U src/

# User: "Migrate from old API to new API"
# Step 1: Preview
sg run -p 'oldAPI.call($$$ARGS)' -r 'newAPI.execute($$$ARGS)' --dry-run src/
# Step 2: Apply
sg run -p 'oldAPI.call($$$ARGS)' -r 'newAPI.execute($$$ARGS)' -U src/
```

#### Scenario C: Create Linting Rule

```yaml
# User: "Set up a rule to prevent console.log in production"
# Create rules/no-console.yml
id: no-console
language: JavaScript
rule:
  pattern: console.$METHOD($$$ARGS)
severity: warning
message: Avoid console.$METHOD in production
note: Use a proper logger instead
fix: logger.info($$$ARGS)
```

Then run: `sg scan`

#### Scenario D: Debug Pattern

```bash
# User: "Why doesn't my pattern match?"

# Step 1: See how ast-grep parses your pattern
sg run -p 'your pattern' -l javascript --debug-query=ast

# Step 2: See the AST of your target code
# Create a test file, then:
sg run -p '.' test-file.js --debug-query=ast

# Step 3: Adjust pattern based on AST structure
```

### 6. Test and Validate

**Before applying changes:**

1. **Preview first**: Use `--dry-run` with `sg run`
2. **Test on sample**: Create a test file with known cases
3. **Check AST**: Use `--debug-query` to verify pattern parsing
4. **Validate results**: Review matched code before applying `-U`

**For rule files:**

```bash
# Create test cases
sg new test no-console-test

# Run tests
sg test

# Update snapshots if needed
sg test -U
```

## Advanced Topics

### Using Constraints

Narrow matches by adding constraints on meta-variables:

```yaml
rule:
  pattern: console.log($ARG)
constraints:
  ARG:
    kind: string  # Only match if $ARG is a string literal
```

### Transform Meta-Variables

Manipulate captured variables before using in fix:

```yaml
transform:
  UPPER:
    convert:
      source: $VAR
      toCase: SCREAMING_SNAKE_CASE
fix: logger.log($UPPER)
```

### Utility Rules (DRY Principle)

Define reusable rule logic:

```yaml
# utils/is-react-component.yml
id: is-react-component
language: TypeScript
rule:
  any:
    - kind: function_declaration
      has: { kind: jsx_element }
    - kind: arrow_function
      has: { kind: jsx_element }

# Then use in other rules:
rule:
  pattern: console.log($$$)
  inside:
    matches: is-react-component
```

## Reference Materials

- **[./cli-reference.md](./cli-reference.md)** - Complete CLI command reference
- **[./rule-patterns.md](./rule-patterns.md)** - Common patterns and examples
- **[./troubleshooting.md](./troubleshooting.md)** - Debugging and common issues
- **[./advanced-techniques.md](./advanced-techniques.md)** - Transforms, testing, CI/CD

## Quick Tips

1. **Start with the playground**: Use https://ast-grep.github.io/playground.html to test patterns interactively
2. **Use `--debug-query`**: When patterns don't match, inspect the AST
3. **Always preview**: Use `--dry-run` before applying changes with `-U`
4. **Add `stopBy: end`**: For relational rules to search thoroughly
5. **Keep patterns simple**: Start basic, add complexity only when needed
6. **Test with examples**: Create test cases before running on the whole codebase

## Common Pitfalls to Avoid

❌ **Using `sg` alone** - The bare `sg` command is deprecated, use `sg run` instead
❌ **Forgetting language** - Specify `-l` when using `--debug-query` or working with stdin
❌ **Skipping preview** - Always use `--dry-run` before `-U` for refactoring
❌ **Complex first patterns** - Start simple, add constraints/relations only when needed
❌ **Missing `stopBy: end`** - Relational rules without this might miss matches

## Example: Complete Workflow

**User request**: "Replace all console.log with our logger, but only in production code (not tests)"

**Step 1: Understand**
- Pattern: `console.log($$$ARGS)`
- Rewrite: `logger.info($$$ARGS)`
- Filter: Exclude test files

**Step 2: Preview**
```bash
sg run -p 'console.log($$$ARGS)' \
       -r 'logger.info($$$ARGS)' \
       --globs '!**/*.test.js' \
       --dry-run \
       src/
```

**Step 3: Apply**
```bash
sg run -p 'console.log($$$ARGS)' \
       -r 'logger.info($$$ARGS)' \
       --globs '!**/*.test.js' \
       -U \
       src/
```

**Step 4: Validate**
```bash
# Check git diff
git diff --stat

# Verify changes look correct
git diff src/
```

---

**Remember**: ast-grep operates on the Abstract Syntax Tree, not raw text. This makes it more powerful than grep/sed for structural code changes, but requires understanding the code's structure.
