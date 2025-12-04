Purpose and Scope
Headless Execution Mode enables non-interactive, programmatic execution of Codex sessions. This mode is designed for automation workflows, CI/CD pipelines, and scripting scenarios where a full terminal UI is not available or desired. The headless mode (codex exec) processes a single user prompt, executes all required actions automatically (subject to approval policies), and exits upon completion.

For information about the interactive Terminal User Interface, see Terminal User Interface (TUI). For details on CLI entry points and subcommands, see CLI Entry Points and Subcommands.

Command-Line Interface
Entry Point
The codex exec subcommand is the primary entry point for headless execution. It is implemented in 
codex-rs/exec/src/lib.rs
 and dispatched from 
codex-rs/cli/src/main.rs
349-354

# Basic usage
codex exec "Your prompt here"

# Read prompt from stdin
echo "Fix the build" | codex exec

# Explicit stdin mode
codex exec -

# Resume a previous session
codex exec resume <SESSION_ID> "Follow-up prompt"
codex exec resume --last "Continue from most recent"
Key CLI Arguments
The CLI structure is defined in 
codex-rs/exec/src/cli.rs
7-82

Flag	Description	Default
--json	Output events as JSONL instead of human-readable text	false
--model, -m	Override model selection	From config
--sandbox, -s	Set sandbox policy (read-only, workspace-write, danger-full-access)	From config
--full-auto	Enable automatic execution with workspace-write sandbox	false
--cd, -C	Set working directory	Current directory
--output-last-message, -o	Write final agent message to file	None
--output-schema	JSON schema for structured final response	None
--include-plan-tool	Enable experimental plan tracking	false
--skip-git-repo-check	Allow execution outside git repositories	false
--color	Color output control (always, never, auto)	auto