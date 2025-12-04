#!/usr/bin/env python3
"""
Parse GitHub repository URLs into owner/repo format.

Supports multiple input formats:
- Full URLs: https://github.com/owner/repo
- SSH URLs: git@github.com:owner/repo.git
- Shorthand: owner/repo
- Local repos: Reads .git/config for remote URL
"""

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def parse_github_url(url_or_path: str) -> str:
    """
    Extract owner/repo from various GitHub URL formats.

    Args:
        url_or_path: GitHub URL, shorthand, or path

    Returns:
        owner/repo format string

    Raises:
        ValueError: If URL format is invalid or not a GitHub URL
    """
    # Pattern: owner/repo (already in correct format)
    if re.match(r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$', url_or_path):
        return url_or_path

    # Pattern: SSH URL (git@github.com:owner/repo.git)
    ssh_match = re.match(r'^git@github\.com:([^/]+)/(.+?)(\.git)?$', url_or_path)
    if ssh_match:
        owner = ssh_match.group(1)
        repo = ssh_match.group(2).rstrip('.git')
        return f"{owner}/{repo}"

    # Pattern: HTTPS URL
    if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
        parsed = urlparse(url_or_path)
        if parsed.netloc != 'github.com':
            raise ValueError(f"Not a GitHub URL: {url_or_path}")

        # Extract path components
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitHub URL format: {url_or_path}")

        owner = path_parts[0]
        repo = path_parts[1].rstrip('.git')
        return f"{owner}/{repo}"

    raise ValueError(f"Unrecognized URL format: {url_or_path}")


def parse_local_repo(repo_path: str) -> str:
    """
    Extract owner/repo from local repository's .git/config.

    Args:
        repo_path: Path to local git repository

    Returns:
        owner/repo format string

    Raises:
        ValueError: If not a git repo or no GitHub remote found
    """
    path = Path(repo_path)
    git_config = path / '.git' / 'config'

    if not git_config.exists():
        raise ValueError(f"Not a git repository: {repo_path}")

    # Read git config and find GitHub remote URL
    config_content = git_config.read_text()

    # Look for GitHub remote URL patterns
    # Pattern 1: url = https://github.com/owner/repo.git
    https_match = re.search(r'url\s*=\s*https://github\.com/([^/]+)/(.+?)(?:\.git)?(?:\s|$)', config_content)
    if https_match:
        owner = https_match.group(1)
        repo = https_match.group(2).rstrip('.git')
        return f"{owner}/{repo}"

    # Pattern 2: url = git@github.com:owner/repo.git
    ssh_match = re.search(r'url\s*=\s*git@github\.com:([^/]+)/(.+?)(?:\.git)?(?:\s|$)', config_content)
    if ssh_match:
        owner = ssh_match.group(1)
        repo = ssh_match.group(2).rstrip('.git')
        return f"{owner}/{repo}"

    raise ValueError(f"No GitHub remote found in {git_config}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse GitHub repository URLs into owner/repo format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://github.com/anthropics/claude-code"
  %(prog)s "git@github.com:anthropics/claude-code.git"
  %(prog)s "anthropics/claude-code"
  %(prog)s --check-local /path/to/repo
        """
    )
    parser.add_argument(
        'url_or_path',
        nargs='?',
        default='.',
        help='GitHub URL, owner/repo shorthand, or local repo path'
    )
    parser.add_argument(
        '--check-local',
        action='store_true',
        help='Parse from local git repository .git/config'
    )

    args = parser.parse_args()

    try:
        if args.check_local:
            result = parse_local_repo(args.url_or_path)
        else:
            result = parse_github_url(args.url_or_path)

        print(result)
        sys.exit(0)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
