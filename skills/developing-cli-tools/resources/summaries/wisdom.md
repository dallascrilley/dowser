                                   
# SUMMARY

Jeff D. and CLI development experts present comprehensive guidelines for building command-line applications with focus on user experience, composability, and modern best practices.

# IDEAS

• Great help documentation is essential for CLIs since users cannot rely on visual UI guidance like web applications provide users.

• Flags should be preferred over arguments because they make commands clearer and easier to understand for users executing them.

• CLI applications must display version information through multiple methods to ensure users can easily find version numbers.

• Stdout should contain program output while stderr should contain all messaging, warnings, and errors from the application.

• Error messages should include error codes, titles, descriptions, fix instructions, and URLs for comprehensive user guidance.

• Modern CLIs should use colors, spinners, and progress bars to provide visual feedback while remaining scriptable when needed.

• Prompting for input improves UX when stdin is a TTY but must never require prompts to maintain scriptability for automation.

• Tables should output one record per line without borders to remain compatible with grep, awk, and other Unix tools.

• CLI startup time is critical; applications should aim for 100-500ms startup time to feel responsive and fast.

• Contributing guidelines and open source code encourage users to diagnose problems and extend functionality through plugins.

• Multi-command CLIs should use consistent subcommand patterns with colons preferred over spaces for topic separation.

• XDG-spec should be followed for file storage to use standard locations like ~/.config and ~/.local/share directories.

• Human-first design prioritizes making CLIs usable by people rather than optimizing for machine-to-machine communication.

• Simple composable parts that work together enable users to build larger systems by combining multiple CLI tools.

• Consistency across programs means users can apply learned patterns to new tools without requiring extensive new learning.

• Saying just enough means providing sufficient information to prevent user confusion without overwhelming them with data.

• Ease of discovery requires comprehensive help texts, examples, and suggestions to guide users toward success.

• Conversation as interaction norm acknowledges that CLI usage involves repeated invocations and learning through trial-and-error.

• Robustness requires both objective stability and subjective feeling of reliability through attention to detail.

• Empathy means exceeding user expectations by showing you understand their problems and want them to succeed.

• Chaos in terminal conventions creates power and flexibility but requires intentional rule-breaking with clarity of purpose.

• Use command-line argument parsing libraries to handle arguments, flags, help text, and spelling suggestions sensibly.

• Return zero exit code on success and non-zero on failure so scripts can determine whether programs succeeded.

• Display extensive help text when users pass -h or --help flags to provide immediate access to documentation.

• Show concise help text by default when commands require arguments but receive none to guide users quickly.

• Provide web-based documentation so people can search online and link to specific parts of your documentation.

• Terminal-based documentation should be accessible via the tool itself to work without internet connectivity requirements.

• Human-readable output is paramount; machines come second in priority when designing CLI output formats.

• Machine-readable output should not impact usability; use --plain and --json flags to support different use cases.

• Display output on success but keep it brief; traditionally Unix commands display nothing but this confuses humans.

• If you change state, tell the user exactly what happened so they can model the system state accurately.

# INSIGHTS

• CLI design balances human usability with machine composability by following Unix conventions while breaking them intentionally.

• Error messages are documentation; comprehensive error messages with fix instructions save users enormous time debugging issues.

• Terminal detection via TTY enables CLIs to adapt intelligently between interactive human use and scriptable automation contexts.

• Configuration precedence (flags > env vars > project config > user config > system config) enables flexible usage patterns.

• Progress indicators and spinners dramatically improve perceived performance by showing work happening without actual speedups.

• Table output design for grep-compatibility maintains Unix philosophy while modern --json flags enable sophisticated data manipulation.

• Subcommand design with topic:verb patterns prevents ambiguity and enables hierarchical organization of complex tool functionality.

• XDG compliance and standard environment variables reduce cognitive load by following established cross-platform conventions.

• Prompts improve UX for interactive use while scriptability requires non-interactive alternatives through flags and environment variables.

• Open source with contribution guidelines creates community investment and enables users to solve problems independently.

# QUOTES

• "CLIs are a fantastic way to build products. Unlike web applications, they take a small fraction of the time to build and are much more powerful." - Jeff D.

• "With the web, you can do whatever the developer programmed. With CLIs, you can easily mash-up multiple tools together yourself to perform advanced tasks." - Jeff D.

• "Great help is essential. It's far more important than when building a web application as you can't guide the user with a UI." - Jeff D.

• "Flags are also much easier to write autocomplete logic for as you know exactly what the value should be." - Jeff D.

• "stdout is for output, stderr is for messaging." - Jeff D.

• "Things go wrong in CLIs much more often than in web apps. Without a UI to guide the user, the only thing we can do is display an error to the user." - Jeff D.

• "Modern CLIs shouldn't be afraid to show off. Use colors/dimming to highlight important information." - Jeff D.

• "Spinners and progress bars are also not a good idea when it's not a tty. These work by outputting ansi codes to overwrite which only works on a screen." - Jeff D.

• "Just think if every CLI was this helpful how incredible it would be to be a programmer." - Jeff D.

• "Human-first design: Traditionally, UNIX commands were written under the assumption they were going to be used primarily by other programs." - CLI Guidelines

• "Simple parts that work together: A core tenet of the original UNIX philosophy is the idea that small, simple programs with clean interfaces can be combined." - CLI Guidelines

• "Consistency across programs: The terminal's conventions are hardwired into our fingers." - CLI Guidelines

• "Saying just enough: A command is saying too little when it hangs for several minutes and the user starts to wonder if it's broken." - CLI Guidelines

• "Ease of discovery: GUIs have the upper hand because everything you can do is laid out in front of you on the screen." - CLI Guidelines

• "Conversation as the norm: Running a program usually involves more than one invocation because it's hard to get it right the first time." - CLI Guidelines

• "Robustness is both an objective and a subjective property. Software should be robust, and it should feel robust." - CLI Guidelines

• "Empathy: Command-line tools are a programmer's creative toolkit, so they should be enjoyable to use." - CLI Guidelines

• "Chaos: The world of the terminal is a mess. Inconsistencies are everywhere, slowing us down and making us second-guess ourselves." - CLI Guidelines

• "Abandon a standard when it is demonstrably harmful to productivity or user satisfaction." - Jef Raskin

• "Expect the output of every program to become the input to another, as yet unknown, program." - Doug McIlroy

• "Note the obsessive use of abbreviations and avoidance of capital letters; Unix is a system invented by people to whom repetitive stress disorder is what black lung is to miners." - Neal Stephenson

• "The primary goal of anyone for developing CLI plugins should always be usability." - Heroku CLI Style Guide

• "Input and output should be consistent across commands to allow the user to easily learn how to interact with new commands." - Heroku CLI Style Guide

• "Care should be taken that in future releases of commands that (when possible) commands do not change their inputs and stdout after general availability in ways that will break current scripts." - Heroku CLI Style Guide

• "Stdout should be used for all output and stderr for warning, errors and out of band information." - Heroku CLI Style Guide

# HABITS

• Always provide --help and -h flags that display comprehensive help documentation including examples and descriptions.

• Use argument parsing libraries like Commander.js, Click, or Cobra to handle flags, arguments, and help text consistently.

• Check that stdout is a TTY before displaying colors, spinners, and progress bars to maintain scriptability.

• Test CLI startup time using the time command and aim for 100-500ms to feel responsive to users.

• Display version information through multiple methods: mycli version, mycli --version, and mycli -V for user convenience.

• Write error messages with error codes, titles, descriptions, fix instructions, and URLs for comprehensive guidance.

• Use environment variables like NO_COLOR, DEBUG, and TERM to allow users to control CLI behavior globally.

• Implement prompting only when stdin is a TTY and always provide flag alternatives to maintain scriptability.

• Output tables with one record per line without borders to maintain compatibility with grep and other Unix tools.

• Pipe stderr from subcommands directly to users to surface all issues immediately to the user's screen.

• Respect the TMPDIR environment variable when creating temporary files instead of hardcoding /tmp paths.

• Follow XDG-spec for configuration files using ~/.config/myapp and ~/.local/share/myapp on Unix systems.

• Include example invocations in help text as users tend to reference examples more than other documentation.

• Use consistent flag names across commands like --all, --debug, --force, --json, and --quiet for familiarity.

• Make configuration additive where possible by adding new flags rather than modifying existing flag behavior.

• Test CLI tools with piped input/output and in non-interactive contexts to ensure scriptability works correctly.

• Document how to run the CLI locally and execute test suites to encourage community contributions.

• Use colors intentionally to highlight important information rather than applying colors to everything indiscriminately.

• Disable colors automatically when output is not a TTY or when NO_COLOR environment variable is set.

• Provide both web-based and terminal-based documentation so users can access help online or offline.

# FACTS

• Exit codes are limited to 8 bits (0-255) so programs should not use error count as exit status.

• Man pages are rarely used by novice developers and don't work on Windows making them less critical.

• Shell completion improves UX significantly and can be implemented through plugins or framework support.

• JSON output enables integration with jq tool ecosystem allowing sophisticated data transformation and filtering.

• TTY detection is the most reliable heuristic for determining whether output is being read by humans.

• POSIX specifies df and du use 512-byte units by default but GNU utilities use 1k units.

• Standard POSIX environment variables include HOME, TMPDIR, SHELL, TERM, EDITOR, and PATH.

• Unicode character widths should be used for column calculations in UTF-8 locales for proper alignment.

• XDG Base Directory Specification is supported by yarn, fish, wireshark, emacs, neovim, and tmux.

• Homebrew collects metrics to Google Analytics with opt-out default and provides detailed FAQ on practices.

• Angular.js collects detailed analytics using Google Analytics requiring explicit opt-in from users.

• Next.js collects anonymized usage statistics with opt-out default for feature prioritization purposes.

• Crash-only software can exit immediately on failure without cleanup by deferring cleanup to next run.

• Docker Compose allows Ctrl-C twice to force container stops instead of graceful shutdown.

• Temporary files in world-writable directories can be created safely using O_WRONLY | O_CREAT | O_EXCL flags.

• The mkstemps function from Gnulib provides secure temporary file creation across platforms.

• Process state from shell substitutions like curl -H "Authorization: Bearer $TOKEN" leaks into globally-readable memory.

• Docker container environment variables can be viewed by anyone with Docker daemon access via docker inspect.

• Systemd unit environment variables are globally readable via systemctl show for all users.

• Secrets should only be accepted via credential files, pipes, AF_UNIX sockets, or secret management services.

• HTTP libraries often automatically check HTTP_PROXY, HTTPS_PROXY, and NO_PROXY environment variables.

• Argument parsing libraries handle spelling suggestions automatically enabling helpful user guidance.

# REFERENCES

• 12 Factor App methodology - Heroku design principles for maintainable applications

• oclif framework - Node.js CLI framework following 12 factor principles with plugin system

• cli-ux library - Heroku CLI utilities for tables, actions, and user interface components

• Commander.js - Popular Node.js command-line interface framework for building CLIs

• Inquirer.js - Interactive command line prompts for Node.js applications

• Chalk - Terminal string styling library for colors and formatting

• Ora - Elegant terminal spinner and progress indicator library

• jq - Command-line JSON processor for data transformation and filtering

• GNU Coding Standards - Comprehensive standards for GNU program development

• POSIX Utility Conventions - Standards for command-line interface design

• The Design of Everyday Things - Don Norman book on design principles

• Macintosh Human Interface Guidelines - 1987 guidelines on UI design

• The Anti-Mac User Interface - Don Gentner and Jakob Nielsen article

• Crash-only software - Concept for robust software design patterns

• no-color.org - Standard for disabling colors in terminal output

• The Unix Programming Environment - Brian W. Kernighan and Rob Pike book

• The Humane Interface - Jef Raskin book on interface design

• In the Beginning was the Command Line - Neal Stephenson essay on CLI history

• The Poetics of CLI Command Names - Article on naming command-line tools

• Open Source Metrics - Guidance on measuring open source project usage

• User experience, CLIs, and breaking the world - John Starich article on CLI design

# ONE-SENTENCE TAKEAWAY

Design CLIs for humans first, make them composable, and provide helpful errors with examples always.

# RECOMMENDATIONS

• Implement comprehensive help text with examples as primary documentation for immediate user guidance access.

• Use flags exclusively for clarity and consistency rather than positional arguments that confuse users.

• Detect TTY to intelligently adapt output between human-friendly formatting and machine-readable plain text.

• Display progress indicators for long-running operations to prevent users from thinking the program crashed.

• Provide configuration through multiple methods: flags, environment variables, and config files in that precedence.

• Make error messages actionable by including error codes, descriptions, fix instructions, and documentation links.

• Support both web-based documentation and terminal-based help so users can access information offline.

• Output machine-readable JSON with --json flag to enable integration with jq and other tools.

• Test CLI tools with piped input/output to ensure they remain composable and scriptable always.

• Follow XDG-spec for file storage to use standard locations users expect and understand.

• Implement shell completion support to help users discover commands and arguments without manual lookup.

• Use colors intentionally to highlight important information rather than decorating all output indiscriminately.

• Respect environment variables like NO_COLOR, DEBUG, and TERM to honor user preferences.

• Prompt for input only when stdin is a TTY and always provide flag alternatives for scripts.

• Return proper exit codes so scripts can reliably determine whether commands succeeded or failed.

• Document how to run locally and run tests to encourage community contributions and improvements.

• Keep startup time under 500ms to feel responsive and not frustrate users with slowness.

• Make output grep-parseable by using one record per line without decorative borders or formatting.

• Provide version information through multiple methods: version subcommand, --version, and -V flags.

• Avoid reading secrets from flags or environment variables; use files or stdin for sensitive data.