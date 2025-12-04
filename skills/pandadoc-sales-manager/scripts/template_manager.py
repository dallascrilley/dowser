#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Manage PandaDoc templates - list, inspect, and export.

This script provides tools to manage templates with search, filter, field inspection,
and JSON/YAML export capabilities.

Usage:
    # List all templates
    uv run template_manager.py list

    # Show template details
    uv run template_manager.py show --template "Sales Proposal"

    # List template fields
    uv run template_manager.py fields --template "Sales Proposal"

    # Export template configuration
    uv run template_manager.py export --template "Sales Proposal" --output template.json

    # Search templates by name
    uv run template_manager.py search --query "proposal"
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load .env file from project root
def load_env_file():
    """Load environment variables from .env file at project root."""
    # Get project root (one level up from scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)

# Load .env before reading environment variables
load_env_file()

# Configuration
BASE_URL = os.environ.get("PANDADOC_BASE_URL", "https://api.pandadoc.com/public/v1")
API_KEY = os.environ.get("PANDADOC_API_KEY", "")

# Set up logging
logger = logging.getLogger(__name__)


class PandaDocException(Exception):
    """Base exception for PandaDoc API errors."""
    pass


class AuthenticationError(PandaDocException):
    """Raised when authentication fails."""
    pass


class TemplateNotFoundError(PandaDocException):
    """Raised when template is not found."""
    pass


def configure_logging(verbose: bool = False) -> None:
    """Configure logging level.

    Args:
        verbose: If True, set to DEBUG level; otherwise INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def validate_api_key() -> None:
    """Validate API key is configured.

    Raises:
        AuthenticationError: If API key is not set
    """
    if not API_KEY:
        raise AuthenticationError(
            "PANDADOC_API_KEY environment variable not set. "
            "Please set your API key before running this script."
        )
    logger.debug("API key validated")


def get_headers() -> Dict[str, str]:
    """Get HTTP headers for API requests.

    Returns:
        Dictionary of headers
    """
    return {
        "Authorization": f"API-Key {API_KEY}",
        "Content-Type": "application/json"
    }


def list_all_templates() -> List[Dict[str, Any]]:
    """List all available templates.

    Returns:
        List of template dictionaries
    """
    logger.info("Listing all templates")
    url = f"{BASE_URL}/templates"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        else:
            logger.error(f"API error: {e.response.status_code}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")

    data = response.json()
    templates = data.get("results", [])
    logger.info(f"Found {len(templates)} templates")
    return templates


def get_template_by_id(template_uuid: str) -> Dict[str, Any]:
    """Get template details by UUID.

    Args:
        template_uuid: Template UUID

    Returns:
        Template dictionary

    Raises:
        TemplateNotFoundError: If template not found
    """
    logger.debug(f"Fetching template: {template_uuid}")
    url = f"{BASE_URL}/templates/{template_uuid}"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise TemplateNotFoundError(f"Template not found: {template_uuid}")
        else:
            logger.error(f"API error: {e.response.status_code}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")

    return response.json()


def find_template(query: str) -> Optional[Dict[str, Any]]:
    """Find template by name or UUID.

    Args:
        query: Template name or UUID

    Returns:
        Template dictionary or None if not found
    """
    templates = list_all_templates()

    # Try exact UUID match
    for tpl in templates:
        if tpl.get("uuid") == query:
            return get_template_by_id(query)

    # Try name match (case-insensitive)
    for tpl in templates:
        if tpl.get("name", "").lower() == query.lower():
            return get_template_by_id(tpl.get("uuid"))

    # Try substring match
    for tpl in templates:
        if query.lower() in tpl.get("name", "").lower():
            return get_template_by_id(tpl.get("uuid"))

    return None


def format_template_list(templates: List[Dict[str, Any]]) -> str:
    """Format template list for display.

    Args:
        templates: List of template dictionaries

    Returns:
        Formatted string
    """
    if not templates:
        return "No templates found"

    lines = [
        "",
        "=" * 80,
        "Available Templates",
        "=" * 80,
        f"{'#':<3} {'Name':<40} {'UUID':<25} {'Pages':<8}",
        "-" * 80,
    ]

    for i, tpl in enumerate(templates, 1):
        name = tpl.get("name", "Unknown")[:40]
        uuid = tpl.get("uuid", "")[:25]
        pages = tpl.get("page_count", "?")
        lines.append(f"{i:<3} {name:<40} {uuid:<25} {pages:<8}")

    lines.append("=" * 80)
    return "\n".join(lines)


def format_template_details(template: Dict[str, Any]) -> str:
    """Format template details for display.

    Args:
        template: Template dictionary

    Returns:
        Formatted string
    """
    lines = [
        "",
        "=" * 80,
        "Template Details",
        "=" * 80,
        f"Name:          {template.get('name')}",
        f"UUID:          {template.get('uuid')}",
        f"Pages:         {template.get('page_count')}",
        f"Created:       {template.get('date_created')}",
        f"Modified:      {template.get('date_modified')}",
    ]

    # Show fields if available
    if "fields" in template and template["fields"]:
        lines.append("")
        lines.append("Fields:")
        for field in template["fields"]:
            field_name = field.get("name")
            field_type = field.get("type", "text")
            lines.append(f"  - {field_name} ({field_type})")

    # Show roles if available
    if "roles" in template and template["roles"]:
        lines.append("")
        lines.append("Roles/Recipients:")
        for role in template["roles"]:
            lines.append(f"  - {role.get('name')}")

    lines.append("=" * 80)
    return "\n".join(lines)


def format_fields_table(template: Dict[str, Any]) -> str:
    """Format template fields as a table.

    Args:
        template: Template dictionary

    Returns:
        Formatted table string
    """
    lines = [
        "",
        f"Template: {template.get('name')}",
        f"UUID: {template.get('uuid')}",
        "=" * 100,
        f"{'Field Name':<40} {'Type':<20} {'Required':<15} {'Description':<25}",
        "-" * 100,
    ]

    fields = template.get("fields", [])
    if not fields:
        lines.append("No fields defined")
    else:
        for field in fields:
            name = field.get("name", "Unknown")[:40]
            field_type = field.get("type", "text")[:20]
            required = "Yes" if field.get("required") else "No"
            description = field.get("description", "")[:25]
            lines.append(
                f"{name:<40} {field_type:<20} {required:<15} {description:<25}"
            )

    lines.append("=" * 100)
    return "\n".join(lines)


def cmd_list(args: argparse.Namespace) -> int:
    """List all templates.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        templates = list_all_templates()

        if args.search:
            templates = [
                t for t in templates
                if args.search.lower() in t.get("name", "").lower()
            ]

        print(format_template_list(templates))
        return 0

    except (AuthenticationError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_show(args: argparse.Namespace) -> int:
    """Show template details.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.template:
            logger.error("--template is required")
            return 1

        template = find_template(args.template)
        if not template:
            logger.error(f"Template not found: {args.template}")
            return 1

        print(format_template_details(template))
        return 0

    except (AuthenticationError, TemplateNotFoundError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_fields(args: argparse.Namespace) -> int:
    """Show template fields.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.template:
            logger.error("--template is required")
            return 1

        template = find_template(args.template)
        if not template:
            logger.error(f"Template not found: {args.template}")
            return 1

        print(format_fields_table(template))
        return 0

    except (AuthenticationError, TemplateNotFoundError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_export(args: argparse.Namespace) -> int:
    """Export template configuration.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.template:
            logger.error("--template is required")
            return 1

        if not args.output:
            logger.error("--output is required")
            return 1

        template = find_template(args.template)
        if not template:
            logger.error(f"Template not found: {args.template}")
            return 1

        # Export to file
        with open(args.output, 'w') as f:
            json.dump(template, f, indent=2)

        logger.info(f"Template exported to {args.output}")
        print(f"SUCCESS: Exported template to {args.output}")
        return 0

    except (AuthenticationError, TemplateNotFoundError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1
    except IOError as e:
        logger.error(f"File error: {e}")
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Search templates.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.query:
            logger.error("--query is required")
            return 1

        templates = list_all_templates()
        results = [
            t for t in templates
            if args.query.lower() in t.get("name", "").lower()
        ]

        print(f"Search results for '{args.query}':")
        print(format_template_list(results))
        return 0

    except (AuthenticationError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Manage PandaDoc templates",
        epilog="""
Commands:
  list              List all available templates
  show              Show template details
  fields            Show template fields
  search            Search templates by name
  export            Export template configuration

Examples:
  python template_manager.py list
  python template_manager.py show --template "Sales Proposal"
  python template_manager.py fields --template "Sales Proposal"
  python template_manager.py search --query "proposal"
  python template_manager.py export --template "Sales Proposal" --output template.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List all templates")
    list_parser.add_argument(
        "--search",
        help="Filter templates by name"
    )

    # Show command
    show_parser = subparsers.add_parser("show", help="Show template details")
    show_parser.add_argument(
        "--template",
        required=True,
        help="Template name or UUID"
    )

    # Fields command
    fields_parser = subparsers.add_parser("fields", help="Show template fields")
    fields_parser.add_argument(
        "--template",
        required=True,
        help="Template name or UUID"
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export template")
    export_parser.add_argument(
        "--template",
        required=True,
        help="Template name or UUID"
    )
    export_parser.add_argument(
        "--output",
        required=True,
        help="Output file path"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search templates")
    search_parser.add_argument(
        "--query",
        required=True,
        help="Search query"
    )

    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    args = parse_arguments()
    configure_logging(args.verbose)

    try:
        # Validate API key
        validate_api_key()

        # Execute command
        if args.command == "list":
            return cmd_list(args)
        elif args.command == "show":
            return cmd_show(args)
        elif args.command == "fields":
            return cmd_fields(args)
        elif args.command == "export":
            return cmd_export(args)
        elif args.command == "search":
            return cmd_search(args)
        else:
            print("No command specified. Use -h for help.")
            return 1

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
