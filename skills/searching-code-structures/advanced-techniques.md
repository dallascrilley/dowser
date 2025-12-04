# Advanced ast-grep Techniques

Advanced features for complex transformations and workflows.

## Transform: Manipulating Meta-Variables

The `transform` field lets you manipulate captured meta-variables before using them in `fix`.

### String Transformations

#### Substring Extraction

```yaml
rule:
  pattern: import $MODULE from '$PATH'
transform:
  # Extract last part of path
  FILENAME:
    substring:
      source: $PATH
      startChar: 0
      endChar: -3  # Remove .js extension
fix: import $MODULE from './$FILENAME'
```

#### Regex Replace

```yaml
rule:
  pattern: debug.$CAMEL_VAR($$$)
transform:
  # Extract part using named capture
  REST:
    replace:
      source: $CAMEL_VAR
      replace: 'user(?<NAME>.*)'
      by: '$NAME'
fix: logger.info({ user: '$REST' }, $$$)
```

#### Case Conversion

```yaml
rule:
  pattern: const $CAMEL = $VALUE
transform:
  # Convert to snake_case
  SNAKE:
    convert:
      source: $CAMEL
      toCase: snake_case
fix: const $SNAKE = $VALUE
```

**Supported cases:**
- `lower`: lowercase
- `upper`: UPPERCASE
- `snake_case`: snake_case
- `SCREAMING_SNAKE_CASE`: SCREAMING_SNAKE_CASE
- `camelCase`: camelCase
- `PascalCase`: PascalCase

### Conditional Transforms

Create variables that depend on content:

```yaml
# Add trailing comma only if args exist
rule:
  pattern: func($$$ARGS)
  not:
    pattern: func(...,)
transform:
  # Create comma if args is not empty
  MAYBE_COMMA:
    replace:
      source: $$$ARGS
      replace: '^.+'  # Matches one or more characters
      by: ','
fix: func($$$ARGS$MAYBE_COMMA)
```

### Chaining Transforms

```yaml
transform:
  # Step 1: Extract
  EXTRACTED:
    substring:
      source: $VAR
      startChar: 4
  # Step 2: Convert case
  FINAL:
    convert:
      source: $EXTRACTED
      toCase: SCREAMING_SNAKE_CASE
fix: const $FINAL = $VALUE
```

### Transform String Syntax (Concise)

```yaml
# Object syntax
transform:
  RESULT:
    substring:
      source: $VAR
      endChar: 1

# Equivalent string syntax
transform:
  RESULT: substring($VAR, endChar=1)
```

## Rewriters: Multi-Step Transformations

For complex transformations, use `rewriters` to chain multiple rules.

```yaml
id: complex-migration
language: JavaScript
rule:
  pattern: oldAPI.$METHOD($$$ARGS)
rewriters:
  # Step 1: Remove quotes from string args
  - id: remove-quotes
    rule:
      pattern: "'$STR'"
      inside:
        pattern: oldAPI.$METHOD($$$)
    fix: $STR

  # Step 2: Transform the call
  - id: migrate-call
    rule:
      pattern: oldAPI.$METHOD($$$ARGS)
    fix: newAPI.execute({ method: '$METHOD', args: [$$$ARGS] })
```

**Rewriters execute in order**, allowing staged transformations.

## Testing Rules

### Test File Structure

```yaml
# rule-test/no-console-test.yml
id: no-console-test
testCases:
  # Case 1: Should report error
  - id: console-in-production
    invalid: |
      function doWork() {
        console.log('debug');
      }

  # Case 2: Should not report
  - id: console-in-test
    valid: |
      describe('test', () => {
        console.log('test output');
      });

  # Case 3: Should apply fix correctly
  - id: console-with-fix
    invalid: console.log('hi');
    fixed: logger.info('hi');
```

### Running Tests

```bash
# Run all tests
sg test

# Run specific test file
sg test -f 'no-console*'

# Update snapshots
sg test -U

# Interactive snapshot updates
sg test -i

# Skip snapshot validation (just check if code is valid)
sg test --skip-snapshot-tests
```

### Test Best Practices

1. **Test positive and negative cases**
   ```yaml
   testCases:
     - id: should-match
       invalid: |
         // code that should trigger rule
     - id: should-not-match
       valid: |
         // code that should not trigger rule
   ```

2. **Test edge cases**
   ```yaml
   testCases:
     - id: empty-args
       invalid: func()
     - id: single-arg
       invalid: func(a)
     - id: multiple-args
       invalid: func(a, b, c)
   ```

3. **Verify fixes**
   ```yaml
   testCases:
     - id: fix-works
       invalid: old($ARG)
       fixed: new($ARG)
   ```

## Utility Rules: Building Blocks

Create reusable rule components.

### Local Utilities

Defined within a rule file:

```yaml
id: my-rule
language: JavaScript
rule:
  pattern: $CALL($$$)
  inside:
    matches: is-react-component
utils:
  is-react-component:
    any:
      - kind: function_declaration
        has: { kind: jsx_element, stopBy: end }
      - kind: arrow_function
        has: { kind: jsx_element, stopBy: end }
```

### Global Utilities

Defined in separate files in `utilDirs`:

```yaml
# utils/is-async-function.yml
id: is-async-function
language: JavaScript
rule:
  any:
    - pattern: async function $NAME($$$) { $$$ }
    - pattern: async ($$$) => { $$$ }
```

```yaml
# rules/my-rule.yml
id: require-error-handling
language: JavaScript
rule:
  matches: is-async-function
  not:
    has:
      kind: try_statement
      stopBy: end
message: Async functions should have error handling
```

### Recursive Utilities

Utilities can reference each other:

```yaml
# utils/is-function.yml
id: is-function
rule:
  any:
    - matches: is-arrow-function
    - matches: is-regular-function

# utils/is-arrow-function.yml
id: is-arrow-function
rule:
  kind: arrow_function

# utils/is-regular-function.yml
id: is-regular-function
rule:
  kind: function_declaration
```

## Fix Configuration (FixConfig)

Advanced fix options beyond simple string replacement.

### Template with Range Expansion

```yaml
fix:
  template: "newFunc($$$ARGS)"
  expandEnd:
    regex: ','  # Also remove trailing comma
```

### Delete Node

```yaml
# Remove the matched node entirely
fix: ''

# Or with range expansion
fix:
  template: ''
  expandEnd: { regex: ',' }
```

## Language Injection (Experimental)

Support embedded languages like CSS in JS.

```yaml
# In sgconfig.yml
languageInjections:
  - hostLanguage: js
    rule:
      pattern: styled.$TAG`$CONTENT`
    injected: css
```

Now you can write rules for CSS inside JavaScript:

```yaml
id: no-important-css
language: css
rule:
  regex: '!important'
message: Avoid !important in styles
```

This will match CSS inside styled-components:
```javascript
const Button = styled.button`
  color: red !important; /* Matches */
`;
```

## Project Configuration (sgconfig.yml)

### Basic Structure

```yaml
# Where to find rules
ruleDirs:
  - rules
  - custom-rules

# Where to find tests
testConfigs:
  - testDir: rule-test
    snapshotDir: __snapshots__
  - testDir: integration-tests

# Where to find utility rules
utilDirs:
  - utils
  - shared-utils

# Map languages to file extensions
languageGlobs:
  html: ['*.vue', '*.svelte', '*.astro']
  typescript: ['*.tsx']
  javascript: ['*.jsx']
```

### Custom Languages

```yaml
customLanguages:
  mojo:
    libraryPath: ./parsers/tree-sitter-mojo.so
    extensions: ['.mojo', '.🔥']
    expandoChar: _  # Use _ instead of $ for meta-variables
    languageSymbol: tree_sitter_mojo
```

### Multi-Platform Support

```yaml
customLanguages:
  mylang:
    # Object-style for different platforms
    libraryPath:
      aarch64-apple-darwin: ./parsers/mac-arm.so
      x86_64-unknown-linux-gnu: ./parsers/linux-x64.so
      x86_64-pc-windows-msvc: ./parsers/windows-x64.dll
    extensions: ['.mylang']
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: ast-grep Lint
on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install ast-grep
        run: |
          curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/ast-grep-x86_64-unknown-linux-gnu.zip -o sg.zip
          unzip sg.zip
          chmod +x sg
          sudo mv sg /usr/local/bin/

      - name: Run ast-grep
        run: sg scan --format github
```

### GitLab CI

```yaml
# .gitlab-ci.yml
ast-grep:
  image: alpine:latest
  before_script:
    - apk add --no-cache curl unzip
    - curl -L https://github.com/ast-grep/ast-grep/releases/latest/download/ast-grep-x86_64-unknown-linux-musl.zip -o sg.zip
    - unzip sg.zip
    - chmod +x sg
  script:
    - ./sg scan --json > report.json
  artifacts:
    reports:
      codequality: report.json
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ast-grep
        name: ast-grep
        entry: sg scan
        language: system
        pass_filenames: false
        always_run: true
```

### NPM Script

```json
{
  "scripts": {
    "lint:ast": "sg scan",
    "lint:ast:fix": "sg scan -U",
    "test:rules": "sg test"
  }
}
```

## Advanced Pattern Techniques

### Field Matching

Match nodes by their semantic role:

```yaml
# Match only the name of a function, not the whole function
rule:
  kind: function_declaration
  has:
    field: name
    pattern: $NAME
    regex: '^test'
```

### Strictness Levels

Control how strictly patterns are matched:

```yaml
rule:
  pattern:
    context: console.log($ARG)
    strictness: relaxed  # Most flexible
```

**Levels:**
- `cst`: Exact concrete syntax (strictest)
- `smart`: Skip unnamed nodes in target (default)
- `ast`: Skip all unnamed nodes
- `relaxed`: Ignore comments and trivia (most flexible)
- `signature`: Match only node kinds, ignore content

### NthChild with Formula

Match nodes by position using An+B notation:

```yaml
# Match every other item
rule:
  nthChild: 2n

# Match all but first
rule:
  nthChild:
    position: n+2

# Match last two items
rule:
  nthChild:
    position: 2
    reverse: true
```

### Range Matching

Match by source position:

```yaml
rule:
  range:
    start:
      line: 0    # 0-based line number
      column: 0  # 0-based column
    end:
      line: 0
      column: 13  # Exclusive
```

Useful for fixing specific locations from other tools.

## Performance Optimization

### 1. Use Kind Over Pattern

```yaml
# Faster
rule:
  kind: function_declaration

# Slower
rule:
  pattern: function $NAME($$$) { $$$ }
```

### 2. Limit File Scope

```yaml
files: ['src/**/*.js']
ignores:
  - '**/node_modules/**'
  - '**/dist/**'
  - '**/*.min.js'
```

### 3. Use stopBy Strategically

```yaml
# Faster (stops early)
rule:
  has:
    pattern: $X
    stopBy:
      kind: statement_block

# Slower (searches to leaf nodes)
rule:
  has:
    pattern: $X
    stopBy: end
```

### 4. Parallelize Scanning

```bash
# Use all cores (default)
sg scan --threads 0

# Limit if needed
sg scan --threads 4
```

## Debugging Complex Rules

### Step-by-Step Debugging

1. **Start with the simplest pattern**
   ```yaml
   pattern: $ANYTHING
   ```

2. **Add one constraint at a time**
   ```yaml
   kind: function_declaration
   ```

3. **Add relational rules incrementally**
   ```yaml
   has: { pattern: $X }
   ```

4. **Add composite logic last**
   ```yaml
   all: [...]
   ```

### Inspection Mode

```bash
# See what files are scanned
sg scan --inspect=summary

# See individual files and rules
sg scan --inspect=entity
```

### JSON Output for Analysis

```bash
# Pretty JSON for humans
sg scan --json=pretty > results.json

# Stream JSON for tools
sg scan --json=stream | jq '.message'

# Compact JSON
sg scan --json=compact
```

## Real-World Example: Complex Migration

Migrate from Moment.js to Day.js:

```yaml
id: migrate-moment-to-dayjs
language: JavaScript
rule:
  any:
    # moment() calls
    - pattern: moment($$$ARGS)
    # moment.format() calls
    - pattern: moment($$$).format($FMT)
    # moment operations
    - pattern: moment($$$).$METHOD($$$ARGS)

rewriters:
  # Step 1: Simple moment() -> dayjs()
  - id: simple-calls
    rule:
      pattern: moment($$$ARGS)
      not:
        pattern: moment($$$).$METHOD($$$)
    fix: dayjs($$$ARGS)

  # Step 2: Format calls
  - id: format-calls
    rule:
      pattern: moment($$$).format($FMT)
    fix: dayjs($$$).format($FMT)

  # Step 3: Methods that need adjustment
  - id: add-method
    rule:
      pattern: moment($D).add($N, '$UNIT')
    fix: dayjs($D).add($N, '$UNIT')

message: Migrate from moment.js to day.js
note: |
  Make sure day.js is installed: npm install dayjs
  Import: import dayjs from 'dayjs'
```

Apply the migration:
```bash
sg scan -r migrate-moment.yml -U src/
```
