# How to Use the CLI Tools Skill

This skill provides expert assistance for building command-line interface (CLI) applications using Node.js/TypeScript and popular CLI frameworks.

## When to Use This Skill

Use the `cli-tools` skill when you need help with:

- Building a new CLI application from scratch
- Adding interactive prompts to your CLI
- Implementing argument parsing and validation
- Creating beautiful terminal output with colors and formatting
- Building progress bars and loading indicators
- Setting up configuration management
- Adding error handling to CLI tools
- Publishing CLI tools to npm
- Testing CLI applications

## How to Invoke

### Method 1: Explicit Invocation

Use the `@cli-tools` mention to explicitly invoke this skill:

```
@cli-tools I need to build a CLI tool that deploys applications to AWS.
It should have commands for init, deploy, and rollback. Can you help me get started?
```

### Method 2: Automatic Detection

Claude will automatically activate this skill when you mention CLI-related keywords:

```
I want to create a command-line tool using Commander.js that has
interactive prompts for user input.
```

Keywords that trigger this skill:
- CLI, command-line, terminal
- Commander.js, Inquirer, Chalk, Ora
- Argument parsing, flags, options
- Interactive prompts, progress bars
- Terminal UI, console output

## Usage Examples

### Example 1: Create a Basic CLI Application

**Request:**
```
@cli-tools Create a basic CLI application using Commander.js with TypeScript.
The CLI should have:
- A "create" command that scaffolds a new project
- A "build" command that compiles the project
- Both commands should show progress with spinners
```

**Response:** The skill will provide complete TypeScript code with Commander.js setup, command definitions, and Ora spinners.

---

### Example 2: Add Interactive Prompts

**Request:**
```
@cli-tools I need to add an interactive wizard to my CLI that asks users for:
1. Project name (required)
2. Framework choice (React, Vue, Angular)
3. TypeScript support (yes/no)
4. Install dependencies (yes/no)

Use Inquirer.js for the prompts.
```

**Response:** The skill will provide Inquirer.js code with proper validation and prompt types.

---

### Example 3: Configuration Management

**Request:**
```
@cli-tools Show me how to implement configuration management for my CLI tool.
It should support:
- Config file (~/.myapprc.json)
- Environment variables
- Command-line flags (highest priority)
```

**Response:** The skill will provide a ConfigManager class that handles multiple config sources with proper precedence.

---

### Example 4: Beautiful Terminal Output

**Request:**
```
@cli-tools I need to display a list of servers in a nice table format with colors.
The table should show: Name, Status (green if active, red if down), IP, and Uptime.
```

**Response:** The skill will provide code using cli-table3 and Chalk for formatted, colorful output.

---

### Example 5: Error Handling

**Request:**
```
@cli-tools What's the best way to handle errors in a CLI application?
I want meaningful error messages and proper exit codes.
```

**Response:** The skill will provide error handling patterns with custom error classes and exit code conventions.

---

### Example 6: Progress Indicators

**Request:**
```
@cli-tools I'm building a CLI that processes 1000 files.
How can I show progress to the user?
```

**Response:** The skill will provide examples of both spinners (for indeterminate progress) and progress bars (for determinate progress).

---

### Example 7: Publishing to npm

**Request:**
```
@cli-tools How do I package and publish my CLI tool to npm so users can install it globally?
```

**Response:** The skill will provide package.json configuration, build scripts, and publishing steps.

---

## Sample Workflows

### Building a Deployment CLI

```
Step 1: @cli-tools Create the basic CLI structure with Commander.js

Step 2: @cli-tools Add an "init" command that creates a config file

Step 3: @cli-tools Add a "deploy" command with environment selection and confirmation prompt

Step 4: @cli-tools Add progress indicators for the deployment process

Step 5: @cli-tools Add error handling and meaningful error messages

Step 6: @cli-tools Help me set up the package.json for npm publishing
```

### Adding Features to Existing CLI

```
@cli-tools I have an existing CLI built with Commander.js.
I want to add:
1. An interactive config wizard
2. Color-coded output (errors in red, success in green)
3. A progress bar when processing multiple files
4. Better error messages with suggestions

Here's my current code: [paste code]
```

## Tips for Best Results

1. **Be specific about your CLI framework**: Mention if you're using Commander.js, Yargs, or building from scratch
2. **Describe the user experience**: Explain what you want users to see in the terminal
3. **Mention your tech stack**: TypeScript vs JavaScript, Node.js version, etc.
4. **Share existing code**: If adding to an existing CLI, share relevant code for context
5. **Specify your use case**: Deployment tool, code generator, file processor, etc.

## What This Skill Covers

### Frameworks & Libraries
- Commander.js - Command and argument parsing
- Inquirer.js - Interactive prompts
- Chalk - Terminal string styling
- Ora - Spinners
- cli-progress - Progress bars
- cli-table3 - Table formatting
- Yargs - Alternative argument parser
- Oclif - CLI framework

### CLI Concepts
- Argument parsing (flags, options, subcommands)
- Interactive prompts and wizards
- Configuration management (files, env vars, flags)
- Terminal output formatting
- Error handling and exit codes
- Progress indicators
- Testing CLI applications
- Publishing to npm
- Shell completions

### Best Practices
- POSIX conventions
- User experience design
- Error messaging
- Composability and piping
- Testing strategies
- Documentation (--help, man pages)

## Integration with Other Skills

This skill works well with:

- **TypeScript/JavaScript skills** - For general coding help
- **Testing skills** - For writing CLI tests
- **DevOps skills** - For deployment and CI/CD CLIs
- **Package management skills** - For npm publishing

## Common Questions

**Q: Should I use Commander.js or Yargs?**
A: Commander.js is more popular and has better TypeScript support. Yargs has more features for complex CLIs. This skill covers both.

**Q: How do I make my CLI available globally?**
A: Set up the `bin` field in package.json and publish to npm. Users can then install with `npm install -g your-package`.

**Q: Can I build CLIs with Python?**
A: This skill focuses on Node.js/TypeScript CLIs. For Python, use the Click or argparse libraries (not covered by this skill).

**Q: How do I test interactive prompts?**
A: Use Inquirer's testing utilities or mock stdin/stdout. This skill includes testing examples.

---

**Need help?** Just mention `@cli-tools` with your question or describe what you're trying to build!
