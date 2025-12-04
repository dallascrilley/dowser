#!/usr/bin/env python3
"""
Generate Codex-compatible setup and maintenance scripts.
Takes repository analysis and produces shell scripts for environment provisioning.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set


class ScriptGenerator:
    """Generates setup.sh and maintenance.sh scripts for Codex environments."""
    
    # Default versions from codex-universal
    DEFAULT_VERSIONS = {
        'python': '3.12',
        'node': '22',
        'rust': '1.87.0',
        'go': '1.25.1',
        'swift': '6.2',
        'ruby': '3.4.4',
        'php': '8.4',
    }
    
    def __init__(self, repo_analysis: Dict, env_vars: Dict = None):
        self.analysis = repo_analysis
        self.env_vars = env_vars or {}
        self.languages = set(repo_analysis.get('languages', []))
        self.package_managers = repo_analysis.get('package_managers', {})
        self.test_frameworks = set(repo_analysis.get('test_frameworks', []))
        self.linters = set(repo_analysis.get('linters', []))
    
    def _get_version(self, lang: str) -> str:
        """Get version for a language from env vars or defaults."""
        env_key = f'CODEX_ENV_{lang.upper()}_VERSION'
        return self.env_vars.get(env_key, self.DEFAULT_VERSIONS.get(lang, ''))
    
    def _header(self) -> str:
        """Generate script header."""
        return """#!/bin/bash
set -euo pipefail

# Auto-generated Codex provisioning script
# Generated from repository analysis

echo "================================================="
echo "🚀 Codex Environment Setup"
echo "================================================="
"""
    
    def _configure_python(self, is_setup: bool) -> str:
        """Generate Python configuration commands."""
        if 'python' not in self.languages:
            return ""
        
        lines = ['\necho "\\n🐍 Configuring Python..."']
        
        if is_setup:
            # Setup: Install dependencies
            if 'poetry' in self.package_managers:
                lines.append('if [ -f "pyproject.toml" ] && command -v poetry &> /dev/null; then')
                lines.append('    echo "  Installing Python dependencies with Poetry..."')
                lines.append('    poetry install')
                lines.append('fi')
            elif 'pipenv' in self.package_managers:
                lines.append('if [ -f "Pipfile" ] && command -v pipenv &> /dev/null; then')
                lines.append('    echo "  Installing Python dependencies with Pipenv..."')
                lines.append('    pipenv install --dev')
                lines.append('fi')
            elif 'uv' in self.package_managers:
                lines.append('if [ -f "pyproject.toml" ] && command -v uv &> /dev/null; then')
                lines.append('    echo "  Installing Python dependencies with uv..."')
                lines.append('    uv sync')
                lines.append('fi')
            elif 'pip' in self.package_managers:
                lines.append('if [ -f "requirements.txt" ]; then')
                lines.append('    echo "  Installing Python dependencies with pip..."')
                lines.append('    pip install --no-cache-dir -r requirements.txt')
                lines.append('fi')
        else:
            # Maintenance: Update if lockfiles changed
            if 'poetry' in self.package_managers:
                lines.append('if [ -f "poetry.lock" ]; then')
                lines.append('    echo "  Updating Poetry dependencies..."')
                lines.append('    poetry install --sync')
                lines.append('fi')
            elif 'uv' in self.package_managers:
                lines.append('if [ -f "uv.lock" ]; then')
                lines.append('    echo "  Syncing uv dependencies..."')
                lines.append('    uv sync')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_node(self, is_setup: bool) -> str:
        """Generate Node.js configuration commands."""
        if 'javascript' not in self.languages and 'typescript' not in self.languages:
            return ""
        
        lines = ['\necho "\\n📦 Configuring Node.js..."']
        
        if is_setup:
            # Setup: Install dependencies
            if 'pnpm' in self.package_managers:
                lines.append('if [ -f "package.json" ]; then')
                lines.append('    echo "  Installing Node dependencies with pnpm..."')
                lines.append('    pnpm install')
                lines.append('fi')
            elif 'yarn' in self.package_managers:
                lines.append('if [ -f "package.json" ]; then')
                lines.append('    echo "  Installing Node dependencies with yarn..."')
                lines.append('    yarn install')
                lines.append('fi')
            elif 'npm' in self.package_managers:
                lines.append('if [ -f "package.json" ]; then')
                lines.append('    echo "  Installing Node dependencies with npm..."')
                lines.append('    npm install')
                lines.append('fi')
        else:
            # Maintenance: Reinstall if package-lock changed
            if 'pnpm' in self.package_managers:
                lines.append('if [ -f "pnpm-lock.yaml" ]; then')
                lines.append('    echo "  Updating pnpm dependencies..."')
                lines.append('    pnpm install')
                lines.append('fi')
            elif 'yarn' in self.package_managers:
                lines.append('if [ -f "yarn.lock" ]; then')
                lines.append('    echo "  Updating yarn dependencies..."')
                lines.append('    yarn install --frozen-lockfile')
                lines.append('fi')
            elif 'npm' in self.package_managers:
                lines.append('if [ -f "package-lock.json" ]; then')
                lines.append('    echo "  Updating npm dependencies..."')
                lines.append('    npm ci')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_go(self, is_setup: bool) -> str:
        """Generate Go configuration commands."""
        if 'go' not in self.languages:
            return ""
        
        lines = ['\necho "\\n🔵 Configuring Go..."']
        
        if is_setup:
            lines.append('if [ -f "go.mod" ]; then')
            lines.append('    echo "  Downloading Go modules..."')
            lines.append('    go mod download')
            lines.append('fi')
        else:
            lines.append('if [ -f "go.sum" ]; then')
            lines.append('    echo "  Verifying Go modules..."')
            lines.append('    go mod verify')
            lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_rust(self, is_setup: bool) -> str:
        """Generate Rust configuration commands."""
        if 'rust' not in self.languages:
            return ""
        
        lines = ['\necho "\\n🦀 Configuring Rust..."']
        
        if is_setup:
            lines.append('if [ -f "Cargo.toml" ]; then')
            lines.append('    echo "  Fetching Rust dependencies..."')
            lines.append('    cargo fetch')
            lines.append('fi')
        else:
            lines.append('if [ -f "Cargo.lock" ]; then')
            lines.append('    echo "  Updating Rust dependencies..."')
            lines.append('    cargo fetch')
            lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_ruby(self, is_setup: bool) -> str:
        """Generate Ruby configuration commands."""
        if 'ruby' not in self.languages:
            return ""
        
        lines = ['\necho "\\n💎 Configuring Ruby..."']
        
        if is_setup:
            if 'bundler' in self.package_managers:
                lines.append('if [ -f "Gemfile" ]; then')
                lines.append('    echo "  Installing Ruby gems..."')
                lines.append('    bundle install')
                lines.append('fi')
        else:
            if 'bundler' in self.package_managers:
                lines.append('if [ -f "Gemfile.lock" ]; then')
                lines.append('    echo "  Updating Ruby gems..."')
                lines.append('    bundle install')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_php(self, is_setup: bool) -> str:
        """Generate PHP configuration commands."""
        if 'php' not in self.languages:
            return ""
        
        lines = ['\necho "\\n🐘 Configuring PHP..."']
        
        if is_setup:
            if 'composer' in self.package_managers:
                lines.append('if [ -f "composer.json" ]; then')
                lines.append('    echo "  Installing PHP dependencies..."')
                lines.append('    composer install')
                lines.append('fi')
        else:
            if 'composer' in self.package_managers:
                lines.append('if [ -f "composer.lock" ]; then')
                lines.append('    echo "  Updating PHP dependencies..."')
                lines.append('    composer install')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_swift(self, is_setup: bool) -> str:
        """Generate Swift configuration commands."""
        if 'swift' not in self.languages:
            return ""
        
        lines = ['\necho "\\n🍎 Configuring Swift..."']
        
        if is_setup:
            if 'swift-pm' in self.package_managers:
                lines.append('if [ -f "Package.swift" ]; then')
                lines.append('    echo "  Resolving Swift packages..."')
                lines.append('    swift package resolve')
                lines.append('fi')
        else:
            if 'swift-pm' in self.package_managers:
                lines.append('if [ -f "Package.resolved" ]; then')
                lines.append('    echo "  Updating Swift packages..."')
                lines.append('    swift package update')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_java(self, is_setup: bool) -> str:
        """Generate Java configuration commands."""
        if 'java' not in self.languages:
            return ""
        
        lines = ['\necho "\\n☕ Configuring Java..."']
        
        if is_setup:
            if 'maven' in self.package_managers:
                lines.append('if [ -f "pom.xml" ]; then')
                lines.append('    echo "  Downloading Maven dependencies..."')
                lines.append('    mvn dependency:resolve')
                lines.append('fi')
            elif 'gradle' in self.package_managers:
                lines.append('if [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then')
                lines.append('    echo "  Downloading Gradle dependencies..."')
                lines.append('    gradle dependencies --quiet || ./gradlew dependencies --quiet')
                lines.append('fi')
        
        return '\n'.join(lines)
    
    def _configure_linters(self, is_setup: bool) -> str:
        """Generate linter/formatter installation commands."""
        if not self.linters or not is_setup:
            return ""
        
        lines = ['\necho "\\n✨ Installing linters and formatters..."']
        
        # Python linters
        python_linters = self.linters & {'ruff', 'black', 'mypy', 'isort'}
        if python_linters and 'python' in self.languages:
            lines.append('# Python linters already installed in base image')
        
        # Node linters
        node_linters = self.linters & {'eslint', 'prettier'}
        if node_linters and ('javascript' in self.languages or 'typescript' in self.languages):
            lines.append('# ESLint and Prettier typically installed via package.json')
        
        # Go linters
        if 'golangci-lint' in self.linters and 'go' in self.languages:
            lines.append('# golangci-lint already installed in base image')
        
        return '\n'.join(lines) if len(lines) > 1 else ""
    
    def _footer(self) -> str:
        """Generate script footer."""
        return """\n
echo "================================================="
echo "✅ Environment setup complete!"
echo "================================================="
"""
    
    def generate_setup_script(self) -> str:
        """Generate the complete setup.sh script."""
        sections = [
            self._header(),
            self._configure_python(is_setup=True),
            self._configure_node(is_setup=True),
            self._configure_go(is_setup=True),
            self._configure_rust(is_setup=True),
            self._configure_ruby(is_setup=True),
            self._configure_php(is_setup=True),
            self._configure_swift(is_setup=True),
            self._configure_java(is_setup=True),
            self._configure_linters(is_setup=True),
            self._footer(),
        ]
        
        return '\n'.join(s for s in sections if s)
    
    def generate_maintenance_script(self) -> str:
        """Generate the complete maintenance.sh script."""
        header = """#!/bin/bash
set -euo pipefail

# Auto-generated Codex maintenance script
# Runs when resuming from cached container

echo "================================================="
echo "🔄 Codex Environment Maintenance"
echo "================================================="
"""
        
        sections = [
            header,
            self._configure_python(is_setup=False),
            self._configure_node(is_setup=False),
            self._configure_go(is_setup=False),
            self._configure_rust(is_setup=False),
            self._configure_ruby(is_setup=False),
            self._configure_php(is_setup=False),
            self._configure_swift(is_setup=False),
            self._footer(),
        ]
        
        return '\n'.join(s for s in sections if s)


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: generate_scripts.py <analysis.json> [--setup | --maintenance | --both]", file=sys.stderr)
        sys.exit(1)
    
    analysis_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else '--both'
    
    try:
        with open(analysis_file) as f:
            analysis = json.load(f)
        
        generator = ScriptGenerator(analysis)
        
        if mode in ('--setup', '--both'):
            setup_script = generator.generate_setup_script()
            with open('setup.sh', 'w') as f:
                f.write(setup_script)
            print("✅ Generated setup.sh")
        
        if mode in ('--maintenance', '--both'):
            maintenance_script = generator.generate_maintenance_script()
            with open('maintenance.sh', 'w') as f:
                f.write(maintenance_script)
            print("✅ Generated maintenance.sh")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
