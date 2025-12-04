# Common Rule Patterns and Examples

A curated collection of proven ast-grep patterns for common tasks.

## Pattern Fundamentals

### Meta-Variable Types

| Syntax | Matches | Example | Usage |
|--------|---------|---------|-------|
| `$VAR` | Single named node | `func($ARG)` → `func(x)` | One argument, variable, etc. |
| `$$$VARS` | Zero or more nodes | `func($$$)` → `func()` or `func(a,b)` | Variable number of items |
| `$$OP` | Single unnamed node | `a $$OP b` → `a + b` | Operators, punctuation |
| `$_VAR` | Non-capturing | `$_($ARG)` matches any function call | Performance optimization |

### Meta-Variable Naming

**Valid names:**
- `$VAR`, `$VARIABLE`, `$MY_VAR` ✅
- `$_`, `$_IGNORE` ✅ (non-capturing)

**Invalid names:**
- `$var` (must be uppercase) ❌
- `$my-var` (no hyphens) ❌
- `$123` (no numbers only) ❌

### Reusing Meta-Variables

When you use the same meta-variable twice, it must match the same content:

```yaml
# Matches: x == x, foo == foo
# Doesn't match: x == y
pattern: $A == $A
```

## Language-Specific Patterns

### JavaScript/TypeScript

#### Function Calls
```yaml
# Any function call with any arguments
pattern: functionName($$$ARGS)

# Specific function, exactly one argument
pattern: functionName($ARG)

# Method call on object
pattern: $OBJ.$METHOD($$$)

# Chained calls
pattern: $OBJ.$METHOD1().$METHOD2($$$)
```

#### Functions & Arrow Functions
```yaml
# Function declaration
pattern: function $NAME($$$PARAMS) { $$$BODY }

# Arrow function
pattern: ($$$PARAMS) => $EXPR

# Async function
pattern: async function $NAME($$$) { $$$ }

# Async arrow function
pattern: async ($$$PARAMS) => { $$$BODY }
```

#### React Patterns
```yaml
# useState hook
pattern: useState($INITIAL)

# useEffect with dependencies
pattern: useEffect($CALLBACK, [$$$DEPS])

# Component with props
pattern: function $COMP($PROPS) { $$$ }

# JSX element with props
pattern: <$TAG $$$PROPS>$$$CHILDREN</$TAG>
```

#### Import/Export
```yaml
# Named import
pattern: import { $$$NAMES } from '$PATH'

# Default import
pattern: import $NAME from '$PATH'

# Import all
pattern: import * as $NAME from '$PATH'

# Dynamic import
pattern: import('$PATH')

# Export default
pattern: export default $EXPR
```

#### Async/Await
```yaml
# Await expression
pattern: await $EXPR

# Promise then
pattern: $PROMISE.then($CALLBACK)

# Promise chain
pattern: $PROMISE.then($$$).catch($ERROR)

# Async function with await
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
```

### Python

#### Function Definitions
```yaml
# Function def
pattern: |
  def $NAME($$$PARAMS):
      $$$BODY

# Async function
pattern: |
  async def $NAME($$$PARAMS):
      $$$BODY

# Method with decorator
rule:
  pattern: |
    def $NAME(self, $$$PARAMS):
        $$$BODY
  inside:
    kind: class_definition
```

#### Class Patterns
```yaml
# Class definition
pattern: |
  class $NAME($$$BASES):
      $$$BODY

# Class method
pattern: |
  @classmethod
  def $NAME(cls, $$$PARAMS):
      $$$BODY

# Static method
pattern: |
  @staticmethod
  def $NAME($$$PARAMS):
      $$$BODY
```

#### Common Calls
```yaml
# Print statements
pattern: print($$$ARGS)

# String formatting
pattern: f"$$$"

# List comprehension (tricky, use kind)
rule:
  kind: list_comprehension
```

### Go

#### Function Patterns
```yaml
# Function declaration
pattern: |
  func $NAME($$$PARAMS) $$$RETURNS {
      $$$BODY
  }

# Method
pattern: |
  func ($RECV $TYPE) $NAME($$$PARAMS) $$$RETURNS {
      $$$BODY
  }

# Defer statement
pattern: defer $CALL()
```

#### Error Handling
```yaml
# Error check
pattern: |
  if err != nil {
      $$$
  }

# Error return
pattern: return $$$, err
```

### Rust

#### Function & Macros
```yaml
# Function
pattern: |
  fn $NAME($$$PARAMS) -> $RETURN {
      $$$BODY
  }

# Macro call
pattern: $MACRO!($$$)

# println! specifically
pattern: println!($$$)
```

#### Pattern Matching
```yaml
# Match expression
pattern: |
  match $EXPR {
      $$$ARMS
  }

# If let
pattern: if let $PATTERN = $EXPR { $$$ }
```

## Common Tasks

### Finding Security Issues

#### Unsafe Eval/Exec
```yaml
id: no-eval
language: JavaScript
rule:
  any:
    - pattern: eval($CODE)
    - pattern: Function($$$)
    - pattern: setTimeout($CODE, $$$)  # when CODE is string
severity: error
message: Avoid eval() and similar unsafe functions
```

#### SQL Injection Risk
```yaml
id: no-sql-concat
language: JavaScript
rule:
  pattern: db.query($SQL + $VAR)
severity: error
message: Use parameterized queries to prevent SQL injection
```

### Code Quality

#### No Console in Production
```yaml
id: no-console
language: JavaScript
rule:
  pattern: console.$METHOD($$$)
  not:
    inside:
      any:
        - kind: function_declaration
          has:
            regex: '^test'
        - kind: arrow_function
          inside:
            pattern: describe($$$)
severity: warning
message: Remove console.$METHOD from production code
fix: ''  # Delete the statement
```

#### Prefer Const
```yaml
id: prefer-const
language: JavaScript
rule:
  pattern: let $VAR = $VALUE
  # Would need additional logic to check if never reassigned
message: Use const for variables that are never reassigned
fix: const $VAR = $VALUE
```

### Refactoring Patterns

#### API Migration
```yaml
id: migrate-api
language: JavaScript
rule:
  pattern: oldAPI.call($METHOD, $$$ARGS)
fix: newAPI.$METHOD($$$ARGS)
message: Migrate to new API
```

#### Modernize Promises
```yaml
id: promise-to-async
language: JavaScript
rule:
  pattern: |
    $PROMISE.then($SUCCESS).catch($ERROR)
note: |
  Consider using async/await:
  try {
    const result = await $PROMISE;
    $SUCCESS(result);
  } catch (e) {
    $ERROR(e);
  }
```

## Advanced Rule Patterns

### Using Constraints

Filter meta-variables by AST node type or other properties:

```yaml
# Only match string literals
id: no-string-console
language: JavaScript
rule:
  pattern: console.log($ARG)
constraints:
  ARG:
    kind: string
```

```yaml
# Match only specific identifiers
rule:
  pattern: $FUNC($$$)
constraints:
  FUNC:
    regex: '^(test|describe|it)$'
```

### Relational Rules

#### Inside Context
```yaml
# Find console.log inside React components
rule:
  pattern: console.log($$$)
  inside:
    any:
      - kind: function_declaration
        has: { kind: jsx_element }
      - kind: arrow_function
        has: { kind: jsx_element }
    stopBy: end
```

#### Has Descendant
```yaml
# Find functions that contain await without try/catch
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
  not:
    has:
      kind: try_statement
      stopBy: end
```

#### Precedes/Follows
```yaml
# Find variables used before declaration
rule:
  pattern: $VAR
  precedes:
    pattern: let $VAR = $$$
```

### Composite Rules

#### All (AND)
```yaml
# Find var declarations inside loops
rule:
  all:
    - pattern: var $NAME = $VALUE
    - inside:
        kind: for_statement
message: Use let instead of var in loops
fix: let $NAME = $VALUE
```

#### Any (OR)
```yaml
# Find any console method
rule:
  any:
    - pattern: console.log($$$)
    - pattern: console.error($$$)
    - pattern: console.warn($$$)
    - pattern: console.debug($$$)
```

#### Not (Negation)
```yaml
# Find async functions without await
rule:
  kind: function_declaration
  has:
    kind: async
  not:
    has:
      pattern: await $EXPR
      stopBy: end
```

## Utility Rules

Create reusable rule components:

```yaml
# utils/is-test-file.yml
id: is-test-file
language: JavaScript
rule:
  any:
    - kind: function_declaration
      has:
        regex: '^(test|it|describe)$'
    - kind: call_expression
      has:
        regex: '^(test|it|describe)$'
```

```yaml
# rules/no-console-in-src.yml
id: no-console-in-src
language: JavaScript
rule:
  pattern: console.$METHOD($$$)
  not:
    inside:
      matches: is-test-file
files: ['src/**/*.js']
```

## Pattern Debugging Tips

### Tip 1: Start Simple

Don't write complex patterns immediately. Build incrementally:

```yaml
# Step 1: Match the outer structure
pattern: console.log($$$)

# Step 2: Add constraints
pattern: console.log($ARG)
constraints:
  ARG: { kind: string }

# Step 3: Add context
rule:
  pattern: console.log($ARG)
  inside: { kind: function_declaration }
  constraints:
    ARG: { kind: string }
```

### Tip 2: Use --debug-query

See how ast-grep parses your pattern:

```bash
sg run -p 'your pattern' -l javascript --debug-query=ast
```

### Tip 3: Inspect Target Code AST

Understand the structure you're trying to match:

```bash
# Put your target code in test.js, then:
sg run -p '.' test.js --debug-query=ast
```

### Tip 4: Test with Examples

Create a test file with known matches and non-matches:

```javascript
// test-examples.js
console.log('should match');
logger.log('should NOT match');
console.log(variable);  // should/shouldn't match depending on rule
```

Then test:
```bash
sg run -p 'your pattern' test-examples.js
```

## Pattern Anti-Patterns

### ❌ Don't: Overly Specific Patterns

```yaml
# Too specific, brittle
pattern: |
  function mySpecificFunction(param1, param2) {
      console.log('exactly this');
  }
```

### ✅ Do: Use Meta-Variables

```yaml
# Flexible, captures variations
pattern: console.log($$$)
```

### ❌ Don't: Forget stopBy

```yaml
# Might miss matches in deeply nested code
rule:
  pattern: $X
  inside: { kind: function_declaration }
```

### ✅ Do: Add stopBy: end

```yaml
# Searches thoroughly
rule:
  pattern: $X
  inside:
    kind: function_declaration
    stopBy: end
```

### ❌ Don't: Rely Only on Regex

```yaml
# Matches text, not structure
rule:
  regex: 'function.*console.log'
```

### ✅ Do: Use Structural Patterns

```yaml
# Matches AST structure
rule:
  kind: function_declaration
  has:
    pattern: console.log($$$)
    stopBy: end
```

## Quick Reference: When to Use What

| Goal | Use |
|------|-----|
| Match exact code shape | `pattern` |
| Match by AST node type | `kind` |
| Match text content | `regex` |
| Filter by meta-variable type | `constraints` |
| Match within context | `inside` with `stopBy: end` |
| Match containing element | `has` with `stopBy: end` |
| Combine multiple conditions | `all`, `any`, `not` |
| Reuse logic | Utility rules + `matches` |
| Transform variables | `transform` |
| Auto-fix | `fix` |
