#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "requests",
#   "python-dotenv",
# ]
# ///

"""
Monitor PandaDoc document status with watch mode and export options.

This script checks document status with support for real-time updates (watch mode),
JSON/CSV export, and status filtering.

Usage:
    # Check single document
    uv run check_document_status.py --document-id "abc123"

    # Watch document status (continuous monitoring)
    uv run check_document_status.py --document-id "abc123" --watch --interval 30

    # Check multiple documents
    uv run check_document_status.py --document-ids "abc123,def456,ghi789"

    # Export to JSON
    uv run check_document_status.py --document-id "abc123" --format json --output status.json

    # Export to CSV
    uv run check_document_status.py --document-ids "abc123,def456" --format csv --output status.csv
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime
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
RATE_LIMIT_DELAY = 6  # seconds (for 10 req/min limit)

# Set up logging
logger = logging.getLogger(__name__)


class PandaDocException(Exception):
    """Base exception for PandaDoc API errors."""
    pass


class AuthenticationError(PandaDocException):
    """Raised when authentication fails."""
    pass


class DocumentNotFoundError(PandaDocException):
    """Raised when document is not found."""
    pass


class RateLimiter:
    """Implements rate limiting for API requests."""

    def __init__(self, requests_per_minute: int = 10):
        """Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []

    def wait_if_needed(self) -> None:
        """Wait if rate limit is reached."""
        now = time.time()
        minute_ago = now - 60

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if t > minute_ago]

        # Check if limit reached
        if len(self.request_times) >= self.requests_per_minute:
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest) + 1
            logger.warning(
                f"Rate limit reached. Waiting {wait_time:.1f} seconds..."
            )
            time.sleep(wait_time)

        # Record this request
        self.request_times.append(now)


rate_limiter = RateLimiter()


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


def get_document_status(document_id: str) -> Dict[str, Any]:
    """Get document status.

    Args:
        document_id: Document ID

    Returns:
        Document data dictionary

    Raises:
        DocumentNotFoundError: If document not found
        AuthenticationError: If authentication fails
    """
    rate_limiter.wait_if_needed()

    logger.debug(f"Fetching status for {document_id}")
    url = f"{BASE_URL}/documents/{document_id}"
    headers = get_headers()

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif e.response.status_code == 404:
            raise DocumentNotFoundError(f"Document not found: {document_id}")
        else:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise
    except requests.exceptions.RequestException as e:
        raise PandaDocException(f"Request failed: {e}")

    return response.json()


def format_status_table(docs: List[Dict[str, Any]]) -> str:
    """Format documents as a table.

    Args:
        docs: List of document dictionaries

    Returns:
        Formatted table string
    """
    if not docs:
        return "No documents found"

    lines = [
        "",
        "Document Status Report",
        "=" * 80,
        f"{'ID':<20} {'Name':<30} {'Status':<20} {'Modified':<15}",
        "-" * 80,
    ]

    for doc in docs:
        doc_id = doc.get("id", "N/A")[:20]
        name = doc.get("name", "N/A")[:30]
        status = doc.get("status", "N/A")[:20]
        modified = doc.get("date_modified", "N/A")[:15]
        lines.append(f"{doc_id:<20} {name:<30} {status:<20} {modified:<15}")

    lines.append("=" * 80)

    # Show recipient status if available
    if docs and "recipients" in docs[0]:
        lines.append("")
        lines.append("Recipient Status:")
        lines.append("-" * 80)
        for doc in docs:
            doc_id = doc.get("id")
            recipients = doc.get("recipients", [])
            if recipients:
                lines.append(f"Document: {doc_id}")
                for recipient in recipients:
                    email = recipient.get("email")
                    role = recipient.get("role", "Unknown")
                    status = recipient.get("recipient_status", "pending")
                    lines.append(f"  - {email} ({role}): {status}")

    return "\n".join(lines)


def export_to_json(docs: List[Dict[str, Any]], output_path: str) -> None:
    """Export documents to JSON file.

    Args:
        docs: List of document dictionaries
        output_path: Output file path
    """
    logger.info(f"Exporting to JSON: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(docs, f, indent=2)
    logger.info(f"Exported {len(docs)} document(s)")


def export_to_csv(docs: List[Dict[str, Any]], output_path: str) -> None:
    """Export documents to CSV file.

    Args:
        docs: List of document dictionaries
        output_path: Output file path
    """
    logger.info(f"Exporting to CSV: {output_path}")

    if not docs:
        logger.warning("No documents to export")
        return

    # Extract flat fields
    with open(output_path, 'w', newline='') as f:
        fieldnames = [
            "id", "name", "status", "date_created", "date_modified",
            "num_recipients", "num_pages"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for doc in docs:
            row = {
                "id": doc.get("id"),
                "name": doc.get("name"),
                "status": doc.get("status"),
                "date_created": doc.get("date_created"),
                "date_modified": doc.get("date_modified"),
                "num_recipients": len(doc.get("recipients", [])),
                "num_pages": doc.get("num_pages"),
            }
            writer.writerow(row)

    logger.info(f"Exported {len(docs)} document(s)")


def display_document_details(doc: Dict[str, Any]) -> None:
    """Display detailed document information.

    Args:
        doc: Document dictionary
    """
    lines = [
        "",
        "=" * 60,
        "DOCUMENT DETAILS",
        "=" * 60,
        f"ID:           {doc.get('id')}",
        f"Name:         {doc.get('name')}",
        f"Status:       {doc.get('status')}",
        f"Created:      {doc.get('date_created')}",
        f"Modified:     {doc.get('date_modified')}",
        f"Pages:        {doc.get('num_pages')}",
    ]

    if "recipients" in doc and doc["recipients"]:
        lines.append("")
        lines.append("RECIPIENTS:")
        for i, recipient in enumerate(doc["recipients"], 1):
            lines.append(f"  {i}. {recipient.get('email')}")
            lines.append(f"     Role: {recipient.get('role')}")
            lines.append(f"     Status: {recipient.get('recipient_status')}")
            lines.append(f"     Signed: {recipient.get('signed_at', 'Not yet')}")

    lines.append("=" * 60)
    print("\n".join(lines))


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Check and monitor PandaDoc document status",
        epilog="""
Examples:
  # Check single document
  python check_document_status.py --document-id "abc123"

  # Watch document (continuous monitoring)
  python check_document_status.py --document-id "abc123" --watch --interval 30

  # Check multiple documents
  python check_document_status.py --document-ids "abc123,def456,ghi789"

  # Export to JSON
  python check_document_status.py --document-id "abc123" --format json --output status.json

  # Export to CSV
  python check_document_status.py --document-ids "abc123,def456" --format csv --output status.csv
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--document-id",
        help="Single document ID to check"
    )
    parser.add_argument(
        "--document-ids",
        help="Multiple document IDs (comma-separated)"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch document status continuously"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Watch interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (for json/csv formats)"
    )
    parser.add_argument(
        "--filter-status",
        help="Filter by status (e.g., 'document.sent')"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_arguments()
    configure_logging(args.verbose)

    try:
        # Validate API key
        validate_api_key()

        # Determine document IDs
        document_ids = []
        if args.document_id:
            document_ids = [args.document_id]
        elif args.document_ids:
            document_ids = [d.strip() for d in args.document_ids.split(",")]
        else:
            logger.error("Must provide either --document-id or --document-ids")
            return 1

        # Watch mode loop
        if args.watch:
            logger.info(f"Watching {len(document_ids)} document(s) (interval: {args.interval}s)")
            print(f"Watching {len(document_ids)} document(s)...")
            print("Press Ctrl+C to stop")
            print()

            try:
                while True:
                    # Fetch all documents
                    documents = []
                    for doc_id in document_ids:
                        try:
                            doc = get_document_status(doc_id)
                            documents.append(doc)
                        except DocumentNotFoundError:
                            logger.warning(f"Document not found: {doc_id}")
                            continue

                    # Apply filters
                    if args.filter_status:
                        documents = [
                            d for d in documents
                            if d.get("status") == args.filter_status
                        ]

                    # Clear screen and display
                    print("\033[2J\033[H")  # ANSI clear screen
                    print(format_status_table(documents))
                    print(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                    # Wait before next check
                    time.sleep(args.interval)

            except KeyboardInterrupt:
                print("\nWatch mode stopped")
                return 0

        else:
            # Single check
            documents = []
            for doc_id in document_ids:
                try:
                    doc = get_document_status(doc_id)
                    documents.append(doc)
                except DocumentNotFoundError as e:
                    logger.error(f"Error: {e}")
                    return 1

            # Apply filters
            if args.filter_status:
                documents = [
                    d for d in documents
                    if d.get("status") == args.filter_status
                ]

            # Display or export
            if args.format == "json":
                if args.output:
                    export_to_json(documents, args.output)
                else:
                    print(json.dumps(documents, indent=2))
            elif args.format == "csv":
                if args.output:
                    export_to_csv(documents, args.output)
                else:
                    logger.error("CSV format requires --output file")
                    return 1
            else:
                # Table format (default)
                print(format_status_table(documents))
                if len(documents) == 1:
                    display_document_details(documents[0])

        return 0

    except KeyboardInterrupt:
        logger.error("Interrupted by user")
        return 1
    except (AuthenticationError, PandaDocException) as e:
        logger.error(f"Error: {e}")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
