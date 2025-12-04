#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Manage PandaDoc product catalog - search, list, and view catalog items.

This script provides tools to search catalog items, view item details, and filter
by category, type, or custom fields.

Usage:
    # Search catalog items
    uv run catalog_manager.py search --query "laptop"

    # List all items (with pagination)
    uv run catalog_manager.py list

    # Show item details by UUID
    uv run catalog_manager.py show --item-uuid "abc123..."

    # Search with filters
    uv run catalog_manager.py search --query "product" --category-id "123" --order-by price --order desc

    # Export search results to JSON
    uv run catalog_manager.py search --query "laptop" --output results.json
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


class CatalogItemNotFoundError(PandaDocException):
    """Raised when catalog item is not found."""
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


def search_catalog_items(
    query: Optional[str] = None,
    item_type: Optional[str] = None,
    billing_type: Optional[str] = None,
    category_id: Optional[str] = None,
    order_by: str = "name",
    order: str = "asc",
    exclude_uuids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Search catalog items.

    Args:
        query: Search query (searches title, SKU, description, category name, custom fields)
        item_type: Filter by item type
        billing_type: Filter by billing type
        category_id: Filter by category ID
        order_by: Sort by (sku, name, price, modified_date)
        order: Sort direction (asc, desc)
        exclude_uuids: List of UUIDs to exclude

    Returns:
        List of catalog item dictionaries
    """
    logger.info(f"Searching catalog items (query: {query})")
    
    # Use v2 API for catalog endpoints
    base_url_v2 = BASE_URL.replace("/v1", "/v2")
    url = f"{base_url_v2}/product-catalog/items/search"
    headers = get_headers()
    
    params = {
        "order_by": order_by,
        "order": order
    }
    
    if query:
        params["query"] = query
    if item_type:
        params["type"] = item_type
    if billing_type:
        params["billing_type"] = billing_type
    if category_id:
        params["category_id"] = category_id
    if exclude_uuids:
        params["exclude_uuids"] = ",".join(exclude_uuids) if isinstance(exclude_uuids, list) else exclude_uuids
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")
    
    data = response.json()
    items = data.get("results", [])
    logger.info(f"Found {len(items)} catalog item(s)")
    return items


def get_catalog_item(item_uuid: str) -> Dict[str, Any]:
    """Get catalog item details by UUID.

    Args:
        item_uuid: Catalog item UUID

    Returns:
        Catalog item dictionary

    Raises:
        CatalogItemNotFoundError: If item not found
    """
    logger.debug(f"Fetching catalog item: {item_uuid}")
    
    # Use v2 API for catalog endpoints
    base_url_v2 = BASE_URL.replace("/v1", "/v2")
    url = f"{base_url_v2}/product-catalog/items/{item_uuid}"
    headers = get_headers()
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise CatalogItemNotFoundError(f"Catalog item not found: {item_uuid}")
        elif e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")
    
    return response.json()


def format_catalog_list(items: List[Dict[str, Any]]) -> str:
    """Format catalog item list for display.

    Args:
        items: List of catalog item dictionaries

    Returns:
        Formatted string
    """
    if not items:
        return "No catalog items found"
    
    lines = [
        "",
        "=" * 100,
        "Catalog Items",
        "=" * 100,
        f"{'#':<3} {'Name':<35} {'SKU':<20} {'Price':<15} {'UUID':<25}",
        "-" * 100,
    ]
    
    for i, item in enumerate(items, 1):
        name = item.get("name", "Unknown")[:35]
        sku = item.get("sku", "N/A")[:20]
        price = item.get("price", "N/A")
        if isinstance(price, (int, float)):
            price = f"${price:,.2f}"
        uuid = item.get("uuid", "")[:25]
        lines.append(f"{i:<3} {name:<35} {sku:<20} {str(price):<15} {uuid:<25}")
    
    lines.append("=" * 100)
    return "\n".join(lines)


def format_catalog_item_details(item: Dict[str, Any]) -> str:
    """Format catalog item details for display.

    Args:
        item: Catalog item dictionary

    Returns:
        Formatted string
    """
    lines = [
        "",
        "=" * 80,
        "Catalog Item Details",
        "=" * 80,
        f"Name:          {item.get('name')}",
        f"UUID:          {item.get('uuid')}",
        f"SKU:           {item.get('sku', 'N/A')}",
        f"Price:         {item.get('price', 'N/A')}",
        f"Type:           {item.get('type', 'N/A')}",
        f"Billing Type:   {item.get('billing_type', 'N/A')}",
    ]
    
    if item.get("description"):
        lines.append(f"Description:   {item.get('description')}")
    
    if item.get("category"):
        category = item.get("category", {})
        if isinstance(category, dict):
            lines.append(f"Category:      {category.get('name', 'N/A')} (ID: {category.get('id', 'N/A')})")
        else:
            lines.append(f"Category:      {category}")
    
    if item.get("custom_fields"):
        lines.append("")
        lines.append("Custom Fields:")
        for field in item.get("custom_fields", []):
            field_name = field.get("name", "Unknown")
            field_value = field.get("value", "N/A")
            lines.append(f"  - {field_name}: {field_value}")
    
    if item.get("metadata"):
        lines.append("")
        lines.append("Metadata:")
        for key, value in item.get("metadata", {}).items():
            lines.append(f"  - {key}: {value}")
    
    lines.append("=" * 80)
    return "\n".join(lines)


def cmd_search(args: argparse.Namespace) -> int:
    """Search catalog items.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        exclude_uuids = None
        if args.exclude_uuids:
            exclude_uuids = [u.strip() for u in args.exclude_uuids.split(",")]
        
        items = search_catalog_items(
            query=args.query,
            item_type=args.type,
            billing_type=args.billing_type,
            category_id=args.category_id,
            order_by=args.order_by,
            order=args.order,
            exclude_uuids=exclude_uuids
        )
        
        if args.output:
            # Export to JSON
            with open(args.output, 'w') as f:
                json.dump(items, f, indent=2)
            logger.info(f"Exported {len(items)} item(s) to {args.output}")
            print(f"SUCCESS: Exported {len(items)} item(s) to {args.output}")
        else:
            # Display formatted list
            print(format_catalog_list(items))
        
        return 0
    
    except (AuthenticationError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List all catalog items.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        items = search_catalog_items(
            order_by=args.order_by,
            order=args.order
        )
        
        if args.output:
            # Export to JSON
            with open(args.output, 'w') as f:
                json.dump(items, f, indent=2)
            logger.info(f"Exported {len(items)} item(s) to {args.output}")
            print(f"SUCCESS: Exported {len(items)} item(s) to {args.output}")
        else:
            # Display formatted list
            print(format_catalog_list(items))
        
        return 0
    
    except (AuthenticationError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def cmd_show(args: argparse.Namespace) -> int:
    """Show catalog item details.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    try:
        if not args.item_uuid:
            logger.error("--item-uuid is required")
            return 1
        
        item = get_catalog_item(args.item_uuid)
        
        if args.output:
            # Export to JSON
            with open(args.output, 'w') as f:
                json.dump(item, f, indent=2)
            logger.info(f"Exported item details to {args.output}")
            print(f"SUCCESS: Exported item details to {args.output}")
        else:
            # Display formatted details
            print(format_catalog_item_details(item))
        
        return 0
    
    except (AuthenticationError, CatalogItemNotFoundError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Manage PandaDoc product catalog",
        epilog="""
Commands:
  list              List all catalog items
  search            Search catalog items
  show              Show catalog item details

Examples:
  uv run catalog_manager.py list
  uv run catalog_manager.py search --query "laptop"
  uv run catalog_manager.py show --item-uuid "abc123..."
  uv run catalog_manager.py search --query "product" --category-id "123" --order-by price --order desc
  uv run catalog_manager.py search --query "laptop" --output results.json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all catalog items")
    list_parser.add_argument(
        "--order-by",
        choices=["sku", "name", "price", "modified_date"],
        default="name",
        help="Sort by field (default: name)"
    )
    list_parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="asc",
        help="Sort order (default: asc)"
    )
    list_parser.add_argument(
        "--output",
        help="Export to JSON file"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search catalog items")
    search_parser.add_argument(
        "--query",
        help="Search query (searches title, SKU, description, category name, custom fields)"
    )
    search_parser.add_argument(
        "--type",
        help="Filter by item type"
    )
    search_parser.add_argument(
        "--billing-type",
        help="Filter by billing type"
    )
    search_parser.add_argument(
        "--category-id",
        help="Filter by category ID"
    )
    search_parser.add_argument(
        "--order-by",
        choices=["sku", "name", "price", "modified_date"],
        default="name",
        help="Sort by field (default: name)"
    )
    search_parser.add_argument(
        "--order",
        choices=["asc", "desc"],
        default="asc",
        help="Sort order (default: asc)"
    )
    search_parser.add_argument(
        "--exclude-uuids",
        help="Comma-separated list of UUIDs to exclude"
    )
    search_parser.add_argument(
        "--output",
        help="Export to JSON file"
    )
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show catalog item details")
    show_parser.add_argument(
        "--item-uuid",
        required=True,
        help="Catalog item UUID"
    )
    show_parser.add_argument(
        "--output",
        help="Export to JSON file"
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
        elif args.command == "search":
            return cmd_search(args)
        elif args.command == "show":
            return cmd_show(args)
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

