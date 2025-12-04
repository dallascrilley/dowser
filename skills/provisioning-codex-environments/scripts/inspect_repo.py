#!/usr/bin/env python3
"""
Repository inspector for detecting languages, package managers, and tooling.
Scans a repository to identify what's needed for Codex provisioning scripts.
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set


class RepoInspector:
    """Inspects a repository to detect languages, package managers, and tooling."""
    
    # Language detection mappings
    LANG_EXTENSIONS = {
        'python': {'.py', '.pyw', '.pyx'},
        'javascript': {'.js', '.mjs', '.cjs'},
        'typescript': {'.ts', '.tsx'},
        'go': {'.go'},
        'rust': {'.rs'},
        'swift': {'.swift'},
        'ruby': {'.rb'},
        'php': {'.php'},
        'java': {'.java'},
        'c': {'.c', '.h'},
        'cpp': {'.cpp', '.cc', '.cxx', '.hpp', '.hxx'},
        'bash': {'.sh', '.bash'},
        'elixir': {'.ex', '.exs'},
    }
    
    # Package manager detection files
    PACKAGE_MANAGERS = {
        # Python
        'poetry': ['pyproject.toml', 'poetry.lock'],
        'pipenv': ['Pipfile', 'Pipfile.lock'],
        'pip': ['requirements.txt', 'setup.py', 'setup.cfg'],
        'uv': ['pyproject.toml', 'uv.lock'],
        
        # Node.js
        'npm': ['package.json', 'package-lock.json'],
        'yarn': ['package.json', 'yarn.lock'],
        'pnpm': ['package.json', 'pnpm-lock.yaml'],
        'bun': ['package.json', 'bun.lockb'],
        
        # Go
        'go': ['go.mod', 'go.sum'],
        
        # Rust
        'cargo': ['Cargo.toml', 'Cargo.lock'],
        
        # Ruby
        'bundler': ['Gemfile', 'Gemfile.lock'],
        
        # PHP
        'composer': ['composer.json', 'composer.lock'],
        
        # Swift
        'swift-pm': ['Package.swift'],
        
        # Java
        'maven': ['pom.xml'],
        'gradle': ['build.gradle', 'build.gradle.kts'],
    }
    
    # Test framework indicators
    TEST_INDICATORS = {
        'pytest': ['pytest.ini', 'setup.cfg', 'pyproject.toml'],
        'unittest': ['test_*.py', '*_test.py'],
        'jest': ['jest.config.js', 'jest.config.ts'],
        'vitest': ['vitest.config.ts', 'vitest.config.js'],
        'go-test': ['*_test.go'],
        'cargo-test': ['Cargo.toml'],
        'rspec': ['spec/'],
        'phpunit': ['phpunit.xml'],
        'junit': ['pom.xml', 'build.gradle'],
    }
    
    # Linter/formatter indicators
    LINTER_INDICATORS = {
        'ruff': ['pyproject.toml', 'ruff.toml'],
        'black': ['pyproject.toml'],
        'mypy': ['mypy.ini', 'setup.cfg', 'pyproject.toml'],
        'eslint': ['.eslintrc', '.eslintrc.js', '.eslintrc.json'],
        'prettier': ['.prettierrc', '.prettierrc.js', 'prettier.config.js'],
        'golangci-lint': ['.golangci.yml', '.golangci.yaml'],
        'clippy': ['Cargo.toml'],
        'rustfmt': ['rustfmt.toml', '.rustfmt.toml'],
    }
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    def detect_languages(self) -> Set[str]:
        """Detect programming languages used in the repository."""
        languages = set()
        
        for ext_map in ['.py', '.js', '.ts', '.go', '.rs', '.rb', '.php', 
                        '.java', '.swift', '.ex', '.sh', '.c', '.cpp']:
            for _ in self.repo_path.rglob(f'*{ext_map}'):
                for lang, exts in self.LANG_EXTENSIONS.items():
                    if ext_map in exts:
                        languages.add(lang)
                        break
                if languages:
                    break
        
        return languages
    
    def detect_package_managers(self) -> Dict[str, List[str]]:
        """Detect package managers and their indicator files."""
        found = {}
        
        for manager, indicators in self.PACKAGE_MANAGERS.items():
            matching_files = []
            for indicator in indicators:
                # Check both exact match and glob pattern
                if (self.repo_path / indicator).exists():
                    matching_files.append(indicator)
                else:
                    # Try as glob pattern
                    matches = list(self.repo_path.rglob(indicator))
                    if matches:
                        matching_files.extend([str(m.relative_to(self.repo_path)) for m in matches[:3]])
            
            if matching_files:
                found[manager] = matching_files
        
        return found
    
    def detect_test_frameworks(self) -> List[str]:
        """Detect testing frameworks in use."""
        frameworks = set()
        
        for framework, indicators in self.TEST_INDICATORS.items():
            for indicator in indicators:
                if (self.repo_path / indicator).exists():
                    frameworks.add(framework)
                    break
                # Check glob patterns
                if '*' in indicator:
                    if list(self.repo_path.rglob(indicator)):
                        frameworks.add(framework)
                        break
        
        return sorted(frameworks)
    
    def detect_linters(self) -> List[str]:
        """Detect linters and formatters in use."""
        linters = set()
        
        for linter, indicators in self.LINTER_INDICATORS.items():
            for indicator in indicators:
                if (self.repo_path / indicator).exists():
                    linters.add(linter)
                    break
        
        return sorted(linters)
    
    def get_repo_structure(self) -> Dict[str, any]:
        """Get complete repository structure analysis."""
        return {
            'languages': sorted(self.detect_languages()),
            'package_managers': self.detect_package_managers(),
            'test_frameworks': self.detect_test_frameworks(),
            'linters': self.detect_linters(),
            'repo_path': str(self.repo_path),
        }
    
    def print_report(self):
        """Print a human-readable inspection report."""
        structure = self.get_repo_structure()
        
        print(f"\n📁 Repository: {structure['repo_path']}\n")
        
        print("🔤 Languages detected:")
        if structure['languages']:
            for lang in structure['languages']:
                print(f"  - {lang}")
        else:
            print("  (none detected)")
        
        print("\n📦 Package managers:")
        if structure['package_managers']:
            for manager, files in structure['package_managers'].items():
                print(f"  - {manager}: {', '.join(files[:2])}")
        else:
            print("  (none detected)")
        
        print("\n🧪 Test frameworks:")
        if structure['test_frameworks']:
            for fw in structure['test_frameworks']:
                print(f"  - {fw}")
        else:
            print("  (none detected)")
        
        print("\n✨ Linters/formatters:")
        if structure['linters']:
            for linter in structure['linters']:
                print(f"  - {linter}")
        else:
            print("  (none detected)")
        print()


def main():
    """CLI entry point."""
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = '.'
    
    try:
        inspector = RepoInspector(repo_path)
        
        # Check for --json flag
        if '--json' in sys.argv:
            structure = inspector.get_repo_structure()
            print(json.dumps(structure, indent=2))
        else:
            inspector.print_report()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
