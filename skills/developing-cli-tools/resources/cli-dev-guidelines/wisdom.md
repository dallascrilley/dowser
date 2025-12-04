# SUMMARY

Comprehensive guide to building user-friendly command-line interfaces, covering argument parsing, help text, documentation, output formatting, error handling, and best practices.

# IDEAS

• Use language-specific argument parsing libraries to handle arguments, flags, help text, and spelling suggestions consistently.

• Return zero exit code on success and non-zero on failure so scripts can determine program outcomes correctly.

• Send primary output to stdout and machine-readable data there; send all messaging and errors to stderr.

• Display extensive help when users pass `-h` or `--help` flags, including descriptions and example invocations.

• Show concise help text by default when commands require arguments but receive none instead of hanging silently.

• Provide support paths like websites or GitHub links in top-level help text for user feedback and issues.

• Lead with examples in help text since users tend to use examples over other forms of documentation primarily.

• Display most common flags and commands at the start of help text to prioritize frequently-used functionality visually.

• Use formatting like bold headings in help text to improve scannability without terminal-dependent escape characters.

• Suggest corrected commands when users make typos, but ask permission rather than executing automatically without confirmation.

• Provide both web-based and terminal-based documentation to ensure accessibility across different user contexts and preferences.

• Consider providing man pages since many users reflexively check `man mycmd` as their first learning step.

• Make terminal documentation accessible via the tool itself through help subcommands like `npm help ls`.

• Lead help text with concrete examples, telling a story that builds toward complex uses progressively.

• Prioritize human-readable output first, then machine-readable output, using TTY detection to determine output format.

• Support `--plain` flag to display plain tabular text for integration with tools like `grep` and `awk`.

• Display formatted JSON output when `--json` flag is passed for complex data structure handling and piping.

• Display output on success but keep it brief; use `-q` option to suppress non-essential output in scripts.

• Explain state changes to users so they can model system state in their heads after command execution.

• Make current system state easy to view when programs perform complex state changes not immediately visible.

• Suggest commands users should run next when commands form workflows to help them discover new functionality.

• Make actions crossing program boundaries explicit, including reading/writing files and talking to remote servers.

• Use ASCII art to increase information density and create scannable output patterns that improve over time.

• Use color intentionally to highlight important text or indicate errors, avoiding overuse that diminishes meaning.

• Disable color when stdout or stderr is not a TTY, NO_COLOR is set, TERM is dumb, or user requests it.

• Avoid animations in non-interactive terminals to prevent progress bars from turning into Christmas trees in CI logs.

• Use symbols and emoji to add structure to output and catch user attention without cluttering the interface.

• Catch errors and rewrite them for humans, treating error messages as conversations guiding users in right directions.

• Signal-to-noise ratio is crucial; group similar errors under single headers rather than printing many similar lines.

• Put most important error information at the end of output where eyes naturally look first for problems.

• Provide debug and traceback information for unexpected errors with instructions on submitting bug reports to maintainers.

• Make bug report submission effortless by providing URLs with pre-populated information from the error context.

• Prefer flags to arguments since flags are clearer about what is happening and easier to modify future.

• Have full-length versions of all flags like both `-h` and `--help` for clarity in scripts and documentation.

• Only use one-letter flags for commonly used flags, particularly at top-level, to avoid polluting short flag namespace.

• Use standard flag names when standards exist so users don't have to remember different options for each command.

• Make the default the right thing for most users since most won't find and remember the right flag.

• Prompt for user input if not provided as argument or flag, but never require prompts in non-interactive contexts.

• Confirm before dangerous operations; use different confirmation strategies based on danger level and operation scope.

• Support `-` to read from stdin or write to stdout when input or output is a file for piping.

• Allow special words like "none" for optional flag values to avoid ambiguity with blank values or arguments.

• Make arguments, flags, and subcommands order-independent where possible to reduce user confusion and frustration.

• Never read secrets from flags since flag values leak into `ps` output and potentially shell history permanently.

• Only use prompts or interactive elements if stdin is an interactive terminal to distinguish piping from scripts.

• Pass `--no-input` to disable all prompts, allowing explicit user control over interactive command behavior completely.

• Don't print passwords as users type by turning off echo in the terminal using language helpers.

• Let users escape easily from programs; make Ctrl-C always work and document escape sequences clearly.

• Be consistent across subcommands using same flag names, output formatting, and similar structures throughout.

• Use consistent names for multiple subcommand levels with either `noun verb` or `verb noun` ordering consistently.

• Avoid ambiguous or similarly-named commands like "update" and "upgrade" that confuse users about which to use.

• Validate user input everywhere since bad data will eventually arrive; check early and bail out quickly.

• Print something within 100ms to show responsiveness even if operations take longer to complete afterward.

• Show progress if something takes a long time using spinners or progress indicators to prevent appearing broken.

• Do stuff in parallel thoughtfully, using libraries for multiple progress bars to avoid confusingly interleaved output.

• Make things time out with configurable network timeouts and reasonable defaults to prevent hanging forever.

• Make programs recoverable so hitting up arrow and enter resumes from where it left off after failure.

• Make programs crash-only by avoiding cleanup after operations or deferring cleanup to next run for robustness.

• Be prepared for misuse; users will wrap programs in scripts, use bad connections, and run many instances.

• Keep changes additive where possible rather than modifying flag behavior in backwards-incompatible ways unnecessarily.

• Warn before making non-additive changes and provide ways users can modify usage today to remain future-proof.

• Changing output for humans is usually okay; encourage users to use `--plain` or `--json` in scripts.

• Don't have catch-all subcommands since they prevent adding new subcommands without risking breaking existing usages.

• Don't allow arbitrary abbreviations of subcommands since this prevents adding commands starting with those letters.

• Don't create time bombs; ensure commands run the same 20 years from now without external dependencies failing.

• Exit as soon as possible when user hits Ctrl-C, saying something immediately before starting cleanup operations.

• Skip long cleanup operations if user hits Ctrl-C again; tell them what will happen on second interrupt.

• Expect programs to start in situations where cleanup hasn't been run; design for crash-only software patterns.

• Use flags for configuration likely to vary from one invocation to next like debugging output and safe modes.

• Use flags and environment variables for stable but varying configuration like paths, color settings, and proxies.

• Use version-controlled files for stable project configuration that applies to all users like Makefile and package.json.

• Follow XDG-spec for configuration file locations to limit dotfile proliferation and support general ~/.config folder.

• Ask user consent before modifying configuration not owned by program; prefer creating new files over modifying existing.

• Apply configuration parameters in precedence order: flags, shell environment variables, project config, user config, system.

• Environment variables are for behavior varying with context in which command runs, not for stable configuration.

• Environment variable names must contain only uppercase letters, numbers, underscores for maximum portability across systems.

• Aim for single-line environment variable values since multi-line values create usability issues with `env` command.

• Avoid commandeering widely used names; check POSIX standard environment variables before naming your own variables.

• Check general-purpose environment variables like NO_COLOR, DEBUG, EDITOR, HTTP_PROXY, SHELL, TERM, TMPDIR, HOME.

• Read environment variables from `.env` where appropriate for project-specific configuration that varies between projects.

• Don't use `.env` as substitute for proper configuration files since `.env` has limitations in data types and organization.

• Don't read secrets from environment variables since they leak into logs, shell substitutions, Docker inspect, systemd.

• Make program name simple and memorable without being too generic to avoid stepping on other commands' toes.

• Use only lowercase letters and dashes sparingly in program names; avoid camelCase or uppercase letters entirely.

• Keep program names short since users type them constantly; reserve shortest commands for most common utilities.

• Make program names easy to type; avoid awkward one-handed hopscotch patterns that strain users' hands repeatedly.

• Distribute as single binary if possible; use PyInstaller or platform package installers if language doesn't compile.

• Make programs easy to uninstall by putting clear instructions at bottom of install instructions for user convenience.

• Don't phone home usage or crash data without explicit user consent; users will discover and become angry.

• Be explicit about what analytics you collect, why, anonymization methods, and retention periods for transparency.

• Ask users to opt-in to analytics rather than defaulting to opt-out to respect user privacy and expectations.

• Consider alternatives to collecting analytics like instrumenting web docs, downloads, or directly talking to users.

# INSIGHTS

• CLI design prioritizes human usability first while maintaining machine compatibility through thoughtful output stream separation.

• Help text serves as immediate documentation bridge; concise defaults with extensive optional help creates optimal discoverability.

• Error messages function as teaching tools that guide users toward solutions rather than simply reporting failure.

• Configuration precedence hierarchy respects user intent at multiple levels while maintaining sensible defaults for most users.

• Progress indication and responsiveness matter more than raw speed for perceived performance in command-line tools.

• Backwards compatibility requires intentional interface design; changes must be additive or properly deprecated with warnings.

• Security in CLI tools demands avoiding flags for secrets while supporting secure alternatives like files and stdin.

• Subcommand consistency and ordering independence reduce cognitive load and prevent frustration from arbitrary syntax rules.

• TTY detection enables intelligent output formatting that serves both human readers and automated scripts simultaneously.

• Environment variables represent contextual configuration while configuration files represent stable project-level decisions requiring versioning.

• Crash-only software design improves robustness by avoiding complex cleanup logic that can fail or hang indefinitely.

• User expectations from Unix traditions shape CLI design; deviating requires strong justification and clear documentation.

• Argument parsing libraries provide consistent flag handling, help text generation, and spelling suggestions out of box.

• Interactive prompts must gracefully degrade in non-interactive contexts; `--no-input` provides explicit user control mechanisms.

• Command naming requires balancing brevity for frequent typing against generality to avoid namespace collisions with existing tools.

# QUOTES

• "Expect the output of every program to become the input to another, as yet unknown, program." — Doug McIlroy

• "Note the obsessive use of abbreviations and avoidance of capital letters; [Unix] is a system invented by people to whom repetitive stress disorder is what black lung is to miners." — Neal Stephenson

• "The purpose of help text is to give a brief, immediate sense of what your tool is, what options are available, and how to perform the most common tasks."

• "Human-readable output is paramount. Humans come first, machines second."

• "If you change what the user typed, they won't learn the correct syntax."

• "Responsive is more important than fast. Print something to the user in <100ms."

• "If the progress bar gets stuck in one place for a long time, the user won't know if stuff is still happening or if the program's crashed."

• "Rather than suggesting the corrected syntax, you might be tempted to just run it for them, as if they'd typed it right in the first place. Sometimes this is the right thing to do, but not always."

• "Make the default the right thing for most users. Making things configurable is good, but most users are not going to find the right flag and remember to use it all the time."

• "Signal-to-noise ratio is crucial. The more irrelevant output you produce, the longer it's going to take the user to figure out what they did wrong."

• "If you can avoid needing to do any cleanup after operations, or you can defer that cleanup to the next run, your program can exit immediately on failure or interruption."

• "People are going to misuse your program. Be prepared for that."

• "In software of any kind, it's crucial that interfaces don't change without a lengthy and well-documented deprecation process."

• "Changing output for humans is usually OK. The only way to make an interface easy to use is to iterate on it."

• "Users of the command-line expect to be in control of their environment, and it is surprising when programs do things in the background without telling them."

• "Secrets should only be accepted via credential files, pipes, AF_UNIX sockets, secret management services, or another IPC mechanism."

• "Users tend to use examples over other forms of documentation, so show them first in the help page, particularly the common complex uses."

• "Don't just use a blank value—this can make it ambiguous whether arguments are flag values or arguments."

• "One of the most common reasons to consult documentation is to fix errors. If you can make errors into documentation, then this will save the user loads of time."

• "You can tell a story with a series of examples, building your way toward complex uses."

• "It's rare that printing nothing at all is the best default behavior, but it's usually best to err on the side of less."

• "If your program produces multiple errors of the same type, consider grouping them under a single explanatory header instead of printing many similar-looking lines."

• "Make it clear how to get out. (Don't do what vim does.)"

• "If you have a subcommand that's likely to be the most-used one, you might be tempted to let people omit it entirely for brevity's sake."

• "Exit as soon as possible when user hits Ctrl-C, saying something immediately before starting cleanup operations."

# HABITS

• Use language-specific argument parsing libraries for consistent flag handling and automatic help text generation.

• Return zero exit code on success and non-zero on failure as standard practice for all command-line programs.

• Check TTY status to determine whether to format output for humans or machines in all output contexts.

• Display concise help text by default when required arguments are missing instead of hanging or crashing silently.

• Lead help text with concrete examples showing common use cases before explaining flags and detailed options.

• Send all primary output to stdout and all messaging, logs, and errors exclusively to stderr consistently.

• Validate all user input early before performing any operations that might modify system state or data.

• Print something within 100ms to show responsiveness even if subsequent operations take significantly longer.

• Use progress indicators or spinners for operations taking longer than a few seconds to prevent appearing broken.

• Support both `--plain` and `--json` flags to serve both human readers and automated scripts simultaneously.

• Disable color output automatically when stdout is not a TTY or when NO_COLOR environment variable is set.

• Catch common errors and rewrite them as helpful guidance rather than dumping raw error messages to users.

• Make program names short, memorable, and easy to type since users will type them constantly throughout day.

• Use only lowercase letters and dashes in program names; avoid camelCase, uppercase, or special characters.

• Provide both web-based and terminal-based documentation for accessibility across different user contexts and preferences.

• Support `-h`, `--help`, and `help` subcommand for help access; make help work regardless of other flags.

• Ask for user confirmation before executing dangerous operations; scale confirmation difficulty to operation severity.

• Allow optional flag values using special words like "none" to avoid ambiguity with blank or missing values.

• Make arguments, flags, and subcommands order-independent where possible to reduce user confusion and syntax errors.

• Never accept secrets via command-line flags; use files, stdin, or environment variables instead for security.

• Implement `--no-input` flag to explicitly disable all interactive prompts in non-interactive contexts.

• Exit immediately on Ctrl-C interrupt; say something immediately before starting any cleanup operations afterward.

• Apply configuration parameters in strict precedence order: flags, environment, project config, user config, system.

• Follow XDG Base Directory Specification for configuration file locations to avoid cluttering user home directories.

• Use environment variables for context-dependent behavior that varies between invocations or terminal sessions.

• Read project-specific configuration from `.env` files for configuration varying between different project contexts.

• Provide clear instructions for uninstalling programs at bottom of installation instructions for user convenience.

• Distribute as single binary when possible; use platform package installers if language doesn't support compilation.

# FACTS

• Exit codes are how scripts determine whether a program succeeded or failed in Unix and Linux systems.

• The XDG Base Directory Specification was developed in 2010 by the X Desktop Group for configuration locations.

• Many popular projects like yarn, fish, wireshark, emacs, neovim, and tmux support XDG Base Directory Specification.

• TTY detection is available in most programming languages for determining if output goes to interactive terminal.

• Docker Compose was originally named `plum` before being renamed to `fig` due to poor typing ergonomics.

• The NO_COLOR environment variable standard specifies disabling color output regardless of application implementation.

• POSIX standard environment variables include HOME, PATH, SHELL, TERM, and others for system configuration.

• Multi-line environment variable values create usability issues with the `env` command in Unix-like systems.

• Secrets in environment variables leak into logs, shell substitutions, Docker inspect output, and systemd services.

• Progress bars using multiple concurrent threads require special libraries to avoid interleaved and confusing output.

• The `less` command with options `less -FIRX` provides optimal paging behavior for terminal output.

• Crash-only software design eliminates need for cleanup logic by deferring cleanup to next run if needed.

• Signal handling for Ctrl-C (INT signal) requires immediate response and optional cleanup with timeouts.

• Docker Compose demonstrates multiple progress bars for parallel operations showing download and extraction status.

• The `jq` command-line JSON processor displays introductory help before suggesting full help flag usage.

• Git commands display most common commands first in help text to prioritize frequently-used functionality.

• Heroku CLI uses formatting with bold headings in help text to improve scannability without escape characters.

• YubiKey-agent uses emoji strategically to add structure and draw attention to important security information.

• The `man` command remains widely used for CLI documentation despite not running on all platforms.

• Configuration files like Makefile, package.json, and docker-compose.yml represent stable project-level decisions.

# REFERENCES

• docopt - Multi-platform argument parsing library

• argbash - Bash-specific argument parsing library

• Cobra - Go argument parsing library

• cli - Go argument parsing library

• optparse-applicative - Haskell argument parsing library

• picocli - Java argument parsing library

• ArgParse.jl - Julia argument parsing library

• Comonicon.jl - Julia argument parsing library

• clikt - Kotlin argument parsing library

• oclif - Node.js argument parsing library

• parseArgs - Deno argument parsing library

• Getopt::Long - Perl argument parsing library

• console - PHP argument parsing library

• CLImate - PHP argument parsing library

• Argparse - Python argument parsing library

• Click - Python argument parsing library

• Typer - Python argument parsing library

• TTY - Ruby argument parsing library

• clap - Rust argument parsing library

• swift-argument-parser - Swift argument parsing library

• jq - Command-line JSON processor tool

• ronn - Man page generation tool

• PyInstaller - Python binary distribution tool

• tqdm - Python progress bar library

• schollz/progressbar - Go progress bar library

• node-progress - Node.js progress bar library

• pypager - Python paging library

• dotenv (Rust) - Environment variable loading library

• dotenv (Node) - Environment variable loading library

• dotenv (Ruby) - Environment variable loading library

• XDG Base Directory Specification - Configuration directory standard

• POSIX Utility Conventions - Unix command-line standards

• GNU Coding Standards - Program behavior guidelines

• 12 Factor CLI Apps - CLI application design principles

• Heroku CLI Style Guide - CLI interface design guidelines

• The Unix Programming Environment - Kernighan and Pike reference

• The Poetics of CLI Command Names - Command naming article

• Do What I Mean (DWIM) - Jargon file concept

• Open Source Metrics - Metrics collection guidelines

• no-color.org - NO_COLOR environment variable standard

• Google Writing Helpful Error Messages - Error message guidelines

• Nielsen Norman Group Error-Message Guidelines - UX error standards

• Crash-only Software: More than meets the eye - Crash-only design article

# ONE-SENTENCE TAKEAWAY

Design command-line interfaces prioritizing human usability through clear help, responsive feedback, and thoughtful error handling.

# RECOMMENDATIONS

• Implement argument parsing using language-specific libraries to handle flags, arguments, and help text consistently.

• Return appropriate exit codes; zero for success and non-zero for specific failure modes for script integration.

• Separate stdout for output and stderr for messaging to enable proper piping and script integration patterns.

• Display concise help when required arguments are missing instead of hanging or showing cryptic error messages.

• Provide extensive help accessible via `-h` and `--help` flags with examples leading documentation sections.

• Use TTY detection to intelligently format output as human-readable or machine-readable based on context.

• Support `--plain` flag for tabular output and `--json` flag for structured data in scripts.

• Disable color automatically when stdout is not a TTY or when NO_COLOR environment variable is set.

• Catch common errors and rewrite them as helpful guidance rather than displaying raw technical error output.

• Suggest next commands users should run when commands form workflows to help discover new functionality.

• Make program names short, memorable, and easy to type using only lowercase letters and dashes.

• Provide both web-based and terminal-based documentation for accessibility across different user contexts and preferences.

• Print progress indicators for operations taking longer than a few seconds to prevent appearing frozen.

• Make arguments, flags, and subcommands order-independent where possible to reduce user confusion and syntax errors.

• Never accept secrets via command-line flags; use files, stdin, or credential management services instead.

• Implement `--no-input` flag to explicitly disable all interactive prompts in non-interactive contexts.

• Ask for confirmation before dangerous operations; scale confirmation difficulty to operation severity and destructiveness.

• Support `-` to read from stdin or write to stdout when input or output is a file.

• Follow XDG Base Directory Specification for configuration file locations to avoid cluttering user home directories.

• Apply configuration parameters in strict precedence order: flags, environment, project config, user config, system.

• Read project-specific configuration from `.env` files for configuration varying between different project contexts.

• Use environment variables for context-dependent behavior that varies between invocations or terminal sessions.

• Exit immediately on Ctrl-C interrupt; say something immediately before starting any cleanup operations afterward.

• Distribute as single binary when possible; use platform package installers if language doesn't support compilation.

• Provide clear instructions for uninstalling programs at bottom of installation instructions for user convenience.

• Collect analytics only with explicit user consent; be transparent about what data is collected and retained.