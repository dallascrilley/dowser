#!/usr/bin/env python3
"""
Format extracted DeepWiki content into clean, structured markdown.

Processes JSON sections into proper markdown with:
- Correct heading hierarchy
- Clean code blocks with language tags
- Preserved lists and tables
- Optional table of contents
- Removed UI artifacts
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List


def clean_text(text: str) -> str:
    """
    Remove UI artifacts and clean markdown text.

    Args:
        text: Raw text content

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Remove common UI artifacts
    artifacts = [
        'Skip to content',
        'Toggle navigation',
        'Back to top',
        '← Previous',
        'Next →',
    ]
    for artifact in artifacts:
        text = text.replace(artifact, '')

    # Clean up stray HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')

    return text.strip()


def fix_code_blocks(text: str) -> str:
    """
    Ensure code blocks have proper fencing and language tags.

    Args:
        text: Text containing code blocks

    Returns:
        Text with fixed code blocks
    """
    # Fix unclosed code blocks
    lines = text.split('\n')
    in_code_block = False
    fixed_lines = []

    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
        fixed_lines.append(line)

    # Close any unclosed code block
    if in_code_block:
        fixed_lines.append('```')

    return '\n'.join(fixed_lines)


def normalize_headings(text: str, base_level: int = 2) -> str:
    """
    Normalize heading levels to start at base_level.

    Args:
        text: Text with headings
        base_level: Starting heading level (default: 2 for ##)

    Returns:
        Text with normalized headings
    """
    lines = text.split('\n')
    normalized = []

    for line in lines:
        # Match markdown headings
        match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if match:
            # Normalize to base_level
            hashes = '#' * base_level
            content = match.group(2)
            normalized.append(f"{hashes} {content}")
        else:
            normalized.append(line)

    return '\n'.join(normalized)


def generate_toc(sections: List[Dict[str, Any]]) -> str:
    """
    Generate table of contents from sections.

    Args:
        sections: List of section dictionaries

    Returns:
        Markdown table of contents
    """
    toc_lines = ["## Table of Contents\n"]

    for section in sections:
        title = section.get('title', 'Untitled Section')
        # Create anchor link (lowercase, replace spaces with hyphens)
        anchor = title.lower().replace(' ', '-').replace('/', '')
        # Remove special characters
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)

        toc_lines.append(f"- [{title}](#{anchor})")

    return '\n'.join(toc_lines)


def format_section(section: Dict[str, Any]) -> str:
    """
    Format a single documentation section.

    Args:
        section: Section dictionary with title and content

    Returns:
        Formatted markdown section
    """
    title = section.get('title', 'Untitled Section')
    content = section.get('content', '')

    if not content.strip():
        print(f"Warning: Empty section '{title}'", file=sys.stderr)
        return ''

    # Clean and format content
    content = clean_text(content)
    content = fix_code_blocks(content)

    # Build section
    section_md = f"## {title}\n\n{content}\n"

    return section_md


def format_document(data: Dict[str, Any], add_toc: bool = False) -> str:
    """
    Format complete documentation from extracted data.

    Args:
        data: Dictionary containing repo info and sections
        add_toc: Whether to add table of contents

    Returns:
        Complete formatted markdown document
    """
    repo_name = data.get('repository', 'Repository')
    owner_repo = data.get('owner_repo', '')
    sections = data.get('sections', [])

    if not sections:
        raise ValueError("No sections found in input data")

    # Build document header
    doc_lines = [
        f"# {repo_name} Documentation",
        f"*Extracted from DeepWiki on {datetime.now().strftime('%Y-%m-%d')}*\n"
    ]

    # Add table of contents if requested
    if add_toc:
        doc_lines.append(generate_toc(sections))
        doc_lines.append("\n---\n")

    # Format each section
    for section in sections:
        formatted = format_section(section)
        if formatted:
            doc_lines.append(formatted)

    # Add footer
    if owner_repo:
        doc_lines.append("---\n")
        doc_lines.append(f"*Documentation source: https://deepwiki.com/{owner_repo}*")

    return '\n'.join(doc_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Format extracted DeepWiki content into clean markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example input JSON format:
{
  "repository": "anthropic-sdk-python",
  "owner_repo": "anthropics/anthropic-sdk-python",
  "sections": [
    {
      "title": "Overview",
      "content": "The Anthropic Python SDK..."
    },
    {
      "title": "Installation",
      "content": "```bash\\npip install anthropic\\n```"
    }
  ]
}

Usage:
  %(prog)s input.json > output.md
  %(prog)s --add-toc input.json > output.md
  cat input.json | %(prog)s --stdin > output.md
        """
    )
    parser.add_argument(
        'input_file',
        nargs='?',
        help='JSON file with extracted sections (use - for stdin)'
    )
    parser.add_argument(
        '--add-toc',
        action='store_true',
        help='Generate table of contents'
    )
    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read from stdin instead of file'
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.stdin or args.input_file == '-':
            input_data = sys.stdin.read()
        elif args.input_file:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_data = f.read()
        else:
            parser.error("Either provide input_file or use --stdin")

        # Parse JSON
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        # Format document
        markdown = format_document(data, add_toc=args.add_toc)

        # Output
        print(markdown)
        sys.exit(0)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
