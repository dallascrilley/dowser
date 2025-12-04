# Template Usage Guide

## Template Variable Syntax

Templates use `{{VARIABLE_NAME}}` syntax for placeholders.

**Conditional sections:**
```
{{#IF_CONDITION}}
Content shown if condition is true
{{/IF_CONDITION}}
```

**Lists:**
```
{{ITEM_LIST}}
```

## Available Templates

Located in `templates/` directory:

- `tool-skill-SKILL.md.template` - Main skill structure
- `helper-script.py.template` - Python helper script
- `helper-script.sh.template` - Bash helper script
- `config-template.yml.template` - Configuration file
- `README-scripts.md.template` - Scripts directory README
- `skill-with-agents-template.md` - Skill with agent support

## Filling Templates

### Manual Approach

1. Copy template to destination
2. Search/replace all `{{VARIABLES}}`
3. Remove conditional sections not needed
4. Fill in list sections

### Programmatic Approach

```python
def fill_template(template_path, variables):
    with open(template_path) as f:
        content = f.read()

    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", value)

    return content
```

## Template Customization

**Add tool-specific sections:**

Templates are starting points. Add sections for:
- Tool-specific features
- Unique configuration options
- Special workflows
- Domain-specific patterns

**Example:** Add "Authentication" section for API tools.

## Helper Script Template Variables

**Python Script Template:**
- `{{SCRIPT_NAME}}` - Script filename without extension
- `{{SCRIPT_DESCRIPTION}}` - One-line description
- `{{SCRIPT_PURPOSE}}` - Detailed purpose explanation
- `{{USAGE_PATTERN}}` - How to invoke
- `{{EXAMPLES}}` - Usage examples
- `{{ARGUMENT_DEFINITIONS}}` - argparse argument definitions
- `{{MAIN_LOGIC}}` - Core script logic
- `{{HELPER_FUNCTIONS}}` - Supporting functions
- `{{ADDITIONAL_IMPORTS}}` - Extra import statements

**Bash Script Template:**
- `{{SCRIPT_NAME}}` - Script filename
- `{{SCRIPT_DESCRIPTION}}` - Description
- `{{USAGE_PATTERN}}` - Usage pattern
- `{{EXAMPLES}}` - Examples
- `{{ARGUMENT_DEFINITIONS}}` - case statement for arguments
- `{{MAIN_LOGIC}}` - Core logic
- `{{DEPENDENCY_CHECKS}}` - Dependency verification

## Config Template Variables

- `{{CONFIG_NAME}}` - Configuration name
- `{{CONFIG_DESCRIPTION}}` - What this config is for
- `{{TOOL_COMMAND}}` - Command that uses this config
- `{{CONFIG_FLAG}}` - Flag to pass config (e.g., -C, --config)
- `{{CONFIG_SECTIONS}}` - Config sections with options

## SKILL.md Template Structure

**Sections (in order):**
1. YAML Frontmatter
2. Title and Overview
3. Prerequisites
4. Quick Start
5. Core Tasks
6. Command Reference
7. Configuration Files
8. Proven Patterns
9. Troubleshooting
10. Helper Scripts
11. Workflow Requirements
12. Common Workflows
13. Tips

**Template Variables:**
- `{{TOOL_NAME}}` - Name of tool
- `{{DESCRIPTION}}` - Tool description
- `{{QUICK_START_COMMANDS}}` - Basic examples
- `{{CORE_TASKS}}` - Common operations
- `{{PROVEN_PATTERNS}}` - Working examples
- `{{TROUBLESHOOTING_TABLE}}` - Quick fixes table
- `{{HELPER_SCRIPTS_LIST}}` - Scripts with descriptions
- `{{WORKFLOW_REQUIREMENTS}}` - Mandatory workflows

## Best Practices

1. **Start with templates** - Don't create from scratch
2. **Fill all variables** - Incomplete templates cause confusion
3. **Remove unused conditionals** - Clean up template
4. **Test templates** - Verify generated content works
5. **Customize for tool** - Add tool-specific sections
6. **Maintain consistency** - Use same patterns across templates

**See:** `templates/` directory for all available templates

