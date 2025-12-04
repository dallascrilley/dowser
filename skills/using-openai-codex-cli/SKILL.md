---
name: using-openai-codex-cli
short_description: >-
  Enable Claude to leverage OpenAI Codex CLI for intelligent code analysis,
  refactoring, and automated editing through non-interactive command-line
  prompting. Covers sandbox modes, model selection, reasoning effort, and
  session resumption.
description: >
  This skill enables Claude to leverage OpenAI Codex CLI for intelligent code
  analysis, refactoring, and automated editing through non-interactive
  command-line prompting. It provides integration with Codex and other LLM-based
  coding assistants, allowing delegation of code-based tasks to external smart
  models via CLI invocation.
license: MIT
when_to_use: >-
  performing code analysis, refactoring existing code, or automating editing
  tasks through the command line, especially when delegating coding tasks to AI
  models without manual intervention.
version: 1.0.0
languages: all
category: agents-and-skills
---

# Codex Skill Guide

## Running a Task
1. Ask the user (via `AskUserQuestion`) which model to run (`gpt-5` or `gpt-5-codex`) AND which reasoning effort to use (`low`, `medium`, or `high`) in a **single prompt with two questions**.
2. Select the sandbox mode required for the task; default to `--sandbox read-only` unless edits or network access are necessary.
3. Assemble the command with the appropriate options:
   - `-m, --model <MODEL>`
   - `--config model_reasoning_effort="<low|medium|high>"`
   - `--sandbox <read-only|workspace-write|danger-full-access>`
   - `--full-auto`
   - `-C, --cd <DIR>`
   - `--skip-git-repo-check`
3. Always use --skip-git-repo-check.
4. When continuing a previous session, use `codex exec --skip-git-repo-check resume --last` via stdin. When resuming don't use any configuration flags unless explicitly requested by the user e.g. if he species the model or the reasoning effort when requesting to resume a session. Resume syntax: `echo "your prompt here" | codex exec --skip-git-repo-check resume --last 2>/dev/null`. All flags have to be inserted between exec and resume.
5. **IMPORTANT**: By default, append `2>/dev/null` to all `codex exec` commands to suppress thinking tokens (stderr). Only show stderr if the user explicitly requests to see thinking tokens or if debugging is needed.
6. Run the command, capture stdout/stderr (filtered as appropriate), and summarize the outcome for the user.
7. **After Codex completes**, inform the user: "You can resume this Codex session at any time by saying 'codex resume' or asking me to continue with additional analysis or changes."

### Quick Reference
| Use case | Sandbox mode | Key flags |
| --- | --- | --- |
| Read-only review or analysis | `read-only` | `--sandbox read-only 2>/dev/null` |
| Apply local edits | `workspace-write` | `--sandbox workspace-write --full-auto 2>/dev/null` |
| Permit network or broad access | `danger-full-access` | `--sandbox danger-full-access --full-auto 2>/dev/null` |
| Resume recent session | Inherited from original | `echo "prompt" \| codex exec --skip-git-repo-check resume --last 2>/dev/null` (no flags allowed) |
| Run from another directory | Match task needs | `-C <DIR>` plus other flags `2>/dev/null` |


## Code Review Workflow
0. IMPORTANT/DO NOT SKIP: Always run the command `codex-code-review --help` and read the help message before using the script.
1. Determine what to review:
   - **Staged/unstaged changes**: Use `codex-code-review "<request>" [files...]`
   - **Committed changes**: Use `codex-code-review --diff "<range>" "<request>" [files...]`
     - Examples: `--diff "main...HEAD"` (PR changes), `--diff "HEAD~3..HEAD"` (last 3 commits)
2. The script automatically:
   - Uses `--sandbox read-only` (reviews don't modify files)
   - Includes staged and unstaged git changes (or committed with --diff)
   - Uses `gpt-5-codex` model with `medium` reasoning effort (hardcoded)
   - Suppresses thinking tokens for clean output
   - Uses `--skip-git-repo-check` flag
   - Runs in foreground (do NOT run in background - output won't be captured)
3. After completion, inform user: "You can resume this Codex session for 
   follow-up analysis using: echo 'your question' | codex exec 
   --skip-git-repo-check resume --last 2>/dev/null"
4. Optional: If user wants to resume, pipe their question directly to the resume command

**Note**: 
- The script reviews ALL changes (both staged and unstaged) by default
- For committed changes (e.g., PR reviews), use `--diff` option: `codex-code-review --diff "main...HEAD" "<request>"`
- Users can stage specific files first if they want to review only certain changes
- **CRITICAL**: Always run in foreground - background execution will not capture output properly

## Following Up
- After every `codex` command, immediately use `AskUserQuestion` to confirm next steps, collect clarifications, or decide whether to resume with `codex exec resume --last`.
- When resuming, pipe the new prompt via stdin: `echo "new prompt" | codex exec resume --last 2>/dev/null`. The resumed session automatically uses the same model, reasoning effort, and sandbox mode from the original session.
- Restate the chosen model, reasoning effort, and sandbox mode when proposing follow-up actions.

## Error Handling
- Stop and report failures whenever `codex --version` or a `codex exec` command exits non-zero; request direction before retrying.
- Before you use high-impact flags (`--full-auto`, `--sandbox danger-full-access`, `--skip-git-repo-check`) ask the user for permission using AskUserQuestion unless it was already given.
- When output includes warnings or partial results, summarize them and ask how to adjust using `AskUserQuestion`.

## Additional References
- [Codex CLI Help Menu (headless execution)](references/headless-execution-help-menu.md) - Complete help output showing all available options and flags for `codex exec` non-interactive execution
- [Codex CLI Headless Execution Mode](references/headless-execution-mode.md) - Overview of non-interactive execution for automation workflows, including CLI arguments, sandbox policies, and session resumption
- [Codex CLI Passing Inputs and Prompts](references/passing-inputs-and-prompts.md) - Guide to attaching files/images, using custom prompt templates, and passing prompts via arguments or stdin
- [Codex CLI Slash Commands and Features](references/slash-commands-and-features.md) - Summary table of interactive slash commands (e.g., `/model`, `/approvals`, `/review`) available during Codex sessions
- [Codex CLI Subcommands and Entry Points](references/subcommands-entry-points.md) - CLI architecture documentation covering subcommand dispatch, authentication, execution modes, and utility commands
