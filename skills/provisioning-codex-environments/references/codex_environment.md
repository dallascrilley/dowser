# Codex Environment Reference

## Overview

The OpenAI Codex cloud environment uses the `codex-universal` base image, which comes pre-installed with common languages, packages, and tools.

## Pre-installed Languages & Tools

### Python
- **Tool**: pyenv
- **Versions**: 3.10, 3.11.12, 3.12, 3.13, 3.14.0
- **Default**: 3.12
- **Global packages**: poetry, uv, ruff, black, mypy, pyright, isort, pytest
- **Environment variable**: `CODEX_ENV_PYTHON_VERSION`

### Node.js
- **Tool**: nvm
- **Versions**: 18, 20, 22
- **Default**: 22
- **Global packages**: npm, yarn (via corepack), pnpm, prettier, eslint, typescript
- **Environment variable**: `CODEX_ENV_NODE_VERSION`

### Rust
- **Tool**: rustup
- **Versions**: 1.83.0, 1.84.1, 1.85.1, 1.86.0, 1.87.0
- **Default**: 1.87.0
- **Components**: rustfmt, clippy
- **Environment variable**: `CODEX_ENV_RUST_VERSION`

### Go
- **Tool**: mise
- **Versions**: 1.22.12, 1.23.8, 1.24.3, 1.25.1
- **Default**: 1.25.1
- **Global tools**: golangci-lint
- **Environment variable**: `CODEX_ENV_GO_VERSION`

### Swift
- **Tool**: mise
- **Versions**: 5.10, 6.1, 6.2
- **Default**: 6.2
- **Environment variable**: `CODEX_ENV_SWIFT_VERSION`
- **Note**: Only available on AMD64 (linux/amd64)

### Ruby
- **Tool**: mise
- **Versions**: 3.2.3, 3.3.8, 3.4.4
- **Default**: 3.4.4
- **Environment variable**: `CODEX_ENV_RUBY_VERSION`

### PHP
- **Tool**: mise
- **Versions**: 8.2, 8.3, 8.4
- **Default**: 8.4
- **Environment variable**: `CODEX_ENV_PHP_VERSION`
- **Composer**: Pre-installed with COMPOSER_ALLOW_SUPERUSER=1

### Java
- **Tool**: mise
- **Versions**: 11 (AMD64 only), 17, 21
- **Default**: 21
- **Build tools**: gradle (8.14), maven (3.9.10), bazelisk

### Other Pre-installed Tools
- **Bun**: 1.2.14
- **Elixir**: 1.18.3 (with Erlang 27.1.2)
- **Bazel**: via bazelisk
- **C/C++**: gcc, clang, LLVM, cmake, ninja, ccache
- **Linters**: cpplint, clang-tidy, clang-format, cmakelang

## Environment Lifecycle

### Setup Phase
1. Container is created from `codex-universal` image
2. Repository is cloned at the specified branch/sha
3. Environment variables and secrets are set
4. **Setup script runs** with internet access available
5. Container state is cached (up to 12 hours)

### Maintenance Phase (from cache)
1. Cached container is resumed
2. Repository is checked out to the task's branch/sha
3. **Maintenance script runs** to update dependencies
4. Agent begins working on the task

### Cache Invalidation
Cache is automatically invalidated when:
- Setup script changes
- Maintenance script changes
- Environment variables change
- Secrets change
- Manual "Reset cache" button is used

## Script Requirements

### Setup Script (`setup.sh`)
- Must use `#!/bin/bash` shebang
- Should use `set -euo pipefail` for error handling
- Has internet access for installing dependencies
- Should install all dependencies and tools needed
- Should be idempotent (safe to run multiple times)
- Can add environment variables to `~/.bashrc` for persistence

### Maintenance Script (`maintenance.sh`)
- Must use `#!/bin/bash` shebang
- Should use `set -euo pipefail` for error handling
- Should only update changed dependencies
- Should be fast and efficient
- Should detect and recover from stale caches

## Network Access

- **Setup phase**: Full internet access to install dependencies
- **Agent phase**: Disabled by default (configurable in environment settings)
- **Proxy**: All outbound traffic passes through HTTP/HTTPS proxy

## Important Notes

1. **Persistent exports**: Use `~/.bashrc` for environment variables that need to persist across shells
2. **Package managers**: Common package managers (npm, yarn, pnpm, pip, pipenv, poetry) can auto-install dependencies
3. **Secrets**: Only available during setup script, removed before agent runs
4. **Environment variables**: Available throughout the entire task duration
5. **Path separators**: Always use forward slashes (`/`), even for cross-platform scripts
