# Skill / Process: Applying GNU Program & CLI Standards

Enable AI agents to build CLI tools and utilities that follow GNU standards for robustness, usability, portability, and consistency.

## Section 1: Best Practice Rules

### 1.1 Technical Rules

- Use dynamic allocation for variable-sized data structures instead of fixed-length buffers. This prevents silent truncation of long lines, filenames, or inputs.
- Preserve all input bytes, including NUL and nonprinting characters, and support multibyte encodings like UTF-8 via appropriate libraries. This ensures tools work correctly on arbitrary binary and international text data.
- Check the return value of every system call and memory allocation (including shrinking `realloc`) and include `strerror` text, file name, and program name in any resulting error message. This makes failures diagnosable and avoids silent corruption.
- Use the POSIX `sigaction` or BSD-style `signal` APIs consistently and avoid USG `signal`. This yields predictable, portable signal handling behavior.
- Parse command-line options with `getopt_long`, defining both POSIX-style short options and consistent GNU long options, and allow options to intermix with operands unless `--` terminates option parsing. This matches user expectations for GNU utilities.
- Implement `--help` and `--version` in every program (including CGI entry points) so that `prog --help` and equivalent PATH_INFO usage provide usage and version information. This guarantees basic discoverability and scripting compatibility.
- Format diagnostics as `program[:sourcefile[:lineno[:column]]]: message` using 1-based line and column numbers, lowercase message starts, and no trailing period. This keeps error messages both human-readable and machine-parseable.
- Avoid using raw error counts as exit statuses and instead map outcomes to conventional bounded codes (e.g., 0 for success, fixed nonzero codes for failures) while reporting counts in the output stream. This prevents 8‑bit exit code wrapping from misrepresenting failures as success.
- Create temporary files in a directory chosen from `TMPDIR` (falling back to `/tmp`) and use race-safe mechanisms such as `open(..., O_CREAT|O_EXCL, 0600)` or `mktemp`-style APIs. This avoids security issues and respects user configuration.
- Treat `/usr` and `/etc` as read-only for internal program state (logs, locks, scores, backups) and write such files to appropriate writable locations unless the user explicitly requests configuration changes there. This keeps programs functional on systems with read-only system directories.

### 1.2 Conceptual / Philosophical Rules

- Prefer following external standards (POSIX, language specs) only when they benefit users, and deviate when strict adherence produces objectively worse behavior, guarded by flags or environment variables for spec-required modes. This balances compatibility with practical usability.
- Default to “never lose or alter user data implicitly” over “make implementation convenient,” avoiding silent truncation, dropped bytes, or mangled encodings. This preserves user trust in core utilities.
- Treat device independence as a core design principle by avoiding behavior that changes based on whether output is a terminal or a file, except for guarded cases like blocking dangerous binary output to a TTY. This makes scripts and pipelines reliable.
- Keep program behavior independent of the executable name and avoid name-based mode switches, using runtime options or build-time variants for alternate behaviors instead. This prevents surprising changes when tools are symlinked or renamed.
- Prioritize robust, precise diagnostics over minimal output by emitting structured, information-rich error messages that capture where and why failures occurred. This greatly speeds debugging and tooling integration.
- Design CLIs so that filenames as positional arguments primarily denote inputs while outputs are specified with options (e.g., `-o` or `--output`). This reduces idiosyncrasies and aligns with established GNU conventions.
- Treat GUIs, D-bus interfaces, and libraries as layers on top of a solid CLI command, ensuring that all core functionality is scriptable and accessible. This maximizes reuse, automation, and accessibility support.
- Favor reentrant library designs with well-chosen, unique name prefixes and a clear separation between public and private symbols. This avoids symbol collisions and threading surprises when libraries are combined.
- Use explicit configuration and environment variables to override heuristic discovery of executables and associated files instead of relying solely on inferred locations. This gives users control when conventions fail.
- Optimize memory usage only when it meaningfully affects scalability limits (e.g., handling arbitrarily large input streams) and avoid complicating design just to appease analysis tools. This keeps code simpler while still supporting large workloads.

## Section 2: Canonical Patterns & Workflows

### Pattern: GNU-Style CLI Definition & Parsing

**Goal**  
- Define and implement a command-line interface consistent with GNU and POSIX expectations.

**When to Use**  
- You are creating a new CLI tool or refactoring an existing one’s argument parsing.
- You need short and long options that align with other GNU utilities.
- You want options to work reliably in scripts and pipelines across platforms.

**Required Inputs**  
- A functional specification of operations, flags, and operands the tool must support.
- Any compatibility requirements with existing tools or scripts.
- Access to the GNU long option table and common naming conventions.

**Workflow Steps**  
1. List all operations and modes the program must support, distinguishing flags, options with values, and positional operands.
2. Assign POSIX-style short options and choose consistent GNU long option names (reusing names from the GNU option table where semantics match).
3. Decide which arguments are inputs versus outputs, ensuring outputs are provided via options (e.g., `-o`, `--output`) even if positional outputs are also accepted for compatibility.
4. Implement parsing using `getopt_long`, allowing options to intermix with operands and honoring `--` to stop option parsing.
5. Add `--help` and `--version` handlers that print standardized usage and version info and exit with appropriate statuses.
6. Validate the final CLI by comparing its behavior and help output to established GNU tools with similar functionality.

**Expected Outputs**  
- **Primary Output:** A complete, GNU-consistent CLI definition plus implementation using `getopt_long` (or equivalent).
- **Secondary Outputs (if any):**
  - Short documentation snippet or usage string describing options and operands.
  - Test cases or example invocations covering typical and edge-case argument combinations.

### Pattern: Robust Error Reporting and Exit Behavior

**Goal**  
- Provide consistent, informative diagnostics and exit codes that are easy to interpret programmatically and by users.

**When to Use**  
- The tool reports errors tied to files, lines, or code locations (e.g., compilers, linters, formatters).
- You need logs or other tools to parse and react to program errors.
- The program must distinguish between different categories of failure.

**Required Inputs**  
- A list of error conditions and their associated context (program name, files, line/column data).
- Requirements for how calling tools or scripts interpret exit codes.
- Knowledge of whether the program runs interactively or noninteractively in its primary mode.

**Workflow Steps**  
1. Classify errors into categories (e.g., usage errors, runtime failures, internal bugs) and assign fixed exit codes within the 0–255 range for each category.
2. For noninteractive modes, format error messages as `program[:sourcefile[:lineno[:column]]]: message` with 1-based positions, lowercase message start, and no trailing period.
3. For interactive modes, omit the program name in messages and instead make the prompt or UI clearly indicate which program is running.
4. Ensure every system call and memory allocation failure is checked and reported with program name, relevant path, and `strerror` text.
5. Avoid using exit status to encode counts or large values, printing any such numbers in the message text instead.
6. Add tests or fixtures that assert correct diagnostic formatting and exit codes for representative failures.

**Expected Outputs**  
- **Primary Output:** Implementation of a consistent error-reporting and exit-code scheme covering all major failure paths.
- **Secondary Outputs (if any):**
  - Error message format examples documented in usage text or developer notes.
  - Test cases verifying formatting and exit behavior for key scenarios.

### Pattern: Safe Temporary & Auxiliary File Management

**Goal**  
- Manage temporary, lock, log, and auxiliary files securely and portably without assuming writable system directories.

**When to Use**  
- The program creates temporary files, lock files, logs, or internal backup/score files.
- The tool may run on systems where `/usr` and `/etc` are read-only.
- Security or multi-user correctness is a concern.

**Required Inputs**  
- The list of internal files the program needs to create or modify during normal operation.
- Any user configuration or environment variables related to file locations (e.g., `TMPDIR`, app-specific overrides).
- Requirements for file permissions and lifetimes.

**Workflow Steps**  
1. Categorize files into temporary, persistent internal state, and user-facing configuration, identifying which need to be writable at runtime.
2. For temporary files, first consult `TMPDIR` and fall back to `/tmp`, creating files with race-safe APIs (`O_CREAT|O_EXCL` or `mktemp`-style helpers) and mode `0600` where appropriate.
3. For persistent internal state (logs, locks, score files), choose writable locations outside `/usr` and `/etc` unless explicitly updating configuration files as part of the program’s job.
4. Ensure directory paths and filenames can be overridden by environment variables or configuration options when heuristics fail.
5. Implement cleanup strategies where necessary, avoiding reliance on manual removal for critical locks or temporary state.
6. Add checks or tests to simulate read-only `/usr` and `/etc` and verify that the program continues to function.

**Expected Outputs**  
- **Primary Output:** File handling logic that respects `TMPDIR`, avoids unsafe temp file creation, and does not rely on writable `/usr` or `/etc` for internal state.
- **Secondary Outputs (if any):**
  - Documentation of environment variables and options controlling file locations.
  - Tests or scripts demonstrating safe behavior under constrained filesystem permissions.

### Pattern: Streaming I/O for Large Files

**Goal**  
- Enable utilities to process arbitrarily large files without exhausting memory or imposing artificial size limits.

**When to Use**  
- The program operates on files or streams that may be larger than available memory (e.g., `cat`, `tail`, line-based processors).
- Input size is unbounded or user-controlled.
- The tool’s primary operations are line-based or stream-oriented.

**Required Inputs**  
- Description of the program’s core operations and whether they can be expressed in terms of streaming or line-by-line processing.
- Expected maximum input sizes and performance constraints.
- Any requirements for random access versus sequential processing.

**Workflow Steps**  
1. Analyze the algorithm to determine whether it can be expressed as streaming or line-by-line processing rather than whole-file operations.
2. Replace whole-file reads with buffered or line-based I/O, keeping only the minimal necessary state (e.g., a single line or sliding window) in memory at any time.
3. Ensure data structures used for per-input-item bookkeeping are dynamically sized rather than pre-limited, while still avoiding unbounded growth where not needed.
4. For operations that inherently require full-file context (e.g., building complex indices), accept that memory use may scale but still handle `malloc` failures as fatal errors.
5. Test behavior with inputs significantly larger than physical memory to confirm no artificial limits or unexpected failures appear.
6. Document any inherent limitations clearly (e.g., maximum supported line length if truly unavoidable) and justify them.

**Expected Outputs**  
- **Primary Output:** Stream-oriented I/O implementation that can handle very large files without arbitrary size limits.
- **Secondary Outputs (if any):**
  - Performance notes or benchmarks demonstrating behavior on large inputs.
  - Tests exercising large-file scenarios and verifying correctness and stability.

## Section 3: Failure Modes & Self-Check Checklist

### 3.1 Common Failure Modes

- Tends to hard-code arbitrary limits on line length, filename size, or number of items. This causes silent truncation or refusal to process valid user data.
- Often emits ad-hoc error messages lacking program name, file, or system error text. This leads to confusing logs and makes debugging and automation difficult.
- Frequently formats diagnostics inconsistently (missing colons, 0-based positions, capitalized messages, trailing periods). This results in tools and users misparsing or misinterpreting errors.
- Sometimes changes behavior based on the executable name or whether output is a TTY. This creates surprising differences when tools are symlinked, renamed, or used in scripts.
- Can treat `/usr` or `/etc` as writable locations for internal state. This produces failures or permission errors on systems where these directories are read-only.
- Often creates temporary files directly in `/tmp` without `O_EXCL` or `mktemp`-style safety. This results in race conditions, clobbered files, or security vulnerabilities.
- Tends to read entire input files into memory for stream-like tools. This causes crashes or unusable performance when handling very large files.
- Often omits `--help` and `--version` or uses nonstandard long option names. This leads to an inconsistent user experience compared to other GNU utilities.

### 3.2 Hard Constraints / Never-Do Rules

- Never silently truncate input or drop characters (including NULs) for convenience. This prevents subtle data corruption and user surprise.
- Never encode raw error counts or large numeric values directly into exit statuses. This avoids 8-bit wraparound hiding failures as successes.
- Always check the result of system calls and memory allocations before using their outputs. This ensures errors are caught early and reported explicitly.
- Always include program name, relevant file, and system error text in noninteractive error messages. This ensures logs and diagnostics remain actionable.
- Always honor `TMPDIR` and use race-safe creation when making temporary files. This protects against security issues and respects user configuration.
- Always support GNU-style `--help` and `--version` options with consistent semantics. This guarantees minimum discoverability of behavior and versioning.

### 3.3 Pre-Response Self-Check Checklist

- [ ] Have I avoided arbitrary limits on input sizes and preserved all input bytes, including NUL and nonprinting characters?
- [ ] Are error messages formatted with the correct `program[:file[:line[:column]]]` structure, 1-based positions, lowercase starts, and no trailing periods where required?
- [ ] Have I used `getopt_long` (or equivalent) with consistent short and long options, including standard `--help` and `--version` handling?
- [ ] Does the program behave consistently regardless of executable name and output device type, except for documented binary-output safeguards?
- [ ] Are temporary, lock, and auxiliary files created securely, honoring `TMPDIR` and avoiding unsafe patterns like non-`O_EXCL` creation in world-writable directories?
- [ ] Does the implementation process large files using streaming or line-based I/O where appropriate instead of loading entire files into memory?
- [ ] Have I ensured that `/usr` and `/etc` are treated as read-only for internal state, except where configuration updates are explicitly requested?
- [ ] If the program discovers its executable or associated files, have I provided environment variables or configuration to override those heuristics?
- [ ] Is the CLI (options, long option names, outputs) consistent with other GNU utilities in similar domains?
- [ ] Would a knowledgeable GNU user find the tool’s behavior, diagnostics, and file usage unsurprising and robust in typical and edge-case scenarios?