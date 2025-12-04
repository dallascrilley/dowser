Skill / Process: Designing Robust, User-Friendly CLI Tools
Enable AI agents to design CLI tools that behave predictably in scripts while providing first-class UX for humans.
Section 1: Best Practice Rules
1.1 Technical Rules
Prefer a mature argument-parsing library over manual parsing. This ensures consistent handling of flags, subcommands, help text, and edge cases like abbreviations or typos.
Route primary command results to stdout and all messaging, logs, and errors to stderr. This keeps pipelines composable while still surfacing information to humans.
Display concise, usage-focused help on bare invocation or invalid input and full, exhaustive help on -h, --help, and help subcommands. This gives fast guidance by default while still supporting deep discovery on demand.
Detect TTY status for stdin, stdout, and stderr and gate prompts, colors, pagers, and animations on it. This prevents interactive features from hanging scripts or polluting non-interactive logs.
Provide machine-readable modes such as --json and --plain that stabilize output structure without sacrificing human readability in the default mode. This allows tooling to rely on stable formats while humans get richer output by default.
Standardize flag names and always offer long forms (and short forms only for high-traffic flags). This aligns with ecosystem expectations and preserves room for future flags.
Prefer flags to positional arguments and keep flags, arguments, and subcommands as order-independent as your parsing library allows. This makes invocations easier to modify and reduces surprising “works only in this order” bugs.
Implement explicit --dry-run and --force/--confirm flows for any operation that mutates or destroys state. This lets users safely preview and intentionally commit dangerous actions in both interactive and scripted contexts.
Use progress indicators, timeouts, and resumable behavior for long-running or networked operations. This keeps the tool responsive, avoids infinite hangs, and lets users simply rerun a failed command to continue.
Implement configuration resolution in strict precedence (flags > env vars > project config > user config > system config) and follow XDG base directories for config files. This creates predictable behavior across machines and environments.
1.2 Conceptual / Philosophical Rules
Default to “optimize for humans, preserve reliability for scripts” when designing output and interaction modes. This keeps day-to-day usage pleasant without breaking automation.
Treat CLI commands, flags, and structured outputs as stable interfaces that require deprecation plans, not casual refactors. This protects users from silent breakage in scripts and workflows.
Prefer explicit, visible actions at system boundaries (filesystem, network, external services) over hidden side effects. This helps users understand and trust what the tool is doing to their systems.
Design for discoverability via rich examples, suggested follow-up commands, and consistent naming across subcommands. This turns the CLI itself into the primary learning surface for users.
Treat error messages as a form of documentation that teaches users how to fix issues and proceed. This converts failure states into guided workflows instead of dead ends.
Bias toward crash-only, idempotent operations that can be retried without cleanup. This makes the tool more robust to interruptions and partial failures.
Assume users will misuse or stress your tool (bad input, flaky network, parallel runs, odd filesystems) and harden behavior accordingly. This prevents “works on my machine” design from leaking into production.
Avoid “Do What I Mean” magic, catch-all subcommands, and arbitrary abbreviations that constrain future extensibility. This preserves your ability to evolve the command surface without breaking existing users.
Make telemetry and analytics explicit, consensual, and well-documented rather than hidden. This maintains user trust and aligns with CLI expectations of local control.
Choose short, memorable, lowercased names that avoid collisions and awkward typing patterns. This respects CLI culture and reduces friction every time the tool is invoked.
Section 2: Canonical Patterns & Workflows
Pattern: TTY-Aware I/O & Help Design
Goal
Deliver clear, context-appropriate output and help that behaves correctly in both interactive terminals and automated pipelines.
When to Use
You are adding or refining help output, colors, or progress UI.
The command may be used in both CI/scripts and interactive shells.
You are introducing new output formats (--json, --plain, etc.).
Required Inputs
Description of the command’s primary outputs and side effects.
Requirements for scripting and integration (e.g., expected pipelines).
Target environments (CI, local dev, remote shells) and their constraints.
Workflow Steps
Classify each piece of output as primary result vs diagnostic/log and assign it to stdout or stderr accordingly.
Detect TTY status for stdin, stdout, and stderr and document how it changes behavior (prompts, colors, pagers, animations).
Design concise default help for bare invocation/invalid usage and full help for -h, --help, and help subcommands, leading with examples.
Introduce --json and/or --plain modes with stable, line-based structures and clear documentation of their schemas.
Implement color and formatting with graceful degradation when colors are disabled or unsupported, and ensure piping/paging produces clean logs.
Expected Outputs
Primary Output: Implemented I/O and help behavior that adapts to TTY vs non-TTY contexts without breaking scripts.
Secondary Outputs (if any):
Documentation snippets describing modes (--help, --json, --plain) and their guarantees.
Test cases or examples that demonstrate behavior in interactive vs piped/CI scenarios.
Pattern: Safe Destructive Operations with Dry Run & Confirmation
Goal
Perform state-changing or destructive operations safely, predictably, and scriptably.
When to Use
A command can delete, overwrite, or irreversibly change resources.
The impact of a single command may be large or non-obvious (bulk edits, cascades).
Required Inputs
Clear description of what resources the command can affect.
Risk categorization for operations (mild, moderate, severe).
Workflow Steps
Identify all destructive or non-trivial state changes and categorize them by severity (mild/moderate/severe).
Implement --dry-run (or -n) that prints what would happen without making changes, using human-readable but high-signal output.
For interactive TTY use, add confirmations appropriate to severity (simple yes/no, typing resource name, etc.); for non-TTY or --no-input, require explicit flags instead.
Provide a --force or --confirm=<value> flag that bypasses prompts in a controlled, explicit way suitable for scripts.
Ensure that rerunning the command after partial failure is safe (idempotent where possible, or resumable with clear messaging) and document that behavior.
Expected Outputs
Primary Output: A command implementation that cannot perform destructive actions silently or accidentally, yet remains fully scriptable.
Secondary Outputs:
Example invocations showing --dry-run, interactive confirmation, and forced execution.
Pattern: Future-Proof CLI Interface Evolution
Goal
Evolve a CLI’s surface area (commands, flags, outputs) without breaking existing users or scripts.
When to Use
You are adding or changing flags, subcommands, or output formats.
You need to deprecate legacy behavior or restructure commands.
You are making changes that could affect scripts depending on current output.
Required Inputs
Current command/flag/output behavior and known usage patterns.
Proposed new behavior and rationale for the change.
Workflow Steps
Analyze how the existing interface is used (docs, examples, expected scripts) and identify any breaking changes introduced by your proposal.
Prefer additive changes (new flags, new subcommands, new structured modes) over changing semantics of existing ones, and avoid catch-all subcommands or abbreviations that block future additions.
When non-additive changes are unavoidable, introduce deprecation warnings in the CLI output that explain the future change and the forward-compatible alternative.
Detect when users adopt the new form and suppress deprecation warnings for them while keeping old behavior stable until removal.
Encourage scripts to rely on --plain or --json interfaces for stability and limit changes in human-oriented output to those modes.
Expected Outputs
Primary Output: A migration-safe plan and implementation for evolving CLI behavior without surprising existing users.
Secondary Outputs (if any):
Deprecation messaging text and examples.
Notes for release documentation describing changes and timelines.
Section 3: Failure Modes & Self-Check Checklist
3.1 Common Failure Modes
Tends to assume an interactive TTY and uses prompts, colors, or pagers even in non-interactive contexts. This causes hung CI jobs and unreadable logs.
Often mixes human messages with primary data on stdout. This leads to broken pipelines when scripts parse the output.
Frequently invents non-standard or inconsistent flag names and semantics across subcommands. This results in user confusion and hard-to-remember invocations.
Sometimes performs destructive operations without clear previews or confirmations. This creates accidental data loss or irreversible changes.
Can change flag behavior or output structure without deprecation or alternate modes. This produces silent breakage in existing user scripts.
3.2 Hard Constraints / Never-Do Rules
Never prompt for input or rely on interactivity when stdin is non-TTY or --no-input is set. This prevents commands from hanging in automated environments.
Never accept secrets directly via flags or environment variables when safer file or pipe mechanisms are feasible. This avoids leaking credentials into process lists, logs, or shared environments.
Always separate primary data from diagnostics using stdout for results and stderr for messages. This ensures pipelines and tools can reliably consume outputs.
Always make telemetry and analytics opt-in or clearly disclosed with simple opt-out controls. This protects user trust and aligns with CLI expectations of transparency.
3.3 Pre-Response Self-Check Checklist
[ ] Have I clearly separated stdout vs stderr and considered TTY detection for prompts, colors, pagers, and animations?
[ ] Have I provided concise default help and richer --help output, leading with realistic examples and common flags?
[ ] Have I designed or preserved machine-readable modes (--json, --plain) so scripts are not dependent on human-oriented output?
[ ] Have I implemented safe patterns for destructive operations, including --dry-run, confirmations, and explicit force flags where appropriate?
[ ] Have I respected configuration precedence (flags > env > project > user > system) and XDG directories where applicable?
[ ] Have I avoided non-obvious magic behaviors (catch-all subcommands, DWIM corrections, ambiguous abbreviations) that constrain future evolution?
[ ] Have I considered idempotence, timeouts, and resumability for long-running or networked operations?
[ ] Have I ensured no secrets are read via flags or environment variables when safer alternatives are available?
[ ] Is the naming of commands and flags consistent, memorable, and aligned with common Unix/CLI conventions?
[ ] Would this CLI behavior remain predictable and non-breaking for existing users if shipped as-is in a future version?