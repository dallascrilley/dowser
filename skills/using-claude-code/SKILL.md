---
name: using-claude-code
short_description: >-
  Expert knowledge for Claude Code CLI including features, commands, skills
  system, MCP servers, slash commands, and best practices. Use when creating
  custom skills, MCP integration, workflow optimization, troubleshooting CLI
  issues, or extending functionality.
description: >-
  Expert knowledge for understanding and using Claude Code CLI effectively,
  including features, commands, skills system, MCP servers, slash commands, and
  best practices. Use when user asks about Claude Code capabilities, how to
  create custom skills, MCP integration, workflow optimization, troubleshooting
  CLI issues, or extending functionality. Keywords - claude code, CLI commands,
  custom skills, MCP servers, slash commands, file operations, git integration,
  debugging, skill creation, workflow optimization.
when_to_use: >
  Use when user asks about Claude Code capabilities, features, or commands;
  creating custom skills or MCP integration; workflow

  optimization; troubleshooting CLI issues; creating slash commands or hooks;
  file operations and git integration; or extending

  functionality with tools and servers.
version: 1.0.0
category: agents-and-skills
---

# Using Claude Code - CLI Mastery

## When to Activate This Skill

Use this skill when user asks about:
- "How do I create a custom skill?"
- "What can Claude Code do?"
- "How do I use MCP servers?"
- "Show me Claude Code commands"
- "How can I optimize my workflow with Claude?"
- "Debug my skill"
- "What's the best way to integrate with APIs?"
- Questions about Claude Code features, capabilities, or usage
- Creating slash commands or hooks
- File operations and git integration
- Web tools and search capabilities
- Troubleshooting Claude Code issues

## Core Capabilities

### Understanding Claude Code Architecture
- CLI command structure and usage
- Skills system and skill creation
- MCP (Model Context Protocol) server integration
- File operations (read, edit, search, glob)
- Git integration and version control
- Web tools (fetch, search)
- Slash commands and hooks

### Creating Custom Skills
- **Skills System**: Create custom expertise domains
- **Structure**: Organize skills by domain (finance, development, content, etc.)
- **Documentation**: Clear SKILL.md with YAML frontmatter
- **Testing**: Validate skills work correctly
- **Version Control**: Track skill definitions in git
- **Sharing**: Share useful skills with team or community

### MCP Server Integration
- **What**: Model Context Protocol for external integrations
- **How**: Configure MCP servers in settings
- **Use Cases**: APIs, databases, external tools, custom protocols
- **Best Practice**: Use MCP for any external system interaction

### Workflow Optimization
- Create reusable slash commands for common tasks
- Use hooks for automated workflows
- Organize skills by frequency of use
- Leverage file operations efficiently
- Batch related operations

## Key Features Explained

### Skills System
Custom expertise domains that Claude loads when relevant to your task.

**Structure:**
```
.claude/skills/[skill-name]/
├── SKILL.md           # Required - skill definition
└── CLAUDE.md          # Optional - extended context
```

**SKILL.md Format:**
```markdown
---
name: skill-name
description: What skill does and when to use it
---

# Skill Name

## When to Activate This Skill
- Trigger phrases
- Use cases

## [Content Sections]
```

### Slash Commands
Quick command execution for common workflows.

**Location:**
- `.claude/commands/` (project-level)
- `~/.claude/commands/` (user-level)

**Format:** YAML frontmatter + bash permissions

### MCP Servers
External integrations via Model Context Protocol.

**Configuration:** `.claude/settings.json` or `~/.claude/settings.json`

**Common Uses:**
- API integrations
- Database connections
- Custom tool integrations
- External service access

### File Operations
- **Read**: View file contents
- **Edit**: Modify files in place
- **Write**: Create new files
- **Glob**: Pattern-based file finding
- **Grep**: Search file contents

### Git Integration
- Status, diff, log
- Commit with proper messages
- Branch management
- Pull request creation

## Best Practices

### Skill Creation
1. **Clear Purpose**: One skill, one domain
2. **Good Description**: Include trigger phrases and keywords
3. **Proper Structure**: YAML frontmatter + organized content
4. **Test Thoroughly**: Verify skill loads and works
5. **Version Control**: Track in git
6. **Document Clearly**: Make it easy for others (and future you) to understand

### MCP Integration
1. **Use for External Systems**: Don't hardcode API calls
2. **Configure Properly**: Test server connections
3. **Handle Errors**: Graceful fallbacks
4. **Document Dependencies**: List required MCP servers

### Workflow Optimization
1. **Create Patterns**: Identify repeated tasks
2. **Automate Common Tasks**: Slash commands and hooks
3. **Organize by Domain**: Group related skills
4. **Progressive Disclosure**: Simple interface, deep capabilities
5. **Context Awareness**: Load heavy context only when needed

### Troubleshooting
1. **Check Logs**: Review CLI output
2. **Validate Format**: YAML syntax, file structure
3. **Test Incrementally**: Build up complexity
4. **Verify Paths**: Check file locations
5. **Review Permissions**: Ensure access rights

## Common Task Patterns

### Creating a New Skill
```bash
# 1. Create directory
mkdir -p .claude/skills/my-skill

# 2. Write SKILL.md with frontmatter
# 3. Test activation
# 4. Iterate and refine
```

### Integrating External API
```bash
# 1. Set up MCP server for API
# 2. Configure in settings.json
# 3. Create skill that uses MCP server
# 4. Test and document
```

### Building Slash Command
```bash
# 1. Create command directory
mkdir -p .claude/commands/my-command

# 2. Write command.md with YAML + bash
# 3. Test execution
# 4. Document usage
```

### Optimizing Workflow
```bash
# 1. Identify repeated pattern
# 2. Choose automation type (skill/command/hook)
# 3. Implement and test
# 4. Share with team
```

## Example Use Cases

### "How do I create a custom skill?"
1. Explain skill structure and purpose
2. Show SKILL.md format with YAML frontmatter
3. Demonstrate creating directory and file
4. Guide through testing and validation
5. Provide best practices for organization

### "What's the best way to integrate with APIs?"
1. Recommend MCP server approach
2. Explain configuration in settings.json
3. Show skill creation for API interaction
4. Demonstrate error handling
5. Provide example patterns

### "How can I debug my skill?"
1. Check YAML frontmatter syntax
2. Verify file structure and paths
3. Review skill description and triggers
4. Test activation manually
5. Check for conflicts with other skills
6. Validate any referenced files exist

### "Show me how to use MCP servers"
1. Explain Model Context Protocol concept
2. Show settings.json configuration
3. List common MCP server types
4. Demonstrate integration in skills
5. Provide testing approach

## Resources

### Official Documentation
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code) - Complete CLI guide
- [MCP Specification](https://modelcontextprotocol.io) - Protocol details
- [Anthropic API Docs](https://docs.anthropic.com/) - API reference

### Skill Examples
- Check `.claude/skills/` for existing patterns
- Review `~/.claude/skills/` for user-level skills
- Explore community skills marketplace

### Getting Help
- `/help` - Built-in CLI help
- GitHub Issues - Report bugs or request features
- Community - Share and discover skills

## Quick Reference

### File Locations
- **Project Skills**: `.claude/skills/[name]/`
- **User Skills**: `~/.claude/skills/[name]/`
- **Project Commands**: `.claude/commands/[name]/`
- **User Commands**: `~/.claude/commands/[name]/`
- **Settings**: `.claude/settings.json` or `~/.claude/settings.json`

### Skill Structure
```
skill-name/
├── SKILL.md      # Required: name, description, content
└── CLAUDE.md     # Optional: extended context
```

### Command Structure
```
command-name/
└── command.md    # YAML frontmatter + bash script
```

### MCP Configuration
```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run",
      "args": ["arg1", "arg2"]
    }
  }
}
```

## Remember

- **Skills = Knowledge Domains**: Organize by topic
- **MCP = External Integration**: Don't hardcode APIs
- **Commands = Quick Actions**: Automate common tasks
- **Hooks = Event Automation**: Trigger on events
- **Documentation = Future You**: Write clear docs
- **Testing = Confidence**: Validate before sharing
- **Simplicity = Power**: Start simple, add complexity only when needed
