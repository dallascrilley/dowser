# Skill / Process: Designing High-Quality Command-Line Interfaces (CLIs)

Design CLI tools that feel natural to humans, compose cleanly in scripts, and remain stable, debuggable, and extensible over time.

## Section 1: Best Practice Rules

### 1.1 Technical Rules

- Use a mature CLI argument-parsing library (with subcommand and help support) instead of manual argv inspection, so flags, args, and errors stay consistent across commands.
- Reserve `-h`/`--help` exclusively for help and wire every entry point (`mycli`, `mycli cmd`, `mycli help cmd`, `mycli cmd -h/--help`) to display concise or full help even if other flags or args are present.
- Prefer named flags over positional args whenever more than one input type is involved, keeping multiple positional args only for homogeneous lists such as file paths or globs.
- Route primary results and machine-readable payloads solely to stdout and send progress, prompts, warnings, and errors to stderr, including stderr propagated unchanged from child processes.
- Detect TTY vs non-TTY for stdout and stderr and automatically disable colors, spinners, animations, and pagers when output is piped or when NO_COLOR/TERM=dumb/`--no-color` indicates they are unwanted.
- Offer explicit machine-friendly modes such as `--json` and a plain tabular mode (`--plain`/`--no-headers`/`--no-truncate`) that guarantee one logical record per line for downstream tools.
- Implement table helpers where callers can choose visible columns (`--columns`), sort (`--sort`, with multi-column and inverse support), and filter (`--filter`) instead of handcrafting ad-hoc column layouts each time.
- Standardize flag names and semantics (`--all`, `--force`, `--dry-run`, `--quiet`, `--output`, `--no-input`, `--json`, `--version`) to match common Unix/GNU conventions and reuse them consistently across subcommands.
- Implement prompting logic that triggers only when stdin is a TTY, always has equivalent flags or args, respects `--no-input`/`--non-interactive`, and cleanly skips prompts in scripted or piped contexts.
- Add configurable timeouts, retry policies, and idempotent steps for network and filesystem operations so rerunning the same command is safe and long-running tasks can be resumed or retried predictably.

### 1.2 Conceptual / Philosophical Rules

- Default to human-optimized interaction at a TTY and expose opt-in switches for scripts, rather than optimizing for automation and forcing humans to memorize extra flags for sane behavior.
- Lead with realistic, copy-pasteable examples in help and docs because users adopt commands by mimicking concrete scenarios long before they internalize abstract descriptions.
- Treat every flag, argument, subcommand, environment variable, and structured output format as a stable public API and assume someone will eventually depend on its exact behavior in a script.
- Prefer additive evolution (new flags, new subcommands, new formats) over breaking changes, and when deprecation is unavoidable, emit clear, actionable warnings at the exact point of use before changing behavior.
- Default to error messages that read like a short conversation—what failed, why it likely happened, and exactly what to run next—rather than exposing raw stack traces or low-level library messages.
- Bias toward explicit, user-confirmed state changes (especially destructive ones) instead of “do what I mean” behavior that silently rewrites ambiguous input or auto-corrects potentially dangerous commands.
- Model multi-command CLIs as coherent verb–noun or noun–verb hierarchies and ensure shared concepts (targets, filters, output modes, config) feel identical everywhere to reduce cognitive load.
- Separate human and machine concerns by allowing human-facing formatting and wording to evolve for clarity while guaranteeing long-term stability for documented plain/JSON output modes.
- Assume your CLI will be combined with unknown future tools and environments, so design exit codes, streaming output, and text formats to be composable, grep/jq-friendly, and free of hidden side channels.
- Design for hostile or unusual environments (poor networks, weird terminals, odd filesystems) from the start, treating bug reports from those edge cases as first-class data for improving robustness.

## Section 2: Canonical Patterns & Workflows

### Pattern: Design a New CLI Command Interface

**Goal**  
- Define a new command or subcommand that is memorable, scriptable, and consistent with the rest of the CLI.

**When to Use**  
- You are adding a new piece of functionality to an existing CLI.
- You are designing a new CLI from scratch and defining its initial commands.
- You are refactoring a set of ad-hoc scripts into a coherent command surface.
- You need to expose a new resource type or workflow as a first-class operation.

**Required Inputs**  
- Clear description of the operation’s purpose, inputs, and outputs.
- List of related existing commands and their flag conventions.
- Any constraints around scripting, interactivity, or backward compatibility.

**Workflow Steps**  
1. Choose a topic and verb (or noun–verb pair) that match existing naming patterns and decide whether the command is top-level or a subcommand under an existing topic.
2. Enumerate required and optional inputs, then map heterogeneous inputs to flags (with long and short forms) and reserve at most one or two positional args for obvious primary operands.
3. Define help text: a one-line description under 80 characters, 1–3 realistic examples (including at least one with flags), and a link or reference to more detailed documentation.
4. Configure the argument parser with the chosen name, flags, and subcommand structure, ensuring `-h`/`--help` works everywhere and mis-typed commands produce suggestions rather than silent failure.
5. Decide on default output: concise, human-readable text or a table for interactive use, plus corresponding `--json`/plain modes that provide stable shapes for scripts.
6. Add prompts or confirmations only where they improve safety (e.g., destructive actions), ensuring every prompt has a bypass path via flags/env vars and can be globally disabled for automation.
7. Validate the design by walking through one interactive use case and one scripted use case (shell pipeline or CI) and adjust flags, output, or naming where friction appears.

**Expected Outputs**  
- **Primary Output:** A fully specified command definition (name, flags, args, help text, and output modes) ready for implementation.  
- **Secondary Outputs (if any):**
  - Notes on examples and tutorials to add to web docs.
  - A short compatibility note if any existing behavior is being deprecated or changed.

---

### Pattern: Human-Readable Output with Scriptable Modes

**Goal**  
- Present results in a way that is easy for humans to scan while remaining robust for parsing and composition in scripts.

**When to Use**  
- A command returns a list or table of resources, events, or metrics.
- Users are likely to filter, sort, or aggregate the output using shell tools.
- The same command must serve both casual terminal users and automated pipelines.

**Required Inputs**  
- The data model for each record (fields, types, and typical counts).
- Expected human workflows (e.g., “find failures”, “see latest N items”).
- Requirements for structured formats (fields that must be present in JSON/plain modes).

**Workflow Steps**  
1. Choose a concise default human view (3–6 key columns or fields) and define truncation behavior for long values, aiming to fit comfortably within common terminal widths.
2. Implement a table or formatted text renderer that outputs exactly one logical record per line without ASCII borders, while showing headers by default and allowing `--no-headers`.
3. Add flags such as `--columns`, `--sort`, and `--filter` to allow users to customize views without relying on brittle string parsing or column counting.
4. Provide a `--plain` or equivalent mode that disables any multi-line cells, truncation tricks, or extra adornments, guaranteeing a stable one-record-per-line format for tools like `grep`, `cut`, and `awk`.
5. Implement `--json` that returns a structured, documented schema (array or stream of objects) suitable for `jq` and web integration, and avoid mixing human language noise into this output.
6. Gate colors, symbols, and progress embellishments behind TTY detection and user preferences so they never pollute JSON/plain streams or logs unless explicitly requested.
7. For commands that change state, append a brief summary line or suggested next command (e.g., “Run `mycli status` to view changes”) to help users build mental models and workflows.

**Expected Outputs**  
- **Primary Output:** A command whose default output is easily readable and whose `--json`/plain modes are stable and reliable for scripting.  
- **Secondary Outputs (if any):**
  - Output schema notes for documentation.
  - Example pipelines demonstrating `grep` and `jq` usage.

---

### Pattern: Helpful Error and Debug Experience

**Goal**  
- Turn failures into actionable guidance for the user and gather enough context to debug unexpected issues without overwhelming them.

**When to Use**  
- Any operation that touches the network, filesystem, or external services.
- Commands that involve multiple steps or complex preconditions.
- Areas where past bugs have been hard to reproduce or triage.

**Required Inputs**  
- Catalog of expected failure modes (permission issues, not found, timeouts, validation errors).
- Error codes or messages returned by dependencies (APIs, libraries, system calls).
- Bug-reporting path (issue tracker URL, support email, or similar).

**Workflow Steps**  
1. Classify failures into “expected” (user or environment issues) and “unexpected” (bugs or truly unknown states) and decide which should produce tailored messages vs debug dumps.
2. For each expected error, design a structured message that includes a short code, one-line title, optional human description, a concrete remediation command or action, and a URL for deeper explanation.
3. Map major failure classes to distinct non-zero exit codes and document them, so scripts can differentiate between user errors, transient conditions, and internal bugs.
4. Implement a centralized error handler that formats messages consistently, sends them to stderr, and ensures normal output on stdout is not mixed with error noise.
5. Add a debug mode controlled via flags (`--debug`, `--verbose`) and environment variables (`DEBUG=...`) that surfaces stack traces, HTTP traces, or raw payloads in a controlled way (typically to stderr or a log file).
6. When an unexpected error occurs, emit a concise summary plus instructions or a pre-filled URL for bug reporting, optionally pointing to a log file containing full debug details.
7. Periodically review logs and user reports to refine error messages and remediation hints, folding recurring support questions back into clearer primary errors.

**Expected Outputs**  
- **Primary Output:** A consistent error-handling layer that produces human-friendly messages, appropriate exit codes, and optional rich debugging information.  
- **Secondary Outputs (if any):**
  - Error code reference for docs.
  - Template text for bug-report issues including fields for logs and debug info.

---

### Pattern: Resilient Long-Running and Networked Operations

**Goal**  
- Execute long-running or network-intensive tasks in a way that feels responsive, survives interruptions, and can be safely retried.

**When to Use**  
- Commands that download/upload data, perform migrations, or process large datasets.
- Operations that depend on remote services or flaky networks.
- Multi-step workflows where partial progress should be preserved.

**Required Inputs**  
- Breakdown of the operation into discrete steps and side effects.
- Knowledge of which steps are idempotent or can be made idempotent.
- Constraints on execution time, retries, and failure semantics.

**Workflow Steps**  
1. Decompose the operation into logically independent, idempotent steps and define checkpoints or markers that represent “safe points” for resuming work.
2. Add progress indication appropriate to the context (spinner, percentage, multi-bar progress) while ensuring underlying logs are available in debug mode and that non-TTY output remains clean.
3. Configure sensible default timeouts and retry policies for network calls, with flags/env vars to override them, and ensure all such failures surface clear, actionable messages.
4. Implement Ctrl-C handling that stops at the next safe boundary, reports what was completed, and either performs bounded cleanup or defers cleanup to the next run in a crash-only fashion.
5. Provide an explicit “resume” behavior (implicit via idempotence or explicit via flags/checkpoints) so re-running the same command after a transient failure continues rather than redoing everything or corrupting state.
6. Test the operation in degraded conditions (slow network, partial data, mid-run interruption, non-TTY output) and tighten timeouts, progress reporting, and recovery paths based on observed behavior.
7. Document the guarantees (what is atomic, what may be partially applied, how to safely retry) so both humans and automations know how to orchestrate the command.

**Expected Outputs**  
- **Primary Output:** A long-running or networked command that remains responsive, recoverable, and safe to retry under real-world conditions.  
- **Secondary Outputs (if any):**
  - Notes on operational runbooks or recommended retry strategies.
  - Example invocations showing timeout overrides and resume behavior.

<!-- Repeat structure for remaining patterns (if needed) -->

## Section 3: Failure Modes & Self-Check Checklist

### 3.1 Common Failure Modes

- Tends to print human-facing status messages and prompts to stdout instead of stderr. This causes scripts to break when they parse output or pipe it into other tools.  
- Often relies on multiple positional arguments for different concepts instead of flags. This leads to confusing invocation order, hard-to-remember syntax, and accidental misuse.  
- Frequently leaves colors, spinners, or progress bars enabled when output is piped. This results in log files and CI logs filled with escape codes and unreadable “Christmas tree” output.  
- Sometimes exposes raw stack traces or library error messages directly to users. This creates noisy, intimidating errors that don’t explain what to do next and leak internal implementation details.  
- Can change human-readable output shape or wording between versions without providing stable `--plain`/`--json` modes. This produces subtle breakages in existing scripts that depended on the previous format.  
- Tends to require interactive prompts for essential inputs without non-interactive alternatives. This causes commands to hang or fail when run in CI, cron, or other automated environments.

### 3.2 Hard Constraints / Never-Do Rules

- Never overload `-h` or `--help` with any behavior other than showing help. This prevents users and tools from losing a universal escape hatch for understanding the CLI.  
- Never emit primary result data or structured records to stderr. This avoids corrupting pipelines and ensures scripts can reliably consume stdout only.  
- Never require an interactive prompt as the sole way to provide input. This prevents deadlocks in non-TTY environments and keeps every command scriptable.  
- Always provide a non-interactive confirmation mechanism (`--force`, `--confirm=name`, or equivalent) before performing dangerous or destructive actions. This ensures safety for humans while still enabling automation.  
- Always treat `--json`/plain modes as stable contracts before changing output. This ensures existing scripts continue to work even as human-facing formatting evolves.  

### 3.3 Pre-Response Self-Check Checklist

- [ ] Have I chosen flags, args, and subcommands so that inputs are unambiguous, scriptable, and consistent with existing commands (including reserved use of `-h/--help`)?  
- [ ] Does my implementation route primary data to stdout and all progress, logging, prompts, and errors to stderr, including from child processes?  
- [ ] Does the command show concise help and examples when run with no args (where appropriate) and full help when any of the help mechanisms (`-h`, `--help`, `mycli help ...`) are used?  
- [ ] Can the command run fully non-interactively (no required prompts) using flags or env vars, and does `--no-input` or equivalent reliably disable all interactive behavior?  
- [ ] Does the output provide both a readable default view and at least one stable, documented machine-readable mode (`--json` or `--plain`) suitable for `grep`/`jq` and pipelines?  
- [ ] Are exit codes strictly zero for success and non-zero for failure, with important error classes mapped to distinct, documented codes?  
- [ ] For any long-running or networked operation, have I added visible progress, reasonable timeouts, and a safe retry/resume story?  
- [ ] Have I avoided breaking existing flags, commands, or output shapes, or, where impossible, added clear deprecation warnings and migration guidance?  
- [ ] Would a new user be able to accomplish the primary task using only `--help` output and the provided examples without reading external docs?  
- [ ] Would this command’s behavior and surface pass review by an experienced CLI developer focused on usability, composability, and backward compatibility?  