---
name: Developing CLI Tools
description: >-
  Build command-line tools that are human-friendly, scriptable, and composable
  following modern best practices
when_to_use: >-
  When creating CLIs, adding subcommands, designing argument interfaces,
  implementing help systems, handling stdin/stdout/stderr, building interactive
  prompts, creating progress indicators, or when CLI output breaks in
  pipes/scripts. When users report confusing arguments, missing help, broken
  piping, or color codes in logs.
version: 1.0.0
languages:
  - typescript
  - javascript
  - python
  - go
dependencies: 'Commander.js, Click, Cobra, Inquirer, Chalk, Ora (language-specific)'
category: coding
---

# Developing CLI Tools

## Overview

**Build CLIs for humans first, make them scriptable second.** Great CLIs adapt intelligently between interactive terminal use and automated scripting by detecting TTY, providing comprehensive help, routing output correctly, and respecting user preferences.

**Core principles:**
- Design defaults for terminal users, expose opt-in flags for automation
- TTY detection, stdout/stderr routing, and error handling are **non-negotiable fundamentals**, not optional polish
- Time pressure is never justification for skipping these basics - they prevent bugs, not cause them

## When to Use

Use this skill when:
- Creating new CLI tools or adding commands/subcommands
- Implementing argument parsing and validation
- Designing help text and documentation
- Building interactive prompts or confirmations
- Handling long-running operations with progress indicators
- Debugging why CLI output breaks in pipes or scripts
- Users report confusing command syntax or missing help
- Scripts fail due to interactive prompts or color codes

## Quick Reference

### Essential CLI Patterns

| Pattern | Implementation | Why |
|---------|---------------|-----|
| **Help everywhere** | `-h`, `--help`, `mycli help cmd` | Users try all variations |
| **Output routing** | Results � stdout, messages � stderr | Enables piping and redirection |
| **TTY detection** | Disable colors/spinners when piped | Prevents escape codes in logs |
| **Flags over args** | `--from X --to Y` not `X Y` | Clear intent, autocomplete-friendly |
| **Exit codes** | 0 = success, non-zero = failure | Scripts need to detect errors |
| **Version info** | `--version`, `-V`, `version` subcommand | Debugging starts with versions |
| **Machine modes** | `--json`, `--plain` for stable output | Scripts need parseable data |
| **Prompts** | Only when stdin is TTY + flag alternative | Must remain scriptable |

### Configuration Precedence (highest to lowest)

1. Command-line flags (`--flag=value`)
2. Environment variables (`MYAPP_SETTING=value`)
3. Project config file (`.myapprc` in project dir)
4. User config file (`~/.config/myapp/config`)
5. System config file (`/etc/myapp/config`)

### Error Message Structure

```
Error: <ERROR_CODE> - <Title>

<Human-readable description>

Fix with: <exact command to run>

More info: <URL to docs>
```

## Core Patterns

### Complete CLI Example (TypeScript/Commander.js)

```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';

const program = new Command()
  .name('myapp')
  .version('1.0.0')
  .command('deploy')
  .option('-e, --environment <env>', 'target', 'production')
  .option('--force', 'skip prompts')
  .option('--json', 'machine output')
  .action(async (opts) => {
    const isTTY = process.stdout.isTTY;

    // Prompt only if TTY and not forced
    if (isTTY && !opts.force) {
      const { confirm } = await import('inquirer').then(m =>
        m.default.prompt([{ type: 'confirm', name: 'confirm',
                           message: `Deploy to ${opts.environment}?` }]));
      if (!confirm) process.exit(1);
    }

    const spinner = isTTY ? ora('Deploying...').start() : null;

    try {
      const result = await deploy(opts.environment);
      if (spinner) spinner.succeed();

      // Data to stdout, messages to stderr
      opts.json
        ? console.log(JSON.stringify(result))
        : console.error(`Deployed: ${result.url}`);
    } catch (err) {
      if (spinner) spinner.fail();
      console.error(`Error: DEPLOY_FAILED - ${err.message}`);
      console.error(`Fix: myapp logs -e ${opts.environment}`);
      process.exit(1);
    }
  });

program.parse();
```

### TTY-Aware Output Helper

```typescript
// Disable colors based on env/flags/TTY
const useColor = !process.env.NO_COLOR &&
                 process.env.TERM !== 'dumb' &&
                 process.stdout.isTTY;

export const output = {
  data: (obj: any) => console.log(JSON.stringify(obj)),  // stdout
  info: (msg: string) => console.error(useColor ? chalk.blue(msg) : msg),
  error: (msg: string) => console.error(useColor ? chalk.red(msg) : msg)
};
```

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| **Messages to stdout** | Breaks piping/redirection | All messages → stderr, data → stdout |
| **Required prompts** | Hangs in CI/scripts | Prompt only if `stdin.isTTY`, provide flag alternative |
| **Colors when piped** | Escape codes in logs | Check `stdout.isTTY` and `NO_COLOR` env |
| **Multiple positional args** | Confusing order | Use explicit flags: `--from X --to Y` |
| **Missing help/examples** | Users can't learn | Add `-h`, `--help`, usage examples |
| **No `--json` mode** | Scripts can't parse output | Provide stable machine-readable format |
| **Hardcoded paths** | Breaks cross-platform | Respect `XDG_*`, `TMPDIR` env vars |

## Red Flags - STOP

If you're tempted to skip fundamentals, you're rationalizing:

- "TTY detection is **nice-to-have**" → **WRONG**. It prevents escape codes in logs (production bugs).
- "Perfect is the enemy of good" → **WRONG**. These aren't perfection, they're basic correctness.
- "Fix it after the demo/deadline" → **WRONG**. Bugs ship, technical debt compounds, users suffer.
- "Add `--silent` flag for scripts" → **WRONG**. CLIs should work by default when piped.
- "Just move to stderr, skip TTY detection" → **WRONG**. Colors still break without TTY check.

**Reality:** The 30 minutes to do it right prevents hours of debugging and emergency fixes later.

## Testing

Verify both TTY and piped contexts:
```bash
mycli deploy           # Interactive (TTY)
mycli deploy | cat     # Piped (no colors/spinners)
mycli deploy > out.txt # Redirected (data only on stdout)
```

## File Storage

Follow XDG spec: `~/.config/myapp` (config), `~/.local/share/myapp` (data), `~/.cache/myapp` (cache). Respect `$XDG_*` and `$TMPDIR` env vars.

## Resources

- AGENTS.md - AI agent workflows for CLI development
- resources/cli-dev-guidelines/developing-cli-tools.md - Comprehensive patterns
- resources/12-factor-cli-apps/12-factor-cli-apps.md - 12-factor methodology
- resources/summaries/wisdom.md - Distilled best practices
