# Claude Code Action Workflows Skill

Comprehensive skill for creating and editing GitHub Actions workflows that integrate Claude Code Action.

## What This Skill Does

- **Validates Authentication**: Checks for `CLAUDE_CODE_OAUTH_TOKEN` secret and provides CLI commands to set it
- **Generates Workflows**: Provides templates for interactive assistants, automated reviews, CI auto-fix, and issue triage
- **Configures Permissions**: Ensures proper GitHub permissions and tool allowlists
- **Troubleshoots Issues**: Identifies and fixes common configuration problems

## When to Use

Use this skill when:
- Creating `.github/workflows/*.yml` files for Claude Code Action
- Setting up @claude interactive assistants
- Configuring automated PR reviews or CI auto-fix
- Validating or fixing CLAUDE_CODE_OAUTH_TOKEN secret
- Troubleshooting workflow authentication or permissions
- Configuring tool permissions and MCP servers

## Quick Start

### 1. Check Authentication

```bash
# Run the secret checker script
~/.claude/skills/claude-action-workflows/scripts/check_claude_secret.sh
```

### 2. Create a Workflow

Choose from example templates in `examples/`:
- `claude-assistant.yml` - Interactive @claude assistant
- `pr-auto-review.yml` - Automated PR review
- `ci-auto-fix.yml` - CI failure auto-remediation

### 3. Customize Configuration

- Set tool permissions via `--allowedTools`
- Configure model and turn limits
- Add path filters for targeted runs

## Key Features

### Secret Validation

Automatically checks and helps set:
- `CLAUDE_CODE_OAUTH_TOKEN` (recommended, uses Claude Pro/Max subscription)
- `ANTHROPIC_API_KEY` (alternative, separate billing)

### Workflow Patterns

**Interactive Mode:** Responds to @claude mentions
**Automation Mode:** Runs on events (PRs, issues, workflow failures)
**Path-Specific:** Only triggers on critical file changes
**Multi-Stage:** Progressive review (Haiku → Sonnet → Opus)

### Security Best Practices

- Least-privilege tool permissions
- OAuth token authentication (short-lived)
- No wildcard Bash access
- Loop prevention for CI auto-fix

## Structure

```
claude-action-workflows/
├── SKILL.md                    # Main skill instructions
├── TEST_SCENARIOS.md           # Test cases and token efficiency metrics
├── scripts/
│   └── check_claude_secret.sh  # Secret validation script
├── references/
│   ├── permissions-guide.md    # Complete permissions reference
│   ├── tool-allowlist-patterns.md  # Tool permission patterns
│   └── troubleshooting.md      # Common issues and solutions
└── examples/
    ├── claude-assistant.yml    # Interactive assistant template
    ├── pr-auto-review.yml      # Automated PR review template
    └── ci-auto-fix.yml         # CI auto-fix template
```

## Token Efficiency

**Without Skill:** ~3000+ tokens, 15-30 minutes
**With Skill:** ~1200 tokens, 5-10 minutes
**Savings:** ~60% tokens, ~67% time

## References

- **Technical Reference:** `/docs/reference/TECHNICAL-REFERENCE.md` in claude-code-action repo
- **Cheat Sheet:** `ULTIMATE-CLAUDE-CODE-ACTION-CHEAT-SHEET.md` in claude-code-action repo
- **Authentication:** `~/.config/ai-rules/COMMON_ENV.md` for token values

## Common Issues

| Issue                         | Solution                                    |
| ----------------------------- | ------------------------------------------- |
| Secret not set                | Run `check_claude_secret.sh`                |
| OIDC authentication error     | Add `id-token: write` permission            |
| Tool not allowed              | Add to `--allowedTools` list                |
| Claude doesn't respond        | Check trigger condition and user access     |
| CI logs inaccessible          | Add `actions: read` permission              |

## Testing

See `TEST_SCENARIOS.md` for:
- 5 documented test scenarios
- Token efficiency measurements
- Known issues with sources

## License

Part of Personal AI Infrastructure (PAI). For use with claude.ai/code.
