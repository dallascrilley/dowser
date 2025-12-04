# Phase 4: Artifact Creation

## Goal
Generate all skill components using templates and design specifications.

## Artifact Creation Workflow

### Step 1: Create Directory Structure

```bash
mkdir -p ~/.claude/skills/[tool-name]/{references,scripts,templates}
```

### Step 2: Generate Helper Scripts

**For each helper script in design:**

1. **Choose template**
   - Python scripts: `templates/helper-script.py.template`
   - Bash scripts: `templates/helper-script.sh.template`

2. **Fill in template variables**
   - Script name, description, purpose
   - Usage pattern, examples
   - Argument definitions
   - Main logic
   - Helper functions

3. **Implement custom logic**
   - Input validation
   - Processing steps
   - Output generation
   - Error handling

4. **Add helpful features**
   - Verbose/debug mode
   - Dry-run mode
   - Color-coded output
   - Progress indicators
   - Clear error messages

5. **Make executable**
   ```bash
   chmod +x scripts/[script-name].sh
   chmod +x scripts/[script-name].py
   ```

### Step 3: Create Config Templates

**For each config template in design:**

1. **Use config template**: `templates/config-template.yml.template`

2. **Fill in variables:**
   - Config name, description
   - Tool command, config flag
   - Config sections with options

3. **Add explanatory comments**
   - What each option does
   - Default value
   - When to change it
   - Related options

4. **Include usage example**

### Step 4: Write Reference Docs

**For each reference doc in design:**

**cli-reference.md / api-reference.md:**
- Command structure
- Flags/Options (syntax, type, default, description, examples, notes)
- Exit codes
- Environment variables

**config-reference.md:**
- Configuration file format
- Configuration options (type, default, description, allowed values, example, notes)

**patterns.md:**
- Pattern name, use case, prerequisites
- Workflow (step-by-step commands)
- Expected output
- Variations
- Troubleshooting

**troubleshooting.md:**
- Issue description
- Symptoms
- Cause
- Diagnosis (diagnostic commands)
- Solution (step-by-step)
- Prevention

### Step 5: Create scripts/README.md

Document all helper scripts:
- Purpose
- Usage
- Options
- Examples
- Common workflows
- Troubleshooting

## Validation Checkpoint

After artifact creation:
- [ ] All helper scripts created and executable
- [ ] All config templates created
- [ ] All reference docs created
- [ ] scripts/README.md created
- [ ] All files follow naming conventions
- [ ] All templates are valid (no syntax errors)

## Agent-Powered Generation

**Two agents run in parallel:**

1. **Script & Automation Generator**
   - Generates ALL helper scripts sequentially
   - Creates: setup.sh, validate_*.py, generate_*.py, inspect_*.sh, test utilities
   - Model: Haiku (fast for well-defined generation)
   - Tools: read, write
   - Output: All helper scripts + scripts/README.md

2. **Configuration & Documentation Generator**
   - Generates ALL config templates and reference docs sequentially
   - Creates: Config templates (basic, advanced, scenario-specific)
   - Creates: Reference docs (CLI, config, patterns, troubleshooting)
   - Model: Haiku
   - Tools: read, write
   - Output: All templates + all reference documentation

**Speedup:** ~2.5x faster than sequential (2 min vs 5 min)

