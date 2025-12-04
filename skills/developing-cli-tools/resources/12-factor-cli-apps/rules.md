
# CLI Best Practices Rules

## Help & Documentation
- Display help with `mycli`, `mycli --help`, `mycli -h`, and `mycli help` for all commands and subcommands.
- Reserve `-h` and `--help` flags exclusively for help display.
- Provide in-CLI help, web-based documentation, and shell completion support.
- Include command descriptions, argument descriptions, flag descriptions, and usage examples in all help text.
- Lead help text with common usage examples before flag listings.
- Display concise help by default and extensive help when explicitly requested.
- Link to web documentation from help text for detailed information.

## Arguments & Flags
- Prefer flags over arguments for clarity and future extensibility.
- Use flags for different types of arguments; reserve positional arguments for homogeneous collections only.
- Provide both short (`-x`) and long (`--example`) versions of all flags.
- Reserve one-letter flags for commonly used options only.
- Use standard flag names matching conventions (`--all`, `--debug`, `--force`, `--json`, `--help`, `--version`, etc.).
- Accept `--` to stop parsing and pass remaining arguments to subprocesses.
- Support `-` in file arguments to read from stdin or write to stdout.
- Never require sensitive data via flags; use files or stdin instead.

## Subcommands
- Use subcommands for complex CLIs; use single commands for simple utilities.
- Display subcommand list or help when no arguments are provided.
- Use colons to separate topics from subcommands (e.g., `heroku domains:add`).
- Maintain consistent naming and behavior across all subcommands.
- Avoid ambiguous or similarly-named subcommands.
- Never create catch-all subcommands that intercept unknown commands.
- Never allow arbitrary abbreviations of subcommand names.

## Output
- Send primary output to stdout; send errors, warnings, and logs to stderr.
- Use stdout for machine-readable output (JSON, CSV) and human-readable results.
- Use stderr for all messaging, progress indicators, and debug information.
- Pipe stderr from subcommands directly to the user's screen.
- Output structured data as JSON when `--json` flag is passed.
- Provide `--plain` flag for machine-parseable output without formatting.
- Display brief success messages; avoid silent success unless explicitly configured.
- Show column headers by default but allow hiding with `--no-headers`.
- Avoid table borders; output one entry per line for piping compatibility.
- Support `--columns`, `--sort`, `--filter`, and `--no-truncate` flags for table output.
- Detect TTY and disable colors/animations when piping to files or non-interactive terminals.
- Respect `NO_COLOR`, `TERM=dumb`, `--no-color`, and app-specific `MYAPP_NOCOLOR` environment variables.
- Use colors and formatting intentionally to highlight important information.
- Use spinners and progress bars for long-running operations in interactive terminals.
- Show progress indicators for operations exceeding 100ms to prevent appearing hung.

## Errors
- Return zero exit code on success; return non-zero exit codes on failure.
- Provide informative error messages containing: error code, title, description, fix instructions, and documentation URL.
- Catch expected errors and rewrite them for human understanding.
- Provide debug output and tracebacks for unexpected errors via `DEBUG` environment variable.
- Write error logs with timestamps and truncate them to prevent disk bloat.
- Strip ANSI color codes from error logs.
- Minimize signal-to-noise ratio by grouping similar errors under explanatory headers.
- Place critical error information at the end of output where eyes naturally focus.

## Interactivity
- Prompt for input only when stdin is an interactive terminal (TTY).
- Never require prompts; always allow input via flags or arguments for scripting.
- Require explicit confirmation for dangerous operations via flag or typed confirmation.
- Use checkboxes and radio buttons to present multiple options visually.
- Hide passwords while typing by disabling terminal echo.
- Respect `--no-input` flag to disable all interactive prompts.
- Allow Ctrl-C to exit immediately; add timeout to cleanup operations.

## Performance
- Aim for startup time under 500ms; target 100-500ms range.
- Print output within 100ms to show responsiveness.
- Load only the command being executed, not all commands.
- Use lazy loading to minimize overhead even with hundreds of commands.

## Version & Debugging
- Display version via `mycli version`, `mycli --version`, and `mycli -V`.
- Treat `mycli -v` as version display unless `-v,--verbose` flag exists.
- Include helpful diagnostic information beyond version number.
- Send version string in User-Agent headers for server-side debugging.

## Configuration & Environment
- Follow XDG Base Directory Specification: use `~/.config/myapp` for config, `~/.local/share/myapp` for data, `~/.cache/myapp` for cache (or platform-specific equivalents).
- Read configuration from flags, environment variables, project-level files, user-level files, and system-wide files in order of precedence.
- Use environment variables for context-dependent behavior, not stable configuration.
- Support `.env` files for project-specific environment variables.
- Check standard environment variables: `NO_COLOR`, `DEBUG`, `EDITOR`, `HTTP_PROXY`, `SHELL`, `TERM`, `TMPDIR`, `HOME`, `PAGER`, `LINES`, `COLUMNS`.
- Never read secrets from environment variables; use files, stdin, or credential services.
- Use only uppercase letters, numbers, and underscores in environment variable names.
- Avoid commandeering widely-used environment variable names.

## Code & Distribution
- Use a command-line argument parsing library for your language.
- Distribute as a single binary when possible.
- Keep code open source with clear license and contribution guidelines.
- Provide setup instructions for local development and testing.
- Add code of conduct to project.
- Make uninstallation easy and document it clearly.

## Robustness
- Validate all user input early and provide actionable error messages.
- Make programs crash-only: avoid cleanup requirements and exit immediately on failure.
- Make programs recoverable: allow resuming from where they failed.
- Support reasonable network timeouts with configurable options.
- Expect misuse: handle bad connections, multiple concurrent instances, and unfamiliar environments.

## Future-Proofing
- Keep changes additive; avoid breaking interface changes.
- Warn users before making non-additive changes and provide migration path.
- Allow changing human-readable output freely; keep `--plain` and `--json` stable for scripts.
- Never create catch-all behaviors that prevent future subcommand additions.
- Never allow arbitrary abbreviations that lock in future naming.

## Naming
- Use simple, memorable, lowercase names with dashes only if necessary.
- Keep names short but not cryptic; reserve shortest names for most common utilities.
- Prioritize ease of typing over brevity.

## Analytics
- Never collect usage or crash data without explicit opt-in consent.
- Clearly document what data is collected, why, anonymization methods, and retention period.
- Consider alternatives: instrument web docs, track downloads, or directly ask users for feedback.