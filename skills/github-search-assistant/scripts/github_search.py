#!/usr/bin/env python3
"""
GitHub Search API Script

Execute GitHub searches via API and format results.

Usage:
    python github_search.py --query "language:python stars:>100" --type repositories
    python github_search.py --query "is:issue is:open label:bug" --type issues --limit 20

Environment:
    GITHUB_TOKEN - Optional GitHub personal access token for higher rate limits
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class GitHubSearcher:
    """GitHub Search API client."""

    BASE_URL = "https://api.github.com/search"

    SEARCH_TYPES = {
        'repositories': 'repositories',
        'code': 'code',
        'issues': 'issues',
        'pullrequests': 'issues',  # PRs use issues endpoint with is:pr qualifier
        'commits': 'commits',
        'topics': 'topics',
        'users': 'users'
    }

    def __init__(self, token: Optional[str] = None):
        """Initialize with optional GitHub token."""
        self.token = token or os.environ.get('GITHUB_TOKEN')

    def _make_request(self, url: str) -> Dict[str, Any]:
        """Make authenticated request to GitHub API."""
        headers = {
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'GitHub-Search-Assistant'
        }

        if self.token:
            headers['Authorization'] = f'token {self.token}'

        request = Request(url, headers=headers)

        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('message', str(e))
            except json.JSONDecodeError:
                error_msg = str(e)

            if e.code == 403:
                print(f"\n⚠️  Rate limit exceeded: {error_msg}", file=sys.stderr)
                print("💡 Set GITHUB_TOKEN environment variable for higher limits (5000/hour vs 60/hour)", file=sys.stderr)
            else:
                print(f"\n❌ API Error ({e.code}): {error_msg}", file=sys.stderr)

            sys.exit(1)
        except URLError as e:
            print(f"\n❌ Network Error: {e.reason}", file=sys.stderr)
            sys.exit(1)

    def search(
        self,
        query: str,
        search_type: str = 'repositories',
        limit: int = 10,
        sort: Optional[str] = None,
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Execute GitHub search.

        Args:
            query: GitHub search query string
            search_type: Type of search (repositories, code, issues, etc.)
            limit: Maximum number of results to return (max 100 per request)
            sort: Sort field (stars, forks, updated, etc.)
            order: Sort order (asc or desc)

        Returns:
            Search results dictionary
        """
        if search_type not in self.SEARCH_TYPES:
            valid_types = ', '.join(self.SEARCH_TYPES.keys())
            raise ValueError(f"Invalid search type. Must be one of: {valid_types}")

        # Map search type to API endpoint
        endpoint_type = self.SEARCH_TYPES[search_type]

        # Build URL
        encoded_query = quote_plus(query)
        url = f"{self.BASE_URL}/{endpoint_type}?q={encoded_query}&per_page={min(limit, 100)}"

        if sort:
            url += f"&sort={sort}&order={order}"

        return self._make_request(url)

    def format_results(
        self,
        results: Dict[str, Any],
        search_type: str,
        limit: int
    ) -> str:
        """Format search results as readable text."""
        items = results.get('items', [])
        total_count = results.get('total_count', 0)

        if not items:
            return "No results found."

        output = []
        output.append(f"\n## Search Results\n")
        output.append(f"**Total matches**: {total_count:,}")
        output.append(f"**Showing**: {min(len(items), limit)} results\n")

        for idx, item in enumerate(items[:limit], 1):
            output.append(f"### {idx}. {self._format_item(item, search_type)}\n")

        return '\n'.join(output)

    def _format_item(self, item: Dict[str, Any], search_type: str) -> str:
        """Format individual search result item."""
        if search_type in ['repositories', 'code']:
            return self._format_repository_or_code(item, search_type)
        elif search_type in ['issues', 'pullrequests']:
            return self._format_issue_or_pr(item)
        elif search_type == 'commits':
            return self._format_commit(item)
        elif search_type == 'users':
            return self._format_user(item)
        else:
            return json.dumps(item, indent=2)

    def _format_repository_or_code(self, item: Dict[str, Any], search_type: str) -> str:
        """Format repository or code search result."""
        if search_type == 'code':
            repo = item.get('repository', {})
            name = f"{repo.get('full_name', 'Unknown')}/{item.get('name', 'Unknown')}"
            url = item.get('html_url', '')
            description = f"Path: {item.get('path', 'N/A')}"
        else:
            name = item.get('full_name', 'Unknown')
            url = item.get('html_url', '')
            description = item.get('description', 'No description')

        stars = item.get('stargazers_count') or item.get('repository', {}).get('stargazers_count', 0)
        language = item.get('language') or item.get('repository', {}).get('language', 'Unknown')
        updated = item.get('updated_at', 'Unknown')

        lines = [
            f"**{name}**",
            f"- **URL**: {url}",
            f"- **Description**: {description}",
            f"- **Stars**: {stars:,}",
            f"- **Language**: {language}",
            f"- **Updated**: {updated}"
        ]

        return '\n'.join(lines)

    def _format_issue_or_pr(self, item: Dict[str, Any]) -> str:
        """Format issue or PR search result."""
        title = item.get('title', 'Unknown')
        url = item.get('html_url', '')
        state = item.get('state', 'Unknown')
        user = item.get('user', {}).get('login', 'Unknown')
        created = item.get('created_at', 'Unknown')
        comments = item.get('comments', 0)
        labels = [label.get('name') for label in item.get('labels', [])]

        is_pr = 'pull_request' in item
        item_type = "Pull Request" if is_pr else "Issue"

        lines = [
            f"**{title}**",
            f"- **Type**: {item_type}",
            f"- **URL**: {url}",
            f"- **State**: {state}",
            f"- **Author**: {user}",
            f"- **Created**: {created}",
            f"- **Comments**: {comments}"
        ]

        if labels:
            lines.append(f"- **Labels**: {', '.join(labels)}")

        return '\n'.join(lines)

    def _format_commit(self, item: Dict[str, Any]) -> str:
        """Format commit search result."""
        commit_data = item.get('commit', {})
        sha = item.get('sha', 'Unknown')[:7]
        message = commit_data.get('message', 'No message').split('\n')[0]
        author = commit_data.get('author', {}).get('name', 'Unknown')
        date = commit_data.get('author', {}).get('date', 'Unknown')
        url = item.get('html_url', '')
        repo = item.get('repository', {}).get('full_name', 'Unknown')

        lines = [
            f"**{sha}: {message}**",
            f"- **Repository**: {repo}",
            f"- **URL**: {url}",
            f"- **Author**: {author}",
            f"- **Date**: {date}"
        ]

        return '\n'.join(lines)

    def _format_user(self, item: Dict[str, Any]) -> str:
        """Format user search result."""
        login = item.get('login', 'Unknown')
        url = item.get('html_url', '')
        user_type = item.get('type', 'User')

        lines = [
            f"**{login}**",
            f"- **URL**: {url}",
            f"- **Type**: {user_type}"
        ]

        return '\n'.join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Execute GitHub searches via API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for repositories
  python github_search.py --query "language:python machine-learning stars:>100" --type repositories

  # Search for issues
  python github_search.py --query "is:issue is:open label:bug" --type issues --limit 20

  # Search for code
  python github_search.py --query "symbol:authenticate language:python" --type code

  # Search with sorting
  python github_search.py --query "topic:cli language:rust" --type repositories --sort stars --order desc

Environment Variables:
  GITHUB_TOKEN - GitHub personal access token (optional, increases rate limits)
        """
    )

    parser.add_argument(
        '--query',
        required=True,
        help='GitHub search query string'
    )

    parser.add_argument(
        '--type',
        default='repositories',
        choices=list(GitHubSearcher.SEARCH_TYPES.keys()),
        help='Search type (default: repositories)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of results to show (default: 10, max: 100)'
    )

    parser.add_argument(
        '--sort',
        help='Sort field (e.g., stars, forks, updated)'
    )

    parser.add_argument(
        '--order',
        choices=['asc', 'desc'],
        default='desc',
        help='Sort order (default: desc)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output raw JSON instead of formatted text'
    )

    args = parser.parse_args()

    # Create searcher
    searcher = GitHubSearcher()

    # Execute search
    try:
        results = searcher.search(
            query=args.query,
            search_type=args.type,
            limit=args.limit,
            sort=args.sort,
            order=args.order
        )

        # Output results
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            formatted = searcher.format_results(results, args.type, args.limit)
            print(formatted)

    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nSearch cancelled.", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
