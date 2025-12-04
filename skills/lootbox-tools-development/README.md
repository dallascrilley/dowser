# Lootbox Tools Development Skill

A comprehensive skill for developing, integrating, and validating lootbox tools.

## About This Skill

This skill provides complete guidance for working with lootbox—a TypeScript-based tool integration system that provides LLMs with unified access to:

- **Native TypeScript tools** - Custom functions in `.lootbox/tools/`
- **MCP Servers** - External tools via Model Context Protocol
- **CLI Wrappers** - Command-line applications exposed as typed functions

## What's Included

### Main Guidance (SKILL.md)

- Understanding lootbox architecture
- Native tool development workflow (step-by-step)
- MCP server integration workflow
- Tool validation & testing
- Essential implementation patterns
- Anti-patterns to avoid
- Quick reference checklist

### Templates (assets/templates/)

Boilerplate code for common tool types:

- `basic_kv_tool.ts` - Key-value store template
- `api_wrapper_tool.ts` - External API wrapper template

Copy and customize for your use case.

### MCP Configurations (assets/mcp-configs/)

Example configurations for integrating MCP servers:

- `perplexity.mcp.json` - Perplexity search integration
- `custom.mcp.json` - Custom MCP server template

### Reference Guides (references/)

Detailed documentation:

- **tool_interface_spec.md** - Complete interface specification with examples
- **common_patterns.md** - 9 battle-tested implementation patterns
- **troubleshooting.md** - Solutions for common issues

### Scripts (scripts/)

Utilities for tool development:

- `validate_tool.sh` - Validate tool file syntax and structure

## Quick Start

### Create a Native Tool (5 minutes)

1. **Start with SKILL.md** → "Native Tool Development Workflow"
2. **Use template** → Copy `assets/templates/basic_kv_tool.ts`
3. **Place in project** → Save to `.lootbox/tools/<toolname>.ts`
4. **Customize** → Edit functions and interfaces for your use case
5. **Validate** → Run `./scripts/validate_tool.sh .lootbox/tools/<toolname>.ts`

### Integrate MCP Server (3 minutes)

1. **Start with SKILL.md** → "MCP Server Integration Workflow"
2. **Use template** → Copy `assets/mcp-configs/perplexity.mcp.json`
3. **Create config** → Save to `.mcp.json` or `lootbox.config.json`
4. **Set credentials** → Add API keys to `env` section
5. **Verify** → Run `lootbox server` to connect

## Key Concepts

**Namespace** - A group of related functions (one per `.ts` file)

**Tool Function** - Async function with typed args and results
```typescript
export interface MyFunctionArgs { /* input */ }
export interface MyFunctionResult { /* output */ }
export async function myFunction(args: MyFunctionArgs): Promise<MyFunctionResult> { }
```

**RPC** - Remote Procedure Call via WebSocket

**MCP Server** - External application exposing tools via Model Context Protocol

## File Structure

```
lootbox-tools-development/
├── SKILL.md                    # Main skill content
├── README.md                   # This file
├── assets/
│   ├── templates/             # Tool templates
│   │   ├── basic_kv_tool.ts
│   │   └── api_wrapper_tool.ts
│   └── mcp-configs/           # MCP configuration examples
│       ├── perplexity.mcp.json
│       └── custom.mcp.json
├── references/                # Detailed documentation
│   ├── tool_interface_spec.md
│   ├── common_patterns.md
│   └── troubleshooting.md
└── scripts/                   # Development utilities
    └── validate_tool.sh
```

## Common Tasks

### Task: Validate My Tool File
```bash
./scripts/validate_tool.sh .lootbox/tools/myapp.ts
```

### Task: Check Available Tools
```bash
lootbox tools
```

### Task: Get Type Definitions
```bash
lootbox tools types mytool
```

### Task: Test a Function
```bash
lootbox exec 'await tools.mytool.myfunction({param: "value"})'
```

### Task: Understand Error Messages
→ See `references/troubleshooting.md`

### Task: See Implementation Examples
→ See `references/common_patterns.md` (9 patterns provided)

### Task: Learn Interface Specification
→ See `references/tool_interface_spec.md` (complete reference)

## Learning Path

**Complete Beginner:**
1. Read SKILL.md sections:
   - "Understanding Lootbox Architecture"
   - "Native Tool Development Workflow"
2. Copy `assets/templates/basic_kv_tool.ts`
3. Follow step-by-step in the workflow
4. Test with `lootbox exec`

**Want to Use External APIs:**
1. Copy `assets/templates/api_wrapper_tool.ts`
2. Follow "MCP Server Integration Workflow" in SKILL.md
3. Reference `references/common_patterns.md` Pattern 4

**Experienced, Need Patterns:**
1. Skip to `references/common_patterns.md`
2. Pick relevant pattern (9 patterns available)
3. Adapt to your needs

**Debugging Issues:**
1. Run: `lootbox tools types <namespace>`
2. Check error messages against `references/troubleshooting.md`
3. Reference "Tool Validation & Testing" in SKILL.md

## Bundled Resources Quick Reference

| Resource | Purpose | When to Use |
|----------|---------|-------------|
| `basic_kv_tool.ts` | Key-value store template | Creating persistent storage tool |
| `api_wrapper_tool.ts` | API wrapper template | Wrapping external REST API |
| `perplexity.mcp.json` | MCP config example | Integrating Perplexity search |
| `custom.mcp.json` | Custom MCP template | Creating custom MCP server config |
| `tool_interface_spec.md` | Complete type reference | Understanding interface design |
| `common_patterns.md` | 9 implementation patterns | Building your tool |
| `troubleshooting.md` | Error solutions | Debugging issues |
| `validate_tool.sh` | Syntax validator | Checking tool files |

## Key Principles

1. **Type Safety** - All tools have strong TypeScript types
2. **Async First** - All functions are async/Promise-based
3. **Single Namespace** - One file = one group of related functions
4. **Auto-Discovery** - No registration needed, tools discovered by convention
5. **Progressive Disclosure** - Learn incrementally as needed

## Related Documentation

- **Official Lootbox Guide** - See the comprehensive guide this skill is based on
- **MCP Specification** - Model Context Protocol standard
- **TypeScript Handbook** - For async/await and interface syntax

## Examples in This Skill

- Complete KV store tool (basic_kv_tool.ts)
- Complete API wrapper tool (api_wrapper_tool.ts)
- User management example (tool_interface_spec.md)
- Batch processing pattern (common_patterns.md)
- Caching with TTL pattern (common_patterns.md)
- And 4 more complete patterns

## Getting Help

**For quick lookup:** `references/troubleshooting.md`

**For implementation examples:** `references/common_patterns.md`

**For interface design:** `references/tool_interface_spec.md`

**For step-by-step:** SKILL.md workflows

## Success Criteria

Your tool is ready when:

- [ ] Tool file in `.lootbox/tools/<name>.ts`
- [ ] `lootbox tools` shows your namespace
- [ ] `lootbox tools types <name>` shows your functions
- [ ] `lootbox exec 'await tools.<name>.<func>({...})'` works
- [ ] Tool validates with: `./scripts/validate_tool.sh`
- [ ] Error handling works as expected
- [ ] Documentation complete (comments in code)

---

**Version:** 1.0
**Based on:** lootbox Tool Integration Guide
**Last Updated:** 2025-11-27
