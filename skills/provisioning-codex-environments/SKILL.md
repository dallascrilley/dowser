---
name: provisioning-codex-environments
short_description: >-
  Generate setup.sh and maintenance.sh scripts for OpenAI Codex cloud
  environments with auto-detected dependencies.
description: >-
  Generate Codex-compatible setup and maintenance scripts for any repository.
  Use when creating provisioning scripts for OpenAI Codex cloud environments,
  setting up development environments, or configuring language runtimes and
  dependencies. Automatically detects languages, package managers, testing
  frameworks, and linters to generate optimal setup.sh and maintenance.sh
  scripts that work with the codex-universal base image.
when_to_use: >-
  When creating Codex provisioning scripts, setting up cloud dev environments,
  or configuring multi-language project dependencies.
version: 1.0.0
category: cloud-and-infra
---

# Codex Provisioning Script Generator

Generate production-ready setup and maintenance scripts for OpenAI Codex cloud environments. This skill analyzes any repository and produces shell scripts that correctly initialize language runtimes, install dependencies, and configure development tools.

## Quick Start

Generate provisioning scripts for the current directory:

```bash
# Inspect repository and generate both scripts
python scripts/inspect_repo.py . --json > analysis.json
python scripts/generate_scripts.py analysis.json --both
```

This produces:
- `setup.sh` - Runs during environment provisioning
- `maintenance.sh` - Runs when resuming from cache

## When to Use This Skill

Use this skill when you need to:
- Create Codex provisioning scripts for a new project
- Set up a development environment in Codex cloud
- Configure multi-language projects with proper dependencies
- Ensure consistent environment setup across team members
- Update provisioning scripts after adding new dependencies or tools

## Workflow

### Step 1: Inspect the Repository

Run the inspection script to detect languages, package managers, and tools:

```bash
python scripts/inspect_repo.py /path/to/repo
```

This produces a human-readable report showing detected:
- Programming languages (Python, Node.js, Go, Rust, etc.)
- Package managers (poetry, npm, cargo, bundler, etc.)
- Test frameworks (pytest, jest, go test, etc.)
- Linters and formatters (ruff, eslint, clippy, etc.)

For JSON output (required for script generation):

```bash
python scripts/inspect_repo.py /path/to/repo --json > analysis.json
```

### Step 2: Generate Scripts

Generate setup and maintenance scripts from the analysis:

```bash
# Generate both scripts
python scripts/generate_scripts.py analysis.json --both

# Or generate individually
python scripts/generate_scripts.py analysis.json --setup
python scripts/generate_scripts.py analysis.json --maintenance
```

### Step 3: Review and Customize

Review the generated scripts:
- **setup.sh**: Installs all dependencies during provisioning
- **maintenance.sh**: Updates dependencies when resuming from cache

Customize as needed:
- Add environment variable exports to `~/.bashrc` for persistence
- Install additional tools not detected automatically
- Add project-specific setup steps
- Configure custom build or test commands

### Step 4: Deploy to Codex

Copy the scripts to your Codex environment settings:
1. Open Codex settings → Environments
2. Paste setup.sh content into "Setup script" field
3. Paste maintenance.sh content into "Maintenance script" field
4. Configure environment variables (CODEX_ENV_*_VERSION) if needed

## Script Features

### Automatic Language Detection

The generated scripts support these languages:
- **Python**: pyenv, poetry, pipenv, uv, pip
- **Node.js**: nvm, npm, yarn, pnpm, bun
- **Go**: go modules
- **Rust**: cargo, rustup
- **Ruby**: bundler, rbenv
- **PHP**: composer
- **Swift**: Swift Package Manager
- **Java**: maven, gradle
- **Elixir**: mix, hex

### Smart Dependency Management

**Setup script** (runs during provisioning):
- Detects package managers from lockfiles
- Installs all dependencies with appropriate tools
- Configures language versions via CODEX_ENV_* variables
- Sets up linters and formatters
- Handles multiple package managers in one project

**Maintenance script** (runs from cache):
- Only updates dependencies if lockfiles changed
- Fast and idempotent
- Verifies environment integrity
- Recovers from stale caches

### Error Handling

All generated scripts use:
- `set -euo pipefail` for strict error handling
- Clear progress logging with emoji markers
- Conditional checks before installing (idempotent)
- Graceful handling of missing files

## Advanced Usage

### Multi-Language Projects

For projects using multiple languages:

```bash
# Example: Python + Node.js + Go project
python scripts/inspect_repo.py . --json > analysis.json
python scripts/generate_scripts.py analysis.json --both
```

The generated scripts will:
1. Install Python dependencies (poetry/pip)
2. Install Node.js dependencies (npm/yarn/pnpm)
3. Download Go modules
4. Configure all necessary toolchains

### Custom Environment Variables

Pass environment variables to control runtime versions:

```bash
# In Codex environment settings, set:
CODEX_ENV_PYTHON_VERSION=3.13
CODEX_ENV_NODE_VERSION=20
CODEX_ENV_RUST_VERSION=1.86.0
```

The setup script will automatically configure these versions.

### Adding Custom Steps

After generation, customize the scripts:

```bash
# Add to setup.sh after language setup:
echo "\n🔧 Custom project setup..."
# Install custom tools
pip install --break-system-packages custom-tool
# Build project-specific assets
npm run build:assets
# Create required directories
mkdir -p data/cache logs
```

### Handling Edge Cases

For projects with non-standard structure:

1. Run inspection to get baseline analysis
2. Manually edit analysis.json to add missing items:
   ```json
   {
     "languages": ["python", "javascript"],
     "package_managers": {
       "poetry": ["pyproject.toml"],
       "npm": ["package.json"]
     },
     "test_frameworks": ["pytest", "jest"],
     "linters": ["ruff", "eslint"]
   }
   ```
3. Generate scripts with modified analysis

## Common Patterns

### Python Project with Poetry

```bash
# Detection finds: poetry, pytest, ruff, mypy
# Generated setup.sh includes:
poetry install
```

### Node.js Project with pnpm

```bash
# Detection finds: pnpm, vitest, eslint, prettier
# Generated setup.sh includes:
pnpm install
```

### Monorepo with Multiple Languages

```bash
# Detection finds: Python + Node.js + Go
# Generated scripts handle all three:
poetry install     # Python
pnpm install      # Node.js
go mod download   # Go
```

### Rust Project with Clippy

```bash
# Detection finds: cargo, clippy, rustfmt
# Generated setup.sh includes:
cargo fetch
# clippy and rustfmt already in base image
```

## Output Format

When using this skill directly (not via scripts), output provisioning scripts using XML format:

```xml
<provisioning_scripts>
  <setup><![CDATA[
#!/bin/bash
set -euo pipefail
# ... generated setup script content ...
  ]]></setup>

  <maintenance><![CDATA[
#!/bin/bash
set -euo pipefail
# ... generated maintenance script content ...
  ]]></maintenance>
</provisioning_scripts>
```

## Troubleshooting

### Scripts not detecting package manager

Run inspection manually and check analysis.json:
```bash
python scripts/inspect_repo.py . --json | jq .package_managers
```

If missing, ensure lockfiles are present:
- Python: `poetry.lock`, `Pipfile.lock`, or `requirements.txt`
- Node: `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`
- Rust: `Cargo.lock`
- Go: `go.sum`

### Dependencies not installing

Check that:
1. Lockfiles are committed to repository
2. Package manager is available in codex-universal base image
3. Internet access is enabled during setup phase

### Environment variables not persisting

Add exports to `~/.bashrc` in setup script:
```bash
echo 'export MY_VAR="value"' >> ~/.bashrc
```

## Additional Resources

- **references/codex_environment.md**: Complete Codex environment reference
  - Pre-installed tools and versions
  - Environment lifecycle details
  - Network access configuration
  - Best practices for script authoring
