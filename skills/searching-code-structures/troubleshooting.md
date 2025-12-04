# Troubleshooting ast-grep

Common issues and their solutions when working with ast-grep.

## Pattern Not Matching

### Issue: "Pattern doesn't match but it should"

**Diagnosis:**
```bash
# See how ast-grep parses your pattern
sg run -p 'your pattern' -l javascript --debug-query=ast

# See the AST of your target code
echo 'your code' | sg run -p '.' --stdin -l javascript --debug-query=ast
```

**Common causes:**

1. **Language not specified**
   ```bash
   # ❌ Wrong
   sg run -p 'pattern' --debug-query=ast

   # ✅ Correct
   sg run -p 'pattern' -l javascript --debug-query=ast
   ```

2. **Pattern too strict**
   ```yaml
   # ❌ Matches only exact formatting
   pattern: console.log( $ARG )

   # ✅ Matches any whitespace
   pattern: console.log($ARG)
   ```

3. **Wrong meta-variable type**
   ```yaml
   # ❌ $ARG matches exactly one argument
   pattern: func($ARG)

   # ✅ $$$ARGS matches zero or more
   pattern: func($$$ARGS)
   ```

4. **Relational rule without stopBy**
   ```yaml
   # ❌ Only searches immediate parent
   rule:
     pattern: await $EXPR
     inside: { kind: function_declaration }

   # ✅ Searches all the way to root
   rule:
     pattern: await $EXPR
     inside:
       kind: function_declaration
       stopBy: end
   ```

**Solutions:**

**Try relaxed strictness:**
```bash
sg run -p 'pattern' --strictness=relaxed src/
```

**Try using `kind` instead:**
```yaml
# Instead of complex pattern
pattern: function foo($$$) { $$$ }

# Use kind
rule:
  kind: function_declaration
  has:
    field: name
    pattern: foo
```

**Test with the playground:**
Visit https://ast-grep.github.io/playground.html to interactively test patterns.

## Meta-Variable Issues

### Issue: "Meta-variable $VAR not found"

**Problem:** Using a meta-variable in `fix` or `constraints` that doesn't exist in `pattern`.

```yaml
# ❌ Wrong - $MSG not captured
rule:
  pattern: console.log($ARG)
fix: logger.info($MSG)

# ✅ Correct
rule:
  pattern: console.log($ARG)
fix: logger.info($ARG)
```

**Remember:**
- Meta-variables in `fix` must be captured in `rule`
- Constraint keys don't use `$` prefix
- Meta-variables are case-sensitive

### Issue: Meta-variables matching unexpected content

**Problem:** `$VAR` matches more than you want.

```yaml
# This might match: func(a + b)
# Where $ARG captures the entire expression "a + b"
pattern: func($ARG)
```

**Solution:** Add constraints to narrow matches:
```yaml
pattern: func($ARG)
constraints:
  ARG:
    kind: identifier  # Only match simple identifiers
```

## No Rules Found

### Issue: "Error: No rules found" or rules don't run

**Diagnosis:**
```bash
# Check project structure
ls -la sgconfig.yml rules/

# List configured rules
sg scan --list
```

**Common causes:**

1. **Wrong directory**
   ```bash
   # ❌ Running from wrong location
   cd src/ && sg scan

   # ✅ Run from project root (where sgconfig.yml is)
   cd /path/to/project && sg scan
   ```

2. **Missing sgconfig.yml**
   ```bash
   # Create project structure
   sg new project
   ```

3. **Wrong path in sgconfig.yml**
   ```yaml
   # ❌ Wrong - absolute path or missing directory
   ruleDirs:
     - /absolute/path/rules

   # ✅ Correct - relative to sgconfig.yml
   ruleDirs:
     - rules
     - custom-rules
   ```

4. **Rule file has errors**
   ```yaml
   # ❌ Wrong - missing required fields
   id: my-rule
   rule:
     pattern: console.log($$$)

   # ✅ Correct - has language field
   id: my-rule
   language: JavaScript
   rule:
     pattern: console.log($$$)
   ```

## YAML Syntax Errors

### Issue: "Invalid YAML syntax"

**Common mistakes:**

1. **Tabs instead of spaces**
   ```yaml
   # ❌ Uses tabs (invisible here)
   rule:
   	pattern: func()

   # ✅ Uses spaces
   rule:
     pattern: func()
   ```

2. **Incorrect list syntax**
   ```yaml
   # ❌ Missing dash
   all:
     pattern: a
     pattern: b

   # ✅ Correct list
   all:
     - pattern: a
     - pattern: b
   ```

3. **Unquoted special characters**
   ```yaml
   # ❌ Special chars need quotes
   pattern: func($ARG)
   regex: ^test.*

   # ✅ Properly quoted
   pattern: "func($ARG)"
   regex: '^test.*'
   ```

4. **Multi-line strings**
   ```yaml
   # ✅ Method 1: Literal block
   pattern: |
     function $NAME() {
       $$$
     }

   # ✅ Method 2: Folded block
   pattern: >
     function $NAME() {
       $$$
     }

   # ✅ Method 3: Quoted
   pattern: "function $NAME() { $$$ }"
   ```

**Validation:**
```bash
# Use a YAML validator
yamllint rules/my-rule.yml

# Or try loading the rule
sg scan -r rules/my-rule.yml --dry-run
```

## Performance Issues

### Issue: "Scanning is very slow"

**Diagnosis:**
```bash
# Time the scan
time sg scan

# Check how many files are being scanned
sg scan --inspect=summary
```

**Solutions:**

1. **Add file filters**
   ```yaml
   # In rule file
   files: ['src/**/*.js']
   ignores:
     - '**/node_modules/**'
     - '**/dist/**'
     - '**/*.test.js'
   ```

2. **Use kind instead of pattern**
   ```yaml
   # ✅ Faster
   rule:
     kind: function_declaration

   # ❌ Slower
   rule:
     pattern: function $NAME($$$) { $$$ }
   ```

3. **Limit threads**
   ```bash
   # If system is overloaded
   sg scan --threads 4
   ```

4. **Check .gitignore is respected**
   ```bash
   # Make sure you're not ignoring .gitignore
   sg scan  # respects .gitignore by default

   # If you need to bypass:
   sg scan --no-ignore=vcs
   ```

## Fix/Rewrite Not Working

### Issue: "Fix is not being applied"

**Diagnosis:**
```bash
# Preview what would be fixed
sg scan --rule my-rule.yml --dry-run

# Or for sg run
sg run -p 'pattern' -r 'replacement' --dry-run src/
```

**Common causes:**

1. **Missing -U flag**
   ```bash
   # ❌ Just shows matches
   sg run -p 'old' -r 'new' src/

   # ✅ Applies changes
   sg run -p 'old' -r 'new' -U src/
   ```

2. **Rule doesn't match**
   ```bash
   # Test if rule matches first
   sg scan -r rules/my-rule.yml
   # No matches? Fix your pattern first
   ```

3. **Fix uses undefined meta-variable**
   ```yaml
   # ❌ $NEW_VAR not captured
   rule:
     pattern: old($ARG)
   fix: new($NEW_VAR)

   # ✅ Uses captured variable
   rule:
     pattern: old($ARG)
   fix: new($ARG)
   ```

## False Positives

### Issue: "Rule matches code it shouldn't"

**Solution: Add more constraints**

```yaml
# Original - too broad
rule:
  pattern: console.log($$$)

# Improved - exclude test files
rule:
  pattern: console.log($$$)
  not:
    inside:
      matches: is-test-file
files: ['src/**/*.js']
ignores: ['**/*.test.js']
```

**Solution: Use composite rules**

```yaml
# Match console.log but only in production code
rule:
  all:
    - pattern: console.log($$$)
    - inside:
        kind: function_declaration
    - not:
        inside:
          kind: call_expression
          has:
            regex: '^(describe|it|test)$'
```

## Language Not Supported

### Issue: "Language X is not supported"

**Check supported languages:**
```bash
# ast-grep supports: JavaScript, TypeScript, Python, Go, Rust,
# Java, C, C++, C#, HTML, CSS, and more

# For custom/new languages, check:
# https://ast-grep.github.io/advanced/custom-language.html
```

**For non-standard extensions:**
```yaml
# In sgconfig.yml
languageGlobs:
  html: ['*.vue', '*.svelte']
  typescript: ['*.tsx']
```

**For completely custom languages:**
```yaml
# In sgconfig.yml
customLanguages:
  mylang:
    libraryPath: ./parsers/mylang.so
    extensions: ['.mylang']
```

## Test Failures

### Issue: "Test snapshots don't match"

**Diagnosis:**
```bash
# Run tests to see failures
sg test

# See detailed diff
sg test --snapshot-dir=__snapshots__
```

**Solutions:**

1. **Update snapshots if changes are intentional**
   ```bash
   # Interactive update
   sg test -i

   # Update all
   sg test -U
   ```

2. **Fix rule if behavior is wrong**
   ```bash
   # Edit rule, then rerun
   vi rules/my-rule.yml
   sg test
   ```

3. **Add more test cases**
   ```yaml
   # In rule-test/my-rule-test.yml
   id: my-rule-test
   testCases:
     - id: should-match-this
       invalid: |
         console.log('test');
     - id: should-not-match-this
       valid: |
         logger.info('test');
   ```

## Common Error Messages

### "Pattern syntax error"

**Cause:** Invalid pattern syntax for the language.

**Solution:** Check the pattern is valid code in that language:
```bash
sg run -p 'your pattern' -l javascript --debug-query=pattern
```

### "Metavariable not found"

**Cause:** Using `$VAR` in fix/constraint that doesn't exist in pattern.

**Solution:** Ensure all variables in `fix` are captured in `rule`.

### "Ambiguous pattern"

**Cause:** Pattern could be parsed multiple ways.

**Solution:** Use `context` and `selector`:
```yaml
pattern:
  context: 'class { $FIELD }'
  selector: field_definition
```

### "Tree-sitter parse error"

**Cause:** Target code has syntax errors.

**Solution:** Fix the syntax errors in your code, or adjust the pattern to handle partial syntax.

## Getting Help

### Use the Playground

Test patterns interactively: https://ast-grep.github.io/playground.html

### Debug Flags

```bash
# See pattern AST
sg run -p 'pattern' -l js --debug-query=pattern

# See target AST
sg run -p '.' file.js --debug-query=ast

# Inspect scanning process
sg scan --inspect=summary
```

### Create Minimal Reproduction

1. Create a small test file with the code you're trying to match
2. Write the simplest pattern possible
3. Test incrementally
4. Share both files when asking for help

### Check Documentation

- CLI Reference: https://ast-grep.github.io/reference/cli.html
- Rule Guide: https://ast-grep.github.io/guide/rule-config.html
- API Reference: https://ast-grep.github.io/reference/api.html

## Quick Troubleshooting Checklist

When something doesn't work:

- [ ] Is `ast-grep` installed? (`sg --version`)
- [ ] Did you specify the language? (`-l javascript`)
- [ ] Are you in the right directory? (where `sgconfig.yml` is)
- [ ] Does the pattern parse? (`--debug-query`)
- [ ] Does the target code parse? (check for syntax errors)
- [ ] Did you use `stopBy: end` for relational rules?
- [ ] Are meta-variables properly captured?
- [ ] Did you preview changes first? (`--dry-run`)
- [ ] Are file paths/globs correct?
- [ ] Is YAML syntax valid? (no tabs, proper indentation)
