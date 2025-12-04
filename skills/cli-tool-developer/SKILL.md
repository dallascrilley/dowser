---
name: cli-tool-developer
short_description: >-
  Build command-line tools in Node.js/TypeScript and Python with argument
  parsing, interactive prompts, terminal UI, and frameworks like Commander.js,
  Click, Typer.
description: >-
  Expert assistance for building command-line interface (CLI) applications with
  Node.js/TypeScript and Python, including argument parsing, interactive
  prompts, terminal UI, progress indicators, and CLI frameworks like
  Commander.js, Inquirer, Chalk, Ora (Node.js) and Click, Typer, Argparse,
  Cement, Cliff (Python).
keywords: >-
  cli, command-line, terminal, commander, inquirer, chalk, ora, click, typer,
  argparse, cement, cliff, python cli, nodejs cli, typescript cli,
  argument-parsing, interactive-prompts, terminal-ui
when_to_use: >
  Use when building CLI applications in Node.js/TypeScript or Python,
  implementing argument parsing, creating interactive prompts,

  building terminal UIs with colors/formatting, implementing progress
  indicators, or using CLI frameworks (Commander.js, Click, Typer).
version: 1.0.0
category: coding
---

# CLI Tool Development Skill

You are a CLI tool development expert with knowledge of building command-line applications, argument parsing, and terminal user interfaces in both Node.js/TypeScript and Python ecosystems.

## Core Capabilities

- Build interactive CLI applications in Node.js/TypeScript and Python
- Implement argument parsing and validation
- Create beautiful terminal UIs with colors and formatting
- Build progress bars and loading indicators
- Implement configuration management
- Create interactive prompts and menus
- Build CLI tools with Commander.js, Yargs (Node.js) or Click, Typer, Argparse, Cement, Cliff (Python)
- Implement proper error handling and help messages
- Create installable CLI packages
- Add shell completions and man pages

## Best Practices

- Provide clear help messages and documentation
- Follow POSIX conventions for arguments
- Use colors and formatting for better UX
- Implement --version and --help flags
- Provide meaningful error messages
- Show progress for long-running operations
- Allow configuration via files and env variables
- Make commands composable and scriptable
- Follow the principle of least surprise
- Test CLI tools thoroughly

---

# Node.js/TypeScript CLI Development

## Code Patterns

### CLI with Commander.js

```typescript
#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';

const program = new Command();

program
  .name('myapp')
  .description('A powerful CLI tool')
  .version('1.0.0');

program
  .command('init')
  .description('Initialize a new project')
  .option('-t, --template <type>', 'project template', 'basic')
  .action(async (options) => {
    const spinner = ora('Initializing project...').start();

    try {
      await initializeProject(options.template);
      spinner.succeed(chalk.green('Project initialized successfully!'));
    } catch (error) {
      spinner.fail(chalk.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

program
  .command('deploy')
  .description('Deploy the application')
  .option('-e, --environment <env>', 'deployment environment', 'production')
  .action(async (options) => {
    const answers = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'confirm',
        message: `Deploy to ${options.environment}?`,
        default: false,
      },
    ]);

    if (answers.confirm) {
      console.log(chalk.blue(`Deploying to ${options.environment}...`));
      // Deploy logic
    }
  });

program.parse();
```

### Interactive Prompts

```typescript
import inquirer from 'inquirer';
import chalk from 'chalk';

export async function setupWizard() {
  console.log(chalk.bold.blue('\nWelcome to the Setup Wizard!\n'));

  const answers = await inquirer.prompt([
    {
      type: 'input',
      name: 'projectName',
      message: 'Project name:',
      validate: (input) => input.length > 0 || 'Project name is required',
    },
    {
      type: 'list',
      name: 'framework',
      message: 'Choose a framework:',
      choices: ['React', 'Vue', 'Angular', 'Svelte'],
    },
    {
      type: 'checkbox',
      name: 'features',
      message: 'Select features:',
      choices: [
        { name: 'TypeScript', checked: true },
        { name: 'ESLint', checked: true },
        { name: 'Testing', checked: false },
        { name: 'CI/CD', checked: false },
      ],
    },
    {
      type: 'confirm',
      name: 'installDeps',
      message: 'Install dependencies now?',
      default: true,
    },
  ]);

  return answers;
}
```

### Progress Indicators

```typescript
import ora from 'ora';
import chalk from 'chalk';
import cliProgress from 'cli-progress';

// Spinner for indeterminate progress
export async function runWithSpinner(message: string, task: () => Promise<void>) {
  const spinner = ora(message).start();

  try {
    await task();
    spinner.succeed(chalk.green('Done!'));
  } catch (error) {
    spinner.fail(chalk.red(`Failed: ${error.message}`));
    throw error;
  }
}

// Progress bar for determinate progress
export async function processWithProgress(items: any[]) {
  const progressBar = new cliProgress.SingleBar({
    format: 'Progress |{bar}| {percentage}% | {value}/{total} items',
    barCompleteChar: '\u2588',
    barIncompleteChar: '\u2591',
  });

  progressBar.start(items.length, 0);

  for (let i = 0; i < items.length; i++) {
    await processItem(items[i]);
    progressBar.update(i + 1);
  }

  progressBar.stop();
}
```

### Configuration Management

```typescript
import { cosmiconfigSync } from 'cosmiconfig';
import { readFileSync, writeFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

export interface Config {
  apiKey?: string;
  defaultEnvironment?: string;
  verbose?: boolean;
}

export class ConfigManager {
  private configPath: string;
  private config: Config;

  constructor(appName: string) {
    this.configPath = join(homedir(), `.${appName}rc.json`);
    this.config = this.loadConfig();
  }

  private loadConfig(): Config {
    // Try to load from config file
    const explorer = cosmiconfigSync(appName);
    const result = explorer.search();

    if (result) {
      return result.config;
    }

    // Load from env variables
    return {
      apiKey: process.env.API_KEY,
      defaultEnvironment: process.env.DEFAULT_ENV || 'production',
      verbose: process.env.VERBOSE === 'true',
    };
  }

  get(key: keyof Config): any {
    return this.config[key];
  }

  set(key: keyof Config, value: any): void {
    this.config[key] = value;
    this.save();
  }

  private save(): void {
    writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
  }
}
```

### Error Handling

```typescript
import chalk from 'chalk';

export class CLIError extends Error {
  constructor(message: string, public exitCode: number = 1) {
    super(message);
    this.name = 'CLIError';
  }
}

export function handleError(error: Error): never {
  if (error instanceof CLIError) {
    console.error(chalk.red(`Error: ${error.message}`));
    process.exit(error.exitCode);
  }

  console.error(chalk.red('An unexpected error occurred:'));
  console.error(chalk.red(error.stack || error.message));
  process.exit(1);
}

// Use in your CLI
process.on('uncaughtException', handleError);
process.on('unhandledRejection', handleError);
```

### Table Output

```typescript
import Table from 'cli-table3';
import chalk from 'chalk';

export function displayTable(data: any[]) {
  const table = new Table({
    head: [
      chalk.cyan('Name'),
      chalk.cyan('Status'),
      chalk.cyan('Version'),
      chalk.cyan('Updated'),
    ],
    colWidths: [20, 15, 15, 20],
  });

  data.forEach((item) => {
    table.push([
      item.name,
      item.status === 'active' ? chalk.green(item.status) : chalk.yellow(item.status),
      item.version,
      item.updated,
    ]);
  });

  console.log(table.toString());
}
```

### Package.json Setup

```json
{
  "name": "my-cli-tool",
  "version": "1.0.0",
  "description": "A powerful CLI tool",
  "bin": {
    "myapp": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "ts-node src/index.ts",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["cli", "tool"],
  "dependencies": {
    "commander": "^11.0.0",
    "inquirer": "^9.2.0",
    "chalk": "^5.3.0",
    "ora": "^7.0.0",
    "cli-progress": "^3.12.0",
    "cli-table3": "^0.6.3",
    "cosmiconfig": "^9.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/inquirer": "^9.0.0",
    "typescript": "^5.0.0",
    "ts-node": "^10.9.0"
  }
}
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Testing CLI Tools

```typescript
import { execSync } from 'child_process';
import { describe, it, expect } from 'vitest';

describe('CLI Tool', () => {
  it('should display version', () => {
    const output = execSync('node dist/index.js --version').toString();
    expect(output).toContain('1.0.0');
  });

  it('should display help', () => {
    const output = execSync('node dist/index.js --help').toString();
    expect(output).toContain('Usage:');
  });

  it('should execute init command', () => {
    const output = execSync('node dist/index.js init --template basic').toString();
    expect(output).toContain('initialized successfully');
  });
});
```

## Node.js Resources

- [Commander.js](https://github.com/tj/commander.js) - Complete solution for Node.js command-line interfaces
- [Inquirer.js](https://github.com/SBoudrias/Inquirer.js) - Collection of common interactive command line user interfaces
- [Chalk](https://github.com/chalk/chalk) - Terminal string styling
- [Ora](https://github.com/sindresorhus/ora) - Elegant terminal spinner
- [cli-progress](https://github.com/npkgz/cli-progress) - Easy to use progress bars
- [cli-table3](https://github.com/cli-table/cli-table3) - Pretty unicode tables
- [cosmiconfig](https://github.com/cosmiconfig/cosmiconfig) - Find and load configuration
- [Yargs](https://github.com/yargs/yargs) - Alternative argument parser
- [Oclif](https://oclif.io/) - Framework for building CLIs

## Publishing Your Node.js CLI

1. **Test locally**: `npm link` to test your CLI globally
2. **Build**: `npm run build` to compile TypeScript
3. **Version**: `npm version [major|minor|patch]`
4. **Publish**: `npm publish` to make it available on npm
5. **Distribution**: Users can install with `npm install -g your-cli-tool`

---

# Python CLI Frameworks

Python offers a rich ecosystem of CLI frameworks ranging from lightweight built-in modules to enterprise-grade frameworks with plugin architectures.

## Python Framework Comparison

| Framework   | Notable Features                                    | Typical Use Case              | Dependencies |
|-------------|-----------------------------------------------------|-------------------------------|--------------|
| **Click**   | Flexible, decorator-based, rich UX, composable      | Most command-line tools       | Minimal      |
| **Typer**   | Type hints, auto-docs, easy onboarding, modern      | Modern CLIs, rapid prototyping| Click-based  |
| **Argparse**| Built-in, minimal dependencies, simple interfaces   | Scripts and small utilities   | None (stdlib)|
| **Cement**  | Modular, plugins, controller-based, enterprise-ready| Large, complex CLIs           | Moderate     |
| **Cliff**   | Command hierarchies, extensible commands            | Structured CLI suites         | cmd2, stevedore|

## Click - Decorator-Based CLI Framework

Click is the gold standard for Python CLI tools, offering a flexible decorator-based approach with excellent UX.

```python
#!/usr/bin/env python3
import click
from typing import Optional

@click.group()
@click.version_option(version='1.0.0')
@click.pass_context
def cli(ctx):
    """A powerful CLI tool built with Click."""
    ctx.ensure_object(dict)

@cli.command()
@click.option('--template', '-t', default='basic', help='Project template')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def init(template: str, verbose: bool):
    """Initialize a new project."""
    click.echo(click.style(f'Initializing project with template: {template}', fg='green'))

    with click.progressbar(range(100), label='Setting up project') as bar:
        for i in bar:
            # Simulate work
            pass

    click.echo(click.style('✓ Project initialized successfully!', fg='green', bold=True))

@cli.command()
@click.option('--environment', '-e', default='production',
              type=click.Choice(['dev', 'staging', 'production']))
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
def deploy(environment: str, force: bool):
    """Deploy the application."""
    if not force:
        if not click.confirm(f'Deploy to {environment}?'):
            click.echo('Deployment cancelled.')
            return

    with click.progressbar(length=100, label=f'Deploying to {environment}') as bar:
        for i in range(100):
            bar.update(1)
            # Simulate deployment

    click.echo(click.style(f'✓ Deployed to {environment}!', fg='green'))

@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', type=click.File('w'), default='-')
def process(files, output):
    """Process one or more files."""
    for filename in files:
        click.echo(f'Processing {filename}...', file=output)
        # Process file logic

if __name__ == '__main__':
    cli()
```

### Click Features

- **Decorators**: Clean syntax with `@click.command()`, `@click.option()`, `@click.argument()`
- **Type validation**: Built-in types (INT, FLOAT, STRING, PATH, FILE, CHOICE)
- **Progress bars**: `click.progressbar()` for long operations
- **Styled output**: `click.style()` for colors and formatting
- **Nested commands**: Command groups for complex CLIs
- **Testing support**: `CliRunner` for automated testing

```python
# Testing Click CLIs
from click.testing import CliRunner

def test_init_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['init', '--template', 'basic'])
    assert result.exit_code == 0
    assert 'initialized successfully' in result.output
```

## Typer - Type Hints for Modern CLIs

Typer builds on Click, using Python type hints for automatic validation and documentation generation.

```python
#!/usr/bin/env python3
import typer
from typing import Optional, List
from enum import Enum
from pathlib import Path

app = typer.Typer(help="A modern CLI tool built with Typer")

class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    production = "production"

class Framework(str, Enum):
    react = "react"
    vue = "vue"
    angular = "angular"
    svelte = "svelte"

@app.command()
def init(
    project_name: str = typer.Argument(..., help="Name of the project"),
    framework: Framework = typer.Option(Framework.react, help="Framework to use"),
    typescript: bool = typer.Option(True, help="Use TypeScript"),
    install_deps: bool = typer.Option(True, help="Install dependencies"),
):
    """Initialize a new project with the specified configuration."""
    typer.echo(f"Creating project: {project_name}")
    typer.echo(f"Framework: {framework.value}")
    typer.echo(f"TypeScript: {typescript}")

    with typer.progressbar(range(100), label="Setting up project") as progress:
        for value in progress:
            # Simulate work
            pass

    typer.secho("✓ Project initialized successfully!", fg=typer.colors.GREEN, bold=True)

@app.command()
def deploy(
    environment: Environment = typer.Option(Environment.production, help="Deployment environment"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    config_file: Optional[Path] = typer.Option(None, help="Config file path"),
):
    """Deploy the application to the specified environment."""
    if not force:
        confirm = typer.confirm(f"Deploy to {environment.value}?")
        if not confirm:
            typer.echo("Deployment cancelled.")
            raise typer.Abort()

    typer.echo(f"Deploying to {environment.value}...")

    if config_file:
        typer.echo(f"Using config: {config_file}")

    typer.secho(f"✓ Deployed to {environment.value}!", fg=typer.colors.GREEN)

@app.command()
def process(
    files: List[Path] = typer.Argument(..., help="Files to process"),
    output: Optional[Path] = typer.Option(None, help="Output file"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Process one or more files."""
    for file in files:
        if verbose:
            typer.echo(f"Processing {file}...")
        # Process file logic

    if output:
        typer.echo(f"Results saved to {output}")

if __name__ == "__main__":
    app()
```

### Typer Features

- **Type hints**: Automatic validation from type annotations
- **Auto-completion**: Shell completion for bash, zsh, fish
- **Auto-documentation**: Help text generated from docstrings and type hints
- **Enums**: Type-safe choices with Python enums
- **Path validation**: Built-in `Path` type with existence checking
- **Testing**: Uses Click's testing utilities

```python
# Testing Typer CLIs
from typer.testing import CliRunner

runner = CliRunner()

def test_init():
    result = runner.invoke(app, ["init", "myproject", "--framework", "react"])
    assert result.exit_code == 0
    assert "initialized successfully" in result.output
```

## Argparse - Built-in Python CLI Framework

Argparse is Python's standard library solution for CLI argument parsing - zero dependencies, perfect for simple scripts.

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog='myapp',
        description='A simple CLI tool using argparse',
        epilog='Thanks for using myapp!'
    )

    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument(
        '--template', '-t',
        choices=['basic', 'advanced', 'minimal'],
        default='basic',
        help='Project template'
    )
    init_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy application')
    deploy_parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'staging', 'production'],
        default='production',
        help='Deployment environment'
    )
    deploy_parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation'
    )

    # Process command
    process_parser = subparsers.add_parser('process', help='Process files')
    process_parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        help='Files to process'
    )
    process_parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file'
    )

    return parser

def cmd_init(args):
    """Handle init command."""
    print(f"Initializing project: {args.name}")
    print(f"Template: {args.template}")

    if args.verbose:
        print("Running in verbose mode...")

    # Initialization logic
    print("✓ Project initialized successfully!")

def cmd_deploy(args):
    """Handle deploy command."""
    if not args.force:
        response = input(f"Deploy to {args.environment}? [y/N] ")
        if response.lower() != 'y':
            print("Deployment cancelled.")
            return

    print(f"Deploying to {args.environment}...")
    # Deployment logic
    print(f"✓ Deployed to {args.environment}!")

def cmd_process(args):
    """Handle process command."""
    for file in args.files:
        if not file.exists():
            print(f"Error: {file} does not exist", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {file}...")
        # Process file logic

    if args.output:
        print(f"Results saved to {args.output}")

def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Dispatch to command handlers
    commands = {
        'init': cmd_init,
        'deploy': cmd_deploy,
        'process': cmd_process,
    }

    commands[args.command](args)

if __name__ == '__main__':
    main()
```

### Argparse Features

- **Built-in**: No external dependencies
- **Subcommands**: `add_subparsers()` for command hierarchies
- **Type conversion**: Automatic type conversion with `type=` parameter
- **Validation**: `choices=` for restricted values
- **Actions**: `store_true`, `store_false`, `append`, `count`, etc.
- **Help generation**: Automatic `--help` generation

## Cement - Enterprise CLI Framework

Cement is a modular, plugin-based framework designed for large, complex CLI applications.

```python
#!/usr/bin/env python3
from cement import App, Controller, ex
from cement.core.exc import CaughtSignal
import sys

class BaseController(Controller):
    """Base controller for the application."""

    class Meta:
        label = 'base'
        description = 'A powerful CLI tool built with Cement'
        arguments = [
            (['-v', '--version'],
             {'action': 'version',
              'version': '1.0.0'}),
        ]

    @ex(
        help='show example output',
        arguments=[
            (['-f', '--foo'],
             {'help': 'notorious foo option',
              'action': 'store',
              'dest': 'foo'}),
        ],
    )
    def example(self):
        """Example command."""
        data = {'foo': self.app.pargs.foo}
        self.app.render(data, 'example.jinja2')

class ProjectController(Controller):
    """Project management controller."""

    class Meta:
        label = 'project'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(
        help='initialize a new project',
        arguments=[
            (['name'],
             {'help': 'project name',
              'action': 'store'}),
            (['-t', '--template'],
             {'help': 'project template',
              'action': 'store',
              'dest': 'template',
              'default': 'basic',
              'choices': ['basic', 'advanced', 'minimal']}),
        ],
    )
    def init(self):
        """Initialize a new project."""
        name = self.app.pargs.name
        template = self.app.pargs.template

        self.app.log.info(f'Initializing project: {name}')
        self.app.log.info(f'Template: {template}')

        # Initialization logic
        print(f'✓ Project {name} initialized successfully!')

    @ex(
        help='list all projects',
    )
    def list(self):
        """List all projects."""
        projects = ['project1', 'project2', 'project3']

        for project in projects:
            print(f'  - {project}')

class DeployController(Controller):
    """Deployment controller."""

    class Meta:
        label = 'deploy'
        stacked_type = 'nested'
        stacked_on = 'base'

    @ex(
        help='deploy application',
        arguments=[
            (['-e', '--environment'],
             {'help': 'deployment environment',
              'action': 'store',
              'dest': 'environment',
              'default': 'production',
              'choices': ['dev', 'staging', 'production']}),
            (['-f', '--force'],
             {'help': 'skip confirmation',
              'action': 'store_true',
              'dest': 'force'}),
        ],
    )
    def run(self):
        """Deploy the application."""
        env = self.app.pargs.environment
        force = self.app.pargs.force

        if not force:
            response = input(f'Deploy to {env}? [y/N] ')
            if response.lower() != 'y':
                print('Deployment cancelled.')
                return

        self.app.log.info(f'Deploying to {env}...')
        # Deployment logic
        print(f'✓ Deployed to {env}!')

class MyApp(App):
    """Main application class."""

    class Meta:
        label = 'myapp'
        handlers = [
            BaseController,
            ProjectController,
            DeployController,
        ]

def main():
    """Main entry point."""
    with MyApp() as app:
        try:
            app.run()
        except CaughtSignal as e:
            print(f'\n{e}')
            app.exit_code = 0

if __name__ == '__main__':
    main()
```

### Cement Features

- **Controllers**: Organize commands into logical controllers
- **Plugins**: Extensible plugin architecture
- **Configuration**: Multi-source config (files, env vars, CLI args)
- **Logging**: Built-in logging framework
- **Templates**: Jinja2 template rendering
- **Hooks**: Hook system for extending behavior
- **Extensions**: Rich extension ecosystem

## Cliff - Structured Command CLIs

Cliff (Command Line Interface Formulation Framework) provides a structured approach to building CLIs with command hierarchies.

```python
#!/usr/bin/env python3
import sys
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne

class InitCommand(Command):
    """Initialize a new project."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name', help='Project name')
        parser.add_argument(
            '--template', '-t',
            default='basic',
            choices=['basic', 'advanced', 'minimal'],
            help='Project template'
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.info(f'Initializing project: {parsed_args.name}')
        self.app.LOG.info(f'Template: {parsed_args.template}')

        # Initialization logic
        print(f'✓ Project {parsed_args.name} initialized successfully!')
        return 0

class DeployCommand(Command):
    """Deploy the application."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--environment', '-e',
            default='production',
            choices=['dev', 'staging', 'production'],
            help='Deployment environment'
        )
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Skip confirmation'
        )
        return parser

    def take_action(self, parsed_args):
        env = parsed_args.environment

        if not parsed_args.force:
            response = input(f'Deploy to {env}? [y/N] ')
            if response.lower() != 'y':
                print('Deployment cancelled.')
                return 0

        self.app.LOG.info(f'Deploying to {env}...')
        # Deployment logic
        print(f'✓ Deployed to {env}!')
        return 0

class ListProjects(Lister):
    """List all projects."""

    def take_action(self, parsed_args):
        columns = ('Name', 'Status', 'Version')
        data = [
            ('project1', 'active', '1.0.0'),
            ('project2', 'inactive', '0.9.0'),
            ('project3', 'active', '2.1.0'),
        ]
        return (columns, data)

class ShowProject(ShowOne):
    """Show project details."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name', help='Project name')
        return parser

    def take_action(self, parsed_args):
        return (
            ('Name', 'Status', 'Version', 'Created'),
            (parsed_args.name, 'active', '1.0.0', '2025-01-01'),
        )

class MyApp(App):
    """Main application class."""

    def __init__(self):
        super().__init__(
            description='A powerful CLI tool built with Cliff',
            version='1.0.0',
            command_manager=CommandManager('myapp.commands'),
        )

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug(f'prepare_to_run_command {cmd.__class__.__name__}')

    def clean_up(self, cmd, result, err):
        self.LOG.debug(f'clean_up {cmd.__class__.__name__}')

def main(argv=sys.argv[1:]):
    """Main entry point."""
    app = MyApp()

    # Register commands
    app.command_manager.add_command('init', InitCommand)
    app.command_manager.add_command('deploy', DeployCommand)
    app.command_manager.add_command('list', ListProjects)
    app.command_manager.add_command('show', ShowProject)

    return app.run(argv)

if __name__ == '__main__':
    sys.exit(main())
```

### Cliff Features

- **Command base classes**: `Command`, `Lister`, `ShowOne` for different output types
- **Structured output**: Automatic table formatting, JSON, YAML, CSV output
- **Command discovery**: Plugin-based command discovery
- **Logging**: Built-in logging configuration
- **Interactive mode**: Optional interactive shell
- **OpenStack integration**: Used by OpenStack CLI clients

## Python CLI Best Practices

### Setup.py / Pyproject.toml Configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='myapp',
    version='1.0.0',
    description='A powerful CLI tool',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'click>=8.0.0',
        'typer>=0.9.0',
        'rich>=13.0.0',  # For beautiful terminal output
    ],
    entry_points={
        'console_scripts': [
            'myapp=myapp.cli:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
```

```toml
# pyproject.toml (modern approach)
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "1.0.0"
description = "A powerful CLI tool"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
dependencies = [
    "click>=8.0.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
]

[project.scripts]
myapp = "myapp.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
]
```

### Rich Terminal Output

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Styled output
console.print("[bold green]Success![/bold green] Operation completed.")
console.print("[bold red]Error:[/bold red] Something went wrong.", style="red")

# Tables
table = Table(title="Projects")
table.add_column("Name", style="cyan")
table.add_column("Status", style="magenta")
table.add_column("Version", style="green")

table.add_row("project1", "active", "1.0.0")
table.add_row("project2", "inactive", "0.9.0")

console.print(table)

# Progress bars
for i in track(range(100), description="Processing..."):
    # Do work
    pass

# Panels
console.print(Panel("This is important information", title="Notice", border_style="blue"))

# Syntax highlighting
code = '''
def hello():
    print("Hello, World!")
'''
syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)
```

### Configuration with YAML/TOML

```python
import yaml
import tomli  # Python 3.11+ has tomllib built-in
from pathlib import Path

def load_config():
    """Load configuration from YAML or TOML."""
    config_file = Path.home() / '.myapp' / 'config.yaml'

    if not config_file.exists():
        return get_default_config()

    if config_file.suffix == '.yaml':
        with open(config_file) as f:
            return yaml.safe_load(f)
    elif config_file.suffix == '.toml':
        with open(config_file, 'rb') as f:
            return tomli.load(f)

    return get_default_config()

def get_default_config():
    """Return default configuration."""
    return {
        'api_key': None,
        'default_environment': 'production',
        'verbose': False,
    }
```

### Testing Python CLIs

```python
# test_cli.py
import pytest
from click.testing import CliRunner
from myapp.cli import cli

@pytest.fixture
def runner():
    return CliRunner()

def test_init_command(runner):
    result = runner.invoke(cli, ['init', '--template', 'basic'])
    assert result.exit_code == 0
    assert 'initialized successfully' in result.output

def test_deploy_with_force(runner):
    result = runner.invoke(cli, ['deploy', '--environment', 'production', '--force'])
    assert result.exit_code == 0
    assert 'Deployed to production' in result.output

def test_missing_required_argument(runner):
    result = runner.invoke(cli, ['init'])
    assert result.exit_code != 0
    assert 'Missing argument' in result.output
```

## Python Resources

- [Click](https://click.palletsprojects.com/) - Composable command line interface toolkit
- [Typer](https://typer.tiangolo.com/) - Modern CLI framework with type hints
- [Argparse](https://docs.python.org/3/library/argparse.html) - Parser for command-line options
- [Cement](https://builtoncement.com/) - Advanced CLI Application Framework
- [Cliff](https://docs.openstack.org/cliff/) - Command Line Interface Formulation Framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Python Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) - Interactive CLI building

## Publishing Python CLIs

### PyPI Distribution

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI
twine upload dist/*

# Users can then install with:
pip install myapp
```

### Entry Points

```python
# In setup.py or pyproject.toml
entry_points={
    'console_scripts': [
        'myapp=myapp.cli:main',
        'myapp-admin=myapp.admin:main',
    ],
}
```

After installation, `myapp` and `myapp-admin` are available as shell commands.

---

# Common CLI Patterns (Both Ecosystems)

## Subcommands

Group related commands under a parent command:

- `git commit`, `git push` - Git subcommands
- `docker run`, `docker build` - Docker subcommands
- `npm install`, `npm test` - npm subcommands

## Flags and Options

### Short and Long Flags

- Short: `-v`, `-h`, `-f`
- Long: `--verbose`, `--help`, `--force`
- Combined: `-vf` (verbose + force)

### Options with Values

- Short: `-o file.txt`, `-e production`
- Long: `--output=file.txt`, `--environment=production`
- Space-separated: `--output file.txt`

## Interactive Mode

Use interactive prompts when:
- User input is required but not provided
- Confirmation is needed for destructive operations
- Configuration wizard is appropriate

Fallback to non-interactive mode:
- When using `--force` or `--yes` flags
- In CI/CD environments (detect with `sys.stdin.isatty()` or `process.stdin.isTTY`)
- When piping input

## Piping and Composability

Support Unix philosophy - tools should work together:

```bash
# Read from stdin
cat file.txt | myapp process

# Write to stdout
myapp generate | tee output.txt

# Chain commands
myapp extract data.json | myapp transform | myapp load
```

**Implementation Tips**:
- Read from stdin when no file argument provided
- Write to stdout by default (use `-o` flag for file output)
- Use stderr for logs and progress (leaves stdout clean for piping)
- Support `--quiet` flag to suppress all output except results

## Exit Codes

Standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Misuse of command (invalid arguments)
- `130` - Terminated by Ctrl+C (SIGINT)

Custom exit codes:
- `10+` - Application-specific errors

**Node.js**:
```typescript
process.exit(0);  // Success
process.exit(1);  // Error
```

**Python**:
```python
sys.exit(0)  # Success
sys.exit(1)  # Error
```

## Configuration Hierarchy

Priority order (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Project config file (`.myapp.json` in current dir)
4. User config file (`~/.myapp/config.json`)
5. System config file (`/etc/myapp/config.json`)
6. Default values

## Environment Variables

**Naming convention**: `MYAPP_SETTING_NAME`

```bash
export MYAPP_API_KEY="secret"
export MYAPP_DEFAULT_ENV="production"
export MYAPP_VERBOSE="true"
```

**Node.js**:
```typescript
const apiKey = process.env.MYAPP_API_KEY;
```

**Python**:
```python
import os
api_key = os.environ.get('MYAPP_API_KEY')
```

## Version Management

Always provide a `--version` flag:

**Node.js**:
```typescript
program.version('1.0.0');
```

**Python Click**:
```python
@click.version_option(version='1.0.0')
```

**Python Typer**:
```python
app = typer.Typer(version='1.0.0')
```

## Shell Completions

### Node.js (Oclif)

```typescript
// Automatic completion support in Oclif
oclif.run(['autocomplete', 'bash']);
```

### Python (Click)

```python
# Enable completion
@click.group()
@click.option('--completion', is_flag=True, expose_value=False, help='Enable completion')
def cli():
    pass

# Install completion
# bash: _MYAPP_COMPLETE=bash_source myapp > ~/.myapp-complete.bash
# zsh: _MYAPP_COMPLETE=zsh_source myapp > ~/.myapp-complete.zsh
```

### Python (Typer)

```python
import typer

app = typer.Typer()

# Automatic completion support
# Install with: typer myapp.py utils docs --name myapp

if __name__ == "__main__":
    app()
```

---

# Framework Selection Guide

## Choose Node.js/TypeScript When:

- Building tools for web developers
- Integration with Node.js ecosystem (npm packages)
- TypeScript type safety is important
- Need rich NPM package ecosystem
- Desktop/mobile development teams (familiar with JS/TS)

**Recommended Stack**: Commander.js + Inquirer + Chalk + Ora

## Choose Python When:

- Data processing, scientific computing, ML/AI tools
- System administration, DevOps automation
- Cross-platform scripts with minimal dependencies
- Integration with Python ecosystem (data science, ML libraries)
- Backend/infrastructure teams (familiar with Python)

**Recommended Stack**:
- **Simple scripts**: Argparse (built-in, zero dependencies)
- **Modern CLIs**: Typer (type hints, auto-docs)
- **Complex CLIs**: Click (flexible, composable)
- **Enterprise CLIs**: Cement (modular, plugins)

## Framework Decision Tree

```
Start
├── Need built-in solution (no dependencies)?
│   ├── Node.js → Use built-in process.argv + minimist
│   └── Python → Use Argparse
│
├── Building simple CLI (1-5 commands)?
│   ├── Node.js → Commander.js
│   └── Python → Click or Typer
│
├── Building complex CLI (10+ commands, plugins)?
│   ├── Node.js → Oclif
│   └── Python → Cement or Cliff
│
└── Need rapid prototyping with type safety?
    ├── Node.js → Commander.js + TypeScript
    └── Python → Typer
```

---

# Cross-Platform Considerations

## Path Handling

**Node.js**:
```typescript
import { join, resolve } from 'path';
const configPath = join(process.env.HOME, '.myapp', 'config.json');
```

**Python**:
```python
from pathlib import Path
config_path = Path.home() / '.myapp' / 'config.json'
```

## Terminal Detection

**Node.js**:
```typescript
const isInteractive = process.stdin.isTTY && process.stdout.isTTY;
```

**Python**:
```python
import sys
is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
```

## Signal Handling

**Node.js**:
```typescript
process.on('SIGINT', () => {
    console.log('\nGracefully shutting down...');
    process.exit(0);
});
```

**Python**:
```python
import signal
import sys

def signal_handler(sig, frame):
    print('\nGracefully shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
```

---

**This skill provides comprehensive coverage of CLI development in both Node.js/TypeScript and Python ecosystems, with practical examples and best practices for building professional command-line tools.**
