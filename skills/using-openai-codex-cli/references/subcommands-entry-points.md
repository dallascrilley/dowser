CLI Tools and Subcommands

This document covers the command-line interface architecture and subcommand dispatch system for Codex. The CLI provides a unified entry point that routes to different execution modes including interactive TUI, headless execution, MCP server operation, and various utility commands.

For interactive TUI functionality, see Terminal User Interface (TUI). For headless automation features, see Headless Execution Mode. For MCP server implementation details, see MCP Server Implementation.

CLI Architecture Overview
The Codex CLI is built around a multitool dispatcher that routes commands to different execution engines based on subcommands. When no subcommand is provided, it defaults to the interactive TUI mode.

Process Lifecycle and Initialization
Before the main CLI logic executes, the process undergoes security hardening via pre_main_hardening(), which is invoked using the #[ctor::ctor] attribute to run before main():

The arg0_dispatch_or_else() function handles special binary name dispatching (e.g., when the binary is invoked with a platform-specific name) before proceeding to cli_main().

codex-rs/process-hardening/src/lib.rs
1-115

CLI Dispatcher Architecture

Main Dispatcher System
The CLI uses a MultitoolCli structure that implements clap's Parser trait to handle argument parsing and subcommand dispatch.

MultitoolCli Structure
The main CLI structure combines global configuration overrides with subcommand-specific options:

Component	Type	Purpose
config_overrides	CliConfigOverrides	Global -c key=value style configuration
interactive	TuiCli	Default TUI mode configuration
subcommand	Option<Subcommand>	Optional subcommand routing
When no subcommand is specified, the CLI forwards to interactive TUI mode with the global configuration overrides merged in.

Sources: 
codex-rs/cli/src/main.rs
25-48

Configuration Precedence System
The CLI implements a sophisticated configuration precedence system where subcommand-specific flags override global flags:

The prepend_config_flags() function ensures that global flags are inserted at the beginning of the override list, giving subcommand flags higher precedence.

Core Execution Subcommands
Subcommand	Alias	Purpose	Target Module
exec	e	Non-interactive execution	codex_exec
mcp	-	MCP server operations	codex_mcp_server
proto	p	Protocol stream via stdin/stdout	codex_cli::proto
resume	-	Resume previous sessions	codex_tui
Authentication Subcommands
The authentication system supports multiple login methods through the login and logout subcommands:

Subcommand	Purpose	Implementation
login	Authenticate with ChatGPT OAuth or API key	run_login_with_chatgpt(), run_login_with_api_key(), run_login_with_device_code()
login status	Check current authentication status	run_login_status()
logout	Remove stored credentials	run_logout()

Login Methods
The login command supports three authentication methods:

API Key Login (--api-key): Directly stores an OpenAI API key in ~/.codex/auth.json:

codex login --api-key sk-proj-...
Device Code Login (--experimental_use-device-code): Uses OAuth device code flow for environments without browser support. Displays a 9-digit code that users enter at /deviceauth/authorize:

Requests device code from /deviceauth/usercode
Polls /deviceauth/token every interval seconds (15 minute timeout)
Exchanges authorization code for tokens
Stores access/refresh tokens
ChatGPT OAuth Login (default): Launches a local HTTP server and opens browser for OAuth flow:

Starts server on localhost with random port
Opens browser to authentication URL with PKCE challenge
Handles callback with authorization code
Exchanges code for tokens using exchange_code_for_tokens()

Login Status
The login status subcommand displays current authentication state:

codex login status
Outputs either:

Logged in using an API key - sk-proj-***ABCDE (masked key)
Logged in using ChatGPT
Not logged in (exit code 1)

Subcommand	Alias	Purpose	Implementation
apply	a	Apply git diffs from agent	run_apply_command()
completion	-	Generate shell completions	generate() from clap_complete
debug	-	Internal debugging tools	Platform-specific sandbox testing
Hidden/Internal Subcommands
Subcommand	Purpose	Visibility
generate-ts	Generate TypeScript protocol bindings	Hidden from help
The generate-ts command is used internally during development to generate TypeScript definitions for the protocol types defined in codex-protocol. It takes an output directory and optional Prettier executable path:

codex generate-ts --out ./codex-cli/protocol --prettier ./node_modules/.bin/prettier

Subcommand Dispatch Flow
Main Dispatch Logic
The dispatch logic follows this pattern:

Each subcommand handler receives the merged configuration overrides and delegates to the appropriate execution engine.

Sources: 
codex-rs/cli/src/main.rs
166-282

Resume Command Special Handling
The resume command has special logic for merging flags and determining session restoration behavior:

The resume command supports three modes:

Session ID provided: Resume specific session directly
--last flag: Resume most recent session without picker
Default: Show session picker for user selection
Sources: 
codex-rs/cli/src/main.rs
295-361

Debug Subcommands
The debug subcommand provides platform-specific sandbox testing utilities:

Debug Command Structure


Both debug subcommands accept a --full-auto flag for convenience testing and trailing arguments for the command to execute under sandbox constraints.

Shell Completion Support
The CLI provides shell completion generation via the completion subcommand:

Supported Shells
Shell	Default	Command
Bash	✓	codex completion bash
Zsh		codex completion zsh
Fish		codex completion fish
PowerShell		codex completion powershell

The completion system uses clap's built-in completion generation with the command name standardized to "codex" regardless of the actual executable name.