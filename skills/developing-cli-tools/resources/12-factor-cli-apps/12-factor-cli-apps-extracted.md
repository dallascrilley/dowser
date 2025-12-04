# Skill / Process: Building 12-Factor CLI Applications

Enable creation of CLI tools that follow proven UX patterns for discoverability, composability, and user experience.

## Section 1: Best Practice Rules

### 1.1 Technical Rules

- Support all help variations (`mycli`, `mycli --help`, `mycli help`, `mycli -h`, `mycli subcommand --help`, `mycli subcommand -h`). This ensures users can discover functionality regardless of which help pattern they try.
- Reserve `-h` and `--help` exclusively for help output, never for other flags. This prevents conflicts when users expect standard help behavior.
- Use flags instead of positional arguments when accepting 2+ different types of inputs. This eliminates ambiguity about which argument means what.
- Support `--` as a flag terminator to stop parsing and pass remaining arguments to subprocesses. This allows forwarding flags with conflicting names to child processes.
- Support version through `version`, `--version`, and `-V` commands (and `-v` if no verbose flag exists). This prevents users from trying multiple commands to discover version information.
- Send version string as User-Agent header in API requests. This enables server-side debugging and usage analytics.
- Write errors, warnings, and progress messages to stderr; write only structured output data to stdout. This enables proper shell redirection without mixing data and messaging.
- Include error code, title, description, fix instructions, and URL in every error message. This transforms errors from roadblocks into actionable guidance.
- Support `DEBUG` environment variable for component-grouped verbose logging. This provides detailed diagnostics without cluttering normal output.
- Check if stdout/stderr is a TTY before using colors, spinners, or progress bars. This prevents ANSI codes from corrupting redirected output files.
- Respect `TERM=dumb`, `NO_COLOR`, `--no-color`, and `MYAPP_NOCOLOR` environment variables to disable colors. This honors user preferences and accessibility needs.
- Prompt for input when stdin is a TTY, but always allow flag-based overrides for automation. This provides interactive UX while maintaining scriptability.
- Never output table borders or decorative characters in tabular output. This enables piping to `wc`, `grep`, and other text-processing tools.
- Ensure each table row represents exactly one data entry (one line per record). This makes row-based operations like counting and filtering trivial.
- Show only essential columns by default, with `--columns` flag to add more. This prevents overwhelming users while preserving access to detailed data.
- Truncate table rows that exceed screen width unless `--no-truncate` is set. This maintains readability on narrow terminals.
- Support `--no-headers` to hide column headers, `--filter` for column-specific filtering, and `--sort` for multi-column sorting. This enables advanced data manipulation without external tools.
- Provide CSV and JSON output formats in addition to human-readable tables. This enables programmatic consumption and integration with tools like `jq` and `awk`.
- Target 100-500ms startup time for the CLI binary itself (excluding network/CPU-bound operations). This creates a responsive feel that encourages frequent use.
- Show progress indicators (spinners or progress bars) for any operation taking longer than 500ms. This prevents users from thinking the CLI has frozen.
- Use colons (`:`) to separate subcommands from topics (e.g., `heroku domains:add`), not spaces. This allows topic-level commands to accept arguments without parser ambiguity.
- Display subcommand list or help when no arguments are provided, never execute default behavior. This helps users discover available commands.
- Follow XDG-spec for config (`~/.config/myapp`), data (`~/.local/share/myapp`), and cache file locations, with macOS-specific cache path (`~/Library/Caches/myapp`). This respects platform conventions and user environment overrides.

### 1.2 Conceptual / Philosophical Rules

- Default to "help users discover functionality" over "assume users know what to do" when designing command structure. This reduces support burden and increases adoption.
- Prefer "flags over args" when argument types differ, even if it requires more typing. This eliminates confusion about argument order and meaning.
- Default to "make errors actionable" over "just report what went wrong" when designing error messages. This transforms failures into learning opportunities.
- Prefer "stdout for data, stderr for messaging" over mixing concerns in a single stream. This enables proper shell composition and redirection.
- Default to "detect and adapt to environment" over "assume interactive terminal" when rendering output. This ensures CLIs work in scripts, CI/CD, and automation contexts.
- Prefer "prompt when interactive, allow flags for automation" over requiring one or the other exclusively. This optimizes for both human and machine users.
- Default to "make output parseable by default" over "optimize only for human readability" when designing table output. This enables shell composition and tool chaining.
- Prefer "show progress for perceived speed" over "silent waiting" for long operations. This creates better UX even when actual execution time is unchanged.
- Default to "start fast, load lazily" over "load everything upfront" when designing CLI architecture. This keeps startup time low even as the CLI grows.
- Prefer "colon-separated topics" over "space-separated subcommands" when building multi-level command hierarchies. This preserves the ability to accept arguments at topic level.

## Section 2: Canonical Patterns & Workflows

### Pattern: Implementing Help System

**Goal**  
Create a discoverable help system that works across all common invocation patterns and provides both in-CLI and web documentation.

**When to Use**  
- Building a new CLI from scratch
- Adding help functionality to existing CLI
- Refactoring help system to improve discoverability

**Required Inputs**  
- CLI command structure (commands, subcommands, flags, arguments)
- Command descriptions and usage examples
- Web documentation URL (if applicable)

**Workflow Steps**  
1. Implement help handlers for all patterns: `mycli`, `mycli --help`, `mycli help`, `mycli -h`, `mycli subcommand --help`, `mycli subcommand -h`
2. Reserve `-h` and `--help` flags exclusively for help (never repurpose for other functionality)
3. Include command description, argument descriptions, flag descriptions, and usage examples in help output
4. Create or update README/web documentation with same information (enables Google indexing)
5. Implement shell completion support to provide interactive help discovery
6. Add help text validation/linting to ensure all commands have descriptions

**Expected Outputs**  
- **Primary Output:** Help system that responds to all standard help patterns
- **Secondary Outputs:**
  - Updated web documentation (README or docs site)
  - Shell completion configuration
  - Help text validation rules

### Pattern: Designing Command Interface

**Goal**  
Create a command interface that balances clarity, discoverability, and composability with shell tools.

**When to Use**  
- Designing new commands or subcommands
- Refactoring existing commands with confusing argument patterns
- Adding new functionality that needs user input

**Required Inputs**  
- Command purpose and required inputs
- List of inputs (their types and whether they're optional)
- Whether command will be used in automation/scripts

**Workflow Steps**  
1. Determine if command is single-command or multi-command CLI (use subcommands if CLI does multiple distinct tasks)
2. For multi-command CLIs, use colons (`:`) to separate topics from subcommands (e.g., `mycli topic:action`)
3. Convert positional arguments to flags when there are 2+ different types of arguments
4. Allow variable-length arguments only when all arguments are the same type (e.g., `rm file1 file2 file3`)
5. If command forwards to subprocess, support `--` flag terminator to stop parsing
6. When no arguments provided, show subcommand list or help (never execute default behavior)
7. Add prompts for required inputs when stdin is TTY, but allow flag overrides for automation

**Expected Outputs**  
- **Primary Output:** Command interface with clear flag-based API
- **Secondary Outputs:**
  - Help text showing flag usage
  - Examples demonstrating common usage patterns

### Pattern: Implementing Error Handling

**Goal**  
Create error messages that transform failures into actionable guidance with full diagnostic information available when needed.

**When to Use**  
- Implementing error handling for new commands
- Improving existing error messages that are unhelpful
- Adding debugging support for production issues

**Required Inputs**  
- Error conditions that can occur in the CLI
- Context about what operation was being performed
- Potential fixes or workarounds for each error type

**Workflow Steps**  
1. Write all errors and warnings to stderr (never stdout) to preserve redirection behavior
2. Structure each error message with: error code, title, description, fix instructions, and URL for more info
3. Implement `DEBUG` environment variable support using component-grouped logging (e.g., `DEBUG=myapp:api,myapp:auth`)
4. Add full traceback output for unhandled exceptions (accessible via `--debug` flag or `DEBUG` env var)
5. Include helpful diagnostic information in version command output (OS, Node version, etc.)
6. Ensure error logs have timestamps, truncate periodically, and strip ANSI codes
7. Send version string as User-Agent in API requests to enable server-side debugging

**Expected Outputs**  
- **Primary Output:** Error handling system with structured, actionable messages
- **Secondary Outputs:**
  - Debug logging infrastructure
  - Error log rotation/truncation mechanism
  - Version command with diagnostic info

### Pattern: Creating Table Output

**Goal**  
Generate tabular output that is both human-readable and machine-parseable, enabling shell composition.

**When to Use**  
- Displaying lists of resources (apps, files, records)
- Showing structured data with multiple attributes
- Creating output that users might want to filter, sort, or count

**Required Inputs**  
- Data to display (list of records with attributes)
- Which columns are essential vs optional
- Whether output will be consumed by scripts

**Workflow Steps**  
1. Design table with one row per data entry (one line per record, no borders)
2. Show only essential columns by default, implement `--columns` flag for additional columns
3. Truncate rows that exceed screen width unless `--no-truncate` is set
4. Show column headers by default, allow `--no-headers` to hide them
5. Implement `--filter` for column-specific filtering and `--sort` for multi-column sorting
6. Add `--output json` and `--output csv` format options
7. Ensure table output goes to stdout (not stderr) so it can be redirected to files

**Expected Outputs**  
- **Primary Output:** Table rendering system with parsing-friendly format
- **Secondary Outputs:**
  - JSON and CSV output formatters
  - Column filtering and sorting logic

## Section 3: Failure Modes & Self-Check Checklist

### 3.1 Common Failure Modes

- Tends to use positional arguments when there are 2+ different types of inputs. This causes confusion about argument order and makes the CLI harder to use correctly.
- Often writes errors or progress messages to stdout instead of stderr. This corrupts redirected output files and breaks shell composition.
- Frequently assumes interactive terminal and always uses colors/spinners without TTY detection. This outputs ANSI codes to files when output is redirected.
- Sometimes creates error messages that only describe what went wrong without fix instructions. This leaves users stuck without clear next steps.
- Can forget to support `--` flag terminator when forwarding arguments to subprocesses. This prevents passing flags with conflicting names to child processes.
- Often uses space-separated subcommands instead of colons, then tries to accept arguments at topic level. This creates parser ambiguity that breaks the command.
- Tends to execute default behavior when no arguments are provided instead of showing help. This prevents users from discovering available commands.
- Frequently outputs table borders or decorative characters in tabular data. This makes it impossible to pipe output to `wc`, `grep`, or other text-processing tools.

### 3.2 Hard Constraints / Never-Do Rules

- Never repurpose `-h` or `--help` flags for anything other than displaying help. This prevents conflicts with user expectations and standard CLI conventions.
- Never write errors, warnings, or progress messages to stdout. This ensures proper shell redirection behavior and prevents corrupting output files.
- Never output ANSI color codes, spinners, or progress bars when stdout/stderr is not a TTY. This prevents corrupting redirected output files.
- Always check if stdin is a TTY before prompting for input, and always allow flag-based overrides. This ensures the CLI remains scriptable and automatable.
- Always write table output with one row per entry and no borders. This enables shell composition and text-processing tool integration.
- Always show help or subcommand list when no arguments are provided, never execute default behavior. This helps users discover functionality.

### 3.3 Pre-Response Self-Check Checklist

- [ ] Have I implemented help for all standard patterns (`mycli`, `mycli --help`, `mycli help`, `mycli -h`, `mycli subcommand --help`, `mycli subcommand -h`)?
- [ ] Have I reserved `-h` and `--help` exclusively for help output?
- [ ] Have I used flags instead of positional arguments when there are 2+ different types of inputs?
- [ ] Have I written all errors, warnings, and progress messages to stderr (not stdout)?
- [ ] Have I checked if stdout/stderr is a TTY before using colors, spinners, or progress bars?
- [ ] Have I respected `TERM=dumb`, `NO_COLOR`, `--no-color`, and app-specific color disable flags?
- [ ] Have I structured error messages with code, title, description, fix instructions, and URL?
- [ ] Have I ensured table output has one row per entry with no borders?
- [ ] Have I implemented `--` flag terminator support if the command forwards to subprocesses?
- [ ] Have I used colons (`:`) to separate topics from subcommands (not spaces)?
- [ ] Have I ensured the CLI shows help or subcommand list when no arguments are provided?
- [ ] Have I followed XDG-spec for config/data/cache file locations (with macOS-specific cache path)?
- [ ] Have I targeted 100-500ms startup time and added progress indicators for longer operations?
- [ ] Have I provided JSON/CSV output formats in addition to human-readable tables?
- [ ] Would this CLI work correctly when piped, redirected, or used in automation scripts?

